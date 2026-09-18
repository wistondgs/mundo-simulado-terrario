# TCS-01 · Foundational Cybernetic Capability Synthesis

**Primera campaña experimental fuerte de Terrario · 2026-09-17**

Doctrina que la gobierna: [`TERRARIO_CANON_02.md`](TERRARIO_CANON_02.md).
Estado medido del código: [`CARTOGRAFIA_TERRARIO_01.md`](CARTOGRAFIA_TERRARIO_01.md).
Disciplina de trabajo: [`GATES_DE_TRABAJO_01.md`](GATES_DE_TRABAJO_01.md).

---

## Qué NO es esta campaña

> Una corrida larga **no** es una trayectoria de 100 000 pasos de un solo A4. Eso produce mucha
> traza y poca inferencia.

TCS-01 es una **campaña longitudinal y composicional**:

```
Concepto → algoritmo candidato → capacidad otorgada → agente → mundo
        → conducta → evidencia → composición siguiente
```

## Misión

Construir el primer mapa causal serio del espacio de capacidades de Terrario. La pregunta no es
*¿qué agente consigue más reward?* sino:

> ¿Qué capacidades computacionales procedentes del corpus, implementadas mediante qué algoritmos y
> combinadas de qué manera, producen propiedades medibles del fenotipo de inteligencia buscado?

### Las tres preguntas científicas

| | |
|---|---|
| **Q₁** | ¿El algoritmo realmente implementa funcionalmente el concepto que dice representar? |
| **Q₂** | ¿Qué cambia causalmente en la conducta cuando esa capacidad se otorga? |
| **Q₃** | ¿Qué propiedades nuevas aparecen cuando varias capacidades **certificadas** interactúan? |

## Prohibiciones de interpretación

Queda prohibido leer `use_memory=True` como *«el agente posee memoria funcional»*, o
`use_planner=True` como *«el agente está planificando»*. **El nombre del módulo no es evidencia**
(L-2, I-02).

Y ante un fallo, la inferencia válida nunca es «la memoria no sirve» sino:

> La implementación **MEM-X vN** del concepto **C**, bajo el mundo **W** y la composición **S**,
> produjo / no produjo el efecto **E**.

Ésa es la granularidad científica de Terrario.

---

# 1 · La unidad fundamental: Capability Passport

Ningún algoritmo entra a la campaña sin pasaporte. Veintidós campos, todos obligatorios:

```
CONCEPT_ID               nombre normalizado del concepto
CORPUS_PROVENANCE        fuentes, nodos y relaciones del corpus            ← L-1
OPERATIONAL_DEFINITION   qué significa computacionalmente poseerla
ALGORITHM_ID             implementación concreta
ALGORITHM_VERSION
CAPABILITY_ID            capacidad otorgable resultante
INPUTS
OUTPUTS
INTERNAL_STATE
ALLOWED_INFORMATION      qué puede conocer legítimamente
FORBIDDEN_INFORMATION    qué sería fuga u oráculo
EXPECTED_BEHAVIOR
NEGATIVE_PREDICTION      qué debería ocurrir al quitarla
REQUIRED_WORLD_PROPERTY  qué debe exigir el mundo para que sea necesaria
PRIMARY_ENDPOINT
SECONDARY_ENDPOINTS
FALSIFICATION_CONTROLS
INTERVENTION_PURITY
KNOWN_DEPENDENCIES
KNOWN_CONFOUNDERS
STATUS
```

Un concepto admite varios pasaportes: `Cᵢ → Aᵢ₁, Aᵢ₂, Aᵢ₃` son **tres capacidades candidatas**, no
una.

---

# 2 · Primer conjunto candidato

No entran creatividad, imaginación, formación de hipótesis ni metacognición sólo porque están en el
corpus. Primero necesitan operacionalizaciones concretas.

Empezamos por las familias que **ya tienen correspondencia computacional**:

| Familia conceptual | Implementación candidata | Estado de admisión |
|---|---|---|
| Regulación / homeostasis | `HomeostaticState` | admisible |
| Memoria | `EpisodicMemory` y `LongTermMemory` — **dos algoritmos**, no necesariamente dos conceptos | admisible |
| Predicción / modelo del mundo | `WorldModel` | **BLOQUEADA** |
| Aprendizaje | `OnlineLearner` | admisible |
| Planificación / previsión | `Planner` | **BLOQUEADA** |
| Incertidumbre | `UncertaintyEstimator` | admisible |
| Plasticidad / exploración | mecanismo de entropía, **como candidato**, sin asumir equivalencia conceptual | admisible |
| Integración temporal | `TemporalCore`, **sólo si** el corpus le asigna un constructo explícito | condicional |

