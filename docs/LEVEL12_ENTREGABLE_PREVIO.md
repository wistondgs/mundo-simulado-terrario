# Nivel 1.2 · entregable previo a implementar

Respuesta a la PARTE XII de la especificación. Repositorio inspeccionado en
`experiment/level1-reversal-plasticity-01`, HEAD `ef67ee5`, árbol limpio.

> **VEREDICTO: NO IMPLEMENTAR TODAVÍA.**
> Cinco contradicciones materiales, dos de ellas bloqueantes por sí solas.
> Ninguna obliga a cambiar la capacidad; todas obligan a una decisión tuya.

---

# A · Contradicciones encontradas · punto 20, primero por ser bloqueante

## C1 · La geometría del mundo no admite `δ ∈ {5,6}` · BLOQUEANTE

**Hecho de código.** El mundo del 1.1 usa `grid_size = 7`
([stream.py:109](terrario/level11/stream.py:109),
[measurement.py:69](terrario/level11/measurement.py:69)) y `Grid.random` cierra
el borde entero ([world.py:74-77](terrario/level1/world.py:74)). El interior
libre es por tanto **5×5**, filas y columnas `1…5`.

**Hecho medido** sobre esa geometría:

```
δ máximo entre dos celdas interiores            8
δ máximo desde el centro (3,3)                  4     ← δ=5 y δ=6 imposibles
δ máximo alineado a un eje                      4     ← δ=5 y δ=6 imposibles
posiciones interiores que alcanzan δ ≥ 6     20/25
posiciones interiores que alcanzan δ ≥ 5     24/25
```

§6 define `LEJOS = δ ∈ {4,5,6}`. Si la referencia debe ser una celda de la
rejilla, entonces:

- **con desplazamiento alineado a eje** (la única lectura que hace `G*`
  inequívoca), `δ` no pasa de `4`, y `LEJOS` colapsa a `{4}`;
- **con desplazamiento libre en 2D**, `δ ∈ {5,6}` sólo existe desde posiciones
  periféricas — y la periferia es exactamente donde los bits de pared valen `1`.

Eso produce `P(D \mid o) \neq 0.5` por construcción: **`BODY_DISTANCE_CONFOUNDED`
antes de correr nada**, y el gate L12-5 detectaría un defecto de diseño, no del
organismo.

**Dos salidas, y la decisión es tuya.**

| salida | coste |
|---|---|
| **(a) la referencia es un desplazamiento relativo abstracto, no obligada a caer en la rejilla** | ninguno: el mundo congelado no se toca y el factorial es exacto |
| (b) agrandar la rejilla | **inaceptable**: cambia la distribución de `o`, y con ella el cuerpo 1.0 y la línea base 1.1 |

**Recomiendo (a)**, y creo que ya está latente en tu texto: §4 dice que la
referencia «no bloquea celdas, no puede ser tocada», y §7 pide generar *«un
desplazamiento relativo compatible con ambos»*. Nada exige que `r_t` sea una
celda. Con (a), `r_t = p_t + δ·\text{DELTA}[G^*]` vive en un plano abstracto sin
bordes, `δ ∈ {1,2} ∪ {4,5,6}` es realizable desde **toda** posición, y
`P(D\mid o) = 0.5` y `P(D\mid g) = 0.5` son exactos por construcción.

**No lo implemento hasta que lo confirmes**, porque (a) cambia qué es la
referencia, y eso es parte de la capacidad, no del código.

## C2 · La tolerancia del gate §43 heredada de 1.1 haría fallar una implementación correcta · BLOQUEANTE

§43 pide que los cuatro `H(S_k)` reproduzcan el oráculo *«dentro de tolerancia
preregistrada»* sin fijarla. La tolerancia de 1.1 es `0.02`. **Medido**, sobre
`200 000` realizaciones simuladas de `N = 2048`:

```
max_k |Δ_k|     media 0.0265   p95 0.0489   p99 0.0612   p99.99 0.0892   máx 0.1138

tolerancia   fallo por semilla   fallo en 8 semillas
   0.02           0.66921              0.9999      ←  la de 1.1
   0.05           0.04403              0.3025
   0.08           0.00060              0.0048
   0.10           0.00002              0.0001
```

