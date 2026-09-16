# Terrario — auditoría de arquitectura y capacidades

**Fecha de auditoría:** 2026-09-14  
**Checkout auditado:** `experiment/cognitive-live-observatory-01` en `a9bfb7a585fe20091821f0e1d920a31956001282`  
**Alcance:** reconstrucción read-mostly del checkout local. No es una certificación científica ni una reejecución completa de QA.

## Resultado ejecutivo

Terrario es un laboratorio local para investigar agentes en mundos deterministas. Combina un simulador clásico, un laboratorio científico persistente y una interfaz visual. El núcleo de fiabilidad existe: identidad, semillas, trazas, CAS/SQLite, preregistro, controles de ciclo de vida, checkpoints y una observación separada del agente.

El problema operativo principal no es que esos mecanismos existan: es que hay **dos superficies con garantías diferentes**:

```text
CLI clásica ──> ExperimentController / ExperimentRunner ──> archivos de resultados y observer
Lab científico ─> API local ─> SQLite + CAS + preregistro + dispatcher ─> artefactos crudos/LIVE/playback
```

La primera es adecuada para desarrollo, diagnóstico y ejecución avanzada. La segunda es la única ruta que implementa el ciclo de preregistro, autorización, plan sellado, intento durable, artefactos CAS y reproducción de ejecución científica. La recomendación documental es declarar el Lab como ruta canónica y clasificar la CLI como `ADVANCED_DEVELOPMENT`, sin retirarla.

## Método y límites de evidencia

Se priorizó wiring ejecutable, código, pruebas, contratos y entrypoints; la documentación se usó como índice y se contrastó con el código. Se ejecutaron con éxito 14 pruebas focalizadas:

```text
tests/test_scientific_state_contract.py
tests/test_causal_fork_core.py
```

No se ejecutó la suite completa ni browser E2E. Por tanto, una capacidad con código y wiring, pero sin prueba ejecutada durante esta auditoría, se marca `IMPLEMENTED_UNVERIFIED` cuando corresponde. Los conteos globales no se publican: los componentes se superponen y convertir el catálogo semántico en un conteo de archivos sería engañoso.

Los dos cambios que ya existían al iniciar y no pertenecen a esta auditoría son:

```text
M scripts/seed_scientific_live_e2e.py
M tests_frontend/e2e/scientific-live.spec.js
```

## Taxonomía

`IMPLEMENTED` significa que hay implementación conectada y evidencia de prueba relevante. `IMPLEMENTED_UNVERIFIED` conserva la distinción cuando se confirmó wiring pero no se ejecutó evidencia suficiente aquí. `PARTIAL` significa que el alcance está explícitamente limitado. `EXPERIMENTAL` es una superficie no promotable a evidencia. `LEGACY` permanece para compatibilidad o historia. `MISSING` significa que el nombre o la arquitectura lo sugieren, pero no se encontró realización operacional. `UNKNOWN` no se convierte en hipótesis.

## Topología real

```text
scenarios/*.yaml + configs/*.yaml
        │
        ▼
core RNG/types/contracts ─> world state/rules/physics/scheduler
        │                              │
        ├─> A0…A4 agent factory ───────┤
        │                              ▼
        └─> ExperimentController ─> ScientificObserver ─> JSONL/checkpoints/forensic files
                                            │
                                            └─> post-learning scientific state

Theory/World Studio/Composer ─> Preregistration lock ─> ScientificExecutionService
                                                        │
                                                        ▼
                                             Dispatcher / materialized trials
                                                        │
                                  ┌─────────────────────┼────────────────────┐
                                  ▼                     ▼                    ▼
                              SQLite/CAS             LIVE/SSE          playback from CAS
                                  │                     │
                                  └──── Lab read models/UI/Scientific World2D ┘
```

### Paquetes y responsabilidades

