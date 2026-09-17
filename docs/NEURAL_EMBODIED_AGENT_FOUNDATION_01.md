# NEURAL-EMBODIED-AGENT-FOUNDATION-01 · dossier de Gate 0

**Encargo:** ORIENTACIONES PARA ANTHROPIC, 2026-09-17, §100.
**Alcance:** auditoría y diseño. **Ningún código escrito, ningún contrato modificado** (§63, §107).
**Estado del árbol al auditar:** rama `experiment/cognitive-live-observatory-01`, HEAD `838bcaf`,
worktree limpio, 0 ficheros modificados, 0 stash, un solo worktree. **No había WIP que proteger**
(§64).

---

## A · Auditoría real de Terrario

### A.1 El presupuesto de cómputo, que decide más de lo que parece

```
torch 2.5.1+cu121        CUDA disponible: False
12 núcleos               6 hilos de torch
23 GB RAM                sin GPU
```

`CUDA_OS_BLOCKED` es un bloqueador **declarado y activo** en `project_manifest.json`. No es una
circunstancia pasajera de la sesión: el proyecto lo lleva registrado.

Medido hoy sobre D4T, 1200 pasos, runtime directo: **93 ms/paso**, 112 s por corrida, 8 corridas
en 13 min. La matriz completa de efectos principales —9 condiciones × 5 semillas = 45 corridas—
cuesta **≈ 1,4 h**. Ése es el presupuesto real que existe, y es el que §74 dice que debe mandar.

### A.2 La superficie sensorial, medida

```
observación del agente     127 dimensiones
   channels  (4, 5, 5)     100   ventana local, radio 2
   mask      (5, 5)         25   visibilidad
   agent_energy              1   ← única variable interoceptiva
   time_fraction             1   reloj, no interocepción

espacio de acción           25   5 acciones × 5 direcciones
                                 MOVE · PUSH · CONSUME · INSPECT · NOOP
```

**La interocepción de Terrario es un escalar.** No hay integridad, ni daño, ni temperatura, ni
reservas, ni margen de viabilidad. Y `agent_energy` viene **normalizado por `max_energy`**, así
que el organismo no puede distinguir 60/100 de 600/1000.

### A.3 El cortafuegos de fuga: ya existe y está aplicado

```python
def validate_projection(self, projection):
    forbidden = set(projection) & OBSERVER_ONLY_FIELDS
    unknown   = set(projection) - AGENT_FIELDS
    if forbidden or unknown: raise LeakageError(...)
```
`world_contracts.py:97-101`

`AGENT_FIELDS = {channels, mask, agent_energy, time_fraction}` ·
`OBSERVER_ONLY_FIELDS = {world, world_truth, objects, agents, occupancy, rules, rules_version,
causal_property, energy_value}`.

**§35, §36 y §37 están sustancialmente satisfechos por contrato**, no por disciplina. El
laboratorio conoce `world_truth`; la política no puede pedirlo sin que el contrato lance. Es la
pieza más sólida del sistema y conviene no tocarla.

### A.4 El stack de agentes

| | parámetros | plasticidad | homeostasis |
|---|---:|---|---|
| A0 Random | 0 | ninguna — `learn()` es no-op | no |
| A1 Reactive | 170.169 | Adam, REINFORCE | no |
| A2 GRU | 499.385 | Adam, REINFORCE | no |
| A3 WorldModel | 703.675 | Adam, modelo + REINFORCE | no |
| **A4 Advanced** | **1.351.617** | `OnlineLearner` | **sí** |

**A0 es el agente nulo que pide §40, y ya existe.**

A4 tiene ocho módulos ablacionables por configuración: `use_temporal`, `use_episodic_memory`,
`use_longterm_memory`, `use_world_model`, `use_uncertainty`, `use_planner`,
`use_online_learning`, `use_homeostasis`. Más `homeostasis_threshold` como número declarable.

### A.5 Mundos

`D0` diferencias · `D1` objetos y persistencia · `D2` propiedades y binding · `D3` causalidad ·
`D4`/`D4S` adaptación · `D4T` variedad temporal (tres inversiones a intervalos iguales).
`D5`–`D11` son `FUTURE_DESIGN` en el manifiesto: herramientas, planificación, incertidumbre,
signos, social, linaje, cultura.

