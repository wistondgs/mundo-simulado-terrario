"""A held-out examination for an acquired capability, not a survival score.

Survival is too distal. An organism can eat more because it wandered into a
denser corner, and an organism that learned something real can still die. The
capability needs an exam of its own, sat on entities it has never met, with
learning switched off while it sits.

The capability under test is deliberately small and cognitively real:

    learn from experience which PERCEPTUAL class yields a favourable or
    unfavourable consequence, and use that regularity in situations never
    experienced.

It cannot be solved from coordinates, identifiers, position, seed, direction,
order of appearance, a hardcoded planner or a scenario rule, because the probe
entities are generated fresh with channel values disjoint from anything the
organism could have encountered. What carries over is only the latent relation.

Three exams, kept apart, because a single number hides which link broke:

    PREDICTION   does the world model expect the right consequence?
    SELECTION    given alternatives, is the favourable one chosen?
    REALISATION  given the choice, is it executed against that referent?

So "predicts well, chooses badly" and "chooses well, acts badly" stay
distinguishable from "did not learn". Each has a known chance level -- 0.5 for
prediction and selection with two alternatives -- which is what makes the
readings interpretable instead of merely reportable.
"""

from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
import torch
import torch.nn.functional as F

from terrario.core.action_contract import (
    ActionIntent, AddressingMode, SelectorType, TargetStatus,
    perceive_targets, resolve,
)
from terrario.core.types import DIRECTION_DELTA, ActionType, Direction, Observation, Position
from terrario.experiment.controller import build_world_state
from terrario.lab.measurement_status import Reading, ratio

#: The D4T rule: channel 0 at or above 0.7 gives energy, at or below 0.3 costs
#: it. Everything between is inert. The bands below stay inside those thresholds
#: while being disjoint from each other, so a TEST entity obeys the same latent
#: relation as a TRAIN entity and shares no channel value with one.
FAVOURABLE_THRESHOLD = 0.7
UNFAVOURABLE_THRESHOLD = 0.3

TRAIN_BANDS = {"favourable": (0.70, 0.84), "unfavourable": (0.16, 0.30)}
TEST_BANDS = {"favourable": (0.86, 0.98), "unfavourable": (0.02, 0.14)}


@dataclass(frozen=True)
class Probe:
    """One exam question: two entities in contact, one good and one bad."""

    label: str
    scenario: dict[str, Any]
    favourable_direction: Direction
    unfavourable_direction: Direction
    favourable_entity: int
    unfavourable_entity: int
    channels: dict[str, list[float]]


def build_probes(count: int, *, bands: dict[str, tuple[float, float]] = TEST_BANDS,
                 seed: int = 20260917, grid: int = 14, channels: int = 4,
                 decorrelate_distractors: bool = False) -> list[Probe]:
    """Probe states with entities whose channel values were never experienced.

    `decorrelate_distractors` is the harder variant. In training, channel 1 runs
    opposite to channel 0, so an organism that latched onto channel 1 would look
    exactly as competent as one that learned the rule. Randomising the
    distractors here separates them: only a reading of channel 0 survives.
    """
    rng = random.Random(seed)
    probes: list[Probe] = []
    for index in range(count):
        x = rng.randrange(2, grid - 2)
        y = rng.randrange(2, grid - 2)
        directions = rng.sample([Direction.UP, Direction.DOWN, Direction.LEFT,
                                 Direction.RIGHT], 2)
        good_dir, bad_dir = directions
        good = _channels(rng, bands["favourable"], channels, decorrelate_distractors)
        bad = _channels(rng, bands["unfavourable"], channels, decorrelate_distractors)
        entries = []
        for direction, vector in ((good_dir, good), (bad_dir, bad)):
            dx, dy = DIRECTION_DELTA[direction]
            entries.append({"pos": [x + dx, y + dy], "channels": vector, "movable": False})
        probes.append(Probe(
            label=f"probe{index}",
            scenario={"grid_size": [grid, grid], "objects": entries,
                      "agent_start": {"pos": [x, y], "energy": 100.0}},
            favourable_direction=good_dir, unfavourable_direction=bad_dir,
            favourable_entity=0, unfavourable_entity=1,
            channels={"favourable": good, "unfavourable": bad}))
    return probes


