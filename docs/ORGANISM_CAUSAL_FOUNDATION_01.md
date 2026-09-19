# ORGANISM-CAUSAL-FOUNDATION-01

**2026-09-18.** Dejar a Terrario capaz de **observar y falsar** cambios adaptativos, antes de
introducir B2/B5/B1. No mejora conducta: su objetivo es poder demostrar después qué ocurrió.

**Nombres.** El repositorio ya usa G0–G8 con otro significado (G1 = hashes de cartografía,
G4 = pureza de intervención, G8 = reportabilidad de instrumento). Los cinco gates de este paquete
van como **OCF-G1..OCF-G5** para que no se pisen.

| Gate | Qué exige | Estado |
|---|---|---|
| **OCF-G1** Autoridad de estado | cada variable adaptativa tiene un dueño y los writers están enumerados | **NO PASA** — medido, 1 pieza disputada |
| **OCF-G2** Intervención de término | un término ON/OFF produce evidencia observable aunque no mueva conteos de invocación | sin empezar |
| **OCF-G3** Congelación adaptativa | con freeze completo, `adaptive_hash_t = adaptive_hash_{t+n}` | frontera definida, interruptor sin construir |
| **OCF-G4** Atribución de señal | UNC, CURIO y META pueden consumir una fuente común sin confundirse | sin empezar |
| **OCF-G5** Linaje | una mutación adaptativa reconstruible como causa → escritura → persistencia → lectura | sin empezar |

---

## OCF-G1 · Autoridad de estado — MEDIDO

`scripts/state_authority_probe.py`. La tabla de escritores de `FRONTERA_ESTADO_APRENDIDO_01` se
llenó **leyendo** el código. Esta sonda **instrumenta**: intercepta `__setattr__` del agente y de
cada submódulo, envuelve las tres fases, y además hashea el conjunto adaptativo al final de cada una
para atribuir las escrituras en sitio (`M.data.copy_`), que no pasan por `__setattr__`.

### Resultado sobre 68 pasos de un mundo generado

**Exactamente una pieza tiene dos escritores.** Las otras veinte, uno solo.

```
  estado                                perceive   decide    learn
  ------------------------------------------------------------------
  homeostasis._energy                         68        ·       68     ← DISPUTADA
  agente._hidden                               ·      136        ·
  agente._last_latent                         68        ·        ·
  agente._last_state / _last_action / …        ·       68        ·
  agente._energy_baseline / _baseline_count    ·        ·       68
  agente.last_prediction_error                 ·        ·       68
  episodic_memory._write_idx                   ·        ·       68
  learner._step_count                          ·        ·       68
```

Cambios en sitio del conjunto adaptativo, por fase:

```
  parámetros (optimizador)      learn 68
  longterm_memory.M             learn 68
  episodic_memory._buffer       learn 68
  _energy_baseline              learn 45     ← 45, no 68: sólo cuando hay `_last_log_prob`
  homeostasis._energy           perceive 68 · learn 68     ← DISPUTADA
  homeostasis._threshold        nunca                      ← la costura limpia de B3
```

### Lo que esto fija

1. **El problema de autoridad está localizado en un solo atributo.** No es una refactorización del
   organismo: es `homeostasis._energy`, con `update()` acumulando en `learn` y `perceive`
   pisándolo por asignación. O1 es más pequeño de lo que el diagnóstico sugería.
2. **`homeostasis._threshold` no lo escribe nadie.** Confirma que el setpoint es la costura limpia
   para B3: convertirlo de constante a variable de estado no colisiona con ningún escritor.
3. **`_energy_baseline` se mueve 45 de 68 veces**, no 68. Depende de `_last_log_prob`, así que su
   deriva es función de cuántas veces el agente produjo una política, no de cuántos pasos vivió.

### La sonda se falsa a sí misma

Una sonda que no demuestra su pasividad no es evidencia. La anterior de esta familia infló dos
magnitudes ×18.6 y ×10 por contaminarse, y no se vio hasta una verificación adversarial. Aquí la
vida instrumentada y la limpia terminan con la misma huella, pieza por pieza:

```
  _energy_baseline           -0.0323529412  =  -0.0323529412
  episodic_memory._buffer     5efb9513c22c  =   5efb9513c22c
  homeostasis._energy          0.149166667  =    0.149166667
  homeostasis._threshold               0.5  =            0.5
  longterm_memory.M           ba2cf78c7f68  =   ba2cf78c7f68
  parámetros (optimizador)    184a8507682e  =   184a8507682e

  OBSERVER_PASSIVITY = SÍ
```

Eso cierra también el punto 8 del alcance: *demostrar observer passivity*. Está demostrada para
esta sonda; queda pendiente para el observador del experimento.

### Veredicto

```
OCF-G1 = NO PASA    1 atributo y 1 pieza adaptativa con escritor múltiple
```

No se repara aquí: reparar la autoridad es **O1 · HOMEOSTASIS-AUTHORITY**, y exige antes fijar el
contrato de quién posee el estado corporal frente al estado estimado.

---

## Contrato que O1 tendrá que fijar

De la decisión consolidada, la semántica que hoy no existe:

```
x_body(t)          variable fisiológica autoritativa — del mundo/cuerpo
      ↓ interocepción
x̂_internal(t)      lo que el organismo estima de sí mismo
      ↓
d(t) = x* − x̂(t)   desviación
      ↓
drive              transformación de la desviación
```

