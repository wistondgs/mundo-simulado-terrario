# Preregistration human review workflow

## Review and lock ceremony

1. Create a draft from exact `ExperimentDraft` and `TrialMatrix` versions.
2. Obtain a separate upstream design approval bound to the exact `ExperimentDraft` version and hash.
3. Run readiness; blocking findings cannot be acknowledged.
4. Resolve references and materialize the ten-component candidate root.
5. Inspect the readable review package: question, null/rivals, causal boundary, controls, metrics/endpoints, Observer, seeds/partitions, matrix, analysis, policies, environment, software, exposure findings, hashes, and provenance.
6. Submit that exact root.
7. Record `APPROVE_PREREGISTRATION`, `REQUEST_CHANGES`, or `REJECT` as a separate human action. Accepted warnings are bound individually by `finding_hash`, `rule_id`, and `rule_version`.
8. Run a second explicit lock ceremony. Revalidation and root reconstruction occur before the transactional lock.

No browser field can set actor, state, approval, or lock. A validator never changes governance state. The lock re-checks the expected root/ETag, current bundle version, reconstructed component root, current readiness, the approving decision bound to the same root, the exact warning-acceptance set, review-package availability, current governance state, and the absence of an existing lock, then appends the audit event, attestation, lock row, and state transition in one transaction.

## Amendments and deviations

A locked scientific amendment creates an `AmendmentRecord` and a new draft linked by parent root; only a separately reviewed and locked child can supersede its parent. The superseded parent remains verifiable, immutable, exportable, and historically accessible. Deviations are typed, sealed, and append-only, and never mutate the original bundle.

## Exposure Ledger and holdout integrity

Preview, Seed Browser, and Sandbox record an exposure event before revealing or using a seed; if persistence fails, the reveal fails closed. Status is derived as `UNEXPOSED` only from a verified inventory declaration, otherwise `PREEXPOSED`, `POSTLOCK_EXPOSED`, or `CONTAMINATION_REVIEW_REQUIRED`. A confirmatory seed already inspected is never presented as clean. Exposure never modifies the historical root, never deletes the preregistration, and is append-only.

Seed partitions are `TRAIN`, `DEVELOPMENT`, `EXPLORATORY_TEST`, `CONFIRMATORY_TEST`, `TRANSFER`, and `HOLDOUT`; incompatible overlaps are detected. Holdout opening is recorded. Holdout exposure is not an automatic invalidation, but it forces an explicit contamination state and review.

## Evidence firewall

Preregistration cannot create a `ScientificRun`, `EvidenceRecord`, `EvidenceGraph` edge, or `ScientificConclusion`. The HTTP contract intentionally exposes no execution or evidence-publication endpoint, and the verification report carries `scientific_execution: false` and `evidence_publication: false`. Connecting a locked preregistration to a real scientific execution is a future independent phase.
