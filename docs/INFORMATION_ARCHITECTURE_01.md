# INFORMATION_ARCHITECTURE_01

Fecha: 2026-09-15
Misión: arquitectura de información para Terrario; no es diseño visual, plan de componentes ni autorización para modificar producción.

## 1. Executive State

**Estado:** `PASS_WITH_HUMAN_DECISIONS`.

La evidencia permite reemplazar la organización histórica de vistas/paneles por una arquitectura conceptual basada en **intención → tarea → modo → objeto focal → acción → información → evidencia/provenance**. No se elimina ninguna capacidad: la reducción propuesta es de información permanente y de mezcla de modos, no de semántica científica disponible.

`Compose → ExperimentDraft → TrialMatrix → Preregistration → authorized execution` permanece como cadena de identidades diferentes. Theory Hypergraph, Operational Hypergraph, sandbox, Scientific LIVE y replay siguen siendo dominios/modos distintos. Las decisiones sobre cuál contexto debe abrir primero, qué actividad domina y si World2D es el centro siguen siendo humanas; el modelo las tolera sin deformar contratos.

## 2. Evidence Baseline

| Baseline claim | Runtime / contract evidence | Estado |
| --- | --- | --- |
| Compose prepara un `ExperimentDraft` durable | `static/app.js:59-63`; `api.py` `experiment-drafts`; `experiment_composer.py` | FACT / CONFIRMED |
| TrialMatrix materializa ensayos, no ejecuta | `build_trial_matrix`; `execution_performed=False`; persistencia `NON_EXECUTING_TRIAL_MATRIX` | FACT / CONFIRMED |
| Preregistro requiere correspondencia exacta draft/matrix | `preregistration/service.py:_assemble` compara `matrix.draft_hash` con hash del draft | FACT / CONFIRMED |
| Lab y Workspace son superficies distintas | `index.html`/`app.js` vs `workspace/main.js` | FACT / CONFIRMED |
| Hypergraphs distintos | `/api/hypergraph` frente a `/api/operational-hypergraph` | FACT / CONFIRMED |
| Sandbox, LIVE y replay son distintos | `views/world2d.js`, `views/scientific-world2d.js`, CAS/SSE | FACT / CONFIRMED |
| Guía y Compose concuerdan | `TERRARIO_USER_MANUAL.md:103-123` | FACT / CONFIRMED |

Revalidación de pruebas existentes: `test_experiment_composer.py`, `test_worldstream.py`, `test_worldtruth_isolation.py` y `test_sandbox_runtime.py` pasaron (43 tests); las pruebas dirigidas de root autorizado/playback científico y de hiperarista operacional también pasaron en la validación previa. El warning de NVML fue ambiental y no alteró resultados.

**PRECONDITION_DRIFT:** ninguno demostrado. El worktree ya estaba sucio; no se limpia ni se atribuye a esta tarea.

## 3. Canonical Task Model

