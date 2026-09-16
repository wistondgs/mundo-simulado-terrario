# TERRARIO-CANONICAL-ORCHESTRATION-CONTRACT-01

**Diseño de contratos; no implementación.** Checkout `experiment/cognitive-live-observatory-01` @ `a9bfb7a`. Las modificaciones preexistentes de scripts/E2E y los documentos de auditoría/COS no se modificaron.

## Executive decision

**ORCHESTRATION_DECISION = THIN_ORCHESTRATION_FACADE.** No hace falta un segundo runner, una base de datos nueva ni un `CanonicalOrchestrator` soberano. Las autoridades ya existen. Una futura fachada delgada debe coordinar/representar contratos existentes, sin convertirse en fuente de verdad:

```text
Experiment Composer -> PreregistrationService -> ScientificExecutionService
-> ScientificExecutionDispatcher -> Observer/CAS -> verification/read models
```

El único gap que bloquea implementación es definir la interfaz de selección que transporte una preregistration root bloqueada sin pedir al operador copiar una hash; no bloquea este contrato.

## COS_OPEN_GAPS

| Gap | Etapa | Evidencia | Resolución de contrato | Bloquea |
| --- | --- | --- | --- | --- |
| Política institucional de autorización | AUTHORIZE | `ExecutionAuthorization` existe; su razón organizacional no está codificada | conservar confirmación/actor/scope; política se configura fuera | No |
| Presets seguros de recurso/observer | DESIGN/AUTHORIZE | profile y ceiling existen como inputs | sólo presets versionados y visibles; no inferir decisión científica | No |
| D1–D4 y fork | VALIDATE/FORK | `causal.py` califica sólo A0×D0 | capability-aware fail closed | No |
| Browser E2E completo | implementación futura | QA no reejecutado | gate de implementación/UX | No |
| Selección de root sin copia manual | LOCK→RUN | panel actual acepta hash | futuro selector derivado de protocolo bloqueado | Sí, para UX canónica |

## Mapa de autoridades

| Stage | Autoridad actual | Input | Output/persistencia |
| --- | --- | --- | --- |
| EXPLORE | `WorldScenarioRegistry`, `CapabilityRegistry`, `AgentInspector` | consultas | descriptores sin mutar protocolo |
| DESIGN | `ExperimentDraft` / composer | decisiones científicas | draft versionable |
| VALIDATE | `validate_draft`, world/agent contracts | draft | findings y TrialMatrix derivada |
| REVIEW | preregistration review service | draft/version | package, decisiones/attestations |
| LOCK | `PreregistrationService.lock` | revisión y root esperada | bundle/root/audit chain bloqueados |
| AUTHORIZE | `ScientificExecutionService.authorize/bind` | root bloqueada, actor, scope/ceiling | authorization vinculada |
| RUN | `ScientificExecutionService.plan/command`, dispatcher | execution con plan | leases, jobs, attempts, raw artifacts |
| OBSERVE | `ScientificLivePublisher`, ScientificFrame | identity/cursor | SSE/live frames; read-only |
| VERIFY | `ScientificExecutionService.verify` | execution ID | PASS/FAIL/INCOMPLETE/DEVIATED/ABORTED |
| REVIEW_RESULTS | CAS/read models | execution/artifacts | resultados y análisis derivado |
| PLAYBACK | trace/CAS + `OfflineReplay` | trace cursor | lectura registrada |
| RESTORATION | `CheckpointManager.restore` | checkpoint compatible | runtime restaurado |
| FORK | `CausalForkCore` | snapshot/capability/spec | ramas exactas o rechazo |

No se detectó autoridad incompatible. Composer, preregistration y execution son autoridades sucesivas, no fuentes rivales.

## Cadena de objetos canónica

```text
ExperimentDraft (mutable)
  --validate--> validated findings + TrialMatrix (derivada)
  --review/submit/lock--> PreregistrationBundle/root (inmutable)
  --request/authorize/plan--> ScientificExecutionPlan (sellado)
  --START--> execution jobs + Attempt(s)
  --run--> ScientificFrame(s), ScientificTrace, checkpoints, raw artifacts
  --complete/verify--> verification report + reviewable result set
```

| Objeto | Owner | Identidad/persistencia | Mutabilidad y fallo cerrado |
| --- | --- | --- | --- |
| ExperimentDraft | composer/persistence | artifact version | mutable hasta versión/revisión; invalid draft no llega a lock |
| TrialMatrix | composer | hash/cells derivadas | no es fuente editable alternativa |
| Preregistration | preregistration service | version/root/audit chain | lock inmutable; root/readiness incorrecta rechaza ejecución |
| ScientificExecutionPlan | execution service | plan hash, software/environment snapshot | se sella tras autorización; no se replantea en run |
| Attempt | dispatcher/execution DB | attempt/trial/execution identity | runtime durable; lease vencido lleva a recovery |
| ScientificFrame | controller/live publisher | execution/trial/attempt/sequence | observación atómica/read-only; cursor inválido resync/rechazo |
| Trace/artifact | CAS + SQLite descriptors | content hash | raw append-only; CAS inválido falla verify |
| Checkpoint | observer | step/metadata/RNG/world snapshot | restauración sólo compatible |
| Playback state | cliente | cursor local | no científico, nunca muta trace |
| Fork spec | causal core | spec/snapshot hashes | sólo capability calificada; fail closed |

