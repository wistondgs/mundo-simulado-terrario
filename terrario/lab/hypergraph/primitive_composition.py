"""The composition map, at the stage before anything deserves a name.

This is deliberately **not** built on `theory_operational`.  That ontology
exists and works; bringing it here would import a vocabulary designed for a
question that has been retired, and the new programme is supposed to start
without one.  Two record types, six statuses, and nothing else.

The unit of interest is not a node.  It is:

    {P_i, P_j, ...}  ->  ?

and the question mark is load-bearing.  `A + B -> C` is what gets written
*after* an experiment, and until then the edge holds a hypothesis with an
output nobody has seen.  An emergent starts life as `E001`, because calling it
attention or reasoning on the day it appears is how a measurement becomes a
theory without passing through evidence.

Four things are structural rather than advisory:

**An emergent cannot be born named.**  Ids are `E###`; a handful of words that
name whole faculties are refused outright.  The naming comes later, from
accumulated evidence, and a textual rule against it is the failure mode this
project keeps finding in its own history.

**A world always travels with an edge.**  `{P03,P06} -> E004` in one world and
`{P03,P06} -> NONE` in another are not a contradiction, they are two
conditions, and an edge with no world cannot say which one it is.

**Absence of emergence is writable.**  `NO_EFFECT` is a result: later, when
`{A,B,C}` does produce something, `{A,B}` producing nothing is what identifies
`C` as the element that unlocked it.  So `NO_EFFECT` demands an empty output
and no degrees of freedom, and an edge that produced something cannot claim it.

**Replication is computed, never declared.**  `REPLICATED` means the same
composition gave the same output in more than one world.  That is a property
of a *set* of edges and no single edge can assert it about itself.

There is no target capability here, no final architecture and no expected
level of intelligence.  The map says what exists, what was combined with what,
what happened, what did not happen, and what is still unknown.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Iterable, Mapping

SCHEMA_VERSION = "terrario.lab.primitive-composition/v0.1"

#: Ausencia de emergencia. No es lo mismo que no haber mirado.
NONE_OUTPUT = "NONE"


class CompositionStatus(StrEnum):
    """Six, and no more.  Twenty epistemic categories is the previous map."""

    UNKNOWN = "UNKNOWN"
    HYPOTHESIS = "HYPOTHESIS"
    OBSERVED = "OBSERVED"
    REPLICATED = "REPLICATED"
    NO_EFFECT = "NO_EFFECT"
    CONTRADICTED = "CONTRADICTED"


class DofStatus(StrEnum):
    """Whether an instrument measured degrees of freedom here. Never a value.

    `MEASURED` with `delta_dof = 0` and `NOT_MEASURED` are different facts and
    collapsing them is the epistemological error this map was caught making:
    the historical import has no degree-of-freedom measurement at all, and
    printing zero for it invents a result the old programme never produced.
    """

    NOT_MEASURED = "NOT_MEASURED"
    MEASURED = "MEASURED"


class BoundaryStatus(StrEnum):
    """Whether the negative boundary is written down."""

    BOUNDARY_KNOWN = "BOUNDARY_KNOWN"
    BOUNDARY_UNKNOWN = "BOUNDARY_UNKNOWN"


class MinimalityStatus(StrEnum):
    """Separate from the boundary, because a boundary is not a proof.

    A thing can state exactly what it cannot do and still decompose further.
    The strong claim needs the absence of a finer operational decomposition
    pertinent to the current programme that preserves the phenomenon we want
    to manipulate, and nothing here demonstrates that for anything yet.
    """

    NOT_ESTABLISHED = "NOT_ESTABLISHED"
    MINIMAL_UNDER_CURRENT_VOCABULARY = "MINIMAL_UNDER_CURRENT_VOCABULARY"


class Sourcing(StrEnum):
    """Where a primitive came from, which is not the same as who believes it.

    Six existing vocabularies were audited before this one was added and each
    breaks on a checkable point: `theory_operational.DERIVED` means composed
    from two or more parents and its constructor refuses fewer than two, which
    is the opposite direction; `HypothesisOrigin` is tied to
    `EvidenceClass.HYPOTHESIS` and a catalogue entry is not a hypothesis;
    `ProvenanceLevel` is confined to bibliographic sources with a reference id;
    `AssertionClass`, `EpistemicStatus.ANALYST_INFERENCE` and
    `MappingRelation.PART_OF` each answer a different question. The closest
    pair in the repo, `crossgraph` `DERIVED_FROM` / `EXTRACTED_FROM`, needs
    endpoints in a sovereign domain that a primitive is not registered in.
    """

    #: Hay un claim citable del corpus --claim_id, locator y hash-- que enuncia
    #: este concepto. Hoy: NINGUNA primitiva.
    DIRECTLY_SOURCED = "DIRECTLY_SOURCED"
    #: Se construyó, corrió y se cerró con gates como un nivel histórico. Dice
    #: que ocurrió, no que el corpus lo sostenga.
    HISTORICALLY_OPERATIONALIZED = "HISTORICALLY_OPERATIONALIZED"
    #: Salió de trocear un concepto más grande durante el análisis. El concepto
    #: fuente está citado; el corte lo hizo el proyecto.
    DERIVED_BY_DECOMPOSITION = "DERIVED_BY_DECOMPOSITION"
    UNKNOWN = "UNKNOWN"


class DerivationAuthority(StrEnum):
    """Quién hizo el corte, cuando hubo corte."""

    PROJECT_ANALYSIS = "PROJECT_ANALYSIS"
    NOT_A_DERIVATION = "NOT_A_DERIVATION"


class Cost(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    UNKNOWN = "UNKNOWN"


class DegreeOfFreedom(StrEnum):
    """What got wider, asked as six questions rather than named as a faculty.

    These are the only vocabulary the map has for what a composition bought,
    and each is a question someone can answer by looking.
    """

    #: ¿puede distinguir más estados?
    STATE_DISCRIMINATION = "STATE_DISCRIMINATION"
    #: ¿puede depender de más pasado?
    TEMPORAL_CONDITIONING = "TEMPORAL_CONDITIONING"
    #: ¿puede escoger entre más acciones?
    ACTION_RANGE = "ACTION_RANGE"
    #: ¿puede modificar algo por experiencia?
    EXPERIENCE_DEPENDENT_CHANGE = "EXPERIENCE_DEPENDENT_CHANGE"
    #: ¿puede mantener más relaciones simultáneamente?
    SIMULTANEOUS_RELATIONS = "SIMULTANEOUS_RELATIONS"
    #: ¿puede responder diferente al mismo presente?
    SAME_PRESENT_DIFFERENT_RESPONSE = "SAME_PRESENT_DIFFERENT_RESPONSE"


#: Nombres de facultad entera. Un emergente no nace llamandose asi: el nombre
#: llega despues, de la evidencia acumulada, y ponerlo el primer dia es como
#: una medicion se convierte en teoria sin pasar por la evidencia.
NOMBRES_PREMATUROS = frozenset({
    "reasoning", "razonamiento", "planning", "planificacion", "planificación",
    "attention", "atencion", "atención", "curiosity", "curiosidad",
    "episodic", "episodica", "episódica", "metacognition", "metacognicion",
    "metacognición", "agency", "agencia", "consciousness", "conciencia",
    "intelligence", "inteligencia", "understanding", "comprension",
    "comprensión", "language", "lenguaje", "theory_of_mind", "self_model",
})


class MapRefused(ValueError):
    """Something the map will not hold, and why."""


def _premature(texto: str) -> str | None:
    minusculas = texto.lower().replace("-", "_").replace(" ", "_")
    for palabra in NOMBRES_PREMATUROS:
        if palabra in minusculas:
            return palabra
    return None


@dataclass(frozen=True)
class Primitive:
    """One minimal functional possibility, answering six questions and no more.

    `cannot` is not decoration.  A primitive that only says what it can do
    grows in the reader's head until it is a faculty again, and the boundary
    is the whole reason these are called minimal.
    """

    id: str
    name: str
    can: str
    cannot: str
    requires: tuple[str, ...] = ()
    cost: Cost = Cost.UNKNOWN
    #: Cómo sabemos que está presente. Sin esto no es una primitiva, es un deseo.
    detection: str = ""
    provenance: str = ""
    #: De dónde salió, y --si salió de trocear algo-- de qué exactamente.
    sourcing: Sourcing = Sourcing.UNKNOWN
    source_concept: str = ""
    derivation_authority: DerivationAuthority = DerivationAuthority.NOT_A_DERIVATION
    #: La identidad del claim de corpus, cuando lo hay. Hoy no lo hay para nadie.
    corpus_claim_id: str = ""
    boundary_status: BoundaryStatus = BoundaryStatus.BOUNDARY_KNOWN
    minimality_status: MinimalityStatus = MinimalityStatus.NOT_ESTABLISHED
    #: Por qué no hay descomposición más fina pertinente. Sólo para la
    #: afirmación fuerte, y sin ella la afirmación fuerte se rechaza.
    minimality_basis: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "requires", tuple(self.requires))
        if not self.id.startswith("P") or not self.id[1:].isdigit():
            raise MapRefused(f"{self.id}: a primitive is P followed by digits")
        for campo in ("name", "can", "cannot", "detection"):
            if not str(getattr(self, campo)).strip():
                raise MapRefused(
                    f"{self.id}: «{campo}» is empty. A primitive answers six "
                    f"questions; one it does not answer is not yet minimal, it "
                    f"is just short")
        if self.id in self.requires:
            raise MapRefused(f"{self.id} cannot require itself")
        if self.minimality_status is MinimalityStatus.MINIMAL_UNDER_CURRENT_VOCABULARY \
                and not self.minimality_basis.strip():
            raise MapRefused(
                f"{self.id} claims minimality with no basis. An explicit «cannot» "
                f"is a boundary, not a proof: a thing can state what it cannot do "
                f"and still decompose further, and the strong claim needs the "
                f"absence of a finer decomposition that preserves the phenomenon")
        if self.boundary_status is BoundaryStatus.BOUNDARY_KNOWN \
                and self.minimality_status is \
                MinimalityStatus.MINIMAL_UNDER_CURRENT_VOCABULARY \
                and not self.minimality_basis.strip():
            raise MapRefused(f"{self.id}: a known boundary is not minimality")

        if self.sourcing is Sourcing.DERIVED_BY_DECOMPOSITION:
            if not self.source_concept.strip():
                raise MapRefused(
                    f"{self.id} is DERIVED_BY_DECOMPOSITION and names no source "
                    f"concept. Without it the record reads as «the corpus "
                    f"discovered {self.id}», when what happened is that a source "
                    f"concept was cut up during analysis")
            if self.derivation_authority is DerivationAuthority.NOT_A_DERIVATION:
                raise MapRefused(
                    f"{self.id} was decomposed and declares no authority for the "
                    f"cut; who cut it is what separates analysis from attestation")
        elif self.source_concept.strip():
            raise MapRefused(
                f"{self.id} names a source concept and is not "
                f"DERIVED_BY_DECOMPOSITION")

        if self.sourcing is Sourcing.DIRECTLY_SOURCED and not self.corpus_claim_id.strip():
            raise MapRefused(
                f"{self.id} claims DIRECTLY_SOURCED with no claim id. Direct "
                f"sourcing means a citable claim exists -- id, locator and hash -- "
                f"and saying so without one is the whole error this field exists "
                f"to make impossible")
        if self.corpus_claim_id.strip() and self.sourcing is not Sourcing.DIRECTLY_SOURCED:
            raise MapRefused(
                f"{self.id} carries a corpus claim id and does not claim to be "
                f"directly sourced")

    def as_record(self) -> Mapping[str, Any]:
        return {"id": self.id, "name": self.name, "can": self.can,
                "cannot": self.cannot, "requires": list(self.requires),
                "cost": self.cost.value, "detection": self.detection,
                "provenance": self.provenance,
                "sourcing": self.sourcing.value,
                "source_concept": self.source_concept,
                "derivation_authority": self.derivation_authority.value,
                "corpus_claim_id": self.corpus_claim_id,
                "boundary_status": self.boundary_status.value,
                "minimality_status": self.minimality_status.value,
                "minimality_basis": self.minimality_basis}

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> "Primitive":
        """Reconstruye sin pérdida lo que `as_record` serializó."""
        return cls(
            id=record["id"], name=record["name"], can=record["can"],
            cannot=record["cannot"], requires=tuple(record.get("requires", ())),
            cost=Cost(record.get("cost", Cost.UNKNOWN.value)),
            detection=record.get("detection", ""),
            provenance=record.get("provenance", ""),
            sourcing=Sourcing(record.get("sourcing", Sourcing.UNKNOWN.value)),
            source_concept=record.get("source_concept", ""),
            derivation_authority=DerivationAuthority(
                record.get("derivation_authority",
                           DerivationAuthority.NOT_A_DERIVATION.value)),
            corpus_claim_id=record.get("corpus_claim_id", ""),
            boundary_status=BoundaryStatus(
                record.get("boundary_status", BoundaryStatus.BOUNDARY_KNOWN.value)),
            minimality_status=MinimalityStatus(
                record.get("minimality_status",
                           MinimalityStatus.NOT_ESTABLISHED.value)),
            minimality_basis=record.get("minimality_basis", ""))


@dataclass(frozen=True)
class Hyperedge:
    """`{inputs} -> output`, in one world, with what got wider and how we know."""

    id: str
    inputs: frozenset[str]
    world: str
    output: str
    status: CompositionStatus
    #: Todo lo que se mantuvo fijo aparte del mundo: organismo, presupuesto,
    #: implementación, instrumento. Dos aristas sólo son comparables dentro del
    #: mismo scope, y sin él «añadir P04 cambió el resultado» es una frase sin
    #: condiciones.
    scope: str = ""
    dof_status: DofStatus = DofStatus.NOT_MEASURED
    dof_measurement_ref: str | None = None
    dof_before: int | None = None
    dof_after: int | None = None
    new_degrees_of_freedom: frozenset[DegreeOfFreedom] = frozenset()
    evidence: str = ""
    note: str = ""
    provenance: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "inputs", frozenset(self.inputs))
        object.__setattr__(self, "new_degrees_of_freedom",
                           frozenset(self.new_degrees_of_freedom))
        if not self.inputs:
            raise MapRefused(f"{self.id}: an edge with no inputs composes nothing")
        if not str(self.world).strip():
            raise MapRefused(
                f"{self.id}: no world. The same composition can hold in one world "
                f"and not in another, and an edge that does not say which cannot "
                f"be told apart from one that contradicts it")
        if not str(self.scope).strip():
            # Estaba declarado obligatorio en prosa y no se comprobaba, y eso
            # hacía VACUA la puerta de scope: dos aristas con el defecto vacío
            # comparaban iguales y autorizaban una inferencia sin condiciones.
            raise MapRefused(
                f"{self.id}: no scope. Two edges are only comparable under matched "
                f"organism, budget and implementation, and two edges that both "
                f"omit it would compare equal and license an inference with no "
                f"conditions at all")

        if self.output != NONE_OUTPUT:
            premature = _premature(self.output)
            if premature:
                raise MapRefused(
                    f"{self.id}: «{self.output}» names a whole faculty ({premature}). "
                    f"An emergent is born E### and earns a name from accumulated "
                    f"evidence, not on the day it appears")
            if not (self.output.startswith("E") and self.output[1:].isdigit()):
                raise MapRefused(
                    f"{self.id}: «{self.output}» is neither {NONE_OUTPUT} nor an "
                    f"E### emergent")

        if self.status is CompositionStatus.NO_EFFECT:
            if self.output != NONE_OUTPUT or self.new_degrees_of_freedom:
                raise MapRefused(
                    f"{self.id} claims NO_EFFECT and carries an output or a degree "
                    f"of freedom; something happened")
        elif self.output == NONE_OUTPUT and self.status in {
                CompositionStatus.OBSERVED, CompositionStatus.REPLICATED}:
            raise MapRefused(
                f"{self.id} observed nothing and is not NO_EFFECT; absence of "
                f"emergence is a result and has its own status")

        if self.status is CompositionStatus.REPLICATED:
            raise MapRefused(
                f"{self.id}: REPLICATED is computed over several worlds by "
                f"`replicated`, never declared by one edge about itself")
        if self.status in {CompositionStatus.OBSERVED, CompositionStatus.NO_EFFECT,
                           CompositionStatus.CONTRADICTED} and not self.evidence:
            raise MapRefused(
                f"{self.id} settles a composition with no evidence reference")

        # Y la distinción que este mapa ya se equivocó una vez en sostener.
        if self.dof_status is DofStatus.NOT_MEASURED:
            for campo in ("dof_measurement_ref", "dof_before", "dof_after"):
                if getattr(self, campo) is not None:
                    raise MapRefused(
                        f"{self.id} is NOT_MEASURED and carries «{campo}». "
                        f"Nothing measured degrees of freedom here, and a value "
                        f"in that column would be a result nobody produced")
            if self.new_degrees_of_freedom:
                raise MapRefused(
                    f"{self.id} is NOT_MEASURED and names a degree of freedom; "
                    f"naming one IS the measurement")
        else:
            if not self.dof_measurement_ref:
                raise MapRefused(
                    f"{self.id} claims MEASURED with no instrument reference")
            if self.dof_before is None or self.dof_after is None:
                raise MapRefused(
                    f"{self.id} claims MEASURED without both readings")
            if self.dof_before < 0 or self.dof_after < 0:
                raise MapRefused(f"{self.id}: a count of freedoms is not negative")
            salto = self.dof_after - self.dof_before
            if salto > 0 and not self.new_degrees_of_freedom:
                raise MapRefused(
                    f"{self.id} measured a rise of {salto} and names none of them")
            if salto <= 0 and self.new_degrees_of_freedom:
                raise MapRefused(
                    f"{self.id} names a new degree of freedom and measured "
                    f"delta {salto}")

    @property
    def delta_dof(self) -> int | None:
        """`None` cuando nadie midió. `0` medido es un resultado distinto."""
        if self.dof_status is DofStatus.NOT_MEASURED:
            return None
        return self.dof_after - self.dof_before

    def label(self) -> str:
        return (f"{{{', '.join(sorted(self.inputs))}}} --{self.world}--> "
                f"{self.output}")

    def as_record(self) -> Mapping[str, Any]:
        return {"id": self.id, "inputs": sorted(self.inputs), "world": self.world,
                "scope": self.scope, "output": self.output,
                "status": self.status.value,
                "dof_status": self.dof_status.value,
                "dof_measurement_ref": self.dof_measurement_ref,
                "dof_before": self.dof_before, "dof_after": self.dof_after,
                "delta_dof": self.delta_dof,
                "new_degrees_of_freedom":
                    sorted(d.value for d in self.new_degrees_of_freedom),
                "evidence": self.evidence, "note": self.note,
                "provenance": self.provenance}


def replicated(edges: Iterable[Hyperedge]) -> tuple[tuple[frozenset[str], str], ...]:
    """Compositions observed with the same output in more than one world.

    Computed, because replication is a property of a set of edges and no
    single edge can say it about itself.
    """
    mundos: dict[tuple[frozenset[str], str], set[str]] = {}
    for edge in edges:
        if edge.status is CompositionStatus.OBSERVED:
            mundos.setdefault((edge.inputs, edge.output), set()).add(edge.world)
    return tuple(sorted((clave for clave, w in mundos.items() if len(w) > 1),
                        key=lambda c: (sorted(c[0]), c[1])))


def unlocking_element(edges: Iterable[Hyperedge]) -> tuple[Mapping[str, Any], ...]:
    """Which single addition changed the result, **under one matched scope**.

    This is what `NO_EFFECT` is for: `{A}` producing nothing is the row that
    later identifies `C`.  But it identifies it only inside the conditions
    that were held fixed.  Two edges in the same world with different budgets,
    organisms or implementations differ in more than the added element, and
    the inference would be about all of it at once.

    So the scope comes back with the finding, and what is licensed is «adding
    X changed the outcome under this scope», never «X unlocks Y».
    """
    lista = list(edges)
    vacios = [e for e in lista if e.status is CompositionStatus.NO_EFFECT]
    hallazgos: list[Mapping[str, Any]] = []
    for edge in lista:
        if edge.output == NONE_OUTPUT or edge.status is not CompositionStatus.OBSERVED:
            continue
        for vacio in vacios:
            if (vacio.world == edge.world and vacio.scope == edge.scope
                    and vacio.inputs < edge.inputs
                    and len(edge.inputs - vacio.inputs) == 1):
                hallazgos.append({
                    "element": next(iter(edge.inputs - vacio.inputs)),
                    "from_empty": vacio.id, "to_observed": edge.id,
                    "world": edge.world, "scope": edge.scope,
                    "claim": "adding this element changed the outcome under this "
                             "scope; it is not a universal unlocker"})
    return tuple(sorted(hallazgos, key=lambda h: (h["element"], h["to_observed"])))


def genuine_interaction(edges: Iterable[Hyperedge],
                        edge: Hyperedge) -> frozenset | None:
    """Degrees of freedom the whole has and no smaller combination showed.

    `None` when the edge carries no measurement: an empty set would say «the
    composition is exactly the union of its parts», and nobody looked.
    """
    if edge.dof_status is DofStatus.NOT_MEASURED:
        return None
    menores: set[DegreeOfFreedom] = set()
    for otra in edges:
        if (otra.id != edge.id and otra.world == edge.world
                and otra.scope == edge.scope and otra.inputs < edge.inputs
                and otra.dof_status is DofStatus.MEASURED):
            menores |= otra.new_degrees_of_freedom
    return edge.new_degrees_of_freedom - menores


def delta_df(stages: list[tuple[str, frozenset[str]]],
             edges: Iterable[Hyperedge], world: str) -> tuple[Mapping[str, Any], ...]:
    """`DF(S_n) - DF(S_{n-1})` along an accumulating organism.

    A stage covered by no measured edge comes back `NOT_MEASURED` with `None`
    for every value.  It does **not** come back zero: a measured zero says the
    rung added nothing and an unmeasured one says nobody looked, and the first
    version of this function printed the second as the first.
    """
    lista = [e for e in edges if e.world == world]
    salida = []
    previo: frozenset | None = None
    for nombre, capacidades in stages:
        cubren = [e for e in lista if e.inputs <= capacidades]
        medidas = [e for e in cubren if e.dof_status is DofStatus.MEASURED]
        if not medidas:
            salida.append({"stage": nombre, "capabilities": sorted(capacidades),
                           "dof_status": DofStatus.NOT_MEASURED.value,
                           "df": None, "delta_df": None, "gained": None,
                           "why": "no edge covering this stage carries a degree "
                                  "of freedom measurement"})
            continue
        actual: set[DegreeOfFreedom] = set()
        for edge in medidas:
            actual |= edge.new_degrees_of_freedom
        salida.append({
            "stage": nombre, "capabilities": sorted(capacidades),
            "dof_status": DofStatus.MEASURED.value,
            "measurement_refs": sorted({e.dof_measurement_ref for e in medidas}),
            "df": sorted(d.value for d in actual),
            "delta_df": None if previo is None else len(actual) - len(previo),
            "gained": None if previo is None
                      else sorted(d.value for d in (actual - previo))})
        previo = frozenset(actual)
    return tuple(salida)


#: P01-P07 son las siete semillas historicas. Sus numeros de nivel son
#: cronologia, no escalera: aqui son siete elementos disponibles del banco y
#: nada mas.
#:
#: P08-P20 salen de descomponer el Mapa Global
#: (docs/INVENTARIO_CONCEPTOS_01.md). El criterio de exclusion es duro --si una
#: capacidad contiene dentro otra capacidad funcional identificable todavia no
#: es primitiva-- y casi ningun concepto de nivel superior lo pasa entero. Lo
#: que entra es la DESCOMPOSICION, y la provenance lo dice: el concepto fuente
#: esta citado, el troceo lo hice yo.
def primitives_v01() -> tuple[Primitive, ...]:
    return (
        Primitive(
            sourcing=Sourcing.HISTORICALLY_OPERATIONALIZED,
            id="P01", name="sensorimotor_contingency",
            can="tell that its own act changed what it senses",
            cannot="say which act, in which direction, or how far",
            cost=Cost.LOW,
            detection="acting and not acting give different observation streams",
            provenance="HISTORICAL seed · level 1.0 · frozen campaign 3ef016c · the ONLY rung with NO sealed pre-registered oracle: it has seven sealed gates and no oracle document, unlike 1.1-1.7"),
        Primitive(
            sourcing=Sourcing.HISTORICALLY_OPERATIONALIZED,
            id="P02", name="directional_orientation",
            can="use an external signal g_t to tell one direction from another",
            cannot="say how far, nor hold the direction once the signal is gone",
            requires=("P01",), cost=Cost.LOW,
            detection="behaviour differs by the value of g_t alone",
            provenance="HISTORICAL seed · level 1.1 · frozen campaign 3ef016c"),
        Primitive(
            sourcing=Sourcing.HISTORICALLY_OPERATIONALIZED,
            id="P03", name="qualitative_proximity",
            can="tell near from far as a quality",
            cannot="measure a distance, order three distances, or keep it",
            requires=("P01",), cost=Cost.LOW,
            detection="behaviour differs by near/far with everything else fixed",
            provenance="HISTORICAL seed · level 1.2 · frozen campaign 3ef016c · "
                       "ceiling 8/55"),
        Primitive(
            sourcing=Sourcing.HISTORICALLY_OPERATIONALIZED,
            id="P04", name="persistence_one_step",
            can="keep one signal available for one tick after it is gone",
            cannot="recover episodes, select what to keep, or hold a sequence",
            requires=("P01",), cost=Cost.LOW,
            detection="same present with a different previous tick gives a "
                      "different response; omitting the tick removes it",
            provenance="HISTORICAL seed · level 1.3 · frozen campaign 32d400f"),
        Primitive(
            sourcing=Sourcing.HISTORICALLY_OPERATIONALIZED,
            id="P05", name="minimal_conjunctive_binding",
            can="hold two references as one pair rather than two loose values",
            cannot="bind three, rebind on the fly, or name what it bound",
            requires=("P04",), cost=Cost.MEDIUM,
            detection="swapping which value goes with which changes the response",
            provenance="HISTORICAL seed · level 1.4 · frozen campaign 68d852d"),
        Primitive(
            sourcing=Sourcing.HISTORICALLY_OPERATIONALIZED,
            id="P06", name="observational_temporal_regularity",
            can="carry P(o_{t+1} | o_t)",
            cannot="condition on its own act, on a change bit, on an efferent "
                   "copy or on a position -- `observe` rejects all four in "
                   "execution",
            cost=Cost.MEDIUM,
            detection="prediction beats the frozen and temporally shuffled arms",
            provenance="HISTORICAL seed · level 1.6 · frozen campaign c2b808b"),
        Primitive(
            sourcing=Sourcing.HISTORICALLY_OPERATIONALIZED,
            id="P07", name="own_action_contingency",
            can="carry C_17(O, A, O'), the deviation per action over the "
                "temporal expectation",
            cannot="acquire the causal relevance or the generality of the "
                   "concept «action»",
            requires=("P06",), cost=Cost.MEDIUM,
            detection="twin worlds: the effect is present where the action "
                      "moves the transition and exactly zero where it does not",
            provenance="HISTORICAL seed · level 1.7 · frozen campaign 6cf55a4"),

        Primitive(
            sourcing=Sourcing.DERIVED_BY_DECOMPOSITION,
            source_concept="use_online_learning / LEARN-A1",
            derivation_authority=DerivationAuthority.PROJECT_ANALYSIS,
            id="P08", name="outcome_driven_association_change",
            can="change one association as a result of what followed",
            cannot="choose what to change, keep a history of changes, or "
                   "generalise the change",
            requires=("P01",), cost=Cost.LOW,
            detection="the same input maps differently after a different outcome",
            provenance="DECOMPOSED from use_online_learning / LEARN-A1 · "
                       "INVENTARIO_CONCEPTOS_01.md capa 1"),
        Primitive(
            sourcing=Sourcing.DERIVED_BY_DECOMPOSITION,
            source_concept="use_homeostasis / HOMEO-A1",
            derivation_authority=DerivationAuthority.PROJECT_ANALYSIS,
            id="P09", name="internal_deviation_detection",
            can="tell that an internal magnitude sits away from a reference",
            cannot="act on it, move the reference, or hold more than one",
            cost=Cost.LOW,
            detection="response varies with the internal magnitude at fixed input",
            provenance="DECOMPOSED from use_homeostasis / HOMEO-A1 · capa 1"),
        Primitive(
            sourcing=Sourcing.DERIVED_BY_DECOMPOSITION,
            source_concept="use_uncertainty / UNC-A1",
            derivation_authority=DerivationAuthority.PROJECT_ANALYSIS,
            id="P10", name="observation_frequency_discrimination",
            can="tell a case it has met often from one it has met rarely",
            cannot="turn that into a confidence, a variance or a policy",
            requires=("P08",), cost=Cost.LOW,
            detection="response differs between equally-valued cases of "
                      "different count",
            provenance="DECOMPOSED from use_uncertainty / UNC-A1 · capa 1"),
        Primitive(
            sourcing=Sourcing.DERIVED_BY_DECOMPOSITION,
            source_concept="use_episodic_memory / EPMEM-A1",
            derivation_authority=DerivationAuthority.PROJECT_ANALYSIS,
            id="P11", name="persistence_beyond_one_step",
            can="keep a signal available for more than one tick",
            cannot="index, retrieve by content, or choose what survives",
            requires=("P04",), cost=Cost.MEDIUM,
            detection="the response depends on a tick further back than one",
            provenance="DECOMPOSED from use_episodic_memory / EPMEM-A1 · capa 1 · "
                       "the module itself is NOT primitive: it contains "
                       "retrieval, indexing and selection"),
        Primitive(
            sourcing=Sourcing.DERIVED_BY_DECOMPOSITION,
            source_concept="use_longterm_memory / LTMEM-A1",
            derivation_authority=DerivationAuthority.PROJECT_ANALYSIS,
            id="P12", name="persistence_across_an_episode_boundary",
            can="carry something through a reset that clears the rest",
            cannot="decide what deserves to cross, or merge what crossed",
            requires=("P11",), cost=Cost.MEDIUM,
            detection="a second episode differs from the first in a way a fresh "
                      "organism does not show",
            provenance="DECOMPOSED from use_longterm_memory / LTMEM-A1 · capa 1"),
        Primitive(
            sourcing=Sourcing.DERIVED_BY_DECOMPOSITION,
            source_concept="use_entropy_regularization / PLAST-A1",
            derivation_authority=DerivationAuthority.PROJECT_ANALYSIS,
            id="P13", name="same_present_variable_action",
            can="emit a different act for the same present",
            cannot="choose when to vary, or narrow the variation with experience",
            cost=Cost.LOW,
            detection="repeated identical presents give a distribution, not a "
                      "single act",
            provenance="DECOMPOSED from use_entropy_regularization / PLAST-A1 · "
                       "capa 1"),
        Primitive(
            sourcing=Sourcing.DERIVED_BY_DECOMPOSITION,
            source_concept="use_curiosity / CURIO-A1",
            derivation_authority=DerivationAuthority.PROJECT_ANALYSIS,
            id="P14", name="seen_versus_unseen_discrimination",
            can="tell a case it has met before from one it has not",
            cannot="value novelty, seek it, or rank degrees of it",
            requires=("P11",), cost=Cost.LOW,
            detection="first encounter and repeat encounter differ at equal input",
            provenance="DECOMPOSED from use_curiosity / CURIO-A1 · capa 1 · the "
                       "module contains novelty detection AND a reward term"),
        Primitive(
            sourcing=Sourcing.DERIVED_BY_DECOMPOSITION,
            source_concept="use_factored_action",
            derivation_authority=DerivationAuthority.PROJECT_ANALYSIS,
            id="P15", name="two_factor_action_composition",
            can="build one act out of two independent factors",
            cannot="learn the factorisation, or add a third factor",
            cost=Cost.LOW,
            detection="the act space is the product of the factors and each "
                      "moves independently",
            provenance="DECOMPOSED from use_factored_action · capa 1 · declared "
                       "there as «channel repair, not a corpus concept»"),
        Primitive(
            sourcing=Sourcing.DERIVED_BY_DECOMPOSITION,
            source_concept="B1 ultraestabilidad / segundo lazo · HEA-014 · C-HEA-014-01",
            derivation_authority=DerivationAuthority.PROJECT_ANALYSIS,
            id="P16", name="gradient_free_own_parameter_redraw",
            can="re-draw one of its own parameters without a gradient",
            cannot="choose which, know whether it helped, or keep the better one",
            requires=("P09",), cost=Cost.MEDIUM,
            detection="parameters move at a threshold crossing with no error "
                      "signal present",
            provenance="DECOMPOSED from B1 ultraestabilidad / second loop · "
                       "capa 2 · HEA-014 S.7/26 · C-HEA-014-01"),
        Primitive(
            sourcing=Sourcing.DERIVED_BY_DECOMPOSITION,
            source_concept="B2 recompensa interoceptiva · HEA-001",
            derivation_authority=DerivationAuthority.PROJECT_ANALYSIS,
            id="P17", name="internal_magnitude_as_reinforcement",
            can="treat the reduction of an internal deviation as the reinforcer",
            cannot="weigh it against an external one, or hold two of them",
            requires=("P09", "P08"), cost=Cost.MEDIUM,
            detection="behaviour tracks the internal deviation when the external "
                      "payoff is held flat",
            provenance="DECOMPOSED from B2 recompensa interoceptiva · capa 2 · "
                       "HEA-001 · the seam `_policy_reward` already exists, inert"),
        Primitive(
            sourcing=Sourcing.DERIVED_BY_DECOMPOSITION,
            source_concept="B3 alostasis · HEA-011 §2",
            derivation_authority=DerivationAuthority.PROJECT_ANALYSIS,
            id="P18", name="movable_reference_point",
            can="change the reference an internal magnitude is compared against",
            cannot="anticipate when to move it, or learn where to move it",
            requires=("P09",), cost=Cost.MEDIUM,
            detection="the same internal magnitude reads as deviation at one "
                      "time and not at another",
            provenance="DECOMPOSED from B3 alostasis · capa 2 · HEA-011 §2 · "
                       "anticipation is NOT included: that part is not primitive"),
        Primitive(
            sourcing=Sourcing.DERIVED_BY_DECOMPOSITION,
            source_concept="B4 aversión al riesgo · HEA-001",
            derivation_authority=DerivationAuthority.PROJECT_ANALYSIS,
            id="P19", name="spread_versus_mean_discrimination",
            can="tell two cases apart when their means match and their spreads "
                "do not",
            cannot="prefer either, or weigh the preference by anything",
            requires=("P10",), cost=Cost.MEDIUM,
            detection="response differs between equal-mean, unequal-spread cases",
            provenance="DECOMPOSED from B4 aversion al riesgo · capa 2 · "
                       "HEA-001 · the preference itself is not included"),
        Primitive(
            sourcing=Sourcing.DERIVED_BY_DECOMPOSITION,
            source_concept="B5 metacognición · HEA-017 · C-HEA-017-01",
            derivation_authority=DerivationAuthority.PROJECT_ANALYSIS,
            id="P20", name="own_error_signal_readable",
            can="read its own prediction error as an input",
            cannot="act on it, or change policy because of it",
            requires=("P06",), cost=Cost.MEDIUM,
            detection="behaviour varies with the error magnitude at fixed "
                      "observation",
            provenance="DECOMPOSED from B5 metacognicion · capa 2 · HEA-017 · "
                       "C-HEA-017-01 · `last_prediction_error` is computed and "
                       "governs nothing"),
    )


#: Conceptos del Mapa Global que NO produjeron primitiva, y por que. Un mapa
#: que solo lista lo que entro no deja comprobar el criterio de exclusion.
EXCLUDED = (
    ("use_planner / PLAN-A1",
     "contains a world model and a search over it: two identifiable functional "
     "capabilities inside one name"),
    ("use_world_model / WM-A1",
     "its minimal core is already P06 (observational) and P07 (action-"
     "conditioned); nothing primitive is left over"),
    ("use_temporal / TEMP-A1",
     "its minimal core is already P06; what remains, integration over a window, "
     "contains retention"),
    ("B6 impulsos modulares en competencia",
     "contains two reward functions and an arbitration between them. And with "
     "N=1 essential variable its experiment cannot be run at all: HEA-005 §3.3 "
     "fixes one variable and measures «the rest», and there is no rest"),
    ("capa 3 entera · competencia entre necesidades, perturbacion-respuesta, "
     "variedad requisita, clausura operacional, Markov blanket",
     "these lack substrate rather than primitiveness: a second essential "
     "variable, a perturbation operator, an enumerated state space. Not "
     "excluded for being too big -- excluded for having nothing to run on"),
)


#: Lo unico que el programa historico midio COMO composicion. Todo lleva
#: provenance HISTORICAL y el mundo donde se midio.
def edges_v01() -> tuple[Hyperedge, ...]:
    return (
        Hyperedge(
            id="H001", scope="campaign-a1f180b · frozen organism B+Q · 2x2 factorial cells, same budget and implementation",
            inputs=frozenset({"P03", "P04"}), world="W-level1-grid",
            output="E001", status=CompositionStatus.OBSERVED,
            evidence="frozen campaign a1f180b · 2x2 factorial H x M · 10 gates",
            note="superadditive interaction measured. WHICH degree of freedom "
                 "widened was never this campaign's question: dof_status is "
                 "NOT_MEASURED, which is not a delta of zero",
            provenance="HISTORICAL"),
        Hyperedge(
            id="H002", scope="campaign-02d5c43 · organism B+Q+H+M · ten-gate protocol",
            inputs=frozenset({"PSI_UNIDENTIFIED"}), world="W-level1-grid",
            output=NONE_OUTPUT, status=CompositionStatus.NO_EFFECT,
            evidence="frozen campaign 02d5c43 · gate RB-7 total dependence",
            note="psi alone contributes exactly zero. The identity of psi is "
                 "UNKNOWN: level 1.4's oracle uses the symbol for an "
                 "experimental bijection NOT given to the agent, and equating "
                 "the two would be convenience, not evidence",
            provenance="HISTORICAL"),
        Hyperedge(
            id="H003", scope="campaign-02d5c43 · organism B+Q+H+M · ten-gate protocol",
            inputs=frozenset({"PSI_UNIDENTIFIED", "P04"}),
            world="W-level1-grid", output="E002",
            status=CompositionStatus.OBSERVED,
            evidence="frozen campaign 02d5c43 · ten gates green",
            note="psi needs M UNDER THIS SCOPE. With H002 this is the pattern "
                 "NO_EFFECT is for: the pair works and one half alone does "
                 "not. That the two are matched on organism, budget and "
                 "implementation is asserted by the campaign's own ablation "
                 "gate RB-7 and was NOT re-verified here",
            provenance="HISTORICAL"),
        Hyperedge(
            id="H004", scope="campaign-6cf55a4 · same organism, budget and instrument; the twins differ ONLY in the world transition",
            inputs=frozenset({"P06", "P07"}), world="W-level17-twin-A",
            output="E003", status=CompositionStatus.OBSERVED,
            evidence="frozen campaign 6cf55a4 · 16/16 pairs · 13/13 gates",
            note="dof_status NOT_MEASURED for the same reason as H001",
            provenance="HISTORICAL"),
        Hyperedge(
            id="H005", scope="campaign-6cf55a4 · same organism, budget and instrument; the twins differ ONLY in the world transition",
            inputs=frozenset({"P06", "P07"}), world="W-level17-twin-B",
            output=NONE_OUTPUT, status=CompositionStatus.NO_EFFECT,
            evidence="frozen campaign 6cf55a4 · I_B(A;O'|O) = 0 EXACTLY, with "
                     "T_B(s'|s,a) = 1/4 sum_b T_A(s'|s,b)",
            note="the same composition as H004 in a world where the act does "
                 "not move the transition. NOT a contradiction of H004: two "
                 "conditions, which is why the world travels with the edge",
            provenance="HISTORICAL"),
        Hyperedge(
            id="H006", scope="campaign-9b7bdb0 · round C",
            inputs=frozenset({"P04", "P06", "P07"}),
            world="W-level18", output="E004", status=CompositionStatus.UNKNOWN,
            note="the campaign that would have settled this is a FAMILY_MISMATCH: "
                 "the oracle sealed Z_{t+1} = F(Z_t, A_t, O_{t+1}) and what ran "
                 "was the degenerate Z_{t+1} = F(Z_t, A_t), 0/400 differences "
                 "under varying observations. It did not falsify the "
                 "composition -- it measured a different one",
            provenance="HISTORICAL"),
    )
