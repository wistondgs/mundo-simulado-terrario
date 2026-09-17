"""Bounded CPU engineering sandbox with a hard scientific-evidence firewall."""
from __future__ import annotations
import json,os,subprocess,tempfile,uuid
from dataclasses import dataclass,field,replace
from enum import StrEnum
from pathlib import Path
from types import MappingProxyType
from typing import Any,Mapping
from terrario.agent.agents import create_agent
from terrario.lab.agent_composition import validate_selection
from terrario.agent.scientific import scientific_state
from terrario.core.contracts import Transition
from terrario.core.rng import RNGManager
from terrario.core.action_contract import (ActionIntent,ActionProvenance,AddressingMode,
    ExecutionStatus,SelectorType,TargetStatus,perceive_targets,resolve)
from terrario.core.types import ActionType,Consequence,DIRECTION_DELTA
from terrario.experiment.controller import build_world_state
from terrario.lab.world_authoring import CompiledWorld,GeneratedWorldInstance,generate_instance
from terrario.lab.world_contracts import ConfigurationState,LabConfiguration,scientific_hash
from terrario.world.physics import Physics
from terrario.world.rules import RuleEngine
from terrario.world.scheduler import ChangeScheduler
from terrario.world.state import WorldStateManager

TRACE_SCHEMA="terrario.sandbox.trace/v1"; MAX_STEPS=2000
class ExecutionClassification(StrEnum): PREVIEW_ONLY="PREVIEW_ONLY"; ENGINEERING_SANDBOX="ENGINEERING_SANDBOX"; SCIENTIFIC="SCIENTIFIC"
class RunState(StrEnum): CREATED="CREATED"; VALIDATED="VALIDATED"; READY="READY"; RUNNING="RUNNING"; PAUSED="PAUSED"; STOPPING="STOPPING"; COMPLETED="COMPLETED"; TERMINATED="TERMINATED"; FAILED="FAILED"; INVALIDATED="INVALIDATED"
_TRANS={RunState.CREATED:{RunState.VALIDATED,RunState.INVALIDATED},RunState.VALIDATED:{RunState.READY,RunState.INVALIDATED},RunState.READY:{RunState.RUNNING,RunState.STOPPING},RunState.RUNNING:{RunState.PAUSED,RunState.COMPLETED,RunState.STOPPING,RunState.FAILED},RunState.PAUSED:{RunState.RUNNING,RunState.STOPPING},RunState.STOPPING:{RunState.TERMINATED,RunState.FAILED},RunState.COMPLETED:set(),RunState.TERMINATED:set(),RunState.FAILED:set(),RunState.INVALIDATED:set()}

#: Steps between full snapshots of a running sandbox trace.  See `step`.
SNAPSHOT_EVERY=50
_TERMINAL=frozenset({RunState.COMPLETED,RunState.TERMINATED,RunState.FAILED})

class SandboxBoundaryError(ValueError): code="PROTOCOL_BOUNDARY_ERROR"
class SandboxValidationError(ValueError): code="CONFIG_ERROR"

@dataclass(frozen=True)
class SandboxExecutionSpec:
    scenario_id:str; scenario_hash:str; world_definition_hash:str; world_seed:int; world_instance_hash:str
    difficulty_fingerprint:str; agent_reference:str; agent_seed:int; observer_mode:str; step_limit:int
    trace_level:str; device:str; classification:ExecutionClassification; config_hash:str; provenance:Mapping[str,Any]
    #: Which concepts the organism is built from.  Empty means A4's defaults,
    #: so an existing spec keeps the agent it always had.  It is part of the
    #: spec -- and therefore of its hash -- because a different mix is a
    #: different organism, not a different view of one.
    agent_configuration:Mapping[str,Any]=MappingProxyType({})
    def __post_init__(self):
        if self.classification!=ExecutionClassification.ENGINEERING_SANDBOX: raise SandboxBoundaryError("sandbox accepts ENGINEERING_SANDBOX only")
        object.__setattr__(self,"agent_configuration",MappingProxyType(validate_selection(self.agent_configuration)))
        if self.device!="cpu": raise SandboxValidationError("LAB-UI-02B sandbox is CPU-only")
        if not 1<=self.step_limit<=MAX_STEPS: raise SandboxValidationError(f"step_limit must be 1..{MAX_STEPS}")
        object.__setattr__(self,"provenance",MappingProxyType(dict(self.provenance)))

