"""What a task demands, written down before anybody names a capability.

`A3a` compared two mechanism signatures.  This compares nothing: it reads a
task and asks what the task, by its own structure, makes hard.  The two are
different questions and the second is the one a level designer faces first.

The rule the previous unit taught, and the reason this one is built the way it
is: **a structural feature is not a demand.**  Recursion did not imply that
histories must stay apart; a constraint had to say so.  The same trap is
waiting here, in a shape that is even more convincing:

    encoder_adaptive and decoder_adaptive  ->  they must learn to coordinate

They need not.  Two components can learn at the same time and never have to
agree about anything, and a rule that cannot tell those apart would fill the
graph with a coordination demand no task ever made.  What licenses the demand
is a third fact -- that performance depends on their *compatibility*, not on
each separately -- and that fact is declared, not inferred.

So a `TaskContract` holds functional facts and nothing else: how much
information arrives, how much survives, when each thing happens, which parts
can change, whose meaning was supplied, and what performance actually depends
on.  It contains no capability names.  It cannot: a contract that already
knew which capability the task needs would be the answer wearing the
question's clothes.

Nine refusals live in the constructor, because a task that cannot be written
down is a task that cannot exist:

    bits below zero                         information is not negative
    a response before its question          answers do not precede asking
    feedback before the response            nor does its judgement
    a signal before the decision it judges  nor does a retention's credit
    the query in hand, relevance unknown    you are holding the question
    adaptive with its meaning supplied      nothing left to adapt
    compatibility without both components   there is nothing to be compatible
    an outcome of an unreachable alternative there is nothing whose outcome
                                            that would be

**Two clocks, not one.**  `feedback_time` judges the response.
`retention_credit_signal_time` is when something attributable to the
*retention* arrives, and they come apart: a judgement glued to the answer can
still be far from the decision one wants to credit.  Only the second distance
was ever what delayed credit meant.

**And an instrument is not a solution.**  This module briefly held that
counterfactual replay dissolved delayed credit.  It does not: being able to
re-run the situation buys nothing if the alternative cannot be brought about,
its outcome cannot be seen, or the result cannot be assigned to the choice.
So replay no longer touches the delay at all; with all four conditions it
derives that a *direct credit instrument exists*, which is a different and
much weaker thing to say.

What comes out is typed, and the typing is load-bearing.  A `TASK_PRESSURE`
is a property of the task: it can exist with no mechanism anywhere able to
answer it, so it can never reach `acquisition_candidates`.  Reading a
pressure as a capability the organism must acquire is how the question stops
being a question.

Everything this module emits is `HYPOTHESIS`, with
`DERIVED_FROM_TASK_CONTRACT` as origin, and both are refused in the
constructor rather than asked for in a review.  A task's structure can say
what is hard.  It cannot say what an organism needs, and the distance between
those two is the whole programme.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Mapping

from terrario.lab.relation_ledger import EvidenceClass, HypothesisOrigin

SCHEMA_VERSION = "terrario.lab.task-contract/v1"


class ContractRefused(ValueError):
    """A task that cannot be written down, and why."""


class RoleNature(StrEnum):
    """Whether a role is something the task imposes or something that can learn.

    `T3`'s whole point: a bottleneck with a fixed encoder has the pressure and
    cannot have the policy.  Collapsing the two would read "this is hard" as
    "something here can be learned", which is the step that turns a task
    description into an unearned training plan.
    """

    TASK_PRESSURE = "TASK_PRESSURE"
    LEARNABLE_CONTROL = "LEARNABLE_CONTROL"
    #: Que dos partes tengan que encajar no es una presion sobre el organismo
    #: ni algo que una sola de ellas pueda aprender; es una exigencia sobre la
    #: pareja, y puede no tener dueno.
    COORDINATION_REQUIREMENT_CANDIDATE = "COORDINATION_REQUIREMENT_CANDIDATE"
    #: Ni exigencia ni presion: un instrumento que existe. Decir que existe no
    #: es decir que el problema que podria resolver esta resuelto.
    AVAILABLE_INSTRUMENT = "AVAILABLE_INSTRUMENT"


class DerivedRoleKind(StrEnum):
    """Abstract demands.  Resolving one to a capability is not this layer."""

    CAPACITY_CONSTRAINED_RETENTION = "CAPACITY_CONSTRAINED_RETENTION"
    FUTURE_RELEVANCE_UNCERTAINTY = "FUTURE_RELEVANCE_UNCERTAINTY"
    SELECTIVE_RETENTION_PRESSURE = "SELECTIVE_RETENTION_PRESSURE"
    ADAPTIVE_RETENTION_POLICY = "ADAPTIVE_RETENTION_POLICY"
    DELAYED_CREDIT_TO_RETENTION = "DELAYED_CREDIT_TO_RETENTION"
    DIRECT_RETENTION_CREDIT_AVAILABLE = "DIRECT_RETENTION_CREDIT_AVAILABLE"
    COORDINATION_PRESSURE = "COORDINATION_PRESSURE"


NATURE: dict[DerivedRoleKind, RoleNature] = {
    DerivedRoleKind.CAPACITY_CONSTRAINED_RETENTION: RoleNature.TASK_PRESSURE,
    DerivedRoleKind.FUTURE_RELEVANCE_UNCERTAINTY: RoleNature.TASK_PRESSURE,
    DerivedRoleKind.SELECTIVE_RETENTION_PRESSURE: RoleNature.TASK_PRESSURE,
    DerivedRoleKind.DELAYED_CREDIT_TO_RETENTION: RoleNature.TASK_PRESSURE,
    DerivedRoleKind.ADAPTIVE_RETENTION_POLICY: RoleNature.LEARNABLE_CONTROL,
    DerivedRoleKind.COORDINATION_PRESSURE:
        RoleNature.COORDINATION_REQUIREMENT_CANDIDATE,
    DerivedRoleKind.DIRECT_RETENTION_CREDIT_AVAILABLE: RoleNature.AVAILABLE_INSTRUMENT,
}


@dataclass(frozen=True, kw_only=True)
class TaskContract:
    """Functional facts about a task.  No capability names, by construction.

    Times are abstract ticks with no unit.  Only their order is read, and
    making them explicit is what keeps `query_after_retention` from becoming
    an independent boolean somebody can set inconsistently with the rest.
    """

    label: str

    #: Cuánta información trae la fuente, y cuánta sobrevive al canal.
    source_information_bits: float
    retention_capacity_bits: float

    #: Si se sabe qué hará falta ANTES de decidir qué se guarda.
    relevance_known_before_retention: bool

    retention_time: int
    query_time: int
    response_time: int
    feedback_time: int

    encoder_adaptive: bool
    decoder_adaptive: bool

    #: Que algo esté fijo no implica que su significado se haya dado: una
    #: proyección aleatoria fija no es adaptativa y nadie dijo qué codifica.
    encoder_semantics_given: bool
    decoder_semantics_given: bool

    performance_depends_on_encoder: bool
    performance_depends_on_decoder: bool
    performance_depends_on_compatibility: bool

    #: Cuando llega una senal ATRIBUIBLE a esta decision de retencion. No es
    #: `feedback_time`: el juicio de la respuesta y el credito de la retencion
    #: son dos temporalidades distintas, y confundirlas hace que un feedback
    #: inmediato a la respuesta parezca resolver un credito que sigue lejos.
    retention_credit_signal_time: int
    feedback_is_attributable_to_that_retention: bool

    counterfactual_replay_allowed: bool
    alternative_retention_can_be_intervened: bool
    outcome_of_alternative_is_observable: bool

    def __post_init__(self) -> None:
        if not str(self.label).strip():
            raise ContractRefused("a contract needs a label, even though nothing reads it")
        for campo in ("source_information_bits", "retention_capacity_bits"):
            if getattr(self, campo) < 0:
                raise ContractRefused(f"{self.label}: {campo} is negative; "
                                      f"information does not come in below zero")
        if self.response_time < self.query_time:
            raise ContractRefused(
                f"{self.label}: the response precedes the query it answers")
        if self.feedback_time < self.response_time:
            raise ContractRefused(
                f"{self.label}: feedback precedes the response it judges")
        if self.query_time <= self.retention_time \
                and not self.relevance_known_before_retention:
            raise ContractRefused(
                f"{self.label}: the query is already in hand when retention is "
                f"decided, so relevance cannot also be unknown")
        for parte in ("encoder", "decoder"):
            if getattr(self, f"{parte}_adaptive") \
                    and getattr(self, f"{parte}_semantics_given"):
                raise ContractRefused(
                    f"{self.label}: the {parte} is adaptive and its meaning was "
                    f"supplied; there is nothing left for it to adapt")
        if self.retention_credit_signal_time < self.retention_time:
            raise ContractRefused(
                f"{self.label}: a signal about a retention arrives before the "
                f"retention it is about")
        if self.outcome_of_alternative_is_observable \
                and not self.alternative_retention_can_be_intervened:
            raise ContractRefused(
                f"{self.label}: the outcome of an alternative retention is "
                f"observable and the alternative cannot be brought about; there "
                f"is nothing whose outcome that would be")
        if self.performance_depends_on_compatibility and not (
                self.performance_depends_on_encoder
                and self.performance_depends_on_decoder):
            raise ContractRefused(
                f"{self.label}: performance depends on compatibility between two "
                f"components and not on both of them; there is nothing to be "
                f"compatible with")

    # --- hechos derivados, para que nadie los declare aparte ni al revés ---

    @property
    def is_bottleneck(self) -> bool:
        return self.source_information_bits > self.retention_capacity_bits

    @property
    def query_after_retention(self) -> bool:
        return self.query_time > self.retention_time

    @property
    def feedback_after_retention(self) -> bool:
        return self.feedback_time > self.retention_time

    @property
    def retention_credit_delay(self) -> int:
        """Lo que separa decidir de enterarse, que no es lo mismo que responder
        y enterarse."""
        return self.retention_credit_signal_time - self.retention_time

    def as_record(self) -> Mapping[str, Any]:
        return {"schema_version": SCHEMA_VERSION, "label": self.label,
                "source_information_bits": self.source_information_bits,
                "retention_capacity_bits": self.retention_capacity_bits,
                "relevance_known_before_retention": self.relevance_known_before_retention,
                "retention_time": self.retention_time, "query_time": self.query_time,
                "response_time": self.response_time, "feedback_time": self.feedback_time,
                "encoder_adaptive": self.encoder_adaptive,
                "decoder_adaptive": self.decoder_adaptive,
                "encoder_semantics_given": self.encoder_semantics_given,
                "decoder_semantics_given": self.decoder_semantics_given,
                "performance_depends_on_encoder": self.performance_depends_on_encoder,
                "performance_depends_on_decoder": self.performance_depends_on_decoder,
                "performance_depends_on_compatibility":
                    self.performance_depends_on_compatibility,
                "retention_credit_signal_time": self.retention_credit_signal_time,
                "feedback_is_attributable_to_that_retention":
                    self.feedback_is_attributable_to_that_retention,
                "counterfactual_replay_allowed": self.counterfactual_replay_allowed,
                "alternative_retention_can_be_intervened":
                    self.alternative_retention_can_be_intervened,
                "outcome_of_alternative_is_observable":
                    self.outcome_of_alternative_is_observable,
                "retention_credit_delay": self.retention_credit_delay,
                "is_bottleneck": self.is_bottleneck,
                "query_after_retention": self.query_after_retention}


@dataclass(frozen=True)
class DerivedRole:
    """One demand the task's structure makes, and never more than a hypothesis."""

    kind: DerivedRoleKind
    rationale: str
    falsification_question: str
    evidence: EvidenceClass = EvidenceClass.HYPOTHESIS
    origin: HypothesisOrigin = HypothesisOrigin.DERIVED_FROM_TASK_CONTRACT

    def __post_init__(self) -> None:
        if self.evidence is not EvidenceClass.HYPOTHESIS:
            raise ContractRefused(
                f"{self.kind.value} claims {self.evidence.value}; a task's structure "
                f"says what is hard, and nothing was run to find out")
        if self.origin is not HypothesisOrigin.DERIVED_FROM_TASK_CONTRACT:
            raise ContractRefused(
                f"{self.kind.value} hides where it came from; a role read off a "
                f"contract must say so or it will later read as someone's finding")

    @property
    def nature(self) -> RoleNature:
        return NATURE[self.kind]

    def as_record(self) -> Mapping[str, Any]:
        return {"role": self.kind.value, "nature": self.nature.value,
                "rationale": self.rationale,
                "falsification_question": self.falsification_question,
                "evidence": self.evidence.value, "origin": self.origin.value}