**Fuera de la campaña:** `use_factored_action`. No es una capacidad de inteligencia del corpus, es
infraestructura de direccionamiento.

**Por qué `WorldModel` y `Planner` están bloqueadas.** Medido con `purity_check.py`:
`use_world_model=False` desactiva el planner por completo (40 invocaciones → 0) y desvía conducta
hacia `policy_head` (97 → 120). Comparten la intervención, así que **no pueden entrar como factores
independientes** hasta que el alias se repare. Las otras 8 de 10 intervenciones son puras.

---

# 3 · Las siete fases

```
FASE 0   SCIENTIFIC RUNTIME GATE
FASE 1   CAPABILITY CERTIFICATION
FASE 2   SINGLE-CAPABILITY CAMPAIGN
FASE 3   COMPOSITION CAMPAIGN
FASE 4   PROGRESSIVE WORLD LADDER
FASE 5   CONFIRMATORY HOLDOUT
FASE 6   HYPERGRAPH ASSIMILATION
```

**No se salta una fase porque el resultado «se ve claro».**

---

# FASE 0 · Scientific Runtime Gate

Forma parte de la campaña. No es mantenimiento lateral.

Antes de que una corrida produzca evidencia:

```
D4T_declarado = D4T_ejecutado    para toda la física científicamente relevante
```

## 0.1 · La prueba

Misma definición de mundo, misma semilla, **misma secuencia fija de acciones** (no A4, para no
contaminar con diferencias del agente), por ambas superficies. Comparación paso a paso:

```
time · rules_version · agent position · agent energy · alive
object set · object positions · opportunity lineage · generation
cooldown · respawn · world events · state hash
```

Ante cualquier divergencia física:

```
CAMPAIGN_STATUS = BLOCKED_RUNTIME_SEMANTICS
```

No se sigue acumulando «evidencia».

## 0.2 · Estado medido de la Fase 0 — **PASS**

| | | evidencia |
|---|---|---|
| `find_target` unificado | ✅ | una implementación en vez de tres |
| `build_episode_components` unificado | ✅ | una construcción en vez de cuatro |
| `run_step` — una sola secuencia | ✅ | fixture de conducta idéntica, 9 casos con su digest |
| Ciclo de oportunidades encendido en el banco | ✅ | D4T 250 pasos: 32→29 pasó a **32→32**, con 3 de id ≥ 10000 |
| `set_global_determinism` simétrico | ✅ | mismo spec dos veces ⇒ mismo `initial_parameters_hash` |
| Test de paridad automático | ✅ | 6 pruebas; falla nombrando **primer paso y primer campo** |

```
WORLD_RUNTIME_PARITY = PASS
```

El test se escribió **antes** de reparar, para que el defecto quedara demostrado y no afirmado:
el determinismo se sostiene campo por campo incluidos linaje y generación —que `state_hash` no
cubre porque excluye `properties`—; semillas distintas **sí** divergen, que es el control negativo
que le falta a un test que siempre coincide; el ciclo **sí** cambia D4T; y **no** cambia D0, que fue
el permiso para encenderlo sin tocar los mundos que nunca lo declararon.

Consecuencia: toda evidencia anterior queda declarada `runtime Sandbox pre-parity`. Los números de
D4T del banco no son comparables con los de antes de este punto.

## 0.3 · Gate de instrumento

Sólo entran como **endpoints primarios** métricas con `STATUS = REPORTABLE`. Una cantidad no
calibrada puede guardarse como exploratoria, pero **jamás promover ni eliminar una capacidad**.

Cuatro semánticas estrictamente separadas: `0`, `NOT_EVALUABLE`, `MISSING`, `INVALID`. Nunca
`NOT_EVALUABLE → 0`.

Cada endpoint principal declara: definición · numerador · denominador · conditioning set · soporte
· controles · rango esperado · versión.

