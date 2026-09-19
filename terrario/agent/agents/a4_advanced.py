"""A4_ADVANCED — the full cognitive architecture.

Pipeline:
    PerceptualEncoder → latent e_t
    SSMCore (or GRUCore) → temporal state h_t
    EpisodicMemory.read(e_t) → memory_context
    LongTermMemory.read(h_t) → lt_context
    Combined state s_t = concat(e_t, h_t, memory_context, lt_context)
    WorldModel(s_t, a_t) → predictions
    UncertaintyEstimator(s_t, a_t) → uncertainty
    PolicyHead(s_t) → action logits
    Planner (optional) → refined action
    HomeostaticState → modulates exploration
    OnlineLearner → updates all modules

Fully ablatable via config dict. When a module is ablated, it is replaced
by a no-op or zeros — NOT removed from the pipeline.
"""

from __future__ import annotations

import hashlib
from typing import Any

import torch
import torch.nn.functional as F

from terrario.agent.base import AgentInterface
from terrario.agent.encoder import PerceptualEncoder
from terrario.agent.adaptive_freeze import AdaptiveFreeze, combine
from terrario.agent.homeostasis import HomeostaticState
from terrario.agent.learner import OnlineLearner
from terrario.agent.memory import EpisodicMemory, LongTermMemory
from terrario.agent.policy import Planner, PolicyHead
from terrario.agent.temporal import GRUCore, SSMCore, TemporalCore
from terrario.agent.uncertainty import UncertaintyEstimator
from terrario.agent.world_model import WorldModel
from terrario.core.contracts import Transition
from terrario.core.action_contract import (
    IMPLEMENTED_MODES,
    MAX_TARGET_SLOTS,
    SELECTOR_OF_MODE,
    TARGET_BEARING_OPERATIONS,
    AddressingMode,
    SelectorType,
)
from terrario.core.types import (
    NUM_ACTION_TYPES, NUM_DIRECTIONS, TOTAL_ACTIONS, Action, ActionType, Direction, Observation,
)

_DIRECTION_OF_OFFSET = {(-1, 0): Direction.UP, (1, 0): Direction.DOWN,
                        (0, -1): Direction.LEFT, (0, 1): Direction.RIGHT}

DEFAULT_CONFIG: dict[str, Any] = {
    "use_temporal": True,
    "use_episodic_memory": True,
    "use_longterm_memory": True,
    "use_world_model": True,
    "use_uncertainty": True,
    "use_planner": True,
    "use_online_learning": True,
    # Action Contract v2, agent-side. The WORLD's action space is untouched --
    # still 25, still type x direction -- so no world contract, no config_hash
    # and no design already preregistered is affected. What changes is how the
    # policy FACTORS the choice: one head for the operation, one for the
    # selector, sampled independently, log-probabilities summed.
    #
    # The reason is credit assignment, not expressiveness. The channel could
    # always express "eat the thing to my left"; the measured addressing rate
    # was 2-4% for every agent including the random one, which is chance. A
    # joint 25-way problem receiving seven informative samples per lifetime
    # cannot be learned. Two 5-way problems receive the same samples each.
    "use_factored_action": False,
    # Which selector type the action carries. T0 addresses a direction (the v1
    # channel, exactly); T1 addresses an entity the organism perceived. Only
    # this differs between the two arms -- operation, reward, perception,
    # metabolism, learner, planner and world model are untouched -- which is
    # what makes T a clean causal intervention rather than a different organism.
    "addressing_mode": "T0_DIRECTIONAL",
    # OFF by default: turning it on changes what A4 does, and what A4 does is
    # pinned by the golden behavioural characterisation and the protected hash
    # manifest.  It arrives as a condition to be measured, not as a silent
    # improvement -- which is also better science than assuming the fix works.
    "use_entropy_regularization": False,
    #: The price paid for keeping the policy undecided.  Scientific content,
    #: so it is declared here rather than written into a loss expression.
    "entropy_coefficient": 0.01,
    # Ablatable at the CONSUMPTION site, not at construction: see __init__.
    "use_homeostasis": True,
    # The eta the ORGANISM regulates against, which is not the world's death
    # boundary (energy <= 0) nor the observer's eta in the viability metric.
    # Declared here so a preregistration can set it instead of finding it
    # hardcoded in a constructor signature.
    "homeostasis_threshold": 0.5,
    "temporal_core": "ssm",
    "latent_dim": 128,
    "hidden_dim": 256,
    "memory_capacity": 1000,
    "memory_slots": 64,
    "memory_dim": 128,
    "ensemble_size": 5,
    "planner_horizon": 5,
    "planner_candidates": 10,
    "learning_rate": 3e-4,
    "grad_clip": 1.0,
    "update_frequency": 1,
    # G4 intervention boundary.  This is not a capability-composition flag:
    # both arms retain `use_online_learning` and compute the same proposal; the
    # control suppresses only OnlineLearner's optimizer commit.
    "learning_commit_enabled": True,
    # OCF-G3. `learning_commit_enabled` sólo suprime `optimizer.step()`;
    # esto congela la frontera adaptativa entera. Ver adaptive_freeze.py.
    "full_adaptive_freeze": False,
    "num_channels": 4,
    "view_size": 5,
}


