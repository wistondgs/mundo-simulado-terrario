"""Sitting an exam must not be an opportunity to study for it.

The first version of the guard named seven attributes by hand and missed two.
`A4.perceive` assigns `homeostasis._energy` directly, and that value reaches the
sampling temperature through `exploration_bias`; `_trace` grew by one event per
probe. Neither moved a number, because the exam never calls `decide` and so
never consumes the generator or reads the temperature -- but a hand-kept list
drifts from the code it guards, which is the whole reason the guard is derived
now rather than enumerated.
"""

import torch

from terrario.agent.agents import create_agent
from terrario.lab.capability_exam import build_probes, sit_exam


def _agent():
    torch.manual_seed(7)
    return create_agent("A4", {"num_channels": 4, "view_size": 5}, seed=7)


def _volatile(agent):
    return {
        "homeostasis_energy": agent.homeostasis._energy,
        "agent_trace": len(agent._trace),
        "episodic_trace": len(agent.episodic_memory._trace),
        "episodic_size": agent.episodic_memory.size,
        "step": agent._step,
        "last_action": agent._last_action,
        "hidden": float(agent._hidden.norm()),
        "generator": agent._generator.get_state().clone(),
    }


def test_sitting_an_exam_leaves_no_trace_on_the_organism():
    agent = _agent()
    before = _volatile(agent)
    sit_exam(agent, build_probes(40, seed=1))
    after = _volatile(agent)
    assert torch.equal(before.pop("generator"), after.pop("generator")), (
        "the exam consumed the agent's random generator")
    assert before == after


def test_the_homeostatic_energy_the_guard_used_to_miss_is_restored():
    """The specific field whose omission would have changed sampling temperature."""
    agent = _agent()
    agent.homeostasis._energy = 0.9          # a value no probe supplies
    sit_exam(agent, build_probes(20, seed=2))
    assert agent.homeostasis._energy == 0.9, (
        "perceive assigned the probe's 0.5 and the guard did not put it back; "
        "exploration_bias and the sampling temperature move with it")


def test_bank_order_does_not_change_what_a_bank_reports():
    """Three banks in sequence must not contaminate one another."""
    first, second = build_probes(30, seed=3), build_probes(30, seed=4)

    agent = _agent()
    alone = sit_exam(agent, second)["prediction"]

    agent = _agent()
    sit_exam(agent, first)
    after_another = sit_exam(agent, second)["prediction"]

    assert alone.status is after_another.status
    assert alone.value == after_another.value
