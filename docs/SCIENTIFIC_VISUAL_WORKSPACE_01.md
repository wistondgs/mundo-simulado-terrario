# SCIENTIFIC-VISUAL-WORKSPACE-01

## Classification and boundary

`ADVANCED SCIENTIFIC VISUAL WORKSTATION + INTERACTIVE HYPERGRAPH + PROVENANCE EXPLORATION + MANUAL RESEARCH COMPOSITION + D2 SCIENTIFIC STUDIO + WORLD2D INTEGRATION`

This phase turns the federated scientific backend into a **manipulable scientific laboratory**, not a dashboard, demo, or MVP. The design principle is:

> **The user manipulates the science; the system preserves structure, provenance, and integrity.**

The UI never decides which theory is correct, which concepts should merge, which hyperedges should be accepted, which reference "wins", or which result demonstrates intelligence. It gives the user a powerful surface to do those operations consciously.

## What is delivered

- **Modular ES architecture** — native ES modules with JSDoc typing, no framework, no heavy build. State is separated by concern (server scientific state, composition, selection, viewport/layout, transient UI). The legacy `app.js` keeps working; the workspace is a new self-contained application under `terrario/lab/static/workspace/`.
- **Workspace shell** — a true multipanel workstation: Explorer, Scientific Canvas, Inspector, Provenance, Composition, Timeline/History, World. Panels dock, resize, hide/show, and fullscreen; layout persists as a user preference (never scientific state).
- **Scientific canvas** — canvas renderer with pan, zoom, minimap, fit-to-selection, lasso/box selection, multi-select, keyboard navigation, search, filters, domain/relation/provenance visibility, expand neighborhood, collapse, pin/unpin, group/ungroup, focus mode, and history. Layout (force/hierarchical/radial/manual) runs in a Web Worker off the main thread.
- **First-class hypergraph** — hyperedges render as junction nodes connected to every member, preserving n-ary semantics (never reduced to pairwise edges). The hyperedge inspector shows members, roles, outcome, provenance, necessity, sufficiency, confounders, discriminating test, readiness, and lineage; a candidate hyperedge is never shown as a proven mechanism.
- **Reference / Document / Claim inspectors** — full bibliographic identity, document versions, SHA-256, provenance, source claims, protocols, paradigms, methods, constructs, metrics, limitations, replications, critiques, retraction/correction state. Claim type classification (`SOURCE_TEXT`, `SOURCE_REPORTED_CLAIM`, `ANALYST_INTERPRETATION`, `MACHINE_EXTRACTION_UNVERIFIED`, `USER_NOTE`) is never hidden.
- **Provenance drilldown + Path Explorer** — from any node/edge/hyperedge: why is this here, where did it come from, who asserted it, which source/version/snapshot/rule, was it reviewed. Path Explorer uses CrossGraph `explain_path`, distinguishing `GRAPH_PATH`, `PROVENANCE_PATH`, `DEPENDENCY_PATH`, and `SCIENTIFIC_TRACE` (a topological path is never shown as scientific evidence).
- **Trace breaks** — first-class UI showing where a trace ends, which domain/identity/relation is missing, and its state. The three current D2 trace breaks are visible; they are never auto-filled.
- **Research Composition** — the central working layer. Add via drag/drop, multiselect, search, or context menu; connect, disconnect, create composition-local links and hyperedges, annotate, group, compare, duplicate, branch, version, archive. Composition-local relations never modify the canonical graphs; promotion to a canonical cross-link is a separate reviewed act (candidate → validation → human review → ACTIVE). Undo/redo via a command journal that never rewrites append-only scientific history.
- **D2 Scientific Studio** — a specialized D2 view projected over the general model (no hardcoded knowledge), with a D2 reference layer (scientific concepts / reference precedents / Terrario design / trace breaks) and the D2 test family when present as data.
- **World2D integration** — synchronized World Truth / Agent View / Observer View (always distinctly labelled; World Truth is never shown as the agent's observation), a timeline with scrub/step, and engineering-sandbox control (Start/Step/Pause/Resume/Stop) always labelled `ENGINEERING_SANDBOX · NOT EVIDENCE`. No scientific-execution button.
- **Two operating modes** — `EXPLORATORY_LATEST` vs `PINNED_REPRODUCIBLE`, shown unambiguously; pinned mode shows the CrossGraph snapshot, FederationManifest, domain snapshots, and root hashes.

## Performance prerequisite (resolved)

The known limitation — CrossGraph rebuilt adjacency O(E) per query — is resolved. A **materialized adjacency index** (derived, rebuildable, snapshot-aware, non-authoritative, transactionally invalidated, verifiable) plus a snapshot-keyed query cache now serve interactive navigation. Measured on a 100k-link sparse graph: indexed neighborhood ~6 ms, warm repeated query ~4 ms (targets were <250 ms and <100 ms). See `FRONTEND_PERFORMANCE_MODEL.md` and `VISUAL_WORKSPACE_TRACEABILITY_MATRIX.md`.

## Integrity firewall

The workspace reads but never writes the TheoryGraph, ReferenceGraph, EvidenceGraph, or a locked preregistration; it cannot publish evidence, mark a theory true, compute a support score, preregister, or execute a trial. Verified before/after by explicit tests.

## Next gate

`WORLD2D-DEEP-INTEGRATION` — deeper live multi-view synchronization, accelerated render loop, and advanced Observer-event timelines, building on this workspace.