Con `0.02` el gate cae en **el 99.99 % de las campañas de ocho semillas** aunque
el aprendiz sea exactamente correcto. La razón es que `H(s)` se estima con
`n_s ≈ 461…563` muestras por token, no con las decenas de miles del 1.1.

**Propongo `0.10`**, que es `1.13 ×` el máximo observado en 200 000 réplicas y
deja el riesgo familiar en `1·10⁻⁴`. Es una tolerancia **derivada de la
distribución muestral**, no elegida — exactamente la lección del umbral
inventado de 1.1.

Y una observación que hace el gate más fino: **el Brier es un instrumento mucho
más agudo que la desviación por token**.

```
BS de FULL_12 · media 0.145751 · p99 0.146545      frente a  BS* = 8/55 = 0.1454545
exceso esperado por muestreo = 0.000297  (cerrado: Σ_s P(s)·MSE_s)
```

Sugiero por tanto **dos criterios con tolerancias distintas**: `BS ≤ 0.1480`
(holgado ×5 sobre el exceso esperado) y `max_k|Δ_k| ≤ 0.10`.

## C3 · Los gates L12-4 y L12-5 no pueden fallar · BLOQUEANTE para su valor probatorio

Si el par `(D,G)` se sortea de una lista balanceada construida **antes** de mirar
el mundo (§59, y estoy de acuerdo), entonces `P(D\mid g) = 0.5` y
`P(D\mid o) = 0.5` son **identidades de construcción**, no resultados. Los gates
L12-4 y L12-5 no pueden rechazar nada sobre el generador nominal.

Es exactamente el defecto que ya nos costó una reparación en 1.0 — *«el gate de
generalización sólo podía aprobar por ausencia de prueba»* — y la clase de fallo
que el handoff §5 nombra: **un verificador cuyo caso degenerado es aprobar**.

Tu §62 exige fixture negativa para cobertura, fuga, linaje y factorización
(ítems 31–34) pero **no para estos dos**. Falta:

- un generador que elija `D` condicionado a `g` → L12-4 debe disparar
  `DIRECTION_DISTANCE_CONFOUNDED`;
- un generador que elija `D` condicionado a `o` (p. ej. LEJOS sólo en celdas
  abiertas) → L12-5 debe disparar `BODY_DISTANCE_CONFOUNDED`.

Con ellas los dos gates pasan de *«no puede fallar»* a *«audita el generador»*,
que es lo que realmente son. Los añado salvo que digas lo contrario.

## C4 · «Identidad numérica» en §25 no se sostiene con el instrumento muestreado

**Hecho de código.** `Level11Agent.act` rompe empates consumiendo RNG:

```python
tied = np.flatnonzero(np.isclose(values, values.max()))
return Direction(int(rng.choice(tied)))
```
[agent.py:52-56](terrario/level11/agent.py:52)

`alignment_rate(agent, semantics, rng)`
([metrics.py:85](terrario/level11/metrics.py:85)) muestrea ese desempate;
`alignment_rate_expected(agent, semantics)`
([metrics.py:100](terrario/level11/metrics.py:100)) lo promedia **en cerrado y
sin RNG**. Ésta es la reparación que ya hicimos en 1.1: el muestreo dio `0.5000`
frente a una esperanza de `0.4688` y habría levantado un
`INTEGRATION_MODEL_MISMATCH` falso.

Por tanto el gate L12-8 debe usar **`alignment_rate_expected`**, con el que
`R_align^{pre} = R_align^{post}` es **identidad exacta bit a bit**, no
«equivalencia dentro de tolerancia». Con el instrumento muestreado la identidad
sólo se cumple si además se reinyecta el mismo estado de RNG, y eso es una
propiedad del arnés, no del organismo.

## C5 · No existe envoltorio congelado para `Q`, sólo para `B`

**Hecho de código.** `FrozenFactoredBody` no expone `observe`
([body.py:29-50](terrario/level11/body.py:29)) — ésa es la garantía estructural
del 1.1. Pero `DirectionalAssociation.observe` **sí existe**
([orientation.py:47](terrario/level11/orientation.py:47)) y `Level11Agent`
publica `self.orientation` como atributo
([agent.py:41](terrario/level11/agent.py:41)).

Envolver `Level11Agent` tal cual dejaría `core.inherited.orientation.observe(...)`
al alcance de un descuido. `FrozenLevel11Core` necesita **dos** envoltorios sin
`observe`, no uno. Se construye íntegro en `level12/inherited.py`; `level11/` no
se toca.

