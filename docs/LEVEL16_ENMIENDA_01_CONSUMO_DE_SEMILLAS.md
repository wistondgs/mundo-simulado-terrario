# Enmienda 01 al oráculo de `LEVEL1.6` · consumo del intervalo de semillas

**Fecha:** 2026-09-20
**Oráculo enmendado:** `9b0d39b` · `docs/LEVEL16_ORACULO_PREREGISTRADO.md` §12 y §16
**Estado en que se emite:** antes del primer commit de implementación · cero código escrito
**Motivo:** el oráculo invoca una «regla preregistrada» de reemplazo que no preregistró.

El oráculo **no se edita**. Esta enmienda es aditiva y se lee junto a él.

---

## 1 · El hueco, literal

§12 dice:

> Las semillas `N-MUNDO` se reemplazan por regla preregistrada y se contabilizan y
> publican igualmente.

§16 dice:

```
140000011 … 140000042     32 reservadas · 16 vidas válidas + margen de N-MUNDO
```

Entre las dos falta lo único que importa: **cómo** se recorre el intervalo, **cuándo**
se decide que una semilla no sirve, y **qué no puede** provocar un reemplazo. Sin eso,
32 reservadas para 16 vidas es un grado de libertad de 16 semillas que se resolvería
mirando resultados. Se cierra aquí.

## 2 · Regla de consumo

```
k ← 0                                   vidas válidas acumuladas
para s = 140000011, 140000012, …, 140000042   ascendente, sin saltos:
        construir el mundo de s
        evaluar el predicado N-MUNDO sobre el mundo        ← ANTES de vivir
        si N-MUNDO:  registrar, publicar, NO correr la vida, siguiente s
        si no:       k ← k+1 · esta semilla es la vida k · correr
        si k = 16:   PARAR
```

Las semillas no consumidas quedan **sin usar y reservadas**. No se recurre a ellas
para nada: ni para sustituir un resultado incómodo, ni para «confirmar», ni para
ampliar potencia después de ver la campaña.

## 3 · El predicado se evalúa sobre el mundo, no sobre la vida

```
N-MUNDO  ⟺  |O_alcanzables| < 2   ó   no existe transición alcanzable con o' ≠ o
```

Es función exclusiva de la topología de la rejilla y la posición natal. **No requiere
que el organismo exista**, no consume pasos y no mira observaciones producidas. Se
calcula por análisis del grafo de celdas alcanzables desde la natal.

De ahí sale la propiedad que hace la regla no-rescatable: el veredicto de una semilla
está determinado antes de que haya nada que rescatar.

## 4 · Qué NO provoca reemplazo · la mitad que evita la trampa

```
N-EXPERIENCIA       permanece entre las 16 · cuenta en el denominador
N-PLASTICIDAD       permanece entre las 16 · cuenta en el denominador
NEGATIVO VERDADERO  permanece entre las 16 · cuenta en el denominador
POSITIVO            permanece entre las 16 · cuenta en el denominador
```

Las cuatro son categorías **posteriores a la vida**. Reemplazar cualquiera de ellas
sería seleccionar vidas favorables, que es exactamente lo que el criterio estructural
de §12 existía para impedir. Una vida que vivió es una vida que cuenta.

`INVÁLIDO` no es categoría de semilla: es un defecto de cableado, fuga o pasividad.
Invalida **la campaña entera**, nunca una vida suelta. No se sustituye la semilla: se
repara el código y se vuelve a correr todo desde `140000011`.

## 5 · Derivación de flujos · sin esto, la regla no es determinista

Evaluar el predicado no puede alterar la vida que la semilla produciría. Se sella la
cuarentena de flujos, con la misma forma que el resto del linaje:

```
mundo y posición natal      default_rng([s, 0])
fuente motora S0            default_rng([s, 1])
continuación POST           continúa el MISMO estado de S0 tras el freeze
barajado TEMPORAL-SHUFFLED  default_rng([s, 2])       nunca toca la trayectoria
```

Corolario exigible: la trayectoria `a_{0:T}`, `o_{0:T}` de la semilla `s` es idéntica
se haya evaluado el predicado o no, y su hash lo demuestra.

## 6 · Publicación obligatoria

Se publica **toda** semilla tocada, en orden ascendente, incluidas las descartadas:

```
semilla · veredicto · |O_alcanzables| · transiciones alcanzables
        · tamaño del componente natal · estrato · (si vivió) clasificación final
```

El informe declara además `semillas consumidas` y `semillas no consumidas`, de forma
que el recorrido del intervalo sea reconstruible sin acceso al código.

## 7 · Condición de parada nueva

```
SEED_POOL_EXHAUSTED   32 semillas consumidas sin alcanzar 16 vidas válidas
```

No se amplía el intervalo sobre la marcha. Ampliarlo exige otra enmienda fechada,
emitida **antes** de mirar resultado alguno.

Con la tasa medida `p(N-MUNDO) = 0.0192`:

```
E[N-MUNDO entre 32]                      0.614
P(al menos una descartada)               0.4623     ← lo normal es descartar alguna
P(32 no bastan para 16 válidas)          2.8 · 10⁻²¹
```

Es decir: si `SEED_POOL_EXHAUSTED` llega a dispararse, **no es mala suerte, es un
defecto** — el predicado o el generador de mundos no se comportan como se midió. La
condición de parada funciona aquí como detector de error, no como riesgo estadístico.

## 8 · Alcance

Esta enmienda fija procedimiento de muestreo. **No** toca el endpoint primario, los
brazos, los umbrales, los gates, la taxonomía ni la afirmación máxima autorizada.
Nada de lo sellado en `9b0d39b` cambia de valor.
