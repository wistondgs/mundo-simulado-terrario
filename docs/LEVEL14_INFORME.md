# `LEVEL1.4-CONJUNCTIVE-BINDING-01` · informe

**`LEVEL14_STATUS = VERIFIED`** · los siete gates en las ocho líneas base.

Base `7ac43fb`, árbol propio, sin `terrario/level13/` en disco. Oráculo sellado en
`3bdf6fb` **antes** de existir el código; auditoría previa en `4d…` del mismo
árbol. Semillas `100000011 … 100000018`.

---

## 1 · Qué permite probar que ningún nivel podía probar

1.0 variaba `o`, 1.1 variaba `g`, 1.2 variaba `s`, 1.3 variaba la historia. Los
cuatro miden la respuesta a un **atributo**.

> Éste es el primer experimento del linaje en el que los atributos presentes son
> **idénticos** entre condiciones y sólo cambia la **relación** entre ellos.

Los conjuntos marginales `{g₁,g₂}` y `{s₁,s₂}` son los mismos en las dos
condiciones; lo único que difiere es qué va con qué. Es la prueba correcta de
binding, y antes no se podía formular.

## 2 · Binding

```
brazo               BS_binding   Δ vs sellado   readout MSE  ref H propia
FULL_14            0.000011891      -7.18e-19      0.000003      0.000003
ORACLE             0.000000000      +0.00e+00      0.000000      0.000000
SHUFFLED           0.250000000      +0.00e+00      0.064477      0.064477
UNBOUND            0.250000000      +0.00e+00      0.064477      0.064477
FROZEN_BINDER      0.250000000      +0.00e+00      0.064477      0.064477
SINGLE_G           0.250000000      +0.00e+00      0.064477      0.064477
SINGLE_D           0.250000000      +0.00e+00      0.064477      0.064477
```

`FULL_14` reproduce `1/84100` con una desviación de `7·10⁻¹⁹` --ruido de coma
flotante--, y los cinco brazos sin canal caen **exactamente** en `0.25`. El
`ORACLE` da cero exacto.

La columna de referencia usa la `H` del propio organismo, no la `H*` sellada,
para no confundir calidad de 1.2 con calidad de 1.4. Coincide con lo medido hasta
el último decimal mostrado.

**El barajado construye la independencia, no la muestrea.** Cada `x` con cada `y`
exactamente cuatro veces da `A_xy = 5` en las dieciséis celdas y `C(y|x) = 1/4`
exacto: **varianza cero**, a diferencia del barajado de 1.1 y 1.2, que permutaba
un flujo muestreado. Y hay contrato que comprueba lo contrario: barajar los
registros **enteros** conserva toda la relación y deja el resultado en
`1/84100`, que es el defecto exacto del control de 1.1.

## 3 · La sonda · el discriminador

```
se varía             Q         H         C     readout
g               0.9712    0.0000    0.0000      0.0000
s               0.0000    0.5830    0.0000      0.0020
binding         0.0000    0.0000    0.0000      0.2212
```

**Sólo la intervención en el binding mueve el readout sin mover un solo factor.**
`Q`, `H` y `C` quedan en cero exacto: los atributos presentes son los mismos y los
portadores no cambian; lo único que cambia es la relación.

Cada factor se mide de forma invariante a la permutación de portadores --suma
sobre los elementos de la escena--, porque medirlo en una posición concreta
habría hecho que intervenir en el binding moviera `H` de rebote.

## 4 · Exclusión de atajos e identidad

```
emparejar por índice (banco ordenado)   0.5000     criterio 0.5
I(G;X), I(S;Y) en adquisición           (0.0, 0.0)
I(G;X), I(S;Y) en evaluación            (0.0, 0.0)
una sola referencia · BS de UNBOUND     0.0000     → no certifica binding
huellas B/Q/H idénticas pre/post        True
```

Con una sola referencia hasta el brazo ciego acierta siempre: el gate se **niega
a certificar**, que es lo correcto.

## 5 · Qué compraron las seis correcciones de la auditoría

| corrección | qué habría pasado sin ella |
|---|---|
| **C1** banco de evaluación enumerado con paridad `A`/`B` | emparejar por índice habría dado `1.0` y la métrica no lo habría distinguido de un binder de verdad |
| **C1** balance en los **dos** bancos | `ATTRIBUTE_IDENTITY_LEAK` entrando por donde el gate no miraba |
| **C2** `FrozenProximity` | `core.proximity.observe(...)` al alcance de un descuido |
| **C3** las 24 permutaciones a la suite | 192 celdas presentadas como 192 comprobaciones, sobreestimando por 24 |
| **C4** escena ordenada para la fixture | el gate de orden no podía fallar: con `frozenset` la invariancia es cierta por construcción |
| **C5** contrato de cardinalidad | una escena de dos elementos idénticos tendría **una** referencia en silencio |
| **C6** simetría `A`/`B` sellada | `BS_binding` sería un error condicionado, no un Brier |

