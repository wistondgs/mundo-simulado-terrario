# Nivel 1.4 · entregable previo a implementar

Auditoría de `LEVEL1.4-CONJUNCTIVE-BINDING-01` contra el repositorio real.
Inspeccionado: `experiment/level1-reversal-plasticity-01`, HEAD `7ac43fb`.

> **VEREDICTO: NO IMPLEMENTAR TODAVÍA.**
> Seis hallazgos, tres bloqueantes. Ninguno obliga a cambiar la capacidad.
>
> **Tu aritmética es exacta, las siete cifras.** Y el canal de portadores
> sobrevive el ataque que pediste — pero por una razón que sólo está demostrada
> en el banco de adquisición, no en el de evaluación.

---

# A · Tu pregunta primero · ¿es `X`/`Y` un `object_id` disfrazado?

**No lo es, y la razón es verificable.** Con el banco de §12 --las 16
combinaciones `(g,s)` por cada portador-- medido en aritmética exacta:

```
P(G | X) = 1/4     EXACTO para los cuatro portadores
P(S | X) = 1/4     EXACTO
```

El portador no carga **ninguna** información sobre los atributos. Ese es el
punto que temías y aguanta.

**Pero conviene nombrar bien lo que sí es.** `ψ` es una biyección **fija que
persiste en todos los ensayos**. Lo que el organismo aprende es una tabla
permanente: «`x0` va con `y2`». Dentro de una escena, `x0` y `y2` son **la misma
etiqueta escrita en dos alfabetos**.

La distinción que aguanta frente a «identidad de objeto» es ésta:

| | persiste | qué designa |
|---|---|---|
| `object_id` | la ligadura al **referente** | la misma cosa, ensayo tras ensayo |
| portador `X`/`Y` | la ligadura `x ↔ ψ(x)` | un **canal**, cuyo contenido cambia entero cada ensayo |

La analogía justa: **dos frecuencias de radio que se sabe que llevan la misma
emisión.** Saber cuáles se emparejan es conocimiento real --`log₂(4!) = 4.585`
bits-- y no dice absolutamente nada sobre qué se está emitiendo.

**Y el límite honesto:** una vez conocida `ψ`, el binding es **consulta de tabla,
no inferencia**. Hay dos elementos y dos asignaciones posibles; el agente toma un
argmax sobre dos productos. Es binding en su tamaño mínimo no degenerado, con un
bit de margen. No está mal --es lo mismo que en 1.1 y 1.3--, pero la afirmación
de §52 debe decir «dos referencias simultáneas» y no dejar entender binding a
nivel de escena.

---

# B · Hallazgos

## C1 · El banco de evaluación no está especificado, y ahí vive el atajo · BLOQUEANTE

§12 especifica el banco de adquisición con precisión quirúrgica: 64 escenas, y el
balance `P(G|X) = P(S|X) = ¼` sale **exacto**. §14 define los mundos `A` y `B`
pero **no dice qué contiene el banco de evaluación**: ni cómo se enumeran
`(x₁,x₂,g₁,g₂,s₁,s₂)`, ni --lo decisivo-- que `A` y `B` aparezcan en igual
número.

**Por qué es lo más grave de la lista.** Si el banco evaluara sólo el mundo `A`,
un *index-binder* --emparejar `directions[0]` con `proximities[0]`-- acertaría
siempre, y la métrica de §17 no podría distinguirlo de `FULL`. **La simetría
`A`/`B` es exactamente lo que mata ese atajo**, y es lo que falta escrito.

Y hay un segundo agujero por la misma vía: `P(G|X) = P(G)` está demostrado para
la adquisición y **no demostrado para la evaluación**. Si en las escenas de dos
referencias `x₁` fuera sistemáticamente con `g₁`, el portador sí sería una
etiqueta de atributo ahí — que es precisamente el `ATTRIBUTE_IDENTITY_LEAK` de
§30, entrando por la puerta que ese gate no vigila.

**Propuesta:** enumerar el banco de evaluación explícitamente y demostrar su
balance, incluyendo paridad `A`/`B` exacta, igual que se hizo con el de
adquisición.

## C2 · No existe envoltorio congelado para `H` · y es la tercera vez · BLOQUEANTE

**Hecho de código:**

```
terrario/level12/proximity.py:45   QualitativeDistanceModel.observe(...)   ← existe
terrario/level12/agent.py:32       self.proximity = proximity              ← público
```

