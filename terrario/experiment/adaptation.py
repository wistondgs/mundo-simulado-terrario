"""Preregistered H-ADAPT-001/v0.1 causal adaptation measurements."""

from __future__ import annotations

import math
import hashlib
import json
import os
import time
import tracemalloc
from pathlib import Path
from dataclasses import dataclass
from typing import Any

import numpy as np
import torch

from terrario.core.rng import RNGManager
from terrario.experiment.config import ExperimentConfig
from terrario.experiment.controller import ExperimentController, build_world_state, load_scenario, materialize_scenario
from terrario.experiment.specs import EvidenceRecord, EvidenceSpec
from terrario.observer.logger import ScientificObserver
from terrario.world.physics import Physics
from terrario.world.rules import RuleEngine
from terrario.world.scheduler import ChangeScheduler
from terrario.world.state import WorldStateManager


NOT_APPLICABLE = "NOT_APPLICABLE"
INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


@dataclass(frozen=True)
class AdaptationThresholds:
    pre_change_competence: float = 0.70
    expected_disruption_absolute_drop: float = 0.20
    recovery_fraction_of_pre: float = 0.90
    consecutive_recovery_windows: int = 2
    transfer_fraction_of_recovered: float = 0.80
    minimum_informative_interactions: int = 12
    window_steps: int = 100


def causal_competence(
    traces: list[dict[str, Any]], start: int, end: int, minimum_interactions: int = 12,
) -> dict[str, float | int | str]:
    """Observer-only correctness rate over informative interactions."""
    interactions = [
        trace["causal_interaction"] for trace in traces
        if start <= trace.get("step", -1) < end and trace.get("causal_interaction", {}).get("informative")
    ]
    count = len(interactions)
    if count < minimum_interactions:
        return {"status": INSUFFICIENT_EVIDENCE, "competence": math.nan, "opportunities": count}
    correct = sum(bool(interaction["causally_appropriate"]) for interaction in interactions)
    return {"status": "VALID", "competence": correct / count, "opportunities": count}


def prediction_metrics(
    traces: list[dict[str, Any]], change_step: int, predictor_available: bool,
    window_steps: int = 100,
) -> dict[str, float | str]:
    if not predictor_available:
        return {"prediction_error_spike": NOT_APPLICABLE, "prediction_error_decay": NOT_APPLICABLE}
    pre = [trace.get("prediction_error") for trace in traces if change_step - window_steps <= trace.get("step", -1) < change_step]
    post = [trace.get("prediction_error") for trace in traces if change_step <= trace.get("step", -1) < change_step + window_steps]
    pre = [float(value) for value in pre if value is not None]
    post = [float(value) for value in post if value is not None]
    if not pre or not post:
        return {"prediction_error_spike": math.nan, "prediction_error_decay": math.nan}
    baseline = float(np.mean(pre))
    spike = float(max(post) - baseline)
    x = np.arange(len(post), dtype=np.float64)
    decay = float(np.polyfit(x, np.asarray(post, dtype=np.float64), 1)[0]) if len(post) > 1 else 0.0
    return {"prediction_error_spike": spike, "prediction_error_decay": decay}


