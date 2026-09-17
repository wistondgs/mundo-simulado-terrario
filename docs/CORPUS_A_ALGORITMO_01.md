# CORPUS-A-ALGORITMO-01 · cómo un concepto se vuelve instrumento

**Estatus:** hallazgo de sesión, no normativo. No modifica PROCESO-DE-TRABAJO-01.
**Fecha:** 2026-09-16.
**Pregunta que responde:** «¿cómo se crean estos conceptos en Terrario para luego convertirlos
en algoritmos?»
**Método:** no se diseñó una receta. Se leyeron los **dos únicos conceptos que ya completaron
el viaje** — `planned-action-evaluation-pathway` y `viability-recovery-profile` — y se extrajo
la ruta que ambos recorrieron. Todo lo afirmado abajo tiene archivo y línea.

---

## 0. El hallazgo en una línea

> La ruta concepto → algoritmo **ya existe y se ha recorrido dos veces**. Lo que no existe es
> la **columna operacional del corpus**: de 189 claims, 133 son `CONCEPTUAL_ARGUMENT`, y un
> argumento conceptual no lleva dentro el criterio que lo haría medible.

El cuello de botella no es código, y no es tamaño de corpus. Es que **el corpus registra lo que
los autores dijeron, no lo que habría que observar para contradecirlos.** Ese salto lo pone hoy
un humano, a mano, una vez por concepto.

---

## 1. La ruta real, con sus siete etapas

Lo que sigue no es un diseño: es la traza de `viability-recovery-profile`, que es el caso más
completo porque su fuente es de 1956 y su instrumento es de esta semana.

```
1  FUENTE          Ashby, An Introduction to Cybernetics, cap. 10 — corpus TI-0049, sha256 verificado
2  CLAIM           CLM-0052/0053, evidence_type = FORMAL_DERIVATION, attribution = AUTHOR_EXPLICIT
3  ESTRUCTURA      E (variables esenciales) · η (región viable) · D (perturbación) · F (regulador)
4  PROYECCIÓN      E  := world_truth.agents[*].energy      (mínimo entre agentes)
                   η  := energy >= viable_floor * max_energy
                   D  := cambio de world_revision
                   F  := no se mide; se mide su EFECTO sobre la variedad que llega a E
5  INSTRUMENTO     specification() congela parámetros DENTRO del hash   viability_recovery_metric.py:87
6  CALIBRACIÓN     validate_construct() sobre trayectorias sintéticas   viability_recovery_metric.py:234
                   cuya respuesta se conoce por construcción — valida el APARATO, no al agente
7  REGISTRO        MetricDefinition(... NOT_VALIDATED_FOR_CONSTRUCT)    metrics_observer.py:152
                   la promoción a VALIDATED es firma humana, no un default de la librería
```

El otro caso, `planned-action-evaluation-pathway`, recorre exactamente las mismas siete etapas
desde LeCun (HYPERCAND-08) en vez de Ashby, y es **el único que llegó a la etapa 7 con firma**
(`planning_trace_metric.py:49`, `:124`). Ése es CL-7.

### La etapa 4 es el acto científico, y es manual

Las etapas 1–3 las hace el corpus. Las 5–7 las hace la maquinaria. **La 4 no la hace nadie
automáticamente**: alguien decide que «variable esencial» significa `energy` y que
«perturbación» significa `world_revision`. Esa decisión es irreversible en la práctica — queda
sellada dentro del `metric_spec_hash` — y es donde se gana o se pierde la validez de constructo.

No hay atajo. Un LLM puede proponer la proyección; no puede firmarla.

---

## 2. Las tres aduanas que matan conceptos

Un concepto del corpus tiene que pasar tres controles. Casi ninguno pasa los tres.

### Aduana 1 · ¿el claim lleva criterio operacional?

De 189 claims del snapshot `theory-f59dbb6d6ee3850c`:

| evidence_type | n | ¿sirve para instrumentar? |
|---|--:|---|
| `CONCEPTUAL_ARGUMENT` | 133 | **no** — no nombra qué observar |
| `COMPUTATIONAL_EXPERIMENT` | 7 | sí, con adaptación de dominio |
| `FORMAL_CONSTRUCTION` | 4 | sí, bajo sus axiomas |
| `FORMAL_DEFINITION` / `FORMAL_DERIVATION` | 5 | **sí — Ashby y Legg–Hutter están aquí** |
| `machine learning` / `behavioral` / `robotics experiment` | 7 | sí |
| `PSYCHOMETRIC_OPERATIONALIZATION` | 2 | sí, pero mide test, no organismo |
| `OPERATIONAL_DEFINITION` | 1 | sí — Pathak, curiosidad ≡ error de predicción |
| `ALGORITHM_SPECIFICATION` | 1 | sí — Pathak, error → recompensa intrínseca |
| resto (síntesis, revisión, limitación) | 29 | no |

