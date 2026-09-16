# RNFE-GENESIS-INSPECTION-01

**Encargo:** inspección detallada de Genesis y opinión sobre el proyecto, detenido a la espera
de reingeniería.
**Método:** el código, no la documentación — por instrucción explícita del investigador, que
coincide con el mandato del propio `docs/analysis/00_INDEX.md`: *«Fuente de verdad: el CÓDIGO»*.
**Solo lectura.** Repo: `/home/wis/Desarrollo/RNE_v16-genesis-v2`, rama `genesis/v2-foundation`,
último commit `433beca` (2026-09-07).

---

## 1. Primero: el código está bastante mejor de lo que dice su propia auditoría

`docs/analysis/` es un trabajo excelente —17 documentos, línea por línea— pero su índice es del
**2026-07-04** y la síntesis del **07-10**. El repo siguió hasta el **09-07**. Está desfasada
justo en los dos meses de la línea Genesis.

Verifiqué en código su lista de bugs. **La mayoría ya están resueltos y nadie lo anotó:**

| Hallazgo de julio | Estado real hoy (verificado en código) |
|---|---|
| Shims legacy en la raíz (`cognition/ core/ episteme/ src/`…) | **eliminados** — ninguno existe |
| `trainer_fenix`, `fenix_agent` rotos | **eliminados** |
| `fase0_cert` invoca `run_aeon.py` inexistente | **eliminado** del código vivo (solo en `archive/`) |
| `trajectory_window` con `if False` | **eliminado** |
| ≥3 definiciones de `HealthStatus` | **1** — con `tests/regression/test_healthstatus_unification.py` |
| 2 × `CombinedModel` | **1** |
| DB de ~890 MB versionada | **fuera** |
| `.detach().requires_grad_(True)` rompiendo backprop | sigue, pero **dentro de `runtime/legacy/`** ⇒ inerte |

Además apareció una **cuarentena interna nueva**: `runtime/legacy/` (1.904 líneas), importada
sólo por el CLI histórico `aeon_main_loop.py` y un test de regresión. Aislamiento correcto.

Quedan abiertos, menores: `EpistemeMeter` ×2 y `EventBus` ×2.

**Conclusión de salud:** 1.933 tests **colectan limpios en 1,2 s, cero errores de importación**.
No es un proyecto podrido. Si vas a reestructurar partiendo de la foto de julio, vas a reparar
cosas que ya reparaste.

## 2. Cuánto creció

| | julio (auditoría) | hoy |
|---|---:|---:|
| `runtime/` | ~33.700 líneas | **~57.000** |
| Subsistemas nuevos | — | `neural` 6.169 · `life` 2.772 · `conjunction` 2.205 · `legacy` 1.904 |
| `lab/genesis` | no existía | **19.723** |
| Tests | — | 1.933 recogidos |

`lab/genesis` es una **isla limpia**: no importa nada de `runtime`, `contracts` ni `engines`.
Toda su dependencia es interna. Eso es bueno para aislarlo y malo para integrarlo: hoy la capa
epistémica de Genesis **no está cableada al organismo**.

## 3. El problema estructural real — y no es la calidad del código

**Hay 100 banderas de entorno `RNFE_*` distintas en `runtime/`.** Y la capacidad cognitiva vive
detrás de ellas, **apagada por defecto**, con un invariante declarado explícitamente:

> `intervention_override.py:17` — *«Gated por `RNFE_REASONING_ACTUATES=1` (sombra OFF por
> defecto ⇒ camino nominal byte-idéntico)»*
>
> `organism/experience.py:14` — *«Gated por `RNFE_EXPERIENCE` (off por defecto ⇒ conducta
> byte-idéntica)»*
>
> `ADR_BUCLE_A_ACTIVATION.md` — *«Con TODOS los flags OFF, la conducta es byte-idéntica»*

**Esa disciplina es buena ingeniería**, y quiero ser claro: es modo sombra, y es exactamente
cómo se añade capacidad a un sistema que no te puedes permitir desestabilizar. El ADR del Bucle A
es de manual: tres banderas, todas apagadas, rollback de un interruptor, y activación
condicionada a compuertas con intervalo de confianza (Gate A1, Gate R1).

**Pero tiene un modo de fallo, y creo que es exactamente lo que estás sintiendo.**

Tras suficientes iteraciones, el organismo **por defecto** es una política reactiva ingenua. El
comentario del propio código lo dice sin piedad (`deferred_load_scenario.py:255`):

> *«Política reactiva ingenua (víctima de la trampa): ante carga elevada elige el arreglo
> inmediato más fuerte — que rebota vía deuda. El organismo previsor debe aprender a preferir
> shed; lo hace vía el override de previsión A11+A12 (bajo `RNFE_REASONING_ACTUATES`).»*