Hoy el código colapsa `x_body` y `x̂_internal` en un solo atributo, y por eso hay dos escritores. La
consecuencia que importa: **la percepción interna no tiene por qué ser perfecta**, y con un solo
atributo no se puede ni expresar que no lo sea.

---

## OCF-G3 · FULL_ADAPTIVE_FREEZE — CONSTRUIDO, GATE ABIERTO

`terrario/agent/adaptive_freeze.py` + `scripts/adaptive_freeze_gate.py`.

**Una sola autoridad lógica, cuatro puntos de commit.** No cuatro `if freeze:` dispersos por A4:
`AdaptiveFreeze.allow(component)` es la política única y los cuatro writers la consultan antes de
materializar. La palabra es *commit*: el organismo puede calcular que quiere aprender —forward,
pérdidas, gradientes, candidatos de experiencia, diagnósticos— y lo que no puede bajo freeze es
materializar el cambio.

**Bloqueo, no reversión.** `allow` se evalúa *antes* de que la escritura ocurra y, al devolver
False, la escritura no llega a ejecutarse. `escribir → leer → revertir` no equivale a
`no escribir → leer` aunque las dos terminen con el mismo hash.

### Matriz de aceptación

| Componente | NORMAL | heredado (`learning_commit_enabled=False`) | FULL |
|---|---|---|---|
| parámetros | cambia | **no cambia** | no cambia |
| buffer episódico | cambia | **cambia** | no cambia |
| `M` | cambia | **cambia** | no cambia |
| `_energy_baseline` | cambia | **cambia** | no cambia |
| hash adaptativo | cambia | cambia | **idéntico** |
| candidatos adaptativos | existen | existen | **existen** |
| commits adaptativos | 60/60 por writer | parciales | **0 de 240** |

La fila que demuestra el freeze es la última pareja: **240 intentos, 0 commits**. Un brazo que
termina idéntico porque nadie intentó escribir no probaría nada.

### Los doce criterios

```
[✓] G3.1 fidelidad de frontera      [✓] G3.7 determinismo
[✓] G3.2 control positivo           [✓] G3.8 pasividad del testigo (replay)
[✓] G3.3 congelación completa       [✓] G3.H pasividad de auditoría (ruta real)
[✓] G3.4 evidencia de bloqueo       [✓] G3.I integración en runtime
[✓] G3.5 sin reversión disfrazada   [✓] G3.J control positivo real
[✓] G3.6 discriminación heredada    [✓] G3.K evidencia en runtime
```

**Regresión (criterio K del contrato).** NORMAL se comporta exactamente como antes de la
infraestructura. Comprobado llevando el generador reparado a un árbol en HEAD y dejando allí el A4
previo, de modo que lo único que difiere es la autoridad de commit:

```
                acciones          energía        parámetros       M         buffer      baseline
A4 previo   22cebff62237db7a  821d6dc4e607e17d  1a2e3fe9d68a7a0e  355b9c…  bef0ce…  -0.0166666666667/60
A4 nuevo         idéntico          idéntico          idéntico     idéntico  idéntico       idéntico
```

**Un defecto propio que el gate cazó.** La primera corrida daba G3.6 en rojo: el brazo heredado
parecía mover parámetros. No los movía. `longterm_memory.M` **es** un `nn.Parameter` y está dentro
de `get_parameters()`, aunque no lo gobierne el optimizador — se escribe con `M.data.copy_()`.
Incluirlo en la huella de «parámetros» solapaba dos piezas de la frontera. `learned_state_audit.py`
ya lo excluía por lo mismo.

### Por qué el gate queda ABIERTO — condición de parada 10

El criterio E exige que `_adaptive_state_hash` permanezca idéntica. Medido:

```
episodic_buffer       la ve
longterm_M            la ve
energy_baseline       NO LA VE
```

Se le puede sumar 42.0 a `_energy_baseline` y 17 a `_baseline_count`, y
`_adaptive_state_hash` no se mueve. Pero `FRONTERA_ESTADO_APRENDIDO_01` **adoptó** la frontera
«la línea que `_adaptive_state_hash` ya trazaba **más `_energy_baseline`**». Es decir: la huella
agregada del proyecto no cubre la frontera que el proyecto adoptó.

Consecuencia concreta: el criterio E **se satisface en vacío** para esa pieza, y
`adaptation.py:331` usa esa huella para medir el estado adaptativo antes de una transferencia.

Por instrucción explícita —*«Si el hash omite una pieza perteneciente a la frontera adoptada,
detener OCF-G3 y reportarlo»*— no se repara aquí: cambiar la huella toca `adaptation.py`, fuera de
alcance. **El gate lo comprueba él mismo y se niega a declarar PASS mientras la omisión exista**,
para que no dependa de que alguien lo recuerde.

```
OCF-G3 = ABIERTO POR CONDICIÓN DE PARADA 10
```

### Provenance del protocolo (punto 13)

`full_adaptive_freeze` vive en la configuración del agente, así que el modo adaptativo viaja en
cualquier artefacto que selle la configuración. Lo que **no** está resuelto: nada obliga a que un
artefacto lo declare, así que una evidencia futura todavía puede quedar con el modo implícito.
Queda anotado, no cerrado.

### Fuera de alcance, respetado

No se tocó `homeostasis._energy`, `_threshold`, B2, B3, B5, B1, curiosity, uncertainty ni el
acoplamiento planner/world-model. La autoridad de commit no necesitó ninguno.
