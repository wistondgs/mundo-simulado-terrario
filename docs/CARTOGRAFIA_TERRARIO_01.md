# Cartografía de Terrario

HEAD `d1c7e4f` · 2026-09-17 · 149 ficheros Python, 30 703 líneas en `terrario/`

**Qué es este documento.** Respuestas verificables a las 710 preguntas del interrogatorio de
cartografía. Cada afirmación se apoya en lectura de código con `fichero:línea` o en una medición
ejecutada, no en el nombre de los módulos. Donde una respuesta no pudo verificarse se dice
explícitamente en vez de rellenarse.

**Convención.** `→` indica llamada o dependencia. Los números entre corchetes son las preguntas
originales.

---

# I · Topología real del repositorio

## 1 · Árbol lógico por dominio funcional

Extraído con AST sobre los imports reales, no por carpetas.

```
core/        (6 ficheros)   tipos primitivos. NADA sale de aquí.
  types.py            Action, ActionType, Direction, Position, Observation,
                      Consequence, ObjectSpec, AgentState, WorldState
  action_contract.py  Contrato de Acción v2 (455 líneas)
  contracts.py        Transition
  rng.py              RNGManager
  events.py           LearningEvent
  ids.py

world/       (8)        física. → core
  state.py            WorldStateManager · AUTORIDAD del estado
  physics.py          PhysicsEngine · MOVE/PUSH/CONSUME/INSPECT/NOOP
  rules.py            RuleEngine · evalúa y aplica efectos
  scheduler.py        ChangeScheduler · inversiones programadas
  opportunities.py    OpportunityLifecycle · despawn/cooldown/respawn
  transition.py       AUTORIDAD COMPARTIDA · build_world_state, find_target,
                      build_episode_components, SEMANTICS_VERSION
  scenario.py
  observation.py

agent/       (18)       el ser. → core ÚNICAMENTE
  base.py             AgentInterface
  encoder.py          PerceptualEncoder (Conv×3 → Linear → LayerNorm)
  temporal.py         TemporalCore abstracto · GRUCore · SSMCore
  memory.py           EpisodicMemory (no-nn) · LongTermMemory (nn.Module)
  world_model.py      WorldModel · 3 cabezas
  uncertainty.py      UncertaintyEstimator · ensemble K=5
  policy.py           PolicyHead · Planner (random shooting)
  homeostasis.py      HomeostaticState (no-nn)
  learner.py          OnlineLearner · un único Adam
  scientific.py       proyección de estado para el observador
  agents/             A0 A1 A2 A3 A4 + factoría

observer/    (7)        traza. → core
  trace.py  storage.py  logger.py  checkpoints.py  probes.py

experiment/  (10)       ejecución científica. → world, core, observer, agent
  controller.py       ExperimentController
  adaptation.py       protocolo de adaptación (628 líneas)
  runner.py  campaign.py  metrics.py  specs.py  statistics.py  hypothesis.py

lab/         (99)       laboratorio. → core, world, experiment, agent, observer
  sandbox_runtime.py  SandboxService
  api.py              superficie HTTP
  run_measures.py     las mallas de medición
  agent_composition.py  catálogo de conceptos y validación
  instrument_registry.py / instrument_calibration.py / measurement_status.py
  snapshot_bank.py / capability_exam.py / selector_isolation.py
  world_contracts.py / world_authoring.py / world_registry.py
  preregistration/ · persistence/ · execution/ · crossgraph/ ·
  referencegraph/ · hypergraph/ · worldstream/ · theory/
```

## 2 · Núcleo del runtime

`core`, `world`, `agent`. Son los únicos paquetes que un timestep necesita.

## 3 · Exclusivos del laboratorio

`lab` (99 de 149 ficheros Python — el 66 % del repositorio) y `experiment`.

## 4 · Exclusivos de UI/observación

`observer` (traza, almacenamiento, checkpoints, sondas) y, dentro de `lab`,
`worldstream/` (SSE) y `api.py`.

## 5 · Compartidos entre runtime y laboratorio

`core` (19 aristas desde lab, 17 desde agent) y `world` (14 aristas desde lab).

## 6 · Entrypoints ejecutables

Con bloque `__main__`:

| Entrypoint | Qué es |
|---|---|
| `terrario/lab/api.py` | superficie HTTP del laboratorio |
| `terrario/lab/preregistration/__main__.py` | CLI de preregistro |
| `terrario/lab/instrument_registry.py` | informe del registro de instrumentos |
| `terrario/lab/instrument_calibration.py` | informe de controles de falsación |
| 30 scripts en `scripts/` | campañas, demostraciones, experimentos |

## 7 · Quién usa `SandboxService`

`lab/api.py`, `lab/worldstream/service.py`, `lab/worldstream/api.py`, y los scripts
`screen_concepts.py`, `experiment_t0_vs_t1.py`, `experiment_closed_loop_t.py`,
`experiment_capability_acquisition.py`.

## 8 · Quién usa `ExperimentController`

`experiment/runner.py`, `experiment/specs.py`, `experiment/adaptation.py`, `lab/causal.py`,
`lab/execution/runtime.py`, `lab/characterization.py`.

## 9 · Ejecución científica preregistrada

`lab/execution/runtime.py` → `ExperimentController`. Es la única ruta que llama a
`RNGManager.set_global_determinism` **y** atraviesa el servicio de preregistro.

## 10 · World2D Live

`lab/worldstream/service.py` + `lab/worldstream/api.py` → `SandboxService`. **La interfaz visual
corre sobre el banco, no sobre la ejecución científica.**

## 11 · Replay

No hay entrypoint de replay dedicado. `observer/trace.py` y `observer/storage.py` guardan; la
reconstrucción la hacen consumidores concretos (`lab/models.thaw`). *Verificación pendiente de un
barrido específico.*

## 12 · Screening y ablación

`scripts/screen_concepts.py` y `scripts/ablation_study.py`, ambos sobre `SandboxService`.

## 13 · Rutas que crean agentes o mundos fuera de esos entrypoints — **sí, varias**

**Crean agentes** (`create_agent`): `experiment/controller.py`, `experiment/adaptation.py`,
`lab/sandbox_runtime.py`, `lab/agent_inspector.py`, `lab/causal.py`, `lab/execution/runtime.py`,
y los scripts `screen_concepts`, `experiment_one_step_twins`, `experiment_capability_acquisition`.

**Crean mundos** (`build_world_state` / `WorldStateManager(...)`): `experiment/controller.py`,
`experiment/adaptation.py`, `lab/sandbox_runtime.py`, `lab/world_authoring.py`,
`lab/d2_operational.py`, `lab/causal.py`, `lab/execution/runtime.py`, **`lab/capability_exam.py`**,
**`lab/snapshot_bank.py`**, `scripts/simulate_d4_signal.py`, `scripts/verify_reproducibility.py`.

Los dos últimos módulos de `lab` son míos, de esta noche: construyen estados sin atravesar ningún
runtime, deliberadamente — son bancos exógenos, no simulaciones.

## 14-15 · Ver 13.

## 16 · Quién puede avanzar un timestep

Sólo dos funciones lo hacen de principio a fin:
`ExperimentController.run_episode` ([controller.py:196](terrario/experiment/controller.py:196)) y
`SandboxService._step_runtime` ([sandbox_runtime.py:142](terrario/lab/sandbox_runtime.py:142)).
`world.advance_time()` lo invoca `PhysicsEngine.step` al final ([physics.py:83](terrario/world/physics.py:83)).

## 17 · Cuántos loops de simulación existen realmente

**Dos.** Ver §XXI para la diferencia línea a línea.

## 18 · Qué comparten

`WorldStateManager`, `PhysicsEngine`, `RuleEngine`, `ChangeScheduler`, `create_agent`,
`Transition`, `get_observation`, `apply_step_energy_cost`.

## 19 · Qué duplican

- ~~**`_find_target`**: `controller.py:317` y `sandbox_runtime.py:294`.~~ **RESUELTO**
  (2026-09-17). Una sola implementación en
  [world/transition.py](terrario/world/transition.py); los dos sitios delegan y el método del
  controller se conserva porque `causal.py` lo llama a través de paquetes. Eran semánticamente
  idénticos, que es la única razón por la que el traslado es demostrablemente neutro — probado con
  la fixture de conducta.
- ~~La construcción del mundo, copiada en cuatro sitios~~ **RESUELTO** (2026-09-17):
  `build_episode_components` en `world/transition.py`. Los fallbacks habían derivado —
  `duration → config.max_steps_per_episode` en un sitio y el literal `500` en otro — y ahora el
  fallback es un parámetro, porque los dos llamadores difieren legítimamente en orquestación.
  `build_world_state` se movió de `experiment/` a `world/`, con re-export para los treinta
  ficheros que lo importan desde allí.
- La construcción del `Transition` y el cálculo de `energy_delta`. **Pendiente.**
- La secuencia perceive → decide → physics → rules → cost. **Pendiente** — es `run_step`.

## 20 · Divergencias semánticas — ver §XXI.

---

# II · Autoridad sobre el estado del mundo

## 21 · El objeto autoritativo

`WorldState` ([core/types.py](terrario/core/types.py)), un dataclass con `grid_width`,
`grid_height`, `time`, `objects: dict[int, ObjectSpec]`, `agents: dict[int, AgentState]`,
`rules_version`, `occupancy: np.ndarray`. Lo custodia `WorldStateManager`
([world/state.py](terrario/world/state.py)).

## 22-23 · Quién puede mutarlo · ¿una autoridad o varias?

La API declarada de mutación es cerrada y son **doce** métodos:

```
set_time · advance_time · set_rules_version · move_agent · move_object
remove_object · add_object · set_agent_energy · set_agent_alive
apply_step_energy_cost · set_object_channels · restore
```

**Pero `_mutable_state()` devuelve el dataclass crudo y se usa en 38 sitios**:

| Fichero | Usos |
|---|---|
| `world/physics.py` | 12 |
| `experiment/controller.py` | 6 |
| `world/opportunities.py` | 5 |
| `lab/sandbox_runtime.py` | 5 |
| `lab/causal.py` | 4 |
| `world/rules.py` | 3 |
| `world/scheduler.py` · `lab/worldstream/service.py` · `experiment/adaptation.py` | 1 c/u |

**Veredicto: la autoridad es nominal, no estructural.** Cualquiera con el manager muta por debajo
de la API. [39] `lab/worldstream/service.py` — un servicio de *observación* — está en la lista.

## 24 · Secuencia exacta de `state_t → state_t+1`

Ver §XXI, donde las dos secuencias están enfrentadas paso a paso.

## 25-31 · Dónde ocurre cada cosa

| | Dónde |
|---|---|
| [25] acción aplicada primero | `PhysicsEngine.step` → `_handle_move/_handle_push/_handle_consume/_handle_inspect` |
| [26] objetos actualizados | `RuleEngine.apply_effects` (destrucción), `physics._handle_push` (movimiento) |
| [27] coste metabólico | `WorldStateManager.apply_step_energy_cost` ([state.py:164](terrario/world/state.py:164)), **después** de las reglas en ambos loops |
| [28] posición del agente | `WorldStateManager.move_agent`, llamado desde `physics._handle_move` y `_handle_push` |
| [29] consecuencias materializadas | `RuleEngine.apply_effects`; `physics` sólo marca `consume_pending_obj_<id>` |
| [30] timestep incrementado | `world.advance_time()` al final de `PhysicsEngine.step` ([physics.py:83](terrario/world/physics.py:83)) |
| [31] eventos generados | `physics` los devuelve como strings; `_classify_events` los separa en agente/observador |

## 32-33 · Antes y después de la acción

**Antes:** `get_observation` (la que ve el agente), `scheduler.check` (inversiones de regla),
y en el controller `lifecycle.advance` (respawns).
**Después:** `rules.evaluate/apply_effects`, `apply_step_energy_cost`, la segunda
`get_observation`, y en el controller `lifecycle.consume`.

## 34-36 · Pre-state y post-state en la traza — **hay un campo así**

[36] **Sí.** `SandboxTraceStep.observer_world` contiene `world.serialize()` tomado **después** de
la transición, mientras que `agent_action` es la acción tomada **contra el mundo anterior**. El
nombre no lo dice. Fue la causa de un defecto real: emparejar la acción de un paso con el mundo de
ese mismo paso puntuaba todo consumo exitoso como fallo, porque el objeto comido ya no estaba. La
reparación vive en `run_measures._cadena`, que empareja `rows[i].observer_world` con
`rows[i+1].agent_action` ([run_measures.py](terrario/lab/run_measures.py)).

## 37 · Campos reconstruidos en vez de registrados

Varios, y es una fuente de fragilidad sistemática:

- `energy_delta` se **reconstruye** restando energías de pasos consecutivos en
  `run_measures._eating`, `_energy_ledger` y en `experiment_capability_acquisition.stream_from`.
  No se registra por paso en la traza del banco.
- La línea base metabólica se reconstruye como mediana de pasos ociosos cuando el escenario no
  declara coste.
- Las oportunidades y su adyacencia se reconstruyen desde `observer_world` en `_cadena`.

Contraste: `action_contract` (v2) **sí se registra durante la transición**, con intención,
resolución y ejecución separadas.

## 38 · Mutaciones fuera de la transición principal

`OpportunityLifecycle.consume` y `.advance` (sólo controller), `RuleEngine.apply_effects`,
`ChangeScheduler.check` (cambia `rules_version`), y cualquiera de los 38 usos de `_mutable_state`.

## 39 · Mutación desde observación, métricas o UI

**Sí, desde la UI de observación.**
`lab/worldstream/service.py::_provenance_sidecar` llama a `_mutable_state()` para construir el
mapa forense de celdas a `object_id`. En la implementación actual lo recorre sin escribir, por lo
que las pruebas de pasividad no muestran una trayectoria alterada; pero rompe la frontera
estructural: una capa clasificada como observadora obtiene el dataclass mutable autoritativo.
Las métricas auditadas leen serializaciones/trazas, no mutan el mundo directamente.

## 40 · Pruebas de que la observación científica no altera la trayectoria

`tests/test_observer_passivity_campaign.py` y `tests/test_agent_observer_view_separation.py`.
El sellado lo define [world_contracts.py:12](terrario/lab/world_contracts.py:12):

```python
AGENT_FIELDS         = {"channels", "mask", "agent_energy", "time_fraction"}
OBSERVER_ONLY_FIELDS = {"world", "world_truth", "objects", "agents", "occupancy",
                        "rules", "rules_version", "causal_property", "energy_value"}
```

con `LeakageError` como excepción tipada, más una segunda lista en
[planning_trace_metric.py:21](terrario/lab/planning_trace_metric.py:21):
`optimal_action`, `future_cost`, `oracle_score`, `target_solution`,
`planning_horizon_solution`, `world_truth`.

---

# III · WorldDefinition y física declarada

## 41 · Representación canónica

`WorldDefinition` en [world_contracts.py](terrario/lab/world_contracts.py), dataclass congelado con
`SCHEMA_VERSION = "terrario.lab.world/v1"`, hasheado por `scientific_hash` sobre
`canonical_json` (claves ordenadas, separadores fijos). Junto a él: `ScenarioDefinition`,
`ConfigurationState`, `DifficultyProfile`, `ObservationContract`, `ActionContract`,
`WorldRuleDefinition`, `WorldProvenance`.

## 42 · Propiedades que un escenario puede declarar hoy

De `scenarios/d4_temporal_variety.yaml`, que es el más completo:

```yaml
name · observer_phases · grid_size · duration · max_energy · step_energy_cost
expose_time_fraction · seed · view_radius · num_channels · agent_start{pos,energy}
procedural_layout{placement_margin, class_templates{clase:{count,channels}}}
opportunity_lifecycle{cooldown_steps, minimum_agent_distance,
                      placement_margin, recent_position_exclusion}
objects[] · rules{rules[{id,condition{object_channel{index,min,max},action},
                        effect{energy_delta,destroy_object,transform_channels}}]}
changes[{at_step, rules}]
```

## 43-44 · Obligatorias y con default implícito

**Obligatorias** en el banco: `duration`, `max_energy`, `step_energy_cost`,
`expose_time_fraction`. `SandboxService` levanta `WORLD_PHYSICS_NOT_DECLARED` si falta alguna
([sandbox_runtime.py:108](terrario/lab/sandbox_runtime.py:108)) — una reparación previa: antes el
banco inventaba la física por defecto.

**Con default implícito**: `view_radius` → 2, `num_channels` → 4,
`agent_start` → `{pos:[5,5], energy:100.0}` ([controller.py:106](terrario/experiment/controller.py:106)),
`movable` → True, `energy_value` → 0.0, `placement_margin` → 1,
`cooldown_steps` → `[3,8]`, `minimum_agent_distance` → 2, `recent_position_exclusion` → 2.

## 45-46 · Dónde se validan y se compilan

`lab/world_authoring.py::_runtime_economy` fija los defaults de economía **una sola vez, en la
frontera del YAML**. `lab/world_registry.py::adapt_legacy_scenario` proyecta el YAML legado a
`WorldDefinition`/`ScenarioDefinition`. `lab/world_contracts.py` valida contratos.
`experiment/controller.py::materialize_scenario` materializa el `procedural_layout` con
`np.random.default_rng(world_seed)`.

## 47-50 · Quién consume qué

| Propiedad | Ambos | Sólo Controller | Sólo Sandbox | **Nadie** |
|---|---|---|---|---|
| grid_size, duration, max_energy, step_energy_cost, view_radius, num_channels, agent_start, rules, changes, procedural_layout | ✓ | | | |
| `opportunity_lifecycle` | | **✓** | | |
| `observer_phases` | | ✓ (fases y ventana forense) | | |
| `expose_time_fraction` | ✓ | | | |
| `selector_type` / `selector_value` de la acción | | | **✓** (AC2) | |

[50] **Sí: `opportunity_lifecycle` es declarado y NO consumido por el banco** — ver §IV y §XXI.

## 51 · Física ejecutada que no está en WorldDefinition

- El **orden** de aplicación (physics → rules → coste) no está declarado en ningún sitio: vive en
  el cuerpo de los dos loops.
- La **desaparición del objeto** la decide `effect.destroy_object`, pero la muerte del agente la
  decide `apply_effects` con el umbral `new_energy <= 0.0`, no declarado en el escenario
  ([rules.py:226](terrario/world/rules.py:226)).
- El **desplazamiento por PUSH** (el agente sigue al objeto) es física de `_handle_push`, no
  declarada.

## 52 · Componentes que interpretan configuración cruda

`PhysicsEngine`, `RuleEngine.load_rules`, `ChangeScheduler`, `OpportunityLifecycle` y ambos
loops leen dicts de escenario directamente. No reciben una representación compilada.

## 53-54 · ¿Existe `WorldDefinition → ExecutableWorldSemantics`?

**Parcialmente, desde el 2026-09-17.** `WorldDefinition` sigue siendo una representación
descriptiva y hasheable que el runtime nunca consume. Lo que cambió es que la **construcción** del
episodio ya no se interpreta por separado: `build_episode_components`
([world/transition.py](terrario/world/transition.py)) es la única que arma mundo, reglas, calendario
y física, y las cuatro copias delegan en ella. `SEMANTICS_VERSION` declara bajo qué semántica se
produjo un resultado.

Lo que **sigue interpretándose por separado** es la secuencia del paso — `run_step` no existe aún —
y ésa es la raíz que queda de §XXI.

## 55-59 · Divergencias declarado ↔ ejecutado

| | Controller | Sandbox |
|---|---|---|
| [59] respawn / cooldown | **sí** (`OpportunityLifecycle`) | **no** — mundo estrictamente agotable |
| [57] orden de reglas | physics → `_find_target` → rules | `_find_target` → physics → rules |
| [58] terminación | `alive` comprobado al inicio del paso → `break` | `terminated` calculado al final |
| [56] determinismo global | `RNGManager.set_global_determinism` | **no lo llama** |
| aprendizaje | `learning_enabled` opcional | siempre activo |
| contrato de acción v2 | inerte | activo |
| semilla de física | `seed + step` | `world_seed + step` |

Medición: D4T sobre el banco, 250 pasos → **32 objetos al inicio, 29 al final, cero respawns**.

## 60 · Fuente de verdad ante discrepancia

Hoy, **el cuerpo del loop que se esté ejecutando**. No hay árbitro. El YAML describe, la
documentación narra y el runtime decide. Ésa es la deuda P0.5.

---

# IV · OpportunityLifecycle y dinámica de objetos

Fichero: [world/opportunities.py](terrario/world/opportunities.py), 246 líneas.

## 61 · Responsabilidades

Registrar las oportunidades iniciales (`register_initial`), despachar el despawn cuando una es
consumida (`consume`), programar su reaparición con un cooldown, materializar los respawns
vencidos (`advance`), elegir la posición (`_spawn_position`) y exportar geometría para el
observador (`geometry`).

## 62 · Estado interno

`_next_object_id` (arranca en 10 000), `_next_opportunity_id`, `_pending[]`,
`_recent_positions[]`, `events[]`, `records{}`, y `_lineage{}` (añadido hoy).

## 63-64 · Qué es una `opportunity`

**Una posibilidad de interacción con identidad persistente a través de reapariciones.** No es el
objeto físico —cada respawn crea un `ObjectSpec` nuevo con `object_id` nuevo— ni una aparición
aislada —el linaje las une—. Es el tercer concepto.

## 65-66 · Linaje y generación

`_lineage: dict[opportunity_id] → (lineage_root, generation)`. Las iniciales tienen
`(sí mismas, 0)`. Al consumir, el respawn hereda `(root, generation+1)`.

## 67 · Qué ocurre al consumir

1. `RuleEngine.apply_effects` destruye el objeto (`destroy_object: true`).
2. El controller detecta que `target_before.object_id` ya no está y llama a `lifecycle.consume`.
3. Se sortea el cooldown con `_stream(seed, "cooldown", root, generation+1)`.
4. Se encola en `_pending` con `due_step = step + cooldown`.
5. Se emite un `OpportunityEvent("despawn", ...)` y se registra la posición en `_recent_positions`.

## 68-69 · Quién decide cooldown y lugar

Cooldown: `_stream(seed,"cooldown",root,gen)` sobre `cooldown_steps` (3–8 en D4T).
Lugar: `_spawn_position`, que construye un conjunto de candidatos —celdas libres, a distancia
mínima del agente, fuera de `_recent_positions`— y sortea con `_stream(seed,"placement",root,gen)`.

## 70 · Cuándo conserva identidad

**El `object_id` nunca se conserva** (cada respawn toma uno nuevo desde 10 000). El
`opportunity_id` tampoco. Lo que se conserva es el **linaje**: `(root, generation)`.

## 71-73 · Las cuatro identidades

| Identidad | Qué es | ¿La ve el agente? |
|---|---|---|
| `entity_id` / `object_id` | clave en `WorldState.objects` | **no** — `OBSERVER_ONLY` |
| `opportunity_id` | etiqueta de registro del ciclo | **no** |
| `lineage_root` | identidad a través de reapariciones | **no** |
| `generation` | ordinal dentro del linaje | **no** |
| `ObservationHandle` (`entity_6f21`) | nombre opaco por fotograma | **tampoco** — ver abajo |

[72] **Ninguna es visible para el agente.** Bajo T1 el organismo emite un **índice de ranura**
(0..15), nunca un identificador. El handle existe para la procedencia.

## 74-76 · Qué debe ir a checkpoint, replay y hash

Debería ir: `_pending`, `_lineage`, `_next_object_id`, `_next_opportunity_id`,
`_recent_positions`, `records`. **Verificación pendiente**: no he comprobado que
`observer/checkpoints.py` incluya ninguno — ver §XX.

## 77-78 · Colisión y orden total

`RuleEngine.evaluate` devuelve **todos** los efectos que casan y `apply_effects` los aplica en
orden de lista; `destroy_object` está guardado por `if target_object_id in objects`, así que una
segunda destrucción del mismo objeto es un no-op silencioso. El orden total dentro del paso del
controller es: `scheduler.check` → `lifecycle.advance` → `physics.step` → `rules.apply_effects`
→ `lifecycle.consume` → `apply_step_energy_cost`. **No hay orden declarado**; es el orden del
código.

## 79 · Pruebas sobre múltiples generaciones

`tests/test_exogenous_rng_coupling.py` — nueve, incluidas
`test_each_reappearance_of_a_lineage_draws_its_own_variate` y
`test_the_generation_ordinal_is_local_to_its_lineage`.

## 80 · Lógica parecida fuera del lifecycle

`ChangeScheduler` (calendario de eventos con estado `fired`) y
`experiment/adaptation.py` (fases ACQUISITION/CAUSAL_CHANGE/RECOVERY).

---

# V · RNG, determinismo y causalidad

## 81-85 · Fuentes de aleatoriedad

| Librería | Dónde |
|---|---|
| `numpy` | `core/rng.py`, `experiment/statistics.py`, `controller.materialize_scenario`, `world/opportunities.py`, `observer/checkpoints.py` |
| `random` (stdlib) | `core/rng.py`, `lab/snapshot_bank.py`, `lab/capability_exam.py`, `lab/instrument_calibration.py` |
| `torch` | `core/rng.py`, `agent/policy.py`, y **el RNG global de torch** en la construcción de todo `nn.Module` |

[85] No hay otras librerías con RNG.

## 86-90 · Semillas

- **Mundo**: `world_seed` en el escenario → `materialize_scenario` y `OpportunityLifecycle`.
- **Agente**: `agent_seed` → `torch.Generator` pasado a `create_agent`, usado **sólo para muestreo**.
- **Pesos**: salen del **RNG global de torch**. `memory.py:156` hace `torch.randn(...)` sin
  generator; lo mismo toda capa `nn.Linear`/`nn.Conv2d`.

[90] **Hoy no se garantiza estructuralmente.** Dos agentes con la misma `agent_seed` construidos
en secuencia en un proceso reciben pesos **distintos**, porque el RNG global avanza con cada
construcción. Los bancos lo compensan llamando `torch.manual_seed(seed)` **antes** de
`create_agent`. `experiment_capability_acquisition.py` va más lejos: **verifica** que los cuatro
gemelos comparten `initial_parameters_hash` y aborta si no.

## 91-92 · Claves derivadas vs. orden de llamada

**Derivadas**: `OpportunityLifecycle` → `blake2b(seed:kind:root:generation)`;
`materialize_scenario` → `default_rng(world_seed)`; física → `RNGManager(seed+step)` fresco por paso.

[92] **Todavía dependen del orden**: el `torch.Generator` del agente (secuencial por diseño), el
RNG global de torch en construcción de módulos, y `_recent_positions` del lifecycle (historia, no
sorteo).

## 93-95 · Separación semántica de streams

`RNGManager` deriva `world_seed`, `agent_seed`, `observer_seed` de la master, y mantiene
`_world_rng`/`_world_np`, `_agent_rng`/`_agent_np`/`_agent_torch`.
[94] **Sí**: cooldown y posición usan `kind` distinto en la clave blake2b — probado en
`test_placement_and_cooldown_of_one_reappearance_are_separate_streams`.
[95] Layout y perturbaciones comparten `world_seed`; la política usa el generator del agente.

## 96 · ¿Inventario completo de sorteos?

**No existe.** Esta tabla es lo más cercano, y la construí por barrido, no por un registro que el
sistema mantenga.

## 97 · ¿Puede una acción cambiar cuántos sorteos hace el mundo?

**Hoy no** — tras la reparación de linaje×generación. **Antes sí**: el cooldown y la posición se
sembraban con `len(self.events)`, el número de oportunidades consumidas.

Pero hay un matiz [97 bis]: **dentro del agente sí**. `policy.py:68` consume un sorteo que
descarta, `_ = torch.rand(probs.shape, generator=generator)`, cuyo tamaño depende de la forma del
espacio de acción. Un A4 plano consume 25+1 variables por decisión; uno factorizado, 1+1.

## 98-99 · ¿Consumen RNG métricas, observadores o UI?

`run_measures`, `instrument_registry` y `measurement_status` **no** consumen RNG.
`instrument_calibration` y `snapshot_bank` sí, con semilla propia y explícita.
`experiment/statistics.py` usa `default_rng(seed)` para remuestreo. La UI (`worldstream`) no.

## 100 · ¿Puede el replay regenerar las mismas variables latentes?

Para el mundo, **sí** desde la reparación: la clave es `(seed, kind, root, generation)` y no
depende de la trayectoria. Para el agente, **sólo si se restaura el estado del generator**, y ver
§XX sobre si el checkpoint lo incluye.

## 101-102 · Qué significa "reproducible por semilla"

`scripts/verify_reproducibility.py` y `tests/test_reproducibility.py` exigen **identidad de
trayectoria** (mismo `state_hash` paso a paso), no identidad bit a bit de pesos ni equivalencia
estadística.

## 103 · Qué detectaría un RNG global accidental

`RNGManager.set_global_determinism` + comparación de trayectorias en `test_reproducibility.py`.
**Pero el banco no llama a `set_global_determinism`**, así que esa detección no cubre la ruta por
la que corren todos los experimentos.

## 104-105 · Estado RNG en checkpoints · sensibilidad al orden

`observer/checkpoints.py` guarda `np.random.get_state` y lo restaura. Ver §XX para el resto.
[105] Siguen sensibles al orden: construcción de módulos, generator del agente,
`_recent_positions`.

---

# VI · Ciclo completo del agente A4

## 106 · Call graph exacto, `world_state → action`

```
WorldStateManager.get_observation(0, view_radius=2, num_channels=4)
   └─ Observation(channels(4,5,5), mask(5,5), agent_energy, time_fraction)
A4.perceive(obs)                                    [a4_advanced.py:343]
   ├─ encoder.encode_observation(obs.channels) → latent (128,)
   └─ homeostasis._energy = obs.agent_energy        ← asignación DIRECTA
A4.decide()                                         [a4_advanced.py:~380]
   ├─ si _last_latent es None → acción uniforme aleatoria y retorno
   ├─ temporal_core(latent, hidden) → h (256,)         [si use_temporal]
   ├─ _build_state(latent, h) → s_t (640,)
   │     ├─ episodic_memory.read(latent, k=5) → memory_context (128,)
   │     ├─ longterm_memory.read(h)          → lt_context (128,)
   │     └─ concat(latent 128, h 256, memory 128, lt 128) = 640
   ├─ logits = policy_head(s_t)                        (25,)
   ├─ temperature = 1 + homeostasis.exploration_bias   [si use_homeostasis]
   ├─ uncertainty: 25 acciones × ensemble 5 → logits += 0.1·var   [si use_uncertainty]
   ├─ RAMA FACTORIZADA  [si use_factored_action o T1]
   │     ├─ operation_head(s_t) → op_logits (5,)
   │     ├─ planner.plan(...)  con prob 0.5  → op y dirección    [si planner Y world_model]
   │     ├─ selector: slot_logits (16) bajo T1, direction_head (5) si no
   │     └─ return Action(operation, direction, selector_type, selector_value)
   └─ RAMA PLANA
         ├─ si use_planner Y use_world_model:
         │     planner.plan(s_t, world_model, horizon=5, candidates=10)
         │     con prob 0.5 → action = planned; si no → policy_head.sample(logits, T)
         ├─ si no: policy_head.sample(logits, T)
         └─ return Action.from_int(action_int)
```

## 107 · Orden de participación

percepción → memoria (lectura) → núcleo temporal → construcción de estado → política →
homeostasis (temperatura) → incertidumbre (sesgo de logits) → planificador → muestreo.
**La memoria se lee dentro de `_build_state`, no después.** El planificador es el último en
intervenir y puede **sobrescribir** la elección de la política.

## 108-110 · La observación

