from dataclasses import replace
from pathlib import Path
import hashlib,json
import pytest
from terrario.lab.sandbox_runtime import *
from terrario.lab.world_authoring import compile_registry_world
from terrario.lab.world_contracts import ConfigurationState
from terrario.lab.world_registry import WorldScenarioRegistry,configuration_for

def setup(tmp_path,wid="D2",steps=4,seed=42):
    e=WorldScenarioRegistry(".").get(wid); c=compile_registry_world(wid,e.source); config=derive_sandbox(configuration_for(e)); spec=make_spec(config,c,seed,seed+1000003,steps); service=SandboxService(tmp_path); return service,service.create(spec,config,c),config,c
def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def test_sandbox_rejects_scientific_classification(tmp_path):
    e=WorldScenarioRegistry(".").get("D2");c=compile_registry_world("D2",e.source);config=derive_sandbox(configuration_for(e))
    with pytest.raises(SandboxBoundaryError): make_spec(config,c,42,1,2,ExecutionClassification.SCIENTIFIC)
def test_evidence_firewall_always_rejects_sandbox():
    with pytest.raises(SandboxBoundaryError): EvidenceFirewall().register(ExecutionClassification.ENGINEERING_SANDBOX,{})
def test_locked_config_requires_derived_child_and_parent_is_unchanged():
    e=WorldScenarioRegistry(".").get("D2");base=configuration_for(e);locked=base.transition(ConfigurationState.PREREGISTERED,"p").transition(ConfigurationState.LOCKED,"l");before=locked.content_hash;c=compile_registry_world("D2",e.source)
    with pytest.raises(SandboxValidationError): make_spec(locked,c,1,2)
    child=derive_sandbox(locked);assert locked.state==ConfigurationState.LOCKED and locked.content_hash==before and child.state==ConfigurationState.SANDBOX and child.provenance.parent_id==locked.config_id
def test_lifecycle_step_pause_resume_complete_and_watermark(tmp_path):
    s,run,_,_=setup(tmp_path,steps=2);assert run.state==RunState.READY;s.step(run.run_id);assert run.state==RunState.PAUSED;s.resume(run.run_id);assert run.state==RunState.RUNNING;s.step(run.run_id);assert run.state==RunState.COMPLETED
    payload=s.storage.read(run.run_id);assert payload["classification"]=="ENGINEERING_SANDBOX" and payload["scientific_evidence"] is False and all(x["classification"]=="ENGINEERING_SANDBOX" for x in payload["timeline"])
def test_trace_keeps_agent_observation_separate_from_world_truth(tmp_path):
    s,run,_,_=setup(tmp_path);t=s.step(run.run_id);assert set(t.agent_observation)=={"channels","mask","agent_energy","time_fraction"};assert "objects" in t.observer_world and "objects" not in t.agent_observation
def test_unique_restart_and_same_seed_are_isolated(tmp_path):
    s,run,_,_=setup(tmp_path);s.step(run.run_id);other=s.restart(run.run_id);assert other.run_id!=run.run_id and other.spec.world_seed==run.spec.world_seed and not other.timeline and len(run.timeline)==1
def test_two_runs_do_not_share_world_agent_or_timeline(tmp_path):
    s,a,config,c=setup(tmp_path);b=s.create(a.spec,config,c);s.step(a.run_id)
    assert len(a.timeline)==1 and len(b.timeline)==0 and s._runtime[a.run_id]["world"] is not s._runtime[b.run_id]["world"] and s._runtime[a.run_id]["agent"] is not s._runtime[b.run_id]["agent"]
def test_stop_does_not_overwrite_prior_run(tmp_path):
    s,run,_,_=setup(tmp_path);s.stop(run.run_id);before=s.storage.read(run.run_id)
    with pytest.raises(SandboxValidationError):s.stop(run.run_id)
    assert s.storage.read(run.run_id)==before
def test_ready_storage_is_explicitly_incomplete(tmp_path):
    s,run,_,_=setup(tmp_path);payload=s.storage.read(run.run_id);assert payload["complete"] is False and payload["trace_schema_version"]==TRACE_SCHEMA
def test_preview_and_sandbox_do_not_change_frozen_scientific_review(tmp_path):
    review=Path("scientific_reviews/review-fee74e994bc654ca/scientific_review.json");before=digest(review);s,run,_,_=setup(tmp_path);s.run_bounded(run.run_id);assert digest(review)==before
def test_d2_end_to_end_and_d3_d4_spec_compatibility(tmp_path):
    s,run,_,_=setup(tmp_path,"D2",2);s.run_bounded(run.run_id);assert s.storage.read(run.run_id)["state"]=="COMPLETED"
    for wid in ("D3","D4"):
        service,r,_,_=setup(tmp_path/wid,wid,1);assert r.spec.classification==ExecutionClassification.ENGINEERING_SANDBOX
