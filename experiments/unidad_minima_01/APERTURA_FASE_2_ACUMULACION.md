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

### Resultado · los seis corrieron el 28-oct, antes de la corrida confirmatoria

Muestra: los **12 primeros mundos W₁** del banco canónico (de 174), que dan **138 familias**
(45 componibles, 93 no componibles). Código `unidad_minima_09_fase2.py`; artefactos
`artifacts/mutantes_09_fase2_pilot12.json` y los seis `mutantes_09_*.jsonl`. Las cifras de
abajo se copian de esos artefactos, no de la terminal (guarda de Opus del 27-oct).

| mutante | qué exigía la ficha | qué dio | veredicto |
|---|---|---|---|
| **M-a** olvido total | ≈ fresca con retraso; si queda **igual** que con núcleo 64, esos 64 pasos no aportan nada | alcance en el hito 64, clase componible: **núcleo 0 → 0,444**, núcleo 64 → 0,356, fresca → 0,467. No es igual, y el sentido **sorprende**: olvidar del todo va **mejor** que conservar 64 pasos, y queda casi en la fresca | **PASS**, con un hallazgo: el núcleo de 64 no es neutro, **estorba**, porque lo que conserva es mundo viejo |
| **M-b** elegir al revés | la más lejana no debe superar a la más cercana | medias de la curva: componible **0,8730 contra 0,8730** (idénticas), control **0,8618 contra 0,8725**. El órgano actuó en **138 de 138** celdas, y las dos versiones divergieron de verdad en **una**: ahí la más lejana eligió 3 571 pasos y **no identificó nunca**, la más cercana eligió 14 y **identificó en todos los hitos** | **PASS**, y se dice que el veredicto se apoya en una celda: en las otras 137 el órgano elige tan poco (≈3 pasos de 3 586) que no puede distinguir |
| **M-c** sin olvido | reproducir el ahogo: curva plana, tope | curva de la heredera **plana en los siete hitos**: 0,022 → 0,044 (componible) y 0,0215 → 0,0215 (control), contra **1,000** de la fresca en las dos clases; 302 y 620 topes; 152 201 y 323 285 pasos en parálisis | **PASS**. El hallazgo del que depende todo C5 queda **verificado con ojos frescos y con otra implementación** |
| **M-d** bit conmutado | el filtro descarta el 100 % de la componible y `no_vacio` aborta | 216 (W₁, patrón, clase) miradas: pasan **0 componibles** y 93 no componibles; `no_vacio` abortó con su mensaje | **PASS** |
| **M-e** fresca con la vida de la heredera | coincidir exactamente con F1 | 138 familias: **ninguna medida difiere y ningún registro difiere** | **PASS** |
| **M-f** C5 que ignora lo heredado | dar exactamente F1 | 138 familias: **ninguna de las diecisiete medidas difiere**; difieren los registros acumulados y los contadores propios de C5 (`refutaciones` en 138, por venir heredado de W₁ igual que en C1) | **PASS** |

**Y de paso, la garantía que C5 cede, ya medida en esta muestra** (§5-bis):

| | componible (45 celdas) | no componible (93) |
|---|---|---|
| `c5_consistente` | **1,000** | **1,000** |
| `c5_minima` | **0,978** | **0,956** (91 celdas determinadas; 2 agotaron el tope de búsqueda) |
| `c5_estados_sobre_minimo` | 0,022 | 0,066 |
| transiciones heredadas / revisadas / supervivientes | 5,56 / 248 / 1,07 | 5,59 / 517 / 1,32 |
| `herencia_borrada_por_distincion` | **0** | **0** |

Las dos cosas que §5-bis prometía medir en vez de suponer: la consistencia **se cumple sin
excepción**, y la minimalidad **se pierde**, en el 2,2 % y el 4,4 % de las celdas y por 0,02
y 0,07 estados de más. Eso es el precio de la herencia, en número. Y la reparación local es
la que actúa: la herencia no se perdió **ni una vez** por la otra vía (abrir una distinción
nueva y vaciar la máquina).

**Enmienda que sale de los mutantes** (y que por tanto es prospectiva respecto de la
confirmatoria, no posterior): M-c no puede correr con presupuesto *infinito* —no sería
medible y repetiría E-32—. Corre con **3 000 000 de pasos por intento** (15× el normal) y un
**tope por celda de 20 000 000**, al alcanzarlo la unidad queda **paralizada**: sigue viviendo
con la hipótesis que tenga y deja de intentar explicar, que es lo que «no puedo explicar mi
memoria» significa cuando explicarla no se puede pagar. Se cuenta `pasos_sin_aprender`.

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

## 13 · Enmienda prospectiva · el maestro, y el alumno que se vuelve maestro

**Escrita el 28-oct antes de la corrida pareada**, sobre `ORIENTACIONES_FASE_2_MAESTRO.md`
(T1/T2) y `ORIENTACIONES_FASE_2_DOS_UNIDADES.md` (la maestra como segunda unidad). Código
`unidad_minima_10_maestro.py`, que **importa** 08 y 09 y no los toca. Mismo banco, mismas
familias, pareado por familia. **Fable revisa esta enmienda; Wis adjudica.**

