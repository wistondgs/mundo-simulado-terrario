# TERRARIO-CANONICAL-OPERATIONAL-SURFACE-01

**Tipo:** especificación de diseño; no implementación.  
**Checkout:** `experiment/cognitive-live-observatory-01` @ `a9bfb7a585fe20091821f0e1d920a31956001282`.  
**Estado del worktree al inicio:** cambios preexistentes en `scripts/seed_scientific_live_e2e.py` y `tests_frontend/e2e/scientific-live.spec.js`; documentos de auditoría no rastreados. No se atribuyen ni se modifican.

## 1. Executive Decision

`Scientific Lab` es la superficie operacional canónica propuesta para experimentos científicos. La CLI clásica se preserva como `ADVANCED / DEVELOPMENT / DIAGNOSTIC`. Esta decisión se apoya en wiring existente: sólo Lab conecta composición, preregistro, autorización, plan sellado, intentos, CAS/SQLite, LIVE y verificación. La CLI construye `ExperimentConfig` y llama directamente a `ExperimentRunner`; no sustituye esos controles.

**No se crea una abstracción nueva.** El núcleo conceptual existente es la cadena:

```text
ExperimentDraft -> validated TrialMatrix -> locked Preregistration
-> ScientificExecution + Authorization -> sealed ScientificExecutionPlan
-> Attempt(s) -> raw artifacts / verification -> review
```

Evidencia: `lab/experiment_composer.py`, `lab/preregistration/service.py`, `lab/execution/{domain,service,dispatcher}.py`, `main.py`.

## 2. Problema operacional actual

El operador ve conceptos pertenecientes a tres responsabilidades distintas: decisiones científicas, guardrails de seguridad e internals de ejecución. Además, coexisten CLI, sandbox/WorldStream y Scientific Lab. Sin una semántica explícita, “run”, “world”, “replay” y “evidence” parecen equivalentes cuando no lo son.

La solución no es retirar CAS, hashes, lock, leases, checkpoints, observer o SSE. Es encapsular su manipulación ordinaria y exponerlos como detalle inspeccionable.

## 3. Principios de diseño

1. **Declare once, derive everywhere else.** Scenario, agente, control, semillas, métricas y límites se declaran una vez en el diseño; las capas posteriores los derivan y los vinculan.
2. **Una ruta primaria.** La ejecución científica sólo parte de un protocolo bloqueado y autorizado.
3. **Progresive disclosure.** Operación, detalle científico y diagnóstico de ingeniería son niveles distintos.
4. **Fail closed.** Una capacidad no calificada no aparece como operación disponible.
5. **Encapsulación auditable.** Todo valor derivado conserva input, derivación, output y provenance inspeccionable.
6. **Firewall epistemológico.** Estado, observación, medición, análisis y claim científico nunca se promocionan automáticamente.
7. **No modificar semántica existente.** La propuesta es una proyección sobre contratos actuales.

## 4. Modelo canónico de usuario

El operador trabaja con cuatro sustantivos principales:

```text
Experiment  - qué se quiere comparar y por qué
Protocol    - la versión revisada y bloqueada del experimento
Run         - una ejecución científica del protocolo
Review      - inspección de resultados, integridad y análisis
```

Las entidades internas (`CAS object`, `lease`, `attempt id`, cursor SSE, plan hash) no son decisiones ordinarias. Permanecen accesibles en diagnóstico y provenance.

## 5. Vocabulario canónico

| Término | Definición operacional | Alias interno / no confundir |
| --- | --- | --- |
| Experiment | definición modificable de pregunta, condiciones y medición | `ExperimentDraft`; no es un Run |
| Protocol | versión revisada y bloqueada que fija el experimento | preregistration root; no es sólo YAML |
| Run | ejecución científica autorizada de un Protocol | `ScientificExecution`; no es sandbox ni CLI clásica |
| Attempt | unidad concreta de trabajo dentro de un Run | `run_attempt`; no es un experimento nuevo |
| Result | artefacto crudo y métricas de un Run | no es claim científico |
| Recorded Playback | lectura de traza ya registrada | antes “replay”; no reejecuta |
| State Restoration | restauración de checkpoint ejecutable | no es playback visual |
| Sandbox | entorno de exploración/ingeniería | `WorldStream`; siempre NOT EVIDENCE |
| Scientific Frame | frame atómico observado de un Attempt | no es estado interno completo del Agent |
| Fork | comparación causal desde snapshot calificado | sólo A0×D0 exacto hoy |
| Evidence | conclusión que pasa proceso científico | raw artifact/CAS no es Evidence |

