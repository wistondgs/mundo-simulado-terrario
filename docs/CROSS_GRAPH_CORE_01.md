# CROSS-GRAPH-CORE-01

## Classification and boundary

`FEDERATED SCIENTIFIC GRAPH INFRASTRUCTURE + TYPED CROSS-DOMAIN IDENTITY + VERSION-AWARE TRAVERSAL + PROVENANCE + HYPERGRAPH SUPPORT + INTEGRITY`

This phase builds a **versioned scientific federator**, not another monolithic graph. It lets you ask of any known element — *where did this come from, what is it connected to, and how far can I follow its provenance?* — and traverse the whole system without losing identity, version, snapshot, provenance, semantics, or the boundaries between domains.

Central rule: **CrossGraph connects; it never fuses.** Each domain stays sovereign:

```text
ScientificReferenceGraph   TheoryGraph   Hypergraph   Hypothesis
World/Scenario   Experiment/Preregistration   EvidenceGraph
```

CrossGraph owns only cross-domain identities, mappings, links, link provenance, federation snapshots, traversal indexes, derived projections, and audit history. It never copies an authoritative entity out of its store, never modifies a historical graph, never decides which theory is correct, and never executes a trial.

## What is delivered

- **Domain registry** — 12 extensible domains (`REFERENCE`, `CORPUS`, `CLAIM`, `ONTOLOGY`, `THEORY`, `HYPERGRAPH`, `HYPOTHESIS`, `WORLD`, `SCENARIO`, `EXPERIMENT`, `PREREGISTRATION`, `EVIDENCE`) behind a central adapter contract; no scattered domain logic.
- **Typed cross-domain identity** — `CrossDomainEntityRef` (domain, entity_type, entity_id, version_id, snapshot_id, content_hash, schema_version). A reproducible reference pins exact version/snapshot/hash; saved scientific state never uses "latest".
- **Relation semantics registry** — 19 versioned relations with source/target domain constraints, directionality, inverse, transitivity, symmetry, scientific meaning, allowed provenance classes, and acyclicity. `SUPPORTS_THEORY` is intentionally absent: it may only ever be introduced by an explicit EvidenceGraph declaration, never by CrossGraph inference.
- **Cross-link model + lifecycle** — `CrossDomainLink` with assertion class and state (`CANDIDATE`, `ACTIVE`, `REJECTED`, `SUPERSEDED`, `RETRACTED`, `STALE_ENDPOINT`, `UNRESOLVED`). No destructive delete; correction is `old link -> new link` by lineage. A `MACHINE_CANDIDATE` can never be `ACTIVE`.
- **Hyperlinks** — n-ary `CrossDomainHyperlink` preserving members, roles, relation semantics, provenance, and version.
- **Domain adapters** — real adapters for all 12 domains; historical domains (TheoryGraph, Hypergraph, Hypothesis, EvidenceGraph) are strictly read-only.
- **Endpoint resolution** — before activation both endpoints must resolve (exists, version, snapshot, hash). Inaccessible endpoints are classified `DANGLING` / `STALE_VERSION` / `STORE_UNAVAILABLE` / `HASH_MISMATCH` and kept with provenance, never deleted.
- **Traversal engine** — BFS, DFS, shortest typed path, bounded path enumeration, reverse traversal, hyperedge-aware, all bounded by `max_depth`/`max_nodes`/`max_edges`/`allowed_domains`/`allowed_relations`/timeout. `explain_path` gives node/link sequence, relation meaning, provenance, versions, and warnings. A topological `GRAPH_PATH` is never presented automatically as valid scientific reasoning; `SCIENTIFIC_TRACE` validation requires active links, resolvable endpoints, provenance, exact versions, compatible semantics, and no unreviewed machine candidates.
- **Federation manifest + snapshot** — `FederationManifest` pins the exact snapshot combination of every federated domain; `CrossGraphSnapshot` (append-only) commits manifest hash + cross-link-set hash + parent + root hash.
- **GraphSlice** — frontend-ready nodes/edges/hyperedges, provenance summaries, domain identity, warnings, pagination, snapshot manifest.
- **ResearchComposition** — a durable working layer referencing papers/claims/concepts/theory nodes/hyperedges/hypotheses/scenarios/experiments. Composition-local links are distinguished from canonical cross-domain links; a visual connection never alters canonical knowledge.
- **TraceBreak registry** — explicit records (`from`, expected next domain, reason, missing identity/relation, discovered_at, resolution state) wherever a trace cannot continue. Gaps are never filled automatically.

## D2 end-to-end trace (real data)

Built over the imported corpus and the historical TheoryGraph:

- **Treisman feature binding** (`SCI-D2-006`, `FEATURE_BINDING`): Reference resolves, but the TheoryGraph has no canonical feature-binding concept → a real `TraceBreak` is recorded (not invented).
- **Object files** (`SCI-D2-008`, `OBJECT_FILES`): Reference → `MAPS_TO` → TheoryGraph `RawConceptRecord:P3C-0052` ("object files"), an ACTIVE resolvable link; a separate `TraceBreak` records that the reference has no extracted source claim.
- **Scenario trace** (`SCI-D2-001` → D2 scenario → D2 world): `INSTANTIATES_WORLD` ACTIVE; Reference→Scenario recorded as a reviewed candidate.

These validate the heterogeneous architecture; they are not claims that Terrario replicates cognition.

## Firewalls

CrossGraph reads but never writes the TheoryGraph, EvidenceGraph, ReferenceGraph, or a locked Preregistration; it cannot create `EVIDENCE_FOR`/`EVIDENCE_AGAINST` by its own inference, create a hypothesis or ExperimentDraft, preregister, or execute. Verified before/after by explicit tests.

## Verification

- Cross-graph suite: core + advanced tests pass (multiprocess link concurrency with no lost update, crash injection keeping the previous snapshot valid, the required mutation tests, backup/restore preserving roots, export/import, snapshot reproducibility, stale endpoints, missing domains, hash mismatch, invalid relation, invalid hyperedge, path budgets).
- Full repo suite and historical integrity (A0–A4, H-ADAPT integrity only, preregistration, theory snapshot, evidence) remain green.
- Performance: real measurements over a 100k-link synthetic dataset; two accidental O(N²) paths (supersede-state resolution and per-node adjacency scans) were detected and eliminated. See `CROSS_GRAPH_TRACEABILITY_MATRIX.md`.

## Next gate

`SCIENTIFIC-VISUAL-WORKSPACE-01` — the serious scientific frontend: manipulable hypergraphs, references, claims, TheoryGraph, manual compositions, D2 and World2D on a single working surface, backed by this federator.
