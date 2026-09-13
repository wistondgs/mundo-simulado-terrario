"""Versioned HTTP contract for the federated cross-graph.

Query routes and mutating governance routes are separated. This API exposes no
route that writes a sovereign domain (TheoryGraph, EvidenceGraph,
ReferenceGraph, Preregistration), creates a hypothesis/ExperimentDraft,
preregisters, or executes a trial.
"""
from __future__ import annotations

import secrets
from typing import Any, Mapping

from terrario.lab.crossgraph.domain import (
    AssertionClass, CrossDomainEntityRef, CrossGraphNotFound, Domain, HyperlinkMember,
    LinkState, UnresolvableEndpoint,
)
from terrario.lab.crossgraph.queries import CrossGraphQueries
from terrario.lab.crossgraph.service import CrossGraphService
from terrario.lab.crossgraph.traversal import TraversalBudget
from terrario.lab.crossgraph.verify import CrossGraphVerifier
from terrario.lab.persistence import ArtifactNotFound


def _ref(payload: Mapping[str, Any]) -> CrossDomainEntityRef:
    return CrossDomainEntityRef(
        Domain(str(payload["domain"])), str(payload["entity_type"]), str(payload["entity_id"]),
        payload.get("version_id"), payload.get("snapshot_id"), payload.get("content_hash"),
        payload.get("schema_version"))


def _budget(payload: Mapping[str, Any]) -> TraversalBudget:
    return TraversalBudget(
        int(payload.get("max_depth", 4)), int(payload.get("max_nodes", 500)),
        int(payload.get("max_edges", 2000)), int(payload.get("max_results", 100)),
        float(payload.get("timeout_s", 5.0)),
        tuple(payload.get("allowed_domains", ())), tuple(payload.get("allowed_relations", ())))


