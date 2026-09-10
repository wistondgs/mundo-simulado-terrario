from pathlib import Path

from terrario.lab.api import LabAPI


def api(): return LabAPI(Path("."))


def test_capability_registry_matrix_and_agent_descriptor_api():
    service=api(); status,body=service.dispatch("GET","/api/capabilities")
    assert status==200 and set(body["matrix"])=={"A0","A1","A2","A3","A4"}
    status,agent=service.dispatch("GET","/api/agents/A4")
    assert status==200 and agent["parameter_count"]>0
    assert agent["warning"]=="INTERPRETATION_REQUIRES_ANALYSIS"


def test_runtime_inspector_requires_valid_sandbox_run():
    status,body=api().dispatch("GET","/api/agents/A4/runtime?run_id=absent")
    assert status==200 and body["availability"]=="NOT_EXPOSED"


def test_runtime_inspector_reads_only_a_valid_engineering_trace():
    service=api()
    status,run=service.dispatch("POST","/api/sandbox",{"world_id":"D2","agent_reference":"A0","world_seed":7,"agent_seed":8,"step_limit":2,"classification":"ENGINEERING_SANDBOX"})
    assert status==201
    service.dispatch("POST",f"/api/sandbox/{run['sandbox_run_id']}/step",{})
    status,snapshot=service.dispatch("GET",f"/api/agents/A0/runtime?run_id={run['sandbox_run_id']}")
    assert status==200 and snapshot["availability"]=="AVAILABLE"
    assert snapshot["classification"]=="ENGINEERING_SANDBOX"
    assert snapshot["observer_payload_in_agent_internals"] is False


def test_compatibility_api_separates_technical_and_cognitive():
    service=api()
    status,body=service.dispatch("POST","/api/compatibility",{"scenario_id":"D2","agent_id":"A0"})
    assert status==200 and body["report"]["execution_compatible"] is True
    status,body=service.dispatch("POST","/api/compatibility",{"scenario_id":"D2","agent_id":"A0","action_interface":False})
    assert body["report"]["status"]=="INVALID_INTERFACE"


def test_metric_observer_registry_applicability_and_estimate_api():
    service=api()
    assert service.dispatch("GET","/api/metrics")[0]==200
    status,body=service.dispatch("POST","/api/metrics/applicability",{"scenario_id":"D2","metric_id":"prediction-error","observer_signals":[]})
    assert status==200 and body["status"]=="MISSING_REQUIRED_SIGNAL"
    status,body=service.dispatch("POST","/api/observer/estimate",{"profile_id":"FULL_DEBUG","steps":100,"trials":5})
    assert status==200 and body["classification"]=="ESTIMATE" and body["estimated_bytes"]>0


def experiment_payload(**changes):
    payload={"draft_id":"ED-API-1","scenario_id":"D2","agent_ids":["A4"],"world_seeds":[1,2],"agent_seeds":[3],"source_artifact":"HYPERCAND-01"}
    payload.update(changes); return payload


def test_experiment_validate_and_create_never_execute_or_approve():
    service=api()
    status,body=service.dispatch("POST","/api/experiment-drafts/validate",experiment_payload())
    assert status==200 and body["artifact_type"]=="ExperimentDraft" and body["scientific_execution"] is False
    assert body["draft"]["state"]=="REVIEW_BLOCKED"
    assert all(x["code"]!="APPROVED_FOR_EXECUTION" for x in body["findings"])
    status,created=service.dispatch("POST","/api/experiment-drafts",experiment_payload())
    assert status==201 and created["scientific_execution"] is False
    assert service.dispatch("POST","/api/experiment-drafts",experiment_payload())[0]==409


def test_experiment_diff_preserves_parent_and_trial_matrix_never_runs():
    service=api(); service.dispatch("POST","/api/experiment-drafts",experiment_payload())
    status,diff=service.dispatch("POST","/api/experiment-drafts/diff",{"parent_id":"ED-API-1","reason":"seed delta","changes":{"world_seeds":[99]}})
    assert status==200 and diff["persisted"] is False and diff["diff"]["hash_changed"] is True
    assert service.dispatch("GET","/api/experiment-drafts/ED-API-1")[1]["world_seeds"]==[1,2]
    status,result=service.dispatch("POST","/api/trial-matrices/build",experiment_payload(warning_threshold=1))
    matrix=result["matrix"]
    assert status==200 and result["execution_performed"] is False
    assert matrix["total_trials"]==4 and "COMBINATORIAL_EXPLOSION" in matrix["warnings"]
    assert all(cell["status"]=="BLOCKED" and cell["blockers"] for cell in matrix["cells"])


def test_02c_api_has_no_scientific_execution_route_or_review_bypass():
    service=api()
    assert service.dispatch("POST","/api/experiment-drafts/execute",experiment_payload())[0] in {400,405}
    status,body=service.dispatch("POST","/api/experiment-drafts/validate",experiment_payload(source_review_state="APPROVED_FOR_EXECUTION"))
    assert status==400 and "unknown experiment draft fields" in body["error"]
