# UI_ARCHITECTURE_PRECONDITIONS_01

Fecha: 2026-09-15  
Objetivo: reconciliación contractual previa a cualquier rediseño. Este documento no modifica ni autoriza cambios de interfaz, dominio, runtime ni datos científicos.

## 1. Executive State

**Resultado:** `PASS_WITH_FINDINGS`. La relación `Compose ↔ TrialMatrix` está determinada por código ejecutable, persistencia y pruebas. No hay conflicto de dominio: `Compose` es la superficie/controlador de preparación; su objeto durable es `ExperimentDraft`; `TrialMatrix` es una materialización durable, no ejecutante, derivada del payload científico del draft. El preregistro exige que la matriz esté ligada al hash del `ExperimentDraft` exacto.

La auditoría previa contenía un error objetivo ya corregido: la guía actual sí describe Compose, TrialMatrix y el handoff a preregistro. Persisten decisiones humanas sobre prioridad y arquitectura de información. Por ello `REDESIGN_SAFE_TO_START=PARTIAL`: se puede iniciar únicamente el futuro gate de arquitectura de información bajo los límites de este documento; no un rediseño ni una simplificación de contratos.

## 2. Repository Evidence

| Campo | Evidencia observada |
| --- | --- |
| Repository root | `/mnt/wsl/PHYSICALDRIVE2p3/home/wis/mundo simulado terrario` |
| Branch / PRE_HEAD | `experiment/cognitive-live-observatory-01` / `a9bfb7a585fe20091821f0e1d920a31956001282` |
| Worktree | Sucio antes de esta tarea: WIP rastreado y no rastreado en dominio, frontend, tests, docs y artefactos. No interfiere con documentación de reconciliación; se preserva. |
| Entradas | Lab clásico: `terrario/lab/static/index.html` + `app.js`; Workspace: `static/workspace/index.html` + `main.js`; servidor: `terrario/lab/api.py`. |
| Persistencia | `artifact_versions` mantiene `version_id`, tipo, hash científico, payload y lineage; unicidad por `(kind, scientific_hash)` (`persistence/migrations.py`, `store.py`). |
| WIP protegido | `scripts/seed_scientific_live_e2e.py` y `tests_frontend/e2e/scientific-live.spec.js` estaban modificados antes de esta tarea. No se leyeron para editar ni se escribieron. Hashes observados al cierre: `e8134f861b5e9d013b9c33e3d3db5f7dd073fcae`, `cafe0e2084f4de1e2748812162fe362fb949b43e`. |

FACT: no hubo checkout, cambio de rama, limpieza ni modificación de producción. El único contenido creado/actualizado por esta tarea son los dos documentos de auditoría.

## 3. Audit Verification Matrix

| Audit finding | Evidence sampled | Verified | Contradiction | Notes |
| --- | --- | ---: | ---: | --- |
| Lab y Workspace son superficies distintas | `static/index.html`, `workspace/main.js:199-215` | CONFIRMED | No | 15 vistas clásicas frente a 9 paneles montados por Workspace. |
| Compose crea diseño, no run | `api.py` POST `experiment-drafts*`; `experiment_composer.py`; `test_lab_02c_api.py` | CONFIRMED | No | Respuestas declaran `scientific_execution=False`; no hay ruta execute de Compose. |
| TrialMatrix no ejecuta | `api.py` POST `trial-matrices/build`; `build_trial_matrix`; pruebas 02c | CONFIRMED | No | `execution_performed=False`; las celdas son intenciones. |
| Draft y matriz llegan al preregistro | `preregistration/service.py:_assemble`; handoff E2E | CONFIRMED | No | Exige dos `version_id` de tipos exactos y la pertenencia hash. |
| Guía discrepa con Compose | `docs/TERRARIO_USER_MANUAL.md:103-123` | CONTRADICTED | Sí, auditoría previa | La guía actual describe el flujo correcto; se corrigió sólo ese hecho en `UI_FORENSIC_AUDIT_01`. |
| Theory Hypergraph y Operational Hypergraph no son equivalentes | `/api/hypergraph`, `/api/operational-hypergraph`, prueba de hiperarista operacional | CONFIRMED | No | El primero expresa corpus/estatus; el segundo lineage operacional. |
| Sandbox, LIVE y replay son modos distintos | `world2d.js`, `scientific-world2d.js`, `execution/runtime.py`, pruebas WorldStream | CONFIRMED | No | Scientific World2D es read-only; playback es CAS terminal. |
| ScientificFrame conserva vistas separadas | `execution/runtime.py:ScientificFrame` | CONFIRMED | No | `world_truth`, `agent_observation`, `observer_view`, identidad y cursor son atómicos. |
| Sobrecarga por montaje simultáneo | `workspace/main.js:199-215` | CONFIRMED | No | Es un hecho de topología; la prioridad humana no puede inferirse. |

