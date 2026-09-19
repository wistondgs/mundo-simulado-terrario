# ADAPTIVE-REGULATION-01 · FASE 0

Auditoría de código previa a tocar una línea. Cada respuesta lleva `archivo:línea`.
Clasificación: **HECHO DE CÓDIGO** (se lee), **HECHO MEDIDO** (se corrió),
**INFERENCIA** (se deduce de los dos anteriores).

Árbol: `/home/wis/causal-bench-01`, rama `bench/causal-capability-01`.

---

## Resumen ejecutivo

La FASE 0 encontró lo que hacía falta para construir el borde —un predictor de
consecuencia energética condicionado a la acción, evaluable en las 25 acciones sin
planner— y **encontró también que la variable esencial que ese borde debe regular no
se mueve en el mundo donde el organismo aprende**.

En el mundo rico, el `drive` es mayor que cero en **2 de 300 pasos (1 %)**, con
varianza `0.000000`. El brazo `ADAPTIVE_REGULATOR` y el brazo `NO_DRIVE_LEARNER`
serían numéricamente idénticos en el 99 % de los pasos. El experimento, tal como está
mandado, devolvería un nulo que no significa nada.

La causa no es el umbral. Son tres defectos encadenados, ninguno en A4.

---

## Las 17 respuestas

### Bloque I · La señal de necesidad

**1 · ¿Dónde se calcula `drive`?**
`homeostasis.py:39` — `return max(0.0, self._threshold - self._energy)`. Propiedad
calculada, no almacenada. **HECHO DE CÓDIGO**

**2 · ¿Quién lo consume?**
Nadie causalmente. Dos apariciones: `a4_advanced.py:513` y `a4_advanced.py:562`, las
dos dentro de `self._trace.append({...})`. Es un observable, no una causa.
**HECHO DE CÓDIGO**

**3 · ¿Dónde se calcula `energy_delta`?**
`transition.py:366` `energy_delta = rules.apply_effects(...)` y `transition.py:374`
`energy_delta += world.apply_step_energy_cost(0)`. Es decir: **efecto de regla + coste
de paso**, en unidades **absolutas**. `rules.py:129` lo lee del escenario.
**HECHO DE CÓDIGO**

**4 · ¿Quién escribe `homeostasis._energy`?**
Dos sitios, y escriben **magnitudes distintas**:
- `a4_advanced.py:358` (en `perceive`) → `= observation.agent_energy`, **normalizada** [0,1]
- `a4_advanced.py:583` (en `learn`) → `update(consequence.energy_delta)`, **absoluta**

`homeostasis.py:59` hace `self._energy = max(0.0, min(1.0, self._energy + energy_delta))`.
**HECHO DE CÓDIGO** → ver **D1**.

### Bloque II · El predictor de consecuencia

**5 · ¿Tiene el modelo del mundo una cabeza de energía condicionada a la acción?**
Sí. `a4_advanced.py` llama `self.world_model(state, action_onehot)` y recibe
`(next_state, energy_pred, _)`. La cabeza existe y toma la acción como entrada.
**HECHO DE CÓDIGO**

**6 · ¿Qué objetivo recibe?**
`a4_advanced.py:635` — `consequence.energy_delta`. El mismo número que la regla del
mundo produjo. **HECHO DE CÓDIGO**

**7 · ¿Cuándo se actualiza?**
En `learn()`, por el `OnlineLearner`, bajo `optimizer.step()`; es decir, bajo el
control de `learning_commit_enabled` y del componente `parameters` de la huella
adaptativa. **HECHO DE CÓDIGO**

**8 · ¿Puede evaluarse para las 25 acciones sin el planner multistep?**
**Sí, y ya se hace.** `diagnostic_probes.py:147-162` (`consume_advantage_on`) recorre
`for action_int in range(TOTAL_ACTIONS)`, construye el one-hot y llama
`agent.world_model(state, onehot)`. Se corre en cada lectura del banco de sondas,
bajo `passive_probe`, sin tocar azar ni estado recurrente.
**HECHO MEDIDO** — es el instrumento con el que se midió DISCOVERY-32.

### Bloque III · La ruta a la acción

**9 · ¿Qué ruta transforma valoración en acción?**
`a4_advanced.py:544-547`, rama `else` — `policy_head.sample(logits, temperature)`.
`policy.py:75` ofrece además `greedy(logits)`. **HECHO DE CÓDIGO**

**10 · ¿Puede esa ruta recibir una señal homeostática genérica?**
Sí, y el patrón ya está en uso: `a4_advanced.py:438` —
`logits = logits + 0.1 * uncertainties`. Sumar un vector de 25 a los logits antes de
muestrear es una operación que el código ya hace. **HECHO DE CÓDIGO**

