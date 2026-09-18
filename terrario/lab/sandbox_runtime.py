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
    ExecutionStatus,SelectorType,TARGET_BEARING_OPERATIONS,TargetStatus,
    perceive_targets,resolve)
from terrario.core.types import ActionType,Consequence,DIRECTION_DELTA
from terrario.experiment.controller import build_world_state
from terrario.lab.world_authoring import CompiledWorld,GeneratedWorldInstance,generate_instance
from terrario.lab.world_contracts import ConfigurationState,LabConfiguration,scientific_hash
from terrario.world.physics import Physics
from terrario.world.rules import RuleEngine
from terrario.world.scheduler import ChangeScheduler
from terrario.world.state import WorldStateManager
from terrario.world.transition import (
    WorldPhysicsNotDeclared, build_episode_components, find_target, run_step)

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
        try:
            # El ciclo de oportunidades pasa a ejecutarse. El banco corría D4S y
            # D4T sin respawn ni despawn aunque el escenario los declara con
            # cooldown 3-8: 32 objetos al inicio, 29 a los 250 pasos, cero
            # reapariciones. Era un mundo estrictamente agotable que nadie
            # diseñó. `enabled = bool(config)`, así que en los mundos que no lo
            # declaran -- D0 a D3 -- esto es inerte, y hay un test de paridad que
            # lo fija en vez de confiarlo.
            components=build_episode_components(
                s,duration_fallback=s.get("duration",0),strict_physics=True,
                with_lifecycle=True,world_seed=run.spec.world_seed)
        except WorldPhysicsNotDeclared as exc:
            raise SandboxValidationError(str(exc)) from exc
        manager=components.world; rules=components.rules
        # The world fixes the sensory shape; the spec fixes which concepts exist.
        #
        # Seeded before construction, not only inside it. `create_agent` seeds a
        # per-agent torch.Generator, but module weights come from the GLOBAL
        # torch RNG -- `memory.py:156` calls torch.randn with no generator, and
        # so does every nn.Linear. So two runs of the same spec in one process
        # produced different organisms, and `initial_parameters_hash` was not
        # reproducible across processes. The benches were compensating by hand
        # with torch.manual_seed before each create; the scientific path has
        # called set_global_determinism since the beginning, and this is the
        # asymmetry that made "same seed" mean different things on each surface.
        RNGManager.set_global_determinism(run.spec.agent_seed)
        agent=create_agent(run.spec.agent_reference,{"num_channels":s.get("num_channels",4),"view_size":2*s.get("view_radius",2)+1,**dict(run.spec.agent_configuration)},run.spec.agent_seed,device="cpu")
        # `physics` stays the same object the components carry: a test replaces it
        # here to prove a failing step is classified, and a second instance would
        # make that injection land on a copy nobody runs.
        return {"scenario":s,"world":manager,"rules":rules,"scheduler":components.scheduler,"physics":components.physics,"agent":agent,"components":components}
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
        # La secuencia del paso ya no vive aquí: la ejecuta `run_step`, la misma
        # que ejecuta la ruta científica. Lo que queda en este método es
        # instrumentación del banco — su esquema de traza y sus hashes — que es
        # exactamente lo que sí puede diferir entre superficies.
        step=len(run.timeline); world=r["world"]; agent=r["agent"]
        outcome=run_step(r["components"],agent,step,
                         world_seed=run.spec.world_seed,agent_seed=run.spec.agent_seed,
                         max_steps=run.spec.step_limit)
        obs=outcome.observation_t; action=outcome.action; provenance=outcome.provenance
        consequence=outcome.consequence; terminated=outcome.terminated
        agent_obs={"channels":obs.channels.tolist(),"mask":obs.mask.tolist(),"agent_energy":obs.agent_energy,"time_fraction":obs.time_fraction}
        world_events=tuple(consequence.observer_events)+tuple(f"rule_change:{x.old_version}->{x.new_version}" for x in outcome.change_events)
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
def _find_target(world,action):
    """Delegates to the shared semantics; agent 0 is the sandbox's only agent."""
    return find_target(world,0,action)
