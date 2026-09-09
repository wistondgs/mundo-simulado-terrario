from terrario.lab.read_model import LabReadModel
from tests.lab_helpers import lab_root

def test_lab_read_model_indexes_typed_records(tmp_path):
    model = LabReadModel(lab_root(tmp_path))
    assert model.experiments()[0].run_count == 1
    assert model.run(model.runs()[0].id).code_hash == "code"
    assert model.hypotheses()[0].id == "H-X"
