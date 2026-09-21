"""What a campaign reveals about the ladder, which is not what it revealed about C.

A campaign produces two things that the project kept conflating.  Level 1.8's
scientific result is `FAMILY_MISMATCH`: under the family it implemented, the
construct was not realised.  Its developmental reading is different and does
not replace it -- the attempt exposed that a rung was missing before this one
could be attempted at all.

    scientific_result            FAMILY_MISMATCH
    developmental_interpretation CEILING_PROBE

So a probe is an interpretive object and deliberately not an `EvidenceClass`,
not an `EpistemicStatus`, and never a substitute for the campaign's own
outcome.  It sits beside the result and reads it.

**The rule that makes it safe: a probe can never promote a candidate to a
dependency.**  1.8 revealing that `F(Z,A)` cannot express the required
participation of the next observation justifies naming `EVSENS`, `REPUPD` and
`HISTDIS` as candidates.  It does not license writing `EVSENS REQUIRED_FOR
PREDSTATE`.  Turning the interpretation of a failure into demonstrated theory
is the exact move this module exists to block, so every claim a probe emits
comes out as a hypothesis and the constructor of the ledger refuses the rest.

**And an ordinary negative is not a ceiling.**  An organism that simply did not
learn tells us about the organism, not about the ladder.  If every negative
became a ceiling probe, the label would mean nothing and the programme would
have bought a synonym for disappointment.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping

from terrario.lab.persistence.canonical import content_hash
from terrario.lab.relation_ledger import (
    EffectForm, EpistemicStatus, EvidenceClass, HypothesisOrigin, RelationClaim,
    RelationSemantics, Scope,
)

SCHEMA_VERSION = "terrario.lab.ceiling-probe/v1"


class BlockerClass(StrEnum):
    """What kind of wall the campaign hit.

    `PERFORMANCE_ONLY` exists so it can be refused: "the agent did not learn"
    is a result about the agent and says nothing about what was missing
    beforehand.  Accepting it would make every disappointing campaign a
    developmental finding.
    """

    FAMILY_CANNOT_EXPRESS = "FAMILY_CANNOT_EXPRESS"
    PRECURSOR_UNESTABLISHED = "PRECURSOR_UNESTABLISHED"
    NECESSITY_UNDETERMINED = "NECESSITY_UNDETERMINED"
    RESOURCE_OR_BUDGET = "RESOURCE_OR_BUDGET"
    PERFORMANCE_ONLY = "PERFORMANCE_ONLY"


#: Los que sí informan sobre la escalera. El resto habla del organismo.
DEVELOPMENTAL_BLOCKERS = frozenset({
    BlockerClass.FAMILY_CANNOT_EXPRESS,
    BlockerClass.PRECURSOR_UNESTABLISHED,
    BlockerClass.NECESSITY_UNDETERMINED,
})


class ProbeStatus(StrEnum):
    OPEN = "OPEN"
    PARTIALLY_RESOLVED = "PARTIALLY_RESOLVED"
    CLOSED = "CLOSED"


class ProbeRefused(ValueError):
    """A reading the probe will not hold, and why."""


@dataclass(frozen=True)
class CeilingProbe:
    """One campaign's developmental reading, beside its scientific result."""

    probe_id: str
    target_capability: str
    #: El resultado científico de la campaña, tal cual. No se reescribe.
    source_result: str
    source_result_ref: str
    scope: Scope
    observed_blocker: str
    blocker_class: BlockerClass
    source_evidence_refs: tuple[str, ...] = ()
    candidate_missing_precursors: frozenset[str] = frozenset()
    candidate_lesions: frozenset[str] = frozenset()
    candidate_family_questions: tuple[str, ...] = ()
    non_claims: tuple[str, ...] = ()
    status: ProbeStatus = ProbeStatus.OPEN
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "candidate_missing_precursors",
                           frozenset(self.candidate_missing_precursors))
        object.__setattr__(self, "candidate_lesions", frozenset(self.candidate_lesions))

        for name in ("probe_id", "target_capability", "source_result",
                     "source_result_ref", "observed_blocker"):
            if not str(getattr(self, name)).strip():
                raise ProbeRefused(f"a ceiling probe requires a non-empty {name}")

        if self.blocker_class not in DEVELOPMENTAL_BLOCKERS:
            # La sexta negativa. Un negativo corriente habla del organismo, no
            # de la escalera, y ascenderlo gratis convertiría la etiqueta en un
            # sinónimo de decepción.
            raise ProbeRefused(
                f"{self.probe_id}: {self.blocker_class.value} is not developmental "
                f"evidence; an ordinary negative is not a ceiling")

        if not self.source_evidence_refs:
            raise ProbeRefused(
                f"{self.probe_id}: a blocker read from nothing is an opinion; "
                f"name the evidence that showed it")

        if not self.non_claims:
            raise ProbeRefused(
                f"{self.probe_id}: interpreting a blocker without saying what it "
                f"does NOT license is how an interpretation becomes a theory")

        if not (self.candidate_missing_precursors or self.candidate_lesions
                or self.candidate_family_questions):
            raise ProbeRefused(
                f"{self.probe_id}: a probe that proposes nothing is a note, not a probe")

    def emitted_claims(self) -> tuple[RelationClaim, ...]:
        """Everything a probe may put in the ledger, and it is all hypothesis.

        The third negative, enforced by construction rather than by review: a
        probe has no way to emit a causal class, so no reading of a failure can
        become a measured dependency by passing through here.
        """
        return tuple(
            RelationClaim(
                claim_id=f"{self.probe_id}-{precursor}",
                precursors=frozenset({precursor}), target=self.target_capability,
                semantics=RelationSemantics.UNKNOWN_RELATION,
                effect=EffectForm.UNRESOLVED,
                evidence=EvidenceClass.HYPOTHESIS,
                status=EpistemicStatus.UNRESOLVED,
                origin=HypothesisOrigin.DERIVED_FROM_NEGATIVE,
                basis=f"candidato derivado de {self.probe_id}: {self.observed_blocker}",
                non_claim="; ".join(self.non_claims))
            for precursor in sorted(self.candidate_missing_precursors))

    @property
    def content_identity(self) -> str:
        """Order-independent by construction.

        The seventh negative.  Candidates live in frozensets and questions are
        sorted here, so two probes written with the arguments in a different
        order are the same probe -- which is what the alphabetical failure of
        `EVSENS` taught: an ordering nobody chose must not carry meaning.
        """
        return content_hash({
            "probe_id": self.probe_id, "target": self.target_capability,
            "source_result": self.source_result, "blocker": self.observed_blocker,
            "blocker_class": self.blocker_class.value,
            "precursors": sorted(self.candidate_missing_precursors),
            "lesions": sorted(self.candidate_lesions),
            "questions": sorted(self.candidate_family_questions),
            "non_claims": sorted(self.non_claims),
        })

    def as_record(self) -> Mapping[str, Any]:
        return {
            "schema_version": self.schema_version, "probe_id": self.probe_id,
            "target_capability": self.target_capability,
            "scientific_result": self.source_result,
            "developmental_interpretation": "CEILING_PROBE",
            "source_result_ref": self.source_result_ref,
            "source_evidence_refs": list(self.source_evidence_refs),
            "scope": self.scope.as_record(),
            "observed_blocker": self.observed_blocker,
            "blocker_class": self.blocker_class.value,
            "candidate_missing_precursors": sorted(self.candidate_missing_precursors),
            "candidate_lesions": sorted(self.candidate_lesions),
            "candidate_family_questions": sorted(self.candidate_family_questions),
            "non_claims": sorted(self.non_claims), "status": self.status.value,
            "content_identity": self.content_identity,
        }


