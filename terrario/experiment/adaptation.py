"""Preregistered H-ADAPT-001/v0.1 causal adaptation measurements."""

from __future__ import annotations

import math
import hashlib
import json
import os
import time
import tracemalloc
from pathlib import Path
from dataclasses import asdict, dataclass
from typing import Any, Callable

import numpy as np
import torch

from terrario.core.rng import RNGManager
from terrario.agent.device import device_status
from terrario.experiment.config import ExperimentConfig
from terrario.experiment.campaign import (
    ExperimentalValidity,
    ReasonCode,
    RunCompletionCertificate,
    RunIdentity,
    ValidityField,
    build_evidence_manifest,
    build_trace_manifest,
    directory_hash,
    stable_hash,
    storage_governance,
    verify_run_completion,
    write_manifest,
)
from terrario.experiment.controller import ExperimentController, build_world_state, load_scenario, materialize_scenario
from terrario.experiment.specs import EvidenceRecord, EvidenceSpec
from terrario.experiment.statistics import descriptive, paired_comparison, sensitivity_label
from terrario.observer.logger import ScientificObserver
from terrario.observer.windows import ForensicWindowPolicy
from terrario.world.physics import Physics
from terrario.world.rules import RuleEngine
from terrario.world.scheduler import ChangeScheduler
from terrario.world.state import WorldStateManager
from terrario.world.opportunities import summarize_opportunity_contract


NOT_APPLICABLE = "NOT_APPLICABLE"
INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
PROTOCOL_VERSION = "0.2"


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


def assess_run_validity(record: dict[str, Any], thresholds: AdaptationThresholds = AdaptationThresholds()) -> ExperimentalValidity:
    """Classify run validity before considering its adaptation outcome."""
    health = record["numerical_health"]
    technical = (
        health["finite_parameters"] and health["finite_memory"]
        and not health["nonfinite_learning_events"] and not health["aborted"]
    )
    technical_reason = ReasonCode.VALID_UNCLASSIFIED if technical else (
        ReasonCode.NUMERICAL_FAILURE if health["nonfinite_learning_events"] or not health["finite_parameters"] or not health["finite_memory"]
        else ReasonCode.TECHNICAL_FAILURE
    )
    opportunity = record.get("opportunity_contract")
    world_signal = True if opportunity is None else (
        opportunity["record_count"] > 0
        and opportunity["all_spawn_positions_reachable"]
        and opportunity["concurrent_balance_pass"]
    )
    metrics = record["metrics"]
    interaction = metrics["pre_change_status"] == "VALID" and metrics["post_change_status"] == "VALID"
    prelearned = interaction and metrics["pre_change_competence"] >= thresholds.pre_change_competence
    primary_steps = record.get("primary", {}).get("num_steps")
    change_exposure = (
        interaction if primary_steps is None
        else primary_steps >= record["change_step"] + 2 * thresholds.window_steps
    )
    transfer = record["transfer_parameters_unchanged"] and record["transfer_adaptive_state_unchanged"]
    interpretable = technical and world_signal and interaction and prelearned and change_exposure and transfer
    classification = ReasonCode(record.get("classification", ReasonCode.VALID_UNCLASSIFIED))
    return ExperimentalValidity(
        ValidityField(technical, technical_reason, health),
        ValidityField(world_signal, ReasonCode.VALID_UNCLASSIFIED if world_signal else ReasonCode.WORLD_SIGNAL_FAILURE, opportunity or {}),
        ValidityField(interaction, ReasonCode.VALID_UNCLASSIFIED if interaction else ReasonCode.INSUFFICIENT_AGENT_INTERACTION, {
            "pre_change_status": metrics["pre_change_status"], "post_change_status": metrics["post_change_status"],
        }),
        ValidityField(prelearned, ReasonCode.VALID_UNCLASSIFIED if prelearned else ReasonCode.NOT_LEARNED_PRE_CHANGE, {
            "competence": metrics["pre_change_competence"], "threshold": thresholds.pre_change_competence,
        }),
        ValidityField(change_exposure, ReasonCode.VALID_UNCLASSIFIED if change_exposure else ReasonCode.NO_DISRUPTION_OBSERVED, {
            "change_step": record.get("change_step"), "primary_steps": primary_steps,
        }),
        ValidityField(transfer, ReasonCode.VALID_UNCLASSIFIED if transfer else ReasonCode.TRANSFER_CONTAMINATED, {}),
        ValidityField(interpretable, ReasonCode.VALID_UNCLASSIFIED if interpretable else (
            technical_reason if not technical else ReasonCode.WORLD_SIGNAL_FAILURE if not world_signal else
            ReasonCode.INSUFFICIENT_AGENT_INTERACTION if not interaction else ReasonCode.NOT_LEARNED_PRE_CHANGE if not prelearned else
            ReasonCode.NO_DISRUPTION_OBSERVED if not change_exposure else ReasonCode.TRANSFER_CONTAMINATED
        ), {}),
        classification,
    )


