from dataclasses import replace
import multiprocessing
from pathlib import Path

import pytest

from terrario.lab.api import LabAPI
from terrario.lab.persistence import ArtifactRepository
from terrario.lab.persistence.codecs import preregistration_draft_from_payload
from terrario.lab.preregistration.domain import SeedCommitment, assert_transition, PreregistrationState, InvalidTransition
from terrario.lab.preregistration.repository import PreregistrationRepository
from tests.test_preregistration_core import approve_upstream, create_request, locked_flow, sources


def _lock_worker(root, args, output):
    try:
        repository = PreregistrationRepository(ArtifactRepository(root))
        result = repository.lock(*args)
        output.put(("LOCKED", result.attestation_id))
    except Exception as exc:
        output.put((getattr(exc, "code", type(exc).__name__), str(exc)))


def _candidate(api, preregistration_id="PR-ADV"):
    experiment, matrix = sources(api)
    request = create_request(experiment, matrix, preregistration_id=preregistration_id)
    _, created = api.dispatch("POST", "/api/v1/preregistrations", request)
    approve_upstream(api, experiment)
    _, candidate = api.dispatch("POST", f"/api/v1/preregistrations/{preregistration_id}/prepare-review",
        {"expected_hash": created["data"]["scientific_hash"], "reason": "candidate"})
    root = candidate["data"]["bundle_root_hash"]
    _, submitted = api.dispatch("POST", f"/api/v1/preregistrations/{preregistration_id}/submit", {"reason": "review"})
    findings = candidate["data"]["review_package"]["readiness"]["findings"]
    accepted = [{k: x[k] for k in ("finding_hash", "rule_id", "rule_version")} for x in findings if not x["blocking"]]
    _, decision = api.dispatch("POST", f"/api/v1/review-requests/{submitted['data']['review_id']}/decisions",
        {"artifact_hash": root, "decision": "APPROVE_PREREGISTRATION", "reason": "approve", "warning_acceptances": accepted})
    return candidate["data"], decision["data"], tuple(sorted(x["finding_hash"] for x in findings if not x["blocking"]))


def test_every_scientific_mutation_changes_root_and_ui_does_not(tmp_path):
    api = LabAPI(Path("."), data_root=tmp_path / ".terrario")
    experiment, matrix = sources(api)
    draft = api.preregistrations._assemble(create_request(experiment, matrix, preregistration_id="PR-MUT"))
    root = api.preregistrations.commitments.build(draft).bundle_root_hash
    mutations = (
        replace(draft, metrics=(replace(draft.metrics[0], proxy="changed proxy"),)),
        replace(draft, seeds=SeedCommitment.materialize((999,), draft.seeds.agent_seeds)),
        replace(draft, endpoints=(replace(draft.endpoints[0], decision_rule="changed rule"),)),
        replace(draft, analysis=replace(draft.analysis, effect_measure="median difference")),
        replace(draft, observer=replace(draft.observer, trace_policy="FORENSIC")),
        replace(draft, protocol=replace(draft.protocol, trial_matrix_hash="a" * 64)),
        replace(draft, protocol=replace(draft.protocol, scenario_hash="b" * 64)),
        replace(draft, software=replace(draft.software, git_commit="different")),
    )
    assert all(api.preregistrations.commitments.build(x).bundle_root_hash != root for x in mutations)
    ui_only = replace(draft, ui_preferences={"zoom": 2, "panel_position": "right", "theme": "dark"})
    assert api.preregistrations.commitments.build(ui_only).bundle_root_hash == root
    assert preregistration_draft_from_payload(__import__("terrario.lab.persistence.canonical", fromlist=["plain"]).plain(draft)).scientific_hash == draft.scientific_hash


@pytest.mark.parametrize("source,target", [
    (PreregistrationState.DRAFT, PreregistrationState.PREREGISTERED_LOCKED),
    (PreregistrationState.READY_FOR_REVIEW, PreregistrationState.PREREGISTERED_LOCKED),
    (PreregistrationState.WITHDRAWN, PreregistrationState.DRAFT),
    (PreregistrationState.SUPERSEDED, PreregistrationState.DRAFT),
])
def test_invalid_state_transitions_are_rejected(source, target):
    with pytest.raises(InvalidTransition): assert_transition(source, target)


