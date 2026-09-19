# ARQUITECTURA DEL ORGANISMO TERRARIO vNEXT
## De predictor adaptativo a ser que adquiere capacidades

**2026-09-18.** Etiquetas: **[MED]** medido en esta sesión · **[CORPUS]** con locator ·
**[EXT]** literatura externa · **[INF]** inferencia · **[HIP]** hipótesis.

---

# 0 · La tesis, y por qué contradice el orden de cuellos de botella propuesto

El encargo ordena los cuellos así:
`percepción → representación → aprendizaje → planificación → acción → adaptación`,
y trata la planificación como el sospechoso principal.

**[MED] Los datos dicen que el cuello vinculante está antes, y que es casi gratis.**

```
observation.channels        2 usos   →  encoder  →  s_t     ← el ÚNICO que decide
observation.mask            0 usos
observation.time_fraction   0 usos
observation.agent_energy    2 usos   →  temperatura del softmax

vistas distintas que A4 puede producir en un mundo 5×5 VACÍO:   1  de 25 celdas
las mismas, si leyera la máscara:                              25  de 25
```

**[INF] En un mundo sin objetos, A4 no puede percibir que se movió.** Y entonces
`P(s_{t+1}|s_t,a_t)` no es un modelo difícil de aprender: es una **función constante**. El world
model puede estar perfecto y transportar cero información. Cualquier discusión sobre el planner
ocurre aguas abajo de eso.

**[INF] La máscara ya se calcula y se tira.** El coste de arreglarlo es concatenar un plano al
encoder. Es la intervención más barata del documento y la que tiene la predicción más grande.

Reordeno los cuellos según lo medido:

| # | Cuello | Evidencia | Coste de atacarlo |
|---|---|---|---|
| **1** | **El organismo descarta 3 de 4 campos sellados de su observación** | [MED] 0 usos de `mask` y `time_fraction`; 1 vista por 25 celdas | trivial |
| **2** | **El planner busca en el espacio motor, no en el de affordances** | [MED] 10 secuencias de 25⁵ = 9.7M; cobertura 1.0×10⁻⁶ | medio |
| **3** | **El estado corporal no entra en la decisión, sólo en la temperatura** | [MED] `s_t = concat(latente, hidden, mem, ltm)`; docstring del propio código | medio, toca `s_t` |
| **4** | **La valoración del planner es `energía − 10·done` y nada más** | [MED] `policy.py:151` | medio |
| **5** | **`s_t` alimenta 7 módulos: totalmente unido** | [MED] 7 consumidores de `state_dim` | alto |
| 6 | El puente conocimiento→conducta | pendiente de la campaña | desconocido |

**[INF] El 6 —el que más nos preocupaba— puede ser consecuencia del 1 y el 2**, y no una
patología propia. Atacar el 6 sin resolver 1 y 2 sería tratar un síntoma.

---

# A · Diagnóstico funcional de A4

**Puede hoy**: percibir canales de objetos en una ventana 5×5; integrar temporalmente; escribir y
leer dos memorias; predecir `(s', energía, done)` desde `(s, a)` con target real y detached;
estimar varianza de ensemble; muestrear 10 rollouts; emitir una acción de 25; actualizar por
gradiente en línea; modular su temperatura por energía.

**No puede hoy**: percibir su posición sin objetos alrededor; saber cuánto tiempo lleva vivo;
condicionar su **preferencia** —no su aleatoriedad— por su estado corporal; saber qué acciones son
posibles aquí; razonar sobre nada que no sea una acción primitiva; distinguir «el mundo es
estocástico» de «mi modelo es malo»; representar qué sabe hacer.

**[MED] Y hay un hecho que reencuadra todo**: el planner **es** la conducta alimentaria —con
`use_planner=False`, cero CONSUME en 201 pasos y muerte; con él, 210 consumos efectivos. No es un
refinamiento sobre una política: es el único mecanismo que produce alimentación.

---

# B · Qué debería representar el organismo

**[INF] La crítica a la lista propuesta**: mezcla niveles. `WORLD MODEL` y `AFFORDANCE MODEL` son
modelos; `EXPLORATION` y `META-CONTROL` son políticas sobre modelos; `MEMORY` es un sustrato. Una
arquitectura donde todo es «un subsistema» reproduce el problema que ya tenemos — once módulos
colgando de un estado único.

**[HIP] Propongo tres capas por lo que hacen con el tiempo, no por lo que nombran:**

```
SUSTRATO      lo que persiste           cuerpo · memorias · parámetros
MODELOS       lo que predice            mundo · sí mismo · affordances
CONTROL       lo que decide             reactivo · deliberativo · meta
```

Y **cuatro representaciones que hoy no existen**, cada una con su justificación medida:

1. **Estado corporal como parte del estado decisional.** [MED] Hoy sólo temperatura. Sin esto,
   B2 es media capacidad: una política que no ve el hambre aprende una política promediada sobre
   estados de hambre.
