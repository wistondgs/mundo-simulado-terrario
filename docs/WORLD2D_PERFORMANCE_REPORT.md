# World2D performance report

All figures below are local, reproducible engineering measurements from 2026-09-13. They are not scientific evidence and do not describe an experimental result.

## Environment and method

- Host: Linux `6.18.33.2-microsoft-standard-WSL2` x86_64; 11 GiB RAM, 950 GiB free on `/tmp` at trace completion.
- Node `v24.18.1`, Python `3.12.3`, Playwright `1.63.0`; headless official Chromium `153.0.8010.12` and Firefox `155.0`, desktop viewport/DPR `1`.
- `tests_frontend/e2e/world2d-performance.spec.js` uses the production `Canvas2DRenderer` and `WebGL2Renderer`, eight rAF warm-ups, then 36 rAF-paced samples per case. One surface is World Truth; three are World Truth, Agent Observation, and Observer View shapes. Object populations and channel grids are deterministic synthetic instrumentation payloads, not a ScientificRun.
- Table cells are **CPU p50/p95/max ms · sustained FPS**. Chromium also exposes sampled `performance.memory`; Firefox does not, so no heap value is invented. A visual frame is counted as dropped when its rAF interval exceeds 50 ms. `longtask` is unavailable in Firefox here.

## Integrated render matrix

### Chromium

| Entities / views | Canvas2D | WebGL2 | Drops / long tasks (Canvas, WebGL) |
|---|---:|---:|---:|
| 100 / 1 | 0.1 / 0.2 / 0.2 · 60.2 | 0.1 / 0.2 / 0.3 · 59.9 | 0/0, 0/0 |
| 100 / 3 | 0.2 / 0.4 / 0.4 · 59.9 | 0.1 / 0.4 / 0.5 · 60.2 | 0/0, 0/0 |
| 1k / 1 | 0.5 / 0.7 / 0.8 · 59.9 | 0.4 / 0.7 / 1.6 · 60.2 | 0/0, 0/0 |
| 1k / 3 | 1.2 / 1.6 / 4.8 · 59.9 | 0.7 / 1.0 / 1.4 · 59.9 | 0/0, 0/0 |
| 10k / 1 | 6.3 / 24.8 / 29.8 · 59.5 | 4.0 / 7.5 / 13.7 · 60.2 | 0/0, 0/0 |
| 10k / 3 | 15.3 / 19.1 / 23.4 · 37.0 | 8.1 / 15.1 / 27.3 · 59.9 | 0/0, 0/0 |
| 50k / 1 | 55.1 / 69.9 / 176.1 · 17.2 | 26.8 / 35.7 / 40.0 · 36.8 | 36/43, 0/4 |
| 50k / 3 | 138.8 / 189.2 / 421.0 · 6.8 | 57.2 / 100.9 / 113.5 · 17.3 | 36/43, 31/39 |

Chromium heap samples ranged from 10.0 MB at 100–1k to 72.2 MB (Canvas) / 37.3 MB (WebGL) at 50k/three views. This is sampled JS heap only, not GPU memory.

### Firefox

| Entities / views | Canvas2D | WebGL2 | Dropped visual frames (Canvas, WebGL) |
|---|---:|---:|---:|
| 100 / 1 | 1 / 2 / 3 · 58.8 | 0 / 1 / 1 · 62.5 | 0, 0 |
| 100 / 3 | 1 / 3 / 4 · 58.8 | 0 / 1 / 3 · 58.8 | 0, 0 |
| 1k / 1 | 2 / 4 / 5 · 58.8 | 0 / 1 / 1 · 58.8 | 0, 0 |
| 1k / 3 | 3 / 4 / 5 · 58.8 | 1 / 1 / 2 · 58.8 | 0, 0 |
| 10k / 1 | 10 / 11 / 19 · 62.5 | 3 / 4 / 4 · 58.8 | 0, 0 |
| 10k / 3 | 27 / 30 / 32 · 37.0 | 5 / 6 / 9 · 58.8 | 0, 0 |
| 50k / 1 | 57 / 122 / 142 · 17.5 | 18 / 30 / 52 · 55.6 | 36, 1 |
| 50k / 3 | 152 / 179 / 181 · 6.6 | 40 / 128 / 137 · 25.0 | 36, 12 |

The 10k/three-view 30 FPS goal passes with Canvas2D in both browsers (37.0 FPS) and with WebGL2. The 50k/three-view stress workload fails the 30 FPS goal in both browsers; this is an observed limit, not a pass. The maximum tested population is 50k.

