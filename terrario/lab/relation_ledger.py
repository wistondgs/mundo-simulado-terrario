"""A developmental relation, with the four things about it that vary freely.

The first version of this model had two axes and they were the wrong two.
`CONTRADICTED` sat beside `MEASURED`, which puts how-we-know and what-we-now-
think on one dimension: a factorial that refutes a relation is measured *and*
contradicted, and there was no way to write that down.  So there are four here,
and they move independently:

    semantics     REQUIRES, FACILITATES, SYNERGIZES_WITH...  what is claimed
    effect        NECESSARY, SUFFICIENT, SUBSTITUTABLE...    what shape it has
    evidence      MEASURED_FACTORIAL, VERIFIED_CODE...       how it is known
    status        SUPPORTED, CONTRADICTED, SUPERSEDED        what we now hold

Three refusals live in the constructor rather than in a style guide, because a
textual prohibition is the failure mode this whole programme was built out of.

**Scope is one of them.**  The only measured edge the project has -- psi's
functional contribution depending on M -- was measured in one world, with one
organism, under one mechanism family.  Written without that, a local
interaction becomes a universal law the first time somebody reads it quickly,
and nothing would complain.

**Hypothesis provenance is another.**  A candidate proposed by a person after
reading the corpus and one emitted by a model are the same row two months
later.  The rule that no model decides causal necessity is unauditable unless
the ledger records who proposed what.

**And a superseded claim must name its successor.**  Level 1.5 went through
four supersessions and reconciling which one governed had to be done by hand.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Mapping

SCHEMA_VERSION = "terrario.lab.relation-ledger/v1"


class RelationSemantics(StrEnum):
    """What is being claimed.  Read from the dependent side to the depended-on."""

    REQUIRES = "REQUIRES"
    FACILITATES = "FACILITATES"
    SUFFICIENT_SET = "SUFFICIENT_SET"
    ALTERNATIVE_TO = "ALTERNATIVE_TO"
    SUBSTITUTABLE_WITH = "SUBSTITUTABLE_WITH"
    INHIBITS = "INHIBITS"
    SYNERGIZES_WITH = "SYNERGIZES_WITH"
    IMPLEMENTS = "IMPLEMENTS"
    REALIZES = "REALIZES"
    PARTICIPATES_IN = "PARTICIPATES_IN"
    CONTRADICTS = "CONTRADICTS"
    UNKNOWN_RELATION = "UNKNOWN_RELATION"


class EffectForm(StrEnum):
    """The shape of the effect, which the semantics alone does not fix."""

    NECESSARY = "NECESSARY"
    CONDITIONAL_NECESSITY = "CONDITIONAL_NECESSITY"
    SUFFICIENT = "SUFFICIENT"
    FACILITATING = "FACILITATING"
    SYNERGISTIC = "SYNERGISTIC"
    SUBSTITUTABLE = "SUBSTITUTABLE"
    INHIBITORY = "INHIBITORY"
    UNRESOLVED = "UNRESOLVED"


class EvidenceClass(StrEnum):
    """How it is known.  The distinction the whole programme rests on.

    `REPLICATED_DETERMINISTIC` is here because the project already produces it
    and had nowhere to put it: level 1.6's reconciliation replayed against the
    committed table cell by cell at 5e-5 with zero differences, when the
    original artefacts no longer existed.  That is neither a measurement --
    there is no original artefact -- nor a document, because a check was run.
    """

    MEASURED_FACTORIAL = "MEASURED_FACTORIAL"
    MEASURED_LESION = "MEASURED_LESION"
    MEASURED_INTERVENTION = "MEASURED_INTERVENTION"
    REPLICATED_DETERMINISTIC = "REPLICATED_DETERMINISTIC"
    VERIFIED_CODE = "VERIFIED_CODE"
    VERIFIED_FORMAL = "VERIFIED_FORMAL"
    SUPPORTED_CORPUS = "SUPPORTED_CORPUS"
    DECLARED_DOCUMENT = "DECLARED_DOCUMENT"
    HYPOTHESIS = "HYPOTHESIS"
    UNKNOWN = "UNKNOWN"


#: Classes that assert a causal fact and therefore cannot be scopeless.
CAUSAL_CLASSES = frozenset({
    EvidenceClass.MEASURED_FACTORIAL, EvidenceClass.MEASURED_LESION,
    EvidenceClass.MEASURED_INTERVENTION,
})

#: Classes that settle a claim by running something, as opposed to by reading.
EXECUTED_CLASSES = CAUSAL_CLASSES | {EvidenceClass.REPLICATED_DETERMINISTIC}


class EpistemicStatus(StrEnum):
    SUPPORTED = "SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    UNRESOLVED = "UNRESOLVED"
    SUPERSEDED = "SUPERSEDED"


class HypothesisOrigin(StrEnum):
    """Who proposed it, so that "no model decides causal necessity" is auditable."""

    HUMAN_PROPOSED = "HUMAN_PROPOSED"
    CORPUS_SOURCED = "CORPUS_SOURCED"
    GENERATED = "GENERATED"
    DERIVED_FROM_NEGATIVE = "DERIVED_FROM_NEGATIVE"
    DERIVED_FROM_TASK_CONTRACT = "DERIVED_FROM_TASK_CONTRACT"
    NOT_A_HYPOTHESIS = "NOT_A_HYPOTHESIS"


@dataclass(frozen=True)
class Scope:
    """Where a relation was found to hold.  Absent scope is not universality."""

    world: str
    organism: str
    mechanism_family: str
    campaign: str
    resource_budget: str = ""
    condition: str = ""

    def __post_init__(self) -> None:
        for name in ("world", "organism", "mechanism_family", "campaign"):
            if not str(getattr(self, name)).strip():
                raise ValueError(f"scope requires a non-empty {name}")

    def as_record(self) -> Mapping[str, Any]:
        return {"world": self.world, "organism": self.organism,
                "mechanism_family": self.mechanism_family, "campaign": self.campaign,
                "resource_budget": self.resource_budget, "condition": self.condition}


class LedgerRefused(ValueError):
    """A row the ledger will not hold, and why."""


@dataclass(frozen=True)
class RelationClaim:
    """One row: `target <--semantics-- precursors`, with all four axes.

    The direction is stated rather than implied.  `M REQUIRES SELECTION` read
    as "M requires SELECTION" and meant the reverse, and an edge whose meaning
    depends on how the reader parses it is worse than no edge.
    """

    precursors: frozenset[str]
    target: str
    semantics: RelationSemantics
    effect: EffectForm
    evidence: EvidenceClass
    status: EpistemicStatus
    basis: str
    scope: Scope | None = None
    evidence_ref: str | None = None
    origin: HypothesisOrigin = HypothesisOrigin.NOT_A_HYPOTHESIS
    superseded_by: str | None = None
    non_claim: str = ""
    claim_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "precursors", frozenset(self.precursors))
        if not self.precursors or not self.target:
            raise LedgerRefused("a claim needs precursors and a target")
        if self.target in self.precursors:
            raise LedgerRefused(f"{self.target} cannot be its own precursor")
        if not str(self.basis).strip():
            raise LedgerRefused("a claim without a stated basis is a guess wearing a type")

        if self.evidence in EXECUTED_CLASSES and not self.evidence_ref:
            raise LedgerRefused(
                f"{self.label()} claims {self.evidence.value} with no evidence_ref; "
                f"that is the claim this ledger exists to refuse")
        if self.evidence in CAUSAL_CLASSES and self.scope is None:
            # M2. Sin esto, la interacción local de un solo mundo se convierte
            # en ley universal la primera vez que alguien la lea deprisa.
            raise LedgerRefused(
                f"{self.label()} asserts a causal fact with no scope; a relation "
                f"measured in one world is not a law")
        if self.evidence is EvidenceClass.HYPOTHESIS \
                and self.origin is HypothesisOrigin.NOT_A_HYPOTHESIS:
            raise LedgerRefused(
                f"{self.label()} is a hypothesis with no stated origin; without it "
                f"nobody can audit how many of these a model proposed")
        if self.status is EpistemicStatus.SUPERSEDED and not self.superseded_by:
            raise LedgerRefused(
                f"{self.label()} is SUPERSEDED and does not name its successor")

    def label(self) -> str:
        """Direction stated, never implied."""
        lado = " + ".join(sorted(self.precursors))
        return f"{self.target} --{self.semantics.value}--> {lado}"

    @property
    def is_measured(self) -> bool:
        return self.evidence in CAUSAL_CLASSES

    @property
    def is_read(self) -> bool:
        return self.evidence in {EvidenceClass.VERIFIED_CODE,
                                 EvidenceClass.VERIFIED_FORMAL,
                                 EvidenceClass.REPLICATED_DETERMINISTIC}

    def as_record(self) -> Mapping[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION, "claim_id": self.claim_id,
            "target": self.target, "precursors": sorted(self.precursors),
            "semantics": self.semantics.value, "effect": self.effect.value,
            "evidence_class": self.evidence.value, "status": self.status.value,
            "scope": self.scope.as_record() if self.scope else None,
            "evidence_ref": self.evidence_ref, "origin": self.origin.value,
            "superseded_by": self.superseded_by, "non_claim": self.non_claim,
            "basis": self.basis, "label": self.label(),
        }


#: What each kind of assertion needs before it counts as settled.  U4: the
#: bar is per claim type, not one global "was anything measured".
EVIDENCE_POLICY: dict[EffectForm, frozenset[EvidenceClass]] = {
    EffectForm.NECESSARY: CAUSAL_CLASSES,
    EffectForm.CONDITIONAL_NECESSITY: CAUSAL_CLASSES,
    EffectForm.SUFFICIENT: CAUSAL_CLASSES,
    EffectForm.SYNERGISTIC: frozenset({EvidenceClass.MEASURED_FACTORIAL}),
    EffectForm.SUBSTITUTABLE: CAUSAL_CLASSES,
    EffectForm.INHIBITORY: CAUSAL_CLASSES,
    # Presencia estructural: leer el código basta, y decir lo contrario sería
    # exigir un experimento para comprobar que una rama existe.
    EffectForm.FACILITATING: frozenset({
        EvidenceClass.VERIFIED_CODE, EvidenceClass.VERIFIED_FORMAL,
        *CAUSAL_CLASSES}),
    EffectForm.UNRESOLVED: frozenset(),
}


def meets_policy(claim: RelationClaim) -> bool:
    """Whether this claim's evidence clears the bar for what it asserts."""
    if claim.status is not EpistemicStatus.SUPPORTED:
        return False
    admisibles = EVIDENCE_POLICY.get(claim.effect, frozenset())
    return claim.evidence in admisibles


