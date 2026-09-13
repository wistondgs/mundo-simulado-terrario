"""Integrity firewall tests for the Scientific Visual Workspace.

Verifies that workspace/frontend operations (graph-slice, composition save,
D2 projection, World2D preview) never modify the TheoryGraph, ReferenceGraph,
EvidenceGraph, locked preregistrations, A0-A4, or execute H-ADAPT.
"""
from pathlib import Path

import pytest

from terrario.lab.api import LabAPI


@pytest.fixture
def api(tmp_path):
    return LabAPI(Path("."), data_root=tmp_path / ".terrario")


def _domain_snapshots(api):
    return {
        "theory": api.cross_graph.adapters[
            __import__("terrario.lab.crossgraph.domain", fromlist=["Domain"]).Domain.THEORY
        ].get_snapshot(),
        "reference": api.cross_graph.adapters[
            __import__("terrario.lab.crossgraph.domain", fromlist=["Domain"]).Domain.REFERENCE
        ].get_snapshot(),
    }


def test_workspace_queries_do_not_modify_sovereign_stores(api):
    from terrario.lab.crossgraph.domain import Domain
    before = _domain_snapshots(api)
    # Exercise the same read paths the workspace uses.
    api.dispatch("POST", "/api/v1/cross-graph/graph-slice", {
        "ref": {"domain": "WORLD", "entity_type": "WorldDefinition", "entity_id": "D2"}, "depth": 1})
    api.dispatch("POST", "/api/v1/reference-graph/projection", {"d_level": "D2"})
    api.dispatch("GET", "/api/v1/cross-graph/trace-breaks")
    api.dispatch("GET", "/api/v1/cross-graph/verify")
    after = _domain_snapshots(api)
    assert before == after, "workspace queries must not alter domain snapshots"


def test_workspace_composition_save_does_not_touch_canonical_graphs(api):
    from terrario.lab.crossgraph.domain import Domain
    before = _domain_snapshots(api)
    links_before = api.cross_graph.counts()["links"]
    api.dispatch("POST", "/api/v1/cross-graph/compositions", {
        "title": "firewall test",
        "refs": [{"domain": "WORLD", "entity_type": "WorldDefinition", "entity_id": "D2"}],
        "local_links": [{"kind": "visual", "from": "a", "to": "b"}],
        "notes": ""})
    after = _domain_snapshots(api)
    assert before == after
    # A composition-local link never becomes a canonical cross-link.
    assert api.cross_graph.counts()["links"] == links_before


def test_workspace_firewall_flags(api):
    _, report = api.dispatch("GET", "/api/v1/cross-graph/verify")
    for flag in ("theory_graph_modified", "evidence_graph_modified",
                 "reference_graph_modified", "preregistration_modified",
                 "scientific_execution", "evidence_publication"):
        assert report["data"][flag] is False


def test_workspace_has_no_execution_or_evidence_route(api):
    # The cross-graph and reference-graph APIs expose no route to execute a
    # trial, publish evidence, or mark a theory true.
    import terrario.lab.crossgraph.api as cg_api
    import terrario.lab.referencegraph.api as rg_api
    for module in (cg_api, rg_api):
        source = Path(module.__file__).read_text()
        for forbidden in ("ScientificRun(", "EvidenceRecord(", "add_evidence(",
                          "link_evidence(", "ScientificConclusion(", "execute_trial(",
                          "mark_theory_true", "support_score"):
            assert forbidden not in source, f"{forbidden} found in {module.__name__}"