**~27 de 189 claims (14%) pueden originar un instrumento.** El resto puede originar una
hipótesis, una rival, o una advertencia — no una medición.

### Aduana 2 · ¿se proyecta sobre la superficie sellada?

Terrario no puede medir lo que no emite. La superficie completa, hoy:

```
AGENT_FIELDS       channels · mask · agent_energy · time_fraction          world_contracts.py:12
OBSERVER_ONLY      world · world_truth · objects · agents · occupancy ·
                   rules · rules_version · causal_property · energy_value  world_contracts.py:13
CANALES (9)        world · consequence · agent_energy · sensation · decision ·
                   planner_proposal_trace · prediction_error ·
                   causal_intervention · internal_tensors[DEBUG_ONLY]      metrics_observer.py
INTERVENCIÓN       cambio de reglas programado (ChangeScheduler) + fork do(X)
ESCENARIOS         D0 D1 D2 D3 D4 D4S   (D5–D11 = FUTURE_DESIGN)
```

Cuatro campos para el agente y nueve canales para el observador. **Ése es el universo de lo
medible.** Un concepto que exige otra cosa no está esperando un algoritmo: está pidiendo un
mecanismo nuevo — y eso lo prohíbe la moratoria de PROCESO-DE-TRABAJO-01 §4 hasta que
`scientific_results > 0`.

`internal_tensors` es `DEBUG_ONLY` por contrato. Leerlo como evidencia rompe la separación que
hace interpretable todo lo demás; no es un atajo hacia «representación».

### Aduana 3 · ¿hay promoción humana?

10 métricas registradas. **Una sola** con `VALIDATED_FOR_CONSTRUCT`:
`planned-action-evaluation-pathway`. `viability-recovery-profile` está implementada, pasa sus
seis casos sintéticos, y está deliberadamente registrada como `NOT_VALIDATED` — porque promover
es lo que vuelve publicable un resultado, y eso es firma, no código (`metrics_observer.py:144-168`).

---

## 3. Triaje de los 64 bloques contra la superficie

`ANALYST_MAPPING`, provisional y reversible, en el sentido de `CONCEPT_CANONICAL_MAP_v0.2`.
La clase no dice si el concepto es importante: dice **qué haría falta para poder refutarlo aquí.**

### Clase A · instrumentable hoy, sin mecanismo nuevo (8 bloques: 1, 9, 16, 20, 27, 45, 46, 62)

| Bloque | Señal | Estado |
|---|---|---|
| 1 núcleo existencial: viabilidad, homeostasis, variedad reguladora | `world_truth.energy` + `world_revision` | **ya construido**, falta firma |
| 46 recuperación · 16 adaptación | idem + diseño pareado | el instrumento existe; separarlas es **diseño**, no canal |
| 45 robustez | idem + matriz de semillas | disponible |
| 20 persistencia y retención | idem, medido en episodio posterior | disponible |
| 27 planificación (disponibilidad de la vía) | `planner_proposal_trace` | **ya construido y validado** = CL-7 |
| 9 predicción (error, actualización) | `prediction_error` | canal `CONDITIONAL`: existe el canal, falta agente que lo llene |
| 62 criterios experimentales | preregistro, ablación pareada, semillas held-out | es la maquinaria misma |

Los bloques **10 causalidad** y **11 contrafactualidad** quedan aparte, con advertencia: el fork
`do(X)` mide la intervención **del científico**, no la capacidad causal **del organismo**.
Instrumentados como si fueran lo mismo, producirían el error más caro disponible en este
repositorio.

### Clase B · bloqueado por un canal que no existe (12 bloques)

3 experiencia · 4 memoria · 22 metacognición · 23 autoconocimiento · 24 techo epistemológico ·
25 maestro externo · 30 selección de estrategia · 43 repertorio · 5/6/7/34 representación,
conceptos, abstracción, invención representacional.