def adaptation_metrics(
    episode_data: dict[str, Any], change_step: int, predictor_available: bool,
    transfer_data: dict[str, Any] | None = None, thresholds: AdaptationThresholds = AdaptationThresholds(),
) -> dict[str, Any]:
    traces = episode_data["traces"]
    window = thresholds.window_steps
    pre = causal_competence(traces, max(0, change_step - window), change_step, thresholds.minimum_informative_interactions)
    immediate = causal_competence(traces, change_step, change_step + window, thresholds.minimum_informative_interactions)
    recovery_windows = [
        causal_competence(traces, start, start + window, thresholds.minimum_informative_interactions)
        for start in range(change_step + window, episode_data["num_steps"], window)
    ]
    pre_value = pre["competence"]
    immediate_value = immediate["competence"]
    post_drop = (
        float(pre_value - immediate_value)
        if pre["status"] == "VALID" and immediate["status"] == "VALID" else math.nan
    )
    recovery_target = pre_value * thresholds.recovery_fraction_of_pre if pre["status"] == "VALID" else math.nan
    recovery_latency: float | str = INSUFFICIENT_EVIDENCE
    recovered = math.nan
    for index in range(len(recovery_windows) - thresholds.consecutive_recovery_windows + 1):
        candidate = recovery_windows[index:index + thresholds.consecutive_recovery_windows]
        if all(item["status"] == "VALID" and item["competence"] >= recovery_target for item in candidate):
            recovery_latency = float(window + index * window)
            recovered = float(candidate[-1]["competence"])
            break

    old_positive_classes = {
        trace["causal_interaction"].get("hidden_causal_class") for trace in traces
        if trace.get("step", -1) < change_step and trace.get("causal_interaction", {}).get("causally_appropriate")
    }
    perseveration = sum(
        trace.get("causal_interaction", {}).get("hidden_causal_class") in old_positive_classes
        for trace in traces if change_step <= trace.get("step", -1) < change_step + window
        and trace.get("causal_interaction", {}).get("informative")
    )
    def entropy(start: int, end: int) -> float:
        classes = [trace["causal_interaction"].get("hidden_causal_class") for trace in traces
                   if start <= trace.get("step", -1) < end and trace.get("causal_interaction", {}).get("informative")]
        if not classes:
            return math.nan
        _, counts = np.unique(classes, return_counts=True)
        probs = counts / counts.sum()
        return float(-(probs * np.log2(probs)).sum())
    exploration_shift = entropy(change_step, change_step + window) - entropy(max(0, change_step - window), change_step)

    transfer = {"transfer_score": INSUFFICIENT_EVIDENCE}
    if transfer_data is not None:
        value = causal_competence(transfer_data["traces"], 0, transfer_data["num_steps"], thresholds.minimum_informative_interactions)
        transfer = {"transfer_score": value["competence"], "transfer_opportunities": value["opportunities"], "transfer_status": value["status"]}
    return {
        "pre_change_competence": pre_value, "pre_change_status": pre["status"], "pre_change_opportunities": pre["opportunities"],
        "post_change_drop": post_drop, "post_change_status": immediate["status"], "post_change_opportunities": immediate["opportunities"],
        "perseveration_count": int(perseveration), "recovery_latency": recovery_latency,
        "recovered_competence": recovered, "exploration_shift": exploration_shift,
        **prediction_metrics(traces, change_step, predictor_available, window), **transfer,
    }


def adaptation_criterion(metrics: dict[str, Any], thresholds: AdaptationThresholds = AdaptationThresholds()) -> str:
    """Classify the preregistered criterion without treating it as universal."""
    if metrics["pre_change_status"] != "VALID" or metrics["pre_change_competence"] < thresholds.pre_change_competence:
        return "NOT_LEARNED_PRE_CHANGE"
    drop = metrics["post_change_drop"]
    if not isinstance(drop, float) or math.isnan(drop):
        return "NO_DISRUPTION_OBSERVED"
    if drop < thresholds.expected_disruption_absolute_drop:
        return "NO_DISRUPTION_OBSERVED"
    if metrics["recovery_latency"] == INSUFFICIENT_EVIDENCE:
        return "FAILED_TO_RECOVER"
    if not isinstance(metrics["recovered_competence"], float) or metrics["recovered_competence"] < metrics["pre_change_competence"] * thresholds.recovery_fraction_of_pre:
        return "PARTIAL_RECOVERY"
    transfer_score = metrics.get("transfer_score")
    if isinstance(transfer_score, float) and not math.isnan(transfer_score) and transfer_score >= metrics["recovered_competence"] * thresholds.transfer_fraction_of_recovered:
        return "RECOVERED_AND_TRANSFERRED"
    return "RECOVERED"


