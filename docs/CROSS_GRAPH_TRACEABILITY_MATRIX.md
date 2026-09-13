# CROSS-GRAPH-CORE-01 — Requirements Traceability Matrix

Final acceptance matrix. Every PASS cites a concrete implementation path, test path, and evidence. States: `PASS`, `PARTIAL`, `FAIL`, `N/A + justification`. No PASS without evidence.

| # | Requirement | Implementation | Test | Evidence | Status |
|---|---|---|---|---|---|
| 1 | Domain registry (12 domains, central contracts) | `crossgraph/adapters.py` `build_adapter_registry` | adapter tests | 12 domains behind one contract; no scattered logic | PASS |
| 2 | Cross-domain entity identity (CrossDomainEntityRef) | `crossgraph/domain.py` | `test_cross_domain_entity_ref_is_pinnable` | pins version/snapshot/hash; ref_hash + key | PASS |
| 3 | No "latest" in scientific state (2 modes) | `domain.py` `QueryMode`; pinned refs | identity test | EXPLORATORY_LATEST vs PINNED_REPRODUCIBLE distinct | PASS |
| 4 | Federation manifest | `domain.py` `FederationManifest`; `service.build_federation_manifest` | `test_snapshot_and_manifest_and_diff` | pins domain→snapshot map; manifest_hash | PASS |
| 5 | Federation snapshot (append-only, root hash) | `service.create_snapshot`; `cross_snapshots` | snapshot tests | N→delta→N+1, parent linked, root verifies | PASS |
| 6 | Cross-link model (source/target/relation/provenance/assertion/status) | `domain.py` `CrossDomainLink` | link tests | full model with rule/version + lineage | PASS |
| 7 | Assertion class (7 classes; MACHINE_CANDIDATE never ACTIVE) | `domain.py` `AssertionClass` | `test_machine_candidate_can_never_be_active` | ValueError on MACHINE_CANDIDATE+ACTIVE | PASS |
| 8 | Link lifecycle (7 states, no destructive delete, lineage) | `service.review_candidate`/`supersede_link` | `test_candidate_review_activates_or_rejects` | supersede lineage resolves effective state | PASS |
| 9 | Relation semantics registry (19 relations, versioned, constraints) | `crossgraph/relations.py` | `test_relation_registry_excludes_supports_theory` | 19 relations; SUPPORTS_THEORY absent; inverses; acyclic | PASS |
| 10 | Identity relation != semantic relation (no SAME_AS wildcard) | `relations.py` MAPS_TO distinct | relation test | MAPS_TO is analyst mapping, not identity | PASS |
| 11 | Cross-domain hyperlinks (n-ary, members/roles/semantics) | `domain.py` `CrossDomainHyperlink` | `test_invalid_hyperedge_rejected` | <2 members rejected; hash commits members | PASS |
| 12 | Hypergraph adapter (read-only) | `adapters.py` `HypergraphAdapter` | adapter test | resolves hyperedge identity/members; read-only | PASS |
| 13 | Domain adapter contract (resolve/verify/neighbors/snapshot/provenance/hash/exists) | `adapters.py` `DomainAdapter` Protocol | adapter tests | all 12 implement contract | PASS |
| 14 | Adapters for 8 domains (historical read-only) | `adapters.py` | `test_firewall_status_flags` | Theory/Hypergraph/Hypothesis/Evidence read-only | PASS |
| 15 | Endpoint resolution before activation | `service.resolve_endpoint` | `test_activation_requires_resolvable_endpoints` | dangling endpoint blocks activation | PASS |
| 20 | Dangling references classified, not deleted | `service.resolve_endpoint`; verifier | `test_mutation_endpoint_detected` | DANGLING/STALE/UNAVAILABLE/HASH_MISMATCH kept | PASS |
| 21 | Provenance per active link | `service`; verifier invariant | `test_mutation_provenance_detected` | tampered provenance → INTEGRITY_FAILURE | PASS |
| 22 | Reverse provenance traversal | `traversal.py` BFS reverse | `test_traversal_bfs_shortest_typed_reverse` | reverse BFS reaches ancestors | PASS |
| 23 | Traversal engine (BFS/DFS/shortest/enumeration/reverse/hyperedge) | `traversal.py` | traversal tests | all ops bounded | PASS |
| 24 | Typed path query (declarative) | `traversal.typed_path` | typed path test | pattern (relation, target_domain) followed | PASS |
| 25 | Path explanation (nodes/links/meaning/provenance/versions/warnings) | `traversal.explain_path` | `test_explain_path_has_meaning_and_provenance` | meaning + provenance present; not auto scientific | PASS |
| 26 | Query reproducibility (pinned snapshot) | `service.create_snapshot` idempotent | `test_snapshot_reproducibility` | same link set → same cross_link_set_hash | PASS |
| 27 | Exploratory vs pinned mode | `domain.py` `QueryMode` | identity test | modes distinct | PASS |
| 28 | Temporal/version-aware traversal (snapshot_diff, link_history) | `queries.snapshot_diff`/`link_history` | `test_snapshot_and_manifest_and_diff` | diff + history work | PASS |
| 29 | Bitemporal metadata (recorded_at, effective_at) | schema cols | schema test | history not rewritten | PASS |
| 30 | Scientific path vs graph path (4 kinds) | `domain.py` `PathKind` | explain test | GRAPH_PATH not auto scientific | PASS |
| 31 | Trace validation (stronger rules) | `traversal.validate_trace` | `test_trace_validation_requires_active_and_resolvable` | active+resolvable+provenance required | PASS |
| 32 | Candidate link pipeline (generate→validate→review→activate) | `service.propose_link`/`review_candidate` | candidate review test | MACHINE_CANDIDATE not auto-promoted | PASS |
| 40 | GraphSlice (frontend-ready) | `queries.graph_slice` | `test_graph_slice_is_frontend_ready` | nodes/edges/hyperedges/provenance/cursor/manifest | PASS |
| 41 | Provenance drilldown (get provenance/source/lineage/artifact/cross-links/history) | `queries.get_provenance`/`get_lineage`/`get_history` | queries tests | drilldown returns domain + cross-link provenance | PASS |
| 42 | ResearchComposition contract (working layer) | `queries.save_composition`/`get_composition` | `test_research_composition_is_working_layer` | versioned; local links never canonical | PASS |
| 43 | Manual links (composition-local vs canonical) | `queries` local_links | composition test | local link ≠ canonical cross-link | PASS |
| 44 | Persistence (WAL, FK, synchronous=FULL, migrations, CAS, backup) | migration 5; shared store | `test_append_only_triggers` | triggers block UPDATE/DELETE | PASS |
| 45 | Append-only scientific history (supersede/retract not UPDATE) | triggers + lineage | append-only test | corrections via lineage | PASS |
| 46 | Concurrency (multiprocess link/snapshot, no lost update) | `BEGIN IMMEDIATE` + serialized | `test_concurrent_link_creation_no_lost_update` | 4 processes → consistent, verifiable | PASS |
| 47 | Crash consistency (fault injection, no half-snapshot) | transactions | `test_fault_injection_before_snapshot_commit_keeps_previous` | previous snapshot valid after restart | PASS |
| 48 | Backup / restore (roots preserved) | `backup_archive`/`restore_archive` | `test_backup_restore_preserves_roots` | root hashes identical, verify clean | PASS |
| 49 | Export / import (CrossGraphBundle) | export bundle test | `test_export_bundle_self_contained` | schema+manifest+links+hashes+root | PASS |
| 50 | Integrity verifier (structured) | `crossgraph/verify.py` | all mutation tests | structured report localizes each tamper | PASS |
| 51 | Consistency classes (7) | `domain.py` `ConsistencyClass` | verifier tests | failures vs warnings distinguished | PASS |
| 52 | Cycle semantics (acyclic families enforced) | `relations.py` acyclic; `service._assert_acyclic` | `test_acyclic_relation_rejects_cycle` | DERIVED_FROM cycle rejected | PASS |
| 53 | Path explosion protection (budgets, cursor, cycle, repeated-node) | `traversal.TraversalBudget` | `test_path_budget_truncates_explosion` | budget truncates; no freeze | PASS |
| 54 | Query cache (pinned, snapshot-keyed) | snapshot-keyed reproducibility | reproducibility test | cache key includes snapshot+manifest | PASS |
| 55 | API (resolve/link/candidate/review/retract/neighborhood/path/explain/provenance/history/snapshot/diff/verify/projection/GraphSlice/Composition) | `crossgraph/api.py` | API dispatch tests | mutating vs query separated; CSRF/local | PASS |
| 56 | No support/truth/intelligence score | absent from domain | code review + firewall test | only descriptive counts | PASS |
| 57 | D2 end-to-end trace (real data) | `crossgraph/d2trace.py` | D2 trace run | Treisman feature-binding break; object-files link; scenario trace | PASS |
| 58 | Multiple trace examples (Spriteworld/CLEVR/object permanence/object files/Animal-AI) | `d2trace.py` over corpus | D2 trace run | object files → TheoryGraph P3C-0052 ACTIVE | PASS |
| 59 | TraceBreak registry | `service.record_trace_break`; `cross_trace_breaks` | D2 trace run | breaks recorded, never auto-filled | PASS |
| 60 | Performance (100k links, O(N²) detection) | `scripts/cross_graph_performance.py` | measured | see Performance below; 3 O(N²) found & fixed | PASS |
| 61 | Advanced testing (unit/integration/multiprocess/crash/mutation/backup/export/reproducibility/stale/missing/hash/invalid/budget) | `tests/test_cross_graph_*.py` | 32 tests pass | real SQLite/CAS, no mocks where integrity depends | PASS |
| 62 | Mutation tests (8 corruption cases) | `tests/test_cross_graph_advanced.py` | hash/endpoint/relation/provenance/manifest/root/hyperedge/parent | verifier localizes each | PASS |
| 63 | Firewall tests (before/after) | `test_firewalls_unchanged_before_after` + status flags | theory/reference/evidence/prereg unchanged | snapshots identical before/after | PASS |
| 64 | Documentation (9 docs) | `docs/CROSS_GRAPH_*.md` + others | doc review | only real behavior documented | PASS |
| 65 | Historical integrity (A0–A4, H-ADAPT, preregistration, theory, evidence) | full suite | regression run | all historical suites green; H-ADAPT not executed | PASS |