**La decisión de Wis que la motiva (28-oct).** «A mí nadie me enseña a leer. No puedo
aprender a leer solo.» «Sin maestro» deja de ser principio del ser y vuelve a ser lo que
era: una restricción del problema de identificación de la Fase 1. La norma que sí rige es
la otra: **nadie le resuelve las relaciones.** El maestro da palabras para vivir; nunca
una transición, un estado ni una salida.

### 13.1 · Las celdas

| celda | maestro | qué controla |
|---|---|---|
| **F1** | ninguno | la vara |
| **T1** | omnisciente, espera al error | el techo con el disparo del contraejemplo |
| **T2** | omnisciente, no espera | el techo con el disparo de itinerario |
| **U1** | unidad que **identificó** W₂ | ¿una unidad enseña como el omnisciente cuando tiene razón? |
| **U2** | unidad que **no** identificó (vivió sólo 64 pasos) | ¿canaliza hacia el error? (Derex et al. 2025, `SV`; que valga aquí es `HIPÓTESIS`) |
| **U3** | unidad de **otro** mundo de la misma clase | enseñar lo ajeno; predicción ≤ F1 |
| **U-sham** | unidad que da palabras donde el alumno **acierta** | el precio de ser mandado a lo que ya sabés |
| **M-canal** | unidad que da la palabra y el alumno **no la vive** | el único canal es vivir la palabra: debe dar F1 |
| **M-literal** | el disparo literal del encargo | deja medido qué hace ese disparo |
| **K2…K5** | cada alumna, maestra de la siguiente | la fidelidad a lo largo del linaje (Kirby, Griffiths & Smith 2014, `SV`; que nuestra cadena degrade es `HIPÓTESIS`, y es la predicción por defecto) |
| **Pareja** | dos frescas que se enseñan mutuamente | Bender & Slonim 1994, `LC` (sin leer aquí; A4 de `LITERATURA_PENDIENTE.md`): ¿dos sin maestro llegan donde una no? `HIPÓTESIS` en nuestro banco |
| **M-pareja-simétrica** | la pareja del encargo, las dos en el mismo sitio | deja medido que no cruza ningún bit |

**El presupuesto.** Las palabras que da el maestro se viven **dentro** de la vida del
alumno: todas las celdas gastan exactamente los mismos pasos de mundo que F1 y lo que
cambia es **qué** se vive, no **cuánto**. El gasto del maestro se registra aparte y no
decide (norma de Wis).

**U2, por qué 64 pasos.** La maestra de vida completa identifica el 99,6 % de las familias,
así que «la maestra que no identificó» se quedaría con nueve familias de 2 134. Se define
como la unidad que vivió sólo hasta el primer hito (64 pasos) y no identificó. Declarado
aquí, antes de medir.

### 13.2 · Cuatro defectos del encargo, medidos antes de la corrida, y qué se cambió

Pruebas de instrumento sobre **un** mundo W₁ (8 familias), con todas las celdas. Los cuatro
son del encargo, no de la implementación, y los cuatro se arreglan **antes** de medir, no
después de ver fallar.

**Y el alcance de estas cifras, dicho sin adornos:** vienen de un mundo. Sirven para lo que
se usaron —decidir el diseño de la celda antes de la corrida— y **no** para concluir nada:
cada una de las cuatro queda como **predicción a confirmar en la corrida pareada** con su
celda al lado (M-literal, M-pareja-simétrica, U-sham y M-canal son precisamente las celdas
que las vuelven a medir sobre las 2 134 familias). Lo que pasó con `c5_minima` —un piloto de
12 mundos subestimó la pérdida en un orden de magnitud— es la razón de esta advertencia.

1. **El canal y el cálculo no pueden ser verdad a la vez (E-46).** La orientación pide que
   cruce **un bit por paso** («las dos declaran su predicción antes de actuar») y además que
   la maestra dé «la palabra más corta en la que, según H_m, la predicción de U_a falla».
   Para calcular eso la maestra necesita **leer H_a**, que es muchísimo más que un bit. Se
   declara el canal como parámetro y se miden los dos: `ve_la_hipotesis` (la letra del
   encargo, techo de lo que una maestra podría) y `un_bit` (la maestra sólo recibe el bit
   de desacuerdo y da lo único que su propia máquina le permite señalar: la palabra más
   corta que separa dos de sus estados).
2. **El disparo literal vacía la celda.** Con el disparo del encargo —intervenir sólo
   cuando discrepan en la letra que el alumno estaba por tomar— la palabra que cruza fue de
   **longitud 1 en el 100 %** de las intervenciones y **la misma letra en 7 de 9**: la celda
   reprodujo F1 **curva por curva** (0,667 y 1,000 en los hitos 64 y 128). Con el disparo que
   no espera al desacuerdo local, el alumno identificó **en el hito 64** donde F1 necesitó
   **128**. Conclusión de instrumento, **sobre un mundo y por tanto a confirmar**: lo que
   hace que enseñar sirva parece ser el **disparo** y no el maestro; la celda M-literal y el
   par T1/T2 lo vuelven a medir sobre el banco entero. U1, U2, U3, U-sham, M-canal y la cadena usan el disparo que no espera; el
   literal se conserva como **M-literal**, para que quede medido y no afirmado. T1 y T2
   conservan cada uno el disparo de su definición, que es lo que los distingue.
