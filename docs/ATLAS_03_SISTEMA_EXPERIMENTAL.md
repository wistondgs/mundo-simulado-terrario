# Atlas 03 · El sistema experimental

**2026-09-21** · `1cf9b8f` · depositado en `CARTOGRAFIA_TERRARIO_01.md` **§XLI**
· 19 citas `fichero:línea`, todas verificadas contra el fuente.

Cubre el punto 7 del contrato: mundos, runners, preregistro, lesiones,
controles, métricas, gates, CAS, ledger y semillas.

---

## 1 · Hay un paso compuesto y cuatro llamadas a la física en crudo

| Ruta | Llama | Contrato de acción | Lifecycle | Coste de paso | RNG exógeno |
|---|---|---|---|---|---|
| `ExperimentController` | `run_step` | sí | sí | sí | `world_seed + step` |
| `SandboxService` | `run_step` | sí | sí | sí | `world_seed + step` |
| oráculos + 4 guiones | `run_step` | sí | sí | sí | `world_seed + step` |
| **`CausalRuntime.step`** | `physics.step` | **no** | **no** | sí | **`agent_seed + tick`** |
| **`verify_reproducibility.py`** | `physics.step` | **no** | **no** | **no** | propio |

Las tres primeras dicen en un comentario que la secuencia ya no vive en ellas y
que lo único que difiere es su instrumentación. **Eso es cierto y se verifica.**
Las dos últimas son otra física.

## 2 · El banco causal · declara su estrechez, pero no toda

`CausalRuntime` no es un duplicado descuidado: comprueba su alcance y devuelve
`NOT_FORKABLE` salvo agente `A0_RANDOM`, escenario `d0_differences.yaml` y sin
`opportunity_lifecycle`.

**La cualificación no mira el modo de direccionamiento.** Medido en vivo:

```
A0Random(addressing_mode="T1_ENTITY").decide()  →  CONSUME
    target_id = -1 · direction = NONE · selector_value = 3
DIRECTION_DELTA[NONE] = (0, 0)
```

Sin el contrato de acción, `find_target` mira **la propia celda del organismo**.
Es decir: **bajo T1, en el banco causal, un organismo no puede consumir nunca**,
y la corrida se clasificaría igual como `EXACT_FORKABLE`. No aparece un objetivo
fantasma: aparece un organismo paralizado que se leería como «T1 rinde mal».

Hoy **nadie construye el banco con T1** — el árbol no tiene un solo sitio. Es un
hueco latente, no un resultado contaminado, y cerrarlo cuesta una línea.

La segunda divergencia: el banco siembra el RNG **global** y deriva los sorteos
exógenos de `agent_seed + tick`, que es exactamente la semántica que `run_step`
canonizó fuera porque «ataría los shocks exógenos futuros a qué agente corre».
Inerte hoy —la física no consume su RNG—, deja de serlo el día que lo consuma.

## 3 · El guion de reproducibilidad no verifica el paso real

`verify_reproducibility.py` llama a `physics.step` y **reimplementa la búsqueda
de objetivo en línea** — una cuarta copia, justo la que `find_target` documenta
haberse extraído para evitar. Sin contrato de acción, sin lifecycle y **sin
coste de paso**.

Verifica con rigor la reproducibilidad de una tubería que ninguna campaña
ejecuta.

## 4 · El test de paridad compara la ruta consigo misma

`test_world_runtime_parity.py` está bien hecho —agente guionizado, para que una
divergencia no confunda «las físicas difieren» con «los agentes difieren»; el
fallo nombra el primer paso y el primer campo—. Pero `_trayectoria` ejecuta
**`run_step` las dos veces**.

Prueba determinismo, no paridad entre superficies. Su propio encabezado dice que
existe porque «un nivel superado bajo una superficie y reprobado bajo la otra no
es un nivel superado», y **las superficies que podrían diverger son las que no
compara**.