class A4Advanced(AgentInterface):
    """Full cognitive architecture with all modules ablatable via config."""

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        generator: torch.Generator | None = None,
    ):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self._generator = generator or torch.Generator()
        self._trace: list[dict[str, Any]] = []
        self._step: int = 0

        latent_dim: int = self.config["latent_dim"]
        hidden_dim: int = self.config["hidden_dim"]
        memory_dim: int = self.config["memory_dim"]
        memory_slots: int = self.config["memory_slots"]
        memory_capacity: int = self.config["memory_capacity"]
        ensemble_size: int = self.config["ensemble_size"]

        # ── Core modules (always present) ────────────────────────────
        self.encoder = PerceptualEncoder(
            self.config["num_channels"],
            self.config["view_size"],
            latent_dim,
        )

        # ── Temporal core ────────────────────────────────────────────
        self._use_temporal: bool = self.config["use_temporal"]
        if self._use_temporal:
            if self.config["temporal_core"] == "gru":
                self.temporal_core: TemporalCore = GRUCore(latent_dim, hidden_dim)
            else:
                self.temporal_core = SSMCore(latent_dim, hidden_dim)
        else:
            # No-op temporal core: hidden is always zeros
            self.temporal_core = SSMCore(latent_dim, hidden_dim)
            # Freeze parameters so it doesn't learn
            for p in self.temporal_core.parameters():
                p.requires_grad_(False)

        self._hidden: torch.Tensor = self.temporal_core.initial_state(1)

        # ── Episodic memory ──────────────────────────────────────────
        self._use_episodic: bool = self.config["use_episodic_memory"]
        self.episodic_memory = EpisodicMemory(capacity=memory_capacity)

        # ── Long-term memory ─────────────────────────────────────────
        self._use_longterm: bool = self.config["use_longterm_memory"]
        self.longterm_memory = LongTermMemory(memory_slots, memory_dim, input_dim=hidden_dim)
        if not self._use_longterm:
            for p in self.longterm_memory.parameters():
                p.requires_grad_(False)

        # ── Combined state dimension ─────────────────────────────────
        # s_t = concat(e_t, h_t, memory_context, lt_context)
        # memory_context is a weighted average of retrieved embeddings (latent_dim)
        # lt_context is memory_dim
        self._state_dim = latent_dim + hidden_dim + latent_dim + memory_dim

        # ── World model ──────────────────────────────────────────────
        self._use_world_model: bool = self.config["use_world_model"]
        self.world_model = WorldModel(self._state_dim, TOTAL_ACTIONS)
        if not self._use_world_model:
            for p in self.world_model.parameters():
                p.requires_grad_(False)

        # ── Uncertainty estimator ────────────────────────────────────
        self._use_uncertainty: bool = self.config["use_uncertainty"]
        self.uncertainty_estimator = UncertaintyEstimator(
            self._state_dim, TOTAL_ACTIONS, ensemble_size
        )
        if not self._use_uncertainty:
            for p in self.uncertainty_estimator.parameters():
                p.requires_grad_(False)

        # ── Policy head ──────────────────────────────────────────────
        self.policy_head = PolicyHead(self._state_dim)

        # ── Planner ──────────────────────────────────────────────────
        self._use_planner: bool = self.config["use_planner"]
        self.planner = Planner(generator=self._generator)

        # ── Factored intention: operation x selector ─────────────────
        # Built ONLY when enabled, so a default agent has the same modules,
        # the same parameter count and the same initial-parameter hash it had
        # before this existed.
        self._addressing_mode = AddressingMode(self.config["addressing_mode"])
        if self._addressing_mode not in IMPLEMENTED_MODES:
            raise ValueError(
                f"{self._addressing_mode.value} is reserved and has no resolver. "
                f"Implemented: {[m.value for m in IMPLEMENTED_MODES]}")
        self._selector_type = SELECTOR_OF_MODE[self._addressing_mode]
        # Entity addressing needs the factored heads; directional addressing may
        # have them or not, and that third arm matters: T0-flat vs T0-factored
        # isolates the architecture change, so a gain under T1 cannot be credited
        # to "two heads instead of one".
        entity = self._addressing_mode is AddressingMode.T1_ENTITY
        self._use_factored_action: bool = bool(self.config["use_factored_action"]) or entity
        self._selector_dim = MAX_TARGET_SLOTS if entity else NUM_DIRECTIONS
        if self._use_factored_action:
            self.operation_head = torch.nn.Linear(self._state_dim, NUM_ACTION_TYPES)
            self.selector_head = torch.nn.Linear(self._state_dim, self._selector_dim)
        self._offered_targets: list[Any] = []
        if entity:
            # The selector's DOMAIN depends on the operation: v in Domain(s, O_t).
            # MOVE and NOOP address space, not entities -- there is no such thing
            # as moving "at" an object -- so they keep a direction under every
            # addressing mode. Pinning their direction to NONE, which is what the
            # first version of this did, does not change how the organism refers:
            # it paralyses it. That arm measured a stationary agent -- one
            # opportunity in three hundred steps against dozens for the same
            # agent under T0, and a random policy scoring 1.0 addressing off a
            # denominator of 1. T must vary addressing and nothing else, and
            # locomotion is not addressing.
            self.direction_head = torch.nn.Linear(self._state_dim, NUM_DIRECTIONS)
            # BEHAVIOURAL PARITY INITIALISATION.
            #
            # An independently initialised entity head makes T1 mean four things
            # at once: a new selector, new parameters, a new initial policy
            # distribution and a new collapse dynamic. Nothing is attributable.
            #
            # Instead the slot logit is the directional logit of the direction
            # that REACHES that slot, plus a residual:
            #
            #     logit_T1(e) = logit_T0(d(e)) + r(e),     r(e) = 0 at t=0
            #
            # The residual head is zeroed, so at the first step T1 emits exactly
            # the distribution T0 would have emitted. T1 therefore adds
            # representational capacity WITHOUT introducing new random behaviour,
            # and anything that diverges later diverged by learning.
            self.selector_residual = torch.nn.Linear(self._state_dim, MAX_TARGET_SLOTS)
            torch.nn.init.zeros_(self.selector_residual.weight)
            torch.nn.init.zeros_(self.selector_residual.bias)

        # ── Entropy regularisation of the policy ─────────────────────
        self._use_entropy_regularization: bool = self.config["use_entropy_regularization"]
        self._entropy_coefficient: float = float(self.config["entropy_coefficient"])

        # ── Homeostasis ──────────────────────────────────────────────
        # The flag gates CONSUMPTION, not construction.  The homeostatic state
        # is tracked either way, so the observer trace keeps its shape and the
        # control arm still reports drive and exploration_bias; what the flag
        # removes is whether that pressure reaches the action distribution.
        # Ablating the bookkeeping too would confound "viability has no causal
        # authority" with "viability was not measured".
        self._use_homeostasis: bool = self.config["use_homeostasis"]
        self.homeostasis = HomeostaticState(threshold=self.config["homeostasis_threshold"])

        # ── Online learner ───────────────────────────────────────────
        self._use_online_learning: bool = self.config["use_online_learning"]
        self._learning_commit_enabled: bool = bool(self.config["learning_commit_enabled"])
        self.adaptive_freeze = AdaptiveFreeze(
            enabled=bool(self.config.get("full_adaptive_freeze", False)))
        learnable_modules: dict[str, torch.nn.Module] = {
            "encoder": self.encoder,
            "policy_head": self.policy_head,
        }
        if self._use_temporal:
            learnable_modules["temporal_core"] = self.temporal_core
        if self._use_longterm:
            learnable_modules["longterm_memory"] = self.longterm_memory
        if self._use_world_model:
            learnable_modules["world_model"] = self.world_model
        if self._use_uncertainty:
            learnable_modules["uncertainty_estimator"] = self.uncertainty_estimator
        if self._use_factored_action:
            learnable_modules["operation_head"] = self.operation_head
            learnable_modules["selector_head"] = self.selector_head
        if hasattr(self, "direction_head"):
            learnable_modules["direction_head"] = self.direction_head
            learnable_modules["selector_residual"] = self.selector_residual

        self.learner = OnlineLearner(
            modules=learnable_modules,
            lr=self.config["learning_rate"],
            grad_clip=self.config["grad_clip"],
            update_frequency=self.config["update_frequency"],
        )

        # ── Internal state for learning ──────────────────────────────
        self._last_latent: torch.Tensor | None = None
        self._last_hidden: torch.Tensor | None = None
        self._last_state: torch.Tensor | None = None
        self._last_action: int = 0
        self._last_log_prob: torch.Tensor | None = None
        self.last_prediction_error: float | None = None
        self._last_prediction: dict[str, float] = {}
        self._last_logits: torch.Tensor | None = None
        self._last_probs: torch.Tensor | None = None
        self._last_uncertainty: float | None = None
        self._energy_baseline: float = 0.0
        self._baseline_count: int = 0

    # ── Pipeline helpers ─────────────────────────────────────────────

    def _build_state(
        self,
        latent: torch.Tensor,
        hidden: torch.Tensor,
    ) -> torch.Tensor:
        """Build the combined state vector s_t.

        s_t = concat(e_t, h_t, memory_context, lt_context)
        Ablated modules contribute zeros.
        """
        latent_dim: int = self.config["latent_dim"]
        hidden_dim: int = self.config["hidden_dim"]
        memory_dim: int = self.config["memory_dim"]

        # Episodic memory context
        if self._use_episodic and self.episodic_memory.size > 0:
            retrieved, weights, _ = self.episodic_memory.read(latent, k=5)
            # Weighted average of retrieved embeddings
            memory_context = (retrieved * weights.unsqueeze(-1)).sum(dim=0)  # (latent_dim,)
        else:
            memory_context = torch.zeros(latent_dim, device=latent.device, dtype=latent.dtype)

        # Long-term memory context
        if self._use_longterm:
            lt_context, _ = self.longterm_memory.read(hidden)  # (memory_dim,)
        else:
            lt_context = torch.zeros(memory_dim, device=latent.device, dtype=latent.dtype)

        state = torch.cat([latent, hidden, memory_context, lt_context])
        return state

    def _action_to_onehot(self, action_int: int) -> torch.Tensor:
        device = next(self.encoder.parameters()).device
        onehot = torch.zeros(TOTAL_ACTIONS, device=device)
        onehot[action_int] = 1.0
        return onehot

    # ── AgentInterface implementation ────────────────────────────────

    def perceive(self, observation: Observation) -> None:
        self._last_latent = self.encoder.encode_observation(observation.channels)

        # Update homeostasis with observed energy
        self.homeostasis._energy = observation.agent_energy

        self._trace.append({
            "op": "perceive",
            "step": self._step,
            "latent_norm": self._last_latent.norm().item(),
            "agent_energy": observation.agent_energy,
        })

    def offer_targets(self, targets: list[Any]) -> None:
        """Receive the slot table for this step, before deciding.

        The organism already perceives these entities through its channels; the
        table is a derived view of its own observation, not new information. What
        it adds is the mapping from slot to relative offset, which is what makes
        parity with the directional contract expressible.
        """
        self._offered_targets = list(targets)

    def _slot_logits(self, state: torch.Tensor, temperature: float) -> torch.Tensor:
        """Directional prior over slots, plus a residual that starts at zero."""
        directional = self.direction_head(state) / temperature
        residual = self.selector_residual(state)
        logits = torch.full((MAX_TARGET_SLOTS,), -1e9,
                            device=state.device, dtype=state.dtype)
        for target in self._offered_targets:
            dx, dy = target.offset
            # Only a slot in contact has a direction that reaches it; one further
            # away inherits the NONE prior, which under T0 is the choice that
            # reaches no cell. Same prior, same meaning.
            direction = _DIRECTION_OF_OFFSET.get((dx, dy), Direction.NONE)
            logits[target.slot] = directional[int(direction)] + residual[target.slot]
        if not self._offered_targets:
            # Nothing perceived: no slot can be preferred, and a uniform choice
            # over an empty table is the honest distribution. Masking everything
            # would make the softmax undefined.
            logits = residual
        return logits

    def decide(self) -> Action:
        if self._last_latent is None:
            action_int = int(torch.randint(0, TOTAL_ACTIONS, (1,), generator=self._generator).item())
            return Action.from_int(action_int)

        latent = self._last_latent

        # ── Temporal core ────────────────────────────────────────────
        self._last_hidden = self._hidden.clone()
        if self._use_temporal:
            x = latent.unsqueeze(0)
            output, self._hidden = self.temporal_core(x, self._hidden)
            self._hidden = self._hidden.detach()
            h = output.squeeze(0)
        else:
            h = torch.zeros(self.config["hidden_dim"], device=latent.device, dtype=latent.dtype)

        # ── Build combined state ─────────────────────────────────────
        state = self._build_state(latent, h)
        # Keep this graph alive through learn(): the encoder and temporal core
        # are learnable participants in the policy/world-model update.
        self._last_state = state

        # ── Policy ───────────────────────────────────────────────────
        logits = self.policy_head(state)

        # Modulate temperature by homeostatic exploration bias.  This is the
        # only site where the organism's viability pressure reaches behaviour:
        # `drive` is computed and reported but consumed nowhere.  With
        # use_homeostasis False the temperature is the unmodulated 1.0.
        temperature = (1.0 + self.homeostasis.exploration_bias) if self._use_homeostasis else 1.0

        # ── Uncertainty bonus ────────────────────────────────────────
        if self._use_uncertainty:
            # Add exploration bonus for uncertain actions
            with torch.no_grad():
                uncertainties = torch.zeros(TOTAL_ACTIONS, device=state.device, dtype=state.dtype)
                for a in range(TOTAL_ACTIONS):
                    a_onehot = self._action_to_onehot(a)
                    _, var, _ = self.uncertainty_estimator.predict(state, a_onehot)
                    uncertainties[a] = var.mean().item()
                # Boost logits for uncertain actions (curiosity)
                logits = logits + 0.1 * uncertainties
                self._last_uncertainty = float(uncertainties.mean().item())
        else:
            self._last_uncertainty = None

        # ── Factored sampling ────────────────────────────────────────
        if self._use_factored_action:
            op_logits = self.operation_head(state)
            sel_logits = self.selector_head(state)
            op_probs = F.softmax(op_logits / temperature, dim=-1)
            sel_probs = F.softmax(sel_logits / temperature, dim=-1)
            # The planner has to stay in the loop. The factored branch returns
            # before the planner refinement below, so a factored arm was not
            # "the same organism addressing differently" -- it was an organism
            # with no planner, and the screening showed the planner is one of
            # only two modules that move behaviour at all (+6.7 meals). Comparing
            # T0 against a plannerless T1 would have measured the ablation, not
            # the contract. The planner proposes in the flat 25-space, so its
            # OPERATION is taken here and the selector heads keep choosing the
            # referent: the planner says what to do, addressing says on what.
            op = int(torch.multinomial(op_probs, 1, generator=self._generator).item())
            planned_direction: int | None = None
            if (self._use_planner and self._use_world_model
                    and torch.rand(1, generator=self._generator).item() < 0.5):
                planned_action, _ = self.planner.plan(
                    state, self.world_model,
                    horizon=self.config["planner_horizon"],
                    num_candidates=self.config["planner_candidates"],
                )
                op = int(planned_action) // NUM_DIRECTIONS
                # The planner proposes a WHOLE action, operation and direction.
                # Taking only the operation and letting a freshly initialised
                # direction head supply the rest is not the same organism: under
                # T0 movement was planned, under T1 it was drawn from a head that
                # collapses within a few hundred steps. The agent then wedged
                # against an object -- MOVE on 61% of steps and two cells
                # visited, with something adjacent at every single step. The
                # planner keeps its direction here; what T1 changes is only how
                # an operation that acts ON something names its referent.
                planned_direction = int(planned_action) % NUM_DIRECTIONS
            operation = ActionType(op)
            addresses_entity = (self._selector_type is SelectorType.TARGET_ID
                                and operation in TARGET_BEARING_OPERATIONS)
            if addresses_entity:
                slot_logits = self._slot_logits(state, temperature)
                slot_probs = F.softmax(slot_logits, dim=-1)
                sel = int(torch.multinomial(slot_probs, 1, generator=self._generator).item())
                sel_log = torch.log(slot_probs[sel] + 1e-8)
                direction = Direction.NONE
            elif hasattr(self, "direction_head"):
                dir_probs = F.softmax(self.direction_head(state) / temperature, dim=-1)
                sel = (planned_direction if planned_direction is not None
                       else int(torch.multinomial(dir_probs, 1, generator=self._generator).item()))
                sel_log = torch.log(dir_probs[sel] + 1e-8)
                direction = Direction(sel)
            else:
                sel = (planned_direction if planned_direction is not None
                       else int(torch.multinomial(sel_probs, 1, generator=self._generator).item()))
                sel_log = torch.log(sel_probs[sel] + 1e-8)
                direction = Direction(sel)
            action_int = op * NUM_DIRECTIONS + (sel if sel < NUM_DIRECTIONS else 0)
            log_prob = torch.log(op_probs[op] + 1e-8) + sel_log
            self._last_action, self._last_log_prob = action_int, log_prob
            self._last_logits, self._last_probs = op_logits.detach(), op_probs.detach()
            # The §1 invariant: what was INTENDED travels separately from what
            # the world resolved, so "chose wrong" and "chose right and the
            # actuator missed" never collapse into one failure again.
            self._trace.append({
                "op": "decide", "step": self._step, "action_int": action_int,
                "intended_operation": op, "intended_selector": sel,
                "addressing_mode": self._addressing_mode.value,
                "selector_type": self._selector_type.name,
                "log_prob": float(log_prob.item()), "temperature": temperature,
                "factored": True,
                "drive": self.homeostasis.drive,
                "exploration_bias": self.homeostasis.exploration_bias,
            })
            self._step += 1
            # Under T1 the direction is pinned to NONE so the directional path
            # cannot resolve anything: entity addressing must stand on its own,
            # or AC2-5 is violated by the physics falling back to a neighbour.
            return Action(
                action_type=operation, direction=direction,
                selector_type=int(SelectorType.TARGET_ID if addresses_entity
                                  else SelectorType.DIRECTION),
                selector_value=sel,
            )

        # ── Planner refinement ───────────────────────────────────────
        if self._use_planner and self._use_world_model:
            planned_action, plan_trace = self.planner.plan(
                state,
                self.world_model,
                horizon=self.config["planner_horizon"],
                num_candidates=self.config["planner_candidates"],
            )
            # Blend planner and policy: use planner action with some probability
            plan_prob = 0.5
            if torch.rand(1, generator=self._generator).item() < plan_prob:
                action_int = planned_action
                log_prob = torch.log(F.softmax(logits, dim=-1)[action_int] + 1e-8)
            else:
                action_int, log_prob, _ = self.policy_head.sample(
                    logits, temperature, generator=self._generator
                )
        else:
            action_int, log_prob, _ = self.policy_head.sample(
                logits, temperature, generator=self._generator
            )

        self._last_action = action_int
        self._last_log_prob = log_prob
        self._last_logits = logits.detach().clone()
        self._last_probs = F.softmax(logits, dim=-1).detach().clone()

        self._trace.append({
            "op": "decide",
            "step": self._step,
            "action_int": action_int,
            "log_prob": log_prob.item(),
            "temperature": temperature,
            "hidden_norm": self._hidden.norm().item(),
            "state_norm": state.norm().item(),
            "drive": self.homeostasis.drive,
            "exploration_bias": self.homeostasis.exploration_bias,
        })
        return Action.from_int(action_int)

    def _policy_reward(self, consequence: Transition) -> float:
        """What the policy is reinforced on.

        For A4 this is the metabolic consequence and nothing else: the organism
        is paid only by the world. A descendant that has a reason of its own to
        act overrides this, and the override is then the entire causal surface
        of that capability -- which is what makes it ablatable.
        """
        return float(consequence.energy_delta)

    def learn(self, consequence: Transition) -> None:
        if self._last_state is None or self._last_latent is None:
            self._step += 1
            return

        # ── Homeostasis: NO se actualiza aquí ────────────────────────
        # `homeostasis._energy` es **estado interoceptivo sentido ahora**, y su
        # única autoridad es `perceive` (línea 358), que lo toma de
        # `observation.agent_energy` en unidades NORMALIZADAS [0,1].
        #
        # Aquí había `self.homeostasis.update(consequence.energy_delta)`, que
        # sumaba energía **absoluta** a esa variable normalizada: con
        # `max_energy = 60`, el coste de paso de 0.15 restaba 60× de más y una
        # sola comida (+9.85) la saturaba a 1.0. Era inocuo sólo porque
        # `perceive` lo pisaba antes de que nadie leyera, y porque `drive` no
        # tenía consumidores. Dejarlo convertiría el primer lector de `drive`
        # en un lector de basura.
        #
        # Aprender la consecuencia y sentir el estado son dos procesos: el
        # segundo no debe reescribir retroactivamente la lectura del primero.
        # Lo que este método sí hace con `consequence` es entrenar al predictor.

        # ── Write to episodic memory ─────────────────────────────────
        if self._use_episodic:
            prediction_error = 0.0
            if self._use_world_model and self._last_state is not None:
                with torch.no_grad():
                    a_onehot = self._action_to_onehot(self._last_action)
                    _, e_pred, _ = self.world_model(self._last_state, a_onehot)
                    prediction_error = abs(e_pred.item() - consequence.energy_delta)

            if self.adaptive_freeze.allow("episodic_buffer"):
                self.episodic_memory.write(
                    embedding=self._last_latent,
                    action=self._last_action,
                    energy_delta=consequence.energy_delta,
                    prediction_error=prediction_error,
                    timestamp=self._step,
                )

        # ── Write to long-term memory ────────────────────────────────
        if self._use_longterm:
            h = self._hidden.squeeze(0) if self._hidden.dim() > 1 else self._hidden
            if self.adaptive_freeze.allow("longterm_M"):
                self.longterm_memory.write(h, h)

        # Prediction remains an observer metric even for the no-online-learning
        # ablation. It must not depend on whether parameters will be updated.
        if self._use_world_model:
            a_onehot = self._action_to_onehot(self._last_action)
            with torch.no_grad():
                _, energy_prediction, done_prediction = self.world_model(self._last_state, a_onehot)
                self.last_prediction_error = abs(float(energy_prediction.item()) - consequence.energy_delta)
                self._last_prediction = {
                    "energy": float(energy_prediction.item()),
                    "done_probability": float(torch.sigmoid(done_prediction).item()),
                    "prediction_error": self.last_prediction_error,
                }
        else:
            self.last_prediction_error = None
            self._last_prediction = {}

        # ── Learning ─────────────────────────────────────────────────
        if self._use_online_learning:
            wm_loss = None
            policy_loss = None
            before_params = self.get_parameters()
            before_hash = self._parameters_hash(before_params)

            # World model loss
            if self._use_world_model and consequence.new_observation is not None:
                a_onehot = self._action_to_onehot(self._last_action)
                energy_target = torch.tensor([consequence.energy_delta], device=self._last_state.device)
                done_target = torch.tensor([1.0 if consequence.done else 0.0], device=self._last_state.device)

                # Build the next combined state as target
                with torch.no_grad():
                    next_latent = self.encoder.encode_observation(
                        consequence.new_observation.channels
                    )
                    # Run temporal core one step with next latent
                    if self._use_temporal:
                        next_x = next_latent.unsqueeze(0)
                        _, next_h = self.temporal_core(next_x, self._hidden)
                        next_h = next_h.squeeze(0)
                    else:
                        next_h = torch.zeros(
                            self.config["hidden_dim"], device=next_latent.device, dtype=next_latent.dtype,
                        )
                    next_state_target = self._build_state(next_latent, next_h)

                wm_losses = self.world_model.loss(
                    self._last_state.unsqueeze(0),
                    a_onehot.unsqueeze(0),
                    next_state_target.unsqueeze(0),
                    energy_target,
                    done_target,
                )
                wm_loss = wm_losses["loss_total"]

            # Policy loss: REINFORCE with baseline
            if self._last_log_prob is not None and self._last_state is not None:
                # The one seam.  A4 reinforces on the metabolic consequence and
                # nothing else, which `_policy_reward` returns unchanged -- this
                # is inert here and exists so a descendant can add a reward term
                # without duplicating 187 lines of this method and letting the
                # copy drift.  Baseline and advantage read the same quantity, or
                # the advantage stops being centred.
                reward = self._policy_reward(consequence)
                # OCF-G3: `_baseline_count` y `_energy_baseline` son una sola
                # pieza adaptativa y se congelan juntas. `advantage` sigue
                # calculándose con la línea base vigente: lo que se congela es
                # la adaptación, no el cálculo de la política.
                if self.adaptive_freeze.allow("energy_baseline"):
                    self._baseline_count += 1
                    self._energy_baseline += (
                        reward - self._energy_baseline
                    ) / self._baseline_count

                advantage = reward - self._energy_baseline

                # Re-compute log_prob with fresh graph to avoid double-backward
                if self._use_factored_action:
                    op, sel = divmod(int(self._last_action), NUM_DIRECTIONS)
                    fresh_probs = F.softmax(self.operation_head(self._last_state), dim=-1)
                    sel_probs = F.softmax(self.selector_head(self._last_state), dim=-1)
                    fresh_log_prob = (torch.log(fresh_probs[op] + 1e-8)
                                      + torch.log(sel_probs[sel] + 1e-8))
                else:
                    fresh_logits = self.policy_head(self._last_state)
                    fresh_probs = F.softmax(fresh_logits, dim=-1)
                    fresh_log_prob = torch.log(fresh_probs[self._last_action] + 1e-8)
                policy_loss = -fresh_log_prob * advantage

                # Entropy regularisation, off by default so A4 stays the agent
                # every existing baseline pins.  It exists because the measured
                # failure is not about food: over 400 steps of D4T the organism
                # chose CONSUME 173 times with an object adjacent 222 times, and
                # aimed UP in 215 of 236 attempts.  Indecision collapsed to 0.05
                # bits.  It cannot learn which channel feeds it, because it
                # stopped varying the action that would sample the answer --
                # and _find_target resolves CONSUME by direction, so aiming
                # wrong is not eating.
                #
                # REINFORCE with a running-mean baseline on a reward that is the
                # step cost almost every step gives a near-constant advantage,
                # which piles probability onto whatever was done first.  The
                # standard remedy is a term that pays for keeping the policy
                # undecided, and it was simply absent.
                #
                # Declared and flagged rather than tuned in silence: the
                # coefficient is the price of indecision, which is scientific
                # content, not a constant.
                if self._use_entropy_regularization:
                    entropy = -(fresh_probs * torch.log(fresh_probs + 1e-8)).sum()
                    policy_loss = policy_loss - self._entropy_coefficient * entropy

            # Uncertainty estimator loss: train ensemble to predict energy_delta
            if self._use_uncertainty and self._use_world_model:
                a_onehot = self._action_to_onehot(self._last_action)
                energy_target_t = torch.tensor([[consequence.energy_delta]], device=self._last_state.device)
                state_batch = self._last_state.unsqueeze(0)
                action_batch = a_onehot.unsqueeze(0)
                x = torch.cat([state_batch, action_batch], dim=-1)
                unc_loss = torch.tensor(0.0, device=self._last_state.device, requires_grad=True)
                for head in self.uncertainty_estimator.heads:
                    pred = head(x)
                    unc_loss = unc_loss + F.mse_loss(pred, energy_target_t)
                unc_loss = unc_loss / len(self.uncertainty_estimator.heads)
                if wm_loss is not None:
                    wm_loss = wm_loss + unc_loss
                else:
                    wm_loss = unc_loss

            # Step the learner
            event = self.learner.step(
                world_model_loss=wm_loss,
                policy_loss=policy_loss,
                commit=combine(self.adaptive_freeze, "parameters",
                               also=(self._learning_commit_enabled,)),
            )

            if event is not None:
                after_params = self.get_parameters()
                parameter_delta_norm = sum(
                    (after_params[name] - value).norm().item()
                    for name, value in before_params.items()
                )
                self._trace.append({
                    "op": "learn",
                    "step": self._step,
                    "loss_total": event.loss_total,
                    "loss_components": event.loss_components,
                    "grad_norms": event.grad_norms,
                    "energy_delta": consequence.energy_delta,
                    "advantage": advantage if self._last_log_prob is not None else 0.0,
                    "done": consequence.done,
                    "before_parameters_hash": before_hash,
                    "after_parameters_hash": self._parameters_hash(after_params),
                    "parameter_delta_norm": parameter_delta_norm,
                    "gradient_norm": sum(event.grad_norms.values()),
                    "loss_before": event.loss_total,
                    "loss_after": event.loss_total,
                    "commit_applied": self._learning_commit_enabled,
                })
        else:
            self._trace.append({
                "op": "learn",
                "step": self._step,
                "energy_delta": consequence.energy_delta,
                "done": consequence.done,
                "online_learning": False,
            })

        self._step += 1

    def get_internal_state(self) -> dict[str, Any]:
        return {
            "step": self._step,
            "agent_type": "A4_ADVANCED",
            "latent_norm": self._last_latent.norm().item() if self._last_latent is not None else 0.0,
            "hidden_norm": self._hidden.norm().item(),
            "state_norm": self._last_state.norm().item() if self._last_state is not None else 0.0,
            "episodic_memory_size": self.episodic_memory.size,
            "homeostasis": self.homeostasis.get_state(),
            "energy_baseline": self._energy_baseline,
            "config": {k: v for k, v in self.config.items()},
        }

    def get_scientific_state(self) -> dict[str, Any]:
        """Detached observer-only neural state for OBSERVE-02."""
        return {
            "latent": self._last_latent.detach().clone() if self._last_latent is not None else None,
            "temporal": self._hidden.detach().clone(),
            "state": self._last_state.detach().clone() if self._last_state is not None else None,
            "episodic_memory_size": self.episodic_memory.size,
            "longterm_memory_norm": float(self.longterm_memory.M.detach().norm().item()),
            "prediction": dict(self._last_prediction),
            "prediction_error": self.last_prediction_error,
            "uncertainty": self._last_uncertainty,
            "logits": self._last_logits.detach().clone() if self._last_logits is not None else None,
            "probabilities": self._last_probs.detach().clone() if self._last_probs is not None else None,
            "active_ablations": [key for key, value in self.config.items() if key.startswith("use_") and not value],
            "learning": {"updates": self.learner.step_count, "online_learning": self._use_online_learning},
        }

    def get_trace_events(self) -> list[dict[str, Any]]:
        events = list(self._trace)
        self._trace.clear()

        # Collect sub-module traces
        events.extend(self.episodic_memory.get_trace())
        events.extend(self.longterm_memory.get_trace())
        events.extend(self.planner.get_trace())
        events.extend(self.homeostasis.get_trace())
        events.extend(self.adaptive_freeze.get_trace())
        events.extend(self.learner.get_trace())

        return events

    def reset(self) -> None:
        self._step = 0
        self._trace.clear()
        self._hidden = self.temporal_core.initial_state(1)
        self._last_latent = None
        self._last_hidden = None
        self._last_state = None
        self._last_action = 0
        self._last_log_prob = None
        self.last_prediction_error = None
        self._last_prediction = {}
        self._last_logits = None
        self._last_probs = None
        self._last_uncertainty = None
        self._energy_baseline = 0.0
        self._baseline_count = 0

        self.episodic_memory.reset()
        self.longterm_memory.reset_memory()
        self.homeostasis.reset()
        self.learner.reset()
        self.adaptive_freeze.reset()

    def _parameter_modules(self) -> list[tuple[str, torch.nn.Module]]:
        """One list, so a module added later cannot be silently left out.

        get_parameters, set_parameters and parameter_count each carried their
        own hardcoded copy. A head added to the agent was invisible to all
        three at once: the parameter count under-reported it, the identity hash
        did not cover it, and a twin restored from parameters would have
        dropped it without a word. The order is the original one, so a default
        agent hashes exactly as it did before.
        """
        modules = [
            ("encoder", self.encoder),
            ("temporal_core", self.temporal_core),
            ("longterm_memory", self.longterm_memory),
            ("world_model", self.world_model),
            ("uncertainty_estimator", self.uncertainty_estimator),
            ("policy_head", self.policy_head),
        ]
        for nombre in ("operation_head", "selector_head", "direction_head", "selector_residual"):
            modulo = getattr(self, nombre, None)
            if isinstance(modulo, torch.nn.Module):
                modules.append((nombre, modulo))
        return modules

    def get_parameters(self) -> dict[str, torch.Tensor]:
        params: dict[str, torch.Tensor] = {}
        for prefix, module in self._parameter_modules():
            for name, p in module.named_parameters():
                params[f"{prefix}.{name}"] = p.detach().clone()
        return params

    def set_parameters(self, params: dict[str, torch.Tensor]) -> None:
        with torch.no_grad():
            for prefix, module in self._parameter_modules():
                for name, p in module.named_parameters():
                    key = f"{prefix}.{name}"
                    if key in params:
                        p.copy_(params[key])

    def parameter_count(self) -> int:
        return sum(p.numel() for _, module in self._parameter_modules()
                   for p in module.parameters() if p.requires_grad)

    @staticmethod
    def _parameters_hash(params: dict[str, torch.Tensor]) -> str:
        digest = hashlib.sha256()
        for name, value in sorted(params.items()):
            digest.update(name.encode())
            digest.update(value.detach().cpu().contiguous().numpy().tobytes())
        return digest.hexdigest()
