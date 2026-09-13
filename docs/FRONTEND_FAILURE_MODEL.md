# Frontend failure model

The workspace distinguishes error classes and degrades locally rather than collapsing.

## Error model

The UI distinguishes: `DOMAIN_UNAVAILABLE`, `STALE_REFERENCE`, `HASH_MISMATCH`, `TRACE_BREAK`, `UNREVIEWED_CANDIDATE`, `INTEGRITY_FAILURE`, and `QUERY_BUDGET_EXCEEDED`. These are never shown as a generic "Error": each class has a distinct banner style and message, and integrity failures are visually distinct from warnings and trace breaks.

## Offline / local failure

If a domain adapter fails, the workspace does not collapse. Degradation is localized: the affected panel or query shows the domain status (e.g. `degraded`), the rest of the workspace keeps working, and the local ResearchComposition is preserved. The top status line shows connection state (`links N`, or `degraded`).

## Unsaved state recovery

Composition and workspace preferences autosave to durable persistence. Visual work is protected against browser crash, tab close, and server restart. Reloading re-mounts the shell and restores the persisted panel layout; the composition working layer is preserved. Autosave never mutates the canonical graph and never auto-promotes links.

## Mutation safety

Canonical scientific operations are append-only. The visual undo/redo journal never rewrites scientific history; pushing a canonical operation to it throws. Composition-local changes are clearly separated from canonical ones, so a user cannot accidentally alter canonical knowledge through the canvas.

## Backend authorization boundary

Read-only queries (even when sent as POST) do not require CSRF; only mutating governance routes (links, hyperlinks, imports, snapshot/composition creation) require a local Host/Origin and the session CSRF token. This keeps read exploration unimpeded while protecting every state-changing operation.
