# Cierre de la Fase 2 · ¿lo vivido se acumula? · 28-oct-2026

**Programa:** UNIDAD MÍNIMA. **Ejecutó:** Opus. **Orientó y revisó contra los artefactos:** Fable. **Adjudicó:** Wis.
**Documento de entrada que ordena el día:** `ORIENTACIONES_OPUS_PUNTO_DE_ENTRADA.md`. **Ficha de la fase:** `APERTURA_FASE_2_ACUMULACION.md` (con sus enmiendas fechadas). **Registro:** `ERRORES_Y_GUARDAS.md`, 52 entradas al cerrar.

**El criterio de la fase, fijado por Wis el 27-oct:** no es economía, es **desarrollo**. Alcance, exactitud, repertorio e instruibilidad. **El cómputo y el tiempo se registran siempre y no deciden nunca.**

**La regla nueva de Wis, aplicada en cada resultado de abajo:** si un resultado no cambia un órgano, el mundo o la herencia, **es bibliográfico y se dice así**.

---

## 0 · La respuesta de la fase, en cuatro frases

1. **Heredar no se pudo medir en este banco.** Ni la traza (lastre, medido) ni la máquina (nulo por techo del diseño): lo que se heredaba era la parte que la unidad fresca consigue gratis en 18 pasos, y la primera medición está en el paso 64.
2. **Enseñar sí funciona, y lo que enseña es el disparo.** El mismo maestro omnisciente no hace nada si espera al error y lleva a la alumna de 0,64 a 0,94 si no espera.
3. **Una unidad puede enseñar a otra con palabras**, menos que quien conoce el mundo y mucho más que nadie. Y su techo es su propia máquina: el alumno llega antes y llega menos lejos.
4. **El linaje transmite capacidades, no máquinas — y sólo cuando el mundo nuevo compone con el viejo.** Cinco generaciones conservan la función en la clase componible (0,865 → 0,872) y la pierden en la control (0,779 → 0,737), mientras en las dos la estructura deriva y se estabiliza en una forma distinta de la original.

---

## 1 · Lo que se construyó, y qué toca cada cosa

| módulo | qué es | toca |
|---|---|---|
| `unidad_minima_08_fase2.py` | prototipo exploratorio de Fable (E-37): heredar la **traza** | — (no se tocó; `sha256 621c0534…`) |
| `unidad_minima_09_fase2.py` | **C5** (heredar la máquina sin la traza) y los **seis mutantes** de la ficha | importa 08 |
| `unidad_minima_10_maestro.py` | **el maestro** (T1, T2) y **la maestra-unidad** (U1, U2, U3, U-sham, M-canal, M-literal), la **cadena** de cinco y la **pareja** | importa 08 y 09 |
| `unidad_minima_11_adquisicion.py` | **la adquisición posterior**: la organización transformada como base para un mundo nuevo | importa 08, 09 y 10 |
| `analisis_10_pareado.py` | las comparaciones **pareadas sobre la intersección** de familias | lee las filas |
| `guardas.py` | las guardas importables con sus contadores | — |

Ninguno modifica a otro: cada uno **importa** y añade. Así «corren sobre el mismo banco y la misma medida» es estructural y no una afirmación.

---

## 2 · C5 · heredar la máquina sin la traza · `NULO POR TECHO DEL DISEÑO`

**Corrida:** 174 mundos madre, **2 134 familias**, dos procesos con las cifras medidas idénticas. Brazos F1, C5, M-e, M-f.

**El resultado.** En el hito 64 de la clase componible —el punto donde la ficha dijo que se decidía— **C5 0,644 contra F1 0,642**, z 0,05 contra un umbral de 2,64; pareado 1 familia a 0 de 766. Curvas idénticas desde el hito 128.

**Por qué es nulo y no negativo, con la medida que lo demuestra.** Lo que C5 hereda es la máquina de W₁, y a la unidad fresca identificar W₁ le cuesta:

| | mín | **mediana** | p75 | **p90** | p95 | máx |
|---|---|---|---|---|---|---|
| primer paso desde el que identifica W₁ y no lo pierde | 2 | **18** | 23 | **28** | 45 | 67 |

