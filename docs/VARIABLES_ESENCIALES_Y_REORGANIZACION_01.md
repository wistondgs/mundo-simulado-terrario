# VARIABLES-ESENCIALES-Y-REORGANIZACION-01

**Estatus:** hallazgo de código, no normativo.
**Fecha:** 2026-09-16.
**Encargo:** «establecer en el código qué constituye las variables esenciales, qué determina la
viabilidad y qué causa realmente la reorganización» — prioridad experimental de la ficha de
objetivo actualizado.
**Método:** lectura directa del runtime. Cada afirmación lleva archivo y línea. No se modificó
nada.

---

## Respuesta corta

| Pregunta | Respuesta en el código |
|---|---|
| ¿Qué constituye `E`? | un escalar, `energy`, más un booleano derivado, `alive` |
| ¿Qué determina la viabilidad? | **tres fronteras distintas, de tres dueños distintos, sin reconciliar** |
| ¿Qué causa la reorganización? | `energy_delta` usado como **recompensa**, en las cuatro arquitecturas con plasticidad |

Y de ahí sale el hallazgo que importa:

> **La variable esencial y la señal de recompensa son el mismo número.** El gate 1 no puede
> decidirse retirando la recompensa externa, porque no hay ninguna que retirar: `do(reward = 0)`
> es literalmente `do(energy_delta = 0)`, que es suprimir la variable esencial.

---

## 1. Qué constituye las variables esenciales

```python
class AgentState:
    agent_id: int
    pos: Position
    energy: float
    alive: bool = True
```
`core/types.py:84-88`

Eso es todo. `Eₜ` tiene **una** componente escalar. No hay cuerpo, sensores, actuadores,
recursos, desgaste ni integridad estructural como variables esenciales: existen como
configuración del escenario, no como magnitudes que puedan salir de rango.

Consecuencia para la ficha de objetivo: cuando se pide que «cambien las variables esenciales y
las condiciones bajo las cuales se puede mantener la viabilidad», hoy sólo puede cambiar el
umbral de una única variable. **No se puede cambiar cuál variable es crítica, porque sólo hay
una.**

---

## 2. Qué determina la viabilidad

Tres fronteras, tres dueños, tres números que nadie ha reconciliado:

| Frontera | Valor | Dónde | Dueño |
|---|---|---|---|
| muerte | `energy <= 0.0` | `world/state.py:170-171` y `world/rules.py:226-227` | el mundo |
| umbral homeostático | `threshold = 0.5` sobre energía normalizada | `agent/homeostasis.py:20` | el organismo |
| η del instrumento | `viable_floor × max_energy`, calibrado en ≈ 0.23 | `viability_recovery_metric.py:161` | el observador |

Las tres responden a la pregunta «¿está viable?» y dan tres respuestas distintas para la misma
trayectoria. Un organismo con energía 30/100 está: **vivo** para el mundo, **bajo presión** para
sí mismo, y **dentro de η** para el instrumento.

Dos detalles que conviene no descubrir más tarde:

- La muerte por decaimiento vive dentro de `apply_step_energy_cost`, que **retorna antes si
  `step_energy_cost == 0.0`** (`world/state.py:166-167`). En un escenario sin coste energético el
  organismo no puede morir por decaimiento. `d4_change.yaml`, que es lo que resuelve `D4`, no
  declara dinámica de energía.
- η se calibró sobre `AGENTS = ("A1", "A2", "A3")` (`scripts/calibrate_viability_eta.py:38`), y
  **A4 es la única arquitectura con lazo homeostático**. La frontera de viabilidad del observador
  se fijó sin el único organismo que posee una señal interna de viabilidad.

---

## 3. Qué causa realmente la reorganización

### 3.1 Quién tiene plasticidad

| Agente | Plasticidad | Homeostasis |
|---|---|---|
| A0 | ninguna — `learn()` es no-op | no |
| A1 | `Adam`, REINFORCE | no |
| A2 | `Adam`, REINFORCE | no |
| A3 | `Adam`, modelo de mundo + REINFORCE | no |
| A4 | `OnlineLearner` | **sí** |

### 3.2 Qué señal la dispara

En A1 y A3 el código lo dice con todas las letras:

```python
# REINFORCE: -log_prob * reward
reward = consequence.energy_delta
loss = -self._last_log_prob * reward
```
`agent/agents/a1_reactive.py:85-87`, y equivalente en `a3_worldmodel.py:140-142`