@dataclass(frozen=True)
class TaskRoleDerivation:
    contract: str
    derived: tuple[DerivedRole, ...]
    schema_version: str = SCHEMA_VERSION

    @property
    def roles(self) -> tuple[DerivedRoleKind, ...]:
        return tuple(sorted({r.kind for r in self.derived}, key=lambda k: k.value))

    def of_nature(self, nature: RoleNature) -> tuple[DerivedRoleKind, ...]:
        return tuple(k for k in self.roles if NATURE[k] is nature)

    @property
    def pressures(self) -> tuple[DerivedRoleKind, ...]:
        """What the task imposes.  Nobody has to be able to answer it."""
        return self.of_nature(RoleNature.TASK_PRESSURE)

    @property
    def controls(self) -> tuple[DerivedRoleKind, ...]:
        return self.of_nature(RoleNature.LEARNABLE_CONTROL)

    @property
    def coordination_requirements(self) -> tuple[DerivedRoleKind, ...]:
        return self.of_nature(RoleNature.COORDINATION_REQUIREMENT_CANDIDATE)

    @property
    def instruments(self) -> tuple[DerivedRoleKind, ...]:
        return self.of_nature(RoleNature.AVAILABLE_INSTRUMENT)

    @property
    def acquisition_candidates(self) -> tuple[DerivedRoleKind, ...]:
        """The only roles anything downstream may read as something to acquire.

        A pressure is a property of the task, and a task can impose one with
        no mechanism in existence able to answer it.  Reading a pressure as a
        capability the organism must acquire is how the question stops being
        a question, so pressures cannot reach this list at all.
        """
        return self.controls

    def as_record(self) -> Mapping[str, Any]:
        return {"schema_version": self.schema_version, "contract": self.contract,
                "roles": [k.value for k in self.roles],
                "pressures": [k.value for k in self.pressures],
                "controls": [k.value for k in self.controls],
                "coordination_requirements":
                    [k.value for k in self.coordination_requirements],
                "instruments": [k.value for k in self.instruments],
                "acquisition_candidates": [k.value for k in self.acquisition_candidates],
                "derived": [r.as_record() for r in self.derived]}