Envolver `Level12Agent` tal cual dejaría `core.proximity.observe(...)` al alcance
de un descuido. `FrozenLevel12Core` necesita **tres** envoltorios, no dos.

**Y conviene ver el patrón, porque se repite con precisión:**

```
1.1  construyó FrozenFactoredBody     para B, que creó 1.0
1.2  construyó FrozenDirectional      para Q, que creó 1.1
1.3  volvió a construir FrozenDirectional  (otra vez, desde cero)
1.4  tendrá que construir FrozenProximity  para H, que creó 1.2
```

**Cada nivel congela lo que heredó y deja mutable lo que añade.** El resultado es
que cada decimal paga el mismo peaje y lo escribe otra vez.

**Sugerencia de proceso, para ti:** que el nivel que **añade** un modelo entregue
también su envoltorio congelado, como parte de su propio cierre. El 1.2 habría
entregado `FrozenProximity` y el 1.4 no tendría que inventarlo. No cambia ninguna
capacidad y elimina una reincidencia estructural.

## C3 · Las 192 celdas de §45 son un solo número · BLOQUEANTE para el informe

**Medido:** las `24` permutaciones de `ψ` producen **un valor distinto**. Uno.

```
valores distintos de (C, P(binding), BS) entre las 24 permutaciones:  1
```

Y no es sorprendente: el banco de adquisición es determinista dado `ψ`, y la
estructura es simétrica bajo relabelado. Además **el binder no lee `B`, `Q` ni
`H` durante la adquisición**, así que `A_xy` es idéntica también en las ocho
líneas base. Y el readout funcional tampoco depende del etiquetado de `ψ`.

Consecuencia: `BS_binding` vale literalmente lo mismo en las 192 celdas. Lo único
que varía es el readout, y varía sólo entre las **8** líneas base, a través de su
`H` y su `Q`.

**Propuesta:** las 24 permutaciones son un **contrato parametrizado** --«la
implementación no puede tener `ψ` cableada»-- y van a la suite de tests. La
campaña son 8 celdas. Presentar 192 como 192 comprobaciones sobreestimaría por un
factor de 24.

## C4 · §31 es invacuable con `frozenset`

§31 exige invariancia a permutar el orden de los dos elementos de cada modalidad.
Con `frozenset` (§41) eso es cierto **por construcción**: dos frozensets con los
mismos elementos son el mismo objeto, se construyan en el orden que se
construyan. **El test no puede fallar nunca.**

Es la misma forma que L12-5 y L13-2: un gate cuyo único comportamiento posible es
aprobar. Lo que sí tiene contenido es el negativo de §32 — y para que el
*index-binder* exista hay que darle una representación **ordenada** propia
(lista o tupla) y enseñar que cae al permutar esa lista. La fixture necesita su
propio tipo de escena.

## C5 · `frozenset` tampoco puede contener duplicados

Si los dos elementos direccionales compartieran `(carrier, cue)`, el conjunto
colapsa a uno y la escena pasa a tener **una** referencia en silencio — que es
justo lo que §34 manda rechazar como `BINDING_CONSTRUCT_NOT_FALSIFIABLE`. Hace
falta un contrato en la construcción: exactamente dos de cada, comprobado.

## C6 · §17 no es un Brier score, es un error cuadrático condicionado

`BS = (P − 1)²` presupone que el mundo `A` es el verdadero. Sobre un banco
simétrico en `A`/`B` coincide con el Brier por simetría — pero esa simetría es
exactamente lo que §14 no declara (**C1**). O se sella la paridad, o la métrica
se renombra a lo que es.

---

# C · Verificaciones contra el repositorio

```
7ac43fb                        = cierre implementado de 1.2 · CONFIRMADO
level13 alcanzable desde ahí   = NO · la rama 1.3 sale de ef67ee5, es hermana
terrario/ en 7ac43fb           = level1 level11 level12 (sin level13) ✓
semillas 100000011…100000025   = colisión con lo usado: NINGUNA
```

Y tu propia regla de hace dos mensajes: **1.4 necesita su propio worktree**,
creado desde `7ac43fb`. Entonces «cero dependencia de 1.3» es estructural — en
ese disco `terrario/level13/` no existe— y no una aserción del informe.

## Aritmética sellada · verificada en fracciones

