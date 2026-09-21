# 1.7 · los seis instrumentos, medidos · previo al preregistro

**Fecha:** 2026-09-20 · calibración `150000011…150000026`
**Confirmatorias `160000011…160000074`: ciegas, sin medir.**

---

## 1 · `D_K^action` · el mismo confundido que `D_C`, y yo no lo busqué

Encontré el confundido en `D_C`, lo reparé, y **no comprobé si la métrica hermana
lo tenía**. Lo tenía. `D_K` contra el kernel verdadero mezclaba conocimiento de
acción con datos extra de la fase A.

```
D_K_action  =  ε_NA − ε_A

ε_NA = E_p_ref KL[ P_W(·|o,a) ‖ M_NA(·|o) ]      el baseline que ignora el comando
ε_A  = E_p_ref KL[ P_W(·|o,a) ‖ M_1(·|o,a) ]
```

Contraparte interna exacta de `D_C = L(NA) − L(M_1)`. Recalculado (`T_P = 1024`):

| `T_17` | `D_W` | `ε_NA` | `ε_A` | **`D_K^action`** | ratio | `D_C` |
|---|---|---|---|---|---|---|
| 64 | 0.8817 | 1.0213 | 0.9444 | **+0.0769** | 0.087 | 0.0865 |
| 256 | 0.8817 | 1.0053 | 0.7656 | **+0.2397** | 0.273 | 0.2497 |
| 1024 | 0.8817 | 0.9596 | 0.4155 | **+0.5441** | 0.617 | 0.5436 |
| 4096 | 0.8817 | 0.9111 | 0.1490 | **+0.7622** | 0.864 | 0.7703 |

**El `D_K` negativo a 64 pasos era el confundido, no el mecanismo.** Corregido da
`+0.0769`. La medida interna y la externa coinciden casi exactamente en los cuatro
presupuestos — es una comprobación de consistencia fuerte, no una coincidencia.

## 2 · Exposición partida en cuatro · y por qué yo dije de más

Dije «la exposición no es el cuello de botella». **Es falso**, y la partición lo
muestra:

| `T_17` | `E_rate` | `E_total` | `C_OA` | `N` mín | `N` p10 | `N` mediana |
|---|---|---|---|---|---|---|
| 64 | 0.8638 | 55.3 | **0.638** | **0.0** | 0.2 | 0.7 |
| 256 | 0.8716 | 223.1 | 0.920 | 0.8 | 1.6 | 4.8 |
| 1024 | 0.8786 | 899.7 | 0.999 | 7.6 | 12.0 | 22.5 |
| 4096 | 0.8726 | 3574.2 | 1.000 | 46.9 | 57.1 | 92.9 |

`E_rate` es **plana** en 0.87 a los cuatro presupuestos: mide densidad informativa
de lo visitado, no acumulación. A 64 pasos la cobertura ponderada de contextos
informativos es 0.638 y **el contexto informativo mínimo tiene cero visitas**.

```
S0 entra rápido en regiones donde la acción informa      ← cierto
la exposición está resuelta                              ← FALSO
```

## 3 · `SHUFFLED-ACTION` estratificado por `O_t`, con su nula

Permuta los tokens **dentro de cada estrato de `O_t`**, conservando exactamente la
secuencia de `O_t`, la de `O_{t+1}`, las cuentas de acción por observación y el
tamaño de muestra. Verificado por contrato: `Counter((o,a))` idéntico antes y
después.

| `T_17` | dispersión real | dispersión barajada | nula media | sd | tolerancia | destructiva | `D_C` barajado |
|---|---|---|---|---|---|---|---|
| 256 | 0.0594 | 0.0255 | 0.0253 | 0.0017 | 0.0322 | 16/16 | +0.0046 |
| 1024 | 0.1650 | 0.0360 | 0.0372 | 0.0027 | 0.0479 | 16/16 | −0.0024 |
| 4096 | 0.2811 | 0.0306 | 0.0302 | 0.0025 | 0.0401 | **15/16** | −0.0101 |

La dispersión barajada cae **sobre la media de la nula** en los tres presupuestos,
y el brazo barajado no obtiene ventaja. Sin umbral fijo en ninguna parte.

> **Aviso honesto:** un fallo de destructividad en 16 a `T_17 = 4096`. Con
> tolerancia de 4σ eso no debería ocurrir casi nunca, así que el sospechoso es la
> **nula de sólo 8 réplicas**: su `sd` tiene ~27 % de error relativo y la
> tolerancia hereda ese ruido. Antes de sellar el oráculo hay que subir las
> réplicas y volver a medir. **No lo he cambiado por mi cuenta.**

## 4 · Las 24 permutaciones opacas · mismo código, 24 correspondencias

```
D_C  media +0.5652   sd entre permutaciones 0.0134
     mín +0.5435 (LEFT DOWN RIGHT UP)   ·   máx +0.5881 (UP RIGHT DOWN LEFT)
     positivas 24 de 24
contenido aprendido idéntico entre dos cableados distintos:  False
```

El mismo aprendiz, sin un cambio de código, adquiere las veinticuatro
correspondencias con una dispersión de 0.013 nats. **El contenido no estaba
escondido en la semántica del token.**

## 5 · `Γ = D_C^A − D_C^B` · el endpoint que explota el gemelo

| `T_17` | `D_C^A` | `D_C^B` | **`Γ`** | sd | `Γ > 0` | `D_K^action` en B |
|---|---|---|---|---|---|---|
| 256 | +0.2497 | −0.0108 | **+0.2604** | 0.0426 | 16/16 | −0.0092 |
| 1024 | +0.5436 | −0.0109 | **+0.5545** | 0.0697 | 16/16 | −0.0124 |
| 4096 | +0.7703 | −0.0067 | **+0.7769** | 0.0744 | 16/16 | −0.0122 |

`Γ` cancela el coste de la sobreparametrización: al ser `D_C^B` levemente
negativo, `Γ` queda por encima de `D_C^A`. En B, `D_K^action ≈ −0.012` y
`D_C ≈ −0.011`: ambas ≈ 0 y ninguna positiva, que es lo exigido.

## 6 · Los presupuestos candidatos, con la evidencia que los apoya

```
T_P  = 4096    L(M_0^W) 1.2694, saturado · aquí la saturación es deseable:
               no estudiamos cómo aprende 1.6, queremos que esté presente

T_17 = 1024    D_K^action/D_W 0.617 · en pendiente, lejos de saturar
               C_OA 0.999 · N mín 7.6 · la exposición ya no es el límite
               Γ +0.5545 con sd 0.0697 · efecto grande y medible
```

Regla developmental: **saturación para el predecesor, pendiente para la
adquisición nueva.** Siguen siendo candidatos, no preregistro.

---

## Estado

```
hecho    1 · D_K^action relativo a NO-ACTION, curva recalculada
hecho    2 · exposición en rate / total / cobertura / recuentos
hecho    3 · SHUFFLED-ACTION estratificado y calibrado por su nula
hecho    4 · las 24 permutaciones opacas
hecho    5 · Γ = D_C^A − D_C^B por mundo gemelo
hecho    6 · en B: D_K^action ≈ 0 y D_C ≈ 0

pendiente  subir las réplicas de la nula y repetir el 15/16
pendiente  sellar T_P, T_17, endpoint y gates
```

23 contratos verdes. **Nada ha tocado las semillas confirmatorias.**