3. **La pareja simétrica no puede cruzar nada (E-47).** Con las dos unidades en el mismo
   sitio del mundo leyendo la misma corriente de letras, **no cruza ni un bit en toda la
   vida**: dos unidades deterministas idénticas con la misma entrada construyen la misma
   hipótesis paso a paso, nunca discrepan y no tienen nada que enseñarse (medido: 0
   intervenciones y 3 586 contraejemplos imposibles). Los dos robots de Bender & Slonim 1994 (`LC`,
   sin leer aquí) cooperan, según el resumen de su resultado, porque están en **vértices
   distintos** del grafo; que la asimetría sea lo que importa en NUESTRO banco es
   `HIPÓTESIS`, y la mide esta misma celda. Así que cada unidad tiene su
   propia posición y su propio itinerario, desplazado un paso: la asimetría mínima,
   determinista, sin azar. La versión del encargo queda como **M-pareja-simétrica**.
4. **U-sham no es un control neutro, y no puede serlo.** Medido: alcance **0,000** en los
   siete hitos contra 1,000 de F1, con 3 584 intervenciones. Un maestro que manda al alumno
   a lo que ya sabe **le gasta la vida**, así que la predicción «U-sham ≈ F1» del encargo no
   puede cumplirse por construcción. U-sham pasa a ser lo que de hecho mide —el precio de ser
   mandado a lo que ya se sabe, que es la dirección que Derex et al. 2025 (`SV`) describen
   para la instrucción, aquí como `HIPÓTESIS` confirmada en una prueba de instrumento— y el control neutro de «el único canal es
   vivir la palabra» es **M-canal**, que sí dio F1 exactamente.

### 13.3 · Medidas

Alcance pareado en la curva (64, 128, 256) · intervenciones, letras dadas, longitud de la
palabra y `contraejemplos_imposibles` · **canalización**: número de hipótesis canónicas
distintas que el alumno visita, con y sin maestro, y si identificó al final (ahí quedó la
verdad dentro) · **fidelidad en la cadena** por generación: identifica, isomorfa a la
anterior, isomorfa a la primera, transiciones distintas · **retención** con la hipótesis
congelada y **retención aprendiendo** 512 pasos sin maestro · **cooperación**: fracción de
familias donde identifican **las dos** frente a F1, y pareado.
La transferencia a una cascada W₃ queda **declarada y no construida** en esta celda: pide
un banco de 12 estados y un tope de estados mayor, y entra con T3 en la fase siguiente.

### 13.4 · Predicciones, escritas antes de correr

1. **U1 ≈ T2 > F1** en alcance temprano: una unidad que tiene razón enseña como el
   omnisciente, porque lo que enseña es dónde mirar y no la verdad.
2. **U2 ≤ F1**, y con canalización: visita **menos** hipótesis que la fresca.
3. **U3 ≤ F1.** **M-canal = F1 exactamente.** **M-literal = F1 exactamente.**
   **M-pareja-simétrica**: 0 intervenciones.
4. **Cadena K5:** por defecto (Kirby, Griffiths & Smith 2014, `SV`, sobre cadenas de
   aprendices deterministas; la transferencia a nuestro banco es `HIPÓTESIS`) la fidelidad
   **cae** con k. Si se **mantiene**, es el
   hallazgo: lo transmitido por contraejemplos no se lava, porque cada alumna lo verifica en
   el mundo antes de volverse maestra. Se informan por separado la fidelidad **de función**
   (¿identifica?) y la **de forma** (¿máquina isomorfa?), porque en la prueba de instrumento
   se separaron: función 1,000 en las cuatro generaciones y forma 0,2–0,8.
5. **Pareja > F1** pareado, concentrado en la clase recurrente.

**Falsadores.** U1 ≈ F1 con intervenciones > 0: una unidad no puede enseñar a otra con
palabras en este banco. Fidelidad que **mejora** con k sin que mejore la identificación: la
cadena converge a algo estable y falso (el prior exagerado de Kirby) y hay que decirlo. Si
**M-canal ≠ F1**, el instrumento filtra información por un canal que no son las palabras:
defecto, y no se lee nada más.

---

## Enmiendas prospectivas

1. **M-c sin presupuesto infinito** (§10): 3 000 000 por intento y 20 000 000 por celda, con
   parálisis al alcanzarlo. Motivo: un criterio sin tope no es medible (E-32).
2. **La celda del maestro y de las dos unidades** (§13), con sus cuatro cambios de §13.2,
   todos medidos antes de la corrida pareada.

## Resultado · C5, sobre el banco completo · 28-oct-2026

**Corrida confirmatoria:** los **174** mundos W₁ del banco canónico, **2 134 familias**
(766 componibles, 1 368 no componibles), 998 descartadas por no abrir distinción nueva
—los mismos números del generador que el prototipo—. Brazos F1, C5, M-e, M-f. Reloj:
249 s con 11 trabajadores. Corrida **dos veces en dos procesos distintos**: todas las
cifras medidas, idénticas. Artefactos `artifacts/unidad_minima_09_fase2.{txt,json,jsonl}`
y la primera corrida conservada en `..._corrida1.txt`.

### La respuesta a la pregunta de la fase · `NULO POR TECHO DEL DISEÑO`

