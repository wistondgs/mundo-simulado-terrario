# La selección, contra el código real

**2026-09-18.** Clasificación de los trece mecanismos elegidos en: **reusable · sobrescrito ·
costura lista · por construir**. Cada fila con fichero y línea.

---

## Tres hallazgos que cambian el orden de implementación

### 1 · La trampa de pureza alcanza a tres de tus elecciones a la vez

`purity_check` decide si una capacidad es ablacionable contando **invocaciones de módulo**. Un
término sumado a una recompensa o a una pérdida no mueve ningún conteo. El pasaporte ya lo nombra
dos veces, y no como sospecha sino como hecho:

> *«Es el único candidato que NO es un módulo sino un término. Su ablación no mueve ningún conteo de
> invocación, así que `purity_check` la declara pura por construcción: no puede detectar impureza de
> pérdida.»* — sobre `use_entropy_regularization`, [capability_passport.py:382](terrario/lab/capability_passport.py:382)

> *«Trampa de pureza: si se implementa como término sumado a los logits en vez de como módulo,
> `purity_check` la declarará PURE por construcción y el gate pasará en vacío.»* — sobre
> `use_curiosity`, [capability_passport.py:552](terrario/lab/capability_passport.py:552)

**B2 (recompensa interoceptiva) y B5 (metacognición) son términos, igual que curiosidad.** Si se
implementan como tales, el gate que los certificaría **pasa sin probar nada**. Tres de los
mecanismos que elegiste comparten el mismo punto ciego de medición, y hay que resolverlo **antes**
de escribirlos, no después.

### 2 · Tres mecanismos se pelean por el mismo órgano

`last_prediction_error` alimentaría a la vez a curiosidad, a UNC-A1 y a B5. El pasaporte lo avisa:

> *«UNC-A1 ya consume señal con forma de error de predicción y ya posee el eje `novelty`. La
> superficie de intervención se solapa y hay que separarla antes de atribuir nada.»*

En tu circuito, INCERTIDUMBRE, CURIOSIDAD y METACOGNICIÓN son tres cajas distintas. En el código
son una señal sola. Separarlas es trabajo de diseño previo, no una consecuencia de implementarlas.

### 3 · «Tener una necesidad propia» es justamente lo que está roto

Es la primera fila de tu tabla y la única de la base que no funciona. Ver abajo.

---

## Fila por fila

### Base necesaria

| Mecanismo | Estado | Evidencia |
|---|---|---|
| **`use_homeostasis`** | **SOBRESCRITO** | `HomeostaticState.update(energy_delta)` acumula energía interna ([homeostasis.py:49](terrario/agent/homeostasis.py:49)) y `learn` la llama ([a4:577](terrario/agent/agents/a4_advanced.py:577)) — pero `perceive` la **pisa por asignación directa**: `self.homeostasis._energy = observation.agent_energy` ([a4:352](terrario/agent/agents/a4_advanced.py:352)). El estado «interno» no es interno: es una copia de la lectura del mundo. |
| **B2 · interocepción** | **COSTURA LISTA, INERTE** | `_policy_reward` devuelve `float(consequence.energy_delta)` ([a4:569](terrario/agent/agents/a4_advanced.py:569)) y su docstring dice que existe para esto. Y tu `e_t` **ya está calculado**: `drive = max(0, threshold − energy)` ([homeostasis.py:39](terrario/agent/homeostasis.py:39)). `r_int = drive_t − drive_{t+1}` es computable hoy sin código nuevo. |
| **`use_online_learning`** | **REUSABLE** | Único en **READY_FOR_CERTIFICATION**. |
| **`use_episodic_memory`** | **REUSABLE**, sin cita | NO_CORPUS_PROVENANCE. |
| **`use_longterm_memory`** | **REUSABLE**, sin cita | `M` se escribe **fuera del optimizador** ([memory.py:239](terrario/agent/memory.py:239)): sigue cambiando con `learning_commit_enabled=False`. |
| **`use_temporal`** | **REUSABLE**, sin cita | `_hidden` va detached ([a4:403](terrario/agent/agents/a4_advanced.py:403)). |
| **`use_world_model`** | **ENREDADO** | MEDIDO: `use_world_model=False` apaga el planner entero (40 invocaciones → 0) y desvía conducta a `policy_head` (97 → 120). **WM y planner no son dos cajas separables hoy**, aunque tu circuito los dibuje en serie. |
| **`use_uncertainty`** | **REUSABLE**, colisiona | ver hallazgo 2. |
| **`use_planner`** | **REUSABLE**, sin mundo | NO_CORPUS_PROVENANCE, sin mundo que lo exija, y atado a WM. |

### Segundo orden