2. **Observabilidad como dato.** La máscara dice **qué no se ve**. Un organismo que no representa
   los límites de su percepción no puede distinguir «no hay comida» de «no veo comida» — y ésa es
   la distinción que separa exploración de resignación.
3. **Affordances**: qué acciones tienen sentido aquí. [EXT] Gibson (1979): el organismo percibe
   posibilidades de acción, no propiedades objetivas. **[INF] No es filosofía: es una reducción del
   espacio de búsqueda de 25⁵ a algo enumerable.**
4. **Self-model**: `P(consecuencia | estado_corporal, mundo, acción)`, distinto de
   `P(mundo' | mundo, acción)`. [MED] A4 tiene el segundo y no el primero. Sin el primero no puede
   saber que la misma comida vale distinto según su energía — que es la prueba mínima de motivación.

---

# C · Tres diseños

## Diseño A · mínima evolución  ·  «que perciba lo que ya se le entrega»

- **Representación**: el encoder recibe `channels ⊕ mask`; `s_t` gana dos escalares,
  `energía_normalizada` y `time_fraction`.
- **Control**: sin cambios.
- **Coste**: un plano de entrada al encoder y dos dimensiones en `s_t`. Toca 7 módulos por forma,
  cero por lógica.
- **Firma conductual esperada**: discriminación posicional donde hoy hay una sola vista; y
  `π(a|o, E_baja) ≠ π(a|o, E_alta)` en **preferencia**, no sólo en varianza.
- **Modo de fallo**: si la energía entra en `s_t`, `next_state_head` pasa a predecir **también la
  energía futura**. Eso es una capacidad nueva entrando por la puerta de atrás y hay que declararla.
- **[INF] Es el diseño que recomendaría probar primero, y no por conservadurismo**: es el único
  cuyo cuello está medido y cuyo coste es casi nulo.

## Diseño B · intermedia  ·  «que busque en el espacio correcto»

Todo lo de A, más:

- **Affordance model**: una cabeza que, desde la observación, puntúa qué acciones son **aplicables**
  aquí. El planner muestrea **condicionado** por ella en vez de uniformemente.
- **Valoración del planner**: `energía predicha` pasa a `reducción de desviación homeostática
  predicha` — el término B2, pero dentro del planner en vez de dentro de la pérdida de política.
- **Coste**: una cabeza pequeña; el planner igual de barato porque el muestreo se concentra.
- **Firma**: la cobertura efectiva del planner sube órdenes de magnitud sin subir el número de
  rollouts. **Predicción falsable**: con 10 rollouts condicionados debería igualarse o superarse el
  rendimiento de 100 rollouts uniformes.
- **Modo de fallo**: si la affordance se aprende del mismo gradiente, puede colapsar a «siempre
  CONSUME» y reducir la exploración a cero.

## Diseño C · rediseño fuerte  ·  «que tenga repertorio»

Todo lo de B, más:

- **Biblioteca de skills**: el planner deja de razonar sobre acciones primitivas y razona sobre
  unidades reutilizables — `APPROACH(x)`, `CONSUME(x)`, `WITHDRAW`. El horizonte 5 pasa a valer
  mucho más porque cada paso es una secuencia.
- **Estado modular**: `s_t` se parte en subespacios y cada modelo lee el suyo. [CORPUS] Ashby
  S.11/10: *«for the accumulation of adaptations to be possible the system must not be fully
  joined»*. Nuestro `s_t` alimenta siete módulos.
- **Tres lazos separados**: reactivo (sin planner, para cuando el affordance es inequívoco),
  deliberativo (planner), y meta (cuándo usar cuál).
- **Coste**: alto. Es otro organismo.
- **Modo de fallo**: los skills se descubren de una distribución de experiencia que el organismo
  aún no sabe generar. **[INF] Riesgo real de que C sea prematuro: un repertorio aprendido de una
  conducta que todavía es azar sería un repertorio de azar.**

---

# D · Frontera provisto / aprendido / descubierto

**[HIP]** La pregunta «qué ponemos y qué adquiere» tiene una respuesta operativa: **poner la
estructura, nunca el contenido.**

| Provisto (innato) | Aprendido | Descubierto | Meta-aprendido |
|---|---|---|---|
| que existe un estado corporal | **qué** lo mueve | que hay contingencias contextuales | cuándo ser plástico |
| que hay affordances | **cuáles** aquí | regularidades no suministradas | qué buscar |
| que hay un modelo del mundo | sus parámetros | — | cuándo el modelo no sirve |
| que hay memoria | su contenido | qué merece recordarse | — |
| el criterio de viabilidad | dónde están los límites | — | — |

**[INF] La línea que propongo**: si el organismo tuviera que inventar la homeostasis, estaríamos
reinventando informática, no creando inteligencia. Si le damos el mapeo cue→puerta, no descubre
nada. **La estructura es andamio; el contenido es la evidencia.**

---

# E · La ontología: cuatro unidades, no una

