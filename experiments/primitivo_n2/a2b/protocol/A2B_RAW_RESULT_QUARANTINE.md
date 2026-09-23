# A2b raw-result quarantine

1. A fresh blind executor verifies the input hashes and preconditions.
2. It runs the one fixed command once and writes only `raw_results/`.
3. It captures process stdout and stderr verbatim.
4. It creates every artifact in `schemas/A2B_OUTPUT_MANIFEST.json`.
5. It computes `raw_hashes.sha256`, excluding that file from its own listing.
6. It validates the mandatory output manifest and instantiates the run manifest.
7. A custodian commits/seals the raw-result tree and records
   `A2B_RAW_RESULTS_COMMIT`.
8. Only after that commit may a separate adjudicator receive comparison or
   reference material.

No reference output, A1/A2 output, comparison table, or Gate B material may
be present in the blind execution workspace before step 8. If a result becomes
visible before sealing, mark the run `INVALID` and quarantine it without
comparison.
