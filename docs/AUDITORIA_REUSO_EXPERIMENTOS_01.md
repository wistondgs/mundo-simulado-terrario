# Qué del sistema sirve ya para E0 y E1

**2026-09-18.** El criterio rector cambió: la unidad de progreso es «el organismo demostró una
capacidad nueva». Esta auditoría no propone nada: mide qué hay construido que sirva para
`EXP-MOTOR-GROUNDING-01` y `EXP-HUNGER-INTEROCEPTION-01` **sin construir motor nuevo**.

---

## 1 · Sirve tal cual

| Pieza | Para qué | Dónde |
|---|---|---|
| **Motor completo** — física, reglas, calendario | correr cualquier escenario, no sólo mundos generados | `build_episode_components` + `run_step` |
| **La máscara codifica las paredes** | E0: percibir proximidad al límite. Medido: máscara 9/25 en la esquina, 25/25 en el centro | `get_observation` |
| **`agent_start.energy` es parámetro de escenario** | E1: dos cuerpos, mismo mundo, distinta energía | escenario |
| **Tres brazos N / LEGACY / FULL** | el control causal de **todos** los experimentos: mismo organismo con y sin poder adaptar | `adaptive_freeze.py`, certificado hoy |
| **Huella adaptativa por componente** | D2 y D3 de tu definición de descubrimiento: cambio interno y persistencia | `adaptive_components`, `adaptive_fingerprint` |
| **Gemelos con stream grabado** | estadística pareada: misma experiencia para los tres brazos | `force_action` + `replay` |
| **Cuatro medidas de viabilidad** | `pasos_vividos`, `sigue_vivo`, `energia_final`, `balance_energia` | `run_measures.py:399-412` |
| **Ocho instrumentos registrados** | `examen_prediccion` sirve a E0; `contabilidad_energetica` a E1 | `instrument_registry` |
| **`homeostasis.drive`** | ya calcula `max(0, setpoint − energía)`, que es tu `d_t` | `homeostasis.py:39` |
| **`_policy_reward`** | la costura de B2, inerte y esperando | `a4_advanced.py:569` |
| **`last_prediction_error`** | la señal de E0 y de B5, ya calculada | `a4_advanced.py:607` |

**Lo que OCF-G3 compra aquí, y es mucho:** tu `ReachRate_learned > ReachRate_frozen` de E0 y tu
control de E3 con tres organismos idénticos **ya tienen el brazo congelado**, certificado y con
evidencia de 240 intentos / 0 commits. Sin eso, «el organismo aprendió» no era falsable.

## 2 · Sirve con una costura pequeña, sin tocar el motor

**El cuerpo permutado de E0.** `DIRECTION_DELTA` es una constante global que la física lee
directamente, así que el mapeo motor→desplazamiento **no** es por mundo. Pero `Physics` es una
clase normal y viaja **inyectada** en `EpisodeComponents.physics`. Una subclase que sobreescriba
`_handle_move` con una permutación derivada de la semilla entra por ahí. No hay cambio de motor:
hay una clase nueva y un campo que ya existe.

## 3 · NO sirve, y hay que decirlo

### 3.1 · El 7×7 vacío de E0 no funciona. Medido.

En un mundo vacío el organismo sólo distingue dónde está por la máscara. Contando vistas distintas
por celda:

```
  rejilla   radio   vistas distintas   celdas   ¿cada celda única?
  5x5       2                     25       25   SÍ
  5x5       3                     25       25   SÍ
  6x6       2                     25       36   no
  6x6       3                     36       36   SÍ
  7x7       2                     25       49   no      <-- lo que E0 pedía
  7x7       3                     49       49   SÍ
  9x9       2                     25       81   no
```

Con 7×7 y radio 2, **(3,3) y (3,4) producen la misma observación**: en el interior el organismo no
puede percibir que se movió, y `P(s_{t+1}|s_t,a_t)` es inaprendible ahí por construcción.

