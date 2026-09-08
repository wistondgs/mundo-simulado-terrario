# Terrario

Terrario is a CPU-valid deterministic experimental world for investigating
agent behavior. It records a typed transition from observation through action,
consequence, learning, and scientific observation. It is not a claim of
intelligence or adaptation by any agent.

## Reproduce

```bash
.venv/bin/python -m pytest
.venv/bin/python main.py verify --steps 10
```

The local environment baseline is recorded in `ENVIRONMENT.md`. CUDA is an
external platform concern: experiments select a device explicitly and default
to CPU.
