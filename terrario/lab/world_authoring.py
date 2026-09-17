"""World drafts, deterministic generation, pure previews, and structural seed analysis."""
from __future__ import annotations
import hashlib,json
from copy import deepcopy
from dataclasses import dataclass,field,replace
from pathlib import Path
from types import MappingProxyType
from typing import Any,Mapping
import yaml
from terrario.experiment.controller import build_world_state,materialize_scenario
from terrario.lab.models import thaw
from terrario.lab.world_contracts import SCHEMA_VERSION,WorldDefinition,WorldInstance,WorldProvenance,scientific_hash
from terrario.lab.world_registry import adapt_legacy_scenario
from terrario.world.state import WorldStateManager

GENERATOR_VERSION="terrario-world-generator/1"
MAX_DIMENSION=128; MAX_OBJECTS=4096; MAX_SEED_POPULATION=256

@dataclass(frozen=True)
class DraftFinding:
    category:str; code:str; path:str; message:str; blocking:bool

@dataclass(frozen=True)
class WorldDraft:
    draft_id:str; schema_version:str; purpose:str; topology:str; dimensions:tuple[int,int]
    entities:tuple[Mapping[str,Any],...]; object_distributions:tuple[Mapping[str,Any],...]
    initial_conditions:Mapping[str,Any]; deterministic_rules:tuple[Mapping[str,Any],...]
    stochastic_rules:tuple[Mapping[str,Any],...]; observation_sources:tuple[str,...]
    action_availability:tuple[str,...]; termination_conditions:tuple[str,...]
    intervention_targets:tuple[str,...]; scheduled_events:tuple[Mapping[str,Any],...]; resource_structure:Mapping[str,Any]; seed_semantics:str
    provenance:WorldProvenance
    def __post_init__(self):
        for name in ("initial_conditions","resource_structure"): object.__setattr__(self,name,MappingProxyType(dict(getattr(self,name))))
        object.__setattr__(self,"entities",tuple(MappingProxyType(dict(x)) for x in self.entities))
    def edit(self,reason:str,**changes):
        return replace(self,draft_id=f"{self.draft_id}.next",provenance=WorldProvenance("lab-user",reason,self.provenance.created_at,self.provenance.source,self.draft_id,scientific_hash(self),changes),**changes)

@dataclass(frozen=True)
class CompiledWorld:
    definition:WorldDefinition; runtime_template:Mapping[str,Any]; warnings:tuple[DraftFinding,...]; generator_version:str=GENERATOR_VERSION
    def __post_init__(self): object.__setattr__(self,"runtime_template",MappingProxyType(deepcopy(dict(self.runtime_template))))

@dataclass(frozen=True)
class GeneratedWorldInstance:
    identity:WorldInstance; generator_version:str; structure:Mapping[str,Any]; instance_hash:str; statistics:Mapping[str,Any]; provenance:WorldProvenance
    def __post_init__(self):
        object.__setattr__(self,"structure",MappingProxyType(deepcopy(dict(self.structure))))
        object.__setattr__(self,"statistics",MappingProxyType(dict(self.statistics)))
    def manifest(self): return {"world_definition_hash":self.identity.definition_hash,"world_seed":self.identity.seed,"generator_version":self.generator_version,"schema_version":SCHEMA_VERSION,"instance_hash":self.instance_hash,"structural_statistics":dict(self.statistics),"creation_provenance":thaw(self.provenance)}

@dataclass(frozen=True)
class WorldPreview:
    classification:str; instance_manifest:Mapping[str,Any]; topology:Mapping[str,Any]; world_truth:Mapping[str,Any]; observer_view:Mapping[str,Any]; agent_view:Mapping[str,Any]; rule_schedule:tuple[Mapping[str,Any],...]; intervention_points:tuple[Mapping[str,Any],...]; statistics:Mapping[str,Any]

def draft_from_legacy(identifier:str,path:str|Path)->WorldDraft:
    raw=yaml.safe_load(Path(path).read_text()).get("scenario",{}); prov=WorldProvenance("LEGACY_ADAPTER","editable draft projection","RUNTIME",str(path))
    return WorldDraft(f"draft-{identifier.lower()}",SCHEMA_VERSION,raw.get("description",""),"bounded rectangular grid",tuple(raw["grid_size"]),tuple(raw.get("objects",[])),tuple([raw["procedural_layout"]] if raw.get("procedural_layout") else []),raw.get("agent_start",{}),tuple(raw.get("rules",{}).get("rules",[])),tuple(),("channels","mask","agent_energy","time_fraction"),("MOVE","PUSH","CONSUME","INSPECT","NOOP"),(f"duration:{raw.get('duration',500)}","agent death"),("world rules",),tuple(raw.get("changes",[])),_runtime_economy(raw),"world_seed controls layout/schedule only",prov)