## 4. Compose Contract

`Compose` no es una entidad de dominio única. Es la vista clásica **Lab · Experiments · Compose** y su controlador (`index.html:15`, `app.js:59-63`) que construye un payload. Su entidad durable es `ExperimentDraft` (`experiment_composer.py`).

| Aspecto | Contrato verificado |
| --- | --- |
| Domain role | Preparar y validar un diseño experimental antes de revisión, preregistro o ejecución. |
| Identity | `draft_id` humano + `version_id` durable + hash de `scientific_payload`; preferencias UI no cambian este hash. |
| Inputs | escenario/hash, variantes, agente(s), controles y contraste, métrica/Observer, seeds, repeticiones, límite, dispositivo, proveniencia e hipótesis opcional. |
| Validation / state | `validate_draft` produce findings; estados `DRAFT`, `INCOMPLETE`, `READY_FOR_REVIEW`, `REVIEW_BLOCKED`, `PREREGISTRATION_READY`. Revisión upstream no se autoeleva. |
| Persistence | `POST /api/experiment-drafts` crea `ExperimentDraft`, clasificación `SCIENTIFIC_DESIGN_DRAFT`; sobrescritura silenciosa rechazada. |
| Consumers | review request, preregistration y, de modo indirecto, planificación de ejecución tras lock/autorización. |
| Runtime | No inicia ejecución, no produce evidencia y no autoriza. |
| Scenario / agent / configuration | Fija hashes de escenario, agentes/interfaz, controles, seeds, métricas y observer; deriva versiones en vez de mutar el objeto fuente. |
| UI / documentation | Compose expone validar, guardar durable y crear matriz; la guía secciones 7–8 describe el mismo camino. |

FACT: `POST /api/experiment-drafts/validate` no persiste; `POST /api/experiment-drafts` persiste. Son pasos con lifetime distinto.

## 5. TrialMatrix Contract

| Aspecto | Contrato verificado |
| --- | --- |
| Domain role | Expansión reproducible del diseño a `TrialIntent` no ejecutante. |
| Identity | `matrix_id=TM-<hash>`; `version_id` durable; hash científico de payload sin warnings/flag no científico; `draft_hash` liga la matriz al diseño. |
| Generation | `build_trial_matrix(draft, blockers, threshold)`; endpoint persiste clasificación `NON_EXECUTING_TRIAL_MATRIX` y deduplica por hash. |
| Dimensionalidad normal | `variants × (agents + controls) × world_seeds × agent_seeds × repetitions`; cada celda contiene condición, seeds, métrica, Observer, estado/bloqueadores. |
| Dimensionalidad CL-7 | Para `hypothesis_mapping`, exactamente brazos `PLANNER_PRESERVED` y `PLANNER_ABLATED`, cada par de seeds una vez por brazo; no producto factorial artificial. |
| Invariantes | semillas explícitas; celdas completas; cardinalidad consistente; configuración de brazo inmutable; fingerprint de estado inicial; hash semántico orden-independiente en matriz pareada. |
| Runtime | `execution_performed=False`; `READY_FOR_FUTURE_EXECUTION` o `BLOCKED` no equivalen a un run. |
| Preregistration | El servicio exige versiones de `ExperimentDraft`/`TrialMatrix` y falla cerrado si `matrix.draft_hash != experiment.scientific_hash`. Valida identidad, cardinalidad, no ejecución y consistencia de seeds. |
| Analysis / export | Fija la unidad/celdas y se incorpora como referencia versionada/hash en bundle portable de preregistro; no es análisis ni evidencia. |
| UI | Compose muestra multiplicadores y celdas; el Builder de preregistro recupera IDs durables desde `sessionStorage`. |

