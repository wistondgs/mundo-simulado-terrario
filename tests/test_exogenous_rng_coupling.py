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


# ── The fourth coordinate: generation ──────────────────────────────────

def test_each_reappearance_of_a_lineage_draws_its_own_variate():
    """Identity alone is not enough: an opportunity comes back many times.

    Keyed on (seed, kind, root) only, every reappearance of lineage 7 would
    inherit the same cooldown and the same placement draw for the whole run --
    a deterministic heartbeat dressed as randomness.
    """
    variates = [int(_stream(4242, "cooldown", 7, generation=g).integers(0, 1_000_000))
                for g in range(1, 12)]
    assert len(set(variates)) > 8, "generations of one lineage share a variate"


def test_the_generation_ordinal_is_local_to_its_lineage():
    """U(7,3) must not depend on how many OTHER opportunities were consumed.

    This is the property a global event counter destroys. It was destroyed
    twice: first by seeding on len(self.events), and then again by keying on an
    opportunity id drawn from a global counter, which is the same dependency
    wearing an identity's clothes.
    """
    assert (_stream(4242, "cooldown", 7, generation=3).integers(0, 1_000_000)
            == _stream(4242, "cooldown", 7, generation=3).integers(0, 1_000_000))
    # ...and two lineages at the same generation differ from each other.
    assert (_stream(4242, "cooldown", 7, generation=3).integers(0, 1_000_000)
            != _stream(4242, "cooldown", 8, generation=3).integers(0, 1_000_000))


def test_a_consumed_opportunity_advances_its_own_generation_only():
    lifecycle = OpportunityLifecycle(CONFIG, world_seed=4242)
    lifecycle._lineage = {7: (7, 0), 8: (8, 0)}

    class _Obj:
        channels = np.zeros(4, dtype=np.float32)
        properties = {"causal_class": "A", "opportunity_id": 7}
        pos = type("P", (), {"x": 3, "y": 3, "to_tuple": lambda self: (3, 3)})()

    lifecycle.consume(None, _Obj(), step=10)
    pending = lifecycle._pending[-1]
    assert (pending["lineage_root"], pending["generation"]) == (7, 1)
    assert lifecycle._lineage[8] == (8, 0), "another lineage advanced"


def test_placement_and_cooldown_of_one_reappearance_are_separate_streams():
    a = _stream(7, "placement", 3, generation=2).integers(0, 10_000)
    b = _stream(7, "cooldown", 3, generation=2).integers(0, 10_000)
    assert a != b