# ── Los dos techos reales ────────────────────────────────────────────────

def ceiling_probes_v1() -> tuple[CeilingProbe, ...]:
    from terrario.lab.relation_ledger import L18, RB  # noqa: F401  (RB para ámbitos futuros)

    return (
        CeilingProbe(
            probe_id="CP-18",
            target_capability="PREDSTATE",
            source_result="FAMILY_MISMATCH",
            source_result_ref="level18-predictive-state-01 · Ronda C · BUDGET SELECTION = NONE",
            scope=L18,
            observed_blocker=(
                "la familia realizada Z_{t+1}=F(Z_t,A_t) no expresa la sellada "
                "Z_{t+1}=F(Z_t,A_t,O_{t+1}): la observación entra en la clave de "
                "la ruta y nunca discrimina"),
            blocker_class=BlockerClass.FAMILY_CANNOT_EXPRESS,
            source_evidence_refs=(
                "prueba hermética: 0/400 diferencias variando observaciones, "
                "297/400 variando acciones",
                "predictive_state.py:168 · self._came_from = (self._here, command)",
                "H(C|2 pares obs-acción) resuelve el 91 % contra el 48 % de 6 acciones"),
            candidate_missing_precursors=frozenset({"EVSENS", "REPUPD", "HISTDIS"}),
            candidate_family_questions=(
                "¿puede una familia de actualización de estado con participación "
                "causal de la nueva observación realizar el constructo sellado?",),
            non_claims=(
                "no dice que el estado predictivo sea inalcanzable, sólo que esta "
                "familia no puede expresarlo",
                "no establece que EVSENS, REPUPD o HISTDIS sean requisitos: son "
                "candidatos derivados del bloqueo",
                "no ordena los tres candidatos entre sí")),

        CeilingProbe(
            probe_id="CP-15",
            target_capability="SELECTION",
            source_result="FROZEN_BY_DESIGN",
            source_result_ref="NIVEL_15_CONGELADO.md · condición de descongelación escrita",
            scope=Scope(world="banco de mensajes 16→4", organism="B+Q+H+M+ψ",
                        mechanism_family="dos tablas, emisión y lectura",
                        campaign="1.5 · sólo diseño, sin código",
                        condition="piloto de coaprendizaje no recuperable"),
            observed_blocker=(
                "a la memoria selectiva le falta la necesidad: la escasez la "
                "impone el experimentador, no la produce el organismo"),
            blocker_class=BlockerClass.PRECURSOR_UNESTABLISHED,
            source_evidence_refs=(
                "LEVEL15_05 · precondición acumulativa declarada y no adjudicada",
                "cierre preimplementación · α, exploración y clasificador UNKNOWN",
                "condición de descongelación: experiencia útil > capacidad de conservarla"),
            candidate_missing_precursors=frozenset(
                {"LIMRET", "FUTVAL", "TEMPCRED", "SELPOL", "COADAPT"}),
            candidate_lesions=frozenset({"PSI"}),
            non_claims=(
                "no dice que la selección aprendida sea inalcanzable",
                "no establece que los cinco candidatos sean requisitos",
                "no decide si ψ es requisito funcional o andamiaje: eso es la lesión",
                "no ordena los cinco candidatos entre sí")),
    )