## Renderer decision

`Canvas2D` remains the production primary because it has full Agent channel/mask presentation and meets the normal 10k/three-view target. `WebGL2` is the measured accelerated implementation: its CPU cost is lower at density and it has a tested local Canvas fallback, but it is not promoted over the complete observation presentation until visual and keyboard-picking parity for Agent channel/mask rendering is established. Canvas is retained permanently as the compatibility fallback.

## Live command-to-visible latency

`tests_frontend/e2e/world2d-live-latency.spec.js` performed ten real local sandbox cycles in each official browser during the final 89-test regression. A single `node:perf_hooks` monotonic clock brackets Playwright input through HTTP command handling, sandbox update, SSE, client reduction, rAF, and observed DOM state; it does not compare process clocks.

| Browser / operation | n | p50 ms | p95 ms | max ms |
|---|---:|---:|---:|---:|
| Chromium STEP → visible tick | 10 | 57.9 | 67.7 | 68.4 |
| Chromium START → first later visible tick | 10 | 151.7 | 155.3 | 169.3 |
| Chromium PAUSE → visible acknowledgement | 10 | 48.7 | 131.9 | 136.1 |
| Chromium RESUME → next visible tick | 10 | 144.9 | 148.7 | 180.4 |
| Firefox STEP → visible tick | 10 | 191.2 | 231.3 | 268.1 |
| Firefox START → first later visible tick | 10 | 189.6 | 205.0 | 210.9 |
| Firefox PAUSE → visible acknowledgement | 10 | 92.7 | 106.3 | 152.9 |
| Firefox RESUME → next visible tick | 10 | 178.7 | 187.5 | 202.7 |

Chromium meets the p95 <200 ms orientation target for all four measured operations and STEP p50 <75 ms. Firefox misses that target for STEP (p95 231.3 ms) and START (p95 205.0 ms), and misses the STEP p50 orientation target. These are measured browser-specific limits in this environment, not test failures hidden by a permissive assertion. Ten observations are insufficient to report a useful p99.

## Trace-v2 scale and seek

`scripts/worldstream_performance.py` writes structurally complete WorldFrames through the production `TraceArchive`: append-only JSONL, SHA-256 hash chain, SQLite index, `fsync` per record, and 256-tick derived checkpoints. Seek samples include start, quartiles, final tick, and seeded random ticks. This is a synthetic engineering trace, never evidence.

| Records | Write time / rate | Trace / index / checkpoints | Cold seek p50 / p95 / max ms | Warm seek p50 / p95 / max ms | Integrity |
|---:|---:|---:|---:|---:|---|
| 10k (64 seeks) | 65.60 s / 152.45 rec/s | 11,915,575 B / 1,404,928 B / 39 · 31,440 B | 2.69 / 4.26 / 6.26 | 2.63 / 3.65 / 5.34 | valid |
| 100k (128 seeks) | 1,436.60 s / 69.61 rec/s | 120,455,575 B / 14,639,104 B / 390 · 318,558 B | 23.58 / 32.92 / 40.89 | 23.15 / 33.65 / 37.68 | valid; sequence 99,999 |

`TRACE_SEEK_100K` passes the <250 ms p95 objective by a large margin. The lower append rate at 100k is expected from durable per-record `fsync` plus SQLite index work; it is not hidden behind buffered writes.

`TRACE_SEEK_1M = NOT_EXECUTED_RESOURCE_BOUND`. Extrapolating only from the completed 100k run gives approximately 14,366 s (3.99 h) write time, 1.205 GB JSONL, 146 MB SQLite index, and 3.2 MB checkpoints before filesystem/WAL overhead. Disk and RAM were available, but a nearly four-hour durable local write exceeded the accepted final-hardening execution budget. This status is not a PASS.

Browser presentation history is bounded in code (`BoundedFrameHistory`, default 512 frames) and verified by `tests_frontend/unit/worldstream.test.js`; older frames are recovered from the authoritative indexed trace. The completed browser matrix measures heap at bounded workloads but is not a multi-hour live-memory soak. That latter stress remains open rather than being inferred from the bound.

## Reproduction

```text
LD_LIBRARY_PATH=/tmp/world2d-browser-libs/usr/lib/x86_64-linux-gnu \
  node node_modules/@playwright/test/cli.js test tests_frontend/e2e/world2d-performance.spec.js --project=chromium

.venv/bin/python scripts/worldstream_performance.py --records 100000 --samples 128
```
