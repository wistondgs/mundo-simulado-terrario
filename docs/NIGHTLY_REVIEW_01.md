# NIGHTLY-REVIEW-01 · 2026-09-16

**Encargo:** «realiza toda la revisión nocturna… vamos a hacer las corridas para seguir
detectando aún más defectos».
**Regla observada:** ninguna corrida tocó el root científico vivo. Verificado al principio y al
final: `.terrario/terrario.db` sigue en `5527cf7b…`, con 283 solicitudes, 283 decisiones y 141
ejecuciones — idéntico.
**Nada de lo aquí producido es evidencia científica.**

---

## 1. Corridas ejecutadas

| Suite | Resultado | Tiempo |
|---|---|---|
| `pytest` completo (antes del arreglo del tutorial) | **560 pasan · 1 skip · 1 falla** de 562 | 10 min 54 s |
| `pytest` completo (después) | **560 pasan · 1 skip · 1 falla** — idéntico, cero regresiones | 10 min 09 s |
| Playwright e2e, corrida 1 | 111 pasan · 2 fallan de 113 (D-02) | 5 min 42 s |
| Playwright e2e, corrida 2 (tras reparar D-02) | 112 pasan · 1 falla — **otra distinta** (D-03) | 5 min 48 s |
| Playwright e2e, corrida 3 (tras reparar D-03) | **113 / 113 en verde** | 5 min 36 s |
| Barrido diagnóstico Fase 1 (58 pasos) | 55/58 → reparado | 2 min 42 s |
| Barrido completo con `tools` (68 pasos) | 65/68 → reparado → **67/68** | 3 min 10 s |
| Grupo `tools` reverificado | **10/10** | — |
| Matriz A×D (5 agentes × 8 escenarios) | **40/40 celdas arrancan y terminan** | 114 s |
| `pytest` en contenedor (gate de conducta deseleccionado) | **559 pasan · 1 skip · 1 falla** de 561 | 15 min 55 s |
| Guard del root vivo | `unchanged (guard passed)` en las tres corridas de pytest | — |

El único rojo persistente es `test_protected_source_and_historical_artifact_hashes_match_baseline`,
que es una decisión humana pendiente, no un fallo (§2).

---

## 2. La decisión A/B de la línea base: resuelta por evidencia

Solo **2 archivos de 70** derivaron respecto de la base `410b2693`:
`terrario/agent/scientific.py` (+169) y `terrario/experiment/controller.py` (+58).

Los otros cuatro tests del mismo archivo **pasan**, incluidos
`test_d2_d3_d4_a0_a1_a4_match_checked_in_behavior` y
`test_same_case_repeats_semantically_byte_for_byte`. **El fuente cambió; la conducta no.**

Y las 227 líneas añadidas son `_observer_decision_trace` y `_observer_planner_proposal_trace`,
cuyos campos coinciden uno a uno con los `required_event_fields` de `planning_trace_metric.py`:

> **Esas líneas SON el instrumento que mide CL-7.** La opción A (restaurar) dejaría la métrica
> `planned-action-evaluation-pathway` sin vía de observación.

**Recomendación: opción B**, nueva línea base `system_baseline_03`, con el diff y este
razonamiento adjuntos. No es «hacer verde la prueba»: es rebaselinar con revisión formal, la
segunda alternativa que el propio autor planteó. **La firma sigue siendo humana.**

---

## 3. Defectos encontrados

### D-01 · El ciclo de vida del lease está incompleto por los dos extremos — ALTO

En el root vivo hay **3 ejecuciones en `RUNNING` desde el 2026-09-14**, con leases que vencieron
entre 60 y 81 segundos después de crearse. Llevan dos días mostrándose como «en ejecución».

Tres piezas de un mismo ciclo existen y ninguna se dispara:

| Pieza | Existe | Se invoca |
|---|---|---|
| `renew_lease()` | sí | **nunca** — ni en producción ni en tests |
| `fail()` | sí | **nunca** — ni en producción ni en tests |
| `recover_expired_leases()` + `POST …/recover` | sí | **nunca automáticamente** |

Consecuencias encadenadas:

1. El lease dura 60 s y nadie lo renueva: **toda** ejecución de más de un minuto corre con lease
   vencido. La única `COMPLETED` del root vivo duró 2 h 37 min.
2. Cuando un ensayo falla, `dispatcher.py` marca el *job* y el *attempt* como fallidos, pero la
   *ejecución* se queda en `RUNNING`: `ExecutionService.fail()` no lo llama nadie.