### A.6 Instrumentos

12 métricas registradas. **Una sola con `VALIDATED_FOR_CONSTRUCT`**:
`planned-action-evaluation-pathway`. Las de viabilidad están implementadas y deliberadamente sin
promover — promover es firma humana.

### A.7 La cadena científica

```
144 Preregistration · 141 PREREGISTERED_LOCKED · 141 autorizaciones
141 ejecuciones · 238 intentos COMPLETED · 476 artefactos crudos
  1 verificación PASS 5/5

  0 METRIC_RESULT        0 scientific_results        0 empirical_evidence
```

La cadena llegó al último metro y se detuvo. El eslabón que falta —evaluar un instrumento
preregistrado sobre una traza sellada y sellar el resultado— existe ahora como
`metric_result_sealing.py`, con ocho tests y **cero uso sobre datos reales**.

---

## B · Mapa de integración

Dónde entraría un organismo neuronal nuevo **sin romper contratos**:

| capa | contrato que la gobierna | ¿puede entrar algo nuevo? |
|---|---|---|
| Observación | `ObservationContract`, `AGENT_FIELDS` | **no sin decisión**: ampliar la interocepción cambia qué ve el agente |
| Agente | `AgentInterface` (`perceive`/`decide`/`learn`) | **sí** — es donde entra, junto a A0–A4 |
| Acción | `ActionContract`, 25 acciones | sí, sin cambios |
| Mundo | `WorldStateManager`, reglas, `ChangeScheduler` | sí, escenarios nuevos son aditivos |
| Observador | 9 canales, `SCIENTIFIC_TRACE` | **sí, con cuidado** — canal nuevo = mecanismo nuevo |
| Métricas | `MetricRegistry` | sí, aditivo |
| Persistencia | CAS + ledger append-only | sin cambios |

El punto de entrada natural es **A5**, registrado aditivamente en `agent_composition.CONCEPTS`
y en la fábrica, exactamente como se registró D4T entre los mundos. Nada del contrato científico
necesita moverse para alojarlo.

**Riesgo de integración identificado hoy y no resuelto:** hay dos caminos de ejecución del
sandbox — la pantalla usa HTTP con streaming en vivo, el arnés de tamizado usa el runtime
directo. Pueden divergir como divergieron `compile_draft` y `controller` hasta esta mañana.

---

## C · Comparación arquitectónica

### C.1 El hallazgo que reordena la comparación

**La abstracción intercambiable que pide §12 ya existe en el repositorio.**

```python
class TemporalCore(nn.Module):     # interfaz abstracta
class GRUCore(TemporalCore)        # recurrente
class SSMCore(TemporalCore)        # state-space lineal: h_t = diag(a)·h_{t-1} + B·x_t
```
`agent/temporal.py:16, 43, 63` — y `DEFAULT_CONFIG["temporal_core"] = "ssm"`.

Terrario **ya corre con un núcleo SSM por defecto**, ya tiene la elección GRU/SSM tras una
interfaz, y ya puede ablacionarla con `use_temporal`. El `DynamicsBackend` del §12 no hay que
inventarlo: hay que extenderlo del núcleo temporal a la dinámica latente completa.

### C.2 Las tres familias contra las restricciones reales

| | RSSM compacto | Transformer (Dreamer-4-like) | Mamba-2 / SSM |
|---|---|---|---|
| encaje con 127 dims | **holgado** | capacidad muy por encima de la señal | holgado |
| coste sin GPU | el único viable medido | **prohibitivo**: sin CUDA, atención O(L²) sobre 1200 pasos | bueno, O(L) |
| semillas y ablaciones posibles | 45 corridas ≈ 1,4 h | días por matriz | comparable a RSSM |
| identificabilidad causal | alta: estado explícito | baja: estado disperso en la atención | media |
| auditabilidad | alta | baja | media |
| datos que necesita | pocos | muchos | medios |
| ya presente en el repo | parcial (GRU/SSM core) | no | **sí, `SSMCore`** |