VARIANTS: dict[str, dict[str, Any]] = {
    "A0_RANDOM": {"agent_type": "A0_RANDOM", "agent_config": {}},
    "A1_REACTIVE": {"agent_type": "A1_REACTIVE", "agent_config": {}},
    "A2_GRU": {"agent_type": "A2_GRU", "agent_config": {}},
    "A3_WORLD_MODEL": {"agent_type": "A3_WORLD_MODEL", "agent_config": {}},
    "A4_ADVANCED": {"agent_type": "A4_ADVANCED", "agent_config": {"use_planner": False}},
    "A4_NO_MEMORY": {"agent_type": "A4_ADVANCED", "agent_config": {"use_planner": False, "use_episodic_memory": False, "use_longterm_memory": False}},
    "A4_NO_PREDICTION": {"agent_type": "A4_ADVANCED", "agent_config": {"use_planner": False, "use_world_model": False}},
    "A4_NO_ONLINE_LEARNING": {"agent_type": "A4_ADVANCED", "agent_config": {"use_planner": False, "use_online_learning": False}},
}


def _phase_components(scenario: dict[str, Any]):
    world = WorldStateManager(
        build_world_state(scenario), scenario.get("duration", 500), scenario.get("max_energy", 100.0),
        scenario.get("step_energy_cost", 0.0), scenario.get("expose_time_fraction", True),
    )
    rules = RuleEngine()
    rules.load_rules(scenario.get("rules", {}))
    world.set_rules_version(rules.version)
    return world, rules, ChangeScheduler(scenario.get("changes", []), rules)


def _stable_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()


def _adaptive_state_hash(agent: Any) -> str:
    """Hash parameters plus mutable memory, excluding ordinary recurrent state."""
    digest = hashlib.sha256()
    for name, value in sorted(agent.get_parameters().items()):
        digest.update(name.encode())
        digest.update(value.detach().cpu().contiguous().numpy().tobytes())
    episodic = getattr(getattr(agent, "episodic_memory", None), "_buffer", [])
    for item in episodic:
        digest.update(item["embedding"].detach().cpu().contiguous().numpy().tobytes())
        digest.update(str((item["action"], item["energy_delta"], item["timestamp"])).encode())
    longterm = getattr(getattr(agent, "longterm_memory", None), "M", None)
    if longterm is not None:
        digest.update(longterm.detach().cpu().contiguous().numpy().tobytes())
    return digest.hexdigest()


def numerical_health(episode_data: dict[str, Any], agent: Any) -> dict[str, Any]:
    parameters = list(agent.get_parameters().values())
    nonfinite_events = sum(len(trace.get("numerical_events", [])) for trace in episode_data["traces"])
    memory = getattr(getattr(agent, "longterm_memory", None), "M", None)
    return {
        "finite_parameters": all(bool(torch.isfinite(value).all()) for value in parameters),
        "finite_memory": memory is None or bool(torch.isfinite(memory).all()),
        "nonfinite_learning_events": nonfinite_events,
        "aborted": episode_data["num_steps"] == 0,
    }


