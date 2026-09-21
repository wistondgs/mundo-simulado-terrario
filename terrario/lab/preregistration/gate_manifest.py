"""What each gate certifies, frozen before the run that evaluates it.

The rail already seals metrics and endpoints.  A gate is neither: an endpoint is
*what gets measured*, a gate is *what stands certified if the number falls on the
right side*.  Nothing sealed that, and the consequence was measured.

In `organism-fusion-hm-01` the preregistration gave `F-9` to passivity and listed
omitting the tick among the obligatory negative fixtures.  The runner evaluated
nine rows and used `F-9` for the tick.  Every number was true, the campaign
reported `VERIFIED`, and passivity silently left the inventory with its number
apparently covered -- a reader counting nine rows and seeing `F-0`..`F-9` would
conclude one was missing, not that one had been substituted.

Nothing could have caught it, because a gate's name and what it certifies were
written in the same place at the same moment: the run.  A pair that is authored
together cannot contradict itself.

So the identity is frozen separately and earlier, and `certifies` is a property
reference rather than prose -- prose would make the check hostage to rewording,
and the seal is the canonical payload, not its rendering.  The run reports which
property each gate certified; the seal says which it must have.  They are
compared by identity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from terrario.lab.persistence.canonical import content_hash, plain

GATE_MANIFEST_SCHEMA = "terrario.lab.preregistration-gate-manifest/v1"
GATE_OUTCOME_SCHEMA = "terrario.lab.gate-outcome/v1"


class GateManifestError(ValueError):
    """A manifest that cannot be sealed.  Raised at build time, never at run time."""


@dataclass(frozen=True)
class SealedGate:
    """One gate, as promised before any code ran.

    `certifies` is an identifier and `statement` is its human rendering.  Keeping
    them apart is what makes the later comparison exact: rewording the statement
    is a documentation change, while changing what the gate certifies is a
    different gate and must be seen as one.
    """

    gate_id: str
    certifies: str
    certifies_revision: str
    statement: str
    criterion: str
    negative_fixture: str
    instrument_ref: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        for name in ("gate_id", "certifies", "certifies_revision", "statement",
                     "criterion", "negative_fixture"):
            if not str(getattr(self, name)).strip():
                raise GateManifestError(f"sealed gate requires a non-empty {name}")
        # The project's own rule, from every oracle in both lineages: a gate whose
        # only possible behaviour is PASS is not a gate.  Sealing the fixture with
        # the gate is what stops it from being supplied after seeing the result.
        object.__setattr__(self, "instrument_ref",
                           dict(self.instrument_ref) if self.instrument_ref else None)

    @property
    def property_identity(self) -> tuple[str, str]:
        return (self.certifies, self.certifies_revision)

    def payload(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id, "certifies": self.certifies,
            "certifies_revision": self.certifies_revision, "statement": self.statement,
            "criterion": self.criterion, "negative_fixture": self.negative_fixture,
            "instrument_ref": plain(self.instrument_ref) if self.instrument_ref else None,
        }

    @property
    def semantic_id(self) -> str:
        return "GATE-" + content_hash(self.payload())[:16]


@dataclass(frozen=True)
class GateManifest:
    """The sealed inventory.  Its size is a promise, not a report."""

    gates: tuple[SealedGate, ...]
    schema_version: str = GATE_MANIFEST_SCHEMA

    def __post_init__(self) -> None:
        object.__setattr__(self, "gates", tuple(self.gates))
        if not self.gates:
            raise GateManifestError("a gate manifest with no gates certifies nothing")
        seen: dict[str, SealedGate] = {}
        for gate in self.gates:
            if gate.gate_id in seen:
                raise GateManifestError(f"duplicate gate id {gate.gate_id!r}")
            seen[gate.gate_id] = gate
        properties: dict[tuple[str, str], str] = {}
        for gate in self.gates:
            previous = properties.get(gate.property_identity)
            if previous is not None:
                # Two numbers for one property is how an inventory grows a row
                # that certifies nothing new -- and how a count stays plausible
                # while a property drops out.
                raise GateManifestError(
                    f"{gate.gate_id} and {previous} both certify "
                    f"{gate.certifies}@{gate.certifies_revision}")
            properties[gate.property_identity] = gate.gate_id

    def by_id(self) -> dict[str, SealedGate]:
        return {gate.gate_id: gate for gate in self.gates}

    def payload(self) -> dict[str, Any]:
        return {"schema_version": self.schema_version,
                "gates": [gate.payload() for gate in self.gates]}

    @property
    def manifest_hash(self) -> str:
        return content_hash(self.payload())


@dataclass(frozen=True)
class GateOutcome:
    """What a run reports for one gate.

    It carries the property it believes it certified.  Requiring the runner to
    restate it is the whole mechanism: a runner that only reported `passed` could
    not be caught disagreeing with the seal.
    """

    gate_id: str
    certifies: str
    certifies_revision: str
    passed: bool
    evidence: str
    negative_fixture_fell: bool | None = None
    schema_version: str = GATE_OUTCOME_SCHEMA

    def payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version, "gate_id": self.gate_id,
            "certifies": self.certifies, "certifies_revision": self.certifies_revision,
            "passed": self.passed, "evidence": self.evidence,
            "negative_fixture_fell": self.negative_fixture_fell,
        }


@dataclass(frozen=True)
class GateReconciliation:
    """Whether a run's inventory is the one that was sealed.

    Deliberately not a boolean: `consistent` answers whether the run evaluated
    the promised gates under the promised meanings, which is a different question
    from whether they passed.  A campaign can be perfectly consistent and
    negative, and that is a publishable result.
    """

    consistent: bool
    failures: tuple[str, ...] = ()
    unproven_fixtures: tuple[str, ...] = ()
    manifest_hash: str = ""
    evaluated: int = 0
    sealed: int = 0

    def as_record(self) -> dict[str, Any]:
        return {"consistent": self.consistent, "failures": list(self.failures),
                "unproven_fixtures": list(self.unproven_fixtures),
                "manifest_hash": self.manifest_hash,
                "evaluated": self.evaluated, "sealed": self.sealed}


def reconcile(manifest: GateManifest,
              outcomes: Sequence[GateOutcome]) -> GateReconciliation:
    """Compare a run's gate inventory against the sealed one.

    Every disagreement gets its own code, because "the inventory does not match"
    is exactly the message that let the fusion's substitution pass as a missing
    row.  What failed has to name itself.
    """
    sealed = manifest.by_id()
    failures: list[str] = []
    unproven: list[str] = []
    reported: set[str] = set()

    for outcome in outcomes:
        if outcome.gate_id in reported:
            failures.append(f"GATE_REPORTED_TWICE:{outcome.gate_id}")
            continue
        reported.add(outcome.gate_id)
        promise = sealed.get(outcome.gate_id)
        if promise is None:
            failures.append(f"GATE_NOT_SEALED:{outcome.gate_id}")
            continue
        if (outcome.certifies, outcome.certifies_revision) != promise.property_identity:
            # The fusion's F-9, stated as a machine can see it.
            failures.append(
                f"GATE_CERTIFIES_MISMATCH:{outcome.gate_id}:"
                f"sealed={promise.certifies}@{promise.certifies_revision}:"
                f"run={outcome.certifies}@{outcome.certifies_revision}")
            continue
        if not str(outcome.evidence).strip():
            failures.append(f"GATE_EVIDENCE_ABSENT:{outcome.gate_id}")
        if outcome.negative_fixture_fell is None:
            unproven.append(outcome.gate_id)
        elif not outcome.negative_fixture_fell:
            failures.append(f"GATE_NEGATIVE_FIXTURE_DID_NOT_FALL:{outcome.gate_id}")

    for gate_id in sealed:
        if gate_id not in reported:
            failures.append(f"SEALED_GATE_NOT_EVALUATED:{gate_id}")

    return GateReconciliation(
        consistent=not failures, failures=tuple(sorted(set(failures))),
        unproven_fixtures=tuple(sorted(set(unproven))),
        manifest_hash=manifest.manifest_hash,
        evaluated=len(reported), sealed=len(sealed))


def manifest_from_payload(payload: Mapping[str, Any]) -> GateManifest:
    """Rebuild from a sealed payload, recomputing identity rather than trusting it.

    Same discipline as `TheoryOperationalHyperedge.from_payload`: deserialisation
    that accepts a stored hash is a hash nobody checks.
    """
    if payload.get("schema_version") != GATE_MANIFEST_SCHEMA:
        raise GateManifestError("unsupported gate manifest schema")
    gates = tuple(
        SealedGate(
            gate_id=str(item["gate_id"]), certifies=str(item["certifies"]),
            certifies_revision=str(item["certifies_revision"]),
            statement=str(item["statement"]), criterion=str(item["criterion"]),
            negative_fixture=str(item["negative_fixture"]),
            instrument_ref=item.get("instrument_ref"),
        )
        for item in payload.get("gates", ())
    )
    manifest = GateManifest(gates=gates)
    if "manifest_hash" in payload and payload["manifest_hash"] != manifest.manifest_hash:
        raise GateManifestError("gate manifest hash does not match its content")
    return manifest
