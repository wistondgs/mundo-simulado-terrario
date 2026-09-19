# `LEVEL1.2-QUALITATIVE-DISTANCE-01` · oráculo preregistrado

**Sellado antes de existir el experimento.** Todo número de este documento está
calculado en cerrado o derivado de la distribución muestral; ninguno proviene de
una corrida del organismo.

Adjudicado por Wis. Enmienda central sobre la propuesta previa: **el sensor
depende de `δ`, no de la clase**. Linaje: `1.0` cuerpo · `1.1` orientación ·
`1.2` proximidad cualitativa.

---

## 1 · Referencia latente · adjudicado C1(a)

Desplazamiento relativo **abstracto y axial**:

```
r_t = p_t + δ_t · DELTA[G_t]
```

`r_t` puede caer fuera de la rejilla. No bloquea, no colisiona, no puede tocarse,
no altera la física. Sólo define dirección y distancia latentes.

**Axial, nunca diagonal**: con offsets diagonales `(-3,-3)` tiene `δ=6` y ninguna
dirección única, y haría falta una regla de proyección.

Motivo de la adjudicación, medido sobre el mundo congelado (`grid_size = 7`,
borde cerrado, interior libre 5×5): `δ` máximo desde el centro `(3,3)` es **4**;
`δ` máximo alineado a eje es **4**. Exigir que la referencia fuera una celda
habría hecho `δ ∈ {5,6}` imposible y confundido distancia con posición antes de
correr nada.

## 2 · Clases y margen

```
δ ∈ {1, 2}      → CERCA (N)
δ ∈ {4, 5, 6}   → LEJOS (F)
δ ∈ {0, 3}      → NO SE GENERAN NUNCA
```

`δ = 3` no es una tercera clase: es margen, y se evita generándolo, no
filtrándolo.

## 3 · Emisión del sensor · condicionada a `δ`

**La evidencia sensorial nace de la distancia física, no de la etiqueta.**

```
δ        S0     S1     S2     S3      suma
1      0.02   0.08   0.30   0.60      1.00
2      0.08   0.22   0.30   0.40      1.00
─────────────────────────────────────────────
4      0.43   0.28   0.20   0.09      1.00
5      0.50   0.30   0.15   0.05      1.00
6      0.57   0.32   0.10   0.01      1.00
```

Con `δ` uniforme dentro de cada clase, las marginales por clase son, en
aritmética exacta de fracciones:

```
P(s | N) = 1/20, 3/20, 3/10, 1/2   =  0.05, 0.15, 0.30, 0.50
P(s | F) =  1/2, 3/10, 3/20, 1/20  =  0.50, 0.30, 0.15, 0.05
```

**Verificado idéntico** a las marginales que se habían sellado antes de la
enmienda. Por tanto el oráculo del agente no cambia: el organismo ve `s`, nunca
`δ`, y su problema es el mismo.

Lo que sí cambia es que `δ` pasa a ser causalmente relevante. Y por eso es
auditable: dentro de una misma clase,

```
max_k |P(s | δ=1) − P(s | δ=2)| = 0.20
max_k |P(s | δ=4) − P(s | δ=6)| = 0.14
```

Un generador que ignorara `δ` y emitiera desde la marginal produce exactamente
`0.00` en ambas. **El contrato L12-11 lo comprueba**, para que la enmienda sea
una propiedad verificada y no una declaración.

## 4 · Oráculo del agente

```
H*(s) = P(s|N) / (P(s|N) + P(s|F))         con P(N) = P(F) = 1/2

H*(S0) = 1/11  = 0.090909
H*(S1) = 1/3   = 0.333333
H*(S2) = 2/3   = 0.666667
H*(S3) = 10/11 = 0.909091

P(S0..S3) = 0.275, 0.225, 0.225, 0.275
```

## 5 · Techos

```
BS*  = Σ_s P(s)·H*(s)(1−H*(s))  =  8/55  =  0.145454545…     EXACTO
BS_ignorante (H ≡ 1/2)          =  1/4   =  0.250000         EXACTO
Accuracy* = Σ_s P(s)·max(H*,1−H*) = 4/5  =  0.800000         EXACTO
```

