# Scientific World Model v1

`terrario.lab.world/v1` is a non-invasive Lab projection over the existing Core. `WorldDefinition` describes a reproducible family; `WorldInstance` binds its scientific hash to a seed. `ScenarioDefinition` adds experimental purpose, observation/action contracts, interventions, metrics, capabilities, confounders, and provenance. `ScenarioVariant` stores an explicit parent hash and delta.

The audit classified the new concepts as follows: create WorldDefinition, ScenarioVariant, DifficultyProfile, and WorldProvenance; adapt the legacy Scenario and rule/event representations; extend the existing observation boundary; adapt existing Action enums and metrics. The legacy operational models remain authoritative for execution and are not replaced.

## Identity policy

Scientific hashes use canonical JSON with sorted keys. World/scenario provenance and configuration UI preferences, lifecycle state, lineage identifiers, and display IDs do not alter scientific identity. Scientific parameters do. World instance identity is `definition_hash + seed`. Provenance retains parent ID/hash and structured scientific delta without overwriting the parent.

## Boundaries

Agent observation permits only raw channels, visibility mask, normalized energy, and optional time fraction. World objects, rules, causal properties, and energy values remain Observer-only. Contracts validate both declarations and projected data. Scientific/Observer views are projections and cannot mutate an episode.

Configuration states are `DRAFT`, `SANDBOX`, `PREREGISTERED`, `LOCKED`, and `ARCHIVED`. Only the first two are editable. Domain methods reject illegal edits and transitions independent of UI.

Difficulty is a complete 14-dimensional vector with explicit `VALUE`, `NOT_APPLICABLE`, or `UNSPECIFIED`; zero is never used as a synonym for not applicable. Presets expand immediately and saved configurations do not depend on their label.

## Legacy registry and D2

D0–D4 are marked implemented only because each YAML parses and is covered by existing world/controller tests. D5–D11 remain unknown/not registered. D2 is projected using the same contracts as D3 and D4. Its movable flag and energy value are World properties, its channel window is primitive observation, and “functional property” remains an analyst interpretation—not an automatically learned representation.

The compatibility check is `GENERALIZES`: D2, D3, and D4 share the same schema with no contract specialization.
