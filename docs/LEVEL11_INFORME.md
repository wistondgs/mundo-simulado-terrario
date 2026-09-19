# `LEVEL1.1-INTEGRATION-VERIFICATION-01` · informe

**`LEVEL11_STATUS = VERIFIED`**

Rama `experiment/level1-reversal-plasticity-01` · guion
`scripts/level11_integration_verification.py` · salida en
`artifacts/level11/verification.txt`.

Ocho realizaciones, semillas `70000019 … 70000026`, del espacio propio del
linaje 1.1. **Sin bootstrap, sin intervalos, sin significancia**: ocho
realizaciones no son una muestra poblacional, son ocho comprobaciones de que el
mecanismo se reproduce.

---

## 1 · Qué se verificó, y qué no

Esto **no fue un experimento confirmatorio**. Antes de escribir código calculé
cada gate en cerrado y ninguno tenía resultado incierto: `COMPOSITE` da `0.0000`
contra `0.1250` de todos los controles, y la varianza de muestreo de los modelos
aprendidos está cinco órdenes de magnitud por debajo de esa brecha. Correr 32
semillas con bootstrap habría establecido que `0.0000 < 0.1250`.

La pregunta que sí tenía sentido: **¿reproduce la implementación el mecanismo que
diseñamos?** El oráculo se selló en `docs/LEVEL11_ORACULO_PREREGISTRADO.md`
antes de existir el experimento.

## 2 · Predicción · Brier por estrato

```
brazo            total       A       B       C  balanced  oráculo       Δ
COMPOSITE       0.0001   0.000   0.000   0.000     0.000    0.000  +0.000
BODY-ONLY       0.1249   0.250   0.000   0.125     0.125    0.125  +0.000
CUE-ONLY        0.1218   0.000   0.973   0.000     0.324    0.333  −0.009
FROZEN          0.1249   0.250   0.000   0.125     0.125    0.125  +0.000
SHUFFLED        0.0957   0.564   0.000   0.034     0.199        —       —
JOINT-TABLE     0.0781   0.070   0.087   0.078     0.078        —       —
SIEMPRE-CERO    0.1250   1.000   0.000   0.000     0.333    0.333  +0.000
IGNORANTE       0.2500   0.250   0.250   0.250     0.250    0.250  +0.000
```

`A` = la acción que el cue señala y está libre · `B` = la señala y está bloqueada
· `C` = cualquier otra acción. `32 / 32 / 192` de las 256 tripletas.

**`balanced` es la primaria, y hay una razón medida.** En el total,
`BODY-ONLY`, `CUE-ONLY`, `FROZEN` y **un predictor constante que dice siempre
cero** empatan los cuatro en `0.125`, con perfiles de fallo **opuestos**:
`CUE-ONLY` es perfecto en A y catastrófico en B (`0.973`); `SIEMPRE-CERO` es
exactamente lo inverso (`1.000` en A). El promedio los cancela; la balanceada los
separa en `0.125` contra `0.333`.

Por eso el total nunca se reporta solo: **siempre-cero en total = `0.1250`**.

## 3 · Conducta · `R_align` en cerrado

```
brazo            medido  oráculo        Δ
COMPOSITE        1.0000   1.0000  +0.0000
CUE-ONLY         1.0000   1.0000  +0.0000
BODY-ONLY        0.4688   0.4688  −0.0000
FROZEN           0.4688   0.4688  −0.0000
SHUFFLED         0.4531        —        —
JOINT-TABLE      0.8125        —        —
SIEMPRE-CERO     0.2500   0.2500  +0.0000
IGNORANTE        0.2500   0.2500  +0.0000
```

**`CUE-ONLY` iguala exactamente a `COMPOSITE`.** La conducta no puede probar
integración, y estaba previsto: quien conoce la señal acierta siempre en los
estados donde la dirección señalada está libre, sepa o no si lo está.

Lo que prueba integración es el estrato **B**: `COMPOSITE 0.000` contra
`CUE-ONLY 0.973`. Ahí el cuerpo es lo único que puede saber que el movimiento
señalado no es realizable.

## 4 · Holdout · 16 pares `(o,g)` nunca vistos juntos

```
COMPOSITE      0.000
FROZEN         0.125
SHUFFLED       0.206
JOINT-TABLE    0.250     ← su prior: no tiene celda para esos pares
```

**Y esto está determinado por la arquitectura, no descubierto.** Ni `B(o,a)` ni
`Q(g,a)` indexan el par `(o,g)`, así que retirar combinaciones no le quita nada a
ninguno de los dos factores. Por eso la fixture de factorización falsa es
obligatoria: sin ella el gate composicional **no puede rechazar nada**.

