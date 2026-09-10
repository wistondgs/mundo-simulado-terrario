# Experiment Design Compiler

The compiler accepts only families approved for experiment design. It emits an immutable `ExperimentDesignDraft` with target rivals, discriminating predictions, interventions, controls, confounders, paired-seed strategy, metrics, preregistration thresholds, falsification rules, stopping conditions, validity gates, capabilities, provenance, cost, and priority.

The validator rejects designs without a null/rival, falsification, controls, observable metrics, provenance, capabilities, or mitigation for critical confounders. Conversion to an executable `ExperimentSpec` additionally requires `APPROVED_FOR_EXECUTION`. Generated portfolio designs remain `GENERATED` and blocked.

Costs are deterministic and label their basis `OBSERVED_BASED` only when runtime and storage observations are both supplied; otherwise they are `ASSUMPTION_BASED`. Priority keeps discriminating power, feasibility, theoretical coverage, identifiability, cost, and an information-gain proxy separate.

Structural dry runs only check wiring, metric/capability availability, and the preserved gate. Their artifact type is `ENGINEERING_DRY_RUN` and `scientific_evidence` is always false.
