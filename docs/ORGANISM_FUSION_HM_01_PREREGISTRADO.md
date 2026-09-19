# `ORGANISM-FUSION-HM-01` · preregistro

**Sellado antes de existir el código.** Todos los valores salen de aritmética
exacta sobre enumeración; ninguno de una corrida.

Base `7ac43fb` (cierre implementado del Nivel 1.2), en árbol propio. Rama
`experiment/organism-fusion-hm-01`.

---

## 0 · Qué es esto, y qué NO es

**No es un decimal.** No hay adquisición nueva, no hay parámetro que se aprenda
aquí, no hay `N_TRAIN` propio. El `1.4` ya tiene su adquisición definida --binding
conjuntivo-- y queda **congelado tal como está preregistrado en `3bdf6fb`**, sin
tocar su árbol.

Es un **artefacto de composición**: reúne capacidades ya verificadas para
comprobar que existe un solo organismo que las contiene y las usa juntas.

## 1 · Qué responde que ningún nivel podía responder

Hoy están demostrados `B+Q+H` (Nivel 1.2) y, por separado, `B+Q+M` (Nivel 1.3).
Son **hermanos**, los dos forkean de 1.1, y **no existe ninguna instancia con las
cuatro**. La acumulación ha ocurrido dentro de cada rama y nunca entre ellas.

La pregunta es doble y el orden importa:

```
1 · ¿pueden H y M coexistir en el mismo organismo sin alterarse?      coexistencia
2 · ¿participan las dos en una misma respuesta?                        uso conjunto
```

La primera la contestaría una suite conjunta: demuestra que **las piezas caben en
el mismo árbol**. La segunda necesita el factorial: demuestra que **ambas
participan en el mismo cálculo**. Son cosas distintas y sólo la segunda es
interesante.

## 2 · Las dos genealogías, separadas

```
genealogía de la evidencia    congelada · cada experimento conserva su rama y su árbol
genealogía del organismo      este artefacto · reúne componentes compatibles
```

El contrato histórico «en 1.3 no existe `level12/`» **sigue siendo correcto para
aquel experimento** y no se traslada aquí, cuyo propósito es justamente
reunirlos. No se borra el contrato antiguo: se distingue su ámbito.

## 3 · Se reúnen procedimientos, no artefactos

**Hecho de código medido.** `reconstruct` es idéntico en 1.2 y en 1.3 salvo
docstrings y saltos de línea; `H` se adquiere **sin leer `B` ni `Q`**; `M` tiene
cero parámetros.

Pero por eso mismo no se pueden traer los objetos: la `H` de 1.2 se adquirió
sobre el flujo de la semilla `80000011` y la `M` de 1.3 se probó sobre el núcleo
de `90000011`. Traerlas literalmente mezclaría procedencias y produciría
exactamente **dos cuerpos y dos orientaciones ocultos dentro de una supuesta
fusión**.

```
una semilla σ  →  un núcleo (B, Q) reconstruido con el código sellado de 1.1
               →  H readquirida con el código sellado de 1.2 sobre el flujo de σ
               →  M, mecanismo sin parámetros
```

**«Un solo núcleo» se comprueba por identidad de objeto**, no por huellas
iguales: dos núcleos distintos con la misma huella seguirían siendo dos cuerpos.

## 4 · `M` entra por copia literal, verificada contra el original congelado

`terrario/organism/memory.py` es **copia byte a byte** de
`terrario/level13/memory.py` en `705239c`. Es el idioma que ya usa este
repositorio: `level11/world.py` es copia literal de `level1/world.py` con
contrato de linaje.

Los árboles comparten base de objetos, así que el contrato lee el blob congelado
directamente --`git show 705239c:terrario/level13/memory.py`-- y exige identidad.
No hay merge, no hay push, y la semántica de `M` no puede derivar en silencio.

## 5 · Congelación · tres envoltorios

```
FrozenOrganism
  ├── FrozenFactoredBody     B    existe en level11
  ├── FrozenDirectional      Q    se reescribe aquí
  └── FrozenProximity        H    NUEVO · nadie lo había construido
```

`QualitativeDistanceModel.observe` existe (`terrario/level12/proximity.py:45`) y
`Level12Agent` publica `self.proximity` (`terrario/level12/agent.py:32`).
**Ninguna pieza del organismo expone `observe`**, y el contrato lo recorre por
AST.

Durante la fusión **no cambia ningún parámetro**: las tres huellas son idénticas
antes y después, y `M` no tiene ninguna.

## 6 · El ensayo

```
PRESENT   recibe (o_present, g)   ·  la memoria escribe g  ·  sin acción, sin mundo
TICK      la memoria pasa a HELD_1
QUERY     recibe (o_query, s)     ·  el cue ya NO está     ·  la memoria devuelve ĝ
RESET     única operación que borra
```

`o_present = (1,0,0,0)` fijo, independiente del cue. `o_query` recorre las 16
observaciones, también independiente del cue, luego `I(G ; o_query) = 0` por
enumeración. La semántica de `M` es la sellada en `09c1d80`: leer antes del tick
devuelve nada, leer no consume, sólo `reset` borra, y a los dos ticks expira.