3. `RECOVERY_REQUIRED` solo lo produce `recover_expired_leases`. Está declarado en el dominio, en
   `EXECUTION_STATE_MACHINE.md` y hasta tiene clase CSS en `workspace.css` — y es **inalcanzable**
   en operación normal.

Resultado: una ejecución solo puede salir de `RUNNING` completándose. El panel dice «3 corriendo»
cuando la respuesta verdadera es «3 abandonadas hace dos días».

**Y hay un segundo lease, igual de incompleto.** `execution_jobs` tiene columna
`lease_expires_at` y **nadie la escribe jamás**: 0 filas de 248 la tienen puesta. El dispatcher
solo fija `lease_owner` al reclamar (`dispatcher.py:54`). Consecuencia visible en el root vivo:

```
job execution-job-57716b6c…  CLAIMED  owner=e2e-worker  expira=NULL  desde 2026-09-14T17:26
job execution-job-216aed75…  CLAIMED  owner=e2e-worker  expira=NULL  desde 2026-09-14T17:26
```

Dos trabajos reclamados por un worker de pruebas que murió hace dos días. Sin expiración, nada
puede reclamarlos nunca. Nótese el propietario: `e2e-worker` — son restos de la contaminación,
anteriores al aislamiento.

**Corolario operativo:** el aislamiento detuvo la hemorragia, pero **los escombros siguen ahí**:
137 ejecuciones `READY`, 3 `RUNNING`, 2 trabajos `CLAIMED` y 282 solicitudes de revisión de
prueba. Limpiarlos es una decisión aparte, y humana: son filas de un almacén append-only.

**No aplico el arreglo:** tocar la máquina de estados de ejecución científica es decisión humana.
Propuesta mínima: invocar `recover_expired_leases` al arrancar la API y exponer el botón en la UI
(el estado ya tiene estilo); después, renovar el lease desde el worker.

### D-02 · Un test e2e acoplado al estado científico vivo — ALTO · **REPARADO**

`tests_frontend/e2e/cl7-human-review-entry.spec.js` tenía dentro, a fuego:

```
review-82c0a332b5524f1f9907aa0d5ce2c067
ac03a38f909efab73cea98efa1cc439215464d4b43ab2bc07dcb8f0150b21770
```

Es decir: el id de revisión y el hash de diseño **reales** de CL-7. Tres problemas:

1. Solo pasaba mientras la suite corriera contra el `.terrario` vivo — el test *codificaba* la
   contaminación que cerramos.
2. Escribía en el formulario de ceremonia de **una revisión humana real y pendiente**.
3. Se rompió en cuanto el científico hizo su trabajo y decidió esa revisión.

**Reparado.** Nuevo `scripts/seed_pending_design_review_e2e.py` siembra su propia revisión
pendiente en el root de pruebas; el spec descubre el id y el hash dinámicamente. Verde en
Chromium y Firefox. El contrato que prueba —la ceremonia es obligatoria— queda intacto.

### D-03 · Carrera asíncrona en la paleta de comandos — ALTO · **REPARADO**

Detectado porque un test pasó en una corrida y falló en la siguiente. No era un test
intermitente: era un defecto real de la interfaz.

`PaletteView._update()` es `async` y lanza una búsqueda de referencias por **cada pulsación**,
sin secuenciar. Escribir «pin snapshot» deja unas once peticiones en vuelo que **resuelven en
desorden**: la última en llegar pinta la lista, aunque corresponda a un prefijo anterior.

Y el primer comando de la lista depende del prefijo:

```
"p"            -> primer comando: "Open reference"          (necesita argumento)
"pin snapshot" -> primer comando: "Pin snapshot / toggle mode"
```

Por tanto **Enter podía ejecutar un comando que el operador nunca eligió.** En una interfaz
científica eso es grave: la acción registrada no es la acción pretendida.

**Reparado** con un testigo de secuencia (`_updateToken`): una respuesta vieja se descarta en
lugar de repintar. Detalle importante durante el arreglo: sin inicializar el contador en el
constructor, `++undefined` da `NaN` y `NaN !== NaN` es siempre cierto — habría descartado
*todas* las actualizaciones y roto la paleta entera. Inicializado y verificado.

El test también se endureció: ahora comprueba **qué** comando está primero antes de pulsar Enter,
en vez de conformarse con que la lista tenga algo. Tres corridas seguidas en verde.

### D-04 · La config de fábrica pide un dispositivo que el manifiesto declara bloqueado — MEDIO

`configs/default.yaml` fija `device: "cuda"`. El manifiesto declara `CUDA_OS_BLOCKED`. El comando
que aparece en el propio docstring de `main.py` falla:

