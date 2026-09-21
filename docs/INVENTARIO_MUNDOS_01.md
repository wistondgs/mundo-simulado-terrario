# Inventario de mecanismos de mundo · qué existe ya para E0–E9

**2026-09-18 · READ-ONLY.** No implementa, no propone mundos, no modifica nada.

## 1 · Snapshot

```
repo      /home/wis/mundo simulado terrario
branch    experiment/cognitive-live-observatory-01
HEAD      f72d2258c84814aa5304bb350a45096e19ecfd41
status    1 fichero sin seguimiento (este documento). Cero modificaciones.
worktrees  principal · sweet-dirac-968e1e (agent_composition) · ocf-g3-close
```

## 2 · Inventario maestro de productores

| ID | Mecanismo | Fichero / símbolo | Tipo | Consumidor | Runtime | Estado |
|---|---|---|---|---|---|---|
| P1 | **Generador cue→demora→elección** | `lab/world_generator.py` · `generate`, `world_for`, `control_for` | generador paramétrico | oráculos, boundary, scripts | física autoritativa vía `build_episode_components` | **activo**, reparado hoy |
| P2 | **Taller de mundos** | `lab/world_authoring.py` · `WorldDraft`, `validate_draft`, `compile_draft`, `generate_instance`, `SeedBrowser`, `preview` | borrador → compilado → instancia | `lab/api.py`, registro | produce `WorldDefinition` + `runtime_template` | **activo** |
| P3 | **Registro de escenarios** | `lab/world_registry.py` · `WorldScenarioRegistry`, `adapt_legacy_scenario`, `scenario_from_runtime`, `definition_from_runtime` | adaptador legado→contrato | taller, api | — | **activo** |
| P4 | **Escenarios YAML** | `scenarios/*.yaml` (12) | escritos a mano | `controller.load_scenario` | `ExperimentController` | **activos** |
| P5 | **Materializador** | `experiment/controller.py` · `load_scenario`, `materialize_scenario` | plantilla → instancia por semilla | controlador, taller | autoritativo | **activo** |
| P6 | **Ensamblador de episodio** | `world/transition.py` · `build_episode_components`, `build_world_state` | escenario → `EpisodeComponents` | todas las rutas | **es** el runtime | **activo** |
| P7 | **Frontera de mundo generado** | `lab/generated_world_boundary.py` | generado → `WorldDefinition`/`WorldInstance` | pasaportes | — | **activo** |
| P8 | **Compositor de experimentos** | `lab/experiment_composer.py` · `ExperimentDraft`, `TrialMatrix`, `TreatmentArm`, `SeedPair`, `InitialStateFingerprint` | matriz de ensayos, **no ejecuta** | api | — | **activo, acotado** |
| P9 | **Ciclo de oportunidad** | `world/opportunities.py` · `OpportunityLifecycle` | respawn/cooldown/linaje de objetos | `build_episode_components(with_lifecycle=True)` | autoritativo | **activo** |
| P10 | **Calendario de cambios** | `world/scheduler.py` · `ChangeScheduler` | intercambio de reglas en `at_step` | todas las rutas | autoritativo | **activo** |
| P11 | **Examen de capacidad** | `lab/capability_exam.py` · `sit_exam`, `Probe` | observaciones sintéticas, sin mundo | pasaportes | — | **activo** |
| P12 | **Oráculos amputables** | `lab/world_oracles.py` · `Oracle`, `run_life`, `verdict_for` | organismo guionizado | falsación de mundos | autoritativo | **activo**, atado a P1 |
| P13 | **Fixture visual D2** | `lab/d2_visual_fixture.py` | fixture de test | tests | — | test-only |
| P14 | **Caracterización** | `lab/characterization.py` · `characterize_matrix` | matriz D×A congelada | baseline tests | autoritativo | **activo** |

**Rutas de ejecución reales** (quien llama a `run_step`/`run_episode`): `experiment/controller.py`
(`ExperimentController`), `experiment/adaptation.py`, `lab/execution/runtime.py`,
`lab/sandbox_runtime.py`, `lab/world_oracles.py`, y cuatro scripts de auditoría. **Todas** pasan por
`build_episode_components` o por el controlador, así que todas usan la física autoritativa.

## 3 · Matriz de capacidades

