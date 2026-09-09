import pytest
from dataclasses import FrozenInstanceError
from terrario.lab.read_model import LabReadModel
from tests.lab_helpers import lab_root

def test_read_model_records_are_immutable(tmp_path):
    record = LabReadModel(lab_root(tmp_path)).runs()[0]
    with pytest.raises(FrozenInstanceError): record.status = "changed"

def test_raw_evidence_is_unchanged_by_queries(tmp_path):
    root=lab_root(tmp_path); p=root/"runs/pilot/x_results.json"; before=p.read_bytes(); m=LabReadModel(root)
    m.catalog(); m.timeline(m.runs()[0].id)
    assert p.read_bytes() == before