La crea `WorldStateManager.get_observation` ([state.py:64](terrario/world/state.py:64)).
Dimensión: `(num_channels, 2·view_radius+1, 2·view_radius+1)` = **(4, 5, 5)** en D4T, más
`mask (5,5)`, `agent_energy` escalar y `time_fraction` escalar. Total **4·25 + 25 + 2 = 127**
valores. Antes de entrar a A4 no recibe ninguna transformación: `encode_observation` copia el
array y lo pasa al encoder convolucional.

## 111-115 · Los canales, exactamente

**Éste es el punto que más se malinterpreta en todo el repositorio.**

```
obs canal 0 = OCCUPANCY (1.0 si hay algún objeto en la celda)   ← derivado
obs canal 1 = canal 0 del objeto     ← EL CANAL CAUSAL (0.82 / 0.18)
obs canal 2 = canal 1 del objeto     (0.18 / 0.82)  anti-correlado
obs canal 3 = canal 2 del objeto     (0.35 / 0.12)
canal 3 del objeto (0.12 / 0.35)     ← NUNCA LLEGA AL AGENTE
```

El desplazamiento lo hace `channels[1 : 1+n_obj_ch] = avg[:n_obj_ch]` con
`n_obj_ch = min(4, num_channels-1) = 3` ([state.py:104-108](terrario/world/state.py:104)).

[112] Físicos: los canales del objeto. [113] Derivado: occupancy. [114] Producido por el
laboratorio: los valores de las plantillas de clase, fijados en el YAML del escenario.

[115] **Sí, hay una variable que permite inferir la etiqueta oculta por un atajo**: la regla
depende del canal 0 del objeto (obs canal 1), pero el canal 1 del objeto (obs canal 2) está
**perfectamente anti-correlado** con él en D4T (0.82/0.18 frente a 0.18/0.82). Un organismo que
aprendiera obs canal 2 sería indistinguible de uno que aprendiera obs canal 1. Ése es el atajo
que el banco `decorrelated` de P1 existe para separar.

## 116-122 · El recorrido interno

[116] La observación entra al temporal core **ya codificada**: `temporal_core(latent.unsqueeze(0), hidden)`.
[117] Devuelve `(output, new_h)`; con `SSMCore`, `output = new_h @ C.T` y `new_h = clamp(a)·h + x@B.T`.
[118-120] El world model, la memoria y la incertidumbre **no reciben el latente ni el hidden
directamente**: reciben `s_t`, el vector concatenado de 640. La excepción es
`longterm_memory.read(h)`, que lee con el hidden, y `episodic_memory.read(latent)`, que lee con
el latente.
[121] El planner recibe `s_t` y el `world_model`.
[122] `logits = policy_head(s_t)`, luego modificados por temperatura e incertidumbre.

## 123 · Dónde ocurre el muestreo

Tres sitios distintos:
- `policy_head.sample(logits, temperature, generator)` — rama plana ([policy.py:69](terrario/agent/policy.py:69)).
- `torch.multinomial(op_probs, 1, generator)` y el selector — rama factorizada.
- `planner.plan` sortea `torch.randint(0, 25, (horizon,))` por candidato.

**No hay `argmax` en la ruta de decisión.** `policy_head.greedy` existe y no se usa en A4.

## 124 · Después de seleccionar la operación

Bajo T0 nada más: se devuelve `Action.from_int`. Bajo T1 se determina si la operación lleva
entidad (`ALLOWED_SELECTORS`), se muestrea la ranura sobre `_slot_logits`, y la dirección se fija
a `NONE`.

## 125-128 · Qué estado cambia y cuándo

| Estado | Cambia en | ¿Con `_use_online_learning=False`? |
|---|---|---|
| `_last_latent` | `perceive` | **sí** |
| `homeostasis._energy` | `perceive` (asignación) | **sí** |
| `_hidden` | `decide` (temporal core) | **sí** |
| `_last_state`, `_last_action`, `_last_log_prob`, `_last_logits`, `_last_probs`, `_last_uncertainty` | `decide` | **sí** |
| `_step` | `decide` y `learn` | **sí** |
| `episodic_memory._buffer` | `learn` | **sí** |
| `longterm_memory.M` | `learn` (write bajo `no_grad`) | **sí** |
| `_energy_baseline`, `_baseline_count` | `learn`, dentro del bloque | **no** |
| Parámetros de los 6 módulos | `learner.step` | **no** |

[128] **Componentes que cambian conducta sin tocar parámetros**: la memoria episódica (su
contenido entra en `s_t`), la memoria de largo plazo (`M` se escribe fuera del optimizador), el
estado recurrente, y la homeostasis vía temperatura. **Los cuatro siguen vivos en el gemelo
congelado de P1** — de ahí que `G` aísle específicamente la contribución paramétrica.

## 129-131 · Persistencia

Nada persiste entre episodios en el uso actual: cada corrida construye un agente nuevo.
`episodic_memory.reset()`, `longterm_memory.reset_memory()` y `homeostasis.reset()` existen y
**no los llama ningún loop**. [131] Ver §XX.

---

# VII · Arquitectura de acciones

## 132-134 · Representación canónica

`Action` ([core/types.py:128](terrario/core/types.py:128)): `action_type`, `direction`,
`target_id = -1`, `selector_type = 0`, `selector_value = -1`.

`to_int()` = `action_type·5 + direction`; `from_int()` invierte. **Preservan operación y
dirección; destruyen `target_id`, `selector_type` y `selector_value`.** Ése fue el defecto
original: `target_id` existía y nada de lo que el agente emitía llegaba a él.

## 135-136 · Quién asume 25 acciones y quién entiende la forma factorizada

**Asumen 25 planas**: `policy_head` (`Linear(256, TOTAL_ACTIONS)`), `world_model`
(`action_dim = TOTAL_ACTIONS`), `uncertainty_estimator`, `Planner.plan`
(`torch.randint(0, TOTAL_ACTIONS, ...)`), `_action_to_onehot`, y todas las mallas de
`run_measures` salvo `_cadena`.

**Entienden la forma factorizada**: `core/action_contract.py`, la rama factorizada de
`A4.decide`, `sandbox_runtime._apply_action_contract`, `run_measures._cadena` y
`_realizacion`.

## 137-140 · Dónde se resuelve el selector

`selector_type` lo fija el agente en `decide` según `ALLOWED_SELECTORS[operation]` y el
`addressing_mode`. `selector_value` lo muestrea el agente. La **resolución** ocurre en
`action_contract.resolve`, llamada desde `sandbox_runtime._apply_action_contract`.

[139] **Sí, existe tabla canónica**: `ALLOWED_SELECTORS` en
[action_contract.py](terrario/core/action_contract.py), derivada de la física real:

```
MOVE    → {SPATIAL_DIRECTION}      _handle_move sólo usa DIRECTION_DELTA
PUSH    → {SPATIAL_DIRECTION}      empuja hacia una dirección y sigue
CONSUME → {SPATIAL_DIRECTION, OBSERVED_ENTITY}
INSPECT → {}                       _handle_inspect NO lee dirección ni target
NOOP    → {}
```

[140] Antes de esa tabla la semántica **sí** estaba repartida entre handlers.

## 141-144 · Validación

[141-142] **Nadie valida que MOVE o PUSH reciban dirección.** `Direction` tiene default `NONE` y
`DIRECTION_DELTA[NONE] = (0,0)`, así que un MOVE sin dirección es un no-op silencioso.
[143] CONSUME lo valida `ActionIntent.__post_init__` (rango del selector) y `resolve` (existencia,
alcance, oclusión) — **sólo en el banco**.
[144] Un selector incompatible levanta `ValueError` en `ActionIntent`; `SelectorType.RELATION`
levanta `NotImplementedError`.

## 145-149 · Estados de resolución

| Estado | Significado | Cuándo se determina |
|---|---|---|
| `VALID` | la entidad existe, fue percibida y está en contacto | `resolve` |
| `NONEXISTENT` | la ranura estaba vacía, o la dirección apunta a celda sin objeto | `resolve` |
| `OUT_OF_RANGE` | la entidad existe y fue percibida, pero no está en contacto | `resolve` |
| `STALE` | el handle era real; la entidad ya no está en el mundo | `resolve` |
| `OCCLUDED` | dentro de la ventana, oculta por la máscara | `perceive_targets` (no entra en la tabla) |
| `NOT_ADDRESSED` | la operación no lleva objetivo | `resolve` |

## 150-153 · Registro de intención, resolución y ejecución

`ActionProvenance` registra los tres por separado: `intended_target`, `resolved_target`,
`executed_target`, más `target_status` y `execution_status`.
[153] **Sí se distinguen** — es el invariante AC2-5, y `tasa_realizacion` mide
`P(executed == intended | intención válida)`.

## 154-156 · Locomoción

[154] Cambian posición: **MOVE** (`_handle_move` → `move_agent`) y **PUSH**
(`_handle_push` mueve el objeto y **el agente lo sigue**).
[155-156] La locomoción por PUSH es **física declarada en el handler**, no emergente: el código
mueve explícitamente al agente detrás del objeto. Pero su uso como medio principal de
desplazamiento **sí es emergente**: en D4T medido, PUSH fue la operación modal con 158 de 300
pasos, frente a 34 de MOVE.

## 157-158 · INSPECT

`_handle_inspect` devuelve `["inspect"]` y **no lee ni `direction` ni `target_id`**
([physics.py:165](terrario/world/physics.py:165)). El docstring dice «the observation system
handles the increased detail separately» — **no existe tal sistema**. INSPECT no produce
información observable posterior de ningún tipo.

## 159-160 · NOOP y efectos comunes

NOOP emite el evento `"noop"` y nada más; el **coste metabólico se aplica igual**, fuera de
physics, en `apply_step_energy_cost`. [160] Efectos comunes a toda operación: el coste por paso,
el avance del tiempo (`advance_time` al final de `physics.step`) y la clasificación de eventos.

---

# VIII · Modelo del mundo

## 161-166 · Clase, cabezas, targets y losses

`WorldModel(nn.Module)` en [agent/world_model.py:15](terrario/agent/world_model.py:15).

```
backbone: Linear(640+25, 256) → ReLU → Linear(256,256) → ReLU     ← COMPARTIDO
  ├─ next_state_head: Linear(256, 640)   target = s_{t+1}    loss = MSE
  ├─ energy_head:     Linear(256, 1)     target = energy_delta   loss = MSE
  └─ done_head:       Linear(256, 1)     target = 0/1        loss = BCEWithLogits
loss_total = loss_state + loss_energy + loss_done          ← PESOS IGUALES, SIN PONDERAR
```

[166] **No hay ponderación.** `loss_state` es un MSE sobre 640 dimensiones y `loss_energy` sobre
1. En magnitud, el estado domina la loss del world model por construcción.

## 167-172 · `energy_head`

[167-168] Predice **el delta energético del paso**, no energía absoluta ni recompensa.
[169-172] Entrada: `concat(s_t (640), action_onehot (25))`. **Incluye la acción**; **no incluye
representación del objetivo** —bajo T0 la acción codifica la dirección, así que el objetivo está
implícito en la geometría; bajo T1 la ranura **no entra en el one-hot**—; **incluye el estado
recurrente**, porque `s_t` contiene `h`.

## 173-177 · Horizonte y alineación

[173] **Un paso.** [174-175] El target se **reconstruye**: `consequence.energy_delta` lo calcula
el loop restando; en `experiment_capability_acquisition.stream_from` se reconstruye otra vez
desde la serie de energías del observador. [176] Se alinea `(s_t, a_t) → energy_delta_{t→t+1}`.
[177] **Sí hay riesgo de off-by-one**, y ya se materializó una vez: `_cadena` emparejaba la
acción del paso *i* con el mundo del paso *i*, cuando el mundo registrado es posterior a la
acción. Corregido en `run_measures`, pero la reconstrucción sigue siendo la fuente.

## 178-180 · Qué actualiza y qué comparte

[178] La loss del energy head actualiza **el backbone compartido, el encoder y el temporal core**
—`_last_state` conserva el grafo—, además de su propia capa.
[179] **Sí comparte**: las tres cabezas cuelgan del mismo backbone.
[180] **Sí puede mejorar una y empeorar otras**: comparten backbone y las losses se suman sin pesos.

## 181-187 · Dónde se usa la salida

[182] **El planner la consume directamente**: `score = Σ energy_pred − 10·Σ sigmoid(done_pred)`
([policy.py:~150](terrario/agent/policy.py)).
[183] **La política NO la consume.** `logits = policy_head(s_t)` no ve ninguna predicción.
[184] Además se registra como diagnóstico: `prediction_error` y `_last_prediction`.

### Medición: qué predice realmente

Agente sin entrenar, 25 acciones sobre un mismo estado:

```
energy_head   desv 0.00349   rango 0.01510
done_head(p)  desv 0.00084   rango 0.00375
```

Tras 600 pasos de D4T, sobre 400 sondas:

```
energy_head   media 0.0047   desv 0.00370   rango 0.0154
```

Los deltas reales del stream: media **−0.0583**, mínimo **−1.06**, máximo **+0.94**.

**`energy_head` es efectivamente constante.** Su dispersión tras entrenar (0.0037) es
indistinguible de la que tenía al nacer (0.0035), y **130 veces menor** que la diferencia que
debería representar (2.0 entre favorable y desfavorable). No aprendió ni siquiera la media.

En la puntuación del planner, con los pesos del propio código:

```
contribución de energía por rollout de 5 pasos:  5 · 0.0035 = 0.0174
contribución de done    por rollout de 5 pasos: 50 · 0.0008 = 0.0418
razón done / energía: 2.4×
```

[195 bis] **El planner no elige por energía predicha.** Elige, en la medida en que elige algo, por
terminación predicha — y ambas señales son ruido de una red sin entrenar.

[185] **No es ablacionable**: no hay flag que quite `energy_head` conservando el resto.
[186] El planner recibe las **predicciones aprendidas**, no features previas a la cabeza.
[187] **Sí, hay predicciones que nunca llegan a conducta**: `next_state_head` alimenta el rollout
interno del planner pero su error nunca se reporta; `prediction_error` sólo se registra.

---

# IX · Planner

## 188-192 · El algoritmo real

**Random shooting**, [policy.py:98](terrario/agent/policy.py:98):

```python
for candidate in range(num_candidates):        # 10
    actions = torch.randint(0, 25, (horizon,)) # 5 acciones AL AZAR
    sim_state = state.clone()
    for a in actions:
        next_state, energy_pred, done_pred = world_model(sim_state, onehot(a))
        total_energy += energy_pred; done_prob_accum += sigmoid(done_pred)
        sim_state = next_state
        if done_prob > 0.9: break
    score = total_energy - 10.0 * done_prob_accum
return best_actions[0]
```

[189] «Planificar» en A4 es: **sortear diez secuencias aleatorias de cinco acciones, puntuarlas
con un modelo del mundo no entrenado y devolver la primera acción de la mejor**.
[190] Genera secuencias explícitas, [191] horizonte 5, [192] evalúa **trayectorias**, no acciones
individuales.

## 193-197 · Qué consume

[193] Función de valor: `Σ energía − 10·Σ P(done)`, con el 10 escrito en el código y no declarado
en ningún escenario. [194] Consume `energy_head` y `done_head`.
[195] **No consume memoria.** [196] **No consume incertidumbre.** [197] **No consume homeostasis.**
Recibe únicamente `s_t` y el `world_model`.

## 198-203 · Qué devuelve

Un **entero** (`best_action` en el espacio plano de 25) más un trace. [199-200] Operación y
dirección van empaquetadas en ese entero. [201] **No devuelve distribución.** [202] Los scores por
candidato existen sólo en el trace. [203] **No devuelve secuencia** al agente, aunque la calcula.

## 204-205 · Discrepancia y autoridad

Se resuelve por **moneda**: `plan_prob = 0.5` fijo. Con probabilidad ½ gana el planner, con ½ la
política. [205] **No hay autoridad final**; hay un sorteo. Y cuando gana el planner, la
`log_prob` que se usa para REINFORCE es la de la política evaluada **sobre la acción del
planner** — una actualización fuera de política tratada como si fuera dentro.

## 206-209 · Por qué su ablación lleva las comidas a cero

**Éste es el hallazgo central de la sección.** La rama está condicionada a **ambos** flags:

```python
if self._use_planner and self._use_world_model:
```

Verificado ejecutando 40 decisiones y contando invocaciones a `planner.plan`:

```
A4 completo        40 / 40 llamadas
use_planner=False   0 / 40
use_world_model=False   0 / 40      ← MISMA RUTA ELIMINADA
```

**`use_world_model=False` desactiva el planificador.** Los dos efectos «significativos» del
tamizado —modelo del mundo +6.33 comidas, planificador +6.67— **son la misma intervención medida
dos veces**. Y la conjunción `anticipacion` (ambos) elimina exactamente la misma ruta que
cualquiera de los dos por separado, lo que explica su residuo fuertemente sub-aditivo (−6.67).

[207] Desaparece la inyección de una acción **casi uniforme** en el 50 % de los pasos.
[208-209] El fallback es `policy_head.sample(logits, temperature)`, es decir, **la política
colapsada**. No es funcionalmente comparable: el planner, con un modelo del mundo que no predice
nada, funciona como **fuente de exploración**, no como planificador.

## 210-212 · Congelado, aprendizaje y pruebas

[210] **Sí**, el planner opera con un world model congelado: sólo lo llama bajo `no_grad`.
[211] **Sí**, el world model puede aprender sin que el planner use el cambio —y de hecho es lo
que ocurre: su salida es constante—.
[212] **No existe ninguna prueba** que demuestre que modificar una predicción cambia la elección
del planner.

---

# X · Aprendizaje online

## 213-216 · El bloque y los optimizadores

El bloque `if self._use_online_learning:` empieza en [a4_advanced.py:602] y termina justo antes
del `else` del trace. [214] Dentro pueden cambiar los parámetros de los seis módulos registrados.
[215] **Un solo optimizador**: `torch.optim.Adam` sobre **todos** los parámetros juntos
([learner.py:41](terrario/agent/learner.py:41)). [216] No hay separación por módulo.

## 217-219 · Cuándo ocurre cada operación

`zero_grad`, `backward` y `step` ocurren **en el mismo timestep**, dentro de `OnlineLearner.step`,
llamado al final de `A4.learn`. No hay acumulación entre pasos.

## 220-226 · Cuántas actualizaciones y qué las dispara

**Medición sobre D4T, 300 pasos, semilla 1000042:**

```
pasos: 300        update_count final: 300        ← UNA ACTUALIZACIÓN POR PASO
operaciones: PUSH 158 · INSPECT 53 · MOVE 34 · NOOP 30 · CONSUME 25
deltas informativos (|delta − coste| > 0.5): 3      [−1.06, −1.06, +0.94]
coste por paso declarado: 0.06
```

[221-224] La condición no es interacción, ni señal informativa, ni recompensa no nula:
**basta con que exista `wm_loss` o `policy_loss`**, y ambas existen en todo paso con
`_last_state` no nulo. [225] En un paso sin información se actualiza igual, con
`energy_target = −0.06`. [226] Un «ejemplo informativo» es un paso cuyo delta energético se
aparta del coste metabólico por más de media unidad — es decir, un consumo que alcanzó algo.

[245] **Tasa efectiva `evento informativo → optimizer step`: ≈ 1 : 100.** El 99 % del gradiente
es el coste por paso constante.

## 227-231 · Las losses por desenlace

| Desenlace | `energy_target` | `policy_loss` | ¿aprende algo? |
|---|---|---|---|
| consumo favorable | **+0.94** | `−log π(a)·(0.94 − baseline)` | sí, señal real |
| consumo perjudicial | **−1.06** | advantage fuertemente negativo | sí |
| `OUT_OF_RANGE` | **−0.06** | advantage ≈ 0 | [229] indistinguible de no hacer nada |
| `NONEXISTENT` | **−0.06** | advantage ≈ 0 | [230] indistinguible de no hacer nada |

[231] **De un intento fallido no se aprende nada distinto de un NOOP.** El mundo no devuelve
ninguna señal que separe «apunté a nada» de «apunté a algo inalcanzable» de «no hice nada»: los
tres cuestan 0.06. La descomposición de desperdicio existe **en el instrumento**, no en la
experiencia del organismo.

## 232-245 · Asignación de crédito y maquinaria

[232] REINFORCE con **baseline de media móvil**: `advantage = energy_delta − _energy_baseline`,
donde el baseline se actualiza incrementalmente. Con el 99 % de los deltas igual a −0.06, el
baseline converge a −0.06 y el advantage de esos pasos tiende a cero — pero **no es cero**, y hay
1194 de ellos frente a 6 con señal.

[233-238] **No hay buffer de transición, ni replay, ni n-step return, ni descuento, ni
eligibility traces.** Cada paso se entrena una vez, con su propio desenlace inmediato.
[239] **No hay BPTT**: el hidden se detach explícitamente (`self._hidden = self._hidden.detach()`).
[240-241] Se hace `detach()` sobre `_hidden` tras el temporal core, sobre las predicciones del
world model en el cálculo de `prediction_error`, y sobre `_last_logits`/`_last_probs`.
[242] **No puede entrenar dos veces**: cada paso llama a `learner.step` una vez.
[243] **Sí puede perderse**: si `_last_state` es None (primer paso) o la loss no es finita
(`learning_skipped_nonfinite`).

[244] **Sí: se actualizan pesos aunque el instrumento clasifique la experiencia como no
informativa.** Las dos clasificaciones son independientes y nunca se hablan.

## 246-248 · Qué cambia cuantitativamente

Se registra `parameter_delta_norm` y `grad_norms` por módulo en cada `learn`, y
`before_parameters_hash`/`after_parameters_hash`. Es la medición disponible hoy.
[247] **Verificación pendiente**: no he medido qué módulos permanecen casi constantes.

---

# XI · Memorias

## 249-255 · Memoria episódica

`EpisodicMemory` ([memory.py:16](terrario/agent/memory.py:16)) — **no es `nn.Module`**, por tanto
**no tiene parámetros y no recibe gradiente**.

[250] Unidad almacenada: `{embedding, action, energy_delta, prediction_error, timestamp}`.
[251] Recuperación: **coseno** entre el latente actual y los embeddings guardados, top-k con
`k=5`, pesos por softmax de las similitudes.
[252] El criterio es **puramente similitud perceptiva**; ni el `prediction_error` ni el
`energy_delta` guardados influyen en la selección: se almacenan y no se leen nunca
[647].
[253] Capacidad 1000 (`memory_capacity`), buffer circular.
[254] Olvida por sobrescritura FIFO al llenarse — con 1200 pasos, apenas.
[255] Lo recuperado lo consume `_build_state`: media ponderada → `memory_context` (128,).

## 256-265 · Memoria de largo plazo

`LongTermMemory(nn.Module)` — matriz `M (64, 128)` como `nn.Parameter`, más cinco proyecciones
lineales.

[257] Guarda una **mezcla continua** en 64 ranuras, no episodios discretos.
[258] Escribe en `learn`, con `key = value = h` (el hidden), bajo `torch.no_grad()`:
`M ← M·(1−gate) + outer(w, v)·gate`, con `nan_to_num` y `clamp(±10)` defensivos.
[259] Lee en `_build_state`, con atención sobre `h`.
[260] Afecta la acción vía `lt_context` dentro de `s_t`.
[261-262] Afecta al world model y al planner por la misma vía: ambos reciben `s_t`.
[263] Sus **proyecciones** sí reciben gradiente; **`M` no**, porque se escribe bajo `no_grad`.

[264] **Estado de memoria que sigue cambiando con el aprendizaje congelado**: el buffer episódico
**y** la matriz `M`. Ambos. [265] Dependen de gradiente: `query_proj`, `key_proj`,
`write_key_proj`, `value_proj`, `write_gate`.

## 266-272 · La interacción negativa al quitar ambas

[266] La explicación arquitectónica: `_build_state` **contribuye ceros** por el módulo ausente y
**no cambia dimensiones**. Con episódica fuera, `memory_context` es un vector de ceros de 128;
con la de largo plazo fuera, `lt_context` es otro de 128. Quitar una deja `s_t` con 128
dimensiones muertas y 128 vivas que siguen cambiando paso a paso; quitar **ambas** deja 256
dimensiones constantes, lo que **reduce la varianza de entrada a la política** y puede
estabilizarla. Es una hipótesis mecánica compatible con el residuo −3.0, y **no la he probado**.

[267-269] Con episódica fuera queda la ruta `h → longterm.read → lt_context`. Con la de largo
plazo fuera queda `latent → episodic.read → memory_context`. Sin ambas, `s_t` = `concat(latent,
h, 0, 0)`.
[270] **No hay fallback condicionado**: los ceros son el fallback.
[271] **No cambian dimensiones ni concatenaciones.** `_build_state` siempre devuelve 640.
[272] Ablacionar memoria **no** toca otros parámetros ni normalizaciones, pero **sí cambia qué
módulos entran en el optimizador**: `learnable_modules` se construye condicionalmente, así que el
Adam de un agente sin memoria de largo plazo tiene menos parámetros y por tanto distinto estado
interno.

---

# XII · Estado temporal / SSM

## 273-277 · Qué es `SSMCore`

[temporal.py:70](terrario/agent/temporal.py:70). Un **modelo lineal de espacio de estados
diagonal**:

```
h_t = clamp(a, ±0.999) · h_{t-1} + x_t @ Bᵀ
y_t = h_t @ Cᵀ
```

Parámetros: `a (256,)` inicializado en 0.99±0.01, `B (256,128)`, `C (256,256)`.
[274] Entrada: el latente del encoder (128,). [275-276] Estado: `h (256,)`.
[277] Lo consume `_build_state` (entra en `s_t`) y `longterm_memory.read(h)`.

## 278-280 · Entrenamiento

[278] **Sí se entrena**, está en `learnable_modules` cuando `use_temporal=True`.
[279] Con la señal combinada: la loss del world model y la de la política llegan a él porque
`_last_state` conserva el grafo hasta el temporal core.
[280] **Sí puede modificar la acción** aunque su ablación no moviera D4T: `h` ocupa 256 de las 640
dimensiones de `s_t`.

## 281-283 · ¿Hace falta historia?

[281-283] **No existe hoy ninguna tarea que exija historia temporal.** D4T es Markoviano en lo
esencial: la consecuencia de CONSUME depende del canal del objeto adyacente, visible en el
instante. Las inversiones de regla en los pasos 300/600/900 son el único elemento no estacionario,
y detectarlas requeriría comparar consecuencias a través del tiempo — algo que ningún instrumento
mide hoy. **No hay ningún escenario donde `SSMCore` sea necesariamente útil.**

## 284-286 · Qué ocurre con `use_temporal=False`

[285] Se sustituye por **ceros**: `h = torch.zeros(hidden_dim)`. No hay bypass ni encoder
alternativo. El módulo **sigue construido** —existe en el objeto— pero ni se llama ni entra en el
optimizador.
[286] **Sí, el número de parámetros downstream se mantiene**: `s_t` sigue siendo 640, con 256
ceros.

## 287-290 · H-Net y Mamba2

[287-288] **Verificación pendiente**: no he encontrado código de H-Net ni dependencias preparadas
para Mamba2 en el barrido de `terrario/`. Puede estar en documentación o en `theory_snapshots/`.
[289-290] **Sí existe interfaz abstracta estable**: `TemporalCore` con `forward`, `initial_state`
y `hidden_dim`. Cambiar el núcleo no exigiría tocar contratos downstream **mientras respete
`hidden_dim`**, porque `_build_state` concatena por posición.

---

# XIII · Incertidumbre y exploración

## 291-294 · Qué cantidad produce

`UncertaintyEstimator` ([uncertainty.py:12](terrario/agent/uncertainty.py:12)): un **ensemble de
K=5 cabezas** `Linear(665,128) → ReLU → Linear(128,1)`, cada una prediciendo el delta energético.
La incertidumbre es la **varianza entre las cinco predicciones**.

[292] Es **epistémica por construcción** —desacuerdo del ensemble—, pero como las cinco cabezas se
entrenan con **la misma loss sobre el mismo target en cada paso**, convergen juntas y la varianza
mide sobre todo la diferencia de inicialización. En la práctica es **un score aprendido**.
[294] Depende de los parámetros de las cinco cabezas y de `s_t`.

## 295-298 · Dónde entra a la decisión

```python
for a in range(25):
    _, var, _ = uncertainty_estimator.predict(state, onehot(a))
    uncertainties[a] = var.mean()
logits = logits + 0.1 * uncertainties
```

[296] **Sí cambia logits**, con coeficiente 0.1 escrito en el código.
[297] **No cambia los scores del planner** — el planner no la consulta.
[298] Cambia exploración sólo por esa vía.

## 299-306 · Entrenamiento y calibración

[299] **Sí se entrena explícitamente**, y sólo si `use_uncertainty AND use_world_model`:
la loss es la media de MSE de las cinco cabezas contra `energy_delta`, **sumada a `wm_loss`**.
[300] **No tiene calibración conocida.** [301] «Incertidumbre alta» no tiene significado numérico
declarado en ninguna parte.
[302-303] **Verificación pendiente**: no he medido su comportamiento fuera de distribución ni ante
contradicción.
[304] Relación con el error de predicción: **indirecta** — ambas cabezas predicen el mismo target,
pero nada las compara.
[305] Se conserva `_last_uncertainty` (un escalar, la media) por paso en el trace.
[306] **Sí puede subir tras bajar**; nada lo impide.

## 307-315 · Regularización de entropía y colapso

[307-310] `entropy = −Σ p·log p` sobre `fresh_probs`, la distribución **plana de 25 acciones**
recalculada en `learn`. `policy_loss −= coeficiente · entropy`, con coeficiente 0.01. Entra en la
loss **sólo si `use_entropy_regularization=True`**, que viaja apagado.

[311] **Sí, la ausencia de este término explica el colapso mecánicamente**, y el comentario del
propio código lo dice: REINFORCE con baseline de media móvil sobre una recompensa que es el coste
por paso casi siempre da un advantage casi constante, «que apila probabilidad sobre lo que se hizo
primero».

[312-314] **Verificación pendiente**: no he medido los logits antes y después de los primeros
eventos informativos, así que **no puedo afirmar si el colapso precede o sigue a la evidencia**.
Es una medición concreta y pendiente.
[315] Gradientes capaces de producirlo: `policy_loss = −log π(a)·advantage`, sobre `policy_head`,
el encoder y el temporal core.

---

# XIV · Homeostasis y viabilidad

## 316-321 · Las variables

`HomeostaticState` ([homeostasis.py](terrario/agent/homeostasis.py)) — **no es `nn.Module`**.

```
_energy      [0,1]
_threshold   0.5  (config: homeostasis_threshold)
drive              = max(0, threshold − energy)     DERIVADA
exploration_bias   = 1 − energy                     DERIVADA
```

> **Medido el 2026-09-18 (OCF-G1).** `_energy` tiene **dos escritores**: `perceive` lo asigna
> desde `observation.agent_energy` ([a4_advanced.py:358](terrario/agent/agents/a4_advanced.py:358))
> y `learn` lo acumula con `update()` ([a4:577](terrario/agent/agents/a4_advanced.py:577)), 68 y 68
> veces en una vida de 68 pasos. De 21 estados instrumentados es el **único** con autoridad
> disputada. Queda deliberadamente sin reparar: es O1, no OCF-G3. `_threshold` no lo escribe nadie
> en runtime, que es lo que lo hace la costura limpia para la alostasis. Ver §XXXVII.

[317] **Sólo una es independiente: `_energy`.** [318] `drive` y `exploration_bias` son **alias
funcionales** de la misma variable; ninguna aporta información que la otra no tenga.

## 322-325 · Qué ve A4 de su propia energía

`perceive` hace **asignación directa**: `self.homeostasis._energy = observation.agent_energy`
([a4_advanced.py:358](terrario/agent/agents/a4_advanced.py:358)).

