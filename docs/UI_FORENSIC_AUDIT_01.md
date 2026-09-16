# UI_FORENSIC_AUDIT_01

Fecha: 2026-09-15  
Alcance: inventario y trazabilidad de las superficies actuales. No es un rediseño ni una autorización para eliminar o simplificar contratos.

## 1. Repository State

| Campo | Valor observado |
| --- | --- |
| Raíz | `/mnt/wsl/PHYSICALDRIVE2p3/home/wis/mundo simulado terrario` |
| Rama | `experiment/cognitive-live-observatory-01` |
| HEAD | `a9bfb7a585fe20091821f0e1d920a31956001282` |
| Backend | Python 3.12, paquete `terrario`, `ThreadingHTTPServer` en `terrario/lab/api.py` |
| Frontend | HTML/CSS/ES modules sin framework para `/`; ES modules/canvas para `/workspace/index.html` |
| Build | setuptools (`pyproject.toml`); no bundler frontend observado |
| E2E | Playwright (`package.json`, `playwright*.js`, 17 specs en `tests_frontend/e2e`) |

FACT: el worktree está deliberadamente sucio y contiene WIP en backend, frontend, tests, documentación y artefactos no rastreados. Esta auditoría no limpia, cambia de rama ni modifica ese WIP. El archivo presente sólo documenta hallazgos.

FACT: `scripts/run_lab.py` invoca la API de laboratorio. `terrario/lab/api.py:488-573` sirve archivos estáticos y tiene dos transportes SSE: sandbox WorldStream y Scientific LIVE.

FACT (CORREGIDO por `UI-ARCHITECTURE-PRECONDITIONS-01`): `docs/TERRARIO_USER_MANUAL.md` no está versionado, pero su contenido actual sí documenta `Compose`, `ExperimentDraft`, `TrialMatrix` y el handoff a preregistro (secciones 7–8). La afirmación previa de que la guía negaba la existencia de Compose era incorrecta. La guía, el Lab clásico y el contrato de dominio son coherentes en este punto.

## 2. UI Surface Inventory y Route/View Map

### Lab clásico — ruta `/`

Entrada: `terrario/lab/static/index.html`; controlador único: `terrario/lab/static/app.js`; estilos: `terrario/lab/static/styles.css`.

| Vista | Propósito observable | Superficies principales | Contratos principales | Clase |
| --- | --- | --- | --- | --- |
| Inicio | resumen de estado | snapshot, ocho contadores, fronteras | `/api/status` | A/G |
| Manual | ruta humana por teoría/diseño | cinco pasos, enlaces de vista, explicación de dos hipergrafos | frontend estático | G/D |
| Experimentos | catálogo histórico | tabla, refrescar, inspector provenance | `/api/experiments`, `/api/experiments/{id}` | C/D |
| Run | análisis de un run leído | selector, métricas, timeline canvas | `/api/runs`, timeline, agent/observer view | C |
| Mundo | replay clásico | canvas, Agent/Observer, replay, salto, metadata | `/api/runs/{id}/*` | C |
| World Lab | construir/previsualizar sandbox | WorldDraft, seeds, preview, sandbox controls, timeline/event inspector | worlds, sandbox, seed APIs | F/E |
| Capabilities | descriptor A0–A4 y compatibilidad | matriz, inspector, escenario/agente, informe | capabilities, agents, compatibility | C/F |
| Metrics | definición y observabilidad | registry, detalle, configurador observer, estimate | metrics, observer profiles/estimate | C/F |
| Compose | crear diseño durable | formulario, warning, identidad, TrialMatrix | experiment-drafts, trial-matrices, review request | F/D |
| D2 Studio | validar/diff de configuración | controles, JSON patch, warnings, output | studio/d2, config validate/diff | F/C |
| Hipergrafo | navegación teórica | filtros, path finder, canvas, node inspector | `/api/hypergraph` | C/G |
| Diseño experimental | familias/rivales | filtros, portfolio, detalle | theory portfolio | C/F |
| Revisión científica | evaluación de diseños | resumen, cola, paquete | scientific-review | C/D |
| Analizador | análisis determinista separado | drafts, preview, resultado | analyzer/deterministic | C |
| Configuración | inspector y sandbox UI local | hashes, controles locales | frontend-only sandbox state; experimento seleccionado | D/E |

