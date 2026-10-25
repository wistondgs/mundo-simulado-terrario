# FICHA DE APERTURA · regeneración tras lesión (ítem 0.2)

**Fecha:** 2026-10-25 · **Veredicto: `OPEN`** (autoriza código) · **Gate previo:** `PARTIALLY_SOLVED`, ver `PRIOR_ART_REGENERACION_TRAS_LESION.md`

1. **Pregunta.** Si se destruye la hipótesis de una unidad que ya predecía sin error, ¿cuánto le cuesta volver a predecir sin error, y cuánto de ese coste lo paga la experiencia retenida en vez de la vida nueva?

2. **Constructo y medida.** Constructo: *reparabilidad*, separada en sus dos monedas. Medidas: (a) **pasos de vida nueva** hasta el último error posterior a la lesión; (b) **pasos repasados** sobre la experiencia retenida; (c) si la máquina recuperada es la misma que la de antes de la lesión; (d) si el futuro de 6656 pasos vuelve a 1,0000.

3. **Hipótesis.** La experiencia retenida es un sustituto de la vida: con ella, la reparación se paga en repaso y no en vida; sin ella, se paga en vida.

4. **Predicciones, escritas antes de correr.**
   - Brazo **con traza y repaso** (modo «reconstrucción desde lo retenido»): **0 pasos de vida nueva**; repaso del orden del tamaño de la traza; máquina idéntica a la previa; futuro 1,0000.
   - Brazo **con traza sin repaso** (la refutación conduce la reparación): pocos pasos de vida nueva, **menos** que el brazo sin traza, porque cuando llegue la primera refutación el repaso dispone de toda la vida.
   - Brazo **sin traza** (regeneración viviendo): del orden de los 21 pasos del nacimiento, y en ningún caso más de ~60.
   - Brazo **sham** (se contabiliza la lesión pero no se borra nada): 0 en todo.

5. **Falsador.** Que el brazo con traza tarde **tanto como** el brazo sin traza en vida nueva. Eso significaría que lo retenido no es sustituto de la vida, y el constructo «retención» de 01 y 02 estaría mal nombrado.

6. **Banco.** Los tres mundos de 01 congelados (aliasado, visible, bit inerte) y cinco momentos de lesión, t ∈ {64, 128, 256, 512, 1024}, con el resto de la misma vida shortlex como corriente de recuperación. Curva, no punto: la norma de la casa prohíbe un presupuesto único elegido donde ya saturó.

7. **Controles.** El brazo **sham** es el control de que la medida discrimina (si sham y lesión real dan lo mismo, la lesión no lesiona). El mundo del **bit inerte** es el control de que no se inventa capacidad: allí la máquina tiene 1 estado y la lesión no puede costar nada. El mundo **visible** es el control de que el reactivo también se recupera.

8. **Tres capas.** *Programado*: la lesión, qué se borra en cada brazo, los momentos de lesión. *Disposición*: el orden canónico de los estados y el orden shortlex de la vida, heredados de 01 sin cambio. *Adquirido*: la máquina recuperada, el número de refutaciones y de repasos que costó, y los pasos de vida nueva.

9. **Contadores de actividad.** Por brazo: refutaciones posteriores a la lesión, distinciones reabiertas, pasos repasados. En el mundo aliasado, un contador de refutaciones en **0** fuera del brazo sham significa resultado **nulo por inactividad**: la vía de reparación no se ejecutó y el experimento no probó lo que dice probar.

10. **Mutantes del gate, antes de lo real.** (i) El sham, que es un mutante incorporado: debe dar 0 y, si da lo mismo que la lesión real, el gate está roto. (ii) Una lesión que borra la hipótesis **y** reconstruye llamando a la máquina guardada (no a la vía de reparación) debe quedar prohibida por construcción: no se escribe ese camino.

