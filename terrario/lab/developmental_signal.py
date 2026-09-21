"""Two things a campaign's absence can mean, and they are not the same thing.

Level 1.8 ran.  It produced `FAMILY_MISMATCH`, and reading that as "a rung was
missing" is an interpretation of an execution.  Level 1.5 never ran: it was
frozen because attempting it was not yet justified.  Writing both as "reached a
ceiling" puts an experiment that happened and one that did not on the same
footing, and the second would quietly acquire the authority of the first.

    ScientificResult            !=  DevelopmentalSignal
    ObservedCeiling             !=  DesignHold

    1.8   execution -> FAMILY_MISMATCH   -> ObservedCeiling
    1.5   no execution -> FROZEN_BY_DESIGN -> DesignHold

Neither is an `EvidenceClass` and neither is an `EpistemicStatus`.  What
happened, how we know it, and what we read into it are three axes, and this
module only holds the third.

Both may emit hypotheses and nothing else.  That 1.8's family cannot express
the causal participation of the next observation justifies naming candidate
dimensions; it never licenses `EVSENS REQUIRED_FOR PREDSTATE`.  A hold is
weaker still: it says an attempt is not yet justified, which is a statement
about us rather than about the organism.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Mapping

from terrario.lab.persistence.canonical import content_hash
from terrario.lab.relation_ledger import (
    EffectForm, EpistemicStatus, EvidenceClass, HypothesisOrigin, RelationClaim,
    RelationSemantics, Scope,
)

SCHEMA_VERSION = "terrario.lab.developmental-signal/v1"


class SignalOrigin(StrEnum):
    OBSERVED_EXECUTION = "OBSERVED_EXECUTION"
    DESIGN_DECISION = "DESIGN_DECISION"


class BlockerClass(StrEnum):
    """What kind of wall, when there was a wall.

    `PERFORMANCE_ONLY` and `RESOURCE_OR_BUDGET` exist to be refused: "the agent
    did not learn" and "it ran out of budget" are results about the run, not
    about the ladder, and admitting them would make every disappointing
    campaign a developmental finding.
    """

    FAMILY_CANNOT_EXPRESS = "FAMILY_CANNOT_EXPRESS"
    PRECURSOR_UNESTABLISHED = "PRECURSOR_UNESTABLISHED"
    NECESSITY_UNDETERMINED = "NECESSITY_UNDETERMINED"
    RESOURCE_OR_BUDGET = "RESOURCE_OR_BUDGET"
    PERFORMANCE_ONLY = "PERFORMANCE_ONLY"


DEVELOPMENTAL_BLOCKERS = frozenset({
    BlockerClass.FAMILY_CANNOT_EXPRESS,
    BlockerClass.PRECURSOR_UNESTABLISHED,
    BlockerClass.NECESSITY_UNDETERMINED,
})

#: Marcas que NO son desenlaces de ejecución. Un techo observado que las cite
#: está diciendo que observó algo que nunca corrió.
NON_EXECUTION_MARKERS = frozenset({
    "FROZEN_BY_DESIGN", "NOT_ATTEMPTED", "DESIGN_ONLY", "DEFERRED", "FROZEN",
})

#: Y al revés: desenlaces de campaña que no pueden hacerse pasar por decisión.
EXECUTION_OUTCOMES = frozenset({
    "FAMILY_MISMATCH", "SCIENTIFIC_NEGATIVE", "POSITIVE", "VERIFIED",
    "NEGATIVE", "INVALID", "BUDGET SELECTION = NONE",
})


#: Lo que basta para afirmar que una familia no puede realizar un constructo.
#: Tres caminos, no uno: si se puede demostrar formalmente por adelantado que
#: `F(Z,A)` no distingue dos casos que sólo difieren en `O_{t+1}`, gastar una
#: campaña para ganarse el derecho a preguntar por otra familia seria una
#: ceremonia, no un metodo.
ADMISSIBLE_FAMILY_EVIDENCE = frozenset({
    EvidenceClass.VERIFIED_FORMAL, EvidenceClass.VERIFIED_CODE,
    EvidenceClass.MEASURED_INTERVENTION, EvidenceClass.MEASURED_FACTORIAL,
    EvidenceClass.MEASURED_LESION,
})


class SignalRefused(ValueError):
    """A reading the model will not hold, and why."""


@dataclass(frozen=True)
class FamilyContradiction:
    """Evidence that a mechanism family cannot realise the construct.

    Independent of how the signal arose: what licenses asking about another
    family is the contradiction, not the fact that something was run.  A formal
    proof that `F(Z,A)` cannot separate two cases differing only in the next
    observation settles it without spending a campaign to earn the right to ask.
    """

    statement: str
    evidence: EvidenceClass
    evidence_ref: str

    def __post_init__(self) -> None:
        if not str(self.statement).strip() or not str(self.evidence_ref).strip():
            raise SignalRefused("a family contradiction needs a statement and a reference")
        if self.evidence not in ADMISSIBLE_FAMILY_EVIDENCE:
            raise SignalRefused(
                f"{self.evidence.value} cannot establish that a family fails to "
                f"express a construct")

    def as_record(self) -> Mapping[str, Any]:
        return {"statement": self.statement, "evidence_class": self.evidence.value,
                "evidence_ref": self.evidence_ref}


class ProbeStatus(StrEnum):
    OPEN = "OPEN"
    PARTIALLY_RESOLVED = "PARTIALLY_RESOLVED"
    CLOSED = "CLOSED"


def _shared_checks(signal: Any, campos: tuple[str, ...]) -> None:
    """What both kinds owe, regardless of where they came from."""
    for name in campos:
        if not str(getattr(signal, name)).strip():
            raise SignalRefused(f"{type(signal).__name__} requires a non-empty {name}")
    if not signal.non_claims:
        raise SignalRefused(
            f"{signal.signal_id}: interpreting a gap without saying what it does "
            f"NOT license is how an interpretation becomes a theory")
    if not (signal.candidate_missing_precursors or signal.candidate_lesions
            or signal.candidate_family_questions):
        raise SignalRefused(
            f"{signal.signal_id}: a signal that proposes nothing is a note")


def _emit(signal: Any) -> tuple[RelationClaim, ...]:
    """Everything either kind may put in the ledger, and it is all hypothesis."""
    return tuple(
        RelationClaim(
            claim_id=f"{signal.signal_id}-{precursor}",
            precursors=frozenset({precursor}), target=signal.target_capability,
            semantics=RelationSemantics.UNKNOWN_RELATION,
            effect=EffectForm.UNRESOLVED,
            evidence=EvidenceClass.HYPOTHESIS,
            status=EpistemicStatus.UNRESOLVED,
            origin=HypothesisOrigin.DERIVED_FROM_NEGATIVE,
            basis=f"candidato derivado de {signal.signal_id}: {signal.rationale}",
            non_claim="; ".join(signal.non_claims))
        for precursor in sorted(signal.candidate_missing_precursors))


def _identity(signal: Any, extra: Mapping[str, Any]) -> str:
    """Order-independent: candidates live in frozensets and questions are sorted."""
    return content_hash({
        "signal_id": signal.signal_id, "target": signal.target_capability,
        "origin": signal.origin.value, "rationale": signal.rationale,
        "precursors": sorted(signal.candidate_missing_precursors),
        "lesions": sorted(signal.candidate_lesions),
        "questions": sorted(signal.candidate_family_questions),
        "non_claims": sorted(signal.non_claims), **extra})


@dataclass(frozen=True)
class ObservedCeiling:
    """A wall a campaign actually hit, read for what it says about the ladder."""

    signal_id: str
    target_capability: str
    #: El desenlace científico, tal cual. No se reescribe ni se sustituye.
    source_result: str
    source_result_ref: str
    scope: Scope
    rationale: str
    blocker_class: BlockerClass
    source_evidence_refs: tuple[str, ...] = ()
    candidate_missing_precursors: frozenset[str] = frozenset()
    candidate_lesions: frozenset[str] = frozenset()
    candidate_family_questions: tuple[str, ...] = ()
    non_claims: tuple[str, ...] = ()
    #: Presente solo cuando algo admisible contradice a la familia. Un
    #: paquete de preguntas sobre familias no es, por si solo, motivo
    #: para preguntar por otra.
    family_contradiction: "FamilyContradiction | None" = None
    status: ProbeStatus = ProbeStatus.OPEN
    origin: SignalOrigin = SignalOrigin.OBSERVED_EXECUTION
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "candidate_missing_precursors",
                           frozenset(self.candidate_missing_precursors))
        object.__setattr__(self, "candidate_lesions", frozenset(self.candidate_lesions))
        _shared_checks(self, ("signal_id", "target_capability", "source_result",
                              "source_result_ref", "rationale"))

        if self.origin is not SignalOrigin.OBSERVED_EXECUTION:
            raise SignalRefused(
                f"{self.signal_id}: an observed ceiling did not come from a decision")
        if self.source_result.strip().upper() in NON_EXECUTION_MARKERS:
            # El contrato 2. Un techo observado que cita una congelación está
            # diciendo que observó algo que nunca corrió.
            raise SignalRefused(
                f"{self.signal_id}: {self.source_result} is not an execution outcome; "
                f"a capability that was never attempted reached no ceiling")
        if self.blocker_class not in DEVELOPMENTAL_BLOCKERS:
            raise SignalRefused(
                f"{self.signal_id}: {self.blocker_class.value} is not developmental "
                f"evidence; an ordinary negative is not a ceiling")
        if not self.source_evidence_refs:
            raise SignalRefused(
                f"{self.signal_id}: a blocker read from nothing is an opinion; "
                f"name the evidence that showed it")

    def emitted_claims(self) -> tuple[RelationClaim, ...]:
        return _emit(self)

    @property
    def content_identity(self) -> str:
        return _identity(self, {"kind": "ObservedCeiling",
                                "source_result": self.source_result,
                                "blocker_class": self.blocker_class.value})

    def as_record(self) -> Mapping[str, Any]:
        return {
            "schema_version": self.schema_version, "signal_id": self.signal_id,
            "signal_kind": "OBSERVED_CEILING", "origin": self.origin.value,
            "target_capability": self.target_capability,
            "scientific_result": self.source_result,
            "source_result_ref": self.source_result_ref,
            "source_evidence_refs": list(self.source_evidence_refs),
            "scope": self.scope.as_record(), "rationale": self.rationale,
            "blocker_class": self.blocker_class.value,
            "candidate_missing_precursors": sorted(self.candidate_missing_precursors),
            "candidate_lesions": sorted(self.candidate_lesions),
            "candidate_family_questions": sorted(self.candidate_family_questions),
            "non_claims": sorted(self.non_claims), "status": self.status.value,
            "content_identity": self.content_identity}


@dataclass(frozen=True)
class DesignHold:
    """A capability deliberately not attempted, and why it was not justified.

    It says something about us, not about the organism.  Nothing here may be
    read as the organism having tried and failed -- there was no attempt.
    """

    signal_id: str
    target_capability: str
    #: La decisión, no un desenlace. `FROZEN_BY_DESIGN` y parientes.
    source_decision: str
    decision_ref: str
    scope: Scope
    rationale: str
    unresolved_precursors: frozenset[str] = frozenset()
    candidate_lesions: frozenset[str] = frozenset()
    candidate_family_questions: tuple[str, ...] = ()
    non_claims: tuple[str, ...] = ()
    #: Presente solo cuando algo admisible contradice a la familia. Un
    #: paquete de preguntas sobre familias no es, por si solo, motivo
    #: para preguntar por otra.
    family_contradiction: "FamilyContradiction | None" = None
    status: ProbeStatus = ProbeStatus.OPEN
    origin: SignalOrigin = SignalOrigin.DESIGN_DECISION
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "unresolved_precursors",
                           frozenset(self.unresolved_precursors))
        object.__setattr__(self, "candidate_lesions", frozenset(self.candidate_lesions))
        _shared_checks(self, ("signal_id", "target_capability", "source_decision",
                              "decision_ref", "rationale"))

        if self.origin is not SignalOrigin.DESIGN_DECISION:
            raise SignalRefused(
                f"{self.signal_id}: a hold is a decision, not an observation")
        if self.source_decision.strip().upper() in EXECUTION_OUTCOMES:
            # El contrato 4, y el simétrico del 2: un desenlace de campaña
            # disfrazado de decisión borraría que el experimento sí ocurrió.
            raise SignalRefused(
                f"{self.signal_id}: {self.source_decision} is a campaign outcome, "
                f"not a design decision; a hold cannot be built from a result")

    #: Alias para que ambos tipos respondan a la misma pregunta sin que el
    #: censo tenga que saber cuál es cuál.
    @property
    def candidate_missing_precursors(self) -> frozenset[str]:
        return self.unresolved_precursors

    def emitted_claims(self) -> tuple[RelationClaim, ...]:
        return _emit(self)

    @property
    def content_identity(self) -> str:
        return _identity(self, {"kind": "DesignHold",
                                "source_decision": self.source_decision})

    def as_record(self) -> Mapping[str, Any]:
        return {
            "schema_version": self.schema_version, "signal_id": self.signal_id,
            "signal_kind": "DESIGN_HOLD", "origin": self.origin.value,
            "target_capability": self.target_capability,
            "source_decision": self.source_decision, "decision_ref": self.decision_ref,
            "scope": self.scope.as_record(), "rationale": self.rationale,
            "unresolved_precursors": sorted(self.unresolved_precursors),
            "candidate_lesions": sorted(self.candidate_lesions),
            "candidate_family_questions": sorted(self.candidate_family_questions),
            "non_claims": sorted(self.non_claims), "status": self.status.value,
            "content_identity": self.content_identity}


def observed_ceilings(signals) -> tuple[ObservedCeiling, ...]:
    """The census of walls actually hit.  Holds are not walls and are excluded."""
    return tuple(s for s in signals if isinstance(s, ObservedCeiling))


def design_holds(signals) -> tuple[DesignHold, ...]:
    return tuple(s for s in signals if isinstance(s, DesignHold))


# ── Las dos señales reales, ahora de clase distinta ──────────────────────

def developmental_signals_v1() -> tuple[Any, ...]:
    from terrario.lab.relation_ledger import L18

    ceiling_18 = ObservedCeiling(
        signal_id="OC-18",
        target_capability="PREDSTATE",
        source_result="FAMILY_MISMATCH",
        source_result_ref="level18-predictive-state-01 · Ronda C · BUDGET SELECTION = NONE",
        scope=L18,
        rationale=(
            "la familia realizada Z_{t+1}=F(Z_t,A_t) no expresa la sellada "
            "Z_{t+1}=F(Z_t,A_t,O_{t+1}): la observación entra en la clave de la "
            "ruta y nunca discrimina"),
        blocker_class=BlockerClass.FAMILY_CANNOT_EXPRESS,
        family_contradiction=FamilyContradiction(
            statement="F(Z_t,A_t) no puede separar dos historias que sólo "
                      "difieren en O_{t+1}",
            evidence=EvidenceClass.MEASURED_INTERVENTION,
            evidence_ref="level18 · 0/400 variando observaciones"),
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
            "no establece que EVSENS, REPUPD o HISTDIS sean requisitos",
            "no ordena los tres candidatos entre sí"))

    hold_15 = DesignHold(
        signal_id="DH-15",
        target_capability="SELECTION",
        source_decision="FROZEN_BY_DESIGN",
        decision_ref="NIVEL_15_CONGELADO.md · decisión de Wis tras el mapa causal v3",
        scope=Scope(world="banco de mensajes 16→4", organism="B+Q+H+M+ψ",
                    mechanism_family="dos tablas, emisión y lectura",
                    campaign="1.5 · sólo diseño, sin código ni rama",
                    condition="la capacidad nunca se intentó"),
        rationale=(
            "a la memoria selectiva le falta la necesidad: la escasez la impone "
            "el experimentador, no la produce el organismo, así que intentar la "
            "adquisición todavía no está justificado"),
        unresolved_precursors=frozenset(
            {"LIMRET", "FUTVAL", "TEMPCRED", "SELPOL", "COADAPT"}),
        candidate_lesions=frozenset({"PSI"}),
        non_claims=(
            "NO dice que el organismo intentara adquirirla y encontrara un techo: "
            "no hubo ejecución",
            "no dice que la selección aprendida sea inalcanzable",
            "no establece que los cinco precursores sean requisitos",
            "no decide si ψ es requisito funcional o andamiaje: eso es la lesión",
            "no ordena los cinco entre sí"))

    return (ceiling_18, hold_15)
