# E0 y E1 · las preguntas de arquitectura, contestadas contra el código

**2026-09-18 · READ-ONLY.** `repo /home/wis/mundo simulado terrario` · rama
`experiment/cognitive-live-observatory-01` · **HEAD `f72d225`** · árbol sin modificar (sólo
documentos nuevos sin seguimiento). No implementa, no toca A4, no crea mundos.

---

## STOP CONDITION · corrijo mi propia conclusión de la auditoría anterior

`AUDITORIA_REUSO_EXPERIMENTOS_01.md` dice que **5×5 radio 2 da 25 vistas para 25 celdas** y que por
tanto E0 es construible hoy. Eso es cierto **del contrato de observación** y **falso de A4**.

A4 consume **1 de los 4 campos sellados**:

```
observation.channels        2 usos   -> encoder -> latente -> s_t     ← el único que decide
observation.mask            0 usos   ← y la máscara era lo que distinguía las posiciones
observation.agent_energy    2 usos   -> homeostasis -> temperatura
observation.time_fraction   0 usos
```

Medido de nuevo, contando sólo lo que A4 lee:

```
  mundo                           canales solos   + máscara   celdas
  5x5 vacío                                   1          25       25
  7x7 vacío                                   1          49       49
  5x5 con 1 objeto en (0,0)                   9          24       24
  5x5 con 4 objetos en las esquinas          15          21       21
```

**En un mundo vacío A4 ve UNA sola observación esté donde esté.** El problema de E0 no era la
geometría: era que el campo que codifica las paredes lo descarta el agente. La salida barata no es
una rejilla mayor, son **objetos como referencias**.

---

## A · Cadena causal de E0

| Etapa | Fichero / símbolo | Dato | ¿Adaptativo? | Consumidor aguas abajo |
|---|---|---|---|---|
| decisión | `a4:397 decide` → `policy_head(s_t)` | logits, temperatura `1+(1−E)` | no | `Action.from_int` |
| acción → física | `transition.run_step` → `EpisodeComponents.physics` | `Action` | no | `Physics._handle_move` |
| desplazamiento | `physics.py:93` `DIRECTION_DELTA[direction]` | nueva posición | no | `world.move_agent` |
| observación t+1 | `state.py:121 get_observation` | `channels`, `mask`, `agent_energy`, `time_fraction` | no | `consequence.new_observation` |
| **target de aprendizaje** | `a4:640-652`, **dentro de `torch.no_grad()`** | `next_state_target = _build_state(encode(canales_t+1), h_t+1)` | no (detached) | `world_model.loss` |
| **pérdida** | `world_model.py:111` | `loss_state = MSE(next_state_pred, next_state_target)`, **dentro de `loss_total`** | sí | `learner.step` |
| entrada de la acción | `a4:656` `a_onehot` | one-hot de la acción ejecutada | — | backbone del WM |
| **escritura** | `learner.py:159 optimizer.step()` | parámetros | **sí** | — |
| lectura posterior | `policy.py:136` `next_state, energy_pred, done_pred = world_model(sim_state, …)`; `sim_state = next_state` | rollout de H pasos | no | `Planner.plan` |
| **efecto conductual** | `policy.py:151` `score = total_energy − 10·done_prob` | **sólo energía y done** | no | `best_action = actions[0]` |

### Lo que esto contesta

**La cadena de aprendizaje existe entera y es sana.** El world model predice `next_state` a partir
de `(s_t, a_t)`; el target es la observación **real** posterior, codificada; está **detached**
(`torch.no_grad()`), así que no hay colapso de representación; y `loss_state` entra en `loss_total`,
que va al optimizador. **A4 sí puede aprender «esta acción mueve mi cuerpo así».**

**El contrafactual motor sintético da distinto.** Dos `Physics` con desplazamientos distintos
producen `consequence.new_observation` distintos ⇒ `next_state_target` distintos ⇒ gradiente
distinto. El ejemplo que recibe el learner **no** es el mismo. (Con la salvedad del STOP de arriba:
en un mundo vacío los dos targets colapsan al mismo, porque A4 ve una sola observación.)

**Pero el retorno a la conducta está acotado a la energía.** El planner **sí** usa
`next_state_head` —`sim_state = next_state` propaga el rollout— pero puntúa
`total_energy − 10·done_prob`. En un mundo vacío sin reglas, `energy_delta` es
`−step_energy_cost` constante para toda acción: **el score es plano y un modelo motor perfecto no
cambia ni una decisión**.

**No existe representación de objetivo.** Búsqueda de `goal` / `destination` / posición objetivo en
`terrario/agent`, `terrario/world`, `terrario/core`: todos los aciertos son `target_pos` interno de
la física (la celda adyacente en una dirección). **`ReachRate` no puede ser el endpoint principal de
E0**: no hay dónde escribir la meta ni quién la leería.