## C6 · Tres empates exactos que hay que preregistrar para que no se lean como hallazgos

Cerrados, no medidos:

| empate | por qué |
|---|---|
| `NO_DISTANCE` = `FROZEN_DISTANCE` = **`0.25` exacto** | ambos dan `H(s) = 0.5` para todo `s`; uno por sustitución, otro por prior intacto |
| `FULL_12` = `SENSOR_ONLY` **exactamente** en `BS_distance` | `H` es el único factor que predice distancia; `B` y `Q` no entran en la métrica |
| `SHUFFLED` ≈ `0.2504` ≈ ignorante | barajar lleva `H(s) → 1/2`; el residuo `≈ 0.0004` es varianza de estimación |

El segundo importa: **`BS_distance` no puede demostrar integración**, igual que
`R_align` no podía demostrarla en 1.1. Lo único que la demuestra son los tres
probes de una variable (§24) y la composición triple (§22). Conviene que el
informe lo diga antes de enseñar la tabla, no después.

---

# B · Los veinte puntos

## 1 · Cómo se reconstruye el Nivel 1.1 congelado

**No hay snapshot.** Barrido de `terrario/level1*/`, `scripts/level11*` y
`artifacts/`: no existe `pickle`, `np.save`, `torch.save` ni `json.dump` de
estado. `artifacts/level11/` contiene sólo `verification.txt`, que es texto.

Por tanto **se reconstruye**, de forma determinista, con la receta exacta de
`run_seed` ([experiment.py:152-168](terrario/level11/experiment.py:152)):

```python
semantics = CueSemantics.identity()
holdout   = build_holdout(semantics, seed=0)          # congelado, no por semilla
body      = train_body(σ)                              # 8192 transiciones, FEATURES
stream    = orientation_babbling(σ + 7, n=2048, semantics=semantics, holdout=holdout)
q         = train_orientation(stream, semantics)
```

**Precondición, no adquisición:** antes de congelar se verifican sobre `σ` los
criterios 1.1 — cobertura informativa `≥ 30`, `0` violaciones físicas, `0` fugas
de holdout, y `BS_balanced(COMPOSITE) ≈ 0`. Si no se cumplen:
`LEVEL11_BASELINE_REGRESSION`, y la semilla se excluye **antes** de tocar 1.2.

## 2 · Fingerprints

- **Cuerpo (1.0):** `FrozenFactoredBody.digest()` ya existe
  ([body.py:39](terrario/level11/body.py:39)) — SHA-256 sobre `_belief`,
  `_base`, `_feature`.
- **Orientación (1.1):** **no existe**. Se añade en `level12/inherited.py` con la
  misma forma, sobre `DirectionalAssociation._belief`.
- **Compuesto:** `FrozenLevel11Core.fingerprint()` = SHA-256 de los dos anteriores
  concatenados.

**Comparación intra-corrida, no contra constante dorada.** El cuerpo depende de
`σ`, así que el criterio es `fingerprint_antes == fingerprint_después` dentro de
cada semilla — el mismo criterio que usó 1.1 y que dio `True` en las ocho.

## 3 · Ficheros exactos a crear

```
terrario/level12/__init__.py
terrario/level12/reference.py      referencia latente, δ, clase física, sensor
terrario/level12/proximity.py      QualitativeDistanceModel · H(s)
terrario/level12/inherited.py      FrozenLevel11Core · dos envoltorios sin observe
terrario/level12/agent.py          Level12Agent · predict_distance, act, predict_joint
terrario/level12/stream.py         generador factorial (D,G) y experiencias
terrario/level12/metrics.py        Brier, posteriors, probes, matriz de confusión
terrario/level12/experiment.py     seis brazos + oráculo Bayes + run_seed
scripts/level12_qualitative_distance.py
tests/test_level12_lineage.py
tests/test_level12_distance.py
docs/LEVEL12_ORACULO_PREREGISTRADO.md      sellado ANTES de ejecutar
```

Nada más. `terrario/level12/world.py` **no se crea**: se importa
`terrario.level11.world`, que es copia literal del 1.0 y está bajo contrato de
linaje.

## 4 · Cero modificaciones a `level1/` y `level11/`