**Consecuencia que conviene fijar:** `HomeostaticState.update(energy_delta)`, llamado en `learn`,
acumula deltas en `_energy` — y `perceive` **lo sobrescribe** en el paso siguiente. Como el orden
es `perceive → decide → learn`, el valor acumulado **nunca se lee para decidir**. `update()`
sirve únicamente para el registro del trace. Es estado escrito y no leído [647].

[325] El agente ve **energía normalizada absoluta**, no delta. En D4T arranca en 0.60 (60/100) y
baja; `exploration_bias` va de 0.40 hacia 1.0 y la temperatura de 1.40 hacia 2.0.

## 326-331 · Cómo entra a la decisión

```python
temperature = (1.0 + homeostasis.exploration_bias) if use_homeostasis else 1.0
```

[327] **Modifica la política**, y sólo por temperatura. [328] **No modifica el planner.**
[329] **No modifica la loss.**
[330-331] Con `use_homeostasis=False` la temperatura queda en 1.0 fija. **Es una ablación real de
la vía causal**, no una sustitución por defaults: el estado homeostático se sigue calculando y
reportando, lo que se elimina es su autoridad sobre la distribución. Fue una decisión explícita
para no confundir «la viabilidad no tiene autoridad causal» con «la viabilidad no se midió».

## 332-335 · Muerte y línea base

[332] La muerte la decide `RuleEngine.apply_effects`: `if new_energy <= 0.0: set_agent_alive(False)`
([rules.py:226](terrario/world/rules.py:226)). **Y sólo ahí** — `apply_step_energy_cost` reduce la
energía pero **no comprueba el umbral**. *Verificación pendiente*: si el coste por paso lleva la
energía a cero sin que ninguna regla dispare, la muerte no se declararía en ese paso.
[333] El controller comprueba `alive` **al principio** del paso y hace `break`; el banco lo calcula
**al final** como `terminated`.
[334] En D4T, con energía inicial 60 y coste 0.06 × 1200 pasos = **−72**, el organismo muere por
degradación sin interactuar. La viabilidad es real, no decorativa.
[335] Línea base de no hacer nada: **muerte en el paso 1000** (60 / 0.06).

---

# XV · Percepción y features

## 336-338 · Dónde se construye y qué significa cada canal

`WorldStateManager.get_observation` ([state.py:64](terrario/world/state.py:64)).

```
obs[0] = occupancy  ∈ {0,1}          derivado de state.occupancy
obs[1] = canal 0 del objeto           ← EL CANAL CAUSAL
obs[2] = canal 1 del objeto
obs[3] = canal 2 del objeto
canal 3 del objeto                    ← TRUNCADO, nunca llega
```

Con varios objetos en una celda, los canales se **promedian**.

## 339-349 · D4T en concreto

[339] El canal 0 del objeto lleva 0.82 (clase A) o 0.18 (clase B).
[340-341] Esos valores están escritos **en el escenario**,
`scenarios/d4_temporal_variety.yaml`, en `procedural_layout.class_templates`:

```yaml
A: {count: 16, channels: [0.82, 0.18, 0.35, 0.12]}
B: {count: 16, channels: [0.18, 0.82, 0.12, 0.35]}
```

Y la regla que los usa vive en el mismo fichero: `object_channel {index: 0, min: 0.7}` → +1.0,
`{index: 0, max: 0.3}` → −1.0, ambas con `destroy_object: true`.

[342-343] **Correlaciones accidentales**: el canal 1 del objeto está **perfectamente
anti-correlado** con el 0 (0.18/0.82 frente a 0.82/0.18), y el canal 2 también separa las clases
(0.35/0.12). De los tres canales de objeto que el agente ve, **los tres son perfectamente
predictivos**.
[344-348] Todos los valores son **constantes por clase**: no dependen de posición, identidad ni
historia. Sólo hay dos vectores perceptivos distintos en todo el mundo.

[349] **Sí, la red puede inferir la clase por al menos dos atajos** distintos del canal causal.
Ésa es la razón del banco `decorrelated` en P1.

## 350-360 · Ranuras perceptivas (sólo T1)

[350] `action_contract.perceive_targets` las construye desde el estado del mundo, filtrando por
ventana de visión y máscara.
[351-352] Orden: **por distancia Manhattan y luego fila-columna**. Es estable y determinista.
[353] **Sí filtra posición** —la ranura 0 es la entidad más cercana— pero **no identidad**: el
handle se re-acuña por fotograma bajo `EPHEMERAL`.
[354-355] Con más entidades que ranuras (`MAX_TARGET_SLOTS = 16`) se **trunca** y se **reporta**
`perceived_truncated=True`. Se quedan las 16 más cercanas.
[356-359] Con menos, `_slot_logits` pone **−1e9** en las ranuras vacías, así que su probabilidad
tras softmax es nula: **una ranura vacía no puede producir elección**. Si no se percibe nada, se
usa el residual sin máscara, porque enmascarar todo dejaría el softmax indefinido.
[360] **Distancia**: el agente la recibe implícitamente por la posición en la ventana, y bajo T1
adicionalmente por el orden de las ranuras.

---

# XVI · P1 · CAPABILITY-ACQUISITION-01

## 361 · Call graph

```
_fresh(seed, config) ×4          torch.manual_seed(seed) → create_agent("A4")
  └─ verifica que los 4 comparten initial_parameters_hash, o aborta
sit_exam(a0, banco) ×3           held_out · decorrelated · seen_values
Bench.experience(D4T, 1200, seed) → SandboxService → traza
stream_from(traza)               reconstruye (obs, acción, delta, eventos)
replay(learner,  stream)
replay(frozen,   stream)         _use_online_learning = False
replay(shuffled, stream, shuffle_credit=True)
sit_exam(cada gemelo, cada banco) ×9
causal_gain(...)                 G = (L_post − L_pre) − (F_post − F_pre)
```

## 362-364 · Estado compartido y estado que puede diferir

[363] La igualdad paramétrica se **demuestra**, no se asume: los cuatro agentes se construyen bajo
la misma semilla global y la corrida compara sus `initial_parameters_hash`, abortando si difieren.
[364] Estado **no paramétrico** que arranca idéntico por construcción: `_hidden` en ceros, buffer
episódico vacío, `M` inicializada con la misma semilla, `_energy_baseline = 0`.

## 365-367 · El stream

Lo genera **el learner corriendo en el banco**, y `stream_from` lo reconstruye desde la traza
sellada. Cada registro: `observation`, `next_observation`, `action_int`, `energy_delta`
(**reconstruido restando energías consecutivas**), `events`, `done`, `step`, `seed`.
[367] La relación es `(obs_t, acción_t) → delta_{t→t+1}`, con el emparejamiento explícito en el
bucle de `stream_from`.

## 368-372 · Forzar la acción

`force_action(agent, action_int)` fija `_last_action` y **recalcula la log-probabilidad bajo la
política de ESE gemelo**. [370] Se usa para el término REINFORCE `−log π(a)·advantage`.
[371-372] **Sí, la recalcula sobre una política cuyo estado recurrente ya diverge** — y eso es
deliberado: la alternativa, dejar que cada gemelo actúe por su cuenta, daría tres experiencias
distintas y devolvería la comparación a dos trayectorias. El efecto es que el gradiente de
política de F y S se evalúa en un punto que su propia historia recurrente produjo, con la acción
de L. Es la definición operativa de «misma experiencia».

## 373-377 · ¿Reciben lo mismo?

[373] **Sí**, el mismo objeto `Observation`. [374] **Sí**, el mismo `energy_delta` —salvo S, que
recibe la permutación—. [375] Mismo `step`. [376] El estado homeostático es idéntico porque
`perceive` lo asigna desde la misma observación. [377] **Sí, las memorias reciben las mismas
escrituras**: F escribe en el buffer episódico y en `M` exactamente igual que L.

## 378-382 · Qué está bloqueado en F

[378] **Únicamente el bloque `if self._use_online_learning:`**, es decir, `learner.step()` y por
tanto `zero_grad/backward/step` del Adam.
[379] Fuera del bloque pueden cambiar en F: `_hidden`, el buffer episódico, `M` (escrita bajo
`no_grad`), `_step`, `homeostasis._energy`. **Parámetros con gradiente, no.**
[380] **No hay BatchNorm ni running stats** en A4: el encoder usa `LayerNorm`, que no mantiene
estadísticas. Verificado en el inventario de módulos.
[381-382] **No hay Dropout** en ningún módulo de A4.

## 383-386 · El control S

[383] Se baraja **la lista de `energy_delta`**, nada más: observaciones, acciones, longitud y
timesteps quedan intactos.
[384] **Sí preserva los marginales**: es una permutación, así que la multiplicidad es exacta.
[385] **Medido** sobre un stream realista de 1000 pasos con 7 eventos informativos:

```
¿misma multiplicidad?  True        ¿misma longitud?  True
posiciones que conservan VALOR:   986 / 1000   ← el coste metabólico repetido
eventos informativos que NO se movieron:  0 / 7
```

Las 986 posiciones que «conservan valor» son el coste metabólico: ahí no hay correspondencia que
romper. **La correspondencia que importa quedó rota por completo.**
[386] Con un **derangement por corrida** el riesgo residual desaparece. Hoy es ~0.7 %: la
probabilidad de que alguno de los ~7 eventos caiga en su propio índice entre ~1000 huecos.

## 387-396 · Los exámenes

[387-390] **Predicción**: se puntúa `energy_head(s_t, onehot(CONSUME·5+dir))` para la dirección
favorable frente a la desfavorable; acierta si la primera es mayor. [389] Los **empates salen del
denominador** —un predictor constante no expresa preferencia, y puntuarlo 0.0 sería llamarlo
«seguro y al revés»—. [390] Soporte: 400 sondas por banco, con 400/400 evaluadas en las corridas
reales.
[391-395] **Selección**: `softmax` sobre el par de logits de las dos alternativas, renormalizado.
Bajo T1 usa `_slot_logits`; bajo T0, `direction_head` si existe y `policy_head` si no.
[394] **El planner NO participa** en el examen. [395] La política sí, vía sus logits.

## 396-397 · Realización, y por qué `G_R` es cero estructural

[396] Hoy construye un `ActionIntent(CONSUME, DIRECTION, dirección_favorable)` y lo resuelve.
[397] **Ese intent no consulta al organismo en ningún punto.** Bajo T0 la dirección favorable
siempre resuelve, así que el examen devuelve **1.0 para cualquier agente, antes y después**, y
`G_R ≡ 0` por construcción. Mide una propiedad del contrato, no del ser. **Debe reconstruirse
sobre la elección propia del organismo.**

## 398-406 · Efectos secundarios del examen

[398-399] Sentar el examen **mutaba** `_hidden`, `_last_latent`, `_last_state`, `_last_action`,
`_last_log_prob`, `_step` y `_offered_targets` — de modo que tres bancos en secuencia se
contaminaban entre sí y **el orden de los bancos habría formado parte del resultado**. Ahora
`sit_exam` guarda y restaura esas siete variables en un `try/finally`.
[400-405] Lo que **podría** seguir mutando: [401] las memorias **no**, porque `sit_exam` nunca
llama a `learn` y `_build_state` sólo **lee**; [402] los contadores están restaurados;
[403] el RNG del agente **sí avanza** si `decide` se llegara a llamar — no se llama;
[404] no hay running statistics; [405] no hay caches.
[406] **No existe una prueba que garantice que el examen es de sólo lectura.** Es una omisión
concreta.

## Defecto del banco de examen — encontrado durante esta cartografía

`capability_exam._observation` y `experiment_one_step_twins._observation` construyen la ventana
perceptiva **a mano**, escribiendo los canales del objeto desde el índice 0. El formato real,
medido lado a lado:

```
OBSERVACIÓN REAL (WorldStateManager.get_observation)
  canal 0: 1.0000   ← occupancy
  canal 1: 0.8200   ← canal 0 del objeto, EL CAUSAL
  canal 2: 0.1800
  canal 3: 0.3500

MI BANCO DE EXAMEN
  canal 0: 0.8742   ← canal 0 del objeto
  canal 1: 0.1258
  canal 2: 0.3283
  canal 3: 0.2417
  (sin canal de occupancy)
```

**El examen presenta observaciones en un formato que el agente nunca vio durante el
entrenamiento.** Consecuencias, separadas con cuidado:

- La comparación **L / F / S sigue siendo internamente válida**: los tres brazos recibieron el
  mismo formato, así que `G_P ≈ 0` se sostiene como diferencia de diferencias.
- La **validez del examen como medida de la capacidad queda comprometida**: un organismo que
  hubiera aprendido la relación podría fallar este examen por formato.
- `intention_representability` **no está afectada** — opera sobre el estado del mundo y nunca
  construye observaciones.
- El aislamiento del selector (`INTERVENTION_ISOLATION = PASS`, McNemar) **tampoco**, porque es
  pareado sobre la misma cognición.

---

# XVII · Qué significa realmente «seis ejemplos informativos»

## 407-409 · Definición formal

Un paso es **informativo** cuando `|energy_delta − baseline| > 0.5`, con `baseline` el coste
declarado por paso ([run_measures._eating](terrario/lab/run_measures.py)). No es el número de
actualizaciones ni el de desenlaces no nulos: es **el número de consumos que alcanzaron algo**.

## 410-413 · Distribución medida

D4T, 300 pasos, semilla 1000042: **3 eventos** — dos perjudiciales (−1.06) y uno favorable
(+0.94). Extrapolado a 1200 pasos: ~12. El rollout cerrado dio `comidas_efectivas` con **mediana
6.0** sobre 16 semillas. [412-413] **Verificación pendiente**: no he extraído el mínimo y el
máximo por semilla del artefacto.

## 414-415 · ¿Seis ejemplos son seis actualizaciones?

**No. Seis ejemplos conviven con 1200 actualizaciones.** Medido: `update_count = 300` tras 300
pasos. `update_frequency = 1`, así que **cada paso produce un `optimizer.step()`**, informativo o
no.

## 416-422 · Pesos, tasa y regularización

```
learning_rate 3e-4 · optimizer Adam · grad_clip 1.0 (norma global)
update_frequency 1 · weight_decay: NINGUNO · regularización: sólo entropía, apagada
```

[416] Cada ejemplo pesa igual: no hay ponderación por informatividad.
[419] La norma de gradiente se registra por módulo en `grad_norms`; **verificación pendiente**: no
he extraído su magnitud típica.

## 423-426 · Qué señal domina la loss total

```
loss_total = loss_state (MSE sobre 640 dims)
           + loss_energy (MSE sobre 1 dim)
           + loss_done (BCE)
           + unc_loss (media de 5 MSE)
           + policy_loss
```

**`loss_state` domina por dimensionalidad** y `loss_energy` recibe una fracción. Y dentro de
`loss_energy`, el 99 % de los targets es **−0.06 constante**.

### Medición: lo que `energy_head` acaba siendo

Tras 600 pasos de D4T, sobre 400 sondas: **media 0.0047, desviación 0.0037**. Al nacer:
desviación 0.0035. **No se movió.** Y la cantidad que debe representar varía 2.0.

[424] **No: la señal perceptiva asociada al canal causal no recibe gradiente suficiente.** Recibe
seis muestras contra 1194 de ruido constante, en una loss donde además compite con un MSE de 640
dimensiones.

[425-426] El gradiente **sí puede trazarse** desde `energy_head` hasta el encoder: `_last_state`
conserva el grafo a través de `_build_state` → `temporal_core` → `encoder`. **Dónde se corta**:
en `_hidden`, que se detach tras el temporal core, de modo que no hay propagación a través del
tiempo.

## 427-432 · ¿Seis muestras son insuficientes para ESTA implementación?

**Hasta ahora era una inferencia, no una demostración.** Por eso existe
`scripts/experiment_learner_sample_efficiency.py`: entrega al mismo A4 un stream controlado
**fuera del mundo**, con N ejemplos informativos, construyendo las observaciones con
`WorldStateManager.get_observation` para que el formato sea el real, y mide si la cabeza de
energía discrimina sobre un banco reservado con valores de canal disjuntos.

Dos curvas: **pura** (N ejemplos seguidos) y **diluida** (los mismos N repartidos 1 de cada 100
pasos metabólicos, la densidad real de D4T). Separan «no puede aprenderlo» de «no recibe
suficientes» de «la dilución lo impide».

### Resultado de la curva pura

`artifacts/learner_sample_efficiency_pure.json` — 5 semillas, 150 sondas, azar 0.5:

```
n=6    0.492      n=96    0.507      n=768   0.483
n=12   0.493      n=192   0.561      n=1536  0.532
n=24   0.500      n=384   0.547
rango entre semillas: 0.307 – 0.693
```

**No es monótona y no se separa del azar ni con 1536 ejemplos informativos puros** — 256 veces la
exposición de una vida en D4T, sin un solo paso metabólico de por medio. La dilución queda
descartada como explicación única: el cuadrante es «ninguna aprende».

Eso desplaza la pregunta de «¿recibe bastante señal?» a «¿qué en la ruta de la señal impide que
1536 ejemplos limpios muevan la cabeza de energía?», que es lo que mide `LEARNING-SIGNAL-PATHWAY`.

*La curva diluida no llegó a correr.*

### Pasividad del examen de este script

Su `exam()` era una reimplementación local sin guardián de estado, y el `before` corría
inmediatamente antes del entrenamiento que debía medir. Medido: **puntuaciones idénticas hasta el
último dígito con y sin examen previo, en tres semillas**, porque `feed` percibe antes de decidir
y el examen nunca decide — no consume el generador ni lee la temperatura que estaba corrompiendo.
Defecto real, efecto nulo, y ahora usa el mismo guardián derivado que `sit_exam`.

---

# XVIII · Métricas e instrumentos científicos

## 433-437 · El registro

Vive en [lab/instrument_registry.py](terrario/lab/instrument_registry.py). Cada `MetricSpec`
declara: `metric_id`, `semantic_definition`, **`conditional_form`** (la expresión `P(A|B,C)`
escrita, no implícita), `numerator`, `denominator`, `conditioning_set`, `valid_domain`,
`undefined_conditions`, `expected_range`, `instrument_controls`, `version`, `exploratory`, `notes`.

**Ocho métricas registradas, las ocho `REPORTABLE`:**

| Métrica | Forma condicional |
|---|---|
| `tasa_oportunidad` | `P(O_t)` |
| `tasa_interaccion` | `P(C_t)` |
| `tasa_direccionamiento` | `P(T_t \| C_t, O_t)` |
| `conversion_aprendizaje` | `P(B_t \| T_t, C_t, O_t)` |
| `tasa_realizacion` | `P(ejecutado == pretendido \| intención válida)` |
| `contabilidad_energetica` | `P(ΔV_obs == ΔV_declarado \| sin interacción)` |
| `representabilidad_intencion` | `P(∃a ∈ A_T : Execute(s,a) realiza I \| I realizable)` |
| `examen_prediccion` | `P(E[ΔV\|fav] > E[ΔV\|desfav] \| ambas en contacto, canales nunca vistos)` |

[436] Ninguna en `DEFINED` sin calibrar. [437] Ninguna en `FAILED_CONTROL`.

## 438-440 · Métricas fuera del registro

**La mayoría.** `run_measures` produce ~20 mallas y sólo cuatro están registradas. Fuera quedan:
`pasos_vividos`, `sigue_vivo`, `energia_final`, `balance_energia`, `acciones_distintas`,
`variedad_conductual`, `indecision_media`, `actualizaciones`, `perturbaciones_vistas`,
`el_mundo_actua`, `comidas_efectivas`, `tasa_informativa`, `aciertos_al_comer`,
`mejor_tramo_al_comer`, `cambio_propio`, `colapso_politica`.

[439-440] **Sí, un script puede reportar una métrica no registrada.** `assert_reportable` existe y
**ningún script la llama**. La puerta está construida y **no está cableada**.

## 441-449 · Las cuatro semánticas

Codificadas en [lab/measurement_status.py](terrario/lab/measurement_status.py): `Status.OK`,
`NOT_EVALUABLE`, `MISSING`, `INVALID`, con `Reading` congelado y `ratio()` como constructor único.
La defensa es **estructural**: `float(reading)` levanta `NotEvaluableError` salvo que sea `OK`, y
no existe método que convierta una lectura no-OK en número.

[442] **Sí pueden perderse al serializar** si alguien escribe `reading.value` en vez de
`reading.as_record()`; `as_record()` conserva `status`, `value`, `support` y `reason`.
[443-445] **Verificación pendiente**: no he comprobado su representación en CSV, SQLite ni UI.
[446] Las conocen: `summarise`, `aggregate` en `experiment_t0_vs_t1` y `experiment_closed_loop_t`,
y `analyze_closed_loop`.
[447-448] **Sí, `mean()` las convertiría** si se le pasara `.value`; por eso los agregadores filtran
por `.evaluable` antes de promediar y **cuentan aparte** los ausentes.
[449] Cubierto por `tests/test_measurement_status.py` (10 pruebas), incluida
`test_a_non_ok_reading_refuses_to_become_a_number`.

## 450-456 · Numerador, denominador y procedencia

[450] Declaran ambos explícitamente las ocho registradas.
[451] **Reconstruyen el denominador implícitamente** las mallas no registradas de `run_measures`.
[452-453] Los 21 controles de falsación, con oráculo, anti-oráculo y caso nulo:

```
tasa_direccionamiento   perfect_targeting · never_target · t1_perfect · t1_never · uniform_random
tasa_oportunidad        empty_world · adjacent_every_step
tasa_interaccion        never_target · perfect_targeting
conversion_aprendizaje  non_learning · oracle_learner
tasa_realizacion        faithful · substituted · no_contract
contabilidad_energetica ledger_balanced · ledger_undeclared_flow
representabilidad       t0_reachable · t1_reachable · t1_blind · no_intentions
examen_prediccion       oracle · anti_oracle · tie
```

[454] **Dependen de reconstrucción de trazas**: todas las de `run_measures`.
[455] **Se registran durante la transición**: `action_contract` (la procedencia v2) y
`scientific_state`.
[456] Las segundas son **más fiables**, y la diferencia ya se materializó: el defecto de
emparejamiento pre/post-estado sólo pudo ocurrir en una métrica reconstruida.

## 457-458 · Versionado

`MetricSpec.version` existe (todas en 1) y `MEASURES_SCHEMA` versiona el conjunto.
[458] El mecanismo para evidencia histórica es `scripts/reclassify_screening.py`, que marca
`SUPERSEDED_BY_INSTRUMENT_CALIBRATION` sin borrar: **la medición se conserva, la interpretación se
retira**.

---

# XIX · Traza, ScientificFrame y evidencia

## 459-465 · Schema

`SandboxTraceStep` ([sandbox_runtime.py:58](terrario/lab/sandbox_runtime.py:58)), dataclass
congelado:

| Campo | Parte |
|---|---|
| `sandbox_run_id`, `classification`, `config_hash`, `world_definition_hash`, `world_instance_hash`, `world_seed`, `agent_seed`, `agent_identity`, `trace_schema_version` | [465] procedencia |
| `observer_world`, `world_events`, `terminated` | [461] mundo |
| `agent_observation`, `agent_action`, `agent_events` | [462] agente |
| `scientific_state` | [463] cognición |
| `agent_action.action_contract` | [464] instrumento (AC2) |

`scientific_state` ([agent/scientific.py:104](terrario/agent/scientific.py:104)) contiene
`policy_logits`, `policy_probabilities`, `policy_entropy`, `selected_action`,
`selected_action_probability`, `latent_state`, `temporal_state`, `memory_summary`, `prediction`,
`prediction_error`, `uncertainty`, `current_loss`, `gradient_norm`, `parameter_delta_norm`,
`learning_summary`, `active_ablations`.

## 466-485 · Verificación pendiente

[466-485] **No he verificado**: la identidad que une JSONL, SQLite y ScientificFrame, cuál es
autoritativa, cuándo se materializa el frame, el truncado por transporte cognitivo, CAS,
atomicidad, garantías de SSE, resync ni backpressure. Requiere leer
`observer/trace.py` (418 líneas), `observer/storage.py` (363), `observer/logger.py` (430) y
`lab/worldstream/service.py` (327). **Es la laguna más grande de esta cartografía.**

Lo que sí consta: `observer/trace.py::_connect` es un `@contextmanager` desde una reparación
previa (había conexiones SQLite filtradas), y existe una condición de carrera intermitente
`UNIQUE constraint failed: records.sequence` **no reparada**, que se evita ejecutando los
experimentos sobre el runtime directo en vez de la capa de streaming.

---

# XX · Checkpoints y persistencia

## 486-499 · Qué contiene

`CheckpointManager.save` ([observer/checkpoints.py:59](terrario/observer/checkpoints.py:59)):

```
params.safetensors     ← agent.get_parameters()
optimizer.safetensors  ← agent.get_optimizer_state()  si existe
metadata.json          ← step, saved_at, metadata
runtime_state.pt       ← random.getstate() · np.random.get_state()
                         torch.get_rng_state() · agent._generator.get_state()
                         optimizer.state_dict()
```

| | ¿Incluido? |
|---|---|
| [487] parámetros neuronales | **sí**, los 6 módulos |
| [488] optimizadores | **sí**, vía `runtime_state.pt` |
| [489] estado recurrente `_hidden` | **NO** |
| [490] memoria episódica | **NO** |
| [491] memoria persistente `M` | **sí**, es `nn.Parameter` de `longterm_memory` |
| [492] estado del world model | **sí**, son parámetros |
| [493] estado del planner | no tiene estado persistente (sólo trace) |
| [494] incertidumbre | **sí**, son parámetros |
| [495] RNG | **sí**, los cuatro |
| [496-497] lifecycle del mundo y generaciones | **NO** |
| [498] métricas acumuladas | **NO** |

**Medido**: A4 **no tiene `get_optimizer_state`**, así que `optimizer.safetensors` nunca se
escribe para A4; el estado del Adam llega sólo por `runtime_state.pt`.

[499] Quedan deliberadamente fuera los tensores no portables; queda fuera **por omisión**
`_hidden`, `_energy_baseline`, `_baseline_count`, `_step`, el buffer episódico y el estado del
mundo.

## 500-505 · Reproducción

[500] **No.** Restaurar un checkpoint de A4 **no** reproduce el siguiente timestep exactamente,
porque `_hidden` y el buffer episódico no se guardan y ambos entran en `s_t`.
[501] Las pruebas son `tests/test_checkpoint_reconstruction.py`, tres:
`restores_agent_rng_trajectory`, `restores_worldtruth_for_identical_replay` y
`reconstructs_a1_learning_trajectory_with_adam_state`. **La tercera usa A1, no A4.**
[502-503] La frontera atómica es el directorio `step_XXXXXXXX/`; no hay protección contra
checkpointar a mitad de una actualización.
[504-505] **Verificación pendiente**: versionado del formato y carga de checkpoints antiguos.

---

# XXI · Sandbox frente a ejecución científica

## 506-508 · Los dos call graphs y dónde divergen

```
SandboxService.run_bounded → .step → ._step_runtime
ExperimentController.run   → .run_episode
```

[508] **Divergen en la primera función**: no comparten ningún bucle. Ambos reconstruyen la
secuencia por su cuenta a partir de los mismos servicios.

## 509-517 · Qué comparte y qué no cada uno

| | Controller | Sandbox |
|---|---|---|
| [509] servicios comunes | `WorldStateManager`, `Physics`, `RuleEngine`, `ChangeScheduler`, `create_agent` | ídem |
| [510] física exclusiva | **`OpportunityLifecycle`** (respawn/cooldown) | — |
| [511] instrumentación exclusiva | anotaciones causales, `geometry`, ventana forense, fases | **Contrato de Acción v2** |
| [512] máquina de estados | fases del escenario | `RunState` (CREATED/RUNNING/COMPLETED/TERMINATED/FAILED) |
| [513] terminación | `alive` al inicio → `break` | `terminated` al final |
| [514] observadores | `build_scientific_state` + anotaciones | `scientific_state` |
| [515] semillas | `RNGManager.set_global_determinism(agent_seed)` | **no lo llama** |
| [516] trace writer | `step_traces[]` en memoria + observer | `SandboxTraceStep` + `storage.write` cada 50 |
| [517] checkpoints | `CheckpointManager` | ninguno |

## 518-522 · Autoridad científica

[518] Sólo desde el controller, vía `lab/execution/runtime.py` y el servicio de preregistro, puede
sellarse evidencia.
[519] `screen_concepts` → **Sandbox**. [520] P0 y P1 → **Sandbox**.
[521] World2D Live → **Sandbox**.
[522] **La ruta considerada autoritativa es la del `ExperimentController`. Ninguno de los
experimentos de esta noche corrió por ella.**

## 523-525 · Conformidad y drift

[523] **No existe ninguna prueba de conformidad entre ambos loops.** Es el hueco que P0.5 debe
cerrar.
[524] Comparten los servicios pero **no la secuencia**; el porcentaje de comportamiento
compartido exactamente hoy no está medido y no puede estarlo sin esa prueba.
[525] Fuentes potenciales de drift: `_find_target` duplicado, el orden physics/target, la base de
la semilla de física, el gate de aprendizaje y la ausencia de lifecycle.

---

# XXII · Preregistro y evidencia

## 526-534 · Estructura y estados

[lab/preregistration/domain.py](terrario/lab/preregistration/domain.py), 648 líneas, todo en
dataclasses congelados con `frozen_mapping`.

**Máquina de estados del preregistro:**

```
DRAFT → READY_FOR_REVIEW → REVIEW_IN_PROGRESS → REVIEWED → PREREGISTERED_LOCKED
                                                        ↘ SUPERSEDED / WITHDRAWN
```

**Decisiones de revisión**: `APPROVE_PREREGISTRATION`, `APPROVE_FOR_EXPERIMENT_DESIGN`,
`REQUEST_CHANGES`, `REJECT`.

[534] **La distinción exploratorio/confirmatorio es de primera clase**: `StudyIntent` ∈
{`EXPLORATORY`, `CONFIRMATORY`, `REPLICATION`, `ABLATION`, `STRESS_TEST`, `METHOD_VALIDATION`},
`CausalMode` ∈ {`CAUSAL`, `DESCRIPTIVE_ONLY`}, `EndpointRole` ∈ {`PRIMARY`, `SECONDARY`,
`DIAGNOSTIC`, `EXPLORATORY`}, y `Partition` ∈ {`TRAIN`, `DEVELOPMENT`, `EXPLORATORY_TEST`,
`CONFIRMATORY_TEST`, `TRANSFER`, `HOLDOUT`}.

[528-529] Se congela al pasar a `PREREGISTERED_LOCKED`. Después sólo cabe enmienda o desviación.

## 530-532 · Enmiendas y desviaciones

`DeviationType` ∈ {`PROTOCOL_DEVIATION`, `SEED_DEVIATION`, `METRIC_DEVIATION`,
`OBSERVER_DEVIATION`, `ANALYSIS_DEVIATION`, `ENVIRONMENT_DEVIATION`, `EXCLUSION_DEVIATION`}.

[532] La diferencia: una **enmienda** cambia el protocolo **antes** de ejecutar y se somete a
revisión; una **desviación** registra que la ejecución **no siguió** el protocolo bloqueado.

Existe además un sistema de **exposición** que no había visto en ningún otro laboratorio de este
tamaño: `ExposureKind` ∈ {`PREVIEWED`, `SANDBOXED`, `INSPECTED`, `ANALYZED`,
`MANUAL_DECLARATION`} y `ExposureStatus` ∈ {`UNEXPOSED`, `PREEXPOSED`, `POSTLOCK_EXPOSED`,
`CONTAMINATION_REVIEW_REQUIRED`}. Registra si alguien **miró los datos** antes de bloquear.