> **Corregido el 28-oct, después de la primera redacción y antes del cierre.** Esta sección
> decía «**No. Lo heredado no acumula**» y añadía que para Genesis no había nada que guardar.
> **Las dos frases afirmaban más de lo que la corrida puede sostener**, y lo señaló Fable
> revisando los artefactos. La corrección está abajo, en «Por qué esto es nulo y no
> negativo», con la medida que lo demuestra, y el error quedó registrado como **E-50** —con
> el agravante de que la propia puerta de §11 tenía la guarda que lo impedía y el programa
> **no la evaluaba**.

Curva de alcance (fracción que identifica W₂):

| clase | brazo | 64 | 128 | 256 | 512 | 1024 | 2048 | 3586 |
|---|---|---|---|---|---|---|---|---|
| componible | F1 | 0,642 | 0,832 | 0,933 | 0,965 | 0,988 | 0,988 | 0,996 |
| componible | **C5** | **0,644** | 0,832 | 0,933 | 0,965 | 0,988 | 0,988 | 0,996 |
| no componible | F1 | 0,684 | 0,893 | 0,965 | 0,980 | 0,996 | 1,000 | 1,000 |
| no componible | **C5** | **0,681** | 0,891 | 0,965 | 0,980 | 0,996 | 1,000 | 1,000 |

En el hito 64 de la clase componible —el punto donde la ficha dijo que se decidía—
**C5 0,644 contra F1 0,642, con z = 0,05** frente a un umbral ajustado de **2,64**.
Pareado por familia: identifica sólo C5 en **1** familia de 766 y sólo F1 en **0**. En la
clase control C5 queda un pelo por debajo (z = 0,21; sólo C5 en 1, sólo F1 en 6).

Formalmente eso cumple el falsador de §6. **Pero el falsador estaba mal planteado**, y por
eso el resultado no se lee como negativo.

**Y no es nulo por inactividad.** La reparación local actuó **3 302** veces en la clase
componible y **6 310** en la control; de las ~5,4 transiciones heredadas por celda
sobrevivieron **2,98** y **2,51** al final de la vida en W₂. La herencia estuvo ahí y
funcionó como se diseñó.

### Por qué esto es nulo y no negativo · el techo estaba en el tratamiento

**Lo que C5 hereda es la máquina de W₁. Identificar W₁ desde cero le cuesta a la unidad
fresca una mediana de 18 pasos.** Medido sobre los 174 mundos madre, como primer paso desde
el que su hipótesis identifica W₁ y no vuelve a perderlo:

| | |
|---|---|
| mínimo · mediana · p75 · p90 · p95 · máximo | 2 · **18** · 23 · **28** · 45 · 67 |
| antes del paso 28 | 156 / 174 (89,7 %) |
| **antes del paso 64** | **171 / 174 (98,3 %)** |
| antes del paso 128 | 174 / 174 (100 %) |

**La primera medida de la curva está en el hito 64.** Así que lo más que la herencia podía
ahorrar son ~18 pasos de los **64 que transcurren antes de la primera medición**: el
experimento **no podía detectar** un efecto de heredar, lo hubiera o no. Y las curvas de C5
y F1, **idénticas desde el hito 128**, lo dicen desde el otro lado: lo que cuesta en W₂ es
el **cerrojo nuevo**, que ninguna herencia puede traer; la parte heredada es la parte que
sale gratis de todos modos.

**Veredicto: `NULO POR TECHO DEL DISEÑO`, y ahora lo calcula el programa.** La corrida se
repitió con la puerta completa —los criterios (d) y (g) implementados y la precondición del
banco medida dentro de la campaña— y su salida dice, sin que medie prosa mía:

```
PRECONDICIÓN DEL BANCO (E-50) · lo que C5 hereda es la máquina de W1, y a la fresca
identificar W1 le cuesta: mediana 19, p90 29, máximo 68 pasos (173 mundos);
170/173 lo consiguen antes del primer hito (64).
  ⇒ la herencia NO TIENE dónde mostrarse: cualquier resultado de esta celda es
    NULO POR TECHO DEL DISEÑO
  [FAIL] (g) no saturación en componible: los brazos se separan en el hito 64
         (rango 0.642–0.644, z 0.05 contra umbral 2.64)
  [PASS] (g) ⇒ VEREDICTO componible: NULO POR TECHO DEL DISEÑO, no negativo
  [PASS] (g) ⇒ VEREDICTO no_componible: NULO POR TECHO DEL DISEÑO, no negativo
  criterios que la ficha §11 enumera y esta corrida NO evalúa (el veredicto es parcial
  mientras falten):
    (d) no sobreatribución: C1 <= F1 en los tres hitos (componible) y C2 ~ C1
```

(La mediana sale 19 y no 18 porque dentro de la campaña se usa `último error + 1`, que es
gratis, en vez de la comprobación directa del futuro fijo paso a paso; las dos medidas
coinciden en p75, p90, p95 y máximo y difieren en uno en la mediana. Se informa la que el
programa calcula.)

### El control de asimetría A↔B, pendiente desde la Fase 1

Intercambiar las dos letras del mundo es intercambiar el itinerario y los desempates, que
empiezan y se rompen hacia A. Corrida completa con el intercambio:

| | F1 hito 64 | C5 hito 64 | pareado | veredicto de la puerta |
|---|---|---|---|---|
| componible, normal | 0,642 | 0,644 | 1 / 0 | nulo por techo |
| componible, **A↔B** | **0,860** | **0,873** | **10 / 0** | nulo por techo |
| control, normal | 0,684 | 0,681 | 1 / 6 | nulo por techo |
| control, **A↔B** | 0,708 | 0,704 | 1 / 7 | nulo por techo |

