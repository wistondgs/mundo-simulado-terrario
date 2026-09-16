# Terrario

Terrario is a deterministic experimental world for investigating
agent behavior. It records a typed transition from observation through action,
consequence, learning, and scientific observation. It is not a claim of
intelligence or adaptation by any agent.

## Reproduce

```bash
.venv/bin/python -m pytest
.venv/bin/python main.py verify --steps 10
```

The local environment baseline is recorded in `ENVIRONMENT.md`. General
experiments select `cpu`, `cuda`, or `auto` through `ExperimentConfig.device`.
The H-ADAPT campaign requires CUDA by default and refuses to run while the GPU
is unavailable:

```bash
.venv/bin/python scripts/run_h_adapt_001.py --stage preflight --device cuda
```

Use `--device cpu` only for an explicitly CPU-scoped run. `--device auto`
allows a documented CPU fallback.

## Operational workspace

Open the repository root as an Obsidian vault and begin at
[`knowledge/00 Control/Inicio.md`](knowledge/00%20Control/Inicio.md). It is the
operational source for navigation, prioritization and human decisions; the
technical state remains derived from the versioned manifest and immutable
scientific artifacts. Refresh the generated dashboard after a manifest change:

```bash
./.venv/bin/python scripts/sync_obsidian_vault.py --write
./.venv/bin/python scripts/sync_obsidian_vault.py --check
```

## Containerised dev/test harness

A Docker harness runs the test suites and the lab UI in a disposable environment, so ports, stray
servers and runtime state cannot collide with the host's. It is **not** an execution environment for
science: a preregistration seals `observed_environment` into its bundle root hash and no gate
compares that against the environment that actually runs, so scientific execution stays on the host.

```bash
docker compose -f docker/compose.yaml run --rm pytest
```

See [`docs/DOCKER_HARNESS.md`](docs/DOCKER_HARNESS.md) for the scientific boundary, the design
decisions and the measured deviations from the host.

## Durable Lab artifacts

Terrario Lab stores world drafts, experiment drafts, and non-executing trial
matrices in a local SQLite/CAS data root at `.terrario/`. Scientific artifact
versions are append-only; the directory is runtime state and is not committed.
Historical artifacts can be indexed as immutable references without copying or
publishing them as evidence:

```bash
.venv/bin/python scripts/index_lab_history.py --root .
```