**La restricción decisiva no es teórica, es aritmética.** §74 pide un modelo que permita muchas
corridas; §76 define utilidad científica como función de reproducibilidad, observabilidad y
modularidad, no de rendimiento. Con 127 dimensiones de observación, 25 acciones y **sin GPU**, un
Transformer compra expresividad que la señal no puede usar y paga con el presupuesto que hace
posible el método.

### C.3 Qué aportaría Mamba-2, concretamente

Su ventaja es contexto largo a coste lineal. Los episodios de Terrario son de 1200 pasos, así que
la ventaja **es real en principio**. Pero:

1. Ya hay un `SSMCore`, y es el default.
2. **Nadie ha demostrado todavía que el núcleo temporal importe.** `use_temporal` es ablacionable
   y el tamizado de hoy no lo incluyó.

Por tanto la pregunta 3 del §101 tiene una respuesta empírica disponible **antes** de importar
nada: correr el tamizado con `use_temporal` entre las condiciones. Si ablacionar el núcleo
temporal no mueve ninguna de las nueve mallas en D4T, cambiar `SSMCore` por Mamba-2 no puede
aportar nada todavía, y el trabajo estaría en el mundo, no en el backbone.

---

## D · Arquitectura recomendada

**Latent Embodied World Model modular**, con dinámica de referencia compacta tipo RSSM detrás de
la interfaz `TemporalCore` ya existente, extendida a `DynamicsBackend`.

```
  exterocepción (channels, mask)        interocepción (vector, hoy escalar)
              │                                      │
        encoder externo                     encoder interoceptivo
              └──────────────┬───────────────────────┘
                      estado latente z_t = [z_world, z_self, z_coupling]
                                   │
                        dinámica condicionada por acción
                          p(z_{t+1} | z_t, a_t)        ← DynamicsBackend
                                   │
        ┌──────────────┬───────────┴───────┬────────────────┐
   predicción      incertidumbre      imaginación      estimador de viabilidad
   mundo/self       epistémica         rollouts             (riesgo)
        └──────────────┴───────────┬───────┴────────────────┘
                          arbitraje motivacional
                                   │
                              actor / valor
```

Los tres bloques `z_world / z_self / z_coupling` del §34 **deben ser condición experimental, no
decisión de diseño**: arquitectura A (latente único), B (factorizado), C (factorizado con
acoplamiento) son tres brazos comparables con el mismo contrato de medición.

---

## E · Frontera innato / aprendido

| | innato | aprendido | estado en Terrario |
|---|:--:|:--:|---|
| sensores y su geometría | ✓ | | existe: ventana 5×5, 4 canales |
| espacio de acción | ✓ | | existe: 25 acciones |
| señal interoceptiva | ✓ | | **existe sólo como escalar normalizado** |
| mecanismo de plasticidad | ✓ | | existe: `OnlineLearner` |
| arquitectura del encoder | ✓ | | existe |
| dinámica recurrente | ✓ | | existe: GRU/SSM |
| capacidad de memoria | ✓ | | existe: episódica y largo plazo |
| **qué objeto es comida** | | ✓ | prohibido precargar |
| **qué acción preserva viabilidad** | | ✓ | prohibido precargar |
| **estructura causal del mundo** | | ✓ | prohibido precargar |
| **mapa del mundo** | | ✓ | prohibido — el agente ve radio 2 |
| categorías perceptuales | | ✓ | no demostradas |
| política | | ✓ | aprendida, hoy por refuerzo energético |

La frontera está **bien defendida por el contrato de observación**: nada de la columna prohibida
puede llegar al agente sin que `validate_projection` lance.

---

## F · Contrato de motivación

§17 pide evaluar un vector. Mi lectura, contra lo que Terrario puede sostener hoy:

| componente | definible hoy | bloqueo |
|---|---|---|
| `M_v` presión de viabilidad | **parcial** | existe `exploration_bias = 1 − energía` → temperatura; una sola vía, un solo parámetro |
| `M_i` ganancia de información | no | requiere modelo con incertidumbre calibrada; `UncertaintyEstimator` existe pero su salida no alimenta ninguna decisión |
| `M_c` progreso de competencia | no | no hay medida de competencia preregistrada |
| `M_n` novedad | trivialmente sí | y §18/§19 explican por qué no debe usarse sola |
| `M_e` empowerment | no | requiere estimar I(A;S′), inviable sin modelo |
| `M_x` externa | **sí, y es el problema** | `energy_delta` ES la recompensa |