**La conclusión es robusta al intercambio y los niveles absolutos no lo son**: la dificultad
del banco en el hito 64 salta de 0,642 a 0,860 en la clase componible según con qué letra
empiece el itinerario. Así que **ninguna cifra absoluta de esta fase se cita sin decir que
depende de la letra**, y las comparaciones entre brazos —que es lo que la puerta lee— sí
aguantan. Queda una señal **registrada y no leída**: con A↔B el pareado es 10 a 0 a favor de
C5 (McNemar z = 2,85, por encima del umbral de 2,64, aunque el z no pareado que la ficha
preregistró da 0,75). Vive dentro de una celda declarada nula por techo, así que **no se
lee como hallazgo**; es una razón más para la cascada honda.

**Lo que la herencia necesita para poder mostrarse, con número:** que W₁ le sea **caro** a la
fresca, es decir que tarde **más que el primer hito** en identificarlo. Eso pide mundos madre
de **6 a 8 estados con cuatro o más estados mínimos**, el tramo donde la Fase 1 midió que
identificar cuesta cientos de pasos o no se logra (ver `CIERRE_FASE_1.md` §3 y
[[fase-1-cerrada-degrada-en-8]]), y W₂ el cerrojo encima. Ésa es la cascada honda, y ahora
tiene criterio de admisión en vez de intuición.

### Lo que sí cambió, registrado y sin decidir nada

| | componible F1 → C5 | control F1 → C5 |
|---|---|---|
| repertorio al final de W₂ | 1,40 → **1,47** | 0,85 → 0,86 |
| instruibilidad | 1,32 → **1,35** | 1,35 → 1,35 |
| estados usados | 3,65 → **3,93** | 4,34 → 4,54 |
| trabajo medio (pasos) | 135 609 → 135 617 | 156 540 → 156 068 |

C5 termina con **más repertorio y más instruibilidad** en la clase componible, y con **más
estados**. Las tres diferencias son pequeñas y **no se les ha calculado el ruido**: se
informan como registro, y la puerta (e) —repertorio C5 ≥ F1— pasa por comparación simple,
que es lo que pedía. Lo que el gasto dice es que C5 **no es más caro** que la fresca: su
reparación local evita las relecturas que ahogaban a la heredera con traza.

### La garantía que C5 cede, en número

| | componible (766 celdas) | no componible (1 368) |
|---|---|---|
| `c5_consistente` | **1,000** | **1,000** |
| `c5_minima` | **0,685** | **0,777** |
| celdas determinadas | 764 / 766 | 1 356 / 1 368 |
| `c5_estados_sobre_minimo` | **0,45** | 0,31 |
| heredadas / revisadas / supervivientes | 5,38 / 3 302 / 2,98 | 5,47 / 6 310 / 2,51 |
| `herencia_borrada_por_distincion` | 28 celdas | 34 celdas |

§5-bis prometió medir la pérdida en vez de suponerla, y aquí está: la **consistencia con la
traza retenida se cumple en las 2 134 celdas, sin una excepción**; la **minimalidad se pierde
en el 31,5 % y el 22,3 %** de las celdas, por **0,45 y 0,31 estados de más** en promedio. Eso
es el precio de heredar la máquina, y se pagó **sin recibir nada en alcance**.

**Una advertencia sobre el piloto.** Los 12 primeros mundos (§10) daban `c5_minima` = 0,978
y 0,956 y `herencia_borrada` = 0. El banco completo da 0,685 y 0,777 y 28 y 34 celdas. El
piloto subestimó la pérdida **en un orden de magnitud**: doce mundos de 174 no representan
este banco para esta medida, y ninguna cifra de minimalidad debe citarse de un piloto.

### Veredicto de la puerta de §11

| | |
|---|---|
| **(a)** `c5_consistente == 1,000` | **PASS** en las dos clases |
| **(b)** los seis mutantes | **PASS** los seis (§10) |
| **(c)** acumulación: C5 > F1 en el hito 64, componible, z sobre umbral | **FAIL** — z = 0,05 contra 2,64 |
| **(c)** control: C5 ≤ F1 en el hito 64, no componible | **PASS** |
| **(e)** repertorio C5 ≥ F1 | **PASS** (1,47 ≥ 1,40) |
| **(f)** actividad: `transiciones_heredadas_revisadas` > 0 | **PASS** (3 302 y 6 310) |

### Qué queda dicho, y qué no

**Queda dicho, y sólo esto:**
- El mecanismo de C5 **funciona**: hereda, repara localmente, y la reparación actúa (3 302 y
  6 310 veces). No es una idea sin implementación.
- La **consistencia** con la traza retenida se cumple en las 2 134 celdas sin una excepción, y
  la **minimalidad se pierde** en el 31,5 % y el 22,3 % de ellas, por 0,45 y 0,31 estados. El
  precio de heredar está medido aunque la ganancia no se haya podido medir.
- C5 **no es más caro** que la fresca: su reparación local evita las relecturas que ahogaban a
  la heredera con traza (135 617 contra 135 609 pasos).
- Heredar la **traza** sí quedó medido como lastre por el prototipo, y eso se sostiene: allí la
  heredera gastaba 5× más y olvidaba 6,6× más, que no es un techo de medición sino un coste.