**[INF] La crítica a «capacidad» es correcta y la respuesta no es sustituirla: es admitir que son
cuatro objetos distintos y medibles por separado.**

| Unidad | Qué afirma | Cómo se mide con lo que YA tenemos |
|---|---|---|
| **Capacidad** | «puede ejecutar X» | probe congelado, contraste pareado |
| **Región de competencia** | «mantiene desempeño bajo este conjunto de condiciones» | familia de mundos por configuración + frontera |
| **Envolvente de regulación** | «absorbe estas perturbaciones» | **no medible hoy**: no hay operador de perturbación |
| **Repertorio** | «tiene estas transformaciones reutilizables» | **no medible hoy**: no hay skills |

[CORPUS] Ashby define supervivencia como región, no como acierto (S.3/15). **[INF] Las dos primeras
son medibles hoy; las dos últimas requieren construir el organismo que las tendría. Eso ordena el
trabajo por sí solo.**

---

# F · El experimento mínimo que falsa mi propuesta antes de comprometernos

**La afirmación fuerte de este documento es §0: el cuello vinculante es perceptivo, no de
planificación.** Se falsa con una sola intervención y el laboratorio que ya existe.

```
INTERVENCIÓN   el encoder recibe `channels ⊕ mask`. Nada más. Ni energía, ni time_fraction,
               ni affordances, ni skills.

GEMELOS        mismo nacimiento, un clon con máscara y otro sin. Intervención declarada,
               equivalencia de nacimiento verificada.

MEDIDA 1       vistas distinguibles en el mundo vacío        predicción: 1 → 25
MEDIDA 2       ganancia de discriminación en el banco        predicción: ΔG > 0
MEDIDA 3       probabilidad de entrar en régimen alto        predicción: sube
```

**Falsación**: si con la máscara la discriminación del banco **no** mejora y la entrada en régimen
alto **no** cambia, entonces la percepción no era el cuello y mi reordenamiento de §0 está mal —
y habría que volver al planner, que es donde el encargo lo situaba.

**[INF] Por qué este experimento y no otro**: es el único donde la predicción cuantitativa
—1 vista frente a 25— es una consecuencia aritmética de la geometría, no una esperanza. Si la
conducta no se mueve pese a que la percepción demostrablemente sí, habremos localizado el corte
entre percepción y conducta con una precisión que ningún otro experimento de este documento da.

**Coste**: un plano de entrada. Reutiliza gemelos contrafactuales, congelación, banco de sondas y
el endpoint de régimen que ya calculé sobre DISCOVERY-32.

---

# G · Qué NO construir todavía

- **Skills.** Un repertorio aprendido de una conducta dominada por azar es un repertorio de azar.
- **Meta-control.** No hay dos estrategias entre las que arbitrar.
- **Perturbación y ultraestabilidad.** El organismo aún no regula nada que perturbar.
- **Modularización de `s_t`.** Correcta a largo plazo, cara, y sin evidencia todavía de que el
  acoplamiento sea el cuello.
- **Cualquier cosa que dependa de `action_availability`.** [MED] Se declara y el runtime no la
  aplica.

---

# H · Riesgos de lo que propongo

1. **Meter energía en `s_t` cambia la forma de 7 módulos y hace que el world model prediga el
   cuerpo.** Puede ser deseable; es una capacidad nueva y hay que declararla, no dejarla entrar de
   lado.
2. **Un affordance model aprendido del mismo gradiente puede colapsar** y matar la exploración.
3. **[MED] El pareado contrafactual sólo quitó el 14% de la varianza** (correlación NORMAL~FULL de
   +0.140). Si la conducta está dominada por transiciones estocásticas de régimen, **ninguna mejora
   arquitectónica se verá en conteos** — se verá en probabilidad de entrar en régimen. Eso vale para
   evaluar cualquiera de los tres diseños.
4. **El riesgo mayor: que A, B y C sean todos correctos y ninguno suficiente**, porque el cuello
   real sea que el organismo nunca consigue la primera experiencia informativa por sí mismo. Eso no
   es arquitectura: es exploración, y lo mediría E2-C.

---

# I · Respuesta a la pregunta final

**¿Qué arquitectura construiría?** Un organismo de tres capas —sustrato, modelos, control— donde
lo que se provee es **estructura** y lo que se adquiere es **contenido**; con cuatro
representaciones que hoy faltan: cuerpo en el estado decisional, observabilidad como dato,
affordances como filtro previo a la búsqueda, y un self-model separado del world model. Sería
superior al A4 actual no por tener más piezas sino por **buscar en el espacio correcto**: A4
evalúa 10 de 9.7 millones de secuencias motoras cuando el espacio relevante tiene unidades
contables.

**¿Cuál es la modificación mínima que lo falsa?** Darle la máscara al encoder. Un plano. Si con
ella el organismo pasa de una vista a veinticinco y su conducta no cambia, mi tesis es falsa y el
cuello está donde el encargo decía.
