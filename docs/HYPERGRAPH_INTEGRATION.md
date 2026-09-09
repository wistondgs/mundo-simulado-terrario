# Hypergraph Integration

Terrario ingests structured, derived JSON/YAML artifacts for concepts RAW,
canonical maps, relation audits, hyperedge candidates, source provenance, claims
and coverage. Corpus PDFs and the canonical corpus stay outside Terrario.

The supported traversal is `source -> claim -> concept -> relation -> hyperedge ->
hypothesis -> experiment -> evidence`. Every edge carries provenance and one of
the explicit epistemic statuses. `HYPERCAND` maps to `TESTABLE_CONJUNCTION`; the
adapter rejects attempts to promote it automatically to evidence or fact.

Human scientific review remains the promotion gate between corpus-derived
material, hypotheses and experimental evidence.
