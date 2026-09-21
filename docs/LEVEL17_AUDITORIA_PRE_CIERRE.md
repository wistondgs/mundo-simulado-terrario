# 1.7 · tres auditorías antes del cierre · sin narrativa

**Fecha:** 2026-09-20 · HEAD de lanzamiento `13223f1` · **no se ha tocado código**
Datos crudos: `resultados/confirmatorio_16_pares.json`

---

# 1 · La nula de B · 32 contra 48 · **DESVIACIÓN REAL**

Leído de la ruta ejecutada, no de memoria.

### ¿Cuántas permutaciones usa `L17-8` en `13223f1`?

**Ninguna propia.** `gate_null_world(report, observed, null_samples)` **recibe** la
nula; no la genera. El número depende enteramente de quién lo llame.

### ¿Qué dice literalmente `ac12cc3`?

```
línea 177   32 permutaciones estratificadas de la vida de B → distribución nula de D_C^B
línea 219   nula        32 permutaciones estratificadas independientes
```

«de **la** vida de B», en singular: **32 por vida**.

### ¿De dónde salió el 48?

Del script ad-hoc con el que calculé el agregado:

```python
for p in P[:6]:            # 6 vidas de B
    for k in range(1, 9):  # 8 permutaciones cada una
6 × 8 = 48
```

### ¿Ese 48 decidió un PASS/FAIL?

**Sí.** Esa lista de 48 se pasó como `null_samples` a `gate_null_world`, produjo la
tolerancia `+0.0035`, y de ahí salió el PASS de `L17-8`.

### Clasificación de la desviación

```
D-1   8 permutaciones por vida donde el oráculo selló 32
D-2   agrupadas entre vidas en vez de una nula POR vida
D-3   sólo 6 de las 16 vidas contribuyeron a la nula
D-4   campaign.py NO llama a gate_null_world en ninguna parte
```

**`D-4` es la de fondo y la peor:** el runner confirmatorio **no evalúa `L17-8`**.
`campaign.py` define `NULL_REPLICAS = 32`, pero lo usa sólo para
`shuffled.audit`, que es la destructividad de `L17-9`. De los trece gates, uno se
evaluó **fuera de la ruta congelada**, en un script escrito después de abrir las
semillas.

No está corregido. No se ha vuelto a correr nada.

---

# 2 · Método del intervalo · **AMBIGÜEDAD DEL ORÁCULO, no violación**

Lo único que `ac12cc3` selló:

```
línea 159   GATE PRIMARIO   CI95_inferior( media de Γ sobre 16 pares )  >  0
línea 160                   intervalo pareado por mundo
```

Fija la **unidad** (el par) y no fija el **método**. Lo que el gate ejecuta es
`gates.py:440`:

```python
inferior = valores.mean() - 1.96 * valores.std(ddof=1) / np.sqrt(n)
```

es decir, normal bilateral. Sobre los mismos 16 pares:

| método | inferior |
|---|---|
| normal `z = 1.96` — **el ejecutado** | **+0.255425** |
| Student `t(15) = 2.13145` | +0.253325 |
| bootstrap percentil 2.5 (20 000) | +0.256166 |
| prueba de signo 16/16 | `p = 3.05e-05` |

La conclusión no cambia con ninguno. Queda documentado que **el oráculo no fijó el
método**, y que el ejecutado fue el normal.

---

# 3 · La caída de Γ · post hoc autorizado, **sólo calibración**

Semillas `150000011…150000026`, `T_17 = 1024` fijo, código congelado, variando
únicamente `T_P`.

| `T_P` | `D_W` | `D_K^action` | `D_C^A` | `D_C^B` | `Γ` | `Γ/D_W` |
|---|---|---|---|---|---|---|
| 256 | 0.8817 | +0.7387 | +0.7388 | −0.0348 | **+0.7736** | 0.878 |
| 1024 | 0.8817 | +0.5441 | +0.5358 | −0.0109 | **+0.5467** | 0.620 |
| 4096 | 0.8817 | +0.2732 | +0.2736 | −0.0019 | **+0.2755** | 0.313 |

Pareado por semilla, `Γ(4096) − Γ(1024)`:

```
ΔΓ         media -0.2712   sd 0.0410   negativas 16/16
ΔD_K^act   media -0.2709   negativas 16/16      <- caen juntos
ΔD_W       media  0.00e+00  máx |Δ| 0.00e+00    <- el mundo no cambió
```

### La comparación que cierra la pregunta

```
Γ confirmatorio  (T_P = 4096, mundos 160…)   +0.2794   ratio 0.3118
Γ calibración    (T_P = 4096, mundos 150…)   +0.2755   ratio 0.3128
```

**Predice el confirmatorio con 0.004 nats de diferencia.** `D_W` idéntico a
`0.00e+00` en los tres presupuestos, y `D_K^action` y `D_C` bajando juntos.

Queda distinguido, con evidencia y no con plausibilidad:

```
DESCARTADO   «los mundos confirmatorios tenían menos dependencia disponible»
SOSTENIDO    un predecesor más consolidado encoge la adquisición nueva
             a T_17 fijo, y lo hace de forma sistemática (16/16)
```

---

**No se ha escrito ningún cierre. No se ha corregido la desviación. No se ha
abierto ninguna semilla más.**
