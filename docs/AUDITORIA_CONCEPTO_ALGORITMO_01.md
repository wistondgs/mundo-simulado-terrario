# Auditoría concepto → algoritmo
## Qué dice cada módulo que es, y qué hace realmente

**2026-09-18.** **[COD]** hecho de código con fichero:línea · **[MED]** medido · **[INF]** inferencia.

---

# Parte 1 · ¿Está bien fundamentado el algoritmo que representa cada concepto?

| Flag | Concepto que declara | Lo que el algoritmo HACE | Veredicto |
|---|---|---|---|
| `use_homeostasis` | REGULACION_HOMEOSTATICA | `temperature = 1 + (1 − energía)` **[COD]** `a4:427`, y nada más | **MAL FUNDADO** |
| `use_uncertainty` | ESTIMACION_DE_INCERTIDUMBRE | varianza entre 2 MLP entrenadas con **idénticos datos y targets** → `logits + 0.1·var` **[COD]** `a4:438`, `:728-731` | **MAL FUNDADO** |
| `use_planner` | PLANIFICACION_ANTICIPATORIA | suma energía predicha sobre 4 continuaciones **aleatorias**; ordena mal el 71% **[MED]** | **MAL FUNDADO** |
| `use_world_model` | MODELO_PREDICTIVO_DEL_MUNDO | `(s,a) → (s', e, done)`, target real, detached, acción como entrada **[COD]** `world_model.py:111` | **BIEN FUNDADO** |
| `use_temporal` | INTEGRACION_TEMPORAL | GRU sobre latentes, hidden detached **[COD]** `a4:403` | **BIEN FUNDADO** |
| `use_episodic_memory` | MEMORIA_EPISODICA | escribe cada paso; lee top-k por coseno **[COD]** `memory.py:65` | **BIEN FUNDADO como mecanismo** |
| `use_longterm_memory` | MEMORIA_PERSISTENTE | `M` con escritura gateada, recortada a ±10 | **PARCIAL** |
| `use_entropy_regularization` | PLASTICIDAD_EXPLORATORIA | término en la pérdida de política; **por defecto `False`** **[COD]** `a4:84`, `:716` | **NO ES UN MÓDULO** |
| `use_curiosity` (A5) | MOTIVACION_INTRINSECA | término sumado | **NO ES UN MÓDULO** |
| `use_factored_action` | — | reparación de canal | **no es un concepto** |

## Los tres mal fundados, en detalle

### `use_homeostasis` no implementa homeostasis

**[COD]** La única línea causal es `a4:427`: `temperature = 1 + exploration_bias`, donde
`exploration_bias = 1 − energía`. Todo lo demás —`a4:513, 514, 562, 563`— es traza.

Y lo decisivo: **`drive`, que es la magnitud central del concepto, no tiene ningún consumidor
causal.** `drive = max(0, umbral − energía)` se calcula y sólo se registra. Es decir, **el setpoint
no participa en la conducta**: la temperatura depende de la energía cruda, no de su distancia al
objetivo.

Un algoritmo que fuera homeostasis tendría que: defender un setpoint, producir acción correctiva
hacia él, y mantener una variable esencial dentro de límites. Este hace **una sola cosa**: subir la
aleatoriedad cuando baja la energía. Eso es un **calendario de exploración indexado por energía**,
y llamarlo homeostasis es un error de nombre que además contamina el pasaporte HOMEO-A1.

### `use_uncertainty` no estima incertidumbre

**[COD]** Ensemble de K cabezas, cada una `MSE(head(x), energy_delta)` sobre **el mismo input y el
mismo target**. Nada las decorrela: ni bootstrap, ni targets distintos, ni priors. Difieren **sólo
en inicialización**. Con `ensemble_size: 2` es la varianza de dos números.

Lo más que se puede decir —y acepto tu formulación— es **desacuerdo de ensemble no calibrado**. No
separa epistémico de aleatorio, no mide ganancia de información, no mide progreso de aprendizaje.
Que el comentario del código diga `(curiosity)` no es evidencia funcional.

### `use_planner` no planifica

