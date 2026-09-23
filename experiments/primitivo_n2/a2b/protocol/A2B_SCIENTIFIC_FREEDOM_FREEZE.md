# A2b scientific degrees-of-freedom freeze

The normative mathematics, enumeration, controls, and comparison criteria are
those of the sealed SPEC. They cannot be tuned after a blind result exists.

- Monte Carlo is **disabled**. It is optional in SPEC §11.3 and is not needed
  for the primary exact mathematical adjudication; disabling it removes an
  unnecessary stochastic degree of freedom.
- The blind builder uses CPython 3.12 and the standard library only. Source
  decomposition is implementation-only; semantic output is not.
- Exact quantities use integers/rationals. Information measures use IEEE-754
  binary64 and are serialized as finite values rounded to six decimal places.
- Every ambiguity is recorded. A value-affecting ambiguity unresolved by the
  SPEC makes the scientific run `INVALID`; it is never resolved post hoc.
- There is exactly one scientific command invocation per sealed run identifier.
  Failure is recorded, not repaired and rerun under that identifier.
- Comparison is outside the blind workspace and happens only after raw-result
  sealing.