`FindingSeverity` ∈ {`STRUCTURAL_ERROR`, `SCHEMA_ERROR`, `INTEGRITY_ERROR`, `REFERENCE_ERROR`,
`SCIENTIFIC_WARNING`, `EXPOSURE_WARNING`, `RESOURCE_WARNING`}.

## 535-544 · Sellado y hashes

[541] El gate humano que bloquea hoy: `tests/test_system_baseline_characterization.py::
test_protected_source_and_historical_artifact_hashes_match_baseline`, contra
`tests/fixtures/system_baseline_02/`.
[542] Exige regeneración **cualquier cambio a una fuente protegida** — y `a4_advanced.py` lo es,
por eso ese test lleva fallando toda la noche, deliberadamente.
[543] **No deberían exigirla** los cambios a instrumentos de laboratorio, scripts y documentación.
[544] La procedencia de evidencia reinterpretada se preserva con `reclassify_screening.py`, que
escribe `.reclassified.json` junto al original y estampa `rng_mechanism` y `batch_note`.

[536-540] **Verificación pendiente**: qué cubren exactamente los hashes (código, configuración,
métricas, tests) requiere leer `lab/evidence_publication.py` y las fixtures de baseline.

---

# XXIII · Ablaciones y composición

## 545-551 · Cómo se construye un agente con flags

`lab/agent_composition.py::validate_selection` es **fail-closed**: rechaza una clave desconocida en
vez de descartarla en silencio. Tres familias de clave:

```
_KEYS          los 10 use_*      deben ser bool
_TUNING_KEYS   numéricos         validados contra [minimum, maximum]
_CHOICE_KEYS   addressing_mode   validado contra dominio enumerado
```

[546] **Las ablaciones NO eliminan módulos: los dejan construidos y cortan su ruta.**
[547] Los downstream reciben **ceros** de la misma dimensión.
[548] **No cambian dimensiones**: `_build_state` siempre devuelve 640.
[549-550] **Sí cambia el número de parámetros entrenables**, porque `parameter_count` cuenta sólo
`requires_grad`, y **sí cambia qué módulos entran al optimizador**: `learnable_modules` se
construye condicionalmente. Un agente sin memoria de largo plazo tiene un Adam distinto.
[551] Cambian rutas de control: las ramas `if self._use_*`.

## 552-554 · Ablaciones que no son intervenciones locales

[552] **Sí, hay una, y es grave**: `use_world_model=False` **también desactiva el planificador**,
porque la rama exige ambos flags. Medido: 0 de 40 llamadas a `planner.plan`.
[553] Activan fallback: `use_temporal` → ceros, `use_episodic_memory` → ceros,
`use_longterm_memory` → ceros, `use_homeostasis` → temperatura 1.0, `use_planner` /
`use_world_model` → `policy_head.sample`.
[554] **Interacciones implícitas**: `use_planner × use_world_model` (la misma rama);
`use_uncertainty × use_world_model` (la loss de incertidumbre exige ambos).

## 555-559 · Baseline y compartición

[555-556] La baseline es la configuración por defecto; la misma inicialización se garantiza con
`torch.manual_seed(seed)` antes de `create_agent`, y en P1 además **verificando el hash**.
[557] **Comparten parámetros**: las tres cabezas del world model comparten backbone.
[558] **Comparten optimizador**: un único Adam sobre todo.
[559] **Sí, una ablación puede modificar gradientes de un módulo supuestamente intacto**, por dos
vías: el Adam es global —quitar parámetros cambia el estado del optimizador— y las losses se suman
sin pesos, así que eliminar `unc_loss` cambia la magnitud total que retropropaga al backbone
compartido, al encoder y al temporal core.

## 560-565 · Los efectos fuertes, explicados

[560-562] **Son el mismo efecto.** Ambas ablaciones eliminan la misma ruta: la inyección de la
acción del planner en el 50 % de los pasos. Y como `energy_head` es constante (§VIII), esa acción
es **casi uniforme**: el planner no planifica, **explora**. Quitarlo deja sola a una política
colapsada, y una política colapsada no come.

[563-564] Las conjunciones del corpus, con sus flags exactos:

```
sin:nucleo_lecun      (use_world_model, use_longterm_memory, use_planner)
sin:memoria_completa  (use_episodic_memory, use_longterm_memory)
sin:anticipacion      (use_world_model, use_planner)
```

[565] **Modificación indirecta**: `anticipacion` elimina **exactamente la misma ruta** que
cualquiera de sus dos componentes por separado, lo que explica su residuo −6.67 sin necesidad de
invocar interacción alguna. `nucleo_lecun` hereda lo mismo más la memoria.

---

# XXIV · Tests

## 566-575 · Distribución

**152 ficheros, 711 pruebas, 1 omitida, 1 fallando** (el gate de hashes protegidos).

| Subsistema | Ficheros |
|---|---|
| lab | 10 |
| api | 6 · experiment 6 · world 6 |
| observer 5 · metric 5 | |
| agent 4 | |
| sandbox 3 · preregistration 3 · opportunities 3 | |
| a4 2 · trace 2 · measure 2 · reproducibility 2 | |
| storage · checkpoint · instrument · calibration · action_contract · selector · baseline · composition · screening | 1 c/u |

[567-570] **Verificación pendiente**: el desglose unitaria / integración / end-to-end exige
clasificar las 711 una a una. Los **controles científicos** sí están contados: **21** de
falsación de instrumento, más 22 de contrato de acción y 12 de paridad de selector.

[573-575] Ejercitan `SandboxService` 3 ficheros; `ExperimentController`, los de `experiment`.
**Ninguno ejercita ambos sobre el mismo escenario** — [523] de nuevo.

## 576-586 · Qué falta

[576] **Sin test**: el examen de P1 como sólo lectura [406]; la conformidad entre loops [523];
que una predicción del world model cambie la elección del planner [212]; el round-trip de
checkpoint para **A4** [501].
[579] Dependen de hashes exactos: `test_system_baseline_characterization.py`.
[580-581] La omitida es `test_agent_factory.py:35`, con
`@pytest.mark.skipif(not torch.cuda.is_available())` — **no hay CUDA en esta máquina**.
[582] Contra el riesgo de que un test verde replique la implementación defectuosa, la respuesta
del repositorio son los **controles con respuesta analítica conocida**: [583] el más fuerte es
`uniform_random_agent` → **0.0400 teórico contra 0.0404 medido**.
[584] Usan oráculo: `oracle_learner`, `exam_oracle`, `perfect_targeting_agent`,
`t1_perfect_targeting_agent`, `realization_faithful`, `ledger_balanced`.
[585] **Faltan controles negativos** para las ~16 mallas de `run_measures` fuera del registro.
[586] **No hay tests metamórficos** de ningún tipo.

---

# XXV · Rendimiento

## 587-593 · Dónde se van los segundos

**Coste por decisión**, medido aislando módulos (5 semillas, 100 decisiones):

```
A4 completo            39.04 ms
sin planner            22.21 ms     → el planner cuesta 16.8 ms  (43 %)
sin incertidumbre      22.42 ms     → incertidumbre cuesta 16.6 ms (43 %)
sin ambos               3.15 ms     → todo el resto del agente: 8 %
```

La razón es aritmética y está en el código:
- **planner**: 10 candidatos × 5 pasos de horizonte = **50 pasadas del world model por decisión**.
- **incertidumbre**: 25 acciones × 5 cabezas del ensemble = **125 pasadas por decisión**.

**Reparto por fase del timestep** (proporciones firmes; los absolutos estaban contaminados por
carga en paralelo):

```
learn (backward + Adam)    ~72 %
decide (forward)           ~27 %
perceive (encoder)         ~1 %
physics.step               ~0.03 %
get_observation            ~0.01 %
serialize (traza)          ~0.002 %
```

[589-593] **El mundo, el logging, las métricas, la serialización y el observador juntos no llegan
al 0.1 %.** El coste es **enteramente la red neuronal**. Un perfilado previo ya había eliminado el
coste cuadrático de la traza (`storage.write` por paso, 18 min → 2.4 min) con la cadencia de
snapshot cada 50 pasos.

## 594-596 · Vectorización y coste cuadrático

[594] Vectorizables por lotes: las 25 evaluaciones de incertidumbre y los 10 rollouts del planner
—hoy son **bucles Python**—.
[595] Estrictamente serial por dependencia causal: la recurrencia del temporal core y la secuencia
percibir→decidir→actuar.

[596] **Sí, hay un O(n²) inadvertido**, y no es con objetos sino con memoria:

```python
stored = torch.stack([e["embedding"] for e in self._buffer])   # memory.py:98
similarities = (query_norm @ stored_norm.T)
```

`EpisodicMemory.read` **apila el buffer entero en cada lectura**, y se lee una vez por decisión.
Con capacidad 1000 y 1200 pasos, el coste acumulado crece cuadráticamente hasta el tope.

## 597-605 · Escalar semillas

[601] `torch.get_num_threads() = 6` — **no es single-thread**, así que varias semillas en paralelo
compiten entre sí. Lo observé directamente esta noche: seis suites acumuladas hicieron que una
corrida de 1200 pasos pasara de 95 s a más de 110 s.
[602] **Sí pueden ejecutarse en procesos separados**: cada corrida construye su propio agente,
mundo y RNG. Lo que **impide paralelizar con seguridad** [603] son las **rutas globales de
escritura**: cada `Bench` escribe en un directorio `.sandbox-<nombre>` fijo, compartido entre
semillas del mismo script.
[604-605] **Verificación pendiente**: no he buscado locks ni temporales compartidos.

**Defecto encontrado durante esta cartografía:** esos directorios `.sandbox-*` **no están en
`.gitignore`**, que sólo cubre `.sandbox/`. Cuatro commits de esta noche versionaron **~1.2 GB**
de datos regenerables; `.git` pesa 339 MB. El arreglo no destructivo es añadir `.sandbox-*/` y
`git rm -r --cached`; los blobs quedan en la historia hasta una reescritura.

---

# XXVI · Qué es A4, sin los nombres

## 606 · El algoritmo, despojado

> **A4 es un actor-crítico sin crítico.**
>
> Un encoder convolucional produce un latente de 128. Una recurrencia lineal diagonal produce un
> hidden de 256. Dos memorias —una búsqueda por coseno sobre un buffer circular y una matriz con
> atención— producen 128 + 128. Los cuatro se concatenan en un vector de 640.
>
> Sobre ese vector, un `Linear(640→25)` produce logits. Un ensemble de cinco MLP los sesga en 0.1
> por su varianza. La temperatura es `1 + (1 − energía normalizada)`.
>
> En paralelo, un MLP de dos capas predice el siguiente estado, el delta energético y la
> terminación. Un buscador aleatorio sortea diez secuencias de cinco acciones, las puntúa con ese
> MLP y devuelve la primera de la mejor. **Una moneda decide si manda el buscador o la política.**
>
> Cada paso, un único Adam minimiza la suma **sin pesos** de: MSE de estado (640 dims), MSE de
> energía (1 dim), BCE de terminación, MSE del ensemble, y REINFORCE con baseline de media móvil.
>
> No hay buffer de repetición, ni descuento, ni retorno a n pasos, ni trazas de elegibilidad, ni
> propagación a través del tiempo.

## 607-614 · Qué es cada componente

| | Componentes |
|---|---|
| [607] neuronales | encoder, temporal core, world model, ensemble de incertidumbre, policy head, proyecciones de la memoria de largo plazo |
| [608] simbólicos | ninguno |
| [609] reglas manuales | `plan_prob = 0.5`, `−10.0·done`, `+0.1·varianza`, `temperature = 1 + bias`, umbral homeostático 0.5 |
| [610] heurísticas | random shooting, top-k por coseno, escritura con puerta sigmoide |
| [611] **aprenden** (gradiente) | encoder, temporal core, world model, incertidumbre, policy head, proyecciones de LT memory |
| [612] **sólo acumulan estado** | buffer episódico, matriz `M`, `_hidden`, homeostasis, `_energy_baseline` |
| [613] planifican | `Planner`, y sólo por sorteo |
| [614] seleccionan | `policy_head.sample`, `torch.multinomial`, y la moneda del planner |

## 615-622 · Creencias, hipótesis y lo que ya no está

[615-616] **No existe ninguna creencia con confianza asociada.** Lo más cercano es la varianza del
ensemble, que no está calibrada y cuyo «alto» no tiene significado numérico declarado.
[617] **No existe ninguna hipótesis** en el agente. Las hipótesis viven en el laboratorio.
[618] `prediction_error = |energy_pred − energy_delta|`, calculado en `learn` bajo `no_grad` y
**registrado, nunca consumido**.
[619] **No hay actualización bayesiana** de ningún tipo.
[620] **No hay MDL** en `terrario/agent/`.
[621] **No hay EIG.** La exploración es la varianza del ensemble sumada a los logits con
coeficiente 0.1 — no es ganancia de información esperada.
[622] Por tanto: **de Bayes, MDL y EIG no queda nada en A4.** Si la descripción histórica los
menciona, describe algo que el código no hace.

## 623-628 · Emergente, programado, y qué puede adquirir

[623] **Programado explícitamente**: todo lo enumerado arriba.
**Emergente**: el colapso de la política, el uso de PUSH como medio principal de locomoción
(158 de 300 pasos), y el papel del planner como fuente de exploración.

[624] **Qué puede decidir A4 que A0 no puede representar**: condicionar la acción al contenido
perceptivo. A0 sortea uniformemente; A4 tiene una distribución que **depende del estado**. Es una
diferencia real de expresividad, y el tamizado la confirma: A4 completo come ~6.7 y sin planner
~0, mientras A0 come ~10 de 16 en las mismas condiciones. **A4 puede representar más que A0 y
rinde peor que A0.**

[625] **Qué conocimiento puede adquirir**: en principio, la relación canal→consecuencia, vía
`energy_head`. **Medido: no la adquiere.** Desviación 0.0037 tras entrenar, contra 0.0035 al
nacer, sobre una cantidad que varía 2.0.

[626] **Evidencia en código y tests de que lo adquirido persiste**: sólo
`test_checkpoint_reconstruction`, y sobre A1.
[627] **Evidencia de transferencia**: ninguna. El banco `decorrelated` de P1 existe para medirla y
dio `G ≈ 0`.
[628] **Evidencia de metaaprendizaje**: ninguna; P6 no está construido.

## 629-630 · Nombres que mienten

**Sobrestiman lo que hacen:**

| Nombre | Lo que hace realmente |
|---|---|
| `Planner` | sortea 10 secuencias al azar y las puntúa con un modelo que no predice nada |
| `UncertaintyEstimator` | varianza de 5 cabezas entrenadas con la misma loss sobre el mismo target |
| `WorldModel` | tres cabezas sobre un MLP; la de energía es constante |
| `LongTermMemory` | matriz con atención cuyo contenido no recibe gradiente |
| `HomeostaticState.update()` | se sobrescribe antes de leerse; sólo alimenta el trace |
| `_handle_inspect` | devuelve una cadena constante; su docstring promete un sistema que no existe |
| `use_temporal` | recurrencia real, pero ninguna tarea actual exige historia |

**Subestiman lo que son:**

| Nombre | Lo que es realmente |
|---|---|
| `validate_selection` | una puerta fail-closed con tres dominios de tipo distintos |
| `world_contracts.py` | el sellado de la superficie de observación, con excepción tipada |
| `measurement_status.py` | imposibilita estructuralmente coaccionar ausencia a cero |
| `_stream` en `opportunities` | desacopla el azar exógeno de la conducta del organismo |
| `preregistration/domain.py` | registro de exposición que detecta si alguien miró los datos antes de bloquear |

---

# XXVII · Causalidad del comportamiento actual

## 631-635 · Las cinco trayectorias, función a función

**[631] Comida beneficiosa**

```
get_observation → perceive → encoder → temporal_core → episodic.read → longterm.read
→ _build_state(640) → policy_head → +0.1·incertidumbre → /temperatura
→ [moneda] planner.plan(50 pasadas) ó policy_head.sample
→ Action(CONSUME, dir)
→ [banco] perceive_targets → resolve → VALID → target_id
→ physics._handle_consume → "consume_pending_obj_N"
→ rules.evaluate → canal0 ≥ 0.7 → apply_effects: +1.0, remove_object
→ apply_step_energy_cost: −0.06  ⇒  delta = +0.94
→ homeostasis.update(+0.94) [sólo trace]
→ episodic.write(latente, acción, +0.94, error)
→ longterm.write(h, h) bajo no_grad
→ world_model.loss(estado, energía=+0.94, done)
→ advantage = 0.94 − baseline ≈ +1.0  ⇒  policy_loss = −log π(a)·1.0
→ unc_loss: 5 cabezas hacia +0.94
→ Adam.step sobre los 6 módulos
```

**[632] Comida perjudicial**: idéntico salvo `canal0 ≤ 0.3 → −1.0`, delta −1.06, advantage ≈ −1.0,
y el signo de `policy_loss` invertido.

**[633] `NONEXISTENT`** y **[634] `OUT_OF_RANGE`**: `rules.evaluate` devuelve `[]`
—no hay objeto, o no es adyacente—, `apply_effects` no se llama, delta = **−0.06**.
Todo lo demás ocurre igual: memoria, losses, Adam.

**[635] NOOP**: `physics` emite `"noop"`, delta = **−0.06**. Igual que los dos anteriores.

> **Los tres últimos son idénticos para el organismo.** El mundo no devuelve ninguna señal que
> separe «apunté a nada» de «apunté a algo inalcanzable» de «no hice nada». La descomposición de
> desperdicio de §P0 existe **en el instrumento**, no en la experiencia.

## 636-640 · Qué experiencia altera más qué

[636] **Parámetros**: una comida —favorable o perjudicial—, porque el advantage se aparta del
baseline en ~1.0 en vez de ~0.
[637] **Memoria**: todas por igual; el buffer episódico escribe en cada paso sin filtro.
[638] **World model**: una comida, por el mismo motivo (`energy_target` ±1 en vez de −0.06).
[639] **Política**: una comida.
[640] **Estado del planner**: ninguna — **el planner no tiene estado persistente**.

## 641-645 · El primer cambio interno

[641] El primer cambio que podría explicar una decisión futura distinta es la **escritura en el
buffer episódico**, que ocurre antes que cualquier paso del optimizador y **sin depender de él**.
[642] Sobrevive el timestep. [643] Sobrevive el episodio (capacidad 1000 > 1200 pasos con
sobrescritura mínima). [644] **NO sobrevive al checkpoint** [490].
[645] Lo lee `_build_state` en la decisión siguiente, vía `episodic_memory.read(latent, k=5)`.

## 646 · La cadena `write → storage → read → efecto`

| Tipo | write | storage | read | ¿efecto conductual? |
|---|---|---|---|---|
| episódico | `learn` | `_buffer` | `_build_state` | **sí**, vía `s_t` |
| largo plazo | `learn` | `M` | `_build_state` | **sí**, vía `s_t` |
| paramétrico | `Adam.step` | pesos | todo forward | **sí**, en principio |
| recurrente | `decide` | `_hidden` | `_build_state` | **sí** |
| homeostático | `perceive` | `_energy` | temperatura | **sí** |
| `prediction_error` | `learn` | `last_prediction_error` | **nadie** | **no** |
| `energy_delta` y `prediction_error` en el episodio | `episodic.write` | buffer | **nadie los lee** | **no** |

## 647-649 · Lo escrito y nunca leído

[647] **Estado escrito que nunca se lee:**
- `action`, `energy_delta`, `prediction_error` y `timestamp` en cada entrada episódica: se
  almacenan y la recuperación es **puramente por coseno del embedding**. Cuatro de los cinco
  campos son inertes.
- `HomeostaticState._energy` acumulado por `update()`: lo sobrescribe `perceive`.
- `last_prediction_error` y `_last_prediction`: sólo trace.
- `Planner` `all_rollouts` y `best_score`: sólo trace.

[648] **Salidas calculadas que nunca influyen en acciones**: `next_state_head` fuera del rollout
interno, `done_head` fuera de la puntuación del planner, `prediction_error`, y **la varianza del
ensemble cuando `use_uncertainty=False`** —se sigue construyendo el módulo—.

[649] **Módulos conectados nominalmente y sin efecto causal efectivo hoy**:
- `energy_head` **sobre la conducta**: su salida entra al planner, pero su dispersión (0.0035) es
  2.4 veces menor que la del `done_head` ponderado, y ambas son ruido.
- `SSMCore`: ocupa 256 de 640 dimensiones y ninguna tarea exige historia.
- `INSPECT`: 53 de 300 pasos gastados en una operación sin efecto alguno.

---

# XXVIII · Deuda y contradicciones

## 650-653 · Documentación que ya no describe el código

- `_handle_inspect`: *«The observation system handles the increased detail separately»* —
  **no existe tal sistema**.
- `Physics.step`: el parámetro `rng` se documenta como *«currently unused but available for future
  stochastic physics»* — correcto, pero ambos loops construyen un `RNGManager` completo por paso
  para nada.
- `HomeostaticState`: *«Energy is normalized to [0,1]»* y `update()` suma deltas absolutos; en la
  práctica `perceive` lo sobrescribe con el valor normalizado, así que el contrato se cumple **por
  accidente**.
- `sit_exam`: afirmaba no mutar al agente y mutaba siete variables. Corregido hoy.
- [652] `opportunity_lifecycle` en D4T: **declarado e ignorado** por el runtime que ejecuta todos
  los experimentos.
- [653] `use_temporal`: cambia comportamiento, pero **ninguna tarea actual lo requiere**.

## 654-656 · Código muerto e inalcanzable

- `policy_head.greedy`: existe, A4 no lo llama.
- `EpisodicMemory.reset`, `LongTermMemory.reset_memory`, `HomeostaticState.reset`,
  `OnlineLearner.reset`: **ningún loop los llama**.
- `SelectorType.RELATION`: reservado, levanta `NotImplementedError` — inalcanzable **a propósito**.
- La rama omnisciente `truth.objects.get(action.target_id)` en `controller._find_target`:
  **inalcanzable**, porque nada escribe `target_id` en esa ruta.

## 657-667 · Fallos que se convierten en números plausibles

[657-658] `try/except` alrededor de lógica científica:
- `OnlineLearner.step`: captura loss o gradiente no finitos y **devuelve `None` en silencio**,
  registrando `learning_skipped_nonfinite` en el trace. Un paso sin actualizar es indistinguible
  de uno actualizado salvo que alguien lea ese trace.
- `LongTermMemory.write`: `nan_to_num` y `clamp(±10)` **antes** de escribir, y descarta la
  escritura si el resultado no es finito, con `write_accepted: False` en el trace.
- `action_contract._visible`: `except (IndexError, TypeError): return True` — **una máscara
  malformada hace visible todo**.

[659-663] **Fallos que terminan como cero, lista vacía o NOOP:**
- `RuleEngine.evaluate` con `target_object is None` → `[]` → delta 0.0. Un CONSUME que no alcanzó
  nada y un NOOP son el mismo número.
- `Action` con `direction=NONE` → `DIRECTION_DELTA[NONE] = (0,0)` → **MOVE se vuelve NOOP en
  silencio**.
- `_find_target` devuelve `None` en cinco caminos distintos, todos indistinguibles aguas abajo.
- `_agents(step)` devuelve `{}` si no hay agentes; `entidades(x)` devuelve `[]`.

[664] **`or 0`, `or []`, `get(..., default)` en rutas científicas**: abundantes en `run_measures`
—`(step.get("observer_world") or {})`, `.get("agents") or {}`, `tuple(step.get("agent_events") or ())`—
y en `sandbox_runtime`. Son defensivos y **ocultan la diferencia entre ausencia y vacío**.

[665] **Dónde puede `None` adquirir semántica numérica**: en `run_measures`, un `Measure` con
`evaluable=False` lleva `value=None` y `reason=NOT_EVALUABLE`; cualquier consumidor que lea
`m["value"]` sin mirar `evaluable` obtiene `None`, y `sum`/`mean` sobre eso falla o —si alguien lo
filtra con `or 0`— **se convierte en cero**.

[666-667] **Rutas que todavía pueden violar la semántica nueva**: las ~16 mallas de
`run_measures` fuera del registro, que usan el par `(value, evaluable, reason)` en vez de
`Reading`, y toda la capa de persistencia y UI, **no verificada** [443-445].

---

# XXIX · Arquitectura futura

## 668-669 · Contratos estables y contratos atados a D4T

**Suficientemente estables para Genesis**: `AgentInterface` (`perceive`/`decide`/`learn`),
`Transition`, `Observation`, `TemporalCore`, `WorldDefinition` como representación hasheable,
`Reading` y la máquina de estados del instrumento, `ActionIntent`/`Resolution`/`ActionProvenance`.

**Atados a D4T**: `TOTAL_ACTIONS = 25` incrustado en `policy_head`, `world_model`,
`uncertainty_estimator` y `Planner`; `num_channels=4`; `view_size=5`; el umbral 0.7/0.3 de las
reglas; los valores 0.82/0.18 de las plantillas.

## 670-679 · Supuestos incrustados

| Supuesto | Dónde |
|---|---|
| [670] rejilla 2D | `Position(x,y)`, `occupancy` como `ndarray` 2D, `DIRECTION_DELTA`, `get_observation` |
| [671] cinco direcciones | `NUM_DIRECTIONS`, `to_int`/`from_int`, `direction_head`, `DIRECTION_DELTA` |
| [672] objetos discretos | `ObjectSpec`, `objects: dict[int, ...]`, `perceive_targets` |
| [673] recompensa escalar | `energy_delta: float` en todo `Consequence`, `energy_head` de 1 dim, el baseline de REINFORCE |
| [674] episodios finitos | `max_duration`, `truncated`, `done_head` |
| [675] **un solo agente** | `agent_id=0` **literal** en `_step_runtime`, `_find_target`, `perceive_targets`, `sit_exam`, `_cadena`, `run_measures._agents` |
| [676] soportarían varios sin cambios | `Physics.step` (itera `sorted(actions.keys())`), `WorldState.agents` (es un dict), `RuleEngine` |
| [677] memoria atada a ranuras | **no**: las memorias indexan por embedding y por atención, no por ranura perceptiva |
| [678] planner atado al espacio de acción | **sí**: `torch.randint(0, TOTAL_ACTIONS, ...)` |
| [679] world model atado a dimensiones | **sí**: `action_dim = TOTAL_ACTIONS`, `state_dim = 640` |

## 680-687 · Fronteras

[680] **Cambiar mundo sin cambiar agente**: hoy es posible mientras el nuevo mundo produzca
`Observation(channels, mask, agent_energy, time_fraction)` con la misma forma y acepte `Action`.
El cuello es `TOTAL_ACTIONS`.
[681] **Cambiar agente sin cambiar laboratorio**: casi. El obstáculo concreto es
`agent_composition` importando `DEFAULT_CONFIG` de `a4_advanced`, que hace que el catálogo de
conceptos **sea** el de A4.
[682] **Añadir capacidades sin crear otro runtime**: hoy no hay mecanismo; cada capacidad nueva de
esta noche —AC2, bancos exógenos, gemelos de un paso— **añadió código al banco**.

[683] **El límite entre «ser» y «mundo»** es nítido y está en `Observation` / `Action`, sellado por
`AGENT_FIELDS` y `OBSERVER_ONLY_FIELDS` con excepción tipada.
[684] **El límite entre «ser» e «instrumentación»** es nítido **en una dirección**: el agente no
importa nada del laboratorio [685: **no, ningún sitio**]. En la otra **no lo es** [686: **sí**]:
`agent_composition → a4_advanced.DEFAULT_CONFIG`, `agent_inspector → agent.agents`,
`sandbox_runtime → agent.scientific` y `agent.agents`, `execution.runtime → agent.scientific`.

[687] **El acoplamiento que impediría probar otra arquitectura bajo los mismos experimentos** es
ése: el catálogo de conceptos, la validación de composición y por tanto todo el tamizado están
escritos contra la configuración concreta de A4.

---

# XXX · Las preguntas más importantes

## 688 · El único call graph real de un timestep de A4, de mundo a mundo

```
┌─ MUNDO ────────────────────────────────────────────────────────────────┐
│ WorldStateManager.get_observation(0, view_radius=2, num_channels=4)     │
│   obs[0]=occupancy · obs[1..3]=canales 0..2 del objeto · mask · energía │
└────────────────────────────────────────────────────────────────────────┘
                                   ↓ Observation (127 valores)
┌─ SER ──────────────────────────────────────────────────────────────────┐
│ perceive: encoder(obs.channels) → latente(128)                          │
│           homeostasis._energy = obs.agent_energy      [asignación]      │
│ decide:   temporal_core(latente, h) → h(256)                            │
│           episodic.read(latente, k=5) → 128    [O(n) sobre el buffer]   │
│           longterm.read(h)           → 128                              │
│           s_t = concat(128, 256, 128, 128) = 640                        │
│           logits = policy_head(s_t)                          (25)       │
│           logits += 0.1 · var(ensemble)          [125 pasadas]          │
│           T = 1 + (1 − energía)                                         │
│           moneda 0.5 → planner.plan  [50 pasadas]  ó  policy.sample     │
│           → Action(operación, dirección)                                │
└────────────────────────────────────────────────────────────────────────┘
                                   ↓ Action
┌─ SÓLO EN EL BANCO ─────────────────────────────────────────────────────┐
│ perceive_targets → resolve → target_id sólo si VALID → ActionProvenance │
└────────────────────────────────────────────────────────────────────────┘
                                   ↓
┌─ MUNDO ────────────────────────────────────────────────────────────────┐
│ scheduler.check(step)                    [puede invertir las reglas]    │
│ lifecycle.advance(step)                  [SÓLO ExperimentController]    │
│ physics.step → _handle_* → move_agent/move_object → advance_time()      │
│ _find_target → rules.evaluate → apply_effects → ±1.0, remove_object     │
│ lifecycle.consume(...)                   [SÓLO ExperimentController]    │
│ apply_step_energy_cost(0) → −0.06                                       │
│ get_observation → obs_{t+1}                                             │
└────────────────────────────────────────────────────────────────────────┘
                                   ↓ Transition
┌─ SER ──────────────────────────────────────────────────────────────────┐
│ learn: homeostasis.update(delta)           [sobrescrito antes de leerse]│
│        episodic.write(latente, acción, delta, error)                    │
│        longterm.write(h, h)                [no_grad]                    │
│        world_model.loss(estado 640, energía, done)                      │
│        advantage = delta − baseline; policy_loss = −log π(a)·advantage  │
│        unc_loss = media de 5 MSE                                        │
│        Adam.step sobre los 6 módulos       [CADA PASO, sin excepción]   │
└────────────────────────────────────────────────────────────────────────┘
```

## 689 · Autoridad por estado

| Estado | Autoridad | Escape |
|---|---|---|
| mundo | `WorldStateManager` (12 métodos) | `_mutable_state()` en **38 sitios** |
| reglas | `RuleEngine` (`_version`) | `ChangeScheduler` las reemplaza |
| oportunidades | `OpportunityLifecycle` | existe sólo en una de las dos rutas |
| parámetros | `OnlineLearner` (un Adam) | `M` se escribe fuera, bajo `no_grad` |
| recurrente | `A4._hidden` | — |
| memoria episódica | `EpisodicMemory._buffer` | — |
| azar del mundo | clave `(seed, kind, root, generation)` | — |
| azar del agente | `torch.Generator` + **RNG global** para pesos | el global no está controlado por el banco |
| traza | `SandboxTraceStep` / `step_traces` | dos formatos distintos |

## 690 · Todos los lugares donde se muta estado en un timestep