```
AgentFactoryError: Requested device 'cuda' is unavailable: cuda_requested_but_unavailable
```

El fallo es **correcto** —falla cerrado, en 1,6 s, con mensaje exacto— y el Lab además lo bloquea
antes (`BLOCKED_CUDA` en el composer). El defecto es de puerta de entrada: lo primero que alguien
teclea no arranca. Una línea: `device: "cpu"`.

### D-05 · Colisión de etiquetas entre medición y atestación — MEDIO

En `demonstrate_cl7_runtime_readiness.py`, dos líneas seguidas:

```
SCIENTIFIC_RESULTS: 0     <- medición del root de datos
SCIENTIFIC_RESULT: NO     <- literal, atestación del propio script
```

Un carácter de diferencia, significados distintos, nada que distinga lo medido de lo declarado.
El script **no miente** (abre la base en `mode=ro`), pero es exactamente la clase de ambigüedad
que produjo un «no le entiendo».

### D-06 · `verify()` no es idempotente — MEDIO · propuesto, sin aplicar

Verificar dos veces la misma ejecución devuelve `500 UNIQUE constraint failed`. En la UI, el
segundo clic en «Verify integrity» falla. Parche propuesto en `CL7_PAIRED_SCRATCH_RUN_01.md` §4.

### D-07 · Cuatro scripts no encuentran su propio paquete — MEDIO · **REPARADO**

Veinte de los veinticinco scripts insertan la raíz del proyecto en `sys.path` antes de importar
`terrario`. Cuatro no lo hacían:

| Script | Síntoma |
|---|---|
| `cross_graph_performance.py` | `ModuleNotFoundError: No module named 'terrario'` al invocarlo directamente |
| `reference_graph_performance.py` | igual |
| `tutorial_scientific_chain.py` | igual — y es **la rampa de entrada**; el doc lo compensaba pidiendo `PYTHONPATH=.` |
| `run_cl7_paired_scratch.py` · `seed_scientific_live_e2e.py` | funcionaban solo porque quien los llama fija `PYTHONPATH` |

Python pone en `sys.path[0]` el directorio del *script*, no el directorio de trabajo, así que
`cd` a la raíz no basta. Los cuatro alineados con el idioma de los otros veinte; el tutorial
ya no necesita prefijo y su documentación se actualizó. Grupo `tools` del barrido: **10/10**.

### D-08 · Código muerto en el servicio de ejecución — BAJO

Sin llamadas en producción: `runtime.identity_hash` (tampoco en tests),
`crossgraph.service.cached_query` (solo en tests — la caché nunca se usa).

---

## 3bis. Docker: la hipótesis del contenedor, ahora medida

`docs/DOCKER_HARNESS.md` afirmaba que el único coste de la rueda CPU de torch sería el gate de
caracterización de conducta, deseleccionado por nombre. **Medido:**

| | tests | pasan | skip | fallan |
|---|---:|---:|---:|---:|
| Host | 562 | 560 | 1 | 1 |
| Contenedor (1 deseleccionado) | 561 | **559** | 1 | 1 |

560 − 559 = 1, **exactamente el test deseleccionado**. La hipótesis queda confirmada con número:
la rueda CPU no cuesta nada más. El único fallo en ambos lados es el mismo gate de hashes
protegidos (§2).

Coste en tiempo: **15 min 55 s** en contenedor frente a **10 min 09 s** en host — factor **1,57×**.

El guard del root vivo también pasó dentro del contenedor, lo que confirma que el volumen
nombrado sombrea de verdad el `.terrario` del host.

## 4. Lo que está sano, y conviene saberlo

- **La matriz A×D corre entera: 40/40.** Los dos ejes del experimento son ejecutables hoy.
- **560 de 562 tests pasan**, y el guard del root vivo funcionó en ambas corridas.
- **113/113 e2e** tras la reparación, en dos navegadores.
- **El aislamiento del root vivo aguanta**: tras dos suites completas de e2e, el hash no se movió.
- Los tres fallos del primer barrido fueron **dos errores míos de invocación** y un defecto real
  (D-03). Los scripts fallaron cerrado, que es lo correcto.

---

## 5. Documentación producida

| Documento | Qué cierra |
|---|---|
| `AGENT_AND_WORLD_LADDER.md` | A0–A4 y D0–D4 se mencionaban en 7 docs y no se explicaban en ninguno; son la variable independiente y la demanda ambiental del proyecto |
| `CORPUS_SUFFICIENCY_REVIEW_01.md` | el corpus, medido y corregido (§6) |
| `CORPUS_ACQUISITION_LIST_01.md` | qué falta leer, por prioridad, mapeado a cada escalón |

