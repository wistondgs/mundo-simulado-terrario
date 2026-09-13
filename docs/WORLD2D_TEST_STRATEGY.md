# World2D test strategy

Backend tests cover tick zero, three-view atomicity, `t/t+1`, firewall projection invariance, revision conflict, idempotency, ring gaps, hash-chain corruption, index rebuild/seek, versioned API, and legacy adapter. Frontend unit tests cover contracts, wrong bases, duplicate/out-of-order data, wrong sessions, bounded overflow, and non-causal diffs.

Playwright exercises a real backend, authenticated SSE, live session creation, STEP, synchronized presentation, and revision/idempotency behavior. Existing accessibility and interaction suites remain applicable. Chromium uses the cached official build; Firefox uses Playwright's official build.

Fault/restart scale tests beyond those listed in the traceability matrix are not called PASS without executed evidence.