| Task | Domain objects | Required mode | Primary action | Primary / secondary information | Provenance requirement | Existing surfaces | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Preparar diseño | Hypothesis, ExperimentDraft | CONFIGURE | definir/validar | campos científicos / findings | source artifact, draft hash | Diseño, Compose | IMPLEMENTED |
| Configurar agente | Agent, Configuration | CONFIGURE | evaluar compatibilidad | interfaz/capacidades / descriptor | agent identity | Capabilities, Compose, D2 | IMPLEMENTED |
| Configurar mundo | World, Scenario, Configuration | CONFIGURE | validar/previsualizar | escenario/seeds / diff | scenario hash | World Lab, D2 Studio | IMPLEMENTED |
| Definir matriz | ExperimentDraft, TrialMatrix | CONFIGURE | materializar | dimensiones/celdas / blockers | draft hash, matrix version | Compose | IMPLEMENTED |
| Preregistrar | Preregistration | READY | preparar/revisar/bloquear | commitments / readiness | draft+matrix versions, root | Preregistros, Review Center | IMPLEMENTED |
| Autorizar/ejecutar | authorization, plan, execution | READY/LIVE | request/authorize/command | root/state/plan / resource ceiling | root, revision, plan hash | Scientific Execution | IMPLEMENTED |
| Observar comportamiento | ScientificFrame, World | LIVE | attach/follow | frame/mode / selected view | execution/trial/attempt | World2D Scientific | IMPLEMENTED |
| Observar cognición | CognitiveState, ScientificFrame | LIVE/REPLAY | inspect frame | raw projection / deltas | frame lineage/capability state | Cognitive Observatory | IMPLEMENTED |
| Controlar sandbox LIVE | sandbox session, World | LIVE_SANDBOX | start/pause/step | state/revision / timeline | session/trace ID | World2D, World Lab | IMPLEMENTED |
| Inspeccionar ejecución | execution, trial, attempt | COMPLETED/ANALYSIS | inspect/verify | status/artifacts / details | IDs, hashes, verification | Scientific Execution, Inspector | PARTIAL UI |
| Reproducir | Trace, ScientificFrame | REPLAY | open/seek/compare | cursor/frame / timeline | CAS trace identity | Mundo, World2D, Scientific World2D | IMPLEMENTED |
| Comparar | frames, metrics, runs | COMPARISON | choose comparison | deltas/metric result / history | compared identities | World2D, Run, Analyzer | PARTIAL |
| Analizar métricas | Metric, Analysis | ANALYSIS | select/inspect | result/definition / limitations | metric schema, source run | Metrics, Run, Analyzer | IMPLEMENTED as reading |
| Investigar anomalía | finding/error/trace | DIAGNOSTIC | inspect/resync/verify | error class / transport detail | affected identity/cursor | World2D, Scientific World2D, Execution | IMPLEMENTED |
| Navegar teoría | Theory, Concept, Hyperedge | THEORY | filter/select/path | relation/status / source claim | locator/epistemic status | Hipergrafo, Explorer | IMPLEMENTED |
| Inspeccionar hipótesis | Hypothesis, candidate | THEORY/CONFIGURE | derive/review | mechanism/prediction / rival | source candidate | Diseño, Operational Hypergraph | PARTIAL |
| Conectar hipótesis con experimento | hypothesis, ExperimentDraft | CONFIGURE | set provenance/derive | source ID / mapping findings | semantic ID, draft hash | Diseño → Compose | IMPLEMENTED with gate |
| Inspeccionar evidencia | Evidence, completed execution | ANALYSIS | inspect publication record | classification / supporting artifacts | evidence/trace identity | API/Inspector | PARTIAL UI |
| Inspeccionar provenance | any durable artifact | all modes | open identity/lineage | current object identity / deep audit | IDs/hash/revision/lineage | inspectors/forms/frames | IMPLEMENTED, distributed |
| Diagnosticar infraestructura | transport/session/rendering | DIAGNOSTIC | resync/export/inspect | failure state / technical payload | session/cursor/error scope | World2D, Workspace | IMPLEMENTED |

## 4. Operational Modes — MODE_INFORMATION_MATRIX

| Mode | Focal object | Legitimate actions | L0/L1 information | Context / prohibited information | Authority / confusion risk |
| --- | --- | --- | --- | --- | --- |
| CONFIGURE | draft, world or configuration | edit, validate, derive, preview | object type, validation state, primary fields | selected details; no run/result claim | backend validators; must not resemble authorized execution |
| READY | locked preregistration / planned execution | request, bind authorization, seal, start when legal | root, authorization, state/revision, plan hash | resource/audit detail; no mutable draft editing as if sealed | execution service; lock ≠ authorization |
| LIVE | sandbox session **or** scientific attempt | mode-specific controls or read-only attach | explicit class, state, active identity | selected frame/cognition; replay controls not primary | sandbox controller vs SSE; never exchange them |
| PAUSED | scientific execution or sandbox session | resume/cancel where legal | paused state, active identity, legal actions | timeline/anomaly detail | server state machine; no arbitrary state change |
| COMPLETED | execution/run/attempt | verify, inspect, open playback | terminal classification, identity, artifact availability | deep result/provenance | execution/CAS; completion ≠ evidence |
| REPLAY | trace/frame sequence | seek, compare, inspect | recorded/read-only badge, trace ID, cursor | frame/cognition/metrics | CAS/trace reader; never command runtime |
| ANALYSIS | run, metrics, evidence candidate | inspect, aggregate, review | selected result + interpretation boundary | provenance, raw artifact | analysis APIs; raw result ≠ conclusion |
| COMPARISON | pair/set of frames/runs | choose, align, compare | compared objects and comparison basis | differences/history | read-only; avoid same-identity illusion |
| THEORY | concept, hyperedge, hypothesis | navigate, filter, derive design | epistemic status/source class | source locators/details | theory store; not Operational Hypergraph |
| DIAGNOSTIC | error/session/transport | resync, verify, export diagnostic | error class, affected object, safe recovery | implementation detail | runtime/API; diagnostic data temporarily escalates |

`IDLE`, `CONNECTING`, `RESYNCING`, `LOST` and `TERMINAL` are viewer/transport substates, not substitutes for the scientific execution state machine. `STEPPING` is an action in LIVE_SANDBOX, not a scientific execution state.

## 5. Canonical Object Model

