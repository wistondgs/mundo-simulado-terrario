"""Versioned registry of cross-domain relation semantics.

Relation semantics are declared here as data with constraints, never as loose
strings scattered through the code. `SUPPORTS_THEORY` is intentionally absent:
it may only ever be introduced by an explicit EvidenceGraph declaration, never
by CrossGraph inference.
"""
from __future__ import annotations

from terrario.lab.crossgraph.domain import AssertionClass, Domain, RelationSemantics

RELATION_REGISTRY_VERSION = "terrario.cross-graph-relations/v1"

_ALL = tuple(d.value for d in Domain)
_REVIEWED = (
    AssertionClass.SOURCE_EXPLICIT.value, AssertionClass.USER_ASSERTED.value,
    AssertionClass.ANALYST_ASSERTED.value, AssertionClass.SYSTEM_DERIVED.value,
    AssertionClass.IMPORTED.value, AssertionClass.LEGACY_MAPPING.value,
)


def _rel(relation_type, source, target, meaning, inverse=None, transitive=False,
         symmetric=False, acyclic=False, provenance=_REVIEWED,
         directionality="DIRECTED") -> RelationSemantics:
    return RelationSemantics(
        relation_type=relation_type, source_domain_constraint=tuple(source),
        target_domain_constraint=tuple(target), directionality=directionality,
        inverse_relation=inverse, transitive=transitive, symmetric=symmetric,
        scientific_meaning=meaning, allowed_provenance_classes=tuple(provenance),
        acyclic=acyclic, registry_version=RELATION_REGISTRY_VERSION)


RELATIONS: dict[str, RelationSemantics] = {r.relation_type: r for r in (
    _rel("DERIVED_FROM", _ALL, _ALL, "entity is derived from another", acyclic=True),
    _rel("DERIVED_FROM_VERSION", _ALL, _ALL, "entity is derived from an exact prior version", acyclic=True),
    _rel("EXTRACTED_FROM", (Domain.CLAIM.value, Domain.ONTOLOGY.value),
         (Domain.REFERENCE.value, Domain.CORPUS.value), "claim/concept was extracted from a source"),
    _rel("REFERS_TO_CONCEPT", (Domain.CLAIM.value, Domain.REFERENCE.value),
         (Domain.ONTOLOGY.value, Domain.THEORY.value), "claim/reference refers to a concept"),
    _rel("CANONICAL_CANDIDATE_FOR", (Domain.ONTOLOGY.value,), (Domain.ONTOLOGY.value, Domain.THEORY.value),
         "raw concept is a candidate for a canonical concept"),
    _rel("MAPS_TO", _ALL, _ALL, "analyst-asserted mapping between distinct entities (not identity)"),
    _rel("OPERATIONALIZES", (Domain.EXPERIMENT.value, Domain.SCENARIO.value, Domain.HYPOTHESIS.value),
         (Domain.THEORY.value, Domain.ONTOLOGY.value, Domain.HYPOTHESIS.value),
         "experiment/scenario operationalizes a construct"),
    _rel("MOTIVATES", (Domain.THEORY.value, Domain.REFERENCE.value, Domain.CLAIM.value),
         (Domain.HYPOTHESIS.value, Domain.EXPERIMENT.value), "source motivates a hypothesis/experiment"),
    _rel("INSPIRED_BY", _ALL, (Domain.REFERENCE.value, Domain.THEORY.value, Domain.HYPERGRAPH.value),
         "entity was methodologically inspired by another"),
    _rel("TESTS", (Domain.EXPERIMENT.value, Domain.SCENARIO.value, Domain.PREREGISTRATION.value),
         (Domain.HYPOTHESIS.value,), "experiment/scenario tests a hypothesis", inverse="TESTED_BY"),
    _rel("TESTED_BY", (Domain.HYPOTHESIS.value,), (Domain.EXPERIMENT.value, Domain.SCENARIO.value),
         "hypothesis is tested by an experiment", inverse="TESTS"),
    _rel("DISCRIMINATES_BETWEEN", (Domain.EXPERIMENT.value, Domain.SCENARIO.value),
         (Domain.HYPOTHESIS.value,), "experiment discriminates between rival hypotheses"),
    _rel("USES_SCENARIO", (Domain.EXPERIMENT.value, Domain.PREREGISTRATION.value),
         (Domain.SCENARIO.value,), "experiment uses a scenario"),
    _rel("INSTANTIATES_WORLD", (Domain.SCENARIO.value, Domain.EXPERIMENT.value),
         (Domain.WORLD.value,), "scenario/experiment instantiates a world definition"),
    _rel("PREREGISTERS", (Domain.PREREGISTRATION.value,), (Domain.EXPERIMENT.value, Domain.HYPOTHESIS.value),
         "preregistration locks an experiment/hypothesis"),
    _rel("PRODUCES", (Domain.EXPERIMENT.value,), (Domain.EVIDENCE.value,),
         "experiment produces an evidence record", inverse="HAS_EVIDENCE_RECORD"),
    _rel("HAS_EVIDENCE_RECORD", (Domain.EVIDENCE.value,), (Domain.EXPERIMENT.value,),
         "evidence record belongs to an experiment", inverse="PRODUCES"),
    _rel("EVIDENCE_RELATES_TO", (Domain.EVIDENCE.value,), (Domain.HYPOTHESIS.value, Domain.THEORY.value),
         "evidence relates to a hypothesis/theory as declared by the EvidenceGraph"),
    _rel("SUPERSEDES", _ALL, _ALL, "entity supersedes another", acyclic=True),
)}


def get_relation(relation_type: str) -> RelationSemantics | None:
    return RELATIONS.get(relation_type)