### Workspace científico — ruta `/workspace/index.html`

Entrada: `terrario/lab/static/workspace/index.html`; orquestador: `workspace/main.js`; shell: `workspace/core/shell.js`; cliente: `workspace/core/api.js`.

| Panel | Región | Función | Datos/contrato | Clase |
| --- | --- | --- | --- | --- |
| Explorer | izquierda | referencias y mundos | ReferenceGraph y `WorldDefinition` | G/C |
| Operational Hypergraph | izquierda | catálogo operacional y puente de hipótesis | `/api/operational-hypergraph`, status | C/D |
| Scientific Canvas | centro | slice/selección/layout de cross-graph | `graph-slice`, layout worker | C/G |
| Inspector | derecha | detalle y provenance de selección | reference/cross-graph provenance | B/D |
| Research Composition | derecha | composición local versionada | cross-graph compositions | B/F |
| World2D | inferior | preview/sandbox/replay de ingeniería | world preview, WorldStream/SSE/traces | A/E |
| Scientific Execution | inferior | solicitud, autorización, plan y control | `/api/v1/scientific-executions*` | A/F/D |
| World2D Scientific | inferior | LIVE/read-only y playback científico | ScientificFrame SSE/CAS playback | A/C/D |
| D2 Scientific Studio | inferior | configuración/fixture D2 | D2 audit/fixture | F/C |

FACT: `workspace/main.js:199-215` monta los nueve paneles simultáneamente y `WorkspaceShell` ofrece ocultar, fullscreen y un switcher persistido en `localStorage` (`core/shell.js`).

## 3. Component Topology y UI-to-Contract Traceability

| UI visible | Estado/control frontend | Transporte/backend | Modelo/significado científico |
| --- | --- | --- | --- |
| World2D sandbox | `World2DPanel`, `WorldStreamClient`, `session`, `frames` | POST `world-stream/sessions`, commands/resync; SSE stream (`world2d/protocol.js:91-108`) | sandbox de ingeniería; explícitamente no evidencia |
| World2D trace | `PlaybackController`, tick presentado | trace events/seek/compare (`world2d/playback.js:5-20`) | reproducción de traza, no reejecución |
| Scientific Execution | `ScientificExecutionPanel.execution` | request → authorization → bind → plan → command → dispatch/verify (`views/scientific-execution.js:15-18`) | `ScientificExecutionService`, autorización y plan con hash |
| Scientific World2D | `ScientificWorld2DPanel.state`, cursor, `followingLive` | Scientific execution live SSE, snapshot, playback | `ScientificFrame`, identity/cursor/attempt; viewer de sólo lectura |
| Cognitive Observatory | render dentro de Scientific World2D | `frame.cognitive_state`; `world2d/cognitive.js` | proyección científica transportada, no tensor bruto ni input al agente |
| Composer clásico | `state.experimentDraft`, `state.trialMatrix` | validate/create draft, build matrix; governance review | `ExperimentDraft` y `TrialMatrix`, no run |
| Hipergrafo clásico | `state.graph`, `graphSpots`, `graphFocusIds` | `/api/hypergraph` → `LabAPI._hypergraph()` | TheoryGraph/EvidenceGraph export; relaciones epistemológicas |
| Hipergrafo operacional | `OperationalHypergraphPanel.edges` | `/api/operational-hypergraph` | cadena tipada diseño→preregistro→attempt→frame→trace, no EvidenceGraph |
| Provenance | inspector, node detail, execution status/json | cross/reference provenance; artifact descriptors, CAS, verification | reproducibilidad e integridad, no conclusión científica |

FACT: `ScientificFrame` se crea con identidad, tick, WorldTruth, Agent Observation, Observer View, cursor y proyección cognitiva (`execution/runtime.py:42-115`). `execution/live.py:91` exige binding de identidad antes de publicar una frame.

FACT: la API expone CSRF/sesión, APIs versionadas de preregistro, ejecución, evidencia, WorldStream, ReferenceGraph y CrossGraph (`api.py:93-109`).

## 4. Operational State Machine

### Ejecución científica

```text
REQUESTED
  --bind authorization--> VALIDATING -> AUTHORIZED
  --seal plan-----------> PLANNED -> READY
  --START---------------> RUNNING --all jobs sealed--> COMPLETED --verify--> PASS/FAIL/DEVIATED
                         | PAUSE                 | failure/lease
                         v                       v
                     PAUSING -> PAUSED       FAILED / RECOVERY_REQUIRED
                         | RESUME
                         v
                      RUNNING
```

