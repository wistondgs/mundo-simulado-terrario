# FICHA DE APERTURA · Fase 2 · ¿lo vivido se acumula?

**Fecha:** 2026-10-27 · **Veredicto: `OPEN`** (autoriza código) · **Gate previo:** `OPEN_UNDER_CURRENT_SEARCH` para la pregunta compuesta, en `PRIOR_ART_FASE_2.md` · **Manda:** `ORIENTACIONES_FASE_2_TRASPASO.md` sobre los pasos 2–4 de la receta

---

## 0 · Guardas que aplican, y la declaración que esta ficha no puede omitir

**Esta ficha NO es ciega.** El prototipo de Fable corrió tres pilotos y una campaña completa de 2 134 familias **antes** de que existiera ficha alguna (E-37). Por tanto:

- **Los números del prototipo se usan para fijar predicciones y márgenes, y para nada más.** No cierran nada, no cuentan como evidencia y no entran al cierre como resultado.
- **Dos mecanismos del prototipo no estaban preregistrados y se encontraron corriendo:** el **olvido por fracaso** (agotar el presupuesto de un intento conserva los últimos 64 pasos y reempieza sobre ellos) y el **cerrojo** de W₂. Se adoptan como **disposición suministrada declarada**, no como hallazgo.
- **Esta ficha es un preregistro sobre un terreno ya visto.** Decirlo es lo único que la salva de ser una racionalización: cualquier lector debe poder descontar que las predicciones de §5 se escribieron sabiendo lo que el prototipo mostró. Por eso §6 añade un falsador que el prototipo **no** puede haber sugerido: el de C5, el brazo que no existe todavía.

| entrada | cómo se cumple aquí |
|---|---|
| **E-37** supervisor sin ficha | esta ficha; y el prototipo queda etiquetado exploratorio en todo el cierre |
| **E-38** bit nuevo inobservable por construcción | el filtro de familias que no abren distinción nueva **aborta** si una clase queda vacía (`no_vacio`); mutante M-d |
| **E-39** matar a la unidad al agotar el presupuesto | prohibido el `break`: agotar el presupuesto **dispara el olvido**, no termina la vida; mutante M-c reproduce el ahogo a propósito |
| **E-02** cero comprado con señal suministrada | el cambio de mundo lo hace el experimentador y **la unidad no recibe aviso**; el brazo fresco se borra por mano externa y así se declara |
| **E-21** la fila no guarda el objeto | cada celda guarda **la máquina final serializada** y la de W₁ |
| **E-07/E-35** determinismo verificable | `sin_azar_usado()` por AST sobre los módulos; dos corridas un hash |
| **E-15** mutantes que no ejercitan el instrumento | M-c, M-d y M-e son de instrumento, no de capacidad |
| **E-22** umbral bajo el ruido | todo margen de §5 se compara contra el ruido de muestreo de las dos celdas, con alfa ajustado por comparaciones |
| **E-25** umbral absoluto entre escalas | el repertorio se compara **entre brazos** del mismo W₂, nunca contra W₁, que tiene la mitad de estados (§4 del traspaso) |
| **E-33** implicación subida a bicondicional | ninguna afirmación de §5 se enuncia en dos sentidos sin medir los dos |
| **E-34** «no existe» por «no hemos encontrado» | el gate lista las búsquedas; ninguna afirmación de ausencia sin ellas |
| **E-36** documento vivo sin comprobar versión | hash del traspaso y de la receta registrados al empezar: `0935cb66…` y `fd0acf40…` |
| **E-40** (nueva, ver abajo) hash copiado de la terminal | todo hash de un documento se copia del **artefacto que la propia corrida escribió** |

**Lo que cubre un experimento previo:** la unidad (02), el disparo de relectura por consistencia (03), la elección por conveniencia (04) y la verdad de referencia (05). No se reescriben.

---

## 1 · Pregunta

**¿Lo vivido se acumula?** Tras vivir W₁, ¿puede la unidad en W₂ **algo que una unidad fresca no puede con la misma vida**?

Medido como **alcance, exactitud, repertorio e instruibilidad**. El cómputo y el tiempo se **registran siempre y no deciden nunca**: una unidad que se desarrolle gastando más que una fresca sigue siendo un desarrollo (norma de Wis del 27-oct).

