# `ORGANISM-FUSION-REMEMBERED-BINDING-01` · informe

**`REMEMBERED_BINDING_STATUS = VERIFIED`** · los diez gates en las ocho semillas.

Base `68d852d`, árbol propio. Preregistro sellado en `180737b` **antes** del
código, con **Enmienda 1** (§4). Semillas `120000011 … 120000018`.

---

## 1 · Qué es

**No es un decimal.** Reúne `B` (1.0), `Q` (1.1), `H` (1.2), `M` (1.3) y `ψ`
(1.4) en una instancia. Es la pieza que faltaba antes del 1.5: existía
`B+Q+H+M` y existía 1.4 con `ψ`, pero **ningún organismo tenía memoria y binding
a la vez**.

## 2 · La tarea

```
PRESENT   un cue g*   ·  M lo escribe  ·  sin acción
TICK
QUERY     escena de DOS referencias, el cue ya no está fuera
RESET
```

*¿Cuál es la proximidad de la referencia cuyo cue recordé?*

Sin `M` no se sabe **qué** referencia es la diana; sin `ψ` se sabe cuál es pero no
qué evidencia le pertenece. `M` sigue guardando **un solo `CueToken`**, sin
portador y sin ampliar horizonte.

## 3 · El factorial

```
    M     ψ      medido     sellado            Δ
   ON    ON    0.018264    0.018182    +0.000081
   ON   OFF    0.024770    0.024716    +0.000054
  OFF    ON    0.053058    0.053054    +0.000004
  OFF   OFF    0.053058    0.053054    +0.000004

mejora sólo M        0.028299
mejora sólo ψ        0.000000      ← CERO EXACTO
mejora conjunta      0.034813
INTERACCIÓN          0.006515      (sellada 0.006534)
```

> **`ψ` sin `M` no aporta absolutamente nada.** Su contribución marginal es cero
> exacto, y las dos filas con `M OFF` valen lo mismo hasta el último decimal.

Es más fuerte que la fusión `H+M`, donde las dos capacidades aportaban por
separado. Aquí la dependencia es **total**: toda la interacción es superaditiva
porque uno de los dos efectos marginales es nulo.

**Y hay que decir qué clase de hecho es:** es una propiedad de **la tarea que
diseñamos**, no un descubrimiento sobre el organismo. Elegimos una consulta donde
el binding es inútil sin la diana. Sigue siendo la tarea correcta, porque es la
única en la que las dos capacidades son portantes.

## 4 · Defecto hallado · y estaba en el sello

**La primera tabla del preregistro estaba mal ponderada.** Ponderaba «acción
alineada» al `1/2` cuando sobre cuatro acciones ocurre en **una de cada cuatro**,
así que los cuatro valores salían casi al doble.

Se descubrió porque la corrida discrepó del sello por un factor cercano a dos.
**El sello hizo su trabajo aun estando mal**: la discrepancia obligó a mirar, y lo
que estaba mal era el sello, no la medición. Recalculado con la ponderación
correcta, el cerrado **predice la medición**:

```
             corregido      medido           Δ
M ON  ψ ON    0.018182    0.018264    +0.000081
M ON  ψ OFF   0.024716    0.024770    +0.000054
M OFF ψ ON    0.053054    0.053058    +0.000004
```

Las diferencias son exactamente el error de `B` y `Q` aprendidas frente a
ideales. La enmienda está en el preregistro como **Enmienda 1**, con los valores
originales **retirados** y sin reescribir el commit sellado.

**Lo que la enmienda no cambió:** la contribución marginal de `ψ` sigue siendo
cero exacto, las filas con `M OFF` siguen empatando, la interacción sigue siendo
enteramente superaditiva. El error era de **escala, no de estructura** — y eso es
suerte, no mérito.

## 5 · Una operación de lectura declarada

Localizar el elemento direccional cuyo cue coincide con el recordado es una
comparación de identidad sobre tokens opacos --la misma que hace `Q` al indexar
su fila--, pero **ningún readout anterior la tenía**. Se declara **suministrada
por diseño**, como la regla de composición.

**No es atención, no es búsqueda, no es memoria relacional.**

## 6 · Integridad

```
un solo núcleo, por identidad de objeto      True
cinco huellas idénticas pre/post             True
memory.py byte-idéntico al blob de 705239c   True
semántica de M verificada                    True
C(ψ(x)|x) = 17/20 tras la fusión             True
invariancia a los 12 pares de portadores     0.0e+00
sin el tick, el brazo completo cae a         0.053058   = el suelo de M OFF
```

**El banco reducido no eligió el resultado:** los doce pares de portadores dan el
mismo número, con dispersión exactamente cero. Reducir sin demostrar la
invariancia habría sido elegir el banco después de conocerlo.

Se construyó además el envoltorio congelado del binder --`FrozenBinder`--, que el
Nivel 1.4 no necesitaba porque era quien lo creaba. Es la tercera vez que una
fusión tiene que construir el envoltorio que el nivel de origen no entregó.

**Y los diez gates se evalúan en ejecución desde el primer día**, no después:
en 1.4 el guion informaba siete donde el preregistro sellaba once y hubo que
reconciliar el inventario a posteriori.

## 7 · Qué está permitido afirmar

> Un mismo organismo conservó intactas cinco capacidades adquiridas en ramas
> distintas y las hizo participar en una misma predicción: recordó durante un
> tick qué referencia se le había señalado y usó una correspondencia aprendida
> entre portadores para recuperar la evidencia de proximidad que le pertenecía.

**Obligatorio:** la regla de composición y la operación de localización por token
fueron **suministradas por diseño**. Verificación del conjunto, no descubrimiento
de integración. Cada capacidad se adquirió **en aislamiento de las demás**.

**No autorizado:** atención, búsqueda, memoria relacional, identidad de objeto,
selección de recuerdos, ni organismo unificado en sentido fuerte.

## 8 · Ficheros

```
terrario/remembered/   memory (copia literal) · core · agent · metrics · experiment
scripts/organism_remembered_binding.py
tests/test_remembered_binding.py      22 contratos

suite del linaje 1.0+1.1+1.2+1.4+fusión:  176 contratos verdes
terrario/level1, level11, level12, level14: sin un solo cambio desde 68d852d
```

```bash
cd /home/wis/organism-remembered-binding-01
PY="/home/wis/mundo simulado terrario/.venv/bin/python"
OMP_NUM_THREADS=2 "$PY" -u scripts/organism_remembered_binding.py
OMP_NUM_THREADS=2 "$PY" -m pytest tests/test_remembered_binding.py -q --no-header -p no:cacheprovider
```

## 9 · Lo que queda

La infraestructura para el **Nivel 1.5 · selección bajo capacidad temporal
limitada** está completa. La pregunta abierta sigue siendo la que se adjudicó:
*¿qué aprende a conservar cuando no puede conservarlo todo?*, con `H₁` guardar
dirección, `H₂` guardar proximidad y `H₃` una representación conjunta parcial.

Y hay un dato de este experimento que le concierne: **la memoria actual guarda
un `CueToken` y nada más**. Ampliar su contenido es precisamente la capacidad que
1.5 debe estudiar, no un detalle de implementación.