| Object | Canonical identity / owner | Persistence & lifecycle | Human actions | Relevant modes | Current representation |
| --- | --- | --- | --- | --- | --- |
| Agent | A0–A4 + implementation identity / capabilities | registered, not a UI alias | inspect, assess, bind | CONFIGURE, LIVE | Capabilities, Compose, frames |
| World / Scenario | world ID + content hash / registry | definition, preview/materialization | choose, validate, preview | CONFIGURE, sandbox | World Lab, D2, World2D |
| Configuration | typed content hash / D2/world contract | mutable draft → validated version | edit, validate, diff | CONFIGURE | D2 Studio(s) |
| ExperimentDraft | artifact/version/scientific hash / composer | mutable by derivation, durable version | validate, save, derive, review | CONFIGURE | Compose |
| TrialMatrix | matrix/version/hash / composer | durable immutable materialization | build, inspect | CONFIGURE/READY | Compose, Preregistros |
| Preregistration | ID + sealed root / governance | draft → reviewed → locked | prepare, submit, lock, verify | READY | Preregistros, Review Center |
| Trial / Run / Attempt | trial intent / run / attempt IDs / execution | planned → materialized → terminal | inspect, verify | LIVE, COMPLETED, REPLAY | Execution, Run, World2D |
| Trace / Checkpoint | CAS/blob and cursor / runtime | sealed recorded artifact | open, seek, compare | REPLAY, DIAGNOSTIC | Mundo, World2D |
| ScientificFrame | trial identity + frame sequence / observation | transient SSE then durable trace | attach, inspect | LIVE, REPLAY | Scientific World2D |
| CognitiveState | frame-bound projection / observation | frame payload, not universal latent state | inspect/diff | LIVE, REPLAY | Cognitive Observatory |
| Metric / Analysis / Comparison | metric schema / analysis identity / selected set | definitions durable; outputs derived | assess, inspect, compare | ANALYSIS | Metrics, Run, Analyzer |
| Theory / Concept / Hyperedge / Hypothesis | snapshot/node/candidate semantic IDs / theory | source-backed, epistemic lifecycle | navigate, inspect, derive | THEORY, CONFIGURE | Hipergrafo, Design |
| Evidence | publication identity / evidence domain | only after eligible workflow | inspect | ANALYSIS | API, partial UI |

Temporary frontend representations include shell layout, selected panel, `followingLive`, local bookmarks, render queues and unsaved Research Composition state. They must not be presented as scientific authority.

## 6. Information Layer Model

| Layer | Definition | Examples | Exposure policy |
| --- | --- | --- | --- |
| L0 — ORIENTATION | dónde estoy / qué ocurre | context, explicit mode/classification, focused object | persistent per active context |
| L1 — PRIMARY OPERATION | lo necesario para la acción legal actual | controls, validation, execution state, active frame | persistent only in applicable mode |
| L2 — CONTEXT | necesario por selección/estado | selected cell/node/frame/object history | inspector or selection-driven |
| L3 — SCIENTIFIC INSPECTION | explicación científica profunda | cognitive projection, metrics, arms, causal limits | on demand, preserved verbatim |
| L4 — PROVENANCE | identidad, reproducibilidad, audit | IDs, hashes, versions, seeds, lineage, lock | immediately reachable, escalates on integrity risk |
| L5 — DIAGNOSTIC | transport/implementation troubleshooting | SSE state, cursor gaps, renderer errors, debug estimates | diagnostic scope; escalates on failure |

**Exception:** root hash, plan hash, trace identity and mode classification rise to L1 when they gate an action or distinguish LIVE from replay. L4/L5 otherwise must not dominate orientation.

## 7. Contextualization Matrix

| Information permanent today | Current location | Required modes / objects | Safe status | Contract implication / risk |
| --- | --- | --- | --- | --- |
| Full JSON identity panels | Compose, Scientific Execution | selected durable artifact; READY/LIVE | SAFE_CONTEXTUAL | short identity remains L0/L1; full version/hash lineage stays one action away |
| Trial cells (up to 120) | Compose | selected matrix | CONDITIONAL | dimensions, total, blockers and matrix ID remain L1/L2; individual cells contextual |
| Full node record | Hypergraph side inspector | selected concept/hyperedge | SAFE_CONTEXTUAL | preserve selected ID/status/locator access |
| World Truth + Agent View + Observer View | World2D | active frame | MUST_REMAIN_VISIBLE | three views enforce truth/observation separation |
| Sandbox toolbar controls | World2D | LIVE_SANDBOX | MUST_REMAIN_VISIBLE only in mode | hide in preview/replay, never transfer to Scientific LIVE |
| Frame provenance JSON | Scientific World2D | active frame/attempt | CONDITIONAL | compact identity L0/L1; complete payload L4 inspector |
| Cognitive field grid and deltas | Cognitive Observatory | selected current/replayed frame | CONDITIONAL | capability states and raw-vs-derived labeling must remain available |
| SSE/cursor/renderer internals | World2D / Scientific viewer | DIAGNOSTIC or transport fault | SAFE_CONTEXTUAL | automatically escalate on gap/loss/resync |
| Review/package/audit chain | Preregistros | governance/audit | CONDITIONAL | lock/root/decision shown at L1 when sealing; deep chain L4 |
| Workspace global panel switcher | Workspace | preference/navigation | UNKNOWN | evidence does not establish which contexts users need simultaneously |