class AdaptationProtocolRunner:
    """Runs paired H-ADAPT-001 conditions and frozen transfer evaluations."""

    def __init__(
        self, scientific_scenario_path: str, transfer_scenario_path: str,
        output_dir: str, observer_mode: str = "scientific_standard", agent_overrides: dict[str, Any] | None = None,
    ):
        self.scientific_scenario = load_scenario(scientific_scenario_path)
        self.transfer_scenario = load_scenario(transfer_scenario_path)
        self.scientific_scenario_path = scientific_scenario_path
        self.output_dir = output_dir
        self.observer_mode = observer_mode
        self.agent_overrides = agent_overrides or {}

    def run_variant(self, variant_id: str, seed: int) -> dict[str, Any]:
        if variant_id not in VARIANTS:
            raise ValueError(f"Unknown H-ADAPT-001 variant: {variant_id}")
        variant = VARIANTS[variant_id]
        primary = materialize_scenario(self.scientific_scenario, seed)
        transfer = materialize_scenario(self.transfer_scenario, seed + 10_000_019)
        world_spec_hash = _stable_hash({"objects": primary["objects"], "changes": primary.get("changes", []), "rules": primary["rules"]})
        agent_seed = seed + 1_000_003
        config = ExperimentConfig(
            experiment_id="H-ADAPT-001", hypothesis=None, scenario_path=self.scientific_scenario_path,
            agent_types=[variant["agent_type"]], agent_config={**self.agent_overrides, **variant["agent_config"]},
            seeds=[seed], num_episodes=1, max_steps_per_episode=primary["duration"],
            # The protocol saves its single exact pre-transfer checkpoint below.
            # Periodic optimizer snapshots multiply storage without adding a
            # preregistered comparison point.
            observer_mode=self.observer_mode, checkpoint_every=0, output_dir=self.output_dir, device="cpu",
        )
        controller = ExperimentController(config)
        controller.scenario = primary
        RNGManager.set_global_determinism(agent_seed)
        agent = controller._create_agent(variant["agent_type"], agent_seed, primary)
        run_root = Path(self.output_dir) / "h_adapt_001" / variant_id / f"seed_{seed:08d}"
        tracemalloc.start()
        cpu_start, wall_start = time.process_time(), time.perf_counter()
        primary_world, primary_rules, primary_scheduler = _phase_components(primary)
        with ScientificObserver(str(run_root / "primary"), self.observer_mode, {
            "hypothesis_id": "H-ADAPT-001", "protocol_version": "0.1", "variant_id": variant_id,
            "seed": seed, "world_seed": seed, "agent_seed": agent_seed, "phase": "training",
        }) as primary_observer:
            primary_data = controller.run_episode(
                agent, primary_world, Physics(), primary_rules, primary_scheduler, primary_observer,
                agent_seed, scenario=primary, learning_enabled=True, phase="training",
            )
            change_step = primary["changes"][0]["at_step"]
            primary_observer.checkpoint(agent, primary_data["num_steps"], {
                "world_snapshot": primary_world.serialize(), "phase": "pre_transfer", "change_step": change_step,
            })
        before_transfer = {name: value.clone() for name, value in agent.get_parameters().items()}
        adaptive_state_before_transfer = _adaptive_state_hash(agent)
        transfer_world, transfer_rules, transfer_scheduler = _phase_components(transfer)
        with ScientificObserver(str(run_root / "transfer"), self.observer_mode, {
            "hypothesis_id": "H-ADAPT-001", "protocol_version": "0.1", "variant_id": variant_id,
            "seed": seed, "world_seed": seed + 10_000_019, "agent_seed": agent_seed, "phase": "transfer_no_learning",
        }) as transfer_observer:
            transfer_data = controller.run_episode(
                agent, transfer_world, Physics(), transfer_rules, transfer_scheduler, transfer_observer,
                agent_seed + 20_000_003, scenario=transfer, learning_enabled=False, phase="transfer_no_learning",
            )
        after_transfer = agent.get_parameters()
        transfer_parameters_unchanged = all(
            np.array_equal(value.detach().cpu().numpy(), after_transfer[name].detach().cpu().numpy())
            for name, value in before_transfer.items()
        )
        adaptive_state_after_transfer = _adaptive_state_hash(agent)
        _, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        predictor = variant["agent_type"] in {"A3_WORLD_MODEL", "A4_ADVANCED"} and variant_id != "A4_NO_PREDICTION"
        metrics = adaptation_metrics(primary_data, change_step, predictor, transfer_data)
        classification = adaptation_criterion(metrics)
        updates = getattr(getattr(agent, "learner", None), "step_count", getattr(agent, "_step", 0))
        invalid_reason = None
        if primary_data["num_steps"] < change_step + 2 * AdaptationThresholds().window_steps:
            invalid_reason = "episode_ended_before_recovery_window"
        observed_storage = sum(path.stat().st_size for path in run_root.rglob("*") if path.is_file())
        forensic_steps = 0
        if self.observer_mode == "forensic_full":
            # D4 has bounded change/recovery windows; transfer has no change
            # and is intentionally short, so it is captured in full.
            forensic_steps = min(primary_data["num_steps"], 501) + transfer_data["num_steps"]
        parameter_count = agent.parameter_count()
        checkpoint_estimate = max(64 * 1024, parameter_count * 4 * 3)
        return {
            "variant_id": variant_id, "seed": seed, "world_seed": seed, "agent_seed": agent_seed,
            "world_spec_hash": world_spec_hash,
            "change_step": change_step, "primary": primary_data, "transfer": transfer_data,
            "metrics": metrics, "classification": classification, "invalid_reason": invalid_reason,
            "agent_identity": agent.agent_identity, "trainable_parameter_count": parameter_count,
            "updates": updates, "gradient_steps": updates if variant_id != "A0_RANDOM" else 0,
            "wall_seconds": time.perf_counter() - wall_start, "cpu_seconds": time.process_time() - cpu_start,
            "peak_tracemalloc_bytes": peak_memory, "transfer_parameters_unchanged": transfer_parameters_unchanged,
            "transfer_adaptive_state_unchanged": adaptive_state_before_transfer == adaptive_state_after_transfer,
            "numerical_health": numerical_health(primary_data, agent),
            "checkpoint_ref": str(run_root / "primary" / "checkpoints" / f"step_{primary_data['num_steps']:08d}"),
            "observed_storage_bytes": observed_storage,
            "estimated_storage": estimate_trace_storage(
                primary_data["num_steps"] + transfer_data["num_steps"], forensic_steps, checkpoint_bytes=checkpoint_estimate,
            ),
        }

    def run(self, seeds: list[int], variants: list[str] | None = None) -> dict[str, Any]:
        selected = variants or list(VARIANTS)
        records = [self.run_variant(variant, seed) for seed in seeds for variant in selected]
        evidence = [
            EvidenceRecord(
                EvidenceSpec("adaptation", "H-ADAPT-001", f"{record['variant_id']}->recovery"),
                "H-ADAPT-001", f"{record['variant_id']}:seed-{record['seed']}",
                self.protocol_hash(), self.code_hash(), record["metrics"],
            ).to_dict()
            for record in records
        ]
        return {
            "records": records, "evidence": evidence, "summary": summarize_records(records),
            "pilot_diagnostic": diagnose_pilot(records, seeds, selected),
        }

    def protocol_hash(self) -> str:
        payload = {"scientific": self.scientific_scenario, "transfer": self.transfer_scenario, "variants": VARIANTS}
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    @staticmethod
    def code_hash() -> str:
        import subprocess
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def summarize_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {"variants": {}, "paired_ablations": {}}
    for variant_id in sorted({record["variant_id"] for record in records}):
        values = [record["metrics"].get("recovered_competence") for record in records if record["variant_id"] == variant_id]
        numeric = np.asarray([value for value in values if isinstance(value, float) and not math.isnan(value)], dtype=float)
        summary["variants"][variant_id] = {
            "n_total": sum(record["variant_id"] == variant_id for record in records),
            "n_valid": int(len(numeric)), "mean": float(numeric.mean()) if len(numeric) else math.nan,
            "median": float(np.median(numeric)) if len(numeric) else math.nan,
            "std": float(numeric.std()) if len(numeric) else math.nan,
            "iqr": float(np.percentile(numeric, 75) - np.percentile(numeric, 25)) if len(numeric) else math.nan,
        }
    full = {record["seed"]: record for record in records if record["variant_id"] == "A4_ADVANCED"}
    for ablation in ("A4_NO_MEMORY", "A4_NO_PREDICTION", "A4_NO_ONLINE_LEARNING"):
        differences = []
        for record in records:
            if record["variant_id"] != ablation or record["seed"] not in full:
                continue
            left, right = full[record["seed"]]["metrics"].get("recovered_competence"), record["metrics"].get("recovered_competence")
            if isinstance(left, float) and isinstance(right, float) and not math.isnan(left) and not math.isnan(right):
                differences.append(left - right)
        summary["paired_ablations"][ablation] = {"n": len(differences), "mean_difference": float(np.mean(differences)) if differences else math.nan, "by_seed": differences}
    return summary