@dataclass(frozen=True)
class SandboxTraceStep:
    sandbox_run_id:str; classification:str; config_hash:str; world_definition_hash:str; world_instance_hash:str
    world_seed:int; agent_seed:int; agent_identity:Mapping[str,Any]; step:int; agent_observation:Mapping[str,Any]
    agent_action:Mapping[str,Any]; agent_events:tuple[str,...]; observer_world:Mapping[str,Any]
    world_events:tuple[str,...]; scientific_state:Mapping[str,Any]; terminated:bool; trace_schema_version:str=TRACE_SCHEMA

@dataclass
class SandboxRun:
    run_id:str; spec:SandboxExecutionSpec; state:RunState; instance:GeneratedWorldInstance
    timeline:list[SandboxTraceStep]=field(default_factory=list); termination_reason:str|None=None; error:Mapping[str,Any]|None=None
    def transition(self,target):
        if target not in _TRANS[self.state]: raise SandboxValidationError(f"invalid transition {self.state}->{target}")
        self.state=target

class EvidenceFirewall:
    def register(self,classification:ExecutionClassification,*_args,**_kwargs):
        if classification!=ExecutionClassification.SCIENTIFIC: raise SandboxBoundaryError("non-scientific artifacts cannot enter EvidenceGraph")
        raise SandboxBoundaryError("sandbox process has no scientific evidence writer")

class SandboxStorage:
    def __init__(self,root:str|Path): self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True)
    def write(self,run:SandboxRun):
        self.root.mkdir(parents=True,exist_ok=True)
        target=self.root/f"{run.run_id}.json"; payload=serialize_run(run); fd,temp=tempfile.mkstemp(prefix=run.run_id,suffix=".tmp",dir=self.root)
        try:
            with os.fdopen(fd,"w") as f: json.dump(payload,f,sort_keys=True); f.flush(); os.fsync(f.fileno())
            os.replace(temp,target)
        finally:
            if os.path.exists(temp): os.unlink(temp)
        return target
    def read(self,run_id): return json.loads((self.root/f"{run_id}.json").read_text())