**171 de 174 mundos antes del paso 64.** La primera medida de la curva está en el hito 64: lo más que la herencia podía ahorrar son ~18 pasos de los 64 que pasan **antes de medir**. El experimento no podía detectar el efecto, lo hubiera o no. Lo que cuesta en W₂ es el **cerrojo nuevo**, que ninguna herencia trae.

El veredicto lo **calcula el programa**, no la prosa: la precondición del banco y el criterio (g) de la ficha están implementados y su salida dice `NULO POR TECHO DEL DISEÑO` en las dos clases, más la lista de los criterios de la ficha que esa corrida **no** evalúa (el (d), que pide los brazos C1 y C2).

**Lo que sí quedó medido de C5, y se sostiene:**
- El mecanismo **funciona y actúa**: 3 302 y 6 310 reparaciones locales; de ~5,4 transiciones heredadas por celda sobreviven 2,98 y 2,51.
- **La garantía que cede, en número** (lo que §5-bis prometió medir y no suponer): `c5_consistente` = **1,000 en las 2 134 celdas, sin una excepción**; `c5_minima` = **0,685** y **0,777** —la minimalidad se pierde en el 31,5 % y el 22,3 % de las celdas— por **0,45** y 0,31 estados de más.
- **No es más caro** que la fresca (135 617 contra 135 609 pasos): la reparación local evita las relecturas que ahogaban a la heredera con traza.

**Qué cambia en el ser:** **un órgano nuevo, conservado.** La reparación local de transiciones heredadas es un mecanismo que no existía y que funciona: permite conservar una máquina al cambiar de mundo sin que la primera refutación la borre. Se queda en el ser. Lo que **no** cambia es la herencia como estrategia: sigue sin estar medida.

**Los seis mutantes de la ficha §10 corrieron antes de la confirmatoria y pasaron los seis.** El que importaba:
- **M-c (sin olvido)** reprodujo **el ahogo** con ojos frescos y otra implementación: curva **plana en los siete hitos** (0,022 → 0,044 componible; 0,0215 constante en el control) contra **1,000** de la fresca; 302 y 620 topes. El diagnóstico del que dependía todo C5 queda verificado.
- **M-a (olvido total)** dio un hallazgo no previsto: olvidar **del todo** (0,444 en el hito 64) va **mejor** que conservar el núcleo de 64 pasos (0,356), y queda casi en la fresca (0,467). **El núcleo de 64 no es neutro: estorba**, porque lo que conserva es mundo viejo.
- **M-e** y **M-f** reproducen F1 en **las diecisiete medidas** sobre 138 familias.
- **M-b** pasa, y se dice que su veredicto se apoya en **una** celda: en las otras 137 el órgano «elegir» actúa ~3 pasos de 3 586 y no puede distinguir. En esa una, la versión «más lejana» eligió 3 571 pasos y **no identificó nunca**; la «más cercana» eligió 14 e identificó en todos los hitos.
- **M-d** descarta el **100 %** de la clase componible con el bit conmutado y la guarda `no_vacio` aborta.

**El control de asimetría A↔B**, pendiente desde la Fase 1: intercambiar las letras mueve la dificultad del hito 64 de **0,642 a 0,860** en la clase componible **sin cambiar ninguna conclusión**. Por tanto **ninguna cifra absoluta de esta fase se cita sin decir que depende de la letra**; las comparaciones entre brazos aguantan. Señal **registrada y no leída**: con A↔B el pareado de C5 es 10 a 0 (McNemar z 2,85), dentro de una celda declarada nula por techo.

**Lo que la herencia necesita para poder mostrarse, con número:** que W₁ le cueste a la fresca **más que el primer punto de medición**. Eso pide mundos madre de 6 a 8 estados con **n_min ≥ 4**, el tramo donde la Fase 1 midió que identificar cuesta cientos de pasos o no se logra. Es la puerta del mundo caro de la Fase 3.

---

## 3 · El maestro, la maestra-unidad y el linaje

**Corrida:** las **2 134 familias** (766 componibles, 1 368 control), **30 546 filas**, quince celdas, 11 trabajadores. Canal `ve_la_hipotesis`. Toda comparación es **pareada sobre la intersección** de familias con F1 (McNemar con corrección de continuidad, umbral de z 2,87), **en el primer hito donde F1 está por encima del suelo** sobre esa intersección — regla declarada, igual para todas las celdas, porque donde la vara vale 0,000 no se puede decir si el tratamiento ayuda.

