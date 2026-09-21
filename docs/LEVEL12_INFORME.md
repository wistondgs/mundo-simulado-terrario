# `LEVEL1.2-QUALITATIVE-DISTANCE-01` · informe

**`LEVEL12_STATUS = VERIFIED`** · los doce gates en las ocho semillas.

Rama `experiment/level1-reversal-plasticity-01` · guion
`scripts/level12_qualitative_distance.py` · oráculo sellado en
`docs/LEVEL12_ORACULO_PREREGISTRADO.md`, commit `3697c5f`, **antes** de existir el
código. Semillas `80000011 … 80000018`, `N = 2048`.

Sin bootstrap y sin intervalos: ocho realizaciones no son una muestra
poblacional, son ocho comprobaciones de que el mecanismo se reproduce.

---

## 1 · Lo nuevo de 1.2 · el techo no es cero

En 1.0 y en 1.1 la respuesta perfecta existía y el organismo la alcanzaba. Aquí
**no existe**: el sensor es ambiguo por construcción y ni el mejor predictor
posible baja de `8/55`.

```
BS*  (Bayes, conoce la matriz de emisión)   0.145455  =  8/55   EXACTO
BS   ignorante (H ≡ ½)                      0.250000  =  1/4    EXACTO
Accuracy*  (clasificador Bayes)             0.800000  =  4/5    EXACTO
```

El `80 %` **no es un defecto**: es el techo que impone el sensor. Por eso la
métrica primaria es probabilística y la exactitud sólo se reporta al lado.

## 2 · Predicción · Brier poblacional

No se puntúa sobre el flujo con el que se entrenó, y no hizo falta un banco: las
marginales están selladas, así que el riesgo se calcula en cerrado. Sin RNG de
evaluación y sin ruido de banco.

```
brazo                 BS_pop    Δ vs BS*   max|Δ_k|   bal.acc         J_N
FULL_12             0.145753   +0.000299     0.0244    0.8000    0.018255
BAYES_ORACLE        0.145455   +0.000000     0.0000    0.8000    0.018215
SENSOR_ONLY         0.145753   +0.000299     0.0244    0.8000    0.326652
SHUFFLED_DISTANCE   0.246048   +0.100593     0.4133    0.5281    0.030785
NO_DISTANCE         0.250000   +0.104545     0.4091    0.5000    0.031273
FROZEN_DISTANCE     0.250000   +0.104545     0.4091    0.5000    0.031273

referencias analíticas:  BS* = 0.145455  ·  ignorante = 0.250000  ·  J_N* = 1/55
peor semilla: BS_pop 0.146614 (tolerancia 0.1480) · max|Δ| 0.0612 (tolerancia 0.10)
```

El exceso medido sobre el techo, `+0.000299`, coincide con el exceso calculado en
cerrado antes de correr, `Σ_s P(s)·MSE_s = 0.000297`.

**Posteriors frente al oráculo sellado:**

```
token    H medido        H*           Δ
S0       0.090203    0.090909   −0.000706
S1       0.338774    0.333333   +0.005441
S2       0.657847    0.666667   −0.008820
S3       0.908123    0.909091   −0.000968
```

## 3 · Los tres empates estaban preregistrados · no son hallazgos

```
NO_DISTANCE = FROZEN_DISTANCE = 0.250000   EXACTO
FULL_12     = SENSOR_ONLY     = 0.145753   EXACTO
```

> **`BS_distance` no prueba integración.** `H` es el único factor que predice
> distancia; `B` y `Q` no entran en la métrica. Un agente sin cuerpo y sin
> orientación empata con el completo hasta el último decimal.

Es exactamente la situación del Nivel 1.1, donde `R_align` empataba entre
`COMPOSITE` y `CUE-ONLY`. Lo que separa aquí es la columna `J_N`:
**`SENSOR_ONLY` da `0.3267` contra `0.0183` del completo**, un factor de 18. Sin
cuerpo, `J_N` promete movimientos imposibles; sin orientación, movimientos
desalineados.

## 4 · Integración · intervención de una sola variable

```
brazo                   varía o                varía g                varía s
                      B      Q      H        B      Q      H        B      Q      H
FULL_12             0.999  0.000  0.000    0.000  0.978  0.000    0.000  0.000  0.818
NO_DISTANCE         0.999  0.000  0.000    0.000  0.978  0.000    0.000  0.000  0.000
SENSOR_ONLY         0.000  0.000  0.000    0.000  0.000  0.000    0.000  0.000  0.818
```

**Los seis ceros cruzados son exactos**, no aproximados. Cada entrada mueve su
factor y sólo el suyo; el brazo sin la adquisición nueva tiene su tercera columna
en cero y el control ciego tiene las dos primeras. Es evidencia por situación, sin
promedios ni intervalos.

## 5 · Integridad

