# E1, E2 y el cuerpo remapeado · medido contra el código

**2026-09-18 · READ-ONLY.** `HEAD f72d225` · rama `experiment/cognitive-live-observatory-01` ·
**cero modificaciones al código** (sólo documentos nuevos sin seguimiento).

---

## TRES CORRECCIONES QUE CAMBIAN LA DECISIÓN

### 1 · «El organismo nunca consume» era un artefacto de mi configuración

Lo medí con `use_planner: False` — **el brazo ablacionado**. Con el planner encendido, y comida en
las cuatro celdas adyacentes:

```
A4 con planner     227 CONSUME emitidos · 210 con efecto · energía final 60.00
A4 sin planner       0 CONSUME          ·   0 con efecto · MUERE en el paso 201
A0 aleatorio        83 CONSUME          ·  67 con efecto · energía final 60.00
```

**El planner es lo que produce la conducta alimentaria**, y triplica al azar. Sin él A4 no emite ni
un CONSUME en 201 pasos y se muere. Todo lo que dije sobre un organismo que no toca el mundo estaba
medido sobre el arm equivocado.

### 2 · `action_availability` se declara pero nadie la aplica

`WorldDraft` la valida contra `{MOVE,PUSH,CONSUME,INSPECT,NOOP}` y los codecs la serializan, pero
**ningún código de runtime la consulta**: cero apariciones en `terrario/world/`,
`terrario/experiment/` y `terrario/agent/`. Un mundo «sólo MOVE» es una declaración, no una
restricción. El planner muestrea uniforme sobre las 25 acciones sin saber de ella.

### 3 · El radio del mundo y el del agente no se negocian

`ObservationEncoder` fija `flat_dim = 64·⌈view_size/2⌉²` en la construcción: 576 para `view_size=5`,
1024 para 7. Un mundo con `view_radius=3` contra un agente con `view_size=5` **revienta**
(`mat1 and mat2 shapes cannot be multiplied (1x1024 and 576x16)`). Los dos se declaran aparte y hay
que igualarlos a mano.

---

## A · Extensión de `s_t` · mapa y formas

```python
self._state_dim = latent_dim + hidden_dim + latent_dim + memory_dim      # a4:177
state = torch.cat([latent, hidden, memory_context, lt_context])          # a4:343 — SIN normalización
```

Con la configuración usada hoy (`16+24+16+8`) → **`state_dim = 64`**.

**Siete módulos se construyen con ese tamaño** y cambiarían de forma al añadir un escalar:

| Módulo | Línea | Peso afectado |
|---|---|---|
| `WorldModel` | a4:181 | `backbone[0]`: `(state_dim+25) → 256`; `next_state_head`: `256 → state_dim` **(entrada y salida)** |
| `uncertainty_estimator` | a4:189 | cada cabeza del ensemble |
| `policy_head` | a4:196 | `Linear(state_dim, 256)` |
| `operation_head` | a4:220 | `Linear(state_dim, NUM_ACTION_TYPES)` |
| `selector_head` | a4:221 | `Linear(state_dim, selector_dim)` |
| `direction_head` | a4:234 | `Linear(state_dim, NUM_DIRECTIONS)` |
| `selector_residual` | a4:250 | `Linear(state_dim, MAX_TARGET_SLOTS)` |

**`next_state_head` es el caso delicado**: predice un vector de `state_dim`, así que al ampliar el
estado el world model pasaría a **predecir también la energía futura**. Eso puede ser deseable
—sería predicción metabólica— pero no es un efecto lateral: es una capacidad nueva entrando por la
puerta de atrás.

**Memorias:** el buffer episódico guarda `_last_latent` —**no** `s_t`— y lo indexa por similitud de
latente (`a4:588`). La LTM lee con `hidden` (`a4:341`). **Así que añadir energía a `_build_state`
NO contamina las claves de memoria.** Ése era mi temor y no se cumple: sólo se contaminarían si la
energía entrara por `channels`.

**`NO_AUX_FEATURE_SLOT`.** Buscado otra vez por comportamiento: no hay `aux_features`, ni vector de
contexto, ni entrada escalar auxiliar, ni conditioning. La única vía es ampliar `torch.cat`.

**Checkpoints:** `set_parameters` copia por nombre y **salta lo que no encuentra**
(`if key in params`), así que no explota — pero un gemelo restaurado desde parámetros viejos
quedaría con las filas nuevas sin inicializar, en silencio.

## B · Temporalidad de B2

```
perceive(obs_t)      homeostasis._energy ← obs_t.agent_energy      (PRE)
decide()             acción
[transición del mundo]
learn(consequence)
  a4:583             homeostasis.update(consequence.energy_delta)  ← ya es POST
  ...
  a4:671             reward = self._policy_reward(consequence)      ← aquí drive ya es POST
```

**`drive_before` NO está disponible cuando se llama a `_policy_reward`**: `update()` corre 88 líneas
antes, dentro del mismo `learn()`. Es recuperable de dos formas —`energía_after − energy_delta`, o
capturándolo en `perceive`— pero hoy no existe snapshot pre-transición.

**Qué usa hoy el aprendizaje de política:** `reward = float(consequence.energy_delta)`, y de ahí
salen `_energy_baseline` y `advantage`. **`energy_delta` además alimenta** `energy_target` del world
model (a4:635) y las cabezas de incertidumbre (a4:730). Sustituirlo tocaría tres consumidores; por
eso sumar o mantener separado no es lo mismo que reemplazar.