## 6. Compose ↔ TrialMatrix Relationship

### Comparación contractual

| Property | Compose | TrialMatrix |
| --- | --- | --- |
| Domain role | Superficie de authoring/validación; produce `ExperimentDraft` | Materialización de intenciones de ensayo del payload del draft |
| Persistent identity | La vista no; `ExperimentDraft` sí | Sí, `matrix_id`/`version_id`/hash |
| Authoritative representation | `ExperimentDraft.scientific_payload` en backend | `TrialMatrix` persistida en backend |
| Created when | Validate es efímero; Save crea el draft durable | Build materializa el producto de un draft payload |
| Mutable when | Cambios científicos requieren derivación/nueva versión | No se edita; se regenera desde nuevo diseño y se deduplica si idéntica |
| Consumed by | revisión humana y preregistro | preregistro, plan y conteo de intents |
| Scientific meaning | Contrato de comparación experimental | Espacio explícito de comparaciones/replicaciones posibles |
| UI exposure | Formulario clásico | Tabla/celdas clásicas; ID entregado a preregistro |
| Runtime role | Ninguno directo | Ninguno directo; antecedente de intentos sellados |
| Preregistration relation | Debe ser versión durable exacta | Debe pertenecer por `draft_hash` a esa versión exacta |
| Analysis relation | Declara métricas/observer/contrastes | Fija unidades, seeds y cardinalidad; no analiza |

**Clasificación demostrada:** `COMPOSE_PRODUCES_TRIAL_MATRIX`, con la precisión necesaria: la UI puede llamar ambos endpoints desde el mismo payload de formulario; la relación autoritativa se vuelve verificable sólo entre `ExperimentDraft` durable y `TrialMatrix` durable mediante `draft_hash` en `_assemble`.

```text
mutable Compose form
 ├─ validate → findings (efímero; nunca run)
 ├─ save → ExperimentDraft version + scientific_hash
 └─ build → TrialMatrix version + draft_hash
                         │
preregistration._assemble ── requires matrix.draft_hash == experiment.scientific_hash
                         │
locked preregistration root → explicit authorization → sealed plan → TrialIntent/attempt
```

## 7. Contract / Documentation Drift Analysis

| Layer | Evidencia | Clasificación |
| --- | --- | --- |
| Guía | `TERRARIO_USER_MANUAL.md` explica Validate/Save/Build, IDs exactos y el hecho de que diseño/matriz no ejecutan | FACT: coherente con dominio actual |
| Lab clásico | Botones llaman endpoints separados; guarda IDs en `sessionStorage`; abre Builder | FACT: coherente con guía |
| Dominio/API | Produce los dos artefactos, persiste, impone hashes y no ejecuta | FACT: autoritativo |
| Tests | 02c cubre no ejecución/durabilidad; E2E cubre handoff de IDs exactos; core preregistro cubre lock/integridad | FACT: cobertura parcial pero relevante |

**DOCUMENTATION_DRIFT corregido:** la afirmación de la auditoría previa sobre ausencia de Compose en la guía era `STALE/CONTRADICTED`, no una discrepancia viva.