def diagnose_pilot(records: list[dict[str, Any]], seeds: list[int], variants: list[str]) -> dict[str, Any]:
    """Validity gates for H-ADAPT-001; never a performance ranking."""
    expected = len(seeds) * len(variants)
    by_seed = {seed: [record for record in records if record["seed"] == seed] for seed in seeds}
    paired = all(len(group) == len(variants) and len({record["world_spec_hash"] for record in group}) == 1 for group in by_seed.values())
    health = [record["numerical_health"] for record in records]
    p1 = len(records) == expected and all(item["finite_parameters"] and item["finite_memory"] and not item["nonfinite_learning_events"] and not item["aborted"] for item in health)
    sufficient = [record for record in records if record["metrics"]["pre_change_status"] == "VALID" and record["metrics"]["post_change_status"] == "VALID"]
    predictors = [record for record in records if record["variant_id"] in {"A3_WORLD_MODEL", "A4_ADVANCED", "A4_NO_MEMORY", "A4_NO_ONLINE_LEARNING"}]
    prediction_real = all(isinstance(record["metrics"].get("prediction_error_spike"), float) and not math.isnan(record["metrics"]["prediction_error_spike"]) for record in predictors)
    transfer_frozen = all(record["transfer_parameters_unchanged"] and record["transfer_adaptive_state_unchanged"] for record in records)
    prelearned = any(record["metrics"]["pre_change_status"] == "VALID" and record["metrics"]["pre_change_competence"] >= AdaptationThresholds().pre_change_competence for record in records)
    random_values = [record["metrics"].get("pre_change_competence") for record in records if record["variant_id"] == "A0_RANDOM"]
    random_calibrated = all(not isinstance(value, float) or math.isnan(value) or value < AdaptationThresholds().pre_change_competence for value in random_values)
    gates = {
        "P1_numerical_integrity": p1, "P2_paired_worlds": paired,
        "P3_sufficient_signal": bool(sufficient), "P4_random_baseline_calibrated": random_calibrated,
        "P5_prechange_learning": prelearned, "P7_prediction_error_real": prediction_real,
        "P8_transfer_frozen": transfer_frozen,
    }
    return {"status": "PASS" if all(gates.values()) else "FAIL", "expected_runs": expected, "completed_runs": len(records), "gates": gates}