**Mundo** (7): `scheduler.check` → `set_rules_version`; `lifecycle.advance` → `add_object`;
`physics._handle_move/_handle_push` → `move_agent`/`move_object`; `physics.step` →
`advance_time`; `rules.apply_effects` → `remove_object`/`set_object_channels`/`set_agent_energy`/
`set_agent_alive`; `lifecycle.consume` → `_pending`, `_lineage`, `_recent_positions`;
`apply_step_energy_cost` → energía.

**Agente** (9): `_last_latent`, `homeostasis._energy`, `_hidden`, `_last_state/_action/_log_prob/
_logits/_probs/_uncertainty`, `_step`, `episodic._buffer`, `longterm.M`, `_energy_baseline`,
parámetros vía Adam.

## 691 · Qué ve A4 y qué no ve nunca

**Ve** (127 valores): 4×5×5 canales —occupancy y los canales 0..2 del objeto, promediados por
celda—, la máscara 5×5, su energía normalizada, y `time_fraction` (**0.0 en D4T**, porque
`expose_time_fraction: false`).

**No ve nunca**: posiciones absolutas, identificadores de objeto, `opportunity_id`, linaje,
generación, las reglas, `rules_version`, `energy_value`, `causal_property`, el canal 3 del objeto
(truncado), nada fuera de la ventana 5×5, ni ninguna señal que distinga `NONEXISTENT` de
`OUT_OF_RANGE` de NOOP.

## 692 · Qué aprende `_use_online_learning`, y con qué gradiente

Un único `Adam(lr=3e-4, grad_clip=1.0)` sobre los seis módulos, minimizando **cada paso**:

```
MSE(next_state, 640 dims) + MSE(energy, 1 dim) + BCE(done) + media de 5 MSE + (−log π(a)·A)
```

El gradiente llega al encoder y al temporal core porque `_last_state` conserva el grafo. **Se
corta en `_hidden`**, que se detach — no hay propagación a través del tiempo. `advantage =
delta − media_móvil(delta)`, y con el 99 % de los deltas en −0.06, el advantage de esos pasos
tiende a cero **sin ser cero**, 1194 veces contra 6.

## 693 · Dónde queda cada tipo de conocimiento

```
perceptivo      → pesos del encoder            gradiente
temporal        → pesos del SSM + _hidden      gradiente + estado
episódico       → _buffer (1000)               SIN gradiente
asociativo      → matriz M (64×128)            SIN gradiente, escrita bajo no_grad
predictivo      → world_model                  gradiente
de acción       → policy_head                  gradiente
de incertidumbre→ 5 cabezas                    gradiente
metabólico      → _energy_baseline             SIN gradiente
```

**Cuatro de los ocho no dependen del optimizador**, y los cuatro siguen vivos en el gemelo
congelado de P1. Por eso `G` aísla específicamente la contribución paramétrica.

## 694 · Quién usa después ese conocimiento

Todo converge en `_build_state` → `s_t`(640) → `policy_head` y `world_model`. **`s_t` es el único
cuello de botella cognitivo del organismo.** Nada influye en la acción sin pasar por él, salvo la
temperatura homeostática y la moneda del planner.

## 695 · Predicciones con efecto conductual y predicciones decorativas

| Predicción | Consumidor | ¿Efecto? |
|---|---|---|
| `energy_head` | planner | **nominal** — su dispersión es 0.0035, y ponderada pesa 2.4× menos que `done` |
| `done_head` | planner | **sí**, y es la que más pesa en la puntuación |
| `next_state_head` | rollout interno del planner | indirecto |
| varianza del ensemble | logits, ×0.1 | **sí**, si `use_uncertainty` |
| `prediction_error` | **nadie** | **decorativa** |

## 696 · Cómo el planner convierte predicción en elección

Sortea 10 secuencias de 5 acciones al azar. Para cada una acumula `Σ energy_pred` y
`Σ sigmoid(done_pred)`, y puntúa `score = Σ energía − 10·Σ done`. Devuelve `actions[0]` de la
mejor. Con ambas cabezas produciendo ruido de magnitud ~0.01, **la elección la decide el ruido
numérico**. En la práctica es un muestreador casi uniforme del espacio de 25 acciones, activo en
el 50 % de los pasos.

## 697-698 · Por qué colapsa la política, y cuándo

[697] El mecanismo está escrito en el propio código: REINFORCE con baseline de media móvil sobre
una recompensa que es el coste por paso casi siempre da un advantage casi constante, «que apila
probabilidad sobre lo que se hizo primero». Sin término de entropía —apagado por defecto— nada lo
contrarresta. Medido: `modal_action_share` mediana **0.58** en el rollout cerrado.

[698] **No lo sé, y es medible.** No he registrado los logits antes y después de los primeros
eventos informativos. **Es la medición pendiente más informativa de toda la cartografía**, porque
separa «colapsa por la geometría de la loss aun sin evidencia» de «colapsa al recibir las primeras
señales».

## 699 · Por qué seis eventos no producen aprendizaje detectable

Cinco razones medidas, que se suman:

1. **1 : 200.** 1200 actualizaciones por ~6 ejemplos informativos.
2. **La loss de energía compite con un MSE de 640 dimensiones**, sin ponderación.
3. **El 99 % de los targets de energía es −0.06 constante**, así que la cabeza converge a una
   constante: desviación 0.0037 tras entrenar contra 0.0035 al nacer.
4. **El fallo no informa**: `NONEXISTENT`, `OUT_OF_RANGE` y NOOP entregan el mismo −0.06. El
   organismo no puede aprender a apuntar porque fallar no se distingue de no intentarlo.
5. **El examen de P1 usaba un formato de observación distinto del entrenado** —canal causal en el
   índice 0 en vez del 1, sin occupancy—, así que la medida de la capacidad está comprometida
   aunque la diferencia de diferencias se sostenga.

## 700-702 · ¿Puede aprenderlo con experiencia suficiente?

`scripts/experiment_learner_sample_efficiency.py` responde esto **midiéndolo**, no infiriéndolo:
entrega al mismo A4 un stream controlado fuera del mundo, con observaciones construidas por
`WorldStateManager.get_observation` —formato real—, en dos curvas: **pura** (N ejemplos seguidos)
y **diluida** (los mismos N a 1 de cada 100, la densidad de D4T).

[702] La hipótesis mecánica sobre qué limita primero la eficiencia muestral, a contrastar con esa
curva: **la ponderación de la loss**, no la capacidad. `energy_head` recibe 1 de las 642
dimensiones de error que retropropagan al backbone compartido.

**Medido (curva pura, `artifacts/learner_sample_efficiency_pure.json`, 5 semillas, azar 0.5):**

```
n=6 0.492 · n=12 0.493 · n=24 0.500 · n=48 0.487 · n=96 0.507
n=192 0.561 · n=384 0.547 · n=768 0.483 · n=1536 0.532
```

[700] **No.** No se separa del azar con 1536 ejemplos informativos puros, y la curva no es
monótona. [701] No hay eficiencia muestral que medir: no hay curva ascendente.
[702] La hipótesis de la ponderación sigue en pie y **sin contrastar** — la curva dice que algo en
la ruta de la señal lo impide, no cuál de los eslabones. Eso es `LEARNING-SIGNAL-PATHWAY`.

*La curva diluida no llegó a correr; con la pura plana, ya no discrimina nada.*

## 703-705 · Divergencias entre mundos, y qué física ejecutó cada evidencia

[703]

```
D4T_DECLARED       ≠  D4T_SANDBOX_EJECUTADO   (sin ciclo de oportunidades)
D4T_SANDBOX        ≠  D4T_CONTROLLER          (orden, semilla, terminación, determinismo global)
replay                                        NO VERIFICADO
```

[704-705] **Toda la evidencia de esta noche —tamizado de 39 corridas, P0 con 16 parejas, gemelos
de un paso con 3000 estados, P1 con 8 semillas— corrió sobre `SandboxService`.** Ninguna sobre la
ruta autoritativa. Por tanto ninguna es «efecto en el D4T declarado»: son **efecto en D4T bajo el
runtime Sandbox**, en un mundo estrictamente agotable.

## 706 · Módulos llamados «inteligencia» sin capacidad demostrada

| Módulo | Estado causal |
|---|---|
| `use_temporal` | efecto nulo en D4T; ninguna tarea exige historia |
| `use_episodic_memory` | +2.67 comidas, **por debajo de la dispersión entre semillas** |
| `use_longterm_memory` | +0.33, por debajo de la dispersión |
| `use_uncertainty` | +1.67, por debajo de la dispersión; sin calibración |
| `use_online_learning` | **0.00** — quitarlo no cambia nada medible |
| `use_entropy_regularization` | −0.67 bajo T0 |
| `use_world_model` / `use_planner` | +6.33 / +6.67, **y son el mismo efecto**, que es exploración, no planificación |

**Ningún módulo de A4 ha demostrado causalmente una capacidad cognitiva.** El único efecto
grande y reproducible es una inyección de acción casi uniforme.

## 707 · Capacidades sí demostradas por código y experimento

1. **El contrato de acción v1 era expresivamente suficiente**: `R = 1.0` bajo ambos contratos
   sobre 1894 intenciones realizables en 3000 estados exógenos, con el control ciego a 0.0.
2. **T1 separa referencia de alcance**: 16 de 16 parejas, `Δ = +0.598`, p = 3.1e−05. Bajo T0 el
   98.5 % de los consumos apunta a espacio vacío; bajo T1 el 95 % refiere a una entidad real.
3. **El selector tiene un efecto local aislable**: `INTERVENTION_ISOLATION = PASS` en 3000 de 3000
   pares, McNemar χ² = 11.775, p < 0.001.
4. **A4 condiciona su acción al contenido perceptivo**, cosa que A0 no puede representar — aunque
   rinda peor que A0.

## 708-709 · El circuito mínimo, y dónde se rompe

```
regularidad externa        canal 0 del objeto, umbral 0.7 / 0.3        ✓ existe
      ↓
exposición                 ~6 ejemplos por vida                        ✗ HAMBRUNA
      ↓
percepción                 encoder ve el canal en obs[1]               ✓ llega
      ↓
representación             s_t (640)                                   ✓ existe
      ↓
predicción                 energy_head                                 ✗ CONSTANTE
      ↓
valoración                 planner: score = Σe − 10·Σd                 ✗ dominada por ruido
      ↓
decisión                   policy_head, moneda 0.5                     ✗ COLAPSADA
      ↓
realización                98.5 % apunta a vacío bajo T0               ✗ CANAL
      ↓
conservación               memorias sin gradiente, no checkpointeadas  ? sin medir
      ↓
revisión                   sin instrumento de reversión               — no construido
```

[709] **Se rompe en cuatro sitios a la vez**, y los cuatro están medidos. El primero en el orden
causal es la exposición, y sus dos fuentes también están medidas: el canal de acción y el mundo
agotable.

## 710 · Qué del código contradice nuestra interpretación conceptual

**Siete contradicciones, en orden de gravedad:**

1. **«El modelo del mundo y el planificador producen efectos conductuales detectables» eran dos
   hallazgos. Son uno.** `use_world_model=False` desactiva el planner: 0 de 40 llamadas. Y ese
   efecto único no es cognición, es exploración por ruido.
2. **El `energy_head` no predice.** Desviación 0.0037 sobre una cantidad que varía 2.0. Todo lo
   que se ha dicho sobre «el modelo del mundo aprende algo del mundo» carece de soporte.
3. **`OpportunityLifecycle` no se ejecuta donde corren los experimentos.** Toda la evidencia
   histórica es sobre un mundo más pobre que el declarado.
4. **El fallo de acción no informa al organismo.** La descomposición referencia / alcance /
   discriminación existe en el instrumento y **no en la experiencia**. El organismo no puede
   aprender a apuntar porque el mundo le cobra lo mismo por fallar que por no intentar.
5. **De Bayes, MDL y EIG no queda nada en A4.** Si la teoría los menciona, describe otro sistema.
6. **`HomeostaticState.update()` es estado escrito y nunca leído**, y cuatro de los cinco campos
   de cada entrada episódica también.
7. **El banco de examen de P1 usa un formato de observación que el agente nunca vio.** Encontrado
   en esta cartografía; obliga a matizar el alcance del resultado negativo de P1.

---

# Apéndice · Lagunas declaradas

No verificado en esta pasada, y por qué:

| Sección | Preguntas | Qué falta leer |
|---|---|---|
| XIX traza y evidencia | 466-485 | `observer/trace.py` (418), `storage.py` (363), `logger.py` (430), `worldstream/service.py` (327) |
| XVIII serialización | 443-445 | representación de las cuatro semánticas en CSV, SQLite y UI |
| XXII hashes | 536-540 | `lab/evidence_publication.py` y las fixtures de baseline |
| XX versionado | 504-505 | formato de checkpoint y carga de versiones antiguas |
| XII H-Net / Mamba2 | 287-288 | barrido fuera de `terrario/` |
| XIII fuera de distribución | 302-303 | medición del comportamiento del ensemble |
| XXIV clasificación | 567-570 | clasificar 711 pruebas una a una |
| XXV concurrencia | 604-605 | búsqueda de locks y temporales compartidos |
| XI hipótesis de memoria | 266 | probar la explicación del residuo −3.0 |
| XIII colapso | 312-314 | **registrar logits antes y después de los primeros eventos informativos** |

La última es la más valiosa de todas: separa «colapsa por la geometría de la loss» de «colapsa al
recibir evidencia».

---

# XXXI · La cadena científica de evidencia

Mapeo del 2026-09-17. Cubre `terrario/lab/preregistration/`, `terrario/lab/execution/`,
`terrario/lab/evidence_publication.py`, `terrario/lab/persistence/`,
`terrario/lab/measurement_status.py`, `terrario/lab/instrument_registry.py`,
`terrario/lab/metric_result_sealing.py`.

## 31.1 · La cadena, y dónde se corta

```
✅ fuente (PDF + sha256) → claim → hiperarista con roles
✅ hiperarista → hipótesis → ExperimentDraft         146 borradores reales
✅ ExperimentDraft → Preregistro → TrialMatrix → run_attempt
                                                      144 preregistros · 146 matrices
                                                      240 intentos · 141 ejecuciones
❌ corrida → evidencia          scientific_results = 0 · empirical_evidence = 0
❌ evidencia → hiperarista      el campo no existe; corroboration_status sólo sabe negar
❌ el ciclo experimental real    screen_concepts / experiment_* escriben a runs/ y artifacts/
                                 y no tocan ninguna tabla del grafo
```

**240 intentos ejecutados, cero resultados científicos publicados.** Todo el aparato corre y nada
ha cruzado nunca el cortafuegos.

## 31.2 · Preregistro

`AnalysisPlan` ([domain.py:288](terrario/lab/preregistration/domain.py:288)) — 12 campos, **ninguno
con default**; los defaults reales los inyecta el ensamblador en
[service.py:621](terrario/lab/preregistration/service.py:621).

`ProtocolSnapshot` ([domain.py:397](terrario/lab/preregistration/domain.py:397)) — 19 campos.

**Máquina de estados** ([domain.py:49](terrario/lab/preregistration/domain.py:49)):

```
DRAFT → READY_FOR_REVIEW → REVIEW_IN_PROGRESS → REVIEWED → PREREGISTERED_LOCKED
                                                     ↓              ↓
                                                   DRAFT      SUPERSEDED / WITHDRAWN
```

`assert_transition` sólo se usa en **2 de 7** transiciones (`withdraw` y `supersede`); las demás se
validan con comparaciones de string sueltas en el repositorio. Dos fuentes de verdad.

**Amendment vs deviation** ([service.py:322](terrario/lab/preregistration/service.py:322)):
una *deviation* registra lo que pasó distinto de lo planeado y no engendra nada; un *amendment* es
cambio de diseño y **debe parir un preregistro hijo** salvo que sea metadatos. Ambos se sellan como
`POST_LOCK_GOVERNANCE_RECORD`.

**Inmutabilidad estructural** ([migrations.py:183](terrario/lab/persistence/migrations.py:183)):

```sql
CREATE TRIGGER artifact_versions_no_update BEFORE UPDATE ON artifact_versions
BEGIN SELECT RAISE(ABORT, 'artifact versions are append-only'); END;
```

## 31.3 · Diecisiete roturas de provenance

| # | Rotura | Dónde | Sev |
|---|---|---|---|
| 17 | **`assert_reportable` no lo llama nada en producción**; dos registros de métricas disjuntos | [instrument_registry.py:255](terrario/lab/instrument_registry.py:255) | 🔴 |
| 13 | `definition_version` es una **constante global** — la semántica de métrica no se versiona en el ledger; la comprobación de `evidence_publication` es tautológica | [service.py:675](terrario/lab/preregistration/service.py:675) | 🔴 |
| 1 | `observation_contract_hash`, `action_contract_hash`, `interventions_hash` y `agent_identity_hashes` **hashean etiquetas literales**, no contenido | [service.py:592](terrario/lab/preregistration/service.py:592) | 🔴 |
| 10 | `implementation_hash` hashea la **ruta del símbolo**; reescribir el evaluador no lo mueve | [service.py:675](terrario/lab/preregistration/service.py:675) | 🔴 |
| 9 | `dirty_diff_hash` hashea `git status --porcelain` — **nombres, no contenido** | [service.py:752](terrario/lab/preregistration/service.py:752) | 🔴 |
| 11 | `_git` devuelve `""` ante cualquier fallo → **árbol sucio declarado limpio** | [service.py:786](terrario/lab/preregistration/service.py:786) | 🔴 |
| 16 | **`NOT_EVALUABLE` no es publicable**: `denominator <= 0` es blocker. La ausencia de soporte desaparece del registro permanente | [evidence_publication.py:278](terrario/lab/evidence_publication.py:278) | 🟠 |
| 15 | `run_measures.py` **no importa `measurement_status`**: colapsa MISSING, NOT_EVALUABLE e INVALID en `None` | `run_measures.py` | 🟠 |
| 14 | `missing_data_behavior` **hardcodeado a `"ERROR"`** para toda métrica; la política real del instrumento nunca llega al ledger | [service.py:678](terrario/lab/preregistration/service.py:678) | 🟠 |
| 8 | Los **5 gates humanos** registran el mismo literal `"local-user"` | `preregistration/api.py`, `execution/api.py` | 🟠 |
| 12 | `epistemic_classification` sin verificación contra la regla ni contra el número | [metric_result_sealing.py:66](terrario/lab/metric_result_sealing.py:66) | 🟠 |
| 6 | CONFIRMATORY sobre semillas expuestas = warning **aceptable**; `"VERIFIED_UNEXPOSED_INVENTORY"` es convención de string no verificada | [validation.py:206](terrario/lab/preregistration/validation.py:206) | 🟠 |
| 7 | `software_identity` degrada a `"UNKNOWN"` sin bloquear | [dispatcher.py:76](terrario/lab/execution/dispatcher.py:76) | 🟡 |
| 5 | Una ejecución `ABORTED` **no marca el preregistro** | (ausencia de código) | 🟡 |
| 2 | `assert_transition` en 2 de 7 transiciones | [service.py:305](terrario/lab/preregistration/service.py:305) | 🟡 |
| 3 | `sequence=2` hardcodeada en el evento de estado de revisión | [repository.py:206](terrario/lab/preregistration/repository.py:206) | 🟡 |
| 4 | `withdraw` imposible desde `DRAFT`; devuelve 500 | [domain.py:636](terrario/lab/preregistration/domain.py:636) | 🟡 |

## 31.4 · Lo que sí está bien atado

Cadena hash de eventos de ejecución ([execution/service.py:430](terrario/lab/execution/service.py:430));
cadena de auditoría del preregistro ([repository.py:486](terrario/lab/preregistration/repository.py:486));
verificación CAS de componentes del bundle ([commitments.py:106](terrario/lab/preregistration/commitments.py:106));
binding revisión↔lock↔attestation ([repository.py:342](terrario/lab/preregistration/repository.py:342));
aislamiento de aliasing en forks causales (`BRANCH_ALIASING_DETECTED`, [causal.py:224](terrario/lab/causal.py:224));
liberación **visible** de trabajos huérfanos (`_release_orphaned_jobs`, `TRIAL_RELEASED_AFTER_LEASE_LOSS`);
y el único default que falla hacia la incertidumbre: `.get("critical", True)` en desviaciones
([evidence_publication.py:281](terrario/lab/evidence_publication.py:281)).

## 31.5 · `measurement_status` — la coerción a cero es estructuralmente imposible

[measurement_status.py:67](terrario/lab/measurement_status.py:67):

```python
def __float__(self) -> float:
    if self.status is not Status.OK:
        raise NotEvaluableError(...)
```

No hay `.or_zero()`, ni `.value_or()`, ni `__int__`. `ratio()` resuelve el denominador vacío **en el
único sitio donde nace**. Sus consumidores son cuatro: `selector_isolation`, `snapshot_bank`,
`capability_exam` y `sandbox_runtime`. **`run_measures.py`, el camino de medida principal, no está
entre ellos.**

## 31.6 · Persistencia

9 migraciones numeradas, 65 tablas, checksum sha256 por migración verificado antes **y después** de
aplicar ([store.py:156](terrario/lab/persistence/store.py:156)); backup automático si hay contenido;
WAL con `synchronous=FULL`; `BEGIN IMMEDIATE`. Sin downgrade.

---

# XXXII · La capa de conocimiento

> **Parcialmente superada por §XXXVIII** (relectura del 2026-09-21): las cifras
> del corpus, el estado de la citabilidad de conceptos y el catálogo de
> composición se releyeron allí. El veredicto estructural de esta sección se
> sostiene.

Mapeo del 2026-09-17. Cubre `terrario/lab/hypergraph/`, `terrario/lab/crossgraph/`,
`terrario/lab/referencegraph/`, `terrario/lab/theory/`, `terrario/lab/agent_composition.py`,
`knowledge/`, `theory_snapshots/`.

**Veredicto:** contratos tipados de alta calidad (≈6500 líneas), con **dos subsistemas
físicamente vacíos en producción** y un solo punto de contacto con el ciclo experimental.

## 32.1 · Qué está conectado de verdad

| Módulo | Líneas | Filas en producción | Consumidor real |
|---|---|---|---|
| `agent_composition.py` | 170 | — | ✅ `sandbox_runtime:10,50` + 4 scripts de experimento |
| `hypergraph/` | ~500 | 2 hipótesis, 146 borradores | sólo API HTTP / UI |
| `theory/` | ~1400 | 1 snapshot, 146 borradores | sólo API HTTP / UI |
| `referencegraph/` | **1293** | **0 en 22 tablas** | ninguno (fuera de tests y un benchmark sintético) |
| `crossgraph/` | **1740** | **0 en 9 tablas** | ninguno |

`crossgraph/d2trace.py` —la pieza que uniría Reference → Claim → Theory → Hyperedge → Scenario—
**no tiene ningún llamador, ni siquiera un test**.

Confirmación negativa: `grep "hypergraph\|crossgraph\|referencegraph\|theory"` sobre
`terrario/lab/run_measures.py` da **una coincidencia, y es un comentario**.
`terrario/experiment/controller.py` no importa nada de esta capa.

## 32.2 · Corpus

El corpus físico **existe**: 42 PDFs en `/home/wis/Documentos/teoria de la inteligencia/`.
El formato que `import_corpus.py` consume —`manifest/CORPUS_MANIFEST.jsonl`— **no existe en
ninguna parte del disco**.

El catálogo real vive en otro sitio y otro formato:
`theory_snapshots/theory-f59dbb6d6ee3850c/SOURCE_PROVENANCE_v0.3.csv`, con `ingestion_summary.json`
declarando 44 fuentes, 189 claims, 283 conceptos raw, 224 canónicos, 206 relaciones, 8 hiperaristas.

**Son dos sistemas paralelos que nunca se tocaron.**

`referencegraph/domain.py` modela 17 tipos de nodo y 22 de arista, con `ClaimLocator`
([domain.py:181](terrario/lab/referencegraph/domain.py:181)) capaz de citar página, sección, figura,
tabla, párrafo, apéndice y suplemento. El importador **crea el locator vacío**
([import_corpus.py:367](terrario/lab/referencegraph/import_corpus.py:367)).

## 32.3 · Conceptos

**El ciclo de madurez RAW → DEFINED → RELATED → OPERATIONALIZABLE → IMPLEMENTED → INSTRUMENTED →
TESTED → RETAINED/REVISED/REJECTED no existe.** Lo que hay son tres enums desconectados:

- `EpistemicStatus` ([models.py:14](terrario/lab/models.py:14)) — 9 valores, **sin función de
  transición**; el código sólo verifica que no suba: `raise ValueError("materialization cannot
  promote epistemic status")`.
- `ReviewState` ([theory/factory.py:19](terrario/lab/theory/factory.py:19)) — sí tiene máquina real,
  pero se aplica a **diseños de experimento**, no a conceptos.
- `ScientificReadiness` — tabla hardcodeada por candidato.

**`Concept`** ([agent_composition.py:32](terrario/lab/agent_composition.py:32)): `key, label,
purpose, without_it, block, corpus_block`. Diez conceptos.

**`corpus_block` es un `int` que ningún otro fichero lee** — `grep` da una sola línea, su
declaración. Sin `reference_id`, sin `claim_id`, sin locator. El comentario más honesto del
repositorio está justo ahí ([agent_composition.py:89](terrario/lab/agent_composition.py:89)):

> `# Corpus block 0 -- meaning NONE. Every other concept here answers to a numbered block`
> `# of the 64-block map; this one does not, and saying it did would be a fabricated citation.`

## 32.4 · Hipergrafo — lo mejor construido de la capa

`TheoryHyperedgeBinding` ([theory_operational.py:27](terrario/lab/hypergraph/theory_operational.py:27))
— **13 campos, todos obligatorios**, con validación fail-closed:

```python
raise ValueError("hyperedge binding requires a complete provenance locator")
raise ValueError("role binding basis is not source-backed")
```

**Roles reales, verificados** en `HYPEREDGE_ROLE_BINDINGS_v0.2.csv`: `agent`,
`action_sequence_proposer`, `future_state_predictor`, `intrinsic_cost_and_critic_evaluator`.
Exactamente el caso donde memoria, modelo del mundo y planificador ocupan lugares distintos en la
misma hipótesis. `materialize()` verifica el **sha256 del PDF real** y rechaza si no coincide.

**Lo que el hipergrafo NO puede hacer:**

- **Adjuntar evidencia.** No hay campo. `corroboration_status` sólo toma `"NOT_CLAIMED"` y
  `"STRUCTURAL_COMPOSITION_NOT_CORROBORATION"` — existe **para declarar que no hay corroboración**.
- **Registrar contexto** (mundo, régimen, agente, versión de instrumento). Ausente por completo de
  `_semantic_payload()`.
- **Tipar dependencias.** `relation_type` toma dos valores. No existen `REQUIERE / REGULA /
  HABILITA / COMPENSA`. El tipado fuerte existe en `RelationStrength`
  ([theory/models.py:25](terrario/lab/theory/models.py:25)) con 5 niveles, pero se aplica a CSV de
  auditoría, no al hipergrafo.

Consecuencia: **es un almacén de estructura, no de conocimiento acumulado.**

## 32.5 · Generación de hipótesis — sí funciona

Tres generadores: `compose()` (deriva hiperaristas exigiendo compatibilidad de roles con
`rationale`), `OperationalHypothesisCompiler.compile()` (hiperarista → `HypothesisDraft` con
premisas trazadas), y `build_portfolio()` (explosión combinatoria: para HYPERCAND-08 con 6
componentes → 63 rivales + 1 nula).

Producción real: **2 `OperationalHypothesisDraft` y 146 `ExperimentDraft`** en la base de datos,
con `provenance.source_artifact = "HYPERCAND-01"`.

Pero `build_portfolio` llama a `generate(edge, snapshot_id)` **sin pasar `source_claim_ids`**
([factory.py:337](terrario/lab/theory/factory.py:337)), así que ese campo queda vacío en todo el
portafolio generado.

---

# XXXIII · Observación, traza e interfaz

Mapeo del 2026-09-17. Cubre `terrario/observer/`, `terrario/lab/worldstream/`,
`terrario/lab/api.py`, `terrario/lab/metrics_observer.py`, `terrario/agent/scientific.py`,
`terrario/lab/static/`, `tests_frontend/`, `scripts/`.

## 33.1 · Seis de once clases de traza son código muerto

`TRACE_REGISTRY` ([trace.py:406](terrario/observer/trace.py:406)) declara 11 clases. El **único**
llamador de `log_step` pasa un dict vacío
([controller.py:263](terrario/experiment/controller.py:263)), y `logger.py` sólo escribe una traza
si está en ese dict.

> **2026-09-18.** La traza de A4 lleva además `adaptive_freeze_attempt`, un evento por intento de
> escritura sobre la frontera adaptativa, con `attempted` / `committed` / `blocked_reason`. Es
> observabilidad del commit, no genealogía del conocimiento: eso es OCF-G5. Ver §XXXVII.

**Nunca se construyen:** `DecisionTrace`, `PerceptionTrace`, `TemporalTrace`, `MemoryTrace`,
`PredictionTrace`, `LearningTrace`. Confirmado contra disco: una corrida real sólo produce
`world`, `consequence`, `sensation`, `provenance` y `transition`.

`ObserverRegistry` declara el canal `decision` con `payload_schema="DecisionTrace"` y
`availability="AVAILABLE"` — y **ningún `DecisionTrace` se escribe jamás**.

## 33.2 · Dos esquemas de traza, traducción de un solo sentido

| | `TransitionTrace` | `SandboxTraceStep` |
|---|---|---|
| versión | `terrario.observer.transition/v2` | `terrario.sandbox.trace/v1` |
| observación | `observation_t` **y** `observation_t1`, ambos con hash | sólo `agent_observation`, sin hash |
| terminación | `terminated` **y** `truncated` | sólo `terminated` |
| contrato de acción v2 | ausente | presente |

`worldstream/service.py:212` construye un `TransitionTrace` *a partir de* un `SandboxTraceStep`
poniendo `internal_state={}` y `agent_trace_events=[]`, y **fabrica los hashes de observación ad
hoc** con `sha256` del payload JSON en vez de `Observation.obs_hash()`. Dos definiciones distintas
de «el hash de esta observación» conviviendo.

**No hay campo común entre una sesión de sandbox y un trial científico.** Es deliberado —el
cortafuegos— pero significa que no se pueden correlacionar por identidad.

## 33.3 · Autoridad de la traza

- **Worldstream:** *«El JSONL es autoritativo; todo otro artefacto es desechable»*
  ([worldstream/trace.py:31](terrario/lab/worldstream/trace.py:31)). El SQLite guarda punteros de
  byte; `_ensure_index` detecta divergencia y reconstruye; `verify()` recorre la cadena de hashes.
- **Científico:** *«A live in-memory view is only an accelerator; terminal truth is CAS»*
  ([execution/observation.py:71](terrario/lab/execution/observation.py:71)).

## 33.4 · Pasividad — cinco mutaciones desde código de observación

| | Dónde | Qué pasa | ¿Cambia trayectoria? |
|---|---|---|---|
| **V1** | `capability_exam.py` vs `a4_advanced.py:347` | la lista `volatile` omitía `homeostasis._energy` (1.0→0.5) y `_trace` (0→40) | **sí en potencia** — energía → `exploration_bias` → temperatura → muestreo. **Medido: efecto nulo**, porque el examen nunca llama `decide()`. **Reparado**: el conjunto ahora se deriva. |
| **V2** | `experiment_learner_sample_efficiency.py` | `exam()` reimplementado sin guardián, y el `before` corría justo antes del entrenamiento | **medido: idéntico hasta el último dígito** en 3 semillas. **Reparado.** |
| **V3** | [opportunities.py:195](terrario/world/opportunities.py:195) desde `controller.py:246` | `geometry()` muta `min_distance_during_lifetime` y `ever_visible` | **no** — pero la métrica depende de cuántas veces se llamó y con qué `view_radius` |
| **V4** | [a4_advanced.py:774](terrario/agent/agents/a4_advanced.py:774) desde `controller.py:264` | `get_trace_events()` **vacía** `_trace` del agente y de 5 submódulos | **no** — pero un segundo observador vería cero eventos. Observar consume lo observado. |
| **V5** | [logger.py:183](terrario/observer/logger.py:183) | el logger escribe `None` en el objeto de traza del llamador | no (código muerto) |