**11 · ¿Qué depende obligatoriamente del planner?**
El planner se invoca en dos sitios, los dos guardados por
`self._use_planner and self._use_world_model` (`a4_advanced.py:461`, `a4_advanced.py:528`).
Nada fuera de esos guardas lo requiere; `a4_advanced.py:816` sólo vacía su traza.
**HECHO DE CÓDIGO**

**12 · ¿Qué ocurre con el planner desactivado?**
Medido antes: 0 CONSUME efectivos. Pero `a4_advanced.py:536-541` muestra que el
planner sólo gana la decisión con `plan_prob = 0.5`; la política **puede** emitir
CONSUME. La lectura correcta no es «sin planner no puede», sino **«sin planner nunca
aprendió a hacerlo, porque el planner generaba las experiencias de consumo de las que
la política aprende»**. **INFERENCIA** sobre dos hechos de código y una medición.

**13 · ¿Existe un selector one-step reutilizable?**
En el agente, **no**: `policy.py:75 greedy()` opera sobre logits, no sobre el modelo
del mundo. Fuera del agente, **sí**: `diagnostic_probes.py:147-162`. Es una función de
laboratorio, no un órgano. **HECHO DE CÓDIGO** → decide el CASO (ver abajo).

### Bloque IV · Legitimidad y contabilidad

**14 · ¿Qué señales de recompensa ya usan `energy_delta`?**
Tres consumidores: `_policy_reward`, el objetivo `energy_target` del modelo del mundo
(`a4_advanced.py:635`) y el objetivo de las cabezas de incertidumbre
(`a4_advanced.py:728-731`). **HECHO DE CÓDIGO**

**15 · ¿Es la energía observada verdad legítima o información privilegiada?**
**Legítima con una salvedad grave.** `state.py:110` —
`energy_norm = min(agent.energy / self._max_energy, 1.0)` — entra en la observación
como `agent_energy`. Es interocepción del propio estado: un organismo situado la
tiene. La salvedad es el recorte a 1.0, que destruye toda información por encima del
techo. Ver **D3**.
`energy_delta` **no** se observa: llega por `consequence` en `learn`. Es recuperable
por diferencia de energías **sólo mientras no haya recorte**. **HECHO DE CÓDIGO**

**16 · ¿Podría la doble escritura alterar el circuito?**
Sí, y es la trampa principal. Orden real del paso (`transition.py:349,354,387`):
`perceive → decide → learn`. `learn` deja `_energy` corrompida; `perceive` del paso
siguiente la pisa antes de que nadie lea. Hoy es inocuo **porque no hay lector**. En
cuanto FASE 1 añada un lector, qué valor lee depende de en qué fase lo lea.
**HECHO DE CÓDIGO** → ver **D1**.

**17 · ¿Qué cambia en la huella adaptativa?**
`adaptive_freeze.py:195` — `CANONICAL_ORDER = ("parameters", "episodic_buffer",
"longterm_M", "baseline")`. `energy_head` ya está dentro de `parameters`. Un borde que
sólo **module** con `f(drive)` sin parámetros propios **no amplía la frontera
adaptativa**. Si `f` tuviera parámetros aprendidos, sería un quinto componente y habría
que declararlo. **HECHO DE CÓDIGO**

---

## Los tres defectos

### D1 · Desajuste de unidades en `homeostasis`

`learn` suma energía **absoluta** a una variable **normalizada**.

| | escribe | unidad | ejemplo real |
|---|---|---|---|
| `a4:358` `perceive` | `observation.agent_energy` | normalizada [0,1] | `0.4975` |
| `a4:583` `learn` | `update(energy_delta)` | absoluta | `+9.85` / `−0.15` |

Con `max_energy = 60`, el coste de paso correcto en unidades normalizadas sería
`0.15/60 = 0.0025`. `learn` resta `0.15`: **60× de más**. Una sola comida
(`+9.85`) satura a `1.0`.

Medido (semilla 4242, mundo rico):

```
paso   dE (abs)   _E tras learn     lo que perceive repone
   0      -0.15        0.3500        0.4975   (learn resta 60x)
   2      +9.85        1.0000        0.5242   (learn satura)
```

**HECHO MEDIDO.** Enmascarado hoy por el orden de fases y por la ausencia de lector.

### D2 · La energía del agente no tiene techo

`max_energy` aparece en `terrario/world/` **sólo** como divisor en `state.py:110` y en
la serialización. **Nunca acota `agent.energy`.** El nombre promete un límite que la
física no impone.

Medido, mundo rico, 300 pasos: energía cruda **máx 1725.60** con `max_energy = 60`.
**28.8× el techo.** **HECHO MEDIDO**

### D3 · El sensor satura y borra la variable esencial