**Estado medido:** 6 de 22 mallas tienen control de falsación. Dos registros de métricas disjuntos.
Una sola métrica `VALIDATED_FOR_CONSTRUCT`.

---

# FASE 1 · Capability Certification

Aquí **no** se pregunta si la capacidad produce inteligencia general. Se pregunta si **hace lo que
pretende hacer**. Cada capacidad recibe su propio **mundo diagnóstico**.

## 1.1 · Los mundos diagnósticos

| Capacidad | Lo que el mundo debe exigir |
|---|---|
| **Homeostasis** | regular conducta según estado interno, con compromisos reales entre energía, exploración, riesgo y oportunidad futura. Un mundo donde siempre convenga lo mismo no prueba homeostasis. |
| **Memoria episódica** | un `cue_t` cuya información sea necesaria para `decision_{t+k}` y **no observable en `t+k`**. Si la solución sigue visible durante la decisión, el mundo no exige memoria. |
| **Memoria de largo plazo** | retención a través de demora, interferencia, nuevas observaciones y múltiples eventos. La pregunta no es «¿almacenó?» sino `almacenó → recuperó → utilizó`. |
| **Modelo predictivo** | transiciones que dependan de `(estado, acción)` y no se resuelvan por reacción instantánea. |
| **Planificación** | un problema donde `acción localmente atractiva ≠ secuencia globalmente favorable`. |
| **Aprendizaje** | una regla inicialmente desconocida pero aprendible por experiencia. **La capacidad se otorga; el contenido no.** |
| **Incertidumbre** | situaciones familiares, ambiguas y novedosas, distinguidas de forma **calibrada**. No basta con producir un número llamado `uncertainty`. |
| **Plasticidad** | `Rule_A → Rule_B` tras haber aprendido A. Se mide resistencia, velocidad de revisión, olvido, recuperación y nueva estabilización. |

## 1.1 bis · Estado medido de los pasaportes (P1, cerrado)

Nueve pasaportes registrados, con el estado **calculado** y no declarado:

```
capacidad  concepto                      contrato  procedencia  pureza  mundo  instrumento
HOMEO-A1   REGULACION_HOMEOSTATICA         si         NO         si      NO       NO
EPMEM-A1   MEMORIA_EPISODICA               si         NO         si      NO       NO
LTMEM-A1   MEMORIA_PERSISTENTE             si         NO         si      NO       NO
LEARN-A1   APRENDIZAJE_POR_EXPERIENCIA     si         NO         si      NO       si
UNC-A1     ESTIMACION_DE_INCERTIDUMBRE     si         NO         si      NO       NO
PLAST-A1   PLASTICIDAD_EXPLORATORIA        si         NO         si      NO       NO
TEMP-A1    INTEGRACION_TEMPORAL            si         NO         si      NO       NO
WM-A1      MODELO_PREDICTIVO_DEL_MUNDO     si         NO         NO      NO       si
PLAN-A1    PLANIFICACION_ANTICIPATORIA     si         NO         NO      NO       NO

listas para certificar: 0 de 9
```

### El hallazgo que reencuadra la Fase 1

**Mundo: falla 9 de 9.** No existe hoy un solo mundo que exija a ninguna de las nueve capacidades.

Eso no es una deuda de infraestructura: **invalida la lectura de todas las ablaciones nulas
medidas hasta ahora**. Que el núcleo temporal, la incertidumbre y las dos memorias «no muevan nada»
en D4T no dice nada sobre ellas, porque D4T exige consumo discriminativo y nada más.

Consecuencia operativa: la Fase 1 no es «correr ablaciones». Es **construir los mundos
diagnósticos**, uno por capacidad, cada uno con su control — y el motor de reglas sólo puede
condicionar sobre `(canal del objeto, acción)`, sin posición, tiempo, historia ni estado del
agente. Si un mundo diagnóstico necesita más que eso, el hueco de gramática es parte del hallazgo.

**Procedencia: falla 9 de 9.** L-1 la incumple el catálogo entero, y hasta repararlo ninguna
capacidad puede certificarse aunque todo lo demás pase.

```bash
python scripts/passport_check.py               # la matriz
python scripts/passport_check.py --detalle EPMEM-A1
```

## 1.2 · Los cuatro brazos mínimos

