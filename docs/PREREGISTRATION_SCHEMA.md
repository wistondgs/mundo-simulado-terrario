# Preregistration schema

`terrario.lab.preregistration/v1` is an immutable scientific commitment assembled from exact `ExperimentDraft` and `TrialMatrix` versions. Its domain types live in `terrario/lab/preregistration/domain.py`; lossless decoding lives in `terrario/lab/persistence/codecs.py`.

## Domain model

Every first-class concept is a frozen dataclass, not a generic dictionary. The typed contracts are:

- `PreregistrationDraft` — the full scientific commitment under construction.
- `PreregistrationBundle` / `ComponentDescriptor` — the sealed, content-addressed result.
- `ProtocolSnapshot` — exact identities of every scientific dependency.
- `AnalysisPlan` — the frozen statistical/analytical commitment.
- `RandomizationPlan`, `SeedCommitment`, `SeedPartition`.
- `EndpointCommitment`, `ControlCommitment`, `MetricCommitment`, `ObserverCommitment`, `ObserverChannelCommitment`.
- `EnvironmentRequirement`, `ObservedEnvironment`, `SoftwareManifest`.
- `ExclusionPolicy`/`ExclusionRule`, `FailurePolicy`/`FailureRule`, `StoppingRule`.
- `ReviewDecision`, `ExposureRecord`, `DeviationRecord`, `AmendmentRecord`, `PreregistrationAttestation`.

The schema separates scientific question, causal design, protocol, controls, metrics, endpoints, Observer, four seed classes, partitions, randomization, replication, analysis, stopping, exclusions, failures, storage, required environment, observed environment, and software.

## ProtocolSnapshot

`ProtocolSnapshot` pins the exact identities of the scientific dependencies: `ExperimentDraft` version + hash, `TrialMatrix` version + hash, scenario id + hash, compiled `world_definition_hash`, `observation_contract_hash`, `action_contract_hash`, `interventions_hash`, variant ids, difficulty fingerprint, agent ids plus per-agent `agent_identity_hashes`, controls, step limit, repetitions, termination semantics, and device requirement. Live references such as `latest`, `current`, `active`, and `default` are prohibited; only exact content hashes are committed.

## AnalysisPlan

`AnalysisPlan` freezes mode, comparisons, transformations, grouping variables, aggregation, effect measure, uncertainty reporting, optional statistical method, multiplicity policy, missing-data policy, sensitivity analyses, and interpretation boundary. Endpoint roles are `PRIMARY`, `SECONDARY`, `DIAGNOSTIC`, `EXPLORATORY`. `DESCRIPTIVE_ONLY` is supported explicitly; p-values are never required.

## Closed enums and field rejection

Enums are closed (`StudyIntent`, `CausalMode`, `EndpointRole`, `Partition`, `PreregistrationState`, `ReviewDecisionValue`, `ExposureKind`, `ExposureStatus`, `DeviationType`). Unknown top-level and nested scientific fields are rejected by the codec and by `_reject_unknown` in the service, so a client cannot smuggle execution hints (for example a `python` key inside `analysis`). UI preferences remain outside `scientific_payload` and never enter a scientific hash.

## State machine

State progression is `DRAFT → READY_FOR_REVIEW → REVIEW_IN_PROGRESS → REVIEWED → PREREGISTERED_LOCKED`; locked records may become `SUPERSEDED` or `WITHDRAWN`, without deletion. Invalid transitions raise `INVALID_PREREGISTRATION_TRANSITION` via `assert_transition`. A `SUPERSEDED` preregistration remains historically immutable and cryptographically verifiable; supersession is a governance lineage event, not an invalidation of the historical root.
