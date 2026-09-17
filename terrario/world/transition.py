"""One semantics for a timestep, so a result means one thing.

Terrario grew three complete implementations of the same step -- the scientific
one in `ExperimentController.run_episode`, the engineering one in
`SandboxService._step_runtime`, and a third in `CausalRuntime.step` -- plus a
fourth inside the reproducibility test and its script. They diverged in physics,
not only in bookkeeping: the sandbox never instantiated `OpportunityLifecycle`,
so a scenario that declares a respawn cooldown of 3 to 8 steps ran there as a
strictly depleting world. Measured on D4T over 250 steps: 32 objects at the
start, 29 at the end, not one respawn.

The consequence is that "D4T" had no single meaning, and every recent result --
the screening, the paired T0/T1 rollout, the one-step twins, the capability
run -- was produced on the surface that is not the authoritative one.

This module holds the parts that decide what happened. Storage, streaming,
observers, run state, provenance and trace schemas stay with whichever surface
owns them: those can differ without the world differing.

Nothing here is new behaviour. Each function is lifted from the path that was
already correct, and the behaviour fixture -- nine cases over D2, D3 and D4,
compared field for field including its semantic digest -- is what proves the
lift changed nothing.
"""

from __future__ import annotations

from terrario.core.types import DIRECTION_DELTA, Action, ActionType, ObjectSpec
from terrario.world.state import WorldStateManager

#: The semantics a piece of evidence was produced under. It travels with the
#: result rather than being inferred later from a commit date, because the
#: question "which physics ran this?" had to be answered by reading code.
SEMANTICS_VERSION = "terrario.world.transition/v1"


def find_target(world: WorldStateManager, agent_id: int, action: Action) -> ObjectSpec | None:
    """The object a CONSUME acts on, by entity or by the faced cell.

    Lifted verbatim from two implementations that were character-for-character
    equivalent and written differently -- `ExperimentController._find_target`
    and the module-level `_find_target` in the sandbox. Keeping two was a drift
    waiting to happen: the third caller reached across packages for the
    controller's private method to avoid writing a third.

    Adjacency is Manhattan distance exactly 1, which excludes the agent's own
    cell and the diagonals. The `target_id` branch looks the entity up in world
    truth; that is safe only because the sole writer of `target_id` is a
    resolution that already checked the organism could perceive it.
    """
    if action.action_type != ActionType.CONSUME:
        return None
    truth = world._mutable_state()
    agent = truth.agents[agent_id]
    if action.target_id >= 0:
        target = truth.objects.get(action.target_id)
        if target is None:
            return None
        if abs(target.pos.x - agent.pos.x) + abs(target.pos.y - agent.pos.y) != 1:
            return None
        return target
    position = agent.pos + DIRECTION_DELTA[action.direction]
    return next((obj for obj in truth.objects.values() if obj.pos == position), None)
