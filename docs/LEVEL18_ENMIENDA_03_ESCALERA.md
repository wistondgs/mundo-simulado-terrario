# Nivel 1.8 · Enmienda 03 — la escalera de `T` y qué significa «cobertura»

**Prospectiva.** Se sella ANTES de correr la calibración de 16 semillas, y antes
de haber mirado un solo número de cobertura, de margen pareado o de `sd`.

---

## 1. AMBIGÜEDAD DE PROTOCOLO · declarada

§10 del oráculo fija la **regla**:

> elegir el MENOR `T` tal que (a) FIXED-DEPTH-1 queda batido con margen ≥ 2 sd
> entre vidas · (b) `ΔL / 0.3427 < 0.90` · (c) la cobertura de contextos
> informativos no es el cuello de botella · empate → el menor `T`

y **no fija el conjunto de candidatos** entre los que se busca ese mínimo.
Tampoco define cómo se mide `(c)`.

Buscar candidatos *después* de haber visto que 4096 funciona sería libertad
analítica real. Por eso se para y se sella aquí.

---

## 2. Lo que YA se ha visto, y por tanto no puede sellarse como si no

Honestidad sobre el estado de conocimiento en el momento de sellar:

| visto | no visto |
|---|---|
| `ΔL` medio a `T`=1024 y 4096, **8 semillas** de diagnóstico | cualquier número a `T`=64 o 256 |
| censo de estados, splits, merges a esos dos presupuestos | cualquier número sobre 16 semillas |
| `I(C;Z\|O)` con nula, y la lesión de merge | **márgenes pareados por vida** |
| que el margen medio sobre DEPTH-1 es positivo a ambos | **`sd` entre vidas de ese margen** |
| | **toda medida de cobertura** |

La condición (a) depende de `sd(m)`, que no se ha calculado nunca. El criterio
puede fallar a los dos presupuestos ya vistos.

---

## 3. La escalera · adoptada, no inventada

El único conjunto de presupuestos que el documento sellado contiene está en §2,
en la medición de la dependencia del predecesor, escrita **antes de que
existiera ningún learner**:

```
T_18=64  4.89×   ·  256  3.64×  ·  1024  2.03×  ·  4096  1.13×
```

```
ESCALERA   64 · 256 · 1024 · 4096         en ese orden, ascendente
BÚSQUEDA   el primer peldaño que cumpla (a) y (b) y (c) simultáneamente
AGOTADA    si ninguno cumple → UN solo peldaño más, 16384
            si 16384 tampoco → 1.8 queda NO DEMOSTRADO al presupuesto sellado
```

La cláusula de agotamiento se sella ahora precisamente para que «seguir
ampliando hasta que salga» no sea una opción disponible después.

---

## 4. La aritmética de (a) · pareada, porque el oráculo ya la definió así

§7 línea 165 define el margen sobre FIXED-DEPTH-1 como

```
margen  =  L_POST(FD1) − L_POST(FULL)
```

que es **idénticamente** el delta pareado por vida:

```
ΔL_C18,i − ΔL_DEPTH1,i = [L_C17,i − L_FULL,i] − [L_C17,i − L_FD1,i]
                       = L_FD1,i − L_FULL,i = m_i
```

El diseño es pareado —los tres brazos comparten mundo, cableado, motor, banco y
masa heredada—, así que no se calculan dos desviaciones separadas de dos medias.

```
CRITERIO (a)   media(m)  ≥  2 · sd(m, ddof=1)        ← literal, «2 sd entre vidas»
```

Se reportará también `media(m) ≥ 2·sd/√N` —la forma de error estándar, que es la
que §7 línea 158 fijó para el ENDPOINT— pero **no es el criterio**: §10 escribe
«sd entre vidas» sin `√N`, y se aplica lo escrito. Si las dos lecturas
seleccionasen `T` distintos, se reporta el hecho y decide el humano; no se
elige la que dé el resultado preferido.

---

## 5. Qué significa (c) · operacionalizada sin una sola constante

«La cobertura de contextos informativos no es el cuello de botella» se lee como
lo que protege: que la comparación C18 vs DEPTH-1 no esté dominada por falta
accidental de exposición.

Para cada vida, sobre el banco de evaluación, se mide la fracción de pasos que
caen en una celda `(estado, O_t, A_t)` que **no recibió ninguna evidencia**
durante el entrenamiento — es decir, predicha sólo por el prior heredado.

```
CRITERIO (c)   hambre(FULL)  ≤  hambre(DEPTH-1)        promediado entre vidas
```

Sin umbral, sin constante ajustada: se compara un brazo contra el comparador
suministrado sobre el mismo banco. Si la ventaja de C18 fuese un artefacto de
cobertura, el hambriento sería C18, que sostiene diez veces más estados que los
cuatro de DEPTH-1. El criterio **puede fallar**, y ése es el punto.

Cero es una frontera estructural, no un umbral elegido.

Se reportarán además, sin papel decisorio: contextos observados y con soporte,
firmas visitadas, distribución de soporte por estado, estados con evidencia
nula, y masa heredada retenida por ellos.

---

## 6. Semillas

```
CALIBRACIÓN   150000011 … 150000026    las DIECISÉIS que §10 nombra
DIAGNÓSTICO   150000011 … 150000018    las ocho ya usadas · calibración previa,
                                        no se borran y no son la entrada de la regla
CONFIRMATORIAS 180000011 … 180000074   INTACTAS · no se tocan en esta enmienda
```

---

## 7. Lo que esta enmienda NO hace

- No toca el learner, ni el criterio de split, ni la semántica de merge, ni el
  prior, ni el reparto de masa, ni el routing, ni el scoring.
- No cambia el endpoint, ni su `CI95_inferior`, ni el baseline continuo.
- No añade, quita ni reordena gates.
- No declara ningún `T_18`. La regla aún no se ha aplicado.
