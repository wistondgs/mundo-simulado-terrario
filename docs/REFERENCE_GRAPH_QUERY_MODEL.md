# Reference graph query model

The query service (`ReferenceGraphQueries` in `terrario/lab/referencegraph/queries.py`) provides first-level reads and read-only projections. Queries never mutate the graph and never create a snapshot. The HTTP surface is `/api/v1/reference-graph/*` (`terrario/lab/referencegraph/api.py`); mutating governance routes (imports, manual snapshot) are separated from query routes and require local Host/Origin + CSRF.

## First-level queries

- `get_reference(reference_id)` — one reference with tags/constructs/paradigms.
- `get_document_versions(reference_id)` — explicit version lineage for the work.
- `get_claims(reference_id)` — source claims with locators and provenance.
- `get_protocol(reference_id)` — the extracted experimental protocol, if any.
- `get_provenance(reference_id)` — D-level tags, edge provenance, claim provenance.
- `get_neighborhood(node_id, depth)` — bounded traversal (depth capped at 4).
- `find_references(title, doi, year, author)` — bibliographic lookup.
- `find_by_construct(construct)` / `find_by_paradigm(paradigm)` — node-payload search.
- `find_replications()` / `find_critiques()` / `find_limitations()` — by edge type.
- `search_claims(text)` — FTS5 over authorized claim text/summary.
- `snapshot_diff(left_id, right_id)` — node/edge set and root comparison.
- `verify_snapshot(snapshot_id)` — structured per-snapshot verification.

## Projections

`projection(...)` builds a derived read-only view filtered by construct, paradigm, author, year/period, discipline, Terrario D-level, document status, or verification state. A projection is explicitly `read_only: true` and `is_snapshot: false`; it is a view, never a new scientific snapshot, and it never mutates the underlying graph.

## D-level tagging

References may carry D-level tags (`D0…D11`) with a relevance kind (`PRIMARY_RELEVANCE`, `SECONDARY_RELEVANCE`, `TRANSITION_REFERENCE`, `CONTROL_REFERENCE`) and a provenance level. D-levels are accepted as data; the system never assigns a D-level automatically without a rule or provenance.

## Cross-graph boundary

References may store opaque foreign IDs toward the TheoryGraph, Hypergraph, worlds, and experiments as contracts for the next phase. This phase does **not** implement general cross-domain traversal; that belongs to `CROSS-GRAPH-CORE-01`.

## Firewall

The query/API layer exposes no route that writes the EvidenceGraph, modifies the TheoryGraph, creates a hypothesis, creates an ExperimentDraft, preregisters, or executes a ScientificRun. Every status response carries `scientific_execution: false`, `evidence_publication: false`, `theory_graph_modified: false`, `evidence_graph_modified: false`.