**El bloqueo central del encargo entero está aquí.** §14 exige separar restricción de viabilidad
de impulsos de optimización. En Terrario hoy:

```
variable esencial  = agent.energy               core/types.py:87
señal de refuerzo  = consequence.energy_delta   a1:86 · a3:141 · a4:417
```

Son la misma magnitud, una en nivel y otra en diferencia. **`do(reward = 0)` es
`do(energy_delta = 0)`**, que suprime la variable esencial en vez de aislarla. Mientras eso siga
así, ninguna pregunta del §101 sobre motivación es decidible: cualquier resultado queda
confundido con «la recompensa gobierna la política», que es la hipótesis nula.

---

## G · Contrato del world model

**Recibe:** `z_t`, `a_t`. **Predice:** `z_{t+1}`, y cabezas separadas para estado externo y
estado interno. **Aprende:** por error de predicción propio, no por recompensa.

Medición (§49), y ninguna es reconstruction loss sola: predicción a un paso · a varios pasos ·
condicionada por acción · **calibración** · consistencia contrafactual · predicción del propio
estado interno · desempeño fuera de distribución.

Terrario hoy tiene `WorldModel` en A3 y A4 prediciendo `energy_delta` y `done`. Es un predictor
de consecuencia inmediata, no una dinámica latente. La distancia es real.

---

## H · Contrato del modelo de sí mismo

Operacionalmente, y sin afirmar fenomenología (§4): **`z_self` es la parte del latente desde la
que se puede predecir el estado interno futuro mejor que desde `z_world`.**

Test de existencia, falsable: entrenar dos sondas lineales congeladas sobre `z_t` —una para
variables internas futuras, otra para propiedades externas futuras— y comprobar disociación. Si
ambas leen igual de bien de todo el latente, **no hay self-model, hay concatenación** (§101 Q5).

**Bloqueo declarado:** con una sola variable interoceptiva, `z_self` tiene casi nada que
representar. Este contrato no es ejecutable hasta que la interocepción sea un vector.

---

## I · Contrato de imaginación

Un rollout es `z_t → ẑ_{t+1} → ẑ_{t+2} …` bajo acciones hipotéticas, **sin tocar el mundo**.

Validación obligatoria (§26, §93): comparar trayectoria imaginada contra realizada a horizontes
crecientes, y registrar el error por horizonte. Un actor que mejora en imaginación mientras el
error de rollout crece está explotando el modelo, no planificando.

Terrario ya tiene el precedente exacto: `planned-action-evaluation-pathway` mide **disponibilidad
de la vía**, no calidad del plan, y lo declara en su propio `does_not_measure`.

---

## J · Contrato de memoria

Tres cosas que no deben confundirse: estado temporal de trabajo · experiencia episódica ·
abstracción semántica.

**El test es causal y ya está escrito en §29:**

```
P(A | O, H₁) ≠ P(A | O, H₂)     con la observación presente equivalente
```

Escribir y recuperar no cuenta. Terrario ya tiene el antecedente: `drive` se calcula, se reporta
en el estado científico y **no se consume en ninguna parte**. Y tres campos declarados del
contrato —`parameter_delta_norm`, `current_loss`, `gradient_norm`— están permanentemente en
`NOT_APPLICABLE` porque el agente los calcula y no los expone. Eso es `implementado ⇏ usado`
(§42) con nombre y línea.

---

## K · Contrato de medición

| | |
|---|---|
| hipótesis primaria | un sustrato con dinámica latente aprendida y acceso interoceptivo anticipa consecuencias sobre su propia viabilidad mejor que controles sin esa representación |
| hipótesis nula | la anticipación observada se explica por la política aprendida por refuerzo energético, sin contribución del estado latente |
| intervención | ablación del backend de dinámica, manteniendo encoder, memoria y política |
| control | A0 aleatorio · A4 con dinámica ablacionada · mismo mundo, mismas semillas |
| outcome primario | **BLOQUEADO** — ver §M |
| outcomes secundarios | las nueve mallas de `run_measures` que sobreviven a toda ablación |
| condición de fallo | el efecto no supera la dispersión entre semillas del propio brazo |