# ── El inventario tipado ─────────────────────────────────────────────────

RB = Scope(world="d0/64 escenas del banco de ψ", organism="B+Q+H+M+ψ",
           mechanism_family="binder conjuntivo congelado + memoria de un paso",
           campaign="organism-remembered-binding-01", resource_budget="8 semillas",
           condition="factorial 2×2 sobre uso conjunto")

L18 = Scope(world="5 mundos del banco de 1.8", organism="1.8 · C17 + learner",
            mechanism_family="estado predictivo por partición de historia",
            campaign="level18-predictive-state-01",
            resource_budget="60.000 pasos", condition="ingeniería inversa v1")


def relation_ledger_v1() -> tuple[RelationClaim, ...]:
    """Sólo relaciones que YA existen en código, campañas, documentos o matemática.

    Ninguna se promueve por lectura: una dependencia leída entra como
    `VERIFIED_CODE`, no como necesidad causal, y el analizador la trata como
    lo que es.
    """
    filas: list[RelationClaim] = []

    # --- la única medida, y su alcance --------------------------------------
    filas.append(RelationClaim(
        claim_id="REL-001", precursors=frozenset({"M"}), target="PSI_USEFUL",
        semantics=RelationSemantics.REQUIRES, effect=EffectForm.NECESSARY,
        evidence=EvidenceClass.MEASURED_FACTORIAL,
        status=EpistemicStatus.SUPPORTED, scope=RB,
        evidence_ref="organism-remembered-binding-01 · gate RB-7 · mejora sólo ψ = 0.000000",
        basis="factorial 2×2: ψ sola no mejora; interacción +0.006515",
        non_claim="no dice que M sea requisito developmental universal de ψ, "
                  "sólo que en este contexto su contribución funcional depende de M"))

    filas.append(RelationClaim(
        claim_id="REL-002", precursors=frozenset({"H", "M"}), target="PSI_USEFUL",
        semantics=RelationSemantics.SYNERGIZES_WITH, effect=EffectForm.SYNERGISTIC,
        evidence=EvidenceClass.MEASURED_FACTORIAL,
        status=EpistemicStatus.SUPPORTED, scope=RB,
        evidence_ref="organism-remembered-binding-01 · gates RB-5 y RB-6",
        basis="interacción superaditiva medida, 0.006515 contra 0.006534 sellado",
        non_claim="superaditividad en este banco; no generaliza a otros mundos"))

    # --- lo que 1.8 REFUTÓ: medido y contradicho, que son ejes distintos ----
    filas.append(RelationClaim(
        claim_id="REL-003", precursors=frozenset({"M"}), target="PREDSTATE",
        semantics=RelationSemantics.SUFFICIENT_SET, effect=EffectForm.SUFFICIENT,
        evidence=EvidenceClass.MEASURED_INTERVENTION,
        status=EpistemicStatus.CONTRADICTED, scope=L18,
        evidence_ref="level18-predictive-state-01 · prueba hermética 0/400 vs 297/400",
        basis="la familia realizada F(Z,A) no expresa la sellada F(Z,A,O)",
        non_claim="no dice que el estado predictivo sea inalcanzable, sino que "
                  "esta familia no puede expresarlo"))

    # --- leídas del código: ciertas, y no causales --------------------------
    for cid, pre, tgt, why in (
        ("REL-004", "TEMPREG", "HISTDIS",
         "1.7 hereda el MECANISMO de 1.6 instanciado y congelado, no una tabla forastera"),
        ("REL-005", "M", "SELECTION",
         "el canal temporal ES una retención; M es necesaria por construcción del constructo"),
        ("REL-006", "ACTCON", "PREDSTATE",
         "1.8 hereda C_17 como prior; C17-LESION con prior plano pierde 0,79 nats"),
    ):
        filas.append(RelationClaim(
            claim_id=cid, precursors=frozenset({pre}), target=tgt,
            semantics=RelationSemantics.REQUIRES, effect=EffectForm.FACILITATING,
            evidence=EvidenceClass.VERIFIED_CODE, status=EpistemicStatus.SUPPORTED,
            basis=why,
            non_claim="presencia estructural leída en código; no dice que la "
                      "capacidad sea inadquirible sin el precursor"))

    # --- hipótesis, con quién las propuso -----------------------------------
    for cid, pre in (("REL-007", "LIMRET"), ("REL-008", "FUTVAL"),
                     ("REL-009", "TEMPCRED"), ("REL-010", "SELPOL"),
                     ("REL-011", "COADAPT")):
        filas.append(RelationClaim(
            claim_id=cid, precursors=frozenset({pre}), target="SELECTION",
            semantics=RelationSemantics.UNKNOWN_RELATION, effect=EffectForm.UNRESOLVED,
            evidence=EvidenceClass.HYPOTHESIS, status=EpistemicStatus.UNRESOLVED,
            origin=HypothesisOrigin.HUMAN_PROPOSED,
            basis="descomposición del objetivo por Wis; nadie movió este precursor "
                  "y miró 1.5"))

    filas.append(RelationClaim(
        claim_id="REL-012", precursors=frozenset({"PSI"}), target="SELECTION",
        semantics=RelationSemantics.UNKNOWN_RELATION, effect=EffectForm.UNRESOLVED,
        evidence=EvidenceClass.HYPOTHESIS, status=EpistemicStatus.UNRESOLVED,
        origin=HypothesisOrigin.HUMAN_PROPOSED,
        basis="X=(G,P) con |X|=16 es el espacio del binding; requisito funcional "
              "o andamiaje, sin decidir"))

    for cid, pre in (("REL-013", "EVSENS"), ("REL-014", "REPUPD"),
                     ("REL-015", "HISTDIS")):
        filas.append(RelationClaim(
            claim_id=cid, precursors=frozenset({pre}), target="PREDSTATE",
            semantics=RelationSemantics.UNKNOWN_RELATION, effect=EffectForm.UNRESOLVED,
            evidence=EvidenceClass.HYPOTHESIS, status=EpistemicStatus.UNRESOLVED,
            origin=HypothesisOrigin.DERIVED_FROM_NEGATIVE,
            basis="escalera derivada del FAMILY_MISMATCH: la firma requerida "
                  "necesita que O_{t+1} entre en el estado"))

    return tuple(filas)
