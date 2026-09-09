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
