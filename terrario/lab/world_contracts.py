"""Versioned scientific World/Scenario/Configuration contracts for Terrario Lab."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, fields, is_dataclass, replace
from enum import Enum, StrEnum
from types import MappingProxyType
from typing import Any, Mapping

SCHEMA_VERSION = "terrario.lab.world/v1"
AGENT_FIELDS = frozenset({"channels", "mask", "agent_energy", "time_fraction"})
OBSERVER_ONLY_FIELDS = frozenset({"world", "world_truth", "objects", "agents", "occupancy", "rules", "rules_version", "causal_property", "energy_value"})


class ContractError(ValueError):
    code = "SCHEMA_ERROR"
    def __init__(self, message: str): super().__init__(f"{self.code}: {message}")
class ConfigError(ContractError): code = "CONFIG_ERROR"
class WorldError(ContractError): code = "WORLD_ERROR"
class ObservationContractError(ContractError): code = "OBSERVATION_CONTRACT_ERROR"
class LeakageError(ObservationContractError): code = "LEAKAGE_ERROR"
class ProtocolError(ContractError): code = "PROTOCOL_ERROR"
class ProvenanceError(ContractError): code = "PROVENANCE_ERROR"


def _plain(value: Any) -> Any:
    if is_dataclass(value): return {f.name:_plain(getattr(value,f.name)) for f in fields(value)}
    if isinstance(value,Mapping): return {str(k):_plain(v) for k,v in sorted(value.items(),key=lambda x:str(x[0]))}
    if isinstance(value,(tuple,list,set,frozenset)): return [_plain(x) for x in value]
    if isinstance(value,Enum): return value.value
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(_plain(value),sort_keys=True,separators=(",",":"),ensure_ascii=False)


def scientific_hash(value: Any) -> str:
    payload=value.scientific_payload() if hasattr(value,"scientific_payload") else value
    return hashlib.sha256(canonical_json(payload).encode()).hexdigest()


@dataclass(frozen=True)
class WorldProvenance:
    creator: str; reason: str; created_at: str
    source: str | None = None; parent_id: str | None = None; parent_hash: str | None = None
    delta: Mapping[str,Any] = None
    def __post_init__(self): object.__setattr__(self,"delta",MappingProxyType(dict(self.delta or {})))


@dataclass(frozen=True)
class WorldRuleDefinition:
    rule_id: str; condition: Mapping[str,Any]; effect: Mapping[str,Any]
    def __post_init__(self):
        object.__setattr__(self,"condition",MappingProxyType(dict(self.condition)))
        object.__setattr__(self,"effect",MappingProxyType(dict(self.effect)))


@dataclass(frozen=True)
class WorldDefinition:
    world_id: str; schema_version: str; dimensions: tuple[int,int]; topology: str
    entity_families: tuple[str,...]; generative_rules: tuple[WorldRuleDefinition,...]
    state_constraints: Mapping[str,Any]; observation_sources: tuple[str,...]
    allowed_actions: tuple[str,...]; causal_rules: tuple[str,...]; stochastic_rules: tuple[str,...]
    resource_rules: tuple[str,...]; termination_conditions: tuple[str,...]; seed_semantics: str
    provenance: WorldProvenance
    def __post_init__(self):
        if self.schema_version != SCHEMA_VERSION: raise WorldError(f"unsupported schema {self.schema_version}")
        if len(self.dimensions)!=2 or any(type(x) is not int or x<=0 for x in self.dimensions): raise WorldError("dimensions must be two positive integers")
        object.__setattr__(self,"state_constraints",MappingProxyType(dict(self.state_constraints)))
    def scientific_payload(self):
        return {k:v for k,v in _plain(self).items() if k != "provenance"}
    @property
    def content_hash(self): return scientific_hash(self)


@dataclass(frozen=True)
class WorldInstance:
    definition_hash: str; seed: int
    @property
    def world_instance_hash(self): return scientific_hash({"definition_hash":self.definition_hash,"seed":self.seed})


@dataclass(frozen=True)
class ObservationContract:
    channels: tuple[str,...]; primitive_features: tuple[str,...]; visibility: str
    partial_observability: bool; temporal_resolution: int; quantization: str
    noise: float; missingness: float; normalization: str; latency: int
    prohibited_fields: tuple[str,...] = tuple(sorted(OBSERVER_ONLY_FIELDS))
    def __post_init__(self):
        if self.temporal_resolution<=0 or self.latency<0: raise ObservationContractError("invalid temporal values")
        if not 0<=self.noise<=1 or not 0<=self.missingness<=1: raise ObservationContractError("noise/missingness outside [0,1]")
        leaked=set(self.channels)|set(self.primitive_features)
        if leaked & OBSERVER_ONLY_FIELDS: raise LeakageError(f"observer-only fields requested: {sorted(leaked & OBSERVER_ONLY_FIELDS)}")
        if not set(self.prohibited_fields)>=OBSERVER_ONLY_FIELDS: raise LeakageError("observer-only denylist cannot be weakened")
    def validate_projection(self, projection: Mapping[str,Any]):
        forbidden=set(projection)&OBSERVER_ONLY_FIELDS
        unknown=set(projection)-AGENT_FIELDS
        if forbidden or unknown: raise LeakageError(f"invalid agent projection fields: {sorted(forbidden|unknown)}")
        return True


@dataclass(frozen=True)
class ActionDefinition:
    name: str; parameter_domains: Mapping[str,Any]; preconditions: tuple[str,...]
    cost: float; failure_semantics: str
    def __post_init__(self): object.__setattr__(self,"parameter_domains",MappingProxyType(dict(self.parameter_domains)))


@dataclass(frozen=True)
class ActionContract:
    actions: tuple[ActionDefinition,...]; invalid_action_behavior: str
    def __post_init__(self):
        names=[a.name for a in self.actions]
        if not names or len(names)!=len(set(names)): raise ContractError("action names must be present and unique")


@dataclass(frozen=True)
class InterventionPoint:
    intervention_id: str; event_kind: str; target: str; timing_or_trigger: str
    manipulated_variable: str; allowed_values: tuple[Any,...]; manipulation_check: str | None
    provenance: WorldProvenance
    def __post_init__(self):
        if self.event_kind not in {"ENVIRONMENTAL_EVENT","SCIENTIFIC_INTERVENTION"}: raise ProtocolError("invalid event kind")
        if self.event_kind=="SCIENTIFIC_INTERVENTION" and not self.manipulation_check: raise ProtocolError("scientific intervention requires manipulation check")


@dataclass(frozen=True)
class MetricBinding:
    metric_id: str; construct: str; proxy: str; implementation_reference: str | None
    unit: str; direction: str; applicable_scenario: str; required_signals: tuple[str,...]
    aggregation: str; limitations: tuple[str,...]; implementation_status: str
    def __post_init__(self):
        if self.implementation_status not in {"IMPLEMENTED","PARTIAL","PROPOSED","MISSING"}: raise ContractError("invalid metric implementation status")


class DimensionState(StrEnum): VALUE="VALUE"; NOT_APPLICABLE="NOT_APPLICABLE"; UNSPECIFIED="UNSPECIFIED"


@dataclass(frozen=True)
class DifficultyDimension:
    state: DimensionState; value: float|int|None; unit: str; interpretation: str
    def __post_init__(self):
        if self.state==DimensionState.VALUE and self.value is None: raise ContractError("VALUE needs a value")
        if self.state!=DimensionState.VALUE and self.value is not None: raise ContractError("non-VALUE dimension cannot carry a value")


DIFFICULTY_DIMENSIONS=("world_size","object_density","distractor_density","observation_noise","partial_observability","temporal_dependency","memory_horizon","rule_complexity","rule_volatility","action_cost","resource_pressure","planning_depth","transfer_distance","causal_ambiguity")
_UNITS={"world_size":"cells","object_density":"ratio","distractor_density":"ratio","observation_noise":"ratio","partial_observability":"ratio","temporal_dependency":"steps","memory_horizon":"steps","rule_complexity":"rule count","rule_volatility":"changes/episode","action_cost":"energy/action","resource_pressure":"ratio","planning_depth":"steps","transfer_distance":"declared distance","causal_ambiguity":"confound count"}


@dataclass(frozen=True)
class DifficultyProfile:
    dimensions: Mapping[str,DifficultyDimension]
    def __post_init__(self):
        if set(self.dimensions)!=set(DIFFICULTY_DIMENSIONS): raise ContractError("difficulty profile must explicitly contain all dimensions")
        object.__setattr__(self,"dimensions",MappingProxyType(dict(self.dimensions)))
    @property
    def fingerprint(self): return scientific_hash(self)


def difficulty_preset(name: str) -> DifficultyProfile:
    levels={"TRIVIAL":0.0,"EASY":0.2,"MODERATE":0.5,"HARD":0.75,"STRESS":1.0}
    if name not in levels: raise ConfigError(f"unknown preset {name}")
    x=levels[name]; dims={k:DifficultyDimension(DimensionState.VALUE,round(x,3),_UNITS[k],f"expanded {name} template value; world adapter must interpret") for k in DIFFICULTY_DIMENSIONS}
    return DifficultyProfile(dims)


@dataclass(frozen=True)
class ScenarioDefinition:
    scenario_id: str; schema_version: str; world_ref: str; scientific_purpose: str
    initial_state_constraints: Mapping[str,Any]; observation_contract: ObservationContract
    action_contract: ActionContract; required_ground_truth: tuple[str,...]
    interventions: tuple[InterventionPoint,...]; metric_bindings: tuple[MetricBinding,...]
    required_capabilities: tuple[str,...]; known_confounders: tuple[str,...]
    implementation_status: str; provenance: WorldProvenance
    def __post_init__(self):
        if self.schema_version!=SCHEMA_VERSION: raise ContractError(f"unsupported schema {self.schema_version}")
        object.__setattr__(self,"initial_state_constraints",MappingProxyType(dict(self.initial_state_constraints)))
    def scientific_payload(self): return {k:v for k,v in _plain(self).items() if k!="provenance"}
    @property
    def content_hash(self): return scientific_hash(self)


@dataclass(frozen=True)
class ScenarioVariant:
    variant_id: str; parent_scenario_hash: str; delta: Mapping[str,Any]; provenance: WorldProvenance
    def __post_init__(self): object.__setattr__(self,"delta",MappingProxyType(dict(self.delta)))
    @property
    def content_hash(self): return scientific_hash({"parent_scenario_hash":self.parent_scenario_hash,"delta":self.delta})


class ConfigurationState(StrEnum): DRAFT="DRAFT"; SANDBOX="SANDBOX"; PREREGISTERED="PREREGISTERED"; LOCKED="LOCKED"; ARCHIVED="ARCHIVED"
_TRANSITIONS={ConfigurationState.DRAFT:{ConfigurationState.SANDBOX,ConfigurationState.PREREGISTERED},ConfigurationState.SANDBOX:{ConfigurationState.DRAFT,ConfigurationState.PREREGISTERED},ConfigurationState.PREREGISTERED:{ConfigurationState.LOCKED,ConfigurationState.ARCHIVED},ConfigurationState.LOCKED:{ConfigurationState.ARCHIVED},ConfigurationState.ARCHIVED:set()}


@dataclass(frozen=True)
class LabConfiguration:
    config_id: str; schema_version: str; state: ConfigurationState; scenario: ScenarioDefinition
    variant: ScenarioVariant|None; difficulty: DifficultyProfile; seeds: tuple[int,...]
    observer_configuration: Mapping[str,Any]; agent_reference: str
    metric_bindings: tuple[MetricBinding,...]; provenance: WorldProvenance
    ui_preferences: Mapping[str,Any]
    def __post_init__(self):
        if self.schema_version!=SCHEMA_VERSION: raise ConfigError(f"unsupported schema {self.schema_version}")
        if not self.seeds or len(self.seeds)!=len(set(self.seeds)): raise ConfigError("seeds must be nonempty and unique")
        object.__setattr__(self,"observer_configuration",MappingProxyType(dict(self.observer_configuration)))
        object.__setattr__(self,"ui_preferences",MappingProxyType(dict(self.ui_preferences)))
    def scientific_payload(self):
        data=_plain(self)
        for field_name in ("config_id","ui_preferences","provenance","state"): data.pop(field_name)
        return data
    @property
    def content_hash(self): return scientific_hash(self)
    @property
    def editable(self): return self.state in {ConfigurationState.DRAFT,ConfigurationState.SANDBOX}
    def edit(self,reason: str,**changes):
        if not self.editable: raise ConfigError(f"{self.state} configuration is immutable")
        forbidden=set(changes)-{"scenario","variant","difficulty","seeds","observer_configuration","agent_reference","metric_bindings","ui_preferences"}
        if forbidden: raise ConfigError(f"unsupported fields: {sorted(forbidden)}")
        before=self.content_hash; candidate=replace(self,**changes)
        delta=config_diff(self,candidate)
        provenance=WorldProvenance("lab-user",reason,self.provenance.created_at,self.provenance.source,self.config_id,before,delta["scientific"])
        return replace(candidate,config_id=f"{self.config_id}.next",provenance=provenance)
    def transition(self,target: ConfigurationState,reason: str):
        if target not in _TRANSITIONS[self.state]: raise ConfigError(f"invalid transition {self.state}->{target}")
        return replace(self,state=target,provenance=WorldProvenance("lab-user",reason,self.provenance.created_at,self.provenance.source,self.config_id,self.content_hash,{"state":{"from":self.state,"to":target}}))


def config_diff(a: LabConfiguration,b: LabConfiguration) -> Mapping[str,Any]:
    groups={"scenario":("scenario",),"difficulty":("difficulty",),"observation":("scenario.observation_contract",),"action":("scenario.action_contract",),"intervention":("scenario.interventions",),"metric":("metric_bindings",)}
    scientific={}
    for group,paths in groups.items():
        for path in paths:
            left,right=_path(a,path),_path(b,path)
            if canonical_json(left)!=canonical_json(right): scientific[path]={"from":_plain(left),"to":_plain(right)}
    for name in ("seeds","observer_configuration","agent_reference","variant"):
        if canonical_json(getattr(a,name))!=canonical_json(getattr(b,name)): scientific[name]={"from":_plain(getattr(a,name)),"to":_plain(getattr(b,name))}
    ui={} if canonical_json(a.ui_preferences)==canonical_json(b.ui_preferences) else {"ui_preferences":{"from":_plain(a.ui_preferences),"to":_plain(b.ui_preferences)}}
    return MappingProxyType({"scientific":MappingProxyType(scientific),"ui":MappingProxyType(ui)})


def _path(value,path):
    for part in path.split("."): value=getattr(value,part)
    return value


@dataclass(frozen=True)
class ValidationFinding:
    category: str; code: str; path: str; message: str; blocking: bool


def validate_configuration(config: LabConfiguration) -> tuple[ValidationFinding,...]:
    findings=[]; world=config.scenario.world_ref
    for name,dim in config.difficulty.dimensions.items():
        if dim.state==DimensionState.VALUE and name in {"object_density","distractor_density","observation_noise","partial_observability","resource_pressure"} and not 0<=float(dim.value)<=1:
            findings.append(ValidationFinding("VALIDATION_ERROR","DOMAIN_ERROR",f"difficulty.{name}","ratio must be within [0,1]",True))
    available=set(config.scenario.observation_contract.channels)|set(config.scenario.observation_contract.primitive_features)
    for metric in config.metric_bindings:
        missing=set(metric.required_signals)-available-set(config.scenario.required_ground_truth)
        if missing: findings.append(ValidationFinding("VALIDATION_ERROR","METRIC_SIGNAL_MISSING",f"metric.{metric.metric_id}",f"missing signals {sorted(missing)}",True))
        if metric.implementation_status!="IMPLEMENTED": findings.append(ValidationFinding("SCIENTIFIC_WARNING","WEAK_PROXY",f"metric.{metric.metric_id}","metric is not fully implemented",False))
    if not world: findings.append(ValidationFinding("VALIDATION_ERROR","WORLD_BINDING_MISSING","scenario.world_ref","world reference required",True))
    if config.state==ConfigurationState.SANDBOX: findings.append(ValidationFinding("SCIENTIFIC_WARNING","SANDBOX_ONLY","state","sandbox results are not scientific evidence",False))
    if config.state not in {ConfigurationState.PREREGISTERED,ConfigurationState.LOCKED,ConfigurationState.ARCHIVED}: findings.append(ValidationFinding("SCIENTIFIC_WARNING","NOT_PREREGISTERED","state","configuration is not preregistered",False))
    return tuple(findings)
