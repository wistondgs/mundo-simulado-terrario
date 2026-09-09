from terrario.lab.models import thaw
from terrario.lab.read_model import LabReadModel
from tests.lab_helpers import lab_root

def test_observer_truth_not_exposed_in_agent_view(tmp_path):
    m=LabReadModel(lab_root(tmp_path)); rid=m.runs()[0].id
    agent=thaw(m.agent_view(rid)); observer=thaw(m.observer_view(rid))
    assert "objects" not in agent and "active_rule" not in agent
    assert observer["objects"]["9"]["properties"]["causal_class"] == "SECRET"
