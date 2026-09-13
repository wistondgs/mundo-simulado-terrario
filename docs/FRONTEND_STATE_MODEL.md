# Frontend state model

Frontend state is separated by concern and never mixed into one amorphous global store.

## Stores

- **serverScientificState** — a read-only mirror of data fetched from the backend (status, references, snapshots, trace breaks, verify reports). The backend remains the source of truth.
- **compositionState** — the active ResearchComposition working layer: members, local links, local hyperedges, annotations, dirty flag, version count.
- **selectionState** — selected node keys, focused key, inspected key/kind.
- **viewportState** — pan/zoom, layout choice, node positions, panel layout, operating mode, pinned snapshot. This is **never** scientific state.
- **transientState** — ephemeral UI: palette open, search query, dragging, hover, busy, current error.

Each store is a tiny observable (`Store` with `get`/`set`/`subscribe`). `set` produces a new state object; the previous snapshot is never mutated.

## Command journal

Undo/redo is driven by a `CommandJournal` that distinguishes three operation kinds:

- `UI` — pure visual operations (selection, viewport);
- `COMPOSITION` — composition working-layer operations;
- `CANONICAL` — canonical scientific operations, which are **append-only and never undoable** through the visual journal (the journal throws if one is pushed).

## Invariants

- Layout/viewport changes never touch scientific state and never affect a scientific hash.
- Composition-local links/hyperedges live only in `compositionState`; they never become canonical cross-links.
- The operating mode (`EXPLORATORY_LATEST` vs `PINNED_REPRODUCIBLE`) is explicit state, shown unambiguously, and never conflated.
