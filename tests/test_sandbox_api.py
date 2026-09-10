import pytest
from terrario.lab.api import LabAPI

@pytest.fixture
def lab_api(tmp_path):
    api=LabAPI(".");api.sandbox.storage.root=tmp_path;return api

def test_world_preview_seed_and_validation_api(lab_api):
    status,result=lab_api.dispatch("GET","/api/worlds/D2/preview?seed=42");assert status==200 and result["classification"]=="PREVIEW_ONLY"
    status,seeds=lab_api.dispatch("GET","/api/worlds/D2/seeds?values=1,2");assert status==200 and seeds["agent_executed"] is False
    status,validation=lab_api.dispatch("POST","/api/worlds/validate",{"world_id":"D2","dimensions":[0,10]});assert status==200 and not validation["valid"]

def test_sandbox_api_lifecycle_and_trace(lab_api):
    payload={"world_id":"D2","world_seed":42,"agent_seed":1000045,"step_limit":2}
    assert lab_api.dispatch("POST","/api/sandbox/validate",payload)[1]["valid"]
    status,created=lab_api.dispatch("POST","/api/sandbox",payload);assert status==201 and created["classification"]=="ENGINEERING_SANDBOX";rid=created["sandbox_run_id"]
    status,stepped=lab_api.dispatch("POST",f"/api/sandbox/{rid}/step",{});assert status==200 and stepped["state"]=="PAUSED"
    status,done=lab_api.dispatch("POST",f"/api/sandbox/{rid}/run",{"steps":2});assert status==200 and done["state"]=="COMPLETED"
    status,trace=lab_api.dispatch("GET",f"/api/sandbox/{rid}/trace");assert status==200 and len(trace)==2

def test_sandbox_api_rejects_scientific_unknown_and_invalid_requests(lab_api):
    status,result=lab_api.dispatch("POST","/api/sandbox",{"classification":"SCIENTIFIC"});assert status==400 and result["category"]=="PROTOCOL_BOUNDARY_ERROR"
    assert lab_api.dispatch("GET","/api/worlds/UNKNOWN/preview")[0]==404
    assert lab_api.dispatch("GET","/api/sandbox/missing")[0]==404

def test_sandbox_stop_after_completion_is_rejected(lab_api):
    status,created=lab_api.dispatch("POST","/api/sandbox",{"step_limit":1});rid=created["sandbox_run_id"]
    lab_api.dispatch("POST",f"/api/sandbox/{rid}/step",{})
    status,result=lab_api.dispatch("POST",f"/api/sandbox/{rid}/stop",{});assert status==400 and result["category"]=="CONFIG_ERROR"
