"""The last door: may this number become scientific evidence?

Terrario had two registries answering that question and neither was the
authority.  `instrument_registry` knew what an instrument means scientifically
and had zero production callers; `metrics_observer` knew what the runtime can
observe and had no notion of whether it was certified.  Below both,
`EvidenceRecord(metrics: dict[str, float])` could bypass either.  The result
was that reportability was a property nobody enforced.

This module is the single boundary where the question is asked, and it asks it
again even when preregistration and runtime already did.  That redundancy is
the point: a gate that trusts its callers is documentation, not a gate.

What it deliberately does NOT do, because each was a way a false finding got in
before:

    it does not recompute a metric        -- that would let the gate disagree
                                             with the run it is admitting
    it does not modify a Reading          -- NOT_EVALUABLE never becomes 0.0
    it does not impute missingness        -- absent stays absent
    it does not reinterpret INVALID       -- broken data is not poor performance

It decides admission and returns why.  Nothing else.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Mapping

from terrario.lab import instrument_registry as authority
from terrario.lab.measurement_status import Status

ADMISSION_SCHEMA = "terrario.lab.evidence-admission/v1"

#: Endpoint roles that carry a confirmatory claim.  Only these require a
#: canonical instrument: a diagnostic reading is allowed to be rough, it is
#: just not allowed to be a finding.
CONFIRMATORY_ROLES = frozenset({"PRIMARY"})
SUPPORTING_ROLES = frozenset({"SECONDARY"})
NON_SCIENTIFIC_ROLES = frozenset({"DIAGNOSTIC", "EXPLORATORY"})


class Admission(StrEnum):
    ADMITTED = "ADMITTED"
    REFUSED = "REFUSED"


@dataclass(frozen=True)
class AdmissionVerdict:
    """Admission is not the same claim as a number.

    `numeric_claim` separates two things a single boolean used to conflate: the
    reading is admissible as a scientific outcome, and the reading asserts a
    quantity.  A NOT_EVALUABLE primary endpoint is a real, publishable result --
    the experiment ran and produced no support -- and it must survive into
    provenance precisely so that nobody later reads its absence as a zero.
    """

    outcome: Admission
    blockers: tuple[str, ...]
    instrument: authority.InstrumentRef | None
    reading_status: Status | None
    numeric_claim: bool
    endpoint_role: str
    schema_version: str = ADMISSION_SCHEMA

    @property
    def admitted(self) -> bool:
        return self.outcome is Admission.ADMITTED

    def as_record(self) -> dict[str, Any]:
        return {"schema_version": self.schema_version, "outcome": self.outcome.value,
                "blockers": list(self.blockers), "endpoint_role": self.endpoint_role,
                "instrument": self.instrument.as_record() if self.instrument else None,
                "reading_status": self.reading_status.value if self.reading_status else None,
                "numeric_claim": self.numeric_claim}


def _reading_status(record: Any, blockers: list[str]) -> Status | None:
    """A reading must arrive as a reading.  A bare float is not one."""
    if record is None:
        blockers.append("READING_ABSENT")
        return None
    if isinstance(record, (int, float)) and not isinstance(record, bool):
        # This is the exact shape of the legacy path, and admitting it would
        # reopen it: a number with no status cannot say whether its zero means
        # "measured zero" or "nothing to measure".
        blockers.append("READING_IS_BARE_NUMERIC")
        return None
    if not isinstance(record, Mapping) or "status" not in record:
        blockers.append("READING_MALFORMED")
        return None
    try:
        status = Status(str(record["status"]))
    except ValueError:
        blockers.append("READING_STATUS_UNKNOWN")
        return None
    value = record.get("value")
    if status is Status.OK:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            blockers.append("READING_OK_WITHOUT_VALUE")
    elif value is not None:
        # A non-OK reading carrying a number is the coercion this whole module
        # exists to prevent, arriving pre-packaged.
        blockers.append("READING_NON_OK_CARRIES_VALUE")
    return status


def admit_evidence(*, endpoint_role: str, instrument_ref: Any, reading: Any,
                   preregistered_instrument_ref: Any = None,
                   protocol_locked: bool = True) -> AdmissionVerdict:
    """Decide admission for one endpoint of one attempt.

    `instrument_ref` is what the run executed; `preregistered_instrument_ref` is
    what the sealed protocol promised.  They are compared rather than merged,
    because a runtime that quietly substitutes a newer instrument is the drift
    this gate is for.
    """
    blockers: list[str] = []
    role = str(endpoint_role).upper()
    confirmatory = role in CONFIRMATORY_ROLES
    scientific = confirmatory or role in SUPPORTING_ROLES
    if role not in CONFIRMATORY_ROLES | SUPPORTING_ROLES | NON_SCIENTIFIC_ROLES:
        blockers.append("ENDPOINT_ROLE_UNKNOWN")

    status = _reading_status(reading, blockers)

    resolved: authority.InstrumentRef | None = None
    if instrument_ref is None:
        if scientific:
            blockers.append("INSTRUMENT_REF_ABSENT")
    else:
        try:
            ref = (instrument_ref if isinstance(instrument_ref, authority.InstrumentRef)
                   else authority.InstrumentRef.from_record(instrument_ref))
            if scientific:
                authority.assert_admissible(ref)
            else:
                authority.resolve(ref)
            resolved = ref
        except authority.InstrumentResolutionError as exc:
            blockers.append(exc.code)
        except RuntimeError:
            # assert_reportable refuses a registered but uncertified instrument.
            blockers.append("INSTRUMENT_NOT_REPORTABLE")
            resolved = None

    if scientific:
        if not protocol_locked:
            blockers.append("PROTOCOL_NOT_LOCKED")
        if preregistered_instrument_ref is None:
            blockers.append("PROTOCOL_INSTRUMENT_BINDING_ABSENT")
        elif resolved is not None:
            promised = (preregistered_instrument_ref
                        if isinstance(preregistered_instrument_ref, authority.InstrumentRef)
                        else authority.InstrumentRef.from_record(preregistered_instrument_ref))
            if promised.instrument_id != resolved.instrument_id:
                blockers.append("INSTRUMENT_MISMATCH")
            elif promised.version != resolved.version:
                blockers.append("INSTRUMENT_VERSION_DRIFT")
            elif promised.spec_hash != resolved.spec_hash:
                blockers.append("INSTRUMENT_SPEC_DRIFT")

    outcome = Admission.REFUSED if blockers else Admission.ADMITTED
    return AdmissionVerdict(
        outcome=outcome, blockers=tuple(sorted(set(blockers))), instrument=resolved,
        reading_status=status, numeric_claim=outcome is Admission.ADMITTED and status is Status.OK,
        endpoint_role=role)
