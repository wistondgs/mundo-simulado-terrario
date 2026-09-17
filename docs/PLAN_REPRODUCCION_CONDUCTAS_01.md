# PLAN-REPRODUCCION-CONDUCTAS-01

**Estatus:** plan propuesto. No normativo, subordinado a `PROCESO_DE_TRABAJO_01`.
**Fecha:** 2026-09-16 (noche).
**Encargo:** «vamos a reproducir todos esos comportamientos en Terrario» — no todos a la vez.
**Alcance:** ordenar la reproducción de las conductas del mapa conceptual ampliado, con el coste
de cada una medido en este código, no estimado.

---

## 0. La bifurcación que decide todo

El propio mapa la fija en §63:

```
Nombre ≠ implementación ≠ uso funcional ≠ evidencia de capacidad
```

«Reproducir» significa dos cosas distintas según el bloque:

**Reproducir como mecanismo** — dar ranura en el organismo. Aplica a percepción, memoria, modelo
del mundo, planificación, incertidumbre, aprendizaje, homeostasis: cosas que **se instalan**.

**Reproducir como fenómeno** — provocar que ocurra y poder detectarlo. Aplica a recuperación,
reorganización, dependencia de historia, transferencia, novedad funcional, desarrollo: cosas que
**no se instalan**. Un módulo llamado `Reorganizer` cumpliría la primera flecha de §63 y ninguna
de las otras tres.

Los 64 bloques no son 64 módulos. **La mitad del trabajo está en el mundo y en el detector, no en
el agente**, y ése es el orden que este plan sigue.

---

## 1. Coste real, verificado en el código

### Nivel 0 · ya hecho
`use_homeostasis` (commit `551b219`). Variedad reguladora ablacionable.

### Nivel 1 · escenario nuevo, ningún mecanismo
Lo que el motor ya soporta y **ningún escenario usa**:

- `ChangeScheduler.check` (`world/scheduler.py:49-88`) itera toda la lista de `changes` y dispara
  cada entrada vencida. **Multi-perturbación está soportado.** Ningún escenario declara más de
  una: `d4_change`, `d4_change_fast` y `d4_adaptation_scientific` tienen exactamente un `at_step`.
- Las reglas admiten condición sobre `object_channel` y efecto con signo, magnitud y
  `destroy_object`. Variarlos produce **tipos** distintos de perturbación, no sólo momentos.
- `procedural_layout`, `opportunity_lifecycle` y `grid_size` dan variedad ambiental.

Coste: el diccionario de escenarios está **hardcodeado** en `world_registry.py:35`, así que un id
nuevo toca ese archivo y los guards de identidad — precedente conocido, es lo que pasó al
registrar D4S. **No toca el manifiesto protegido**: ni `world_registry.py` ni los YAML están entre
los 70 archivos de SYSTEM-BASELINE-02.

Regla dura: **id nuevo, nunca editar un YAML existente.** Editar `d4_adaptation_scientific.yaml`
cambiaría su `content_hash` y con él el `config_hash` de todo diseño que ya lo referencie.

### Nivel 2 · bandera sobre módulo existente
Como la de hoy. Variedad conductual —restringir el conjunto de acciones por escenario, hoy fijo
en `MOVE · PUSH · CONSUME · INSPECT · NOOP`— y las siete `use_*` que ya existen en A4.

### Nivel 3 · módulo nuevo en el agente
- **Variedad estratégica**: `Π` no existe. El canal `decision` da la acción elegida, no la
  política. Representar políticas múltiples es trabajo real.
- **Metacognición con control**: `UncertaintyEstimator` produce monitorización; falta el lazo que
  la use para cambiar de estrategia. Es exactamente el hueco que `CORPUS_ACQUISITION_LIST_02`
  señala con Nelson & Narens.

### Nivel 4 · runtime, no módulo
**Variedad social.** La estructura de estado admite varios agentes (`agents` es un diccionario, y
la métrica de viabilidad ya hace `min` entre ellos), pero el runtime es monoagente por cableado:
`scenario.py:69`, `opportunities.py:57`, `controller.py:217, 238, 241, 310`. Y `scenario.py`
**sí** está en el conjunto protegido, así que esto vuelve a mover el baseline.

---

## 2. El orden propuesto

### Etapa 0 · no adelantar la cola
CL-7 sigue siendo el único ciclo cerrable, y `scientific_results = 0` en el ledger. **Este plan no
adelanta esa cola.** Todo lo que sigue está pensado para no consumir las mismas firmas: las
etapas 1 y 2 no requieren preregistro nuevo porque no producen afirmaciones publicables por sí
solas.

