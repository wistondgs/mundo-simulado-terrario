from dataclasses import replace
import pytest
from terrario.lab.world_authoring import *
from terrario.lab.world_registry import WorldScenarioRegistry

def compiled(wid="D2"):
    e=WorldScenarioRegistry(".").get(wid); return compile_registry_world(wid,e.source)
def draft(wid="D2"):
    e=WorldScenarioRegistry(".").get(wid); return draft_from_legacy(wid,e.source)

def test_valid_world_draft_and_deterministic_compilation():
    d=draft(); assert validate_draft(d)==()
    a=compile_draft(d);b=compile_draft(d);assert a.definition.content_hash==b.definition.content_hash
def test_invalid_schema_geometry_and_action_are_classified():
    d=draft(); findings=validate_draft(replace(d,schema_version="bad",dimensions=(0,999),action_availability=("EXEC",)))
    assert {x.code for x in findings}>={"SCHEMA_ERROR","INVALID_GEOMETRY","INVALID_ACTION_REFERENCE"} and all(x.blocking for x in findings)
def test_impossible_density_is_rejected_without_autofix():
    d=draft(); crowded=replace(d,dimensions=(1,1)); assert any(x.code=="OVERDENSE_WORLD" for x in validate_draft(crowded))
    with pytest.raises(ValueError): compile_draft(crowded)
def test_missing_ground_truth_is_warning_not_silent_invention():
    findings=validate_draft(replace(draft(),observation_sources=()))
    assert any(x.code=="GROUND_TRUTH_INSUFFICIENT" and not x.blocking for x in findings)
def test_compilation_preserves_source_and_draft_immutability():
    d=draft(); before=scientific_hash(d); c=compile_draft(d)
    assert scientific_hash(d)==before and c.definition.provenance.source==d.provenance.source
def test_same_seed_repeats_instance_and_preview_purely():
    c=compiled(); before=c.definition.content_hash;a=generate_instance(c,42);b=generate_instance(c,42);p1=preview(c,42);p2=preview(c,42)
    assert a.instance_hash==b.instance_hash and p1==p2 and c.definition.content_hash==before and p1.classification=="PREVIEW_ONLY"
def test_different_seeds_have_distinct_manifest_identity():
    c=compiled(); assert generate_instance(c,1).instance_hash!=generate_instance(c,2).instance_hash
def test_agent_preview_contains_no_observer_truth():
    agent=preview(compiled(),42).agent_view
    assert set(agent)=={"channels","mask","agent_energy","time_fraction"} and not ({"objects","rules_version","energy_value","world_truth"}&set(agent))
def test_seed_browser_is_structural_and_deterministic():
    browser=SeedBrowser(compiled());a=browser.analyze([1,2,3]);b=browser.analyze([1,2,3])
    assert a==b and a["classification"]=="WORLD_STRUCTURE_ONLY" and a["agent_executed"] is False
def test_degenerate_flags_are_explicit_and_repeatable():
    c=compiled(); structure=dict(generate_instance(c,42).structure);structure["objects"]=[]
    assert degeneracy_flags(structure)==degeneracy_flags(structure) and {"EMPTY_WORLD","NO_INTERACTION_OPPORTUNITY"}<=set(degeneracy_flags(structure))
def test_seed_population_is_bounded():
    with pytest.raises(ValueError): SeedBrowser(compiled()).analyze(range(MAX_SEED_POPULATION+1))
def test_d2_d3_d4_use_same_generation_preview_seed_path():
    for wid in ("D2","D3","D4"):
        c=compiled(wid); assert preview(c,7).classification=="PREVIEW_ONLY" and SeedBrowser(c).inspect(7)["instance_hash"]
