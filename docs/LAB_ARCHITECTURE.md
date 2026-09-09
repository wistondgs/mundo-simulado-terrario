# Terrario Lab Architecture

## Layers

`CORE` owns mutable experimental state and campaign execution. `LAB READ MODEL`
indexes completed artifacts and returns detached immutable records. `LAB API` is a
GET-only transport. `UI` consumes that API and never imports Core. `EXTERNAL
ANALYZER` receives frozen selections and may emit only `DERIVED_ANALYSIS`.
`CORPUS/HYPERGRAPH` accepts structured JSON or YAML derived artifacts, never PDFs.

## Write boundaries

| Layer | May read | May write |
|---|---|---|
| Core | configs, world, agent | runs and RAW evidence |
| LabReadModel | completed artifacts | optional metadata catalog only |
| API/UI | LabReadModel | no experimental data |
| Sandbox | isolated session state | sandbox configuration only |
| Analyzer | frozen request | derived analysis artifact only |

The catalog stores IDs, statuses, hashes, provenance and paths. It does not copy
trace rows. Missing measurements are `NOT_APPLICABLE`; they are never coerced to
zero. Recorded replay points carry `origin: RECORDED`.

## Commands

```bash
.venv/bin/python scripts/run_lab.py --host 127.0.0.1 --port 8765
.venv/bin/python scripts/build_lab_catalog.py --output runs/lab_catalog.json
.venv/bin/python -m pytest
```

The single local service hosts both `/api/*` and the static UI at `/`.
