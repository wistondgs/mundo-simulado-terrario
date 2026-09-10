# LAB-UI-02B execution-path audit

| Path | Entrypoint | Config/seed | World creation | Runner | Trace/persistence | Evidence side effect | Classification |
|---|---|---|---|---|---|---|---|
| Standard experiment | `ExperimentController.run` | `ExperimentConfig`, world + agent offsets | legacy YAML + `materialize_scenario` | `ExperimentController` | `ScientificObserver`, run directory | eligible for experiment records | scientific/legacy |
| H-ADAPT | `run_h_adapt_001.py` | locked protocol, paired seeds | scientific + transfer scenarios | adaptation campaign | evidence manifests/checkpoints | explicit scientific evidence | scientific, blocked CUDA |
| Lab replay | read-only API | recorded run ID/step | none | none | reads historical traces | none | recorded/read-only |
| Old UI sandbox | browser-local controls | UI step | none | none | none | none | placeholder |
| World preview 02B | `/api/worlds/{id}/preview` | definition + world seed | `generate_instance` | none | none | impossible by dependency graph | `PREVIEW_ONLY` |
| Engineering sandbox 02B | `/api/sandbox` | `SandboxExecutionSpec`, distinct world/agent seeds | immutable compiled definition | `SandboxService` | `.sandbox/`, atomic classified trace | rejected by `EvidenceFirewall`; no evidence writer imported | `ENGINEERING_SANDBOX` |

RNGs already present include Python-adjacent orchestration, NumPy world materialization, Torch agent initialization/policy generators, per-step `RNGManager`, and separate campaign seed offsets. Therefore 02B does not claim one universal seed. World preview uses only `world_seed`; sandbox additionally declares `agent_seed`. A future run-level randomization seed remains separate.

The scientific runner was not wrapped because it couples to `ScientificObserver`, checkpoint and evidence-oriented persistence. The sandbox instead reuses only operational primitives: world materialization/state, Physics, rules, scheduler, observation boundary, and the existing exact agent factory.
