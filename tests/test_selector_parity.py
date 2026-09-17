"""T1 must start behaving as T0, or the contrast confounds four things at once."""

import numpy as np
import pytest
import torch

from terrario.agent.agents import create_agent
from terrario.core.action_contract import (
    AddressingMode, MAX_TARGET_SLOTS, PerceivedTarget,
)
from terrario.core.types import Direction, Observation
from terrario.lab.selector_isolation import CHAIN, FIRST_PERMITTED, PairedStep, isolation_verdict


def _agent(mode, seed=11):
    torch.manual_seed(seed)
    return create_agent({"agent_id": "A4", "config": {"addressing_mode": mode}},
                        {"num_channels": 4, "view_size": 5}, seed=seed)


def _observe(agent):
    agent.perceive(Observation(
        channels=np.zeros((4, 5, 5), dtype=np.float32),
        mask=np.ones((5, 5), dtype=np.float32),
        agent_energy=0.5, time_fraction=0.1))


def _targets(offsets):
    return [PerceivedTarget(slot=i, handle=f"entity_{i:04x}", entity_id=i + 1,
                            offset=off, adjacent=abs(off[0]) + abs(off[1]) == 1)
            for i, off in enumerate(offsets)]


def test_the_residual_starts_at_zero():
    agent = _agent("T1_ENTITY")
    assert torch.count_nonzero(agent.selector_residual.weight) == 0
    assert torch.count_nonzero(agent.selector_residual.bias) == 0


def test_slot_log_odds_equal_direction_log_odds_at_initialisation():
    """The exact parity claim, stated so it does not depend on normalisation.

    T0 spreads its mass over five directions; T1 over however many entities were
    perceived. The supports differ, and that difference IS the representational
    content of entity addressing -- you cannot refer to an empty cell. What must
    match is the RELATIVE preference between two referents both contracts can
    name, and log-odds is that quantity without the normaliser.
    """
    agent = _agent("T1_ENTITY")
    _observe(agent)
    agent.offer_targets(_targets([(-1, 0), (0, 1), (1, 0)]))  # UP, RIGHT, DOWN
    agent._last_latent = torch.randn(agent.config["latent_dim"])
    state = agent._build_state(agent._last_latent, torch.zeros(agent.config["hidden_dim"]))

    slots = agent._slot_logits(state, 1.0)
    directional = agent.direction_head(state)
    pairs = [(0, Direction.UP), (1, Direction.RIGHT), (2, Direction.DOWN)]
    for (slot_a, dir_a), (slot_b, dir_b) in zip(pairs, pairs[1:]):
        slot_odds = float(slots[slot_a] - slots[slot_b])
        dir_odds = float(directional[int(dir_a)] - directional[int(dir_b)])
        assert slot_odds == pytest.approx(dir_odds, abs=1e-5), (
            "an entity slot does not inherit the prior of the direction that reaches it, "
            "so T1 starts from a different policy than T0 and the contrast is confounded")


def test_a_distant_slot_inherits_the_prior_of_no_direction():
    agent = _agent("T1_ENTITY")
    _observe(agent)
    agent.offer_targets(_targets([(2, 2)]))  # perceived, not in contact
    agent._last_latent = torch.randn(agent.config["latent_dim"])
    state = agent._build_state(agent._last_latent, torch.zeros(agent.config["hidden_dim"]))
    slots = agent._slot_logits(state, 1.0)
    directional = agent.direction_head(state)
    assert float(slots[0]) == pytest.approx(float(directional[int(Direction.NONE)]), abs=1e-5)


def test_unperceived_slots_cannot_be_chosen():
    agent = _agent("T1_ENTITY")
    _observe(agent)
    agent.offer_targets(_targets([(0, 1)]))
    agent._last_latent = torch.randn(agent.config["latent_dim"])
    state = agent._build_state(agent._last_latent, torch.zeros(agent.config["hidden_dim"]))
    slots = agent._slot_logits(state, 1.0)
    assert torch.softmax(slots, dim=-1)[1:].sum() < 1e-6


# ── The first-divergence gate ──────────────────────────────────────────

def _link(**overrides):
    base = {name: "same" for name in CHAIN}
    base.update(overrides)
    return base


def test_a_difference_at_the_selector_is_permitted():
    pair = PairedStep("s", _link(), _link(selector_representation="TARGET_ID"))
    assert isolation_verdict([pair])["INTERVENTION_ISOLATION"] == "PASS"


@pytest.mark.parametrize("link", [l for l in CHAIN if l != FIRST_PERMITTED])
def test_a_difference_before_the_selector_fails_isolation(link):
    # Each of these corresponds to a version of the contract that actually
    # shipped and was only caught later: the planner omitted, PUSH transformed,
    # the planner's direction discarded, a head initialised differently.
    pair = PairedStep("s", _link(), _link(**{link: "different"}))
    verdict = isolation_verdict([pair])
    assert verdict["INTERVENTION_ISOLATION"] == "FAIL"
    assert verdict["first_failures"][0]["first_divergence"] == link


def test_identical_arms_pass_because_most_operations_do_not_take_an_entity():
    pair = PairedStep("s", _link(), _link())
    assert isolation_verdict([pair])["INTERVENTION_ISOLATION"] == "PASS"
