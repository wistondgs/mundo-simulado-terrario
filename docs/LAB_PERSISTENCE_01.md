# LAB-PERSISTENCE-01

## Classification

`DURABLE_ENGINEERING_INFRASTRUCTURE_NOT_SCIENTIFIC_EVIDENCE`

This phase changes storage and recovery only. It does not execute a scientific campaign, approve a design, preregister an experiment, create an `ExecutionPlan`, run H-ADAPT, or publish evidence.

## Baseline

- PRE_HEAD: `20431a317e680cc53410ed5bb07ff3d3225aeb06`.
- Recorded checkpoint wording: `322 passed, 1 skipped`.
- Actual collection in this environment: 322 total cases.
- Actual initial result: `321 passed, 1 skipped`.

The historical checkpoint used “322 passed” for what is now confirmed to be 322 collected cases. HEAD and protected files were unchanged when this discrepancy was measured. The phase uses the observed `321 passed, 1 skipped` as its executable baseline and does not rewrite the prior checkpoint.

## Durable layout

Runtime state defaults to:

```text
.terrario/
├── terrario.db
├── blobs/sha256/
├── staging/
├── quarantine/
├── backups/
├── exports/
├── locks/
└── runtime/
```

The directory is ignored by Git. Tests and tools may provide an explicit data root.

SQLite enables WAL, foreign keys, `synchronous=FULL`, and a five-second busy timeout on every repository connection. Schema migrations are numbered, checksummed, transactional, physically idempotent under concurrent startup, and backed up before a future migration changes an existing database.

## Artifact model

`artifacts` contains stable identities. `artifact_versions` contains immutable JSON payloads, separately stored scientific payloads, canonical SHA-256 hashes, parent version/hash, delta, reason, actor, classification and seal state.

Database triggers prohibit updates or deletes of:

- artifact versions;
- artifact state events;
- review decisions;
- job events;
- audit events.

New state is appended to `artifact_state_events`. Scientific content uses canonical UTF-8 JSON and rejects non-finite numbers. UI-only fields can remain in the full payload while being excluded from the scientific payload and hash.

## Integrated Lab artifacts

The former `LabAPI` dictionaries were removed for:

- `WorldDraft`;
- `ExperimentDraft`;
- `TrialMatrix`.

World and experiment drafts now survive a new `LabAPI` process pointed at the same data root. Trial matrices are content-addressed and deduplicated, remain non-executing, and expose `execution_performed: false` after recovery.

The legacy diff endpoint remains an unpersisted preview to preserve its contract. Durable derivation is available at the repository boundary and will be exposed through `/api/v1` in its planned API phase.

## Blob protocol

Blob writes use:

```text
staging file → flush → fsync → SHA-256 → atomic rename → directory fsync → DB manifest
```

An interrupted staging file is moved to quarantine instead of deleted. A complete CAS blob without a committed `blob_manifests` row is detectable through `unregistered_blobs()` and is not a registered scientific artifact.

## Historical references

`HistoricalArtifactIndexer` indexes, but never copies or edits:

- theory snapshot manifests;
- scientific review manifests;
- historical `*_results.json` files.

Historical runs receive `LEGACY_UNVERIFIED_RUN_REFERENCE` and `scientific_evidence_published: false`. Indexing is idempotent and content changes at an existing identity produce a provenance conflict.

Run the read-only indexer with:

```bash
.venv/bin/python scripts/index_lab_history.py --root .
```

The implementation verification used a temporary data root. It found one theory snapshot, one scientific review, and six historical result files without changing them.

## Bundles and backups

Exports contain artifact identity, exact version, scientific payload/hash and a bundle hash. Import validates both hashes before deduplicating or creating a local version. Tampered bundles are rejected.

Backups use SQLite's online backup API after a full WAL checkpoint. Backup validity is tested by opening the result and running `PRAGMA integrity_check`.

## Scientific boundaries

- Persistence cannot turn a draft into an approval.
- Persistence cannot turn a matrix into an execution.
- Historical indexing cannot turn a run into evidence.
- No evidence graph writer was added.
- No GPU path was invoked.
- Theory snapshots and historical evidence remain external immutable references.

## Next gate

`PREREGISTRATION-CORE-01` may begin only after the full suite, protected manifest, historical hashes, static checks and clean-worktree checkpoint pass.

## Final verification

- Focused persistence/API/project/baseline tests: passed.
- Concurrent initialization: five repeated two-thread races passed.
- Independent process race: passed.
- Static Python compilation: passed.
- `git diff --check`: passed.
- Full suite: `336 passed, 1 skipped`.
- Protected characterization: passed inside the full suite.
- Actual-history index against a temporary database: 1 theory snapshot, 1 scientific review, 6 historical runs, database integrity `ok`.
- Scientific execution performed: false.
- Evidence publication performed: false.
