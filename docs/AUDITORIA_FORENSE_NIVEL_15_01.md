# Auditoría forense del Nivel 1.5

**2026-09-21** · pasos 1–3 del encargo. Sin implementar nada.

---

## Veredicto corto

```
1. precondición B+Q+H+M+ψ       EXISTE Y VERIFICA        ejecutado hoy, 10 gates
2. campaña piloto · código      NO EXISTE EN NINGÚN ÁRBOL
2. campaña piloto · parámetro   NO CONSTA, y el propio documento lo dice
3. constructo vs optimizador    separado en dirección, NO en magnitud
```

**El piloto de 1.5 es irreproducible.** No porque alguien lo perdiera: porque el
parámetro que produjo la diferencia nunca se escribió.

---

## 1 · La precondición · la única buena noticia, y es sólida

El registro canónico de 1.5 afirma que el organismo previo contiene
`B+Q+H+M+ψ` y que «la fusión fue verificada antes de abrir 1.5» —con la
cobertura «disponible **conceptualmente**», que invitaba a desconfiar—.

**Comprobado por ejecución, no por lectura.** El árbol
`organism-remembered-binding-01` tiene el organismo de las cinco capacidades en
`terrario/remembered/core.py`, y su campaña corre hoy:

```
REMEMBERED_BINDING_STATUS = VERIFIED

  un solo núcleo, por identidad de objeto   True
  cinco huellas idénticas pre/post          True
  memory.py byte-idéntico al blob           True
  C(ψ(x)|x) = 17/20 tras la fusión          True
  invariancia a los 12 pares de portadores  0.0e+00

  RB-0 … RB-9   diez gates, todos PASA
```

Y trae un resultado que conviene no perder, porque es una dependencia medida y
no una suposición:

```
mejora sólo M      0.028299
mejora sólo ψ      0.000000   ← cero exacto: ψ sin M no aporta
mejora conjunta    0.034813
INTERACCIÓN        0.006515   (sellada 0.006534)
```

`RB-7 dependencia total`. **ψ sola no contribuye nada**; necesita M.

`B`, `Q` y `H` vienen del núcleo congelado de 1.4; ψ se readquiere con su banco
determinista de 64 escenas y se congela allí —«nadie había construido un
envoltorio para el binder, porque el nivel que lo creó no lo necesitaba»—; `M`
no tiene parámetros. Se reúnen procedimientos, no artefactos.

**La precondición no hay que inferirla: está construida y pasa sus gates.**

---

## 2 · La campaña piloto · qué se conserva y qué no

### El código no existe

Barrido sobre los nueve árboles: **cero ficheros `.py`** contienen las semillas
del piloto —`20260920`, `777`, `31337`— ni marca alguna de `level15`. El
`encoder.py` que aparece en las búsquedas es el codificador perceptual de A4,
sin relación con el emisor de 1.5.

Los nueve documentos lo dicen de sí mismos en cada versión: «no existe código de
Nivel 1.5; no existe carpeta; no existe rama».

### Qué SÍ se conserva

| elemento | estado | dónde |
|---|---|---|
| construcción del constructo | **completo** | `01_ENTREGABLE_1` · H1/H2/H3, matriz de pérdidas, regímenes |
| regiones diagnósticas | **completo** | H1 conservar `G`; H2 conservar `P`; H3 un bit balanceado de cada uno, `Z₃=(γ(G),π(P))` |
| regímenes | **completo** | `R_G`, `R_P`, `R_J` con `P(Q)=4/5` y `1/10,1/10` |
| óptimos analíticos | **completo** | `L*(R_G)=1/8`, y la tabla donde ninguna estrategia domina |
| resultados del piloto | **completos como números** | tasas por semilla y presupuesto |
| semillas del piloto | **conservadas y quemadas** | `20260920·777·31337` BURNED; 16 nuevas reservadas |
| mecanismo | **nombrado, no especificado** | «dos tablas de aprendizaje local, una de emisión y una de lectura» |

### Qué NO se conserva, y es lo que decide

```
magnitud exacta del paso constante      NO CONSTA
variante exacta de la actualización     NO SELLADA
programa de exploración                 pendiente de preregistro
clasificador de clase informacional     pendiente de preregistro
```

Y no lo digo yo. Lo dice el documento que superó al piloto:

> «La magnitud exacta del paso constante **no consta en la evidencia textual
> preservada aquí** y debe especificarse antes del preregistro final.»
> — `LEVEL15_06:206`

