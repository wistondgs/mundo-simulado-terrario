# Frontend performance model

Interactive scientific navigation has two performance prerequisites, both resolved in this phase.

## Materialized adjacency index

CrossGraph originally rebuilt its adjacency O(E) per query — far too slow for sustained interactive navigation. This phase adds a **materialized adjacency index** (`cross_adjacency_index`, migration 6) that is:

- **rebuildable** — discarded and rebuilt from `cross_links` (the source of truth);
- **snapshot-aware / version-stamped** — stamped with the canonical link-set hash it was built from;
- **non-authoritative** — a derived cache, never a source of truth; a corrupt index is detected and rebuilt;
- **transactionally invalidated** — every canonical link write marks it stale in O(1);
- **verifiable** — the integrity verifier can recompute the link-set hash to detect corruption.

A fast O(1) staleness check guards the interactive path; the O(E) hash verification is reserved for the integrity verifier, not per-query.

## Query cache

A derived cache for **pinned** queries, keyed by `query spec + CrossGraph snapshot root + FederationManifest hash`. A result is never served from the wrong snapshot. Exploratory-latest queries are never cached here.

## Measured results (this machine; not a universal claim)

Query path (100k-link sparse graph):

- indexed neighborhood (depth 3): **~6 ms** (target <250 ms)
- warm repeated pinned query: **~4 ms** (target <100 ms)
- non-indexed equivalent: ~2750 ms (the O(E) path the index replaces)

Render benchmarks (canvas renderer, synthetic visible graphs):

- 1,000 visible nodes / 999 edges: median render **4.9 ms** (~204 FPS), pan 4.7 ms, JS heap ~2.6 MB
- 10,000 visible nodes / 9,999 edges: median render **32.1 ms** (~31 FPS), pan 31.1 ms, JS heap ~5.3 MB

## Main-thread responsiveness

Expensive force-directed layout runs in a Web Worker off the main UI thread. Rendering is requestAnimationFrame-batched. Incremental loading (GraphSlice, cursors, bounded expansion) means the browser never loads 100k links at once. Local dev telemetry (query duration, GraphSlice size, render/layout duration, memory pressure) is instrumented; no telemetry leaves the machine.