class SandboxService:
    def __init__(self,storage_root:str|Path): self.storage=SandboxStorage(storage_root); self._runs={}; self._runtime={}
    def validate_spec(self,spec,config,compiled,instance):
        errors=[]
        if config.state!=ConfigurationState.SANDBOX: errors.append("configuration state must be SANDBOX")
        if spec.world_definition_hash!=compiled.definition.content_hash: errors.append("world definition hash mismatch")
        if spec.world_instance_hash!=instance.instance_hash: errors.append("world instance hash mismatch")
        if spec.scenario_hash!=config.scenario.content_hash: errors.append("scenario hash mismatch")
        if spec.difficulty_fingerprint!=config.difficulty.fingerprint: errors.append("difficulty fingerprint mismatch")
        if spec.classification!=ExecutionClassification.ENGINEERING_SANDBOX: errors.append("classification rejected")
        return {"valid":not errors,"errors":tuple(errors),"classification":"ENGINEERING_SANDBOX","scientific_evidence":False}
    def create(self,spec,config,compiled):
        instance=generate_instance(compiled,spec.world_seed); validation=self.validate_spec(spec,config,compiled,instance)
        if not validation["valid"]: raise SandboxValidationError("; ".join(validation["errors"]))
        run=SandboxRun("sandbox-"+uuid.uuid4().hex,spec,RunState.CREATED,instance); run.transition(RunState.VALIDATED); run.transition(RunState.READY)
        self._runs[run.run_id]=run; self._runtime[run.run_id]=self._build_runtime(run); self._runtime[run.run_id].update({"compiled":compiled,"config":config}); self.storage.write(run); return run
    def _build_runtime(self,run):
        s=dict(run.instance.structure)
        # Required, not defaulted: a world whose physics is missing is a world
        # nobody declared, and substituting zero here is how an organism ended
        # up running 1200 steps with no energy cost and no reward. The defaults
        # belong at the YAML boundary (`_runtime_economy`), where a person can
        # see what they are choosing.
        missing=[k for k in ("duration","max_energy","step_energy_cost","expose_time_fraction") if k not in s]
        if missing: raise SandboxValidationError(f"WORLD_PHYSICS_NOT_DECLARED: {sorted(missing)}")
        manager=WorldStateManager(build_world_state(s),s["duration"],s["max_energy"],s["step_energy_cost"],s["expose_time_fraction"]); rules=RuleEngine();rules.load_rules(s.get("rules",{}));manager.set_rules_version(rules.version)
        # The world fixes the sensory shape; the spec fixes which concepts exist.
        agent=create_agent(run.spec.agent_reference,{"num_channels":s.get("num_channels",4),"view_size":2*s.get("view_radius",2)+1,**dict(run.spec.agent_configuration)},run.spec.agent_seed,device="cpu")
        return {"scenario":s,"world":manager,"rules":rules,"scheduler":ChangeScheduler(s.get("changes",[]),rules),"physics":Physics(),"agent":agent}
    def step(self,run_id):
        run=self.get(run_id)
        if run.state==RunState.READY: run.transition(RunState.RUNNING)
        elif run.state==RunState.PAUSED: run.transition(RunState.RUNNING)
        if run.state!=RunState.RUNNING: raise SandboxValidationError(f"cannot step {run.state}")
        try: trace=self._step_runtime(run,self._runtime[run_id]); run.timeline.append(trace)
        except Exception as exc:
            run.error={"category":classify_error(exc),"message":str(exc)}; run.transition(RunState.FAILED); self.storage.write(run); raise
        if trace.terminated or len(run.timeline)>=run.spec.step_limit:
            run.termination_reason="AGENT_TERMINATED" if trace.terminated else "STEP_LIMIT"; run.transition(RunState.COMPLETED)
        else: run.transition(RunState.PAUSED)
        # Snapshotting on a cadence rather than on every step. `write` serializes
        # the WHOLE run, timeline included, plus an fsync and an atomic replace,
        # so writing at step N wrote N steps: the total was quadratic and it
        # dominated everything else. Measured on D4T, cost per step climbed from
        # 0.42 s to 1.19 s over 600 steps, identically with and without the
        # episodic memory and with and without the planner -- because it was
        # never the organism.
        #
        # Nothing is traded away that anyone reads. The file's only consumer is
        # `_discover_lost_sessions`, which asks whether a run existed, whether it
        # completed, and how far it got -- for a session the runtime declares
        # PROCESS_RESTART_RUNTIME_NOT_RESTORABLE either way. A terminal state is
        # always written immediately, so a finished run is never stale; an
        # interrupted one may under-report its step count by less than the
        # cadence, on a trace that could not have been resumed regardless.
        if run.state in _TERMINAL or len(run.timeline)%SNAPSHOT_EVERY==0: self.storage.write(run)
        return trace
    def _step_runtime(self,run,r):
        step=len(run.timeline); s=r["scenario"]; world=r["world"]; agent=r["agent"]
        obs=world.get_observation(0,s.get("view_radius",2),s.get("num_channels",4)); agent.perceive(obs); action=agent.decide()
        action,provenance=_apply_action_contract(world,obs,action,agent,step,run.spec.world_seed)
        changes=r["scheduler"].check(world,step); target=_find_target(world,action); physical=r["physics"].step(world,{0:action},RNGManager(run.spec.world_seed+step)); effects=r["rules"].evaluate(world,0,action,target); delta=r["rules"].apply_effects(world,0,target.object_id,effects) if target else 0.0; delta+=world.apply_step_energy_cost(0)
        consequence=physical.get(0,Consequence(delta,[]));consequence.energy_delta=delta; next_obs=world.get_observation(0,s.get("view_radius",2),s.get("num_channels",4));terminated=not world._mutable_state().agents[0].alive; consequence.new_observation=next_obs;consequence.done=terminated or step+1>=run.spec.step_limit
        transition=Transition(obs,str(agent.get_internal_state()),action,consequence,next_obs,terminated,step+1>=run.spec.step_limit,step,run.spec.agent_seed);agent.learn(transition)
        agent_obs={"channels":obs.channels.tolist(),"mask":obs.mask.tolist(),"agent_energy":obs.agent_energy,"time_fraction":obs.time_fraction}
        world_events=tuple(consequence.observer_events)+tuple(f"rule_change:{x.old_version}->{x.new_version}" for x in changes)
        return SandboxTraceStep(run.run_id,"ENGINEERING_SANDBOX",run.spec.config_hash,run.spec.world_definition_hash,run.spec.world_instance_hash,run.spec.world_seed,run.spec.agent_seed,dict(agent.agent_identity),step,agent_obs,{"action_type":action.action_type.name,"direction":action.direction.name,"target_id":action.target_id,**provenance},tuple(consequence.events),world.serialize(),world_events,scientific_state(agent),terminated)
    def run_bounded(self,run_id,steps=None):
        limit=min(steps or self.get(run_id).spec.step_limit,self.get(run_id).spec.step_limit)
        while self.get(run_id).state not in {RunState.COMPLETED,RunState.TERMINATED,RunState.FAILED} and len(self.get(run_id).timeline)<limit: self.step(run_id)
        return self.get(run_id)
    def pause(self,run_id):
        run=self.get(run_id)
        if run.state==RunState.RUNNING: run.transition(RunState.PAUSED)
        elif run.state!=RunState.PAUSED: raise SandboxValidationError(f"cannot pause {run.state}")
        self.storage.write(run); return run
    def resume(self,run_id):
        run=self.get(run_id)
        if run.state!=RunState.PAUSED: raise SandboxValidationError(f"cannot resume {run.state}")
        run.transition(RunState.RUNNING);self.storage.write(run);return run
    def stop(self,run_id):
        run=self.get(run_id)
        if run.state in {RunState.COMPLETED,RunState.TERMINATED,RunState.FAILED}: raise SandboxValidationError(f"cannot stop {run.state}")
        run.transition(RunState.STOPPING);run.termination_reason="USER_STOP";run.transition(RunState.TERMINATED);self.storage.write(run);return run
    def restart(self,run_id):
        old=self.get(run_id); compiled=self._runtime[run_id]["compiled"] if "compiled" in self._runtime[run_id] else None
        if compiled is None: raise SandboxValidationError("compiled provenance unavailable")
        return self.create(replace(old.spec,provenance={**old.spec.provenance,"restart_of":run_id}),self._runtime[run_id]["config"],compiled)
    def get(self,run_id):
        if run_id not in self._runs: raise KeyError(run_id)
        return self._runs[run_id]
    def active(self):
        """Runs still holding a session slot, so a caller can free them by name."""
        closed={RunState.COMPLETED,RunState.TERMINATED,RunState.FAILED}
        return tuple({"sandbox_run_id":r.run_id,"state":r.state.value,"world_id":r.spec.scenario_id}
                     for r in self._runs.values() if r.state not in closed)

