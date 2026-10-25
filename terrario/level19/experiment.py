"""Sealed L19 experiment: acquisition, passive prediction and causal choice.

The hidden key is confined to this world.  It determines outcomes but is never
passed to ``PredictiveStateLearner`` or its decision method.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from math import log, sqrt
from pathlib import Path
from typing import Any, Literal

import numpy as np

from terrario.level17.efference import ALL_COMMANDS, EfferenceCopy

from .persistence import load_checkpoint, save_checkpoint
from .predictive_state import PredictiveStateLearner


IMPLEMENTATION_ID = "LEARNER-19-v1"
TRAIN_SEEDS = tuple(range(310001, 310033))
HELD_OUT_SEEDS = tuple(range(320001, 320033))
TRAIN_EPISODES = 256
EVALUATION_EPISODES = 256

START = (0, 0, 0, 0)
CUE_0 = (1, 0, 0, 0)
CUE_1 = (0, 1, 0, 0)
SUCCESS = (0, 0, 1, 0)
FAILURE = (0, 0, 0, 1)
PROBES = (EfferenceCopy(ALL_COMMANDS[0]), EfferenceCopy(ALL_COMMANDS[1]))
CHOICES = PROBES


@dataclass(frozen=True)
class Episode:
    """Private world record. Only observations/actions leave this world."""

    hidden_key: int
    probe: EfferenceCopy
    cue: tuple[int, int, int, int]

    @property
    def target(self) -> EfferenceCopy:
        return CHOICES[self.hidden_key]


def _episode(rng: np.random.Generator, *, noise: float = 0.0) -> Episode:
    hidden = int(rng.integers(2))
    probe = PROBES[int(rng.integers(2))]
    cue_bit = hidden ^ probe.index
    if float(rng.random()) < noise:
        cue_bit ^= 1
    return Episode(hidden, probe, CUE_1 if cue_bit else CUE_0)


def _outcome(episode: Episode, action: EfferenceCopy) -> tuple[int, int, int, int]:
    return SUCCESS if action == episode.target else FAILURE


def _learn_episode(learner: PredictiveStateLearner, episode: Episode,
                   decision: EfferenceCopy) -> None:
    learner.begin()
    learner.observe(START, episode.probe, episode.cue)
    learner.observe(episode.cue, decision, _outcome(episode, decision))


def train(seed: int, *, episodes: int = TRAIN_EPISODES,
          action_aware: bool = True) -> PredictiveStateLearner:
    """Uniform exploration. Return/success never chooses training actions."""
    rng = np.random.default_rng([seed, 11])
    learner = PredictiveStateLearner(action_aware=action_aware)
    for _ in range(episodes):
        episode = _episode(rng)
        _learn_episode(learner, episode, CHOICES[int(rng.integers(2))])
    return learner


def _loss(model: PredictiveStateLearner, seed: int, *, episodes: int,
          noise: float) -> tuple[float, float]:
    """Passive held-out prediction, full state vs exactly pooled evidence."""
    rng = np.random.default_rng([seed, 29])
    full_total = 0.0
    reactive_total = 0.0
    for _ in range(episodes):
        episode = _episode(rng, noise=noise)
        action = CHOICES[int(rng.integers(2))]
        outcome = _outcome(episode, action)
        model.begin()
        model.follow(episode.probe, episode.cue)
        full_total -= log(max(model.probability(episode.cue, action, outcome), 1e-300))
        reactive_total -= log(max(model.reactive_probability(episode.cue, action, outcome), 1e-300))
        model.follow(action, outcome)
    return full_total / episodes, reactive_total / episodes


def _decision_trace(model: PredictiveStateLearner, seed: int, *, episodes: int,
                    noise: float) -> tuple[float, str]:
    """The only policy path: argmax of acquired predictive success probability."""
    rng = np.random.default_rng([seed, 43])
    successes = 0
    trace: list[dict[str, Any]] = []
    for t in range(episodes):
        episode = _episode(rng, noise=noise)
        model.begin()
        model.follow(episode.probe, episode.cue)
        before = model.current_state
        scores = [model.probability(episode.cue, action, SUCCESS) for action in CHOICES]
        selected = model.choose_for(episode.cue, SUCCESS, CHOICES)
        outcome = _outcome(episode, selected)
        successes += int(outcome == SUCCESS)
        trace.append({"t": t, "state": before, "probe": episode.probe.index,
                      "cue": episode.cue, "scores": scores,
                      "selected": selected.index, "outcome": outcome})
        model.follow(selected, outcome)
    encoded = json.dumps(trace, sort_keys=True, separators=(",", ":"))
    return successes / episodes, sha256(encoded.encode()).hexdigest()


def _lower_95(values: list[float]) -> float:
    array = np.asarray(values, dtype=float)
    if len(array) < 2:
        return float("-inf")
    return float(array.mean() - 1.96 * array.std(ddof=1) / sqrt(len(array)))


def life(seed: int, *, train_seed: int | None = None,
         train_episodes: int = TRAIN_EPISODES,
         evaluation_episodes: int = EVALUATION_EPISODES,
         checkpoint: str | Path | None = None) -> dict[str, Any]:
    """One paired life; held-out data does not enter any model update."""
    if seed not in HELD_OUT_SEEDS:
        raise ValueError("la vida de evaluación debe pertenecer a la ventana retenida")
    if train_seed is None:
        train_seed = seed - 10_000
    if train_seed not in TRAIN_SEEDS:
        raise ValueError("la vida de entrenamiento debe pertenecer a la ventana exploratoria")
    full = train(train_seed, episodes=train_episodes, action_aware=True)
    observation_only = train(train_seed, episodes=train_episodes, action_aware=False)
    state_before = full.fingerprint()

    def clone(model: PredictiveStateLearner) -> PredictiveStateLearner:
        return PredictiveStateLearner.from_state_dict(model.state_dict())

    checkpoint_hash = None
    restored_trace = None
    if checkpoint is not None:
        checkpoint_hash = save_checkpoint(checkpoint, full, {
            "implementation_id": IMPLEMENTATION_ID, "seed": seed,
            "train_seed": train_seed,
            "train_episodes": train_episodes,
        })
        restored, metadata, loaded_hash = load_checkpoint(checkpoint)
        if (metadata["seed"] != seed or metadata["train_seed"] != train_seed
                or loaded_hash != checkpoint_hash):
            raise RuntimeError("checkpoint L19 no conserva su procedencia")
        if restored.fingerprint() != state_before:
            raise RuntimeError("restauración L19 alteró estado adquirido")
        restored_trace = _decision_trace(restored, seed, episodes=evaluation_episodes, noise=0.0)[1]

    full_loss, reactive_loss = _loss(clone(full), seed, episodes=evaluation_episodes, noise=0.0)
    full_success, full_trace = _decision_trace(clone(full), seed, episodes=evaluation_episodes, noise=0.0)
    obs_success, _ = _decision_trace(clone(observation_only), seed, episodes=evaluation_episodes, noise=0.0)
    lesioned = clone(full)
    lesioned.lesion()
    lesion_success, lesion_trace = _decision_trace(lesioned, seed, episodes=evaluation_episodes, noise=0.0)
    perturbed_full = clone(full)
    perturbed_lesion = clone(full)
    perturbed_lesion.lesion()
    perturb_success, _ = _decision_trace(perturbed_full, seed, episodes=evaluation_episodes, noise=0.10)
    perturb_lesion, _ = _decision_trace(perturbed_lesion, seed, episodes=evaluation_episodes, noise=0.10)
    if checkpoint is not None and restored_trace != full_trace:
        raise RuntimeError("restauración L19 no reproduce selección")
    if full.fingerprint() != state_before:
        raise RuntimeError("evaluación L19 entrenó el modelo")
    return {
        "seed": seed,
        "train_seed": train_seed,
        "implementation_id": IMPLEMENTATION_ID,
        "predictive_loss_full": full_loss,
        "predictive_loss_reactive": reactive_loss,
        "predictive_gain": reactive_loss - full_loss,
        "success_full": full_success,
        "success_observation_only": obs_success,
        "success_lesioned": lesion_success,
        "decision_gain": full_success - lesion_success,
        "observation_action_gain": full_success - obs_success,
        "perturbed_success_full": perturb_success,
        "perturbed_success_lesioned": perturb_lesion,
        "perturbed_decision_gain": perturb_success - perturb_lesion,
        "states": len(full.states()),
        "splits": len(full.modifications()),
        "state_fingerprint": state_before,
        "full_trace_hash": full_trace,
        "lesion_trace_hash": lesion_trace,
        "checkpoint_hash": checkpoint_hash,
    }


def campaign(*, seeds: tuple[int, ...] = HELD_OUT_SEEDS,
             train_seeds: tuple[int, ...] = TRAIN_SEEDS,
             train_episodes: int = TRAIN_EPISODES,
             evaluation_episodes: int = EVALUATION_EPISODES,
             checkpoint_dir: str | Path | None = None) -> dict[str, Any]:
    # Tests may request a strict prefix of the preregistered held-out window;
    # pair it with the matching exploratory prefix, never with sampled seeds.
    if len(seeds) < len(train_seeds) and train_seeds == TRAIN_SEEDS:
        train_seeds = train_seeds[:len(seeds)]
    if set(seeds) & set(train_seeds):
        raise ValueError("las semillas retenidas no pueden ser de entrenamiento")
    if len(seeds) != len(train_seeds):
        raise ValueError("cada vida retenida necesita una vida exploratoria distinta")
    if not set(train_seeds).issubset(TRAIN_SEEDS):
        raise ValueError("las semillas exploratorias deben ser las predeclaradas")
    directory = Path(checkpoint_dir) if checkpoint_dir is not None else None
    lives = [life(seed, train_seed=train_seed, train_episodes=train_episodes,
                  evaluation_episodes=evaluation_episodes,
                  checkpoint=(directory / f"{seed}.json") if directory else None)
             for train_seed, seed in zip(train_seeds, seeds, strict=True)]
    predictive = [row["predictive_gain"] for row in lives]
    decision = [row["decision_gain"] for row in lives]
    action = [row["observation_action_gain"] for row in lives]
    perturbation = [row["perturbed_decision_gain"] for row in lives]
    accepted = (_lower_95(predictive) > 0.0 and _lower_95(decision) > 0.0
                and all(value > 0.0 for value in action)
                and _lower_95(perturbation) > 0.0)
    if accepted:
        verdict: Literal["CAPACIDAD_DEMOSTRADA", "RESULTADO_INCONCLUSO", "MECANISMO_REFUTADO"] = "CAPACIDAD_DEMOSTRADA"
    elif float(np.mean(predictive)) <= 0.0 and float(np.mean(decision)) <= 0.0:
        verdict = "MECANISMO_REFUTADO"
    else:
        verdict = "RESULTADO_INCONCLUSO"
    return {
        "schema_version": "terrario.level19.campaign/v1",
        "implementation_id": IMPLEMENTATION_ID,
        "train_seeds_reserved": TRAIN_SEEDS,
        "held_out_seeds": seeds,
        "train_episodes": train_episodes,
        "evaluation_episodes": evaluation_episodes,
        "lcb95_predictive_gain": _lower_95(predictive),
        "lcb95_decision_gain": _lower_95(decision),
        "lcb95_perturbed_decision_gain": _lower_95(perturbation),
        "verdict": verdict,
        "lives": lives,
    }