def _runtime_economy(raw:Mapping[str,Any])->dict[str,Any]:
    """Every knob that decides what the world DOES, defaulted exactly once.

    The defaults live here, at the boundary where the YAML is in front of you,
    and nowhere downstream. A runtime that substitutes its own turns a missing
    field into different physics without saying so: the sandbox read
    `step_energy_cost` as 0 for D4S and D4T, so an organism that should have
    been spending energy every step could not die, could not leave the viable
    region, and -- because energy_delta is also its reward -- ran with no
    reinforcement signal at all.
    """
    economy={"max_energy":float(raw.get("max_energy",100)),
             "step_energy_cost":float(raw.get("step_energy_cost",0)),
             "expose_time_fraction":bool(raw.get("expose_time_fraction",True))}
    if raw.get("opportunity_lifecycle"): economy["opportunity_lifecycle"]=dict(raw["opportunity_lifecycle"])
    return economy

def validate_draft(d:WorldDraft)->tuple[DraftFinding,...]:
    out=[]
    if d.schema_version!=SCHEMA_VERSION: out.append(DraftFinding("STRUCTURAL_ERROR","SCHEMA_ERROR","schema_version","unsupported schema",True))
    if len(d.dimensions)!=2 or any(type(x)is not int or x<=0 or x>MAX_DIMENSION for x in d.dimensions): out.append(DraftFinding("STRUCTURAL_ERROR","INVALID_GEOMETRY","dimensions",f"dimensions must be 1..{MAX_DIMENSION}",True))
    capacity=d.dimensions[0]*d.dimensions[1] if len(d.dimensions)==2 else 0
    if len(d.entities)>min(capacity,MAX_OBJECTS): out.append(DraftFinding("WORLD_CONSISTENCY_ERROR","OVERDENSE_WORLD","entities","object count exceeds capacity",True))
    legal={"MOVE","PUSH","CONSUME","INSPECT","NOOP"}; unknown=set(d.action_availability)-legal
    if unknown: out.append(DraftFinding("STRUCTURAL_ERROR","INVALID_ACTION_REFERENCE","action_availability",str(sorted(unknown)),True))
    for i,e in enumerate(d.entities):
        pos=e.get("pos")
        if not isinstance(pos,(list,tuple)) or len(pos)!=2 or not (0<=pos[0]<d.dimensions[0] and 0<=pos[1]<d.dimensions[1]): out.append(DraftFinding("WORLD_CONSISTENCY_ERROR","INVALID_INITIAL_STATE",f"entities.{i}.pos","position outside world",True))
        if len(e.get("channels",[]))>64: out.append(DraftFinding("STRUCTURAL_ERROR","INVALID_CHANNELS",f"entities.{i}.channels","too many channels",True))
    if not d.observation_sources: out.append(DraftFinding("SCIENTIFIC_WARNING","GROUND_TRUTH_INSUFFICIENT","observation_sources","no observation source declared",False))
    if not d.intervention_targets: out.append(DraftFinding("SCIENTIFIC_WARNING","NO_MANIPULATION_CHECK","intervention_targets","no intervention-compatible target",False))
    return tuple(out)

def compile_draft(d:WorldDraft)->CompiledWorld:
    findings=validate_draft(d); blocking=[x for x in findings if x.blocking]
    if blocking: raise ValueError("; ".join(f"{x.code}:{x.path}" for x in blocking))
    # The procedural layout and the economy travel INTO the runtime template.
    # Dropping them here is what emptied the sandbox: D4S and D4T declare their
    # objects through `procedural_layout` rather than as an explicit list, so a
    # template built from `entities` alone produced a bare grid with nothing to
    # eat and no decay. `materialize_scenario` -- the same resolver the
    # scientific path uses, imported above -- then returned early because there
    # was no layout to resolve, and both paths silently disagreed about what
    # the world was.
    layout=dict(d.object_distributions[0]) if d.object_distributions else None
    channels=[len(x.get("channels",[])) for x in d.entities]
    if layout: channels+= [len(t.get("channels",[])) for t in layout.get("class_templates",{}).values()]
    operational={"grid_size":list(d.dimensions),"duration":_duration(d),"view_radius":2,"num_channels":max(channels or [4]),"objects":[dict(x) for x in d.entities],"agent_start":dict(d.initial_conditions),"rules":{"rules":[dict(x) for x in d.deterministic_rules]},"changes":[dict(x) for x in d.scheduled_events],**({"procedural_layout":layout} if layout else {}),**dict(d.resource_structure)}
    stable_id="world-"+scientific_hash(operational)[:16]
    runtime={"name":stable_id,"description":"compiled explicit world","seed":0,**operational}
    definition,_=adapt_legacy_scenario(stable_id,runtime,d.provenance.source or d.draft_id)
    return CompiledWorld(definition,runtime,tuple(x for x in findings if not x.blocking))

