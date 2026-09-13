# Hypergraph visual model

The Hypergraph is visualized as a real hypergraph, not as a set of ordinary edges. The guiding rule: an n-ary relation `{A, B, C} -> Y` must not be reduced to three pairwise edges without preserving its semantics.

## Junction-node representation

The workspace uses a **junction-node** (incidence) representation: each hyperedge is drawn as a central junction connected to every member. This keeps the n-ary structure explicit and inspectable, scales to many members, and composes cleanly with the ordinary graph. A hull/group representation was considered and rejected for the default view because it obscures individual membership at high density; the junction keeps every member reachable. The original structure always remains inspectable in the hyperedge inspector.

## Hyperedge inspector

For a selected hyperedge the inspector shows:

- members and their roles;
- the outcome / relation semantics;
- provenance (who asserted it, from which source, in which snapshot);
- necessity and sufficiency of members (when present as data);
- known confounders;
- the discriminating test it suggests;
- scientific readiness;
- lineage (supersedes/retractions).

A **candidate** hyperedge is always visually marked as a candidate (dashed, warm color, `CANDIDATE` tag) and is never presented as a proven mechanism.

## Composition-local hyperedges

The user can create composition-local hyperedges inside a ResearchComposition. These live only in the composition and never become canonical. Promoting a local hyperedge to a canonical cross-domain hyperlink is a separate reviewed act (candidate → human review → activation), not a side effect of drawing.