**No hay instrumento motor.** De los ocho registrados, `examen_prediccion` mide ranking de energía
entre entidad favorable y desfavorable — no desplazamiento, no navegación, no eficiencia de camino,
no controlabilidad.

## B · Veredicto E0

```
E0_NEEDS_SMALL_ADAPTER        para un endpoint de PREDICCIÓN
E0_NEEDS_NEW_LEARNING_PATH    si se insiste en ReachRate
```

Lo pequeño: una subclase de `Physics` (el campo `physics` ya existe) y **objetos como referencias**
en el escenario (configuración). Con eso, el endpoint medible es
`MSE(next_state_pred, next_state_real)` bajando, y el contraste NORMAL contra FULL_ADAPTIVE_FREEZE
ya está certificado.

Lo que **no** es pequeño: que ese conocimiento motor cambie la conducta. Hoy sólo puede hacerlo a
través de energía predicha, así que exigiría un gradiente energético en el mundo —lo que convierte
E0 en E2— o una meta, que no existe.

---

## C · Inventario de ingresos a A4

| Ingreso | Dato | → policy | → planner | → world model | → learner | Reutilizable para E1 |
|---|---|---|---|---|---|---|
| `perceive(obs).channels` | `(C,H,W)` → encoder | **sí** | sí (vía `s_t`) | **sí** | sí | **la única vía con gradiente hoy** |
| `perceive(obs).mask` | ventana visible | no | no | no | no | declarado y **no leído** |
| `perceive(obs).agent_energy` | escalar `[0,1]` | **sólo temperatura** | no | no | no | existe, no decide |
| `perceive(obs).time_fraction` | escalar | no | no | no | no | declarado y **no leído** |
| `homeostasis.drive` | `max(0, θ−E)` | no | no | no | no | calculado, **sin consumidor conductual** |
| `homeostasis.exploration_bias` | `1−E` | **sí, temperatura** | no | no | no | aleatoriedad, no preferencia |
| `_hidden` recurrente | GRU | sí | sí | sí | sí | no lleva estado corporal |
| contexto episódico / LTM | `_build_state` | sí | sí | sí | sí | no lleva estado corporal |
| `learn(consequence)` | `energy_delta`, `new_observation`, `done` | — | — | target | **sí** | `_policy_reward` es la costura |

**`observation.agent_energy`, trazado entero:** lo genera `state.py:121` como `energy_norm`
—normalizado a `[0,1]` dividiendo por `max_energy`—, **después** de aplicar la física del paso. Lo
consumen: el trazado del controlador (`controller.py:233,277`), el oráculo guionizado
(`world_oracles.py:106`, que lo **desnormaliza** y decide con él) y `a4:358`, que lo copia a
`homeostasis._energy`. No se checkpointea aparte de la traza.

**`NO_GENERIC_SELF_STATE_INGRESS`.** Búsqueda por comportamiento de `self_state`, `interocep`,
`propriocep`, `body_channel`, `agent_channel` en todo `terrario/`: los únicos aciertos son
`observation_sources` (una tupla de **nombres** declarados, no un mecanismo) y `AGENT_FIELDS`, que
es el conjunto **sellado** de cuatro campos. No hay superficie genérica para representar propiedades
del propio agente distintas de `observation.channels`.

## D · Veredicto E1a

```
E1A_SMALL_AGENT_ADAPTER
```

La energía **ya llega al agente** (`observation.agent_energy`) y **ya está declarada** como fuente
de observación en `AGENT_FIELDS`. Lo que falta no es un canal del mundo ni un sensor: es que A4
concatene ese escalar a `s_t`. La superficie exacta es `_build_state`, que hoy compone
`concat(e_t, h_t, memory_context, lt_context)`.

**Efecto contrafactual, ingreso por ingreso** — importa porque no queremos repartir energía a toda
la arquitectura:

| Si la energía entra por… | encoder | temporal | memoria | WM | uncertainty | planner | policy | learner |
|---|---|---|---|---|---|---|---|---|
| **`_build_state` (concat a `s_t`)** | no | no | no | **sí** (s_t es su entrada) | **sí** | **sí** | **sí** | sí |
| `channels` como plano extra | **sí** | sí | **sí** (claves de memoria) | sí | sí | sí | sí | sí |
| sólo `policy_head` | no | no | no | no | no | no | sí | sí |

Entrar por `channels` contamina las **claves de memoria** —el recuerdo pasaría a indexarse por
hambre— que es precisamente el efecto colateral a evitar. Entrar por `_build_state` alcanza policy,
planner, WM e incertidumbre a la vez; es lo que E1 quiere y algo más. Entrar sólo por `policy_head`
es lo mínimo, y deja al world model sin poder predecir consecuencias dependientes del estado.

