# Visual QA

Playwright/Chromium is intentionally optional and is not installed in the Core
environment. In environments without a browser, run the UI contract harness:

```bash
.venv/bin/python scripts/run_visual_qa.py
```

Then inspect `http://127.0.0.1:8765` at 1440x900 and 390x844. Check Lab Home,
Experiment Browser, Run Dashboard, Agent/Observer toggle, replay controls,
Hypergraph filters, path results, hyperedge components and Node Inspector.
Agent View must never show object IDs, causal classes, active rules or global
positions. Screenshot differences must not be resolved by hiding scientific
data.