## Contratos de transición

### DESIGN -> VALIDATE

**Input:** ExperimentDraft. **Precondiciones:** world, agent, controles, métricas, seeds/repeticiones y límites declarados. **Autoridad:** composer/validadores. **Output:** findings y TrialMatrix derivada. **Prohibido:** ejecutar, crear intento o convertir warnings en aprobación científica. **Idempotencia:** misma definición produce evaluación/matriz equivalente bajo contratos iguales.

### VALIDATE -> REVIEW -> LOCK

**Input:** diseño válido y revisión humana aplicable. **Autoridad:** PreregistrationService. **Output:** bundle bloqueado/root/audit chain. **Invariantes:** variables protocolarias, seeds, controls, metric, provenance/version. **Fallo cerrado:** readiness, root esperada, decisión o estado inválidos bloquean lock. **UI futura:** seleccionar el protocolo bloqueado, no reingresar su hash.

### LOCK -> AUTHORIZE -> PLAN

**Input:** root bloqueada verificable, actor, scope/recursos. **Autoridad:** ScientificExecutionService. **Output:** authorization vinculada, environment/software snapshot y plan hash sellado. **Fallo cerrado:** root no bloqueada, worktree/entorno no permitido, autorización incompatible o revision obsoleta. **No automatizar:** confirmación de autorización ni su alcance material.

### PLAN -> RUN -> ATTEMPT

**Input:** execution plan sellado. **Autoridad:** `command(START)` y dispatcher. **Output:** lease, jobs, attempt identificado, observer/trace/LIVE. **Atomicidad:** consume authorization y adquiere lease en transición protegida; dispatcher reclama job idempotentemente. **Prohibido:** editar plan, protocolo o identidad durante run.

### ATTEMPT -> OBSERVE -> COMPLETE

**Input:** attempt activo. **Autoridad:** controller/observer/live/dispatcher. **Output:** frames, `SCIENTIFIC_TRACE`, `TRIAL_RESULT`, estado durable. **Invariantes:** Agent/Observer separation, frame identity/atomicidad, transporte bounded, CAS antes de terminal. Un fallo de materialización no se presenta como trayectoria científica completa.

### COMPLETE -> VERIFY -> REVIEW

**Input:** execution terminada y sus artefactos. **Autoridad:** execution verify/read models. **Output:** VerificationClass y resultados revisables. **Verifica:** event chain, CAS, preregistration, plan, execution root y deviations. **No concluye:** hipótesis confirmada, aprendizaje, causalidad o transferencia.

## Comandos y queries canónicos

| Comando humano | Mapeo existente | Precondición |
| --- | --- | --- |
| Validate experiment | composer validate | draft completo |
| Review protocol | preregistration review/readiness | draft/version |
| Lock protocol | preregistration lock | review/root/decisión válida |
| Authorize and run | request + authorize + bind + plan + START | root locked y confirmación |
| Pause / Resume / Cancel | execution command | state legal |
| Verify run | execution verify | execution existente |
| Restore state | checkpoint restore | checkpoint compatible |
| Fork | causal core | `EXACT_FORKABLE` |

Queries: Explore worlds/agents/capabilities; list locked protocols; run status; live frames; verification; artifacts; playback; recovery status. IDs/hashes/cursors sólo se muestran en Scientific Detail/Engineering Diagnostics.

## Estado canónico

Internos: 14 `ExecutionState` (`REQUESTED`…`RECOVERY_REQUIRED`). Proyección canónica: `READY_TO_RUN`, `RUNNING`, `PAUSED`, `NEEDS_ATTENTION`, `COMPLETED`, `FAILED`. Cada estado visible debe enlazar a los estados/eventos internos exactos; no se reemplaza la state machine.

## Capability, recovery y concurrencia

`CapabilityRegistry` y contracts de runtime son fuente de verdad de acciones disponibles. No mostrar Fork, Restoration o campos cognitivos inexistentes; mostrar razón y contrato cuando estén indisponibles. Leases, expected revision, command IDs, transactions SQLite y claims de job siguen internos pero auditables. `RECOVERY_REQUIRED` no reanuda en silencio; exige operación explícita.

## Fronteras preservadas

- CLI: compatible, marcada advanced/development/diagnostic; nunca sustituye cadena científica.
- API: futura fachada sólo compone APIs/servicios existentes; no duplica autoridad.
- Frontend: queda fuera de esta fase; recibirá commands/queries y estados canónicos aprobados.
- Sandbox: `NOT EVIDENCE` preservado y separado de Scientific Run.
- Epistemología: System State -> Observation -> Measurement -> Derived Analysis -> Claim conserva fronteras y provenance.

## Implementation gates

1. Contrato de selector de protocolo bloqueado y derivación de root verificable.
2. Mapeo tested de cada comando canónico a servicio/estado/evento existente.
3. Proyección de estado sin ocultar recovery, deviation o failure.
4. Capability response contractual para fork, restoration y observatorio.
5. Pruebas de provenance/idempotencia/concurrencia para la futura fachada.
6. UX copy que separe Sandbox, Run verified y claim científico.

## Veredicto

Terrario ya tiene las autoridades necesarias. La implementación futura debe ser una fachada delgada de comandos, queries y proyecciones; crear un segundo runner, service layer soberano o fuente de verdad sería una regresión arquitectónica.