### Etapa 1 · variedad temporal de la perturbación — `D4T`
**Qué:** un escenario con varias entradas en `changes:` — secuencia, ritmo, recurrencia y
acumulación en vez de un único golpe.

**Por qué primero:** es la única de las doce variedades que no necesita mecanismo nuevo. El motor
ya la soporta y nadie la ha usado. Y hace significativa por primera vez una dimensión que ya
existe y está clavada en 1: `DifficultyProfile.rule_volatility = len(scenario.interventions)`
(`world_registry.py`).

**Qué desbloquea:** el instrumento de viabilidad mide **una** excursión. Con varias
perturbaciones se puede preguntar si la segunda recuperación es más rápida que la primera — que
es dependencia de historia medida sobre el detector que ya existe, sin canal nuevo.

**Qué NO permitiría afirmar:** nada sobre reorganización endógena. Una recuperación más rápida es
compatible con aprendizaje por refuerzo energético ordinario, porque `energy_delta` sigue siendo a
la vez variable esencial y recompensa.

**Coste:** un YAML, una entrada en el diccionario del registro, guards de identidad, suite
completa. No toca el baseline protegido.

### Etapa 2 · tipos de perturbación — `D4V`
**Qué:** perturbaciones que difieren en clase, no sólo en momento: inversión de regla, cambio de
magnitud, cambio de qué canal es relevante, retirada de oportunidades.

**Por qué segunda:** separa «el organismo se recupera de *la* perturbación» de «se recupera de
*perturbaciones*». Es el paso mínimo hacia variedad requerida en el sentido de Ashby: variedad
reguladora frente a variedad de `D`, no frente a un único `D`.

**Coste:** igual que la etapa 1.

### Etapa 3 · repertorio conductual declarable
**Qué:** que el escenario pueda restringir el conjunto de acciones disponibles.

**Por qué:** es la primera manipulación de variedad reguladora **del lado del organismo** que no
exige módulo nuevo. Permite el contraste que hoy no existe: misma perturbación, repertorio
amplio frente a repertorio estrecho.

**Coste:** bandera, del tamaño de la de hoy. `ActionContract` ya existe y ya declara acciones por
escenario; falta que el runtime la respete como restricción.

### Etapa 4 · el confundido — separar `E` del refuerzo
**Qué:** una segunda variable esencial que no se use como recompensa, **o** un disparador de
plasticidad anclado en la frontera de viabilidad.

**Por qué aquí y no antes:** es la primera etapa que sí es mecanismo nuevo, y es la que **todas
las afirmaciones interesantes necesitan**. Mientras `agent.energy` y `consequence.energy_delta`
sean la misma magnitud, ningún experimento puede distinguir «la viabilidad gobierna la
reorganización» de «la recompensa gobierna la política».

**Requisito previo:** la moratoria de `PROCESO_DE_TRABAJO_01` §4 exige `scientific_results > 0`.
Hoy es 0. **Esta etapa está bloqueada por proceso, no por dificultad.**

### Etapa 5 · metacognición con lazo de control
Monitorización ya existe. Falta que la incertidumbre estimada cambie la estrategia. Módulo nuevo,
pilar 2 del corpus todavía en cero fuentes.

### Etapa 6 · repertorio estratégico `Π`
Representar políticas múltiples, su coexistencia, selección y sustitución. Es el prerrequisito de
los bloques 30, 33 y 43, y de `dV_R/dt` como magnitud medible.

### Etapa 7 · variedad social
Multiagente. Toca el conjunto protegido y seis puntos de cableado monoagente. Es el escalón más
caro del plan y el que menos aporta al gate 1.

---

## 3. Lo que este plan deliberadamente no hace

- **No instala fenómenos.** Recuperación, reorganización, novedad y desarrollo no aparecen como
  etapas de construcción, porque no son módulos. Aparecen como lo que las etapas 1–4 permiten
  *detectar*.
- **No toca `𝒱ₜ` variable.** Mientras no haya registro justificado de cada cambio de límites, una
  región viable móvil es un grado de libertad del experimentador (ADR-002, riesgo declarado).
- **No añade canal de observación.** Las etapas 1–3 se miden con los nueve canales existentes.
- **No adelanta CL-7.**

---

## 4. Regla de avance

Una etapa a la vez, y cada una cierra antes de abrir la siguiente — que es la regla 1 de
`PROCESO_DE_TRABAJO_01` §4 aplicada a este plan. El criterio de cierre de las etapas 1–3 es
modesto y explícito: **el escenario corre, el detector lo evalúa, y queda escrito qué se puede y
qué no se puede afirmar con él.** No requiere firma de preregistro porque no produce evidencia
publicable; sí requiere que nadie presente su salida como tal.

De la etapa 4 en adelante, cada etapa es mecanismo y entra bajo moratoria.