def derive_roles(contract: TaskContract) -> TaskRoleDerivation:
    """What the task makes hard, read off its structure and nothing else."""
    salida: list[DerivedRole] = []

    def anotar(kind: DerivedRoleKind, rationale: str, question: str) -> None:
        salida.append(DerivedRole(kind=kind, rationale=rationale,
                                  falsification_question=question))

    capacidad = contract.is_bottleneck
    if capacidad:
        anotar(DerivedRoleKind.CAPACITY_CONSTRAINED_RETENTION,
               f"{contract.source_information_bits} bits arrive and "
               f"{contract.retention_capacity_bits} survive, so something is dropped",
               "does the task still hold if the channel carries everything?")

    # Que el constructo pida distinguir futuros no basta: hace falta que no
    # se sepa todavia cual. Una consulta posterior con la relevancia ya
    # fijada es compresion, no adivinanza, y confundirlas convertiria todo
    # cuello de botella en un problema epistemico.
    incierto = (not contract.relevance_known_before_retention
                and contract.query_after_retention)
    if incierto:
        anotar(DerivedRoleKind.FUTURE_RELEVANCE_UNCERTAINTY,
               "what will be asked is not settled when retention is decided, "
               "so what is kept has to be bet rather than read off the question",
               "is what will matter already determined before anything is stored?")

    # Y la incertidumbre sola tampoco cuesta nada si cabe todo. La presion
    # necesita las dos: hay que tirar algo Y no se sabe que hara falta.
    selectiva = capacidad and incierto
    if selectiva:
        anotar(DerivedRoleKind.SELECTIVE_RETENTION_PRESSURE,
               "not everything fits and what will matter is not settled, so "
               "which part survives changes the outcome",
               "can the task be solved keeping an arbitrary subset of the same size?")

    # La presion no es una politica. Con el encoder fijo todo el ingrediente
    # de la dificultad esta presente y no hay nada con que aprender una, y
    # leer lo primero como lo segundo es como una descripcion de tarea se
    # convierte en un plan de entrenamiento que nadie gano.
    if selectiva and contract.encoder_adaptive \
            and contract.performance_depends_on_encoder:
        anotar(DerivedRoleKind.ADAPTIVE_RETENTION_POLICY,
               "what is kept can change with experience and performance depends "
               "on which part it is",
               "does holding the encoder at its initial mapping cost anything?")

    # Que haya aprendizaje sobre la retencion no hace diferido el credito: lo
    # hace la distancia entre DECIDIR y recibir una senal atribuible a esa
    # decision. Y esa distancia no es la del feedback sobre la respuesta: un
    # juicio que llega pegado a la respuesta puede seguir a mucha distancia de
    # la retencion que queremos acreditar.
    #
    # El replay contrafactual NO aparece aqui. Poder repetir la situacion es
    # un instrumento, no un credito resuelto: si la recompensa sigue llegando
    # mucho despues, o no se sabe que parte del resultado se debe a la
    # retencion, el problema temporal sigue entero. Esa conjuncion se afirmo
    # antes de tiempo y se retiro.
    if contract.retention_credit_delay > 0 and contract.encoder_adaptive \
            and contract.performance_depends_on_encoder:
        anotar(DerivedRoleKind.DELAYED_CREDIT_TO_RETENTION,
               f"a signal attributable to the retention arrives "
               f"{contract.retention_credit_delay} apart from the decision it "
               f"would credit, and something is trying to learn from it",
               "does a signal about a retention reach it while it is still being made?")

    # Y el instrumento, cuando esta entero. Las cuatro cosas hacen falta:
    # poder repetir, poder poner otra retencion, poder ver como acaba, y poder
    # atribuirle el resultado. Con tres de las cuatro no hay nada que medir.
    if contract.counterfactual_replay_allowed \
            and contract.alternative_retention_can_be_intervened \
            and contract.outcome_of_alternative_is_observable \
            and contract.feedback_is_attributable_to_that_retention:
        anotar(DerivedRoleKind.DIRECT_RETENTION_CREDIT_AVAILABLE,
               "the situation can be re-run with a different retention, the other "
               "outcome can be seen, and the result can be assigned to the choice",
               "does re-running with another retention yield a difference that can "
               "be attributed to it?")

    # Dos partes adaptativas no tienen por que coordinarse: pueden aprender a
    # la vez y no deberse nada. Lo que exige la coordinacion es que el
    # rendimiento dependa de que ENCAJEN, y ese hecho se declara. Y al reves,
    # que dependa de que encajen con una sola parte movil es adaptarse a un
    # blanco fijo, que no es que dos aprendan a ponerse de acuerdo.
    if contract.encoder_adaptive and contract.decoder_adaptive \
            and contract.performance_depends_on_compatibility:
        anotar(DerivedRoleKind.COORDINATION_PRESSURE,
               "both halves can move and performance depends on the pair fitting, "
               "so neither can be settled against a target that is standing still",
               "does performance depend on the pair rather than on each alone?")

    return TaskRoleDerivation(contract=contract.label, derived=tuple(salida))
