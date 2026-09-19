# Informe íntegro · estado del ser, mediciones y confundidos

**Destinatario:** auditoría multi-modelo. Este documento es **autocontenido**: no
remite a ninguna conversación previa. Todo número trae sus condiciones de
medición. Toda afirmación trae su clasificación y su vía de refutación.

**Repositorio:** `/home/wis/causal-bench-01`, rama `bench/causal-capability-01`.
**Fecha de las mediciones:** 2026-09-18/19.

**Clasificación usada:**

| etiqueta | significado |
|---|---|
| `CÓDIGO` | se lee directamente en el fuente citado |
| `MEDIDO` | se obtuvo ejecutando, con las condiciones declaradas en §1 |
| `DERIVADO` | se sigue algebraicamente de `CÓDIGO` |
| `SIN VERIFICAR` | afirmado y no comprobado |

---

# §0 · Cómo auditar este documento

Cada afirmación verificable trae el comando que la confirma o la tumba. La
auditoría no requiere confiar en el autor. Si un comando devuelve algo distinto
de lo declarado, la afirmación es falsa y el documento está mal.

---

# §1 · Configuración realmente usada  ·  `CÓDIGO`

**Advertencia de integridad.** `A4_ADVANCED` tiene un `DEFAULT_CONFIG` y los
experimentos usan un diccionario `BASE` que lo **sobrescribe**. Reportar las
ecuaciones con las dimensiones de `DEFAULT_CONFIG` y los números con las de
`BASE` es un error; se cometió en un documento anterior y se corrige aquí.

## 1.1 · `BASE` — lo que corrió en todas las mediciones

`scripts/exp_adaptive_foraging_01.py:77`

```python
BASE = {
    "use_planner": True, "use_world_model": True, "use_uncertainty": True,
    "use_episodic_memory": True, "use_longterm_memory": True, "use_temporal": True,
    "use_online_learning": True, "view_size": 5,
    "latent_dim": 16, "hidden_dim": 24, "memory_dim": 8, "memory_slots": 4,
    "memory_capacity": 16, "ensemble_size": 2,
    "planner_horizon": 5, "planner_candidates": 10,
}
```

Todo lo demás se hereda de `DEFAULT_CONFIG` (`a4_advanced.py:55`), en particular:

```python
"temporal_core": "ssm",            # NO gru
"homeostasis_threshold": 0.5,
"use_homeostasis": True,
"use_factored_action": False,
"use_entropy_regularization": False,   "entropy_coefficient": 0.01,
"addressing_mode": "T0_DIRECTIONAL",
"learning_rate": 3e-4, "grad_clip": 1.0, "update_frequency": 1,
"learning_commit_enabled": True,
```

## 1.2 · Dimensiones efectivas

| símbolo | `DEFAULT_CONFIG` | **`BASE`, el que corrió** |
|---|---|---|
| `latent_dim` | 128 | **16** |
| `hidden_dim` | 256 | **24** |
| `memory_dim` | 128 | **8** |
| `memory_slots` | 64 | **4** |
| `memory_capacity` (episódica) | 1000 | **16** |
| `ensemble_size` | 5 | **2** |
| `state_dim = latent+hidden+latent+memory` | 640 | **64** |
| entrada del modelo del mundo `= state+25` | 665 | **89** |

`a4_advanced.py:177` — `self._state_dim = latent_dim + hidden_dim + latent_dim + memory_dim`

**Consecuencias que la auditoría debe tener presentes:**

- La memoria episódica tiene **16 entradas**. En un episodio de 300 pasos se
  reescribe unas 19 veces. Cualquier afirmación sobre «memoria de experiencia»
  opera sobre una ventana de 16.
- La memoria a largo plazo tiene **4 ranuras**.
- El latente comprime una ventana `4×5×5 = 100` a **16 dimensiones**. Es un
  cuello estrecho, y es directamente relevante al riesgo de compresión
  representacional al inyectar una variable nueva.