| Componente | Ruta / símbolos | Qué hace y produce | Estado |
| --- | --- | --- | --- |
| Core | `terrario/core/{types,contracts,rng,events}.py` | tipos, transición, RNG y contratos de bajo nivel | IMPLEMENTED |
| World | `terrario/world/{state,physics,rules,scheduler,scenario,opportunities}.py` | WorldTruth, reglas, física, cambios y oportunidades | IMPLEMENTED |
| Controller | `experiment/controller.py:ExperimentController` | materializa escenario, construye agente, ejecuta observar→decidir→consecuencia→learn y registra | IMPLEMENTED |
| Runner clásico | `experiment/runner.py:ExperimentRunner` | comparaciones, ablaciones y reporte agregado | IMPLEMENTED_UNVERIFIED |
| Observer | `observer/{logger,trace,storage,probes}.py` | manifest, transiciones, trazas y captura forense | IMPLEMENTED |
| Checkpoints | `observer/checkpoints.py:CheckpointManager` | parámetros, optimizador, RNG y opcional WorldTruth | IMPLEMENTED; reconstrucción probada |
| Agentes | `agent/agents/{a0_random,…,a4_advanced}.py` | cinco arquitecturas concretas | IMPLEMENTED |
| Scientific state | `agent/scientific.py` | snapshot sólo lectura y proyección de transporte acotada | IMPLEMENTED |
| CLI | `main.py`, `scripts/run_experiment.py`, `scripts/ablation_study.py` | ejecución directa y diagnóstico | IMPLEMENTED_UNVERIFIED / ADVANCED |
| Lab API | `lab/api.py` | servidor HTTP local y composición de servicios | IMPLEMENTED_UNVERIFIED |
| Persistencia | `lab/persistence/{store,blobs,canonical,migrations}.py` | SQLite WAL, CAS, versiones, transacciones y exportación | IMPLEMENTED |
| World authoring/sandbox | `lab/{world_authoring,sandbox,sandbox_runtime}.py` | borradores, validación, preview y runtime de ingeniería | EXPERIMENTAL |
| WorldStream | `lab/worldstream/*` | sesiones y stream de sandbox | EXPERIMENTAL; no evidencia |
| Theory/reference/cross graph | `lab/theory/*`, `referencegraph/*`, `crossgraph/*`, `hypergraph/*` | ingestión, hipótesis, consulta y relaciones derivadas | IMPLEMENTED_UNVERIFIED |
| Experiment composer | `lab/experiment_composer.py` | ExperimentDraft y TrialMatrix, sin ejecutar | IMPLEMENTED_UNVERIFIED |
| Preregistration | `lab/preregistration/*` | versiones, review, lock, auditoría y exposure ledger | IMPLEMENTED |
| Scientific execution | `lab/execution/{service,dispatcher,runtime,live}.py` | autorización, plan, leases, intentos, sellado y recuperación | IMPLEMENTED |
| Scientific World2D | `static/workspace/views/scientific-world2d.js` | observación live/playback de sólo lectura | IMPLEMENTED_UNVERIFIED |
| Causal Fork Core | `lab/causal.py` | bifurcación exacta fail-closed | PARTIAL |
| H-ADAPT | `experiment/adaptation.py`, `scripts/run_h_adapt_001.py` | campaña especializada; CUDA requerida por configuración | EXPERIMENTAL / BLOCKED por entorno sin GPU |
| Genesis / RNFE | búsqueda de módulos y wiring | no se halló integración operacional actual | MISSING |
| Evidence pipeline confirmatorio | docs y servicios de Lab | no hay ruta de promoción automática a EvidenceGraph | MISSING / intencional |

## Entry points reales

| Entrada | Objetivo | Ruta oficial | Salida y persistencia |
| --- | --- | --- | --- |
| `python main.py run` | comparación clásica desde YAML | avanzada, no científica canónica | reporte y observaciones bajo `output_dir` |
| `python main.py verify` | comprobación de reproducibilidad | diagnóstico | salida de script de verificación |
| `python main.py ablate` | ablación A4 clásica | avanzada | comparativa de condiciones |
| `python scripts/run_experiment.py` | duplicado funcional de `main.py run` | alternativa/legacy operativo | mismo runner y reporte |
| `python scripts/run_lab.py` | servidor Lab HTTP | **canónica propuesta** | `.terrario/`, SQLite/CAS y UI |
| `python -m terrario.lab.preregistration` | CLI de preregistro | avanzada | artefactos de Lab |
| `scripts/run_h_adapt_001.py` | campaña H-ADAPT | experimental, dependiente de GPU | artefactos de campaña |

