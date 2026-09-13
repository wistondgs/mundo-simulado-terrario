# Cross-graph traversal model

The traversal engine (`terrario/lab/crossgraph/traversal.py`) navigates the federated graph in both directions without ever treating a topological path as valid scientific reasoning by default.

## Operations

- **BFS / DFS** — forward and reverse, over the active-link adjacency.
- **Shortest typed path** — BFS shortest path between two refs.
- **Bounded path enumeration** — all paths up to a budget.
- **Typed path query** — a declarative pattern of `(relation, target_domain)` steps, e.g. `REFERENCE -> REPORTS_CLAIM -> CLAIM -> REFERS_TO_CONCEPT -> ONTOLOGY`, or `HYPOTHESIS -> TESTED_BY -> EXPERIMENT -> HAS_EVIDENCE_RECORD -> EVIDENCE`. The frontend never reconstructs semantics manually.
- **Reverse traversal** — provenance drillback (EvidenceRecord -> Experiment -> Preregistration -> Scenario -> Hypothesis -> Hyperedge -> Theory concept -> Source claim -> Reference -> Document).
- **Hyperedge-aware traversal** — n-ary links are traversed as units, preserving members and roles.

## Budgets and explosion protection

Every traversal carries `max_depth`, `max_nodes`, `max_edges`, `max_results`, a timeout, `allowed_domains`, `allowed_relations`, and a snapshot manifest. Cycle detection and a repeated-node policy are built in; pagination/cursor bounds large results. An accidental query cannot freeze the Lab.

## Path kinds

`GRAPH_PATH`, `PROVENANCE_PATH`, `SCIENTIFIC_TRACE`, and `DEPENDENCY_PATH` are kept distinct. A topological `GRAPH_PATH` is never presented automatically as valid scientific reasoning.

## Path explanation

`explain_path` returns the node sequence, the link sequence, each relation's meaning, provenance, versions, the snapshot vector, and warnings.

## Trace validation

A `SCIENTIFIC_TRACE` must satisfy stronger rules: active links, resolvable endpoints, provenance present, exact versions, compatible semantics, and no unreviewed machine candidates. `validate_trace` reports each failure.

## Performance

Adjacency indexes (outbound/inbound) are built once per traversal (O(E)), not per node, eliminating an accidental O(N·E) blowup. Measured over a 100k-link synthetic dataset; see `CROSS_GRAPH_TRACEABILITY_MATRIX.md` for real numbers.
