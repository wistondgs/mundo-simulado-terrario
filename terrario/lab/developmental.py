"""What a capability needs before it can be acquired, and what to measure next.

Terrario can isolate small acquisitions and has done it nine times.  Twice it
tried to reach a capability that needed an organisation the organism did not
have, and both times the procedure broke in the same way: 1.5 froze as design,
1.8 spent weeks calibrating a mechanism family that could not express its own
sealed construct.  Neither was a bad experiment.  Both were the same missing
step -- nobody had asked what has to be true before this is learnable.

So this module holds two graphs and refuses to let them be one:

    GENEALOGY       which campaign produced which capability, in time
    DEVELOPMENT     which capability makes which other one acquirable

1.0 through 1.8 is a genealogy.  Reading it as a development is precisely the
error: level 1.6 deliberately inherited nothing cognitive from 1.4, so
chronology there is not dependency.

Every developmental edge carries how we know it, and the distinction that the
whole programme rests on is between an edge that was *measured* and one that
was *read*.  `psi REQUIRES M` is measured: the remembered-binding factorial
reports psi's solo improvement as exactly 0.000000 and gates it.  `CURIO
REQUIRES WM` is read: without prediction there is no prediction error, which is
true, structural, and says nothing about whether the organism could acquire
curiosity without a world model.

The next question is derived, never authored.  A lookup table of good questions
would pass these tests and teach us nothing: the rule is that the informative
experiment is the unresolved precursor closest to what is already demonstrated,
because that is the one testable while holding everything else fixed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping

SCHEMA_VERSION = "terrario.lab.developmental/v1"


class CapabilityState(StrEnum):
    """Genealogical state.  A frozen target and a negative are not failures."""

    DEMONSTRATED = "DEMONSTRATED"
    FROZEN_TARGET = "FROZEN_TARGET"
    NEGATIVE = "NEGATIVE"
    CANDIDATE = "CANDIDATE"


class DependencyKind(StrEnum):
    REQUIRES = "REQUIRES"
    FACILITATES = "FACILITATES"
    SUFFICIENT_SET = "SUFFICIENT_SET"
    ALTERNATIVE = "ALTERNATIVE"
    INHIBITS = "INHIBITS"
    UNKNOWN = "UNKNOWN"


class EvidenceState(StrEnum):
    """How the edge is known, and it is the axis that matters.

    MEASURED means an experiment moved the precursor and watched the target.
    READ means the dependency is visible in code or mathematics without anyone
    having tested whether the target is acquirable without it.  CANDIDATE means
    somebody proposed it.  A target whose precursors are all CANDIDATE is a
    target nobody has earned the right to attempt.
    """

    MEASURED = "MEASURED"
    READ = "READ"
    CANDIDATE = "CANDIDATE"
    CONTRADICTED = "CONTRADICTED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Capability:
    capability_id: str
    label: str
    state: CapabilityState
    #: Which campaign produced it.  Genealogy, never read as dependency.
    origin: str = ""
    note: str = ""


@dataclass(frozen=True)
class DevelopmentalEdge:
    """`precursors --kind--> target`, with how we know and what would settle it."""

    precursors: frozenset[str]
    target: str
    kind: DependencyKind
    evidence: EvidenceState
    basis: str
    #: The campaign that measured it, when one did.  Absent is informative.
    experiment: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "precursors", frozenset(self.precursors))
        if not self.precursors or not self.target:
            raise ValueError("an edge needs precursors and a target")
        if not str(self.basis).strip():
            raise ValueError("an edge without a stated basis is a guess wearing a type")
        if self.evidence is EvidenceState.MEASURED and not self.experiment:
            raise ValueError(
                f"{sorted(self.precursors)}->{self.target} claims MEASURED with no "
                f"experiment; that is the claim this module exists to refuse")


#: Relaciones donde el OBJETIVO depende de los precursores, no al revés. La
#: distinción no es cosmética: `REQUIRES` se lee del que depende hacia aquello
#: de lo que depende, y `SYNERGIZES_WITH` no tiene esa asimetría.
_TARGET_DEPENDS_ON = frozenset({
    DependencyKind.REQUIRES, DependencyKind.FACILITATES,
    DependencyKind.SUFFICIENT_SET, DependencyKind.UNKNOWN,
})


@dataclass(frozen=True)
class GapReport:
    target: str
    known: tuple[str, ...]
    unknown: tuple[str, ...]
    contradicted: tuple[str, ...]
    next_question: str | None
    next_precursor: str | None
    premature: bool
    reason: str
    #: Todos los candidatos empatados en primer lugar. Que sean varios es
    #: información, no ruido: significa que el orden no está determinado por
    #: la evidencia y que la elección es del humano, no del analizador.
    tied_candidates: tuple[str, ...] = ()
    #: Precursores YA demostrados cuya necesidad nadie comprobó. No piden un
    #: experimento de adquisición --ya existen-- sino una lesión. Es la forma
    #: computable de «¿es requisito o es andamiaje?».
    lesion_candidates: tuple[str, ...] = ()
    schema_version: str = SCHEMA_VERSION

    def as_record(self) -> Mapping[str, Any]:
        return {"schema_version": self.schema_version, "target": self.target,
                "known": list(self.known), "unknown": list(self.unknown),
                "contradicted": list(self.contradicted),
                "next_question": self.next_question,
                "next_precursor": self.next_precursor,
                "tied_candidates": list(self.tied_candidates),
                "lesion_candidates": list(self.lesion_candidates),
                "premature": self.premature, "reason": self.reason}


@dataclass
class DevelopmentalGraph:
    capabilities: dict[str, Capability] = field(default_factory=dict)
    edges: list[DevelopmentalEdge] = field(default_factory=list)

    def add(self, capability: Capability) -> Capability:
        if capability.capability_id in self.capabilities:
            raise ValueError(f"duplicate capability {capability.capability_id}")
        self.capabilities[capability.capability_id] = capability
        return capability

    def link(self, edge: DevelopmentalEdge) -> DevelopmentalEdge:
        desconocidas = sorted(
            {*edge.precursors, edge.target} - set(self.capabilities))
        if desconocidas:
            raise ValueError(f"edge names capabilities that do not exist: {desconocidas}")
        self.edges.append(edge)
        return edge

    def into(self, target: str) -> tuple[DevelopmentalEdge, ...]:
        return tuple(e for e in self.edges if e.target == target)

    def demonstrated(self) -> frozenset[str]:
        return frozenset(c.capability_id for c in self.capabilities.values()
                         if c.state is CapabilityState.DEMONSTRATED)


#: Precursors of a precursor: how far a candidate sits from what is settled.
def _distance_to_frontier(graph: DevelopmentalGraph, capability_id: str,
                          demonstrated: frozenset[str], seen: frozenset[str] = frozenset()) -> int:
    """0 if demonstrated; otherwise 1 + the cheapest unresolved precursor path.

    Cycles return a large number rather than recursing: a capability that
    depends on itself through a chain is not nearer the frontier for it.
    """
    if capability_id in demonstrated:
        return 0
    if capability_id in seen:
        return 99
    entrantes = graph.into(capability_id)
    if not entrantes:
        return 1
    return 1 + min(
        max((_distance_to_frontier(graph, p, demonstrated, seen | {capability_id})
             for p in edge.precursors), default=0)
        for edge in entrantes)


def gap_analysis(graph: DevelopmentalGraph, target: str,
                 demonstrated: frozenset[str] | None = None) -> GapReport:
    """What is settled about a target's precursors, and what to measure next.

    `premature` is the answer to "are we trying to teach this too early?", and
    it is deliberately strict: a target is premature when nothing about its
    precursors has been measured.  Reading a dependency out of the code is
    worth a great deal and is not the same as having moved the precursor and
    watched the target.
    """
    if target not in graph.capabilities:
        raise ValueError(f"unknown capability {target}")
    settled = graph.demonstrated() if demonstrated is None else demonstrated
    entrantes = graph.into(target)

    known: list[str] = []
    unknown: list[str] = []
    contradicted: list[str] = []
    for edge in entrantes:
        # Dirección explícita y sin ambigüedad. `M REQUIRES SELECTION` se lee
        # «M requiere SELECTION» y significaba lo contrario; una arista cuya
        # dirección depende de cómo la lea quien pasa es peor que no tenerla.
        precursores = " + ".join(sorted(edge.precursors))
        linea = (f"{target} --{edge.kind.value}--> {precursores}"
                 if edge.kind in _TARGET_DEPENDS_ON
                 else f"{precursores} --{edge.kind.value}--> {target}")
        linea += f"  · {edge.evidence.value}"
        if edge.evidence is EvidenceState.MEASURED:
            known.append(f"{linea} · {edge.experiment}")
        elif edge.evidence is EvidenceState.CONTRADICTED:
            contradicted.append(f"{linea} · {edge.basis}")
        elif edge.evidence is EvidenceState.READ:
            known.append(linea)
        else:
            unknown.append(f"{linea} · {edge.basis}")

    # U4 · el listón es por tipo de afirmación, no un «¿se midió algo?» global.
    # Una presencia estructural se cierra leyendo código; una necesidad causal
    # exige lesión, intervención o factorial. Exigir lo mismo a las dos haría
    # que comprobar que una rama existe necesitara un experimento.
    medidas = [e for e in entrantes if e.evidence is EvidenceState.MEASURED]
    premature = not medidas and bool(entrantes)
    if not entrantes:
        reason = "no declared precursors: the target is not in the graph yet"
        premature = True
    elif premature:
        reason = ("every precursor is declared and none measured; nothing has "
                  "moved a precursor and watched this target")
    else:
        reason = f"{len(medidas)} of {len(entrantes)} precursor relations measured"

    precursor, question, empatados = _next_discriminating(graph, entrantes, settled)
    # Un precursor demostrado cuya arista sigue sin medirse no necesita que lo
    # adquieran: necesita que lo quiten y se mire si el objetivo sobrevive.
    lesionables = tuple(sorted(
        p
        for edge in entrantes
        if edge.evidence in {EvidenceState.CANDIDATE, EvidenceState.UNKNOWN}
        for p in edge.precursors
        if p in settled))
    return GapReport(target=target, known=tuple(known), unknown=tuple(unknown),
                     contradicted=tuple(contradicted), next_question=question,
                     next_precursor=precursor, premature=premature, reason=reason,
                     tied_candidates=empatados, lesion_candidates=lesionables)


def _next_discriminating(graph: DevelopmentalGraph,
                         entrantes: tuple[DevelopmentalEdge, ...],
                         demonstrated: frozenset[str]
                         ) -> tuple[str | None, str | None, tuple[str, ...]]:
    """The unresolved precursor that assumes the least, and everything tied with it.

    Derived rather than authored: the useful next experiment is the one
    testable while holding everything else fixed, which is the precursor with
    the fewest unresolved assumptions of its own.  Choosing the most
    interesting candidate instead is how a project spends weeks calibrating
    the wrong mechanism family.

    **The ties are returned, and that matters more than the winner.** Ordering
    three candidates that assume equally little would come down to the
    alphabet, and a question chosen by the alphabet presented as derived is
    worse than no question: it would look like the graph knew something. When
    the set has more than one member, the evidence does not order them and the
    choice is the human's.
    """
    abiertos = {
        p
        for edge in entrantes
        if edge.evidence in {EvidenceState.CANDIDATE, EvidenceState.UNKNOWN}
        for p in edge.precursors
        if p not in demonstrated
    }
    if not abiertos:
        return None, None, ()
    distancias = {p: _distance_to_frontier(graph, p, demonstrated) for p in abiertos}
    minima = min(distancias.values())
    empatados = tuple(sorted(p for p, d in distancias.items() if d == minima))
    elegido = empatados[0]
    etiqueta = graph.capabilities[elegido].label
    pregunta = (f"can the organism acquire «{etiqueta}» on its own, holding every "
                f"other channel fixed?")
    if len(empatados) > 1:
        pregunta += (f"  [the evidence does not order this against "
                     f"{len(empatados) - 1} other candidate(s); the choice is yours]")
    return elegido, pregunta, empatados


# ── El inventario de hoy ──────────────────────────────────────────────────
#
# Poblado desde campañas ejecutadas y desde código leído, nunca desde prosa
# que suene razonable. Lo que no está medido ni leído entra como CANDIDATE y
# se ve como tal en el informe.

def terrario_graph() -> DevelopmentalGraph:
    g = DevelopmentalGraph()

    # --- genealogía: lo demostrado, con la campaña que lo produjo ---------
    for cid, label, origin in (
        ("B", "contingencia sensorimotora", "1.0 causal-bench-01"),
        ("Q", "orientación direccional", "1.1 causal-bench-01"),
        ("H", "proximidad cualitativa", "1.2 causal-bench-01"),
        ("M", "persistencia de una referencia un paso", "1.3 level13-persistence-01"),
        ("PSI", "ligadura conjuntiva", "1.4 level14-binding-01"),
        ("TEMPREG", "regularidad temporal observacional", "1.6 level16-sensory-change-01"),
        ("ACTCON", "contingencia de la acción propia", "1.7 level17-action-contingency-01"),
    ):
        g.add(Capability(cid, label, CapabilityState.DEMONSTRATED, origin))

    g.add(Capability("PSI_USEFUL", "ligadura que aporta en uso conjunto",
                     CapabilityState.DEMONSTRATED, "fusión organism-remembered-binding-01"))

    # --- los dos techos, y NO son fracasos --------------------------------
    g.add(Capability("SELECTION", "selección aprendida de qué conservar bajo cuello de botella",
                     CapabilityState.FROZEN_TARGET, "1.5 · congelado, sólo diseño"))
    g.add(Capability("PREDSTATE", "estado predictivo suficiente",
                     CapabilityState.NEGATIVE, "1.8 · FAMILY_MISMATCH",
                     note="la familia implementada F(Z,A) no expresaba la sellada F(Z,A,O)"))

    # --- precursores candidatos, ninguno demostrado -----------------------
    for cid, label in (
        ("LIMRET", "retención limitada con competencia entre contenidos"),
        ("FUTVAL", "valor futuro de lo retenido"),
        ("TEMPCRED", "crédito temporal a una decisión de retención anterior"),
        ("SELPOL", "política de selección modificable"),
        ("COADAPT", "coadaptación emisor↔receptor"),
        ("EVSENS", "sensibilidad a nueva evidencia"),
        ("REPUPD", "actualización de representación por observación"),
        ("HISTDIS", "desambiguación por historia"),
    ):
        g.add(Capability(cid, label, CapabilityState.CANDIDATE))

    # --- la ÚNICA arista medida del grafo ---------------------------------
    g.link(DevelopmentalEdge(
        frozenset({"M"}), "PSI_USEFUL", DependencyKind.REQUIRES, EvidenceState.MEASURED,
        basis="factorial 2×2: mejora sólo ψ = 0.000000 exacto, interacción +0.006515",
        experiment="organism-remembered-binding-01 · gate RB-7 dependencia total"))
    g.link(DevelopmentalEdge(
        frozenset({"H", "M"}), "PSI_USEFUL", DependencyKind.SUFFICIENT_SET,
        EvidenceState.MEASURED,
        basis="las cuatro capacidades responden en la misma instancia, interacción superaditiva",
        experiment="organism-remembered-binding-01 · gates RB-5 y RB-6"))

    # --- aristas LEÍDAS del código: ciertas, y no developmentales ---------
    # Cinco pasaportes las declaran en prosa. Son estructurales --sin
    # predicción no hay error de predicción-- y no dicen nada sobre si la
    # capacidad sería adquirible sin el precursor.
    g.link(DevelopmentalEdge(
        frozenset({"TEMPREG"}), "HISTDIS", DependencyKind.REQUIRES, EvidenceState.READ,
        basis="1.7 hereda el MECANISMO de 1.6 instanciado y congelado, no una tabla forastera"))

    # --- candidatos de 1.5: su propia descomposición, ninguno medido ------
    for pre in ("LIMRET", "FUTVAL", "TEMPCRED", "SELPOL", "COADAPT"):
        g.link(DevelopmentalEdge(
            frozenset({pre}), "SELECTION", DependencyKind.UNKNOWN, EvidenceState.CANDIDATE,
            basis="descomposición del objetivo; nadie ha movido este precursor y mirado 1.5"))
    g.link(DevelopmentalEdge(
        frozenset({"M"}), "SELECTION", DependencyKind.REQUIRES, EvidenceState.READ,
        basis="el canal temporal ES una retención; M es necesaria por construcción"))
    g.link(DevelopmentalEdge(
        frozenset({"PSI"}), "SELECTION", DependencyKind.UNKNOWN, EvidenceState.CANDIDATE,
        basis="X=(G,P) con |X|=16 es el espacio del binding; requisito funcional o andamiaje, sin decidir"))

    # --- candidatos de 1.8 -------------------------------------------------
    for pre in ("EVSENS", "REPUPD", "HISTDIS"):
        g.link(DevelopmentalEdge(
            frozenset({pre}), "PREDSTATE", DependencyKind.UNKNOWN, EvidenceState.CANDIDATE,
            basis="escalera propuesta antes de exigir estado predictivo"))
    g.link(DevelopmentalEdge(
        frozenset({"ACTCON"}), "PREDSTATE", DependencyKind.REQUIRES, EvidenceState.READ,
        basis="1.8 hereda C_17 como prior; C17-LESION con prior plano pierde 0,79 nats"))

    # --- lo que 1.8 REFUTÓ, y es información, no fracaso ------------------
    g.link(DevelopmentalEdge(
        frozenset({"M"}), "PREDSTATE", DependencyKind.SUFFICIENT_SET,
        EvidenceState.CONTRADICTED,
        basis="la familia realizada F(Z,A) no expresa F(Z,A,O): 0/400 diferencias "
              "al variar observaciones, 297/400 al variar acciones",
        experiment="level18-predictive-state-01 · ingeniería inversa v1"))

    # --- la genealogía NO es desarrollo, y queda dicho aquí ---------------
    # 1.6 importa de level1 sólo primitivas del cuerpo y del mundo, y NADA de
    # 1.1–1.4: por eso no existe arista developmental de PSI a TEMPREG aunque
    # la cronología las ponga en ese orden.
    return g


# ── El grafo, construido desde el ledger tipado ──────────────────────────

def _collapse(claim) -> "EvidenceState":
    """Las cuatro dimensiones del ledger, proyectadas al eje que el análisis usa.

    La proyección pierde información a propósito y en un solo sentido: el
    ledger es la autoridad y esto es una vista. `CONTRADICTED` gana sobre la
    clase de evidencia porque una relación medida y luego refutada no es
    conocimiento a favor -- que es justo lo que el modelo de dos ejes no podía
    escribir.
    """
    from terrario.lab.relation_ledger import EpistemicStatus

    if claim.status is EpistemicStatus.CONTRADICTED:
        return EvidenceState.CONTRADICTED
    if claim.is_measured:
        return EvidenceState.MEASURED
    if claim.is_read:
        return EvidenceState.READ
    return EvidenceState.CANDIDATE


def graph_from_ledger(capabilities: dict[str, Capability],
                      claims) -> DevelopmentalGraph:
    """Una sola fuente: el ledger. El grafo deja de tener aristas propias."""
    from terrario.lab.relation_ledger import RelationSemantics

    equivalencia = {
        RelationSemantics.REQUIRES: DependencyKind.REQUIRES,
        RelationSemantics.FACILITATES: DependencyKind.FACILITATES,
        RelationSemantics.SUFFICIENT_SET: DependencyKind.SUFFICIENT_SET,
        RelationSemantics.ALTERNATIVE_TO: DependencyKind.ALTERNATIVE,
        RelationSemantics.SUBSTITUTABLE_WITH: DependencyKind.ALTERNATIVE,
        RelationSemantics.INHIBITS: DependencyKind.INHIBITS,
        RelationSemantics.SYNERGIZES_WITH: DependencyKind.SUFFICIENT_SET,
    }
    g = DevelopmentalGraph()
    for capability in capabilities.values():
        g.add(capability)
    for claim in claims:
        g.link(DevelopmentalEdge(
            precursors=claim.precursors, target=claim.target,
            kind=equivalencia.get(claim.semantics, DependencyKind.UNKNOWN),
            evidence=_collapse(claim),
            basis=f"{claim.basis} [{claim.claim_id}]",
            experiment=claim.evidence_ref))
    return g
