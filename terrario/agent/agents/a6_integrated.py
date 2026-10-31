"""A6 · puente ejecutable entre Ser Integrado y el ciclo real de Terrario.

No importa estado verdadero ni etiquetas del mundo. El adaptador suministra un
codec perceptible binario y un codec motor A/B; el aprendizaje y la selección
epistémica siguen siendo ``SerIntegrado`` de Unidad Mínima.
"""
from __future__ import annotations

import hashlib
import json
import pickle
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
        self._last_observation4: tuple[int, int, int, int] | None = None
        self._pending_action: str | None = None
        self._pending_source = "itinerary"
        self._step = 0
        self._events: list[dict[str, Any]] = []
        self.temporal = TemporalModel()
        self.contingency: ActionContingencyModel | None = None
        self.predictive_state = PredictiveStateLearner(action_aware=True)
        self._temporal_freeze_after = int(self.config.get("temporal_freeze_after", 8))
        self.last_prediction_error: float | None = None
        self.prediction_measurement_status = "NOT_MEASURED"

    @staticmethod
    def _bit(observation: Observation) -> int:
        """Bit C5 derivado sólo de la misma frontera sensorial de cuatro bits.

        Energía y tiempo son observables de Terrario, pero no pertenecen al
        contrato sensorial L16--L19. Excluirlos evita que una escena visual
        constante parezca una transición aprendida por el mero transcurso del
        episodio. El codec es deliberadamente muchos-a-uno; su aliasing se
        prueba y se declara, no se presenta como identificación del mundo.
        """
        return A6Integrated._observation4(observation)[0]

    @staticmethod
    def _observation4(observation: Observation) -> tuple[int, int, int, int]:
        """Codec sensorial explícito para los contratos 1.6--1.9.

        Deriva cuatro bits sólo de los canales/máscara perceptibles. No usa
        posición, identidad de objeto, regla, recompensa ni estado verdadero.
        """
        visible = np.asarray(observation.channels) * np.asarray(observation.mask)[None, :, :]
        if visible.shape[0] < 4:
            raise ValueError("A6 requiere al menos cuatro canales perceptibles")
        return tuple(int(np.any(np.abs(visible[channel]) > 0.0)) for channel in range(4))  # type: ignore[return-value]

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
        self._last_observation4 = self._observation4(observation)

    def _predictive_action(self) -> tuple[str, dict[str, float]] | None:
        """Política de ingeniería que sólo se habilita con los tres modelos vivos.

        La lectura ocurre antes de la consecuencia. No representa una meta ni
        una demostración de competencia: sólo hace causalmente observable que
        las estructuras L16/L17/L19 cambian una acción de A6.
        """
        if (self._last_observation4 is None or not self.temporal.frozen
                or self.contingency is None or self.contingency.updates == 0
                or self.predictive_state.updates == 0):
            return None
        current = self._last_observation4
        scores: dict[str, float] = {}
        for symbol in ("A", "B"):
            efference = self._efference(symbol)
            scores[symbol] = (
                0.10 * self.temporal.probability(current, current)
                + self.contingency.probability(current, efference, current)
                + self.predictive_state.probability(current, efference, current)
            )
        # The explicit ordering is a reproducible tie break, not hidden advice.
        return max(((score, symbol) for symbol, score in scores.items()), key=lambda item: (item[0], item[1]))[1], scores

    def decide(self) -> Action:
        if self._last_bit is None:
            raise RuntimeError("A6 decide sin observación")
        predictive = self._predictive_action()
        if predictive is not None:
            proposed, scores = predictive
            source = "l16_l17_l19_predictive_policy"
            self._decision_scores = scores
        else:
            proposed = self.core.letra_elegida()
            if proposed is None:
                proposed, source = ("A" if self._step % 2 == 0 else "B"), "itinerary"
            else:
                source = "exploration_08"
                self.core.c["pasos_elegidos"] += 1
            self._decision_scores = None
        self._pending_action, self._pending_source = proposed, source
        return self._to_action(proposed)

    def learn(self, transition: Transition) -> None:
        if self._pending_action is None or self._last_bit is None:
            raise RuntimeError("A6 learn sin decisión perceptible pendiente")
        action = self._from_action(transition.action_t)
        if action != self._pending_action:
            raise RuntimeError("A6 copia eferente no coincide con acción emitida")
        following = self._bit(transition.observation_t1)
        sensory_before = self._last_observation4
        if sensory_before is None:
            raise RuntimeError("A6 learn sin observación sensorial pendiente")
        sensory_after = self._observation4(transition.observation_t1)
        efference = self._efference(action)
        before = self.core.cognitive_state()
        prediction = self.core.predecir(action)
        prediction_probability = self.predictive_state.probability(sensory_before, efference, sensory_after)
        self.last_prediction_error = float(-np.log(max(prediction_probability, 1e-12)))
        self.prediction_measurement_status = "MEASURED_PRE_OUTCOME"
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
                         "predictive_state_count": len(self.predictive_state.states()),
                         "prediction_error": self.last_prediction_error,
                         "prediction_measurement_status": self.prediction_measurement_status,
                         "decision_scores": self._decision_scores},
        )
        self._events.append({"op": "ser_integrado.transition", "step": transition.step,
                             "action_symbol": action, "source": self._pending_source,
                             "transition_hash": event["transition_hash"],
                             "model_changed": event["state_before_hash"] != event["state_after_hash"]})
        self._last_bit = following
        self._last_observation4 = sensory_after
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
                                     "fingerprint": self.predictive_state.fingerprint()},
                "prediction_measurement_status": self.prediction_measurement_status,
                "last_prediction_error": self.last_prediction_error}

    def get_trace_events(self) -> list[dict[str, Any]]:
        events, self._events = self._events, []
        return events

    def reset(self) -> None:
        """Start a new episode while retaining acquired cognitive state.

        A new organism must be constructed for a fresh life. World changes use
        ``SerIntegrado.transicionar_mundo`` explicitly; this method is only an
        episode boundary and must not silently erase learning.
        """
        self._last_bit = None
        self._last_observation4 = None
        self._pending_action = None
        self._pending_source = "itinerary"

    def _checkpoint_payload(self) -> dict[str, Any]:
        return {
            "schema": "terrario.a6-integrated-checkpoint/v1",
            "core": self.core,
            "temporal": self.temporal,
            "contingency": self.contingency,
            "predictive_state": self.predictive_state,
            "last_bit": self._last_bit,
            "last_observation4": self._last_observation4,
            "pending_action": self._pending_action,
            "pending_source": self._pending_source,
            "step": self._step,
            "events": self._events,
            "prediction_error": self.last_prediction_error,
            "prediction_measurement_status": self.prediction_measurement_status,
        }

    def get_parameters(self) -> dict[str, torch.Tensor]:
        """Portable opaque state for trusted local checkpoint reconstruction.

        A6 has no torch weights. The byte tensor is still necessary because
        observer checkpoints otherwise saved an empty map and could not resume
        its learned symbolic state.
        """
        blob = pickle.dumps(self._checkpoint_payload(), protocol=5)
        return {"a6_runtime_v1": torch.tensor(list(blob), dtype=torch.uint8)}

    def set_parameters(self, params: dict[str, torch.Tensor]) -> None:
        if set(params) != {"a6_runtime_v1"}:
            raise ValueError("checkpoint A6 inválido: se esperaba sólo a6_runtime_v1")
        raw = params["a6_runtime_v1"].detach().cpu().numpy().astype(np.uint8).tobytes()
        payload = pickle.loads(raw)
        if payload.get("schema") != "terrario.a6-integrated-checkpoint/v1":
            raise ValueError("versión de checkpoint A6 desconocida")
        self.core = payload["core"]
        self.temporal = payload["temporal"]
        self.contingency = payload["contingency"]
        self.predictive_state = payload["predictive_state"]
        self._last_bit = payload["last_bit"]
        self._last_observation4 = payload["last_observation4"]
        self._pending_action = payload["pending_action"]
        self._pending_source = payload["pending_source"]
        self._step = payload["step"]
        self._events = payload["events"]
        self.last_prediction_error = payload["prediction_error"]
        self.prediction_measurement_status = payload["prediction_measurement_status"]

    def parameter_count(self) -> int:
        return 0
