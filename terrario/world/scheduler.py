"""ChangeScheduler — fires scheduled rule changes at specific simulation steps."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from terrario.core.events import RuleChangeEvent
from terrario.world.rules import RuleEngine
from terrario.world.state import WorldStateManager


@dataclass
class ScheduledChange:
    """A single scheduled rule change."""
    at_step: int
    rules: dict[str, Any]
    fired: bool = False


class ChangeScheduler:
    """Applies scheduled rule changes to the RuleEngine at designated steps.

    All changes are recorded as RuleChangeEvents for the observer.
    """

    def __init__(
        self,
        changes: list[dict[str, Any]],
        rule_engine: RuleEngine,
    ) -> None:
        self._rule_engine = rule_engine
        self._changes: list[ScheduledChange] = [
            ScheduledChange(at_step=c["at_step"], rules=c["rules"])
            for c in sorted(changes, key=lambda c: c["at_step"])
        ]
        self._history: list[RuleChangeEvent] = []

    @property
    def history(self) -> list[RuleChangeEvent]:
        """All rule change events that have fired, in order."""
        return list(self._history)

    @property
    def pending_count(self) -> int:
        """Number of changes that have not yet fired."""
        return sum(1 for c in self._changes if not c.fired)

    def check(self, world: WorldStateManager, step: int | None = None) -> list[RuleChangeEvent]:
        """Check whether any scheduled changes are due and apply them.

        Parameters
        ----------
        world:
            The WorldStateManager (used to read current time and update
            rules_version in the world state).

        Returns
        -------
        list[RuleChangeEvent]
            Events for each change that fired this step.
        """
        current_step = world._mutable_state().time if step is None else step
        fired: list[RuleChangeEvent] = []

        for change in self._changes:
            if change.fired or current_step < change.at_step:
                continue

            old_version = self._rule_engine.version
            self._rule_engine.load_rules(change.rules)
            new_version = self._rule_engine.version

            # Sync world state's rules_version
            world.set_rules_version(new_version)

            change.fired = True

            event = RuleChangeEvent(
                step=current_step,
                rules_version=new_version,
                old_version=old_version,
                new_version=new_version,
                reason=f"scheduled_change_at_step_{change.at_step}",
            )
            fired.append(event)

        self._history.extend(fired)
        return fired
