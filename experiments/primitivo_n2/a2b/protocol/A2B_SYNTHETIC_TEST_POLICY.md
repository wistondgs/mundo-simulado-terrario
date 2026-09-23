# A2b synthetic-test policy

The fresh blind builder may test its implementation without running the real
256-dynamic A2b scientific instance. Permitted tests are parser and schema
tests, canonical-serialization tests, algebraic identities, hand-constructed
toy dynamics outside the sealed enumeration, deterministic replay tests, and
failure-mode tests.

Forbidden tests reproduce the actual sealed scientific instance, enumerate the
256 real dynamics, generate `por_sistema.jsonl` for the sealed SPEC, compare
against expected values, or reveal a real A2b result. The builder stops after
source/test freeze and its executable commit; it does not invoke the fixed
scientific command.