## 8. Navigation Classification

The baseline is **24 registered surfaces**: 15 static Classic Lab destinations plus 9 Workspace panels. `Preregistros` is dynamically installed by `preregistration.js`; it is a required protocol subflow, recorded below but not falsely counted as one of the original 24.

| Current surface | Classification | Focal object / mode | Rationale |
| --- | --- | --- | --- |
| Inicio | CANONICAL_DESTINATION | orientation | entry/status |
| Manual | CONTEXTUAL_VIEW | task guidance | follows intent, not domain authority |
| Experimentos | CANONICAL_DESTINATION | experiment/run / ANALYSIS | catalog entry |
| Run | DETAIL | selected run / ANALYSIS | requires run selection |
| Mundo | DETAIL | run trace / REPLAY | replay detail |
| World Lab | TOOL | world/config/sandbox | configuration and sandbox tool |
| Capabilities | INSPECTOR | Agent/capability | selection-driven technical/scientific detail |
| Metrics | INSPECTOR | Metric/Observer | selection-driven definition/applicability |
| Compose | CANONICAL_DESTINATION | ExperimentDraft / CONFIGURE | authoring task |
| D2 Studio | TOOL | Configuration / CONFIGURE | validation/diff tool |
| Hipergrafo | CANONICAL_DESTINATION | Theory / THEORY | corpus navigation |
| Diseño experimental | CONTEXTUAL_VIEW | hypothesis/design | theory-to-design bridge |
| Revisión científica | CANONICAL_DESTINATION | review/governance | human decision task |
| Analizador | TOOL | Analysis / ANALYSIS | deterministic analysis tool |
| Configuración | LEGACY_NAVIGATION_CANDIDATE | frontend sandbox state | no runtime authority demonstrated |
| Preregistros (dynamic) | CANONICAL_DESTINATION within protocol | Preregistration / READY | durable governance; no loss permitted |
| Explorer | INSPECTOR | references/worlds | navigation support |
| Operational Hypergraph | CONTEXTUAL_VIEW | operational lineage | distinct from theory graph |
| Scientific Canvas | CONTEXTUAL_VIEW | selected cross-graph slice | selection workspace, not independent domain |
| Inspector | INSPECTOR | selected entity/provenance | context-driven |
| Research Composition | TOOL | local composition | local versioned workspace, not ExperimentDraft |
| World2D | CANONICAL_DESTINATION | World/session/trace | mode-bound world instrument |
| Scientific Execution | CANONICAL_DESTINATION | execution/authorization | governed operational task |
| World2D Scientific | CONTEXTUAL_VIEW | ScientificFrame / LIVE/REPLAY | read-only observation bound to attempt |
| D2 Scientific Studio | TOOL | D2 fixture/protocol | overlap unresolved; retain distinct contract |

## 9. Surface Consolidation Candidates

| Candidate shared context | Current surfaces | Shared object/mode | Contracts that remain distinct | Benefit / risk | Human decision |
| --- | --- | --- | --- | --- | --- |
| Execution Observatory | Scientific Execution + World2D Scientific + Operational Hypergraph | execution/attempt; READY→LIVE→COMPLETED | control, observer, lineage | removes handoff searching; risk of control/read-only confusion | whether execution is a primary activity |
| Protocol & Governance | Compose + Preregistros + Review | ExperimentDraft/TrialMatrix/root; CONFIGURE→READY | draft/matrix/preregistration identities | makes gates legible; risk of implying lock authorizes execution | preferred preparation workflow |
| Knowledge to Design | Hipergrafo + Diseño + capability/metric inspection | theory/hypothesis; THEORY→CONFIGURE | TheoryGraph vs operational graph, agent/metric registries | turns selected source into contextual detail | when theory is used |
| Replay & Analysis | Experimentos + Run + Mundo + Analyzer + Metrics | completed run/trace; REPLAY/ANALYSIS/COMPARISON | replay, metric analysis, evidence | avoids duplicate selection; risk of mistaking replay for live | common comparison task |
| World Instrument | World Lab + World2D sandbox | world/session; CONFIGURE/PREVIEW/LIVE_SANDBOX | draft validation vs runtime session | separates engineering from science; risk if called “execution” | role of World2D |

