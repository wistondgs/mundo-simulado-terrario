"""Four readings that must never merge: ZERO, NOT_EVALUABLE, MISSING, INVALID.

    0.0            there was support, the quantity was computed, it came out zero
    NOT_EVALUABLE  no support exists for the quantity — the denominator is empty
    MISSING        a field the computation needs is absent from the trace
    INVALID        the data is present and violates the contract it claims

`conversion_aprendizaje = 0` is a claim that the organism had informative
exposures and converted none of them. With N_informative = 0 the same 0 is a
claim about nothing, and the two are opposite findings wearing the same digit.
The laboratory has already produced three of those by accident.

The defence here is structural rather than advisory. `float(reading)` raises
unless the reading is OK, `reading.value` is None unless the reading is OK, and
there is no method that turns a non-OK reading into a number. Code that wants to
average, sum, plot or compare must first say what it intends to do with the
absent ones, in the open, at the call site. `ratio()` is the intended
constructor: it returns NOT_EVALUABLE on an empty denominator instead of
dividing, because that single line is where almost every false zero is born.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Any


class Status(enum.StrEnum):
    OK = "OK"
    NOT_EVALUABLE = "NOT_EVALUABLE"
    MISSING = "MISSING"
    INVALID = "INVALID"


class NotEvaluableError(RuntimeError):
    """Raised when a non-OK reading is coerced to a number."""


@dataclass(frozen=True)
class Reading:
    status: Status
    value: float | None = None
    support: int | None = None
    reason: str | None = None

    @staticmethod
    def ok(value: float, support: int | None = None) -> Reading:
        return Reading(Status.OK, float(value), support)

    @staticmethod
    def not_evaluable(reason: str, support: int = 0) -> Reading:
        return Reading(Status.NOT_EVALUABLE, None, support, reason)

    @staticmethod
    def missing(reason: str) -> Reading:
        return Reading(Status.MISSING, None, None, reason)

    @staticmethod
    def invalid(reason: str) -> Reading:
        return Reading(Status.INVALID, None, None, reason)

    @property
    def evaluable(self) -> bool:
        return self.status is Status.OK

    def __float__(self) -> float:
        if self.status is not Status.OK:
            raise NotEvaluableError(
                f"reading is {self.status.value} ({self.reason}); it has no numeric "
                f"value. Decide explicitly how absent readings are handled — do not "
                f"coerce this to 0.0.")
        return float(self.value)  # type: ignore[arg-type]

    def as_record(self) -> dict[str, Any]:
        return {"status": self.status.value, "value": self.value,
                "support": self.support, "reason": self.reason}

    def __str__(self) -> str:
        return f"{self.value:.4f}" if self.status is Status.OK else self.status.value


def ratio(numerator: float | None, denominator: float | None, *,
          what: str = "the quantity") -> Reading:
    """The one place a rate is built, so the empty denominator is handled once."""
    if numerator is None or denominator is None:
        return Reading.missing(f"{what}: numerator or denominator absent from the trace")
    if denominator < 0 or numerator < 0:
        return Reading.invalid(f"{what}: negative count ({numerator}/{denominator})")
    if denominator == 0:
        return Reading.not_evaluable(
            f"{what}: no support — the denominator is empty, so the rate is undefined "
            f"and is NOT zero", support=0)
    if numerator > denominator:
        return Reading.invalid(
            f"{what}: numerator {numerator} exceeds denominator {denominator}, so one "
            f"of the two is counting something the other is not")
    return Reading.ok(numerator / denominator, support=int(denominator))


def summarise(readings: dict[str, Reading]) -> dict[str, Any]:
    """Serialise a set of readings without flattening the four statuses."""
    return {name: reading.as_record() for name, reading in readings.items()}
