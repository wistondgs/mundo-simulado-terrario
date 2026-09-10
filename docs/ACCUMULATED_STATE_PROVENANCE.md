# Accumulated state provenance checkpoint

- Date: 2026-09-10
- PRE_HEAD: `88bf12906bd090501fba1a6ecd8b2eaa98219c76`
- Purpose: neutral consolidation of a coherent working tree accumulated across previously implemented phases.
- Native test command: `.venv/bin/python -m pytest -q`
- Baseline result: `216 passed, 1 skipped`
- Recognized theory snapshot: `theory-f59dbb6d6ee3850c`
- Scientific-review input SHA-256: `fee74e994bc654cac467f403059e2abada2cf5c2cd76a0ff0b44bad984315289`

## State included

Tracked modifications existed in the Lab analyzer, read-only API, and static Lab UI. Untracked additions included the theory graph/ingestion/snapshot layer, hypothesis factory, scientific review, their documentation and tests, builder/QA scripts, the content-addressed theory snapshot, and the frozen scientific-review input/output.

Recognizable functional phases include `THEORY-LAB-INTEGRATION-01`, `HYPOTHESIS-FACTORY-01`, and `SCIENTIFIC-REVIEW-01`. Their combined behavior is covered by the baseline suite and is consolidated together because their dependency closure cannot be separated reproducibly from the accumulated tree.

## Provenance limits

Fine-grained per-file or per-hunk authorship cannot be reconstructed from Git. This checkpoint deliberately does not claim it. The historical boundary and reason for not creating a narrower factory commit are recorded in `SCIENTIFIC_REVIEW_GIT_PROVENANCE.md`.

## Protected state

Ignored `runs/`, historical evidence, A0–A4 implementations, H-ADAPT configuration/protocol, and existing commit history are excluded from the checkpoint and deliberately unmodified. No campaign, training, scientific intervention, or H-ADAPT execution was performed to create this state. No secrets or local `.env` files are included.

This checkpoint records the accumulated state as found and verified; it is not a retroactive assertion of detailed historical authorship.

`git diff --cached --check` reports trailing whitespace in imported CSV snapshot rows. Those bytes are retained deliberately: normalizing source artifacts during consolidation would change their content identity. This is a known source-format condition, not newly introduced code whitespace.