**Qué construyo que la pregunta no pide:** nada, salvo **C5** (§5-bis), que es el brazo sin el cual la pregunta no se puede contestar — el prototipo sólo sabe heredar la **traza**, y eso ya se midió y es lastre. Explícitamente **no** se construye: nada en n ≥ 6, nada con marca, nada estocástico, nada de Genesis.

---

## 2 · Constructo y medidas, con su campo

Constructo: **acumulación** — que lo adquirido amplíe lo que el ser alcanza, sabe y puede ser instruido a hacer.

| medida | qué es | campo |
|---|---|---|
| **alcance** | ¿identifica W₂ salvo isomorfismo, con el mismo presupuesto? Curva por hito, no punto final | `alcance_por_hito`, `identifica_w2` |
| **exactitud** | fracción del futuro fijo de W₂ bien predicha | `exactitud` |
| **repertorio** | **resets verdaderos conocidos**: palabras ≤ 3 que su máquina declara constantes **y** que lo son en el W₂ real desde todos sus estados alcanzables. Comparado **entre brazos**, nunca contra W₁ | `resets_verdaderos` |
| **instruibilidad** | metas externas cumplidas en W₂, y si se cumplen **usando palabras heredadas** | `metas_cumplidas`, `metas_con_palabra_heredada` |
| registro, no criterio | interacciones, trabajo, olvidos, tamaño de biblioteca | `trabajo`, `olvidos`, `pasos_elegidos` |

---

## 3 · Hipótesis

Lo que se puede heredar con provecho es la **máquina**, no la traza. La traza vieja obliga a explicar un mundo que ya no existe y fuerza a olvidar; la máquina es una conjetura que se puede **reparar donde falla**. La acumulación, si existe, aparece temprano en la curva y en el repertorio, no en el alcance final.

---

## 4 · El techo, que es un defecto de diseño y hay que arreglarlo antes de medir

En el prototipo **los seis brazos llegan al techo**: alcance final 0,992–0,996 en la clase componible y 1,000 en la control. Con 3 586 pasos de vida en W₂ todo el mundo identifica, así que el alcance final **no discrimina nada** y la única señal está entre los hitos 64 y 256.

Un criterio sobre una medida saturada no es criterio (norma de la casa, y E-08). Por tanto, **declarado antes de correr**:

- **La medida principal de alcance es la curva en los hitos 64, 128 y 256**, donde hay varianza, y se informa como curva. El alcance final se informa pero **no entra en la puerta**.
- Se añade un presupuesto corto declarado: **W₂ de 512 pasos** como condición principal, con 3 586 como condición secundaria para comprobar que el techo sigue ahí y no se perdió nada.
- Si incluso en 64 pasos todos los brazos quedaran dentro del ruido, el experimento es **NULO por saturación** y se informa así, no como negativo.

---

## 5 · Predicciones, escritas antes de la corrida confirmatoria

Los márgenes salen del prototipo y **se declara que salen de ahí**. Cada comparación se juzga contra el ruido de muestreo de las dos celdas (alfa 0,05 ajustado por el número de comparaciones), no contra un número fijo de puntos.

1. **Heredar la traza no acumula, y además estorba.** En la clase componible, C1 ≤ F1 en la curva de alcance en los tres hitos; pareado, C1 no gana mundos que F1 pierda. *(Prototipo: media de curva 0,879 frente a 0,906; pareado 0 contra 3. Esto ya está medido exploratoriamente y la confirmatoria sólo lo confirma o lo tumba.)*
2. **Elegir ayuda a quien tiene esqueleto y no a quien no lo tiene.** C3 > C1 en los hitos 64 y 128; F3 ≈ F1. *(Prototipo: 0,569 vs 0,542 y 0,785 vs 0,758 en C; F3 0,903 vs F1 0,906, dentro del ruido.)*
3. **La lesión no cambia nada mientras se herede la traza.** C2 ≈ C1 y C2 ≤ F1: lo que pesa es la memoria cruda, no la máquina. *(Prototipo: C2 y C1 idénticos en la curva.)*
4. **El control se comporta.** En la clase no componible, C1 ≤ F1 en los tres hitos y ningún brazo C gana mundos pareados. *(Prototipo: PASS.)*
5. **C5 es la única que puede acumular.** C5 > F1 en el hito 64 de la clase componible, con margen superior al ruido; y C5 ≤ F1 en la clase control. Repertorio de C5 ≥ el de F1 al final de W₂.

---

## 5-bis · C5 · heredar la máquina sin la traza, y qué garantía de 02 se pierde