## 6. Ruta operacional canónica

```text
EXPLORE -> DESIGN -> VALIDATE -> REVIEW & LOCK -> AUTHORIZE & RUN
-> OBSERVE -> VERIFY -> REVIEW RESULTS
                         -> Recorded Playback
                         -> State Restoration/Fork if capability permits
```

| Etapa | Acción del operador | Acción derivada del sistema | Salida |
| --- | --- | --- | --- |
| Explore | inspeccionar worlds, agents, capacidades y restricciones | filtrar por capability | selección informada, sin estado científico |
| Design | declarar pregunta, mundo, agentes, controles, métricas y política de seeds | construir ExperimentDraft | Draft mutable |
| Validate | solicitar validación | compatibilidad, matriz y warnings | Draft validado o errores |
| Review & Lock | revisar protocolo y confirmar lock | versionar, hash, root y provenance | Preregistration bloqueado |
| Authorize & Run | confirmar alcance/recursos y Start | autorización, plan, lease, attempts, observer y trace | Scientific Run |
| Observe | leer estado live | SSE/resync/frame projection | observación no invasiva |
| Verify | solicitar Verify Run | CAS, event chain, binding, artifacts, deviations | PASS/FAIL/DEVIATED/INCOMPLETE |
| Review | interpretar resultados y análisis | discover artifacts/playback | revisión humana |

No hay atajo canónico de Design a Run. La CLI puede seguir ejecutando un experimento clásico, pero su resultado se clasifica como avanzado y no como Run científico sellado.

## 7. Navegación conceptual

La navegación propuesta se organiza por objetivo humano, no por paquetes Python:

```text
Explore       Worlds, Agents, Capabilities, Sandbox
Experiments   Design, Validate, Protocol review, Locked protocols
Runs          Active runs, Observe, Verify, Recovery
Review        Results, Playback, Restoration, comparisons, exports
Advanced      CLI guidance, diagnostics, IDs/hashes/CAS/leases/SSE
```

`Sandbox` debe estar visiblemente separado dentro de Explore y conservar `ENGINEERING SANDBOX · NOT EVIDENCE`. Scientific World2D pertenece a Runs/Review, no a Sandbox.

## 8. Contrato de Experiment Definition

El objeto central existente es `ExperimentDraft`, con `TrialMatrix` derivada. No se propone reemplazarlo.

| Campo | Exposición | Razón |
| --- | --- | --- |
| pregunta/fuente de hipótesis | REQUIRED | decisión científica |
| scenario/world variant | REQUIRED | variable experimental |
| target agent y control | REQUIRED | comparación y control |
| condiciones/intervenciones | REQUIRED cuando aplican | diseño causal |
| métricas | REQUIRED | define medición |
| policy de seeds/repeticiones | REQUIRED | parte del protocolo |
| step limit/termination | REQUIRED o derivado por scenario | afecta muestra y comparabilidad |
| observer profile | REQUIRED con defaults explicados | alcance de observación/coste |
| análisis intent | OPTIONAL, pero persistible | guía revisión, no claim automático |
| device/resource tuning | ADVANCED | ingeniería, sujeto a autorización |
| matrix cell IDs, hashes, CAS IDs | INTERNAL | derivados |

`TrialMatrix` se deriva una sola vez del draft validado. Si cambia un input protocolar, se invalida la matriz derivada; no se edita una celda como fuente de verdad paralela.

## 9. Contrato de validación

La validación debe responder automáticamente: configuración válida, agent/scenario compatibles, controles presentes, métricas disponibles, seeds/repeticiones válidas, profile de observer disponible y capacidad de fork/restoration si se solicitó.

Debe distinguir:

```text
CONFIGURATION_VALID  = contratos y restricciones satisfechos
SCIENTIFICALLY_STRONG = juicio humano sobre hipótesis, confusores y diseño
```

El sistema puede bloquear lo primero y advertir sobre lo segundo; no puede certificar una hipótesis por validación sintáctica.

