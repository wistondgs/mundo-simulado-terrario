import pytest
from terrario.lab.hypergraph.adapter import HypergraphAdapter
from terrario.lab.hypergraph.models import HyperedgeCandidateRecord
from terrario.lab.models import EpistemicStatus

def test_hyperedge_candidate_cannot_be_promoted_to_fact():
    bad=HyperedgeCandidateRecord("h",("a","b"),"source",EpistemicStatus.EVIDENCE_FOR)
    with pytest.raises(ValueError): HypergraphAdapter().add_hyperedge_candidate(bad)

def test_pdf_ingestion_is_rejected(tmp_path):
    p=tmp_path/"source.pdf";p.write_bytes(b"pdf")
    with pytest.raises(ValueError): HypergraphAdapter.ingest([p])