**IMPLEMENTATION_GAP:** Compose permite guardar un draft, editar el formulario y construir luego una matriz distinta; su `sessionStorage` puede entonces contener dos IDs que no pertenecen entre sí. Esto no es conflicto de contrato ni fuga de runtime: preregistro rechaza el par por hash. Falta una prueba E2E dirigida que demuestre la explicación/presentación del rechazo y, por tanto, no se debe prometer que la UI prevenga esa combinación.

**CONTRACT_CONFLICTS=NONE_DEMONSTRATED.**

## 8. UI_OPERATIONAL_STATE_MODEL

Las filas son máquinas diferentes; no son un único estado global.

| Máquina / State | Entry → Exit | Allowed actions | Required information | Forbidden actions | Authority |
| --- | --- | --- | --- | --- | --- |
| Experiment: `DRAFT/INCOMPLETE/READY_FOR_REVIEW/REVIEW_BLOCKED/PREREGISTRATION_READY` | formulario/validación → nuevo draft, revisión o preregistro | validar, persistir, derivar, solicitar revisión cuando aplique | findings, hash, estado, proveniencia | ejecutar o aprobar automáticamente | `validate_draft`, ArtifactStore, review service |
| Execution: `REQUESTED → VALIDATING → AUTHORIZED → PLANNED → READY` | root exacto + autorización/plan → `RUNNING` o cancelación | request, bind, seal, cancel donde sea legal | root, authorization, revision, plan hash | Start sin READY; evidencia | `execution/domain.py`, `service.py` |
| Execution: `RUNNING/PAUSING/PAUSED/STOPPING/RECOVERY_REQUIRED` | comando legal/lease → terminal o recuperación | pause/resume/cancel según transición | execution ID, revision, lease/state | inventar estado, reejecutar sin plan | servidor de ejecución |
| Execution terminal: `COMPLETED/FAILED/CANCELLED/ABORTED` | complete/fail/cancel → terminal | verificar, inspeccionar, reproducir playback | artefactos, integrity report, classification | comandos de runtime | servidor/CAS |
| Sandbox viewer: `PREVIEW/LIVE_SANDBOX/PAUSED/STEPPING/REPLAY` | crear sesión/comando/abrir trace → cierre | controles sandbox y seek según modo | sesión, revision, seed, trace | tratarlo como ensayo científico | WorldStream backend |
| Scientific viewer: `IDLE/CONNECTING/LIVE/RESYNCING/LOST/TERMINAL/PLAYBACK` | attach/SSE/snapshot/CAS → disconnect | attach, resync, inspect, follow, playback, seek | execution/trial/attempt IDs, frame cursor, provenance, artifact state | start/step/pause/resume/reset/seed/intervention | snapshot/SSE/CAS; el panel es read-only |
| Presentation: `THEORY/ANALYSIS/COMPARISON/DIAGNOSTIC` | selección de vista/objeto → otra selección | filtrar, inspeccionar, comparar, buscar paths | identidad y clasificación del objeto seleccionado | inferir evidencia o mutar runtime | frontend sobre APIs de lectura |

Transiciones críticas: `READY --START(server command)--> RUNNING`; `LIVE --TERMINAL event--> TERMINAL --openPlayback(CAS)--> PLAYBACK`; `ExperimentDraft durable + matching TrialMatrix durable --preregistration assemble--> preregistration candidate`. `IDLE`, `CONFIGURE`, `THEORY`, `ANALYSIS`, `COMPARISON` y `DIAGNOSTIC` son modos de presentación/flujo, no estados que la máquina de ejecución pueda aceptar.

## 9. Classic Lab Responsibility Map

