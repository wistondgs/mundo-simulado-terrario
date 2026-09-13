"""Structured integrity verifier for the federated cross-graph."""
from __future__ import annotations

import json
from typing import Any, Mapping

from terrario.lab.crossgraph.domain import (
    AssertionClass, ConsistencyClass, Domain, LinkState, SCHEMA_VERSION,
)
from terrario.lab.crossgraph.relations import get_relation
from terrario.lab.crossgraph.service import CrossGraphService
from terrario.lab.persistence.canonical import content_hash, plain


class CrossGraphVerifier:
    def __init__(self, service: CrossGraphService):
        self.service = service

    def verify(self) -> Mapping[str, Any]:
        failures: list[Mapping[str, Any]] = []
        warnings: list[Mapping[str, Any]] = []

        def fail(kind: ConsistencyClass, detail: str) -> None:
            failures.append({"class": kind.value, "detail": detail})

        def warn(kind: ConsistencyClass, detail: str) -> None:
            warnings.append({"class": kind.value, "detail": detail})

        with self.service.artifacts._connect() as connection:
            links = [dict(r) for r in connection.execute("SELECT * FROM cross_links")]
            hyperlinks = [dict(r) for r in connection.execute("SELECT * FROM cross_hyperlinks")]
            snapshots = [dict(r) for r in connection.execute("SELECT * FROM cross_snapshots")]
            manifests = [dict(r) for r in connection.execute("SELECT * FROM cross_federation_manifests")]

            # link hash integrity + relation semantics + provenance
            for link in links:
                source = self.service._ref_from_json(link["source_ref_json"])
                target = self.service._ref_from_json(link["target_ref_json"])
                expected = content_hash({
                    "link_id": link["link_id"], "source_ref": json.loads(link["source_ref_json"]),
                    "target_ref": json.loads(link["target_ref_json"]),
                    "relation_type": link["relation_type"],
                    "assertion_class": link["assertion_class"], "state": link["state"],
                    "provenance": link["provenance"], "created_at": link["created_at"],
                    "created_by": link["created_by"], "rule_id": link["rule_id"],
                    "rule_version": link["rule_version"],
                    "supersedes_link_id": link["supersedes_link_id"],
                    "effective_at": link["effective_at"]})
                if expected != link["link_hash"]:
                    fail(ConsistencyClass.INTEGRITY_FAILURE, f"LINK_HASH_MISMATCH:{link['link_id']}")
                # denormalized index keys must match the committed refs
                if link["source_key"] != source.key():
                    fail(ConsistencyClass.INTEGRITY_FAILURE,
                         f"SOURCE_KEY_MISMATCH:{link['link_id']}")
                if link["target_key"] != target.key():
                    fail(ConsistencyClass.INTEGRITY_FAILURE,
                         f"TARGET_KEY_MISMATCH:{link['link_id']}")
                semantics = get_relation(link["relation_type"])
                if semantics is None:
                    fail(ConsistencyClass.INTEGRITY_FAILURE,
                         f"UNREGISTERED_RELATION:{link['link_id']}:{link['relation_type']}")
                else:
                    if source.domain.value not in semantics.source_domain_constraint:
                        fail(ConsistencyClass.INTEGRITY_FAILURE,
                             f"SOURCE_DOMAIN_VIOLATION:{link['link_id']}")
                    if target.domain.value not in semantics.target_domain_constraint:
                        fail(ConsistencyClass.INTEGRITY_FAILURE,
                             f"TARGET_DOMAIN_VIOLATION:{link['link_id']}")
                if not link["provenance"]:
                    fail(ConsistencyClass.INTEGRITY_FAILURE, f"PROVENANCE_MISSING:{link['link_id']}")
                if link["assertion_class"] == AssertionClass.MACHINE_CANDIDATE.value \
                        and link["state"] == LinkState.ACTIVE.value:
                    fail(ConsistencyClass.UNREVIEWED_CANDIDATE,
                         f"MACHINE_CANDIDATE_ACTIVE:{link['link_id']}")

            # endpoint resolution for active links (states computed once, and
            # endpoint resolution memoized per unique ref to avoid O(N^2) and
            # repeated adapter I/O across links that share endpoints)
            states = self.service._effective_states(tuple(links))
            resolution_cache: dict[str, Mapping[str, Any]] = {}
            for link in links:
                if states[link["link_id"]] != LinkState.ACTIVE.value:
                    continue
                for ref_json in (link["source_ref_json"], link["target_ref_json"]):
                    ref = self.service._ref_from_json(ref_json)
                    if ref.key() not in resolution_cache:
                        resolution_cache[ref.key()] = self.service.resolve_endpoint(ref)
                    resolution = resolution_cache[ref.key()]
                    if not resolution["resolved"]:
                        status = resolution["status"]
                        kind = (ConsistencyClass.STALE_REFERENCE
                                if status in {"STALE_VERSION", "HASH_MISMATCH"}
                                else ConsistencyClass.DOMAIN_UNAVAILABLE
                                if status == "STORE_UNAVAILABLE"
                                else ConsistencyClass.INTEGRITY_FAILURE)
                        (warn if kind is not ConsistencyClass.INTEGRITY_FAILURE else fail)(
                            kind, f"ENDPOINT_{status}:{ref.key()} for link {link['link_id']}")

            # hyperlink members
            for hyperlink in hyperlinks:
                members = json.loads(hyperlink["members_json"])
                if len(members) < 2:
                    fail(ConsistencyClass.INTEGRITY_FAILURE,
                         f"HYPERLINK_TOO_FEW_MEMBERS:{hyperlink['hyperlink_id']}")
                expected = content_hash({
                    "hyperlink_id": hyperlink["hyperlink_id"], "members": members,
                    "relation_type": hyperlink["relation_type"],
                    "assertion_class": hyperlink["assertion_class"], "state": hyperlink["state"],
                    "provenance": hyperlink["provenance"], "created_at": hyperlink["created_at"],
                    "created_by": hyperlink["created_by"]})
                if expected != hyperlink["link_hash"]:
                    fail(ConsistencyClass.INTEGRITY_FAILURE,
                         f"HYPERLINK_HASH_MISMATCH:{hyperlink['hyperlink_id']}")

            # snapshot ancestry + root
            by_id = {row["snapshot_id"]: row for row in snapshots}
            for snapshot in snapshots:
                parent_id = snapshot["parent_snapshot_id"]
                if parent_id and parent_id not in by_id:
                    fail(ConsistencyClass.INTEGRITY_FAILURE,
                         f"SNAPSHOT_PARENT_MISSING:{snapshot['snapshot_id']}")
            if snapshots:
                seen, cycle = set(), False
                for snapshot in snapshots:
                    cursor, local = snapshot, set()
                    while cursor and cursor["parent_snapshot_id"]:
                        if cursor["snapshot_id"] in local:
                            cycle = True
                            break
                        local.add(cursor["snapshot_id"])
                        cursor = by_id.get(cursor["parent_snapshot_id"])
                if cycle:
                    fail(ConsistencyClass.INTEGRITY_FAILURE, "SNAPSHOT_ANCESTRY_CYCLE")

            # federation manifests well-formed
            for manifest in manifests:
                try:
                    domains = json.loads(manifest["domain_snapshots_json"])
                    if not isinstance(domains, dict):
                        raise ValueError
                except ValueError:
                    fail(ConsistencyClass.INTEGRITY_FAILURE,
                         f"MANIFEST_MALFORMED:{manifest['manifest_id']}")

        report = {
            "schema_version": SCHEMA_VERSION, "valid": not failures,
            "failures": failures, "warnings": warnings,
            "link_count": len(links), "hyperlink_count": len(hyperlinks),
            "snapshot_count": len(snapshots), "manifest_count": len(manifests),
            "theory_graph_modified": False, "evidence_graph_modified": False,
            "reference_graph_modified": False, "preregistration_modified": False,
            "scientific_execution": False, "evidence_publication": False}
        with self.service.artifacts.transaction() as connection:
            connection.execute(
                "INSERT INTO cross_verifications(verification_id,subject_id,report_json,created_at)"
                " VALUES(?,?,?,?)",
                (self.service.artifacts._identifier("verification"), "cross-graph",
                 json.dumps(plain(report)), self.service.artifacts.now()))
        return report
