# PREREGISTRATION-CORE-01

## Classification and boundary

`HUMAN_GOVERNED_SCIENTIFIC_COMMITMENT_INFRASTRUCTURE`

This phase implements a durable preregistration vertical. It does not create an `ExecutionPlan`, start a worker, execute a trial, infer scientific support, or write `EvidenceGraph`. The HTTP contract intentionally has no execution or evidence-publication endpoint.

## Flow delivered

```text
ExperimentDraft version + TrialMatrix version
→ PreregistrationDraft
→ deterministic readiness report
→ ten content-addressed commitments
→ canonical root manifest
→ sealed candidate bundle
→ separate human review request
→ exact-root human decision
→ separate transactional lock
→ local unsigned attestation
→ integrity verification
```

An upstream design decision is also independent. A string such as `APPROVED` inside an ExperimentDraft is insufficient: `review_requests` and `review_decisions` must contain a human decision bound to the exact ExperimentDraft version and hash.

## Scientific commitments

The domain distinguishes study intent, scientific question, causal versus descriptive design, protocol, controls, metric definitions and implementations, endpoints, Observer channels, world/agent/randomization/replacement seeds, seed partitions, randomization, replication, analysis, stopping, exclusion, failure, storage, environment requirements, observed environment, and software identity.

The codec rejects missing or unknown top-level fields. The API rejects client-supplied `state`, `approved`, `locked`, actor, and creator fields. Non-finite values continue to be rejected by `terrario-canonical-json-v1`.

World seeds and agent seeds are independently hashed. The exact TrialMatrix is pinned by version and scientific hash. Each metric preserves construct, proxy, implementation identity/status, required signals, units, direction, aggregation, domain and construct-validation status. A primary endpoint cannot use a non-implemented metric.

## Validation policy

The versioned policy currently includes deterministic rules for:

- pinned references;
- exact upstream approval;
- causal identification commitments;
- implemented primary endpoints;
- Observer signals;
- seed identity and cross-partition overlaps;
- TrialMatrix cardinality and seed parity;
- analysis and multiplicity;
- stopping, exclusion, and failure handling;
- software/dirty-tree reconstruction;
- Exposure Ledger disclosure;
- unavailable CUDA without fallback;
- the distinction between proxy implementation and construct validation.

Structural, schema, integrity, and reference findings block review preparation. Scientific, exposure, and resource warnings must be accepted individually by `finding_hash`, `rule_id`, and `rule_version`. Readiness never approves a hypothesis and never evaluates whether it is true.

## Commitments and root

The bundle commits ten ordered components:

1. scientific question;
2. causal design;
3. protocol;
4. metrics and endpoints;
5. Observer;
6. seeds, partitions, randomization, and replication;
7. analysis;
8. stopping/exclusion/failure/storage policies;
9. environment and software;
10. validation policy.

Each canonical component is written to CAS and receives a content SHA-256 and CAS SHA-256. The ordered root manifest pins source version/hash pairs, the canonicalization profile, and the explicit `scientific_execution: false` and `evidence_publication: false` boundaries. Its canonical SHA-256 is the bundle root.

UI preferences, actor, timestamps, tabs, zoom, and layout do not enter scientific hashes. A future canonicalization change must use a new profile; historical hashes are not recomputed.

## Review and lock authority

Candidate preparation seals the exact root and review package. Submission creates a separate review request. The human decision references the exact version, root, findings, and accepted warning hashes. Any new version makes the previous decision inapplicable.

Lock performs these checks again, under `BEGIN IMMEDIATE`:

1. expected root / ETag;
2. current bundle version;
3. reconstructed component root;
4. current deterministic readiness;
5. approving decision bound to the same root;
6. exact warning acceptance set;
7. review package availability;
8. current governance state;
9. absence of an existing lock.

It then appends the audit-chain event, attestation, lock row, state transition and audit event in one transaction. An idempotency key with identical content returns the original attestation; reuse with different content is rejected. SQL triggers prohibit update/delete of locks, attestations, components, warning acceptances, exposures, and chain events, and prohibit new artifact versions after lock.

