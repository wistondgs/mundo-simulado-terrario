# SCIENTIFIC-REFERENCE-GRAPH-01

## Classification and boundary

`SCIENTIFIC KNOWLEDGE INFRASTRUCTURE + DOCUMENT IDENTITY + PROVENANCE + VERSIONED GRAPH + CLAIM TRACEABILITY + CORPUS BINDING`

This phase implements a durable, versioned scientific reference layer. It records **which documents exist, what they say, which protocols they use, which limitations they report, and where each claim comes from**. It does not write the TheoryGraph, does not write the EvidenceGraph, does not create a hypothesis, does not create an ExperimentDraft, does not preregister, and does not execute a trial.

Hard boundaries, enforced by tests:

- `ScientificReferenceGraph ≠ TheoryGraph ≠ EvidenceGraph`
- `SourceClaim ≠ OurClaim`
- `Reference ≠ Evidence`
- `Citation ≠ ScientificSupport`

No reference enters as truth, no edge implies causality by default, and no automatic extraction is silently promoted to a canonical scientific claim. The domain contains no `TRUE`, `PROVEN`, `CORRECT_THEORY`, or `INTELLIGENCE_SCORE`.

## Three-identity model

The system never collapses three distinct identities:

- **DocumentIdentity** — `SHA-256(file bytes)`, the CAS blob hash. Two different PDFs may be legitimate versions of the same work.
- **BibliographicIdentity** — the work/publication: DOI, or normalized title + authors + year + venue + edition.
- **ReferenceRecordIdentity** — the Terrario-internal record id.

## Flow delivered

```text
corpus package (manifest / records / bibliography / provenance / protocols /
limitations / design principles / version relationships + document bytes)
→ parse → schema validate → file verify → SHA-256 verify → identity resolution
→ duplicate analysis → conflict analysis → ImportPlan
→ (human review on conflict) → stage CAS → transaction → graph snapshot → commit
→ typed nodes/edges with provenance
→ immutable ReferenceGraphSnapshot
→ structured verify_reference_graph
```

A failed import leaves the previous snapshot valid. Quarantine is durable and never auto-repairs significant metadata. Duplicates are detected (SHA-256, DOI, normalized bibliographic identity, title+authors+year) but a candidate is never a destructive merge.

## Graph model

Seventeen node types (`DOCUMENT`, `REFERENCE`, `AUTHOR`, `VENUE`, `SOURCE_CLAIM`, `CONSTRUCT`, `PARADIGM`, `PROTOCOL`, `METHOD`, `METRIC`, `DATASET`, `BENCHMARK`, `ENVIRONMENT`, `LIMITATION`, `REPLICATION`, `CRITIQUE`, `DESIGN_PRINCIPLE`) and twenty-two edge types (`AUTHORED_BY`, `PUBLISHED_IN`, `VERSION_OF`, `CITES`, `REPORTS_CLAIM`, `STUDIES_CONSTRUCT`, `USES_PARADIGM`, `IMPLEMENTS_PROTOCOL`, `USES_METHOD`, `USES_METRIC`, `USES_DATASET`, `EVALUATES_ENVIRONMENT`, `REPORTS_LIMITATION`, `REPLICATES`, `CRITIQUES`, `EXTENDS`, `SUPPLEMENTS`, `CORRECTS`, `METHODOLOGICAL_INSPIRATION`, `TECHNICAL_REFERENCE`, `DIRECT_PARADIGM_ADAPTATION`, `FUTURE_REFERENCE`). Every edge carries an explicit provenance level. `CITES` is distinct from `SUPPORTS` and from `CRITIQUES`; no semantics is invented from bibliographic proximity.

## Content addressing and versioning

Three distinct hashes are never conflated: document bytes hash (CAS), record canonical hash, and snapshot root. Snapshots are immutable: snapshot N → delta → snapshot N+1, each with parent, schema version, node-set hash, edge-set hash, and root hash. Projections are read-only derived views, never new snapshots.

## Real corpus

The phase imports the physically acquired corpus `terrario_scientific_reference_corpus_v0.1` (32 references, 30 documents, 29 PDFs + 29 extracted texts) covering D2 (Spriteworld, CLEVR/CoGenT, IntPhys, Animal-AI, Psychlab, CATER, CausalWorld, Procgen, MiniGrid/BabyAI, Treisman & Gelade, Treisman & Schmidt, Spelke, Kellman & Spelke, Wilcox/Baillargeon, object files) and a broader world-environments set. These enter as data via the manifest/records, never hardcoded. The corpus is reference/methodological provenance, not proof that Terrario replicates cognition.

## Verification

- Full reference-graph suite: core + advanced tests pass.
- Multiprocess import concurrency: single consistent winner, no half-snapshot.
- Crash/fault injection: previous snapshot remains valid.
- Corruption tests (blob byte, DOI, node payload, edge payload, provenance, snapshot root, parent snapshot, version relation): the verifier localizes each.
- Backup/restore: root hashes preserved.
- Performance characterization: real measurements over stepped synthetic scales (see `REFERENCE_GRAPH_TRACEABILITY_MATRIX.md`); no scalability claim is made.

## Next gate

`CROSS-GRAPH-CORE-01` — typed cross-domain identities and traversal across ReferenceGraph, TheoryGraph, Hypergraph, Hypothesis, Scenario, Experiment, and Evidence, without destructive fusion. This phase stores opaque foreign IDs toward those domains as contracts only; it does not implement general cross-domain traversal.
