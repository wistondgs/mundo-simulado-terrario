# World2D browser QA report

This is an engineering-sandbox QA record, not scientific evidence. It records exact browser provenance and observed gaps rather than turning an implementation claim into a pass.

## Browser provenance

| Field | Chromium | Firefox |
|---|---|---|
| Playwright | 1.63.0 | 1.63.0 |
| Browser | Google Chrome for Testing 153.0.8010.12 | Mozilla Firefox 155.0 |
| Executable | `/home/wguti/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome` | `/home/wguti/.cache/ms-playwright/firefox-1543/firefox/firefox` |
| Mode | headless official Playwright build | headless official Playwright build |
| Profile | Playwright Desktop Chrome, DPR 1 | Playwright Desktop Firefox, DPR 1 |
| Host | Linux 6.18.33.2-microsoft-standard-WSL2 x86_64 | same |

The host lacks `libasound2`, `libnss3`, and `libnspr4` runtime libraries required by the managed browsers. No OS package was installed. For these local runs, the exact Debian packages were downloaded and extracted under `/tmp/world2d-browser-libs`, and test commands set `LD_LIBRARY_PATH` to its `usr/lib/x86_64-linux-gnu`. A reproducible system-level alternative is to install `libasound2t64 libnss3 libnspr4` (plus their apt dependencies) with explicit operator approval.

## Real-sandbox coverage

Final regression: **89/89 Playwright passed** with retries disabled (**46 Chromium, 43 Firefox**). Backend final regression was **449 passed, 1 skipped**; frontend unit was **3 passed**. The backend run includes the protected source/historical-artifact hash baseline; H-ADAPT was not executed.

`tests_frontend/e2e/worldstream-live.spec.js` uses the live Lab backend, authenticated session creation, and real SSE: create sandbox → tick 0 → STEP → synchronized three-view tick 1 → START → PAUSE → RESUME → STOP → trace playback. The same suite verifies browser-visible tick identity (`data-view-tick == data-frame-tick`) for all three synchronized views and injects a delayed Agent view into the presentation layer: the UI labels it `STALE`, never `SYNCHRONIZED`.

`tests_frontend/e2e/world2d-live-latency.spec.js` runs ten real command cycles. It validates command acknowledgement, frame publication and presentation; its measured values are in `WORLD2D_PERFORMANCE_REPORT.md`.

## Resilience and interaction QA

- Revision conflict and duplicate command identifiers: backend service test plus authenticated HTTP E2E; one logical transition only.
- Wrong world instance and malformed envelope: reducer unit test rejects them without replacing the current frame.
- Gap/resync, session identity, subscriber and active-session limits, worker failure, and restart-to-`SESSION_LOST`: `tests/test_worldstream.py`.
- WebGL context loss: `tests_frontend/e2e/world2d-renderer-resilience.spec.js` uses real WebGL2, dispatches `webglcontextlost`, and verifies local Canvas2D recovery. The first execution found that a WebGL canvas cannot acquire 2D in Chromium; the renderer now replaces only that presentation canvas, preserves its size and rebinds picking. It also verifies 10k identity picking at DPR 2.
- Keyboard-only: `accessibility.spec.js` focuses and activates new sandbox, STEP, START, PAUSE, RESUME, STOP, trace playback, timeline and next-frame controls without a mouse. Current tick, connection, run state, view statuses, timeline, diff and object-history regions have accessible labels/live state.

## Visual regression

Chromium has deterministic 1440×900 / DPR 1 baselines for the workspace shell, World2D panel and D2 studio in `visual-qa.spec.js-snapshots`. The three existing Chromium baselines initially differed after the intentional World2D session-state/accessibility surface changes and were regenerated using the official browser; the regenerated baseline run passed 3/3. Firefox visual screenshots are intentionally excluded by `playwright.config.js`; cross-browser semantic tests are run there, but Firefox pixel-baseline coverage is **OPEN**, not implied by Chromium coverage.

## Failure record and retry policy

Retries are zero. During hardening, two test-fixture issues were corrected (an Agent channel shape and an existing more-specific timeline aria label). More importantly, the real Chromium WebGL context-loss test exposed and drove the local-canvas recovery fix above. No test was hidden with retries.

## Known open browser QA gaps

- A browser-driven server-process restart / reconnect duration matrix (100 ms, 1 s, and running/paused) is not yet automated. Backend restart behavior is covered, but that is not substituted for browser E2E.
- Two browser contexts attached to the same session and browser-memory soak over thousands of live ticks are not yet automated.
- Firefox visual baselines, World2D-specific hostile-label injection, D2 occlusion/lifecycle UI scenarios, and complete per-panel fault-isolation are not yet covered by this phase's executable suite.

Those gaps remain open in `WORLD2D_CURRENT_GAP_MATRIX.md`; none is counted as acceptance PASS merely because the underlying code has a related unit test.