`Accuracy* = 0.80` **no es un defecto**: es el techo que impone la ambigüedad del
sensor. La métrica primaria es probabilística.

## 6 · `BS_distance` · riesgo poblacional, no banco empírico · adjudicado §4

**El modelo no se puntúa sobre el flujo con el que se entrenó.** No hace falta un
banco adicional: se usa el riesgo poblacional cerrado.

```
BS_pop(H) = ½ Σ_s P(s|N)·(H(s) − 1)²  +  ½ Σ_s P(s|F)·H(s)²
```

Sin RNG de evaluación, sin ruido de banco, exactamente comparable con `8/55`.
Identidad que lo ancla:

```
BS_pop(H) − BS*  =  Σ_s P(s)·(H(s) − H*(s))²        ≥ 0, con igualdad sólo si H = H*
```

`BS_distance` significa **este** Brier poblacional en todos los gates salvo
indicación explícita.

## 7 · Umbrales · derivados, no elegidos

Simulación del generador aprobado — 2048 ensayos, 1024 por clase, `δ` uniforme
dentro de clase, emisión condicionada a `δ` — con `R = 200 000` réplicas,
`np.random.default_rng(20260919)`:

```
BS_pop           media 0.145702   p99 0.146400   p99.99 0.147353   máx 0.147971
max_k |Δ_k|      media 0.02377    p99 0.05508    p99.99 0.07953    máx 0.09747
cobertura mín    media 47.3       mín 23
```

Umbrales congelados:

```
BS_distance(FULL_12)   ≤ 0.1480
max_k |H(S_k) − H*(S_k)| ≤ 0.10
min_{D,s} n_{D,s}      ≥ 30
```

**Cálculo que produjo `0.1480`.** El exceso permitido es
`0.1480 − 8/55 = 0.002545`. El exceso esperado por estimación con
`n_s ≈ 461…563` muestras por token es, en cerrado,

```
E[BS_pop] − BS* = Σ_s P(s)·MSE_s        con  MSE_s = [n_s·H*(1−H*) + (1−2H*)²] / (n_s+2)²
                = 0.000297
```

El umbral es por tanto `8.6 ×` el exceso esperado. Riesgo estimado por
aproximación Gamma al mixture de χ²: `≈ 4·10⁻⁶` por semilla, `≈ 3.5·10⁻⁵` sobre
ocho.

**Advertencia registrada:** el umbral está sólo `1.02 ×` por encima del máximo
observado en 200 000 réplicas (`0.147971`). Es un guardarraíl ajustado, no
holgado. Se sella tal cual por adjudicación; si alguna vez dispara, la primera
hipótesis a descartar es muestreo, no defecto.

**Cálculo que produjo `0.10`.** `Δ_s` tiene desviación típica
`√MSE_s = 0.0122` para `S0,S3` y `0.0219` para `S1,S2`. El umbral está a `4.57 σ`
del token más ruidoso: riesgo `≈ 1·10⁻⁵` por semilla, `≈ 8·10⁻⁵` sobre ocho.
Máximo observado en 200 000 réplicas: `0.09747`.

**Queda explícitamente prohibido heredar el `0.02` del Nivel 1.1.** Medido: con
`0.02` el gate cae en el `99.99 %` de las campañas de ocho semillas aunque el
aprendiz sea exacto, porque `H(s)` se estima con ~500 muestras por token y no con
decenas de miles.

## 8 · Dosis y cobertura

```
N_DISTANCE = 2048        1024 CERCA · 1024 LEJOS
256 ensayos exactos por cada una de las 8 combinaciones (D,G)
celda más rara: p = 0.05 → E[n] = 51.2
```

`P(min_{D,s} n < 30)` medido: `0.00082` por semilla, `0.00658` sobre ocho.
**Se preregistra que ≈ 1 de cada 150 campañas excluirá una semilla** por
`INSUFFICIENT_DISTANCE_DOSE`. Es exclusión esperada, **no**
`DISTANCE_ACQUISITION_FAILED`.

## 9 · Empates preregistrados · no son hallazgos

```
NO_DISTANCE = FROZEN_DISTANCE = 0.250000   EXACTO   (ambos dan H ≡ 1/2)
FULL_12     = SENSOR_ONLY                  EXACTO   (mismo H(s); B y Q no entran)
SHUFFLED    ≈ 0.2504                                (H → 1/2 más varianza finita)
BAYES_ORACLE = 8/55                        EXACTO
```

