# `LEVEL1.1-INTEGRATION-VERIFICATION-01` · oráculo preregistrado

**Sellado antes de escribir el experimento.** No es una campaña confirmatoria: es
una **verificación de integración**. La mayoría de los resultados positivos están
determinados por la arquitectura que nosotros suministramos, así que la pregunta
no es «¿funciona?» sino «¿reproduce la implementación el mecanismo que
diseñamos?».

Cuerpo canónico: **FEATURES / `FactoredContingency`**, congelado.

---

## 1 · La tabla analítica

Calculada con cuerpo ideal `B(o,a) = 1 − o[a]` y orientación perfecta
`Q(g,a) = 1[a = φ(g)]`, sobre las `16 × 4 × 4 = 256` tripletas.

```
brazo                  total       A       B       C
COMPOSITE             0.0000   0.000   0.000   0.000
BODY-ONLY             0.1250   0.250   0.000   0.125
CUE-ONLY              0.1250   0.000   1.000   0.000
FROZEN                0.1250   0.250   0.000   0.125
JOINT-TABLE holdout   0.2500   0.250   0.250   0.250
SIEMPRE-CERO          0.1250   1.000   0.000   0.000
IGNORANTE  (0.5)      0.2500   0.250   0.250   0.250
```

```
estrato A · acción = cue, dirección libre        32 de 256
estrato B · acción = cue, dirección bloqueada    32 de 256
estrato C · acción ≠ cue                        192 de 256
```

**Por qué el total no sirve solo.** `BODY-ONLY`, `CUE-ONLY`, `FROZEN` y
`SIEMPRE-CERO` empatan los cuatro en `0.1250` con perfiles de fallo **opuestos**:
`CUE-ONLY` es perfecto en A y catastrófico en B; `SIEMPRE-CERO` es exactamente lo
inverso. El promedio los cancela.

$$BS_{\text{balanced}}=\frac{BS_A+BS_B+BS_C}{3}
\qquad
\begin{array}{ll}
\text{COMPOSITE} & 0.000\\
\text{BODY-ONLY} & 0.125\\
\text{CUE-ONLY} & 0.333\\
\text{SIEMPRE-CERO} & 0.333
\end{array}$$

**`BS_balanced` es la métrica primaria.** `BS_total` es descriptiva y **nunca**
se reporta sin la referencia de siempre-cero, `0.125`, al lado — igual que el
`0.25` del ignorante en el Nivel 1.0.

## 2 · Conducta analítica, sobre estados accionables

```
COMPOSITE    1.0000
CUE-ONLY     1.0000     ← empata con COMPOSITE
BODY-ONLY    0.4688
FROZEN       0.4688
JOINT-TABLE  0.2500
```

**La conducta no puede probar integración.** `CUE-ONLY` la iguala exactamente. El
único gate que la prueba es L11-6, en estados bloqueados, donde `COMPOSITE` da
`0.000` y `CUE-ONLY` da `1.000` — la mayor brecha del diseño.

## 3 · Dosis

$$N = 2048, \qquad \text{criterio}: \min_{g,a} n^{move}_{g,a} \ge 30$$

Elegido por cobertura, no por intuición. Simulado sobre el generador definido:

```
N = 1024  →  P(alguna de las 16 celdas < 30) = 0.999
N = 1536  →  P(...) = 0.024
N = 2048  →  P(...) = 0.000
```

Una realización que no lo cumpla produce `INSUFFICIENT_ORIENTATION_DOSE` y **no
cuenta como fracaso del agente**.

Error ideal de una celda determinista tras `n` observaciones:
$BS_{\text{cell}} = 1/(n+2)^2$ — con `n = 30`, `9.8 × 10⁻⁴`.

## 4 · Semillas

```
verificación  70000019 … 70000026        8 semillas, congeladas aquí
desarrollo    99999937                   la declarada, ya quemada para eso
```

Del espacio propio del linaje 1.1, disjunto verificado de las 585 tocadas. **Sin
bootstrap, sin intervalos, sin significancia**: ocho realizaciones independientes
no son una muestra poblacional, son ocho comprobaciones de que el mecanismo se
reproduce.

## 5 · Lo que sí puede sorprender

Dos pruebas, y son las únicas cuyo resultado no está determinado por nuestra
propia construcción.

**A · Permutación semántica del cue.** Se cambia la correspondencia
`C_i → dirección` y el agente, que nunca la ve, debe aprender la **nueva** matriz
`Q`. Si aprende la misma con las dos, el código resolvió por nombre o por
ordinal: `CUE_SHORTCUT_DETECTED`.

**B · Factorización falsa.** Fixture donde el significado del cue depende de `o`,
de modo que

$$P(R\mid o,g,a,Y{=}1) \neq P(R\mid g,a,Y{=}1)$$

Se espera `COMPOSITE` degradado, `JOINT-TABLE` capaz de representar la
dependencia, y **L11-4 en FAIL**. Si L11-4 sigue pasando, el gate composicional
no es falsable: `COMPOSITION_GATE_NOT_FALSIFIABLE`.

Sin esta fixture, L11-4 **no puede fallar para COMPOSITE por construcción**: ni
`B(o,a)` ni `Q(g,a)` indexan el par `(o,g)`, así que retirar combinaciones no le
quita nada a ninguno de los dos factores.

## 6 · Probe factorial 2×2

```
                        cue compatible      cue incompatible
dirección libre         estrato A           control de cue
dirección bloqueada     estrato B           doble incompatibilidad
```

Variar `g` con `o` fijo demuestra uso de la señal. Variar `o` con `g` fijo
demuestra uso del cuerpo. Es intervención causal local: no necesita semillas.

## 7 · Stop conditions

```
INTEGRATION_MODEL_MISMATCH        la implementación no reproduce la tabla
CUE_SHORTCUT_DETECTED             resolvió por nombre, no por experiencia
COMPOSITION_GATE_NOT_FALSIFIABLE  L11-4 aprueba con factorización falsa
INSUFFICIENT_ORIENTATION_DOSE     min n_move < 30 en alguna asociación
BODY_MODEL_MUTATED                la huella de FEATURES cambió
LEVEL1_BASELINE_REGRESSION        el Experimento 1 dejó de pasar
MEASUREMENT_NOT_PASSIVE           una sonda movió algo
```

## 8 · Afirmación máxima permitida

> El agente aprendió a utilizar una señal direccional externa y la combinó con su
> conocimiento sensorimotor previo para seleccionar movimientos compatibles con
> esa señal cuando eran físicamente realizables.

**Y no** «conducta adaptativa». El corpus lo prohíbe explícitamente: Ashby
rechaza «responde correctamente a un estímulo» como definición de adaptación
porque *«no tiene significado "correctamente" salvo que signifique conformarse a
lo que el experimentador cree que el animal debería hacer»*
(`R-HEA-014-001`, `extracted_text/HEA-014.txt:5608-5662`).

`R_align` es **cumplimiento de una correspondencia direccional especificada por
el experimentador**. Nada más.

La factorización cuerpo/orientación **la suministramos nosotros**; el organismo
no la descubrió.