`main.py run` y `scripts/run_experiment.py` construyen el mismo `ExperimentConfig` y `ExperimentRunner`; son una duplicación de entrada, no dos motores distintos.

## Matriz de capacidades por superficie

| Capacidad | Core | Backend/API | UI | CLI | Tests | Estado operacional |
| --- | --- | --- | --- | --- | --- | --- |
| Simulación determinista | sí | indirecto | sandbox/visualización | sí | sí | IMPLEMENTED |
| A0–A4 | sí | inspector/runtime | selector/inspector | sí | sí | IMPLEMENTED |
| D0–D4 YAML | sí | registry/studio | D2–D4 visibles | sí | sí | IMPLEMENTED, madurez desigual |
| Comparación clásica | sí | no es ruta Lab | no equivalente | sí | sí | IMPLEMENTED_UNVERIFIED |
| Ablación A4 clásica | sí | no se expone como Lab científico | no confirmada | sí | código y tests | IMPLEMENTED_UNVERIFIED |
| Draft/matriz de ensayo | sí | sí | sí | no necesaria | sí | IMPLEMENTED_UNVERIFIED |
| Preregistro bloqueado | no | sí | superficie separada/cliente | sí | sí | IMPLEMENTED |
| Ejecución científica | runtime | sí | panel Scientific Execution | no como comando corto | sí | IMPLEMENTED |
| LIVE/SSE científico | frames | sí | Scientific World2D | no | sí | IMPLEMENTED_UNVERIFIED |
| Playback de traza científica | CAS | sí | sí | no | parcialmente | IMPLEMENTED_UNVERIFIED |
| Checkpoint/restauración | sí | artefacto | no es control UI ordinario | indirecto | sí | IMPLEMENTED |
| Fork causal exacto | sí | persistido | no se confirmó flujo UI | no canónico | sí | PARTIAL |
| Sandbox WorldStream | sí | sí | sí | no | sí | EXPERIMENTAL, NOT EVIDENCE |
| Export bundle | sí | sí | no se confirmó botón UI | indirecto | sí | IMPLEMENTED_UNVERIFIED |

## A0–A4: semántica comprobada

| Variante | Añade frente a la anterior | No debe afirmarse |
| --- | --- | --- |
| A0 | política aleatoria; sin aprendizaje, memoria ni estado | capacidad cognitiva o adaptación |
| A1 | encoder + política REINFORCE reactiva | memoria, temporalidad o world model |
| A2 | núcleo GRU temporal | memoria persistente o world model |
| A3 | world model sobre estado temporal | memoria episódica/largo plazo |
| A4 | temporal configurable, memorias episódica y de largo plazo, world model, incertidumbre, planner, homeostasis y aprendizaje online | que estos componentes prueben por sí mismos ganancia cognitiva |

Evidencia: factory `agent/agents/__init__.py:create_agent`; implementaciones A0–A4; contratos de estado en `agent/scientific.py`; pruebas `tests/test_agent*.py`, `test_a4_learning.py` y `test_scientific_state_contract.py`.

La observabilidad no es uniforme: A0 comunica principalmente identidad/paso; A1/A2 no declaran todas las señales científicas; A3 declara temporalidad y predicción; A4 declara política, memoria, predicción/error, incertidumbre y resumen de aprendizaje. Las ausencias se modelan como `NOT_APPLICABLE`, no como cero.

## D0–D4: semántica comprobada