**La política motora no cambia.** El Nivel 1.2 dejó cerrado que la distancia no
modifica la acción; aquí la prueba es **predictiva**, no conductual.

## 7 · El readout conjunto

```
J_N(o, ĝ, s, a) = B(o,a) · Q(ĝ,a) · H(s)
J_F(o, ĝ, s, a) = B(o,a) · Q(ĝ,a) · [1 − H(s)]

T_N = 1[movimiento posible] · 1[acción alineada con el cue presentado] · 1[D = N]
```

En palabras: *«este comando es físicamente realizable, corresponde a la dirección
que vi hace un tick, y va con una referencia probablemente cercana».*

Brier poblacional conjunto, cerrado: se integra sobre `D` y sobre `s | D` con las
marginales selladas de 1.2, sin banco empírico y sin RNG de evaluación.

## 8 · El factorial · valores sellados

Con `H OFF` el factor vale su prior ignorante `1/2` — que es exactamente el
`NO_DISTANCE` de 1.2. Con `M OFF` no hay cue en la consulta, luego
`P(alineada) = 1/4`, el prior ignorante de una dirección entre cuatro.

Con cuerpo y orientación **ideales**, en aritmética exacta:

```
   H     M      BS_joint      exacto
  ON    ON      0.018182      1/55        ← las cuatro capacidades
  ON   OFF      0.051420      181/3520
 OFF    ON      0.031250      1/32
 OFF   OFF      0.054688      7/128       ← línea base
```

Y aquí está el contenido del experimento:

```
mejora sólo H          23/7040   = 0.003267
mejora sólo M           3/128    = 0.023438
suma de las dos        47/1760   = 0.026705
mejora conjunta       257/7040   = 0.036506

INTERACCIÓN            69/7040   = 0.009801     SUPERADITIVA
razón conjunta / suma                1.367
```

**La mejora conjunta es mayor que la suma de las mejoras por separado.** Es
calculable de antemano --por tanto es verificación, no descubrimiento-- pero es
una cantidad que **ninguna rama por sí sola podía definir**, porque hace falta
que las dos capacidades existan en el mismo organismo para escribirla.

Ésa es la diferencia entre ejecutar las suites juntas y este factorial.

## 9 · Gates

| gate | criterio |
|---|---|
| **F-0** un solo núcleo | identidad de objeto: los caminos de `H` y de `M` referencian el MISMO `FrozenOrganism` |
| **F-1** linaje intacto | huellas `B`, `Q`, `H` idénticas pre/post; 1.2 verificado antes de congelar |
| **F-2** `M` sin deriva | `organism/memory.py` byte-idéntico al blob de `705239c` |
| **F-3** semántica de `M` | leer antes del tick da nada · leer no consume · dos ticks expiran · `write` sólo acepta `CueToken` |
| **F-4** coexistencia | las cuatro capacidades responden en la misma instancia |
| **F-5** uso conjunto | los cuatro `BS_joint` reproducen la tabla sellada |
| **F-6** interacción | la mejora conjunta supera la suma de las individuales |
| **F-7** sin fuga | `I(G ; o_query) = 0` por enumeración |
| **F-8** política intacta | `R_align` idéntico pre/post con el instrumento cerrado |
| **F-9** pasividad | medir no mueve huellas; cero RNG nuevo en las métricas |

**Fixtures negativas obligatorias:** dos núcleos distintos en vez de uno ·
`memory.py` alterado un byte · omitir el tick · `H` sin congelar · una métrica que
escribe · un banco donde `o_query` codifique el cue.

## 10 · Semillas y azar

```
110000011 … 110000018       disjuntas de todo lo usado y reservado (verificado, con los +7)
```

Cero RNG nuevo en la fusión: el azar heredado reconstruye `B`, `Q` y el flujo de
`H`; el factorial y el Brier son cerrados.

## 11 · Afirmación máxima autorizada

> Un mismo organismo conservó intactas cuatro capacidades adquiridas en ramas
> experimentales distintas --conocimiento corporal, orientación direccional,
> proximidad cualitativa y persistencia de un tick-- y las hizo participar
> simultáneamente en una misma predicción, con una mejora conjunta superior a la
> suma de las mejoras individuales.

**Obligatorio junto a ella:**

> La regla de composición fue suministrada por diseño y no se aprendió. Esto es
> verificación del conjunto, no descubrimiento espontáneo de integración.

**No autorizado:** emergencia, integración descubierta, sinergia cognitiva,
organismo unificado en sentido fuerte, ni que las capacidades se hayan adquirido
en presencia unas de otras — **cada una se adquirió en aislamiento de las
demás**, y eso no cambia por reunirlas después.

## 12 · El libro mayor, con sus tres clases

```
B · Q · H     parámetros aprendidos, cada uno EN AISLAMIENTO de los otros
M             mecanismo suministrado, cero parámetros
composición   suministrada, nunca aprendida, y sostiene todos los resultados
```

Decir «el organismo tiene cuatro capacidades» tapa la tercera fila.
