# Intervention Contract

`InterventionSpec` is versioned and names family, target, operator, parameters,
boundary, duration, scope, capability requirements, resource effect and
randomness policy. Registry entries receive only `CausalRuntime`.

Core entries: C00 explicit control, C01 sham no-op, and `TEST_ENERGY_DELTA`
(test-only). No I01–I12 scientific intervention is implemented. Random
interventions must declare `DEDICATED_STREAM`; none is present in this core.