def _channels(rng: random.Random, band: tuple[float, float], width: int,
              decorrelate: bool) -> list[float]:
    primary = rng.uniform(*band)
    if decorrelate:
        rest = [rng.uniform(0.0, 1.0) for _ in range(width - 1)]
    else:
        rest = [1.0 - primary] + [rng.uniform(0.1, 0.4) for _ in range(width - 2)]
    return [round(primary, 4)] + [round(v, 4) for v in rest]


def _observation(state, view_size: int, channels: int) -> Observation:
    half = view_size // 2
    agent = state.agents[0]
    window = np.zeros((channels, view_size, view_size), dtype=np.float32)
    for obj in state.objects.values():
        dx, dy = obj.pos.x - agent.pos.x, obj.pos.y - agent.pos.y
        if abs(dx) <= half and abs(dy) <= half:
            values = np.asarray(obj.channels, dtype=np.float32)[:channels]
            window[:len(values), dx + half, dy + half] = values
    return Observation(channels=window, mask=np.ones((view_size, view_size), dtype=np.float32),
                       agent_energy=0.5, time_fraction=0.0)


def sit_exam(agent: Any, probes: Sequence[Probe], *, view_size: int = 5,
             channels: int = 4) -> dict[str, Any]:
    """Sit the three exams with no learning and no world advance.

    The agent's parameters are not touched: `learn` is never called, no
    transition is constructed, and the world never steps. Sitting an exam must
    not be an opportunity to study for it.
    """
    predictions = selections = realisations = 0
    predictable = selectable = realisable = 0
    mode = getattr(agent, "_addressing_mode", AddressingMode.T0_DIRECTIONAL)
    details = []

    for probe in probes:
        state = build_world_state(probe.scenario)
        observation = _observation(state, view_size, channels)
        agent.perceive(observation)
        latent = getattr(agent, "_last_latent", None)
        if latent is None:
            continue
        hidden = torch.zeros(agent.config["hidden_dim"], device=latent.device,
                             dtype=latent.dtype)
        cognition = agent._build_state(latent, hidden)

        targets, _ = perceive_targets(state, 0, view_size, salt=probe.label, step=0)
        if hasattr(agent, "offer_targets"):
            agent.offer_targets(targets)

        # ── PREDICTION ────────────────────────────────────────────────
        # The world model is asked what consuming in each direction would cost
        # or yield. Chance is 0.5: it need only rank the two.
        good_action = int(ActionType.CONSUME) * len(Direction) + int(probe.favourable_direction)
        bad_action = int(ActionType.CONSUME) * len(Direction) + int(probe.unfavourable_direction)
        if getattr(agent, "_use_world_model", False):
            with torch.no_grad():
                _, good_energy, _ = agent.world_model(
                    cognition, agent._action_to_onehot(good_action))
                _, bad_energy, _ = agent.world_model(
                    cognition, agent._action_to_onehot(bad_action))
            gap = float(good_energy.item()) - float(bad_energy.item())
            if abs(gap) < 1e-9:
                # A model that predicts the same for both expresses no
                # preference. Scoring a tie as wrong would report a degenerate
                # constant predictor at 0.0 -- confidently backwards -- when the
                # truth is that it said nothing. Ties leave the denominator.
                correct = None
            else:
                predictable += 1
                correct = gap > 0
                predictions += correct
        else:
            correct = None

        # ── SELECTION ─────────────────────────────────────────────────
        # Which referent the policy prefers, read from the distribution rather
        # than from one sample, so the reading is the preference and not a coin.
        preference = _selection_preference(agent, cognition, probe, targets, mode)
        if preference is not None:
            selectable += 1
            selections += preference > 0.5

        # ── REALISATION ───────────────────────────────────────────────
        # Given the intention to act on the favourable entity, does the contract
        # resolve to it?
        realised = _realises(probe, targets, state, mode)
        if realised is not None:
            realisable += 1
            realisations += realised

        details.append({"probe": probe.label, "prediction_correct": correct,
                        "selection_preference": preference, "realised": realised})

    return {
        "prediction": ratio(predictions, predictable, what="prediction on held-out"),
        "selection": ratio(selections, selectable, what="selection on held-out"),
        "realisation": ratio(realisations, realisable, what="realisation on held-out"),
        "n_probes": len(probes), "chance_level": 0.5, "details": details[:50],
    }


