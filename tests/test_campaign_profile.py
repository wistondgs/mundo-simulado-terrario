"""Contracts for sealing a campaign without a person in the path.

The claim under test is not "it works without review".  It is that removing the
human makes the seal *stricter*: the reviewed path may accept a non-blocking
finding by enumerating it, and this one cannot accept anything at all.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from terrario.lab.api import LabAPI
from terrario.lab.persistence.canonical import plain
from terrario.lab.preregistration.campaign_profile import (
    DETERMINISTIC_ACTOR, CampaignSealRefused, seal_campaign,
)
from terrario.lab.preregistration.commitments import ROOT_SCHEMA, ROOT_SCHEMA_V2
from terrario.lab.preregistration.gate_manifest import GateManifest, SealedGate
from tests.test_preregistration_core import (
    approve_upstream, create_request, sources,
)


@pytest.fixture
def api(tmp_path):
    return LabAPI(Path("."), data_root=tmp_path / ".terrario")


GATES = GateManifest(gates=(
    SealedGate(gate_id="G-0", certifies="LINEAGE_INTACT", certifies_revision="v1",
               statement="inherited fingerprints identical before and after",
               criterion="fingerprint_before == fingerprint_after",
               negative_fixture="mutate the inherited core"),
    SealedGate(gate_id="G-1", certifies="PASSIVITY", certifies_revision="v1",
               statement="measuring moves no fingerprint and draws no randomness",
               criterion="fingerprints equal after measuring; metrics import no rng",
               negative_fixture="a metric that writes"),
))


def _drafted(api):
    experiment, matrix = sources(api)
    approve_upstream(api, experiment)
    service = api.preregistrations
    view = service.create(create_request(experiment, matrix), "tester")
    return service, view


def _with_gates(service, view, manifest=GATES):
    return service.derive(view["preregistration_id"], view["scientific_hash"],
                          {"gates": manifest.payload()}, "seal what the gates certify",
                          "tester")


# --- the refusals, which are the point --------------------------------------------

def test_a_campaign_without_a_gate_manifest_is_refused(api):
    """A campaign that has not said what it intends to certify cannot seal."""
    service, view = _drafted(api)
    with pytest.raises(CampaignSealRefused) as refused:
        seal_campaign(service, preregistration_id=view["preregistration_id"],
                      expected_hash=view["scientific_hash"], reason="autonomous seal")
    assert "GATE_MANIFEST_ABSENT" in refused.value.codes


def test_the_autonomous_seal_cannot_waive_a_warning(api, monkeypatch):
    """The reviewed path accepts warnings by enumerating them.  This one refuses,
    which is what makes removing the human safe rather than convenient."""
    service, view = _drafted(api)
    _with_gates(service, view)
    real = service.readiness

    def con_aviso(preregistration_id):
        report = dict(real(preregistration_id))
        report["findings"] = [*report.get("findings", ()),
                              {"blocking": False, "finding_hash": "warn-abc"}]
        return report

    monkeypatch.setattr(service, "readiness", con_aviso)
    with pytest.raises(CampaignSealRefused) as refused:
        seal_campaign(service, preregistration_id=view["preregistration_id"],
                      expected_hash=view["scientific_hash"], reason="autonomous seal")
    assert "WARNING_REQUIRES_HUMAN_ACCEPTANCE:warn-abc" in refused.value.codes


def test_a_blocking_finding_is_reported_apart_from_a_warning(api, monkeypatch):
    service, view = _drafted(api)
    _with_gates(service, view)
    real = service.readiness
    monkeypatch.setattr(service, "readiness", lambda pid: {
        **dict(real(pid)),
        "findings": [{"blocking": True, "finding_hash": "block-1"},
                     {"blocking": False, "finding_hash": "warn-1"}]})
    with pytest.raises(CampaignSealRefused) as refused:
        seal_campaign(service, preregistration_id=view["preregistration_id"],
                      expected_hash=view["scientific_hash"], reason="autonomous seal")
    assert refused.value.codes == ("BLOCKING_FINDING:block-1",
                                   "WARNING_REQUIRES_HUMAN_ACCEPTANCE:warn-1")


def test_the_two_warnings_a_real_draft_carries_are_the_two_a_machine_must_not_sign(api):
    """Measured, not assumed.  The default draft raises exactly `PR-EXPOSURE-001`
    -- whose own description reads "Holdout blindness cannot be asserted without
    review" -- and `PR-PROXY-001`, the proxy that is not validated as its
    construct.  Both are decisions about what a number means, which is the one
    thing a deterministic actor has no standing to make.

    So the strict rule is not an inconvenience to route around: a campaign seals
    autonomously by removing these conditions, or a person signs."""
    service, view = _drafted(api)
    reglas = {f["rule_id"] for f in service.readiness(view["preregistration_id"])["findings"]}
    assert reglas == {"PR-EXPOSURE-001", "PR-PROXY-001"}
    assert all(not f["blocking"]
               for f in service.readiness(view["preregistration_id"])["findings"])


# --- the seal itself ---------------------------------------------------------------

def _condiciones_limpias(service, view, monkeypatch):
    """Remove both findings the way a campaign actually would.

    Exposure is declared for real -- that is the supported path and it genuinely
    clears `PR-EXPOSURE-001`.  Construct validation is granted by moving the
    *registry*, not the draft: the registry is the authority, and a test that
    edited the draft instead would be performing the very forgery
    `_construct_validation_drift` exists to refuse."""
    from dataclasses import replace
    from terrario.lab.metrics_observer import ConstructValidationStatus

    draft = service._draft_from_record(
        service.artifacts.current(view["preregistration_id"], "Preregistration"))
    for seed in draft.seeds.world_seeds:
        service.record_exposure(draft.protocol.scenario_id,
                                draft.protocol.world_definition_hash, seed,
                                "MANUAL_DECLARATION", "tester",
                                "VERIFIED_UNEXPOSED_INVENTORY", "inventory-1")
    real = service.metrics.get
    monkeypatch.setattr(service.metrics, "get", lambda mid: replace(
        real(mid),
        construct_validation_status=ConstructValidationStatus.VALIDATED_FOR_CONSTRUCT))
    # And the draft now honestly restates what the registry grants.
    metrics = [{**m, "validation_status": "VALIDATED_FOR_CONSTRUCT"}
               for m in plain(draft.metrics)]
    return service.derive(view["preregistration_id"],
                          service.artifacts.current(view["preregistration_id"],
                                                    "Preregistration").scientific_hash,
                          {"metrics": metrics}, "registry grants construct validation",
                          "tester")


def test_a_draft_cannot_grant_itself_construct_validation(api):
    """Measured while building this door: `validate_preregistration` reads
    `validation_status` off the draft and `derive` lets a client set it, so
    `PR-PROXY-001` could be silenced upstream of the seal.  Refusing to seal
    while the draft and the registry disagree is what keeps "cannot waive"
    from being theatre."""
    service, view = _drafted(api)
    _with_gates(service, view)
    draft = service._draft_from_record(
        service.artifacts.current(view["preregistration_id"], "Preregistration"))
    forjadas = [{**m, "validation_status": "VALIDATED_FOR_CONSTRUCT"}
                for m in plain(draft.metrics)]
    derived = service.derive(view["preregistration_id"],
                             service.artifacts.current(view["preregistration_id"],
                                                       "Preregistration").scientific_hash,
                             {"metrics": forjadas}, "claim validation", "tester")

    with pytest.raises(CampaignSealRefused) as refused:
        seal_campaign(service, preregistration_id=view["preregistration_id"],
                      expected_hash=derived["scientific_hash"], reason="autonomous seal")
    assert any(c.startswith("CONSTRUCT_VALIDATION_DRIFT:") for c in refused.value.codes)


def test_a_campaign_seals_with_no_human_and_stays_locked(api, monkeypatch):
    service, view = _drafted(api)
    _with_gates(service, view)
    derived = _condiciones_limpias(service, view, monkeypatch)

    sealed = seal_campaign(service, preregistration_id=view["preregistration_id"],
                           expected_hash=derived["scientific_hash"],
                           reason="autonomous seal")

    assert sealed["approved_by"] == DETERMINISTIC_ACTOR
    assert sealed["accepted_warnings"] == []
    assert sealed["sealed_gates"] == 2
    assert sealed["gate_manifest_hash"] == GATES.manifest_hash
    assert service.repository.is_locked(view["preregistration_id"])


def test_the_sealed_actor_is_not_the_literal_the_human_gates_use(api):
    """Five human gates in the rail record `local-user`.  An autonomous seal
    that borrowed it would be indistinguishable from a review that never
    happened."""
    assert DETERMINISTIC_ACTOR != "local-user"


def test_sealing_a_campaign_produces_a_v2_bundle_with_the_gate_role(api, monkeypatch):
    service, view = _drafted(api)
    _with_gates(service, view)
    derived = _condiciones_limpias(service, view, monkeypatch)
    seal_campaign(service, preregistration_id=view["preregistration_id"],
                  expected_hash=derived["scientific_hash"], reason="autonomous seal")

    report = service.verify(view["preregistration_id"])
    assert report["valid"], report["failures"]
    current = service.artifacts.current(view["preregistration_id"], "Preregistration")
    root = current.payload["root_manifest"]
    assert root["schema_version"] == ROOT_SCHEMA_V2
    assert [c["role"] for c in root["components"]][-1] == "gates"


def test_a_draft_without_gates_still_seals_a_v1_bundle(api):
    """The ten roles predate this one and 141 bundles are committed with them.
    A draft that adds nothing must produce exactly the bundle it always did."""
    service, view = _drafted(api)
    prepared = service.prepare_review(view["preregistration_id"], view["scientific_hash"],
                                      "tester", "human path")
    assert prepared["review_package"]["candidate_root_hash"]
    current = service.artifacts.current(view["preregistration_id"], "Preregistration")
    root = current.payload["root_manifest"]
    assert root["schema_version"] == ROOT_SCHEMA
    assert "gates" not in [c["role"] for c in root["components"]]


def test_the_gate_manifest_survives_the_round_trip_through_storage(api):
    """It is stored as a payload and rebuilt through `manifest_from_payload`,
    which recomputes the hash rather than trusting the stored one."""
    service, view = _drafted(api)
    _with_gates(service, view)
    draft = service._draft_from_record(
        service.artifacts.current(view["preregistration_id"], "Preregistration"))
    assert draft.gates is not None
    assert draft.gates.manifest_hash == GATES.manifest_hash
    assert draft.gates.by_id()["G-1"].certifies == "PASSIVITY"