def make_spec(config:LabConfiguration,compiled:CompiledWorld,world_seed:int,agent_seed:int,step_limit:int=100,classification=ExecutionClassification.ENGINEERING_SANDBOX,agent_configuration:Mapping[str,Any]|None=None):
    if config.state!=ConfigurationState.SANDBOX: raise SandboxValidationError("derive an explicit SANDBOX configuration before execution")
    instance=generate_instance(compiled,world_seed)
    return SandboxExecutionSpec(config.scenario.scenario_id,config.scenario.content_hash,compiled.definition.content_hash,world_seed,instance.instance_hash,config.difficulty.fingerprint,config.agent_reference,agent_seed,str(config.observer_configuration.get("mode","scientific_standard")),step_limit,"STANDARD","cpu",classification,config.content_hash,{"config_id":config.config_id,"parent_id":config.provenance.parent_id,"scientific_evidence":False},agent_configuration or {})

def derive_sandbox(config:LabConfiguration,reason="derived engineering sandbox"):
    if config.state in {ConfigurationState.DRAFT}: return config.transition(ConfigurationState.SANDBOX,reason)
    if config.state==ConfigurationState.SANDBOX: return config
    return replace(config,config_id=f"{config.config_id}.sandbox",state=ConfigurationState.SANDBOX,provenance=replace(config.provenance,parent_id=config.config_id,parent_hash=config.content_hash,reason=reason,delta={"state":{"from":config.state.value,"to":"SANDBOX"}}))