```
linaje 1.1 intacto en las 8                  True
R_align idéntico pre/post                    True   (1.0000, igualdad determinista)
violaciones del contrato físico                 0
cobertura informativa mínima                   40   (criterio ≥ 30)
P(CERCA | g) exacto en las 8                 True
asociación D↔o dentro del envelope nulo      True   (máx 7.96 vs envelope 8.89)
separación sensor↔δ mínima                 0.1437   (criterio ≥ 0.10)
```

`R_align` se mide con el instrumento **cerrado**, no con el muestreado: `act`
rompe empates consumiendo RNG, y en 1.1 muestrear eso ya produjo una
discrepancia falsa contra su propio oráculo.

**El margen del envelope es el más justo de todos:** `7.96` contra `8.89`. Pasa en
las ocho, pero no con holgura. Queda registrado por si alguna vez dispara.

## 6 · La enmienda que hizo falta · `δ → S`, no `D → S`

La versión previa emitía el sensor **desde la etiqueta de clase**. Con eso, toda
la geometría --la referencia, Manhattan, el margen en `δ=3`-- era decorativa: se
podía borrar y el experimento daba exactamente el mismo resultado.

La enmienda condiciona la emisión a `δ`. Promediando `δ` uniformemente dentro de
cada clase, las marginales reproducen **exactamente** las selladas (verificado en
aritmética de fracciones: `1/20, 3/20, 3/10, 1/2`), así que `H*`, `8/55` y `4/5`
sobreviven intactos y el problema del organismo no cambia. Lo que cambia es que
la evidencia sensorial nace de la distancia física.

**Y es una propiedad medida, no una declaración.** El contrato L12-11 exige
`max_k |P̂(s|δ=1) − P̂(s|δ=2)| ≥ 0.10`; el generador aprobado da `0.1437` y el
generador ciego a `δ` --que existe sólo como fixture negativa-- da `0.00`.

## 7 · La geometría no cabía en el mundo · el hallazgo que paró la implementación

El mundo congelado es una rejilla de `7` con el borde cerrado, luego su interior
libre es `5×5`. Medido:

```
δ máximo desde el centro (3,3)        4     ← δ ∈ {5,6} imposible
δ máximo alineado a un eje            4     ← δ ∈ {5,6} imposible
posiciones que alcanzan δ ≥ 6      20/25
```

`LEJOS` estaba definido como `δ ∈ {4,5,6}`. Si la referencia hubiera tenido que
ser una celda, sólo habría existido en la periferia --que es justo donde los bits
de pared valen `1`--, y la clase de distancia habría quedado confundida con la
posición **antes de correr nada**.

La salida adjudicada: la referencia es un desplazamiento relativo abstracto y
axial, que puede caer fuera de la rejilla. El mundo congelado no se toca.

## 8 · Umbrales derivados, no heredados

`max_k|Δ_k| ≤ 0.02` es la tolerancia del Nivel 1.1. Medido sobre `200 000`
réplicas simuladas del generador aprobado:

```
tolerancia   fallo por semilla   fallo en 8 semillas
   0.02           0.66921              0.9999
   0.10           0.00002              0.0001
```

Con `0.02` el gate habría caído en el `99.99 %` de las campañas **aunque el
aprendiz fuera exacto**, porque `H(s)` se estima con ~500 muestras por token y no
con las decenas de miles del 1.1. Heredar un umbral es heredar el tamaño de
muestra que lo justificaba.

Ambos umbrales se sellaron con su cálculo: `0.1480` está a `8.6 ×` el exceso
esperado; `0.10` está a `4.57 σ` del token más ruidoso.

## 9 · Reconciliación del inventario de gates

El preregistro sella doce filas --`L12-0` … `L12-11`--. La primera versión del
guion evaluaba **diez**, y el informe lo decía como «los diez gates
**evaluables**»: una palabra que reconocía la brecha sin cerrarla.

Los dos que faltaban **sí estaban verificados**, en contratos y no en el informe
de ejecución, así que el inventario divergía y el siguiente que leyera habría
heredado dos taxonomías --tres, en realidad: la cabecera del guion decía
«once»--.

| gate | dónde estaba | dónde se verifica ahora |
|---|---|---|
| `L12-1` observabilidad | `tests/test_level12_lineage.py` · la vista no tiene verdad ni geometría, y `predict_near` sólo recibe el sensor | **añadido al guion**, por la forma de los tipos |
| `L12-9` falsabilidad | `tests/test_level12_distance.py` · la fixture de factorización falsa | **añadido al guion**, con la misma fixture |

La fixture falsa estaba **duplicada**: una copia en el fichero de contratos y
ninguna en el guion. Ahora vive en `terrario/level12/stream.py` y las dos la
importan, porque dos definiciones del mismo mundo falso son dos gates con el
mismo número.