## 10. Contrato de preregistro y lock

La acción visible es:

```text
Review protocol -> Lock protocol
```

El sistema deriva y persiste root hash, versiones, CAS identity, audit chain y provenance. La root hash se muestra como identificador copiable y en nivel científico/detalle, pero no debe ser una primitiva que el operador transcriba para avanzar entre pantallas. Una selección de “protocolo bloqueado verificable” debe transportar el binding exacto.

No se automatiza lock: es una `SAFETY_DECISION` con confirmación explícita y resumen inmutable de variables, controles, seeds y métricas.

## 11. Contrato de autorización

La autorización protege el consumo de ejecución y vincula root de preregistro, scope, cuota, recursos, actor y expiración. Es principalmente una `SAFETY_DECISION`/política operacional; no es una conclusión científica ni debe confundirse con lock.

La superficie propuesta muestra un resumen de protocolo y recursos, seguida de **Authorize and run**. El sistema crea/vincula `ExecutionAuthorization`, verifica readiness y sella plan. Los campos de scope, cuota y ceilings se mantienen visibles en detalle científico; presets aprobados pueden reducir su edición ordinaria sin perder registro de qué preset se usó.

## 12. Contrato de ejecución

Al pulsar Run, el sistema ejecuta internamente:

```text
create ScientificExecution -> bind authorization -> seal plan
-> consume authorization -> create lease/jobs/attempts
-> initialize runner, observer, trace, persistence and LIVE
```

El operador ve protocolo, estado, progreso, warnings, controles disponibles y recovery. No administra lease owner, command id, internal attempt id, CAS path ni cursor SSE.

El estado interno actual se conserva en `ExecutionState`: `REQUESTED`, `VALIDATING`, `AUTHORIZED`, `PLANNED`, `READY`, `RUNNING`, `PAUSING`, `PAUSED`, `STOPPING`, `COMPLETED`, `FAILED`, `CANCELLED`, `ABORTED`, `RECOVERY_REQUIRED`.

Proyección operacional propuesta:

| Visible | Estados internos | Acción |
| --- | --- | --- |
| Ready to run | REQUESTED/VALIDATING/AUTHORIZED/PLANNED/READY | resolver bloqueos o Start |
| Running | RUNNING/PAUSING/STOPPING | Observe; pause/cancel según contrato |
| Paused | PAUSED | Resume o Cancel |
| Needs attention | RECOVERY_REQUIRED | Recovery guiada, con detalle |
| Completed | COMPLETED | Verify Run y Review |
| Failed | FAILED/CANCELLED/ABORTED | diagnóstico, impacto y recuperación |

La proyección no elimina detalles: enlaza a la transición/evento interno que justifica el estado.

## 13. Contrato de observación

La vista primaria de una ejecución activa muestra:

```text
World view, progress, runtime status, protocol identity,
agent identity, selected metrics, warnings and ScientificFrame summary
```

El detalle científico permite observer view, cognitive projection, trace cursor y frame identity. Diagnóstico permite SSE cursor, retention/resync, attempt ID y transporte. La observación no ofrece controles que modifiquen world, agent, seed, protocol o runtime fuera de comandos autorizados de ejecución.

`OBSERVATION != INFERENCE != SCIENTIFIC CONCLUSION`. La UI no etiqueta estados como “understands”, “intelligence gained” o “learned causality”.

## 14. Contrato de verificación

La acción visible es **Verify Run**. Agrupa:

```text
completion, event-chain integrity, CAS integrity,
preregistration binding, execution root, plan availability and deviations
```

Sus resultados son `PASS`, `FAIL`, `INCOMPLETE`, `DEVIATED`, `ABORTED` o `UNVERIFIABLE`. Debe mostrar qué verificó, qué falló, qué artefactos siguen disponibles y qué interpretación queda prohibida.

```text
RUN VERIFIED != HYPOTHESIS CONFIRMED
```

## 15. Contrato de review

Review responde: qué protocolo se ejecutó, con qué agente/mundo/controles/seeds, qué intentos existieron, qué métricas y desviaciones hay, qué artefactos se preservaron y qué operaciones están disponibles. Es la entrada canónica a análisis derivado, comparación, exportación y playback.