**El backpressure sí puede acortar una corrida.** Superar 16 MiB por frame o 2 GiB de traza lanza
excepción dentro de `_advance`, el worker marca `FAILED` y la simulación para
([worldstream/service.py:174](terrario/lab/worldstream/service.py:174)). Una sesión observada es
más corta que una no observada.

En la ruta científica el fallo de observación **no corrompe** la trayectoria pero **la descarta**:
`OBSERVER_MATERIALIZATION_FAILED` lleva el intento a `MATERIALIZATION_FAILED`.

**Ningún observador, métrica ni la UI consume RNG.** Verificado módulo por módulo.
`perceive_targets` deriva los handles por hash salado, no por sorteo, lo que permite que los
instrumentos usen el mismo resolvedor que el runtime sin tocar ningún flujo aleatorio.

**Brecha:** la pasividad sólo está probada para **A0_RANDOM**. El único agente donde es difícil
—estado recurrente, memoria episódica, baseline, homeostasis— no tiene ni un test.

## 33.5 · Checkpoints — el único artefacto persistente sin versión

`save()` escribe cuatro cosas: `params.safetensors`, `optimizer.safetensors` (**nunca**: ningún
agente implementa `get_optimizer_state`), `metadata.json` (**sin `schema_version`**) y
`runtime_state.pt` con los cuatro estados RNG y el `state_dict` del optimizador.

`_optimizer_for` **sí funciona con A4** por la rama de respaldo `agent.learner._optimizer`, pero es
un acoplamiento por nombre de atributo privado a dos niveles: un agente que lo llame distinto
pierde el estado **en silencio**.

**Restaurar A4 no reproduce el siguiente paso.** Quedan fuera: `_hidden`, `episodic_memory._buffer`,
`_energy_baseline`/`_baseline_count`, `_step`, y **`learner._step_count`** — que decide *si hay
actualización en este paso*. Del mundo quedan fuera el estado completo de `OpportunityLifecycle`
(records, pendientes, posiciones recientes, generaciones de linaje) y qué cambios disparó el
scheduler.

Dos rutas de degradación **silenciosa**: sin `runtime_state.pt` el RNG no se restaura sin aviso; y
`set_parameters` ignora claves que no reconoce, así que un checkpoint anterior a
`operation_head`/`selector_head` deja esas cabezas en su inicialización aleatoria.

Y `torch.load(..., weights_only=False)` — ejecución arbitraria por deserialización, en un
repositorio que eligió `safetensors` precisamente para evitarla.

Hay test de reconstrucción para **A0 y A1**. Ninguno para A4.

## 33.6 · Mallas y controles

**22 mallas** en `run_measures.py`; **6** en el registro de instrumentos. 16 reconstruyen desde la
traza, 6 leen algo registrado durante la transición.

`cambio_propio` está **declarada y es permanentemente inevaluable**: A4 calcula
`parameter_delta_norm` en `learn()` y lo pone en su traza; `get_scientific_state()` no lo lleva. La
malla teóricamente más relevante está rota por un campo que no cruza la frontera — y el código lo
documenta en vez de esconderlo ([run_measures.py:429](terrario/lab/run_measures.py:429)).

`colapso_politica` es la única malla que emite un **veredicto booleano** sobre el organismo, con
tres umbrales escritos a mano y **ningún caso conocido**.

**24 controles de falsación** sobre 8 métricas, cada una con techo, suelo y —donde existe— valor
analítico de azar. Cuatro esperan `None`, codificando que `NOT_EVALUABLE ≠ 0.0`.

## 33.7 · API y pantallas

`lab/api.py` bifurca en `/api/v1/` (científico, delegado) y `/api/` (legado/sandbox). Guardia
global: toda mutación no enumerada devuelve 405.

**Efecto lateral notable:** un `GET` de previsualización de mundo **escribe un registro de
exposición** ([api.py:182](terrario/lab/api.py:182)). Mirar un mundo queda registrado — disciplina
de preregistro correcta contra el *seed hunting*, y a la vez un `GET` que no es seguro, mientras
`/api/status` responde `"mode": "READ_ONLY"`.

Cuatro superficies: `index.html` (15 vistas), `componer.html` (4 pasos, el frontend del sandbox),
`review-center.html` (revisión humana) y `workspace/index.html` (el taller visual científico, con
reductores puros probados en `tests_frontend/unit/`).

## 33.8 · Scripts

38 ficheros. **24 vivos** (10 experimentos, 7 demostraciones CL, 4 semillas E2E, los gates y el
runner), **4 latentes** (benchmarks), **11 históricos** — entre ellos `run_experiment.py` y
`ablation_study.py`, ambos del día 1, anteriores a toda la infraestructura de preregistro.

# XXXIV · Generador de mundos diagnósticos y oráculos amputados

**2026-09-17.** Fase 1 de TCS-01 dejó de escribir un mundo por capacidad y pasó a generarlos.

## 34.1 · La entrada es un conjunto, no una capacidad

`terrario/lab/world_generator.py` recibe un conjunto de `capability_id`. Cada uno declara una
exigencia sobre **un eje** (`DEMAND_OF`); las exigencias se funden por el máximo (`merge`); el mundo
resultante no se pasa sin todas. Con un elemento es el mundo de esa habilidad; con varios, el mundo
varía para exigirlas juntas — la Fase 3 sin mundos nuevos. El control de una capacidad dentro de un
conjunto es el mismo mundo con **su** eje apagado (`control_for`).

> **Corrección del 2026-09-18.** Aquí decía que «`axis_difference` verifica que exigente y control
> difieren en exactamente una dimensión». No lo verifica: compara el `Demand` —la especificación—
> y nunca el mundo realizado. Durante un día certificó en espacio-de-`Demand` una propiedad que el
> mundo no tenía. Lo que ahora sí la sostiene son `_stream` (contenido de estación) y la duración
> pareada de `control_for` (presupuesto metabólico), cada una con su test. Ver §34.6.

Siete ejes: `delay`, `hidden`, `distractors`, `sequence`, `risk`, `novelty`, `inversion`. `OFF` no
coincide con `Demand()` en `hidden`: la base esconde la verdad, pero apagar el eje de LEARN es
precisamente dejar de esconderla.

## 34.2 · Sustrato: pasillo de tres filas

`x` es fila, `y` es columna (`build_world_state` indexa `occupancy[pos.x, pos.y]` con forma
`(grid_h, grid_w)`; `UP = (-1, 0)`, `RIGHT = (0, +1)`). El organismo arranca en `(1, 0)` y avanza
por la fila 1. Cada estación: cue(s) en la fila 0, `delay` columnas después dos puertas en `(0, c)` y
`(2, c)`, adyacentes por `UP`/`DOWN` desde `(1, c)`. Canal 1 marca qué es cada objeto (cue 0.9,
distractor 0.6, novedoso 0.3, puerta 0.1); canal 3 dice qué hace una puerta (0.9 buena, 0.1 mala,
0.5 segura, 0.35 inerte). Dos cues nunca coinciden en la ventana: separación `2·radio + 1`.

Lo que usa del motor y nada más: objetos explícitos, reglas `(object_channel índice 3, CONSUME)`,
`changes` para la inversión, las cuatro claves de economía de `strict_physics`. **No** usa
`procedural_layout` ni `opportunity_lifecycle`: los ensayos repetidos dentro de una vida los dan
las estaciones.

**Contrato con el motor:** `num_channels = 4` ⇒ `obs[1..3] = canales 0..2`, canal 3 truncado.
`channel_3_is_hidden()` lo comprueba contra `WorldStateManager.get_observation` real, no contra
la docstring.

## 34.3 · Oráculos con facultades desmontables

`terrario/lab/world_oracles.py`. Un mundo que «exige memoria» es una afirmación; la prueba es un
organismo guionizado que lo resuelve con todas sus facultades y deja de resolverlo sin exactamente
la que el eje nombra. Leen la **ventana real** — la misma que A4 — y llevan su columna por
integración de camino; nunca miran el estado. `FACULTY_OF_AXIS`: delay→memory, sequence→order,
distractors→filter, hidden→mapping, risk→homeostasis, inversion→inversion. `novelty` no tiene
facultad guionizable: lo que UNC produce es una señal, y un guion no la tiene.

`verdict_for(cap)` corre exigente y control con oráculo completo y amputado; `demands` es
`completo ≥ .95 ∧ amputado ≤ .70 ∧ amputado-en-control ≥ .95`.

## 34.4 · Lo que se falseó al construirlo

Cuatro defectos, todos míos, todos atrapados por una capa distinta:

| Defecto | Quién lo vio |
|---|---|
| La puerta mala pagaba **+6** en vez de cobrar −6 (pasé `loss` positivo a una función que esperaba el signo puesto); las reglas invertidas de PLAST quedaban ambas negativas | **Nadie durante una hora.** La matriz puntúa contra la clave, no contra la energía. Lo vio un trazado de `energy_delta` por decisión. De ahí `door_deltas()` y la capa 2 de los tests: cada tipo de puerta debe producir el delta declarado, por `RuleEngine` real |
| `consumptions_from` comparaba la energía **normalizada** de la observación con el umbral absoluto | Lectura del código; ahora recibe el mundo y desnormaliza |
| Las estaciones novedosas entraban en el denominador y nunca en el numerador (UNC daba 0.625 con oráculo perfecto) | La matriz |
| Las estaciones novedosas tenían ambas puertas **seguras**: consecuencia cierta, así que una incertidumbre calibrada debería ser *baja* ahí | El diseño D7U de un agente del workflow: la incertidumbre necesita un **referente irreducible**. Ahora el canal 3 de cada puerta novedosa es moneda al aire |

Y dos calibraciones que no eran bugs sino mundos que no creaban la situación: HOMEO sin decisiones
a energía baja (inicial 30 nunca cruzaba el umbral 8 → inicial 20, umbral 14, segura +0.5 < esperanza
de la arriesgada +1); PLAST con la inversión al 50 % de `3·ancho`, cuando el oráculo agota el
pasillo antes (→ `2·ancho`, inversión al 30 %).

## 34.5 · Resultado

`scripts/world_demand_check.py --semillas 8`:

```
capacidad  eje          facultad     completo  amputado  amp/ctrl  exige
LEARN-A1   hidden       mapping      1.000     0.541     1.000     si
EPMEM-A1   delay        memory       1.000     0.541     1.000     si
LTMEM-A1   distractors  filter       1.000     0.297     1.000     si
TEMP-A1    sequence     order        1.000     0.547     1.000     si
HOMEO-A1   risk         homeostasis  1.000     0.000     1.000     si   (métrica: modulación)
UNC-A1     novelty      —            1.000     —         —         —    (se comprueba en el mundo)
PLAST-A1   inversion    inversion    1.000     0.000     1.000     si   (métrica: acierto tras inversión)
```

`tests/test_world_generator.py`: 32 pruebas en tres capas (estructura, física, exigencia), incluida
una de conjunto `{EPMEM, TEMP, PLAST}` donde cada facultad amputada por separado hace caer al oráculo.

**Verificación de esta auditoría (2026-09-17):**
`scripts/world_demand_check.py --semillas 8` reprodujo la matriz anterior con 64 decisiones por
capacidad falsable; `tests/test_world_generator.py -q` pasó sus **32** pruebas y el guard confirmó
que la raíz de datos viva de Terrario no cambió.

## 34.6 · Lo que una ronda adversarial encontró, y lo que se reparó (2026-09-18)

Quince agentes contra los PDF del corpus y contra el código. Encontraron **dos defectos críticos en
la maquinaria** —la parte que la revisión previa había declarado sana— y corrigieron dos
afirmaciones del analista. Detalle en `docs/REVISION_GENERADOR_MUNDOS_01.md`.