En A4, la misma magnitud con línea base:

```python
advantage = consequence.energy_delta - self._energy_baseline
policy_loss = -fresh_log_prob * advantage
```
`agent/agents/a4_advanced.py:417-423`

Y el optimizador sólo acepta esas dos entradas:

```python
def step(self, world_model_loss=None, policy_loss=None, total_loss=None)
```
`agent/learner.py:48-52`

**No hay ningún argumento de viabilidad.** El cambio de parámetros se dispara por error
predictivo (modelo de mundo) y por `energy_delta` como recompensa (política). La condición «`E`
está saliendo de `𝒱`» no entra en la plasticidad por ninguna vía.

### 3.3 Los dos caminos de la energía

```
energy_delta ──► homeostasis.update ──► exploration_bias ──► temperatura softmax
                                                             a4_advanced.py:268
             └─► reward / advantage ───► backward() ────────► parámetros
                                                             a1:87 · a3:142 · a4:423
```

El primero es **regulación con repertorio existente** — fenómeno 1 de la ficha. Sólo A4, y sólo
sobre la temperatura de muestreo.

El segundo cambia parámetros, pero su disparador es la magnitud del delta, no la insuficiencia de
la organización. Por la definición de la ficha —«modificar el propio regulador **cuando su
organización existente resulta insuficiente** para conservar la viabilidad»— **no califica como
reorganización endógena**.

`drive` merece mención aparte: se calcula (`homeostasis.py:34-39`), se reporta en el estado
científico (`a4_advanced.py:320`) y **no se consume en ninguna parte**. Es telemetría, no control
— la misma familia que N1.

---

## 4. Los cuatro fenómenos contra el código

| Fenómeno | Estado |
|---|---|
| Regulación | **presente**, estrecho: un lazo, una variable, un parámetro (temperatura), sólo A4 |
| Reorganización endógena | **ausente como tal**: hay cambio de parámetros, disparado por recompensa y no por insuficiencia |
| Desarrollo de capacidad | **ausente**: ningún mecanismo añade distinciones, representaciones o estrategias inexistentes |
| Mejora del proceso de adquisición | **ausente**: `lr`, `grad_clip` y `update_frequency` son constantes de constructor (`learner.py:27-29`) |

---

## 5. El confundido, que es el resultado principal

La ficha pide, en §4, mantener «el ensayo sin recompensa externa y los clamps que separan
viabilidad de sorpresa predictiva». El primer clamp **no se puede aplicar aquí**, y no por falta
de implementación:

```
variable esencial  = agent.energy
señal de refuerzo  = consequence.energy_delta
```

Son la misma magnitud, una en nivel y otra en diferencia. Retirar la recompensa externa deja el
diseño intacto porque la recompensa nunca fue externa: **es la variable esencial derivada en el
tiempo.** Cualquier resultado sobre «la viabilidad tiene autoridad causal sobre la
reorganización» quedaría confundido con «la recompensa tiene autoridad causal sobre la política»,
que es la hipótesis nula.

Separarlas exige una de dos cosas, y **ambas son mecanismos nuevos**, prohibidos por la moratoria
mientras `scientific_results == 0`:

1. una segunda variable esencial que no se use como refuerzo; o
2. un disparador de plasticidad anclado en la frontera de viabilidad y no en el delta.

Por eso este documento nombra el confundido y no lo repara. Nombrarlo antes de preregistrar es
justamente lo que evita que el gate 1 produzca un resultado no interpretable.

---

## 6. Qué queda establecido

1. `E` es un escalar. La ficha habla de variedad endógena sobre cuerpo, sensores y recursos: nada
   de eso es hoy variable esencial.
2. La viabilidad tiene tres definiciones simultáneas y discrepantes. Antes de cualquier
   afirmación sobre `𝒱ₜ` hay que decidir **cuál de las tres es `𝒱`** — y esa es una decisión
   humana, no una constante que el código deba adivinar.
3. La reorganización, hoy, la causa la recompensa. La viabilidad no tiene autoridad causal sobre
   ella por ninguna ruta, y el experimento que lo comprobaría está confundido de origen mientras
   `E` y el refuerzo sean el mismo número.

Ninguna de las tres conclusiones exige construir nada para sostenerse. Las tres son verificables
releyendo los archivos citados.
