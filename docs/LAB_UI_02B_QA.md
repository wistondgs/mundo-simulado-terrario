# LAB-UI-02B QA

Automated browser QA was attempted with the mandated `agent-browser` flow, but the executable is unavailable in this environment. This is `BLOCKED_ENVIRONMENT`, not a visual PASS.

Fallback verification is reproducible:

1. Start `.venv/bin/python -m terrario.lab.api --root . --port 8765`.
2. Confirm the page contains `WorldBuilder`, `SeedBrowser`, `SandboxTimeline`, and the `ENGINEERING SANDBOX · NOT EVIDENCE` watermark.
3. POST a D2 draft to `/api/worlds/preview` and verify `classification=PREVIEW_ONLY` plus exactly the four permitted Agent View fields.
4. GET `/api/worlds/D2/seeds?values=1,2,3` and verify `WORLD_STRUCTURE_ONLY`, `agent_executed=false`.
5. POST `/api/sandbox`, step once, then run bounded; verify `READY → PAUSED → COMPLETED`, two trace entries, and `scientific_evidence=false`.

This flow passed on 2026-09-10. Contract tests additionally verify visible controls, warnings, timeline selection, identity panel, and shared backend routes. A screenshot/console pass remains pending installation of the optional browser tool.