> **`BS_distance` no prueba integración.** Prueba adquisición de la distinción
> probabilística, nada más. La integración la prueban los tres probes de una
> variable, la métrica conjunta y la fixture de factorización falsa.

Es la misma situación estructural que en 1.1, donde `R_align` empataba entre
`COMPOSITE` y `CUE-ONLY`.

## 10 · Generador definitivo · adjudicado §8

```
1. construir 2048 pares (D,G): 256 exactos por combinación
2. barajar con rng_pairing
3. δ ~ uniforme dentro de la clase                        rng_reference
4. offset = δ · DELTA[G]                                  axial
5. g = cue_for(G)        ← el cue SIGNIFICA G, no se sortea aparte
6. s ~ P(· | δ)                                           rng_sensor
7. o ← del mundo, después, sin participar en nada anterior
8. DistanceObservation = (o, g, s)
9. D, δ y Reference quedan sólo en DistanceTrainingRecord
```

**Nunca** elegir `D` a partir de `o`. **Nunca** a partir de `g`.

`g = φ⁻¹(G)` usando la `CueSemantics` heredada: el cue apunta a la referencia y
el sensor dice a qué distancia está. Sortear `g` aparte habría roto el
significado del Nivel 1.1. Como `(D,G)` está balanceado y `φ` es biyectiva,
`P(D | g) = P(D | G) = 0.5` **exacto**.

## 11 · `P(D|o) = 0.5` es esperanza, no identidad muestral · adjudicado §6

El balance factorial garantiza `P(D|G) = 0.5` exactamente, porque cada `(D,G)`
aparece el mismo número de veces. **No** garantiza `P(D|o) = 0.5` en una
realización finita: el mundo produce `o` con independencia, pero los conteos de
CERCA/LEJOS dentro de cada `o` fluctúan.

Por tanto **L12-6 no exige igualdad exacta**. Es auditoría del generador, no
adquisición cognitiva. El criterio se construye **antes de correr**: envelope
nulo por permutación independiente de la asignación `D` respecto del flujo `o`,
`10 000` permutaciones, y el estadístico observado se compara contra el
percentil `99.9` de esa distribución nula. La fixture condicionada a `o` debe
quedar claramente fuera del envelope.

**El umbral no se elige después de mirar las ocho semillas.**

## 12 · Composición triple · autorizada §12

```
J_N(o,g,s,a) = B(o,a)·Q(g,a)·H(s)
J_F(o,g,s,a) = B(o,a)·Q(g,a)·(1−H(s))

T_N = 1[movimiento posible] · 1[acción alineada] · 1[D = N]
T_F = 1[movimiento posible] · 1[acción alineada] · 1[D = F]
```

Brier conjunto estratificado sobre un banco diagnóstico balanceado **separado del
aprendizaje**.

**Clasificación epistemológica, sellada:** esto es *verificación de integración*,
no *descubrimiento de composición*. La arquitectura impone la factorización.

## 13 · Semillas

```
Nivel 1.2 primarias:   80000011 … 80000018        ocho
```

Bloqueadas y no reutilizables: `20260919…` (1.0 ejecutadas) · `31415926`
(quemada) · `31415927 … 31415958` (**reservadas** para la reversión, experimento
deliberadamente no corrido — reservadas, no consumidas) · `70000019 … 70000033`
(1.1 ejecutadas, incluidos los desplazamientos `+7`).

## 14 · RNG

```
heredados (los consume la reconstrucción 1.1, no 1.2):
  train_body(σ)                 → motor_babbling(σ)
  orientation_babbling(σ+7)     → [σ+7,1] mundo · [σ+7,2] acto · [σ+7,3] señal

nuevos de 1.2:
  [σ, 21]  rng_pairing      baraja la lista factorial (D,G)
  [σ, 22]  rng_reference    δ dentro de la clase
  [σ, 23]  rng_sensor       emisión del token
  [σ, 24]  rng_readout      sondas y lecturas
  [σ, 25]  rng_shuffle      control barajado
  [σ, 26]  rng_world12      el mundo del que se lee o
```