**[MED]** Con el modelo entrenado, la acción correcta disponible el 82% de las veces: la elige el
28.7%. Su propio score la coloca **por debajo** de la alternativa el 71% de las veces. La causa está
medida: con la **misma** primera acción y sólo cambiando las continuaciones, el score se mueve en un
rango de **0.1523** frente a un margen decisivo de **0.019** — el ruido es **8×** la señal.

**[INF] No es anticipación: es promediar el azar de cuatro pasos que nunca se ejecutan.**

---

# Parte 2 · La unidad de inteligencia no es un flag

`agent_composition.CONCEPTS` ofrece once conceptos como interruptores conmensurables. **No lo son**,
y está medido:

```
use_planner      OFF → 0 CONSUME en 201 pasos, MUERE   [MED]
use_homeostasis  OFF → temperature pasa de 2−E a 1.0   [COD]
use_entropy_reg  OFF → es el valor POR DEFECTO         [COD]
```

Apagar el primero elimina **la única vía motora del organismo**. Apagar el segundo cambia **una
constante**. Apagar el tercero **no cambia nada porque ya estaba apagado**. Presentarlos en la misma
lista, con la misma forma y el mismo peso, afirma una equivalencia que el código desmiente.

**[INF] Y el daño no es cosmético**: la matriz de ablaciones, los pasaportes y `purity_check`
heredan esa equivalencia falsa. `purity_check` cuenta invocaciones de módulo, así que a un
**término** lo declara puro por construcción — y tres de los once son términos.

## Criterio propuesto: la unidad es la cadena, no el interruptor

**[HIP]** Un módulo cuenta como **unidad de capacidad** sólo si toda la cadena es demostrable, y
cada eslabón se mide por separado:

```
L1  la señal existe y es distinta de cero
L2  hay una transformación declarada que la consume
L3  el resultado entra en el estado que decide
L4  su ablación cambia la acción emitida
L5  ese cambio de acción cambia el resultado en el mundo
```

Aplicado a lo que tenemos:

| Módulo | L1 señal | L2 transform. | L3 en `s_t` | L4 cambia acción | L5 cambia resultado |
|---|---|---|---|---|---|
| `use_planner` | sí | sí | — | **sí [MED]** | **sí [MED]** 0 vs 210 |
| `use_world_model` | sí | sí | — | sí (vía planner) | no medido |
| `use_temporal` | sí | sí | **sí** | no medido | no medido |
| `use_episodic_memory` | sí | sí | **sí** | no medido | no medido |
| `use_longterm_memory` | sí | sí | **sí** | no medido | no medido |
| `use_uncertainty` | sí | sí | **no** | sí (+0.1 logits) | no medido |
| `use_homeostasis` | sí | sí | **no** | sí (temperatura) | no medido |
| `use_entropy_reg` | — | término | **no** | — | — |

**[MED] De once conceptos, exactamente UNO tiene la cadena completa demostrada: `use_planner`.** Y
es el que acabamos de medir que no hace lo que su nombre dice.

**[INF] Ésa es la respuesta a por qué cuatro días no produjeron una capacidad**: no teníamos
unidades de capacidad. Teníamos once interruptores de los cuales uno estaba conectado a la conducta,
tres eran términos invisibles al gate de pureza, y dos llevaban nombres de conceptos que sus
algoritmos no implementan.

---

# Qué se sigue de esto

**[INF]** Tres consecuencias, ninguna opcional:

1. **HOMEO-A1 y UNC-A1 no pueden certificarse tal como están.** No porque falte evidencia: porque
   el algoritmo bajo el pasaporte no es el concepto del pasaporte. Certificarlos sería certificar
   un nombre.
2. **La escalera E0–E9 asume unidades que no existen.** E1 «hambre» presupone que
   `use_homeostasis` es homeostasis. No lo es.
3. **El criterio L1–L5 es medible con el laboratorio que ya está construido** — gemelos de un solo
   nacimiento, intervención declarada, banco de sondas, probe congelado. No hace falta nada nuevo
   para aplicarlo a los once.
