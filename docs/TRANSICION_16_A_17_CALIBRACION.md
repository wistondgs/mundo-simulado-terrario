# Transición 1.6 → decimal siguiente · correcciones y banco de calibración

**Fecha:** 2026-09-20 · **El handoff `e590d65` permanece congelado y no se edita.**
Este documento es aditivo y corrige tres afirmaciones suyas.

**No diseña ninguna capacidad.** Mide física e interroga contratos.

---

# 1 · Una aserción vacua que envié · corregida

`scripts/medir_dependencia_accion.py` comparaba

```python
conditional.mean(axis=1)  ==  twin.mean(axis=1)
```

donde `twin = np.repeat(conditional.mean(axis=1)[:,None,:], 4, axis=1)`. **Es
cierto por construcción.** Demostraba un kernel *observacional* fabricado para ser
gemelo, no un mundo B. Y en el handoff §14.2 lo describí como «verificado sobre la
física real», que es una afirmación más fuerte de lo que el código sostenía.

Es la **sexta aserción vacua** del linaje y la segunda que yo mismo listo en §10
del handoff como clase de defecto conocida.

## 1.1 · La verificación física, con las tautologías marcadas

`T_B(s'|s,a) = ¼ Σ_b T_A(s'|s,b)` construido sobre el kernel de **estados**, y
proyectado al espacio sensorial por el mismo camino que A:

```
semilla 140000011 (20 celdas)
  [tautológico] T_B(·|s,a_i) == T_B(·|s,a_j)     True
  [tautológico] Σ_a T_A/4 == Σ_a T_B/4            True
  [prueba algo] I(O;O') conservada exacta         0.9356 → 0.9356
  [prueba algo] I(A;O'|O) anulada                 1.0678 → 0.000e+00

semilla 140000014 (3 celdas)   I(O;O') 0.3771 → 0.3771   ·  I_A 0.7215 → 0
semilla 140000025 (2 celdas)   I(O;O') 0.1308 → 0.1308   ·  I_A 0.5623 → 0

estacionaria idéntica · máxima diferencia 0.00e+00
```

Las dos últimas **no** son obvias a priori: el mapa de observación aliasa celdas y
podría haber interactuado con la marginalización. No lo hace. A precisión de
máquina, **B es idéntico a A en todo lo que 1.6 mide y no lleva información de
acción alguna.**

Ahora sí se puede escribir *gemelos físicos A/B exactos*.

---

# 2 · El predicado estructural · la separación hace falta, pero no donde yo diría

El handoff §13 dice que `structure.py` y `seeds.py` «no dependen de la capacidad».
**Es incorrecto como principio**, y la corrección tiene un matiz que vale la pena
medir antes de escribirla en un oráculo.

## 2.1 · En la física A, el predicado de 1.6 ya implica dependencia de acción

```
mundos válidos para 1.6 examinados    3 915
de esos, con D_W == 0                     0
D_W mínimo observado                 0.4757
```

Añadir una exclusión `D_W > ε` al consumo de semillas del mundo A sería **un gate
cuyo único comportamiento posible es PASS** — lo que este linaje decidió hace
varios decimales que no es un gate.

## 2.2 · Pero en el mundo B, `D_W = 0` y el predicado de 1.6 pasa

Ése es el caso que obliga a separar, y es decisivo: B tiene estructura temporal
sensorial completa —`I(O;O')` idéntica a la de A— y cero información de acción. Un
predicado que sólo pregunte por estructura temporal lo declara válido.

**Sin la separación, la ausencia de dependencia de acción en B se leería como
`N-EXPERIENCIA`**, que es evidencia sobre S0. Sería atribuir al sustrato un vacío
que es del mundo.

## 2.3 · Forma propuesta · contrato de construcción, no exclusión de muestreo

```
N-MUNDO_físico      |O_alcanzables| < 2        heredado de 1.6, sin cambios
contrato de A       D_W > 0                    verificado; nunca excluye (0/3915)
contrato de B       D_W == 0 exactamente       verificado; SÍ puede fallar si el
                                               gemelo se construye mal
```

El de B es el que puede caer, y por tanto el único de los dos que es un gate de
verdad.

---

# 3 · El banco de calibración · y lo que mi §14 afirmaba de más

El script recorría `consume_seeds().lives`, es decir **las 16 semillas
confirmatorias de 1.6**. Eso contesta «cuánta dependencia había en los 16 mundos
que usamos», no «cuál es la distribución en la clase de mundos».

## 3.1 · Ventanas registradas

```
1.6 confirmatorias    140000011 … 140000042     consumidas · congeladas
1.7 calibración       150000011 … 150000522     512 · usadas AQUÍ
1.7 confirmatorias    160000011 … 160000074     64 · RESERVADAS, sin medir

intersecciones entre las tres: NINGUNA
```

Las de calibración **no** podrán usarse como confirmatorias, y las confirmatorias
**no** se han mirado.

## 3.2 · Distribución poblacional · 500 mundos válidos de 512 (`N-MUNDO` 0.0234)