**No queda dicho** —y la primera redacción de esta sección lo dijo, mal—:
- que heredar la máquina no acumule. **No se midió**: el banco no lo permitía.
- que Genesis no tenga qué guardar. **De esto no se sigue nada sobre Genesis.**

**Lo que sí queda, para la ficha siguiente, como requisito mecánico antes de correr:** que la
unidad fresca tarde en W₁ **más que el primer punto de medición**, comprobado y escrito en el
artefacto. Sin eso, la celda es nula antes de empezar y no se corre.


---

## Resultado · la celda del maestro y de las dos unidades · 28-oct-2026

> ### ⚠ ESTA SECCIÓN ES LA **PRIMERA** CORRIDA Y QUEDA **SUPERADA**
>
> Se conserva **sin corregir**, a propósito, porque es la evidencia de dos defectos de
> instrumento que Fable detectó leyendo los artefactos y que están registrados: **E-49** (la
> campaña arrancó con el módulo **sin** el arreglo del momento de medición, así que el
> `alcance` de cada fila se midió **512 pasos después** de su etiqueta, al terminar el examen
> de retención) y el defecto de la cadena (**la maestra de la generación k+1 era la unidad
> después de ese examen**, con 512 pasos libres de ventaja no declarados).
>
> **Las curvas de esta corrida son válidas; la columna de estado final no.** Y dos de las
> frases de abajo son falsas por eso: que la función se conserve «1,000 en las cinco
> generaciones» **en las dos clases** (se conserva en la componible y **cae** en la control) y
> que el alcance temprano **mejore** con las generaciones (es **plano**).
>
> **Los números que valen están en `CIERRE_FASE_2.md` §3**, de la segunda corrida, con la
> puerta sobre la intersección de familias y el hito de decisión declarado.

**Corrida:** las **2 134 familias** (766 componibles, 1 368 control), **30 546 filas**, quince
celdas, 1 015 s con 11 trabajadores. Canal `ve_la_hipotesis`. Artefactos
`artifacts/unidad_minima_10_maestro.{txt,json,jsonl}`. Las comparaciones se leen
**pareadas y restringidas a las familias donde corren las dos celdas**
(`analisis_10_pareado.py`, McNemar con corrección de continuidad, umbral de z 3,62 por
Bonferroni sobre 168 comparaciones), porque U1 y U2 corren por construcción sobre
subconjuntos distintos y una media contra otra media mezclaría el maestro con la dificultad
del subconjunto.

### 1 · Lo que decide no es el maestro, es el disparo

Mismo maestro omnisciente, mismo conocimiento, mismo presupuesto de vida. Lo único que
cambia es **cuándo** interviene. Alcance pareado contra F1 en la clase componible:

| celda | hito 64 | F1 | z pareado | sólo la celda / sólo F1 |
|---|---|---|---|---|
| **T1** (espera al error) | 0,638 | 0,642 | 0,34 | 16 / 19 |
| **T2** (no espera) | **0,939** | 0,642 | **14,81** | **230 / 3** |

T2 llega a **1,000 desde el hito 128** y lo mantiene; T1 es indistinguible de no tener
maestro en los seis hitos. En la clase control, T2 0,977 contra 0,684 (z 22,13; 400 / 0).
**Es el resultado más limpio del día**, y confirma sobre el banco entero lo que la prueba de
instrumento de un mundo había sugerido (§13.2, punto 2): la predicción se escribió antes y
aguantó con un margen enorme.

### 2 · Una unidad sí puede enseñar, y su techo es su propia máquina

| hito | U1 | F1 | z pareado | sólo U1 / sólo F1 |
|---|---|---|---|---|
| 64 | **0,818** | 0,645 | **8,22** | **193 / 61** |
| 128 | 0,865 | 0,835 | 1,62 | 104 / 81 |
| 256 | 0,865 | 0,937 | 4,45 | 46 / **101** |
| 2048 | 0,865 | **0,992** | 9,20 | 6 / **103** |

**El alumno llega antes y llega menos lejos.** La maestra-unidad acelera de verdad al
principio (+0,173 pareado en el hito 64) y después **estanca al alumno en 0,865**, por
debajo de la vara. En la clase control el techo es más bajo todavía: U1 se queda en 0,779
contra 0,965 de F1 (z 14,91). La lectura: lo que una unidad enseña incluye **sus puntos
ciegos**, y el alumno los paga, porque gastó su vida yendo donde la maestra señalaba en vez
de explorar. **La predicción 1 de §13.4 queda medio confirmada y medio refutada**: U1 > F1
temprano, sí; U1 ≈ el omnisciente, **no** —T2 llega a 1,000 y U1 no pasa de 0,865—.

### 3 · Un maestro equivocado es mucho peor que ninguno, y eso prueba que el canal lleva información

| celda | hito 64 | hito 2048 | pareado al final (sólo celda / sólo F1) |
|---|---|---|---|
| **U2** maestra que no identificó | 0,186 | 0,219 | 0 / **205** |
| **U3** maestra de otro mundo | 0,242 | 0,244 | 0 / **568** |
| **U-sham** palabras donde ya acierta | **0,000** | 0,000 | 0 / **757** |

