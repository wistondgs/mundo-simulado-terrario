# External Analyzer

`ExternalAnalyzerInput` contains a frozen hypothesis specification, protocol and
version, evidence manifest, metrics, selected traces, forensic cases and
provenance. Plugins implement `ExternalAnalyzerPlugin`; no provider is bundled.

Results contain findings, anomalies, alternative explanations, methodological
concerns, confidence and requested follow-up experiments. The registry accepts
only results whose artifact type is `DERIVED_ANALYSIS`.

An analyzer cannot receive mutable WorldState, control an agent, change a world,
edit a protocol lock, overwrite historical runs, mutate RAW evidence, or publish
directly into the hypergraph as fact.