Repetido como pendiente abierto en tres manifiestos distintos.

**Sobre «qué variantes de J se usaron»:** la pregunta no aplica tal cual.
`R_J` no es una variante de un objetivo `J`: es el **tercer régimen
estacionario**, aquel donde la consulta conjunta `Q_J` tiene probabilidad 4/5.
Hay tres regímenes y tres regiones diagnósticas, y el mapeo que el piloto
reporta es `R_G→H1`, `R_P→H2`, `R_J→H3`.

---

## 3 · Constructo contra optimizador · separado en dirección, no en magnitud

Esto ya lo hicieron, y bien.

**El piloto viejo** —regla de media corrida— dio `R_G=31/40`, `R_P=28/40`,
`R_J=31/40`, y sus 30 fallos se descompusieron en **9 óptimos locales exactos**
y **21 fallos interpretados como barreras de coordinación encoder↔decoder**.

**Cambiando sólo la regla de actualización** a paso constante —mismo mecanismo
de dos tablas, mismos contratos de información— las tasas saltaron:

```
presupuesto 10.000     R_G 59/60    R_P 55/60    R_J 60/60
presupuesto 100.000    R_G 60/60    R_P 59/60    R_J 60/60
total del piloto       529/540 = 97,96 %
```

Conclusión ya escrita por ellos, y correcta:

> «los 21 fallos anteriores **no pueden canonizarse como propiedad del problema
> de Nivel 1.5**. Eran, al menos en gran medida, consecuencia de la dinámica de
> actualización anterior.»

**Lo que queda del constructo**, y es poco pero es real:

* `R_P` es sistemáticamente el régimen más difícil en los tres presupuestos, y
  su causa **NO está establecida** —lo declara `04:123`—;
* con paso constante a 10.000 ensayos aparece un transitorio;
* el presupuesto de 100.000 se eligió sobre la curva de la regla **anterior**;
  con paso constante, 10.000 ya dan `174/180 = 96,67 %`.

**Y aquí está el límite de la separación.** La comparación «optimizador viejo vs
optimizador nuevo» se hizo contra una regla cuyo parámetro no está registrado.
La **dirección** del hallazgo se sostiene —cambió sólo la regla y las tasas
saltaron treinta puntos—; la **magnitud** no se puede comprobar, ni reproducir,
ni ajustar. Si mañana alguien quiere saber si `R_P` es difícil por la tarea o
por el paso, no tiene contra qué medir.

---

## 4 · Lo que esto implica para el preregistro

No es una lista de mejoras: son las tres cosas sin las cuales 1.5 no puede
preregistrarse honestamente.

1. **El paso constante hay que fijarlo, no recuperarlo.** No existe. Fijarlo es
   una decisión nueva, y el preregistro debe decir que lo es en vez de
   presentarlo como continuidad del piloto.
2. **El piloto no es línea base reutilizable.** Sus números son ciertos y no son
   verificables. Sirven para orientar el diseño; no para sostener una
   expectativa preregistrada. La banda 15–21 % ya fue retirada por ellos mismos
   por una razón análoga.
3. **`R_P` es la única pregunta científica viva que el piloto dejó**, y está mal
   condicionada: se observó bajo dos optimizadores distintos y no se aisló bajo
   ninguno.

---

## 5 · Huecos que el repositorio no puede responder

Marcados para el paso 4, y **sólo** estos:

* **coordinación emisor–receptor bajo coaprendizaje** · los 21 fallos se
  atribuyeron a esto y luego la atribución se retiró; el repositorio no tiene
  con qué decidir si la barrera existe;
* **dinámica con paso constante en dos tablas acopladas** · por qué un
  transitorio a 10.000 y no a 100.000;
* **aprendizaje bajo cuello de botella** · si la dificultad de `R_P` es un hecho
  conocido de la clase de problema o una propiedad de este diseño;
* **clasificación de representaciones invariante a relabeling** · el clasificador
  de clase informacional está pendiente y es la variable primaria.

---

## 6 · Lo que NO hice

No implementé nada, no diseñé el preregistro, no fijé el paso constante, no
busqué fuera del repositorio, y no descongelé 1.5. La condición de
descongelación que sus autores escribieron —«experiencia útil generada por el
organismo > capacidad disponible para conservarla»— **sigue sin cumplirse**, y
nada de esta auditoría la toca.