These are **presentation candidates**, not entity merges or implementation instructions.

## 10. Classic Lab / Scientific Workspace Models

| Model | Advantages | Contract fit | Duplication / mode clarity | Migration cost | Human decision |
| --- | --- | --- | --- | --- | --- |
| A. Separate products | strong isolation | fits sandbox and theory history | navigation handoffs remain | low | whether users work in two applications |
| B. Separate modes | supports mode-specific information | partial: Lab contains multiple modes | can obscure governance/theory | medium | dominant workflow |
| C. Contexts in one application | maps tasks/objects without entity fusion | high conceptually | good if mode badges/invariants retained | medium/high | opening context and priority |
| D. Operational + scientific layers | highlights control versus interpretation | partial: theory/design cross both | risks relegating theory | medium | whether theory is secondary |

**Inference:** C is the most decision-tolerant *conceptual* target because it preserves boundaries while allowing shared navigation. It is not a product/deployment decision and does not select a winner among A–D without human intent.

## 11. WORLD2D_INFORMATION_BOUNDARY

| Responsibility | Belongs to World2D? | Evidence / boundary |
| --- | --- | --- |
| World representation | Yes | truth/agent/observer canvases are a synchronized frame representation |
| Sandbox observation and control | Yes, engineering-only | WorldStream session commands and explicit `ENGINEERING_SANDBOX · NOT EVIDENCE` |
| Scientific observation | Yes, read-only companion | Scientific World2D attaches to attempt and exposes no controls |
| Cognitive inspection | Contextual companion | frame-bound projection; does not become world state or agent input |
| Trace/replay | Yes | trace/CAS seek and compare, read-only |
| Diagnostics | Yes, contextual L5 | transport gaps, resync, renderer export |
| Preregistration/authorization | No | belongs to Protocol & Governance / Execution authority |
| Evidence conclusion | No | a frame/trace is not evidence publication |

`World2D as the center of Terrario` remains `HUMAN_DECISION`; the boundary does not assume it.

## 12. Cognitive Observatory Architecture

| Class | What it may show | Guardrail |
| --- | --- | --- |
| OBSERVATION FACT | `cognitive_state` carried by identified frame; capability labels; raw/projection values | label it frame-bound and capability-scoped |
| DERIVED INTERPRETATION | adjacent-frame deltas for uncertainty, prediction error, memory and updates | UI already labels these `NOT CAUSAL`; only calculate with contiguous same lineage |
| SCIENTIFIC INFERENCE | claims about learning, belief, transfer or competence | never render as observed state; requires analysis/evidence path |

The meaningful focal object is `ScientificFrame`, not an unanchored “mind state.” Follow-live, inspected historical frame and playback must declare which temporal relation they represent. `UNAVAILABLE`, `UNSUPPORTED`, `NON_FINITE`, `MALFORMED` and `NULL` are values with semantic status, not zero or empty visualization.

## 13. EXPERIMENT_DESIGN_INFORMATION_MODEL

```text
THEORY/HYPOTHESIS (source identity)
  → Compose mutable form / validation findings
  → ExperimentDraft durable version + scientific hash
  → TrialMatrix durable version + draft_hash + cells/arms/seeds
  → Preregistration version + reviewed locked root
  → Authorization + sealed execution plan
  → TrialIntent / attempt / ScientificFrame / trace
```

| Phase | Primary information | Frozen / mutable | Mandatory identity access |
| --- | --- | --- | --- |
| Preparation | fields, controls, metric, Observer, seeds, findings | mutable input; derived versions | source hypothesis/design |
| Draft | validation state, scientific diff | durable version; change through derivation | version ID + draft hash |
| Matrix | dimensionality, total, blockers, selected cell | durable materialization | matrix ID/version + `draft_hash` |
| Preregistration | readiness, commitments, review, lock | sealed root after lock | both source versions/hashes + root |
| Execution | legal state/action and plan | server-controlled | root, authorization, plan/revision |

Hash detail is L4 by default, but the specific identity that gates a transition is L1. Relationships remain navigable; neither a TrialMatrix nor lock may be visually represented as a result or an authorization.

## 14. Theory / Hypergraph Architecture

| Node / bridge | Supported status | Information architecture policy |
| --- | --- | --- |
| Theory → Concept/Relation/HyperedgeCandidate | source-backed theory graph | THEORY context; source/epistemic state contextual but recoverable |
| HyperedgeCandidate → Design | supported portfolio bridge | selected candidate can open design/provenance; no inferred experiment |
| Hypothesis → ExperimentDraft | supported provenance/mapping gate | CONFIGURE context; source identity persists |
| Experiment → Preregistration → Attempt → Frame → Trace | operational lineage | Execution Observatory / Operational Hypergraph |
| Completed result → Evidence | gated/partial UI | do not invent closed loop; use evidence APIs only where available |

