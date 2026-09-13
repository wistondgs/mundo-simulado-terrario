# SCIENTIFIC-VISUAL-WORKSPACE-01 — Requirements Traceability Matrix

Final acceptance matrix. Every PASS cites a concrete implementation path, test path, and evidence. States: `PASS`, `PARTIAL`, `FAIL`, `BLOCKED + justification`. No PASS without evidence.

## Architecture gate

| Requirement | Implementation | Test | Evidence | Status |
|---|---|---|---|---|
| FRONTEND_ARCHITECTURE | `static/workspace/` modular ES, no framework | unit tests + E2E launch | modules load, no fatal boot errors | PASS |
| TYPED_CONTRACT | `core/contracts.js` typedefs | `contract.spec.js` (5 tests) | backend responses match typedefs | PASS |
| STATE_MODEL | `core/state.js` separated stores + journal | `state.test.js` | stores separated; journal rejects CANONICAL | PASS |
| WORKSPACE_SHELL | `core/shell.js` multipanel | E2E launch + interactions | panels dock/hide/fullscreen/persist | PASS |

## Graph gate

| Requirement | Implementation | Test | Evidence | Status |
|---|---|---|---|---|
| GRAPH_CANVAS | `render/graph-renderer.js` | E2E canvas + render benchmark | pan/zoom/minimap/select/expand/fit | PASS |
| HYPERGRAPH | junction-node renderer + inspector | unit + E2E | n-ary preserved, not reduced to pairs | PASS |
| GRAPH_SLICE | `main.js` mergeSlice + backend | `graph.test.js` + contract | incremental, deduped merge | PASS |
| PROVENANCE_DRILLDOWN | `views/inspector.js` | E2E inspector | why/source/who/version/snapshot/reviewed | PASS |
| PATH_EXPLORER | CrossGraph `explain_path` via API | contract + backend tests | 4 path kinds distinguished | PASS |
| TRACE_BREAK_UI | `views/d2studio.js` trace-break layer | E2E D2 trace breaks | 3 current D2 breaks visible, not auto-filled | PASS |
| SNAPSHOT_TIME_TRAVEL | snapshot diff + pinned mode | backend snapshot tests | X vs Y without mutation | PASS |

## Composition gate

| Requirement | Implementation | Test | Evidence | Status |
|---|---|---|---|---|
| RESEARCH_COMPOSITION | `views/composition.js` + backend | E2E composition save | members/links/hyperedges/versioning | PASS |
| MANUAL_LINK | composition-local links | E2E + firewall test | local link ≠ canonical cross-link | PASS |
| LOCAL_HYPEREDGE | composition-local hyperedges | composition panel | local only, never canonical | PASS |
| VERSIONING | backend composition versions | E2E save/diff | parent/delta/child, no overwrite | PASS |
| DIFF | composition diff view | E2E diff | added/removed members/links | PASS |
| UNDO_REDO | `core/state.js` CommandJournal | `state.test.js` | UI/COMPOSITION undoable; CANONICAL rejected | PASS |
| RECOVERY | autosave + persisted layout | E2E reload | shell re-mounts, layout restored | PASS |

## D2 / World gate

| Requirement | Implementation | Test | Evidence | Status |
|---|---|---|---|---|
| D2_STUDIO | `views/d2studio.js` | E2E D2 | constructs + reference layer projected | PASS |
| D2_REFERENCE_LAYER | 4-layer toggle | E2E D2 | concepts/precedents/design/breaks | PASS |
| WORLD2D | `views/world2d.js` | E2E World2D | real backend preview, no 2nd simulator | PASS |
| AGENT_VIEW | agent view + mask | E2E World2D | distinctly labelled | PASS |
| OBSERVER_VIEW | observer private truth | E2E World2D | distinctly labelled | PASS |
| WORLD_TRUTH_SEPARATION | truth ≠ agent observation | E2E World2D | 3 views labelled; truth privileged | PASS |
| TIMELINE | scrub/step/playback | E2E World2D | trace playback differentiated | PASS |
| SANDBOX_CONTROL | Start/Step/Pause/Resume/Stop | E2E World2D | ENGINEERING_SANDBOX badge; no exec button | PASS |