| magnitud | media | sd | mín | p25 | p50 | p75 | máx |
|---|---|---|---|---|---|---|---|
| `D_W = I(A;O'\|O)` | **0.9127** | 0.0983 | 0.5623 | 0.8414 | 0.9165 | 0.9945 | 1.1417 |
| `H(O'\|O)` | 1.2411 | 0.1405 | 0.5623 | 1.1793 | 1.2663 | 1.3295 | 1.5464 |
| `H(O'\|O,A)` | 0.3284 | 0.1351 | 0.0000 | 0.2476 | 0.3491 | 0.4270 | 0.6402 |
| `H(O'\|C)` | 1.0113 | 0.0804 | 0.5623 | 0.9728 | 1.0179 | 1.0603 | 1.1824 |
| aliasing | 0.3706 | 0.1311 | 0.0000 | 0.3158 | 0.3889 | 0.4500 | 0.6316 |
| celdas | 17.27 | 4.29 | 2 | 16 | 18 | 20 | 24 |

```
D_W == 0 en el banco          0 de 500
D_W / H(O'|C)                 0.9027    ← lo que sobrevive al aliasing
```

## 3.3 · Las 16 de 1.6 no son representativas

```
D_W de las 16 confirmatorias de 1.6     0.8447
D_W poblacional                         0.9127 ± 0.0983
                                        z = -2.77
```

**Mi §14 se equivocaba en dos direcciones a la vez:** presentaba como propiedad de
la clase de mundos una medición hecha sobre una muestra sesgada **baja**, y por
tanto **subestimaba** la señal disponible. En la población la acción no aporta
«tanta información como el pasado sensorial» (0.8447 vs 0.8536): aporta **más**
(0.9127 vs ~0.85).

La conclusión de viabilidad se refuerza; la generalidad con que la escribí no
estaba justificada.

---

# 4 · Los estratos nuevos · por aliasing, no por tamaño

```
correlación D_W ~ tamaño de componente     -0.0571     ← prácticamente nula
correlación D_W ~ aliasing                 -0.2923
```

| estrato (terciles de `D_W`) | n | `D_W` | celdas | aliasing |
|---|---|---|---|---|
| bajo (`D_W < 0.8693`) | 167 | 0.8013 | 17.8 | 0.4235 |
| medio | 166 | 0.9173 | 17.5 | 0.3738 |
| alto (`D_W ≥ 0.9645`) | 167 | 1.0196 | 16.6 | 0.3146 |

1.6 estratificaba por **tamaño del componente**, y para una capacidad que use la
acción ese estratificador **no informa nada** (r = −0.06). El que informa es el
**aliasing**: cuantas más celdas comparten firma, menos sobrevive la dependencia de
acción al pasar de celda a observación.

Un decimal que herede los estratos de 1.6 estaría estratificando por una variable
irrelevante.

---

# 5 · La ontología de `M_0` · las dos opciones, con lo que cuesta cada una

Sigue siendo decisión humana. Lo que sí se puede escribir es qué implica cada una.

### Opción A · ontogenia acumulativa en el mismo mundo

```
mundo W  →  fase 1.6 adquiere M_0^W  →  FREEZE M_0^W  →  fase siguiente en el mismo W
```

- El baseline **es** lo que ese organismo sabía de ese mundo. Desarrollo literal.
- El contraste mide exactamente la información **adicional** que aporta la acción.
- Coste: dos fases por vida, y hay que decidir el presupuesto de cada una. El
  presupuesto de 1.6 estaba en saturación; repetirlo aquí volvería a hacer
  `M_0^W` un estimador convergido y el contraste se leería sobre un techo.

### Opción B · `M_0` como baseline científico externo

- Experimentalmente válido y más simple.
- **Deja de representar ontogenia acumulativa.** No se puede decir «el ser ya
  sabía» — se dice «se comparó contra un modelo sin acción».

**Lo que no es aceptable en ninguna de las dos:** llevar una tabla aprendida en la
topología `W₁` a `W₂` y llamarla capacidad heredada. Mezcla mecanismo con
conocimiento, y las 500 mediciones de §3 muestran por qué: `H(O'|O)` varía entre
0.5623 y 1.5464 entre mundos, así que una tabla de otro mundo no es un baseline
neutro sino un baseline **arbitrariamente sesgado**.

---

# 6 · Lo que queda antes de poder escribir un oráculo

```
hecho     banco de calibración independiente, con ventanas disjuntas registradas
hecho     distribución poblacional de D_W, H(O'|O), H(O'|O,A), H(O'|C), aliasing
hecho     estratos por D_W / aliasing, con la evidencia de que el tamaño no sirve
hecho     gemelo A/B verificado al nivel del kernel físico de estados
hecho     contrato estructural separado: D_W>0 en A (nunca excluye) · D_W=0 en B

abierto   la ontología de M_0                        ← decisión humana
abierto   la curva T ↦ (D_E, D_K, D_C)               ← requiere definir D_E y D_K
                                                       ejecutablemente y un aprendiz
abierto   el presupuesto: pendiente, saturado, o la curva como endpoint
```

Y el hallazgo que no cambia: **no hace falta rediseñar el mundo base.** La
dependencia acción–consecuencia existe y es abundante en la clase de mundos que ya
tenemos. El problema no es crear señal — es medir bien cuánta hay, cuánta
experimenta S0 y cuánta consigue adquirir el mecanismo.