Theory Hypergraph and Operational Hypergraph may share navigation but never their ontology, status vocabulary or implied truth claim.

## 15. Provenance Architecture

| Tier | Always identifiable | On demand / inspector | Reserved diagnostic |
| --- | --- | --- | --- |
| Essential identity | object kind, active mode, selected durable/run/attempt identity | full IDs, version, revision, hash | transport correlation IDs |
| Reproducibility | seed/classification when action relies on it | scenario/software/observer/metric commitments | raw implementation payload |
| Deep audit | lock/root/plan when transitioning | lineage, review, CAS descriptor, audit chain | renderer/SSE internals |

Identity cannot depend only on a human label. Any hidden L4 information must be reachable from the selected object without reconstructing it manually.

## 16. Error / Anomaly Architecture

| Error class | L0/L1 escalation | Keep separate from |
| --- | --- | --- |
| Integrity failure / preregistration mismatch | affected identity, gate blocked, recovery path | generic form validation |
| SSE disconnect / gap / resync | connection state, last cursor, resync action | scientific result/failure |
| Trace corruption / replay inconsistency | trace ID, integrity state, read-only stop | live runtime control |
| Observer materialization failure | frame/observer scope, explicit fault | agent failure |
| Invalid configuration | field/finding and validation source | execution failure |
| Execution failure | execution/attempt state, failure record | world or observer fault |
| World/agent failure | selected trial/world/agent scope | transport failure |

A fault elevates its relevant L4/L5 details temporarily; it does not collapse all failures into one red “error.”

## 17. HUMAN_DECISION_REGISTER

| HD-ID | Question | Why it matters | Affected architecture | What proceeds / what stays blocked |
| --- | --- | --- | --- | --- |
| HD-01 | ¿Qué debe aparecer primero? | selects default orientation | entry/queue | contexts exist; default remains blocked |
| HD-02 | ¿Qué actividad domina? | prioritizes contexts/actions | all navigation | all modes remain available; ranking blocked |
| HD-03 | ¿World2D es centro, instrumento o diagnóstico? | determines World Instrument prominence | World2D/Observatory | boundary fixed; placement blocked |
| HD-04 | ¿Cuándo se usa teoría? | determines Knowledge context entry | Hypergraph/Design | provenance bridge fixed; visibility priority blocked |
| HD-05 | ¿Cuál comparación es frecuente? | determines Comparison task path | Replay/Analysis | comparison identity rules fixed; default flow blocked |
| HD-06 | ¿Qué variables cognitivas priorizar? | controls L1 versus L3 exposure | Cognitive Observatory | raw/derived separation fixed; ordering blocked |
| HD-07 | ¿Qué debe persistir durante una corrida? | controls L0/L1 density | Execution Observatory | mode/identity remain; content priority blocked |
| HD-08 | ¿D2 Studio(s) deben compartir contexto? | potential presentation consolidation | D2 tools | no deletion; consolidation blocked |

## 18. Stable Core vs Human Decisions

| Stable core | Human-configurable structure | Blocked decision |
| --- | --- | --- |
| identities, domain types, legal transitions, evidence boundaries, provenance access, mode separation | context order, default destination, inspector expansion, selected object focus, L2–L5 visibility preferences | hierarchy of activities, World2D centrality, theory prominence, cognitive priority, D2 consolidation |

This split lets a future interaction architecture change navigation behavior without needing to reinterpret TrialMatrix, live observation or theory provenance.

## 19. Target Information Architecture

```text
Terrario — decision-tolerant conceptual architecture
├─ Orientation & Work Queue            [L0: current task, mode, active object]
├─ Knowledge & Design                  [THEORY / CONFIGURE]
│  ├─ Theory & hypotheses              [concept, hyperedge, source status]
│  ├─ Design preparation               [ExperimentDraft, agent/world/metric context]
│  └─ Protocol & governance            [TrialMatrix, preregistration, review, lock]
├─ Execution Observatory               [READY / LIVE / PAUSED / COMPLETED]
│  ├─ governed control                 [authorization, plan, legal commands]
│  ├─ scientific observation           [ScientificFrame, CognitiveState]
│  └─ operational lineage              [attempt/frame/trace relationship]
├─ World Instrument                    [CONFIGURE / PREVIEW / LIVE_SANDBOX]
│  ├─ world configuration and preview
│  └─ engineering sandbox and its own replay
├─ Replay & Analysis                   [REPLAY / ANALYSIS / COMPARISON]
│  ├─ run/trace playback and comparison
│  └─ metrics, analysis, eligible evidence inspection
└─ Integrity & Diagnostics             [DIAGNOSTIC, cross-context]
   └─ provenance inspector, validation, transport and recovery
```