> **Esta corrida es la segunda.** La primera tenía dos defectos de instrumento que Fable detectó leyendo los artefactos y que están en §5: el `alcance` de la fila se medía 512 pasos después de su etiqueta (E-49: la campaña arrancó con el módulo sin el arreglo) y la maestra de la generación k+1 era la unidad **después** del examen de retención, con 512 pasos libres de ventaja no declarados. Los dos corregidos; las curvas de la primera corrida eran válidas y la columna de estado final no.

### 3.1 · Lo que enseña es el disparo, no el maestro

Mismo maestro omnisciente, mismo conocimiento del mundo, mismo presupuesto de vida. Lo único que cambia es **cuándo** interviene.

| celda | componible, hito 64 | z pareado | control, hito 64 | z pareado |
|---|---|---|---|---|
| F1 (sin maestro) | 0,642 | — | 0,684 | — |
| **T1** espera al error | 0,638 (16/19) | **0,34** | 0,658 (25/**61**) | **3,77** |
| **T2** no espera | **0,939** (**230**/3) | **14,81** | **0,977** (**400**/0) | **19,95** |

**T2 llega a 1,000 desde el hito 128** y lo mantiene. T1 es indistinguible de no tener maestro en la clase componible y, en la clase control, **significativamente peor** que no tenerlo: esperar al error y mandar entonces a la discrepancia más corta **cuesta**. El resultado más limpio de la fase.

**Qué cambia en el ser: un órgano nuevo, y su parámetro decisivo.** El canal de palabras entra al ser como órgano, con el **disparo** como su parámetro —no «cuándo hay error» sino «siempre que haya algo que distinguir»—. Y entra una norma de diseño: un maestro que espera al error no enseña, porque la palabra más corta donde el alumno falla es la letra que ya iba a tomar (E-46, medido en M-literal: 0,613 contra 0,645, z 2,88 en contra).

### 3.2 · Una unidad puede enseñar, y su techo es su propia máquina

| | componible | control |
|---|---|---|
| U1 en el hito 64 | **0,818** contra 0,645 (193/61, z **8,22**) | **0,770** contra 0,684 (235/117, z **6,24**) |
| U1 al final de la vida | **0,865** contra 0,996 | **0,779** contra 1,000 |
| T2 al final | 1,000 | 1,000 |

**El alumno llega antes y llega menos lejos.** Una unidad que identificó el mundo enseña de verdad —y mucho— al principio, y después **estanca al alumno en su propio nivel**: 0,865 contra 0,996 de la vara. **La predicción «U1 ≈ el omnisciente» queda refutada**: una unidad enseña **menos** que quien conoce el mundo (0,818 contra 0,939) y **mucho más que nadie**. La lectura mecánica: lo que una unidad enseña incluye **sus puntos ciegos**, y el alumno los paga porque gastó su vida yendo donde la maestra señalaba en vez de explorar.

**Qué cambia en el ser:** el maestro **no tiene que ser omnisciente** para que el linaje arranque —basta una unidad que ya vivió—, y a cambio aparece una restricción nueva y medida: **el techo del alumno es la máquina del maestro.** Para pasar de ese techo hace falta algo que la Fase 3 ya tiene previsto: un tercero que compare dos vidas en vez de copiar una.

### 3.3 · El maestro equivocado canaliza al error, y eso prueba que el canal lleva información