---

## 6. Corpus: 152 catalogadas, 65 obtenidas, 100 % de lo legalmente obtenible

`BUILD_REPORT.json`: `records: 152`, `records_with_copy: 65`;
acceso: `PUBLIC_DOMAIN 17 + OPEN 48 = 65`, `RESTRICTED 87`.

**La tasa de adquisición sobre lo obtenible legalmente es del 100 %.** Las 87 restantes están
documentadas una por una en `MISSING_AND_RESTRICTED.md` con autor, año, DOI, enlace y motivo.

El sesgo del corpus **es la forma de los muros de pago**: completas al 100 % las categorías cuya
literatura es gratuita (`01_Filosofia` 8/8 en dominio público, `10_Aprendizaje` 14/14 en arXiv),
vacía al 100 % la que la industria mantiene cerrada — **`04_Desarrollo_Cognitivo`, 0 de 8**, que
es justo la categoría de la pregunta del proyecto (Piaget ×2, Vygotsky, Bruner, Karmiloff-Smith,
Gopnik, Carey, Siegler).

**Reparado esta noche:** la procedencia de la expansión v0.3 declaraba 14 fuentes como
`VERIFIED_LOCAL_FILE` apuntando a `/workspace/scratch/…`, una ruta efímera inexistente; solo 3
eran verificables. Se re-adquirieron desde sus URL legales registradas y se extrajeron de los ZIP
las ya presentes. Ahora: **14/14 presentes, 10 con sha256 idéntico al original**, 3 HTML de PMC
con texto completo y hash nuevo, 1 solo resumen. Escrito como
`SOURCE_PROVENANCE_v0.3.local.csv`; **el original intacto** — promoverlo es decisión humana.

---

## 6bis. Dos fuentes primarias incorporadas esta noche

`X17` — Susan Carey, *Précis of The Origin of Concepts*, BBS 34:113–167 (2011), acceso abierto,
Version of Record, sha256 verificado. Y `SEC-0001` — la reseña de Freeman sobre Karmiloff-Smith,
archivada aparte como fuente **secundaria**, que no sustituye a TI-0035.

De X17 sale `H-RIVAL-CAREY`, una hipótesis rival fuerte **contra el propio proyecto**: ningún
agente no lingüístico puede, según Carey, construir los conceptos *objeto* o *causa* desde
primitivos perceptuales, por lo que cualquier mejora en `d1_objects` o `d3_causality` debe
descartarse primero como generalización estadística. Desarrollado en
`docs/CAREY_BOOTSTRAPPING_VS_TERRARIO.md`, junto con la advertencia metodológica de Carey —
**una celda baja de la matriz A×D no demuestra ausencia de competencia** — que debe entrar en el
plan de análisis de cualquier preregistro de la matriz.

## 7. Un puente entre la teoría y el instrumento

De la reseña de Freeman (*Perception* 1994) sobre *Beyond Modularity*: la redescripción
representacional postula que, tras estabilizarse el dominio conductual, las representaciones
implícitas se transforman **sin sobrescribir los niveles inferiores**.

**Advertencia de constructo:** la escalera A0→A4 es *anatomía comparada* (cinco arquitecturas
distintas); la redescripción es *ontogenia* (una arquitectura que cambia en el tiempo).
Confundirlas sería un error grave. Que A4 tenga planificador no significa que A4 haya redescrito.

**Dónde sí sería medible, con lo que ya existe:** `d4_adaptation_scientific` tiene las fases
`ACQUISITION → CAUSAL_CHANGE → RECOVERY`. La predicción falsable es que un agente que haya
redescrito se recupere tras la inversión **conservando** la política anterior, frente a la
sustitución de uno que solo sobrescribió. Preregistrable sin código nuevo.

---

## 8. Qué requiere decisión humana

1. **Línea base**: opción B, `system_baseline_03` (§2). Es lo único que separa la suite del verde.
2. **D-01**: si se activa la recuperación de leases al arrancar la API.
3. **D-06**: si se aplica la idempotencia de `verify()`.
4. **Procedencia del corpus**: si `SOURCE_PROVENANCE_v0.3.local.csv` pasa a canónico.
5. **CL-7**: sigue en `REVIEW_BLOCKED`; la decisión `REQUEST_CHANGES` («no le entiendo») cerró la
   solicitud sin mutar el diseño. Avanzar exige derivar una versión nueva.
