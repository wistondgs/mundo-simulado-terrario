# PRIOR-ART GATE · Fase 2 · heredar y elegir

**Fecha:** 2026-10-27 · **Veredicto:** `MULTIPLE_NEAR_SOLUTIONS` para los órganos por separado; **`OPEN_UNDER_CURRENT_SEARCH`** para la pregunta compuesta · **Fuentes que responden desde aquí:** Crossref y arXiv (ambas respondieron hoy). Textos completos de Elsevier, ACM y Springer no accesibles: esas quedan verificadas a metadatos.

**La pregunta** *(corregida el 27-oct: este gate se escribió contra una versión anterior de la receta, en la que el criterio era económico. No lo es.)* **¿Lo vivido se acumula?** Es decir: tras una vida, ¿puede la unidad, en la siguiente, **algo que una unidad fresca no puede con la misma vida**? Se mide como **alcance, exactitud, repertorio e instruibilidad**, nunca como ahorro. El cómputo y el tiempo se **registran siempre y no deciden nunca**: que la heredera gaste más que la fresca no cuenta en contra. La Fase 1 dejó un identificador correcto que **no elige qué vivir** y **no hereda** nada de una vida a la siguiente. Este gate dice qué de lo que vamos a construir ya existe.

---

## 1 · Qué dice la literatura ≠ qué tenemos comprobado

### Heredar la máquina

| Qué dice la literatura | Nivel | Qué tenemos |
|---|---|---|
| **Reutilizar un autómata aprendido y repararlo donde falla, en vez de reaprenderlo**, es el núcleo del *adaptive model checking*: Groce, Peled & Yannakakis, LNCS (TACAS 2002), `10.1007/3-540-46002-0_25`; el verificador `AMC` (CAV 2002), `10.1007/3-540-45657-0_44`; versión de revista en *Logic Journal of the IGPL* (2006), `10.1093/jigpal/jzl007`. | SOURCE-VERIFIED a metadatos (Springer/OUP, texto no accesible) | Nada. **Es la pieza que vamos a adaptar**, y así se declara: no la inventamos. |
| Misma línea con la reutilización como objetivo: Damasceno, Mousavi & da Silva Simão, *Learning to Reuse*, `10.1007/978-3-030-34968-4_8` (2019); Ferreira, van Heerdt & Silva, *Tree-Based Adaptive Model Learning*, arXiv 2209.00122 (2022), con implementación en LearnLib. | SOURCE-VERIFIED (resumen de 2209.00122 leído) | Nada corrido. |
| **Transferencia con cotas**: reutilizar una representación reduce la **muestra** necesaria para la tarea siguiente bajo condiciones de diversidad de tareas — Tripuraneni, Jordan & Jin, arXiv **2006.11650** (2020); y en control, Agarwal, Song, Sun, Wang & Wang, *Provable Benefits of Representational Transfer in Reinforcement Learning*, arXiv **2205.14571** (2022, publicado 2023). | SOURCE-VERIFIED (metadatos y títulos; los teoremas no leídos) | Nada. **Traído por la revisión externa.** Mide **ahorro de muestra**, que es precisamente lo que nosotros **no** medimos: ver §3. |

### Elegir qué vivir

| Qué dice la literatura | Nivel | Qué tenemos |
|---|---|---|
| Elegir las entradas **cambia la clase de complejidad** del problema de identificación, no la constante (Kearns & Valiant 1994). | LITERATURE-CLAIM | Nada. Y la separación es **para su protocolo de consultas**, no para el nuestro: se cita como antecedente que hace razonable la apuesta, no como prueba. |
| La historia suficiente para separar estados es «exponencialmente improbable» con acciones al azar (Holmes & Isbell, ICML 2006); un agente determinista **con una marca** mapea cualquier grafo fuertemente conexo en tiempo polinómico sin reset ni maestro, dada una cota de n (Bender et al. 1998). | LITERATURE-CLAIM | Nada. **La marca queda fuera de esta fase** por decisión adjudicada: cambia la interfaz del agente y mezclaría dos preguntas. |
| Sistemas que generan sus propios experimentos cuando la observación no discrimina: LIVE (Shen 1989/94), «acción de prueba» de CALM (Perotto 2007). | LITERATURE-CLAIM (sin acceso al libro ni cifras) | Nada. Antecedente conceptual del órgano «elegir». |

### Heredar las palabras

| Qué dice la literatura | Nivel | Qué tenemos |
|---|---|---|
| **Tablas de macros**: Korf, *Macro-operators: A weak method for learning*, *Artificial Intelligence* 26(1):35–77, 1985, `10.1016/0004-3702(85)90012-8`; marco formal y aprendizaje en tiempo polinómico **dado el orden de rasgos**: Tadepalli & Natarajan, *JAIR* 1996, `10.1613/jair.154`. | SOURCE-VERIFIED a metadatos | Nada. La Fase 0 ya extrajo las palabras de efecto constante y las permutaciones de la máquina aprendida: PROJECT-VERIFIED que existen, no que sirvan. |
| **Una biblioteca sin podar deja de servir**: Cropper, *Forgetting to Learn Logic Programs*, AAAI 2020, `10.1609/aaai.v34i04.5776`. | SOURCE-VERIFIED a metadatos | Nada. **Es la razón de que la poda sea parte del diseño y no un extra** — y se poda **por no servir, no por costar**, que con el criterio corregido no es lo mismo. |