Confirmado y comprobable: los tests de linaje ya existentes
(`tests/test_level11_lineage.py`) verifican la identidad literal de
`world/models/measurement`. Se añade a `test_level12_lineage.py` la comprobación
de que `terrario/level12/` **no importa nada mutable** de los niveles previos:
sólo tipos, `Grid`, y las clases que se envuelven.

Verificación de cierre: `git diff --stat ef67ee5 -- terrario/level1 terrario/level11`
debe salir vacío.

## 5 · Representación de la referencia latente

Sujeto a **C1**. Bajo la salida (a):

```python
@dataclass(frozen=True)
class Reference:
    offset: tuple[int, int]      # desplazamiento relativo al agente
    direction: Direction         # G*, inequívoca porque el offset es axial
    delta: int                   # δ = |offset|, Manhattan
    truth: DistanceTruth         # N o F
```

No se almacena `r_t` absoluto: **la referencia es el desplazamiento**. Eso hace
estructuralmente imposible derivar `p_t` de ella, y elimina la necesidad de que
caiga dentro de la rejilla.

## 6 · Algoritmo de generación independiente

```
1. construir la lista exacta de 2048 pares (D,G): 256 por cada una de las 8 combinaciones
2. barajarla con rng_pairing
3. para cada ensayo, en orden:
     δ  ~ uniforme{1,2}   si D = N      ·   uniforme{4,5,6}   si D = F     (rng_reference)
     offset = δ · DELTA[G]
     s  ~ fila D de la matriz de emisión                                    (rng_sensor)
     o  ← se lee del mundo, DESPUÉS, y no participa en ninguna elección anterior
     g  ← el token direccional del 1.1, sorteado con su propio RNG
```

`δ = 3` y `δ = 0` **nunca se generan**: no hay que excluirlos a posteriori, no
existen. Por construcción `P(D\mid g) = P(D\mid o) = 0.5` exactos — y por eso
C3 exige las fixtures negativas.

**Nota:** el desplazamiento es **axial** (`offset` sobre un solo eje). Es la
única lectura bajo la que `G*` es inequívoca; con un offset diagonal, `(-3,-3)`
tiene `δ=6` y ninguna dirección única. Si prefieres offsets diagonales, hace
falta una regla explícita de proyección y deja de ser cerrado. **Lo declaro como
decisión pendiente, no la tomo.**

## 7 · Matriz de emisión exacta

```
clase      S0     S1     S2     S3      suma
CERCA    0.05   0.15   0.30   0.50      1.00
LEJOS    0.50   0.30   0.15   0.05      1.00
```

Verificado: cada fila suma exactamente `1`. Vive en `reference.py`, sólo la
conoce el mundo experimental, y hay contrato que comprueba que
`QualitativeDistanceModel` no la importa.

## 8 · Separación `Observation` / `TrainingRecord`

Dos tipos, no un campo opcional:

```python
@dataclass(frozen=True)
class DistanceObservation:          # lo ÚNICO que llega a predict()
    observation: Observation
    cue: CueToken
    sensor: ProximityToken

@dataclass(frozen=True)
class DistanceTrainingRecord:       # registro experimental
    view: DistanceObservation
    truth: DistanceTruth
    reference: Reference
```

`predict*` acepta `DistanceObservation` y nada más. `truth` y `reference` sólo
son alcanzables desde el registro, que el agente nunca recibe. La fuga deja de
ser una cuestión de disciplina y pasa a ser un `AttributeError`.

## 9 · Implementación exacta de `H(s)`

```python
class QualitativeDistanceModel:
    def __init__(self, *, prior_alpha=1.0, prior_beta=1.0, frozen=False):
        self._alpha = np.full(4, prior_alpha)
        self._beta  = np.full(4, prior_beta)

    def predict_near(self, sensor: ProximityToken) -> float:
        k = int(sensor)
        return self._alpha[k] / (self._alpha[k] + self._beta[k])

    def observe(self, sensor: ProximityToken, target: DistanceTruth) -> bool:
        if self.frozen: return False
        k = int(sensor)
        if target is DistanceTruth.NEAR: self._alpha[k] += 1
        else:                            self._beta[k]  += 1
        return True
```