Ninguna de las tres es configuración: **las tres modifican A4**. Por eso no elijo.

## E · Veredicto E1b

```
E1B_MISSING_ESTIMATION_PRIMITIVE
```

No hay modelos de sensor, ruido de canal, observación parcial del propio estado ni estimador
aprendido. La observación se construye completa y exacta en `state.py` y se sella en `AGENT_FIELDS`.

## F · Dependencia de O1

```
E1A_VALID_ONLY_AS_PERFECT_INTEROCEPTION
```

E1a **no está bloqueado** por O1: se puede demostrar hoy «misma observación externa + distinto
estado corporal → distinta preferencia aprendida» sin separar `x_body` de `x̂_internal`, porque
`observation.agent_energy` es una copia exacta del estado corporal.

Pero la afirmación que quedaría probada es exactamente ésa y no más: **interocepción perfecta**. Y
hay un detalle que conviene saber antes: el doble escritor de `homeostasis._energy` que OCF-G1
midió es inocuo aquí sólo porque los dos escritores acaban escribiendo el mismo valor. En cuanto
`x̂_internal` deje de ser una copia, esa disputa deja de ser inocua. **E1b exige O1; E1a no.**

## G · E2 / E5 / E8 / E9

| Exp | Clasificación | Infraestructura existente | Hueco exacto | ¿Dónde está el hueco? |
|---|---|---|---|---|
| **E2 búsqueda** | EXISTS_WITH_CONFIG | `d4_adaptation_*` (1 objeto en 14×14); `OpportunityLifecycle` para reaparición; el planner ya puntúa energía a H pasos | ninguno estructural. El planner **ya** optimiza energía futura, que es lo que E2 pide | — |
| **E5 curiosidad** | EXISTS_WITH_COMPOSITION | eje `novelty` con consecuencia irreducible; `last_prediction_error`; `uncertainty_estimator` de ensemble | endpoint de **ganancia de información** y su **caída** tras aprender; ninguno de los 8 instrumentos lo mide | **instrumentación** |
| **E8 metacognición** | mundo EXISTS_AS_IS · mecanismo MISSING_PRIMITIVE | `ChangeScheduler` con `changes:[{at_step,rules}]` da el reversal; `d4_change` y `d4_temporal_variety_*` ya lo usan | el lazo error → meta-estado → cambio de política. `last_prediction_error` va sólo al observador | **agente** |
| **E9 ultraestabilidad** | MISSING_PRIMITIVE | `viability_recovery_metric` ya declara que **no** mide reorganización de parámetros | operador de perturbación de la variable esencial (el scheduler sólo intercambia reglas) **y** el segundo lazo | **mundo + agente** |

## H · Huecos demostrados tras esta auditoría

1. **A4 descarta `mask` y `time_fraction`** — dos de los cuatro campos sellados. Consecuencia
   medida: ciego a su posición en cualquier mundo sin objetos.
2. **No hay representación de objetivo** — `ReachRate` no es expresable.
3. **El planner puntúa sólo energía y `done`** — un modelo motor perfecto no cambia conducta donde
   la energía no depende de la acción.
4. **No hay instrumento motor** — ni desplazamiento, ni navegación, ni controlabilidad.
5. **`NO_GENERIC_SELF_STATE_INGRESS`** — el estado corporal sólo puede entrar modificando A4.
6. **`E1B_MISSING_ESTIMATION_PRIMITIVE`** — sin modelos de sensor ni ruido.
7. **Operador de perturbación** (E9) y **endpoint de ganancia de información** (E5).

## I · Mapa de reutilización · usar, no recrear

| Para | Reutilizar | No recrear |
|---|---|---|
| predicción motora de E0 | `WorldModel.next_state_head` + `loss_state`, ya entrenados y con target detached | otro modelo de transición |
| cuerpo permutado de E0 | subclase de `Physics` + `EpisodeComponents.physics` | tocar `DIRECTION_DELTA` ni el motor |
| referencias posicionales | `entities` del escenario / `WorldDraft` | un sistema de landmarks |
| control causal de todo | brazos N / LEGACY / FULL, certificados | otro mecanismo de congelación |
| experiencia idéntica | `force_action` + `replay` | otro arnés de gemelos |
| reversal de E8 | `ChangeScheduler` + `changes` | fases nuevas |
| contexto × ítem de E6 | condición multicanal de `RuleEngine` | reglas contextuales nuevas |
| reaparición de recursos | `OpportunityLifecycle` | respawn propio |
| mundos held-out de E7 | `SeedBrowser` + `degeneracy_flags` | selección de semillas a mano |
| cambiar tamaño/radio | `WorldDraft.edit(reason, **changes)`, con procedencia | editar YAML a mano |
