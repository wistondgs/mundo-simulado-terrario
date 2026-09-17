"""Trajectories may diverge; the shocks attached to an opportunity may not.

A paired comparison of two action contracts on one world seed only measures the
contract if the world's exogenous events are held across arms. The lifecycle
seeded its cooldown and placement draws from `len(self.events)` -- the number of
opportunities consumed so far -- so the schedule was a function of how often the
ORGANISM ate. T then reached the outcome twice: once as itself, and once through

    T -> RNG call order -> W_{t+1}

which is not separable after the fact by any amount of seeding at the top.
"""

import numpy as np
import pytest

from terrario.world.opportunities import OpportunityLifecycle, _stream

CONFIG = {"cooldown_steps": [3, 8], "placement_margin": 1, "minimum_agent_distance": 2,
          "recent_position_exclusion": 2}


def test_the_same_opportunity_draws_the_same_variate_whatever_came_before():
    early = _stream(4242, "cooldown", 7).integers(0, 1_000_000)
    late = _stream(4242, "cooldown", 7).integers(0, 1_000_000)
    assert early == late


def test_different_opportunities_draw_different_variates():
    variates = {int(_stream(4242, "cooldown", k).integers(0, 1_000_000)) for k in range(32)}
    assert len(variates) > 24, "the stream is not spreading across identities"


def test_cooldown_does_not_depend_on_how_many_events_preceded_it():
    """The property the old key violated, stated directly.

    Two lifecycles on one world seed, one of which has already handled a pile of
    other opportunities, must give opportunity 7 the same cooldown. Under the
    call-order key the second one drew from a stream forty steps down.
    """
    def cooldown_for_seventh(previous_events: int) -> int:
        lifecycle = OpportunityLifecycle(CONFIG, world_seed=4242)
        lifecycle.events = [object()] * previous_events
        return int(_stream(lifecycle._seed, "cooldown", 7).integers(3, 9))

    assert cooldown_for_seventh(0) == cooldown_for_seventh(40)


def test_the_placement_draw_is_keyed_on_identity_not_on_order():
    assert (_stream(99, "placement", 12).integers(0, 10_000)
            == _stream(99, "placement", 12).integers(0, 10_000))
    assert (_stream(99, "placement", 12).integers(0, 10_000)
            != _stream(99, "cooldown", 12).integers(0, 10_000)), (
        "placement and cooldown share a stream, so drawing one shifts the other")


def test_the_world_seed_still_controls_the_schedule():
    # The registry declares "world seed materializes layout; agent seed is
    # independently offset". Two world seeds must genuinely differ.
    assert (_stream(1, "cooldown", 5).integers(0, 1_000_000)
            != _stream(2, "cooldown", 5).integers(0, 1_000_000))
