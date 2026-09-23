# A2b OEIS control resolution

## Questions required before protocol change

**A. Is OEIS part of the primary scientific calculation?** No.  The primary
calculation is the exhaustive enumeration and the quantities prescribed in
SPEC sections 1--11.  OEIS A001372 is only the external anchor in control
12.4 for the already-computed `tipos_S4` count.

**B. Is it a control or validation?** It is a control/validation, as its
location in SPEC section 12 states.  It is not an input to any A2b quantity.

**C. When is it consulted?** SPEC 12.4 says to consult the source directly,
but does not say that this occurs online or during the solver invocation.
SPEC 12 requires controls before interpreting results.  Therefore this
control is performed by the post-seal adjudicator after the raw-result tree
is committed and before any interpretation or comparison conclusion.

**D. Is network semantically necessary?** No.  The network is merely a way
to obtain the reference.  It is neither an input nor a computational step of
the primary calculation.

**E. Can the OEIS reference reveal an expected scientific result?** Yes.  It
states the target value for the aggregate `tipos_S4` at n=4.  It is therefore
an expected-result reference artifact under the blindness policy and cannot
be supplied to the blind builder or executor.

## Binding resolution

This is Route A (offline reference admissible), with the reference classified
as `POST_SEAL_ONLY`.  No OEIS value, snapshot, URL response, or derived value
is included in the blind package.  The blind solver records only
`controles.oeis_A001372_n4.status = "POST_SEAL_ONLY"`; it does not query,
embed, or compare the reference.  The independent post-seal adjudicator may
consult OEIS A001372 directly after the raw-result commit and before
interpreting the results.

This resolves an execution-time delivery conflict without changing the sealed
SPEC: it preserves the direct-source control and its required timing before
interpretation, while preserving the pre-seal firewall.  No calculation,
enumeration, input byte, expected raw result, or comparison criterion changes.