> **La reparación más barata de todo este volumen:** un test de ~20 líneas que
> enfrente `run_step` contra `CausalRuntime.step` bajo T0 con el mismo guion.
> Hoy no existe.

## 5 · Dos disciplinas de RNG opuestas en el mismo repositorio

`RNGManager` deriva mundo, agente y observador con **tres `randint` seguidos**
sobre el maestro: son dependientes del orden de llamada, y meter un cuarto
subsistema entre medias cambiaría retroactivamente todas las semillas de agente.

`OpportunityLifecycle._stream` hace lo contrario y dice por qué:
`blake2b(seed:kind:key:generation)`, «una clave sobre la identidad, nunca sobre
cuántas llamadas vinieron antes».

El ciclo de oportunidades ya resolvió el problema que el gestor de RNG todavía
tiene.

## 6 · Las cuatro lecturas que no pueden fundirse · y esta vez sí se adoptaron

```
0.0            hubo soporte, se calculó, dio cero
NOT_EVALUABLE  no existe soporte — el denominador está vacío
MISSING        falta un campo que el cálculo necesita
INVALID        el dato está y viola el contrato que dice cumplir
```

La defensa es **estructural**: `float(reading)` levanta salvo que sea OK,
`.value` es `None` salvo que sea OK, y no hay método que convierta una lectura
no-OK en número. `ratio()` devuelve `NOT_EVALUABLE` con denominador vacío en vez
de dividir, «porque esa única línea es donde nace casi todo cero falso».

Y **está adoptado** — nueve consumidores, incluidos los cuatro guiones de
experimento. Es la diferencia con la capa de conocimiento: aquí los contratos
tienen usuarios.

## 7 · La última puerta

`evidence_admission` es el único sitio donde se decide si un número puede ser
evidencia, y vuelve a preguntarlo aunque el preregistro y el runtime ya lo
hicieran: «una puerta que confía en quien la llama es documentación, no una
puerta». Sus cuatro no-acciones están escritas como lo que son — cada una fue
una vía por la que entró un hallazgo falso:

```
no recalcula una métrica      no modifica una Reading
no imputa la ausencia         no reinterpreta INVALID
```

## 8 · El preregistro está vivo

Siete estados con transiciones estrictas; `PREREGISTERED_LOCKED` sólo puede ir a
`SUPERSEDED` o `WITHDRAWN`, ambos terminales. `SeedCommitment` sella cuatro
familias de semillas **cada una con su hash**, repartidas en seis particiones
con `CONFIRMATORY_TEST` y `HOLDOUT` entre ellas. `ExposureStatus` lleva la
contabilidad de contaminación.

Y tiene filas:

```
141  preregistros sellados          708  cadena de auditoría
 45  registros de exposición      1 664  eventos de ejecución científica
```

**Ésta es la distinción más útil del volumen:** lo que toca el ciclo
experimental tiene filas; lo que no lo toca —42 de 72 tablas de la capa de
conocimiento— está vacío.

## 9 · «Replay» no es re-ejecución

`OfflineReplay` es un cursor sobre una traza grabada: `forward`, `backward`,
`reset`, `jump`. No vuelve a simular nada. El contrato de conocimiento lo lista
entre las rutas de ejecución; no lo es.

## 10 · Lo que no se sabe

1. **K1** · Si alguna semilla publicada depende del orden de llamada de
   `RNGManager`.
2. **K2** · Si `run_step` y `CausalRuntime.step` dan la misma trayectoria bajo
   T0 con el mismo guion. El test no existe.
3. **K2** · Qué mide de menos `verify_reproducibility.py`: sin coste de paso, el
   criterio de terminación difiere.
4. **K2** · Cuántas de las 141 ejecuciones selladas corrieron por `SandboxService`
   y cuántas por `ExperimentController` — §XXI ya documentó que la semántica
   efectiva del sandbox no ejecuta `OpportunityLifecycle`.
