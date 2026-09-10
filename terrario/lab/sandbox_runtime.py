"""Bounded CPU engineering sandbox with a hard scientific-evidence firewall."""
from __future__ import annotations
import json,os,subprocess,tempfile,uuid
from dataclasses import dataclass,field,replace
from enum import StrEnum
from pathlib import Path
from types import MappingProxyType
from typing import Any,Mapping
from terrario.agent.agents import create_agent
from terrario.agent.scientific import scientific_state
from terrario.core.contracts import Transition
from terrario.core.rng import RNGManager
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
class RunState(StrEnum): CREATED="CREATED"; VALIDATED="VALIDATED"; READY="READY"; RUNNING="RUNNING"; PAUSED="PAUSED"; COMPLETED="COMPLETED"; TERMINATED="TERMINATED"; FAILED="FAILED"; INVALIDATED="INVALIDATED"
_TRANS={RunState.CREATED:{RunState.VALIDATED,RunState.INVALIDATED},RunState.VALIDATED:{RunState.READY,RunState.INVALIDATED},RunState.READY:{RunState.RUNNING,RunState.TERMINATED},RunState.RUNNING:{RunState.PAUSED,RunState.COMPLETED,RunState.TERMINATED,RunState.FAILED},RunState.PAUSED:{RunState.RUNNING,RunState.TERMINATED},RunState.COMPLETED:set(),RunState.TERMINATED:set(),RunState.FAILED:set(),RunState.INVALIDATED:set()}

class SandboxBoundaryError(ValueError): code="PROTOCOL_BOUNDARY_ERROR"
class SandboxValidationError(ValueError): code="CONFIG_ERROR"

@dataclass(frozen=True)
class SandboxExecutionSpec:
    scenario_id:str; scenario_hash:str; world_definition_hash:str; world_seed:int; world_instance_hash:str
    difficulty_fingerprint:str; agent_reference:str; agent_seed:int; observer_mode:str; step_limit:int
    trace_level:str; device:str; classification:ExecutionClassification; config_hash:str; provenance:Mapping[str,Any]
    def __post_init__(self):
        if self.classification!=ExecutionClassification.ENGINEERING_SANDBOX: raise SandboxBoundaryError("sandbox accepts ENGINEERING_SANDBOX only")
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
        s=dict(run.instance.structure); manager=WorldStateManager(build_world_state(s),s.get("duration",run.spec.step_limit),s.get("max_energy",100),s.get("step_energy_cost",0),s.get("expose_time_fraction",True)); rules=RuleEngine();rules.load_rules(s.get("rules",{}));manager.set_rules_version(rules.version)
        agent=create_agent(run.spec.agent_reference,{"num_channels":s.get("num_channels",4),"view_size":2*s.get("view_radius",2)+1},run.spec.agent_seed,device="cpu")
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
        self.storage.write(run); return trace
    def _step_runtime(self,run,r):
        step=len(run.timeline); s=r["scenario"]; world=r["world"]; agent=r["agent"]
        obs=world.get_observation(0,s.get("view_radius",2),s.get("num_channels",4)); agent.perceive(obs); action=agent.decide()
        changes=r["scheduler"].check(world,step); target=_find_target(world,action); physical=r["physics"].step(world,{0:action},RNGManager(run.spec.world_seed+step)); effects=r["rules"].evaluate(world,0,action,target); delta=r["rules"].apply_effects(world,0,target.object_id,effects) if target else 0.0; delta+=world.apply_step_energy_cost(0)
        consequence=physical.get(0,Consequence(delta,[]));consequence.energy_delta=delta; next_obs=world.get_observation(0,s.get("view_radius",2),s.get("num_channels",4));terminated=not world._mutable_state().agents[0].alive; consequence.new_observation=next_obs;consequence.done=terminated or step+1>=run.spec.step_limit
        transition=Transition(obs,str(agent.get_internal_state()),action,consequence,next_obs,terminated,step+1>=run.spec.step_limit,step,run.spec.agent_seed);agent.learn(transition)
        agent_obs={"channels":obs.channels.tolist(),"mask":obs.mask.tolist(),"agent_energy":obs.agent_energy,"time_fraction":obs.time_fraction}
        world_events=tuple(consequence.observer_events)+tuple(f"rule_change:{x.old_version}->{x.new_version}" for x in changes)
        return SandboxTraceStep(run.run_id,"ENGINEERING_SANDBOX",run.spec.config_hash,run.spec.world_definition_hash,run.spec.world_instance_hash,run.spec.world_seed,run.spec.agent_seed,dict(agent.agent_identity),step,agent_obs,{"action_type":action.action_type.name,"direction":action.direction.name,"target_id":action.target_id},tuple(consequence.events),world.serialize(),world_events,scientific_state(agent),terminated)
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
        run.transition(RunState.TERMINATED);run.termination_reason="USER_STOP";self.storage.write(run);return run
    def restart(self,run_id):
        old=self.get(run_id); compiled=self._runtime[run_id]["compiled"] if "compiled" in self._runtime[run_id] else None
        if compiled is None: raise SandboxValidationError("compiled provenance unavailable")
        return self.create(replace(old.spec,provenance={**old.spec.provenance,"restart_of":run_id}),self._runtime[run_id]["config"],compiled)
    def get(self,run_id):
        if run_id not in self._runs: raise KeyError(run_id)
        return self._runs[run_id]

def make_spec(config:LabConfiguration,compiled:CompiledWorld,world_seed:int,agent_seed:int,step_limit:int=100,classification=ExecutionClassification.ENGINEERING_SANDBOX):
    if config.state!=ConfigurationState.SANDBOX: raise SandboxValidationError("derive an explicit SANDBOX configuration before execution")
    instance=generate_instance(compiled,world_seed)
    return SandboxExecutionSpec(config.scenario.scenario_id,config.scenario.content_hash,compiled.definition.content_hash,world_seed,instance.instance_hash,config.difficulty.fingerprint,config.agent_reference,agent_seed,str(config.observer_configuration.get("mode","scientific_standard")),step_limit,"STANDARD","cpu",classification,config.content_hash,{"config_id":config.config_id,"parent_id":config.provenance.parent_id,"scientific_evidence":False})

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
def _find_target(world,action):
    if action.action_type!=ActionType.CONSUME:return None
    truth=world._mutable_state();agent=truth.agents[0]
    if action.target_id>=0:
        t=truth.objects.get(action.target_id);return t if t and abs(t.pos.x-agent.pos.x)+abs(t.pos.y-agent.pos.y)==1 else None
    pos=agent.pos+DIRECTION_DELTA[action.direction];return next((x for x in truth.objects.values() if x.pos==pos),None)