| Brazo | Qué es |
|---|---|
| **OFF** | sustrato común sin autoridad causal de la capacidad |
| **ON** | mismo sustrato + capacidad |
| **SHAM** | misma interfaz y, cuando proceda, estructura computacional equivalente, **sin función informativa** |
| **ORACLE** | solución de referencia |

**ORACLE no compite contra el agente.** Demuestra dos cosas: que el mundo es resoluble y que el
instrumento puede detectar la capacidad.

## 1.3 · Pureza de la intervención

Entre OFF y ON sólo puede cambiar **la capacidad estudiada**. No puede cambiar accidentalmente el
planner, el optimizador global, la inicialización de módulos no relacionados, la observación, el
mundo, el contrato de acción, el número de entradas downstream, las semillas ni otras pérdidas.

Si falla: `CAPABILITY_INTERVENTION_PURITY = FAIL`. La capacidad **no entra** a la campaña
combinatoria. No se «interpreta con cuidado»: se excluye hasta reparar el contrato.

## 1.4 · Los diez criterios de certificación

Simultáneos, sin excepción:

1. El mundo diagnóstico es resoluble por ORACLE.
2. OFF no resuelve sistemáticamente la demanda.
3. ON produce el efecto previsto.
4. El efecto aparece con semillas emparejadas.
5. El efecto supera un mínimo relevante **preregistrado**.
6. El efecto no depende de una fuga de información.
7. SHAM no reproduce el efecto.
8. La intervención es pura.
9. El efecto aparece en estados o instancias **reservadas**.
10. El instrumento es `REPORTABLE`.

Si falla cualquiera:

```
ALGORITHM_STATUS = NOT_VALIDATED_AS_CAPABILITY      ← nunca CONCEPT_DISPROVED
```

## 1.5 · Tamaño

```
8 semillas diagnósticas × 4 brazos × cada algoritmo candidato
```

Las semillas son **las mismas entre brazos**, nunca independientes:

```
semilla 10001:  OFF · ON · SHAM · ORACLE
semilla 10002:  OFF · ON · SHAM · ORACLE
```

---

# FASE 2 · Single-Capability Campaign

Certificada la capacidad, se pasa al mundo libre. Ya no damos experiencias controladas: preguntamos
**qué cambia realmente en el organismo cuando la posee**.

## 2.1 · El portador: `CYBERNETIC-CARRIER-B0`

**No** «A4 completo y le quitamos cosas» — eso confunde ablación con construcción.

B0 es el sustrato mínimo: percepción · acción · estado de viabilidad · interfaz de capacidades ·
instrumentación pasiva.

```
B₀ + C₁ ,  B₀ + C₂ ,  B₀ + C₃ , …
```

Que es literalmente la doctrina: **se le otorga una capacidad al ser y se observa qué ocurre**.

> **Deuda que esto expone.** B0 no existe. Hoy la composición está ligada a
> `a4_advanced.DEFAULT_CONFIG`, así que «quitar capacidades de A4» es lo único posible. Construir B0
> es `EXPERIMENTAL-COMPOSITION-MODEL` (Apéndice B.2 del canon).

## 2.2 · Controles globales

| | |
|---|---|
| **A0 / random** | referencia no inteligente |
| **Carrier B0** | sustrato común |
| **Agente completo actual** | referencia histórica — **no** patrón oro |

## 2.3 · Horizonte y exposición

```
16 semillas × hasta 5 000 pasos por vida
```

Pero **el paso no es la medida de exposición**. Registro obligatorio por corrida:

```
opportunities offered · opportunities perceived · interactions
informative consequences · learning updates · world changes
```

Porque 5 000 pasos sin experiencias relevantes no son 5 000 muestras. Medido: 300 pasos de D4T
producen 3 eventos informativos.

## 2.4 · Oportunidad: propiedad del mundo vs. conducta

No se le pone comida delante para que aprenda. Pero el mundo **sí** debe garantizar que existen
oportunidades suficientes. Se separan para siempre:

```
OpportunityAvailability      ← propiedad del mundo
OpportunityAcquisitionByAgent ← parte de la conducta
```

## 2.5 · El vector de fenotipo

Cada corrida produce Φ, con dominios de viabilidad/regulación, adaptación, persistencia, retención,
transferencia, generalización, exploración/variedad, incertidumbre, recuperación, monitorización
interna y auto-modificación.

