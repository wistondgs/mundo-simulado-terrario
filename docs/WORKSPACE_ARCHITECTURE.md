# Workspace architecture

The Scientific Visual Workspace is a modular native-ES application under `terrario/lab/static/workspace/`. No framework, no heavy build step; modules are typed with JSDoc and served directly as ES modules.

## Layout

```
workspace/
  index.html            entry page
  main.js               orchestration (boot, panels, canvas, palette, actions)
  workspace.css         layout + domain visual language + accessibility
  core/
    contracts.js        JSDoc typedefs (shared backend/frontend shapes) + visual enums
    api.js              typed API client (UI -> typed API -> domain service)
    state.js            separated stores + command journal (undo/redo)
    shell.js            multipanel shell (dock/resize/hide/fullscreen/persist)
  render/
    graph-renderer.js   canvas renderer (pan/zoom/minimap/selection/marquee)
    layout-engine.js    layout facade (force in Web Worker, hierarchical, radial)
  workers/
    layout-worker.js    force-directed layout off the main thread
  views/
    explorer.js         corpus/references/claims/theory/worlds browser
    inspector.js        object detail + provenance drilldown
    composition.js      ResearchComposition working layer
    d2studio.js         D2 specialized view + reference layer
    world2d.js          World Truth / Agent / Observer + timeline + sandbox
    palette.js          command palette + federated search
```

## Design decisions

- **Modular ES, no framework.** Aligns with the repository's avoidance of unnecessary dependencies, keeps the frontend reproducible, and lets each module be unit-tested with `node --test`. The legacy `app.js` keeps working; the workspace is a new application, migrated in a controlled way rather than a big-bang rewrite.
- **Typed contracts.** `core/contracts.js` is the single source of truth for shared shapes (GraphSlice, PathExplanation, TraceBreak, ResearchComposition, ReferenceRecord, WorldViewState). Contract tests assert the backend responses match these typedefs, catching drift automatically.
- **Separated state.** Server scientific state (read-only mirror), composition state, selection state, viewport/layout state, and transient UI state are distinct stores. Layout/viewport changes never touch scientific state and never affect a scientific hash.
- **Typed API boundary.** The frontend never touches SQLite; it calls the typed API client. Mutating scientific operations require an explicit endpoint and carry the session CSRF token.
- **Canvas rendering, Web Worker layout.** The graph renders on canvas (not DOM-node-per-node, which does not scale). Expensive force-directed layout runs in a Web Worker off the main UI thread; layout is a workspace preference, never a scientific hash.

## Security / input boundaries

Paper titles, claims, user notes, and imported metadata are escaped before rendering; corpus text is never trusted as safe HTML. XSS from metadata/document fields is prevented by escaping every interpolated value.
