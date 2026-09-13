# Scientific runtime QA

The integration test creates a locked preregistration, seals a plan, starts its execution control state, dispatches one claimed trial through the real engine, observes tick 0 and later frames, and asserts raw trace/result CAS artifacts. It intentionally dispatches one trial in-process; production scheduling remains a worker concern, not a browser request loop.