| Nivel | Mundo / pregunta operacional | Estado |
| --- | --- | --- |
| D0 | firmas de canales y discriminación básica; reglas sin cambio | IMPLEMENTED; único mundo calificado para fork exacto con A0 |
| D1 | persistencia de objetos/movimiento declarado | LEGACY/IMPLEMENTED_UNVERIFIED: el YAML describe movimiento; requiere verificar que el runtime lo materialice en cada campaña |
| D2 | propiedades funcionales: objetos movibles vs inmovibles | IMPLEMENTED; visible en Studio |
| D3 | correlación frente a variable causal | IMPLEMENTED; la calificación científica no se infiere del YAML |
| D4 | cambio de reglas, adaptación, oportunidades y una variante de transferencia | PARTIAL: runtime y pruebas de contratos existen; protocolo científico/validación/held-out no están cerrados |

Los escenarios no declaran por sí solos una distribución train/test ni evidencia de transferencia. D4 `adaptation_transfer` es una condición implementada, no prueba de transferencia.

## Observatorio cognitivo

La secuencia conectada es:

```text
agent.learn(transition)
  -> scientific_state(agent)
  -> scientific_transport_projection(...)
  -> frame_sink / ScientificFrame
  -> ScientificLivePublisher (SSE) y SCientific_TRACE sellada en CAS
  -> playback
```

`ExperimentController.run_episode` captura el snapshot después de `learn()`. El sink recibe el frame ya capturado; no vuelve a leer internals mutables. Los límites de transporte son explícitos en `agent/scientific.py`: preview 16, mappings 16, claves 80 caracteres, strings 160, ocho dimensiones de shape y 16 KiB máximos serializados. Valores non-finite/malformed se representan explícitamente. El fallo del sink se recoge como `FRAME_SINK_FAILURE`; el dispatcher puede clasificar el intento como `MATERIALIZATION_FAILED`, sin usar esa instrumentación para alterar decisión, mundo, RNG o aprendizaje.

**Qué permite concluir:** que el contrato expone una señal observada de la arquitectura en un tick identificado.  
**Qué no permite concluir:** que la señal sea una representación interna completa, que el agente comprenda algo, o que haya ganancia cognitiva/causalidad/transferencia.

Evidencia: `experiment/controller.py:run_episode`, `agent/scientific.py`, `lab/execution/dispatcher.py`, `lab/execution/live.py`, `tests/test_scientific_state_contract.py`, `tests/test_scientific_live_observability.py`, `tests/test_observer_passivity_campaign.py`.

## Trace, playback y restauración

Hay dos mecanismos distintos que no deben agruparse bajo “replay”:

1. **Recorded Playback.** `lab/replay.py:OfflineReplay` mueve un cursor sobre `RunTimeline` ya registrada. Es una visualización de datos registrados; no ejecuta de nuevo el agente.
2. **State Restoration / Experimental Reconstruction.** `observer/checkpoints.py:CheckpointManager.restore` puede restaurar parámetros, optimizador, RNG Python/NumPy/Torch/generador del agente y, si existe, WorldTruth serializada. Esto sí permite reconstituir estado, sujeto a completitud de checkpoint y compatibilidad de runtime.

En la ruta científica, el dispatcher sella `SCIENTIFIC_TRACE` y `TRIAL_RESULT` antes de emitir terminal; cuando ya no están los frames en memoria, el playback obtiene la traza desde CAS. Un playback no es automáticamente una reejecución reproducida ni evidencia confirmatoria.

## Integridad científica: garantías y fronteras

| Afirmación | Enforcement / evidencia | Estado y límite |
| --- | --- | --- |
| Semillas y determinismo | `RNGManager`, identidad de agente y checkpoint RNG | IMPLEMENTED; no equivale a validar una hipótesis |
| Separación agent/observer | controller crea anotaciones sólo para observer; frame sink observador | IMPLEMENTED; pruebas de pasividad relevantes |
| Inmutabilidad/provenance | canonical JSON, hashes, CAS, versiones, transacciones SQLite | IMPLEMENTED |
| Preregistro antes de ejecución científica | root bloqueada, readiness y plan | IMPLEMENTED; requiere decisiones humanas reales |
| Autorización | authorization ligada a ejecución, recursos y expiración | IMPLEMENTED; política local, no ley científica |
| Trazas e intentos | intent/job/attempt, CAS antes de terminal | IMPLEMENTED |
| Fork causal | snapshot, identidad y ramas aisladas | PARTIAL: sólo A0×D0 y control/sham/test intervention |
| Validación experimental | controles y diseño pueden expresarse | PARTIAL; depende del protocolo concreto |
| Validación científica | no se promueve automáticamente | MISSING/intencional |
| Evidencia de ganancia, transferencia o persistencia | métricas y campañas potenciales | UNKNOWN por experimento; no demostrada por arquitectura |

