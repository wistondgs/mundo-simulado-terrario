# Cartografía de Terrario

HEAD `427f8428` · 2026-09-17 · 179 ficheros, 29 050 líneas en `terrario/`

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

world/       (7)        física. → core
  state.py            WorldStateManager · AUTORIDAD del estado
  physics.py          PhysicsEngine · MOVE/PUSH/CONSUME/INSPECT/NOOP
  rules.py            RuleEngine · evalúa y aplica efectos
  scheduler.py        ChangeScheduler · inversiones programadas
  opportunities.py    OpportunityLifecycle · despawn/cooldown/respawn
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

lab/         (130)      laboratorio. → core, world, experiment, agent, observer
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

`lab` (130 de 179 ficheros — el 73 % del repositorio) y `experiment`.

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

- **`_find_target`**: `controller.py:317` (método) y `sandbox_runtime.py:294` (función módulo).
  Los diferencié: **semánticamente idénticos**, escritos distinto. Duplicación sin drift actual,
  con riesgo de drift permanente.
- La construcción del `Transition` y el cálculo de `energy_delta`.
- La secuencia perceive → decide → physics → rules → cost.

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

**No.** `WorldDefinition` es una representación **descriptiva y hasheable** para el laboratorio;
el runtime nunca la consume. Ambos loops interpretan el dict del escenario **por separado**. Ésa
es la raíz estructural de toda la sección §XXI.

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

## 125-127 · Qué estado cambia y cuándo

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

## 181-184 · Dónde se usa la salida

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

**Random shooting**, [policy.py:85](terrario/agent/policy.py:85):

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

## 232-243 · Asignación de crédito y maquinaria

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

## 256-263 · Memoria de largo plazo

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

[317] **Sólo una es independiente: `_energy`.** [318] `drive` y `exploration_bias` son **alias
funcionales** de la misma variable; ninguna aporta información que la otra no tenga.

## 322-325 · Qué ve A4 de su propia energía

`perceive` hace **asignación directa**: `self.homeostasis._energy = observation.agent_energy`
([a4_advanced.py:347](terrario/agent/agents/a4_advanced.py:347)).

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

## 339-348 · D4T en concreto

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