### El mundo siguiente, y qué permite heredar

| Qué dice la literatura | Nivel | Qué tenemos |
|---|---|---|
| Todo autómata se descompone en **cascada** de componentes de permutación y de reset (Krohn–Rhodes); y en una cascada la novedad **irreducible** exige un componente nuevo, no se obtiene recombinando lo viejo: DeDeo, *Effective theories for circuits and automata*, *Chaos* 21(3):037106, 2011, `10.1063/1.3640747`. | SOURCE-VERIFIED a metadatos | **Nuestra ley de reversibilidad de la Fase 1 es la misma dicotomía vista desde la identificabilidad** (y también es Ginzburg 1968, `10.1016/b978-1-4832-0013-2.50010-2`). Es la justificación de generar W₂ como cascada y de que el control sea la dependencia invertida. |

### Y la pregunta compuesta

| Qué dice la literatura | Nivel | Qué tenemos |
|---|---|---|
| **No hemos encontrado** una demostración de que lo adquirido **amplíe lo que el sistema alcanza** en la vida siguiente, en un sistema del desarrollo. Guerin (2008) lo registra como criterio de «emergencia continuada» **sin evidencia entre los trabajos que él revisa** — alcance menor que «ningún sistema». | LITERATURE-CLAIM | Nada. **Es la pregunta de esta fase.** |
| Y la línea **no está abandonada**: Lagriffoul, *A Schema-Based Robot Controller Complying With the Constraints of Biological Systems*, *Frontiers in Neurorobotics* 16:836767, 2022, `10.3389/fnbot.2022.836767` — basada en esquemas, que es la línea de Drescher. En la misma búsqueda aparece *SB-CoRLA, a schema-based constructivist robot learning architecture*, sin verificar en detalle. | SOURCE-VERIFIED a metadatos (acceso abierto; texto no leído) | Nada. **Corrige una afirmación nuestra**: dijimos «abandonada en 2008» y era falso. |

---

## 2 · Lo que no hemos encontrado, dicho como se debe

- Una unidad que **elija** sus acciones para desambiguar **sin maestro, sin reset y sin azar a la vez**, con garantía. Todo lo leído tiene al menos uno de los tres: oráculo (`hW`, L#), reset (OOPS, RPNI por conjuntos) o paseo aleatorio (Freund, Pierce–Kuipers).
- Una medida de **ampliación de alcance dentro de una vida continua**: cuántos mundos llega a identificar una unidad que ya vivió, frente a una fresca con el mismo presupuesto. Lo que existe mide **ahorro de muestra** para una tarea nueva dada una representación. No es lo mismo, y confundirlo nos atribuiría un teorema ajeno.
- Una medida de **repertorio** —qué palabras sabe y usa al final de la segunda vida frente al final de la primera: crece, se mantiene o se pierde— ni de **instruibilidad**, entendida como cumplir un objetivo externo *usando lo heredado*. No hemos encontrado ninguna de las dos en la literatura leída.
- La combinación de los tres órganos en un mismo sistema sin reset. Cada uno existe por separado.

No decimos que no exista. Decimos que no lo hemos encontrado, con las búsquedas de hoy (Crossref y arXiv) y las del informe de literatura (46 fuentes, un solo lector por fuente, verificación adversarial incompleta).

---

## 3 · Qué se integra, qué se escribe, y la frontera con la transferencia

**Se integra como esquema, citado:** la reparación local de la conjetura (Groce–Peled–Yannakakis), las palabras heredadas como macroacciones (Korf; Tadepalli–Natarajan), la poda obligatoria (Cropper), y la generación de W₂ como cascada (Krohn–Rhodes / DeDeo).

**No se instala ninguna biblioteca.** LearnLib y AALpy suponen maestro y reset, que es exactamente lo que la unidad no tiene; y sus desempates internos no son nuestro orden canónico, lo que rompería el determinismo declarado.

**Se escribe:** el acoplamiento de los tres órganos a una vida continua sin reset —que es donde no hemos encontrado antecedente—, la poda sintáctica, el generador de la familia, y las medidas separadas. El residuo propio es el acoplamiento y la medida, no los mecanismos.

**La frontera con la transferencia, declarada para que nadie la confunda** *(reescrita el 27-oct con el criterio corregido)*. Tripuraneni y Agarwal responden: *dada una representación aprendida en varias tareas, ¿cuántas muestras **ahorra** la tarea siguiente?* Nosotros preguntamos: *dentro de una sola vida continua, sin reset y con un bit de observación, ¿la unidad que ya vivió **alcanza** mundos, conserva palabras y cumple instrucciones que una fresca no, con el mismo presupuesto?* Difieren en cuatro cosas que no son de grado: una vida frente a un conjunto de tareas; sin reset frente a episodios; **alcance, repertorio e instruibilidad frente a complejidad de muestra**; y sobre todo, que para ellos el eje es el ahorro y para nosotros el ahorro **no es el eje** — lo registramos y no decide. Una unidad que se desarrolle gastando **más** que una fresca sigue siendo un desarrollo. Si alguien demuestra que nuestro caso se reduce al suyo, la Fase 2 sobra; eso está entre las preguntas de la revisión externa.
