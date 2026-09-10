# Git provenance audit

- Audit date: 2026-09-10
- PRE_HEAD: `88bf12906bd090501fba1a6ecd8b2eaa98219c76`
- HYPOTHESIS-FACTORY-01 seal: `GIT_PROVENANCE_AMBIGUOUS`
- Staging area at audit: empty

The working tree already combined tracked UI/API modifications with an untracked theory integration layer, snapshot, earlier tests, and factory work. `factory.py` is identifiable, but it depends on untracked theory modules from the preceding integration; the API and UI diffs also contain overlapping changes. Committing only factory-named files would not produce a reproducible unit, while committing the dependency closure would falsely attribute pre-existing work to HYPOTHESIS-FACTORY-01.

No files were reset, deleted, or staged. Scientific review work continues as new isolated modules, tests, documentation, and content-addressed review artifacts. A future human-assisted seal should first establish the intended boundary of the prior theory-integration work.
