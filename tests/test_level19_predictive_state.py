from __future__ import annotations

import json

import numpy as np
import pytest

from terrario.level17.efference import ALL_COMMANDS, EfferenceCopy
from terrario.level19.persistence import load_checkpoint, save_checkpoint
from terrario.level19.predictive_state import PredictiveStateError, PredictiveStateLearner


START = (0, 0, 0, 0)
CUE_0 = (1, 0, 0, 0)
CUE_1 = (0, 1, 0, 0)
SUCCESS = (0, 0, 1, 0)
FAILURE = (0, 0, 0, 1)
A0, A1 = (EfferenceCopy(ALL_COMMANDS[index]) for index in range(2))


def _teach(model: PredictiveStateLearner, episodes: int = 160) -> None:
    # The same sensory cue has opposite meaning after the two probes.  Only an
    # action-conditioned arrival signature can form useful predictive states.
    for i in range(episodes):
        probe = A0 if i % 2 == 0 else A1
        hidden = i % 2
        cue = CUE_1 if hidden ^ probe.index else CUE_0
        decision = A0 if hidden == 0 else A1
        model.begin()
        model.observe(START, probe, cue)
        model.observe(cue, decision, SUCCESS)


def test_acquired_state_routes_same_cue_by_prior_action_and_changes_prediction():
    model = PredictiveStateLearner()
    _teach(model)
    assert len(model.states()) > 1
    model.begin(); model.follow(A0, CUE_0)
    p_a0 = model.probability(CUE_0, A0, SUCCESS)
    model.begin(); model.follow(A1, CUE_0)
    p_a1 = model.probability(CUE_0, A0, SUCCESS)
    # Con prior uniforme sobre 16 observaciones, 80 éxitos dan 81/(80+16), no
    # una probabilidad artificialmente cercana a uno.
    assert p_a0 > 0.8
    assert p_a1 < 0.1
    assert all(event.log_evidence_gain > 0 for event in model.modifications())


def test_action_blind_control_cannot_disambiguate_same_cue():
    model = PredictiveStateLearner(action_aware=False)
    _teach(model)
    model.begin(); model.follow(A0, CUE_0)
    p_a0 = model.probability(CUE_0, A0, SUCCESS)
    model.begin(); model.follow(A1, CUE_0)
    p_a1 = model.probability(CUE_0, A0, SUCCESS)
    assert abs(p_a0 - p_a1) < 0.15


def test_prediction_precedes_outcome_and_follow_does_not_learn():
    model = PredictiveStateLearner()
    _teach(model)
    model.begin(); model.follow(A0, CUE_0)
    before = model.fingerprint()
    first = model.probability(CUE_0, A0, SUCCESS)
    model.follow(A0, SUCCESS)
    assert model.fingerprint() != before  # current causal filter position moved
    assert model.updates == 320
    model.begin(); model.follow(A0, CUE_0)
    assert model.probability(CUE_0, A0, SUCCESS) == first


def test_checkpoint_restores_complete_acquired_state_and_trace(tmp_path):
    model = PredictiveStateLearner()
    _teach(model)
    model.begin(); model.follow(A1, CUE_1)
    path = tmp_path / "learner.json"
    digest = save_checkpoint(path, model, {"seed": 17, "purpose": "test"})
    restored, metadata, loaded = load_checkpoint(path)
    assert metadata == {"seed": 17, "purpose": "test"}
    assert digest == loaded
    assert restored.fingerprint() == model.fingerprint()
    assert np.array_equal(restored.predict(CUE_1, A0), model.predict(CUE_1, A0))


def test_lesion_removes_structural_route_but_preserves_pooled_evidence():
    model = PredictiveStateLearner()
    _teach(model)
    pooled = model.aggregate_evidence().copy()
    model.lesion()
    assert model.states() == (0,)
    assert np.array_equal(model.aggregate_evidence(), pooled)


@pytest.mark.parametrize("bad", [0, "A0", ALL_COMMANDS[0], None])
def test_action_boundary_requires_efference_copy(bad):
    model = PredictiveStateLearner()
    with pytest.raises(PredictiveStateError):
        model.predict(START, bad)