def estimate_trace_storage(
    steps: int, forensic_steps: int, latent_dim: int = 128, hidden_dim: int = 256,
    checkpoint_bytes: int = 0,
) -> dict[str, int]:
    """Conservative byte estimate for hybrid OBSERVE-02 storage."""
    standard_per_step = 16_384
    forensic_per_step = standard_per_step + 4 * (latent_dim + hidden_dim) + 1_250_000
    return {
        "standard_bytes": steps * standard_per_step,
        "forensic_bytes": forensic_steps * forensic_per_step,
        "checkpoint_bytes": checkpoint_bytes,
        "total_bytes": steps * standard_per_step + forensic_steps * (forensic_per_step - standard_per_step) + checkpoint_bytes,
    }


def lock_protocol(path: str, runner: AdaptationProtocolRunner, thresholds: AdaptationThresholds = AdaptationThresholds()) -> dict[str, Any]:
    lock = {
        "hypothesis_id": "H-ADAPT-001", "version": "0.1", "status": "LOCKED",
        "protocol_hash": runner.protocol_hash(), "code_hash": runner.code_hash(),
        "thresholds": thresholds.__dict__, "variants": list(VARIANTS),
    }
    lock_path = Path(path)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text(json.dumps(lock, indent=2, sort_keys=True))
    return lock
