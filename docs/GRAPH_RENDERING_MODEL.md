# Graph rendering model

The scientific canvas renders on HTML canvas (not DOM-node-per-graph-node) so it scales to thousands of visible elements. Rendering is decoupled from layout: positions come from the layout engine and are stored as a workspace preference.

## Capabilities

Pan, zoom (to-cursor), minimap with viewport rectangle, fit-to-selection, lasso/box selection (shift-drag), multi-select, node drag (with multi-drag of the selection), double-click expand-neighborhood, and focus ring. Rendering is requestAnimationFrame-batched; only state changes trigger a frame.

## Domain visual language

Every domain is distinguished by **shape + color + icon + label**, never color alone (accessibility). Shapes: document (reference/document), diamond (concept), hexagon (theory), junction (hyperedge), ellipse (hypothesis), square (scenario), grid (world), flask (experiment), lock (preregistration), star (evidence). Border semantics: selected = thick dark border, focused = accent ring. Assertion class affects edge style: active links solid, machine candidates dashed and warm-colored.

## Hyperedges as first-class

A hyperedge is rendered as a **junction node** connected to every member, preserving the n-ary structure. It is never reduced to pairwise ordinary edges; the original members/roles remain inspectable in the hyperedge inspector. The junction shows the member count.

## Layout engine

- **Force-directed** — runs in a Web Worker (`workers/layout-worker.js`) off the main UI thread, deterministic (seeded), with cooling. Falls back to a synchronous circular layout when workers are unavailable.
- **Hierarchical** — layered by BFS depth from roots.
- **Radial/focus** — concentric around a center node.
- **Manual** — user-dragged positions, persisted.

Layout is a workspace preference and never affects a scientific hash.

## Incremental loading

The canvas never loads 100k links at once. It uses GraphSlice, pagination/cursors, bounded expansion, and progressive disclosure: the canvas starts from a seed neighborhood and expands on demand (double-click / Expand), merging new slices into the existing graph without duplicates.

## Performance

Render benchmarks characterize 1k and 10k visible elements (render duration, pan latency, approximate FPS, JS heap). Real numbers are reported in `VISUAL_WORKSPACE_TRACEABILITY_MATRIX.md`; there is no universal scalability claim.