| celda | componible | z | control | z |
|---|---|---|---|---|
| **U2** maestra que no identificó (hito 128) | 0,219 contra 0,529 (12/**97**) | **8,05** | 0,167 contra 0,660 (11/**224**) | **13,83** |
| **U3** maestra de otro mundo | 0,242 contra 0,645 (10/**317**) | **16,92** | 0,194 contra 0,687 (8/**678**) | **25,54** |
| **U-sham** palabras donde ya acierta | **0,000** contra 0,645 (0/**492**) | **22,14** | 0,003 contra 0,684 (0/**932**) | **30,50** |

Si el canal no llevara información, un maestro equivocado no podría hacer daño. Hace **muchísimo**. U-sham deja al alumno en **0,000 en los siete hitos** y se recupera entero con 512 pasos libres: es el precio exacto de que alguien te gaste la vida en lo que ya sabés.

**Y un matiz que no se cumple como se predijo:** la canalización **no** se ve como «visita menos hipótesis». U2 visita 9,1 hipótesis canónicas distintas contra 8,9 de la vara en la clase componible (**FAIL**), y sí visita menos en la control (PASS). Donde sí se ve claro es en U3 (4,9) y U-sham (2,0). Así que el maestro equivocado **daña el alcance sin estrechar necesariamente la exploración**: son dos cosas distintas y conviene no confundirlas.

**Qué cambia en el ser:** entra una prohibición, y es de las que sólo el linaje puede saber (la lógica del genoma de la Fase 3): **enseñar desde una máquina no verificada es peor que no enseñar.** Antes de maestro, alumno — y ahora con número.

### 3.4 · El linaje transmite capacidades, no máquinas · y sólo cuando el mundo compone

Las dos fidelidades, separadas en criterios con nombre (comprobación 3 de Fable):

| | **función** (identifica) | | | | **estructura** (isomorfía) | |
|---|---|---|---|---|---|---|
| generación | 2 | 3 | 4 | 5 | con la anterior | con la primera |
| **componible** | 0,865 | 0,860 | 0,872 | **0,872** | 0,505 → **0,830** | **0,484** |
| **control** | 0,779 | 0,734 | 0,729 | **0,737** | 0,533 → 0,718 | 0,493 |

- **La función se conserva en la clase componible** (0,865 → 0,872, PASS) **y se degrada en la control** (0,779 → 0,737, FAIL, caída de 0,042). **Kirby se cumple donde el mundo nuevo no compone con el viejo, y no se cumple donde compone.** Ésa es la condición, y no estaba en ninguna predicción.
- **La estructura deriva y se estabiliza en las dos clases:** la isomorfía con la **primera** generación se queda en ~0,48 y la isomorfía con la **anterior** sube de 0,51 a 0,83. La cadena **converge a una forma estable que en la mitad de los linajes no es la del ancestro**, y esa forma estable **no es falsa**: sigue identificando el mundo. El falsador de §13.4 —«converge a algo estable y falso»— **no** se cumple.

**Dos correcciones a lo que yo había informado antes**, las dos por los defectos de la primera corrida: (a) la función **no mejora** con las generaciones —es plana, 0,865 → 0,872—; lo que parecía mejora venía de que la maestra tenía 512 pasos libres de ventaja; (b) la función **no** se conserva en las dos clases: se conserva en la componible y cae en la control.

**Qué cambia en el ser: el contenido de la herencia.** Lo que pasa entre generaciones y sobrevive son **capacidades**, no máquinas: guardar la máquina del ancestro sirve de poco porque en la mitad de los linajes la máquina viva ya no es isomorfa a ella. Eso es, literalmente, el diseño del genoma de la Fase 3 —relaciones **certificadas** y palabras con marca, no un volcado de `trans`— y queda apoyado en medida en vez de en intuición.

### 3.5 · Dos iguales que se enseñan salen peor que uno solo

| | las dos identifican | pareado contra F1 |
|---|---|---|
| componible | 0,962 | sólo la pareja en **0** familias, sólo F1 en **26** |
| control | 0,885 | sólo la pareja en **0**, sólo F1 en **157** |

**En ninguna familia la pareja identifica donde la vara falla.** Con la asimetría mínima que declaré —otro vértice y el itinerario desplazado un paso—, dos frescas enseñándose mutuamente **propagan errores**: cada una manda a la otra a donde su propia máquina equivocada cree que hay algo. **Bender–Slonim no se transfiere a este canal.**

Y el mutante que lo enmarca: **M-pareja-simétrica**, las dos en el mismo sitio con la misma corriente, cruza **0 bits en 3 586 pasos** (3 586 contraejemplos imposibles) y da la curva de F1 exactamente. El defecto E-47 queda medido sobre el banco entero.

**Qué cambia en el ser:** **la población de muchos no se abre todavía**, y no por economía sino porque está medido que cooperar entre iguales sin que ninguno sepa es peor que estar solo. Lo que la Fase 3 añade —un tercero que **compara** dos vidas en vez de copiar una— es exactamente lo que falta aquí, y ahora se sabe por qué.

### 3.6 · El control que valida el canal

**M-canal** —el alumno recibe la palabra y **no la vive**— da F1 **exactamente**: pareado **0 y 0** en los siete hitos de las **dos** clases, z 0,00. **El único canal es vivir la palabra.** Es el control más importante de la celda y no deja margen: nada cruza por detrás.

---

## 4 · La adquisición posterior · `NULO Y FALTO DE POTENCIA`

**La pregunta es de Wis (28-oct):** «¿puede una célula conservar una capacidad mientras modifica su organización interna y utilizar esa organización transformada para aprender algo nuevo?» Son **dos** propiedades seguidas; sólo las dos juntas serían desarrollo cognitivo acumulativo.

**Primera mitad: ocurre** (§3, la cadena). **Segunda mitad: la celda no contesta.**

Banco: **28 familias** de los 174 mundos madre, con `6 ≤ n_min(W₃) ≤ 8` medido **desde el punto por el que la unidad entra** a W₃. W₃ de 12 estados, vida de 18 434 pasos, futuro fijo el bloque **completo** de las 4 096 palabras de longitud 12 (49 152 pasos). Precondición cumplida: a la fresca identificar W₃ le cuesta **128 pasos de mediana** y **32 de 112 celdas no lo logran en toda su vida**.

| brazo | hito 64 | 128 | 512 | 18 434 | estados | exactitud hito 64 |
|---|---|---|---|---|---|---|
| A-fresca | 0,0357 | 0,3929 | 0,6429 | 0,7143 | 5,71 | **0,9139** |
| A-directa | 0,0357 | 0,3929 | 0,6429 | 0,7143 | 5,93 | 0,8897 |
| A-K5 | 0,0357 | 0,3929 | 0,6429 | 0,7143 | 5,93 | 0,8897 |
| A-K5-lesion | 0,0357 | 0,3929 | 0,6429 | 0,7143 | 5,71 | 0,9139 |

Pareado **0 y 0** en los siete hitos y en las tres comparaciones. **Y una lectura mía corregida con la medida:** dije que cuatro curvas idénticas eran «firma de defecto» y supuse que el olvido borraba la herencia antes del primer hito. **Falso:** de 6–8 transiciones heredadas sobreviven **1 a 5 en el paso 64** y los olvidos no empiezan hasta el 128–256. Lo que pasa es que los brazos **sí** difieren —estados 5,71 contra 5,93, exactitud del hito 64 0,9139 contra 0,8897— y la medida **binaria** no ve lo que la **graduada** sí. Con 28 familias, «no se separan» y «no puedo verlo» son indistinguibles.

**Qué cambia en el ser: una tensión de diseño, y es el resultado más valioso de la celda.** La unidad llega a W₃ con **31 olvidos por vida**. El olvido por fracaso es lo que le permite vivir en un mundo que cambia —M-c lo probó— y es **también** lo que le impide acumular, porque cada olvido la deja con sus últimos 64 pasos. **El mismo órgano que la hace sobrevivir al cambio le impide heredarse.** Y hay una salida ya construida y probada en otro sitio: que el olvido **conserve la máquina y suelte la traza**, que es exactamente lo que hace C5 al cambiar de mundo. Un decimal, un órgano modificado, ningún órgano nuevo.

---

## 5 · Los errores de la fase, y qué guarda queda

Nueve entradas nuevas (E-44 a E-52), **ocho de instrumento o de criterio y ninguna de ciencia**, y las dos más caras son de lectura, no de código:

| | qué pasó | guarda que queda |
|---|---|---|
| **E-44** | un mutante que no podía saltar (`trace[-0:]` es la traza entera) | todo mutante informa un **contador de actividad** y la puerta lo compara contra la referencia; si coinciden, **NULO POR INACTIVIDAD** |
| **E-45** | «idéntico en todo» incluyendo registros acumulados heredados por construcción | la fila se parte en **MEDIDAS** (la puerta exige igualdad) y **REGISTROS** (se imprimen siempre, no deciden), declarados antes de comparar |
| **E-46** | el encargo pedía un canal de un bit **y** un cálculo que exige leer la hipótesis del otro; con el disparo literal la celda era vacía por construcción | el **ancho del canal es parámetro** y se corren dos valores; se informa la distribución de longitud de palabra; si la palabra es siempre la letra que ya se iba a tomar, **NULO POR CONSTRUCCIÓN** |
| **E-47** | dos unidades deterministas idénticas en la misma corriente **no cruzan ni un bit** | toda celda con más de un agente **declara de dónde sale la asimetría**; con 0 intervenciones, **NULO POR SIMETRÍA** |
| **E-48** | «doble corrida con hash» **dentro de un mismo proceso** no comprueba el determinismo | se ordena toda colección antes de imprimirla o hashearla, y la doble corrida va en **dos procesos**, comparados por `diff` |
| **E-49** | el hash del código leído **al terminar** no es el del código que corrió | el sha256 se calcula **al importar**, y no se edita un módulo mientras una campaña que lo usa está corriendo |
| **E-50** | **un nulo leído como negativo** porque el techo estaba en el tratamiento; y la ficha ya tenía la guarda que lo impedía, sin implementar | **precondición del banco**: medir qué le cuesta al control conseguir por su cuenta lo que el tratamiento le regala, y exigir que **exceda el primer punto de medición**; la puerta implementa **todos** los criterios de la ficha y **lista los que no evalúa**; y un nulo **no se interpreta, se descompone** (medida graduada junto a la binaria, supervivencia del tratamiento en el primer hito, y tamaño de muestra) |
| **E-51** | truncar un bloque shortlex deja un futuro que mide **una esquina** del mundo: 3 de 64 prefijos, y una máquina de 3 estados «identificaba» un mundo de 12 | ninguna submuestra de un espacio indexado por dígitos se toma **por prefijo**, ni del orden natural ni de una permutación; pasa `muestreo_verificado` antes de usarse. Y la salida mejor: **no muestrear** —evaluar es barato, vivir es lo caro— |
| **E-52** | **todos los `n_min` del programa se miden desde el estado 0**, y en la Fase 2 la unidad no empieza en el 0 | toda medida de dificultad lleva **desde dónde** se calcula, y la selección del banco usa la del **punto de entrada**; si un brazo identifica con menos estados que el mínimo verdadero desde donde predice, **NULO POR FUTURO CIEGO** |

**El patrón que se repite, y conviene decirlo entero:** de las nueve, **seis** son de la misma familia —una medida que no puede ver lo que dice medir— y las tres formas en que apareció fueron el **techo** (lo heredado ya era gratis), el **suelo** (todos fracasan igual) y el **futuro ciego** (el instrumento mira una esquina). La guarda que las cubre a las tres es la misma: **antes de correr, demostrar que la celda puede producir el efecto que busca.** Está implementada como precondición en `09` y en `11`.

---

## 6 · Estado de custodia

Árbol `experiment/unidad-minima-01`. **Nada commiteado**: espera el OK de Wis. Artefactos de la fase en `artifacts/`: C5 (`09`, dos corridas más el control A↔B), los seis mutantes, el maestro (`10`), la adquisición (`11`), el análisis pareado, y los contadores de guardas.

---

## 7 · La pregunta para Wis

Una sola, y es la que sale de §4.

**El olvido que salva impide heredarse. ¿Se cambia el órgano o se cambia el mundo?**

- **Cambiar el órgano:** que el olvido por fracaso **conserve la máquina y suelte la traza** —lo que C5 ya hace al cambiar de mundo— en vez de volver al núcleo de 64 pasos. Es un decimal sobre un órgano que existe, y lo que mediría es si entonces la herencia aparece.
- **Cambiar el mundo:** dejar el órgano como está y llevar la herencia al banco caro (6–8 estados, n_min ≥ 4), donde vivir de cero cuesta cientos de pasos y la herencia tiene dónde mostrarse sin tocar al ser.

**Mi recomendación: las dos, en ese orden, y primero el mundo.** Cambiar el mundo no toca al ser y contesta la pregunta que quedó abierta en §2 con el banco que la Fase 3 ya necesita para otra cosa; cambiar el órgano es una modificación del ser y conviene decidirla **viendo** si el mundo caro bastaba.