| Defecto | Medida antes | Reparación | Medida después |
|---|---|---|---|
| **Un flujo de azar compartido.** Encender `distractors`, `sequence`, `risk` o `novelty` sorteaba de más, corría el flujo y regeneraba `designated`, que ningún eje debe tocar. El control de 4 de 7 ejes era **otro mundo** | 40 sorteos vs 16 (distractors), 24/16 (sequence), 24/16 (risk), 20/16 (novelty); `designated` divergía en 24 de 42 pares (capacidad × semilla) | `_stream(seed, station, purpose)`: el contenido de una estación es función de (semilla, estación, propósito) y de nada más | **0 de 42** pares divergentes |
| **`duration = 2 × ancho`.** `delay` y `sequence` alargan el pasillo y con él la vida y el gasto. Todo contraste de memoria era también un contraste de viabilidad, con sesgo de un solo lado (el control nunca moría) | EPMEM 19.80/10.20 de 20.00 iniciales; TEMP 31.80/19.80. 0.175 del déficit de EPMEM era truncamiento metabólico | `generate(..., duration=)` y `control_for` fija la duración del control a la del exigente | EPMEM 19.80/**19.80**; TEMP 31.80/**31.80**; test por capacidad |
| **`Score` sin canal de viabilidad.** `run_life` devolvía `terminated` y la energía de cada paso; `life_score` los descartaba en una línea | Sobre 420 vidas de oráculo, **7 vidas muertas puntuaban accuracy 1.0**; misma semilla muerta en el paso 61 con 1.0 frente a superviviente de 212 pasos con 0.6 | `Viability`, `viability_from()`, `Score.viability` / `Score.died` (`None` cuando nadie midió) | **0** vidas muertas con accuracy 1.0; las 11 muertes restantes, **todas en brazos amputados** |
| **`merge` fundía `hidden` con `any()`.** HOMEO-A1 declara `hidden=False` como precondición de `modulation`: si las puertas no se distinguen a la vista, el organismo no puede elegir la segura | HOMEO sola: puertas `[0.5,0.1,0.9]` vs `[0.5,0.1,0.1]`. Compuesta con EPMEM: `[0.5,0.1,0.5]` vs `[0.5,0.1,0.5]`. Y un test lo ratificaba | `PINNED` declara los ejes que una capacidad necesita clavados; `demand_for` falla ruidosamente al componer un conjunto incompatible | Componer LEARN con HOMEO exige decidir a mano qué endpoint se abandona |

**El veredicto científico sobrevive y mejora.** `scripts/world_demand_check.py` con 6 semillas tras
las reparaciones:

```
capacidad  eje          facultad     completo  amputado  amp/ctrl  exige
LEARN-A1   hidden       mapping      1.000     0.521     1.000     si   n=48
EPMEM-A1   delay        memory       1.000     0.521     1.000     si   n=48
LTMEM-A1   distractors  filter       1.000     0.381     1.000     si   n=48
TEMP-A1    sequence     order        1.000     0.521     1.000     si   n=48
HOMEO-A1   risk         homeostasis  1.000     0.000     1.000     si   n=48
UNC-A1     novelty      —            1.000     —         —         —    n=38
PLAST-A1   inversion    inversion    1.000     0.000     1.000     si   n=48
```

El brazo amputado de memoria sube de ~0.35 a **0.521 ≈ azar**, que es el número correcto: un
oráculo sin memoria debe puntuar azar, no menos. Lo que le faltaba para llegar a azar era comida.

**Lo que no se reparó, y por qué.** El motor tiene **exactamente una variable esencial**
(`AgentState.energy`; `low_energy=14.0` es un cubo de puntuación, no un umbral fisiológico), así
que ningún eje nuevo del generador puede subirla — y con N=1 el experimento de HEA-005 queda
**indefinido**, no sólo mal medido. No hay operador de perturbación en ningún sitio, así que HEA-009
sigue sin ser aplicable. Y `Score.accuracy` sigue siendo la métrica primaria de seis ejes, que es lo
que Ashby S.5/2 sí prohíbe (`R-HEA-014-001` en corpus v2, locator `extracted_text/HEA-014.txt:5608-5662`):
cambiarlo mueve los siete endpoints primarios PENDIENTE y es decisión de diseño, no reparación.

**Verificación (2026-09-18):** `tests/test_world_generator.py` pasa **72** pruebas (eran 43; las
nuevas generalizan la paridad de contenido a las siete capacidades y añaden paridad metabólica y
viabilidad); `scripts/world_demand_check.py` reprodujo la matriz de arriba; el guard confirmó que la
raíz de datos viva no cambió.


`capability_passport.register` deriva `demanding_world` de `world_generator.demanding_world_id`;
7 de 9 pasaportes tienen mundo (WM-A1 y PLAN-A1 no: el generador no declara exigencia para ellos,
y no la declarará mientras su intervención sea impura).

## 34.6 · Lo que sigue sin resolverse

- **LEARN sigue en el camino crítico.** Cuatro mundos (EPMEM, LTMEM, TEMP, PLAST) exigen aprender
  el mapeo cue→lado, y el learner no se separa del azar con 1536 ejemplos puros. Los mundos ya
  existen; el organismo que los pase, no.
- **`primary_endpoint`** de 7 pasaportes sigue `PENDIENTE`: `score()` produce `accuracy`,
  `modulation`, `accuracy_after`, pero no están registrados como instrumentos calibrados.
- **Procedencia al corpus**, 9 de 9.

# XXXV · G8 · Autoridad instrumental única y frontera de admisión de evidencia

**2026-09-18.** Decisión humana: `instrument_registry` es la autoridad científica canónica.

## 35.1 · El diagnóstico: cuatro autoridades, no dos

El informe de partida decía que había dos nociones de «métrica registrada». Medido, hay cuatro, y
las dos principales **no se solapan en absoluto**:

```
15 métricas en MetricRegistry (lo que consume el preregistro)  →  0 en instrument_registry
 8 instrumentos en instrument_registry (los 8 REPORTABLE)      →  0 con binding de observador
                                             intersección  =  ∅
```

1. `instrument_registry.MetricSpec` + `state_of` — sabe qué significa científicamente un
   instrumento. **Cero llamadores de producción** para `assert_reportable`.
2. `metrics_observer.MetricRegistry` — sabe cómo el runtime obtiene el número. De sus 15 métricas
   **exactamente una** es `VALIDATED_FOR_CONSTRUCT`, y es la única que podía preregistrarse.
3. Módulos `specification()` por métrica (`planning_trace_metric`, `viability_recovery_metric`),
   cada uno con su propio `metric_spec_hash`. El preregistro congelaba ese hash para **un solo
   metric_id, cableado por nombre** en `service.py`.
4. `EvidenceRecord(metrics: dict[str, float])` en `terrario/experiment/specs.py`.

Y el dato que permitió cerrar en modo estricto: **el libro mayor tiene 0 `scientific_results`, 0
`empirical_evidence` y 0 artefactos `METRIC_RESULT`** sobre 238 trazas selladas. Nunca se publicó
evidencia científica, así que no había carril en producción que romper ni nada que certificar
retroactivamente.

## 35.2 · Lo que se construyó

**No un tercer registro** — era la prohibición central. Se añadió resolución **dentro** de la
autoridad y una frontera.

| Pieza | Dónde | Qué hace |
|---|---|---|
| `InstrumentRef` + `resolve` + `assert_admissible` | `instrument_registry` | Referencia con `instrument_id`, `version` y `spec_hash`. Falla cerrado con tres códigos distintos: `UNKNOWN_INSTRUMENT`, `INSTRUMENT_VERSION_DRIFT`, `INSTRUMENT_SPEC_DRIFT` |
| `scientific_instrument` | `metrics_observer.MetricDefinition` | Una **declaración**, no una autorización. Es un id, no una referencia resuelta, para que un módulo de contratos no dependa de la maquinaria de calibración |
| `instrument_ref` | `preregistration.MetricCommitment` | La identidad congelada al cerrar el protocolo |
| `_instrument_findings` | `preregistration.validation` | Un endpoint PRIMARY debe resolver a un instrumento canónico REPORTABLE. Falla cerrado incluso si la autoridad no se puede importar |
| `evidence_admission.admit_evidence` | módulo nuevo | La frontera. Resuelve, exige reportabilidad, compara contra el protocolo y transporta el `Reading` |
| `RESULT_SCHEMA` v2 | `evidence_publication` | Lleva `instrument` y `reading`. Un payload v1 se rechaza para publicación NUEVA, no se actualiza |

La versión se generalizó a partir del patrón que **ya existía** para CL-7 —congelar un
`metric_spec_hash` y verificarlo— en vez de construir uno paralelo. Por eso `MetricCommitment` no
necesitó cambiar su modelo científico: `specification_hash`, `implementation_identity` y
`calibration_report_hash` ya estaban ahí.

## 35.3 · Los cuatro estados de la lectura, ahora transportados

`Reading` existía y era correcto —`float(reading)` lanza si no es OK— pero **nunca llegaba a la
admisión de evidencia**: el sellado exigía `value/numerator/denominator` numéricos y el sobre
exigía `denominator > 0`. Es decir, un `NOT_EVALUABLE` era estructuralmente impublicable y solo
podía colarse como un cero falso. Ahora:

```
OK(0.0, support=12)   → ADMITIDO, numeric_claim=True    el cero sobrevive como hallazgo
NOT_EVALUABLE         → ADMITIDO, numeric_claim=False   existe en provenance, fuera del análisis
MISSING               → ADMITIDO, numeric_claim=False
INVALID               → ADMITIDO, numeric_claim=False
0.99 (float pelado)   → RECHAZADO  READING_IS_BARE_NUMERIC
```

`numeric_claim` separa dos cosas que un booleano confundía: que la lectura sea admisible como
resultado científico, y que afirme una cantidad.

## 35.4 · Vinculación en runtime

El sellado copia el instrumento **del protocolo**, así que protocolo y registro coinciden por
construcción y la comparación en publicación sería vacía. Por eso el evaluador debe declarar
`instrument_id` —qué instrumento acaba de ejecutar— y `seal_metric_result` compara ahí, que es el
único momento en que el instrumento prometido y el ejecutado son visibles a la vez.

## 35.5 · Ruta legacy: preservada, no modificada

`EvidenceRecord(metrics: dict[str, float])` vive entero en `terrario/experiment/`, y el único
escritor de artefactos del despachador produce `SCIENTIFIC_TRACE` y `TRIAL_RESULT` — nunca
`METRIC_RESULT`. El único escritor de `METRIC_RESULT` es `seal_metric_result`, que ahora rechaza
cualquier cosa sin instrumento canónico y sin `Reading`.

Es decir: **la ruta legacy ya era estructuralmente disjunta de la canónica.** Se probó con un test
en vez de editar el tipo histórico, lo que además evita mover un hash protegido sin necesidad.

## 35.6 · Consecuencia: LEARN-A1 queda lista para certificar

```
CLM-0127 ─→ LEARN-A1 ─→ SUPPRESS-COMMIT ─→ mundo diagnóstico ─→ conversion_aprendizaje ─→ evidencia
   G0        operacion.        G4               paridad              instrumento canónico
```

`scripts/passport_check.py`: **1 de 9 listas para certificar**, frente a 0 de 9 al empezar la
sesión. Las otras ocho siguen sin procedencia al corpus (8/9) y siete sin instrumento calibrado.

## 35.7 · Deuda declarada

- La docstring de `capability_passport.py` afirma que `assert_reportable` «no lo llama nada en
  producción». **Ya es falsa** —hay tres llamadores— pero ese fichero está en la lista de
  prohibidos de esta tarea y no se tocó.
- `REGISTRY` de instrumentos sigue indexado solo por `metric_id`: dos versiones del mismo
  instrumento no pueden coexistir. La deriva se detecta, pero un snapshot ejecutable de una versión
  antigua no se puede resolver; la política implementada es **fallar cerrado y exigir enmienda**.
- Las 15 métricas del observador siguen sin binding canónico. No se inventó ninguno: `None` es el
  estado honesto y es lo que las vuelve inutilizables como endpoint confirmatorio.

# XXXVI · La frontera del estado aprendido, y la regla que G8 no había registrado

**2026-09-18.** Dos trabajos pequeños, uno de ellos reparando un defecto propio.

## 36.1 · `PR-INSTRUMENT-001` se emitía sin estar registrada

G8 añadió a `preregistration/validation.py` la regla que exige instrumento canónico en un endpoint
primario, y la emitía desde cuatro sitios — pero nunca la añadió a `RULES`. `_finding` hace
`RULE_BY_ID[rule_id]`, así que cada una de esas rutas lanzaba `KeyError` en vez de devolver un
hallazgo bloqueante, y por la API salía como un 400 opaco en lugar de algo que un revisor pudiera
leer.

Falla ruidoso, no permisivo, así que nada inseguro pasó. Pero la regla dispara exactamente cuando
un endpoint primario no tiene instrumento — lo primero que hará cualquier preregistro confirmatorio
—, de modo que el gate que G8 creía haber puesto era inalcanzable en la práctica.

Sobrevivió porque los 28 tests de G8 ejercitan la autoridad y la frontera de admisión
directamente, y ninguno recorre la ruta de validación de preregistro. Los cinco tests nuevos cubren
esa grieta: las tres formas en que un binding puede fallar, un instrumento registrado pero no
certificado, y una autoridad que no se puede importar — esto último porque un gate que degrada a
permisivo bajo `ImportError` no es un gate.

## 36.2 · `learning_commit_enabled` no es toda la frontera

`scripts/learned_state_audit.py` + `docs/FRONTERA_ESTADO_APRENDIDO_01.md`.

La intervención certificada en G4 congela **perfectamente** lo que gobierna el optimizador:
`‖Δ parámetros‖ = 0` exacto, en tres semillas. Pero `learn()` escribe cinco piezas más de estado
dependiente de experiencia, fuera del optimizador, y la mayor se mueve muchísimo:

```
                         FULL        ABL
‖Δ parámetros‖          1.714          0        ← la intervención es perfecta aquí
‖Δ M‖                   41.09      25.02        ← y no llega hasta aquí
‖Δ M‖ / ‖M inicial‖     76.9×      46.8×
saturación de M          100 %      100 %
```

`longterm_memory.M` es un `nn.Parameter` escrito directamente en `memory.py:239`, bajo `no_grad`,
en cada paso y en los dos brazos. También quedan fuera el buffer episódico y `_energy_baseline`.

Consecuencia: **el brazo suprimido no es un control de cero aprendizaje**, así que el contraste
FULL−ABL no mide «aprender frente a no aprender». El primer piloto de LEARN-A1 queda bloqueado
hasta que se elija entre las cuatro opciones que el documento nombra sin elegir.

## 36.3 · Dos afirmaciones mías sobre M, y su refutación medida

La primera versión de esta sección decía que M satura al 100 % y que su regla de escritura «no tiene
decaimiento». Las dos eran falsas, y `scripts/m_information_audit.py` las midió:

- **La saturación real es 9–25 %**, no 100 %. La cifra anterior era `|M|max / 10`, es decir *si algún*
  elemento tocaba el tope — una mala estadística presentada como un hecho.
- **Sí hay decaimiento.** `M·(1−g)` es el término de retención, y con `g` medido entre 0.43 y 1.0
  (medio ~0.79) el olvido es fuerte. Afirmé una propiedad formal sin medir `g`.

## 36.4 · Qué transporta M, medido

Que M se mueva mucho no demuestra que lleve información. Con el pipeline real, la función de lectura
del propio agente y un contrafáctico de misma geometría y contingencia invertida:

```
signos distintos entre M_A y M_B      0 / 32 en las tres semillas
coseno(M_A, M_B)                      0.802 · 1.000 · 1.000   ← idénticas en 2 de 3
‖Δ logits‖ relativo al intercambiar M  0 … 4.3 %
acciones cambiadas                    0   en las tres semillas y en los dos brazos
inversiones de preferencia            0
```

M tiene ruta causal real hacia la política —entra dos veces en la lectura, `key_proj(M)` fija la
atención y `attn @ M` es el valor— pero intercambiar toda la memoria por la de una historia con la
contingencia opuesta **no cambió una sola decisión**. `M_MAPPING_CARRIER = NO`.

Además, desactivar la memoria a largo plazo por composición es **local**: `_state_dim` no cambia,
ningún otro módulo cambia de recuento de parámetros, y lo único que ocurre es que `longterm_memory`
sale de la lista del learner. `LTM_DISABLE_IS_COMPOSITION_LOCAL = PASS`.

Lo que sigue abierto: buffer episódico, estado recurrente, homeostasis y baseline del learner están
clasificados **leyendo el código**, no probados con el mismo contrafáctico. Sus gates quedan en
`UNKNOWN`, y `UNKNOWN` no se convierte en `PASS`.


---

# XXXVII · Fundación causal del organismo · OCF-G1 y OCF-G3

**2026-09-18.** Antes de dar motivación al organismo hay que poder demostrar qué mecanismo produjo
qué cambio. Los gates van como **OCF-G1..OCF-G5** porque G0–G8 ya están tomados con otro
significado en este mismo documento.

## 37.1 · OCF-G1 · Autoridad de estado — NO PASA

`scripts/state_authority_probe.py`. No lee el código: intercepta `__setattr__` del agente y de cada
submódulo, envuelve `perceive`/`decide`/`learn`, y hashea el conjunto adaptativo al final de cada
fase para atrapar las escrituras en sitio que `setattr` no ve.

De 21 estados, **uno** tiene dos escritores: `homeostasis._energy` (perceive 68, learn 68). Los
otros veinte, uno solo. `homeostasis._threshold` no lo escribe nadie. `_energy_baseline` se mueve
45 de 68 veces, no 68: depende de `_last_log_prob`, así que su deriva cuenta políticas producidas,
no pasos vividos.

La sonda demuestra su propia pasividad: la vida instrumentada y la limpia terminan con la misma
huella en las seis piezas. Sin eso no sería evidencia — la sonda anterior de esta familia infló dos
magnitudes ×18.6 y ×10 por contaminarse, y no se vio hasta una verificación adversarial.

## 37.2 · OCF-G3 · FULL_ADAPTIVE_FREEZE — construido, gate ABIERTO

`terrario/agent/adaptive_freeze.py`, `scripts/adaptive_freeze_gate.py`.

Una **sola autoridad lógica** (`AdaptiveFreeze.allow`) y cuatro puntos de commit que la consultan,
en vez de cuatro `if freeze:` dispersos por A4. Congela exactamente la frontera adoptada
—parámetros, buffer episódico, `M`, `_energy_baseline`— y nada más: percepción, inferencia,
pérdidas, gradientes y candidatos de experiencia siguen funcionando. Lo prohibido es el **commit**,
no el cálculo.

**Bloquea antes de la escritura; no revierte después.** `escribir → leer → revertir` no equivale a
`no escribir → leer` aunque las dos terminen con el mismo hash.

| Componente | NORMAL | heredado | FULL |
|---|---|---|---|
| parámetros | cambia | no cambia | no cambia |
| buffer episódico | cambia | cambia | no cambia |
| `M` | cambia | cambia | no cambia |
| `_energy_baseline` | cambia | cambia | no cambia |
| candidatos adaptativos | existen | existen | **existen** |
| commits adaptativos | 60/60 por writer | parciales | **0 de 240** |

Doce criterios en verde, incluida la ruta real (`run_step`, no sólo replay), pasividad
auditoría-ON/OFF sobre acciones y energía, y regresión: NORMAL es idéntico campo por campo al A4
previo a la infraestructura.

**Pero el gate queda ABIERTO por condición de parada 10.** `_adaptive_state_hash`
([adaptation.py:198](terrario/experiment/adaptation.py:198)) **no ve `_energy_baseline`** —se le
puede sumar 42.0 y no se mueve— mientras que la frontera adoptada en §XXXVI es «lo que esa huella
ya trazaba **más `_energy_baseline`**». La huella agregada del proyecto no cubre la frontera que el
proyecto adoptó, así que el criterio de igualdad agregada se satisface en vacío para esa pieza.
`adaptation.py:331` la usa antes de una transferencia. El propio gate lo comprueba y se niega a
declarar PASS mientras la omisión exista.

Detalle en `docs/ORGANISM_CAUSAL_FOUNDATION_01.md`.

---

# XXXVIII · Corpus, teoría, hipergrafo, memoria y composición · relectura del 2026-09-21

Releído contra `bbaa3e5`. **Sustituye a §XXXII** en las cifras del corpus, en el
estado de la citabilidad de conceptos y en el catálogo de composición; el
veredicto estructural de §XXXII —contratos tipados de alta calidad, dos
subsistemas vacíos, un solo punto de contacto con el ciclo experimental— se
sostiene entero y no se repite aquí.

**Lo que cambia respecto al 17-09:** el corpus físico creció ×2,4 sin que el
snapshot se enterara; un concepto ya es citable por contrato aunque nadie lo
cite todavía; el catálogo de composición tiene un concepto más.

## 38.1 · Tamaño real de la capa, recontado

| Subsistema | Ficheros | Líneas | Filas en producción |
|---|---:|---:|---|
| `terrario/lab/theory/` | 8 | 1 549 | 1 snapshot en disco, **cero tablas** |
| `terrario/lab/hypergraph/` | 5 | 564 | vive dentro del snapshot |
| `terrario/lab/crossgraph/` | 10 | 2 130 | **0 filas en 9 tablas** `cross_*` |
| `terrario/lab/referencegraph/` | 7 | 1 743 | **0 filas en 22 tablas** `ref_*` |
| `terrario/lab/persistence/` | 8 | 2 319 | 30 tablas con filas, ninguna de esta capa |
| `agent_composition.py` + familia `capability_*` | 6 | 1 865 | — |

`.terrario/terrario.db` tiene **72 tablas, 42 vacías**. Las 30 con filas son
todas de ejecución y preregistro —`artifacts` 441, `blob_manifests` 1 480,
`scientific_execution_events` 1 664, `preregistration_components` 1 410—. Las
`ref_*` y las `cross_*` están **enteras a cero**, y también lo están
`empirical_evidence` y `empirical_evidence_links`: la tabla donde se adjuntaría
evidencia a una hiperarista existe y nunca recibió una fila.

## 38.2 · El corpus físico · creció y el snapshot no se enteró

```
/home/wis/Documentos/teoria de la inteligencia/
  101 PDFs en 10 subdirectorios
     acquisition_v0.4                          28
     doc estudios cientificos                  29
     hea_corpus_v2_complete_bundle             15
     homeostatic_enactive_agency_corpus_v0.1   15
     documents_v0.3                            11
     otros cinco                                3
```

El snapshot `theory-f59dbb6d6ee3850c` declara **44 fuentes**
([ingestion_summary.json](theory_snapshots/theory-f59dbb6d6ee3850c/ingestion_summary.json)).
§XXXII contó 42 PDFs el 17-09 en la raíz de esa carpeta; hoy hay 101 repartidos
en subdirectorios versionados. **El corpus creció ×2,4 y nada lo ingirió.**

No es un fallo del importador: `referencegraph/import_corpus.py` consume
`manifest/CORPUS_MANIFEST.jsonl`, que **sigue sin existir en ningún sitio del
disco**, y por eso las 22 tablas `ref_*` siguen a cero. Son dos sistemas
paralelos que nunca se tocaron, y ahora divergen también en tamaño.

## 38.3 · Lo que el snapshot sí contiene, contado

```
44 fuentes · 189 claims · 283 conceptos raw · 224 candidatos canónicos
206 relaciones · 8 hiperaristas · 12 ambigüedades · 12 conflictos
1 035 nodos de teoría · 956 aristas · 141 nodos de evidencia · 136 aristas
```

Los 283 conceptos son **dos capas con propiedades distintas**, y mezclarlas es
lo que hace parecer al corpus más rico de lo que es:

| Capa | Filas | Nombres normalizados distintos | Con definición del autor | Mencionados en algún claim |
|---|---:|---:|---:|---:|
| `CONCEPTS_RAW_v0.1.csv` | 224 | 187 | 224 | **56** |
| `CONCEPTS_RAW_PATCH_v0.3.csv` | 59 | 59 | **0** | 17 |

Las 59 filas del parche **no tienen ni una definición del autor**. No son
conceptos citables: son nombres.

## 38.4 · Citabilidad de un concepto · el contrato existe, el uso no

`d1485b4` cerró la mitad de L-1 que faltaba. El esquema sólo sabía direccionar
claims, y por eso un concepto del corpus —la curiosidad adaptativa de Oudeyer—
existía como fila y **ninguna capacidad podía apuntarle**.

`CorpusConceptReference`
([capability_operationalization.py:84](terrario/lab/capability_operationalization.py:84))
no es un puntero sino una **cadena**:

```
concepto  →  claim que lo menciona, con locator  →  fuente [TI-XXXX]
```

El eslabón del medio es lo que la hace verificable: un concepto no tiene sitio
en un documento que un tercero pueda abrir, y el claim sí. La validación rechaza
un concepto ausente de su claim declarado y uno cuya definición del autor esté
vacía —el guardián que habría rechazado la capa v0.3 entera—.

El segundo arreglo del mismo commit: `snapshot_root()` leía el id de una
constante del módulo
([capability_operationalization.py:26](terrario/lab/capability_operationalization.py:26)),
así que una referencia que declarara un segundo snapshot miraba dentro del
primero, encontraba su manifiesto y fallaba con «corpus snapshot manifest hash
mismatch» —un mensaje que acusa al corpus de corrupción cuando el defecto era no
haber ido al directorio correcto—. Ahora resuelve desde la referencia. **El
laboratorio puede tener más de un corpus.**

**Y nadie cita todavía por esa cadena.** `grep` sobre todo el árbol: las únicas
apariciones de `CorpusConceptReference` son su propia declaración y
[su test](tests/test_capability_operationalization.py:84). Las
operacionalizaciones reales siguen citando sólo claims
([capability_operationalization.py:186](terrario/lab/capability_operationalization.py:186)).
El contrato está construido y sin estrenar, que es el mismo patrón que §XXXII
documentó para `crossgraph/d2trace.py`.

**El techo no es del código, es del corpus:** de 187 nombres normalizados en la
capa v0.1, **56** aparecen en algún claim. Los otros 131 no son citables hasta
que alguien extraiga un claim que los mencione.

## 38.5 · El brazo documental · el corpus que la puerta no vigila

Desde el 18-09 hay un segundo lugar donde vive conocimiento extraído, y no es
código ni base de datos:

| Fichero | Filas |
|---|---:|
| `docs/handoff/HEA_CLAIMS_EXTRAIDOS_v1.csv` | 176 |
| `docs/handoff/HEA_CONCEPTOS_EXTRAIDOS_v1.csv` | 115 |
| `docs/handoff/HEA_CONCEPTOS_SIN_DEFINICION_v1.csv` | 71 |
| `docs/INVENTARIO_CONCEPTOS_01.md` · `docs/ANALISIS_SELECCION_ORGANISMO_01.md` | — |

Y aquí está el defecto de la propia cartografía: **G1 no los vigilaba.** El
patrón de referencias de
[cartografia_check.py](scripts/cartografia_check.py) sólo reconocía rutas bajo
`terrario`, `tests`, `scripts`, `scenarios`, `configs` y `knowledge`, con
extensiones `py|yaml|yml|json|md`. Ni `theory_snapshots/`, ni `docs/handoff/`,
ni `.csv`. El corpus era, por construcción, invisible para el guardián del mapa:
podía crecer ×2,4 sin que ninguna sección quedara obsoleta. Corregido en esta
misma pasada.

**Ampliado de nuevo el 2026-09-21** (§XLII): el gate ya no vigila sólo hashes de
fichero, también verifica cada cita `fichero:línea` del documento —inexistente,
fuera de rango o en blanco—. El hash no podía ver que una cita se pudriera
mientras el fichero registrado seguía igual, y cuatro lo habían hecho.

## 38.6 · Hipergrafo · sigue siendo estructura, no conocimiento

Reverificado línea a línea; §32.4 se sostiene sin cambios:

```
relation_type         TESTABLE_CONJUNCTION | SEMANTIC_ROLE_COMPOSITION      (2)
corroboration_status  NOT_CLAIMED | STRUCTURAL_COMPOSITION_NOT_CORROBORATION (2)
```

([theory_operational.py:107](terrario/lab/hypergraph/theory_operational.py:107),
[:111](terrario/lab/hypergraph/theory_operational.py:111),
[:270](terrario/lab/hypergraph/theory_operational.py:270),
[:273](terrario/lab/hypergraph/theory_operational.py:273))

El segundo valor de `corroboration_status` existe **para declarar que no hay
corroboración**, y las dos tablas que guardarían la que hubiera están vacías.
No existen `REQUIERE / REGULA / HABILITA / COMPENSA`: el tipado fuerte de
relaciones vive en `RelationStrength`
([theory/models.py:25](terrario/lab/theory/models.py:25)) y se aplica a CSV de
auditoría, no al hipergrafo.

## 38.7 · La memoria · dos cosas distintas con el mismo nombre

**La del organismo** está en §XI y no se repite: episódica indexada por
`_last_latent`, largo plazo leída por `hidden`. Lo único que conviene traer aquí
es la consecuencia para esta capa: **ninguna de las dos toca `s_t`**, y por eso
ampliar el estado no contamina las claves de memoria.

**La del laboratorio** es otra cosa, y está partida en tres sitios que no se
hablan:

| Dónde | Qué guarda | Formato |
|---|---|---|
| `.terrario/terrario.db` | ejecución, preregistro, artefactos | SQLite, 1 143 líneas de DDL en [persistence/migrations.py](terrario/lab/persistence/migrations.py) |
| `theory_snapshots/theory-*/` | el conocimiento: 1 035 nodos, 956 aristas | CSV + `theory_graph.json` |
| `docs/handoff/*.csv` | claims y conceptos extraídos a mano | CSV, sin esquema |

`TheoryGraphStore` **no persiste en base de datos**: es un objeto en memoria con
`save()`/`load()` a JSON
([theory/store.py:85](terrario/lab/theory/store.py:85)). La base reservó 31
tablas para esta capa y las 31 están vacías. La memoria del conocimiento es un
directorio de ficheros; la de la ejecución es la base. No hay puente.

## 38.8 · Composición de habilidades · el único punto conectado

`agent_composition.py` sigue siendo la pieza de esta capa que **sí** toca el
ciclo experimental, y ahora son **once** conceptos, no diez: `fd725e3` añadió
`use_curiosity` —«convierte el error de su propia predicción en motivo para
actuar»— con bloque de corpus 28
([agent_composition.py:70](terrario/lab/agent_composition.py:70)).

```
use_temporal · use_episodic_memory · use_longterm_memory · use_world_model
use_uncertainty · use_curiosity · use_planner · use_online_learning
use_entropy_regularization · use_factored_action · use_homeostasis
```

Consumidores reales de `validate_selection`, que es lo que hace que una
selección de capacidades sea un contrato y no un diccionario:

| Consumidor | Línea |
|---|---|
| `terrario/lab/sandbox_runtime.py` | [:52](terrario/lab/sandbox_runtime.py:52) |
| `terrario/lab/api.py` | [:428](terrario/lab/api.py:428) |
| `scripts/experiment_capability_acquisition.py` | [:155](scripts/experiment_capability_acquisition.py:155) |
| `scripts/experiment_t0_vs_t1.py` | [:125](scripts/experiment_t0_vs_t1.py:125) |

**`corpus_block` sigue sin tener lector.** Es un `int` en
[agent_composition.py:39](terrario/lab/agent_composition.py:39) y las otras dos
apariciones en todo el árbol son prosa que dice que nadie lo lee
([capability_passport.py:160](terrario/lab/capability_passport.py:160),
[passport_check.py:84](scripts/passport_check.py:84)). Es decir: el enlace
concepto→corpus del catálogo de composición sigue siendo un número sin
referencia, **mientras al lado existe `CorpusConceptReference`, que es
exactamente la cadena que le falta y que nadie ha conectado**.

Ésa es la costura más corta de toda la capa: once conceptos con un entero
huérfano, y a dos ficheros de distancia el contrato verificable que lo
sustituiría.

## 38.9 · La puerta, ahora automática

G1 dejó de depender de acordarse. `scripts/cartografia_hook.py` ata el
comprobador a dos momentos del arnés (`.claude/settings.json`):

* **al abrir sesión** ejecuta el gate real —1,8 s— y mete su veredicto en el
  contexto, de modo que ninguna sesión empieza sin saber qué secciones
  envejecieron;
* **después de cada `Edit`/`Write`** mira sólo el manifiesto y nombra la sección
  que ese fichero acaba de dejar obsoleta. Milisegundos, sin importar `terrario`.

La autoridad sigue siendo [cartografia_check.py](scripts/cartografia_check.py);
el hook no decide nada por su cuenta y jamás rompe el turno —cualquier excepción
sale como silencio—, porque un hook que rompe el turno se desactiva y entonces
no comprueba nada.

**Lo que este mecanismo NO arregla, y conviene tener escrito:** el manifiesto se
regenera con `--write`, y `--write` no puede comprobar que alguien haya releído.
Si se regenera después de cambiar el código sin reescribir el texto, el gate se
pone verde sobre prosa vieja. El hash prueba que el fichero no cambió desde la
última vez que se dijo «lo leí»; no prueba que se leyera.

---

# XXXIX · La implementación de la capa de conocimiento, leída

Relectura del 2026-09-21 sobre `bbaa3e5`. §XXXII contó y §XXXVIII recontó; **esta
sección lee**. Lo que sigue es el mecanismo: qué calcula cada pieza, con qué
dato, bajo qué guarda y con qué consecuencia. Cada afirmación lleva
`fichero:línea` o la orden que la produjo.

Estados de conocimiento según el contrato del 2026-09-21: **K0** establecido,
**K1** documentado pero verificable en código, **K2** no resuelto —no se rellena
por intuición—, **K3** requiere evidencia externa.

---

## 39.1 · El defecto vivo · el catálogo de composición está roto

**K0, medido hoy, tres pruebas en rojo desde `fd725e3` (18-09).**

```
$ python -c "from terrario.lab.agent_composition import catalogue; catalogue()"
KeyError: 'use_curiosity'                       agent_composition.py:176

$ pytest tests/test_agent_composition.py
FAILED test_every_offered_concept_is_a_key_the_agent_actually_reads
FAILED test_the_catalogue_carries_what_a_person_needs_to_choose
FAILED test_the_mix_reads_as_a_sentence_not_as_flags
```

El contrato del módulo está en su propia cabecera
([agent_composition.py:3](terrario/lab/agent_composition.py:3)): «`key` es la
clave de configuración literal que A4 lee, así que un concepto que deja de
existir deja de ser ofrecible, y `validate_selection` rechaza una clave
desconocida en vez de ignorarla — **una errata que cambia nada en silencio es el
peor modo de fallo que puede tener una pantalla de composición**».

Eso es exactamente lo que ocurre ahora:

| | |
|---|---|
| `CONCEPTS` | 11 conceptos |
| booleanos en `DEFAULT_CONFIG` de A4 | 12 |
| concepto sin bool en A4 | **`use_curiosity`** |
| bools de A4 sin concepto | `learning_commit_enabled`, `full_adaptive_freeze` |

`catalogue()` hace `bool(DEFAULT_CONFIG[c.key])` para cada concepto
([:124](terrario/lab/agent_composition.py:124)) y `describe_selection()` lo
repite ([:176](terrario/lab/agent_composition.py:176)), así que **las dos revientan**. Y `GET /api/agent-concepts`
([api.py:122](terrario/lab/api.py:122)) devuelve `thaw(agent_catalogue())`: el
endpoint que alimenta la pantalla de composición está caído.

Mientras tanto `validate_selection({"use_curiosity": True})` **acepta la clave**
—está en `_KEYS`— y la pasa a un A4 que no la lee. El modo de fallo que la
cabecera declara el peor posible, ocurriendo en el módulo que lo declara.

**La causa no es un descuido de tipeo, es una categoría.** `fd725e3` construyó
la curiosidad como **A5**, un descendiente, no como un interruptor de A4: «A5 is
A4's descendant, not A4 with a flag… turn `use_curiosity` off and A5 is A4». La
clave la lee [a5_cybernetic.py:35](terrario/agent/agents/a5_cybernetic.py:35).
El catálogo modela **un** organismo y el linaje ya tiene **dos**.

Las dos salidas no son equivalentes y ninguna es una reparación mecánica:

1. **El catálogo pasa a ser por agente** — cada `Concept` declara a qué
   configuración pertenece. Es lo correcto si van a existir A5, A6…
2. **`use_curiosity` sale del catálogo de A4** y la composición de A5 se ofrece
   aparte. Más pequeño, y deja el catálogo mintiendo por omisión sobre lo que el
   linaje puede componer.

Es una decisión de modelo, no un arreglo, y por eso queda declarada aquí en vez
de tomada.

## 39.2 · Estado científico de las capacidades · calculado, no declarado

**K0.** `status_of` ([capability_passport.py](terrario/lab/capability_passport.py))
no lee un campo `status`: lo deriva, en orden de precondición —contrato completo
→ procedencia al corpus → pureza de la intervención → existe un mundo que la
exige → endpoint calibrado—. Ejecutado hoy:

```
$ python scripts/passport_check.py
  procedencia   falla en 5 de 10
  pureza        falla en 3 de 10
  mundo         falla en 3 de 10
  instrumento   falla en 8 de 10
  listas para certificar: 1 de 10 — LEARN-A1
```

**La restricción que manda es el instrumento, y no por falta de instrumentos.**
Los 8 del registro están los 8 en `REPORTABLE`. Lo que ocurre es que 8 de las 10
capacidades declaran un endpoint que **no existe a propósito**:

```
HOMEO-A1   PENDIENTE-regulacion-condicionada-al-estado      UNREGISTERED
EPMEM-A1   PENDIENTE-acierto-condicionado-a-historia-releva… UNREGISTERED
LTMEM-A1   PENDIENTE-retencion-tras-interferencia           UNREGISTERED
LEARN-A1   conversion_aprendizaje                            REPORTABLE
UNC-A1     PENDIENTE-calibracion-de-incertidumbre           UNREGISTERED
PLAST-A1   PENDIENTE-velocidad-de-revision-tras-inversion   UNREGISTERED
TEMP-A1    PENDIENTE-desambiguacion-por-historia            UNREGISTERED
WM-A1      examen_prediccion                                 REPORTABLE
PLAN-A1    PENDIENTE-eleccion-no-miope                      UNREGISTERED
CURIO-A1   PENDIENTE-exploracion-dirigida-por-error         UNREGISTERED
```

El prefijo `PENDIENTE-` es un nombre que el registro no puede resolver, así que
`state_of` devuelve `UNREGISTERED` y el pasaporte queda bloqueado en
`NO_CALIBRATED_ENDPOINT`. Es **lo contrario** del modo de fallo «defaults que
convierten fallos en números plausibles»: en vez de sustituir el endpoint que
falta por una métrica parecida, se declara un hueco que la máquina puede ver.
Es la mejor decisión de diseño de toda la capa.

## 39.3 · Corpus · dónde se decide lo epistemológico

**K0 tras leer.** Tres decisiones cargadas se toman por coincidencia de
subcadena, y conviene saberlo antes de citar el snapshot:

| Decisión | Mecanismo real | Dónde |
|---|---|---|
| ¿claim del autor o inferencia del analista? | `"ANALYST" in value.upper()` | [ingestion.py:47](terrario/lab/theory/ingestion.py:47) |
| fuerza de una relación (5 niveles) | subcadenas mezclando español e inglés: `EXPLICIT_CAUSAL`, `REQUIERE`, `DEPENDE`, `FACILITA`, `MODULA`, `INHIBE` | [ingestion.py:51](terrario/lab/theory/ingestion.py:51) |
| ¿la fuente vale como evidencia? | `QUARANTIN` / `MISMATCH` / `UNAVAILABLE` en el texto de integridad | [ingestion.py:126](terrario/lab/theory/ingestion.py:126) |

La frontera autor↔analista es la distinción más cargada del corpus y se decide
con `in`. Un claim que diga «inferred» sin la palabra `ANALYST` entra como
`AUTHOR_CLAIM`. **K2: cuántos de los 189 claims están mal clasificados por esto
no está medido.**

**Lo que sí es sólido.** El snapshot es direccionable por contenido: sha256 por
artefacto, identidad = sha256 de la lista de entradas, colisión comprobada al
reconstruir, y `missing_artifacts` declarado en el manifiesto
([snapshot.py](terrario/lab/theory/snapshot.py)). Y la verificación de la
evidencia operacional es fail-closed en el hash —compara el sha256 del manifiesto
contra el del snapshot base y cada artefacto contra el suyo— **pero fail-open en
la ausencia**: `if not self.evidence_root.exists(): return`
([ingestion.py:90](terrario/lab/theory/ingestion.py:90)). Sin el directorio no
hay error, hay silencio.

**El locator, exacto.** `ClaimLocator` tiene ocho campos —página, sección,
subsección, figura, tabla, párrafo, apéndice, suplemento—, todos opcionales
([referencegraph/domain.py](terrario/lab/referencegraph/domain.py)). En todo el
árbol se construye **una sola vez, sin argumentos**:
`ClaimLocator()` en
[import_corpus.py:367](terrario/lab/referencegraph/import_corpus.py:367).

## 39.4 · El grafo de teoría · 956 aristas que existen si dos cadenas coinciden

**K0 tras leer `build_graph`** ([theory/store.py:104](terrario/lab/theory/store.py:104)).
El grafo no se declara: se **infiere por emparejamiento de texto**.

* claim → fuente: primero por título casefold; si no, por id exacto; si no, por
  la regex `\[((?:TI|DEV|X)\w*-?\d+)\]` buscada dentro del campo `source_id`.
* relación → concepto: por `nombre_original` o `nombre_normalizado_provisional`
  en casefold.
* componente de hiperarista → concepto: el mismo emparejamiento.

Consecuencia que hay que llevar pegada al número: los **1 035 nodos y 956
aristas** del snapshot son las coincidencias que hubo, no las relaciones que el
corpus afirma. Una diferencia de grafía produce **silencio**, no error. **K2: la
tasa de aristas perdidas por no-coincidencia no está medida, y es medible.**

`TheoryGraphStore` no persiste en base de datos: es un objeto en memoria con
`save()`/`load()` a JSON ([store.py:85](terrario/lab/theory/store.py:85)).
`paths()` y `lineage()` son BFS con profundidad máxima 8; `lineage` devuelve
**todas** las rutas ascendentes sin declarar ninguna autoritativa.

## 39.5 · La fábrica de hipótesis · qué calcula de verdad

**K0, ejecutada hoy sobre el snapshot real.**

```
8 hiperaristas → 8 familias → 232 rivales
todas:  identificabilidad = DESCRIPTIVE_ONLY
        prioridad = (0.7, 0.5, 1.0, 0.3, 0.4, 0.6)
        umbrales preregistrados = {}
validate() = ('critical confounders unaddressed',)   en las ocho
```

Mecanismo, pieza por pieza:

* **Generación de rivales** ([factory.py:174](terrario/lab/theory/factory.py:174)):
  `itertools.combinations` sobre los componentes, **todos los subconjuntos no
  vacíos** (2ⁿ−1) más una nula. Seis componentes → 64. El «mecanismo propuesto»
  de cada rival es literalmente `" + ".join(components)`, y las condiciones de
  falsación son plantillas f-string.
* **Identificabilidad**: el compilador llama a la auditoría con un diccionario
  **escrito a mano**, `{"paired_seeds": True, "identical_environment": True}`
  ([factory.py:278](terrario/lab/theory/factory.py:278)). Los otros cinco checks
  —cambio de un solo objetivo, capacidad, información, cómputo y exposición
  emparejadas— quedan en `False` sin mirar nada. 2 de 7 ⇒ `DESCRIPTIVE_ONLY`
  **para todo diseño que la fábrica produzca, por construcción**.
* **Prioridad** ([factory.py:280](terrario/lab/theory/factory.py:280)): seis constantes literales, idénticas en las ocho familias. No
  es una puntuación; es una tupla.
* **Confusores** ([factory.py:249](terrario/lab/theory/factory.py:249)): `from_edge` crea cada `ConfounderSpec` con `critical=True` y
  `mitigation=None`, y `DesignValidator` rechaza «critical confounders
  unaddressed». **Por tanto `to_experiment_spec` no puede tener éxito nunca**
  sobre un diseño generado: la fábrica es estructuralmente incapaz de emitir una
  especificación ejecutable sin intervención humana. Eso no es un defecto —es un
  gate— pero conviene decirlo como lo que es y no como «faltan datos».
* **La puerta de revisión, por dentro**: `build_portfolio` sella la familia como
  `APPROVED_FOR_EXPERIMENT_DESIGN` **él mismo** para superar el `PermissionError`
  del compilador, y devuelve el diseño otra vez en `GENERATED`
  ([factory.py:338](terrario/lab/theory/factory.py:338)). El artefacto que sale
  respeta la puerta; el objeto que entró al compilador la saltó.

## 39.6 · La «revisión científica» · una tabla de juicios, no un análisis

**K0.** `review_portfolio` es determinista e inspeccionable, y eso es cierto.
Pero lo que evalúa está **escrito a mano**: `_DETAILS`
([scientific_review.py:154](terrario/lab/theory/scientific_review.py:154)) es un
diccionario indexado por `HYPERCAND-01 … 08` con el estado del constructo, la
disposición, los roles, los proxies, la métrica y las notas profundas de cada
uno. Y `_dimensions` ([:249](terrario/lab/theory/scientific_review.py:249)) es una
**tabla literal de nueve enteros por candidato**,
sobre la que se calcula el frente de Pareto.

Dos consecuencias que hay que saber antes de usarla:

1. Un noveno candidato **levanta `KeyError`**. La revisión no procesa una
   hiperarista que no sea una de las ocho.
2. `pseudo_falsifiable` está fijado a `True` para todas las entradas
   ([:229](terrario/lab/theory/scientific_review.py:229)), y el orden preferente
   de salida `("HYPERCAND-02","HYPERCAND-01","HYPERCAND-08")` es una constante.

No es deshonesto —codifica un análisis humano y lo vuelve reproducible— pero es
un **registro**, no un analizador, y llamarlo revisión invita a leerlo como lo
segundo.

## 39.7 · Hipergrafos · son tres, no uno

**K0.** La pregunta «¿hiperaristas reales o emulación binaria?» tiene tres
respuestas porque hay tres sistemas distintos con ese nombre:

| Sistema | Qué modela | Aridad | Servido en |
|---|---|---|---|
| **Teórico** · [theory_operational.py](terrario/lab/hypergraph/theory_operational.py) | mecanismos científicos con procedencia al corpus | **n-aria real** | `/api/theory-operational-*` |
| **Operacional** · [operational.py](terrario/lab/hypergraph/operational.py) | el plano de ejecución: HYPOTHESIS → EXPERIMENT_DRAFT → PREREGISTRATION → EXECUTION_PLAN → TRIAL_INTENT → … → CAS_BLOB | tipada | `/api/operational-hypergraph` |
| **Intercambio** · [models.py](terrario/lab/hypergraph/models.py) + [adapter.py](terrario/lab/hypergraph/adapter.py) | ingesta JSON/YAML de artefactos derivados | **binaria** (`source`, `target`) | `/api/hypergraph` |

El endpoint que se llama `hypergraph` a secas sirve el **binario**. El de
hiperaristas reales es el teórico, y se llama de otra manera.

**El teórico es lo mejor construido del repositorio, y su mecanismo es una
cadena de verificación, no una declaración.** `validate_bindings`
([:185](terrario/lab/hypergraph/theory_operational.py:185)) resuelve cada
ligadura contra el claim **y** la fuente importados, y rechaza si: el candidato
no coincide, la procedencia no resuelve, la fuente no es evidencia válida, la
revisión del claim o de la fuente no coincide, **el locator no coincide**, el
claim no resuelve al registro de fuente declarado; y si la versión de la fuente
empieza por `sha256:`, **abre el PDF real y compara el hash**.

`materialize` ([:216](terrario/lab/hypergraph/theory_operational.py:216)) sólo
acepta `APPROVED_CANDIDATES = {"HYPERCAND-02", "HYPERCAND-08"}`
([:22](terrario/lab/hypergraph/theory_operational.py:22)) —dos,
escritos a mano—, exige una ligadura por componente, roles sin duplicar, y
**prohíbe promover el estado epistemológico**. `compose` exige puentes de
compatibilidad con `rationale` explícito y funde ligaduras por
`(participante, rol)`, abortando con `NO_COMPOSITION` si dos roles compatibles
traen semántica de fuente distinta.

`semantic_id` es `content_hash` del payload canónico con la ruta del snapshot
normalizada —el prefijo absoluto de montaje es detalle de despliegue, no
semántica—, y `from_payload` **recalcula la identidad y rechaza si no coincide**.
Lo mismo hace `HypothesisDraft.from_payload`
([theory/models.py](terrario/lab/theory/models.py)). La deserialización es
a prueba de manipulación en las dos.

## 39.8 · La memoria · dos sistemas, dos mecanismos

**K0 · la del organismo** ([agent/memory.py](terrario/agent/memory.py)).

`EpisodicMemory` no es una red: es un **buffer circular de 1 000** entradas
`{embedding, action, energy_delta, prediction_error, timestamp}` con escritura
por índice rotatorio. La lectura es coseno contra todo lo almacenado, `topk`, y
`softmax` **sobre las similitudes top-k**. Detalle que importa para interpretar
su efecto: el softmax se aplica a cosenos en `[-1,1]`, así que cuando las k
similitudes son parecidas los pesos salen casi uniformes — la recuperación pesa
poco aunque encuentre el vecino correcto. Con el buffer vacío devuelve ceros y
lo registra en la traza.

`LongTermMemory` sí es `nn.Module`: matriz `M` de 64×128 como `nn.Parameter`,
lectura por atención escalada, y escritura con puerta:
`M = M·(1−g) + outer(w, v)·g`. **La escritura ocurre fuera del optimizador**,
bajo `no_grad`, y lleva tres guardas explícitas: `nan_to_num_` sobre `M` antes de
escribir, la actualización propuesta sólo se copia si `torch.isfinite(...).all()`,
y se recorta a `[-10, 10]`. El resultado se registra como `write_accepted` en la
traza. Es estado que cambia la conducta sin pasar por el gradiente, y está
protegido a propósito para que una escritura corrupta no envenene todas las
lecturas posteriores.

**K0 · la del laboratorio.** `canonical.py`
([persistence/canonical.py](terrario/lab/persistence/canonical.py)) es la
columna de identidad de toda la capa: `plain()` es un canonizador total y
fail-closed —levanta `CanonicalizationError` ante un tipo no soportado y
**prohíbe los flotantes no finitos** en un artefacto científico—, los conjuntos
se ordenan por su propio json canónico, y `content_hash` es sha256 de eso. Cada
`semantic_id` del repositorio cuelga de esta función.

`ArtifactRepository` ([persistence/store.py](terrario/lab/persistence/store.py))
es el almacén real: migraciones con checksum, versiones por artefacto, eventos
de estado, auditoría, blobs CAS registrados por hash, exportación e importación
de bundles con validación, y `integrity_check`. **Las 42 tablas vacías de las 72
no son un almacén roto: son el esquema de una capa que nunca ingirió.**

## 39.9 · Lo que sigue sin saberse · K2 declarados

1. **Cuántos claims están mal clasificados** por el test de subcadena `ANALYST`.
   Medible sobre los 189 claims con una revisión manual de muestra.
2. **Cuántas relaciones del corpus no llegaron al grafo** por no coincidir la
   grafía del concepto. Medible comparando `RELATIONS_AUDIT` contra las aristas
   creadas.
3. **Si los 57 PDFs que el snapshot no conoce** aportan claims nuevos o son
   duplicados de los 44 ingeridos. No es inferible sin ingerirlos.
4. **Qué mide realmente cada `PENDIENTE-*`**: ocho endpoints declarados por su
   nombre y sin definición operacional. Es **K3** para al menos dos de ellos
   —calibración de incertidumbre y elección no miope—, donde el proyecto no tiene
   evidencia interna para fijar el criterio.
5. **Si la recuperación episódica tiene efecto conductual** dado el aplanamiento
   del softmax descrito en §39.8. Medible con una lesión: fijar los pesos a
   uniformes y comparar.

---

# XL · Atlas 02 · El organismo · runtime y linaje A0–A5

Lectura del 2026-09-21 sobre `7051d7f`. Cubre los puntos 2 y 3 del contrato de
conocimiento: el lazo `percepción → estado → decisión → acción → consecuencia →
aprendizaje`, y qué hereda, qué cambia y qué ejecuta cada organismo del linaje.

`terrario/agent/` son 3 403 líneas. Se leyeron enteras las que deciden conducta.

**Solapa con §VI–§XIV y §XXVI, que ya cubrían este terreno y estaban vigentes
por hash.** Esta lectura no las consultó antes, y por eso re-derivó el planner y
se quedó corta en homeostasis; las correcciones están abajo, marcadas. Ver §XLII.

## 40.1 · El paso autoritativo · quién hace qué y en qué orden

`run_step` ([world/transition.py:316](terrario/world/transition.py:316)) es el
único sitio donde el organismo y el mundo se tocan. El orden exacto:

```
 1  observation_t = world.get_observation(0, view_radius, channels)
 2  agent.perceive(observation_t)
 3  targets = perceive_slot_table(...)   →  agent.offer_targets(targets[0])
 4  action = agent.decide()
 5  action, provenance = apply_action_contract(...)   ← la acción se REESCRIBE
 6  scheduler.check(world, step)         ·  lifecycle.advance(world, step)
 7  physics.step(world, {0: action}, RNGManager(world_seed + step))
 8  find_target → rules.evaluate → rules.apply_effects  ⇒ energy_delta
 9  lifecycle.consume(...) si el objetivo desapareció
10  energy_delta += world.apply_step_energy_cost(0)
11  consequence ← physical[0]; observation_t1; terminated; truncated
12  transition = Transition(obs_t, str(agent.get_internal_state()), action, …)
13  if learning_enabled: agent.learn(transition)
```

Tres cosas que sólo se ven leyendo:

* **El paso 5 reescribe lo que el organismo decidió.** Lo intentado y lo
  resuelto viajan separados —`action` y `provenance`—, que es lo que impide que
  «eligió mal» y «eligió bien y el actuador falló» colapsen en el mismo fallo.
* **El RNG de la física es `world_seed + step`**, derivado del mundo y no del
  agente, así que un cambio de agente no mueve los sorteos exógenos. Hoy es
  inerte porque `Physics.step` no lo consume, y el propio docstring dice que
  canonizarlo ahora es gratis y después no lo sería.
* **`str(agent.get_internal_state())`**: el estado interno entra en la
  `Transition` como **cadena**, no como estructura. Queda registrado y no queda
  consultable.

**Hay un segundo lazo.** `lab/causal.py:134` monta su propio
`perceive → decide → learn` para el banco contrafactual. No es un duplicado
accidental —necesita intervenir entre decidir y transicionar— pero es una
segunda ruta que puede divergir de la autoritativa, y ninguna prueba compara las
dos hoy. **K1.**

## 40.2 · A4 por dentro · de la observación al logit

**Percepción** ([a4_advanced.py:354](terrario/agent/agents/a4_advanced.py:354)).
`encoder.encode_observation(observation.channels)` — Conv(C→32→64→64, stride 2)
→ Linear → LayerNorm → `e_t` de 128. Y una línea que importa:

```python
self.homeostasis._energy = observation.agent_energy     # :358
```

La energía entra **escribiendo el atributo privado** del homeostato, no por un
método. Es el snapshot PRE del paso, y no existe el POST equivalente: `learn()`
llama a `homeostasis.update(energy_delta)` 88 líneas después, así que el valor
que la política usó y el que el aprendizaje usa no son el mismo y nadie guarda
el primero.

**El estado** ([:315](terrario/agent/agents/a4_advanced.py:315)):

```
s_t = concat( e_t 128 , h_t 256 , memoria_episódica 128 , memoria_largo_plazo 128 )
    = 640  con DEFAULT_CONFIG
```

**Un módulo ablacionado contribuye ceros, no desaparece.** La forma de `s_t` es
invariante bajo ablación, y por eso una ablación no cambia el número de
parámetros de nada aguas abajo. Es la decisión que hace comparables los brazos.

**La decisión** ([:397](terrario/agent/agents/a4_advanced.py:397)):

```
h_t ← temporal_core(e_t, h_{t-1})            (detached; SSM por defecto)
s_t ← _build_state(e_t, h_t)
logits ← policy_head(s_t)                    Linear(640,256) → ReLU → Linear(256,25)
temperature ← 1 + homeostasis.exploration_bias      :427
logits ← logits + 0.1 · varianza_del_ensemble       :439   ← «curiosidad» en logits
acción ← planner con probabilidad 0.5, si no muestreo de la política   :536
```

## 40.3 · El planner no planifica · es tiro aleatorio a cara o cruz

`Planner.plan` ([policy.py:98](terrario/agent/policy.py:98)) **no busca**:

* muestrea `num_candidates = 10` secuencias **aleatorias** de largo
  `horizon = 5`;
* las despliega por el modelo del mundo;
* puntúa `score = energía_total − 10.0 · Σ P(done)`
  ([policy.py:149](terrario/agent/policy.py:149));
* devuelve la **primera acción** de la mejor secuencia.

Diez muestras aleatorias sobre 25⁵ ≈ 9,8 millones de secuencias posibles. Y
encima **se usa a cara o cruz**: `plan_prob = 0.5`
([:536](terrario/agent/agents/a4_advanced.py:536)), así que la mitad de los
pasos la acción viene de la política. `use_planner=True` no significa
«planifica»: significa «planifica la mitad de las veces, con diez tiros».

Que éste sea, medido, uno de los dos únicos módulos que mueven la conducta
(+6,7 comidas) dice algo sobre el resto, no sobre la potencia del planner.

> **Corregido contra §IX, que ya lo había medido y esta lectura no consultó.**
> Dos cosas que §IX tiene y esta sección no tenía:
>
> 1. **Los dos efectos «significativos» del tamizado son la misma intervención
>    medida dos veces.** La rama exige `use_planner ∧ use_world_model`, así que
>    apagar el modelo del mundo **desactiva el planner**: 40/40 invocaciones con
>    A4 completo, 0/40 con cualquiera de los dos apagados. «Modelo del mundo
>    +6,33» y «planificador +6,67» son la misma ruta.
> 2. **Cuando gana el planner, REINFORCE se actualiza fuera de política y lo
>    trata como si fuera dentro.** `log_prob` es la de la política evaluada
>    sobre la acción del planner, y `learn()` la recalcula sobre `_last_action`
>    —la del planner— sin razón de importancia. El gradiente empuja a la
>    política hacia una acción que la política no eligió.
>
> Y §IX cierra más fuerte que yo: con un modelo del mundo cuya salida es
> constante, el planner **funciona como fuente de exploración, no como
> planificador**. «No planifica» se queda corto.

El despliegue además arrastra un supuesto que nadie ha comprobado: el modelo del
mundo predice `next_state` de **640 dimensiones**, incluidos los contextos de
memoria, que durante el rollout imaginario no se pueden actualizar. **K2: cuánto
se degrada la predicción a lo largo del horizonte 5 no está medido.**

## 40.4 · El aprendizaje · REINFORCE con línea base corrida

En `learn()` ([:577](terrario/agent/agents/a4_advanced.py:577)), por orden:

1. `homeostasis.update(energy_delta)` — el POST.
2. Escritura episódica, si `adaptive_freeze.allow("episodic_buffer")`.
3. Escritura en memoria de largo plazo: `longterm_memory.write(h, h)` — **clave
   y valor son el mismo vector**.
4. Error de predicción, **calculado aunque el aprendizaje esté apagado**: es una
   métrica del observador y no debe depender de si habrá actualización.
5. Pérdida del modelo del mundo contra `next_state_target`, construido con
   `_build_state` bajo `no_grad`.
6. Política: `advantage = r − baseline`, con la línea base corrida
   `baseline += (r − baseline)/n`, y `loss = −log π(a|s) · advantage`.
   `log π` se **recalcula** con grafo fresco para no hacer doble backward.
7. Entropía, apagada por defecto, con coeficiente declarado como contenido
   científico y no como constante.
8. `learner.step(...)` — un solo Adam sobre todos los módulos.

**El aprendizaje se puede apagar en cuatro sitios distintos, y no significan lo
mismo:**

| Interruptor | Qué suprime |
|---|---|
| `learning_enabled` (llamante, [transition.py:386](terrario/world/transition.py:386)) | que `learn()` se llame siquiera |
| `use_online_learning` | todo el bloque de pérdidas |
| `learning_commit_enabled` | **sólo** `optimizer.step()`; el resto del estado adquirido sigue cambiando |
| `full_adaptive_freeze` | las cuatro piezas de la frontera adoptada |

La frontera está declarada en un solo sitio
([adaptive_freeze.py:39](terrario/agent/adaptive_freeze.py:39)):
`A = { θ, EpisodicBuffer, M, energy_baseline }`, cada una con el fichero que la
escribe. Y el mecanismo **bloquea la escritura antes de que ocurra** en vez de
revertirla después, porque `escribir → leer → revertir` no equivale a
`no escribir → leer` aunque terminen con el mismo hash. Además **registra los
intentos**: congelado sin que nadie intentara escribir no es evidencia de nada.

## 40.5 · Homeostasis · un solo punto de contacto, y una salida que nadie consume

`HomeostaticState` no es una red: dos propiedades sobre un escalar.

```
drive             = max(0, threshold − energy)        homeostasis.py:34
exploration_bias  = 1 − energy                        homeostasis.py:42
```

**`exploration_bias` llega a la conducta por un único sitio**: la temperatura de
muestreo ([:427](terrario/agent/agents/a4_advanced.py:427)). **`drive` se
calcula, se registra en la traza y no se consume en ninguna parte.** Es un
output calculado y no consumido, de los que el contrato de conocimiento pide
localizar, y el propio comentario del código lo dice.

Consecuencia que conviene tener escrita: la presión de viabilidad del organismo
no elige **qué** hacer, sólo **cuánto** desordena la elección. Un organismo
hambriento explora más; no busca comida.

> **§XIV lo tenía, y más afilado.** No es sólo que `drive` no se consuma: es que
> `update(energy_delta)` acumula en `_energy` y **`perceive` lo sobrescribe en
> el paso siguiente**. Como el orden es `perceive → decide → learn`, el valor
> acumulado **nunca se lee para decidir**: `update()` sirve únicamente para el
> trace. Estado escrito y no leído.
>
> Y OCF-G1 lo midió: `_energy` tiene **dos escritores** —68 y 68 veces en una
> vida de 68 pasos— y es el **único de 21 estados instrumentados con autoridad
> disputada**. Queda sin reparar a propósito: es O1, no OCF-G3.

## 40.6 · El linaje · qué añade cada organismo

| | Percepción | Estado temporal | Modelo del mundo | Mem. episódica | Mem. largo plazo | Incertidumbre | Planner | Aprende |
|---|---|---|---|---|---|---|---|---|
| **A0** random | — | — | — | — | — | — | — | no |
| **A1** reactivo | encoder | — | — | — | — | — | — | REINFORCE |
| **A2** GRU | encoder | GRU | — | — | — | — | — | REINFORCE |
| **A3** modelo | encoder | GRU | sí | — | — | — | — | REINFORCE + WM |
| **A4** completo | encoder | SSM/GRU | sí | sí | sí | ensemble 5 | sí | REINFORCE + WM + ensemble |
| **A5** cibernético | *hereda A4 entero* | | | | | | | **+ recompensa intrínseca** |

A0–A4 son **clases hermanas** que reimplementan el lazo cada una: A1, A2 y A3 no
heredan de A4 ni entre sí, sólo de `AgentInterface`. A5 sí hereda: es
`class A5Cybernetic(A4Advanced)` y **sobrescribe un solo método**.

**A5 es la intervención causal más limpia del repositorio, y por construcción.**
Toda la superficie causal de la capacidad cabe en
[a5_cybernetic.py:41](terrario/agent/agents/a5_cybernetic.py:41):

```python
extrinsic = super()._policy_reward(consequence)      # = energy_delta
if not self._use_curiosity: return extrinsic          # ⇒ A5 es A4, bit a bit
return extrinsic + self.curiosity.signal(self.last_prediction_error)
```

A4 deja `_policy_reward` inerte a propósito —devuelve exactamente lo que
sustituyó— para que un descendiente no tenga que duplicar 187 líneas y dejar que
la copia derive.

## 40.7 · «Curiosidad» son dos cosas distintas con el mismo nombre

Y conviene no confundirlas nunca más:

| | Dónde entra | Qué es | Ablacionable |
|---|---|---|---|
| **A4** | en los **logits**: `logits + 0.1·varianza` ([:439](terrario/agent/agents/a4_advanced.py:439)) | bono de exploración por incertidumbre del ensemble, coeficiente fijo 0.1, comentado como «curiosity» | sólo con `use_uncertainty` |
| **A5 · CURIO-A1** | en la **recompensa**: `_policy_reward` | error de la propia predicción, con línea base corrida ([curiosity.py:52](terrario/agent/curiosity.py:52)) | `use_curiosity` |

La distinción no es estética: el pasaporte de CURIO-A1 declara que sumar la
señal a los logits haría que `purity_check` la llamara PURE **por construcción**
y el gate pasaría en vacío. A4 ya hace exactamente eso con otra cantidad.

El mecanismo de A5 es `scale · (error − suelo)`, con
`suelo += (error − suelo)·max(decay, 1/n)`: lo que motiva es **predecir peor de
lo habitual**, no predecir mal en general —sin el suelo, un organismo que
predice mal en todas partes recibe la misma señal en todas partes, que es no
tener dirección—. `None` vale cero y no un valor imputado: no saber cuánto se
equivocó no es equivocarse poco.

**Confusor declarado y sin resolver en el propio módulo:** no hay dinámica
inversa (`CLM-0125`), así que un organismo curioso en un mundo con ruido
irreducible puede quedarse mirando la estática. Está dicho, no impedido. **K3.**

## 40.8 · Lo que no se sabe · K1, K2, K3

1. **K1** · El segundo lazo de `lab/causal.py` frente al autoritativo de
   `run_step`: nadie compara sus semánticas. Es la clase exacta de divergencia
   que ya costó tres resultados.
2. **K2** · Degradación del modelo del mundo a lo largo del horizonte 5, con
   contextos de memoria que el rollout no puede actualizar.
3. **K2** · Qué fracción de las acciones proviene del planner y qué fracción de
   la política en una corrida real. Es `plan_prob = 0.5` en el código, pero el
   planner sólo entra si `use_planner ∧ use_world_model`, y no está contado.
4. **K2** · Si `drive` cambiaría algo al consumirse. Hoy es inerte y por tanto
   la hipótesis «regulación homeostática» se apoya en un único canal, la
   temperatura.
5. **K3** · Cómo acotar la curiosidad frente al ruido irreducible sin dinámica
   inversa. El proyecto no tiene evidencia interna para fijarlo.

---

# XLI · Atlas 03 · El sistema experimental

Lectura del 2026-09-21 sobre `1cf9b8f`. Cubre el punto 7 del contrato: mundos,
runners, preregistro, lesiones, controles, métricas, gates, CAS, ledger y
semillas.

**Corrección de procedimiento.** La versión original de este encabezado afirmaba
qué contestaron §III, §IV, §V y §XVIII–§XXII sin haberlas leído. Lo que sí es
verificable: las cuatro estaban **vigentes por hash** el día de esta lectura, y
§XXI vigila **cero ficheros** —no cita ninguna ruta, así que el gate no puede
validarla en absoluto—. Ver §XLII.

## 41.1 · Cuántas rutas pueden avanzar un timestep · y cuáles son la misma física

Hay **un paso compuesto** —`run_step`
([transition.py:316](terrario/world/transition.py:316))— y **cuatro sitios que
llaman a la física en crudo**. No es lo mismo:

| Ruta | Llama | Contrato de acción | Lifecycle | Coste de paso | RNG exógeno |
|---|---|---|---|---|---|
| `ExperimentController` ([:200](terrario/experiment/controller.py:200)) | `run_step` | sí | sí | sí | `world_seed + step` |
| `SandboxService` ([:178](terrario/lab/sandbox_runtime.py:178)) | `run_step` | sí | sí | sí | `world_seed + step` |
| oráculos y 4 guiones de campaña | `run_step` | sí | sí | sí | `world_seed + step` |
| **`CausalRuntime.step`** ([causal.py:129](terrario/lab/causal.py:129)) | `physics.step` | **no** | **no** | sí | **`agent_seed + tick`** |
| **`verify_reproducibility.py`** ([:55](scripts/verify_reproducibility.py:55)) | `physics.step` | **no** | **no** | **no** | propio |

Las dos primeras dicen en un comentario que la secuencia ya no vive en ellas y
que lo que queda es instrumentación —su esquema de traza y sus hashes—, que es
lo único que puede diferir entre superficies. **Eso es cierto y verificable.**
Las dos últimas son otra cosa.

## 41.2 · El contrato de acción · por qué T0 es un control que no cambió

`apply_action_contract` ([:245](terrario/world/transition.py:245)) es, bajo T0,
**un no-op por construcción**: devuelve la acción que el agente emitió, así que
una corrida T0 es byte-idéntica a una anterior a Action Contract v2. Eso
importa: T0 es el brazo de control, y un control que cambiara en silencio haría
la comparación sin sentido.

Bajo T1 sólo una resolución `VALID` escribe `target_id`; cualquier otra cosa lo
deja en `-1` con la dirección ya fijada en `NONE` por el agente, de modo que un
objetivo irresoluble **no consume nada** en vez de convertirse silenciosamente
en el vecino. La procedencia registra intención, resolución y ejecución por
separado.

`find_target` ([:59](terrario/world/transition.py:59)) es la resolución
compartida, y su docstring cuenta su propia historia: fue extraída de dos
implementaciones carácter por carácter equivalentes, y un tercer llamante
alcanzaba el método privado del controlador para no escribir una tercera copia.

## 41.3 · El banco causal diverge, y su declaración de alcance no lo cubre

`CausalRuntime` **no es un duplicado descuidado**: declara su estrechez y la
comprueba. `capability` ([causal.py:120](terrario/lab/causal.py:120)) devuelve
`NOT_FORKABLE` salvo que el agente sea `A0_RANDOM`, el escenario sea
`d0_differences.yaml` y no haya `opportunity_lifecycle`.

Pero la cualificación enumera agente, mundo y lifecycle, y **no mira el modo de
direccionamiento**. Medido en vivo:

```
A0Random(addressing_mode="T1_ENTITY").decide()  →  CONSUME
    target_id = -1 · direction = NONE · selector_value = 3
DIRECTION_DELTA[NONE] = (0, 0)
```

Sin `apply_action_contract`, `find_target` mira **la propia celda del
organismo**, donde no hay objeto. Es decir: **bajo T1, en el banco causal, un
organismo no puede consumir nunca**, y la corrida se clasificaría igualmente
`EXACT_FORKABLE`. No sería una resolución errónea —no aparece un objetivo
fantasma— sino un organismo paralizado que parecería un T1 que rinde mal.

Hoy **nadie construye el banco con T1**: `grep` sobre el árbol no devuelve un
solo sitio. Es un hueco latente, no un resultado contaminado. Cerrarlo cuesta
una línea en `capability`.

Y la segunda divergencia: el banco siembra el RNG **global**
([causal.py:109](terrario/lab/causal.py:109),
`RNGManager.set_global_determinism(agent_seed)`) y deriva sus sorteos exógenos
de `agent_seed + tick`, que es exactamente la semántica que `run_step` canonizó
fuera —«ataría los shocks exógenos futuros a qué agente corre»—. Hoy es inerte
porque `Physics.step` no consume su RNG, y deja de serlo el día que lo consuma.

## 41.4 · El guion que verifica la reproducibilidad no verifica el paso real

`verify_reproducibility.py` no llama a `run_step`: llama a `physics.step`
([:55](scripts/verify_reproducibility.py:55)) y **reimplementa la búsqueda de
objetivo en línea** —una cuarta copia, la que `find_target` documenta que existía
para evitarse—. No aplica el contrato de acción, no tiene lifecycle y **no aplica
el coste de paso**.

Verifica, con rigor, la reproducibilidad de una tubería que ninguna campaña
ejecuta.

## 41.5 · El test de paridad compara la ruta consigo misma

`tests/test_world_runtime_parity.py` está bien construido: agente guionizado
—para que una divergencia no confunda «las físicas difieren» con «los agentes
difieren»—, y el fallo nombra el primer paso y el primer campo que divergen.

Pero `_trayectoria` ([:88](tests/test_world_runtime_parity.py:88)) **ejecuta
`run_step` las dos veces**. Prueba el determinismo de la ruta autoritativa, no
la paridad entre superficies. Su propio encabezado dice que existe porque «un
nivel superado bajo una superficie y reprobado bajo la otra no es un nivel
superado» — y las superficies que podrían diverger son precisamente las que no
compara.

**No existe hoy ninguna prueba que enfrente `run_step` contra
`CausalRuntime.step`.**

## 41.6 · RNG · dos disciplinas opuestas en el mismo repositorio

**`RNGManager`** ([rng.py:33](terrario/core/rng.py:33)) deriva sus sub-semillas
llamando `randint` tres veces seguidas sobre el maestro:

```python
self.world_seed    = self._python_rng.randint(0, 2**31 - 1)
self.agent_seed    = self._python_rng.randint(0, 2**31 - 1)
self.observer_seed = self._python_rng.randint(0, 2**31 - 1)
```

Son **dependientes del orden de llamada**: insertar un cuarto subsistema entre
el mundo y el agente cambiaría retroactivamente todas las semillas de agente.

**`OpportunityLifecycle._stream`**
([opportunities.py:42](terrario/world/opportunities.py:42)) hace lo contrario, y
su docstring dice por qué: `blake2b(f"{seed}:{kind}:{key}:{generation}")`, «una
clave sobre la identidad, nunca sobre cuántas llamadas vinieron antes», de modo
que la variante de la oportunidad 7 es la misma independientemente del historial.

El ciclo de oportunidades ya resolvió el problema que el gestor de RNG todavía
tiene. **K1: nadie ha comprobado si alguna semilla publicada depende de ese
orden.**

## 41.7 · Las cuatro lecturas que no pueden fundirse · y esta vez se adoptaron

`measurement_status.py` es una defensa **estructural**, no una advertencia:

```
0.0            hubo soporte, se calculó, dio cero
NOT_EVALUABLE  no existe soporte — el denominador está vacío
MISSING        falta un campo que el cálculo necesita
INVALID        el dato está y viola el contrato que dice cumplir
```

`float(reading)` **levanta** salvo que sea OK; `reading.value` es `None` salvo
que sea OK; y no hay método que convierta una lectura no-OK en número
([:41](terrario/lab/measurement_status.py:41)). `ratio()`
([:83](terrario/lab/measurement_status.py:83)) devuelve `NOT_EVALUABLE` con
denominador vacío en vez de dividir, «porque esa única línea es donde nace casi
todo cero falso».

**Y está adoptado**, que es lo que lo distingue del resto de la capa: nueve
consumidores, entre ellos `evidence_admission`, `capability_exam`,
`metric_result_sealing` y los cuatro guiones de experimento.

## 41.8 · La última puerta · admisión de evidencia

`evidence_admission` ([:40](terrario/lab/evidence_admission.py:40)) es el único
sitio donde se pregunta si un número puede convertirse en evidencia, y lo
pregunta **otra vez** aunque el preregistro y el runtime ya lo hicieran: «una
puerta que confía en quien la llama es documentación, no una puerta».

Sus cuatro no-acciones están escritas como lo que son —cada una fue una vía por
la que entró un hallazgo falso—:

```
no recalcula una métrica      no modifica una Reading
no imputa la ausencia         no reinterpreta INVALID
```

Sólo los roles `PRIMARY` exigen instrumento canónico: una lectura diagnóstica
puede ser tosca, lo que no puede es ser un hallazgo.

## 41.9 · Preregistro · siete estados y una contabilidad de exposición

`ALLOWED_TRANSITIONS` ([domain.py:640](terrario/lab/preregistration/domain.py:640))
es una máquina estricta:

```
DRAFT → READY_FOR_REVIEW → REVIEW_IN_PROGRESS → REVIEWED
REVIEWED → DRAFT | PREREGISTERED_LOCKED
PREREGISTERED_LOCKED → SUPERSEDED | WITHDRAWN        (ambos terminales)
```

`SeedCommitment` ([:246](terrario/lab/preregistration/domain.py:246)) sella
cuatro familias de semillas —mundo, agente, aleatorización, reemplazo— **cada
una con su hash**, y `SeedPartition` las reparte en seis particiones, entre
ellas `CONFIRMATORY_TEST` y `HOLDOUT`, con `exception_reason` cuando se sale de
la norma.

`ExposureStatus` ([:91](terrario/lab/preregistration/domain.py:91)) lleva la
contabilidad de contaminación: `UNEXPOSED`, `PREEXPOSED`, `POSTLOCK_EXPOSED`,
`CONTAMINATION_REVIEW_REQUIRED`. **Y está vivo**: 45 filas en
`exposure_records`, junto a 141 preregistros sellados, 708 entradas de cadena de
auditoría y 1 664 eventos de ejecución científica.

Ésta es la parte del laboratorio que **sí se usa**, y la diferencia con la capa
de conocimiento —42 de 72 tablas vacías— es la distinción más útil que da este
volumen: lo que toca el ciclo experimental tiene filas; lo que no, no.

## 41.10 · «Replay» no es re-ejecución

`OfflineReplay` ([replay.py:11](terrario/lab/replay.py:11)) es **un cursor sobre
una línea de tiempo grabada** —`forward`, `backward`, `reset`, `jump`—. No
vuelve a simular nada.

El contrato de conocimiento lista «replay» entre las rutas de ejecución. No lo
es. La única pieza que re-ejecuta para comparar es
`verify_reproducibility.py`, y §41.4 dice qué ejecuta realmente.

## 41.11 · Lo que no se sabe

1. **K1** · Si alguna semilla ya publicada depende del orden de llamada de
   `RNGManager`. Comprobable reconstruyendo las sub-semillas de una campaña.
2. **K2** · Si `run_step` y `CausalRuntime.step` producen la misma trayectoria
   bajo T0 con el mismo guion. Es un test de veinte líneas y hoy no existe.
3. **K2** · Qué mide de menos `verify_reproducibility.py` frente al paso real:
   sin coste de paso, el criterio de terminación difiere.
4. **K2** · Cuántas de las 141 ejecuciones selladas corrieron por la ruta
   `SandboxService` y cuántas por `ExperimentController`. La distinción importa
   porque §XXI ya documentó que la semántica efectiva del sandbox no ejecuta
   `OpportunityLifecycle`.

---

# XLII · Reconciliación · el mapa como caché, y lo que costó no consultarla

Escrita el 2026-09-21 a raíz de una pregunta que era, en efecto, de pura lógica:
si la cartografía existe, ¿por qué un volumen nuevo vuelve a mapear lo que ya
está mapeado?

**La respuesta honesta: el Atlas 01 sí la usó; el 02 y el 03 no.**

## 42.1 · Lo que se pagó dos veces

Las secciones que solapan con el Atlas 02 —§VI a §XIV y §XXVI— estaban **todas
vigentes por hash** el día de la lectura. No estaban obsoletas: estaban en
caché, utilizables, y no se consultaron.

El coste no fue sólo repetir trabajo. Fue **quedarse corto**:

| Ya estaba en el mapa | Qué añadía sobre lo que el Atlas 02 escribió |
|---|---|
| §IX · Planner | `use_world_model=False` **desactiva el planner** (40/40 → 0/40 invocaciones). Los dos efectos «significativos» del tamizado son la misma intervención medida dos veces. |
| §IX · Planner | Cuando gana el planner, REINFORCE usa `log π(a_planner)`: **actualización fuera de política tratada como dentro**. |
| §IX · Planner | Con un modelo del mundo de salida constante, el planner es **fuente de exploración**, no planificador. Más fuerte que «no planifica». |
| §XIV · Homeostasis | `update()` acumula y `perceive` **sobrescribe**: el valor acumulado nunca se lee para decidir. No es que `drive` no se consuma — es que la acumulación entera es sólo traza. |
| §XIV · Homeostasis | OCF-G1: `_energy` es el **único de 21 estados instrumentados con autoridad disputada**, con dos escritores a 68 y 68 en una vida de 68 pasos. |

Las cinco están ahora importadas en §XL, marcadas como corrección, en vez de
quedar como un segundo relato paralelo — que es exactamente el defecto que §XXXIX
reportó del inventario de gates y que esta serie estuvo a punto de repetir a
nivel de documento.

## 42.2 · El defecto del gate que esto destapó

**El hash vigila el fichero; no vigila la cita.**

§XIV citaba `a4_advanced.py:347` y `:352` para una asignación que hoy está en la
**358** —las líneas 347 y 352 son un `device = …` y un separador de comentario—,
y el manifiesto registraba **el mismo hash** que el fichero tiene ahora. Es
decir: la sección estaba **verde** apuntando a otra cosa.

Cómo pasa: `--write` se ejecutó después de que el fichero cambiara, sin
reescribir la prosa. El hash prueba que el fichero es el mismo que cuando se
**registró**, no que cuando se **escribió el texto**.

**Reparado.** `cartografia_check.py` ahora verifica cada `fichero:línea` del
documento: fichero inexistente, línea fuera de rango o línea en blanco. Encontró
**cuatro citas podridas** en su primera pasada, en §IX, §XIX y §XXXI —todas
símbolos que se desplazaron hacia abajo—, más las dos de §XIV halladas leyendo.
Las seis están corregidas.

Lo que el comprobador **no** puede decidir, y queda dicho: que la línea diga lo
que la prosa afirma. Una cita a una línea que existe y no está en blanco pero
apunta al símbolo equivocado sigue pasando. Eso sólo lo caza leer.

Y un hueco que la pasada destapó: **§XXI vigila cero ficheros**. No cita ninguna
ruta, así que el gate no puede invalidarla nunca: está permanentemente al día
por construcción. **K2: cuántas secciones más están en esa situación.**

## 42.3 · La regla, para que no vuelva a pasar

> Antes de abrir un volumen: correr el gate sobre las secciones que solapan,
> **leerlas**, y leer código sólo donde el mapa calle o esté obsoleto.

La cartografía es una caché invalidable. No consultarla no es una pérdida de
tiempo simétrica: se paga en trabajo repetido **y** en hallazgos que ya estaban
y no se recogen. El Atlas 02 habría sido mejor volumen en menos tiempo.