Firma cerrada a cuatro entradas: **no acepta** `o`, `g`, acción, coordenadas ni
`δ`. Y a diferencia del 1.1, los acumuladores son arrays de tamaño fijo, no un
`dict`: **`predict` no puede insertar la celda que lee** — el defecto del 1.0
deja de ser posible por tipo, no por cuidado.

## 10 · Oráculo Bayes, calculado independientemente

`BayesDistanceOracle` **no aprende** y **no ve** `D^*` en inferencia: recibe la
matriz de emisión y devuelve

```
H*(s) = P(s|N) / (P(s|N) + P(s|F))          con P(N) = P(F) = 1/2
```

Se implementa con `fractions.Fraction` y se compara contra la constante sellada.
**No se usa `D^*` como oráculo de predicción**, como bien señalas en §31: eso
daría Brier `0` y excedería la información accesible.

## 11 · Prueba de `BS* = 0.1454545`

Calculado en aritmética exacta:

```
H*(S_k) = 1/11, 1/3, 2/3, 10/11        → 0.090909, 0.333333, 0.666667, 0.909091   ✓
P(S_k)  = 0.275, 0.225, 0.225, 0.275   suma 1                                      ✓
```

Para un predictor calibrado, `E[(H−y)²] = E_s[H*(s)(1−H*(s))]`, luego

```
BS* = 2·(0.275 · 1/11 · 10/11) + 2·(0.225 · 1/3 · 2/3)
    = 2·(0.02272727) + 2·(0.05)
    = 8/55  =  0.145454545454…                                                     ✓
```

**Es exacto, `8/55`, no aproximado.** Y un segundo valor que tu §17 da como
aproximado también es exacto:

```
Accuracy* = Σ_s P(s)·max(H*, 1−H*) = 4/5 = 0.80 exacto                             ✓
```

## 12 · Cobertura para `N = 2048`

Con `1024` por clase exactos, `n_{D,s} \sim \text{Bin}(1024, p_{D,s})`.

```
celda más rara   p = 0.05   E[n] = 51.2
P(Bin(1024,0.05) ≤ 29) = 4.108·10⁻⁴                            ✓ coincide con tu 4.1·10⁻⁴
```

**Matiz.** Tu cota de unión usa las ocho celdas y da `3.29·10⁻³`. Es correcta
pero holgada: sólo **dos** celdas tienen `p = 0.05`; las otras seis van de
`0.15` a `0.50` y su riesgo es despreciable. La cota ajustada es
`2 × 4.108·10⁻⁴ = 8.2·10⁻⁴` por semilla, y sobre ocho semillas
**`≈ 0.0066`**. Medido por simulación: `0.0070`. Coinciden.

Conclusión: `2048` está bien dimensionado, y hay que preregistrar que
**≈ 1 de cada 150 campañas de ocho semillas excluirá una** por
`INSUFFICIENT_DISTANCE_DOSE`. Es exclusión esperada, no fracaso.

## 13 · Diseño del `SHUFFLED` correcto

```python
vistos = [r.view.sensor for r in registros]
vistos = [vistos[i] for i in rng_shuffle.permutation(len(vistos))]
for r, sensor_visto in zip(registros, vistos, strict=True):
    modelo.observe(sensor_visto, r.truth)      # la VERDAD sigue siendo la del ensayo
```

El aprendiz ve el sensor **de otro ensayo** mientras la verdad física sigue
perteneciendo al suyo. **No se permuta sensor y significado juntos**: eso fue
exactamente el defecto de 1.1, donde el control empataba con el brazo principal
porque yo había hecho un reetiquetado consistente.

Predicción cerrada: `H(s) → 1/2`, `BS ≈ 0.2504`. **El tell de que está bien
hecho es que `SHUFFLED` empata con el ignorante, no con `FULL_12`.**

## 14 · Fixture de permutación de tokens

Aplicar una permutación `π` **a los nombres y a la matriz de emisión a la vez**:
la fila de `CERCA` pasa de `[0.05,0.15,0.30,0.50]` a la misma fila reordenada por
`π`. El aprendiz debe recuperar los mismos cuatro posteriors **atados a los
tokens nuevos**: `H(π(S_k)) = H*(S_k)` dentro de la misma tolerancia.

Esto **no** contradice §13: aquí el reetiquetado consistente es precisamente lo
que se quiere (invariancia al nombre); en el control barajado es lo que hay que
evitar (destrucción de información). Son dos pruebas distintas y ambas necesarias.