## DECLARED_BUT_NOT_OPERATIONAL

- **Fork causal general A1–A4/D1–D4:** `PARTIAL`, no operativo; `CausalRuntime.forkability` falla cerrado fuera de `A0_RANDOM × d0_differences`.
- **Intervenciones científicas amplias:** `MISSING`; sólo `C00`, `C01_SHAM` y `TEST_ENERGY_DELTA` están registrados.
- **Evidence pipeline confirmatorio:** `MISSING`; el dispatcher etiqueta outputs como raw artifacts, no EvidenceGraph.
- **Genesis, RNFE y H-ADAPT como plataforma integrada general:** Genesis/RNFE no hallados; H-ADAPT es una campaña experimental dependiente de CUDA, no ruta cotidiana.
- **“Replay” como reproducción experimental completa:** `PARTIAL`; recorded playback y restauración son mecanismos diferentes.
- **D4 como evidencia de adaptación o transferencia:** `DECLARED_ONLY` como conclusión científica; hay escenarios y tests, no una conclusión promotable.

## OPERATIONAL_BUT_POORLY_DOCUMENTED

- El CLI de preregistro y los endpoints de exportación/validación de bundle existen en `lab/preregistration/__main__.py` y `lab/{preregistration,execution}/api.py`.
- `ScientificExecutionDispatcher` conserva intentos, leases, recuperación y sellado CAS, detalles no visibles en el flujo clásico.
- La UI de Scientific Execution ofrece request, autorización, plan, start/pause/resume/cancel y verify; no debe confundirse con el compositor, que sólo crea un borrador/matriz.
- `Scientific World2D` es distinto de World2D/WorldStream sandbox: es visualización científico-read-only de LIVE y playback.

## NOMENCLATURE_AND_SEMANTIC_DRIFT

| Nombre | Significado actual | Riesgo / recomendación documental |
| --- | --- | --- |
| Replay | cursor de timeline **o** lectura de traza desde CAS | usar “Recorded Playback”; reservar “State Restoration” para checkpoint |
| Run | ejecución clásica, sandbox o intento científico | siempre indicar plano: `classic`, `engineering sandbox`, `scientific attempt` |
| World2D | viewer clásico, sandbox o World2D científico | añadir etiqueta visible `ENGINEERING_SANDBOX` o `SCIENTIFIC` |
| Observer | logger/forense del core y plano científico live | separar “observer artifact” de “transport projection” |
| Evidence | artefacto crudo, análisis derivado o evidencia científica | raw/CAS no es evidencia confirmatoria |
| D4 transfer | escenario implementado | no llamarlo transferencia demostrada |
| Fork | mecanismo causal exacto calificado | declarar su rango A0×D0, no extrapolar |

La documentación reciente de observatorio y baseline contiene información útil, pero algunos informes versionados declaran HEADs anteriores al checkout auditado. Estado recomendado: `PARTIALLY_CURRENT`; los contratos y pruebas son más autoritativos que un informe de estado histórico.

## Complejidad operacional

### Complejidad esencial científica — no simplificar

- aislamiento Agent/Observer y no interferencia del observatorio;
- seeds, identidad, escenarios materializados y contratos de transición;
- preregistro, lock, control y desviaciones;
- CAS/hash/provenance y artefactos append-only;
- checkpoints/restauración y distinción entre playback/reconstrucción;
- controles causales y fail-closed de forks;
- estados explícitos, cursor identificado y resync SSE.

### Complejidad esencial de ingeniería — no ocultar, sí encapsular