| Vista | Objeto / datos | Acciones y lifecycle | Dominio / modo |
| --- | --- | --- | --- |
| Inicio / Manual | snapshot, guía | orientar/navegar | presentación |
| Experimentos / Run / Mundo | experimento, run, timeline, replay | seleccionar/inspeccionar/replay | lectura histórica/análisis |
| World Lab | WorldDraft, seed, sandbox session | validar, preview, crear/controlar sandbox | configuración + sandbox ingeniería |
| Capabilities / Metrics | A0–A4, métrica, Observer | inspeccionar compatibilidad/estimación | configuración/análisis |
| Compose | ExperimentDraft, TrialMatrix | validar, guardar, materializar, pedir revisión | diseño/preparación |
| D2 Studio | configuración D2/diff | validar/diff | configuración no ejecutante |
| Hipergrafo / Diseño / Revisión / Analizador | teoría, candidatos, portfolio, review | explorar, derivar, revisar | teoría/análisis/gobernanza |
| Configuración | estado local/sandbox UI | inspeccionar controles locales | diagnóstico; no autoridad de runtime demostrada |

## 10. Scientific Workspace Responsibility Map

| Panel | Objeto / datos | Acciones y lifecycle | Dominio / modo |
| --- | --- | --- | --- |
| Explorer | ReferenceGraph, mundos | abrir/seleccionar | teoría/contexto |
| Operational Hypergraph | cadena diseño→preregistro→intento→frame→trace | navegar/inspeccionar | lineage operacional |
| Scientific Canvas | cross-graph slice/layout | seleccionar/filtrar | exploración |
| Inspector | nodo/provenance | inspeccionar identidad | contexto/auditoría |
| Research Composition | composición cross-graph | componer versión local | análisis/configuración; no ExperimentComposer |
| World2D | preview, sandbox, trace | sandbox commands, playback | ingeniería/replay |
| Scientific Execution | execution/root/authorization/plan | request, authorize, start/pause/resume/cancel, verify | operación científica gobernada |
| World2D Scientific | ScientificFrame, SSE, CAS trace | attach/resync/inspect/follow/playback | observación read-only/replay |
| D2 Scientific Studio | protocolo/fixture D2 | inspeccionar/validar | configuración/análisis |

## 11. Cross-Surface Capability Matrix

| Capability | Classic Lab | Scientific Workspace | Shared contract | Duplicate? | Distinct semantics? |
| --- | --- | --- | --- | --- | --- |
| Theory graph | Hypergraph | Explorer/Canvas/Operational Hypergraph | lectura/provenance, no mismo grafo | No | Sí: teoría vs lineage operacional |
| Experiment authoring | Compose | No ExperimentDraft form observado | ExperimentDraft / TrialMatrix APIs | No | Sí |
| Preregistration | Builder clásico y review center | consume root en Execution | versiones/hash/root | Complementario | Sí |
| World observation | Mundo/World Lab | World2D/Scientific World2D | worlds/traces, pero distintos transportes | No | Sí: replay/sandbox/scientific |
| Execution control | sandbox sólo | Scientific Execution | ninguno entre sandbox y scientific command | No | Sí |
| D2 configuration | D2 Studio | D2 Scientific Studio | D2 contracts/fixture | PARTIAL | Aún no resoluble como duplicación |
| Provenance | detalles de Lab | Inspector/frame provenance | artifact/version/hash | Compartido | Sí, presentación contextual posible |

## 12. Information Criticality Model