Ninguna sonda consume RNG de adquisición. Los probes, `BS_pop` y
`alignment_rate_expected` son cerrados y no consumen ninguno.

## 15 · Brazos

```
FULL_12            B · Q · H aprendido
NO_DISTANCE        H ≡ 1/2 por sustitución            (= el agente 1.1)
FROZEN_DISTANCE    estructura presente, α=β=1
SHUFFLED_DISTANCE  sensor de otro ensayo, verdad del suyo
SENSOR_ONLY        sólo H(s)
BAYES_ORACLE       H*(s) desde la matriz; no aprende
```

`H(s,g)` existe **únicamente** dentro de la fixture de factorización falsa. No es
un organismo.

## 16 · Gates

| gate | criterio |
|---|---|
| **L12-0** integridad de linaje | `fingerprint_antes == fingerprint_después`, identidad exacta |
| **L12-1** contrato de observabilidad | `predict` no alcanza `truth`, `δ`, `p`, `r` |
| **L12-2** cobertura | `min_{D,s} n_{D,s} ≥ 30` |
| **L12-3** adquisición | `FULL < FROZEN`, `< NO_DISTANCE`, `< SHUFFLED`; y `BS ≤ 0.1480` |
| **L12-4** semántica del sensor | `max_k|Δ_k| ≤ 0.10`; invariante a permutación de tokens |
| **L12-5** dirección–distancia | `P(D\|g) = 0.5` exacto |
| **L12-6** cuerpo–distancia | asociación `D↔o` dentro del envelope nulo p99.9 |
| **L12-7** integración acumulativa | tres probes con ceros exactos + Brier conjunto |
| **L12-8** preservación motora | `R_align^pre ≡ R_align^post`, igualdad determinista |
| **L12-9** falsabilidad | fixture falsa: `BS(H(s)) = 1/4`, `BS(H(s,g)) = 8/55` |
| **L12-10** pasividad | huella idéntica tras medir; RNG independientes |
| **L12-11** el sensor depende de `δ` | `max_k|P(s\|δ=1) − P(s\|δ=2)| ≥ 0.10` en el flujo generado |

**Ningún gate se acepta si su único comportamiento posible es `PASS`.** Fixtures
negativas obligatorias, una por gate.

## 17 · Condiciones de parada

```
LEVEL11_BASELINE_REGRESSION      GROUND_TRUTH_LEAK_DETECTED
METRIC_DISTANCE_EXPOSED          PROXIMITY_SENSOR_UNINFORMATIVE
INSUFFICIENT_DISTANCE_DOSE       DIRECTION_DISTANCE_CONFOUNDED
BODY_DISTANCE_CONFOUNDED         DISTANCE_ACQUISITION_FAILED
SENSOR_SHORTCUT_DETECTED         PREVIOUS_KNOWLEDGE_MUTATED
FACTORING_GATE_NOT_FALSIFIABLE   MEASUREMENT_NOT_PASSIVE
RNG_COUPLING_DETECTED            ORACLE_MISMATCH
SENSOR_IGNORES_DISTANCE
```

## 18 · Afirmación máxima autorizada

> El Agente Nivel 1.2 adquirió una distinción probabilística entre dos clases
> cualitativas de proximidad a partir de evidencia sensorial ambigua generada por
> la distancia latente de una referencia externa, conservando intactas sus
> adquisiciones sensorimotoras y direccionales previas.

> El agente acumulativo pudo consultar conjuntamente conocimiento corporal,
> direccional y de proximidad sin modificar los mecanismos adquiridos en niveles
> anteriores.

**No afirmar que «representa distancia».** No conoce coordenadas, ni valor
métrico, ni número de celdas, ni Manhattan, ni el umbral físico. La clasificación
CERCA/LEJOS es una ontología suministrada por el experimentador.

**Tampoco:** navegación, búsqueda, planificación, acercamiento o alejamiento
deliberado, rutas, memoria espacial, mapa, conducta adaptativa, objetivos,
motivación.

**Y expresamente:** el Nivel 1.2 no demuestra que la distancia modifique la
acción. `π_1.2(o,g,s) = π_1.1(o,g)`, por diseño.