| Mecanismo | Estado | Evidencia |
|---|---|---|
| **B5 · metacognición** | **COSTURA LISTA, INERTE** | `last_prediction_error` se escribe en `learn` ([a4:607](terrario/agent/agents/a4_advanced.py:607)) y lo leen **sólo** `get_trace` ([a4:787](terrario/agent/agents/a4_advanced.py:787)) y el observador ([controller.py:226](terrario/experiment/controller.py:226)). El pasaporte: *«El órgano existe y está cableado a la libreta en vez de a la conducta; esta capacidad es cerrar ese lazo, no añadir uno nuevo.»* |
| **B1 · ultraestabilidad** | **POR CONSTRUIR** — pero el endpoint ya está nombrado | Cero implementación en todo `terrario/agent/`. Lo notable: `viability_recovery_metric` ya declara qué **no** mide — *«whether the organism reorganised its own parameters (Ashby's ultrastability proper) — only that the essential variable returned»* ([viability_recovery_metric.py:126](terrario/lab/viability_recovery_metric.py:126)). El instrumento sabe de la distinción y se abstiene. Es el sitio exacto donde entraría el endpoint de B1. |

### Motivación anticipatoria

| Mecanismo | Estado | Evidencia |
|---|---|---|
| **B3 · alostasis** | **COSTURA PARCIAL** | Tu «revisar el objetivo por adelantado» actúa sobre `_threshold`, y `_threshold` es lo **único** de `HomeostaticState` que `perceive` **no** sobrescribe: se fija en construcción ([homeostasis.py:22](terrario/agent/homeostasis.py:22)) desde `config["homeostasis_threshold"]`. Convertirlo de constante a variable de estado es el cambio mínimo. **Pero depende de reparar el sobrescrito**: no se puede revisar el setpoint de un estado que viene copiado de fuera cada paso. |

### Exploración

| Mecanismo | Estado | Evidencia |
|---|---|---|
| **`use_curiosity`** | **EN ROJO + impuro + colisiona** | Rompe tres tests hoy (`KeyError: 'use_curiosity'`, [agent_composition.py:176](terrario/lab/agent_composition.py:176)): el catálogo la ofrece y `DEFAULT_CONFIG` de A4 no la tiene. Confusores declarados y **no** resueltos: CLM-0126 (predecir directo mantiene el error alto; la dinámica inversa que lo baja, A4 no la implementa), solape con UNC, y la trampa de pureza. |

### Transversal

| Mecanismo | Estado | Evidencia |
|---|---|---|
| **Linaje del conocimiento** | **POR CONSTRUIR**, con ancla | No existe: cero `provenance` en todo `terrario/agent/`. Lo que sí hay es la **huella**: `_adaptive_state_hash` ([adaptation.py:198](terrario/experiment/adaptation.py:198)) hashea parámetros + buffer episódico + `M`, «excluyendo estado recurrente ordinario». Dice **que** algo cambió; no **qué** ni **por qué**. Tu K17 es esa huella con la cadena causal colgada. Y tenés razón en separarlo de `lineage_root`/`generation` de `OpportunityLifecycle`: ése es linaje de objetos del mundo. |

---

## Tu definición de «descubrimiento» ya tiene instrumento a medias

Exigís que X produzca **modificación persistente con efecto causal posterior**. Eso es medible hoy
en dos mitades, y la segunda falta:

- **Persistencia** — `_adaptive_state_hash` la detecta. ✅
- **Efecto causal posterior** — nada ata un cambio de estado a una decisión futura. ❌

Y hay un obstáculo medido que le pega justo: `learning_commit_enabled` **no congela** el estado
aprendido. `M`, el buffer episódico y `_energy_baseline` siguen moviéndose en los dos brazos. Así
que «modificación persistente» todavía no tiene un control de «sin modificación» contra el que
contrastarse.

---

## Orden que se deduce de lo anterior

No es una propuesta de prioridades: es el orden en que las dependencias lo permiten.

1. **Reparar el sobrescrito de homeostasis.** Sin esto, B2 mide sobre un estado que no es del
   organismo y B3 no tiene setpoint que revisar. Es la raíz de la rama entera.
2. **Resolver la trampa de pureza para términos.** Antes de escribir B2, B5 o curiosidad: si el
   gate no puede verlos, certificarlos es ceremonia.
3. **Separar el órgano de error de predicción** entre UNC, CURIO y B5. Trabajo de diseño, no de
   código.
4. **B2**, que es conectar `drive` a `_policy_reward` — dos piezas que ya existen.
5. **B5**, cerrando el lazo que el pasaporte describe.
6. **B1**, extendiendo `viability_recovery_metric` con lo que hoy declara no medir.
7. **Linaje**, colgando la cadena causal de `_adaptive_state_hash`.

`use_curiosity` no puede entrar hasta 2, 3 y sus tres tests rojos.