class AdaptationProtocolRunner:
    """Runs paired H-ADAPT-001 conditions and frozen transfer evaluations."""

    def __init__(
        self, scientific_scenario_path: str, transfer_scenario_path: str,
        output_dir: str, observer_mode: str = "scientific_standard", agent_overrides: dict[str, Any] | None = None,
        device: str = "cpu",
    ):
        self.scientific_scenario = load_scenario(scientific_scenario_path)
        self.transfer_scenario = load_scenario(transfer_scenario_path)
        self.scientific_scenario_path = scientific_scenario_path
        self.output_dir = output_dir
        self.observer_mode = observer_mode
        self.agent_overrides = agent_overrides or {}
        self.device = device

    def run_variant(self, variant_id: str, seed: int) -> dict[str, Any]:
        if variant_id not in VARIANTS:
            raise ValueError(f"Unknown H-ADAPT-001 variant: {variant_id}")
        variant = VARIANTS[variant_id]
        primary = materialize_scenario(self.scientific_scenario, seed)
        transfer = materialize_scenario(self.transfer_scenario, seed + 10_000_019)
        world_spec_hash = _stable_hash(primary)
        agent_seed = seed + 1_000_003
        config = ExperimentConfig(
            experiment_id="H-ADAPT-001", hypothesis=None, scenario_path=self.scientific_scenario_path,
            agent_types=[variant["agent_type"]], agent_config={**self.agent_overrides, **variant["agent_config"]},
            seeds=[seed], num_episodes=1, max_steps_per_episode=primary["duration"],
            # The protocol saves its single exact pre-transfer checkpoint below.
            # Periodic optimizer snapshots multiply storage without adding a
            # preregistered comparison point.
            observer_mode=self.observer_mode, checkpoint_every=0, output_dir=self.output_dir, device=self.device,
        )
        controller = ExperimentController(config)
        controller.scenario = primary
        RNGManager.set_global_determinism(agent_seed)
        agent = controller._create_agent(variant["agent_type"], agent_seed, primary)
        run_root = Path(self.output_dir) / "h_adapt_001" / variant_id / f"seed_{seed:08d}"
        tracemalloc.start()
        cpu_start, wall_start = time.process_time(), time.perf_counter()
        primary_world, primary_rules, primary_scheduler = _phase_components(primary)
        primary_start_state_hash = primary_world._mutable_state().state_hash()
        with ScientificObserver(str(run_root / "primary"), self.observer_mode, {
            "hypothesis_id": "H-ADAPT-001", "protocol_version": PROTOCOL_VERSION, "variant_id": variant_id,
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
            "hypothesis_id": "H-ADAPT-001", "protocol_version": PROTOCOL_VERSION, "variant_id": variant_id,
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
        identity = RunIdentity(
            "H-ADAPT-001", PROTOCOL_VERSION, variant_id, seed, agent_seed,
            config.config_hash(), self.code_hash(),
        )
        opportunity_contract = summarize_opportunity_contract(primary_data)
        record = {
            "variant_id": variant_id, "seed": seed, "world_seed": seed, "agent_seed": agent_seed,
            "run_id": identity.run_id, "run_identity": asdict(identity),
            "world_spec_hash": world_spec_hash,
            "change_step": change_step, "primary": primary_data, "transfer": transfer_data,
            "metrics": metrics, "classification": classification, "invalid_reason": invalid_reason,
            "agent_identity": agent.agent_identity, "trainable_parameter_count": parameter_count,
            "updates": updates, "gradient_steps": updates if variant_id != "A0_RANDOM" else 0,
            "wall_seconds": time.perf_counter() - wall_start, "cpu_seconds": time.process_time() - cpu_start,
            "peak_tracemalloc_bytes": peak_memory, "transfer_parameters_unchanged": transfer_parameters_unchanged,
            "transfer_adaptive_state_unchanged": adaptive_state_before_transfer == adaptive_state_after_transfer,
            "numerical_health": numerical_health(primary_data, agent),
            "opportunity_contract": opportunity_contract,
            "checkpoint_ref": str(run_root / "primary" / "checkpoints" / f"step_{primary_data['num_steps']:08d}"),
            "observed_storage_bytes": observed_storage,
            "estimated_storage": estimate_trace_storage(
                primary_data["num_steps"] + transfer_data["num_steps"], forensic_steps, checkpoint_bytes=checkpoint_estimate,
            ),
        }
        validity = assess_run_validity(record)
        record["validity"] = asdict(validity)
        forensic_windows = []
        if self.observer_mode == "forensic_full":
            forensic_windows = ForensicWindowPolicy(change_step).windows(primary_data["num_steps"])
            forensic_windows.append({"phase": "transfer", "start_step": 0, "end_step": transfer_data["num_steps"] - 1})
        trace_manifest = build_trace_manifest(run_root, identity.run_id, self.observer_mode, forensic_windows)
        trace_path = run_root / "TRACE_MANIFEST.json"
        write_manifest(trace_path, trace_manifest)
        evidence_manifest = build_evidence_manifest(run_root, identity.run_id, {
            "protocol_hash": self.protocol_hash(), "code_hash": self.code_hash(), "config_hash": config.config_hash(),
        })
        evidence_path = run_root / "EVIDENCE_MANIFEST.json"
        write_manifest(evidence_path, evidence_manifest)
        certificate = RunCompletionCertificate(
            identity.run_id,
            primary_start_state_hash,
            primary_data["traces"][-1]["state_hash"] if primary_data["traces"] else "aborted",
            evidence_manifest.digest(), stable_hash(metrics), directory_hash(record["checkpoint_ref"]),
            validity.technical_valid.reason, self.code_hash(), config.config_hash(),
        )
        certificate_path = run_root / "RUN_COMPLETION_CERTIFICATE.json"
        certificate_path.write_text(json.dumps(asdict(certificate), indent=2, sort_keys=True, default=str))
        record.update({
            "trace_manifest_path": str(trace_path), "evidence_manifest_path": str(evidence_path),
            "completion_certificate_path": str(certificate_path), "completion_certificate": asdict(certificate),
        })
        return record

    @staticmethod
    def _record_is_complete(record: dict[str, Any]) -> bool:
        certificate = record.get("completion_certificate_path")
        manifest = record.get("evidence_manifest_path")
        return bool(certificate and manifest and Path(certificate).is_file() and Path(manifest).is_file() and verify_run_completion(certificate, manifest))

    @staticmethod
    def _is_experimentally_interpretable(record: dict[str, Any]) -> bool:
        saved = record.get("validity", {}).get("experimentally_interpretable", {}).get("passed")
        return bool(saved) if saved is not None else assess_run_validity(record).experimentally_interpretable.passed

    def _result(self, records: list[dict[str, Any]], seeds: list[int], selected: list[str]) -> dict[str, Any]:
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
            "analysis": analyze_records(records),
            "pilot_diagnostic": diagnose_pilot(records, seeds, selected),
        }

    def run(
        self, seeds: list[int], variants: list[str] | None = None, existing_records: list[dict[str, Any]] | None = None,
        resume: bool = False, retry_invalid: bool = False, progress_path: str | Path | None = None,
    ) -> dict[str, Any]:
        selected = variants or list(VARIANTS)
        prior = {(record["variant_id"], record["seed"]): record for record in existing_records or []}
        records: list[dict[str, Any]] = []
        for seed in seeds:
            for variant in selected:
                previous = prior.get((variant, seed))
                reuse = (
                    resume and previous is not None and self._record_is_complete(previous)
                    and (not retry_invalid or self._is_experimentally_interpretable(previous))
                )
                records.append(previous if reuse else self.run_variant(variant, seed))
                if progress_path:
                    Path(progress_path).write_text(json.dumps(self._result(records, seeds, selected), indent=2, default=str))
        return self._result(records, seeds, selected)

    def preflight(self, seeds: list[int], variants: list[str]) -> dict[str, Any]:
        """Validate executable campaign prerequisites without running an agent."""
        checks = {
            "paired_seed_set": len(seeds) == len(set(seeds)) and bool(seeds),
            "known_variants": bool(variants) and set(variants).issubset(VARIANTS),
            "scientific_lifecycle_enabled": bool(self.scientific_scenario.get("opportunity_lifecycle")),
            "scientific_change_defined": len(self.scientific_scenario.get("changes", [])) == 1,
            "transfer_has_no_learning_change": not self.transfer_scenario.get("changes", []),
            "observer_mode_supported": self.observer_mode in ScientificObserver.VALID_MODES,
        }
        execution_device = device_status(self.device)
        checks["execution_device_available"] = bool(execution_device["available"])
        steps_per_run = int(self.scientific_scenario["duration"]) + int(self.transfer_scenario["duration"])
        projected = estimate_trace_storage(steps_per_run * len(seeds) * len(variants), 0)
        storage = storage_governance(self.output_dir, projected["total_bytes"])
        checks["storage_budget_available"] = bool(storage["within_budget"])
        return {
            "status": "READY" if all(checks.values()) else "BLOCKED",
            "checks": checks,
            "planned_runs": len(seeds) * len(variants),
            "estimated_storage": projected,
            "storage_governance": storage,
            "execution_device": execution_device,
            "protocol_hash": self.protocol_hash(), "code_hash": self.code_hash(),
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


def analyze_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Descriptive, paired analysis over runs that meet every validity gate."""
    interpretable = [record for record in records if assess_run_validity(record).experimentally_interpretable.passed]
    variants: dict[str, Any] = {}
    for variant_id in sorted({record["variant_id"] for record in records}):
        group = [record for record in interpretable if record["variant_id"] == variant_id]
        metrics = {
            name: [record["metrics"].get(name) for record in group]
            for name in ("pre_change_competence", "post_change_drop", "recovered_competence", "recovery_latency", "transfer_score")
        }
        variants[variant_id] = {
            "n_total": sum(record["variant_id"] == variant_id for record in records),
            "n_experimentally_interpretable": len(group),
            "metrics": {name: descriptive([value for value in values if isinstance(value, float)]) for name, values in metrics.items()},
        }
    paired: dict[str, Any] = {}
    full = {
        record["seed"]: record["metrics"].get("recovered_competence")
        for record in interpretable if record["variant_id"] == "A4_ADVANCED"
    }
    for ablation in ("A4_NO_MEMORY", "A4_NO_PREDICTION", "A4_NO_ONLINE_LEARNING"):
        ablated = {
            record["seed"]: record["metrics"].get("recovered_competence")
            for record in interpretable if record["variant_id"] == ablation
        }
        paired[ablation] = paired_comparison(full, ablated, seed=0)
    sensitivity = []
    for threshold in (0.65, 0.70, 0.75):
        eligible = [
            record for record in interpretable
            if record["metrics"].get("pre_change_competence", math.nan) >= threshold
        ]
        sensitivity.append({"pre_change_competence_threshold": threshold, "n_eligible": len(eligible)})
    reference = sensitivity[1]["n_eligible"] / len(interpretable) if interpretable else math.nan
    alternatives = [item["n_eligible"] / len(interpretable) for item in sensitivity] if interpretable else []
    return {
        "analysis_population": {
            "n_completed": len(records), "n_experimentally_interpretable": len(interpretable),
            "excluded_run_ids": [record.get("run_id") for record in records if record not in interpretable],
        },
        "variants": variants, "paired_ablations": paired,
        "sensitivity": {"grid": sensitivity, "stability": sensitivity_label(reference, alternatives)},
    }


def diagnose_pilot(records: list[dict[str, Any]], seeds: list[int], variants: list[str]) -> dict[str, Any]:
    """Validity gates for H-ADAPT-001; never a performance ranking."""
    expected = len(seeds) * len(variants)
    by_seed = {seed: [record for record in records if record["seed"] == seed] for seed in seeds}
    paired = all(len(group) == len(variants) and len({record["world_spec_hash"] for record in group}) == 1 for group in by_seed.values())
    validities = [assess_run_validity(record) for record in records]
    p1 = len(records) == expected and all(item.technical_valid.passed for item in validities)
    world_signal = all(item.world_signal_sufficient.passed for item in validities)
    interactions = all(item.agent_interaction_sufficient.passed for item in validities)
    predictors = [record for record in records if record["variant_id"] in {"A3_WORLD_MODEL", "A4_ADVANCED", "A4_NO_MEMORY", "A4_NO_ONLINE_LEARNING"}]
    prediction_real = all(isinstance(record["metrics"].get("prediction_error_spike"), float) and not math.isnan(record["metrics"]["prediction_error_spike"]) for record in predictors)
    transfer_frozen = all(record["transfer_parameters_unchanged"] and record["transfer_adaptive_state_unchanged"] for record in records)
    prelearned = any(record["metrics"]["pre_change_status"] == "VALID" and record["metrics"]["pre_change_competence"] >= AdaptationThresholds().pre_change_competence for record in records)
    random_values = [record["metrics"].get("pre_change_competence") for record in records if record["variant_id"] == "A0_RANDOM"]
    random_calibrated = all(not isinstance(value, float) or math.isnan(value) or value < AdaptationThresholds().pre_change_competence for value in random_values)
    gates = {
        "P1_numerical_integrity": p1, "P2_paired_worlds": paired,
        "P3_sufficient_signal": world_signal and interactions,
        "P3_world_opportunity_contract": world_signal,
        "P3_agent_interaction_sufficient": interactions,
        "P4_random_baseline_calibrated": random_calibrated,
        "P5_prechange_learning": prelearned, "P7_prediction_error_real": prediction_real,
        "P8_transfer_frozen": transfer_frozen,
    }
    return {
        "status": "PASS" if all(gates.values()) else "FAIL", "expected_runs": expected,
        "completed_runs": len(records), "technical_valid_runs": sum(item.technical_valid.passed for item in validities),
        "experimental_valid_runs": sum(item.experimentally_interpretable.passed for item in validities), "gates": gates,
    }


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