Un raw artifact sigue siendo raw artifact. La promoción de measurement a scientific claim requiere un plan de análisis y revisión humana fuera de la automatización de ejecución.

## 16. Playback, restoration y fork

| Operación | Cuándo se muestra | Contrato visible |
| --- | --- | --- |
| Recorded Playback | existe traza legible | navegación read-only sobre lo registrado |
| State Restoration | existe checkpoint compatible | restauración ejecutable, impacto y compatibilidad explícitos |
| Fork | capability contract lo permite | ramas, control/intervención y calificación |

Fork es capability-aware: hoy `A0_RANDOM × d0_differences.yaml` puede indicar `Fork available`; los demás pares indican `Fork unsupported`, no un botón fallido. Restoration no se ofrece si no existe checkpoint compatible. Playback nunca se presenta como reejecución.

## 17. Progressive disclosure

| Nivel | Expone | Oculta por defecto |
| --- | --- | --- |
| Operational | objetivo, protocolo seleccionado, progreso, acciones seguras, resultados | hashes, leases, IDs, cursor SSE |
| Scientific detail | controles, métricas, seeds, provenance, deviations, frame summary | mecánica de CAS/colas salvo necesidad |
| Engineering diagnostics | IDs, hashes, CAS, attempts, event chain, cursor, lease, transport | nada; es inspección experta |

La información nunca desaparece y ninguna automatización impide verificar su derivación.

## 18. Decisiones humanas y automatización

| Decisión actual | Clase | Superficie canónica | Automatizable | Riesgo de ocultar |
| --- | --- | --- | --- | --- |
| hipótesis/pregunta | SCIENTIFIC | Design | No | crítico |
| scenario, agente, control, métricas | SCIENTIFIC | Design | No | crítico |
| seeds, repeticiones, límites | SCIENTIFIC | Design; defaults auditables | parcialmente | alto |
| observer profile | SCIENTIFIC/OPERATIONAL | Design | default explicable | medio |
| lock protocol | SAFETY | Review & Lock | No | crítico |
| autorización y recurso | SAFETY | Authorize & Run | presets sí, confirmación no | alto |
| plan hash/root/CAS ID | DERIVED | Detail | Sí | bajo si inspectable |
| TrialMatrix | DERIVED | Design review | Sí | medio |
| attempts, leases, command IDs | ENGINEERING | Diagnostics | Sí | bajo |
| SSE cursor/resync | ENGINEERING | automático | Sí | bajo |
| verification command | OPERATIONAL | Verify | disparo sí; interpretación no | alto |
| causal claim | SCIENTIFIC | Review | No | crítico |

Violaciones actuales de Declare Once: YAML clásico y ExperimentDraft expresan configuraciones parecidas; la root hash debe copiarse manualmente al panel de ejecución; entidades de UI/sandbox y runtime pueden mostrar agentes/scenarios sin una selección protocolar común. La futura capa debe derivar una única selección, no fusionar fuentes sin contrato.

## 19. Fuentes de verdad operacionales

| Entidad | Autoridad | Mutable hasta | Derivados/consumidores |
| --- | --- | --- | --- |
| World/Scenario | YAML versionado + registry/WorldDraft según plano | WorldDraft hasta validación; YAML por Git | preview, sandbox, draft, runtime |
| Difficulty | configuración de scenario/WorldDraft | lock de protocolo | matrix, runtime |
| Agent | factory/CapabilityRegistry | lock de protocolo | identity, compatibility, runtime |
| Experiment Definition | ExperimentDraft | validación/versión posterior | TrialMatrix, preregistration |
| Protocol | Preregistration bloqueado | lock | authorization, plan |
| Execution plan | ScientificExecutionPlan sellado | nunca después de seal | jobs, attempts |
| Runtime | ScientificExecution + jobs/attempts | state machine | LIVE, recovery |
| Trace/result | CAS descriptors y SQLite | append-only | playback, verify, review |
| Playback state | cursor UI local | libre, no científico | viewer únicamente |

## 20. Error model