| | P1 generador | P2 taller | P4 YAML | P6 ensamblador |
|---|---|---|---|---|
| **geometría** ancho/alto | derivada de la exigencia | **editable** (`dimensions`, 1..MAX) | literal | pasa-through |
| paredes / obstáculos | filas fijas | entidades en cualquier `pos` | sí | — |
| posición inicial | fija `(1,0)` | `initial_conditions` | `agent_start.pos` | — |
| **percepción** radio | fijo 2 | `observation_sources` declarado; radio en plantilla | `view_radius` | usa el del escenario |
| canales | fijo 4 | ≤64 por entidad | `num_channels` | — |
| info oculta | **sí** (canal 3 truncado) | sí, mismo mecanismo | sí | — |
| **física** inyectable | no la expone | no la expone | no | **`EpisodeComponents.physics`** |
| acciones disponibles | todas | **`action_availability`** ⊆ {MOVE,PUSH,CONSUME,INSPECT,NOOP} | todas | — |
| remapeo acción→efecto | **no existe** | no | no | vía subclase de `Physics` |
| **recursos** tipos/efectos | canal 3 + reglas | `entities`, `object_distributions` | `objects` | — |
| favorable/perjudicial | `gain`/`loss`/`safe` | `deterministic_rules` | `rules` | — |
| respawn/cooldown/linaje | no lo usa | `resource_structure` | `opportunity_lifecycle` | **P9** |
| **energía** inicial/máx/coste | `Economy` | `initial_conditions` | `agent_start.energy`, `max_energy`, `step_energy_cost` | exige las 4 en `strict_physics` |
| setpoint | `low_energy` (puntuación) | — | — | `homeostasis_threshold` es del **agente** |
| **temporal** demoras/secuencias | ejes `delay`/`sequence` | `scheduled_events` | — | — |
| cambio de regla a mitad | eje `inversion` | `scheduled_events` | `changes: [{at_step, rules}]` | **P10** |
| **semilla** qué varía | contenido de estación, por propósito | `SeedBrowser.inspect(seed)` | `materialize_scenario(seed)` | — |
| **recompensa** externa | `energy_delta` por regla | `deterministic_rules` | `rules` | — |
| diferida / contextual | no | condición multicanal | condición multicanal | — |

**Sobre qué puede condicionar una regla:** `object_channels[]` (varios) **+ acción**, y nada más
([rules.py:115](terrario/world/rules.py:115)). No hay condición sobre posición, tiempo, historia ni
estado del agente. Pero **multicanal significa que «contexto × ítem» ya es expresable**: un canal
lleva el tipo, otro el contexto, y la regla exige los dos.

## 4 · Mapa E0–E9

| Exp | Infraestructura existente | Clasificación | Evidencia | Hueco |
|---|---|---|---|---|
| **E0 motor** | P6 + subclase de `Physics` | **EXISTS_WITH_SMALL_ADAPTER** | `EpisodeComponents.physics` es un campo; `Physics._handle_move` es sobreescribible | el adaptador de permutación. **Y el 7×7/r2 no vale: medido 25 vistas / 49 celdas. Sirven 5×5/r2 y 7×7/r3** |
| **E1 hambre** | `agent_energy` ya es fuente de observación declarada (`AGENT_FIELDS`); `homeostasis.drive` ya calcula `d_t`; `_policy_reward` inerte | **MISSING_PRIMITIVE** | `perceive` codifica sólo `observation.channels`; `s_t = concat(e_t,h_t,mem,lt)` sin término interoceptivo; la energía llega sólo a la temperatura del softmax | **la energía no alcanza la política**. No se obtiene por configuración ni composición |
| **E2 búsqueda** | P4 (`d4_*` con recurso no adyacente), P2 para colocarlo | **EXISTS_WITH_CONFIG** | `d4_adaptation_*` tienen 1 objeto en 14×14 | — |
| **E3 valencia** | P1 entero: objetos distinguibles, consecuencia por canal, mapeo por semilla | **EXISTS_AS_IS** | el eje `hidden` es literalmente esto | — |
| **E4 memoria** | P1: cue → demora → elección, con control por eje | **EXISTS_AS_IS** | `EPMEM-A1`, `delay=5`; oráculo completo 1.0, amputado 0.521 | — |
| **E5 curiosidad** | P1 eje `novelty` (consecuencia irreducible); `last_prediction_error` | **EXISTS_WITH_COMPOSITION** | `UNC-A1` tiene mundo; `novelty` ya exige referente irreducible | el endpoint de **ganancia de información** y su caída tras aprender |
| **E6 descubrimiento** | condición multicanal + P10 para el cambio de contexto | **EXISTS_WITH_CONFIG** | `object_channels: []` admite varias condiciones | — |
| **E7 transferencia** | `adaptation.py` con fase de transferencia y `learning_enabled=False`; `d4_adaptation_transfer` | **EXISTS_AS_IS** | `transfer_adaptive_state_unchanged`, reparado hoy | — |
| **E8 metacognición** | mundo: P10 (`changes`) da el reversal. Mecanismo: `last_prediction_error` | **EXISTS_WITH_CONFIG** (mundo) · **MISSING_PRIMITIVE** (mecanismo) | el error se calcula y va sólo al observador | el lazo error → meta-estado → cambio de política |
| **E9 ultraestabilidad** | `viability_recovery_metric` declara que **no** lo mide | **MISSING_PRIMITIVE** | cero apariciones de perturbación en el generador; nadie reorganiza parámetros | operador de perturbación + reorganización |