- SQLite/CAS, migraciones, recuperación de staging, transacciones y WAL;
- leases, idempotencia y estados de intentos de ejecución;
- validación de schemas, límites de transporte y colas SSE;
- manejo de fallas de materialización y recuperación.

### Complejidad accidental / histórica

1. Dos comandos para el mismo runner clásico (`main.py run` y `scripts/run_experiment.py`).
2. Dos planos visuales con nombres similares: sandbox/WorldStream y Scientific World2D.
3. El compositor ofrece controles que parecen ejecutar, pero termina deliberadamente antes de preregistro/autorización.
4. Un operador debe conocer hashes de raíz de preregistro para iniciar ejecución científica.
5. Vocabulario no uniforme para run, replay, world y evidence.
6. Documentación abundante por fases y contracts; es valiosa, pero difícil de navegar como manual.

### Hidden state y coupling

| Tipo | Evidencia | Impacto |
| --- | --- | --- |
| Hidden prerequisite | ejecución necesita root exacta de 64 hex, bloqueada y autorizada | HIGH |
| Hidden state | readiness, revisión, lock, autorización, revision y plan hash | HIGH |
| Hidden coupling | identidad de frame une execution/trial/attempt/cursor | ESSENTIAL, HIGH |
| Hidden coupling | playback científico depende de CAS sellada; LIVE depende de buffer en memoria | ESSENTIAL, MEDIUM |
| Duplicated decision | configuración/semillas/agent se expresan en YAML clásico y drafts/matrices Lab | MEDIUM |
| Multiple source of truth | escenarios YAML vs WorldDraft/registry; cada uno tiene un propósito distinto pero la UI debe explicarlo | MEDIUM |

## Ruta operacional canónica recomendada

```text
1. Lab: consultar World/Agent/Capability y crear o seleccionar un diseño
2. Compose: validar ExperimentDraft y TrialMatrix (no ejecuta)
3. Preregister: revisar, someter y bloquear una raíz exacta
4. Authorize: registrar autorización humana y sellar plan
5. Dispatch: iniciar y supervisar intento científico
6. Observe: LIVE científico de sólo lectura
7. Complete/verify: comprobar CAS, event chain, preregistro y desviaciones
8. Inspect: Recorded Playback, resultados crudos y análisis derivado
9. Restore/Fork: sólo cuando el contrato y la calificación lo permiten
```

La CLI clásica debe anunciarse como `Advanced / Development / Diagnostic`; no sustituye los pasos 3–7 ni debe etiquetar sus resultados como evidencia científica sellada.

## Encapsulación posible sin perder robustez

La arquitectura permite una capa de orquestación por encima de los servicios actuales:

```text
Operator-facing Experiment Studio
  -> canonical orchestration contract
     -> world + agent + protocol selection
     -> preregistration / authorization / execution state machine
     -> observer + trace + CAS
     -> LIVE, playback, derived analysis
```

Clasificación de acciones futuras:

- `SAFE_ENCAPSULATION`: wizard de progreso, etiquetas de plano, resumen de readiness y selección guiada de artefactos existentes.
- `DOCUMENTATION_ONLY`: renombrar operacionalmente Replay/Restoration y clasificar CLI.
- `UI_ORCHESTRATION`: ocultar hashes tras selección de un preregistro verificable, sin alterar la binding backend.
- `API_ORCHESTRATION`: endpoint de “next valid action” que derive estado desde servicios ya autoritativos.
- `ARCHITECTURAL_REFACTOR`: unificar el runner clásico y dispatcher; no iniciar hasta preservar contratos y evidencia.
- `DO_NOT_TOUCH`: CAS, hashes, observer isolation, preregistration lock, frame identity/atomicidad, estados/leases, checkpoint semantics y fail-closed forks.

## Veredicto

Terrario tiene una base interna robusta y una superficie operacional fragmentada. La prioridad correcta no es añadir otro motor, UI o formato de traza: es documentar y diseñar una **superficie operacional canónica** sobre el Lab existente. El mayor hueco científico no es de interfaz: el fork causal sólo está calificado para A0×D0 y no debe extrapolarse.