Contexts are not proposed routes, layout regions, products or visual hierarchy. An object-focused inspector and a provenance access path are cross-context capabilities. The architecture permits co-navigation of related contracts while requiring an explicit mode/classification boundary.

## 20. Current-to-Target Migration Map

| Current | Target context → role | Contract preserved | L0–L5 | Migration risk | Action |
| --- | --- | --- | --- | --- | --- |
| Inicio | Orientation → entry | status/read-only | L0 | low | KEEP |
| Manual | Orientation → contextual help | no authority | L2 | low | RECONTEXTUALIZE |
| Experimentos | Replay & Analysis → catalog | experiment/run IDs | L1/L2 | medium | KEEP |
| Run | Replay & Analysis → selected-run detail | metrics/timeline | L2/L3 | medium | DETAIL_VIEW |
| Mundo | Replay & Analysis → trace detail | replay identity | L1/L2/L4 | high | RECONTEXTUALIZE |
| World Lab | World Instrument → configuration tool | WorldDraft/sandbox | L1–L5 | high | RECONTEXTUALIZE |
| Capabilities | Knowledge & Design → agent inspector | A0–A4 descriptors | L2/L3/L4 | medium | INSPECTOR |
| Metrics | Knowledge & Design / Analysis → metric inspector | registry/applicability | L2/L3/L4 | medium | INSPECTOR |
| Compose | Knowledge & Design → design preparation | ExperimentDraft | L1–L4 | high | KEEP |
| D2 Studio | World Instrument → configuration tool | D2 validation/diff | L1–L5 | high | TOOL |
| Hipergrafo | Knowledge & Design → theory | theory graph/status | L1–L4 | high | KEEP |
| Diseño experimental | Knowledge & Design → hypothesis detail | bridge/provenance | L2–L4 | medium | RECONTEXTUALIZE |
| Revisión científica | Protocol & Governance → review | human decision | L1/L4 | high | KEEP |
| Analizador | Replay & Analysis → analysis tool | deterministic analysis | L1–L4 | medium | TOOL |
| Configuración | Integrity & Diagnostics → local-state detail | no runtime authority | L5 | high | LEGACY_NAVIGATION_CANDIDATE |
| Preregistros dynamic | Protocol & Governance → canonical protocol | root/review/lock | L1–L4 | high | KEEP |
| Explorer | Knowledge & Design → contextual navigator | ReferenceGraph/world ref | L2/L4 | medium | CONSOLIDATE_PRESENTATION |
| Operational Hypergraph | Execution Observatory → operational lineage | typed operational graph | L2–L4 | high | RECONTEXTUALIZE |
| Scientific Canvas | cross-context → selection view | graph slice | L2/L3 | medium | CONTEXTUAL_VIEW |
| Inspector | cross-context → inspector | selected provenance | L2–L4 | medium | CONSOLIDATE_PRESENTATION |
| Research Composition | Knowledge & Design → local research tool | local versioning/noncanonical links | L1–L4 | high | TOOL |
| World2D | World Instrument → mode-bound world tool | sandbox/preview/trace distinction | L0–L5 | high | KEEP |
| Scientific Execution | Execution Observatory → governed control | root/auth/plan/state | L0–L4 | high | KEEP |
| World2D Scientific | Execution Observatory → observation detail | frame/SSE/CAS read-only | L0–L5 | high | RECONTEXTUALIZE |
| D2 Scientific Studio | World Instrument → D2 scientific tool | fixture/protocol | L1–L5 | high | BLOCKED |

## 21. Cognitive Load Reduction Mechanisms

| Mechanism | Existing problem resolved | Scientific safeguard |
| --- | --- | --- |
| Mode-specific actions | live/replay/sandbox controls coexist | expose only legal actions for explicit mode |
| Object-centric inspector | full records are permanently visible | preserve selected object identity and L4 access |
| Progressive disclosure | Compose and World Lab show config/result/audit together | blockers and transition-gating IDs stay L1 |
| Contextual provenance | hashes everywhere obscure task | identity remains reachable and escalates at gate |
| Operation/diagnostic separation | transport details dominate normal work | faults promote diagnostic detail when needed |
| Selection-driven details | graphs/worlds overload unselected detail | do not hide epistemic/mode classification |
| State-aware navigation | historical screen navigation crosses tasks | retain exact object/mode upon movement |
| Focused comparison | analysis/replay selection scattered | compare identities and basis visible |

## 22. Architectural Invariants

