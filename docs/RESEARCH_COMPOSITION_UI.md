# Research Composition UI

The Research Composition is the central working layer of the workspace. It lets the user assemble and manipulate a scientific composition consciously, while the system preserves provenance and never lets the working layer leak into canonical knowledge.

## Building a composition

Members are added via drag/drop, multiselect, search, or context menu. A composition can contain papers, claims, concepts, TheoryGraph nodes, hyperedges, hypotheses, scenarios, worlds, and experiments — each pinned as a `CrossDomainEntityRef`.

## Manual scientific composition

The user can connect, disconnect, create composition-local links, create composition-local hyperedges, annotate, group, compare, duplicate, branch, version, and archive. **These changes never modify the canonical graphs.**

## Canonical promotion boundary

A composition-local relation never silently becomes a canonical cross-link. Promotion is a separate reviewed act:

```text
local relation -> candidate canonical link -> validation -> human review -> ACTIVE
```

## Undo/redo

A command journal drives undo/redo for visual and composition operations. The journal distinguishes `UI`, `COMPOSITION`, and `CANONICAL` operations; a canonical scientific operation is append-only and is never undoable through the visual journal.

## Versioning and diff

Saving creates a new version (`parent`, `delta`, `child`, `actor`, `timestamp`, snapshot bindings) — never a destructive overwrite. Versions can be compared, branched, and restored-as-new-version. The visual diff shows added/removed nodes, added/removed links, changed annotations, and changed snapshot bindings.

## Autosave and recovery

Composition and workspace preferences may autosave. Saving a new scientific version happens when appropriate; autosave never mutates the canonical graph and never auto-promotes links. Unsaved visual work is protected against browser crash, tab close, and server restart via durable persistence.
