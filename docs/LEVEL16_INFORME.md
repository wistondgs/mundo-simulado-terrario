# `LEVEL1.6-DEVELOPMENTAL-SENSORY-CHANGE-01` · informe

**Fecha:** 2026-09-20 · **Veredicto:** `POSITIVO` · 16/16 vidas · 12/12 gates

Oráculo `9b0d39b`, enmiendas `d0ce9f8` (consumo de semillas), `8f8c85d`
(parámetros del mundo) y `5c54848` (clasificación) — **las tres emitidas antes de
correr**. Campaña lanzada una sola vez, sin relanzar.

---

## 1 · El resultado

```
ΔL vs FROZEN      media +1.5947   sd 0.2639   mín +1.3533    16/16 positivas
ΔL vs SHUFFLED    media +0.8308   sd 0.3067   mín +0.1290    16/16 positivas
IC95 inferior     +0.6805                                    CRITERIO PRIMARIO CUMPLIDO
```

| semilla | clase | FULL | SHUFFLED | K-SOMBRA | disponible | temporal | estrato | celdas |
|---|---|---|---|---|---|---|---|---|
| 140000011 | POSITIVO | 1.4193 | 2.3655 | 1.3829 | 1.3897 | 0.9463 | >6 | 20 |
| 140000012 | POSITIVO | 1.1405 | 2.1612 | 1.1078 | 1.6648 | 1.0207 | >6 | 16 |
| 140000013 | POSITIVO | 1.2041 | 1.9764 | 1.1722 | 1.6003 | 0.7723 | >6 | 24 |
| 140000014 | POSITIVO | 0.7123 | 1.1167 | 0.7011 | 2.0715 | 0.4044 | ≤3 | 3 |
| 140000015 | POSITIVO | 1.2662 | 2.3467 | 1.2336 | 1.5390 | 1.0805 | >6 | 18 |
| 140000016 | POSITIVO | 1.3118 | 2.3082 | 1.2668 | 1.5058 | 0.9964 | >6 | 20 |
| 140000017 | POSITIVO | 1.4119 | 2.0837 | 1.4038 | 1.3688 | 0.6718 | >6 | 21 |
| 140000018 | POSITIVO | 1.3188 | 2.1285 | 1.2856 | 1.4870 | 0.8097 | >6 | 22 |
| 140000019 | POSITIVO | 1.2875 | 2.1520 | 1.2580 | 1.5146 | 0.8645 | >6 | 18 |
| 140000020 | POSITIVO | 0.7311 | 1.0908 | 0.7217 | 2.0509 | 0.3597 | ≤3 | 3 |
| 140000021 | POSITIVO | 1.3929 | 2.4237 | 1.3567 | 1.4159 | 1.0308 | >6 | 20 |
| 140000022 | POSITIVO | 1.2535 | 2.5314 | 1.2120 | 1.5606 | 1.2778 | >6 | 18 |
| 140000023 | POSITIVO | 1.2372 | 2.3330 | 1.1971 | 1.5755 | 1.0958 | >6 | 17 |
| 140000024 | POSITIVO | 1.2925 | 2.1075 | 1.2616 | 1.5110 | 0.8150 | >6 | 13 |
| 140000025 | POSITIVO | 0.5675 | 0.6965 | 0.5607 | 2.2119 | 0.1290 | ≤3 | 2 |
| 140000026 | POSITIVO | 1.2993 | 2.3174 | 1.2645 | 1.5081 | 1.0181 | >6 | 18 |

Semillas consumidas `140000011…140000026`. **Descartes `N-MUNDO`: ninguno.**
Sin consumir: 16, que quedan sin usar.

## 2 · Lo cerca que llega del techo

`K-SOMBRA` no estima: resuelve `P(o'|o)` exacta desde la topología. Es el suelo
de pérdida alcanzable en cada mundo.

```
brecha media con el óptimo analítico     0.0288 nats   ·   máxima 0.0450
fracción de lo disponible capturada      0.9813
```

Tras 4 096 pasos de vida uniforme, el contador está a un 2 % del cálculo exacto.

## 3 · El hallazgo: dónde es más difícil el contraste

Los tres mundos de componente pequeño son los que **más** tenían que enseñar y
los que **menos** ventaja temporal producen.

```
semilla     celdas   disponible   ganado   temporal
140000014        3       2.0715   2.0603     0.4044
140000020        3       2.0509   2.0415     0.3597
140000025        2       2.2119   2.2050     0.1290

correlación tamaño de componente vs ventaja temporal    +0.7520
```

La razón es estructural, no anecdótica: en un bolsillo de dos o tres celdas la
secuencia sensorial es casi determinista, así que la ganancia sobre el prior es
enorme —hasta 2.2 nats— pero la **marginal** ya está tan concentrada que barajar
apenas destruye nada. El control se vuelve casi tan bueno como el ser.

### 3.1 · Y por eso tu corrección del criterio importó

Mi propuesta original excluía los componentes de ≤6 celdas. Contrafactual exacto
sobre esta misma campaña:

| criterio | n | media | sd | mín | IC95 inferior |
|---|---|---|---|---|---|
| **estructural (tu adjudicación)** | 16 | +0.8308 | 0.3067 | +0.1290 | **+0.6805** |
| mi exclusión «≤6» | 13 | +0.9538 | 0.1628 | +0.6718 | +0.8653 |

El valor sellado en §11 predecía `+0.8858` — que es, dentro del error, lo que da
**mi exclusión**, no el criterio estructural. Es decir: los números del oráculo se
habían medido sobre una muestra que ya descartaba los mundos pequeños.

Tu criterio metió tres vidas que hacen el contraste sensiblemente más difícil,
bajó el intervalo de +0.87 a +0.68 — y el nivel pasa igual. La afirmación es más
fuerte de lo que habría sido con mi versión, precisamente porque incluye los casos
adversos en vez de seleccionarlos fuera.

## 4 · La métrica secundaria hace exactamente lo que §7 temía

```
BS_change     FULL 0.212128   ·   STATIC-BITCOUNT 0.219067   ·   Δ -0.006938
              beta medio 0.8798          (sellado §7: 0.8363)
              el control gana en 3 de 16 vidas
```

Una regla estática de **un solo parámetro** que sólo mira la observación actual
queda a siete milésimas de la tabla aprendida, y la supera en tres vidas. Si el
endpoint primario fuese `BS_change`, este nivel no habría demostrado nada
temporal. Por eso es secundaria, y por eso `STATIC-BITCOUNT` no tiene distribución
que ofrecer al primario: pedírsela levanta `PrimaryMetricNotApplicable`.

## 5 · Diagnóstico exploratorio · nunca gate

```
banco de su propio mundo     1.1779
banco poblacional            2.7241        ← apenas mejor que FROZEN
FROZEN                       2.7726
```

Confirma §8 en la dirección esperada: contra transiciones de otros mundos el ser
casi no sabe nada, porque 1.6 no declara generalización entre mundos. Es un
diagnóstico y no participa de ningún criterio; un test verifica que el módulo de
gates ni siquiera lo nombra.

## 6 · Gates

```
L16-0   PASS  level11, level12, level13, level14, organism, remembered ausentes del árbol
L16-1   PASS  único emisor de actos: motor.py · 6144 emitidos de 6144 pasos
L16-2   PASS  32 actos reproducidos desde una foto {emitted, rng}
L16-3   PASS  ninguna señal de target, recompensa, novedad o valor en el paquete
L16-4   PASS  identificadores prohibidos en A1: ninguno · aduana en ejecución: sí
L16-5   PASS  el cuerpo no importa la tabla · hash de trayectoria 434c05dc9ad062cc
L16-6   PASS  1.3897 nats disponibles sobre el prior
L16-7   PASS  16/16 vidas mejoran · media +1.5947 nats
L16-8   PASS  IC95 inferior +0.6805 · 16/16 positivas
L16-9   PASS  16/16 pierden la competencia al ablacionar y la recuperan al restaurar
L16-10  PASS  tres pasadas de evaluación sin mover huella ni actualizaciones
L16-11  PASS  el control no predice P(o'|o) y pedírselo levanta
```

Cada uno tiene al menos una fixture negativa que lo hace fallar **por la vía real
del verificador**. 84 contratos en verde antes de lanzar la campaña.

Una salvedad honesta sobre `L16-0`: la segunda rama del predicado `N-MUNDO`
(«ninguna transición alcanzable cambia») está **implicada** por la primera sobre
un componente conexo, y por tanto no admite fixture negativa propia. Queda escrita
con la demostración junto al código.

## 7 · Afirmación máxima autorizada

> El Agente Nivel 1.6 produjo endógenamente su propia trayectoria motora y, a
> partir de las observaciones consecutivas generadas durante esa vida, adquirió un
> modelo temporal de su flujo sensorial que predice mejor sus transformaciones
> futuras, dentro de su propio mundo, que su estado inicial, que un organismo
> congelado y que un control con la temporalidad destruida. El aprendizaje reside
> causalmente en su estado interno y no recibió identidad de acción, recompensa,
> valor, novedad ni etiqueta de cambio.

Y nada más. **No** se afirma detección de cambio —la §4 lo separa: el 12 % de los
movimientos no cambia la observación—, ni contingencia propia, ni causalidad, ni
exploración, curiosidad, motivación, valor, búsqueda, objetivo o agencia fuerte.

## 8 · El libro de suministro, cerrado

```
SUMINISTRADO   cuerpo · S0 con su PRNG · copia eferente bloqueada · tabla 16x16
               prior alpha_0 = 1 · regla de actualización · física del Nivel 1.0
               instrumentación · verdad de terreno · K-SOMBRA · los cuatro controles

ADQUIRIDO      P(o_{t+1} | o_t)
```

## 9 · Reproducción

```
árbol      /home/wis/level16-sensory-change-01
rama       experiment/level16-developmental-sensory-change-01
base       d278f59   (cierre del Nivel 1.0; sin level11…level14 en el disco)
mundo      grid_size 7 · wall_probability 0.25   heredados del 1.0 canónico
prior      alpha_0 = 1.0
vida       T = 4096 · POST = 2048 · 16 vidas
flujos     mundo [s,0] · motor [s,1] · baraja [s,2]
```