- **Memoria y experiencia** necesitan `memory_hit → decision_difference`. Terrario no tiene canal
  de memoria; el eslabón roto vive en RNFE, fuera de este repositorio. Es el paso 3 del orden de
  trabajo, y sus dos gates (H1 estado→acción, H2 historia→estado→acción) ya están separados.
- **Metacognición y techo epistemológico** necesitan auto-reporte *más* prueba de reclutamiento
  causal. `self-specificity` sin `control` es telemetría, por la propia distinción del bloque 22.
- **Representación y conceptos** sólo tendrían `internal_tensors`, que es `DEBUG_ONLY`.

### Clase C · bloqueado por nivel de mundo (15 bloques)

13 razonamiento · 14 resolución de problemas · 28 exploración · 29 motivación intrínseca ·
31 desarrollo · 48–52 social, ToM, cultura, distribuida, colectiva · 53–55 lenguaje, semántica,
sentido común · 59 evolución abierta · 60 novedad.

Requieren D5–D11, todos `FUTURE_DESIGN` en `project_manifest.json`. No es una carencia de
instrumento: el mundo donde ocurrirían no está construido.

### Clase D · el constructo todavía no está operacionalizado (27 bloques)

2 percepción y acoplamiento · 8 modelo del mundo · 12 imaginación · 15 aprendizaje ·
17 plasticidad · 18 generalización · 19 transferencia · 21 metaaprendizaje · 26 agencia · 32 creatividad · 33 invención ·
35–37 flexibilidad, ejecutivas, racionalidad · 38–40 incertidumbre, creencias, información ·
41 eficiencia · 42 capacidades nuevas · 44 capability closure · 47 localización funcional ·
56–58 consciencia, self, automejora · 61 medición · 63 confusiones · 64 la cadena.

Aquí el bloqueo no es técnico. **Falta decir qué observación decidiría la cuestión**, que es
exactamente la advertencia con la que termina `CORPUS_ACQUISITION_LIST_02`. Para varios de
éstos, escribir esa frase *es* el trabajo, y es más difícil que el algoritmo posterior.

Dos casos ilustrativos. **19 transferencia** parece Clase A — existe
`d4_adaptation_transfer.yaml`, un mundo con el mapeo invertido desde t=0. Pero el único instrumento aplicable sería
`D4-energy-trajectory`, que es `NOT_VALIDATED_FOR_CONSTRUCT`: rendir más energía en el mundo B
no es, por sí solo, transferencia. Tiene escenario y no tiene constructo. **2 percepción**
está igual: D1 y D2 implementan persistencia de objetos y binding de propiedades, y no existe
ninguna métrica de percepción validada para su constructo.

**Recuento: 8 instrumentables · 12 sin canal · 15 sin mundo · 27 sin constructo · 2 con
advertencia de atribución (10, 11).** Suma 64.

---

## 4. Lo que el corpus necesita y no tiene

No es más bibliografía. Es **una columna más por claim**, del mismo tipo que las que ya lleva
`RELATIONS_AUDIT_v0.2.csv` (`causal_level`, `necessity`, `sufficiency`, `attribution`):

```
observable_commitment    qué habría que observar para que este claim fuera falso
essential_variable       sobre qué magnitud
disturbance              bajo qué perturbación
ablation                 qué se le quita al sistema para que la afirmación se caiga
```

Las cuatro se pueden rellenar sólo para los ~27 claims de la aduana 1. Para los otros 162, la
casilla honesta es `NO_OPERATIONAL_COMMITMENT`, y esa casilla vacía es un resultado: dice que el
autor no comprometió al concepto con ninguna observación.

Ashby pasa porque escribió E, η, D y F. Pathak pasa porque escribió curiosidad ≡ error de
predicción. Hume no pasa, y no es un defecto de Hume.

---

## 5. El antipatrón

> Un canal nuevo por cada concepto que se quiere medir.

Sesenta y cuatro bloques × un canal cada uno = un organismo con más instrumentación que
conducta, y ninguna vuelta cerrada. Es la misma causa de proceso que diagnosticó
PROCESO-DE-TRABAJO-01: **mecanismos añadidos más rápido que ciclos cerrados.**

La dirección correcta es la inversa: partir de los nueve canales que existen y preguntar qué
conceptos del corpus admiten proyección sobre ellos. Eso es lo que hace la §3, y la respuesta es
siete.

---

## 6. Lo que esto implica para la vuelta activa

CL-7 es el único bloque que atravesó las tres aduanas. No es el concepto más interesante de los
64 — es el único cerrable, que es una propiedad distinta y ahora mismo más valiosa.

