# Scientific execution QA report

Focused gate coverage includes exact-root rejection, explicit authorization, quota consumption, state transition rejection, command idempotency, raw CAS sealing, event-chain verification, export ZIP validation and forbidden-import firewall.

Recorded closure checks:

- `tests/test_scientific_execution_gate.py`, workspace firewall and project manifest: 10 passed.
- protected-system characterization: 5 passed.
- frontend unit suites: 20 passed.
- Playwright: Chromium 46 and Firefox 43 completed without retained failure artifacts. Chromium used `PLAYWRIGHT_CHROMIUM_PATH=/usr/bin/google-chrome` because the cached headless-shell executable is absent in this environment.

The CUDA warning is environmental and no CUDA path was exercised. The current CPU gate deliberately retains worker-specific checkpoint certification and streaming multipart import as future integration work; neither can be represented as a verified completed scientific run.