**El mecanismo.** Al cambiar el mundo, la unidad conserva `trans` y `q` y **vacía la memoria**. Con 02 tal cual eso no funciona: la primera refutación de una transición heredada encuentra la pila de decisiones vacía, abre un estado nuevo y relee una memoria vacía — la máquina heredada se borra. La reparación es **local**: cuando se refuta una transición heredada que no tiene decisión en la pila, esa transición se vuelve **revisable en el paso actual** (se empuja como decisión con su destino actual) en vez de disparar la relectura.

**Qué garantía de 02 se pierde, dicho con precisión.** La búsqueda de 02 es **exhaustiva en orden canónico sobre toda la traza retenida**, y de ahí viene su propiedad fuerte: su máquina final **coincide con la mínima recomputada de cero** por 01 — verificado en la Fase 0 (los tres mundos) y en la Fase 1 (cruce 19 344/19 344, cero discrepancias). Con una transición heredada que se vuelve revisable en el paso actual, **la búsqueda deja de ser exhaustiva sobre la traza**: las transiciones heredadas no fueron elegidas por el orden canónico sobre *esta* traza, sino sobre otra que ya no está. Por tanto **se pierde la garantía de minimalidad**, y con ella la de coincidencia con 01.

**Qué la reemplaza, y cómo se comprueba.** Lo que queda garantizado es más débil y es verificable: **consistencia con la traza retenida**. Y la pérdida **no se supone, se mide**: para cada celda C5 se recomputa `minimal_mealy` sobre su traza retenida y se informan tres fracciones separadas —
- `c5_consistente`: la máquina de C5 explica toda su traza. **Debe ser 1,000**; si no, es un defecto y no un intercambio.
- `c5_minima`: la máquina de C5 **es** la mínima de su traza. Se espera < 1,000: ésa es la garantía que se cede.
- `c5_estados_sobre_minimo`: cuántos estados de más usa cuando no es mínima.

Así el cierre puede decir **cuánto** de minimalidad costó la herencia, en vez de decir que no importa.

**Mutante obligatorio de C5:** «hereda pero ignora lo heredado» (conserva `trans` y la sobrescribe con la máquina vacía antes del primer paso) **debe dar exactamente F1**. Si no coincide, C5 no está midiendo la herencia.

---

## 6 · Falsadores, como números

- **De la hipótesis (§3):** que C5 no supere a F1 en el hito 64 de la clase componible, con la diferencia dentro del ruido. Entonces **ni la traza ni la máquina acumulan** en este banco, y lo que tenemos es un aprendiz y no un ser. *Este falsador el prototipo no puede haberlo sugerido: C5 no existe en él.*
- **De programa:** que además C5 ≈ F1 en repertorio e instruibilidad. Con los contadores activos; si están en 0, es **nulo por inactividad**, no negativo.
- **De instrumento:** que `c5_consistente` < 1,000 (defecto), o que el mutante «ignora lo heredado» no reproduzca F1 (C5 no mide lo que dice).
- Y lo que **no** es falsador: que cualquier brazo C gaste más cómputo, más interacciones o más olvidos que el fresco. Eso es registro.

---

## 7 · Banco y controles · por cada control, qué afirmación exacta controla

**Banco:** los **174** W₁ de n=3 identificados por la unidad y distintos salvo isomorfismo; de cada uno, las familias (W₁, W₂) de las dos clases que **abren una distinción nueva** (el filtro de E-38, con aborto si una clase queda vacía). El prototipo dio 2 134 familias con 998 descartadas; la confirmatoria usa el mismo generador canónico.

| control | qué puede hacer ahí | qué afirmación controla |
|---|---|---|
| **clase no componible** (dependencia invertida) | lo heredado no sirve: la congruencia de W₁ se rompe | que la ganancia de C5, si existe, **viene de la composición** y no de tener historia |
| **brazo lesionado C2** (máquina colapsada, memoria conservada) | tiene la historia, no la distinción | separa **tener historia** de **tener la distinción** |
| **brazo fresco F1** | nada heredado | es la vara; M-e comprueba que es de verdad fresca |
| **intercambio A↔B** en itinerario y desempates | — | control de asimetría pendiente de la Fase 1: ninguna afirmación sobre letras sin él |

---

## 8 · Tres capas, y quién dispara cada paso