Si hubiera que preparar un segundo, el candidato es el bloque 1 vía `viability-recovery-profile`:
fuente formal verificada, instrumento implementado, calibración pasada, escenario existente
(`d4_adaptation_scientific.yaml`, con inversión de reglas en t=450 ± 25). Le falta **una firma,
no una línea de código.**

Y el corpus, mientras tanto, no necesita crecer. Necesita que ~27 de sus claims declaren a qué
observación se comprometen.

---

## 7. Adenda 2026-09-16 · el eje transversal de variedad

ADR-001 (`knowledge/00 Control/ADR-001 Variedad dinamica.md`, PROPOSED) indexa por tiempo todo lo
anterior: `Eₜ, 𝒱ₜ, Dₜ, Rₜ`. Eso **reclasifica parte del triaje de la §3**, y conviene decirlo
antes de que alguien lo lea como si siguiera vigente sin matices.

La clase de un bloque depende de si su variedad está congelada:

| Bloque | Con `𝒱` congelada | Con `𝒱ₜ` |
|---|---|---|
| 1 núcleo existencial | **A** — instrumentable | **B** — η es hoy `viable_floor × max_energy`, y `max_energy` se fija una vez por episodio |
| 16 adaptación · 46 recuperación | **A** | **B** para el Caso 3: reorganización hacia `𝒱₂ ≠ 𝒱₀` |
| 45 robustez · 20 persistencia | **A** | **A** — no dependen de que `𝒱` se mueva |
| 27 planificación · 9 predicción · 62 criterios | **A** | **A** — CL-7 no toca `𝒱` |

De los ocho de la Clase A, **cinco sobreviven sin cambios y tres se vuelven condicionales.** El
que se vuelve condicional es precisamente el que la §6 recomendaba firmar a continuación.

Lo que la corrección **no** cambia: la ruta de siete etapas, las tres aduanas, y el hecho de que
la etapa 4 sea manual. Lo que sí cambia es que la etapa 4 ahora debe declarar **qué congela** —
un η fijo deja de ser una elección de parámetro y pasa a ser un control declarado, con su propia
justificación.

`dV_R/dt` merece una línea aparte. `variety_ratio` mide la variedad de **E**, la variable
regulada; la variedad del **regulador** no tiene canal, y `grep -rn "variety\|repertoire"` sobre
`terrario/` devuelve únicamente este mismo instrumento. El Caso 3 del ADR —`V_R(t₁) > V_R(t₀)`—
es Clase B, no Clase A. Es la señal más interesante del marco corregido y es, hoy, la menos
medible.

---

## 8. Adenda 2026-09-16 (tarde) · la columna llegó, parcialmente

La §4 sostiene que al corpus le falta un compromiso observable por claim. La generación v0.4 del
corpus vivo —fuera de este repositorio— trae una familia nueva, `HISTORY_DEPENDENCE`, cuyas 15
fuentes están seleccionadas **por el control que cada una declara**, y cuyo criterio
`P(R' | H₁, D') ≠ P(R' | H₀, D')` es el Gate H2 de `PROCESO_DE_TRABAJO_01` §8.

Eso responde la aduana 1 para esa familia. **No** mueve los bloques 3 y 4 de Clase B: siguen sin
canal en Terrario. El bloqueo pasa de doble a simple.

Detalle: nada de v0.4 está en el snapshot versionado. El repositorio y el corpus vivo están
desincronizados por una generación entera. Análisis en
[CORPUS_V04_ANALISIS_01.md](CORPUS_V04_ANALISIS_01.md).

---

## 9. Adenda 2026-09-16 (noche) · los diez criterios no son una compuerta fija

La §3 lista el bloque 62 como «es la maquinaria misma». El mapa conceptual ampliado lo acota:
los diez criterios **«no son diez pruebas obligatorias para cada palabra del mapa»** — se
seleccionan según lo que se afirma y deben declararse antes de interpretar resultados. En la
misma línea, `capability closure` (bloque 44) queda marcado como **término de trabajo del
proyecto, no ley general aceptada**.

Eso no relaja nada: exige declarar por adelantado *cuáles* criterios aplican a la afirmación
concreta, en vez de invocar los diez como ritual o de omitirlos en silencio. Y añade lo que a la
tabla le faltaba: tamaño del efecto, incertidumbre, distribución de resultados, condiciones de
exposición y explicaciones alternativas. Una diferencia numérica sin eso no cierra nada.
