# Engineering Sandbox Execution

The 02B sandbox accepts only `ENGINEERING_SANDBOX`. `SCIENTIFIC` requests fail in the domain before a run exists. `SandboxExecutionSpec` is not and cannot convert to `ExperimentSpec`.

Runs use an explicit server-side lifecycle: `CREATED → VALIDATED → READY → RUNNING ↔ PAUSED → COMPLETED/TERMINATED`, with terminal `FAILED` and `INVALIDATED`. Every session owns separate world, agent, scheduler, RNG context and timeline. Restart creates a new ID linked through provenance.

Traces use `terrario.sandbox.trace/v1` and carry the sandbox classification, `scientific_evidence: false`, config/world/instance hashes, separate world and agent seeds, agent identity, observations, actions, Observer truth, events, termination, and schema version. Agent observations never contain Observer truth.

Storage is atomic under ignored `.sandbox/`. Incomplete sessions remain explicitly incomplete. The sandbox imports no EvidenceGraph or scientific result writer. `EvidenceFirewall` rejects any attempt to register a non-scientific artifact and also refuses scientific writes because the sandbox process has no scientific writer.

CPU, dimensions, object count, step count, trace namespace, seed range, and seed-population bounds are explicit. H-ADAPT, campaigns, Experiment Composer and approval are outside this layer.
