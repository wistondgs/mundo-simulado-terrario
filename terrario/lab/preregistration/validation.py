"""Transparent policy-as-code validation for preregistration commitments."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from terrario.lab.persistence.canonical import content_hash, plain
from terrario.lab.preregistration.domain import (
    CausalMode,
    EndpointRole,
    ExposureStatus,
    FindingSeverity,
    Partition,
    PreregistrationDraft,
    StudyIntent,
    ValidationFinding,
)
from terrario.lab.preregistration.cl7 import PLANNING_TRACE_METRIC_ID, paired_matrix_report

POLICY_VERSION = "preregistration-policy-1.0"


@dataclass(frozen=True)
class RuleDefinition:
    rule_id: str
    rule_version: str
    severity: FindingSeverity
    description: str
    source: str = "PREREGISTRATION-CORE-01"


RULES = (
    RuleDefinition("PR-REF-001", "1", FindingSeverity.REFERENCE_ERROR, "All scientific references are pinned."),
    RuleDefinition("PR-REV-001", "1", FindingSeverity.REFERENCE_ERROR, "Upstream design review is approved."),
    RuleDefinition("PR-CAUSAL-001", "1", FindingSeverity.STRUCTURAL_ERROR, "Causal designs declare identification commitments."),
    RuleDefinition("PR-METRIC-001", "1", FindingSeverity.STRUCTURAL_ERROR, "Primary endpoints use implemented metrics."),
    RuleDefinition("PR-SIGNAL-001", "1", FindingSeverity.STRUCTURAL_ERROR, "Required metric signals are recorded."),
    RuleDefinition("PR-SEED-001", "1", FindingSeverity.STRUCTURAL_ERROR, "Seed commitments are explicit and consistent."),
    RuleDefinition("PR-MATRIX-001", "1", FindingSeverity.INTEGRITY_ERROR, "Trial matrix identity and cardinality verify."),
    RuleDefinition("PR-ANALYSIS-001", "1", FindingSeverity.STRUCTURAL_ERROR, "Analysis and multiplicity policies are explicit."),
    RuleDefinition("PR-POLICY-001", "1", FindingSeverity.STRUCTURAL_ERROR, "Stopping, exclusion, and failure policies are explicit."),
    RuleDefinition("PR-SOFTWARE-001", "1", FindingSeverity.INTEGRITY_ERROR, "Software identity can be reconstructed."),
    RuleDefinition("PR-EXPOSURE-001", "1", FindingSeverity.EXPOSURE_WARNING, "Holdout exposure history is disclosed."),
    RuleDefinition("PR-RESOURCE-001", "1", FindingSeverity.RESOURCE_WARNING, "Required execution resources are not silently substituted."),
    RuleDefinition("PR-PROXY-001", "1", FindingSeverity.SCIENTIFIC_WARNING, "Metric implementation is not construct validation."),
    RuleDefinition("PR-CL7-001", "1", FindingSeverity.INTEGRITY_ERROR, "Planning-trace ablation uses a complete paired treatment matrix."),
)
RULE_BY_ID = {rule.rule_id: rule for rule in RULES}


def policy_snapshot() -> Mapping[str, Any]:
    return {
        "policy_version": POLICY_VERSION,
        "rules": [plain(rule) for rule in RULES],
        "deterministic": True,
        "automatic_approval": False,
        "scientific_execution": False,
    }


def policy_snapshot_hash() -> str:
    return content_hash(policy_snapshot())


def _instrument_findings(metric, endpoint) -> list:
    """Resolve a primary endpoint against the canonical instrument authority.

    Fails closed in every branch, including the one where the authority itself
    cannot be imported: an enforcement gate that degrades to permissive under
    an ImportError is not an enforcement gate.
    """
    where = f"metrics.{metric.metric_id}"
    if metric.instrument_ref is None:
        return [_finding("PR-INSTRUMENT-001", where,
                         "Primary endpoint is not bound to a canonical scientific instrument.",
                         endpoint_id=endpoint.endpoint_id, instrument_ref=None)]
    try:
        from terrario.lab import instrument_registry as authority
    except Exception:
        return [_finding("PR-INSTRUMENT-001", where,
                         "Canonical instrument authority is unavailable; a primary endpoint "
                         "cannot be validated and is refused rather than assumed.",
                         endpoint_id=endpoint.endpoint_id)]
    try:
        ref = authority.InstrumentRef.from_record(dict(metric.instrument_ref))
        authority.assert_admissible(ref)
    except authority.InstrumentResolutionError as exc:
        return [_finding("PR-INSTRUMENT-001", where,
                         "Primary endpoint instrument does not resolve in the canonical registry.",
                         endpoint_id=endpoint.endpoint_id, code=exc.code)]
    except RuntimeError as exc:
        return [_finding("PR-INSTRUMENT-001", where,
                         "Primary endpoint instrument is registered but not reportable.",
                         endpoint_id=endpoint.endpoint_id, detail=str(exc))]
    return []


def _finding(rule_id: str, path: str, description: str, **details: Any) -> ValidationFinding:
    rule = RULE_BY_ID[rule_id]
    return ValidationFinding(rule.rule_id, rule.rule_version, rule.severity, path,
                             description, rule.source, details)


def _walk_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for item in value.values():
            yield from _walk_strings(item)
    elif isinstance(value, (tuple, list)):
        for item in value:
            yield from _walk_strings(item)


def validate_preregistration(
    draft: PreregistrationDraft,
    trial_matrix: Mapping[str, Any],
    *,
    upstream_review_approved: bool,
    exposure_status: ExposureStatus,
) -> tuple[ValidationFinding, ...]:
    findings: list[ValidationFinding] = []
    scientific = plain(draft.scientific_payload())

    live_tokens = {"latest", "current", "active", "default"}
    live = sorted({value for value in _walk_strings(scientific) if value.casefold() in live_tokens})
    pinned = draft.protocol.experiment_draft_version_id and draft.protocol.experiment_draft_hash \
        and draft.protocol.trial_matrix_version_id and draft.protocol.trial_matrix_hash \
        and draft.protocol.scenario_hash
    if not pinned or live:
        findings.append(_finding("PR-REF-001", "protocol", "Unpinned or live references are prohibited.", live_references=live))
    if not upstream_review_approved:
        findings.append(_finding("PR-REV-001", "scientific_question.upstream_review", "An exact human upstream approval is required."))

    if draft.causal_design.mode is CausalMode.CAUSAL:
        required = {
            "manipulated_variable": draft.causal_design.manipulated_variable,
            "intervention": draft.causal_design.intervention,
            "comparison": draft.causal_design.comparison,
            "control": draft.causal_design.control,
            "outcome": draft.causal_design.outcome,
            "estimand": draft.causal_design.estimand,
            "manipulation_check": draft.causal_design.manipulation_check,
        }
        missing = sorted(key for key, value in required.items() if not value)
        if missing or not draft.causal_design.identification_assumptions:
            findings.append(_finding("PR-CAUSAL-001", "causal_design", "Causal commitment is incomplete.", missing=missing))

    metric_by_id = {metric.metric_id: metric for metric in draft.metrics}
    primary = tuple(endpoint for endpoint in draft.endpoints if endpoint.role is EndpointRole.PRIMARY)
    if draft.study_intent in {StudyIntent.CONFIRMATORY, StudyIntent.REPLICATION, StudyIntent.ABLATION} and not primary:
        findings.append(_finding("PR-METRIC-001", "endpoints", "This study intent requires a primary endpoint."))
    for endpoint in draft.endpoints:
        metric = metric_by_id.get(endpoint.metric_id)
        if metric is None:
            findings.append(_finding("PR-METRIC-001", f"endpoints.{endpoint.endpoint_id}", "Endpoint metric is absent."))
        elif endpoint.role is EndpointRole.PRIMARY and metric.implementation_status != "IMPLEMENTED":
            findings.append(_finding("PR-METRIC-001", f"metrics.{metric.metric_id}", "Primary metric implementation is not available.", status=metric.implementation_status))
        elif endpoint.role is EndpointRole.PRIMARY:
            # G8.  A confirmatory endpoint must resolve to an instrument the
            # scientific authority has certified.  Being known to the runtime
            # metric registry is not the same claim and never stands in for it:
            # that substitution is how an uncalibrated proxy becomes a finding.
            findings.extend(_instrument_findings(metric, endpoint))
    observer_signals = {channel.channel_id for channel in draft.observer.channels if channel.separation_class != "DEBUG_ONLY"}
    for metric in draft.metrics:
        missing = sorted(set(metric.required_signals) - observer_signals)
        if missing:
            findings.append(_finding("PR-SIGNAL-001", f"metrics.{metric.metric_id}", "Required signals are absent from the scientific Observer commitment.", missing=missing))
        if metric.validation_status != "VALIDATED_FOR_CONSTRUCT":
            findings.append(_finding("PR-PROXY-001", f"metrics.{metric.metric_id}", "Implemented proxy is not validated as the construct.", validation_status=metric.validation_status))

    seeds = draft.seeds
    if not seeds.world_seeds or not seeds.agent_seeds or len(set(seeds.world_seeds)) != len(seeds.world_seeds) or len(set(seeds.agent_seeds)) != len(seeds.agent_seeds):
        findings.append(_finding("PR-SEED-001", "seeds", "World and agent seeds must be nonempty, explicit, and unique."))
    if seeds.world_seed_hash != content_hash(seeds.world_seeds) or seeds.agent_seed_hash != content_hash(seeds.agent_seeds):
        findings.append(_finding("PR-SEED-001", "seeds.hashes", "Seed set hash mismatch."))
    by_kind: dict[str, dict[int, set[Partition]]] = {}
    exceptions: set[tuple[str, int]] = set()
    for assignment in draft.partitions:
        for seed in assignment.seeds:
            by_kind.setdefault(assignment.seed_kind, {}).setdefault(seed, set()).add(assignment.partition)
            if assignment.exception_reason:
                exceptions.add((assignment.seed_kind, seed))
    incompatible = []
    for kind, assignments in by_kind.items():
        for seed, partitions in assignments.items():
            if len(partitions) > 1 and (kind, seed) not in exceptions:
                incompatible.append({"kind": kind, "seed": seed, "partitions": sorted(x.value for x in partitions)})
    if incompatible:
        findings.append(_finding("PR-SEED-001", "partitions", "Seeds overlap incompatible partitions without an explicit exception.", overlaps=incompatible))

    cells = tuple(trial_matrix.get("cells") or ())
    if trial_matrix.get("execution_performed") is not False or int(trial_matrix.get("total_trials", -1)) != len(cells) or not cells:
        findings.append(_finding("PR-MATRIX-001", "trial_matrix", "Frozen TrialMatrix is missing, inconsistent, or executing."))
    matrix_world = {int(cell["world_seed"]) for cell in cells if "world_seed" in cell}
    matrix_agent = {int(cell["agent_seed"]) for cell in cells if "agent_seed" in cell}
    if matrix_world != set(seeds.world_seeds) or matrix_agent != set(seeds.agent_seeds):
        findings.append(_finding("PR-MATRIX-001", "trial_matrix.seeds", "TrialMatrix seeds differ from SeedCommitment."))
    if PLANNING_TRACE_METRIC_ID in metric_by_id:
        cl7 = paired_matrix_report(trial_matrix)
        if not cl7["valid"]:
            findings.append(_finding("PR-CL7-001", "trial_matrix", "CL-7 paired-ablation matrix is incomplete or contradictory.", **cl7))
        metric = metric_by_id[PLANNING_TRACE_METRIC_ID]
        try:
            from terrario.lab.planning_trace_metric import specification, validate_construct
            expected_spec = specification()["metric_spec_hash"]
            expected_calibration = validate_construct()["calibration_report_hash"]
        except Exception:
            expected_spec = expected_calibration = None
        overlap = {
            kind: sorted(set(metric.calibration_seed_set.get(kind, ())) & set(metric.confirmatory_seed_set.get(kind, ())) )
            for kind in {"world", "agent"}
        }
        if (metric.specification_hash != expected_spec or metric.calibration_report_hash != expected_calibration
                or not metric.calibration_report_id or any(overlap.values())):
            findings.append(_finding("PR-CL7-001", "metrics.planned-action-evaluation-pathway",
                "CL-7 metric calibration, specification, or held-out seed binding is invalid.",
                specification_hash=metric.specification_hash, expected_specification_hash=expected_spec,
                calibration_report_hash=metric.calibration_report_hash,
                expected_calibration_report_hash=expected_calibration,
                calibration_confirmatory_overlap="PARTIAL" if any(overlap.values()) else "NONE", overlap=overlap))

    if draft.analysis.multiplicity_policy == "" or not draft.analysis.missing_data_policy or not draft.analysis.interpretation_boundary:
        findings.append(_finding("PR-ANALYSIS-001", "analysis", "Analysis, missing data, and interpretation policies must be explicit."))
    if len(primary) > 1 and draft.analysis.multiplicity_policy not in {"NONE_EXPLICIT", "BONFERRONI", "HOLM", "FDR_BH"}:
        findings.append(_finding("PR-ANALYSIS-001", "analysis.multiplicity_policy", "Multiple primary endpoints require an explicit allowlisted policy."))

    allowed_stopping = {"FIXED_TRIAL_COUNT", "FIXED_SEED_SET", "SEQUENTIAL_PREDEFINED", "RESOURCE_BOUND", "EXTERNAL_TERMINATION_ONLY"}
    allowed_failure = {"RETRY_SAME_SEED", "EXCLUDE", "REPLACE_WITH_PRECOMMITTED_SEED", "COUNT_AS_FAILURE", "HUMAN_REVIEW_REQUIRED"}
    if draft.stopping.rule_type not in allowed_stopping:
        findings.append(_finding("PR-POLICY-001", "stopping", "Stopping rule is not allowlisted."))
    if not draft.failures.rules or any(rule.disposition not in allowed_failure for rule in draft.failures.rules):
        findings.append(_finding("PR-POLICY-001", "failures", "Failure policy is incomplete or not allowlisted."))
    if any(not rule.objective_condition for rule in draft.exclusions.rules):
        findings.append(_finding("PR-POLICY-001", "exclusions", "Exclusions require objective conditions."))

    if not draft.software.git_commit or len(draft.software.dependency_hash) != 64:
        findings.append(_finding("PR-SOFTWARE-001", "software", "Software commit and dependency manifest hash are required."))
    if draft.software.dirty_tree and not draft.environment_requirement.allow_dirty_tree:
        findings.append(_finding("PR-SOFTWARE-001", "software.dirty_tree", "Observed dirty tree violates the environment requirement."))
    if draft.software.dirty_tree and not draft.software.dirty_diff_hash:
        findings.append(_finding("PR-SOFTWARE-001", "software.dirty_diff_hash", "Dirty tree requires a captured diff hash."))

    if exposure_status is not ExposureStatus.UNEXPOSED:
        findings.append(_finding("PR-EXPOSURE-001", "seeds.exposure", "Holdout blindness cannot be asserted without review.", status=exposure_status.value))
    if draft.environment_requirement.agent_device.startswith("cuda") and not draft.observed_environment.cuda_available:
        findings.append(_finding("PR-RESOURCE-001", "environment.agent_device", "CUDA is required but unavailable; execution must remain blocked.", required=draft.environment_requirement.agent_device))
    return tuple(sorted(findings, key=lambda item: (not item.blocking, item.rule_id, item.path, item.finding_hash)))
