# Scientific execution QA report

Focused gate coverage includes exact-root rejection, explicit authorization, quota consumption, state transition rejection, command idempotency, raw CAS sealing, event-chain verification, export ZIP validation and forbidden-import firewall.

The focused suite is `tests/test_scientific_execution_gate.py`. Full backend, browser and performance closure values are recorded only after their commands complete; this report intentionally does not infer them from unit coverage.
