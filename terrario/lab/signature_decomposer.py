"""Candidate functional roles, derived from what two signatures disagree about.

The decomposer must not know that `PREDSTATE` exists, that 1.8 happened, or
that `EVSENS` is a thing.  If it did, it would be a lookup table with a
derivation's manners, and the project has already seen how convincing those
look.

So it compares structure and emits **roles**, which are abstract:

    NEW_EVIDENCE_SENSITIVITY
    STATE_UPDATE_WITH_NEW_EVIDENCE
    HISTORY_CONDITIONAL_DISAMBIGUATION

Resolving a role to a capability in the inventory is a separate layer, and
keeping the two apart is the whole design.  A role that resolves to nothing is
still a finding: it says the catalogue has no name for something the structure
demands.

Three rules produce roles, and each is structural:

1. an argument the required signature has and the realised one does not, or
   has without causal participation, demands sensitivity to it;
2. that argument arriving alongside others demands their combination, because
   varying with something is not the same as folding it into a state;
3. and if the signature is recursive **and the construct requires that two
   admissible histories with the same present remain distinguishable**,
   disambiguation becomes a candidate too.

The third rule used to fire on recursion alone, and that was an
over-derivation.  `Z' = Z + O` is recursive and accumulates history without
demanding that two histories stay apart; deriving a precursor from it would
populate the graph with a requirement the specification never made.  So the
signature says what enters and leaves, a `FunctionalConstraint` says which
differences those variables must preserve, and only the second licenses this
role.

Argument **names carry nothing**.  Roles do.  Renaming every argument while
preserving roles produces an identical derivation, which is what stops the
decomposer from keying on the vocabulary of one campaign.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Mapping

SCHEMA_VERSION = "terrario.lab.signature-decomposer/v1"


class ArgumentRole(StrEnum):
    """What an argument is, independent of what it is called."""

    PRIOR_STATE = "PRIOR_STATE"
    ACTION = "ACTION"
    NEW_OBSERVATION = "NEW_OBSERVATION"
    PRIOR_OBSERVATION = "PRIOR_OBSERVATION"
    REWARD = "REWARD"
    CONTEXT = "CONTEXT"
    OTHER = "OTHER"


class OutputRole(StrEnum):
    NEXT_STATE = "NEXT_STATE"
    PREDICTION = "PREDICTION"
    ACTION_CHOICE = "ACTION_CHOICE"
    VALUE = "VALUE"
    OTHER = "OTHER"


#: Salidas que vuelven a entrar: la firma es recursiva y el estado se arrastra.
RECURSIVE_PAIRS: dict[OutputRole, ArgumentRole] = {
    OutputRole.NEXT_STATE: ArgumentRole.PRIOR_STATE,
}


class FunctionalConstraint(StrEnum):
    """What differences the variables must preserve, beyond who enters.

    A signature fixes arity and roles.  It cannot say that two admissible
    histories sharing a present must lead to different futures -- that is a
    property of the construct, and it is what separates "there is state" from
    "the state has to distinguish".
    """

    #: Exists h1, h2 with the same observable present and different required
    #: future.  Collapsing them loses the construct.
    HISTORY_DISTINGUISHABILITY = "HISTORY_DISTINGUISHABILITY"
    #: The output must vary within a single step, not only across them.
    WITHIN_STEP_SENSITIVITY = "WITHIN_STEP_SENSITIVITY"


class FunctionalRole(StrEnum):
    """Abstract demands, not capability names."""

    NEW_EVIDENCE_SENSITIVITY = "NEW_EVIDENCE_SENSITIVITY"
    STATE_UPDATE_WITH_NEW_EVIDENCE = "STATE_UPDATE_WITH_NEW_EVIDENCE"
    HISTORY_CONDITIONAL_DISAMBIGUATION = "HISTORY_CONDITIONAL_DISAMBIGUATION"


class DiscrepancyKind(StrEnum):
    MISSING_INPUT = "MISSING_INPUT"
    MISSING_CAUSAL_PARTICIPATION = "MISSING_CAUSAL_PARTICIPATION"
    REQUIRED_COMBINATION = "REQUIRED_COMBINATION"


class SignatureError(ValueError):
    pass


@dataclass(frozen=True)
class Argument:
    name: str
    role: ArgumentRole

    def __post_init__(self) -> None:
        if not str(self.name).strip():
            raise SignatureError("an argument needs a name, even though nothing reads it")


@dataclass(frozen=True)
class FunctionalSignature:
    """What a mechanism family takes and produces, by role.

    `causal_participation` is optional and, when given, says which roles
    actually influence the output.  An argument present in the signature and
    absent here is 1.8's defect exactly: the observation was in the routing key
    and never discriminated.
    """

    label: str
    output: OutputRole
    arguments: tuple[Argument, ...]
    causal_participation: frozenset[ArgumentRole] | None = None
    #: Lo que la firma no puede decir: qué diferencias deben preservarse.
    constraints: frozenset[FunctionalConstraint] = frozenset()

    def __post_init__(self) -> None:
        object.__setattr__(self, "arguments", tuple(self.arguments))
        object.__setattr__(self, "constraints", frozenset(self.constraints))
        roles = [a.role for a in self.arguments]
        if len(set(roles)) != len(roles):
            raise SignatureError(f"{self.label}: two arguments share one role")
        if self.causal_participation is not None:
            object.__setattr__(self, "causal_participation",
                               frozenset(self.causal_participation))
            ajenas = self.causal_participation - set(roles)
            if ajenas:
                raise SignatureError(
                    f"{self.label}: {sorted(r.value for r in ajenas)} participate "
                    f"without being arguments")

    @property
    def roles(self) -> frozenset[ArgumentRole]:
        return frozenset(a.role for a in self.arguments)

    @property
    def participating(self) -> frozenset[ArgumentRole]:
        """Roles that actually influence the output; all of them unless stated."""
        return self.roles if self.causal_participation is None else self.causal_participation

    @property
    def is_recursive(self) -> bool:
        return RECURSIVE_PAIRS.get(self.output) in self.roles


@dataclass(frozen=True)
class Discrepancy:
    kind: DiscrepancyKind
    role: ArgumentRole | None
    detail: str

    def as_record(self) -> Mapping[str, Any]:
        return {"kind": self.kind.value,
                "role": self.role.value if self.role else None,
                "detail": self.detail}


@dataclass(frozen=True)
class RoleCandidate:
    """A functional demand the realised family does not meet."""

    role: FunctionalRole
    about: ArgumentRole
    rationale: str
    falsification_question: str

    def as_record(self) -> Mapping[str, Any]:
        return {"functional_role": self.role.value, "about": self.about.value,
                "rationale": self.rationale,
                "falsification_question": self.falsification_question}


@dataclass(frozen=True)
class Decomposition:
    required: str
    realized: str
    discrepancies: tuple[Discrepancy, ...]
    candidates: tuple[RoleCandidate, ...]
    schema_version: str = SCHEMA_VERSION

    @property
    def roles(self) -> tuple[FunctionalRole, ...]:
        """Sorted, so nothing downstream inherits an order nobody chose."""
        return tuple(sorted({c.role for c in self.candidates}, key=lambda r: r.value))

    def as_record(self) -> Mapping[str, Any]:
        return {"schema_version": self.schema_version, "required": self.required,
                "realized": self.realized,
                "discrepancies": [d.as_record() for d in self.discrepancies],
                "candidates": [c.as_record() for c in self.candidates],
                "roles": [r.value for r in self.roles]}


def decompose(required: FunctionalSignature,
              realized: FunctionalSignature) -> Decomposition:
    """Compare two signatures by role and emit what the difference demands.

    An argument the realised family has and the required one does not is not a
    finding: a mechanism may take more than it needs, and inventing a
    requirement from a spare argument would manufacture precursors out of
    generosity.
    """
    if required.output is not realized.output:
        raise SignatureError(
            f"signatures produce different things ({required.output.value} vs "
            f"{realized.output.value}); there is no discrepancy to derive, "
            f"they answer different questions")

    ausentes = sorted(required.roles - realized.roles, key=lambda r: r.value)
    sin_participar = sorted(
        (required.participating & realized.roles) - realized.participating,
        key=lambda r: r.value)

    discrepancias: list[Discrepancy] = []
    candidatos: list[RoleCandidate] = []

    for role in ausentes:
        discrepancias.append(Discrepancy(
            DiscrepancyKind.MISSING_INPUT, role,
            f"{role.value} is required and the realised family does not take it"))
    for role in sin_participar:
        discrepancias.append(Discrepancy(
            DiscrepancyKind.MISSING_CAUSAL_PARTICIPATION, role,
            f"{role.value} is taken and does not influence {required.output.value}"))

    faltantes = sorted(set(ausentes) | set(sin_participar), key=lambda r: r.value)
    presentes = sorted(realized.participating - set(faltantes), key=lambda r: r.value)

    for role in faltantes:
        candidatos.append(RoleCandidate(
            FunctionalRole.NEW_EVIDENCE_SENSITIVITY, role,
            rationale=(f"{required.output.value} must vary with {role.value}, and "
                       f"under the realised family it does not"),
            falsification_question=(
                f"holding everything else fixed, does {required.output.value} "
                f"differ when only {role.value} differs?")))
        if presentes:
            junto = " + ".join(r.value for r in presentes)
            discrepancias.append(Discrepancy(
                DiscrepancyKind.REQUIRED_COMBINATION, role,
                f"{required.output.value} must depend on {role.value} jointly "
                f"with {junto}"))
            candidatos.append(RoleCandidate(
                FunctionalRole.STATE_UPDATE_WITH_NEW_EVIDENCE, role,
                rationale=(f"varying with {role.value} is not folding it into "
                           f"{required.output.value} alongside {junto}"),
                falsification_question=(
                    f"does {required.output.value} depend on the combination of "
                    f"{role.value} and {junto}, rather than on either alone?")))

    # La tercera regla NO dispara por recursión sola, y ésa fue una
    # sobreafirmación corregida: `Z' = Z + O` es recursiva y acumula historia
    # sin exigir que dos historias sigan distinguibles. Hace falta además que
    # el constructo lo pida, y eso vive en las restricciones, no en la firma.
    if (faltantes and required.is_recursive
            and FunctionalConstraint.HISTORY_DISTINGUISHABILITY in required.constraints):
        candidatos.append(RoleCandidate(
            FunctionalRole.HISTORY_CONDITIONAL_DISAMBIGUATION, faltantes[0],
            rationale=("the construct requires two admissible histories with "
                       "the same present to remain distinguishable, and a "
                       "recursive state that collapses them loses it"),
            falsification_question=(
                "do two histories that differ only in the past separate, once "
                "the new argument participates?")))

    return Decomposition(required=required.label, realized=realized.label,
                         discrepancies=tuple(discrepancias),
                         candidates=tuple(candidatos))


def resolve_against_catalogue(decomposition: Decomposition,
                              vocabulary: Mapping[FunctionalRole, str],
                              inventory) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Roles to capability ids, and the roles the catalogue cannot name.

    Deliberately a separate step.  The decomposer derives demands; whether the
    project happens to have a word for one is a fact about the catalogue, and
    an unnamed role is a finding rather than a failure.
    """
    resueltos: list[str] = []
    sin_nombre: list[str] = []
    for role in decomposition.roles:
        capability = vocabulary.get(role)
        if capability is not None and capability in inventory:
            resueltos.append(capability)
        else:
            sin_nombre.append(role.value)
    return tuple(sorted(set(resueltos))), tuple(sorted(set(sin_nombre)))