- *Programado*: el generador de familias, el itinerario base, la verdad de referencia, las cuatro medidas.
- *Disposición suministrada*: la ventana de memoria (512), el núcleo al olvidar (64), el presupuesto por intento (200 000), el tope de estados (8), el cerrojo de W₂, el tope de longitud de palabra, la salida observable, y **el cambio de mundo, que lo hace el experimentador**. Los tres primeros son **a ojo** y se corre una variante (ventana 256) para saber si el resultado depende de ellos (§4 del traspaso).
- *Adquirido*: la máquina en W₁, la máquina en W₂, qué sobrevivió de la primera, qué palabras usó.

**¿Quién dispara cada paso y qué sabe cada brazo que el organismo no sabría?** (E-02) El cambio de mundo es externo y **la unidad no recibe aviso**: lo descubre porque su hipótesis empieza a fallar. El borrado del brazo fresco es externo y por eso ese brazo es la **vara**, no un organismo. El olvido por fracaso lo dispara la unidad con lo que tiene (agota su presupuesto de explicar). En C5 el vaciado de memoria al cambiar de mundo es **externo y declarado**: es la condición experimental «heredar la máquina sin la traza», no algo que la unidad decida.

---

## 9 · Contadores de actividad

`olvidos`, `pasos_elegidos`, `pasos_olvidados` (ya existen) más, nuevos para C5: `transiciones_heredadas_supervivientes`, `transiciones_heredadas_revisadas`, `refutaciones_en_w2`. **Cero en `transiciones_heredadas_revisadas` ⇒ NULO POR INACTIVIDAD:** la reparación local no actuó y el experimento no prueba lo que dice.

---

## 10 · Mutantes, antes de la corrida confirmatoria

Los cinco del traspaso más el de C5. **La ficha no es final hasta que corran** (E-05); su resultado se escribe aquí.

- **M-a · olvido total** (núcleo = 0): la heredera debe quedar ≈ fresca con retraso. Si queda **igual** que con núcleo 64, esos 64 pasos no aportan nada y hay que decirlo.
- **M-b · elegir al revés** (ir a la transición no vista **más lejana**): no debe superar a «la más cercana». Si la supera, el órgano no es lo que creemos.
- **M-c · sin olvido** (presupuesto infinito, tope 8, sin `_olvidar` y **sin `break`**): debe reproducir el ahogo —curva plana, 100 % tope—. Es la guarda de E-39 y la verificación con ojos frescos del hallazgo 1 del traspaso.
- **M-d · bit conmutado** (el patrón de E-38): el filtro debe descartar el **100 %** de la clase componible y `no_vacio` debe abortar.
- **M-e · fresca con la vida de la heredera** (vive W₁ y borra todo al cambiar): debe coincidir **exactamente** con F1.
- **M-f · C5 que ignora lo heredado**: debe dar exactamente F1.

*Resultado de cada uno: se escribe aquí antes de la corrida real.*

---

## 11 · Puerta, con unidad y campo

- **(a)** `c5_consistente == 1,000` en todas las celdas C5 (`c5_consistente`). Si falla, defecto: no se lee nada más.
- **(b)** Los seis mutantes se comportan como §10 dice.
- **(c)** **Acumulación:** `alcance_por_hito[64]` de C5 > de F1 en la clase componible, con z por encima del umbral ajustado; y C5 ≤ F1 en la clase no componible.
- **(d)** **No sobreatribución:** C1 ≤ F1 en los tres hitos de la clase componible (heredar la traza no acumula), y C2 ≈ C1.
- **(e)** **Repertorio** (`resets_verdaderos`): C5 ≥ F1 en la clase componible, comparado entre brazos.
- **(f)** **Actividad:** `transiciones_heredadas_revisadas` > 0.
- **(g)** **No saturación:** en el hito 64 hay varianza entre brazos por encima del ruido; si no, NULO por saturación (§4).

El veredicto lo calcula el programa leyendo esos campos.

---

## 12 · Custodia

`unidad_minima_09_fase2.py` —nuevo fichero, para no tocar el prototipo de Fable, que queda como evidencia exploratoria con su hash `621c0534…`—; filas a `artifacts/unidad_minima_09_fase2.jsonl` con la máquina serializada de W₁ y de W₂; reanudable y con `fsync`; resumen con sha256 del código, versión del intérprete y todos los parámetros; `sin_azar_usado` verificado por AST. Un commit al cerrar, con el OK de Wis.

---

## Enmiendas prospectivas

*(vacío; se rellena si un mutante refuta un criterio antes de la corrida confirmatoria)*

## Resultado

*(vacío)*
