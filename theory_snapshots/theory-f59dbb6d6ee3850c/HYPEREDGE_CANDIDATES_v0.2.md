# HYPEREDGE_CANDIDATES_v0.2

## Criterio

Una candidata se conserva sólo como conjunción contrastable. No se dibuja todavía como hiperarista causal. Se auditan diez dimensiones: componentes, resultado, procedencia, atribución, conjunción, necesidad, suficiencia, fuerza, prueba y confusores.

| ID | Componentes | Resultado | Base | Atribución | Conjunción explícita | Necesidad | Suficiencia | Nivel | Prueba discriminante | Confusores | Decisión |
|---|---|---|---|---|---|---|---|---|---|---|---|
| HYPERCAND-01 | prior knowledge; compositionality; learning-to-learn; causal world model | rapid generalization | Lake et al.; Chollet | ANALYST_SYNTHESIS | joint sufficiency not explicit | none individually established necessary | not established | 2–3 | ablations and transfer under matched priors | construct leakage; task-family overlap | RETAIN_AS_TESTABLE_CONJUNCTION |
| HYPERCAND-02 | agent; environment; goal; percept; action; value | universal-intelligence performance | Legg & Hutter | AUTHOR_FORMAL_STRUCTURE | joint tuple explicit | formal framework requires all roles | metric, not empirical sufficiency | 3 | remove/degenerate each element in formal definition | choice of environment distribution | RETAIN_FORMAL_NOT_CAUSAL |
| HYPERCAND-03 | plasticity; stability; retention; transfer | continual learning | Parisi et al. | ANALYST_SYNTHESIS | trade-off explicit, conjunction inferred | no universal necessity proof | not established | 2 | factorial continual-learning benchmark | shared metrics and compute | RETAIN_AS_DESIGN_HYPOTHESIS |
| HYPERCAND-04 | preparation; incubation; illumination; verification | creative achievement | Wallas | AUTHOR_STAGE_MODEL | sequence proposed | stage necessity disputed | not established | 1–2 | process tracing and stage omission | retrospective reconstruction | RETAIN_LOW_CAUSAL_CONFIDENCE |
| HYPERCAND-05 | problem states; actions; preferences; shared memory; coordination | collective intelligence | Heylighen | ANALYST_RECONSTRUCTION | components distributed across argument | none established necessary | not established | 1–2 | controlled removal in collective task | group size, communication bandwidth | RETAIN_REQUIRES_EMPIRICAL_SUPPORT |
| HYPERCAND-06 | iconic representation; categorical representation; sensory grounding | meaningful symbols | Harnad | AUTHOR_CONSTITUTIVE_ARGUMENT | hybrid architecture explicit | symbol grounding requires non-symbolic connection in argument | not empirical sufficiency | 3 | grounding/transfer tests with modality ablations | task labels may leak semantics | RETAIN_CONSTITUTIVE_NOT_CAUSAL |
| HYPERCAND-07 | axioms; proof search; utility; computational resources | certified self-rewrite | Schmidhuber | AUTHOR_FORMAL_CONSTRUCTION | joint formal machinery explicit | required within construction | sufficient only under axioms/resources | 3–4 | formal implementation and resource-bounded counterexamples | axiom correctness; proof search intractability | RETAIN_FORMAL_CONDITIONAL |
| HYPERCAND-08 | perception; world model; memory; cost; actor; configurator | autonomous planning/action | LeCun | AUTHOR_ARCHITECTURE | joint architecture explicit | necessity not proven outside architecture | not established | 2–3 | component ablation with out-of-distribution control | training signal and representation quality | RETAIN_ARCHITECTURAL_HYPOTHESIS |

## Efecto del parche de desarrollo

- Bruner refuerza que **componentes disponibles + coordinación** puede ser distinto de cada componente aislado.
- Tomasello aporta una conjunción explícita para cognición cultural: lectura de intención + motivación compartida + representación dialógica.
- O’Leary–Sloutsky muestra que componentes nominalmente unidos pueden disociarse; por tanto, una lista conjunta no prueba una sola cadena causal.
- Sobel muestra que “acción” necesita especificación: descubrir mediante intervención no equivale a ejecutar cualquier acción.

## Umbral para T3/T5

Sólo pasan a modelado causal fuerte las candidatas con intervención/ablación identificable, resultado operacional y posibilidad de refutación. Las construcciones formales se mantienen en una capa separada de las regularidades empíricas.
