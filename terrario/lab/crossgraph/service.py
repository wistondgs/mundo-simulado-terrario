"""Core service for the federated cross-graph.

Owns cross-domain links, hyperlinks, federation manifests, snapshots, endpoint
resolution, the candidate-link pipeline, and the structured integrity
verifier. It writes only to its own append-only tables; it never writes to a
sovereign domain store.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from terrario.lab.crossgraph.adapters import DomainAdapter, build_adapter_registry
from terrario.lab.crossgraph.domain import (
    AssertionClass, ConsistencyClass, CrossDomainEntityRef, CrossDomainHyperlink,
    CrossDomainLink, CrossGraphSnapshot, Domain, EndpointStatus, FederationManifest,
    HyperlinkMember, LinkState, SCHEMA_VERSION, SNAPSHOT_SCHEMA_VERSION, TraceBreak,
    UnresolvableEndpoint,
)
from terrario.lab.crossgraph.relations import get_relation
from terrario.lab.persistence import ArtifactRepository
from terrario.lab.persistence.canonical import content_hash, plain


class CrossGraphService:
    def __init__(self, root: str | Path, artifacts: ArtifactRepository):
        self.root = Path(root)
        self.artifacts = artifacts
        self.adapters: dict[Domain, DomainAdapter] = build_adapter_registry(self.root, artifacts)

    # ------------------------------------------------------------- helpers
    @staticmethod
    def _ref_key(ref: CrossDomainEntityRef) -> str:
        return ref.key()

    def _adapter(self, domain: Domain) -> DomainAdapter:
        adapter = self.adapters.get(domain)
        if adapter is None:
            raise UnresolvableEndpoint(f"no adapter for domain {domain.value}")
        return adapter

    # -------------------------------------------------- endpoint resolution
    def resolve_endpoint(self, ref: CrossDomainEntityRef) -> Mapping[str, Any]:
        adapter = self._adapter(ref.domain)
        if not adapter.exists(ref):
            return {"ref": plain(ref), "status": EndpointStatus.DANGLING.value, "resolved": False}
        if not adapter.verify_identity(ref):
            return {"ref": plain(ref), "status": EndpointStatus.HASH_MISMATCH.value, "resolved": False}
        return {"ref": plain(ref), "status": EndpointStatus.RESOLVED.value, "resolved": True,
                "content_hash": adapter.get_content_hash(ref)}

    # ------------------------------------------------------------ link CRUD
    def _validate_relation(self, link: CrossDomainLink) -> None:
        semantics = get_relation(link.relation_type)
        if semantics is None:
            raise ValueError(f"unknown relation type: {link.relation_type}")
        if link.source_ref.domain.value not in semantics.source_domain_constraint:
            raise ValueError(f"relation {link.relation_type} forbids source domain "
                             f"{link.source_ref.domain.value}")
        if link.target_ref.domain.value not in semantics.target_domain_constraint:
            raise ValueError(f"relation {link.relation_type} forbids target domain "
                             f"{link.target_ref.domain.value}")
        if link.assertion_class.value not in semantics.allowed_provenance_classes:
            raise ValueError(f"relation {link.relation_type} forbids assertion class "
                             f"{link.assertion_class.value}")

    def propose_link(self, source_ref: CrossDomainEntityRef, target_ref: CrossDomainEntityRef,
                     relation_type: str, assertion_class: AssertionClass, provenance: str,
                     actor_id: str, state: LinkState = LinkState.CANDIDATE,
                     rule_id: str | None = None, rule_version: str | None = None,
                     activate: bool = False) -> CrossDomainLink:
        if activate and assertion_class is not AssertionClass.MACHINE_CANDIDATE:
            state = LinkState.ACTIVE
        link = CrossDomainLink(
            self.artifacts._identifier("link"), source_ref, target_ref, relation_type,
            assertion_class, state, provenance, self.artifacts.now(), actor_id,
            rule_id, rule_version)
        self._validate_relation(link)
        if link.state is LinkState.ACTIVE:
            for ref in (source_ref, target_ref):
                resolution = self.resolve_endpoint(ref)
                if not resolution["resolved"]:
                    raise UnresolvableEndpoint(
                        f"cannot activate link with {resolution['status']} endpoint {ref.key()}")
            if semantics_acyclic := (get_relation(relation_type) or None):
                if semantics_acyclic.acyclic:
                    self._assert_acyclic(link)
        with self.artifacts.transaction() as connection:
            self._insert_link(connection, link)
        return link

    def _assert_acyclic(self, new_link: CrossDomainLink) -> None:
        # A new acyclic relation must not create a cycle back to its source.
        reachable = self._reachable(new_link.target_ref.key(), new_link.relation_type,
                                    new_link.source_ref.key())
        if reachable:
            raise ValueError(f"relation {new_link.relation_type} would create a cycle")

    def _reachable(self, start_key: str, relation_type: str, target_key: str) -> bool:
        with self.artifacts._connect() as connection:
            frontier, seen = [start_key], {start_key}
            while frontier:
                current = frontier.pop()
                if current == target_key:
                    return True
                rows = connection.execute(
                    "SELECT target_key FROM cross_links WHERE source_key=? AND relation_type=?"
                    " AND state=?", (current, relation_type, LinkState.ACTIVE.value)).fetchall()
                for row in rows:
                    if row["target_key"] not in seen:
                        seen.add(row["target_key"])
                        frontier.append(row["target_key"])
        return False

    def _insert_link(self, connection, link: CrossDomainLink) -> None:
        connection.execute(
            "INSERT INTO cross_links(link_id,source_ref_json,target_ref_json,source_key,target_key,"
            "relation_type,assertion_class,state,provenance,rule_id,rule_version,supersedes_link_id,"
            "link_hash,effective_at,created_at,created_by) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (link.link_id, json.dumps(plain(link.source_ref)), json.dumps(plain(link.target_ref)),
             self._ref_key(link.source_ref), self._ref_key(link.target_ref), link.relation_type,
             link.assertion_class.value, link.state.value, link.provenance, link.rule_id,
             link.rule_version, link.supersedes_link_id, link.link_hash, link.effective_at,
             link.created_at, link.created_by))

    def review_candidate(self, link_id: str, approve: bool, actor_id: str,
                         reason: str) -> CrossDomainLink:
        row = self._link_row(link_id)
        if row is None:
            from terrario.lab.crossgraph.domain import CrossGraphNotFound
            raise CrossGraphNotFound(link_id)
        if row["state"] != LinkState.CANDIDATE.value:
            raise ValueError(f"link {link_id} is not a candidate")
        source = self._ref_from_json(row["source_ref_json"])
        target = self._ref_from_json(row["target_ref_json"])
        new_state = LinkState.ACTIVE if approve else LinkState.REJECTED
        if approve:
            for ref in (source, target):
                resolution = self.resolve_endpoint(ref)
                if not resolution["resolved"]:
                    raise UnresolvableEndpoint(
                        f"cannot activate: {resolution['status']} endpoint {ref.key()}")
        link = CrossDomainLink(
            self.artifacts._identifier("link"), source, target, row["relation_type"],
            AssertionClass(row["assertion_class"]), new_state,
            f"{row['provenance']} | reviewed by {actor_id}: {reason}",
            self.artifacts.now(), actor_id, row["rule_id"], row["rule_version"],
            supersedes_link_id=link_id)
        with self.artifacts.transaction() as connection:
            self._insert_link(connection, link)
        return link

    def supersede_link(self, link_id: str, new_target: CrossDomainEntityRef,
                       actor_id: str, reason: str) -> CrossDomainLink:
        row = self._link_row(link_id)
        if row is None:
            from terrario.lab.crossgraph.domain import CrossGraphNotFound
            raise CrossGraphNotFound(link_id)
        source = self._ref_from_json(row["source_ref_json"])
        link = CrossDomainLink(
            self.artifacts._identifier("link"), source, new_target, row["relation_type"],
            AssertionClass(row["assertion_class"]), LinkState.ACTIVE,
            f"{row['provenance']} | superseded by {actor_id}: {reason}",
            self.artifacts.now(), actor_id, row["rule_id"], row["rule_version"],
            supersedes_link_id=link_id)
        self._validate_relation(link)
        with self.artifacts.transaction() as connection:
            self._insert_link(connection, link)
        return link

    def _link_row(self, link_id: str) -> Mapping[str, Any] | None:
        with self.artifacts._connect() as connection:
            row = connection.execute(
                "SELECT * FROM cross_links WHERE link_id=? ORDER BY created_at DESC LIMIT 1",
                (link_id,)).fetchone()
            return dict(row) if row else None

    @staticmethod
    def _ref_from_json(value: str) -> CrossDomainEntityRef:
        data = json.loads(value)
        return CrossDomainEntityRef(Domain(data["domain"]), data["entity_type"], data["entity_id"],
                                    data.get("version_id"), data.get("snapshot_id"),
                                    data.get("content_hash"), data.get("schema_version"))

    def current_link_state(self, link_id: str) -> LinkState | None:
        """Resolve the effective state by following the supersede lineage."""
        with self.artifacts._connect() as connection:
            current = connection.execute(
                "SELECT * FROM cross_links WHERE link_id=?", (link_id,)).fetchone()
            if current is None:
                return None
            seen = set()
            while True:
                if current["link_id"] in seen:
                    return LinkState(current["state"])
                seen.add(current["link_id"])
                child = connection.execute(
                    "SELECT * FROM cross_links WHERE supersedes_link_id=? ORDER BY created_at DESC"
                    " LIMIT 1", (current["link_id"],)).fetchone()
                if child is None:
                    return LinkState(current["state"])
                current = child

    def active_links(self, connection=None) -> tuple[Mapping[str, Any], ...]:
        rows = self._all_link_rows(connection)
        states = self._effective_states(rows)
        return tuple(row for row in rows if states[row["link_id"]] == LinkState.ACTIVE.value)

    def _all_link_rows(self, connection=None) -> tuple[Mapping[str, Any], ...]:
        if connection is not None:
            return tuple(dict(r) for r in connection.execute("SELECT * FROM cross_links"))
        with self.artifacts._connect() as connection:
            return tuple(dict(r) for r in connection.execute("SELECT * FROM cross_links"))

    @staticmethod
    def _effective_states(rows: tuple[Mapping[str, Any], ...]) -> dict[str, str]:
        """Resolve every link's effective state in O(E) by following supersede
        lineages over indexes built once."""
        by_id = {row["link_id"]: row for row in rows}
        latest_child: dict[str, Mapping[str, Any]] = {}
        for row in rows:
            parent = row["supersedes_link_id"]
            if parent and (parent not in latest_child
                           or row["created_at"] > latest_child[parent]["created_at"]):
                latest_child[parent] = row
        states: dict[str, str] = {}
        for link_id in by_id:
            current, seen = link_id, set()
            while current in by_id and current not in seen:
                seen.add(current)
                child = latest_child.get(current)
                if child is None:
                    break
                current = child["link_id"]
            states[link_id] = by_id[current]["state"] if current in by_id else by_id[link_id]["state"]
        return states

    def _effective_state(self, rows: tuple[Mapping[str, Any], ...], link_id: str) -> str:
        return self._effective_states(rows)[link_id]

    # ------------------------------------------------------------- hyperlinks
    def propose_hyperlink(self, members: tuple[HyperlinkMember, ...], relation_type: str,
                          assertion_class: AssertionClass, provenance: str, actor_id: str,
                          state: LinkState = LinkState.CANDIDATE) -> CrossDomainHyperlink:
        hyperlink = CrossDomainHyperlink(
            self.artifacts._identifier("hyperlink"), members, relation_type, assertion_class,
            state, provenance, self.artifacts.now(), actor_id)
        with self.artifacts.transaction() as connection:
            connection.execute(
                "INSERT INTO cross_hyperlinks(hyperlink_id,members_json,relation_type,"
                "assertion_class,state,provenance,link_hash,created_at,created_by)"
                " VALUES(?,?,?,?,?,?,?,?,?)",
                (hyperlink.hyperlink_id, json.dumps([plain(m) for m in members]), relation_type,
                 assertion_class.value, state.value, provenance, hyperlink.link_hash,
                 hyperlink.created_at, hyperlink.created_by))
        return hyperlink

    # ------------------------------------------------------ federation snapshot
    def build_federation_manifest(self) -> FederationManifest:
        domain_snapshots: dict[str, str] = {}
        for domain, adapter in self.adapters.items():
            snapshot = adapter.get_snapshot()
            if snapshot:
                domain_snapshots[domain.value] = snapshot
        manifest = FederationManifest(
            self.artifacts._identifier("federation-manifest"), domain_snapshots,
            SNAPSHOT_SCHEMA_VERSION, self.artifacts.now())
        with self.artifacts.transaction() as connection:
            connection.execute(
                "INSERT INTO cross_federation_manifests(manifest_id,domain_snapshots_json,"
                "schema_version,manifest_hash,created_at) VALUES(?,?,?,?,?)",
                (manifest.manifest_id, json.dumps(plain(manifest.domain_snapshots)),
                 manifest.schema_version, manifest.manifest_hash, manifest.created_at))
        return manifest

    def create_snapshot(self, actor_id: str, provenance: str,
                        manifest: FederationManifest | None = None) -> CrossGraphSnapshot:
        manifest = manifest or self.build_federation_manifest()
        with self.artifacts.transaction() as connection:
            links = self.active_links(connection)
            hyperlinks = [dict(r) for r in connection.execute(
                "SELECT * FROM cross_hyperlinks WHERE state=?", (LinkState.ACTIVE.value,))]
            link_set_hash = content_hash(sorted(row["link_hash"] for row in links))
            hyperlink_set_hash = content_hash(sorted(row["link_hash"] for row in hyperlinks))
            cross_link_set_hash = content_hash({"links": link_set_hash, "hyperlinks": hyperlink_set_hash})
            parent = connection.execute(
                "SELECT s.* FROM cross_snapshots s LEFT JOIN cross_snapshots c"
                " ON c.parent_snapshot_id=s.snapshot_id WHERE c.snapshot_id IS NULL"
                " ORDER BY s.created_at DESC LIMIT 1").fetchone()
            parent_id = str(parent["snapshot_id"]) if parent else None
            root = content_hash({
                "schema_version": SNAPSHOT_SCHEMA_VERSION,
                "federation_manifest_hash": manifest.manifest_hash,
                "cross_link_set_hash": cross_link_set_hash, "parent_snapshot_id": parent_id,
                "parent_root_hash": parent["root_hash"] if parent else None})
            snapshot = CrossGraphSnapshot(
                self.artifacts._identifier("cross-snapshot"), parent_id, manifest.manifest_hash,
                cross_link_set_hash, root, len(links), len(hyperlinks),
                self.artifacts.now(), actor_id, provenance)
            connection.execute(
                "INSERT INTO cross_snapshots(snapshot_id,parent_snapshot_id,federation_manifest_hash,"
                "cross_link_set_hash,root_hash,link_count,hyperlink_count,actor,provenance,created_at)"
                " VALUES(?,?,?,?,?,?,?,?,?,?)",
                (snapshot.snapshot_id, snapshot.parent_snapshot_id, snapshot.federation_manifest_hash,
                 snapshot.cross_link_set_hash, snapshot.root_hash, snapshot.link_count,
                 snapshot.hyperlink_count, snapshot.actor, snapshot.provenance, snapshot.created_at))
        return snapshot

    def latest_snapshot(self) -> Mapping[str, Any] | None:
        with self.artifacts._connect() as connection:
            row = connection.execute(
                "SELECT s.* FROM cross_snapshots s LEFT JOIN cross_snapshots c"
                " ON c.parent_snapshot_id=s.snapshot_id WHERE c.snapshot_id IS NULL"
                " ORDER BY s.created_at DESC LIMIT 1").fetchone()
            return dict(row) if row else None

    # -------------------------------------------------------------- trace break
    def record_trace_break(self, from_ref: CrossDomainEntityRef, expected_next_domain: str,
                           reason: str, missing: str) -> TraceBreak:
        trace_break = TraceBreak(
            self.artifacts._identifier("trace-break"), from_ref, expected_next_domain,
            reason, missing, self.artifacts.now())
        with self.artifacts.transaction() as connection:
            connection.execute(
                "INSERT INTO cross_trace_breaks(trace_break_id,from_ref_json,expected_next_domain,"
                "reason,missing_identity_or_relation,resolution_state,discovered_at)"
                " VALUES(?,?,?,?,?,?,?)",
                (trace_break.trace_break_id, json.dumps(plain(from_ref)),
                 trace_break.expected_next_domain, trace_break.reason,
                 trace_break.missing_identity_or_relation, trace_break.resolution_state,
                 trace_break.discovered_at))
        return trace_break

    def list_trace_breaks(self) -> tuple[Mapping[str, Any], ...]:
        with self.artifacts._connect() as connection:
            return tuple(dict(r) for r in connection.execute(
                "SELECT * FROM cross_trace_breaks ORDER BY discovered_at"))

    # ----------------------------------------------------------------- counts
    def counts(self) -> Mapping[str, int]:
        with self.artifacts._connect() as connection:
            def count(table: str) -> int:
                return int(connection.execute(f"SELECT count(*) FROM {table}").fetchone()[0])
            active = len(self.active_links(connection))
            candidates = int(connection.execute(
                "SELECT count(*) FROM cross_links WHERE state=?",
                (LinkState.CANDIDATE.value,)).fetchone()[0])
            return {"links": count("cross_links"), "active_links": active,
                    "candidate_links": candidates, "hyperlinks": count("cross_hyperlinks"),
                    "snapshots": count("cross_snapshots"),
                    "federation_manifests": count("cross_federation_manifests"),
                    "trace_breaks": count("cross_trace_breaks"),
                    "compositions": count("cross_compositions")}