---

## L · Matriz de ablación

Independientemente desactivables **hoy**: núcleo temporal · memoria episódica · memoria a largo
plazo · modelo del mundo · incertidumbre · planificador · aprendizaje en línea · homeostasis.

Que un organismo nuevo debería añadir: dinámica latente · interocepción · imaginación ·
cada impulso motivacional por separado · el estimador de viabilidad.

**Requisito derivado de §41:** todo mecanismo nuevo nace con su bandera. La homeostasis de A4
vivió sin bandera hasta hoy, y por eso el bloque 1 no tenía experimento posible.

---

## M · Matriz de observabilidad

El observador puede leer sin intervenir: `world_truth` completo · energía y vida · versión de
reglas · decisión · traza del planificador · error de predicción · incertidumbre · entropía de la
política · ablaciones activas.

**No puede leer, y es el hueco:** la magnitud del cambio propio. `parameter_delta_norm` no llega
al sandbox. Es la observación más pertinente a «crecimiento» (§31) y no existe.

---

## N · Registro de riesgos

| modo de fallo (§89–99) | ¿ya observado en Terrario? |
|---|---|
| survival freeze | **parcialmente**: el organismo no supera a la pasividad — neto ≈ 0 en las cuatro condiciones |
| curiosidad suicida | no aplicable: no hay curiosidad |
| noisy TV | no aplicable todavía |
| reward hacking | **riesgo alto**: la recompensa es la variable esencial |
| explotación del modelo | no medido: no se compara imaginado contra realizado |
| colapso de representación | no medido |
| memoria sin autoridad | **observado**: `drive` calculado y nunca consumido |
| módulo sin autoridad | **observado**: tres campos del contrato permanentemente `NOT_APPLICABLE` |
| emergencia programada a mano | prevenido por el cortafuegos de observación |
| deriva de métrica | prevenido por preregistro sellado |
| efecto del observador | **riesgo abierto**: carrera intermitente en el índice del archivo de traza |

---

## O · Plan de integración

```
1  decidir cuál de las tres fronteras de viabilidad es 𝒱          humano, sin código
2  separar la variable esencial del refuerzo                      desbloquea todo lo demás
3  interocepción como vector, con su ablación                     contrato de observación
4  DynamicsBackend: extender TemporalCore a dinámica latente      aditivo, tras A0–A4
5  tamizar el backend contra A4 y A0                              usa el arnés que ya existe
6  imaginación + validación de rollout por horizonte
7  impulsos motivacionales, uno por uno, cada uno con su bandera
```

Los pasos 1 y 2 no son código. Son la condición para que los demás signifiquen algo.

---

## P · Condiciones de parada (§P, §15)

Me detengo y reporto en vez de inventar cuando:

- **los umbrales de viabilidad no estén fijados.** Hoy hay **tres sin reconciliar**: muerte del
  mundo en `energy <= 0`, umbral del organismo en `0.5`, η del observador ≈ `0.23`. §15 prohíbe
  elegir números; **este bloqueo está activo.**
- no exista medida preregistrada de competencia — **activo**.
- `dwell_k` y la banda de viabilidad no provengan del contrato — **activo**.
- un componente nuevo no pueda ablacionarse.
- una métrica se elija después de ver resultados.

---

## Respuestas explícitas a §101

**1 · ¿Hace falta una red neuronal?** Para la pregunta tal como está formulada, **sí, y por una
razón precisa**: §5 prohíbe que especifiquemos la relación que luego pretenderíamos descubrir. Un
controlador escrito a mano la especifica. Pero la red no es suficiente: hoy A1–A4 son redes y
ninguna demuestra adquisición conceptual.

**2 · ¿RSSM mejor que Transformer para un Terrario 2D?** Sí, y no por elegancia: 127 dimensiones,
25 acciones, **sin GPU**, y un método que necesita decenas de corridas.

