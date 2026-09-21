"""What a mechanism MEANS, with an identity, apart from the code that realises it.

`MetricSpec` already does this for the measuring side: it writes the conditional
form out rather than implying it, and carries an id and a version.  Nothing did
it for the other side.  A capability's mechanism lived as `algorithm_id` plus a
paragraph, so "what we are building" and "what class implements it" were the
same string, and two implementations of one mechanism were indistinguishable
from two mechanisms.

The split this module makes, and the reason for it:

    MechanismSpec       what the mechanism means -- formal, versioned
    AlgorithmBinding    which implementation realises it

Level 1.8 is why `degenerate_of` exists.  Its oracle sealed
`Z_{t+1} = F(Z_t, A_t, O_{t+1})`; what ran was `Z_{t+1} = F(Z_t, A_t)`, the
degenerate case with the observation dropped.  Every number it produced was
true, and it answered a different question than the one sealed.  A mechanism
that names the degenerate cases it must NOT collapse into makes that a
checkable claim instead of something found by reading the source a year later.

The registry is immutable per `(mechanism_id, version)`, the same rule the
versioned designs in `theory/factory.py` already enforce: re-registering an id
and version with different content is refused rather than overwritten.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from terrario.lab.persistence.canonical import content_hash, plain

SCHEMA_VERSION = "terrario.lab.mechanism-spec/v1"


class MechanismError(ValueError):
    """Base for refusals; each subclass carries a code a caller can act on."""

    code = "MECHANISM_ERROR"


class UnknownMechanism(MechanismError):
    code = "UNKNOWN_MECHANISM"


class MechanismVersionDrift(MechanismError):
    code = "MECHANISM_VERSION_DRIFT"


class MechanismSpecDrift(MechanismError):
    code = "MECHANISM_SPEC_DRIFT"


class MechanismImmutable(MechanismError):
    code = "MECHANISM_ALREADY_REGISTERED"


@dataclass(frozen=True)
class MechanismSpec:
    """The formal content of a mechanism, written out rather than implied.

    Deliberately says nothing about Python: no class name, no module, no
    `algorithm_id`.  If this dataclass could name the implementation, the
    distinction it exists to draw would collapse on the first use.
    """

    mechanism_id: str
    version: int
    semantic_definition: str
    #: The construction itself, written out.  `MetricSpec.conditional_form`
    #: carries the same instruction for metrics: state it, do not imply it.
    operational_form: str
    state_variables: tuple[str, ...]
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    invariants: tuple[str, ...]
    #: Forms this mechanism must NOT silently reduce to.  Level 1.8's sealed
    #: `F(Z, A, O)` and implemented `F(Z, A)` are exactly one such pair.
    degenerate_of: tuple[str, ...] = ()
    notes: str = ""
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        for name in ("mechanism_id", "semantic_definition", "operational_form"):
            if not str(getattr(self, name)).strip():
                raise MechanismError(f"a mechanism spec requires a non-empty {name}")
        if int(self.version) < 1:
            raise MechanismError("mechanism versions start at 1")
        if not self.outputs:
            raise MechanismError("a mechanism that produces nothing is not a mechanism")

    def payload(self) -> dict[str, Any]:
        return plain(self)

    @property
    def spec_hash(self) -> str:
        return content_hash(self.payload())

    @property
    def key(self) -> tuple[str, int]:
        return (self.mechanism_id, int(self.version))


@dataclass(frozen=True)
class MechanismRef:
    """A versioned pointer, resolved rather than believed.

    Same discipline as `instrument_registry.InstrumentRef`: carrying the hash
    alongside the id and version is what turns a silent edit of a registered
    mechanism into a refusal instead of a different experiment under the same
    name.
    """

    mechanism_id: str
    version: int
    spec_hash: str

    def as_record(self) -> dict[str, Any]:
        return {"mechanism_id": self.mechanism_id, "version": int(self.version),
                "spec_hash": self.spec_hash}

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> MechanismRef:
        return cls(str(record["mechanism_id"]), int(record["version"]),
                   str(record["spec_hash"]))

    @classmethod
    def to(cls, spec: MechanismSpec) -> MechanismRef:
        return cls(spec.mechanism_id, int(spec.version), spec.spec_hash)


REGISTRY: dict[tuple[str, int], MechanismSpec] = {}


def register(spec: MechanismSpec) -> MechanismSpec:
    """Immutable per (id, version).

    Re-registering identical content is a no-op so that importing a module
    twice is harmless; re-registering different content under the same version
    is refused, because that is how a mechanism changes meaning while every
    reference to it keeps pointing at the old promise.
    """
    existing = REGISTRY.get(spec.key)
    if existing is not None and existing.spec_hash != spec.spec_hash:
        raise MechanismImmutable(
            f"{spec.mechanism_id} v{spec.version} is registered with different "
            f"content; publish a new version instead of editing this one")
    REGISTRY[spec.key] = spec
    return spec


def resolve(ref: MechanismRef) -> MechanismSpec:
    """Fail closed, with a distinct code per way of being wrong.

    Three codes rather than one, because "the mechanism is unknown", "it exists
    at another version" and "it exists at this version and says something else"
    call for three different repairs.
    """
    by_id = [spec for (mid, _), spec in REGISTRY.items() if mid == ref.mechanism_id]
    if not by_id:
        raise UnknownMechanism(ref.mechanism_id)
    spec = REGISTRY.get((ref.mechanism_id, int(ref.version)))
    if spec is None:
        raise MechanismVersionDrift(
            f"{ref.mechanism_id} has no version {ref.version}; registered: "
            f"{sorted(s.version for s in by_id)}")
    if spec.spec_hash != ref.spec_hash:
        raise MechanismSpecDrift(
            f"{ref.mechanism_id} v{ref.version} content changed under its version")
    return spec
