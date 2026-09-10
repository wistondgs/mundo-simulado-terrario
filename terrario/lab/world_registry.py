"""Adapters from legacy D0-D4 YAML into the reusable Lab world grammar."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import yaml
from terrario.core.types import ActionType, Direction
from terrario.lab.models import thaw
from terrario.lab.world_contracts import (SCHEMA_VERSION,ActionContract,ActionDefinition,ConfigurationState,DifficultyDimension,DifficultyProfile,DimensionState,InterventionPoint,LabConfiguration,MetricBinding,ObservationContract,ScenarioDefinition,WorldDefinition,WorldProvenance,WorldRuleDefinition,canonical_json)

@dataclass(frozen=True)
class RegistryEntry:
    world_id: str; status: str; source: str; verified_by: tuple[str,...]
    definition: WorldDefinition|None; scenario: ScenarioDefinition|None

class WorldScenarioRegistry:
    def __init__(self,root: str|Path): self.root=Path(root).resolve(); self._entries=self._load()
    def entries(self): return tuple(self._entries)
    def get(self,identifier: str): return next(e for e in self._entries if e.world_id==identifier)
    def _load(self):
        files={"D0":"d0_differences.yaml","D1":"d1_objects.yaml","D2":"d2_properties.yaml","D3":"d3_causality.yaml","D4":"d4_change.yaml"}; result=[]
        for did,name in files.items():
            path=self.root/"scenarios"/name
            if not path.is_file(): result.append(RegistryEntry(did,"NOT_STARTED",str(path),(),None,None)); continue
            raw=yaml.safe_load(path.read_text()).get("scenario",{})
            definition,scenario=adapt_legacy_scenario(did,raw,str(path))
            result.append(RegistryEntry(did,"IMPLEMENTED",str(path),("legacy YAML parses","world construction/controller tests"),definition,scenario))
        return result

def adapt_legacy_scenario(did: str,raw: dict[str,Any],source: str):
    prov=WorldProvenance("LEGACY_ADAPTER","non-destructive projection","LEGACY_UNKNOWN",source)
    rule_rows=raw.get("rules",{}).get("rules",[])
    rules=tuple(WorldRuleDefinition(str(x.get("id",f"rule-{i}")),x.get("condition",{}),x.get("effect",{})) for i,x in enumerate(rule_rows))
    world=WorldDefinition(f"{did.lower()}-gridworld",SCHEMA_VERSION,tuple(raw["grid_size"]),"bounded rectangular grid",("raw-channel object","single agent"),rules,{"objects":len(raw.get("objects",[])),"agent_start":raw.get("agent_start",{})},("local raw channel window","visibility mask","normalized agent energy","optional time fraction"),tuple(a.name for a in ActionType),tuple(r.rule_id for r in rules),("seeded procedural layout" if raw.get("procedural_layout") else "none",),(f"step energy cost {raw.get('step_energy_cost',0)}",),(f"duration {raw.get('duration',500)}","agent death"),"world seed materializes layout; agent seed is independently offset",prov)
    obs=ObservationContract(tuple(f"channel_{i}" for i in range(raw.get("num_channels",4))),("channels","mask","agent_energy","time_fraction"),f"radius {raw.get('view_radius',2)} local window",True,1,"float32",0.0,0.0,"energy normalized; time optional",0)
    actions=tuple(ActionDefinition(a.name,{"direction":tuple(d.name for d in Direction),"target_id":"integer or -1"},("agent alive",),0.0,"perceptible consequence; no truth disclosure") for a in ActionType)
    action_contract=ActionContract(actions,"reject invalid enum/parameters without world-truth disclosure")
    interventions=tuple(InterventionPoint(f"{did}-change-{i}","ENVIRONMENTAL_EVENT","world rules",f"PRE_STEP at {x.get('at_step')}","rules",("declared replacement",),"observer verifies rules_version and event",prov) for i,x in enumerate(raw.get("changes",[])))
    metric=MetricBinding(f"{did}-energy-trajectory","bounded behavioral performance","energy trajectory","terrario.experiment.metrics.MetricsCalculator","energy","higher",did,("agent_energy",),"trajectory and final value",("energy is not a direct cognitive construct",),"IMPLEMENTED")
    scenario=ScenarioDefinition(did,SCHEMA_VERSION,world.content_hash,raw.get("description","legacy scenario"),{"agent_start":raw.get("agent_start",{}),"object_count":len(raw.get("objects",[]))},obs,action_contract,("objects","rules_version","energy_value"),interventions,(metric,),("gridworld","observer"),(),"IMPLEMENTED",prov)
    return world,scenario

def difficulty_for(entry: RegistryEntry) -> DifficultyProfile:
    world=entry.definition; scenario=entry.scenario; cells=world.dimensions[0]*world.dimensions[1]; objects=int(world.state_constraints.get("objects",0))
    v=lambda state,value,unit,text:DifficultyDimension(state,value,unit,text)
    values={"world_size":v(DimensionState.VALUE,cells,"cells","grid area"),"object_density":v(DimensionState.VALUE,objects/cells,"ratio","objects per cell"),"distractor_density":v(DimensionState.UNSPECIFIED,None,"ratio","requires causal relevance labeling"),"observation_noise":v(DimensionState.VALUE,scenario.observation_contract.noise,"ratio","declared noise"),"partial_observability":v(DimensionState.VALUE,1.0,"bounded local view","local rather than global"),"temporal_dependency":v(DimensionState.VALUE,1,"steps","minimum transition dependency"),"memory_horizon":v(DimensionState.UNSPECIFIED,None,"steps","not defined by legacy scenario"),"rule_complexity":v(DimensionState.VALUE,len(world.generative_rules),"rule count","initial rules"),"rule_volatility":v(DimensionState.VALUE,len(scenario.interventions),"changes/episode","declared schedule"),"action_cost":v(DimensionState.VALUE,0.0,"energy/action","legacy default"),"resource_pressure":v(DimensionState.UNSPECIFIED,None,"ratio","needs normalization"),"planning_depth":v(DimensionState.UNSPECIFIED,None,"steps","not specified"),"transfer_distance":v(DimensionState.NOT_APPLICABLE,None,"declared distance","no transfer phase"),"causal_ambiguity":v(DimensionState.VALUE,1 if entry.world_id=="D3" else 0,"confound count","explicit designed confound only")}
    return DifficultyProfile(values)

def d2_views(entry: RegistryEntry) -> dict[str,Any]:
    if entry.world_id!="D2": raise ValueError("D2 entry required")
    return {"world_view":{"classification":"WORLD_PROPERTY","fields":("position","movable","energy_value","raw channels")},"agent_view":{"classification":"PRIMITIVE_OBSERVATION","fields":entry.scenario.observation_contract.primitive_features,"observer_only_excluded":True},"observer_view":{"classification":"WORLD_PROPERTY","fields":entry.scenario.required_ground_truth},"scientific_view":{"classification":"ANALYST_INTERPRETATION","variables":("movability","channel signature"),"warning":"channel clusters are not learned concepts"}}

def generalization_check(registry: WorldScenarioRegistry) -> dict[str,Any]:
    checks={did:bool(registry.get(did).definition and registry.get(did).scenario) for did in ("D2","D3","D4")}; schemas={registry.get(did).scenario.schema_version for did in checks if checks[did]}
    return {"status":"GENERALIZES" if all(checks.values()) and len(schemas)==1 else "GENERALIZES_WITH_EXTENSION","checks":checks,"schemas":sorted(schemas),"contract_specializations":()}

def configuration_for(entry: RegistryEntry) -> LabConfiguration:
    prov=WorldProvenance("LAB_ADAPTER","editable configuration derived from verified registry","RUNTIME",entry.source,parent_id=entry.scenario.scenario_id,parent_hash=entry.scenario.content_hash,delta={})
    return LabConfiguration(f"config-{entry.world_id.lower()}-draft",SCHEMA_VERSION,ConfigurationState.DRAFT,entry.scenario,None,difficulty_for(entry),(42,),{"mode":"scientific_standard"},"A0_RANDOM",entry.scenario.metric_bindings,prov,{"panel":"difficulty","theme":"system"})

def patched_configuration(config: LabConfiguration,patch: dict[str,Any]) -> LabConfiguration:
    allowed={"difficulty","ui_preferences","seeds","agent_reference","observer_configuration"}
    unknown=set(patch)-allowed
    if unknown: raise ValueError(f"unsupported config patch fields: {sorted(unknown)}")
    changes={}
    if "difficulty" in patch:
        dims=dict(config.difficulty.dimensions)
        for name,value in patch["difficulty"].items():
            if name not in dims: raise ValueError(f"unknown difficulty dimension {name}")
            old=dims[name]
            dims[name]=DifficultyDimension(DimensionState.VALUE,value,old.unit,old.interpretation)
        changes["difficulty"]=DifficultyProfile(dims)
    if "seeds" in patch: changes["seeds"]=tuple(int(x) for x in patch["seeds"])
    if "agent_reference" in patch: changes["agent_reference"]=str(patch["agent_reference"])
    if "observer_configuration" in patch: changes["observer_configuration"]=dict(patch["observer_configuration"])
    if "ui_preferences" in patch: changes["ui_preferences"]=dict(patch["ui_preferences"])
    return config.edit("Config Studio validated patch",**changes)

def configuration_from_payload(payload: dict[str,Any],base: LabConfiguration) -> LabConfiguration:
    """Decode a serialized API configuration without reinterpreting nested scenario semantics."""
    if payload.get("schema_version")!=SCHEMA_VERSION: raise ValueError(f"unsupported schema {payload.get('schema_version')}")
    scenario=payload.get("scenario",{})
    if canonical_json(scenario)!=canonical_json(thaw(base.scenario)):
        raise ValueError("scenario payload does not match registered immutable definition")
    if canonical_json(payload.get("metric_bindings"))!=canonical_json(thaw(base.metric_bindings)) or payload.get("variant") is not None:
        raise ValueError("metric/variant payload does not match registered immutable bindings")
    raw_dims=payload.get("difficulty",{}).get("dimensions",{})
    if set(raw_dims)!=set(base.difficulty.dimensions): raise ValueError("difficulty dimensions are incomplete")
    dims={name:DifficultyDimension(DimensionState(row["state"]),row.get("value"),row["unit"],row["interpretation"]) for name,row in raw_dims.items()}
    return LabConfiguration(str(payload["config_id"]),SCHEMA_VERSION,ConfigurationState(payload["state"]),base.scenario,base.variant,DifficultyProfile(dims),tuple(payload["seeds"]),dict(payload["observer_configuration"]),str(payload["agent_reference"]),base.metric_bindings,base.provenance,dict(payload.get("ui_preferences",{})))
