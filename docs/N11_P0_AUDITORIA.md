# N1.1 · P0 · auditoría antes de diseñar nada

**2026-09-21** · siete frentes medidos sobre el código actual, no recordados.
Ninguna semilla consumida, nada modificado. `PRE_HEAD 064f959`.

N1.1 pregunta `A = f(O_ext)` → `A = f(O_ext, E)`: si un estado interno actual
puede gobernar la decisión con el presente externo equivalente. Sin memoria.

## Veredicto por frente

```
fisiología     energy · la ÚNICA candidata. No hay segunda variable
control        CONTROLLABLE
consecuencia   POSSIBLE_WITHOUT_HOMEOSTASIS       ← la condición de parada NO se activó
fuga           LEAKS · ninguna en el tensor
histórico      el espinazo del instrumento de N1.0 es reutilizable
memoria        HISTORY_FREE_ACHIEVABLE
identidad      station_opportunity_key
```

Cero bloqueos duros. Pero hay una bifurcación que decide qué significa el
estudio, y ocho condiciones que son calibración y no imposibilidad.

## La bifurcación · de dónde viene `E`

Los dos frentes la vieron desde lados opuestos y ninguno es obviamente el
correcto.

**`E` exógena** — el aparato la fija con `set_agent_energy`, la misma ranura que
N1.0 usó para borrarla. Limpia, controlable, balanceable por diseño. Pero
entonces `E` es **un token escrito por el experimentador dentro del campo de
energía**, y eso, en palabras del propio audit, está «más cerca del brazo C de
N1.0 que de la fisiología».

**`E` endógena** — emerge de la trayectoria a través de la frontera de muerte,
que es física genuina: arriesgar con la energía baja es terminal, ir a lo
seguro no. Pero entonces `E` es **una integral de las consecuencias pasadas**
—un token de historia con otro portador— y N1.1 estaría re-corriendo N1.0 en
silencio.

No es una elección de implementación. Decide si el estudio mide interocepción
o mide memoria disfrazada.

## Lo que hay que arreglar antes, medido

**`agent_energy` no está normalizada.** Su docstring dice «normalized 0-1»;
`state.py:110` recorta **por arriba y no por abajo**. Medido: `stored −5.00 →
agent_energy −0.25`, y el motor llega solo —coste de paso desde 2.0 con coste
3.0 da `stored −1.00`, `alive=False`, **observado −0.05**—, así que la
transición terminal que llega a `learn` puede llevar energía negativa. Rango
real `(−∞, 1.0]`.

**El recorte superior pierde información y dispara constantemente.** Bajo
`DEFAULT_ECONOMY`, el 23 % de los pasos de LEARN-A1 tienen `stored >
max_energy`: **69 energías distintas llegan todas como exactamente `1.0`**.
N1.1 no puede heredar esa economía.

**Las condiciones de regla descartan claves desconocidas en silencio.** Probado:
una condición con `agent_energy: {max: 14.0}` **se parsea, la clave se tira sin
error y la regla dispara incondicionalmente**. Se podría escribir una regla
condicionada por energía, el motor la aceptaría y no haría nada. Es el peor
tipo de defecto: una especificación que parece honrada.

**`require_channel_contract` rechaza todo mundo `hidden=False`** — o sea el eje
`risk` entero, que es donde vive HOMEO-A1. Hay que **reformular** el contrato
como «la acción correcta no es derivable de `O_ext` sola», no renunciar a él.

**No existe verdad de terreno dependiente de `E`.** `correct_side` toma
`(station, step)`, y `Score.modulation` mide que la conducta **cambió**, no que
cambió **correctamente**. Hace falta escribir un `correct_side_given_energy`, y
clavarlo en la **línea letal** (`loss = 6.0`) y no en el `low_energy = 14.0`
declarado, que está a ocho unidades de cualquier cosa.

**La frontera de muerte no se ejercita.** `0/20 muertes` medidas bajo HOMEO-A1 +
`DEFAULT_ECONOMY`, energía mínima 0.95. La ruta endógena hoy no existe en la
práctica; habría que re-derivar la economía hasta que arriesgar con poca
energía mate de verdad.

**El reloj es un proxy de `E`.** `expose_time_fraction` viene `True` por defecto
y bajo drenaje determinista reconstruye la energía con `r = −0.973`. No está en
el tensor, pero está.

**Y hay que declarar una inversión de contrato.** `present_without_energy` lleva
un docstring que dice que **no** es la firma de `SAME_PRESENT` y que no debe
usarse como tal. En N1.1 pasa a ser exactamente la firma correcta, porque la
energía deja de ser parte del presente y pasa a ser la variable bajo estudio.
Eso va al preregistro, no se desliza.

## Dos frentes se contradecían · resuelto midiendo

Uno decía que el sustrato ya existe; otro que hace falta un mundo nuevo porque
las 8 decisiones de una vida tienen presentes únicos. Medían configuraciones
distintas:

```
expose_time_fraction=True    16 presentes distintos / 64 decisiones · mayor clase  6
expose_time_fraction=False    4 presentes distintos / 64 decisiones · mayor clase 32
```

Con el reloj apagado **32 decisiones comparten un presente externo**. No hace
falta mundo nuevo; hace falta apagar el reloj y declararlo.

## El constructo ya estaba escrito en el repo

`HOMEO-A1` es `("risk", Demand(hidden=False, risk=True))`, y su pasaporte dice
literalmente: «El organismo modula su conducta según el estado de una variable
esencial interna, de modo que la misma observación externa produzca decisiones
distintas según su viabilidad.» Entrada declarada: `observation.agent_energy`.
Endpoint `Score.modulation = P(safe|low) − P(safe|high)`.

Es N1.1 palabra por palabra, escrito antes de esta conversación, y sin
experimento — uno de los diez pasaportes con **cero** campañas.

## Identidad de decisión, contra `LIMIT-N10-03`

`station_opportunity_key`: `(station.index, door_column, up_id, down_id,
history, designated, ocurrencia dentro de la estación)`. Disponible entero
dentro de `n1_run` en el momento de registrar, y sellado por el generador antes
de correr. Medido estable entre semillas y sensible a la geometría.

## Estado

```
N11_INSTRUMENT_READY        = NOT_YET   (P1 sin hacer)
N11_INFORMATION_SUFFICIENT  = NOT_YET   (P2 sin hacer)
N11_CAUSAL_FORM_SPEC        = NOT_SEALED
READY_TO_IMPLEMENT_N11      = NO
```

P1–P3 están bloqueadas por la bifurcación: exógena y endógena producen
instrumentos, gates y mutantes distintos.
