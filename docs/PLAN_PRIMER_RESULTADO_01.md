# PLAN-PRIMER-RESULTADO-01

**Estatus:** plan propuesto. Subordinado a `PROCESO_DE_TRABAJO_01`.
**Fecha:** 2026-09-16 (noche).
**Origen:** cuatro preguntas — ¿conceptos comparados con el corpus? ¿escenarios creados?
¿infraestructura lista? ¿primeras pruebas hechas? Las respuestas están abajo, verificadas contra
la base de datos y el código, y **cambian cuál es el plan que hacía falta**.

---

## 0. El hallazgo

La infraestructura no está incompleta. **Está sin cerrar en el último metro, y el metro que
falta es uno solo:**

```
238 SCIENTIFIC_TRACE selladas       ✓
238 TRIAL_RESULT sellados           ✓
  0 METRIC_RESULT                   ✗   ← el eslabón
  0 scientific_results
```

`EmpiricalResultPublicationService` exige un artefacto `METRIC_RESULT` sellado en CAS para
publicar. Nunca ha existido ninguno. El escritor existe como API —
`scientific_executions.record_raw_artifact(execution_id, "METRIC_RESULT", ...)` — y **sólo lo
llama un test** (`tests/test_empirical_result_publication.py:54`). Ningún camino de producción
toma una traza sellada, corre el instrumento preregistrado sobre ella y sella la salida.

Aguas arriba está todo hecho y ejercitado. Aguas abajo está todo hecho y probado. Entre medias
falta un paso que ya sabe hacer cada una de sus mitades.

---

## 1. Las cuatro respuestas

### ¿Están los conceptos comparados con el corpus?

**Sí para la generación congelada, no para la nueva.**

| | |
|---|---|
| snapshot `theory-f59dbb6d6ee3850c` (2026-09-09) | 44 fuentes · 283 conceptos RAW · 224 candidatos canónicos · 189 claims · 8 hiperaristas · 21 familias |
| corpus v0.4 (2026-09-16) | 43 adquisiciones, **0 claims extraídos** — su propio gate dice `CORPUS EXPANSION INCOMPLETE` |
| grafo de referencias vivo (`.terrario`) | **0 documentos, 0 claims** — el importador nunca ingirió nada aquí |

La comparación existe y está versionada, pero va **una generación por detrás**. Y la familia con
criterio operacional —`HISTORY_DEPENDENCE`— es justamente la que no está extraída.

### ¿Están creados los escenarios?

**Siete registrados**, uno nuevo de hoy:

```
D0 D1 D2 D3   0 perturbaciones
D4  D4S       1 perturbación
D4T           3 perturbaciones      ← nuevo, etapa 1 del plan de reproducción
```

Del plan de reproducción falta `D4V` (tipos de perturbación). Los agentes son A0–A4 y no han
cambiado; A4 ganó hoy la bandera `use_homeostasis`.

### ¿Está la infraestructura lista para verificar y registrar comportamientos?

**Sí, y más que lista: ya se usó.**

```
144 Preregistration   ·  141 PREREGISTERED_LOCKED
141 autorizaciones de ejecución  ·  145 eventos de autorización
141 scientific_executions  ·  238 run_attempts COMPLETED
476 artefactos de ejecución  ·  1664 eventos
  1 verificación:  classification PASS, checks 5/5, failures [], warnings []
```

### ¿Se hicieron las primeras pruebas?

**Sí — y esto es lo que no esperaba.** No es que no se haya probado nada: se ejecutó 238 veces.

Una cadena completa llegó al final:

```
execution-841bf1707c9c4b9ebd87221e2947a10c
  preregistro   PR-LIVE-ead629e4464e
  completada    2026-09-16 05:53:33
  verificada    2026-09-16 05:53:49   PASS, 5/5, sin fallos ni avisos
  artefactos    SCIENTIFIC_TRACE 491 KB  ·  TRIAL_RESULT 82 KB
```