`state.py:110` recorta a `1.0`. Combinado con D2, el organismo percibe `agent_energy
= 1.0` en la gran mayoría de los pasos y **no puede distinguir 60 de 1725**.

| | mundo rico | mundo anillo |
|---|---|---|
| energía cruda (mín – máx) | 29.70 – **1725.60** | 4.05 – 223.85 |
| pasos con el sensor saturado | **287/300 (96 %)** | 118/300 (39 %) |
| pasos con `drive > 0` | **2/300 (1 %)** | 177/300 (59 %) |
| `drive` máximo | 0.0050 | 0.4325 |
| varianza de `drive` | **0.000000** | 0.020395 |

**HECHO MEDIDO** (semilla 4242, 300 pasos, `threshold = 0.5`, leído en
`observation_t.agent_energy`, que es exactamente lo que `perceive` escribe en
`a4:358` y lo único que `decide` puede leer).

### D4 · La consecuencia que ya estaba ocurriendo

Homeostasis **sí** tiene un consumidor causal, y no es `drive`:
`a4_advanced.py:427` — `temperature = (1.0 + self.homeostasis.exploration_bias)
if self._use_homeostasis else 1.0`, con `exploration_bias = 1.0 − _energy`
(`homeostasis.py:48`).

Bajo saturación, `_energy = 1.0` ⟹ `exploration_bias = 0.0` ⟹ `temperature = 1.0`,
que es **literalmente el valor de la rama `use_homeostasis = False`**.

| | mundo rico | mundo anillo |
|---|---|---|
| `temperature` exactamente `1.0` | **286/300 (95 %)** | 117/300 (39 %) |
| varianza de `temperature` | 0.004936 | 0.129864 |

Es decir: en el mundo donde el organismo aprende, **el flag `use_homeostasis`
es conductualmente inerte en el 95 % de los pasos**. La ablación y el brazo completo
son el mismo organismo casi siempre. Esto no es una predicción sobre el borde nuevo:
es algo que ya venía pasando, sin que nadie lo midiera.

**HECHO MEDIDO**

### D5 · El valorador es interoceptivamente ciego

`a4_advanced.py:322` — `s_t = concat(e_t, h_t, memory_context, lt_context)`.
`observation.agent_energy` aparece en A4 en **exactamente dos sitios**:
`a4:358` (se escribe en `homeostasis._energy`) y `a4:364` (dentro de un dict de
traza). **Nunca entra en ningún tensor.**

Por tanto `energy_head(s_t, a)` **no puede** expresar «consumir paga menos cuando
estoy lleno»: `s_t` no lleva cuán lleno está. Tampoco puede la política. La única
vía por la que la energía propia llega hoy a la conducta es el escalar
`temperature` de `a4:427`.

Dos consecuencias, y la segunda es mía:

1. Un valorador ciego a la interocepción **no es la valoración de un regulador**.
   Un regulador valora acciones *condicionado a la desviación*; `E[Δe|a]` sobre un
   `s_t` sin estado interno es un modelo del mundo, no una fisiología.
2. **La saciedad que acabo de meter en la física produce un objetivo que este
   valorador no puede ajustar.** El mismo par `(s_t, CONSUME)` devolverá `+10` unas
   veces y `0` otras, según una variable que `s_t` no contiene. El modelo aprenderá
   la media. Es decir: reparar D2/D3 sin tocar D5 crea un objetivo inaprendible.

**HECHO DE CÓDIGO**

### D6 · Hay dos umbrales homeostáticos y nunca se han hablado

| | dónde | unidad | valor | quién lo usa |
|---|---|---|---|---|
| del **científico** | `world_generator.py:84` `Economy.low_energy` | absoluta | `14.0` | `:558` y `:640`, para puntuar si una elección se tomó con hambre |
| del **organismo** | `a4_advanced.py:94` `homeostasis_threshold` | normalizada | `0.5` | `homeostasis.py:39` `drive`, `a4:427` `temperature` |

El generador calibró el suyo con razón escrita: «la energía inicial queda a una
pérdida de él, para que una vida cruce el umbral en los dos sentidos». El del
organismo es un `0.5` sin justificación declarada.

Con `max_energy = 60` el umbral del organismo caía en **30 absolutos** frente a los
**14** que el mundo declara como escasez. Reparado D2, el techo de los mundos
generados pasa a `initial + n_estaciones × gain` = **84** con 8 estaciones, y el umbral
del organismo se va a **42**. Es decir: **mi reparación alejó los dos umbrales, de
30-frente-a-14 a 42-frente-a-14.**

El mundo puntúa «decidió con hambre» por debajo de 14. El organismo *siente* hambre por
debajo de 42. Nunca han coincidido, y la calibración cuidadosa del generador es
invisible para el ser.

