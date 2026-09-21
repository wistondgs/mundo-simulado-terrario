# Nivel 1.8 · adjudicación previa

```
┌────────────────────────────────────────────────────────┐
│   EXPLORATORIO / CALIBRACIÓN  ·  NO CONFIRMATORIO      │
└────────────────────────────────────────────────────────┘
```

**Fecha:** 2026-09-20 · base `6cf55a4`, el cierre **congelado** de 1.7
**No es implementación de 1.8.** No hay capacidad diseñada, ni oráculo, ni semillas
reservadas. Ningún archivo de 1.7 fue modificado.

Semillas usadas: `150000011…150000026`, las de **calibración** de 1.7.
Las confirmatorias de 1.7 (`170…`) no se tocaron.

---

# 1 · La candidata

Hasta 1.7 el circuito es abierto:

```
S0  →  A  →  O'  →  aprendizaje        y el aprendizaje nunca vuelve a S0
```

El ser sabe qué efecto tiene cada acción, y eso **no cambia qué acción emitirá
después**. La candidata mínima sería cerrar ese bucle por primera vez:

```
lo que todavía necesito aprender  →  sesgo de acción  →  nueva experiencia
                                  →  nuevo aprendizaje
```

# 2 · Hay techo, y es grande

`resultados/level18_calibration/techo_muestreo.json`

Modelo de error de estimación con presupuesto fijo:

```
error(f) = Σ_oa p_ref(o,a)·(K_oa − 1) / (2·T·f_oa)      con Σ f = 1
uniforme de S0:  f = p_ref            óptimo:  f* ∝ √(p_ref·(K−1))
```

```
razón error_óptimo / error_uniforme       0.4357
ganancia máxima del muestreo perfecto     56.4 %
equivalente                               2.30× el presupuesto, sin tocar nada más
```

**1.8 es viable en la clase de mundos que ya existe.** No hace falta rediseñar el
mundo, igual que no hizo falta para 1.7.

# 3 · Pero el presupuesto de 1.7 lo mataría

`resultados/level18_calibration/barrido_presupuesto.json`

```
T      C_OA    N mín   contextos nunca visitados
  64   0.600     0.0        22.1
 128     —         —           —
 256   0.920     0.0         5.6
1024   1.000     4.1         0.0      ← el presupuesto que 1.7 selló
4096   1.000    39.2         0.0
```

A `T = 1024` el muestreo uniforme **ya llega a todo**: no queda escasez que
seleccionar. Heredarlo mecánicamente repetiría el error de saturación de 1.6.

```
la escasez real vive en   T ≲ 256
```

No se fija todavía un presupuesto. Lo que queda establecido es que **1024 sería una
mala elección experimental**.

# 4 · Los controles ciegos son PEORES que no hacer nada

`resultados/level18_calibration/controles_ciegos.json`

```
f ∝ √p_ref            (ciego)                       −24.5 %   peor que el uniforme
f plano entre contextos                             −70.1 %   mucho peor
  = «muestrea donde menos has contado»
f ∝ √(p_ref·(K−1))    usa K aprendido               +56.4 %
```

Los contextos difieren enormemente en cuánto hay que aprender: el reparto plano
desperdicia presupuesto en contextos deterministas (`K = 1`, nada que aprender) y
mata de hambre a los de `K = 5`.

**Resultado fuerte para la adjudicación:**

> La información necesaria para seleccionar bien **no está en los conteos solos**.
> Toda la ganancia exige `K(o,a)` —cuántas consecuencias distintas admite ese
> contexto— que es propiedad del mundo y debe adquirirse.

1.8 nace con un control ciego que no queda cerca del óptimo: queda **por detrás del
sustrato**. Eso es mejor que el `STATIC-BITCOUNT` de 1.6, donde el control ciego
llegaba a milésimas.

**Advertencia explícita:** que `f* ∝ √(p_ref·(K−1))` funcione **no** significa que
esa regla deba ser la capacidad de 1.8. Codificarla sería regalar la solución. Lo
que estas mediciones establecen es lo **previo**: que el contenido necesario
depende de experiencia.

# 5 · La incertidumbre irreducible es concreta, no hipotética

`resultados/level18_calibration/irreducibilidad_aliasing.json`

```
H(O'|O,A)   media 0.3427 nats   ·   máx 0.4833
```

Procede del aliasing: celdas distintas con la misma firma van a firmas distintas.
**Ningún contador puede bajar de ahí**, por mucho que muestree.

```
incertidumbre alta   ≠   oportunidad de aprendizaje
```

Una señal de necesidad enganchada a incertidumbre cruda perseguiría ese suelo
eternamente. La candidata debe distinguir **reducible** de **irreducible**.

Y como el suelo tiene forma cerrada por semilla, un oráculo futuro puede sellarlo
**antes de que exista código** — la doctrina B-4 que salió de 1.6.

# 6 · Lo que esto NO decide

```
el presupuesto de 1.8
la forma de la señal de necesidad
si la capacidad es «muestreo epistémico» o alguna otra
el endpoint
cualquier gate
```

Y sobre todo: **no decide el problema arquitectónico**, que es más profundo que los
cuatro hallazgos anteriores y vive en
`docs/level18/CONTROL_CAUSAL_POLITICA_ENDOGENA.md`.