FACT: transiciones legales en `execution/domain.py:263-275`; comandos y precondiciones en `execution/service.py:119-157`; completado y verificación en `:175-218`. El panel sólo invoca `START`, `PAUSE`, `RESUME`, `CANCEL`; el servidor impone la transición.

### Modos de visualización

| Modo | Superficie | Entrada | Cambio visible |
| --- | --- | --- | --- |
| PREVIEW | World2D | abrir mundo | truth previsualizada; sin session |
| LIVE SANDBOX | World2D | crear sesión | conexión, revisión, frames y commands sandbox |
| TRACE PLAYBACK | World2D | abrir trace | seek/comparar, sin command de ejecución |
| SCIENTIFIC IDLE/CONNECTING/LIVE/RESYNCING/TERMINAL/PLAYBACK/LOST/ERROR | World2D Scientific | attach, SSE, snapshot o CAS | badge, controles habilitados, cursor, provenance |
| CONFIGURATION | World Lab/Compose/D2 | edición/validación | campos y findings; no evidencia |
| THEORY/ANALYSIS | Hipergrafo/Diseño/Revisión/Analizador | navegar/seleccionar | detalle derivado, sin ejecución |

RISK: el Lab clásico ofrece un sandbox local en Configuración y otro contrato de sandbox en World Lab; no se ha probado que el primero controle runtime real. `static/app.js:74` mantiene ese primero sólo como estado frontend. Deben conservarse como semánticas distintas hasta confirmación humana.

## 5. Current Workflow Reconstruction

FACT — flujo clásico de diseño:

```text
Hipergrafo candidato
 -> Diseño experimental / Compose
 -> Validate ExperimentDraft
 -> persist ExperimentDraft
 -> build durable TrialMatrix
 -> review request / preregistration (si la ruta está disponible)
 -> autorización / plan / Scientific Execution en Workspace
 -> ScientificFrame LIVE o CAS playback
 -> verify integrity
```

FACT: `static/app.js:61-63` materializa draft/matrix; `workspace/views/scientific-execution.js:15-18` consume una root hash bloqueada y despacha. El handoff de versión durable está cubierto por `composer-preregistration-handoff.spec.js`.

INFERENCE: el Lab clásico es el área de preparación/análisis de teoría; Workspace es el área de observación y ejecución moderna. La intención humana de alternar entre ambas no puede inferirse.

UNKNOWN: primer paso humano, criterio para elegir A0–A4/D0–D4, qué campos son frecuentes, y qué resultado guía la siguiente acción.

## 6. World2D Analysis

FACT: World2D separa preview, sandbox LIVE y trace playback (`views/world2d.js:20-60`). Incluye comandos `START/PAUSE/RESUME/STOP/STEP`, scrubber, velocidad, comparación, bookmark, cámara, export diagnostic y selección/picking.

FACT: el SSE sandbox se reconecta/resincroniza con revisión de sesión; un conflicto de revisión o command id duplicado se verifica en `worldstream-live.spec.js:25-31`. Latencia command-to-visible se prueba en `world2d-live-latency.spec.js`.

FACT: World2D Scientific no presenta controles de Start/Step/Pause/Resume/Reset/Seed/Intervention (`scientific-live.spec.js:81-87`); es una frontera entre observación científica y control de ingeniería.

RISK: World2D concentra controles propios del mundo, timeline, compare, cámara, export y diagnósticos de conexión en una sola toolbar. Su necesidad simultánea no se puede decidir sólo por código.

## 7. Cognitive Observatory Analysis

FACT: el observatorio está unido a una frame científica identificada y presenta una proyección delimitada por capacidad; A0 declara dominios no disponibles en lugar de fabricar señales (`scientific-live.spec.js:148`).

FACT: la proyección contiene estado después de `learn()` en `execution/runtime.py:115`; `world2d/cognitive.js` etiqueta `UNAVAILABLE`, `NOT_APPLICABLE`, `NON_FINITE` y `MALFORMED` explícitamente.