The attestation is explicitly `UNSIGNED_LOCAL_ATTESTATION`. It is tamper-evident within the demonstrated local hash and database model, not a public digital signature.

## Exposure Ledger

Legacy World Preview, Seed Browser, WorldDraft preview, and Sandbox creation write an exposure event before revealing or using the selected world seed. If persistence fails, the requested reveal fails closed. Events form per-world/seed hash chains and cannot be updated or deleted.

Readiness derives `PREEXPOSED`, `POSTLOCK_EXPOSED`, or `CONTAMINATION_REVIEW_REQUIRED`; absence of verifiable historical coverage is never represented as unexposed. Exposure never changes a locked root.

## Amendments and deviations

Post-lock amendment/deviation records are separate sealed artifacts linked to the original root and audit chain. They cannot mutate the preregistration. A scientific amendment must proceed through a new preregistration and complete review; there is no shortcut to supersede or approve through metadata.

## Portable bundles

Exports include the generic artifact bundle, root, all component payloads, review package, local attestation, lineage/audit chain, and an outer portable hash. Validation recomputes the outer hash, artifact/scientific hashes, every component hash, and root hash. Manipulation is reported; bytes are never repaired silently. Imported attestations are marked untrusted for local approval and cannot create a local lock.

## API and local security

`/api/v1` returns a uniform `data/meta` or typed `error` envelope. It exposes session/CSRF initialization, health, status, OpenAPI 3.1, preregistration CRUD-by-version, readiness, review package, review decisions, lock, verification, frozen TrialMatrix, audit chain, exposures, amendments, deviations, and bundle validation/import/export.

Actual HTTP mutations require a local Host, local Origin when present, and session CSRF token. Requests over 1 MiB are rejected. `If-Match` is required for derivation/candidate creation/lock and idempotency is supported for lock. Direct in-process tests omit transport security intentionally and exercise the same service authority.

## CLI and UX

The CLI entry point is:

```bash
.venv/bin/python -m terrario.lab.preregistration --root . <command>
```

It covers list/show/create/derive/validate/readiness/review/lock/verify/diff/exposure/post-lock/export/import/audit. Lock has no `--yes`: it displays root, trials, primary endpoints and warning hashes, then requires `LOCK <12-char-root>` and a reason.

The static Lab gains a separate ES module with overview, builder, seeds, matrix, readiness findings, review, lock ceremony, integrity, Exposure Ledger, lineage, post-lock records, and transfer views. Hash URLs restore the logical section. The module obtains CSRF from the server, uses ETags, does not duplicate scientific validation, and never renders a Run button.

## Verification

- Baseline before this phase: `336 passed, 1 skipped`.
- Baseline before the closing corrections: `349 passed, 1 skipped`.
- Focused preregistration tests: 13 core + 18 advanced passed (31 total).
- Full suite at close: `367 passed, 1 skipped`, 0 unexplained failures/regressions.
- Historical regression (theory snapshot, scientific review, evidence graph, A0–A4, H-ADAPT integrity, persistence, sandbox, World Lab, Experiment Composer): verified by hash/diff/tests; H-ADAPT not executed, integrity only.
- Acceptance-gate invariant audit: hash model, structured verifier, four-layer SQL immutability, six-process concurrency, evidence firewall, amendment cycle, import/export, backup/restore — all PASS with concrete evidence.
- Static Python compilation: passed.
- `git diff --check`: passed.
- Live HTTP HTML/module/health/OpenAPI checks: passed.
- Browser automation: not run because `agent-browser` and Node are absent; no dependency was silently installed.
- CUDA: not invoked for work; PyTorch environment capture reports the known NVML warning and no fallback.
- Scientific execution: false.
- Evidence publication: false.

## Next gate

`SCIENTIFIC-REFERENCE-GRAPH-01` followed by `CROSS-GRAPH-CORE-01`. The browser E2E/accessibility gate for this UX remains an explicit known limitation unless a browser runner is made available. The gate connecting a locked preregistration to a real scientific execution is intentionally deferred until scientific traceability (Reference Graph + Cross-Graph) is structured.