Las predicciones 2 y 3 se cumplen, y no al margen: **catastróficamente**. Si el canal no
llevara información, un maestro equivocado no podría hacer daño; hace muchísimo. Y U-sham
—mandar al alumno a lo que ya sabe— lo deja en **0,000 en los siete hitos**, con `retención
congelada` 0,61: es el precio de que alguien te gaste la vida en lo que ya sabés, y **se
recupera entero con 512 pasos libres** (`tras irse` = 0,959).

### 4 · La cadena de cinco generaciones · las dos fidelidades, separadas

| generación | **función**: identifica W₂ | alcance en el hito 64 | **forma**: isomorfa a la anterior | **forma**: isomorfa a la primera | transiciones distintas |
|---|---|---|---|---|---|
| 2 | 1,000 | 0,818 | 0,529 | 0,529 | 5,07 |
| 3 | 1,000 | 0,865 | 0,862 | 0,488 | 8,64 |
| 4 | 1,000 | 0,837 | 0,953 | 0,497 | 8,62 |
| 5 | 1,000 | **0,873** | **0,955** | **0,485** | 8,51 |

**La función se conserva entera a lo largo de cinco transmisiones y la forma se va.** Y hay
un detalle que no estaba en ninguna predicción: la isomorfía con la **anterior** sube hasta
0,955 mientras la isomorfía con la **primera** se queda clavada en ~0,49. La cadena **no se
disuelve: converge a una forma estable que en la mitad de los linajes no es la del
ancestro.** Es el patrón de Kirby a medias —la estructura se lava, la función no— con el
añadido de que lo estable **no es falso**: sigue identificando el mundo. El falsador de
§13.4 («la cadena converge a algo estable y falso») **no** se cumple.

Y la capacidad no sólo se conserva, **mejora**: en el hito 64, de 0,818 (K2) a 0,873 (K5)
contra 0,642 de la vara, z pareado 11,17. Las generaciones tardías llegan **antes** que las
tempranas. En la clase control, en cambio, la cadena hereda el techo de U1 y queda por
debajo de la vara a partir del hito 128 (0,745 contra 0,893).

### 5 · Los controles de instrumento, y dos cosas que yo dije mal

- **M-canal** (recibe la palabra y **no la vive**) da F1 **exactamente**: pareado **0 y 0 en
  los seis hitos de las dos clases**. El único canal es vivir la palabra. El control más
  importante de la celda, y pasa perfecto.
- **M-pareja-simétrica**: **0 intervenciones en 3 586 pasos**, 3 586 contraejemplos
  imposibles, curva idéntica a F1 en las dos clases. El defecto de §13.2 punto 3 queda
  **medido** sobre el banco entero, no afirmado.
- **La pareja cooperativa NO supera a la vara** (predicción 5, **refutada**): 0,597 contra
  0,642 en el hito 64, y **en ninguna familia identifica donde F1 falla** (pareado 0 / 29).
  En la clase control es peor (0,547 contra 0,684, z 7,46). Con la asimetría que yo elegí
  —otro vértice y el itinerario desplazado—, dos unidades enseñándose mutuamente rinden
  menos que una sola. La población de muchos **no** queda justificada por este banco.
- **Y mi afirmación de que el disparo literal «reproduce F1 curva por curva» era de un mundo
  y es falsa en el banco.** M-literal interviene 218 y 482 veces, **un tercio de sus palabras
  son otra letra**, y el efecto neto es **ligeramente dañino**: 0,601 contra 0,684 en el
  control (z 4,56; pareado 24 / 138). No era vacío: era **malo**. La cifra de §13.2 queda
  corregida aquí, que es donde manda la corrida y no el piloto.

### 6 · Lo que esta celda deja

- **El maestro no necesita ser omnisciente para acelerar**, pero sí para no poner techo. Una
  unidad basta para llegar antes; no basta para llegar lejos.
- **Lo transmitido por contraejemplos no se lava**, porque cada alumna lo verifica en el
  mundo antes de volverse maestra: función 1,000 en las cinco generaciones. Eso es «antes de
  maestro, alumno» **como resultado medido**, no como lema.
- **Para Genesis hay, por primera vez, algo que guardar que no es una máquina:** quién enseñó
  a quién y con qué palabras. Con una condición medida: la genealogía conserva la
  **capacidad**, no la **forma** — guardar la máquina del ancestro no serviría de mucho,
  porque en la mitad de los linajes la máquina viva ya no es isomorfa a ella.
- **La pregunta que abre, y que es la de Wis (28-oct):** si la organización se transforma y
  la capacidad se conserva, ¿sirve esa organización transformada para aprender algo
  **nuevo**? Eso es `unidad_minima_11_adquisicion.py` y es la segunda mitad; una sola de las
  dos propiedades no es desarrollo acumulativo.

---

## Resultado · la adquisición posterior (la pregunta de Wis del 28-oct) · `NULO Y FALTO DE POTENCIA`

**La pregunta, en sus palabras:** «¿puede una célula conservar una capacidad mientras modifica
su organización interna y utilizar esa organización transformada para aprender algo nuevo?»
Son **dos** propiedades seguidas, y sólo las dos juntas serían desarrollo cognitivo
acumulativo. Código `unidad_minima_11_adquisicion.py`; artefactos
`artifacts/unidad_minima_11_adquisicion.{txt,json,jsonl}`; 362 s con 11 trabajadores.

### Propiedad 1 · conservación con organización transformada: **ocurre**