def test_real_multiprocess_lock_has_exactly_one_winner(tmp_path):
    data_root = tmp_path / ".terrario"; api = LabAPI(Path("."), data_root=data_root)
    candidate, decision, warnings = _candidate(api)
    version = api.artifacts.current("PR-ADV").version_id; root = candidate["bundle_root_hash"]
    context = multiprocessing.get_context("fork"); output = context.Queue()
    common = ("PR-ADV", version, root, decision["decision_id"], "race-user", "explicit lock", warnings)
    processes = [context.Process(target=_lock_worker, args=(data_root, (*common, f"race-{i}"), output)) for i in range(6)]
    for process in processes: process.start()
    for process in processes: process.join(15); assert process.exitcode == 0
    results = [output.get(timeout=2)[0] for _ in processes]
    assert results.count("LOCKED") == 1
    assert all(x in {"LOCKED", "LOCKED_ARTIFACT"} for x in results)
    with api.artifacts._connect() as connection:
        assert connection.execute("SELECT count(*) FROM preregistration_locks WHERE preregistration_id='PR-ADV'").fetchone()[0] == 1


def test_lock_fault_inside_transaction_rolls_back_after_restart(tmp_path, monkeypatch):
    data_root = tmp_path / ".terrario"; api = LabAPI(Path("."), data_root=data_root)
    candidate, decision, _ = _candidate(api); repository = api.preregistrations.repository
    original = repository._append_chain
    def fail(*args, **kwargs): raise RuntimeError("injected-before-commit")
    monkeypatch.setattr(repository, "_append_chain", fail)
    with pytest.raises(RuntimeError): api.preregistrations.lock("PR-ADV", candidate["bundle_root_hash"], decision["decision_id"], "fault", "human", "fault-key")
    restarted = LabAPI(Path("."), data_root=data_root)
    assert not restarted.preregistrations.repository.is_locked("PR-ADV")
    assert restarted.artifacts.current_state(restarted.artifacts.current("PR-ADV").version_id) == "REVIEWED"
    monkeypatch.setattr(repository, "_append_chain", original)


def test_corrupted_copy_of_audit_chain_is_detected(tmp_path):
    api = LabAPI(Path("."), data_root=tmp_path / ".terrario"); locked_flow(api)
    rows = [dict(x) for x in api.preregistrations.repository.audit_chain("PR-CORE-1")]
    assert api.preregistrations.repository.verify_audit_rows("PR-CORE-1", rows)
    rows[1]["event_payload"] = {"corrupted": True}
    assert not api.preregistrations.repository.verify_audit_rows("PR-CORE-1", rows)


def test_full_backup_restore_preserves_lock_cas_exposure_and_verification(tmp_path):
    api = LabAPI(Path("."), data_root=tmp_path / "source"); locked_flow(api)
    api.dispatch("GET", "/api/worlds/D2/preview?seed=4242")
    archive = api.artifacts.backup_archive("preregistration")
    restored = ArtifactRepository.restore_archive(archive, tmp_path / "restored")
    restored_api = LabAPI(Path("."), data_root=tmp_path / "restored")
    report = restored_api.preregistrations.verify("PR-CORE-1")
    assert restored.integrity_check() == "ok" and report["valid"] and report["locked"]
    assert restored_api.preregistrations.repository.exposures("D2", 4242)


def test_portable_import_preserves_lineage_references_and_requires_local_review(tmp_path):
    source = LabAPI(Path("."), data_root=tmp_path / "source-import"); locked_flow(source)
    bundle = source.preregistrations.export("PR-CORE-1")
    target = LabAPI(Path("."), data_root=tmp_path / "target-import")
    imported = target.preregistrations.import_portable(bundle, "import-reviewer")
    assert imported["imported_attestation_trusted"] is False
    assert imported["requires_local_review_for_lock"] is True
    assert len(target.artifacts.versions("PR-CORE-1")) == len(bundle["artifact_lineage"])
    report = target.preregistrations.verify("PR-CORE-1")
    assert report["valid"] and report["referenced_artifacts_valid"] and report["parent_chain_valid"]
    duplicate = target.preregistrations.import_portable(bundle, "import-reviewer")
    assert duplicate["scientific_hash"] == imported["scientific_hash"]


