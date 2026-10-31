"""LEARNER-19-v1: finite, action-observation predictive states.

The learner only sees an observation, an opaque efference copy, and the next
observation.  A new route is created only when the Dirichlet marginal evidence
of separate incoming sensorimotor signatures exceeds the pooled alternative.
The state is used by callers only through predictive probabilities; it neither
sees a task's hidden key nor its reward before the action is selected.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from math import lgamma
from typing import Any

import numpy as np

from terrario.level16.temporal import OBSERVATION_INDEX
from terrario.level17.efference import EfferenceCopy


ROOT = 0
_ALPHA = 1.0
_SHAPE = (16, 4, 16)


class PredictiveStateError(RuntimeError):
    """A value crossed the sensory or efference boundary incorrectly."""


def _observation(candidate: object, role: str) -> int:
    if not isinstance(candidate, tuple) or len(candidate) != 4:
        raise PredictiveStateError(f"{role} debe ser una observación de cuatro bits")
    index = OBSERVATION_INDEX.get(candidate)  # type: ignore[arg-type]
    if index is None:
        raise PredictiveStateError(f"{role} está fuera del espacio sensorial")
    return index


def _action(candidate: object) -> int:
    if not isinstance(candidate, EfferenceCopy):
        raise PredictiveStateError("la acción debe llegar como EfferenceCopy")
    return candidate.index


@dataclass(frozen=True)
class StructuralModification:
    """An auditable, evidence-bound structural change."""

    event_id: int
    parent_state: int
    children: tuple[int, ...]
    signatures: tuple[tuple[int, int, int], ...]
    log_evidence_gain: float
    update: int


class PredictiveStateLearner:
    """Incrementally differentiates states by `(z, a, o')` evidence.

    ``action_aware=False`` is an intentionally weakened control: it retains the
    same update, prior and evidence test, but erases the action component from
    the structural signature.  It is not used by the full learner.
    """

    implementation_id = "LEARNER-19-v1"

    def __init__(self, *, action_aware: bool = True) -> None:
        self.action_aware = bool(action_aware)
        self._evidence: dict[int, np.ndarray] = {ROOT: np.zeros(_SHAPE)}
        self._incoming: dict[int, dict[tuple[int, int, int], np.ndarray]] = {
            ROOT: {}
        }
        self._routes: dict[tuple[int, int, int], int] = {}
        self._current = ROOT
        self._arrival: tuple[int, int, int] | None = None
        self._updates = 0
        self._events: list[StructuralModification] = []

    def begin(self) -> None:
        """Start a new episode without erasing acquired structure."""
        self._current = ROOT
        self._arrival = None

    @property
    def updates(self) -> int:
        return self._updates

    @property
    def current_state(self) -> int:
        return self._current

    def states(self) -> tuple[int, ...]:
        return tuple(sorted(self._evidence))

    def modifications(self) -> tuple[StructuralModification, ...]:
        return tuple(self._events)

    def _signature(self, state: int, action: int, following: int) -> tuple[int, int, int]:
        return (state, action if self.action_aware else 0, following)

    @staticmethod
    def _row(evidence: np.ndarray, observation: int, action: int) -> np.ndarray:
        return evidence[observation, action] + _ALPHA

    def predict(self, previous: object, efference: object) -> np.ndarray:
        observation = _observation(previous, "la observación")
        action = _action(efference)
        row = self._row(self._evidence[self._current], observation, action)
        return row / row.sum()

    def probability(self, previous: object, efference: object, following: object) -> float:
        return float(self.predict(previous, efference)[
            _observation(following, "la observación siguiente")
        ])

    def choose_for(self, previous: object, success_observation: object,
                   actions: tuple[EfferenceCopy, ...]) -> EfferenceCopy:
        """Select solely by the acquired, pre-outcome predictive distribution."""
        if not actions:
            raise PredictiveStateError("la política necesita al menos una acción")
        target = _observation(success_observation, "la observación de éxito")
        scored = [(float(self.predict(previous, action)[target]), index, action)
                  for index, action in enumerate(actions)]
        return max(scored, key=lambda item: (item[0], -item[1]))[2]

    def _log_marginal(self, table: np.ndarray) -> float:
        """Dirichlet-multinomial code length evidence, row by row."""
        total = 0.0
        for row in table.reshape(-1, _SHAPE[-1]):
            n = float(row.sum())
            total += lgamma(_SHAPE[-1] * _ALPHA) - lgamma(n + _SHAPE[-1] * _ALPHA)
            total += sum(lgamma(float(value) + _ALPHA) - lgamma(_ALPHA) for value in row)
        return total

    def _split_gain(self, state: int) -> float:
        pockets = tuple(self._incoming[state].values())
        if len(pockets) < 2:
            return float("-inf")
        pooled = np.zeros(_SHAPE)
        for pocket in pockets:
            pooled += pocket
        return sum(self._log_marginal(pocket) for pocket in pockets) - self._log_marginal(pooled)

    def _differentiate(self, state: int) -> bool:
        gain = self._split_gain(state)
        if not gain > 0.0:
            return False
        signatures = tuple(sorted(self._incoming[state]))
        if len(signatures) < 2:
            return False
        children: list[int] = []
        moved = np.zeros(_SHAPE)
        for signature in signatures:
            child = max(self._evidence) + 1
            children.append(child)
            pocket = self._incoming[state][signature]
            self._evidence[child] = pocket.copy()
            self._incoming[child] = {}
            self._routes[signature] = child
            moved += pocket
        # Each observation belongs either to its arriving signature or to the
        # parent fallback, never both.  This avoids fabricated evidence.
        self._evidence[state] -= moved
        if float(self._evidence[state].min()) < -1e-9:
            raise PredictiveStateError("la diferenciación duplicó evidencia")
        self._evidence[state] = np.maximum(self._evidence[state], 0.0)
        self._incoming[state] = {}
        self._events.append(StructuralModification(
            len(self._events), state, tuple(children), signatures, float(gain), self._updates,
        ))
        return True

    def observe(self, previous: object, efference: object, following: object) -> None:
        """Predictive update after the world has revealed the consequence."""
        before = _observation(previous, "la observación")
        action = _action(efference)
        after = _observation(following, "la observación siguiente")
        state = self._current
        self._evidence[state][before, action, after] += 1.0
        if self._arrival is not None:
            pocket = self._incoming[state].setdefault(self._arrival, np.zeros(_SHAPE))
            pocket[before, action, after] += 1.0
        self._updates += 1
        self._differentiate(state)
        # A split may have learned the route on which this state arrived.  Its
        # effect is causal only for subsequent predictions, never this outcome.
        state = self._routes.get(self._arrival, state) if self._arrival else state
        outgoing = self._signature(state, action, after)
        self._current = self._routes.get(outgoing, state)
        self._arrival = outgoing

    def follow(self, efference: object, following: object) -> None:
        """Advance the learned filter without training it (evaluation path)."""
        action = _action(efference)
        after = _observation(following, "la observación siguiente")
        outgoing = self._signature(self._current, action, after)
        self._current = self._routes.get(outgoing, self._current)
        self._arrival = outgoing

    def aggregate_evidence(self) -> np.ndarray:
        """A matched reactive predictor formed from exactly the same samples."""
        result = np.zeros(_SHAPE)
        for evidence in self._evidence.values():
            result += evidence
        return result

    def reactive_probability(self, previous: object, efference: object,
                             following: object) -> float:
        before = _observation(previous, "la observación")
        action = _action(efference)
        after = _observation(following, "la observación siguiente")
        row = self._row(self.aggregate_evidence(), before, action)
        return float(row[after] / row.sum())

    def lesion(self) -> None:
        """Remove only learned routing while retaining a matched pooled predictor."""
        pooled = self.aggregate_evidence()
        self._evidence = {ROOT: pooled}
        self._incoming = {ROOT: {}}
        self._routes = {}
        self.begin()

    def state_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "terrario.level19.predictive-state/v1",
            "implementation_id": self.implementation_id,
            "action_aware": self.action_aware,
            "evidence": {str(key): value.tolist() for key, value in self._evidence.items()},
            "incoming": {
                str(state): [[list(signature), value.tolist()]
                             for signature, value in sorted(entries.items())]
                for state, entries in self._incoming.items()
            },
            "routes": [[list(signature), child]
                       for signature, child in sorted(self._routes.items())],
            "current": self._current,
            "arrival": list(self._arrival) if self._arrival is not None else None,
            "updates": self._updates,
            "events": [asdict(event) for event in self._events],
        }

    @classmethod
    def from_state_dict(cls, state: dict[str, Any]) -> "PredictiveStateLearner":
        if state.get("schema_version") != "terrario.level19.predictive-state/v1":
            raise PredictiveStateError("versión de estado L19 desconocida")
        learner = cls(action_aware=bool(state["action_aware"]))
        learner._evidence = {
            int(key): np.asarray(value, dtype=float)
            for key, value in state["evidence"].items()
        }
        if not learner._evidence or any(value.shape != _SHAPE for value in learner._evidence.values()):
            raise PredictiveStateError("estado predictivo persistido inválido")
        learner._incoming = {
            int(state_id): {
                tuple(signature): np.asarray(value, dtype=float)
                for signature, value in entries
            }
            for state_id, entries in state["incoming"].items()
        }
        learner._routes = {tuple(signature): int(child) for signature, child in state["routes"]}
        if set(learner._incoming) != set(learner._evidence):
            raise PredictiveStateError("persistencia no cubre todos los estados")
        if any(child not in learner._evidence or signature[0] not in learner._evidence
               for signature, child in learner._routes.items()):
            raise PredictiveStateError("ruta persistida apunta fuera del estado")
        learner._current = int(state["current"])
        if learner._current not in learner._evidence:
            raise PredictiveStateError("estado actual persistido inexistente")
        arrival = state.get("arrival")
        learner._arrival = tuple(arrival) if arrival is not None else None
        learner._updates = int(state["updates"])
        learner._events = [StructuralModification(
            event_id=int(event["event_id"]), parent_state=int(event["parent_state"]),
            children=tuple(int(value) for value in event["children"]),
            signatures=tuple(tuple(int(value) for value in signature)
                             for signature in event["signatures"]),
            log_evidence_gain=float(event["log_evidence_gain"]), update=int(event["update"]),
        ) for event in state["events"]]
        return learner

    def fingerprint(self) -> str:
        payload = json.dumps(self.state_dict(), sort_keys=True, separators=(",", ":"))
        return sha256(payload.encode()).hexdigest()