**Fixture negativa obligatoria:** un aprendiz que presuponga orden ordinal —
p. ej. que inicialice `H(S_k) = k/3` en vez de `1/2` — debe **fallar** esta
prueba. Sin ese negativo, la prueba no prueba.

## 15 · Fixture de factorización falsa

Tu propuesta de §38 es **exactamente maximal**, y es un resultado cerrado, no una
elección. Invirtiendo la emisión (`S_0 \leftrightarrow S_3`,
`S_1 \leftrightarrow S_2`) para dos de los cuatro valores de `g`:

```
marginal:  P(s|N) = P(s|F) = [0.275, 0.225, 0.225, 0.275]  para las dos clases
           →  H(s) = 1/2 EXACTO en los cuatro tokens
           →  BS(H(s))   = 1/4     = 0.250000     (ignorancia total)
           →  BS(H(s,g)) = 8/55    = 0.145455     (recupera todo)
```

El modelo marginal no se degrada: **se anula**. Y el criterio es un contraste
contra el propio `BS*`, no un umbral inventado — la lección del `0.05` que yo
había elegido en 1.1.

Si con esta fixture el gate de factorización sigue aprobando:
`FACTORING_GATE_NOT_FALSIFIABLE`. La fixture **no pertenece al mundo nominal**.

## 16 · Los tres probes de una variable

Los tres en cerrado, sin RNG y sin promedios, extendiendo `factorial_probe`
([metrics.py:140](terrario/level11/metrics.py:140)):

| probe | se fija | varía | debe moverse | debe quedar EXACTAMENTE igual |
|---|---|---|---|---|
| corporal | `g, s` | `o` | `B`, y `J_N`,`J_F` | `Q`, `H` |
| direccional | `o, s` | `g` | `Q`, y `J_N`,`J_F` | `B`, `H` |
| distancia | `o, g` | `s` | `H`, y `J_N`,`J_F` | `B`, `Q` |

Los ceros deben ser **exactos**, como en 1.1 (`BODY-ONLY` cue `+0.000`,
`CUE-ONLY` cuerpo `−0.000`). Una desviación distinta de cero en el factor que no
debe moverse es `PREVIOUS_KNOWLEDGE_MUTATED`.

**Y una propuesta que dejo a tu criterio.** §46 pide que la composición triple
«responda consistentemente», que todavía no es una operacionalización. Bajo el
generador nominal, `D \perp (o,g)`, así que `J_N = B·Q·H` es una probabilidad
conjunta **genuinamente calibrada** de `(se mueve ∧ alineado ∧ CERCA)`. Eso
permite puntuarla con un Brier estratificado contra el indicador triple, con
oráculo cerrado — un gate que sí puede fallar. **No lo implemento sin que lo
adjudiques**: es una métrica nueva, y las métricas nuevas son decisión tuya.

## 17 · Esquema completo de RNG

Se adopta el patrón ya usado en 1.1, `default_rng([σ, k])`
([stream.py:100-102](terrario/level11/stream.py:100)), que es libre de colisión
por construcción — mejor que sumar desplazamientos enteros.

```
heredados (los consume la reconstrucción 1.1, no 1.2):
  train_body(σ)                  → motor_babbling(σ)
  orientation_babbling(σ+7)      → [σ+7, 1] mundo · [σ+7, 2] acto · [σ+7, 3] señal

nuevos de 1.2:
  [σ, 21]  rng_pairing     baraja la lista factorial (D,G)
  [σ, 22]  rng_reference   δ dentro de la clase
  [σ, 23]  rng_sensor      emisión del token
  [σ, 24]  rng_readout     sondas y lecturas
  [σ, 25]  rng_shuffle     control barajado
```

Ninguna sonda consume RNG de adquisición. Los probes y
`alignment_rate_expected` son cerrados y no consumen ninguno.

**Espacio de semillas.** Ya consumidos: `20260919…` (1.0), `31415926` (quemada),
`31415927…31415958` (reversión), `70000019…70000033` (1.1, incluyendo los
desplazamientos `+7`). Propongo para 1.2 **`80000011 … 80000018`**, ocho
semillas, verificadamente disjuntas de todo lo anterior incluidos sus
desplazamientos derivados.

## 18 · Gates

Los once de tu PARTE VII, con dos criterios cuantificados que faltaban:

| gate | criterio | de dónde sale |
|---|---|---|
| L12-0 linaje | `fingerprint_antes == fingerprint_después` | identidad exacta |
| L12-1 observabilidad | fixture de fuga deliberada detectada | negativo obligatorio |
| L12-2 cobertura | `min_{D,s} n_{D,s} ≥ 30` | §20, riesgo `0.0066` en 8 |
| L12-3 adquisición | `FULL < FROZEN`, `< NO_DISTANCE`, `< SHUFFLED`; y `BS ≤ 0.1480` | **derivado**, exceso esperado `0.000297` |
| L12-4 semántica del sensor | `max_k|Δ_k| ≤ 0.10` | **derivado**, p99.99 `= 0.0892` |
| L12-5 dirección–distancia | `P(D\mid g) = 0.5` · **+ fixture negativa** | C3 |
| L12-6 cuerpo–distancia | `P(D\mid o) ≈ 0.5` · **+ fixture negativa** | C3 |
| L12-7 integración | tres probes, ceros exactos | §24 |
| L12-8 preservación motora | `R_align^{pre} ≡ R_align^{post}` con el instrumento **cerrado** | C4 |
| L12-9 falsabilidad | fixture falsa: `BS(H(s)) = 0.25`, `BS(H(s,g)) = 8/55` | §38, cerrado |
| L12-10 pasividad | huella idéntica tras medir; RNG independientes | §49 |

## 19 · Fixtures negativas

Una por gate, **sin excepción** — la regla del handoff §5. Tus 34 tests cubren
la mayoría; añado las que faltan:

```
· generador con D condicionado a g            → L12-5 debe disparar
· generador con D condicionado a o            → L12-6 debe disparar
· aprendiz con prior ordinal H(S_k)=k/3       → L12-4 debe disparar
· core heredado con observe() alcanzable      → L12-0 debe disparar
· predict() que acepte DistanceTrainingRecord → L12-1 debe disparar
· métrica que escriba en el modelo            → L12-10 debe disparar
```

## 20 · Contradicciones

Sección A. Cinco, más seis empates a preregistrar.

---

# C · Sobre tus tres consultas

Coincido con tu recomendación: **ninguna de las tres entra en 1.2**.

1. **Otra matriz de emisión.** Mide recalibración, que es una pregunta distinta
   de adquisición. Además tiene una virtud que conviene reservar: sería el primer
   sitio del linaje donde la respuesta **no se puede calcular antes de correr**,
   y por tanto el primer candidato legítimo a 32 semillas con bootstrap.
2. **Que CERCA/LEJOS cambie la acción.** De acuerdo: es otra adquisición. Tu §23
   lo protege bien, y es la protección la que hace atribuible el resultado.
3. **Bandas ordinales.** Cambia el constructo de binario a ordinal y con él todo
   el oráculo. Decimal posterior.

---

# D · Una advertencia sobre lo que 1.2 podrá afirmar

No es una objeción al diseño; es un límite que conviene escribir ahora y no
después de ver la tabla.

Como el sensor depende **sólo de la clase** `N/F` y no de `δ`, y la clase se
sortea con independencia del mundo, la tarea que el organismo resuelve es
exactamente: **estimar cuatro parámetros de Bernoulli a partir de 2048 muestras
i.i.d. de una mezcla de dos componentes**. La geometría —Manhattan, la
referencia, el margen en `δ=3`— es andamiaje del **constructo**, no del
**cómputo**: ningún gate mide que `δ` exista.

Eso no invalida nada. Sí fija de qué clase es el hito, igual que en 1.1: la
adquisición nueva son `log₂(4!) = 4.58` bits de correspondencia en el 1.1 y aquí
**cuatro parámetros continuos con techo irreducible**. Lo genuinamente nuevo de
1.2 frente a 1.1 es **la incertidumbre irreducible**: por primera vez el techo no
es `0`, y el organismo debe acercarse a `8/55` en vez de a la perfección. Ése es
el avance, y es real.

La afirmación de tu PARTE XI es correcta tal como está. Sólo añadiría, junto a
las prohibiciones, esta línea:

> El Nivel 1.2 no demuestra que el organismo represente distancia: demuestra que
> distingue probabilísticamente dos clases de proximidad a partir de evidencia
> ambigua. La métrica de la distancia la impone el experimentador.
