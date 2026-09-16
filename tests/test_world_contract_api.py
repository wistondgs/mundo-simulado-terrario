from terrario.lab.api import LabAPI

def test_registry_and_d2_studio_api_are_narrow_and_serializable(tmp_path):
    api=LabAPI(".", data_root=tmp_path/".terrario"); status,worlds=api.dispatch("GET","/api/worlds")
    assert status==200 and len(worlds)==5 and all(x["status"]=="IMPLEMENTED" for x in worlds)
    status,d2=api.dispatch("GET","/api/studio/d2"); assert status==200 and d2["generalization"]["status"]=="GENERALIZES"

def test_config_validation_api_does_not_persist_or_execute(tmp_path):
    api=LabAPI(".", data_root=tmp_path/".terrario"); before=api.d2_configuration
    status,result=api.dispatch("POST","/api/config/validate",{"difficulty":{"world_size":101}})
    assert status==200 and result["scientific_hash"]!=before.content_hash and api.d2_configuration is before

def test_config_diff_api_separates_ui_from_science(tmp_path):
    api=LabAPI(".", data_root=tmp_path/".terrario"); status,result=api.dispatch("POST","/api/config/diff",{"ui_preferences":{"zoom":2}})
    assert status==200 and not result["scientific"] and result["ui"]

def test_invalid_api_patch_is_classified(tmp_path):
    status,result=LabAPI(".", data_root=tmp_path/".terrario").dispatch("POST","/api/config/validate",{"world_truth":True})
    assert status==400 and result["category"]=="CONFIG_ERROR"

def test_lab_api_without_scenarios_keeps_base_api_available(tmp_path):
    api=LabAPI(tmp_path)
    assert api.dispatch("GET","/api/status")[0]==200
    assert api.dispatch("GET","/api/studio/d2")[0]==404

def test_api_configuration_roundtrip_preserves_semantic_identity(tmp_path):
    api=LabAPI(".", data_root=tmp_path/".terrario"); payload=api.dispatch("GET","/api/studio/d2")[1]["configuration"]
    status,result=api.dispatch("POST","/api/config/roundtrip",payload)
    assert status==200 and result["scientific_hash"]==api.d2_configuration.content_hash
    assert result["configuration"]["difficulty"]==payload["difficulty"]
