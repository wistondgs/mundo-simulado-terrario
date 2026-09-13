# Research composition contract

`ResearchComposition` is the durable backend for the future scientific visual workspace. It is a **working layer**, not a source of canonical knowledge: it never modifies the ReferenceGraph, TheoryGraph, Hypergraph, EvidenceGraph, or a Preregistration.

## What a composition references

A composition can pin any `CrossDomainEntityRef`: papers, claims, concepts, theory nodes, hyperedges, hypotheses, scenarios, experiments. References are stored pinned (exact version/snapshot/hash where the domain supports it), so a saved composition is reproducible.

## Composition-local links vs canonical cross-domain links

A composition may carry `local_links` — user-created visual/organizational connections between its members. These are **composition-local**: they live only inside the composition and never become canonical `CrossDomainLink`s. A visual connection on a canvas never alters canonical knowledge. Promoting a local link to a canonical cross-link is a separate, reviewed act (candidate → human review → activation), not a side effect of drawing.

## Versioning

Compositions are versioned (`version`, `parent_composition_id`). Saving again under the same `composition_id` produces a new version; history is preserved. A composition records `title`, `refs`, `local_links`, `notes`, `created_by`, `created_at`.

## Contract for the workspace

The backend provides: save/version a composition, fetch its current state and history, and resolve any member ref back to its sovereign domain for provenance drilldown. The future UI (`SCIENTIFIC-VISUAL-WORKSPACE-01`) builds the canvas on top of this contract; the backend guarantees the composition layer can never write through to a source graph.