INFERENCE: la superficie apoya inspección de acción/política, temporalidad, memoria, predicción/error, incertidumbre y cambios parametrales cuando están declarados. No prueba por sí misma aprendizaje, creencia, transferencia o competencia.

UNKNOWN: las cinco variables que un operador necesita ver primero, y si deben ser overlay del mundo, panel contextual o análisis posterior.

## 8. Experiment, Theory, Provenance and Integrity

| Entidad | Identidad persistente | Superficie actual | Estado del puente |
| --- | --- | --- | --- |
| teoría/concepto/relación | snapshot/node id | Hipergrafo | IMPLEMENTED |
| HyperedgeCandidate | record/original id | Hipergrafo → Diseño | IMPLEMENTED para puente portfolio; E2E `hypergraph-design-bridge.spec.js` |
| hipótesis/diseño | portfolio/draft id | Diseño/Compose | PARTIAL: no intención humana inferida |
| ExperimentDraft | artifact/version/scientific hash | Compose | IMPLEMENTED |
| TrialMatrix | matrix/version id | Compose | IMPLEMENTED |
| preregistration | root hash/revision | API/review; Scientific Execution consume root | PARTIAL: superficies repartidas |
| execution/trial/attempt | execution, trial intent, attempt IDs | Scientific Execution/World2D Scientific | IMPLEMENTED |
| trace/CAS | blob/descriptor hash | playback/verify | IMPLEMENTED |
| métricas/análisis | metric id/derived payload | Run/Metrics/Analizador | IMPLEMENTED como lectura/derivación |
| evidence/conclusion | resultado/publicación | API de evidencia | PARTIAL en UI inspeccionada; no promover automáticamente |

FACT: `evidence_publication.py:66` exige ejecución `COMPLETED`; una frame, trace o artefacto crudo no se convierte en evidencia automáticamente.

RISK: hashes, IDs, revisión, warnings y badges aparecen tanto en formularios como inspectores. Son contratos distintos, pero su exposición permanente puede mezclar provenance, operación y diagnóstico.

## 9. Duplication Map and Mode-Mixing Findings

| Hallazgo | Evidencia | Clasificación | Consecuencia si se “simplifica” sin auditoría |
| --- | --- | --- | --- |
| Dos hipergrafos | Lab clásico Theory/Evidence; Workspace operacional | contextual, no duplicado semántico | confundir teoría con cadena de ejecución |
| Dos mundos | Mundo replay clásico; World2D sandbox; World2D Scientific | modos distintos | permitir control sobre ensayo científico |
| Dos sandbox UI | Configuración frontend-only vs World Lab backend | posible legacy/orphan | presentar control ficticio como runtime |
| Datos de identidad | Compose, preregistro, Scientific Execution, inspector | provenance distribuida | perder handoff exacto |
| D2 en ambos Lab/Workspace | D2 Studio clásico y D2 Scientific Studio | posible duplicación parcial | borrar fixture/contrato diferente |
| Paneles inferiores Workspace | cuatro dominios simultáneos | mezcla de modos potencial | ocultar controles necesarios sin contexto |

## 10. Overload Evidence Matrix

| View | Propósito primario | Regiones visibles | Acciones primarias/secundarias | Diagnóstico/Provenance | Mezcla de modos | Riesgo con evidencia |
| --- | --- | ---:| --- | --- | --- | --- |
| World Lab | configurar sandbox | 5+ | validate/create/run; preview/seeds/timeline | identity, reproducibility, event inspector permanentes | config+preview+control+diagnóstico | alto: wizard de 14 pasos y 7 sandbox buttons visibles (`index.html:12`) |
| Compose | diseño durable | 3 | validate/save/build | warnings, identity, output, matrix | config+review/provenance | alto: configuración, resultados de validación y matriz simultáneos |
| Hipergrafo clásico | navegación teoría | 4 | filtros/path/selección | detalle completo de nodo | theory+diagnóstico de path | medio/alto: 1,176 nodos/1,092 relaciones observados; overview debe ser contextual |
| World2D | observar/controlar sandbox | 3+ | create/start/step/playback | connection, export, compare/bookmark | LIVE+replay controls en una barra | alto potencial; contrato requiere distinguirlos |
| World2D Scientific | observación | 4+ | attach/resync/playback/inspect | cursor/provenance/cognitive projection | LIVE/terminal/playback, correctamente stateful | medio: controles disabled son visibles por diseño |
| Workspace total | estación multipanel | 9 paneles en 4 regiones | navigation/panel tools | snapshot/status/errors | teoría+config+live+analysis | alto: todos se montan simultáneamente (`main.js:199-215`) |