| Nivel | Información / ámbito | Justificación |
| --- | --- | --- |
| P0 — ALWAYS REQUIRED | modo inequívoco; estado/acción autorizada; identidad activa de execution/trial/attempt cuando se actúa | Evita controlar o interpretar el objeto incorrecto. |
| P1 — MODE REQUIRED | root/authorization/plan hash en ejecución; cursor/terminal/CAS en LIVE/replay; session revision/seed en sandbox | Sólo imprescindible para ese modo, pero no opcional dentro de él. |
| P2 — CONTEXT REQUIRED | detalle del nodo, celda, run, agente, mundo, finding seleccionado | Debe aparecer al seleccionar su objeto, no permanentemente. |
| P3 — SCIENTIFIC DETAIL | métricas, Observer channels, brazos, fingerprints, CognitiveState, comparaciones y límites interpretativos | Necesaria para lectura profunda, no para toda navegación. |
| P4 — PROVENANCE / AUDIT | version IDs, hashes, lineage, review decision, lock, CAS descriptor, seeds, software/scenario identities | Debe ser recuperable y copiable; puede ser contextual. |
| P5 — DIAGNOSTIC | SSE connection, error técnico, layout/debug, estimates y sandbox local | Para recuperación/soporte, sin autoridad científica. |
| P6 — REDUNDANT PRESENTATION | Sólo si la misma identidad/estado se demuestra accesible desde otro componente con mismo alcance | `P6` no autoriza remover: no se ha demostrado equivalencia para D2, dos grafos ni mundos. |

## 13. Canonical Object Model

| Object | Canonical identity | Owner domain | Lifecycle / actions | Related objects | Current UI surfaces |
| --- | --- | --- | --- | --- | --- |
| Agent | A0–A4 ID + implementation identity | capabilities/execution | inspect, compatibility, bind | Trial, config, frame | Lab Capabilities, Compose, Workspace |
| World / Scenario | ID + content hash | world registry | configure, preview, materialize | configuration, run, seeds | World Lab, D2, World2D |
| Configuration | typed payload + hash | D2/world contracts | validate, derive, preview | scenario, draft | D2 Studio(s), World Lab |
| ExperimentDraft | artifact/version/scientific hash | experiment composer | validate, persist, derive, review | TrialMatrix, preregistration | Compose/review |
| TrialMatrix / Trial | version/hash / trial ID | composer/execution planning | materialize, validate, plan | draft, seeds, attempt | Compose, preregistration, Execution |
| Preregistration | ID + bundle root hash | governance | assemble, review, lock, verify | draft, matrix, authorization | Builder/review, Execution input |
| Run / Attempt / Trace | run/attempt ID + CAS descriptor | runtime/CAS | execute, seal, replay, verify | execution, frames | Run/Mundo, World2D, Scientific World2D |
| ScientificFrame / CognitiveState | identity + sequence/cursor | execution observation | stream, inspect, replay | attempt, trace | Scientific World2D |
| Metric / Analysis | metric ID/schema/hash | metrics/analysis | applicability, aggregate, inspect | draft, matrix, results | Metrics, Compose, Analyzer |
| Theory / Concept / Hyperedge / Hypothesis | snapshot/node/candidate ID | theory | navigate, derive design | experiment provenance | Hypergraph, Design, Workspace graph |
| Evidence | evidence identity/provenance | evidence publication | publish only after gates | completed result | API; UI is partial |

## 14. Human Decision Impact Matrix

| Human decision still needed | Affected views | Affected contracts | Can proceed without answer? | Consequence / blocked decision |
| --- | --- | --- | --- | --- |
| Primer objetivo al abrir Terrario | Home, Workspace shell, Manual | ninguno | Sí | No definir landing/default hierarchy. |
| Función dominante (observar/configurar/ejecutar/analizar) | todas, sobre todo bottom panels | ninguno | Sí | No promover u ocultar superficies. |
| Rol central de World2D | World Lab, World2D, Scientific World2D | sandbox vs scientific boundary | Sí | No fusionar controles ni escoger default. |
| Cinco variables cognitivas prioritarias | Cognitive Observatory | frame projection labels | Sí | No priorizar/colapsar indicadores. |
| Información visible durante Run | Run, World2D, Execution | P0/P1 presentation | Sí | No decidir densidad por defecto. |
| Comparaciones frecuentes | Canvas, Analyzer, World2D | read models only | Sí | No crear navegación/agrupación nueva. |
| Cuándo usar el hipergrafo | Theory/Operational graph/Design | graph separation | Sí | No consolidar grafos. |
| Vista más costosa/confusa y causa | toda UI | ninguna | Sí | No eliminar/mover elementos por intuición. |