**Las dos geometrías que sí funcionan son 5×5 radio 2 y 7×7 radio 3**, y las dos son parámetros de
escenario. Nada que construir.

### 3.2 · En E1, la energía no llega a la política

Éste es el hallazgo que más cambia el diseño de E1. El propio código lo dice:

> *«Modulate temperature by homeostatic exploration bias. This is the **only site where the
> organism's viability pressure reaches behaviour**: `drive` is computed and reported but consumed
> nowhere.»* — [a4_advanced.py:420](terrario/agent/agents/a4_advanced.py:420)

Y la cadena lo confirma:

```
perceive   encoder.encode_observation(observation.channels)     <- SÓLO canales
_build_state   s_t = concat(e_t, h_t, memory_context, lt_context)   <- sin término interoceptivo
decide     logits = policy_head(s_t);  temperatura = 1 + (1 − energía)
```

`agent_energy` **está** en la observación, pero no entra en `_last_latent`, ni en `s_t`, ni en
`policy_head`. Llega a la conducta por un único camino: la **temperatura del softmax**.

Consecuencia para E1, exacta: hoy se puede demostrar
`π(a | o, E_baja) ≠ π(a | o, E_alta)` — pero la diferencia sería **sólo de aleatoriedad**, no de
preferencia. El organismo hambriento actúa más al azar; no actúa más hacia la comida. Eso no es lo
que E1 quiere demostrar.

Y hay una consecuencia de segundo orden para B2: aunque `_policy_reward` sume la recompensa
interoceptiva, **la política no puede condicionar sobre la energía si la energía no está en el
estado**. Aprendería una política promediada sobre estados de hambre, no una política que dependa
del hambre. **B2 sin energía en el estado es media capacidad.**

### 3.3 · El generador de mundos no es la herramienta para E0/E1

`world_generator` produce un sustrato único: cue → demora → elección, con estaciones y puertas.
E0 y E1 no son eso. Lo correcto es un escenario escrito a mano pasado a `build_episode_components`
—que es lo que el motor acepta— y **no** forzar el generador a un mundo que no es suyo. Los
oráculos amputables tampoco se reutilizan: están atados a la geometría de estación. Lo que sí se
reutiliza es **el patrón**: techo con facultad completa, azar con facultad amputada, control con el
eje apagado.

---

## 4 · El estado real del organismo, que condiciona todo

Medido hoy, mundo LEARN-A1, primera puerta en la columna 2, 68 pasos:

```
A4        CONSUME con efecto = 0    PUSH/LEFT 19 · INSPECT/DOWN 11 · MOVE/UP 9 · PUSH/UP 9
oráculo   CONSUME con efecto = 8    MOVE/RIGHT 60 · CONSUME 8
```

El organismo no ejecuta nunca la acción sobre la que está construida la economía del mundo. **E0 es
exactamente el experimento que ataca eso**, y por eso el orden que propusiste es el correcto: sin
control sensorimotor, cualquier capacidad posterior se mide sobre una conducta que no toca el mundo.

---

## 5 · Lo que hay que decidir antes de E1, y no lo decide el código

La energía no está en el estado. Hay tres salidas y no son equivalentes:

1. **Meter la energía en `s_t`.** Es un cambio de arquitectura de A4 —el vector de estado cambia de
   dimensión, y con él todo parámetro y toda huella histórica.
2. **Dejarla fuera y aceptar que E1 mide modulación de exploración.** Honesto, pero no demuestra lo
   que E1 quiere.
3. **Un canal del mundo que refleje el estado corporal**, de modo que la energía entre por la vía
   perceptiva normal sin cambiar `s_t`. Es interocepción como percepción, que es literalmente el
   contrato `x_body → interocepción → x̂_internal` que O1 tenía que fijar — y encaja con que la
   percepción interna no tenga por qué ser perfecta.

La tercera es la que menos rompe y la que más se parece a lo que ya decidiste. Pero es una decisión
de arquitectura del ser, no una reparación, y por eso no la tomo.
