# D2 Visual Studio

The D2 Scientific Studio is a specialized D2 view projected over the general model. It never hardcodes scientific knowledge; it projects existing data.

## What it shows

When present as data: Object, Property, Identity, Binding, Persistence, Invariance, Occlusion, Generalisation, Transfer, and Representation Probe. These are projected from the reference graph and the TheoryGraph (where mapped); they are not an obligatory ontology.

## D2 test family

Test matrices are shown when available: property discrimination, binding, persistence, individuation, property constancy, occluded retention, combinatorial generalisation, distractor resistance, partial observability, transfer, representation probes, and controls. This list is data-driven, not a fixed schema.

## D2 reference layer

The user can toggle between four layers:

- **scientific concepts** — D2 constructs as projected from the corpus;
- **reference precedents** — the D2 references (Treisman, Spelke, CLEVR, etc.) with their constructs;
- **Terrario design** — the D2 scenario/world design in Terrario;
- **trace breaks** — the first-class trace-break registry.

This makes it possible to see, for example, `Treisman -> feature binding -> missing TheoryGraph mapping` without inventing the mapping: the trace break is shown, not filled.

## Trace breaks as first-class UI

The three current D2 trace breaks are visible: the Treisman feature-binding break (no canonical TheoryGraph concept), the SCI-D2-008 missing source claim, and the scenario-trace break. Each shows where the trace ends, which domain/identity/relation is missing, and its resolution state. They are never auto-filled.
