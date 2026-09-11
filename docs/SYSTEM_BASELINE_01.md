# SYSTEM-BASELINE-01

## Classification and scope

This checkpoint is `ENGINEERING_CHARACTERIZATION_NOT_EVIDENCE`. It executes short CPU characterization cases only; it does not run a scientific campaign, publish evidence, alter Scientific Review, or execute H-ADAPT.

Baseline source commit: `80d9e00643b551c90148b4158cb48f9eaf1abf92`.

Baseline suite: `317 passed, 1 skipped`. The first sandboxed attempt failed because the mounted repository was read-only and an existing API test writes an ignored `.sandbox` trace. Repeating the unmodified suite with filesystem access passed; this is an environment constraint, not a product regression.

## Protected source manifest

`tests/fixtures/system_baseline_01/protected_manifest.json` records 70 files covering:

- `terrario/agent`;
- `terrario/core`;
- `terrario/world`;
- `terrario/experiment`;
- theory snapshots;
- historical scientific reviews;
- the H-ADAPT configuration and runner.

Protected root digest: `7c281f9bcefeea4a5829d61d9f1886e35300343d80dd421073641ec9248a39aa`.

The manifest is a change detector, not a claim that protected code can never evolve. A future intentional refactor must first demonstrate behavioral parity and then create a new, reviewed baseline version instead of silently updating this fixture.

## Behavioral fixture

`tests/fixtures/system_baseline_01/behavior_fixture.json` contains nine cases:

`D2/D3/D4 × A0_RANDOM/A1_REACTIVE/A4_ADVANCED`.

Each case uses:

- CPU only;
- `world_seed = 1729`;
- `agent_seed = 1001732`;
- four operational steps;
- `scientific_standard` Observer mode;
- checkpoints at steps 2 and 4.

The fixture preserves:

- materialized scenario hash and scheduled changes;
- observation hashes at `t` and `t+1`;
- actions;
- consequences and observer events;
- world-state hashes;
- rule versions;
- termination/truncation state;
- metrics;
- agent class, architecture, parameter count and initial parameter hash;
- checkpoint steps;
- trace types and row counts;
- runtime trace-manifest verification.

Volatile timestamps, temporary paths and time-derived observer run IDs are deliberately excluded. Semantic digest: `2461bd9cdcc629da78f30d777b8fe8022a8ee18bb84244d625c4622526946884`.

D4's scheduled causal change is preserved in the fixture but not triggered by the four-step characterization. This prevents a qualification fixture from becoming an accidental long campaign.

## Observed behavior, not repaired here

The audit identified the following debts. They are intentionally recorded rather than changed during baseline capture:

1. `MetricsCalculator.acquisition_rate` maps insufficient history to `0.0`; this conflates unavailable measurement with a flat effect.
2. `MetricsCalculator.prediction_error_history` defaults a missing signal to `0.0`; the Lab registry is stricter, but the legacy calculator is not.
3. `ExperimentConfig` exposes one seed list and `ExperimentController` derives the agent seed by a fixed offset instead of receiving two explicit materialized seed sets.
4. `ExperimentController._code_hash` records HEAD but not dirty-worktree state or dependency identity.
5. `ExperimentController._save_results` can overwrite the same result filename when the experiment ID and output directory are reused.
6. Observer manifests contain wall-clock creation time and time-derived run IDs, so raw trace bytes are not expected to be reproducible; the fixture compares normalized scientific semantics instead.
7. Observer event storage appends/rebuilds files without the durable transaction protocol planned for LAB-PERSISTENCE-01.
8. `run_experiment_specs` constructs `EvidenceRecord` objects directly from completed runs. The future evidence pipeline must interpose integrity, protocol-conformance, analysis and human-review gates.
9. Sandbox and scientific execution still contain parallel interaction loops. Their unification is deferred until the checked-in characterization passes in shadow mode.

## Rebuild procedure

Rebuilding is an explicit review operation, not a routine test step:

```bash
.venv/bin/python scripts/build_system_baseline.py --root . --output /tmp/system-baseline-candidate
```

The candidate must be diffed against the checked-in fixture. A difference must be explained field by field before fixtures are replaced.

## Gate

SYSTEM-BASELINE-01 passes only when:

- protected hashes match;
- all nine cases match the fixture;
- a repeated identical case is semantically identical;
- trace manifests verify;
- checkpoints and metrics are present;
- D4 scheduled change remains captured;
- full suite passes;
- historical evidence remains unchanged;
- repository is clean after local commits.

Next authorized phase from the master plan: `LAB-PERSISTENCE-01`. It is not implemented by this checkpoint.