Si un eje no tiene instrumento válido: **`NOT_EVALUABLE`. Nunca 0.**

## 2.6 · La supervivencia no es inteligencia

Un agente puede sobrevivir inmóvil, repitiendo, o explotando una heurística trivial. Por eso cada
capacidad lleva **dos** cosas: un **endpoint específico** que comprueba su función, y el
**fenotipo común** que mide consecuencias sistémicas.

---

# FASE 3 · Composition Campaign

Aquí empieza de verdad la pregunta del proyecto: **qué ocurre al acumular capacidades**.

## 3.1 · Los candidatos no se eligen por intuición

Cada combinación se etiqueta `CORPUS_DECLARED` o `CORPUS_DERIVED`. Nunca `ME_PARECIÓ_INTERESANTE`.

## 3.2 · Nivel 2 — pares

```
I_AB = Y_AB − Y_A − Y_B + Y_0
```

| | |
|---|---|
| `I_AB > 0` | posible interacción positiva no aditiva |
| `I_AB ≈ 0` | compatible con aditividad |
| `I_AB < 0` | interacción negativa no aditiva |

**No se calcula** si hay suelo, techo, soporte insuficiente o instrumento inválido. En ese caso:
`INTERACTION = NON_IDENTIFIABLE`.

> Esto ya ocurrió: los residuos de conjunción del tamizado salieron ininterpretables por saturación
> en el suelo, y se reportaron como número antes de que existiera esta regla.

## 3.3 · Escala

```
máximo 12 pares o conjunciones · 16 semillas pareadas · hasta 10 000 pasos
```

## 3.4 · La excepción habilitadora

Una capacidad puede dar `ΔC_A ≈ 0` por sí sola y ser **necesaria** para `C_A + C_B`. Un efecto
individual nulo **no elimina automáticamente el concepto**. Si el corpus predice una relación
habilitadora, entra a composición como `DEPENDENCY_TEST`.

## 3.5 · Nivel 3 — tríos

Sólo avanzan los pares con evidencia interesante, las dependencias declaradas y las combinaciones
necesarias para probar una hipótesis del corpus. **Nunca búsqueda ciega de 2ᴺ.**

---

# FASE 4 · Progressive World Ladder

> Los mundos siguientes se crean **cuando el nivel anterior está cerrado**.

No se diseñan ahora diez mundos futuros. Se diseña `WORLD-L1` y se **preregistran las dimensiones**
por las que la dificultad puede crecer.

## 4.1 · Ejes permitidos de dificultad

```
escasez · retardo temporal · distancia causa-efecto · parcialidad observacional
ruido sensorial · número de objetos · distractores · cambio de reglas
perturbaciones · duración · dependencia histórica · coste de acción
novedad · conflicto entre objetivos
```

La configuración concreta del siguiente nivel sólo se define **después** de cerrar el anterior.

## 4.2 · Promoción de nivel — L-5

```
correcto:   cerrar L_n → freeze results → seal evidence → analyze
                       → update hypergraph → design L_{n+1} → preregister L_{n+1}

prohibido:  modificar L1 hasta que produzca el resultado deseado
```

Criterios preregistrados de promoción: capacidad · estabilidad · soporte · no dependencia de
atajo · reproducibilidad · viabilidad suficiente para que la prueba tenga sentido.

## 4.3 · Ningún mundo es estático

Pueden cambiar `W_t`, `sensor_t`, `actuator_t`, `resources_t`, `relations_t`, `rules_t`,
`otherAgents_t`, `viabilityRegion_t`, `strategy_t`, `memory_t`. Las fases avanzadas evalúan
inteligencia **bajo historia y transformación**, no en un snapshot estable.

---

# FASE 5 · Confirmatory Holdout

La campaña exploratoria **no decide** el resultado final.

```
32 semillas confirmatorias × hasta 20 000 pasos
configuraciones: B0 · mejor composición 1 · mejor composición 2 · referencia completa actual
```

Semillas nunca usadas, estados nunca vistos, layouts nunca vistos, instancias nunca inspeccionadas.

**La muerte prematura es un outcome, no una razón para reiniciar.**

---

# FASE 6 · Hypergraph Assimilation

Parte esencial de la campaña, no visualización. Por cada resultado se escribe una relación de
evidencia:

```
{ Concept_A, Algorithm_A, Concept_B, Algorithm_B, World_L2, Difficulty, History } → Outcome
```

con `effect · uncertainty · support · seed set · metric versions · code commit ·
capability versions · world hash · status · provenance`.

## 6.1 · Dos capas que no se sobrescriben

| | |
|---|---|
| **Theory edge** | lo que dice el corpus / la ontología |
| **Evidence edge** | lo que observó Terrario |

Un resultado experimental **no sobrescribe la literatura**. Debe poder coexistir:

```
CORPUS:    A complementa B
TERRARIO:  A+B negativo no aditivo bajo W7
```

Ambos permanecen. Eso es conocimiento científico.

> **Deuda medida:** hoy el hipergrafo **no puede** adjuntar evidencia — `corroboration_status` sólo
> admite `NOT_CLAIMED` y `STRUCTURAL_COMPOSITION_NOT_CORROBORATION` — ni registrar contexto. Es
> `INTELLIGENCE-EVIDENCE-HYPERGRAPH` (Apéndice B.3 del canon).

---

# 7 · Disciplina experimental

## 7.1 · Aleatorización por bloque

Nunca todas las B0, después todas las C1. La temperatura, los procesos del sistema o cualquier
deriva temporal se confundirían con la condición. Se bloquea **por semilla**, con orden
preregistrado y aleatorizado:

```
semilla 101:  C3 · B0 · C1 · C2
semilla 102:  C2 · C1 · B0 · C3
```

## 7.2 · Common Random Numbers

`worldSeed_i` idéntico para todas las configuraciones de un bloque, e inicialización base idéntica
en todos los componentes no intervenidos. Así `Δᵢ = Yᵢ(C) − Yᵢ(B₀)` tiene mucha menos varianza.

## 7.3 · Tres categorías de semilla

| | |
|---|---|
| **Development** | para instrumentación. Nunca confirmatorias. |
| **Exploratory** | screening y composición. |
| **Holdout** | no se ejecutan **ni se inspeccionan** hasta que la hipótesis confirmatoria esté congelada. No se reciclan. |

## 7.4 · Inicialización

Se registran `base_parameters_hash`, `capability_parameters_hash`, `optimizer_structure_hash`,
`agent_configuration_hash`.

Una capacidad en OFF **no puede** hacer que otros módulos nazcan con otros pesos sólo porque la
secuencia de RNG cambió. Si ocurre: `INTERVENTION_PURITY = FAIL`.

## 7.5 · Fallos de ejecución

Nunca `crash → rerun hasta que salga`. Un fallo produce `RUN_STATUS = INVALID / FAILED` con
excepción, timestep, semilla, config, hash y última transición válida. La repetición lleva **run ID
nuevo, vinculado al original**.

## 7.6 · Qué queda congelado dentro de una fase

```
learning rate · world physics · reward/economy · action contract
metric definitions · capability algorithm version · initialization protocol
seed manifest · analysis plan · promotion criteria
```

Si algo debe cambiar: `v1 → v2` y **empieza una cohorte nueva**. No se mezcla.

## 7.7 · Presupuesto y su regla de recorte

| Etapa | Escala |
|---|---|
| Certificación | ~8 semillas × 4 brazos × algoritmos |
| Capacidad individual | 16 semillas × hasta 5 000 pasos |
| Combinaciones | 16 semillas × hasta 10 000 pasos |
| Escalera | 24 semillas para composiciones promovidas |
| Confirmación | 32 semillas × hasta 20 000 pasos |

Total estimado: **500–1000 ejecuciones** y varios millones de timesteps.

Si hay que recortar, se recorta **el número de composiciones exploratorias**. Nunca semillas
confirmatorias, controles, holdout, pareado ni instrumentación.

> Seis combinaciones bien medidas valen más que sesenta con dos semillas.

---

# 8 · Datos por corrida

```
campaign_id · cohort_id · run_id
code_commit · runtime_semantics_hash
concept_ids · algorithm_ids · capability_ids · capability_set_hash
world_id · world_version · world_hash · difficulty_vector
seed · world_seed · agent_seed
base_parameters_hash · capability_parameters_hash
steps · termination_reason
trace · events · scientific_state
metric readings · metric support · metric status
instrument versions
pre/post parameter hashes · memory state summary · learning summary
experiment classification · preregistration id
```

