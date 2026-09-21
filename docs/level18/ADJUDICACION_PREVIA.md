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
ganancia del reparto LIBRE                56.4 %
```

> ### CORRECCIÓN · ese techo no es alcanzable por ningún organismo
>
> El reparto libre reasigna presupuesto **entre observaciones**. Una política
> elige `a` dado `o`; **no elige `o`**. El techo realizable es el del reparto
> dentro de cada observación:
>
> ```
> techo LIBRE        ganancia 56.4 %      NO realizable
> techo ALCANZABLE   ganancia 30.6 %      (mín 17.7 % · máx 50.5 %)
> ```
>
> Mi cifra anterior sobrestimaba el margen **1.84×**. Y ni siquiera 30.6 % es el
> final de la historia: ver §7.

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

---

# 7 · `Q1` · **la respuesta es negativa, y el motivo es estructural**

## 7.1 · `K` sí es un readout de C17 — pero miente donde importa

`K̂(o,a)` = cuántas consecuencias distintas ha visto C17 en ese contexto. Es un
**readout determinista del estado congelado de 1.7**: no requiere estado nuevo.

```
T_17    K̂/K_true   contextos que subestiman   |error| medio
  64      0.4369            62.5 %                0.746
 128      0.6583            40.1 %                0.456
 256      0.8457            19.2 %                0.208
1024      1.0000             0.0 %                0.000
```

**Es exacto justo donde seleccionar es inútil (`T = 1024`, saturado) y falso justo
donde importaría (`T ≤ 256`).** El contexto que más falta muestrear es precisamente
donde `K̂` miente más, porque no se ha visto lo que aún no se muestreó.

## 7.2 · `Q1-B` · ninguna política gana · ni siquiera la del oráculo

`scripts/diagnostico_seleccion.py` · `ε_A` final, menos es mejor:

```
  T    uniforme  lowcount  C17+readout  oráculo K      ganancia readout / oráculo
 64      0.8944    0.8947       0.8941     0.9038            0.0 %  /   −1.1 %
128      0.8701    0.8730       0.8767     0.8935           −0.8 %  /   −2.7 %
256      0.8270    0.8323       0.8537     0.8761           −3.2 %  /   −5.9 %
512      0.7537    0.7637       0.8277     0.8513           −9.8 %  /  −13.0 %
```

**Todas son peores que el uniforme, y empeoran con el presupuesto.** Incluso la que
conoce `K` verdadero, que tiene fuga de oráculo y debería ser una cota superior.

## 7.3 · El mecanismo, medido

```
                    TV( p_visitas ‖ p_ref )
uniforme                    0.1389
oráculo                     0.4310        se aleja 3.10×
```

> **En este mundo, «qué muestreo» y «dónde estoy» son el MISMO grado de libertad.**

La política elige la acción; la acción decide la celda siguiente. El error se
evalúa bajo `p_ref` —la estacionaria del paseo uniforme, que es el único banco
neutral posible— así que cualquier desviación mata de hambre a las observaciones
que `p_ref` pondera. Lo que se gana en asignación se pierde en ubicación, y se
pierde más.

El cálculo del techo asumía `N(o,a)` libre. Es falso: fijar `N(·|o)` cambia `p(o)`.

## 7.4 · Veredicto

```
┌──────────────────────────────────────────────────────────────────┐
│  NO HAY TODAVÍA UNA ADQUISICIÓN NUEVA IDENTIFICABLE              │
│  el muestreo epistémico selectivo NO es adjudicable como 1.8     │
│  en esta clase de mundos                                         │
└──────────────────────────────────────────────────────────────────┘
```

Y no por debilidad del candidato: **por una propiedad del mundo.** Un organismo que
no puede separar muestrear de desplazarse no puede seleccionar experiencia sin
pagarlo en cobertura.

**Límites honestos de este veredicto:**

```
· la política probada es voraz sobre proporciones objetivo. Una que optimizara
  CONJUNTAMENTE asignación y distribución de visitas podría ganar — pero eso
  exige modelar a dónde llevan las acciones, o sea planificación, no muestreo.

· el veredicto depende de evaluar bajo p_ref. Evaluar sobre el futuro que el
  propio selector produce lo haría ganar trivialmente, y eso es el examen
  autoseleccionado que CONTROL_CAUSAL_POLITICA_ENDOGENA §3 prohíbe.
```

## 7.5 · Lo que esto sugiere sobre el orden developmental

Descartaste `retorno` por «meter varias capacidades de golpe». La medición apunta
al revés:

> Para seleccionar qué experimentar hace falta primero poder **volver** a donde
> está lo que falta por aprender. Si cada muestreo te desplaza, seleccionar y
> navegar son el mismo acto.

El candidato previo no sería «sé qué me falta», sino **algo que desacople la
elección de la ubicación**: un repertorio con actos que no desplacen, o la
capacidad de regresar. No lo propongo como diseño — lo señalo porque el orden que
habíamos supuesto puede estar invertido.

---

# 8 · Deliverables de esta fase

| | entregable | estado |
|---|---|---|
| A | los cuatro resultados exploratorios preservados | `resultados/level18_calibration/` |
| B | `ADJUDICACION_PREVIA.md` | este documento |
| C | `CONTROL_CAUSAL_POLITICA_ENDOGENA.md` | escrito |
| D | diagrama causal FULL / LESION / SHADOW / YOKED | `CONTROL…` §4 |
| E | inventario de RNG exógeno/endógeno/instrumental | `CONTROL…` §1.3 |
| F | ¿`K` es readout de C17? | §7.1 · **sí, pero sesgado donde importa** |
| G | cuánto del techo da C17 + política suministrada | §7.2 · **nada; pierde** |
| H | trampa de incertidumbre irreducible | §5 · `H(O'|O,A) = 0.3427` |
| I | métricas de experiencia conseguida | `CONTROL…` §5.1 · vector, no escalar |
| J | qué gates se heredan / adaptan / desaparecen / nacen | `CONTROL…` §6 |
| K | **veredicto** | §7.4 · **NO ADJUDICABLE** |
