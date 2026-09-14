"""Fail-closed exact causal forks for the explicitly qualified A0/D0 runtime.

This is deliberately a small execution-plane primitive.  It uses Terrario's
world, physics, rules, scheduler and agent implementations; it is not a second
simulator and it never writes to EvidenceGraph.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

from terrario.core.contracts import Transition
from terrario.core.rng import RNGManager
from terrario.experiment.config import ExperimentConfig
from terrario.experiment.controller import ExperimentController, build_world_state, materialize_scenario
from terrario.lab.execution.runtime import ScientificTrialIdentity
from terrario.lab.persistence.canonical import canonical_json, content_hash
from terrario.world.physics import Physics
from terrario.world.rules import RuleEngine
from terrario.world.scheduler import ChangeScheduler
from terrario.world.state import WorldStateManager

SNAPSHOT_SCHEMA = "terrario.causal-fork-snapshot/v1"
FORK_SCHEMA = "terrario.causal-fork-identity/v1"
INTERVENTION_SCHEMA = "terrario.intervention-spec/v1"


class ForkError(RuntimeError):
    pass


class Forkability(str, Enum):
    EXACT_FORKABLE = "EXACT_FORKABLE"
    RESTORABLE_BUT_NOT_EXACT = "RESTORABLE_BUT_NOT_EXACT"
    NOT_FORKABLE = "NOT_FORKABLE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ForkabilityCapability:
    classification: Forkability; exact_restore: bool; deterministic_continuation: bool
    unsupported_reasons: tuple[str, ...]; component_capabilities: Mapping[str, str]
    schema_version: str = "terrario.forkability-capability/v1"


@dataclass(frozen=True)
class InterventionSpec:
    intervention_id: str; intervention_family: str; target: str; operator: str
    parameters: Mapping[str, Any]; activation_boundary: str = "POST_STATE_PRE_DECISION"
    duration: str = "INSTANT"; scope: str = "BRANCH"; expected_capabilities: tuple[str, ...] = ()
    randomness_policy: str = "NONE"; resource_effect: str = "NONE"; scientific_rationale_ref: str | None = None
    schema_version: str = INTERVENTION_SCHEMA
    @property
    def spec_hash(self) -> str: return content_hash(asdict(self))

    def validate(self) -> None:
        if self.activation_boundary != "POST_STATE_PRE_DECISION": raise ForkError("INTERVENTION_INVALID: boundary")
        if self.randomness_policy not in {"NONE", "DEDICATED_STREAM"}: raise ForkError("INTERVENTION_INVALID: randomness policy")
        if not all(isinstance(item, str) and item for item in (self.intervention_id, self.intervention_family, self.target, self.operator)):
            raise ForkError("INTERVENTION_INVALID: required identity")


@dataclass(frozen=True)
class CausalForkIdentity:
    fork_id: str; parent_snapshot_id: str; parent_execution_id: str; parent_trial_intent_id: str
    parent_attempt_id: str; fork_tick: int; control_branch_id: str; intervention_branch_id: str
    intervention_spec_hash: str; shared_history_hash: str; schema_version: str = FORK_SCHEMA
    @property
    def identity_hash(self) -> str: return content_hash(asdict(self))


@dataclass(frozen=True)
class CausalForkSnapshot:
    snapshot_id: str; execution_id: str; trial_intent_id: str; attempt_id: str; plan_hash: str
    preregistration_root: str; tick: int; world_identity: str; agent_identity: str
    world_seed: int; agent_seed: int; software_identity: str; payload: Mapping[str, Any]
    payload_hash: str; schema_version: str = SNAPSHOT_SCHEMA
    @property
    def snapshot_hash(self) -> str:
        return content_hash({key: value for key, value in asdict(self).items() if key != "payload_hash"})


class InterventionRegistry:
    """Explicit registry; no dynamic discovery and no ambient runtime access."""
    def __init__(self) -> None: self._handlers: dict[str, Any] = {}
    def register(self, intervention_id: str, handler: Any) -> None:
        if intervention_id in self._handlers: raise ForkError("INTERVENTION_INVALID: duplicate registry id")
        self._handlers[intervention_id] = handler
    def apply(self, runtime: "CausalRuntime", spec: InterventionSpec) -> Mapping[str, Any]:
        spec.validate(); handler = self._handlers.get(spec.intervention_id)
        if handler is None: raise ForkError("INTERVENTION_UNSUPPORTED")
        return handler(runtime, spec)


class CausalRuntime:
    """Stepwise real Terrario runtime with a deliberately narrow qualification."""
    def __init__(self, identity: ScientificTrialIdentity, scenario_path: Path, scenario: Mapping[str, Any]) -> None:
        self.identity, self.scenario_path, self.scenario = identity, scenario_path, dict(scenario)
        config = ExperimentConfig(identity.execution_id, None, str(scenario_path), [identity.agent_identity], {}, [identity.world_seed], 1,
                                  int(self.scenario.get("duration", 100)), "scientific_standard", 0, ".", "cpu")
        self.controller = ExperimentController(config)
        self.world = WorldStateManager(build_world_state(self.scenario), self.scenario.get("duration", 100), self.scenario.get("max_energy", 100.0), self.scenario.get("step_energy_cost", 0.0), self.scenario.get("expose_time_fraction", True))
        self.rules = RuleEngine(); self.rules.load_rules(self.scenario.get("rules", {})); self.world.set_rules_version(self.rules.version)
        self.scheduler = ChangeScheduler(self.scenario.get("changes", []), self.rules)
        RNGManager.set_global_determinism(identity.agent_seed)
        self.agent = self.controller._create_agent(identity.agent_identity, identity.agent_seed, self.scenario)
        self.physics, self.tick, self.terminal, self.trace = Physics(), 0, False, []

    @classmethod
    def create(cls, root: Path, identity: ScientificTrialIdentity, scenario_path: Path) -> "CausalRuntime":
        scenario = materialize_scenario(ExperimentController(ExperimentConfig(identity.execution_id, None, str(scenario_path), [identity.agent_identity], {}, [identity.world_seed], 1, 100, "scientific_standard", 0, str(root), "cpu")).scenario, identity.world_seed)
        scenario["world_seed"] = identity.world_seed
        return cls(identity, scenario_path, scenario)

    @property
    def capability(self) -> ForkabilityCapability:
        reasons: list[str] = []
        if self.identity.agent_identity != "A0_RANDOM": reasons.append("AGENT_CAUSAL_STATE_CONTRACT_NOT_QUALIFIED")
        if self.scenario_path.name != "d0_differences.yaml": reasons.append("WORLD_CAUSAL_STATE_CONTRACT_NOT_QUALIFIED")
        if self.scenario.get("opportunity_lifecycle"): reasons.append("OPPORTUNITY_LIFECYCLE_NOT_QUALIFIED")
        exact = not reasons
        return ForkabilityCapability(Forkability.EXACT_FORKABLE if exact else Forkability.NOT_FORKABLE, exact, exact, tuple(reasons),
                                     {"world": "EXACT" if exact else "UNQUALIFIED", "scheduler": "EXACT", "rules": "EXACT", "agent": "EXACT" if exact else "UNQUALIFIED", "rng": "EXACT" if exact else "UNQUALIFIED"})

    def step(self) -> Mapping[str, Any]:
        if self.terminal: raise ForkError("BRANCH_EXECUTION_FAILED: terminal")
        truth = self.world._mutable_state(); agent_state = truth.agents.get(0)
        if agent_state is None or not agent_state.alive: self.terminal = True; return {"terminal": True}
        observation = self.world.get_observation(0, self.scenario.get("view_radius", 2), self.scenario.get("num_channels", 4))
        self.agent.perceive(observation); action = self.agent.decide(); changes = self.scheduler.check(self.world, self.tick)
        consequences = self.physics.step(self.world, {0: action}, RNGManager(self.identity.agent_seed + self.tick))
        target = self.controller._find_target(self.world, 0, action); effects = self.rules.evaluate(self.world, 0, action, target)
        energy = self.rules.apply_effects(self.world, 0, target.object_id, effects) if target else 0.0
        energy += self.world.apply_step_energy_cost(0); consequence = consequences.get(0); consequence.energy_delta = energy
        observation_t1 = self.world.get_observation(0, self.scenario.get("view_radius", 2), self.scenario.get("num_channels", 4))
        terminated = not self.world._mutable_state().agents[0].alive; truncated = self.tick + 1 >= int(self.scenario.get("duration", 100))
        consequence.new_observation, consequence.done = observation_t1, terminated or truncated
        self.agent.learn(Transition(observation, str(self.agent.get_internal_state()), action, consequence, observation_t1, terminated, truncated, self.tick, self.identity.agent_seed))
        events = self.agent.get_trace_events(); record = {"tick": self.tick, "action": action.to_int(), "world_hash": self.world._mutable_state().state_hash(), "energy": self.world._mutable_state().agents[0].energy, "rule_changes": [{"old": x.old_version, "new": x.new_version} for x in changes], "agent_events": events, "terminal": consequence.done}
        self.trace.append(record); self.tick += 1; self.terminal = consequence.done
        return record

    def run_terminal(self) -> tuple[Mapping[str, Any], ...]:
        while not self.terminal: self.step()
        return tuple(self.trace)

    def causal_state(self) -> Mapping[str, Any]:
        cap = self.capability
        if cap.classification is not Forkability.EXACT_FORKABLE: raise ForkError("FORK_NOT_SUPPORTED: " + ",".join(cap.unsupported_reasons))
        state = {"schema_version": "terrario.causal-runtime-state/v1", "scenario": self.scenario, "scenario_hash": content_hash(self.scenario), "tick": self.tick, "terminal": self.terminal, "world": self.world.serialize(), "rules": self.rules.export_causal_state(), "scheduler": self.scheduler.export_causal_state(), "agent": self.agent.export_causal_state(), "history": self.trace}
        # The snapshot boundary must never retain an alias into a live branch.
        return json.loads(canonical_json(state))

    @classmethod
    def restore(cls, root: Path, identity: ScientificTrialIdentity, scenario_path: Path, state: Mapping[str, Any]) -> "CausalRuntime":
        required = {"scenario", "scenario_hash", "tick", "terminal", "world", "rules", "scheduler", "agent", "history"}
        if state.get("schema_version") != "terrario.causal-runtime-state/v1" or not required <= set(state): raise ForkError("SNAPSHOT_INCOMPLETE")
        if content_hash(state["scenario"]) != state["scenario_hash"]: raise ForkError("SNAPSHOT_CORRUPT: scenario")
        runtime = cls(identity, scenario_path, state["scenario"]); runtime.world.restore(state["world"]); runtime.rules.restore_causal_state(state["rules"]); runtime.scheduler.restore_causal_state(state["scheduler"]); runtime.agent.restore_causal_state(state["agent"])
        runtime.tick, runtime.terminal, runtime.trace = int(state["tick"]), bool(state["terminal"]), list(state["history"])
        return runtime


def canonical_trace_hash(trace: Any) -> str: return content_hash(trace)

def first_divergence(control: tuple[Mapping[str, Any], ...], intervention: tuple[Mapping[str, Any], ...]) -> Mapping[str, Any] | None:
    for index, (left, right) in enumerate(zip(control, intervention, strict=False)):
        if content_hash(left) != content_hash(right):
            for key in sorted(set(left) | set(right)):
                if left.get(key) != right.get(key): return {"tick": left.get("tick", index), "phase": "POST_STATE", "event_type": key, "control": left.get(key), "intervention": right.get(key)}
    if len(control) != len(intervention): return {"tick": min(len(control), len(intervention)), "phase": "POST_STATE", "event_type": "TRACE_LENGTH", "control": len(control), "intervention": len(intervention)}
    return None


def _control(runtime: CausalRuntime, spec: InterventionSpec) -> Mapping[str, Any]:
    before = content_hash(runtime.causal_state()); return {"status": "CONTROL", "before_hash": before, "after_hash": before}
def _sham(runtime: CausalRuntime, spec: InterventionSpec) -> Mapping[str, Any]:
    before = content_hash(runtime.causal_state()); return {"status": "SHAM", "before_hash": before, "after_hash": before}
def _test_energy(runtime: CausalRuntime, spec: InterventionSpec) -> Mapping[str, Any]:
    if spec.target != "WORLD.AGENT_ENERGY" or set(spec.parameters) != {"delta"}: raise ForkError("INTERVENTION_INVALID: target")
    before = content_hash(runtime.causal_state()); agent = runtime.world._mutable_state().agents[0]; runtime.world.set_agent_energy(0, agent.energy + float(spec.parameters["delta"])); return {"status": "APPLIED", "before_hash": before, "after_hash": content_hash(runtime.causal_state())}


class CausalForkService:
    def __init__(self, artifacts, root: Path) -> None:
        self.artifacts, self.root = artifacts, Path(root)
        self.registry = InterventionRegistry(); self.registry.register("C00", _control); self.registry.register("C01_SHAM", _sham); self.registry.register("TEST_ENERGY_DELTA", _test_energy)

    def seal_snapshot(self, runtime: CausalRuntime) -> CausalForkSnapshot:
        state = runtime.causal_state(); payload_hash = content_hash(state); ident = runtime.identity
        snapshot = CausalForkSnapshot("causal-snapshot-" + uuid.uuid4().hex, ident.execution_id, ident.trial_intent_id, ident.attempt_id, ident.plan_hash, ident.preregistration_root_hash, runtime.tick, state["scenario_hash"], ident.agent_identity, ident.world_seed, ident.agent_seed, ident.software_identity, state, payload_hash)
        payload = canonical_json(asdict(snapshot)).encode(); blob = self.artifacts.register_blob(payload, "application/vnd.terrario.causal-snapshot+json")
        with self.artifacts.transaction() as con: con.execute("INSERT INTO causal_snapshots(snapshot_id,execution_id,trial_intent_id,attempt_id,snapshot_hash,blob_hash,schema_version,created_at) VALUES(?,?,?,?,?,?,?,?)", (snapshot.snapshot_id, snapshot.execution_id, snapshot.trial_intent_id, snapshot.attempt_id, snapshot.snapshot_hash, blob.blob_hash, snapshot.schema_version, self.artifacts.now()))
        return snapshot

    def restore(self, snapshot: CausalForkSnapshot, identity: ScientificTrialIdentity, scenario_path: Path) -> CausalRuntime:
        if snapshot.snapshot_hash != content_hash({key: value for key, value in asdict(snapshot).items() if key != "payload_hash"}) or snapshot.payload_hash != content_hash(snapshot.payload): raise ForkError("SNAPSHOT_CORRUPT")
        with self.artifacts._connect() as con:
            row = con.execute("SELECT snapshot_hash,blob_hash FROM causal_snapshots WHERE snapshot_id=?", (snapshot.snapshot_id,)).fetchone()
        if row is None or row["snapshot_hash"] != snapshot.snapshot_hash or not self.artifacts.blobs.verify(row["blob_hash"]):
            raise ForkError("SNAPSHOT_CORRUPT: CAS")
        try:
            sealed = json.loads(self.artifacts.blobs.read(row["blob_hash"]))
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            raise ForkError("SNAPSHOT_CORRUPT: CAS") from exc
        if content_hash(sealed) != content_hash(asdict(snapshot)):
            raise ForkError("SNAPSHOT_CORRUPT: CAS payload")
        if (identity.execution_id, identity.trial_intent_id, identity.attempt_id, identity.plan_hash, identity.preregistration_root_hash) != (snapshot.execution_id, snapshot.trial_intent_id, snapshot.attempt_id, snapshot.plan_hash, snapshot.preregistration_root): raise ForkError("RESTORE_NOT_EXACT: identity binding")
        if identity.software_identity != snapshot.software_identity: raise ForkError("SOFTWARE_INCOMPATIBLE")
        return CausalRuntime.restore(self.root, identity, scenario_path, snapshot.payload)

    def fork(self, snapshot: CausalForkSnapshot, spec: InterventionSpec) -> CausalForkIdentity:
        spec.validate(); shared = content_hash(snapshot.payload["history"]); identity = CausalForkIdentity("causal-fork-" + uuid.uuid4().hex, snapshot.snapshot_id, snapshot.execution_id, snapshot.trial_intent_id, snapshot.attempt_id, snapshot.tick, "branch-control-" + uuid.uuid4().hex, "branch-intervention-" + uuid.uuid4().hex, spec.spec_hash, shared)
        with self.artifacts.transaction() as con:
            con.execute("INSERT INTO causal_forks(fork_id,parent_snapshot_id,parent_execution_id,parent_trial_intent_id,parent_attempt_id,identity_hash,shared_history_hash,intervention_spec_hash,state,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)", (identity.fork_id, identity.parent_snapshot_id, identity.parent_execution_id, identity.parent_trial_intent_id, identity.parent_attempt_id, identity.identity_hash, shared, spec.spec_hash, "SNAPSHOT_SEALED", self.artifacts.now()))
        self._event(identity.fork_id, "FORK_CREATED", {"identity": asdict(identity)})
        return identity

    def execute(self, snapshot: CausalForkSnapshot, identity: ScientificTrialIdentity, scenario_path: Path, spec: InterventionSpec) -> Mapping[str, Any]:
        fork = self.fork(snapshot, spec); control, intervention = self.restore(snapshot, identity, scenario_path), self.restore(snapshot, identity, scenario_path)
        if content_hash(control.causal_state()) != content_hash(intervention.causal_state()): raise ForkError("BRANCH_ALIASING_DETECTED")
        self._event(fork.fork_id, "EQUIVALENCE_VALIDATED", {"shared_history_hash": fork.shared_history_hash})
        control_event = self.registry.apply(control, InterventionSpec("C00", "CONTROL", "NONE", "NOOP", {})); intervention_event = self.registry.apply(intervention, spec)
        self._event(fork.fork_id, "INTERVENTION_APPLIED", {"fork_id": fork.fork_id, "branch_id": fork.intervention_branch_id, "intervention_id": spec.intervention_id, "spec_hash": spec.spec_hash, "tick": fork.fork_tick, "boundary": spec.activation_boundary, "target": spec.target, **intervention_event})
        left, right = control.run_terminal(), intervention.run_terminal(); left_hash, right_hash = canonical_trace_hash(left), canonical_trace_hash(right)
        for branch, role, trace, digest in ((fork.control_branch_id, "CONTROL", left, left_hash), (fork.intervention_branch_id, "INTERVENTION", right, right_hash)):
            blob = self.artifacts.register_blob(canonical_json({"fork_id": fork.fork_id, "branch_id": branch, "role": role, "shared_history_hash": fork.shared_history_hash, "trace": trace}).encode(), "application/vnd.terrario.causal-branch-trace+json")
            with self.artifacts.transaction() as con: con.execute("INSERT INTO causal_branch_bindings(branch_id,fork_id,role,artifact_blob_hash,trace_hash) VALUES(?,?,?,?,?)", (branch, fork.fork_id, role, blob.blob_hash, digest))
        diff = first_divergence(left, right); verified = (spec.intervention_id in {"C00", "C01_SHAM"} and diff is None) or (spec.intervention_id == "TEST_ENERGY_DELTA" and diff is not None)
        self._event(fork.fork_id, "VERIFIED" if verified else "VERIFICATION_FAILED", {"control_trace_hash": left_hash, "intervention_trace_hash": right_hash, "first_divergence": diff, "control_event": control_event, "shared_history_hash": fork.shared_history_hash})
        return {"fork": asdict(fork), "control_trace_hash": left_hash, "intervention_trace_hash": right_hash, "first_divergence": diff, "verified": verified}

    def _event(self, fork_id: str, event_type: str, payload: Mapping[str, Any]) -> None:
        with self.artifacts.transaction() as con:
            sequence = int(con.execute("SELECT COALESCE(MAX(sequence),0)+1 FROM causal_fork_events WHERE fork_id=?", (fork_id,)).fetchone()[0]); record = {"fork_id": fork_id, "sequence": sequence, "event_type": event_type, "payload": payload}
            con.execute("INSERT INTO causal_fork_events(event_id,fork_id,sequence,event_type,payload_json,event_hash,created_at) VALUES(?,?,?,?,?,?,?)", ("causal-fork-event-" + uuid.uuid4().hex, fork_id, sequence, event_type, canonical_json(payload), content_hash(record), self.artifacts.now()))