FACT: estas no son puntuaciones subjetivas; se basan en regiones, controles y contratos simultáneos observables. La prioridad humana entre ellos permanece UNKNOWN.

## 11. UNKNOWN Human Decisions

El código no responde:

1. qué debe saber primero el usuario al abrir Terrario;
2. si la función dominante es observar, configurar, ejecutar, analizar, comparar o validar;
3. el primer paso humano y flujo realmente seguido;
4. rol principal de World2D (depuración vs instrumento científico);
5. cinco variables cognitivas prioritarias;
6. fenómeno prioritario a detectar en observatorio;
7. información que debe permanecer visible antes/durante Run;
8. comparaciones más frecuentes;
9. cuándo/para qué se usa el hipergrafo;
10. cuál vista resulta peor y causa percibida de sobrecarga.

## 12. Architectural Constraints for Future Redesign

1. No mezclar `ENGINEERING_SANDBOX` con Scientific LIVE o EvidenceGraph.
2. ScientificFrame debe conservar identidad atómica, cursor y separación WorldTruth/Agent Observation/Observer View.
3. SSE debe seguir fail-closed ante cursor stale, gap o intento cruzado; CAS playback es autoritativo terminal.
4. Seeds, TrialMatrix, preregistration root, authorization, plan hash y revisión son identidades distintas.
5. Los estados `UNAVAILABLE`, `NOT_APPLICABLE`, `NON_FINITE` y `MALFORMED` no pueden compactarse a cero/ausencia.
6. Hipergrafo teórico y operacional no son intercambiables.
7. Provenance puede ser contextual visualmente, pero no puede perder navegación/recuperación de identidad.

## 13. Risks and Stop Conditions

- FACT (corrección posterior): la guía actual y la superficie clásica coinciden sobre Compose; véase la corrección factual de la sección 1.
- RISK: worktree amplio y WIP impide atribuir todas las modificaciones a una sola línea de trabajo.
- RISK: una vista aparentemente duplicada puede consumir un contrato distinto (D2, sandbox, hipergrafo).
- UNKNOWN: no hay evidencia suficiente para eliminar, ocultar por defecto o promover controles.

Por tanto, cualquier rediseño sigue bloqueado hasta resolver las preguntas humanas y validar la semántica de las superficies con doble función.

## 14. Evidence Appendix

- Rutas/HTTP: `terrario/lab/api.py:93-109, 111-322, 488-573`.
- Lab clásico: `terrario/lab/static/index.html:7-21`, `static/app.js:61-75`.
- Workspace: `static/workspace/main.js:199-215`, `core/shell.js`, `core/api.js:134-158`.
- WorldStream: `static/workspace/world2d/protocol.js:91-108`; `worldstream-live.spec.js`.
- Scientific LIVE: `static/workspace/views/scientific-world2d.js:24-129`; `execution/live.py:91`; `scientific-live.spec.js`.
- Execution state machine: `execution/domain.py:263-280`; `execution/service.py:80-218`; `execution/dispatcher.py:22-42`.
- Test corpus: `tests_frontend/e2e/*.spec.js`, in particular `workspace-launch`, `workspace-interactions`, `accessibility`, `scientific-live`, `world2d-*`, `hypergraph-design-bridge`, `composer-preregistration-handoff`.

## Final Status

```text
PRE_HEAD=a9bfb7a585fe20091821f0e1d920a31956001282
POST_HEAD=a9bfb7a585fe20091821f0e1d920a31956001282
BRANCH=experiment/cognitive-live-observatory-01
WORKTREE=DIRTY_PREEXISTING_WIP_PRESERVED
FILES_CHANGED=docs/UI_FORENSIC_AUDIT_01.md
AUDIT_STATUS=PASS_WITH_UNKNOWNS
TOP_OVERLOAD_FINDINGS=Workspace multipanel mount; World Lab mixed responsibilities; World2D mixed mode controls; full hypergraph density; Compose mixed configuration/provenance/matrix.
UNRESOLVED_HUMAN_QUESTIONS=10 listed in section 11
REDESIGN_SAFE_TO_START=NO
```
