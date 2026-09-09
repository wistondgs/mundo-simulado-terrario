from terrario.lab.api import LabAPI
from tests.lab_helpers import lab_root

def test_lab_api_get_and_read_only_boundary(tmp_path):
    api=LabAPI(lab_root(tmp_path)); status, runs=api.dispatch("GET","/api/runs")
    assert status == 200 and len(runs) == 1
    assert api.dispatch("POST","/api/runs")[0] == 405