1. `LIVE != REPLAY != CONFIGURE != ANALYSIS != DIAGNOSTIC`; mode is explicit and controls remain legal only in their contract.
2. `ENGINEERING_SANDBOX != authorized scientific execution != evidence`.
3. `ExperimentDraft != TrialMatrix != result`; preregistered design is not mutable Compose state.
4. Theory Hypergraph and Operational Hypergraph retain their own type, status and lineage semantics.
5. ScientificFrame preserves atomic identity, cursor, WorldTruth, Agent Observation and Observer View.
6. Derived cognitive deltas remain labeled as derived/non-causal; inference is never rendered as observed state.
7. Observer, agent, world, transport and integrity failures retain distinct classes.
8. Provenance/identity remains recoverable even if no longer permanently displayed.
9. No presentation behavior becomes authority for seed, transition, lock, plan or determinism.
10. Existing durable IDs/hashes/revisions are used; no new scientific identity is invented by navigation.

Evidence: `UI_FORENSIC_AUDIT_01` sections 3–12; `UI_ARCHITECTURE_PRECONDITIONS_01` sections 4–16; execution, World2D and composer contracts cited above.

## 23. Quality Gates

| Gate | Result | Basis |
| --- | --- | --- |
| IA-G0 CONTRACT PRESERVATION | PASS | target maps presentation only; entities/identity unchanged |
| IA-G1 MODE SEPARATION | PASS | explicit mode matrix and World2D boundary |
| IA-G2 OBJECT CLARITY | PASS | every target context has focal object(s) |
| IA-G3 INFORMATION HIERARCHY | PASS | L0–L5 defined with exceptions |
| IA-G4 CONTEXTUALIZATION SAFETY | PASS_WITH_GAPS | candidate matrix exists; user priority and stale-pair UX remain to validate |
| IA-G5 PROVENANCE ACCESS | PASS | cross-context provenance policy and invariant |
| IA-G6 HUMAN-DECISION HONESTY | PASS | eight decisions registered, none inferred |
| IA-G7 MIGRATION TRACEABILITY | PASS | all 24 baseline surfaces plus dynamic preregistration mapped |
| IA-G8 DOMAIN NEUTRALITY | PASS | no domain/model/runtime change proposed |

## 24. Open Risks

- `RISK`: dirty WIP remains broad; future implementation must isolate its own changes.
- `RISK`: Compose can temporarily retain mismatched draft/matrix IDs in frontend state; preregistration fails closed, but specific UX feedback lacks an E2E confirmation.
- `RISK`: D2 Studio and D2 Scientific Studio have unresolved overlap; do not consolidate yet.
- `RISK`: a conceptual context model is not evidence of preferred default navigation.
- `TEST_COVERAGE_GAP`: browser execution of the Compose stale-pair response was not performed in this task.

## 25. Next Valid Objective

`INTERACTION-ARCHITECTURE-01`, constrained by this document, is the next valid objective. It may specify user movement, entry/return behavior and context switching, but must first preserve the invariants and resolve or expose the Human Decision Register rather than selecting preferences silently.

```text
TASK=INFORMATION-ARCHITECTURE-01
BRANCH=experiment/cognitive-live-observatory-01
PRE_HEAD=a9bfb7a585fe20091821f0e1d920a31956001282
POST_HEAD=a9bfb7a585fe20091821f0e1d920a31956001282
WORKTREE_STATUS=DIRTY_PREEXISTING_WIP_PRESERVED

FILES_CREATED=docs/INFORMATION_ARCHITECTURE_01.md
FILES_MODIFIED=NONE

PRECONDITIONS_REVALIDATED=YES
CONTRACT_DRIFT=NONE_DEMONSTRATED
DOMAIN_CONFLICTS=NONE_DEMONSTRATED

CURRENT_SURFACES_MAPPED=24_BASELINE_PLUS_DYNAMIC_PREREGISTRATION_SUBFLOW
TARGET_CONTEXTS_DEFINED=6

HUMAN_DECISIONS_OPEN=HD-01..HD-08
BLOCKING_HUMAN_DECISIONS=DEFAULT_CONTEXT_PRIORITY; WORLD2D_CENTRALITY; THEORY_PRIORITY; D2_CONSOLIDATION

IA_G0=PASS
IA_G1=PASS
IA_G2=PASS
IA_G3=PASS
IA_G4=PASS_WITH_GAPS
IA_G5=PASS
IA_G6=PASS
IA_G7=PASS
IA_G8=PASS

PROTECTED_WIP_STATUS=PREEXISTING_WIP_PRESERVED_NO_WRITES_THIS_TASK

INFORMATION_ARCHITECTURE_STATUS=PASS_WITH_HUMAN_DECISIONS
SAFE_FOR_INTERACTION_ARCHITECTURE=YES
NEXT_VALID_OBJECTIVE=INTERACTION-ARCHITECTURE-01
```