## 15. Future UI Invariants

| Clasificación | Invariante derivado |
| --- | --- |
| DOMAIN_INVARIANT | Compose no es ejecución; `ExperimentDraft` y `TrialMatrix` no autorizan run ni evidencia. |
| DOMAIN_INVARIANT | TrialMatrix conserva dimensionalidad, celdas, blockers y, cuando aplica, pares/brazos/fingerprint; no es una lista plana intercambiable. |
| SCIENTIFIC_INVARIANT | A0–A4, métricas, estado epistemológico y señales no disponibles no se pueden mejorar o inventar por presentación. |
| SCIENTIFIC_INVARIANT | WorldTruth, Agent Observation y Observer View siguen separados; error del observador no pasa a ser error del agente. |
| RUNTIME_INVARIANT | Transiciones de ejecución y comandos permanecen autorizados por servidor, con revisión/lease/idempotencia. |
| RUNTIME_INVARIANT | LIVE científico no se confunde con sandbox ni playback; Scientific World2D no recibe controles de runtime. |
| PROVENANCE_INVARIANT | draft/matrix/root/plan/attempt/frame/trace mantienen identidad y lineage recuperables; preregistro exige correspondencia hash exacta. |
| PROVENANCE_INVARIANT | CAS terminal es la fuente de playback; la memoria de dispatcher no es autoritativa. |
| UX_SAFETY_INVARIANT | Todo cambio de modo presenta su clasificación operacional; `P4` puede ser contextual, nunca irrecuperable. |
| UX_SAFETY_INVARIANT | Teoría y Operational Hypergraph conservan etiquetas que impiden tratarlos como el mismo grafo. |

## 16. Safe Redesign Boundary

| Área | Semáforo | Justificación de contrato |
| --- | --- | --- |
| Etiquetas, tipografía, espaciado y agrupación visual de información ya equivalente | GREEN | No cambia entidad, acción, identidad ni transición si se mantienen P0–P5 accesibles. |
| Inspector contextual y visibilidad progresiva de P2–P5 | YELLOW | Debe preservar selección, hashes, provenance y modo activo; requiere pruebas de recuperación. |
| Shell/switcher de Workspace y orden de paneles | YELLOW | Nueve paneles se montan simultáneamente, pero la prioridad humana no está decidida. |
| Compose y handoff a preregistro | YELLOW | Preservar tres acciones, version IDs y pertenencia `draft_hash`; cubrir el caso de IDs no coincidentes. |
| World Lab / World2D | YELLOW | Puede variar presentación sólo si sandbox/preview/replay siguen inequívocos y sus controles no cruzan a scientific runtime. |
| D2 Studio clásico vs D2 Scientific Studio | RED | Solapamiento parcial no resuelto; podría ocultar contratos de fixture/protocolo distintos. |
| Scientific Execution, Scientific World2D, SSE, CAS playback | RED | Dependencia de transición, identidad, cursor, retry/lease y distinción LIVE/terminal. |
| TrialMatrix, preregistration, authorization y execution plan | RED | Identidades selladas, gobernanza y determinismo; una simplificación puede cambiar el instrumento. |
| Theory/Operational Hypergraph | RED | Semánticas distintas y lineage científico; no hay equivalencia probada. |

## 17. Remaining Unknowns

1. Prioridad humana entre teoría, configuración, observación, ejecución y análisis.
2. Flujo inicial real y criterio de selección A0–A4/D2–D4.
3. Rol deseado de World2D y comparación primaria.
4. Variables cognitivas y umbrales que el operador considera decisivos.
5. Densidad y orden de información durante una corrida.
6. Uso humano de cada hipergrafo y decisión sobre los dos D2 Studio.

## 18. Risks