## Performance gate

| Requirement | Implementation | Test | Evidence | Status |
|---|---|---|---|---|
| MATERIALIZED_ADJACENCY | migration 6 + `service.rebuild_adjacency_index` | `test_cross_graph_adjacency.py` (7 tests) | rebuildable, stale-on-write, verifiable | PASS |
| INCREMENTAL_LOADING | GraphSlice + cursors + bounded expansion | E2E + merge tests | never loads 100k at once | PASS |
| LARGE_GRAPH_RENDER | canvas renderer | `render-benchmark.spec.js` | 1k + 10k measured | PASS |
| QUERY_PERFORMANCE | indexed adjacency + query cache | benchmark probe | neighborhood ~6ms, cached ~4ms | PASS |
| MAIN_THREAD_RESPONSIVENESS | Web Worker layout + rAF batching | render benchmark | layout off main thread | PASS |

## QA gate

| Requirement | Implementation | Test | Evidence | Status |
|---|---|---|---|---|
| FRONTEND_UNIT_TESTS | `tests_frontend/unit/*.test.js` | `npm run test:unit` | 11 passed | PASS |
| API_CONTRACT_TESTS | `tests_frontend/e2e/contract.spec.js` | Playwright | 5 passed | PASS |
| BROWSER_E2E | `tests_frontend/e2e/*.spec.js` | Playwright + real backend | 24 passed | PASS |
| VISUAL_QA | `visual-qa.spec.js` baselines | Playwright screenshots | shell/world2d/d2 baselines | PASS |
| ACCESSIBILITY_QA | `accessibility.spec.js` | Playwright | labels, focus, non-color, reduced-motion | PASS |
| FULL_BACKEND_TESTS | whole repo | `pytest` | 428 passed, 1 skipped | PASS |

## Firewall gate

| Requirement | Implementation | Test | Evidence | Status |
|---|---|---|---|---|
| REFERENCEGRAPH_INTEGRITY | read-only adapters | `test_workspace_firewall.py` | snapshot unchanged before/after | PASS |
| THEORYGRAPH_INTEGRITY | read-only adapters | firewall test | snapshot unchanged | PASS |
| EVIDENCEGRAPH_INTEGRITY | read-only adapters | firewall test | no evidence publication | PASS |
| PREREGISTRATION_INTEGRITY | read-only | firewall test | locked bundles unchanged | PASS |
| A0_A4_INTEGRITY | full suite | regression | green | PASS |
| H_ADAPT_INTEGRITY | not executed | `test_h_adapt_unproven.py` | UNTESTED_HYPOTHESIS preserved | PASS |
| SCIENTIFIC_EXECUTION_FIREWALL | no exec/evidence route | firewall test | no forbidden route/call | PASS |

## Benchmarks (real, this machine; not universal claims)

**Query path** (100k-link sparse graph): indexed neighborhood ~6 ms; warm pinned query ~4 ms; non-indexed equivalent ~2750 ms.

**Render** (canvas, synthetic visible graphs): 1,000 nodes/999 edges — median render 4.9 ms (~204 FPS), pan 4.7 ms, heap ~2.6 MB; 10,000 nodes/9,999 edges — median render 32.1 ms (~31 FPS), pan 31.1 ms, heap ~5.3 MB.

**Max tested visible nodes**: 10,000. **Max tested visible edges**: 9,999.

## Summary

- PASS: all acceptance-gate requirements across architecture, graph, composition, D2/World, performance, QA, and firewall gates.
- PARTIAL: 0.
- FAIL: 0.
- BLOCKED: 0 — the historical visual-QA parking is resolved: real Playwright browser E2E runs against a live backend.

The workspace closes fully validated, including browser E2E, visual QA, accessibility QA, and render/query benchmarks.
