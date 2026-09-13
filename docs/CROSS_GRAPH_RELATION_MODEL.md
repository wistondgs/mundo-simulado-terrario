# Cross-graph relation model

Relation semantics are declared as versioned data in `terrario/lab/crossgraph/relations.py`, never as loose strings scattered through the code.

## RelationSemantics

Every relation type declares:

- `source_domain_constraint` / `target_domain_constraint` — which domains may appear at each end;
- `directionality` — directed (or, where applicable, undirected);
- `inverse_relation` — the named inverse, if any (e.g. `TESTS` ↔ `TESTED_BY`);
- `transitive` / `symmetric` — algebraic properties;
- `scientific_meaning` — a plain-language statement of what the relation asserts;
- `allowed_provenance_classes` — which assertion classes may carry it;
- `acyclic` — whether cycles are forbidden (e.g. `DERIVED_FROM`, `DERIVED_FROM_VERSION`, `SUPERSEDES`);
- `registry_version`.

The registry is validated at link-creation time: an unknown relation, a forbidden source/target domain, or a forbidden assertion class is rejected.

## Initial relations

`DERIVED_FROM`, `DERIVED_FROM_VERSION`, `EXTRACTED_FROM`, `REFERS_TO_CONCEPT`, `CANONICAL_CANDIDATE_FOR`, `MAPS_TO`, `OPERATIONALIZES`, `MOTIVATES`, `INSPIRED_BY`, `TESTS`, `TESTED_BY`, `DISCRIMINATES_BETWEEN`, `USES_SCENARIO`, `INSTANTIATES_WORLD`, `PREREGISTERS`, `PRODUCES`, `HAS_EVIDENCE_RECORD`, `EVIDENCE_RELATES_TO`, `SUPERSEDES`.

## SUPPORTS_THEORY is absent

`SUPPORTS_THEORY` is deliberately not in the registry. Cross-graph never infers that evidence supports a theory; such a relation may only ever be introduced by an explicit EvidenceGraph declaration. Likewise there is no `theory confidence score`, `intelligence score`, `truth score`, or `citation support score` anywhere in the model — only descriptive counts, if a future UI wants them.

## Assertion classes

Links carry an assertion class separating `SOURCE_EXPLICIT`, `USER_ASSERTED`, `ANALYST_ASSERTED`, `SYSTEM_DERIVED`, `MACHINE_CANDIDATE`, `IMPORTED`, and `LEGACY_MAPPING`. A `MACHINE_CANDIDATE` is never promoted automatically to a verified scientific link — it can never be `ACTIVE` (enforced at the domain boundary).

## Link lifecycle

States: `CANDIDATE`, `ACTIVE`, `REJECTED`, `SUPERSEDED`, `RETRACTED`, `STALE_ENDPOINT`, `UNRESOLVED`. There is no destructive delete. Correction is `old link -> new link` through the `supersedes_link_id` lineage; the effective state is resolved by following that lineage to its tip. Candidate links flow through `generation -> validation -> human review -> activation/rejection`.

## Cycle semantics

Cycles are not globally forbidden — they can be legitimate in scientific graphs. But specific relation families are declared acyclic (`DERIVED_FROM`, `DERIVED_FROM_VERSION`, `SUPERSEDES`), and creating a cycle in one of those is rejected at write time. Cycle diagnostics run per relation family.