- `RISK`: worktree amplio y WIP protegido impiden atribuir cambios ajenos a esta tarea; no se limpia.
- `RISK`: la interacción Compose permite IDs de draft/matriz potencialmente no correspondientes antes del gate backend; éste falla cerrado, pero el feedback UI específico no está probado.
- `RISK`: un cambio visual que esconda identidad o modo puede cruzar sandbox/LIVE/replay o teoría/lineage.
- `TEST_COVERAGE_GAP`: no se ejecutó E2E de navegador de Compose handoff en esta corrida por entorno Node/Windows separado; el spec existe y fue inspeccionado. No se afirma verificación visual actual.

## 19. Required Human Decisions

Antes de `INFORMATION-ARCHITECTURE-01`, una persona responsable debe decidir: función primaria, primer flujo, papel de World2D, datos cognitivos prioritarios, información persistente durante corrida, comparaciones frecuentes y criterio de consolidación de D2 Studio. Ninguna respuesta se infirió desde código.

## 20. Redesign Gate Assessment

AC-1 a AC-7 están satisfechos por evidencia/documentación; AC-8 se satisface porque no se cambió producción; AC-9 se satisface en el alcance de esta tarea porque no se escribieron los WIP protegidos; AC-10 determina el próximo gate. El rediseño de UI sigue prohibido en este objetivo.

Pruebas dirigidas ejecutadas:

```text
PASS  tests/test_lab_02c_api.py                         9 tests
PASS  tests/test_experiment_composer.py                 11 tests
PASS  tests/test_worldstream.py + test_worldtruth_isolation.py + test_sandbox_runtime.py   32 tests
PASS  tests/test_theory_operational_hyperedge.py         8 tests
PASS  tests/test_preregistration_core.py -k lock/portable-bundle   2 tests
PASS  tests/test_scientific_execution_gate.py -k root/firewall/playback   2 tests
NOTE  los cuatro tests de preregistro/ejecución emitieron sólo el warning ambiental de NVML no inicializable; no afectó los resultados.
```

```text
TASK=UI-ARCHITECTURE-PRECONDITIONS-01
BRANCH=experiment/cognitive-live-observatory-01
PRE_HEAD=a9bfb7a585fe20091821f0e1d920a31956001282
POST_HEAD=a9bfb7a585fe20091821f0e1d920a31956001282
WORKTREE_STATUS=DIRTY_PREEXISTING_WIP_PRESERVED
FILES_CHANGED=docs/UI_FORENSIC_AUDIT_01.md,docs/UI_ARCHITECTURE_PRECONDITIONS_01.md
AUDIT_REVALIDATION=PASS_WITH_FINDINGS
COMPOSE_TRIALMATRIX_RELATION=COMPOSE_PRODUCES_TRIAL_MATRIX
CONTRACT_CONFLICTS=NONE_DEMONSTRATED
DOCUMENTATION_DRIFT=PREVIOUS_AUDIT_COMPOSE_CLAIM_CORRECTED; CURRENT_GUIDE_ALIGNS_WITH_CODE
TEST_COVERAGE_GAPS=Compose stale-pair UX E2E; current browser E2E run not executed in this environment
HUMAN_DECISIONS_REMAINING=7 decision groups in sections 14 and 19
REDESIGN_GREEN_AREAS=Equivalent presentation-only grouping, labels, typography and spacing
REDESIGN_YELLOW_AREAS=Contextual inspector, Workspace shell, Compose handoff presentation, World Lab/World2D presentation
REDESIGN_RED_AREAS=D2 overlap, scientific execution/LIVE/SSE/CAS, TrialMatrix/preregistration/plan, theory-vs-operational hypergraphs
PROTECTED_ARTIFACTS_STATUS=PREEXISTING_WIP_PRESERVED_NO_WRITES_THIS_TASK
REDESIGN_SAFE_TO_START=PARTIAL
NEXT_VALID_OBJECTIVE=EXTERNAL_REVIEW_THEN_INFORMATION-ARCHITECTURE-01
```