**El resultado experimental no cambia**: los doce pasan en las ocho semillas, y
la salida del guion difiere de la anterior en exactamente dos líneas añadidas
--mayor desviación `0.0612`, peor `BS_pop` `0.146614`, separación `0.1437`,
cobertura `40`: idénticos--.

Cada fila añadida trae su mutante, porque un gate que sólo puede pasar no es un
gate: un campo de más en la vista, un parámetro de más en `predict_near`, y el
mundo nominal en lugar del falso hacen caer lo que les toca.

## 10 · Defectos hallados construyendo

**Escribí un contrato que no podía fallar.** `test_reconstruir_verifica_antes_de_
congelar` lanzaba la excepción a mano en vez de ejercitar `reconstruct`: habría
aprobado con la verificación entera borrada. Es la misma familia que el parser de
la suite que registraba la cadena literal `"FAILED"`. Reemplazado por tres casos
que degradan el flujo del Nivel 1.1 en un solo aspecto cada uno --violaciones,
fugas, cobertura-- y exigen que la semilla quede excluida.

**Preregistré `SHUFFLED ≈ 0.2504` sin su dispersión.** Midió `0.246048`, que a
primera vista parece discrepancia. No lo es: simulado, el brazo barajado tiene
media `0.250364` --el número preregistrado era correcto-- y **desviación típica
`0.0071` por semilla**, de modo que una media de ocho a `0.2460` está a `−1.72 σ`.
El defecto no fue el valor sino darlo sin su anchura: una cifra de cuatro
decimales invita a leer como hallazgo lo que es ruido.

**El `SHUFFLED` correcto, y el que no lo es.** El control baraja el sensor contra
la verdad del ensayo. Barajar los registros **enteros** conserva cada pareja
`(s,D)` y no destruye nada --es el defecto exacto del Nivel 1.1, donde el control
empataba con el brazo que controlaba--. Hay contrato para las dos cosas: que
barajar el sensor lleve `H → ½`, y que reordenar registros deje los posteriors
**idénticos hasta `1e-12`**.

## 11 · Qué está permitido afirmar

> El Agente Nivel 1.2 adquirió una distinción probabilística entre dos clases
> cualitativas de proximidad a partir de evidencia sensorial ambigua generada por
> la distancia latente de una referencia externa, conservando intactas sus
> adquisiciones sensorimotoras y direccionales previas.

> El agente acumulativo pudo consultar conjuntamente conocimiento corporal,
> direccional y de proximidad sin modificar los mecanismos adquiridos en niveles
> anteriores.

**No afirmar que «representa distancia».** No conoce coordenadas, ni valor
métrico, ni número de celdas, ni Manhattan, ni el umbral físico. CERCA/LEJOS es
una ontología suministrada por el experimentador.

**Tampoco:** navegación, búsqueda, planificación, acercamiento o alejamiento
deliberado, rutas, memoria espacial, mapa, conducta adaptativa, objetivos,
motivación.

**Y expresamente:** `π_1.2(o,g,s) = π_1.1(o,g)`. La distancia **no** modifica la
acción, y hay contrato que lo comprueba variando `s` sobre las `16 × 4`
situaciones. Que CERCA/LEJOS decidiera qué hacer sería otra adquisición.

## 12 · Ficheros y reproducción

```
terrario/level12/     962 líneas   reference · proximity · inherited · agent ·
                                   stream · metrics · experiment
scripts/level12_qualitative_distance.py
tests/test_level12_lineage.py     14 contratos
tests/test_level12_distance.py    38 contratos

suite completa del linaje: 98 contratos verdes
terrario/level1/ y terrario/level11/: sin un solo cambio desde el sellado
```

```bash
cd /home/wis/causal-bench-01
PY="/home/wis/mundo simulado terrario/.venv/bin/python"
OMP_NUM_THREADS=2 "$PY" -u scripts/level12_qualitative_distance.py
OMP_NUM_THREADS=2 "$PY" -m pytest tests/test_level12_*.py -q --no-header -p no:cacheprovider
```

## 13 · De qué clase es este hito

Como en 1.1, la factorización se la suministramos nosotros: el organismo no
descubrió que cuerpo, dirección y proximidad se combinan multiplicativamente.
Y como en 1.1, los gates positivos estaban determinados por la arquitectura antes
de correr.

Lo genuinamente nuevo es **la incertidumbre irreducible**. Por primera vez el
organismo no puede acertar siempre, y el criterio deja de ser la perfección para
pasar a ser la distancia al mejor conocimiento que su sensor permite. Esa es la
diferencia real entre 1.2 y los dos decimales anteriores.

Las 32 semillas y el bootstrap siguen reservadas para el primer decimal donde
exista una pregunta cuya respuesta no podamos calcular antes de ejecutar el
organismo. **Cambiar la matriz de emisión y preguntar si se recalibra sería el
primer candidato legítimo** --y está explícitamente fuera de 1.2.