Y seis minutos después, a las **05:59:07**, la decisión humana sobre una revisión fue
`REQUEST_CHANGES` con motivo **«no le entiendo»**.

Es decir: **la cadena llegó a la última compuerta y se detuvo en comprensión, no en capacidad.**
Ese es el estado real, y es muy distinto de «falta infraestructura».

---

## 2. El plan

Cinco pasos hasta `scientific_results = 1`. Ninguno es un mecanismo del organismo, así que
ninguno cae bajo la moratoria — que es precisamente lo que este primer resultado levantaría.

### Paso 1 · Elegir la traza y declarar su instrumento
De las 238 trazas selladas, elegir una cuya ejecución esté `COMPLETED` **y verificada `PASS`**.
Hoy hay exactamente una. Declarar contra qué endpoint preregistrado se evalúa, con sus
parámetros, **antes** de mirar el número. Si el preregistro de esa ejecución declara
`evidence_publication: false` —como lo hace el más reciente del ledger— no sirve para publicar y
hay que preregistrar uno que sí lo declare.

### Paso 2 · Escribir el evaluador que falta
Un paso que lee una `SCIENTIFIC_TRACE` sellada por su descriptor, corre el instrumento
preregistrado sobre ella, y sella la salida como `METRIC_RESULT` con
`record_raw_artifact`. Es la única pieza nueva de todo el plan, y su forma ya está fijada por
el consumidor: `evidence_publication.py` valida esquema, versión, identidad de traza y linaje.
**No decide nada**: proyecta el instrumento sobre datos sellados.

Ambos instrumentos de viabilidad ya aceptan exactamente esta entrada
(`evaluate_scientific_trace`, `evaluate_scientific_trace_segments`), igual que el de CL-7
(`planning_trace_metric.evaluate_scientific_trace`).

### Paso 3 · Correr `eligibility()` y leer los bloqueos
`EmpiricalResultPublicationService.eligibility()` devuelve la lista exacta. Hoy devolvería
`METRIC_RESULT_ARTIFACT_NOT_SEALED`. Después del paso 2 dirá qué más falta, si algo falta —
posibles: `METRIC_NOT_PREREGISTERED_ENDPOINT`, `METRIC_VERSION_MISMATCH`,
`PREREGISTRATION_NOT_EXACT_LOCKED`, `HYPOTHESIS_REVISION_MISMATCH`. **Ese informe es el plan
real del paso 4**, y no se puede escribir antes de tenerlo.

### Paso 4 · Cerrar los bloqueos que queden
Uno a uno, sin tocar el instrumento para que encaje. Si un bloqueo dice que la métrica no es el
endpoint preregistrado, se preregistra de nuevo; **no** se reetiqueta la métrica.

### Paso 5 · `ingest()` y contador a 1
Publica el resultado en el ledger CL-7. Es lo que levanta la moratoria de
`PROCESO_DE_TRABAJO_01` §4 y desbloquea la etapa 4 del plan de reproducción — separar `E` del
refuerzo, que es la que todas las afirmaciones interesantes necesitan.

---

## 3. Lo que este plan no hace

- **No mira el número antes de declarar la regla.** El paso 1 va antes del paso 2 por eso.
- **No promueve ninguna métrica a `VALIDATED_FOR_CONSTRUCT`.** Eso es firma humana y es
  independiente de publicar un resultado.
- **No resuelve «no le entiendo».** Esa decisión sigue siendo del investigador, y `a2ff180` ya
  añadió la tarjeta de diseño que muestra escenario, brazos, semillas, métrica y —sobre todo— qué
  declina medir cada métrica. El plan puede producir un resultado publicable; no puede producir
  comprensión ajena.
- **No toca el corpus.** La extracción T1 de `HISTORY_DEPENDENCE` es trabajo paralelo y no
  bloquea nada de esto.

---

## 4. La frase que resume el estado

No falta infraestructura, no faltan escenarios y no faltan corridas. **Falta la función que
convierte una traza sellada en una medición sellada**, y sin ella 238 trazas verificadas están
esperando que alguien las lea con un instrumento.
