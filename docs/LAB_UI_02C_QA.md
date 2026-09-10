# LAB-UI-02C QA

## Automated contracts

- `tests/test_lab_capabilities.py`: evidence requirements, `UNKNOWN != MISSING`, reproducible scenario requirements, control compatibility, interface failure, real A0–A4 descriptors, no introspection fiction.
- `tests/test_lab_metrics_observer.py`: implementation/validation separation, signal applicability, directionality, construct/proxy separation, observer profile expansion, leakage invariant, storage estimates.
- `tests/test_experiment_composer.py`: review boundary, ground truth, metric signals, technical interface, immutable parent/upstream, scientific/UI hash policy, explicit controls, exact deterministic matrices, D2/D3/D4 generalization.
- `tests/test_lab_02c_api.py`: API boundaries, sandbox-only runtime inspection, no overwrite, no review bypass, no execution.
- `tests/test_lab_02c_ui_contract.py`: visible components, scientific terminology, server-owned domain decisions, multiplier disclosure, absence of execution controls.

## Browser protocol

Start the dependency-free server with:

```bash
.venv/bin/python -m terrario.lab.api --root . --host 127.0.0.1 --port 8765
```

Then verify page content, navigation, browser console, capability cell inspection, metric details, observer estimate, ExperimentDraft validation, and TrialMatrix construction. `agent-browser` is preferred; if unavailable, the environment limitation must be reported and API/static HTTP smoke checks retained as evidence rather than claiming visual QA.

## Scientific invariants

- Observer verbosity does not widen agent input.
- Runtime inspection remains `ENGINEERING_SANDBOX` and non-evidence.
- Composer cannot approve or execute.
- Trial Matrix contains intents, not runs.
- Historical evidence and protected runtime paths are compared against the pre-phase commit before closure.
