import torch
import pytest

from terrario.agent.memory import LongTermMemory
from terrario.agent.temporal import SSMCore


def test_ssm_execution_clamps_an_unstable_learned_transition():
    core = SSMCore(1, 1)
    with torch.no_grad():
        core.a.fill_(2.0)
        core.B.zero_()
        core.C.fill_(1.0)
    _, state = core(torch.zeros(1, 1), torch.ones(1, 1))
    assert state.item() == pytest.approx(0.999)


def test_long_term_memory_repairs_nonfinite_state_before_write():
    memory = LongTermMemory(memory_slots=2, memory_dim=2, input_dim=2)
    with torch.no_grad():
        memory.M.fill_(float("nan"))
    trace = memory.write(torch.ones(2), torch.ones(2))
    assert trace["write_accepted"] is True
    assert torch.isfinite(memory.M).all()