Medida en la celda del maestro, sobre las 2 134 familias (tabla de §4 del resultado
anterior): la función se conserva **1,000 en las cinco generaciones** y el alcance temprano
**mejora** (0,818 → 0,873 contra 0,642 de la vara), mientras la isomorfía con la primera
generación se queda en **0,485** y la isomorfía con la anterior sube a **0,955**. La cadena
converge a una forma estable que en la mitad de los linajes no es la del ancestro, y esa
forma estable **no es falsa**: sigue identificando el mundo.

### Propiedad 2 · adquisición posterior: **la celda no contesta**

Banco: de los 174 mundos madre, **28 familias** con `6 ≤ n_min(W₃) ≤ 8` medido **desde el
punto por el que la unidad entra** a W₃ (E-52). W₃ de 12 estados, vida de 18 434 pasos,
futuro fijo el bloque **completo** de las 4 096 palabras de longitud 12 (49 152 pasos).
Precondición cumplida de verdad: a la fresca identificar W₃ le cuesta **128 pasos de
mediana** y **32 de 112 celdas no lo logran en toda su vida** — el doble del primer hito, y
con un 29 % que nunca llega.

| brazo | hito 64 | 128 | 256 | 512 | 2048 | 18 434 | estados | exactitud hito 64 |
|---|---|---|---|---|---|---|---|---|
| A-fresca | 0,0357 | 0,3929 | 0,5000 | 0,6429 | 0,6429 | 0,7143 | 5,71 | **0,9139** |
| A-directa | 0,0357 | 0,3929 | 0,5000 | 0,6429 | 0,6429 | 0,7143 | 5,93 | 0,8897 |
| A-K5 | 0,0357 | 0,3929 | 0,5000 | 0,6429 | 0,6429 | 0,7143 | 5,93 | 0,8897 |
| A-K5-lesion | 0,0357 | 0,3929 | 0,5000 | 0,6429 | 0,6429 | 0,7143 | 5,71 | 0,9139 |

**Pareado: 0 y 0 en los siete hitos y en las tres comparaciones.** No hay una sola familia
donde un brazo identifique y otro no.

**Y aquí me equivoqué al leerlo, y lo corrijo con la medida.** Al ver cuatro curvas idénticas
dígito a dígito —incluida la del brazo lesionado— dije que eso no era un nulo sino una firma
de defecto, y supuse que el olvido borraba la herencia antes del primer hito. **Fui a medirlo
y es falso:** de las 6–8 transiciones heredadas sobreviven **1 a 5 en el paso 64**, y los
olvidos no empiezan hasta el paso 128–256. La herencia está viva cuando se mide.

Lo que de verdad pasa es más sobrio, y se ve en las dos últimas columnas: **los brazos sí
difieren** —en estados (5,71 contra 5,93) y en exactitud del hito 64 (0,9139 contra
0,8897)— y la medida **binaria** no separa lo que la **graduada** sí ve. Con 28 familias,
«no se separan» y «no puedo verlo» son indistinguibles.

**Veredicto: `NULO Y FALTO DE POTENCIA`.** La única diferencia medible es pequeña, temprana y
**en contra** de la herencia (−0,024 de exactitud en el hito 64, que es lo que cuesta cargar
con una máquina del mundo anterior mientras todavía sirve de poco), y se disuelve después.
La celda **no contesta** la segunda mitad de la pregunta.

**Qué haría falta para que contestara**, con número y no con intuición:
1. **Más banco.** 28 familias no alcanzan para un umbral ajustado. Dos vías sin tocar el
   mecanismo: tomar **todos** los W₃ de cada W₂ en la banda en vez de sólo el más difícil
   (×36 candidatos por familia), y bajar el suelo de la banda a 5.
2. **La medida graduada como principal**, no la binaria: `exactitud` sobre el futuro fijo y
   **pasos hasta identificar**, que es la que sí ve diferencias de 0,02.
3. **Y la tensión del organismo que esto deja al descubierto**, que es lo más interesante que
   sale de aquí: la unidad llega a W₃ con **31 olvidos por vida**. El olvido por fracaso es
   lo que le permite vivir en un mundo que cambia —M-c lo demostró: sin él se ahoga, curva
   plana en 0,022 contra 1,000— y es también lo que le impide **acumular**, porque cada
   olvido la deja con sus últimos 64 pasos. **El mismo órgano que la hace sobrevivir al
   cambio le impide heredarse.** Esa es una pregunta de diseño del ser, no un defecto de
   instrumento, y es la que yo propondría para la fase siguiente: un olvido que **conserve la
   máquina y suelte la traza** —que es exactamente lo que C5 hace al cambiar de mundo, pero
   aplicado al olvido interno— en vez de volver al núcleo de 64 pasos.

### Qué queda dicho de la pregunta de Wis

- **Conservar la capacidad mientras la organización se transforma: sí, medido.** Cinco
  generaciones, 2 134 familias, con la forma yéndose y la función intacta.
- **Usar esa organización transformada para aprender algo nuevo: no se ha podido medir.** No
  es un no; es una celda de 28 familias cuya medida binaria no separa, con la diferencia
  graduada pequeña y en contra.
- Por tanto **no se puede afirmar todavía desarrollo cognitivo acumulativo**, y tampoco
  negarlo. Lo que sí hay es el camino exacto para decidirlo, y una pregunta de diseño del ser
  que antes no estaba sobre la mesa.