**`NO_REWARD_DECOMPOSITION`.** A1 y A2 registran un `"reward"` escalar plano; A4 ni eso. No hay
estructura de componentes de recompensa en ninguna traza.

## C · Cadena planner ↔ foraging · MEDIDA

El planner **sí** propaga `sim_state = next_state` por H pasos y **sí** simula CONSUME (muestrea las
25 acciones). Horizonte 5, 10 candidatos, sobre `25⁵ = 9 765 625` secuencias → cobertura
**1.0 × 10⁻⁶**. Puntúa `total_energy − 10·done_prob`.

**Tres brazos, mismo mundo, misma semilla, 400 pasos, comida en un anillo. n = 1 semilla:**

```
  comida a distancia 2            pasos   consumos   E final
  NORMAL                            400          5     20.15
  LEGACY (θ congelado)              267          1      0.10   MUERE
  FULL_ADAPTIVE_FREEZE              267          1      0.10   MUERE
  A0 aleatorio                      400          9     60.00

  comida a distancia 3            pasos   consumos   E final
  NORMAL                            400          5     20.15
  LEGACY                            334          2      0.05   MUERE
  FULL_ADAPTIVE_FREEZE              267          1      0.10   MUERE
  A0 aleatorio                      267          1      0.10   MUERE
```

**A distancia 3, NORMAL es el único brazo que sobrevive**, y los dos brazos congelados mueren. Ésa
es la firma causal que E2 busca: la diferencia la produce **poder adaptar**, no la arquitectura.
A distancia 2 el azar gana (9 contra 5): el paseo aleatorio encuentra comida cercana mejor que un
planner de 10 candidatos.

**Dónde se rompe la cadena cuando se rompe:** con una sola fuente distante y sin consumiciones
accidentales, el world model nunca ve un ejemplo de `CONSUME → +energía`, así que `energy_pred` es
plano, el score es plano (**varianza medida ≈ 0.001**) y la primera acción del planner no
correlaciona con la dirección de la comida —medido: comida a la derecha → `MOVE/UP`, a la izquierda
→ `PUSH/UP`, arriba → `NOOP/UP`. **El corte es la primera consumición, no el planner.**

## D · Veredicto del cuerpo remapeado

```
PARTIAL — la cadena existe y está medida, pero depende de una condición previa
```

`modelo motor aprendido → posición simulada → comida futura → energía prevista → acción` **sí
existe**: es exactamente el mecanismo que produce los 210 consumos con comida adyacente, y el
contraste NORMAL contra FULL_FREEZE a distancia 3 lo confirma con muerte de por medio.

El primer corte: **el organismo necesita al menos una consumición accidental** para que el world
model aprenda que CONSUME paga. Con comida adyacente la consigue; a distancia 2–3 la consigue a
veces; más lejos, no. Eso no exige `goal` ni `ReachRate`: exige densidad de recurso suficiente al
principio, que es configuración del escenario.

**Por tanto E0′ es expresable hoy** —«mi cuerpo cambió, reaprendo a moverlo para seguir
alimentándome»— con `Physics` inyectada, recurso energético y los tres brazos ya certificados.

## E · Instrumentos reutilizables

| Lo que E1/E2 necesita medir | Existe | Dónde |
|---|---|---|
| tiempo hasta el primer consumo | **no** directamente | derivable de la traza (`step` del primer `effects`) |
| consumo por oportunidad | **sí** | `tasa_oportunidad`, `tasa_realizacion`, `tasa_interaccion` |
| balance energético | **sí** | `contabilidad_energetica`; `run_measures` da `balance_energia`, `energia_final` |
| supervivencia y pasos vividos | **sí** | `run_measures`: `sigue_vivo`, `pasos_vividos` |
| eficiencia de camino | **no** | — |
| error de predicción pre/post remapeo | **parcial** | `last_prediction_error` existe por paso; `examen_prediccion` mide ranking de energía, no desplazamiento |
| recuperación tras remapeo | **no** | — |

## F · Huecos demostrados

1. **`NO_AUX_FEATURE_SLOT`** — la energía sólo entra ampliando `torch.cat` en `_build_state`, y eso
   cambia la forma de **siete** módulos, incluida la salida de `next_state_head`.
2. **No hay snapshot homeostático pre-transición** — `drive_before` se pierde 88 líneas antes de
   `_policy_reward`.
3. **`NO_REWARD_DECOMPOSITION`** — no se puede instrumentar externo contra interoceptivo por separado.
4. **`action_availability` no se aplica** en runtime.
5. **Radio de mundo y de agente acoplados a mano**, sin negociación ni comprobación.
6. **Sin métrica de eficiencia de camino ni de recuperación tras remapeo.**

**Lo que NO es un hueco, contra lo que yo mismo dije:** las claves de memoria **no** se contaminarían
—el buffer indexa por `_last_latent`, la LTM lee por `hidden`, ninguno usa `s_t`.

---

**Advertencia sobre estas cifras.** Las tablas de la sección C son **n = 1 semilla**, una corrida
por brazo. Muestran que el contraste es construible y dónde está el corte; **no son evidencia**. El
protocolo pareado sobre varias semillas es el experimento, no esto.