La salida no arbitraria existe y es una línea: `homeostasis_threshold = low_energy /
max_energy`, con lo que el umbral deja de ser un número mágico y pasa a ser **el punto
que el mundo declara como escasez**. Pero eso es fijar qué es una necesidad para este
organismo, y es de las dos decisiones que no tomo solo.

**HECHO DE CÓDIGO** + **HECHO MEDIDO** (el desplazamiento 30 → 42).

---

## Qué significa para el mandato

La lectura anterior era «A4 tiene 5 de 6 piezas de un circuito homeostático; falta el
borde». **Estaba incompleta en las dos direcciones.** Por un lado homeostasis sí tenía
un consumidor causal —la temperatura, D4— que yo había dado por inerte. Por otro, Falta también la sexta: en el mundo donde el organismo
aprende **no hay desviación que regular**. El `drive` no es una señal ignorada: es una
señal constante a cero.

Por Ashby, esto no es un detalle de calibración. Una variable esencial que no puede ser
desplazada no define región de viabilidad, y sin desplazamiento no hay perturbación que
absorber ni variedad requerida que igualar. Construir el regulador primero sería
construir un controlador para una planta que no se mueve.

Y hay un corolario incómodo para lo ya medido: **DISCOVERY-32 y la campaña
confirmatoria corrieron en el mundo rico**, donde `drive ≡ 0`. Nada de lo que midieron
depende de homeostasis —no la usaban— pero tampoco pueden servir de precedente de que
el organismo regule nada.

---

## La decisión CASO A / B / C

**CASO B**, con matiz favorable.

- **No es CASO A**: el agente no tiene un selector one-step; el único camino del
  `world_model` a la acción, hoy, pasa por el planner multistep.
- **No es CASO C**: el predictor existe (`world_model` cabeza de energía, `a4:635`),
  está entrenado con el objetivo correcto, y **ya está probado que se puede evaluar
  exhaustivamente en las 25 acciones sin planner** (`diagnostic_probes.py:147-162`).

El trabajo es **extraer la interfaz de valoración one-step** que ya existe en el
laboratorio y darle un consumidor en el agente. Es la extracción más pequeña posible:
mover una función probada de `lab/` a un órgano.

**Pero D5 le pone una precondición propia.** Extraer el valorador tal cual daría un
regulador que no puede leer aquello que regula. Antes de mover nada, `s_t` tiene que
llevar interocepción — y ésa sí es una modificación del ser, no de su laboratorio.

La maquinaria para hacerlo con honestidad **ya existe y está validada**:
`observability.py:expand_encoder_input` amplía la entrada del encoder con un canal que
**nace con peso CERO**, de modo que la equivalencia al nacer no es una esperanza sino
una identidad aritmética; y `sham_mask` da el brazo de control que conserva la
distribución marginal y destruye la correspondencia. Los tres brazos —`ZERO`, `SHAM`,
`TRUE`— son exactamente los que separan «tener un canal más» de «tener la información».

Aplicado a la interocepción, el brazo `SHAM` no es una permutación espacial sino la
**energía propia barajada en el tiempo**: la misma marginal, la correspondencia con el
estado real destruida. Si `TRUE` supera a `SHAM`, la ventaja es de saber cómo estoy, no
de tener una entrada más.

---

## Precondición

FASE 1 no puede empezar por el borde. Tiene que empezar por devolverle varianza a la
variable esencial, y eso es física del mundo, no A4:

1. **D2** — acotar `agent.energy` a `max_energy` en el mundo, o declarar explícitamente
   que `max_energy` es sólo una escala de sensor y renombrarlo.
2. **D3** — que el rango del sensor cubra el rango que la física permite.
3. **D1** — una sola autoridad sobre `homeostasis._energy`, en una sola unidad.

Sin (1) y (2), los cuatro brazos del experimento son el mismo brazo.

**D4 es la prueba de que esto no es teórico.** El único acoplamiento homeostático que
A4 ya tenía lleva desapareciendo el 95 % de los pasos, en silencio, en todas las
corridas hechas hasta hoy.

**Quedan dos decisiones que no son mías**, y las dos son la misma clase de cosa: fijan
qué es una necesidad para este organismo.

- **D1** — cuál de las dos escrituras de `homeostasis._energy` sobrevive: ¿el estado
  interno es *lo que el sensor dice ahora* (`perceive`) o *lo que el organismo integra
  de sus consecuencias* (`learn`)?
- **D6** — si el umbral del organismo se deriva del que el mundo declara
  (`low_energy / max_energy`) o sigue siendo un `0.5` independiente.

Ninguna de las dos es un parche. Cualquiera de las dos que se decida mal deja el
experimento midiendo otra cosa.
