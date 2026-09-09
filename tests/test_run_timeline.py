from terrario.lab.models import NOT_APPLICABLE
from terrario.lab.read_model import LabReadModel
from tests.lab_helpers import lab_root

def test_run_timeline_preserves_missing_as_not_applicable(tmp_path):
    m=LabReadModel(lab_root(tmp_path)); point=m.timeline(m.runs()[0].id).points[0]
    assert point.policy_entropy == NOT_APPLICABLE
    assert point.causal_change is True and point.origin == "RECORDED"