# 9 · Artefactos por fase

```
00_MANIFEST              07_CAUSAL_ANALYSIS
01_PREREGISTRATION       08_INTERACTION_MATRIX
02_CAPABILITY_PASSPORTS  09_HYPERGRAPH_EVIDENCE
03_WORLD_CONTRACT        10_FAILURES_AND_DEVIATIONS
04_SEED_MANIFEST         11_DECISION_RECORD
05_RUN_INDEX             12_NEXT_LEVEL_PROPOSAL
06_METRIC_RESULTS
```

**No se avanza de nivel sin `11_DECISION_RECORD`.**

---

# 10 · Stop conditions

La campaña se detiene de inmediato si:

1. Sandbox y runtime científico divergen en física.
2. Una métrica primaria pierde estado `REPORTABLE`.
3. Se detecta fuga de `world_truth`.
4. Dos condiciones supuestamente distintas alteran más de una capacidad.
5. Los pesos base no coinciden donde deberían.
6. Se descubre un alias como `world_model → planner`.
7. El mundo no exige realmente la capacidad analizada.
8. ORACLE no puede resolver el desafío.
9. Hay suelo o techo que vuelve una interacción no identificable.
10. Los holdouts fueron inspeccionados antes del preregistro.
11. El observador cambia la trayectoria.
12. Se produce coerción `NOT_EVALUABLE → 0`.
13. El runtime cambia a mitad de cohorte.
14. Un hash protegido requeriría regeneración automática → **parada humana**.

---

# 11 · Resultado final

No un ranking. Un **`INTELLIGENCE CAPABILITY MAP v0.1`**:

```
Concept → Algorithm → Capability → WorldRequirement → Effect → Interaction → Phenotype
```

y para cada relación: **evidencia + incertidumbre + contexto + provenance**.

La forma que debería tener:

```
Capability A     indispensable en W1 · irrelevante en W2 · perjudicial bajo escasez severa
Capability B     efecto individual nulo · habilita C bajo retardo largo
Capability C+D   interacción positiva · desaparece con ruido perceptivo
Capability E     robusta y transferible
Algorithm E2     supera a E1
Composition S17  mantiene viabilidad · se adapta · recupera tras perturbación · no transfiere
```

Eso sí empieza a ser una teoría computacional de inteligencia.

---

# 12 · Backlog

| | Paquete | Estado |
|---|---|---|
| **P0** | `WORLD-RUNTIME-PARITY-01` — una física ejecutable única | ✅ **PASS** |
| **P1** | `CAPABILITY-PASSPORTS-01` — concepto → operacionalización → algoritmo → capacidad | ✅ **cerrado** — 9 pasaportes, 0 listos |
| **P2** | `CAPABILITY-CERTIFICATION-01` — mundos diagnósticos + OFF/ON/SHAM/ORACLE | pendiente |
| **P3** | `TCS-01-SINGLE` — capacidades individuales | pendiente |
| **P4** | `TCS-01-COMPOSITION` — pares y tríos guiados por corpus | pendiente |
| **P5** | `TCS-01-LADDER` — escalamiento de mundos | pendiente |
| **P6** | `TCS-01-CONFIRMATORY` — holdout científico | pendiente |
| **P7** | `INTELLIGENCE-CAPABILITY-MAP-v0.1` — ingesta al hipergrafo | pendiente |

## 12.1 · Lo que P0 debe cerrar para que P1 empiece

```
✅ find_target unificado
✅ build_episode_components unificado
✅ run_step — una sola secuencia de paso
✅ ciclo de oportunidades encendido en el banco     32→29 objetos pasó a 32→32, con 3 reaparecidos
✅ set_global_determinism simétrico                 mismo spec ⇒ mismo hash de parámetros
✅ test de paridad automático, 6 pruebas            falla nombrando PRIMER paso y PRIMER campo
```

**`WORLD_RUNTIME_PARITY = PASS`.** Toda evidencia anterior queda declarada
`runtime Sandbox pre-parity`.

---

> **TCS-01 en una frase.** No entrenar A4 durante horas esperando que aparezca inteligencia, sino
> iniciar un programa masivo, causal, progresivo y acumulativo para sintetizar experimentalmente
> qué arquitectura de capacidades necesita el ser cibernético.
