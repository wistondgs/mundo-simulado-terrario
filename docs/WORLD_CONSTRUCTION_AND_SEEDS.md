# World construction and Seed Lab

`WorldDraft` is editable metadata and operational content, distinct from sealed `WorldDefinition`. Validation returns `STRUCTURAL_ERROR`, `WORLD_CONSISTENCY_ERROR`, or nonblocking `SCIENTIFIC_WARNING`. Compilation never repairs invalid values; it canonicalizes a valid draft, preserves provenance, and creates an immutable runtime template plus definition hash.

Generation identity is:

`definition hash + world seed + generator version + materialized structure -> instance hash`.

The supported generator version is `terrario-world-generator/1`; determinism is claimed only within this version. Agent seeds do not participate in preview. Instance manifests expose definition, seed, generator/schema versions, instance hash, structural statistics, and provenance.

Preview generates no agent and performs no learning. Agent View contains only channels, mask, normalized energy, and time fraction. Observer View contains detached WorldTruth. Repeated preview has no repository, agent, evidence, or definition side effects.

Seed Browser is bounded to 256 seeds per request and calculates only world-derived structure: counts, density, reachable-cell estimate, distances and resource distribution. Unsupported opportunity statistics remain `NOT_AVAILABLE`. Degeneracy flags warn but never exclude a future scientific seed automatically.
