# `ORGANISM-FUSION-HM-01` · informe

**`FUSION_STATUS = VERIFIED`** · los nueve gates en las ocho semillas.

Base `7ac43fb`, árbol propio. Preregistro sellado en `4028790` **antes** de
existir el código. Semillas `110000011 … 110000018`.

---

## 1 · Qué es esto · dicho antes de los números

**No es un decimal y no adquiere nada.** No hay parámetro que se aprenda aquí, no
hay `N_TRAIN`, no hay dosis. El Nivel 1.4 conserva su adquisición --binding
conjuntivo-- y queda congelado en `3bdf6fb`, con su árbol sin tocar.

Es un artefacto de composición, y responde una pregunta que estaba abierta desde
que cerramos 1.3: `1.2 = B+Q+H` y `1.3 = B+Q+M` son **hermanos**, los dos forkean
de 1.1, y **no existía ninguna instancia con las cuatro**. La acumulación había
ocurrido dentro de cada rama y nunca entre ellas.

## 2 · El factorial · lo que sí demuestra uso conjunto

Una suite conjunta sólo demostraría que las piezas caben en el mismo árbol. Lo
que demuestra que **ambas participan en el mismo cálculo** es esto:

```
    H     M      medido   ref H propia    sellado   Δ vs sellado
   ON    ON    0.018252       0.018216   0.018182     +0.000070
  OFF    ON    0.031274       0.031250   0.031250     +0.000024
   ON   OFF    0.051429       0.051429   0.051420     +0.000008
  OFF   OFF    0.054688       0.054688   0.054688     +0.000000
```

Los cuatro valores son distintos, están en el orden sellado, y ninguno se aparta
más de `7·10⁻⁵` de la tabla preregistrada. La columna del medio usa cuerpo y
orientación ideales con la `H` del propio organismo: separa el error de `B` y `Q`
del error de `H`.

Cuando una capacidad se apaga, su factor toma **su prior ignorante** y no una
constante inventada: sin proximidad, `P(CERCA) = ½` --el `NO_DISTANCE` sellado de
1.2--; sin cue recordado, `P(alineada) = ¼`, una dirección entre cuatro.

## 3 · La interacción · el contenido del experimento

```
mejora sólo H                0.003259
mejora sólo M                0.023414
suma de las dos              0.026672
mejora conjunta              0.036436

INTERACCIÓN                  0.009764     (sellada 69/7040 = 0.009801)
razón conjunta / suma            1.366
```

**La mejora conjunta es mayor que la suma de las mejoras por separado.**

Es calculable de antemano, y por eso es **verificación y no descubrimiento**.
Pero es una cantidad que **ninguna rama por sí sola podía escribir**: hace falta
que las dos capacidades existan en el mismo organismo para poder definirla. Ésa
es exactamente la diferencia entre ejecutar las suites juntas y este factorial.

## 4 · Integridad

```
un solo núcleo, por identidad de objeto      True
huellas B/Q/H idénticas pre/post             True
semántica de M verificada                    True
R_align idéntico pre/post                    True   (1.0000)
I(G ; o_query)                               0.0000 bits
sin el tick, el brazo completo cae a       0.051429   = el brazo sin memoria
```

**«Un solo núcleo» se comprueba por identidad de objeto**, no por huellas
iguales: reconstruir dos veces la misma semilla da huellas idénticas y objetos
distintos, y eso seguirían siendo dos cuerpos. Hay fixture negativa que lo
demuestra.

**Se reunieron procedimientos, no artefactos.** La `H` del Nivel 1.2 se adquirió
sobre el flujo de la semilla `80000011` y la `M` del 1.3 se probó sobre el núcleo
de `90000011`: traer los objetos habría escondido dos cuerpos y dos orientaciones
dentro de lo que dice ser una fusión. Una semilla, un núcleo, `H` readquirida
sobre el flujo de esa misma semilla.

**`M` entró por copia literal**, verificada byte a byte contra el blob congelado
`705239c:terrario/level13/memory.py`, que los árboles comparten en la base de
objetos. Es el idioma que ya usa este repositorio --`level11/world.py` es copia
literal de `level1/world.py`-- y no hizo falta ningún merge.

**Y la semántica de 1.3 sobrevivió a la fusión intacta:** omitir el tick deja
`peek` en nada, el factor direccional vuelve a su prior, y el brazo completo cae
**exactamente** sobre el brazo sin memoria, hasta `1e-12`.

## 5 · El envoltorio que faltaba

Cada nivel de este linaje ha congelado lo que heredaba y ha dejado mutable lo que
añadía: 1.1 congeló `B`, 1.2 congeló `Q`, 1.3 volvió a congelar `Q`, y **nadie
había construido nunca el envoltorio de `H`** --`QualitativeDistanceModel.observe`
existe y `Level12Agent` publica `self.proximity`--. La fusión lo construyó:
`FrozenProximity`, con su fixture negativa.

De aquí en adelante, el nivel que **añade** un modelo entrega también su
envoltorio congelado.

## 6 · Qué no se encontró

**Ningún defecto de integración.** Los dos caminos no comparten estado, ninguna
fase de adquisición mueve la huella de la otra, el `reset` de la memoria no pasa
por encima de nada de proximidad, y las campañas de 1.1 y 1.2 dan sobre esta base
**los mismos números** que en sus ramas originales.

Era exactamente el riesgo que se estaba probando, y salió limpio a la primera. Es
un resultado sin épica, y conviene reportarlo como tal.

## 7 · Qué está permitido afirmar

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
demás**, y reunirlas después no cambia eso.

## 8 · El libro mayor, con sus tres clases

```
B · Q · H     parámetros aprendidos, cada uno EN AISLAMIENTO de los otros
M             mecanismo suministrado, cero parámetros
composición   suministrada, nunca aprendida, y sostiene todos los resultados
```

Decir «el organismo tiene cuatro capacidades» tapa la tercera fila.

## 9 · Ficheros y reproducción

```
terrario/organism/   memory (copia literal) · core · agent · metrics · experiment
scripts/organism_fusion_hm.py
tests/test_organism_fusion.py        26 contratos

suite conjunta 1.0 + 1.1 + 1.2 + fusión:   124 contratos verdes
LEVEL11_STATUS = VERIFIED · LEVEL12_STATUS = VERIFIED sobre esta misma base
terrario/level1, level11, level12: sin un solo cambio desde 7ac43fb
```

```bash
cd /home/wis/organism-fusion-hm-01
PY="/home/wis/mundo simulado terrario/.venv/bin/python"
OMP_NUM_THREADS=2 "$PY" -u scripts/organism_fusion_hm.py
OMP_NUM_THREADS=2 "$PY" -m pytest tests/ -q --no-header -p no:cacheprovider
```

## 10 · Lo que queda

El orden adjudicado deja dos cosas después de esto:

1. **Nivel 1.4 · binding conjuntivo**, ya preregistrado y corregido en `3bdf6fb`.
2. **Restricción de memoria / selección**, si se autoriza — y ésa sí sería una
   adquisición nueva, con una pregunta genuinamente abierta: qué aprende a
   conservar cuando no cabe todo.