**3 · ¿Qué aportaría Mamba-2?** Contexto largo barato. **Es comprobable antes de importarlo**:
ablacionar `use_temporal` en el tamizado. Si no mueve ninguna malla, la respuesta es «nada
todavía».

**4 · ¿Qué componente construye el estado self-world?** La fusión de ambos encoders más la
dinámica. No existe hoy.

**5 · ¿Cómo distinguir self-model de concatenación?** Disociación de sondas — §H.

**6 · ¿Qué variables deben ser interoceptivas?** Derivarlas del contrato del mundo, no
inventarlas (§7). Lo que el mundo ya sostiene: energía **sin normalizar**, vivo/muerto, y margen
hasta la frontera una vez decidida cuál es. Todo lo demás requiere física nueva.

**7 · ¿Qué está prohibido precargar?** La columna «aprendido» de §E, y el contrato ya lo impone.

**8 · ¿Cómo aprende viabilidad sin darle la regla?** Prediciendo su propio estado interno futuro
y pagando el error de esa predicción — no recibiendo recompensa por sobrevivir.

**9 · ¿Cómo evitar reward shaping?** Que los términos entren como restricciones, estimadores y
señales de aprendizaje, no sumados en un escalar (§32).

**10 · ¿Curiosidad sin noisy-TV?** Progreso de aprendizaje o ganancia de información, no error de
predicción. §18–19.

**11 · ¿Competencia falsable?** **UNRESOLVED.** No tengo una que no contenga ya las tareas
futuras. Es un bloqueo declarado, no una omisión.

**12 · ¿Empowerment aporta?** **UNRESOLVED** sin modelo calibrado. Probablemente redundante con
viabilidad + ganancia de información en un mundo de 25 acciones.

**13 · ¿Arbitrar curiosidad y riesgo?** Como restricción con presupuesto de riesgo, no como suma
ponderada (§24).

**14 · ¿Imaginación causalmente?** Ablación del rollout con el resto intacto, más error imaginado
contra realizado por horizonte.

**15 · ¿Memoria afecta conducta?** El test de §29, que ya está escrito.

**16 · ¿El latente contiene self/world?** Sondas congeladas, §H.

**17 · adaptación vs aprendizaje** Persistencia tras demora e interferencia.

**18 · aprendizaje vs meta-aprendizaje** El proceso de aprender debe cambiar, demostrablemente.
Fuera del primer cierre.

**19 · ¿crecimiento?** Batería de propiedades, no un score (§31, §51).

**20 · ¿persistencia?** Retest bajo la misma métrica congelada tras demora.

**21 · ¿transferencia?** `d4_adaptation_transfer.yaml` existe y **no tiene constructo validado**.

**22 · ¿más ablaciones limpias?** RSSM compacto.

**23 · ¿más semillas bajo este cómputo?** RSSM compacto, sin comparación.

**24 · ¿más fácil de auditar causalmente?** RSSM: el estado es explícito y legible.

**25 · ¿qué rescatar de lo neural existente?** `TemporalCore` con sus dos implementaciones, el
`UncertaintyEstimator`, la memoria episódica, y sobre todo **el contrato de observación**.

**26 · ¿qué descartar?** La política REINFORCE sobre `energy_delta` como único aprendizaje.

**27 · ¿qué no debe entrar todavía?** Reasoning estructurado (§71), maestro externo (§72), LLM
como cerebro (§73).

**28 · ¿reproducibilidad?** Semillas declaradas, dispositivo fijado en CPU, y **declarar** dónde
sólo hay reproducibilidad estadística (§45).

**29 · ¿qué ve sólo el laboratorio?** Los nueve campos de `OBSERVER_ONLY_FIELDS`.

**30 · ¿qué ve el organismo?** Los cuatro de `AGENT_FIELDS`. 127 dimensiones.

---

## Veredicto (§106)