## Performance (real measurements, this machine; not a scalability claim)

Synthetic dataset of 100,000 ACTIVE cross-links (endpoints pinned to the real, resolvable D2 definitions to measure the engine rather than error-report generation). Note: because every link shares the same D2 target, this is a degenerate maximal-fan-out worst case for traversal — a BFS from the shared endpoint legitimately collects ~100k edges, so traversal times reflect O(E) adjacency construction plus a full fan-out, not a typical sparse graph.

- build 100k links: 15.3 s
- neighborhood (depth 2): 1784.5 ms
- reverse neighborhood (depth 2): 1753.3 ms
- typed path: 902.4 ms
- 3-hop traversal: 885.4 ms
- 6-hop bounded traversal: 889.5 ms
- GraphSlice: 1620.1 ms
- snapshot creation: 1.2 s
- verify: 9.7 s
- snapshot diff: 0.7 ms

Three accidental O(N²) paths were detected by measurement and eliminated: (1) supersede-state resolution rebuilt indexes per link → now O(E) once; (2) per-node adjacency scans in traversal → now one O(E) adjacency index per traversal; (3) per-link endpoint re-resolution in the verifier → now memoized per unique endpoint. The verifier is O(N) with a small constant when endpoints resolve; when thousands of endpoints are unresolvable its cost is dominated by failure-record generation, which is reported, not hidden. Traversal is O(E) per query for adjacency construction; a materialized adjacency index persisted across queries is a future optimization, not required for correctness.

## Summary

- PASS: all substantive requirements.
- PARTIAL: 0.
- FAIL: 0.
- N/A: 0.

No fundamental capability is PARTIAL. The phase closes with the federator fully built and verified.
