# Theory Graph Schema

Graph node IDs are typed (`RecordType:original_id`) so claims and audited
relations may preserve the same corpus ID without collision. Every node retains
`record_id`, source artifact, source version, original text, provenance and
epistemic status.

`TheoryGraph` contains sources, claims, RAW concepts, canonical candidates,
relations, ambiguities, conflicts, hyperedges, coverage, integrity records and
review drafts. `ExperimentalEvidenceGraph` separately contains project
hypotheses, experiments, runs, evidence references and recorded metrics.

Paths return every match with relation type, epistemic status and provenance;
the implementation does not designate a path as correct.