**Medido:** las 24 permutaciones de `ψ` dan el mismo valor, y ahora son 24
contratos parametrizados en vez de 24 celdas de campaña.

## 6 · Defectos hallados construyendo

**Escribí una aserción vacua.** `assert sin_asignar == sin_asignar` en el contrato
de `BINDING_NOT_NECESSARY`: compara una lista consigo misma y no puede fallar.
Reparado por uno que toma la escena y su gemela con el binding intercambiado, y
exige que el readout **con** asignación las separe y el readout **sin** asignación
no.

Es la cuarta vez en este linaje que el fallo aparece en el código de
verificación: el parser que registraba la cadena `"FAILED"`, tres guardas que
cazaban su propia documentación, el contrato de 1.3 que lanzaba su excepción a
mano, las dos guardas de texto de 1.3, y ahora ésta. **La concentración no es
casual: una aserción equivocada sigue pasando**, mientras que un modelo
equivocado da un número raro. El código que verifica necesita el mismo escrutinio
que el que calcula, y por eso cada gate lleva su negativo.

**Y una sonda mal medida.** La primera versión del probe de tres factores medía
`H` en una posición concreta, así que intercambiar el binding la movía de rebote
y conflacionaba las dos intervenciones. Reparada midiendo cada factor de forma
invariante a la permutación.

## 7 · Qué está permitido afirmar

> El Agente Nivel 1.4 adquirió una correspondencia conjuntiva que le permitió
> vincular una señal direccional y una evidencia de proximidad cualitativa como
> pertenecientes a la misma referencia momentánea, distinguiendo configuraciones
> con atributos marginales idénticos pero asociaciones diferentes, sin modificar
> sus adquisiciones sensorimotoras, direccionales ni de proximidad anteriores.

**Obligatorio junto a ella:**

> El mecanismo de binding y los portadores transitorios fueron suministrados por
> diseño. El experimento no demuestra identidad persistente de objetos ni que el
> agente inventara autónomamente un mecanismo general de binding.

**No autorizado:** objeto, identidad de objeto, entidad persistente, permanencia
del objeto, representación de escena general, atención, memoria relacional,
razonamiento relacional, navegación, selección de objetivos, concepto general de
«la misma cosa». Lo certificado es estrictamente **co-pertenencia conjuntiva
momentánea**.

## 8 · De qué tamaño y de qué clase

La adquisición son `log₂(4!) = 4.585` bits: el contenido de `ψ`, no el concepto
de binding. Y hay un límite que conviene repetir: **una vez conocida `ψ`, el
binding es consulta de tabla, no inferencia.** Dos elementos, dos asignaciones,
un argmax sobre dos productos — binding en su tamaño mínimo no degenerado.

Los positivos eran calculables antes de correr, y eso no los vacía: los convierte
en **verificación** de que la implementación realiza el algoritmo especificado.
Lo genuinamente nuevo sigue siendo lo del §1.

Lo que persiste entre ensayos es la ligadura `x ↔ ψ(x)` --un canal--, no la
ligadura a un referente. Dos frecuencias de radio que se sabe que llevan la misma
emisión: saber cuáles se emparejan no dice nada de qué se emite.

## 9 · Ficheros y reproducción

```
terrario/level14/    carriers · scene · binding · inherited · agent · metrics · experiment
scripts/level14_conjunctive_binding.py
tests/test_level14_lineage.py     10 contratos
tests/test_level14_binding.py     46 contratos (24 de ellos parametrizados sobre ψ)

suite conjunta 1.0 + 1.1 + 1.2 + 1.4:   154 contratos verdes
terrario/level1, level11, level12: sin un solo cambio desde 7ac43fb
```

```bash
cd /home/wis/level14-binding-01
PY="/home/wis/mundo simulado terrario/.venv/bin/python"
OMP_NUM_THREADS=2 "$PY" -u scripts/level14_conjunctive_binding.py
OMP_NUM_THREADS=2 "$PY" -m pytest tests/test_level14_*.py -q --no-header -p no:cacheprovider
```
