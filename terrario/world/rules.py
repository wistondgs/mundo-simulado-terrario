"""RuleEngine — evaluates hidden world rules and applies their effects.

The agent NEVER sees the rules. Rules define how object channel patterns
interact with actions to produce energy changes, destruction, or transformation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from terrario.core.types import Action, ActionType, ObjectSpec
from terrario.world.state import WorldStateManager


@dataclass
class ChannelCondition:
    """Condition on a single perceptual channel of an object."""
    index: int
    min_val: float = float("-inf")
    max_val: float = float("inf")

    def matches(self, channels: np.ndarray) -> bool:
        if self.index >= channels.shape[0]:
            return False
        v = float(channels[self.index])
        return self.min_val <= v <= self.max_val


@dataclass
class RuleCondition:
    """Full condition for a rule: object channel constraints + required action."""
    channel_conditions: list[ChannelCondition] = field(default_factory=list)
    action: str = ""

    def matches(self, obj: ObjectSpec, action: Action) -> bool:
        if self.action and self.action != action.action_type.name:
            return False
        return all(cc.matches(obj.channels) for cc in self.channel_conditions)


@dataclass
class RuleEffect:
    """Effect produced when a rule fires."""
    energy_delta: float = 0.0
    destroy_object: bool = False
    transform_channels: np.ndarray | None = None  # replacement channel vector


@dataclass
class Rule:
    """A single world rule: condition → effect."""
    rule_id: str
    condition: RuleCondition
    effect: RuleEffect


class RuleEngine:
    """Evaluates and applies hidden world rules.

    Rules are loaded from a YAML-compatible dict. The engine maintains a
    version counter that increments on every rule replacement, enabling
    the ChangeScheduler to swap rules mid-episode.
    """

    def __init__(self) -> None:
        self._rules: list[Rule] = []
        self._version: int = 0

    @property
    def version(self) -> int:
        return self._version

    @property
    def rules(self) -> list[Rule]:
        """Read-only view of current rules (for observer logging only)."""
        return list(self._rules)

    def load_rules(self, rules_dict: dict[str, Any]) -> None:
        """Replace all rules from a dict and increment version.

        Expected format::

            rules:
              - id: "rule_0"
                condition:
                  object_channel:
                    index: 0
                    min: 0.5
                    max: 1.0
                  action: "CONSUME"
                effect:
                  energy_delta: 10.0
                  destroy_object: true
                  transform_channels: [0.1, 0.2, 0.3]
        """
        parsed: list[Rule] = []
        for r in rules_dict.get("rules", []):
            cond_data = r.get("condition", {})
            eff_data = r.get("effect", {})

            # Parse channel conditions
            ch_conds: list[ChannelCondition] = []
            oc = cond_data.get("object_channel")
            if oc is not None:
                ch_conds.append(ChannelCondition(
                    index=oc["index"],
                    min_val=oc.get("min", float("-inf")),
                    max_val=oc.get("max", float("inf")),
                ))
            # Support multiple channel conditions
            for extra_oc in cond_data.get("object_channels", []):
                ch_conds.append(ChannelCondition(
                    index=extra_oc["index"],
                    min_val=extra_oc.get("min", float("-inf")),
                    max_val=extra_oc.get("max", float("inf")),
                ))

            condition = RuleCondition(
                channel_conditions=ch_conds,
                action=cond_data.get("action", ""),
            )

            transform = eff_data.get("transform_channels")
            effect = RuleEffect(
                energy_delta=eff_data.get("energy_delta", 0.0),
                destroy_object=eff_data.get("destroy_object", False),
                transform_channels=(
                    np.array(transform, dtype=np.float32) if transform is not None else None
                ),
            )

            parsed.append(Rule(
                rule_id=r.get("id", f"rule_{len(parsed)}"),
                condition=condition,
                effect=effect,
            ))

        self._rules = parsed
        self._version += 1

    def evaluate(
        self,
        world: WorldStateManager,
        agent_id: int,
        action: Action,
        target_object: ObjectSpec | None,
    ) -> list[RuleEffect]:
        """Evaluate all rules against an action and optional target object.

        Returns a list of effects to apply. Multiple rules can fire on the
        same action/object combination.
        """
        if target_object is None:
            return []

        effects: list[RuleEffect] = []
        for rule in self._rules:
            if rule.condition.matches(target_object, action):
                effects.append(rule.effect)
        return effects

    def apply_effects(
        self,
        world: WorldStateManager,
        agent_id: int,
        target_object_id: int,
        effects: list[RuleEffect],
    ) -> float:
        """Apply a list of effects to the world state.

        Returns the total energy delta for the agent.
        """
        total_energy = 0.0

        for eff in effects:
            total_energy += eff.energy_delta

            if eff.destroy_object and target_object_id in world._mutable_state().objects:
                world.remove_object(target_object_id)

            if eff.transform_channels is not None and target_object_id in world._mutable_state().objects:
                world.set_object_channels(target_object_id, eff.transform_channels)

        # Apply energy to agent
        if total_energy != 0.0:
            agent = world._mutable_state().agents[agent_id]
            new_energy = agent.energy + total_energy
            world.set_agent_energy(agent_id, new_energy)
            if new_energy <= 0.0:
                world.set_agent_alive(agent_id, False)

        return total_energy