def compile_registry_world(identifier:str,path:str|Path)->CompiledWorld: return compile_draft(draft_from_legacy(identifier,path))

def generate_instance(c:CompiledWorld,world_seed:int)->GeneratedWorldInstance:
    if type(world_seed)is not int or not -(2**31)<=world_seed<2**31: raise ValueError("world seed outside signed 32-bit range")
    structure=materialize_scenario(deepcopy(dict(c.runtime_template)),world_seed); identity=WorldInstance(c.definition.content_hash,world_seed)
    digest=scientific_hash({"definition_hash":identity.definition_hash,"seed":world_seed,"generator_version":c.generator_version,"structure":structure})
    stats=structural_statistics(structure)
    prov=WorldProvenance("WORLD_GENERATOR","deterministic instance generation","RUNTIME",c.definition.provenance.source,c.definition.world_id,c.definition.content_hash,{"world_seed":world_seed,"generator_version":c.generator_version})
    return GeneratedWorldInstance(identity,c.generator_version,structure,digest,stats,prov)

def structural_statistics(s:Mapping[str,Any])->dict[str,Any]:
    h,w=s["grid_size"]; objects=s.get("objects",[]); start=s.get("agent_start",{}).get("pos")
    distances=[abs(o["pos"][0]-start[0])+abs(o["pos"][1]-start[1]) for o in objects] if start else []
    return {"object_count":len(objects),"density":len(objects)/(h*w),"reachable_space_estimate":h*w-len({tuple(o["pos"]) for o in objects}),"minimum_object_distance":min(distances) if distances else "NOT_AVAILABLE","resource_distribution":_resource_distribution(objects),"opportunity_statistics":"NOT_AVAILABLE"}

def degeneracy_flags(s:Mapping[str,Any])->tuple[str,...]:
    stats=structural_statistics(s); flags=[]; objects=s.get("objects",[])
    if not objects: flags.extend(("EMPTY_WORLD","NO_INTERACTION_OPPORTUNITY"))
    if stats["density"]>.8: flags.append("OVERDENSE_WORLD")
    if not any(float(o.get("energy_value",0))>0 for o in objects): flags.append("RESOURCE_STARVATION")
    if s.get("agent_start",{}).get("pos") in [o.get("pos") for o in objects]: flags.append("TRIVIAL_INITIAL_STATE")
    if not s.get("rules",{}).get("rules",[]): flags.append("INVALID_CAUSAL_SETUP")
    return tuple(flags)

def preview(c:CompiledWorld,seed:int)->WorldPreview:
    instance=generate_instance(c,seed); s=deepcopy(dict(instance.structure)); manager=WorldStateManager(build_world_state(s),s.get("duration",500),s.get("max_energy",100),s.get("step_energy_cost",0),s.get("expose_time_fraction",True)); obs=manager.get_observation(0,s.get("view_radius",2),s.get("num_channels",4))
    agent={"channels":obs.channels.tolist(),"mask":obs.mask.tolist(),"agent_energy":obs.agent_energy,"time_fraction":obs.time_fraction}
    observer=manager.serialize()
    return WorldPreview("PREVIEW_ONLY",instance.manifest(),{"type":c.definition.topology,"dimensions":c.definition.dimensions},observer,observer,agent,tuple(s.get("changes",[])),tuple({"id":x.intervention_id,"target":x.target} for x in ()),instance.statistics)

class SeedBrowser:
    def __init__(self,c:CompiledWorld): self.compiled=c
    def inspect(self,seed:int):
        i=generate_instance(self.compiled,seed); return {"seed":seed,"instance_hash":i.instance_hash,"statistics":dict(i.statistics),"flags":degeneracy_flags(i.structure),"manifest":i.manifest()}
    def analyze(self,seeds):
        values=tuple(int(x) for x in seeds)
        if not values or len(values)>MAX_SEED_POPULATION: raise ValueError(f"seed population must contain 1..{MAX_SEED_POPULATION} seeds")
        rows=tuple(self.inspect(x) for x in values)
        return {"classification":"WORLD_STRUCTURE_ONLY","agent_executed":False,"seeds":rows,"summary":{"count":len(rows),"object_count_range":[min(x["statistics"]["object_count"] for x in rows),max(x["statistics"]["object_count"] for x in rows)],"density_range":[min(x["statistics"]["density"] for x in rows),max(x["statistics"]["density"] for x in rows)]}}

def _duration(d):
    for x in d.termination_conditions:
        if x.startswith("duration:"): return int(x.split(":",1)[1])
    return 500
def _resource_distribution(objects):
    vals=[float(x.get("energy_value",0)) for x in objects]
    return {"positive":sum(x>0 for x in vals),"negative":sum(x<0 for x in vals),"neutral":sum(x==0 for x in vals)}
