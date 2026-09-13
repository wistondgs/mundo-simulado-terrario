# Scientific runtime architecture

`ScientificExecutionDispatcher` is the execution plane. It atomically claims a reserved `execution_job`, creates a `run_attempt`, materializes the exact scenario, agent and seeds from the sealed plan, invokes `ExperimentController.run_episode`, seals raw bytes in CAS, and records terminal job/attempt events. It is separate from `LiveSandboxService` and has no EvidenceGraph dependency.