def test_missing_portable_cas_component_is_rejected(tmp_path):
    api = LabAPI(Path("."), data_root=tmp_path / "portable"); locked_flow(api)
    bundle = api.preregistrations.export("PR-CORE-1")
    bundle["component_payloads"].pop(next(iter(bundle["component_payloads"])))
    report = api.preregistrations.validate_portable(bundle)
    assert not report["valid"] and any(x.startswith("COMPONENT_MISSING") for x in report["failures"])


def test_sql_rejects_review_audit_and_deviation_deletion(tmp_path):
    api = LabAPI(Path("."), data_root=tmp_path / ".terrario"); locked_flow(api)
    deviation = {"deviation_type": "SEED_DEVIATION", "affected_component": "seeds",
        "planned_behavior": "seed 1", "actual_behavior": "seed 2", "reason": "fault",
        "scientific_impact_assessment": "invalidates affected trial", "disposition": "QUARANTINE"}
    _, stored = api.dispatch("POST", "/api/v1/preregistrations/PR-CORE-1/deviations", deviation)
    import sqlite3
    for statement in (
        "UPDATE review_decisions SET reason='x'",
        "DELETE FROM preregistration_audit_chain",
        f"DELETE FROM artifact_versions WHERE version_id='{stored['data']['version_id']}'",
    ):
        with pytest.raises(sqlite3.IntegrityError), api.artifacts.transaction() as connection:
            connection.execute(statement)


def test_candidate_failures_never_publish_partial_governance_state(tmp_path, monkeypatch):
    api = LabAPI(Path("."), data_root=tmp_path / "candidate-fault"); experiment, matrix = sources(api)
    _, created = api.dispatch("POST", "/api/v1/preregistrations", create_request(experiment, matrix, preregistration_id="PR-FAULT"))
    approve_upstream(api, experiment)
    original = api.preregistrations.repository.seal_candidate
    monkeypatch.setattr(api.preregistrations.repository, "seal_candidate", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("after-cas-before-db")))
    with pytest.raises(RuntimeError): api.preregistrations.prepare_review("PR-FAULT", created["data"]["scientific_hash"], "human", "fault")
    restarted = LabAPI(Path("."), data_root=tmp_path / "candidate-fault")
    current = restarted.artifacts.current("PR-FAULT")
    assert current.version_number == 1 and restarted.artifacts.current_state(current.version_id) == "DRAFT"
    assert not restarted.preregistrations.repository.is_locked("PR-FAULT")
    monkeypatch.setattr(api.preregistrations.repository, "seal_candidate", original)


def test_canonical_hash_properties_without_external_dependency():
    import random
    from terrario.lab.persistence.canonical import canonical_json, content_hash
    rng = random.Random(20260912)
    for _ in range(250):
        items = [(f"k{i}", [rng.randint(-1000, 1000), rng.choice([True, False, None])]) for i in range(rng.randint(1, 20))]
        left, right = dict(items), dict(reversed(items))
        assert canonical_json(left) == canonical_json(right)
        assert content_hash(left) == content_hash(right)


def test_unknown_nested_scientific_fields_are_rejected(tmp_path):
    api = LabAPI(Path("."), data_root=tmp_path / "unknown"); experiment, matrix = sources(api)
    request = create_request(experiment, matrix, analysis={"mode": "DESCRIPTIVE_ONLY", "python": "os.system"})
    status, error = api.dispatch("POST", "/api/v1/preregistrations", request)
    assert status == 400 and "analysis" in error["error"]["message"]