def _selection_preference(agent, cognition, probe, targets, mode) -> float | None:
    """P(favourable) among the two alternatives, renormalised over the pair."""
    if mode is AddressingMode.T1_ENTITY and hasattr(agent, "_slot_logits"):
        logits = agent._slot_logits(cognition, 1.0)
        good = next((t.slot for t in targets if t.entity_id == probe.favourable_entity), None)
        bad = next((t.slot for t in targets if t.entity_id == probe.unfavourable_entity), None)
        if good is None or bad is None:
            return None
        pair = torch.softmax(torch.stack([logits[good], logits[bad]]), dim=-1)
        return float(pair[0].item())
    head = getattr(agent, "direction_head", None)
    with torch.no_grad():
        logits = head(cognition) if head is not None else agent.policy_head(cognition)
    if logits.numel() == len(Direction):
        good, bad = int(probe.favourable_direction), int(probe.unfavourable_direction)
    else:
        good = int(ActionType.CONSUME) * len(Direction) + int(probe.favourable_direction)
        bad = int(ActionType.CONSUME) * len(Direction) + int(probe.unfavourable_direction)
    pair = torch.softmax(torch.stack([logits[good], logits[bad]]), dim=-1)
    return float(pair[0].item())


def _realises(probe, targets, state, mode) -> bool | None:
    if mode is AddressingMode.T1_ENTITY:
        slot = next((t.slot for t in targets if t.entity_id == probe.favourable_entity), None)
        if slot is None:
            return False
        intent = ActionIntent(ActionType.CONSUME, SelectorType.TARGET_ID, slot)
    else:
        intent = ActionIntent(ActionType.CONSUME, SelectorType.DIRECTION,
                              int(probe.favourable_direction))
    outcome = resolve(intent, targets, state, 0)
    return (outcome.status is TargetStatus.VALID
            and outcome.entity_id == probe.favourable_entity)


def causal_gain(learner_after: dict, learner_before: dict,
                frozen_after: dict, frozen_before: dict, exam: str) -> dict[str, Any]:
    """G = [L_after - L_before] - [F_after - F_before], on the same exam.

    The double difference is not ceremony. The frozen twin's own score can move
    without any parameter changing, because its recurrent state and its memories
    advanced through the same experience; subtracting only the learner's own
    before-score would credit that drift to learning. What G isolates is the
    contribution of the UPDATES, with exposure held identical by construction.
    """
    readings = {"L_after": learner_after[exam], "L_before": learner_before[exam],
                "F_after": frozen_after[exam], "F_before": frozen_before[exam]}
    if not all(r.evaluable for r in readings.values()):
        return {"status": "NOT_EVALUABLE",
                "reason": "an arm reported no support on this exam",
                "readings": {k: v.as_record() for k, v in readings.items()}}
    learner_delta = float(readings["L_after"]) - float(readings["L_before"])
    frozen_delta = float(readings["F_after"]) - float(readings["F_before"])
    return {"status": "OK", "exam": exam,
            "learner_delta": round(learner_delta, 6),
            "frozen_delta": round(frozen_delta, 6),
            "G": round(learner_delta - frozen_delta, 6),
            "readings": {k: v.as_record() for k, v in readings.items()}}
