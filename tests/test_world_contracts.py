from dataclasses import replace
import pytest

from terrario.lab.configuration import ConfigurationRepository,ConfigStudioService
from terrario.lab.world_contracts import (ConfigurationState,ConfigError,ContractError,DifficultyDimension,DifficultyProfile,DimensionState,LeakageError,ObservationContract,SCHEMA_VERSION,canonical_json,config_diff,difficulty_preset,scientific_hash,validate_configuration)
from terrario.lab.world_registry import WorldScenarioRegistry,configuration_for,d2_views,generalization_check,patched_configuration

def registry(): return WorldScenarioRegistry(".")
def config(): return configuration_for(registry().get("D2"))

def test_world_truth_cannot_enter_agent_observation():
    with pytest.raises(LeakageError): ObservationContract(("world_truth",),("channels",),"local",True,1,"float32",0,0,"none",0)
    with pytest.raises(LeakageError): config().scenario.observation_contract.validate_projection({"channels":[],"objects":{}})

def test_semantically_identical_difficulty_has_same_fingerprint():
    a=difficulty_preset("EASY"); b=DifficultyProfile(dict(reversed(list(a.dimensions.items()))))
    assert a.fingerprint==b.fingerprint

def test_scientific_dimension_change_changes_fingerprint():
    a=difficulty_preset("EASY"); dims=dict(a.dimensions); old=dims["world_size"]
    dims["world_size"]=replace(old,value=old.value+1); assert a.fingerprint!=DifficultyProfile(dims).fingerprint

def test_ui_only_change_preserves_scientific_hash_and_has_ui_diff():
    a=config(); b=a.edit("layout",ui_preferences={"panel":"world","zoom":2})
    assert a.content_hash==b.content_hash and not config_diff(a,b)["scientific"] and config_diff(a,b)["ui"]

def test_locked_and_preregistered_reject_domain_edits():
    prereg=config().transition(ConfigurationState.PREREGISTERED,"preregister")
    with pytest.raises(ConfigError): prereg.edit("illegal",seeds=(1,))
    locked=prereg.transition(ConfigurationState.LOCKED,"lock")
    with pytest.raises(ConfigError): locked.edit("illegal",agent_reference="A1_REACTIVE")

def test_state_machine_rejects_invalid_transition():
    with pytest.raises(ConfigError): config().transition(ConfigurationState.LOCKED,"skip")
    archived=config().transition(ConfigurationState.PREREGISTERED,"p").transition(ConfigurationState.ARCHIVED,"a")
    with pytest.raises(ConfigError): archived.transition(ConfigurationState.LOCKED,"reverse")

def test_config_diff_detects_exact_scientific_parameter():
    a=config(); b=patched_configuration(a,{"difficulty":{"world_size":101}}); diff=config_diff(a,b)
    assert set(diff["scientific"])=={"difficulty"} and not diff["ui"]

def test_preset_is_fully_expanded_and_distinguishes_na():
    p=difficulty_preset("MODERATE"); assert len(p.dimensions)==14 and all(x.state==DimensionState.VALUE for x in p.dimensions.values())
    with pytest.raises(ContractError): DifficultyDimension(DimensionState.NOT_APPLICABLE,0,"x","zero is not NA")

def test_d2_uses_general_contracts_and_separates_views():
    entry=registry().get("D2"); views=d2_views(entry)
    assert entry.scenario.schema_version==SCHEMA_VERSION and views["agent_view"]["observer_only_excluded"]
    assert views["scientific_view"]["classification"]=="ANALYST_INTERPRETATION"

def test_schema_incompatibility_fails_explicitly():
    with pytest.raises(ConfigError,match="unsupported schema"): replace(config(),schema_version="v0")

def test_registry_d0_d4_is_behavior_verified_not_name_inferred():
    # The list is pinned so the registry cannot grow silently. D4S was added
    # deliberately: `d4_change.yaml` declares no energy dynamics, so the
    # essential variable never moves there and viability cannot be measured;
    # `d4_adaptation_scientific.yaml` declares step_energy_cost and the
    # ACQUISITION/CAUSAL_CHANGE/RECOVERY phases. D4 still resolves to its
    # original file -- remapping it would change the config_hash of every
    # design that already references it.
    entries=registry().entries(); assert [x.world_id for x in entries]==["D0","D1","D2","D3","D4","D4S"]
    assert all(x.status=="IMPLEMENTED" and x.verified_by and x.definition for x in entries)

def test_canonical_serialization_is_stable_and_lossless_semantically():
    c=config(); assert canonical_json(c)==canonical_json(c) and scientific_hash(c.scientific_payload())==c.content_hash

def test_config_provenance_creates_child_and_structured_delta():
    a=config(); b=patched_configuration(a,{"seeds":[42,43]})
    assert b.provenance.parent_id==a.config_id and b.provenance.parent_hash==a.content_hash and "seeds" in b.provenance.delta

def test_repository_never_silently_overwrites():
    repo=ConfigurationRepository(); repo.save(config())
    with pytest.raises(ConfigError,match="overwrite"): repo.save(config())

def test_config_studio_typed_and_structured_views_share_one_model():
    studio=ConfigStudioService(config()); before=studio.structured(); child=studio.structured_ui_edit({"panel":"world"})
    assert studio.config is child and studio.structured()!=before and child.content_hash==config().content_hash

def test_validation_distinguishes_errors_from_scientific_warnings():
    sandbox=replace(config(),state=ConfigurationState.SANDBOX)
    findings=validate_configuration(sandbox); assert {x.code for x in findings}>={"SANDBOX_ONLY","NOT_PREREGISTERED"}
    assert all(x.category=="SCIENTIFIC_WARNING" for x in findings)

def test_d2_d3_d4_generalize_without_parallel_models():
    result=generalization_check(registry()); assert result["status"]=="GENERALIZES" and result["contract_specializations"]==()