def serialize_run(run):
    return {"sandbox_run_id":run.run_id,"classification":"ENGINEERING_SANDBOX","scientific_evidence":False,"state":run.state.value,"spec":_plain(run.spec),"timeline":[_plain(x) for x in run.timeline],"termination_reason":run.termination_reason,"error":run.error,"complete":run.state in {RunState.COMPLETED,RunState.TERMINATED},"trace_schema_version":TRACE_SCHEMA}
def classify_error(exc):
    name=type(exc).__name__.lower()
    if "agent" in name:return "AGENT_ERROR"
    if "device" in name:return "DEVICE_ERROR"
    if "world" in name:return "WORLD_ERROR"
    if "trace" in name:return "TRACE_ERROR"
    if isinstance(exc,SandboxBoundaryError):return "PROTOCOL_BOUNDARY_ERROR"
    if isinstance(exc,(ValueError,KeyError)):return "CONFIG_ERROR"
    return "INTERNAL_ERROR"
def _plain(x):
    from terrario.lab.models import thaw
    return thaw(x)
def _apply_action_contract(world,obs,action,agent,step,world_seed):
    """Resolve the organism's intention against what it could actually perceive.

    Under T0 this is a no-op by construction: the directional contract needs no
    resolution layer, and the returned action is the one the agent emitted, so a
    T0 run is byte-identical to a run before Action Contract v2 existed. That
    matters -- T0 is the control arm, and a control that quietly changed would
    make the comparison meaningless.

    Under T1 the slot the organism named is resolved here, and ONLY a VALID
    resolution writes `target_id`. Everything else leaves it at -1 with the
    direction already pinned to NONE by the agent, so an unresolvable target
    consumes nothing rather than silently becoming a neighbour (AC2-5). The
    physics is untouched: it still reads `target_id`, it simply can no longer be
    handed an entity the organism never perceived (AC2-2), because the only
    writer is a resolution that came out of the agent's own view window.
    """
    mode=getattr(agent,"_addressing_mode",None)
    if mode is None or mode is AddressingMode.T0_DIRECTIONAL: return action,{}
    truth=world._mutable_state()
    view=obs.channels.shape[-1]
    targets,truncated=perceive_targets(truth,0,view,salt=f"{world_seed}",step=step,mask=obs.mask)
    intent=ActionIntent(action.action_type,SelectorType(action.selector_type),action.selector_value)
    res=resolve(intent,targets,truth,0)
    resolved=res.status is TargetStatus.VALID
    action.target_id=res.entity_id if resolved else -1
    prov=ActionProvenance(step=step,addressing_mode=mode.value,
        perceived_targets=[t.handle for t in targets],perceived_truncated=truncated,
        chosen_operation=action.action_type.name,chosen_selector_type=SelectorType(action.selector_type).name,
        intended_selector_value=action.selector_value,
        intended_target=next((t.handle for t in targets if t.slot==action.selector_value),None),
        resolved_target=res.handle if resolved else None,target_status=res.status.value,
        executed_target=res.handle if resolved else None,
        execution_status=(ExecutionStatus.EXECUTED.value if resolved else
            ExecutionStatus.NOT_APPLICABLE.value if res.status is TargetStatus.NOT_ADDRESSED
            else ExecutionStatus.FAILED_TARGET_RESOLUTION.value))
    return action,{"action_contract":prov.as_record()}


def _find_target(world,action):
    if action.action_type!=ActionType.CONSUME:return None
    truth=world._mutable_state();agent=truth.agents[0]
    if action.target_id>=0:
        t=truth.objects.get(action.target_id);return t if t and abs(t.pos.x-agent.pos.x)+abs(t.pos.y-agent.pos.y)==1 else None
    pos=agent.pos+DIRECTION_DELTA[action.direction];return next((x for x in truth.objects.values() if x.pos==pos),None)