def test_exposure_states_are_derived_without_mutating_locked_root(tmp_path):
    api = LabAPI(Path("."), data_root=tmp_path / "exposure-states")
    experiment, matrix = sources(api)
    request = create_request(experiment, matrix, preregistration_id="PR-EXPOSURE")
    _, created = api.dispatch("POST", "/api/v1/preregistrations", request)
    draft = api.preregistrations._draft_from_record(api.artifacts.current("PR-EXPOSURE"))
    assert api.preregistrations.readiness("PR-EXPOSURE")["exposure_status"] == "CONTAMINATION_REVIEW_REQUIRED"
    for seed in draft.seeds.world_seeds:
        api.preregistrations.record_exposure(draft.protocol.scenario_id, draft.protocol.scenario_hash, seed,
            "MANUAL_DECLARATION", "inventory-reviewer", "VERIFIED_UNEXPOSED_INVENTORY", f"inventory:{seed}")
    assert api.preregistrations.readiness("PR-EXPOSURE")["exposure_status"] == "UNEXPOSED"
    api.preregistrations.record_exposure(draft.protocol.scenario_id, draft.protocol.scenario_hash,
        draft.seeds.world_seeds[0], "PREVIEWED", "viewer", "TEST_PREVIEW", "preview")
    assert api.preregistrations.readiness("PR-EXPOSURE")["exposure_status"] == "PREEXPOSED"


def test_postlock_preview_is_bound_to_root_and_becomes_postlock_exposed(tmp_path):
    api = LabAPI(Path("."), data_root=tmp_path / "postlock-exposure"); _, _, candidate, _, _, _ = locked_flow(api)
    root = candidate["bundle_root_hash"]
    api.dispatch("GET", "/api/worlds/D2/preview?seed=1")
    readiness = api.preregistrations.readiness("PR-CORE-1")
    assert readiness["exposure_status"] == "POSTLOCK_EXPOSED"
    assert api.artifacts.current("PR-CORE-1").scientific_hash == root


def test_scientific_amendment_creates_new_reviewed_lineage_before_supersede(tmp_path):
    api = LabAPI(Path("."), data_root=tmp_path / "amendment"); _, _, parent_candidate, _, _, _ = locked_flow(api)
    parent_root = parent_candidate["bundle_root_hash"]
    amendment = {"change_class": "SCIENTIFIC", "reason": "stress intent amendment",
        "delta": {"study_intent": "STRESS_TEST"}, "child_preregistration_id": "PR-CHILD"}
    status, record = api.dispatch("POST", "/api/v1/preregistrations/PR-CORE-1/amendments", amendment)
    assert status == 201 and record["data"]["payload"]["parent_root_hash"] == parent_root
    child = api.artifacts.current("PR-CHILD")
    chain = api.preregistrations.repository.audit_chain("PR-CHILD")
    assert chain[0]["event_payload"]["parent_root_hash"] == parent_root
    _, candidate = api.dispatch("POST", "/api/v1/preregistrations/PR-CHILD/prepare-review",
        {"expected_hash": child.scientific_hash, "reason": "review amended root"})
    root = candidate["data"]["bundle_root_hash"]
    _, submitted = api.dispatch("POST", "/api/v1/preregistrations/PR-CHILD/submit", {"reason": "review"})
    warnings = candidate["data"]["review_package"]["readiness"]["findings"]
    accepted = [{k:x[k] for k in ("finding_hash", "rule_id", "rule_version")} for x in warnings if not x["blocking"]]
    _, decision = api.dispatch("POST", f"/api/v1/review-requests/{submitted['data']['review_id']}/decisions",
        {"artifact_hash": root, "decision": "APPROVE_PREREGISTRATION", "reason": "approve amendment", "warning_acceptances": accepted})
    assert api.dispatch("POST", "/api/v1/preregistrations/PR-CHILD/lock",
        {"expected_hash": root, "decision_id": decision["data"]["decision_id"], "reason": "lock amended root"})[0] == 201
    assert api.dispatch("POST", "/api/v1/preregistrations/PR-CORE-1/supersede",
        {"child_preregistration_id": "PR-CHILD", "reason": "replace with reviewed amendment"})[0] == 200
    assert api.preregistrations.verify("PR-CORE-1")["valid"]
    assert api.artifacts.current_state(api.artifacts.current("PR-CORE-1").version_id) == "SUPERSEDED"