```
NEURAL_SUBSTRATE_REQUIRED = PARTIAL
    Necesario para no especificar la relación que queremos descubrir.
    Insuficiente: A1–A4 ya son redes y ninguna demuestra adquisición.

RECOMMENDED_WORLD_MODEL_FAMILY = RSSM compacto tras DynamicsBackend
WHY = 127 dims · 25 acciones · SIN GPU · el método necesita decenas de corridas.
      §76 define utilidad científica por reproducibilidad y ablación, no por rendimiento.

SELF_MODEL_ARCHITECTURE = z = [z_world, z_self, z_coupling] COMO CONDICIÓN EXPERIMENTAL,
      comparada contra latente único. Existencia probada por disociación de sondas.

INTEROCEPTION_REQUIREMENTS = BLOQUEADO. Hoy un escalar normalizado.
      Mínimo para que z_self signifique algo: energía sin normalizar, estado vital,
      margen a la frontera — y la frontera no está decidida.

INNATE_COMPONENTS  = sensores · acciones · plasticidad · encoders · dinámica · memoria
LEARNED_COMPONENTS = categorías · causalidad · política · valor · qué preserva viabilidad

INTRINSIC_MOTIVATION_SET = viabilidad + ganancia de información. Competencia y empowerment
      UNRESOLVED hasta tener medida falsable de competencia.
EXTRINSIC_MOTIVATION_ROLE = condición experimental, nunca el único canal.

VIABILITY_MECHANISM = restricción sobre variables esenciales, NO recompensa. BLOQUEADO:
      hoy la variable esencial y el refuerzo son el mismo número.
CURIOSITY_MECHANISM = progreso de aprendizaje / ganancia de información, no novedad.
COMPETENCE_GROWTH_MECHANISM = UNRESOLVED
IMAGINATION_MECHANISM = rollout latente con validación por horizonte
MEMORY_ARCHITECTURE = trabajo + episódica + largo plazo, cada una con test de autoridad causal

MAJOR_FAILURE_MODES = reward hacking (riesgo alto, la recompensa es la variable esencial) ·
      módulo sin autoridad (ya observado) · survival freeze (parcialmente observado) ·
      explotación del modelo (no medido) · efecto del observador (carrera abierta)

REQUIRED_ABLATIONS = dinámica · interocepción · imaginación · cada impulso · viabilidad ·
      más los ocho módulos que ya se ablacionan

PRIMARY_CAUSAL_HYPOTHESIS = un sustrato con dinámica latente e interocepción anticipa
      consecuencias sobre su propia viabilidad mejor que controles sin esa representación
PRIMARY_NULL_HYPOTHESIS = lo anticipado se explica por la política de refuerzo energético

MEASUREMENT_BLOCKERS =
      1. tres fronteras de viabilidad sin reconciliar
      2. variable esencial == señal de refuerzo
      3. sin medida falsable de competencia
      4. cambio propio (parameter_delta_norm) no observable
      5. dwell_k y banda de viabilidad no fijados por contrato

CURRENT_TERRARIO_BLOCKERS =
      CUDA_OS_BLOCKED · 0 scientific_results · una sola métrica validada ·
      el organismo no supera a la pasividad en D4T · D5–D11 sin construir

CURRENT_RNFE_COMPONENTS_WORTH_REUSING = contrato de observación y su cortafuegos ·
      TemporalCore (GRU/SSM) · UncertaintyEstimator · memoria episódica · ledger sellado
CURRENT_RNFE_COMPONENTS_TO_AVOID = REINFORCE sobre energy_delta como único aprendizaje ·
      cualquier default silencioso sobre parámetros que son contenido científico

READY_FOR_IMPLEMENTATION = NO
```

### Qué falta exactamente para que sea SÍ

1. **Decidir cuál de las tres fronteras es `𝒱`.** Decisión humana, sin código. Bloquea toda
   afirmación sobre regulación.
2. **Separar la variable esencial del refuerzo.** Sin esto, la hipótesis nula no se puede
   rechazar por construcción.
3. **Interocepción como vector**, o `z_self` no tiene qué representar.
4. **Una medida de competencia falsable**, o «crecimiento» sigue siendo metáfora.

Ninguna de las cuatro es una decisión de arquitectura. Las cuatro son anteriores a ella, que es
exactamente lo que dice el orden del §102.

---

**DETENIDO EN §107.** Ningún código escrito. Ningún contrato modificado. Ni H-Net, ni Mamba, ni
Dreamer, ni RNFE conectado, ni métricas tocadas, ni D4/D4S alterados.
