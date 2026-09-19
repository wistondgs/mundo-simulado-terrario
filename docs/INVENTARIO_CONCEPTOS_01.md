# Inventario de conceptos · para elegir qué se implementa

**2026-09-18.** Todo lo que hay, en las cuatro fuentes que existen, y no coinciden entre sí.

| Fuente | Cuántos | Procedencia | Qué es |
|---|---:|---|---|
| `agent_composition.CONCEPTS` | **11** | `corpus_block: int`, **entero que nadie lee** | los módulos configurables que el agente ya tiene |
| `capability_passport.REGISTRY` | **10** | `corpus_provenance` vacío en 8 de 10 | la capacidad medible de cada módulo |
| `corpus_v2` (claims) | **38 conceptos / 21 claims** | `claim_id` + locator + SHA-256 · **citable** | lo que el corpus sostiene hoy |
| `HEA_CONCEPTOS_EXTRAIDOS_v1` | **115** | `definicion_del_autor` en 115/115, locator v1 | el material del que salen los módulos nuevos |

Los 115 por documento: HEA-001 (15), HEA-005 (14), HEA-007 (14), HEA-009 (14), HEA-011 (15),
HEA-014 (15), HEA-015 (14), HEA-016 (14). Por tipo: 40 proceso/mecanismo, 22 propiedad, 20 magnitud,
12 representación, 9 resultado/conducta, 8 teoría, 4 objetivo/valor.

---

## Capa 1 · Ya son módulo (11). Lo que falta es la cita, no el código

Tienen código, ablación y pasaporte. Ninguno cumple L-1.

| Módulo | Capacidad | Estado del pasaporte | Qué le falta |
|---|---|---|---|
| `use_online_learning` | LEARN-A1 · APRENDIZAJE_POR_EXPERIENCIA | **READY_FOR_CERTIFICATION** | sólo la cita |
| `use_homeostasis` | HOMEO-A1 · REGULACION_HOMEOSTATICA | NO_CALIBRATED_ENDPOINT | endpoint + cita |
| `use_uncertainty` | UNC-A1 · ESTIMACION_DE_INCERTIDUMBRE | NO_CALIBRATED_ENDPOINT | endpoint + cita |
| `use_episodic_memory` | EPMEM-A1 · MEMORIA_EPISODICA | NO_CORPUS_PROVENANCE | **cita** |
| `use_longterm_memory` | LTMEM-A1 · MEMORIA_PERSISTENTE | NO_CORPUS_PROVENANCE | **cita** |
| `use_temporal` | TEMP-A1 · INTEGRACION_TEMPORAL | NO_CORPUS_PROVENANCE | **cita** |
| `use_entropy_regularization` | PLAST-A1 · PLASTICIDAD_EXPLORATORIA | NO_CORPUS_PROVENANCE | **cita** |
| `use_planner` | PLAN-A1 · PLANIFICACION_ANTICIPATORIA | NO_CORPUS_PROVENANCE | cita + mundo |
| `use_world_model` | WM-A1 · MODELO_PREDICTIVO_DEL_MUNDO | INTERVENTION_IMPURE | pureza + cita |
| `use_curiosity` | CURIO-A1 · MOTIVACION_INTRINSECA | INTERVENTION_IMPURE | pureza + cita · **y está en rojo** |
| `use_factored_action` | — sin pasaporte | — | es reparación de canal, no concepto de corpus |

**Las citas ya existen en corpus_v2 y encajan directas:**

| Módulo | Claim | Locator |
|---|---|---|
| `use_world_model` | `C-HEA-015-01` GOOD_REGULATOR **REQUIRES** MODEL_OF_SYSTEM | `HEA-015.txt:13-21` |
| `use_homeostasis` | `C-HEA-019-01` HOMEOSTASIS **NAMES** …STEADY_STATES (Cannon) | `HEA-019.txt:2915-2943` |
| `use_homeostasis` | `C-HEA-007-02` ADAPTIVITY **REQUIRES** REGULATION_WRT_VIABILITY | `HEA-007.txt:45-49` |
| `use_curiosity` | `C-HEA-001-02` INTERNAL_STATE_CONTROL **PART_OF** MOTIVATED_BEHAVIOR | `HEA-001.txt:46-61` |
| `use_longterm_memory` | `C-HEA-020-01` LEARNING_SETS **PRODUCE** faster second trial | `HEA-020.txt:28-42` |
| `use_uncertainty` | `C-HEA-017-01` METACOGNITION **HAS_PART** MONITORING_AND_CONTROL | `HEA-017.txt:20-61` |