| Clase | Mensaje obligatorio |
| --- | --- |
| USER_CORRECTABLE | qué campo/selección corregir; no se creó Run |
| PROTOCOL_ERROR | qué contrato no permite lock/plan; impacto en protocolo |
| CAPABILITY_UNAVAILABLE | por qué no está calificado; alternativas no científicas si existen |
| SCIENTIFIC_WARNING | confusor o limitación; no ocultar ni bloquear sin razón contractual |
| RUNTIME_FAILURE | intento afectado, artefactos preservados y siguiente paso |
| INTEGRITY_FAILURE | verificación fallida, qué no puede afirmarse |
| RECOVERY_REQUIRED | lease/sesión afectada, recovery explícita disponible |
| INTERNAL_ERROR | correlación/ID de diagnóstico; no culpar al operador |

## 21. Invariantes preservados

Toda encapsulación debe preservar deterministic identity, semantics de seeds, Agent/Observer separation, identidad/atomicidad de ScientificFrame, preregistration lock, provenance, CAS/hash integrity, append-only artifacts where applicable, checkpoint semantics, trace integrity, SSE resync, execution state machine, authorization/lease/recovery semantics y causal forks fail-closed.

## 22. Frontera de automatización y auditabilidad

| Automatización | Input | Output/provenance | Inspección |
| --- | --- | --- | --- |
| matrix | ExperimentDraft validado | TrialMatrix hash/celdas | Design detail |
| lock identity | protocolo revisado | root/hash/audit chain | Protocol detail |
| plan | root bloqueada + autorización | plan hash, environment/software snapshot | Run detail |
| capability filtering | agent/world/protocol/runtime | acciones disponibles + razón | capability panel |
| run infrastructure | plan sellado | attempts, leases, observer/trace | diagnostics |
| LIVE reconnection | frame identity/cursor | resync state | diagnostics |
| artifact discovery | execution root | lista de artefactos | Review |

No automatizar: selección de hipótesis, controles científicos significativos, interpretación, cambios retroactivos de métrica, aprobación de desviaciones ni confirmación de claims.

## 23. CLI avanzada

| Función | Rol futuro |
| --- | --- |
| `main.py run` / `scripts/run_experiment.py` | desarrollo y comparación directa; documentar duplicación |
| `main.py verify` | diagnóstico/reproducibilidad |
| `main.py ablate` | análisis avanzado |
| CLI preregistration | operación experta/automatización local |
| H-ADAPT | campaña experimental con requisitos de entorno |

No romper CLI, protocolos, traces, checkpoints, API consumers ni CAS. La diferencia es semántica de superficie, no eliminación.

## 24. Compatibilidad y migración conceptual

Fase A: declarar Lab como canónico y CLI como avanzada.  
Fase B: introducir vocabulario y selección derivada de protocolo.  
Fase C: consolidar navegación por Explore/Experiments/Runs/Review.  
Fase D: capability-aware actions y diagnóstico progresivo.  
Fase E: marcar rutas duplicadas como legacy operacional, sin borrarlas.

Son dependencias de diseño, no calendario ni autorización de implementación.

## 25. Gates para la futura implementación

No implementar antes de aprobar:

1. mapa exacto `ExperimentDraft -> TrialMatrix -> preregistration -> plan -> attempt`;
2. contrato de selección de protocolo bloqueado sin copiar root hash manualmente;
3. proyección operacional de estados con trazabilidad a `ExecutionState`;
4. contrato capability-aware para fork/restoration/cognitive fields;
5. etiquetado imposible de confundir entre Sandbox y Scientific Run;
6. pruebas de que automatización preserva provenance y no debilita locks/authorization;
7. revisión humana de copy para no promover observación a claim.

## 26. Open questions

- La política organizacional exacta que exige autorización humana requiere una decisión explícita; el código implementa el mecanismo, no su justificación institucional completa.
- D1 movement y la madurez científica D2–D4 requieren calificación por protocolo, no sólo una UI capability flag.
- No se ejecutó QA completa/browser E2E en esta fase de diseño.
- Debe decidirse qué presets de recursos/observer pueden automatizarse sin sustituir una decisión científica.

## Veredicto

La arquitectura actual permite una superficie canónica sin reducir robustez ni crear otra plataforma. El siguiente paquete correcto es `TERRARIO-CANONICAL-ORCHESTRATION-CONTRACT-01`: traducir esta especificación aprobada a contratos, antes de tocar frontend, API o runner.