class CrossGraphAPI:
    def __init__(self, service: CrossGraphService):
        self.service = service
        self.queries = CrossGraphQueries(service)
        self.verifier = CrossGraphVerifier(service)
        self.session_id = f"session-{secrets.token_hex(16)}"
        self.csrf_token = secrets.token_urlsafe(32)

    # Routes that mutate governance state and therefore require CSRF/local
    # authorization. Read-only queries (even when sent as POST) do not.
    _MUTATING_PREFIXES = (
        ("links",), ("hyperlinks",), ("imports",), ("snapshots",), ("compositions",),
    )

    def dispatch(self, method: str, parts: list[str], query: Mapping[str, list[str]],
                 payload: Mapping[str, Any] | None, headers: Mapping[str, str] | None = None):
        request_id = f"req-{secrets.token_hex(8)}"
        p, headers = dict(payload or {}), dict(headers or {})
        try:
            if method != "GET" and headers and self._is_mutating(parts):
                self._authorize(headers)
            status, data = self._route(method, parts, query, p, headers)
            return status, {"data": data, "meta": {"request_id": request_id,
                                                   "schema_version": "terrario.api/v1"}}
        except Exception as exc:
            code = getattr(exc, "code", "INVALID_REQUEST")
            if isinstance(exc, (ArtifactNotFound, CrossGraphNotFound)): status = 404
            elif isinstance(exc, UnresolvableEndpoint): status = 422
            elif isinstance(exc, PermissionError): status = 403
            elif isinstance(exc, (ValueError, KeyError)): status = 400
            else: status = 500
            return status, {"error": {"code": code, "message": str(exc), "details": {},
                                      "request_id": request_id}}

    def _route(self, method, parts, query, p, headers):
        if method == "GET" and parts == []:
            return 200, {"counts": self.service.counts(), "scientific_execution": False,
                         "evidence_publication": False, "theory_graph_modified": False,
                         "evidence_graph_modified": False, "reference_graph_modified": False,
                         "preregistration_modified": False}
        if method == "POST" and parts == ["resolve"]:
            return 200, self.service.resolve_endpoint(_ref(p))
        if method == "POST" and parts == ["links"]:
            link = self.service.propose_link(
                _ref(p["source_ref"]), _ref(p["target_ref"]), str(p["relation_type"]),
                AssertionClass(str(p.get("assertion_class", "USER_ASSERTED"))),
                str(p["provenance"]), "local-user",
                LinkState(str(p.get("state", "CANDIDATE"))), p.get("rule_id"),
                p.get("rule_version"), bool(p.get("activate", False)))
            return 201, {"link_id": link.link_id, "state": link.state.value,
                         "link_hash": link.link_hash}
        if method == "POST" and parts == ["links", "review"]:
            link = self.service.review_candidate(
                str(p["link_id"]), bool(p["approve"]), "local-user", str(p.get("reason", "")))
            return 200, {"link_id": link.link_id, "state": link.state.value}
        if method == "POST" and parts == ["links", "supersede"]:
            link = self.service.supersede_link(
                str(p["link_id"]), _ref(p["new_target_ref"]), "local-user", str(p.get("reason", "")))
            return 200, {"link_id": link.link_id, "state": link.state.value}
        if method == "POST" and parts == ["hyperlinks"]:
            members = tuple(HyperlinkMember(_ref(m), str(m.get("role", "member")))
                            for m in p["members"])
            hyperlink = self.service.propose_hyperlink(
                members, str(p["relation_type"]),
                AssertionClass(str(p.get("assertion_class", "USER_ASSERTED"))),
                str(p["provenance"]), "local-user",
                LinkState(str(p.get("state", "CANDIDATE"))))
            return 201, {"hyperlink_id": hyperlink.hyperlink_id, "link_hash": hyperlink.link_hash}
        if method == "POST" and parts == ["traverse", "neighborhood"]:
            return 200, self.queries.engine.bfs(_ref(p["ref"]), _budget(p),
                                                bool(p.get("reverse", False)))
        if method == "POST" and parts == ["traverse", "shortest-path"]:
            path = self.queries.engine.shortest_path(
                _ref(p["start_ref"]), _ref(p["end_ref"]), _budget(p),
                bool(p.get("reverse", False)))
            return 200, {"path": self.queries.engine.explain_path(path) if path else None}
        if method == "POST" and parts == ["traverse", "typed-path"]:
            pattern = tuple((step["relation"], step["target_domain"]) for step in p["pattern"])
            paths = self.queries.engine.typed_path(_ref(p["start_ref"]), pattern, _budget(p))
            return 200, {"paths": [self.queries.engine.explain_path(x) for x in paths]}
        if method == "POST" and parts == ["traverse", "validate-trace"]:
            pattern = tuple((step["relation"], step["target_domain"]) for step in p["pattern"])
            paths = self.queries.engine.typed_path(_ref(p["start_ref"]), pattern, _budget(p))
            return 200, {"traces": [self.queries.engine.validate_trace(x) for x in paths]}
        if method == "POST" and parts == ["graph-slice"]:
            return 200, self.queries.graph_slice(
                _ref(p["ref"]), int(p.get("depth", 1)), _budget(p),
                int(p.get("cursor", 0)), int(p.get("page_size", 50)))
        if method == "POST" and parts == ["provenance"]:
            return 200, self.queries.get_provenance(_ref(p["ref"]))
        if method == "POST" and parts == ["lineage"]:
            return 200, self.queries.get_lineage(_ref(p["ref"]), _budget(p))
        if method == "POST" and parts == ["history"]:
            return 200, self.queries.get_history(_ref(p["ref"]))
        if method == "GET" and parts == ["trace-breaks"]:
            return 200, {"items": self.service.list_trace_breaks()}
        if method == "GET" and parts == ["snapshots"]:
            return 200, {"latest": self.service.latest_snapshot()}
        if method == "POST" and parts == ["snapshots"]:
            snapshot = self.service.create_snapshot("local-user", str(p.get("provenance", "manual")))
            return 201, {"snapshot_id": snapshot.snapshot_id, "root_hash": snapshot.root_hash}
        if method == "POST" and parts == ["snapshots", "diff"]:
            return 200, self.queries.snapshot_diff(
                str(p["left_snapshot_id"]), str(p["right_snapshot_id"]))
        if method == "GET" and parts == ["verify"]:
            return 200, self.verifier.verify()
        if method == "POST" and parts == ["compositions"]:
            refs = tuple(_ref(r) for r in p.get("refs", ()))
            composition = self.queries.save_composition(
                str(p["title"]), refs, tuple(p.get("local_links", ())), str(p.get("notes", "")),
                "local-user", p.get("composition_id"), p.get("parent_composition_id"))
            return 201, {"composition_id": composition.composition_id, "version": composition.version}
        if method == "GET" and len(parts) == 2 and parts[0] == "compositions":
            return 200, self.queries.get_composition(parts[1])
        raise ArtifactNotFound("/api/v1/cross-graph/" + "/".join(parts))

    def _is_mutating(self, parts: list[str]) -> bool:
        if not parts:
            return False
        head = parts[0]
        if head in {"links", "hyperlinks", "imports"}:
            return True
        # snapshots and compositions are mutating only on create, not on
        # read-only sub-routes such as snapshots/diff or compositions/{id}.
        if head in {"snapshots", "compositions"}:
            return len(parts) == 1
        return False

    def _authorize(self, headers: Mapping[str, str]) -> None:
        host = headers.get("Host", "")
        origin = headers.get("Origin", "")
        if host and not (host.startswith("127.0.0.1") or host.startswith("localhost")):
            raise PermissionError("non-local Host rejected")
        if origin and not (origin.startswith("http://127.0.0.1") or origin.startswith("http://localhost")):
            raise PermissionError("non-local Origin rejected")
        if headers.get("X-CSRF-Token") != self.csrf_token:
            raise PermissionError("invalid CSRF token")