Esa fixture está en `tests/test_level11_orientation.py` y funciona: con el
significado del cue dependiendo de la observación, `COMPOSITE` se degrada por un
factor de veinte y la tabla conjunta gana.

## 5 · Probe 2×2 · intervención causal por situación

```
brazo           sensib. cue   sensib. cuerpo
COMPOSITE             0.972            0.984
BODY-ONLY             0.000            0.499     ← ciego a la señal
CUE-ONLY              0.973           −0.000     ← ciego al cuerpo
```

Los ceros son exactos. Es evidencia por situación, sin promedios ni intervalos:
variar `g` con `o` fijo y variar `o` con `g` fijo.

## 6 · Integridad

```
cobertura informativa mínima   46   (criterio ≥ 30)
cuerpo intacto en las 8        True
violaciones del contrato       0
fugas del holdout              0
mayor desviación del oráculo   0.0085   (tolerancia 0.02)
```

El cuerpo FEATURES se entrena en fase 0 y pasa a un envoltorio **sin método
`observe`**: el método que no existe no se puede llamar por descuido. Su huella
es idéntica antes y después en las ocho realizaciones, así que la única
estructura que cambió durante 1.1 es `Q`.

## 7 · Defectos hallados construyendo, y cómo se delataron

**El control negativo no era un control.** `SHUFFLED` daba `0.0001` contra
`0.0001` de `COMPOSITE` y `R_align 1.0000` los dos. Yo barajaba la señal **junto
con su semántica**, así que la etiqueta de alineamiento se calculaba contra la
dirección del cue barajado: un reetiquetado consistente, no un desacople. Un
control que empata con lo que controla es como se delató.

**`R_align` se muestreaba donde se puede calcular.** El oráculo promedia el
desempate y la implementación lo sorteaba: `0.5000` frente a una esperanza de
`0.4688`. La verificación habría levantado un `INTEGRATION_MODEL_MISMATCH`
**falso contra su propio oráculo**.

**El umbral de la factorización falsa lo había elegido yo.** `COMPOSITE` se
degradaba a `0.0469` contra un `0.05` inventado. Bajarlo a `0.04` habría sido
ajustar el test al resultado; ahora compara `COMPOSITE` consigo mismo bajo
factorización verdadera, que es un factor y no un número.

**Y una corrección de este informe.** Dije antes que `SHUFFLED` cae al azar,
basándome en una sola semilla donde dio `0.2500`. Sobre las ocho da `0.4531`, y
es lo correcto: barajar destruye el conocimiento de la señal pero **conserva el
cuerpo**, así que su conducta debe tender a la de `BODY-ONLY` (`0.4688`), no al
azar. Donde sí muestra el daño es en la predicción: estrato `A` en `0.564`, que
es exactamente `(1 − 0.25)²` con `Q` colapsada a su marginal de `0.25`.

## 8 · Afirmación permitida

> El agente aprendió a utilizar una señal direccional externa y la combinó con su
> conocimiento sensorimotor previo para seleccionar movimientos compatibles con
> esa señal cuando eran físicamente realizables.

**Y no «conducta adaptativa».** El corpus lo prohíbe explícitamente: Ashby
rechaza «responde correctamente a un estímulo» como definición de adaptación
porque *«no tiene significado "correctamente" salvo que signifique conformarse a
lo que el experimentador cree que el animal debería hacer»* (`R-HEA-014-001`).
`R_align` es **cumplimiento de una correspondencia especificada por el
experimentador**.

**Tampoco:** navegación, orientación con objetivo, búsqueda de rutas, memoria
espacial, representación de distancia, mapa, motivación, planificación, ni
cognición espacial general.

**Y la factorización cuerpo/orientación la suministramos nosotros.** El organismo
no la descubrió. Lo demostrado es que una adquisición nueva puede montarse encima
del conocimiento anterior sin modificarlo, y que ambos pueden usarse juntos —
incluso en combinaciones nunca experimentadas a la vez.

## 9 · Lo que 1.1 costó y lo que aportó

La adquisición nueva son **menos de cinco bits**: cuál de cuatro comandos
corresponde a cada uno de cuatro tokens, `log₂(4!) = 4.58`. Frente a las 36
acumuladores del cuerpo, es diminuta.

Eso no la hace trivial como hito, pero sí fija qué clase de hito es: **de
integración, no de descubrimiento**. Las 32 semillas y el bootstrap quedan
reservados para el primer decimal donde exista una pregunta cuya respuesta no
podamos calcular antes de ejecutar el organismo.