Y el organismo capaz existe sólo como **un brazo de comparación dentro de un script de
benchmark** (`scripts/run_live_agents_trap.py`: `agents_shadow` vs `agents_live`).

**No hay ningún perfil canónico que declare «esto es RNFE encendido».** El canon define
normativamente *qué es* RNFE, pero nada declara cuáles de las 100 banderas lo constituyen.

Y la vía de promoción se muerde la cola: el ADR dice que A3 —hacer A por defecto— exige
*«evidencia cross-seed acumulada de A2 en varios regímenes»*, pero A2 está a su vez gateado. Es
decir: acumular la evidencia exige correr deliberadamente configuraciones no-default, una a una,
indefinidamente.

**Mi lectura: lo que pide reingeniería no es el código. Es el modelo de activación. Tienes un
organismo al que no puedes señalar.**

## 4. El acoplamiento — la restricción real de cualquier reestructuración

Fan-in medido sobre 465 módulos:

```
57  runtime.storage      ← módulo-dios
44  runtime.world
38  runtime.organism
30  runtime.core
23  runtime.reasoning
```

**Seis ciclos entre paquetes de nivel 2:**

```
certification <-> reality      core     <-> storage
certification <-> world        organism <-> world
reality       <-> world        reasoning<-> world
```

`runtime.world` aparece en **cuatro de los seis**. Ése es el nudo. Cualquier reestructuración que
no rompa el acoplamiento bidireccional de `world` va a fracasar, porque `world` es a la vez el
escenario, el corredor de episodios y el punto por el que pasan razonamiento, organismo, realidad
y certificación.

## 5. El defecto que encontré leyendo código (no documentación)

`runtime/world/scenario_runner.py:806-811`:

```python
intervention = self.scenario.select_intervention(observation)
if memory_hits:
    top = memory_hits[0].get("structure", {})
    if top.get("relation_kind") == "support" and observation.alarm:
        # Memoria soporta la intervención por alarma
        intervention = self.scenario.select_intervention(observation)   # ← misma llamada
```

Verifiqué que `select_intervention` es **pura y determinista** (un umbral sobre `load` que
devuelve una cadena; `deferred_load_scenario.py:259-261`). Por tanto la rama **no puede cambiar
nada**: recalcula idénticamente lo que ya estaba en la línea 806.

No es código muerto: es **código que aparenta un efecto que no existe**. Quien lo lea concluirá
que la memoria influye en la intervención. En un sistema cuyo canon promete «memoria viva
multiescala», eso es una trampa a nivel de afirmación central.

*(El mecanismo de memoria que sí actúa es `_experience_biased_intervention`, y está tras
`RNFE_EXPERIENCE`, apagado por defecto. `memory_hits` sí se registra en telemetría, línea 895.)*

## 6. Opinión

**No reestructures el código. No lo necesita tanto como crees.** Lo que necesita reingeniería es
el modelo de activación, y son tres cosas en este orden:

1. **Declara el organismo.** Un perfil canónico: un conjunto nombrado de banderas que *es* RNFE,
   escrito en `canon/normative/`. Mientras no exista, «RNFE» nombra una familia de 2¹⁰⁰
   configuraciones y ningún resultado es sobre RNFE — es sobre una de ellas.
2. **Invierte el defecto.** El camino nominal debería ser el organismo; la sombra debería ser la
   ablación. Hoy está al revés, y eso significa que cada corrida honesta es una desviación
   deliberada del default.
3. **Borra el no-op** de `scenario_runner:806` o hazlo real.

Sólo después, si sigue haciendo falta: romper los ciclos de `runtime.world`.

**Y no tires la disciplina de banderas.** Es lo que te ha permitido llegar hasta aquí sin romper
nada. El arreglo no es quitar las compuertas: es añadir una **vía de promoción que termine** —un
perfil— en vez de una que se extienda para siempre.

## 7. Y aquí encaja Terrario, mejor de lo que dijimos

Genesis no puede responder «qué capacidad es necesaria para qué exigencia» porque tiene 2¹⁰⁰
configuraciones y un solo organismo. Terrario tiene **cinco arquitecturas fijas y ocho entornos**,
y la matriz corre entera.

> **La matriz A×D es precisamente el instrumento que diría qué banderas merecen estar en el
> perfil canónico.**

Terrario no es un desvío de Genesis. Es el generador de evidencia que desatasca su vía de
promoción — la que hoy se muerde la cola. Eso le da a «cerrar un ciclo en Terrario» una razón que
no es pedagógica: **es el insumo que Genesis necesita para poder declarar su organismo.**
