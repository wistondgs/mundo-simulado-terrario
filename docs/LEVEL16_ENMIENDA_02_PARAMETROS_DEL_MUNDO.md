# Enmienda 02 al oráculo de `LEVEL1.6` · parámetros del mundo y del prior

**Fecha:** 2026-09-20
**Oráculo enmendado:** `9b0d39b` · §4, §6, §12
**Estado en que se emite:** antes del primer commit de implementación · ningún resultado confirmatorio visto
**Motivo:** el oráculo mide un mundo cuyos parámetros no escribe, y declara un prior sin valor.

Aditiva. El oráculo no se edita.

---

## 1 · Lo que faltaba

§4 dice «Física sensorimotora elemental del Nivel 1.0: rejilla de 7, cuatro
movimientos, **paredes**, cuatro bits». Dice *paredes*; no dice cuántas. §6 dice
«prior `N₀(o,o') = α₀` simétrico»; no dice cuánto vale `α₀`. Con esos dos huecos, §4
y §12 no son reproducibles y la implementación tendría dos grados de libertad.

## 2 · Los parámetros no se eligen: se heredan

```
grid_size          = 7      terrario/level1/measurement.py:52
wall_probability   = 0.25   terrario/level1/measurement.py:55 · reversal.py:259
```

Es el mundo canónico del Nivel 1.0, ya escrito en el árbol base. §4 dijo que hereda
esa física; esta enmienda sólo lo hace explícito. Ningún valor se ajustó para que
cuadraran los números: se leyó el código del 1.0.

```
α₀ = 1.0     prior uniforme · N₀(o,o') = 1 en las 256 celdas
```

Verificado analíticamente, no por ajuste: con `α₀ = 1` el brazo FROZEN predice
uniforme y su log-loss es exactamente `log 16 = 2.7726`, que es el valor que §8 ya
tenía sellado. Medido: `2.7726` en las 16 vidas, a densidad 0.24 y 0.26 por igual.

## 3 · Reproducción de lo sellado a esos parámetros

20 réplicas independientes de 200 mundos × 4096 pasos; 20 000 mundos para §12.

| §4 | medido | sellado | z |
|---|---|---|---|
| tasa de movimiento | 0.5923 ± 0.0087 | 0.5818 | −1.22 |
| tasa de cambio | 0.5155 ± 0.0065 | 0.5129 | −0.40 |
| movió sin cambiar | 0.1297 ± 0.0060 | 0.1184 | −1.87 |
| `I(o;o')` | 0.8861 ± 0.0358 nats | 0.8957 | +0.27 |
| transiciones distintas | 182 – 184 | 182 | ✓ |

| §12 | medido (n=20000) | sellado (n=5000) |
|---|---|---|
| estratos ≤3 / 4–6 / >6 | 0.0223 / 0.0292 / **0.9485** | 0.023 / 0.028 / **0.949** |
| `N-MUNDO` | **0.0213 ± 0.0020** | 0.0192 |

Los estratos coinciden a tres decimales: es la firma que identifica la densidad sin
ambigüedad. `N-MUNDO` sellado en 0.0192 era un estimador de 5 000 mundos, cuyo error
típico es 0.0019; contra el valor de 20 000 mundos queda a 1.1 σ. **Se refina, no se
corrige:** `N-MUNDO = 0.0213`.

## 4 · La unidad de dispersión es el mundo, no el paso

Advertencia que se incorpora al oráculo porque ya me indujo a error una vez: las
observaciones dentro de una vida están fuertemente correlacionadas, así que el `n`
efectivo de §4 es el **número de mundos** (~200–400), no los 1 638 400 pasos.

```
sd de `mov` entre réplicas de 200 mundos     0.0087
sd que sugeriría el conteo de pasos          0.0004        ← falsa por factor 20
```

**Ningún gate puede exigir de §4 más precisión de la que §4 tiene.** Los valores de §4
y §12 son descriptores de viabilidad del mundo; no son umbrales y no aparecen en
ningún criterio de decisión.

## 5 · Efecto sobre la Enmienda 01

Con `N-MUNDO = 0.0213` en lugar de 0.0192:

```
E[descartes entre 32]              0.682
P(al menos un descarte)            0.4979
P(32 no bastan para 16 válidas)    1.6 · 10⁻²⁰
```

La regla de consumo no cambia. `SEED_POOL_EXHAUSTED` sigue siendo detector de
defecto y no riesgo estadístico. Verificado además: ninguna de las 32 semillas
reservadas es `N-MUNDO` a estos parámetros, luego la campaña consumirá
`140000011…140000026` salvo que el predicado diga otra cosa al correrlo.

## 6 · Alcance

Fija parámetros y refina un descriptor. **No** toca el endpoint primario, los brazos,
los gates, la taxonomía, la prueba causal ni la afirmación máxima autorizada. El
criterio primario —`IC95_inferior(ΔL vs SHUFFLED) > 0`— no depende de ningún valor
aquí tocado.
