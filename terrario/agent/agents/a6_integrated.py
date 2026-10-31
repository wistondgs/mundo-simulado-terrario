"""A6 · puente ejecutable entre Ser Integrado y el ciclo real de Terrario.

No importa estado verdadero ni etiquetas del mundo. El adaptador suministra un
codec perceptible binario y un codec motor A/B; el aprendizaje y la selección
epistémica siguen siendo ``SerIntegrado`` de Unidad Mínima.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch

from terrario.agent.base import AgentInterface
from terrario.core.contracts import Transition
from terrario.core.types import Action, ActionType, Direction, Observation
from terrario.level16.temporal import TemporalModel
from terrario.level17.contingency import ActionContingencyModel
from terrario.level17.efference import CommandToken, EfferenceCopy
from terrario.level19.predictive_state import PredictiveStateLearner


_EXPERIMENT_DIR = Path(__file__).resolve().parents[3] / "experiments" / "unidad_minima_01"
if str(_EXPERIMENT_DIR) not in sys.path:
    sys.path.insert(0, str(_EXPERIMENT_DIR))
from ser_integrado_01 import SerIntegrado  # noqa: E402


class A6Integrated(AgentInterface):
    """Un organismo de Unidad Mínima que percibe, actúa y aprende en Terrario."""

    def __init__(self, config: dict[str, Any] | None = None, generator=None) -> None:
        self.config = dict(config or {})
        self.core = SerIntegrado(
            organism_id=str(self.config.get("organism_id", "A6-integrated")),
            lineage_id=str(self.config.get("lineage_id", "A6-lineage")),
            n_max=int(self.config.get("n_max", 8)),
        )
        self._last_bit: int | None = None
        self._pending_action: str | None = None
        self._pending_source = "itinerary"
        self._step = 0
        self._events: list[dict[str, Any]] = []
        self.temporal = TemporalModel()
        self.contingency: ActionContingencyModel | None = None
        self.predictive_state = PredictiveStateLearner(action_aware=True)
        self._temporal_freeze_after = int(self.config.get("temporal_freeze_after", 8))

    @staticmethod
    def _bit(observation: Observation) -> int:
        """Codec suministrado desde campos perceptibles; nunca lee verdad mundial."""
        visible = np.asarray(observation.channels) * np.asarray(observation.mask)[None, :, :]
        payload = visible.tobytes() + np.asarray([observation.agent_energy, observation.time_fraction]).tobytes()
        return hashlib.sha256(payload).digest()[0] & 1

    @staticmethod
    def _observation4(observation: Observation) -> tuple[int, int, int, int]:
        """Codec sensorial explícito para los contratos 1.6--1.9.

        Deriva cuatro bits sólo de los canales/máscara perceptibles. No usa
        posición, identidad de objeto, regla, recompensa ni estado verdadero.
        """
        visible = np.asarray(observation.channels) * np.asarray(observation.mask)[None, :, :]
        digest = hashlib.sha256(visible.tobytes()).digest()[0]
        return tuple((digest >> shift) & 1 for shift in range(4))  # type: ignore[return-value]

    @staticmethod
    def _efference(symbol: str) -> EfferenceCopy:
        return EfferenceCopy(CommandToken.A0 if symbol == "A" else CommandToken.A1)

    @staticmethod
    def _to_action(symbol: str) -> Action:
        if symbol == "A":
            return Action(ActionType.CONSUME, Direction.LEFT)
        if symbol == "B":
            return Action(ActionType.CONSUME, Direction.RIGHT)
        raise ValueError(f"símbolo motor desconocido: {symbol!r}")

    @staticmethod
    def _from_action(action: Action) -> str:
        return "A" if action.direction in (Direction.LEFT, Direction.UP) else "B"

    def perceive(self, observation: Observation) -> None:
        self._last_bit = self._bit(observation)

    def decide(self) -> Action:
        if self._last_bit is None:
            raise RuntimeError("A6 decide sin observación")
        proposed = self.core.letra_elegida()
        if proposed is None:
            proposed, source = ("A" if self._step % 2 == 0 else "B"), "itinerary"
        else:
            source = "exploration_08"
            self.core.c["pasos_elegidos"] += 1
        self._pending_action, self._pending_source = proposed, source
        return self._to_action(proposed)

    def learn(self, transition: Transition) -> None:
        if self._pending_action is None or self._last_bit is None:
            raise RuntimeError("A6 learn sin decisión perceptible pendiente")
        action = self._from_action(transition.action_t)
        if action != self._pending_action:
            raise RuntimeError("A6 copia eferente no coincide con acción emitida")
        following = self._bit(transition.observation_t1)
        sensory_before = self._observation4(transition.observation_t)
        sensory_after = self._observation4(transition.observation_t1)
        efference = self._efference(action)
        before = self.core.cognitive_state()
        prediction = self.core.predecir(action)
        self.core.leer(action, following)
        # 1.6 aprende sólo secuencias observacionales; tras la frontera sellada,
        # 1.7 aprende sólo desviaciones condicionadas por la copia eferente.
        if not self.temporal.frozen:
            self.temporal.observe(sensory_before, sensory_after)
            if self.temporal.updates >= self._temporal_freeze_after:
                self.temporal.freeze()
                self.contingency = ActionContingencyModel(self.temporal)
        elif self.contingency is not None:
            self.contingency.observe(sensory_before, efference, sensory_after)
        # L19 conserva estado predictivo acción-observación y sus cambios
        # estructurales, sin convertir la consecuencia actual en información previa.
        self.predictive_state.observe(sensory_before, efference, sensory_after)
        self.core.world_id = f"terrario-seed-{transition.seed}"
        event = self.core._record(
            kind="terrario_transition", before=before, action=action, observation=following,
            source=self._pending_source,
            consequence={"prediction": prediction, "energy_delta": transition.energy_delta,
                         "events": list(transition.events), "terminated": transition.done,
                         "observation_hash": transition.observation_t1.obs_hash(),
                         "temporal_updates": self.temporal.updates,
                         "temporal_frozen": self.temporal.frozen,
                         "contingency_updates": self.contingency.updates if self.contingency else 0,
                         "predictive_state_updates": self.predictive_state.updates,
                         "predictive_state_count": len(self.predictive_state.states())},
        )
        self._events.append({"op": "ser_integrado.transition", "step": transition.step,
                             "action_symbol": action, "source": self._pending_source,
                             "transition_hash": event["transition_hash"],
                             "model_changed": event["state_before_hash"] != event["state_after_hash"]})
        self._last_bit = following
        self._pending_action = None
        self._step += 1

    def get_internal_state(self) -> dict[str, Any]:
        return {"agent_type": "A6_INTEGRATED", "step": self._step,
                "cognitive_state": self.core.cognitive_state(),
                "trace_head": self.core.head_hash, "trace_valid": self.core.verify_trace(),
                "temporal": {"updates": self.temporal.updates, "frozen": self.temporal.frozen,
                             "fingerprint": self.temporal.fingerprint()},
                "contingency": None if self.contingency is None else {
                    "updates": self.contingency.updates,
                    "inherited_intact": self.contingency.inherited_is_intact(),
                    "fingerprint": self.contingency.fingerprint()},
                "predictive_state": {"updates": self.predictive_state.updates,
                                     "states": self.predictive_state.states(),
                                     "modifications": len(self.predictive_state.modifications()),
                                     "fingerprint": self.predictive_state.fingerprint()}}

    def get_trace_events(self) -> list[dict[str, Any]]:
        events, self._events = self._events, []
        return events

    def reset(self) -> None:
        self._last_bit = None
        self._pending_action = None
        self._pending_source = "itinerary"

    def get_parameters(self) -> dict[str, torch.Tensor]:
        return {}

    def set_parameters(self, params: dict[str, torch.Tensor]) -> None:
        if params:
            raise ValueError("A6 no tiene parámetros torch; su estado aprendido es simbólico")

    def parameter_count(self) -> int:
        return 0