`use_episodic_memory`, `use_temporal`, `use_entropy_regularization` y `use_planner` **no tienen
claim en corpus_v2**: los 21 claims citables no cubren memoria episódica ni integración temporal.
Eso es un hueco de corpus, no de código.

---

## Capa 2 · Concepto del corpus, implementable en el motor de hoy, sin módulo

Candidatos reales. Cada uno con la costura de código donde entraría.

| # | Concepto | Qué haría el agente | Costura | Fuente |
|---|---|---|---|---|
| **B1** | **Ultraestabilidad / segundo lazo** (step-mechanism, critical state, second-order feedback) | cuando la energía cruce el límite, **cambiar sus propios parámetros al azar** y volver a probar — no ajustar por gradiente | `learner.py` + un gatillo sobre `homeostasis` | HEA-014 S.7/26 · `C-HEA-014-01` |
| **B2** | **Recompensa interoceptiva / reducción de impulso** | que el refuerzo sea la reducción de una desviación interna, no la energía externa | `a4_advanced._policy_reward` — **la costura ya existe, inerte** | HEA-001 (drive, drive function, setpoint) |
| **B3** | **Alostasis / respuesta anticipatoria** | revisar el **objetivo** por adelantado ante un cue indirecto, antes de que haya desviación | `homeostasis_threshold` pasa de constante a variable de estado | HEA-011 §2 · HEA-001 |
| **B4** | **Aversión al riesgo** | ante igual esperanza, preferir la varianza baja **según** la energía | `_policy_reward` + el eje `risk` que el mundo ya tiene | HEA-001 (risk aversion) |
| **B5** | **Metacognición: monitorización y control** | leer su propio error de predicción y **cambiar de política**, no sólo de acción | `a4_advanced` `last_prediction_error` ya se calcula y no gobierna nada | HEA-017 · `C-HEA-017-01` |
| **B6** | **Impulsos modulares en competencia** | dos módulos con función de recompensa propia que **someten valores de acción**, en vez de una suma escalar | A5 entero: es la versión que HEA-005 **no refuta** | HEA-005 · `R-HEA-005-001` |

**B6 tiene una salvedad dura:** Dulberg construye el conflicto con N=4 necesidades y recursos
separados en el espacio. Con N=1 se puede implementar la *arquitectura* modular (dos módulos, dos
recompensas, arbitraje) pero **no se puede correr su experimento**: §3.3 fija una variable y mide
«las restantes», y no hay restantes.

---

## Capa 3 · Concepto del corpus que el motor no aguanta

No es cuestión de escribir el módulo: falta sustrato.

| Concepto | Qué falta | Fuente |
|---|---|---|
| Competencia entre necesidades · conflicto · `viability set` multidimensional | **una segunda variable esencial.** `AgentState` lleva sólo `energy`; `RuleEffect` sólo `energy_delta` | HEA-001, HEA-005, HEA-007 |
| Perturbación–respuesta · `stretch perturbation` · configuraciones metaestables | **un operador de perturbación.** Cero apariciones en todo el generador | HEA-009 · `C-HEA-009-01` |
| Variedad requisita · homomorfismo regulador→mundo | medida sobre un espacio de estados que nadie enumera | HEA-011, HEA-014, HEA-015 |
| Clausura operacional · autopoiesis · sense-making | son **propiedades a demostrar**, no módulos a encender. Y HEA-007 avisa: no llamar agente a algo por lenguaje autopoiético (`R-HEA-007-001`) | HEA-007, HEA-011, HEA-016 |
| Markov blanket · energía libre | otra arquitectura, no un módulo más | HEA-009, HEA-011 |

---

## Lo que bloquea cualquier elección de la Capa 2

Medido hoy, mundo LEARN-A1, primera puerta en la columna 2, 68 pasos:

```
A4         CONSUME con efecto = 0      PUSH/LEFT 19 · INSPECT/DOWN 11 · MOVE/UP 9 · PUSH/UP 9 · MOVE/RIGHT 6
oráculo    CONSUME con efecto = 8      MOVE/RIGHT 60 · CONSUME/DOWN 4 · CONSUME/UP 4
```

**El organismo nunca consume.** Cualquier módulo nuevo de la Capa 2 se mediría sobre una conducta
que no toca el mundo: `accuracy=None` en todos los brazos. No es resultado nulo, es no medible.