```
C(ψ(x)|x) = 17/20        C(y≠ψ(x)|x) = 1/20        fila = 20              ✓
P(binding correcto) = 289/290 = 0.996551724…                              ✓
BS_binding FULL = 1/84100 = 1.1890606e-05                                 ✓
SHUFFLED: A_xy = 5 ∀xy → C = 1/4 → P = 1/2 → BS = 0.25, varianza cero     ✓
N_binding = 64 · P(G|X) = P(S|X) = 1/4 exacto                             ✓
MSE readout UNBOUND = 0.06504438   (decías 0.0650)                        ✓
MSE readout FULL    = 3.0936686e-06 (decías 3.1e-6)                       ✓
log₂(4!) = 4.585 bits                                                     ✓
```

**Las siete cifras que sellaste son correctas.** No he encontrado ni una
desviación.

---

# D · Los 32 puntos de tu §54

| # | respuesta |
|---|---|
| 1 | worktree propio desde `7ac43fb`, rama `experiment/level14-conjunctive-binding-01` |
| 2 | `LEVEL12_STATUS = VERIFIED`, 8 semillas, peor desviación `0.0612` vs tolerancia `0.10` |
| 3 | reconstrucción determinista: `level12.experiment.run_seed`; **no hay estado persistido** |
| 4 | `FrozenFactoredBody.digest` + `FrozenDirectional.digest` + **`FrozenProximity.digest` (a crear, C2)** |
| 5 | estructural: `terrario/level13/` no existe en `7ac43fb`; más contrato de imports por AST |
| 6 | `Enum` con valores string, dos tipos disjuntos, sin ordinal compartido — **nunca `IntEnum`** |
| 7 | `ψ` como `dict[DirectionCarrier, ProximityCarrier]`, biyección verificada; 24 instancias parametrizadas |
| 8 | 64 escenas enumeradas, sin RNG |
| 9 | demostrado exacto: `P(G|X) = P(S|X) = ¼` (adquisición). **Falta el mismo para evaluación, C1** |
| 10 | `A_xy` array `4×4`, prior 1, `observe_single_reference(x, y)` y nada más en la firma |
| 11–13 | verificados en fracciones, arriba |
| 14 | `UNBOUND` no recibe `C(y\|x)`: por simetría `P(A)=P(B)=½`. No inventa asociación |
| 15 | banco donde cada `x` coocurre 4 veces con cada `y` ⇒ `A_xy = 5 ∀` ⇒ exacto, sin muestreo |
| 16 | **pendiente de C1**: hay que enumerarlo y demostrar paridad `A`/`B` |
| 17 | `frozenset`, con contrato de cardinalidad 2 (**C5**) |
| 18 | el *index-binder* necesita un tipo de escena **ordenado** propio (**C4**) |
| 19 | `P(G\|X)=P(G)` en los dos bancos + ausencia de `object_id`/`entity_id` por AST |
| 20 | `V(a) = Σ_i Q(g_i,a)·ĥ_i` contra un **ORACLE-BINDER con el mismo `H`** — tu §23, y es correcto |
| 21 | tres sondas con ceros cruzados exactos, como en 1.2 y 1.3 |
| 22–25 | las cuatro fixtures, con **C4** aplicada a la del índice |
| 26 | de acuerdo en excluir el holdout: `ψ` no indexa `(g,s)`, aprobaría por arquitectura |
| 27 | **cero RNG nuevo**: adquisición enumerada, 24 permutaciones enumeradas, métricas cerradas |
| 28 | `100000011…100000018`, disjuntas (verificado, incluidos los `+7`) |
| 29–30 | los once gates, cada uno con negativo; **C4** convierte el de orden en falsable |
| 31 | los de tu §39, más `FrozenProximity` |
| 32 | sección B |

---

# E · Lo que necesito de ti

1. **C1** — ¿enumero el banco de evaluación con paridad `A`/`B` exacta y demuestro
   su balance `P(G|X)`? *(recomiendo sí: sin ello el atajo de índice es
   indetectable)*
2. **C3** — ¿las 24 permutaciones van a la suite como contrato, y la campaña son 8
   celdas? *(recomiendo sí)*
3. **C4** — ¿la fixture del index-binder recibe un tipo de escena ordenado propio?
   *(recomiendo sí: con `frozenset` el gate no puede fallar)*
4. **C6** — ¿sello la simetría `A`/`B` y mantengo el nombre `BS_binding`, o lo
   renombro? *(recomiendo sellar la simetría)*
5. **Proceso** — ¿el nivel que añade un modelo entrega también su envoltorio
   congelado, de aquí en adelante? *(recomiendo sí; evitaría la tercera
   reincidencia)*

Con esas cinco, el preregistro sale en commit separado antes de una sola línea de
código.