- La incertidumbre es la varianza de **2 cabezas**, no de 5. Una varianza
  muestral de `n=2` es un estimador muy ruidoso.

## 1.3 · Mundo

`scripts/exp_adaptive_foraging_01.py:74,92`

```
VIEW_RADIUS = 2   →  ventana 5×5        NUM_CHANNELS = 4
MAX_ENERGY = 60.0     INITIAL_ENERGY = 30.0
STEP_COST = 0.15      FOOD_GAIN = 10.0      GRID = 7
```

Acciones: `|A| = 25 = 5 tipos × 5 direcciones`, con
`a = 5·tipo + dirección`,
tipos `{MOVE, PUSH, CONSUME, INSPECT, NOOP}`,
direcciones `{UP, DOWN, LEFT, RIGHT, NONE}`.

## 1.4 · Condiciones de cada medición reportada

| medición | semilla | mundo | pasos | aprendizaje |
|---|---|---|---|---|
| saturación, `drive`, temperatura | 4242 | `rich_world` y `ring_world(3)` | 300 | activo |
| desajuste de unidades | 4242 | `rich_world` | 40 | activo |
| ventaja por dirección de MOVE | 4242 | `rich_world` y `ring_world(3)` | 300 | activo |
| cobro del oráculo perfecto | 2 | `world_for(['EPMEM-A1'])` | 132 | oráculo `FULL` |

---

# §2 · El núcleo temporal es SSM, no GRU  ·  `CÓDIGO`

`a4_advanced.py:149`

```python
if self.config["temporal_core"] == "gru":
    self.temporal_core = GRUCore(latent_dim, hidden_dim)
else:
    self.temporal_core = SSMCore(latent_dim, hidden_dim)
```

`temporal.py:88`

```python
def forward(self, x, h):
    transition = self.a.clamp(-0.999, 0.999)
    new_h = transition * h + x @ self.B.T
    output = new_h @ self.C.T
    return output, new_h
```

$$
h_t = \mathrm{clip}(a,-0.999,0.999)\odot h_{t-1} + B\,e_t,
\qquad
\text{out}_t = C\,h_t
$$

Inicialización (`temporal.py:74`): $a \sim 0.99 + 0.01\,\mathcal N(0,1)$.

**Es una recurrencia lineal diagonal**, es decir una media móvil exponencial con
constante de tiempo $\tau \approx -1/\ln|a| \approx 100$ pasos para $a=0.99$.

**Y el gradiente temporal está cortado.** `a4_advanced.py:405`

```python
output, self._hidden = self.temporal_core(x, self._hidden)
self._hidden = self._hidden.detach()
h = output.squeeze(0)
```

`output` y `new_h` son tensores distintos en SSM, pero `output` se computa *desde*
`new_h` antes del `detach`, y `self._hidden` se reasigna. Por tanto:

$$
\frac{\partial \mathcal L_t}{\partial \theta_{\text{SSM}}} \neq 0
\qquad\text{y}\qquad
\frac{\partial \mathcal L_t}{\partial h_{t-1}} = 0
$$

`DERIVADO`. **Consecuencia:** $a$ sí recibe gradiente —del error del paso
actual— pero **nunca recibe crédito por haber recordado lo correcto**, porque
ningún gradiente cruza el tiempo. La longitud efectiva de la traza queda como
hiperparámetro cercano a su inicialización, no como algo aprendido.

**Comando:** `grep -n "temporal_core" terrario/agent/agents/a4_advanced.py`

---

# §3 · El confundido de temperatura  ·  `DERIVADO` sobre `CÓDIGO`

Éste es el hallazgo principal de este informe y el que faltaba en toda la
documentación previa.

## 3.1 · El hecho de código

`a4_advanced.py:427`

```python
temperature = (1.0 + self.homeostasis.exploration_bias) if self._use_homeostasis else 1.0
```

`homeostasis.py:44`

