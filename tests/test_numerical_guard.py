import torch

from terrario.agent.learner import OnlineLearner


def test_online_learner_skips_nonfinite_loss_without_mutating_parameters():
    module = torch.nn.Linear(1, 1)
    learner = OnlineLearner({"linear": module}, lr=0.1)
    before = module.weight.detach().clone()

    result = learner.step(total_loss=torch.tensor(float("nan"), requires_grad=True))

    assert result is None
    assert torch.equal(module.weight, before)
    assert learner.get_trace() == [{
        "op": "learning_skipped_nonfinite", "step": 1, "reason": "nonfinite_loss",
    }]
