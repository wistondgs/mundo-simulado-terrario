# TERRARIO_FINAL_DEEP_AUDIT_REPORT

**Audit status:** evidence-based closure report, 2026-09-15.  This report does
not approve a human review, lock a preregistration, authorize an execution, or
advance CL-8.

## Frozen baseline

- Repository: `/home/wis/mundo simulado terrario`
- Branch / pre-head: `experiment/cognitive-live-observatory-01` /
  `a9bfb7a585fe20091821f0e1d920a31956001282`
- Worktree: already dirty before the audit (documented by `git status --short`);
  no reset, clean, restore, stash, branch switch, merge, pull, or push was used.
- Protected WIP hashes at audit start:
  - `scripts/seed_scientific_live_e2e.py`:
    `7059fa7bfb4f176238d723b049dcd95f4f7a339bb8c20bd6f978628148c38e5c`
  - `tests_frontend/e2e/scientific-live.spec.js`:
    `d188fa8406598c19fc834061d9450baf7760e848a02287e497fe44a9a96e7307`

## Evidence obtained

| Subsystem | Evidence | Result |
| --- | --- | --- |
| Physical corpus | TI-0077 is present under the resolved user corpus and SHA-256 is `5dda279009beae358f08b18b2a4374bfbe65f8c9ed773ea0b9b49f9068566022`. | PASS |
| Corpus/hypergraph path portability | Replaced four test-only hard-coded WSL corpus mounts with an environment-or-user-home resolver. `19 passed` across operational hypergraph, hypothesis, draft, and API regressions. | CLOSED |
| SQLite | `.terrario/terrario.db`: `PRAGMA integrity_check=ok`, `foreign_key_check=0`; results/evidence counts are both zero. | PASS |
| CL-7 matrix | `TM-e4cf621e570a2f1dda8b`: two arms, four seed pairs, eight cells, zero contradictory or duplicate pair/arm cells. | PASS |
| CL-7 metric | spec `d27f0600…586c35`; calibration `35c13c1f…4a98bd`; label-independent evaluator. | PASS |
| CL-7 preregistration | `PREREGISTRATION-CL7-20b807bf16cf7ff4` is durable and remains `DRAFT`; request `review-82c0a332b5524f1f9907aa0d5ce2c067` targets the exact draft revision. | HUMAN REVIEW PENDING |
| Backend regression tranche | `48 passed, 1 skipped` in the first 20-file backend tranche; focused CL-7/preregistration regression passes. | PASS |
| Frontend units | `npm run test:unit`: `34 passed`. | PASS |
| Chromium E2E | 52 tests could not launch because the Playwright Chromium executable is absent. No application assertion ran. | ENVIRONMENT GAP |

## Authority and drift

| Stale file / item | Authoritative source | Difference | Action | Human decision |
| --- | --- | --- | --- | --- |
| `knowledge/01 Roadmap/Ruta activa.md` | Current durable artifacts and active CL-7 instruction | It still prioritizes `PREREGISTRATION-CORE-01`, omitting the active CL-7 review request. | Update only through the governance workflow. | YES |
| `project_manifest.json` and generated `knowledge/_generated/Estado tecnico.md` | Manifest is canonical; generated note is a mirror | Both describe the 14-Sep phase graph, not the newer CL-7 closure artifacts. | Human updates manifest intentionally, then regenerates mirror. | YES |
| Snapshot provenance paths | Frozen theory snapshot | Historical absolute paths are embedded in provenance records. | Do not rewrite frozen snapshot; retain as historical provenance. | NO |

## Remaining gaps

| ID | Classification | Evidence / consequence | Exact next action |
| --- | --- | --- | --- |
| GAP-001 | HUMAN_SCIENTIFIC_DECISION_REQUIRED | `PR-REV-001` is the only blocking preregistration finding. | Human reviews `review-82c0a332b5524f1f9907aa0d5ce2c067`; only then prepare review/lock through the existing workflow. |
| GAP-002 | ENVIRONMENT_GAP | Chromium and Firefox Playwright binaries are unavailable; the attempted browser installation did not complete in this run. | Complete `npx playwright install chromium firefox`, then run Chromium and Firefox E2E without rebaselining snapshots automatically. |
| GAP-003 | TECHNICAL_FIX_REQUIRED | `tests_frontend/e2e/scientific-live.spec.js` invokes `.venv/bin/python` directly; it is protected WIP and is not portable to Windows Node. | After explicit permission to change protected WIP, introduce a platform-neutral interpreter resolver and test it on Windows/WSL. |
| GAP-004 | HISTORICAL_ARTIFACT | `.terrario` includes many historic materialized/locked records and backups. | Retain; audit reachability before any retention policy or deletion decision. |

## Gates recomputed from current evidence

`CL-0` through `CL-6`: no newly observed regression in executed focused/current
tests. `CL-7`: **BLOCKED_PENDING_HUMAN_REVIEW**. `CL-8`:
**BLOCKED_DOWNSTREAM**.

## Final verdict

`TECHNICAL_SYSTEM_INTEGRITY: NOT YET FULLY DEMONSTRATED` — browser E2E and the
remaining backend test tranches need completed runs. `SCIENTIFIC_PIPELINE_READY_TO_HUMAN_REVIEW: YES`.
`READY_TO_APPROVE_PR_REV_001: YES`, subject to the human's independent
scientific judgment. `READY_FOR_SCIENTIFIC_EXECUTION: NO` until review,
preregistration lock, and a separate authorization occur.