```python
@property
def exploration_bias(self) -> float:
    return 1.0 - self._energy
```

`a4_advanced.py:358` — `self.homeostasis._energy = observation.agent_energy`

`policy.py:63` — `probs = F.softmax(logits / temperature, dim=-1)`

Por tanto, con $\varepsilon_t$ la energía propia normalizada:

$$
T_t = 2 - \varepsilon_t \in [1,2],
\qquad
\pi(a\mid s_t) = \mathrm{softmax}\!\big(\ell'/T_t\big)
$$

Y **`ℓ'` no depende de `ε`**: los logits salen de `policy_head(s_t)` y
`s_t = [e_t; h_t; m_t; l_t]` no contiene la energía (`a4_advanced.py:343`); el
bono de incertidumbre tampoco.

**Comando:** `grep -n "agent_energy" terrario/agent/agents/a4_advanced.py`
→ esperado: **dos** apariciones, líneas 358 y 364, la segunda dentro de un dict
de traza. Ninguna entra en un tensor.

## 3.2 · Por qué invalida la prueba estándar de interocepción

La prueba habitual es

$$
H_1:\quad D_{\mathrm{TV}}\big(\pi(\cdot\mid o,\varepsilon_L),\;\pi(\cdot\mid o,\varepsilon_H)\big) > 0
$$

Esta prueba la **pasa el organismo actual, siempre**, con cero competencia
interoceptiva: basta que $\ell'$ no sea constante para que dos temperaturas
distintas den dos distribuciones distintas. No cambia lo que prefiere; cambia
cuán aleatorio actúa.

## 3.3 · El signo del artefacto

Con $\beta = 1/T$:

$$
\frac{\partial p_i}{\partial\beta} = p_i\big(\ell_i - \langle\ell\rangle_p\big),
\qquad
\langle\ell\rangle_p = \sum_j p_j \ell_j
$$

$$
\beta = \frac{1}{2-\varepsilon}
\;\Longrightarrow\;
\frac{\partial\beta}{\partial\varepsilon} = \frac{1}{(2-\varepsilon)^2} > 0
\;\Longrightarrow\;
\frac{\partial p_{a^\star}}{\partial\varepsilon}
= \frac{p_{a^\star}\big(\ell_{a^\star}-\langle\ell\rangle_p\big)}{(2-\varepsilon)^2}
$$

Definiendo $\Delta_{\text{intero}} = P(a^\star\mid \varepsilon_L) - P(a^\star\mid \varepsilon_H)$
con $\varepsilon_L < \varepsilon_H$:

$$
\boxed{\;\operatorname{sign}\big(\Delta_{\text{intero}}\big) = -\operatorname{sign}\big(\ell_{a^\star} - \langle\ell\rangle_p\big)\;}
$$

**Lectura:** el signo esperado —energía baja ⇒ más probabilidad de consumir—
aparece **sólo cuando la acción diana está por debajo de la media de logits**.

- Organismo recién nacido: logits casi uniformes ⇒ $\Delta_{\text{intero}}\approx 0$.
- Organismo que ya aprendió que consumir paga: $\ell_{\text{CONSUME}}$ sube por
  encima de la media ⇒ $\Delta_{\text{intero}} < 0$, y **más negativo cuanto
  mejor sea el organismo**.

La métrica mostraría la interocepción *desapareciendo* conforme crece la
competencia, por un artefacto de temperatura.

## 3.4 · Magnitud del artefacto

Con $\varepsilon_L = 0.5 \to \varepsilon_H = 1.0$: $\beta$ pasa de $0.667$ a
$1.0$, un cambio del 50 % en temperatura inversa. Para
$p_{a^\star}\approx 0.1$ y $\ell_{a^\star}-\langle\ell\rangle \approx 2$:

$$
|\Delta_{\text{intero}}| \approx 0.067
$$

`DERIVADO`, orden de magnitud. **Comparación:** el mayor efecto real medido en
este proyecto es $\Delta G_{NF} = +0.00852$ (DISCOVERY-32, 32 nacimientos). El
artefacto es **casi dos órdenes de magnitud mayor** que cualquier señal
detectada.

## 3.5 · El falsador limpio

Dividir por $T>0$ **preserva el orden de los logits**. Por tanto el artefacto no
puede reordenar acciones, y la interocepción real sí:

$$
\tau_{\text{Kendall}}\big(\ell(o,\varepsilon_L),\,\ell(o,\varepsilon_H)\big) = 1
\qquad\text{hoy, exactamente, por construcción}
$$

Cualquier $\tau < 1$ es evidencia de dependencia corporal que la temperatura no
puede producir. Nulo analítico, no estimado.

## 3.6 · Dónde la misma métrica NO está confundida

En discriminación perceptiva, valencia y memoria, las dos condiciones comparadas
tienen **el mismo $\varepsilon$**, luego la misma $T$, y el factor se cancela.
El confundido es exclusivo de la interocepción, porque es la única habilidad
cuya variable manipulada es la que fija la temperatura.

---

# §4 · Crédito del movimiento  ·  `MEDIDO` + `DERIVADO`

## 4.1 · El hecho físico

Las reglas del mundo tienen condición `action = "CONSUME"`. Para toda acción del
bloque MOVE no disparan, luego el delta energético es sólo el coste de paso:

$$
y_t = -0.15 \qquad \forall\, a \in \mathbb M = \{\text{MOVE}\times\text{5 direcciones}\}
$$

**Medido** (semilla 4242, 300 pasos):

```
MUNDO RICO      línea base final b = +0.0975
  MOVE ↑ / ← / → / ∅ :  energy_delta único = [-0.15]   ventaja A = -0.2475
MUNDO ANILLO    línea base final b = +0.0700
  las cinco direcciones :  energy_delta único = [-0.15]   ventaja A = -0.2200
```

## 4.2 · Lo que esto demuestra, y lo que NO

La recompensa inmediata es **constante sobre el bloque MOVE**, luego la ventaja
$A_t$ es idéntica para las cinco direcciones. De ahí se sigue:

$$
\sum_{a\in\mathbb M}\pi(a\mid s)\,A_{\mathbb M}\,\nabla_\theta\log\pi(a\mid s)
= A_{\mathbb M}\,\nabla_\theta P(\mathbb M\mid s)
$$

**Conclusión válida:** la actualización inmediata **no asigna a MOVE el beneficio
energético que aparece varios pasos después**. No hay crédito por la utilidad
futura de una dirección.

**Conclusión NO válida** —se afirmó antes y se retracta aquí—: que las
probabilidades relativas entre direcciones sólo cambien por ruido. Con
logits acoplados por softmax:

$$
\frac{\partial J}{\partial \ell_i} - \frac{\partial J}{\partial \ell_j}
= (\pi_i - \pi_j)\,(c - \bar r) \neq 0 \quad\text{si } \pi_i \neq \pi_j
$$

La preferencia direccional **puede** cambiar sistemáticamente sin que exista
aprendizaje sobre qué dirección lleva a comida. *Poder cambiar la preferencia* y
*recibir crédito por la utilidad futura* son cosas distintas.

**Y el signo del efecto va al revés de lo que se afirmó.** Con $c = -0.15$ y
$\bar r \approx b > 0$, el término $(c-\bar r)$ es negativo, luego el ascenso
empuja hacia arriba la dirección **menos** probable: es una fuerza igualadora,
no concentradora. A nivel de muestra única,
$\Delta\ell \propto A_t(\mathbf 1_{a_t}-\pi)$ con $A_t<0$ **penaliza la acción
tomada**. La afirmación «la primera dirección sorteada se autorrefuerza» era
falsa, y falsa en sentido opuesto.

## 4.3 · Dos vías de influencia que el argumento anterior no cubría

1. `L_WM` y `L_U` actualizan encoder, núcleo temporal y proyecciones de memoria,
   que **producen `s_t`**, que es la entrada de `policy_head`. Existe una ruta de
   aprendizaje a las preferencias direccionales que no pasa por el gradiente de
   política.
2. El planner gana la decisión con probabilidad $\tfrac12$
   (`a4_advanced.py:536`). En esos pasos $a_t$ **no es una muestra de $\pi$**, y
   recalcular $\log\pi(a_t)$ con grafo fresco no lo convierte en una. Es
   REINFORCE fuera de política sin corrección de importancia. `SIN VERIFICAR`:
   no se ha comprobado si `L_π` se omite, se aplica igual, o se corrige.

## 4.4 · Colapso medido, de procedencia ajena a este informe

Un comentario en `a4_advanced.py:705` registra una medición previa: sobre 400
pasos, el organismo eligió CONSUME 173 veces con objeto adyacente 222 veces, y
apuntó ARRIBA en 215 de 236 intentos; la indecisión colapsó a 0.05 bits.
`find_target` resuelve CONSUME por dirección, luego apuntar mal es no comer.
La regularización por entropía existe, su coeficiente está declarado
(`entropy_coefficient = 0.01`) y **está desactivada por defecto**.

Dado §4.2, ese colapso **no se explica por `L_π`** y queda como pregunta abierta.

---

# §5 · Reparaciones aplicadas en esta sesión  ·  `CÓDIGO` + `MEDIDO`

## 5.1 · Techo energético

`terrario/world/state.py:158` — `max_energy` aparecía en todo `terrario/world/`
sólo como divisor en `state.py:110` y en la serialización. **Nunca acotaba
`agent.energy`.**

```python
def set_agent_energy(self, agent_id: int, energy: float) -> None:
    if self._max_energy > 0:
        energy = min(energy, self._max_energy)
    self._state.agents[agent_id].energy = energy
```

El suelo no se toca: la muerte se decide sobre el valor solicitado.

## 5.2 · Pedido contra realizado

`terrario/world/rules.py` — nueva `EnergyApplication(requested, realized,
energy_before, energy_after)` con `clipped` derivado, y
`apply_effects_detailed`. `apply_effects` conserva su firma —un float— y
devuelve **lo realizado**:

$$
y^{\text{real}} = \mathrm{clip}(E_t + \Delta E^{\text{req}},\, \cdot,\, E_{\max}) - E_t
$$

`terrario/core/types.py:191` — `Consequence` transporta ahora
`requested_energy_delta`, `energy_before`, `energy_after` junto a `energy_delta`.

**Importa porque** el predictor de consecuencias se entrena con
`consequence.energy_delta` (`a4_advanced.py:635`). Devolver lo pedido le
enseñaría una consecuencia que no ocurrió.

## 5.3 · Autoridad interoceptiva única

`a4_advanced.py:583` contenía `self.homeostasis.update(consequence.energy_delta)`
— sumaba energía **absoluta** a una variable **normalizada**. Con
`max_energy = 60`, el coste de paso restaba 60× de más y una comida saturaba.
Eliminado. `perceive` es la única autoridad.

## 5.4 · Techo del generador derivado de la economía

`terrario/lab/world_generator.py:423` — el techo plano de 60.0 mordía al oráculo
perfecto. **Medido** (`world_for(['EPMEM-A1'], seed=2)`, oráculo `FULL`, 8
estaciones, `gain = 8.0`, `step_cost = 0.15`):

```
declarado por acierto : 7.85
cobrado de hecho      : [7.85, 7.85, 7.85, 7.85, 7.85, 7.50, 1.20, 1.20]
```

Las tres últimas estaciones valían una sexta parte. Reparado con
`max(max_energy, initial_energy + n_estaciones × gain)`.

## 5.5 · Efecto medido de las reparaciones

Semilla 4242, 300 pasos, leído en `observation_t.agent_energy` —lo que `perceive`
escribe y lo único que `decide` puede leer:

| | antes | después |
|---|---|---|
| energía cruda máxima (mundo rico) | **1725.60** | 59.85 |
| pasos con el sensor saturado (rico) | 287/300 (96 %) | **0/300** |
| `temperature` exactamente `1.0` ≡ homeostasis OFF (rico) | 286/300 (95 %) | **0/300** |
| `drive > 0` (rico) | 2/300 (1 %) | 2/300 (1 %) |
| `drive > 0` (anillo) | 177/300 (59 %) | 177/300 (59 %) |

**El mundo rico sigue sin excitar el circuito**: `drive` con varianza
`0.000000`. Cualquier prueba de regulación debe correr en el mundo anillo o en
uno con escasez comparable.

## 5.6 · Suite

`pytest tests/ -q`: **5 fallos, los 5 preexistentes**, ninguno nuevo.
Preexistentes: 3 en `test_agent_composition.py`, 2 en
`test_system_baseline_characterization.py`. **Aviso:** el segundo grupo es
precisamente el guardián de deriva conductual de A0/A1/A4, y llevaba rojo desde
antes de estos cambios. No hay guardia de regresión conductual disponible.

---

# §6 · Defectos abiertos

| id | defecto | estado |
|---|---|---|
| D1 | doble autoridad sobre el estado interoceptivo | **reparado** (§5.3) |
| D2 | energía sin techo | **reparado** (§5.1) |
| D3 | saturación del sensor | **reparado** (§5.1) |
| D4 | el único acoplamiento homeostático era inerte el 95 % | **reparado** por D2/D3 |
| D5 | `ε_t` no entra en `s_t`: el valorador es interoceptivamente ciego | **abierto** |
| D6 | dos umbrales homeostáticos sin relación | **abierto** |

## D5 · Formulación

`a4_advanced.py:343` — `state = torch.cat([latent, hidden, memory_context, lt_context])`.
`observation.agent_energy` no entra en ningún tensor.

$$
R^{*}_{X} = \mathbb E\big[\operatorname{Var}(Y\mid X)\big],
\qquad X = (s_t, a_t)
$$

$$
R^{*}_{X+E} = \mathbb E\big[\operatorname{Var}(Y\mid X, E)\big] \;\le\; R^{*}_{X}
$$

La igualdad a cero se alcanza sólo si $(X,E)$ determina $Y$. **No se afirma que
añadir energía garantice error cero**: la red puede quedarse por encima del
límite por compresión, capacidad u optimización. Con `latent_dim = 16` (§1.2)
la compresión es un riesgo concreto, no retórico.

**Condición de validez que hay que construir, no suponer:** `s_t` contiene
historia recurrente y contextos de memoria, que pueden correlacionar con la
energía por duración de vida o encuentros previos. Demostrar
$\operatorname{Var}(Y\mid X)>0$ exige construir casos con
$s^{(1)}=s^{(2)}$, $a^{(1)}=a^{(2)}$, $E^{(1)}\neq E^{(2)}$, $Y^{(1)}\neq Y^{(2)}$.

## D6 · Formulación

| | dónde | unidad | valor | uso |
|---|---|---|---|---|
| del científico | `world_generator.py:84` `Economy.low_energy` | absoluta | 14.0 | puntúa si una elección se tomó con hambre (`:558`, `:640`) |
| del organismo | `a4_advanced.py:94` `homeostasis_threshold` | normalizada | 0.5 | `drive` y `temperature` |

Con `max_energy = 60` el umbral del organismo cae en **30 absolutos** frente a
los **14** declarados como escasez. Tras la reparación §5.4 el techo de los
mundos generados pasa a `initial + n·gain` = **84** con 8 estaciones, y el umbral
del organismo se va a **42**. La reparación **alejó** los dos umbrales.

---

# §7 · Afirmaciones que emití y retracto

Se listan para que la auditoría no las re-derive desde documentos anteriores.

| afirmación | estado | corregida por |
|---|---|---|
| «la dinámica direccional tiene deriva exactamente cero» | **falsa**, §4.2 | revisión externa |
| «la primera dirección sorteada se autorrefuerza» | **falsa y de signo opuesto**, §4.2 | revisión externa |
| «añadir energía lleva $L_{\text{energy}}$ a cero» | **falsa**, §6/D5 | revisión externa |
| «el planner aporta gradiente direccional» | **impreciso**: aporta *selección*, no gradiente | revisión externa |
| «SHAM por desplazamiento temporal fijo destruye la información» | **falsa**: con $E_t=E_0-ct$, $E_{t-k}=E_t+ck$ | revisión externa |
| «`M` se escribe fuera del optimizador» | **falsa**: está dentro (medido, 58 parámetros) y la escriben dos rutas | `adaptive_freeze.py:197` |
| «el núcleo temporal es GRU» | **falsa**: es SSM por defecto, §2 | este informe |
| «$s_t\in\mathbb R^{640}$» | **falsa** para lo medido: es $\mathbb R^{64}$, §1.2 | este informe |
| «el organismo nunca consume» | **falsa**: se midió con el planner ablacionado | medición posterior |
| «la incertidumbre no llega a la decisión» | **falsa**: `a4_advanced.py:438` | `CÓDIGO` |
| «`M` pone un techo a la acumulación» | **retirada**: meseta de norma ≠ saturación de información | — |
| «la curiosidad está implementada» | **retirada**: es un bono de desacuerdo de ensemble sobre logits | — |

---

# §8 · Señales presentes que ningún tensor consume  ·  `CÓDIGO`

Patrón recurrente, y el que ha producido los hallazgos de mayor valor.

| señal | dónde existe | consumidor | comando |
|---|---|---|---|
| `observation.agent_energy` | llega a `perceive` | ninguno (sólo `homeostasis` y traza) | `grep -n "agent_energy" terrario/agent/agents/a4_advanced.py` |
| `observation.mask` | sellada en `Observation` | **cero usos en A4** | `grep -n "\.mask" terrario/agent/agents/a4_advanced.py` |
| `observation.time_fraction` | sellada en `Observation` | ninguno | `grep -n "time_fraction" terrario/agent/agents/a4_advanced.py` |
| `consequence.events` (`move_blocked_wall`, `move_blocked_object`, `move_success`) | generados en `physics.py:97,102,104`, sobreviven al filtro agente/observador en `physics.py:193` | **A4 nunca lee `consequence.events`** | `grep -n "events" terrario/agent/agents/a4_advanced.py` → sólo su propia traza de salida |
| `entry["action"]`, `entry["energy_delta"]` de la memoria episódica | escritos cada paso en `memory.py:42` | la lectura devuelve **sólo embeddings** (`memory.py:110`) | `grep -n 'entry\["action"\]' terrario/agent/` |
| `homeostasis.drive` | `homeostasis.py:39` | ninguno: `a4:513` y `a4:562`, ambos dentro de `self._trace.append` | `grep -rn "drive" terrario/agent/` |

---

# §9 · Lo que está sin verificar

1. Si `L_π` se aplica, se omite o se corrige cuando el planner elige la acción.
2. Si `physics.step` modifica la energía, condición para que
   `energy_delta = E_{t+1}-E_t` sea exacta.
3. `find_target`: sólo se conoce por un comentario en el código que dice que
   resuelve CONSUME por dirección.
4. Manejadores de `PUSH`, `CONSUME`, `INSPECT`, `NOOP` en la física: sólo se ha
   leído `MOVE`.
5. `curiosity.py` y `scientific.py`: nunca abiertos.
6. `use_factored_action` y la regularización por entropía: se conocen los flags y
   los valores por defecto, no su efecto.
7. Si un `no_grad` sobre el objetivo de estado siguiente basta para descartar
   colapso representacional. No basta: requiere prueba funcional distinta.