11. **Puerta.** PASS si en el mundo aliasado, para los cinco momentos: vida nueva del brazo con traza y repaso = 0; vida nueva del brazo sin traza > 0 y ≤ 60; máquina recuperada idéntica a la previa en los dos brazos con recuperación completa; futuro 1,0000; y sham en 0. FAIL si se cumple el falsador del punto 5, o si alguna máquina recuperada difiere de la previa sin que la no-identificabilidad lo explique.

12. **Custodia.** `unidad_minima_03_regeneracion.py`, resultado a `artifacts/unidad_minima_03_regeneracion.json` con el sha256 del código, dos corridas un hash, sin `random`. No se commitea sin que Wis lo diga.

---

## Enmienda prospectiva · 2026-10-25, antes de la corrida real

El paso de mutantes (norma 10) corrió **antes** que el experimento y refutó un criterio
de esta ficha, no un resultado. El punto 7 afirmaba que en el mundo del bit inerte «la
lesión no puede costar nada». Es falso por construcción: aunque allí la máquina tenga un
solo estado, al borrar la experiencia retenida la unidad pierde también qué reacciona
cada letra, y recuperarlo cuesta algún paso de vida nueva.

El mundo del bit inerte no controla el **coste** de la lesión; controla que no se
**invente** capacidad al repararse. El criterio de la puerta queda reemplazado por dos:

- en el bit inerte no se reabre ninguna distinción: estados finales = 1 en los cuatro brazos;
- con traza, 0 pasos de vida nueva; sin traza, no más de 2 (reaprender dos pares letra→reacción).

Se declara aquí y no se vuelve a tocar. El resto de la puerta queda como estaba.

**Mutantes corridos y su resultado** (los tres deben hacer FAIL, y lo hacen):
`lesión falsa` (no se borra nada), `traza falsa` (conservar la traza no conserva nada),
`respaldo` (se restaura la máquina guardada sin vivir ni repasar). El tercero es el que
más importa: impide que la puerta se contente con «volvió a predecir» sin exigir que el
coste se haya pagado.

---

## Resultado y la reparación única · 2026-10-25, la predicción escrita antes de correrla

**La puerta dio FAIL y el falsador §5 se cumplió.** En el mundo aliasado, los pasos de vida
nueva del brazo que conserva la traza y los del que no la tiene fueron **idénticos** en
3 de los 5 momentos de lesión (7 y 7, 8 y 8, 14 y 14), y sólo mejores en 2 (10 frente a 17,
2 frente a 6). Conservar la experiencia **no** redujo los errores de vida nueva.

**Diagnóstico.** La traza no es inútil: cuando la refutación llega, el repaso reconstruye la
máquina correcta y lo hace pagando miles de pasos de repaso (hasta 6137). Lo que no hace es
evitar los errores **anteriores** a esa refutación. La unidad sólo relee su vida cuando se
queda sin alternativas, y hasta que eso ocurre se equivoca exactamente igual que una unidad
sin memoria. El valor de lo retenido depende de que algo **dispare** la relectura.

El brazo `con_traza_y_repaso` cuesta 0 pasos de vida nueva, pero su disparo viene de fuera:
soy yo quien sabe que hubo una lesión. Un organismo no recibe ese aviso. Por eso ese 0 no
cuenta como capacidad de la unidad: está comprado con una señal suministrada.

**La reparación (una, y es la que permite la regla de cierre).** No se toca la puerta ni se
afloja ningún criterio. Se añade un quinto brazo con un disparador **interno**, que la unidad
puede ejecutar con lo que tiene: al ir a predecir, si su hipótesis está vacía y su memoria
no, se relee antes de responder. No es un detector de daño; es notar que no tiene modelo y sí
tiene recuerdos.

Predicción, escrita antes de correr: **0 pasos de vida nueva**, máquina idéntica a la previa,
y el coste pagado entero en pasos releídos. Falsador de la reparación: que siga empatando con
el brazo sin traza, lo que querría decir que el problema no era el disparo.