## 5 · EXISTING_CAPABILITIES_WE_WOULD_REINVENT_IF_WE_DID_NOT_AUDIT

1. **`WorldDraft.edit(reason, **changes)`** — edición paramétrica **con procedencia**. Cambiar
   tamaño o radio ya es esto, no un generador nuevo. Límite: no expone la física.
2. **`SeedBrowser.inspect(seed)` + `preview` + `degeneracy_flags`** — inspección de semillas y
   detección de mundos degenerados **antes** de correrlos. Los mundos held-out de E7 salen de aquí.
3. **`OpportunityLifecycle`** — respawn, cooldown, `lineage_root`/`generation` por objeto. E2, E3 y
   E5 necesitan reaparición de recursos y ya está resuelta.
4. **`ChangeScheduler` con `changes: [{at_step, rules}]`** — el context switch y el reversal de E6 y
   E8. No hace falta inventar fases.
5. **Condición multicanal en `RuleEngine`** — «contexto × ítem» de E6, ya expresable.
6. **`sit_exam` + `Probe`** — examen con observaciones sintéticas, sin mundo. El endpoint de
   predicción de E0 puede medirse aquí sin correr episodios.
7. **El oráculo ya usa interocepción** — `world_oracles.py:106` lee `observation.agent_energy`.
   Demuestra que la señal **basta** para conducta dependiente del estado; el hueco de E1 es de A4,
   no del mundo ni de la observación.
8. **Los tres brazos N/LEGACY/FULL** — el control causal de la escalera entera, certificado hoy.
9. **`force_action` + `replay`** — stream grabado idéntico para varios gemelos.
10. **`characterize_matrix`** — matriz escenario × agente ya congelada, útil como línea base.

## 6 · MISSING_PRIMITIVES

Sólo lo que no existe, no se obtiene por configuración, no se obtiene por composición y no se
reutiliza de otra ruta.

| Hueco | Bloquea | Evidencia negativa | Superficie que falta |
|---|---|---|---|
| **La energía no llega a la política** | E1, y media capacidad de B2 | `perceive` codifica sólo `channels`; `_build_state` no tiene término interoceptivo; búsqueda de `self_state`/`interocep`/`propriocep` en `terrario/`: **cero** | una vía `x_body → sensor → x̂_internal` hacia `s_t`. Decisión de arquitectura del ser |
| **Remapeo acción→efecto** | E0 en su forma falsable | `DIRECTION_DELTA` es constante de módulo; ningún productor lo expone | una subclase de `Physics` — **pequeña**, el campo `physics` ya existe |
| **Operador de perturbación** | E9, y el protocolo de HEA-009 | cero apariciones en el generador; `ChangeScheduler` sólo intercambia reglas | perturbación de la variable esencial, no de la regla |
| **Reorganización de parámetros** | E9 | `viability_recovery_metric` declara explícitamente que no lo mide | el segundo lazo |
| **Endpoint de ganancia de información** | E5 en su forma no trivial | ningún instrumento de los 8 lo mide | distinguir curiosidad de búsqueda de novedad |
| **Brazos distintos de planner** en el compositor | usar P8 para E0–E9 | `TreatmentArm` acepta **sólo** `PLANNER_PRESERVED`/`PLANNER_ABLATED`; `InitialStateFingerprint` sólo valida esas dos configs | vocabulario de brazos. **La ruta cruda no lo necesita** |

## 7 · Preguntas que el código no permite contestar

- **¿Cuánto del 5×5 sirve para E0 con obstáculos?** La medida de 25/25 vistas es para un mundo
  **vacío**. Con entidades la distinguibilidad sube, pero no la he medido.
- **¿`sit_exam` admite probes con energía variable?** Construye `Observation(..., agent_energy=0.5)`
  fijo en la línea 129; si es parametrizable no lo he verificado.
- **¿Las 12 YAML son todas alcanzables hoy?** `characterize_matrix` usa un subconjunto (D2, D3, D4,
  A0, A1, A4). De las otras no sé si algún runner las carga.
- **¿`lab/execution/runtime.py` y `sandbox_runtime.py` aplican la misma física que el controlador?**
  Las tres llaman a `build_episode_components`, pero no he comparado sus parámetros.
