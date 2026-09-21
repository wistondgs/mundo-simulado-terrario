"""The construction plan an engineering AI receives instead of a conversation.

Today the scientific identity of a capability travels in natural language
between sessions: what we supply, what the organism must acquire, which
mechanism we intend, what may not be concluded.  It works because people hold
the meaning, and it is lost the moment a session ends.

This emits the same content as a deterministic structure.  It is not a prompt
and not a template: no sentences are assembled here, because a plan that can be
reworded is a plan whose meaning depends on the wording.  It resolves every
reference and refuses to emit anything when one does not resolve -- an
unresolvable plan is worse than no plan, since it looks actionable.

What it deliberately does not do:

    it does not call a model            the operator AI stays outside
    it does not reword or summarise     every field is the passport's own
    it does not fill a missing field    absent stays absent, and refuses
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from terrario.lab import mechanism_spec as mechanisms
from terrario.lab.capability_passport import (
    REGISTRY, CapabilityPassport, SCHEMA_VERSION_V2, status_of,
)
from terrario.lab.persistence.canonical import content_hash, plain

PLAN_SCHEMA = "terrario.lab.capability-construction-plan/v1"


class PlanRefused(ValueError):
    """Carries the codes, so a caller can tell a missing field from a bad one."""

    def __init__(self, codes: tuple[str, ...]):
        self.codes = tuple(sorted(set(codes)))
        super().__init__("; ".join(self.codes))


@dataclass(frozen=True)
class ResolvedReferences:
    mechanism: mechanisms.MechanismSpec | None
    concepts: tuple[str, ...]
    prerequisites: tuple[str, ...]


def load(capability_id: str) -> CapabilityPassport:
    """Fail closed on an identity that does not resolve."""
    passport = REGISTRY.get(capability_id)
    if passport is None:
        raise PlanRefused((f"UNKNOWN_CAPABILITY:{capability_id}",))
    return passport


def validate(passport: CapabilityPassport) -> tuple[str, ...]:
    """Structural findings, not intelligence.

    Returns codes rather than raising, because a caller inspecting a draft
    wants the whole list, and `emit_plan` is the place that refuses.
    """
    findings: list[str] = []
    if passport.schema_version != SCHEMA_VERSION_V2:
        findings.append(f"NOT_V2:{passport.schema_version}")
    for name in ("supplied", "acquisition_target", "non_claims", "formalization_ref"):
        if not getattr(passport, name):
            findings.append(f"MISSING:{name}")
    for missing in passport.missing():
        findings.append(f"MANDATORY_FIELD_EMPTY:{missing}")
    ref = passport.formalization_ref
    if ref is not None:
        try:
            mechanisms.resolve(ref if isinstance(ref, mechanisms.MechanismRef)
                               else mechanisms.MechanismRef.from_record(ref))
        except mechanisms.MechanismError as exc:
            findings.append(f"{exc.code}:{passport.capability_id}")
        except (KeyError, TypeError, ValueError):
            findings.append(f"FORMALIZATION_REF_MALFORMED:{passport.capability_id}")
    for prerequisite in passport.known_dependencies:
        if prerequisite not in REGISTRY:
            findings.append(f"UNKNOWN_PREREQUISITE:{prerequisite}")
    return tuple(sorted(set(findings)))


def resolve_references(passport: CapabilityPassport) -> ResolvedReferences:
    from terrario.lab.agent_composition import CONCEPTS

    ref = passport.formalization_ref
    spec = None
    if ref is not None:
        spec = mechanisms.resolve(ref if isinstance(ref, mechanisms.MechanismRef)
                                  else mechanisms.MechanismRef.from_record(ref))
    known = {concept.key for concept in CONCEPTS}
    declared = tuple(x for x in (passport.composition_flag,) if x)
    return ResolvedReferences(
        mechanism=spec,
        concepts=tuple(sorted(set(declared) & known)),
        prerequisites=tuple(sorted(passport.known_dependencies)))


def emit_plan(capability_id: str) -> Mapping[str, Any]:
    """The nine questions, answered from the record and from nowhere else.

    Refuses rather than degrade: a plan emitted with an unresolved mechanism
    would send an engineering AI to implement a promise nobody can check it
    against.
    """
    passport = load(capability_id)
    findings = validate(passport)
    if findings:
        raise PlanRefused(findings)
    resolved = resolve_references(passport)
    spec = resolved.mechanism
    plan = {
        "schema_version": PLAN_SCHEMA,
        "capability_id": passport.capability_id,
        "passport_identity": passport.content_identity,
        "passport_state": status_of(passport).value,
        # what are we building
        "target": {"concept_id": passport.concept_id,
                   "operational_definition": passport.operational_definition,
                   "expected_behavior": passport.expected_behavior},
        # which mechanism, formally -- identity, not prose
        "formalization": {"mechanism_id": spec.mechanism_id, "version": spec.version,
                          "spec_hash": spec.spec_hash,
                          "operational_form": spec.operational_form,
                          "invariants": list(spec.invariants),
                          "must_not_degenerate_to": list(spec.degenerate_of)},
        # which code realises it -- kept separate on purpose
        "implementation": {"algorithm_id": passport.algorithm_id,
                           "algorithm_version": passport.algorithm_version},
        # what we give, and what must emerge
        "supplied": [plain(x) for x in passport.supplied],
        "acquisition_target": [plain(x) for x in passport.acquisition_target],
        "prerequisites": list(resolved.prerequisites),
        # what it may not already receive solved
        "forbidden_information": list(passport.forbidden_information),
        "implementation_contract": {"inputs": list(passport.inputs),
                                    "outputs": list(passport.outputs),
                                    "internal_state": list(passport.internal_state),
                                    "allowed_information": list(passport.allowed_information)},
        # how it is judged, and what would sink it
        "experimental_contract": {"required_world_property": passport.required_world_property,
                                  "demanding_world": passport.demanding_world,
                                  "falsification_controls": list(passport.falsification_controls),
                                  "intervention_purity": passport.intervention_purity.value},
        "falsifiers": {"negative_prediction": passport.negative_prediction},
        "evidence_requirements": {"primary_endpoint": passport.primary_endpoint,
                                  "secondary_endpoints": list(passport.secondary_endpoints)},
        # what stays out of reach even if it comes out positive
        "non_claims": list(passport.non_claims),
        "provenance": {"corpus_provenance": list(passport.corpus_provenance),
                       "operationalization_id": passport.operationalization_id},
    }
    return {**plan, "plan_identity": content_hash(plan)}
