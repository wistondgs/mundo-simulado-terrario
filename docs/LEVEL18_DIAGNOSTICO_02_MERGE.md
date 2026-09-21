# Nivel 1.8 · Diagnóstico 02 — qué hizo merge, y qué no

Sobre `17993ef` (merge) y `0c127f7` (reparación de la medición).
Ocho semillas de diagnóstico `150000011…150000018`. Ninguna semilla `180…` tocada.

---

## 0. Primero: el negativo que adjudicamos no era del learner

`probability` no muta el estado a propósito —puntuar no debe aprender—, así que
avanzar el estado recursivo era tarea de quien puntúa, y **nadie lo hacía**.
Sondeado directamente: en 2048 pasos puntuados el learner visitó exactamente un
estado, `{0}`, habiendo terminado el entrenamiento con 30 estados y 16 splits.

Todo número `LEARNER` publicado hasta ahora era la raíz de un árbol cuya
evidencia se había marchado a las hojas. Eso explica también por qué empeoraba
al crecer el presupuesto: las cuentas de la raíz se adelgazan según el organismo
la abandona.

| | reportado antes | con la medición reparada |
|---|---:|---:|
| ΔL learner · T=1024 | +0,0166 | **+0,0757** |
| ΔL learner · T=4096 | −0,1148 | **+0,0901** |

El defecto de routing que reparamos en `1a35caa` era real, pero la ruta de
puntuación no llamaba a `_next_state` ni una vez: no pudo ser la causa del
negativo. **El negativo era el instrumento.**

Segundo defecto, mismo origen: `organization` —la función que `L18-6`
trasplanta— conservaba el recorrido absorbente `routing.get(clave, self._here)`
que `1a35caa` reparó sólo en `_next_state`. El gate de partición suministrada
comparaba particiones leídas sobre un autómata que se quedaba quieto.

Ninguno de los 81 tests cogía ninguno de los dos. Ahora `F5`, `F6` y `F7` los
cogen, verificados contra sus mutantes.

---

## 1. Lo que sí hace merge

Scoring reparado en los dos brazos; se lesiona únicamente la fusión.

| T_18 | brazo | ΔL learner | activos | splits | merges |
|---:|---|---:|---:|---:|---:|
| 1024 | con merge | +0,0757 | 7,6 | 9,0 | 7,4 |
| 1024 | sin merge | +0,0737 | 61,5 | 16,2 | 0,0 |
| 4096 | con merge | +0,0901 | 10,5 | 10,0 | 8,0 |
| 4096 | sin merge | +0,0789 | 90,5 | 23,6 | 0,0 |

Merge **no** es lo que puso ΔL en positivo: sin él ya era +0,074 / +0,079. Lo
que hace es colapsar el censo de estados ×8 (61,5 → 7,6) y ×8,6 (90,5 → 10,5),
con una mejora pequeña de ΔL que **crece con el presupuesto** (+0,0020 → +0,0112),
que es la firma esperada de una sobrefragmentación que se acumula.

Contra 18,6 situaciones verdaderas, el organismo sostiene 7,6 y 10,5 estados.

---

## 2. Lo que merge no hace, y hay que decirlo

`ΔL` mide predicción. No mide que lo construido **sea** el estado latente.
`I(C;Z|O)` mide eso segundo. El estimador empírico de información sesga hacia
arriba con el número de estados, así que se deriva la nula del propio dato:
permutar Z dentro de cada observación destruye la relación C–Z y conserva el
censo de estados, que es lo que sesga.

| T_18 | brazo | \|Z\| | I medida | I nula | I − nula | z | % de H(C\|O) |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1024 | con merge | 6,0 | 0,0116 | 0,0053 | **+0,0063** | 5,60 | 1,01 % |
| 1024 | sin merge | 50,1 | 0,1174 | 0,0640 | **+0,0534** | 11,96 | 8,60 % |
| 4096 | con merge | 8,0 | 0,0180 | 0,0079 | **+0,0101** | 6,78 | 1,58 % |
| 4096 | sin merge | 68,5 | 0,1338 | 0,0811 | **+0,0527** | 11,59 | 8,26 % |

La nula se lleva casi la mitad de la información cruda en todos los brazos, pero
**el orden sobrevive a la corrección**: el learner fragmentado conserva ~5× más
información situacional real que el fusionado. No era sesgo del estimador.

Todos los brazos están por encima de su nula (z entre 5,6 y 12): sus estados sí
llevan información verdadera sobre dónde está. Muy poca. Entre el 1 % y el 8,6 %
de lo que queda por saber después de mirar.

---

## 3. La disociación, que es lo que hay que adjudicar

**Merge retira estados que llevaban información situacional genuina, y al
hacerlo predice algo mejor.**

No es una contradicción; es lo que el criterio sellado pide. La regla es MDL: un
estado sobrevive si paga su complejidad **en predicción**. Un estado que
correlaciona con la posición pero está hambriento de evidencia no paga, y merge
lo retira. Enmienda 02 se cumple al pie de la letra.

Lo que la medición obliga a decir es otra cosa:

- El nivel gana su nombre —desambiguación predictiva adquirida— sobre `ΔL`, y
  `ΔL` es positivo, crece con el presupuesto y **bate a profundidad 1**
  (+0,0901 contra +0,0529), que es exactamente lo que el primer split produce.
  Está capturando historia más allá de su propio último comando.
- El nivel **no** puede afirmar que adquirió el estado latente. Con merge,
  el 1,6 % de la información situacional residual. El oráculo saca +0,56 de ΔL
  donde él saca +0,09: un 16 % del techo alcanzable.

Dicho sin adorno: **construyó un refinamiento predictivo, no un mapa.**

---

## 4. Qué NO se ha tocado

- Ninguna semilla `180000011…180000074`.
- El criterio de split, su momento, las porciones del prior y el routing:
  intactos desde `acb6b14` salvo la reparación de absorción ya adjudicada.
- Ningún umbral, paciencia, cooldown ni tope de estados: `L18-17` lo certifica
  por AST.
- 1.7 sigue congelado y verde en su propio árbol (47 tests, `level18` ausente).
  `L17-0` falla **dentro de este árbol** y debe fallar: certifica que las
  capacidades posteriores están ausentes, y aquí `level18` existe.

---

## 5. Pendiente de adjudicación

1. Si la disociación de §3 se acepta como resultado del nivel —el mecanismo
   adquiere predicción, no identidad de estado— o si obliga a revisar qué
   pregunta sella el oráculo.
2. El split en `t=10`, que quedó **sospechoso, no adjudicado**, y que ahora
   puede re-juzgarse: con merge, 9–10 splits acumulados y 7,4–8 retirados.
3. Si `I(C;Z|O)` corregida por nula entra como instrumento reportable del nivel
   o se queda como diagnóstico.
