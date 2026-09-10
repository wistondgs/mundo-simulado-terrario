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

## Executed verification

- Full suite: `316 passed, 1 skipped`.
- Protected-path diff against `e34bf99b9a2f0a18ec8dc34101876cc73eda0e39`: clean.
- Python compile check for Lab and 02C tests: pass.
- Server smoke test at `127.0.0.1:8765`: HTML and JavaScript returned 200 with all three views.
- API smoke: 15 capabilities across A0–A4; D2/A0 execution-compatible; 7 metrics; `FULL_DEBUG` storage response labeled `ESTIMATE`; Composer returned `ExperimentDraft / REVIEW_BLOCKED / scientific_execution=false`; Trial Matrix returned exactly 16 blocked intents and `execution_performed=false`.
- Automated visual/console QA: `BLOCKED_ENVIRONMENT` because `agent-browser` is not installed (`command not found`). No screenshot or console-clean claim is made. Static, HTTP, API, and contract-test checks passed as the explicit fallback.
