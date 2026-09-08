"""Scientific observer — the main logging interface for Terrario experiments.

The observer is a read-only instrument. It captures traces from the
agent-world interaction without ever calling back into the agent or
modifying any state.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

import numpy as np

from terrario.core.contracts import ImmutableObserverSnapshot, Transition
from terrario.core.types import Action, Consequence, Observation, WorldState
from terrario.observer.storage import StorageManager
from terrario.observer.trace import (
    ConsequenceTrace,
    DecisionTrace,
    LearningTrace,
    MemoryTrace,
    PerceptionTrace,
    PredictionTrace,
    ProvenanceTrace,
    SensationTrace,
    TemporalTrace,
    TransitionTrace,
    WorldTrace,
)


class ScientificObserver:
    """First-class scientific instrument for capturing experiment data.

    Modes:
        performance        — only WorldTrace and ConsequenceTrace
        scientific_standard — all traces, no raw tensors
        forensic_full      — everything including latent vectors, ensembles,
                             similarity scores, and raw tensors
    """

    VALID_MODES = ("performance", "scientific_standard", "forensic_full")

    def __init__(
        self,
        run_dir: str,
        mode: str = "scientific_standard",
        config: dict | None = None,
    ):
        if mode not in self.VALID_MODES:
            raise ValueError(f"Invalid mode '{mode}'. Must be one of {self.VALID_MODES}")

        self.mode = mode
        self.storage = StorageManager(run_dir, mode)
        self._step_count = 0
        self._latencies: list[float] = []
        self._flush_interval = 100

        # Provenance tracking
        self._run_id = hashlib.sha256(
            f"{run_dir}:{time.time()}".encode()
        ).hexdigest()[:16]
        self._episode = 0
        self._seed = 0
        self._config_hash = ""
        self._config: dict[str, Any] = {}

        if config is not None:
            self._config = dict(config)
            self._config_hash = hashlib.sha256(
                json.dumps(config, sort_keys=True, default=str).encode()
            ).hexdigest()[:16]
            self._seed = config.get("seed", 0)
            self.storage.save_manifest(config)

    # ── Main entry point ──────────────────────────────────────────────

    def log_step(
        self,
        step: int,
        world_state: WorldState,
        agent: Any,
        observation: Observation,
        action: Action,
        consequence: Consequence,
        traces: dict,
    ) -> None:
        """Log a complete step. Called by the experiment runner.

        The ``traces`` dict may contain pre-built trace objects keyed by
        their trace name (e.g. ``traces["perception"] = PerceptionTrace(...)``).
        Any traces not provided are auto-generated from the raw arguments
        where possible.
        """
        t0 = time.monotonic()

        # Always log world and consequence traces
        if "world" in traces:
            self.log_world_trace(traces["world"])
        else:
            self.log_world_trace(self._build_world_trace(step, world_state))

        if "consequence" in traces:
            self.log_consequence_trace(traces["consequence"])
        else:
            self.log_consequence_trace(
                self._build_consequence_trace(step, action, consequence)
            )

        if self.mode in ("scientific_standard", "forensic_full"):
            if "sensation" in traces:
                self.log_sensation_trace(traces["sensation"])
            else:
                self.log_sensation_trace(
                    self._build_sensation_trace(step, observation)
                )

            if "decision" in traces:
                self.log_decision_trace(traces["decision"])

            if "perception" in traces:
                self.log_perception_trace(traces["perception"])

            if "temporal" in traces:
                self.log_temporal_trace(traces["temporal"])

            if "memory" in traces:
                mem = traces["memory"]
                if isinstance(mem, list):
                    for m in mem:
                        self.log_memory_trace(m)
                else:
                    self.log_memory_trace(mem)

            if "prediction" in traces:
                self.log_prediction_trace(traces["prediction"])

            if "learning" in traces:
                self.log_learning_trace(traces["learning"])

            if "provenance" in traces:
                prov = traces["provenance"]
            else:
                prov = ProvenanceTrace(
                    step=step,
                    run_id=self._run_id,
                    episode=self._episode,
                    seed=self._seed,
                    config_hash=self._config_hash,
                    timestamp=time.time(),
                )
            self._buffer_event("provenance", prov)

        self._step_count += 1

        # Periodic flush
        if self._step_count % self._flush_interval == 0:
            self.storage.flush_all()

        elapsed = time.monotonic() - t0
        self._latencies.append(elapsed)

    # ── Individual trace loggers ──────────────────────────────────────

    def log_world_trace(self, trace: WorldTrace) -> None:
        self._buffer_event("world", trace)

    def log_sensation_trace(self, trace: SensationTrace) -> None:
        if self.mode == "performance":
            return
        self._buffer_event("sensation", trace)

    def log_perception_trace(self, trace: PerceptionTrace) -> None:
        if self.mode == "performance":
            return
        if self.mode != "forensic_full":
            trace.latent_vector = None
        self._buffer_event("perception", trace)

    def log_temporal_trace(self, trace: TemporalTrace) -> None:
        if self.mode == "performance":
            return
        if self.mode != "forensic_full":
            trace.h_vector = None
        self._buffer_event("temporal", trace)

    def log_memory_trace(self, trace: MemoryTrace) -> None:
        if self.mode == "performance":
            return
        if self.mode != "forensic_full":
            trace.similarity_scores = None
        self._buffer_event("memory", trace)

    def log_prediction_trace(self, trace: PredictionTrace) -> None:
        if self.mode == "performance":
            return
        if self.mode != "forensic_full":
            trace.ensemble_predictions = None
        self._buffer_event("prediction", trace)

    def log_decision_trace(self, trace: DecisionTrace) -> None:
        if self.mode == "performance":
            return
        self._buffer_event("decision", trace)

    def log_consequence_trace(self, trace: ConsequenceTrace) -> None:
        self._buffer_event("consequence", trace)

    def log_learning_trace(self, trace: LearningTrace) -> None:
        if self.mode == "performance":
            return
        self._buffer_event("learning", trace)

    # ── Checkpoint ────────────────────────────────────────────────────

    def checkpoint(self, agent: Any, step: int, metadata: dict[str, Any] | None = None) -> None:
        """Save a checkpoint of the agent's state.

        Extracts parameters from the agent without modifying it.
        The agent must expose ``get_parameters()`` and optionally
        ``get_optimizer_state()`` methods.
        """
        params = {}
        optimizer_state = {}

        if hasattr(agent, "get_parameters"):
            params = agent.get_parameters()
        if hasattr(agent, "get_optimizer_state"):
            optimizer_state = agent.get_optimizer_state()

        checkpoint_metadata = {
            "step": step,
            "mode": self.mode,
            "run_id": self._run_id,
        }
        if metadata:
            checkpoint_metadata.update(metadata)
        self.storage.save_checkpoint(
            {k: self._to_numpy(v) for k, v in params.items()},
            {k: self._to_numpy(v) for k, v in optimizer_state.items()}, step, checkpoint_metadata,
        )

    def log_transition(
        self,
        transition: Transition,
        observer_snapshot: ImmutableObserverSnapshot,
        agent_identity: dict[str, Any],
        agent_internal_state: dict[str, Any],
        agent_trace_events: list[dict[str, Any]],
        parameter_deltas: dict[str, float] | None = None,
    ) -> None:
        """Persist the complete contract without exposing truth to the agent."""
        self._buffer_event("transition", TransitionTrace(
            step=transition.step,
            observation_t_hash=transition.observation_t.obs_hash(),
            observation_t1_hash=transition.observation_t1.obs_hash(),
            observation_t=self._observation_record(transition.observation_t),
            observation_t1=self._observation_record(transition.observation_t1),
            action_t=transition.action_t.to_int(),
            terminated=transition.terminated, truncated=transition.truncated,
            consequence={
                "energy_delta": transition.energy_delta,
                "agent_events": list(transition.events),
                "observer_events": list(transition.consequence_t1.observer_events),
            },
            agent_identity={**dict(agent_identity), "provenance": self._config}, internal_state=dict(agent_internal_state),
            observer_world=observer_snapshot.world, agent_trace_events=list(agent_trace_events),
            parameter_deltas=parameter_deltas,
        ))

    def capture_forensic(self, agent: Any, step: int, parameter_deltas: dict[str, float]) -> None:
        """Capture a small real forensic slice for selected agent modules."""
        if self.mode != "forensic_full":
            return
        for name in ("_last_latent", "_hidden", "_last_state"):
            value = getattr(agent, name, None)
            if value is not None:
                self.storage.save_tensor(f"activation_{name[1:]}", self._to_numpy(value), step)
        gradients: dict[str, float] = {}
        for module_name, value in vars(agent).items():
            if not isinstance(value, __import__("torch").nn.Module):
                continue
            for parameter_name, parameter in value.named_parameters():
                if parameter.grad is None:
                    continue
                name = f"gradient_{module_name}_{parameter_name.replace('.', '_')}"
                self.storage.save_tensor(name, self._to_numpy(parameter.grad), step)
                gradients[f"{module_name}.{parameter_name}"] = float(parameter.grad.norm().item())
        self.storage.save_tensor("parameter_delta_norms", np.asarray(list(parameter_deltas.values()), dtype=np.float32), step)
        self.storage.save_tensor("gradient_norms", np.asarray(list(gradients.values()), dtype=np.float32), step)

    @staticmethod
    def _to_numpy(value: Any) -> np.ndarray:
        if hasattr(value, "detach"):
            return value.detach().cpu().numpy()
        return np.asarray(value)

    @staticmethod
    def _observation_record(observation: Observation) -> dict[str, Any]:
        return {
            "channels": observation.channels.tolist(), "mask": observation.mask.tolist(),
            "agent_energy": observation.agent_energy, "time_fraction": observation.time_fraction,
        }

    # ── Metrics ───────────────────────────────────────────────────────

    def get_step_count(self) -> int:
        return self._step_count

    def get_logging_latency(self) -> float:
        """Average logging latency in milliseconds per step."""
        if not self._latencies:
            return 0.0
        return (sum(self._latencies) / len(self._latencies)) * 1000.0

    # ── Episode tracking ─────────────────────────────────────────────

    def set_episode(self, episode: int) -> None:
        self._episode = episode

    # ── Lifecycle ─────────────────────────────────────────────────────

    def close(self) -> None:
        """Flush all buffers and close storage."""
        self.storage.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    # ── Internal ──────────────────────────────────────────────────────

    def _buffer_event(self, trace_name: str, event) -> None:
        """Add an event to the storage buffer."""
        self.storage.save_trace_events([event], event.step)

    # ── Trace builders ────────────────────────────────────────────────

    @staticmethod
    def _build_world_trace(step: int, world_state: WorldState) -> WorldTrace:
        return WorldTrace(
            step=step,
            world_state_hash=world_state.state_hash(),
            rules_version=world_state.rules_version,
            time=world_state.time,
            num_objects=len(world_state.objects),
            num_agents=len(world_state.agents),
            object_positions={
                oid: obj.pos.to_tuple()
                for oid, obj in world_state.objects.items()
            },
            agent_positions={
                aid: ag.pos.to_tuple()
                for aid, ag in world_state.agents.items()
            },
            agent_energies={
                aid: ag.energy
                for aid, ag in world_state.agents.items()
            },
            occupancy_sum=int(world_state.occupancy.sum()),
        )

    @staticmethod
    def _build_sensation_trace(step: int, obs: Observation) -> SensationTrace:
        c, h, w = obs.channels.shape
        channel_stats: dict[str, float] = {}
        for i in range(c):
            ch = obs.channels[i]
            channel_stats[f"ch{i}_mean"] = float(ch.mean())
            channel_stats[f"ch{i}_std"] = float(ch.std())

        return SensationTrace(
            step=step,
            obs_hash=obs.obs_hash(),
            obs_shape=obs.channels.shape,
            mask_coverage=float(obs.mask.mean()),
            agent_energy=obs.agent_energy,
            time_fraction=obs.time_fraction,
            channel_stats=channel_stats,
        )

    @staticmethod
    def _build_consequence_trace(
        step: int, action: Action, consequence: Consequence
    ) -> ConsequenceTrace:
        return ConsequenceTrace(
            step=step,
            executed_action=action.to_int(),
            energy_delta=consequence.energy_delta,
            done=consequence.done,
            events=list(consequence.observer_events or consequence.events),
        )
