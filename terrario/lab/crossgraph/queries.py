"""Query and presentation layer for the federated cross-graph.

Provides GraphSlice (frontend-ready), provenance drilldown, snapshot diff,
link/entity history, and the durable ResearchComposition contract. All reads
are bounded; compositions are a working layer and never modify source graphs.
"""
from __future__ import annotations

import json
from typing import Any, Mapping

from terrario.lab.crossgraph.domain import (
    CrossDomainEntityRef, Domain, LinkState, QueryMode, ResearchComposition,
)
from terrario.lab.crossgraph.service import CrossGraphService
from terrario.lab.crossgraph.traversal import TraversalBudget, TraversalEngine


class CrossGraphQueries:
    def __init__(self, service: CrossGraphService):
        self.service = service
        self.engine = TraversalEngine(service)

    # ------------------------------------------------------------ GraphSlice
    def graph_slice(self, center: CrossDomainEntityRef, depth: int = 1,
                    budget: TraversalBudget | None = None, cursor: int = 0,
                    page_size: int = 50) -> Mapping[str, Any]:
        budget = budget or TraversalBudget(max_depth=depth)
        neighborhood = self.engine.bfs(center, budget)
        nodes_full = neighborhood["nodes"]
        page = nodes_full[cursor:cursor + page_size]
        next_cursor = cursor + page_size if cursor + page_size < len(nodes_full) else None
        links = [link for link in self.service.active_links()
                 if link["source_key"] in set(nodes_full) or link["target_key"] in set(nodes_full)]
        with self.service.artifacts._connect() as connection:
            hyperlinks = [dict(r) for r in connection.execute(
                "SELECT * FROM cross_hyperlinks WHERE state=?", (LinkState.ACTIVE.value,))]
        latest = self.service.latest_snapshot()
        return {
            "center": center.key(), "depth": depth,
            "nodes": page, "node_count": len(nodes_full),
            "edges": [{"link_id": l["link_id"], "source": l["source_key"],
                       "target": l["target_key"], "relation_type": l["relation_type"],
                       "assertion_class": l["assertion_class"]} for l in links],
            "hyperedges": [{"hyperlink_id": h["hyperlink_id"],
                            "members": json.loads(h["members_json"]),
                            "relation_type": h["relation_type"]} for h in hyperlinks],
            "provenance_summary": {l["link_id"]: l["provenance"] for l in links},
            "warnings": ["truncated"] if neighborhood["truncated"] else [],
            "next_cursor": next_cursor,
            "snapshot_manifest": {"cross_graph_snapshot": latest["snapshot_id"] if latest else None,
                                  "root_hash": latest["root_hash"] if latest else None}}

    # ---------------------------------------------------- provenance drilldown
    def get_provenance(self, ref: CrossDomainEntityRef) -> Mapping[str, Any]:
        adapter = self.service.adapters.get(ref.domain)
        base = adapter.get_provenance(ref) if adapter else {}
        cross_links = [l for l in self.service.active_links()
                       if l["source_key"] == ref.key() or l["target_key"] == ref.key()]
        return {"ref": ref.key(), "domain_provenance": base,
                "cross_links": [{"link_id": l["link_id"], "relation_type": l["relation_type"],
                                 "provenance": l["provenance"], "created_by": l["created_by"],
                                 "created_at": l["created_at"]} for l in cross_links],
                "resolution": self.service.resolve_endpoint(ref)}

    def get_lineage(self, ref: CrossDomainEntityRef, budget: TraversalBudget | None = None
                    ) -> Mapping[str, Any]:
        budget = budget or TraversalBudget(max_depth=6)
        reverse = self.engine.bfs(ref, budget, reverse=True)
        return {"ref": ref.key(), "ancestors": reverse["nodes"], "depth": reverse["depth_reached"]}

    def get_history(self, ref: CrossDomainEntityRef) -> Mapping[str, Any]:
        with self.service.artifacts._connect() as connection:
            rows = [dict(r) for r in connection.execute(
                "SELECT * FROM cross_links WHERE source_key=? OR target_key=? ORDER BY created_at",
                (ref.key(), ref.key()))]
        return {"ref": ref.key(),
                "history": [{"link_id": r["link_id"], "state": r["state"],
                             "relation_type": r["relation_type"], "created_at": r["created_at"],
                             "supersedes_link_id": r["supersedes_link_id"]} for r in rows]}

    # ------------------------------------------------------------- snapshots
    def snapshot_diff(self, left_id: str, right_id: str) -> Mapping[str, Any]:
        with self.service.artifacts._connect() as connection:
            left = connection.execute("SELECT * FROM cross_snapshots WHERE snapshot_id=?",
                                      (left_id,)).fetchone()
            right = connection.execute("SELECT * FROM cross_snapshots WHERE snapshot_id=?",
                                       (right_id,)).fetchone()
        if left is None or right is None:
            from terrario.lab.crossgraph.domain import CrossGraphNotFound
            raise CrossGraphNotFound(f"snapshot not found")
        left, right = dict(left), dict(right)
        return {"left_snapshot_id": left_id, "right_snapshot_id": right_id,
                "same_link_set": left["cross_link_set_hash"] == right["cross_link_set_hash"],
                "same_manifest": left["federation_manifest_hash"] == right["federation_manifest_hash"],
                "same_root": left["root_hash"] == right["root_hash"],
                "link_count_delta": right["link_count"] - left["link_count"],
                "left_root_hash": left["root_hash"], "right_root_hash": right["root_hash"]}

    def link_history(self, link_id: str) -> Mapping[str, Any]:
        with self.service.artifacts._connect() as connection:
            chain, cursor, seen = [], link_id, set()
            while cursor and cursor not in seen:
                seen.add(cursor)
                row = connection.execute("SELECT * FROM cross_links WHERE link_id=?",
                                         (cursor,)).fetchone()
                if row is None:
                    break
                chain.append({"link_id": row["link_id"], "state": row["state"],
                              "created_at": row["created_at"], "created_by": row["created_by"],
                              "provenance": row["provenance"]})
                descendants = connection.execute(
                    "SELECT link_id FROM cross_links WHERE supersedes_link_id=?"
                    " ORDER BY created_at DESC LIMIT 1", (cursor,)).fetchone()
                cursor = descendants["link_id"] if descendants else None
        return {"link_id": link_id, "lineage": chain,
                "current_state": self.service.current_link_state(link_id)}

    # --------------------------------------------------- research composition
    def save_composition(self, title: str, refs: tuple[CrossDomainEntityRef, ...],
                         local_links: tuple[Mapping[str, Any], ...], notes: str,
                         actor_id: str, composition_id: str | None = None,
                         parent_composition_id: str | None = None) -> ResearchComposition:
        with self.service.artifacts.transaction() as connection:
            version = 1
            if composition_id:
                row = connection.execute(
                    "SELECT max(version) AS v FROM cross_compositions WHERE composition_id=?",
                    (composition_id,)).fetchone()
                version = int(row["v"] or 0) + 1
            composition = ResearchComposition(
                composition_id or self.service.artifacts._identifier("composition"),
                title, refs, local_links, notes, version, parent_composition_id,
                self.service.artifacts.now(), actor_id)
            connection.execute(
                "INSERT INTO cross_compositions(composition_id,title,refs_json,local_links_json,"
                "notes,version,parent_composition_id,created_at,created_by) VALUES(?,?,?,?,?,?,?,?,?)",
                (composition.composition_id, composition.title,
                 json.dumps([self._ref_dict(r) for r in refs]), json.dumps([dict(x) for x in local_links]),
                 notes, version, parent_composition_id, composition.created_at, actor_id))
        return composition

    @staticmethod
    def _ref_dict(ref: CrossDomainEntityRef) -> Mapping[str, Any]:
        return {"domain": ref.domain.value, "entity_type": ref.entity_type,
                "entity_id": ref.entity_id, "version_id": ref.version_id,
                "snapshot_id": ref.snapshot_id, "content_hash": ref.content_hash,
                "schema_version": ref.schema_version}

    def get_composition(self, composition_id: str) -> Mapping[str, Any]:
        with self.service.artifacts._connect() as connection:
            rows = [dict(r) for r in connection.execute(
                "SELECT * FROM cross_compositions WHERE composition_id=? ORDER BY version",
                (composition_id,))]
        if not rows:
            from terrario.lab.crossgraph.domain import CrossGraphNotFound
            raise CrossGraphNotFound(composition_id)
        latest = rows[-1]
        return {"composition_id": composition_id, "title": latest["title"],
                "version": latest["version"], "refs": json.loads(latest["refs_json"]),
                "local_links": json.loads(latest["local_links_json"]),
                "notes": latest["notes"], "versions": len(rows),
                "created_by": latest["created_by"], "created_at": latest["created_at"]}
