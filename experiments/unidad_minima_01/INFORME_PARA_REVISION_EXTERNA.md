# Una unidad computacional mínima que construye distinciones causales: qué está medido y qué no

**Fecha:** 2026-10-27 · **Para:** revisión externa · **Objeto:** `experiment/unidad-minima-01`, commit `33c08a4` · **Cómputo:** 16,9 h de CPU sobre 184 849 mundos, que **no son todos válidos** y hay que desglosar: **175 105** de bancos y muestras utilizables (729 de n=3 completo + 65 536 de n=4 completo + 108 840 de la muestra de n=6), **9 581** de una muestra de n=8 **inválida** por el defecto de §8.1 que no se usan para nada, y 163 de la muestra limpia de n=8 en curso en el momento de escribir *(corregido el 27-oct tras revisión externa: la cifra agregada ocultaba que una parte era basura)*

**Qué se pide del lector.** Este informe no reclama un hallazgo. Separa tres cosas: (a) lo que está medido con sus controles, (b) lo que es **reencuentro** con resultados ya publicados y así se declara, y (c) la pregunta que decide el programa y que **no** está medida. Las preguntas concretas donde el juicio externo nos serviría están en §8.

---

## 0 · Encargo al revisor · léelo antes del informe

**Quién eres aquí.** Un revisor adversarial. No tienes acceso a nuestro repositorio, no puedes ejecutar nada, y no hace falta: el informe es autocontenido y todo lo que afirmamos está en él con su número. Las referencias a ficheros y *commits* son sólo procedencia.

**El modo de fallo que nos preocupa de ti.** Un revisor que es un modelo tiende a **confirmar la hipótesis que se le entrega**: devuelve matices elogiosos y llama «prometedor» a lo que debería atacar. Eso ya nos pasó: nuestra propia revisión de literatura no completó su verificación adversarial (6 de 75 votos), y por eso ninguna de sus afirmaciones pasa de «leída por un solo lector». Una respuesta que empiece diciendo que el trabajo es sólido **no nos sirve de nada** y nos cuesta dinero.

**Qué sí nos sirve.** En este orden:

1. **Una refutación con fuente.** Si alguno de los resultados de §2 a §5 es un teorema conocido, dilo con **DOI o URL** y la cita exacta. Preferimos citar a redescubrir, y ya nos ha pasado dos veces: la ley de reversibilidad era Angluin 1982 y la partición transitoria/recurrente estaba en Freund et al. 1993 como exclusión «sin pérdida de generalidad».
2. **Un error en el razonamiento.** Especialmente en la implicación de §4 (`M ⇒ T`) y en la inferencia de §5 («el límite es el itinerario, no la duración»), que es la que más peso carga y se apoya en sólo tres pruebas. *(27-oct: en la primera versión de este informe llamábamos «identidad» a lo de §4; el revisor lo refutó con un contraejemplo y con nuestra propia tabla. Queda como constancia de que el ataque funcionó.)*
3. **Un confundido que no hayamos visto.** Nuestra lista está en §8; lo que buscamos es el sexto que no está ahí.
4. **Una respuesta negativa clara.** «No existe esa demostración» es información valiosa si viene con lo que buscaste y donde buscaste.

**Reglas para tus citas.** Toda referencia con **DOI o URL**. Si respondes de memoria, **dilo explícitamente en esa línea**; no lo presentes como verificado. Nosotros verificamos las nuestras por Crossref y varias «de memoria» resultaron correctas — pero eso fue comprobación, no suerte, y aquí usamos la misma vara contigo. Una cita inventada nos cuesta más que un «no lo sé».

**Las tres afirmaciones que consideramos más frágiles**, por si te sirve para priorizar el ataque:

- **§4, la implicación `M ⇒ T`.** Medida al 100 % en todos los estratos de dos bancos completos. *(27-oct: aquí decíamos «⟺» y «nuestro resultado más fuerte». La recíproca es falsa y la refutaba nuestra propia tabla. Lo que sigue en pie es una implicación, y sigue siendo sospechosa de ser un teorema conocido que no hemos sabido enunciar.)*
- **§5, la invariancia.** «Más vida no compra cobertura» descansa en tres pruebas, en un rango de ×2,5 a ×5,1, y ya la enunciamos una vez de más (dijimos «la fija el mundo» cuando lo correcto era «mundo × itinerario»). Puede seguir siendo demasiado fuerte.
- **§3, la asimetría entre letras.** Que `B` reversible *empeore* la identificación a `n_min` = 2 no lo esperábamos y no tenemos explicación estructural. Puede ser un artefacto de usar una sola salida observable.

**Lo que no necesitamos.** Sugerencias de redes neuronales, de métodos estocásticos o de escalar con GPU: el programa es deterministico y de bajo cómputo por decisión, no por limitación. Y tampoco necesitamos aliento.

---

## 1 · El objeto

Una unidad determinista, sin azar y sin GPU, que interactúa con un mundo oculto. El mundo es una máquina de estados finitos: dos letras `A` y `B` que actúan como mapas arbitrarios sobre `n` estados. La unidad **sólo lee un bit por paso**: `o = [x′ ≠ x]`, «algo cambió». Ese bit no contiene la identidad del estado, así que la misma letra produce reacciones distintas según una historia que la unidad no observa.

La unidad vive **una sola vida continua**: una concatenación de todas las palabras de longitud 1..L en orden shortlex, **sin reset y sin maestro**. En cada paso predice la reacción **antes** de actuar, lee, y si lo leído refuta su hipótesis retrocede a su última decisión; abre un estado nuevo sólo cuando ninguna alternativa queda. Prohibido `random`: dos corridas producen un hash idéntico, y el único campo que difiere entre corridas es el reloj de pared.

Las tres capas se declaran en cada experimento: *programado* (el alfabeto, el criterio de retención), *disposición* (desempates, topes, el orden canónico) y *adquirido* (lo que la unidad construyó).

---

## 2 · Resultado 1 · Es una unidad causal mínima, por intervención y no por correlación

Nivel de evidencia: **COMPUTATIONALLY-REPRODUCED** (reproducido en dos intérpretes distintos, artefactos byte a byte idénticos).

Con dos estados ocultos y el bit de cambio como única observación:

1. **Construye una distinción que no está en su observación.** La máquina final tiene dos estados y su testigo de separación es la letra `A`.
2. **Predice lo que nunca vivió.** Acierto 1,0000 sobre 6 656 pasos de palabras de longitud 8 y 9, nunca vividas; y acierta corridas de `A` **más largas que cualquiera que haya vivido** (sonda A¹⁴B y A¹⁵B).
3. **Lesión:** colapsando los dos estados en uno y conservando la reacción mayoritaria por letra —quitando la distinción y nada más—, el acierto en el futuro cae de **1,0000 a 0,6666**.
4. **Control negativo:** en un mundo donde el bit oculto existe y se conmuta pero **ninguna reacción depende de él**, la unidad termina con **un** estado y **no inventa** la distinción.
5. **Control que debe acertar:** en un mundo donde la reacción revela el estado, un control reactivo de orden 1 acierta igual. El test discrimina.

**Uso instrumental de lo adquirido.** Dada una meta impuesta desde fuera —«que la próxima reacción a `B` sea 1»—, la unidad recorre las palabras de su propia máquina en orden shortlex y ejecuta la más corta que la cumple **desde cualquier estado**: `BA`, longitud 2, que es el mínimo real del mundo y que **ninguna letra sola realiza**. La versión lesionada declara la meta insatisfacible; el control reactivo elige `A`, que le funciona desde el estado en que de hecho está y **falla desde el otro** — acierta sin poder garantizarlo. La robustez se mide **ejecutando** la palabra en el mundo desde los dos estados ocultos, no preguntando al agente.

En el mundo del bit inerte las tres partes declaran la meta **insatisfacible** en vez de inventar una palabra.

---

## 3 · Resultado 2 · Qué decide si una sola vida no elegida basta: reversibilidad

Nivel: **COMPUTATIONALLY-REPRODUCED**, y **reencuentro declarado** con tres formalizaciones previas.

Banco enumerado canónicamente, sin muestreo aleatorio: **todos** los pares de mapas sobre 3 estados (729) y sobre 4 estados (65 536) — bancos **completos** —, más una submuestra determinista de 108 840 sobre 6 estados. La máquina mínima verdadera de cada mundo se calcula por refinamiento de particiones (Hopcroft 1971), restringida a la parte alcanzable, y la identidad se juzga **salvo isomorfismo** por forma canónica.

| n | mundos | con distinción (n_min ≥ 2) | identificados | clase inerte (n_min = 1) |
|---|---|---|---|---|
| 3 | 729 (completo) | 530 | 368 · 69,4 % | 199, **0 distinciones abiertas** |
| 4 | 65 536 (completo) | 51 222 | 32 040 · 62,6 % | 14 314, **0 distinciones abiertas** |
| 6 | 108 840 (muestra) | 86 361 | 48 052 · 55,6 % | 22 479, **0 distinciones abiertas** |

**La ley.** Clasificando cada mundo por si **cada letra es una permutación de la parte alcanzable** (es decir, reversible: no colapsa estados), la identificación a igual `n_min` es monótona:

| estructura | identificación |
|---|---|
| ninguna letra es permutación | 46 – 70 % |
| sólo `B` | 61 – 71 % |
| sólo `A` | 68 – 80 % |
| **las dos** | **100 %, cero excepciones en 2 037 mundos** |

De esos 2 037, **1 200 provienen de los bancos completos de n=3 y n=4**, que no tienen muestreo y por tanto no admiten defecto de muestra. Dicho en una frase: **lo que decide si una vida no elegida basta es si el mundo destruye información.**

**Es un reencuentro y así se presenta, con una cautela que el informe anterior se saltaba.** Angluin probó en 1982 que los lenguajes reversibles son identificables **sólo con ejemplos positivos** (*Inference of Reversible Languages*, JACM 29(3):741–765, `10.1145/322326.322334`). *(27-oct: decíamos «y una vida sin maestro es exactamente un flujo de positivos», como si la correspondencia estuviera establecida. **No lo está.** Angluin trabaja con un conjunto de cadenas de un lenguaje; nosotros con una única traza continua de pares (letra, bit) sin reset. La analogía es sugerente y la citamos como **antecedente**, no como prueba de que nuestro resultado se siga del suyo. Demostrar o refutar esa correspondencia es una de las cosas que pedimos en §8.)* La dicotomía permutación/reset es clásica (Ginzburg 1968, *Covering by Permutation and Reset Semiautomata*, `10.1016/b978-1-4832-0013-2.50010-2`). Nuestra aportación no es la ley: es medirla como **frontera de identificabilidad sobre la población entera** de mundos de este tamaño, con la unidad concreta y bajo lesión.

**Una asimetría que no esperábamos.** A `n_min` = 2, tener `B` reversible **empeora** la identificación en 18–22 puntos. En esos mundos `B` es la letra que escribe, y su irreversibilidad es justamente lo que hace observable la distinción. Las dos letras no son intercambiables, y no sabemos si eso es general o un artefacto de esta salida observable.

---

## 4 · Resultado 3 · La no identificabilidad desde esta vida se parte en dos, y una mitad implica estructura

Nivel: **COMPUTATIONALLY-REPRODUCED** sobre los dos bancos completos.

Cuando la unidad no identifica el mundo, el clasificador distingue dos casos por comparación de tamaños, sin búsqueda: **la vida admite una máquina menor** (el itinerario no fuerza la distinción) o **dos máquinas del mismo tamaño la explican**. *(27-oct: en todo el informe se dice «no identificable **desde esta vida**», nunca «no identificable» a secas. Las dos clases no son del procedimiento: «dos del mismo tamaño» se prueba **exhibiendo** las dos máquinas consistentes y «admite una menor» exhibiendo la menor, así que son propiedades de esa vida y no de este aprendiz — pero la palabra sin el complemento afirma más de lo que se midió.)*

Definimos un estado como **transitorio estructural** si por debajo de él hay **ida sin vuelta**: existe otro estado alcanzable desde él desde el que no se puede volver. Es una propiedad del mundo y no lleva umbral. Porcentaje de mundos con al menos un transitorio estructural:

| clase | n=3 (n_min 2 / 3) | n=4 (n_min 2 / 3 / 4) |
|---|---|---|
| **la vida admite una máquina menor** | — / **100 %** | **100 % / 100 % / 100 %** |
| dos máquinas del mismo tamaño | 95,8 / 58,1 % | 94,1 / 57,9 / 32,9 % |
| identificados | 20,2 / 6,3 % | 23,6 / 10,8 / 5,3 % |

**Lo que está medido es una implicación en un sentido, y sólo uno** *(corregido el 27-oct: este informe decía «identidad» y «exactamente», y era falso. Lo medido es `M ⇒ T`.)*

En los dos bancos completos y en todos sus estratos: si **la vida admite una máquina menor**, entonces el mundo **tiene** un transitorio estructural — 100 %, sin excepciones. Si el mundo no devuelve, la vida no fuerza la distinción.

**La recíproca es falsa, y la refuta esta misma tabla.** El 24 % de los mundos *identificados* con `n_min` = 2 tiene transitorio estructural, e «identificado» es precisamente «no admite una máquina menor». Subimos la implicación a bicondicional teniendo el contraejemplo impreso tres líneas más arriba.

Contraejemplo mínimo, comprobado: `A` manda todos los estados a 1, `B` es la identidad. La parte alcanzable desde 0 es {0, 1}; desde 0 se llega a 1 y de 1 no se vuelve, así que **hay transitorio estructural**. Pero la primera `A` cambia el estado y las siguientes no, de modo que `A` produce las dos reacciones y **la vida exige dos estados**: no admite una máquina menor. `T` sin `M`.

**La pregunta que queda, y es mejor que la que creíamos tener:** `M ⇒ T` dice que el transitorio es *necesario* para que la vida se quede corta. Lo que no sabemos es **bajo qué itinerario y qué longitud** el transitorio llega a ser *suficiente* — y precisamente lo que medimos en §5 es que alargar el mismo itinerario no lo convierte en suficiente. Formulada así, la pregunta es la de la Fase 2 y no una identidad que no teníamos.

La literatura sin reset **excluye** los transitorios en vez de recuperarlos: Freund et al. (STOC 1993) suponen el objetivo fuertemente conexo «sin pérdida de generalidad» precisamente porque el paseo cae en una componente de la que no escapa. *(Nivel para nosotros: LITERATURE-CLAIM; ver §7.)*

---

## 5 · Resultado 4 · Más vida no compra cobertura; el límite es el itinerario

Nivel: **COMPUTATIONALLY-REPRODUCED**, con el rango medido declarado.

La fracción de mundos no determinados crece con el tamaño del mundo (30,6 % → 37,4 % → 44,4 %) y **no se mueve al alargar la vida**, en tres pruebas:

| prueba | vida | resultado |
|---|---|---|
| n=3, una letra más | 258 → 642 pasos | **0 de 162** se resuelven |
| n=4, una letra más | 642 → 1 538 pasos | **6 de 19 182** (0,03 %) |
| n=6, la vida de n=8 | 3 586 → 18 434 pasos | **ningún cambio**, en los cinco estratos de `n_min` |

La invariancia está medida en un rango de ×2,5 a ×5,1 y **no se extrapola fuera de él**.

**Y la escala no degrada.** Estratificando por `n_min` —la única comparación que no mezcla dificultad con estructura— la identificación es **plana** en n: 76,7 / 76,3 / 77,1 % en `n_min`=2 y 63,8 / 62,7 / 65,3 % en `n_min`=3 para n=3/4/6. La caída de la tabla de §3 es **composición**: los mundos grandes tienen `n_min` grande.

**El caso que lo define operativamente.** Hay 24 mundos de n=4 donde la máquina aprendida difiere conductualmente de la verdadera. Son un solo fenómeno: los 24 fallan **exactamente 6 de 896** pasos del futuro, todos sobre la letra `B`, y la diferencia se reduce a **dónde vive una única transición**. Con una letra más de vida se identifican **6 de los 24** — y son exactamente los mismos seis índices que resuelve la prueba de cobertura sobre la clase entera de 19 182. En los 18 restantes, la palabra que separa las dos máquinas (`AABAABB`) **ya está en la vida**: se recorre nueve veces, desde tres estados distintos, y siguen sin identificarse.

De ahí la definición operativa de la clase recurrente: **una palabra separadora presente en la vida no es experiencia si no se ejecuta desde el estado que discrimina.** En una vida sin reset no se elige desde dónde se la recorre.

---

## 6 · El coste: lo que la teoría ya predecía, medido

El mecanismo exige la **máquina mínima consistente** con lo vivido. Trabajo real por paso de vida:

| n | p50 | p90 | p99 | máximo |
|---|---|---|---|---|
| 3 | 1,15 | 2,22 | 5,5 | 9,0 |
| 4 | 1,17 | 5,51 | 25,4 | **185,8** |
| 6 | 1,86 | 88,96 | 1 485 | **132 573** |

La mediana se queda en una pasada de la vida; el máximo se multiplica por **14 730** entre n=3 y n=6. Un criterio de coste declarado antes de medir (máximo ≤ 100× la vida) **falla**, y la fase lo deja en FAIL sin suavizarlo.

Esto **no es un defecto de implementación**: hallar la máquina mínima consistente es NP-difícil (Gold 1978, *Information and Control* 37(3):302–320, `10.1016/s0019-9958(78)90562-4`; Angluin 1978, ibíd. 39(3):337–350, `10.1016/s0019-9958(78)90683-6`) y **no aproximable dentro de ningún polinomio** (Pitt & Warmuth 1993, *JACM* 40(1):95–142, `10.1145/138027.138042`). Es el precio de exigir el mínimo exacto sin maestro. *(27-oct, cedido en revisión: la dureza del problema **no exime a nuestra implementación**. Nuestro retroceso exhaustivo es con casi total seguridad peor que un solucionador SAT exacto sobre la mayoría de instancias, así que la cola es peor caso **del problema y de nuestra búsqueda a la vez**, y con estos datos no podemos repartir los dos factores. El FAIL se mantiene; la atribución se parte en dos y queda abierta.)* La reparación prevista es cambiar a fusión de estados polinómica (RPNI, Oncina & García 1992, `10.1142/9789812797902_0004`; EDSM, Lang, Pearlmutter & Price 1998, `10.1007/bfb0054059`; y el antecedente más cercano a nuestro objeto, MooreMI de Giantamidis & Tripakis, arXiv 1605.07805), declarando por adelantado cuánta identificación se acepta perder por cuánto acotamiento de cola.

---

## 7 · Lo que NO está mostrado, y es la pregunta que decide el programa

**¿Una distinción adquirida abarata la adquisición de la siguiente?**

Eso no está medido. Nada de lo anterior lo prueba. Y es lo que separa **aprendizaje** de **desarrollo**: una unidad que acumula distinciones sin que ninguna abarate la siguiente es un buen identificador de autómatas, no un sistema que se desarrolla.

*(27-oct, corregido en revisión: aquí decíamos «no se ha demostrado en ningún sistema» y «la línea fue abandonada en 2008». Las dos frases son más anchas que su fuente, y es nuestro error registrado E-12 en su forma exacta: decir «no existe» donde sólo cabe «no hemos encontrado».)*

**No hemos encontrado** una demostración de que reutilizar lo adquirido abarate la adquisición siguiente, en un sistema del desarrollo. Guerin (2008) lo registra como criterio de «emergencia continuada» sin evidencia **entre los trabajos que él revisa**, que es un alcance menor que «ningún sistema». Y la línea a la que pertenece esta unidad (Drescher 1991, Shen 1989/94, Chrisman, McCallum, Ring, Holmes & Isbell 2006, Perotto 2007, Georgeon 2012) **tiene continuaciones posteriores** —Lagriffoul 2022 entre ellas—, así que «abandonada» era falso.

**Y existe transferencia con teoría, que no teníamos citada.** Reutilizar una representación reduce la muestra necesaria para la tarea siguiente, bajo condiciones (Tripuraneni, Jordan & Jin 2020; Agarwal et al. 2023). No es nuestro caso —una sola vida, sin reset, un bit de observación, y lo que nos importa es el **coste marginal de la distinción siguiente**, no la muestra de una tarea nueva—, pero entra al gate de la Fase 2 como antecedente obligatorio, y obliga a formular nuestra pregunta de modo que no se confunda con la suya.

**Lo que la Fase 1 sí aporta a esa pregunta** es haber aislado el único límite real: no es la capacidad de la unidad ni la duración de su vida, sino que **no elige qué vivir**. La literatura **sugiere** que elegir acciones no es una mejora de constante sino un salto de clase de complejidad (Kearns & Valiant 1994) y trae construcciones deterministas que lo logran (Bender et al. 1998: un agente con **una marca** mapea cualquier grafo fuertemente conexo en tiempo polinómico, sin reset, sin maestro y sin azar, **dada una cota del número de estados**). *(27-oct, matizado en revisión: la separación de clase de Kearns–Valiant es para **su** protocolo de consultas, no para el nuestro, y Bender exige además fuerte conexión y la cota de n, dos supuestos que nuestros mundos no cumplen en general. Se citan como **antecedentes que hacen la apuesta razonable**, no como pruebas de que nuestro caso se resuelva. Ambos: LITERATURE-CLAIM para nosotros.)*

**La decisión de diseño que bifurcaba el experimento siguiente ya está tomada** *(27-oct, siguiendo la recomendación del revisor)*: la Fase 2 principal corre **sin marca**, con la interfaz actual, porque una marca cambia las capacidades del agente y mezclaría dos preguntas; y porque la construcción de Bender exige supuestos que nuestros mundos no cumplen. La marca queda como **fase aparte y posterior**, no como variante.

---

## 8 · Limitaciones, amenazas a la validez, y lo que preguntaríamos

**Limitaciones declaradas, sin excusa:**

1. **La muestra de n=8 de la Fase 1 es inválida.** El paso de la submuestra (`k = 10¹⁰`) comparte factores con la base del espacio (`8¹⁶ = 2⁴⁸`), de modo que cuatro de las dieciséis entradas de tabla quedaron restringidas y los mundos colapsaban hacia un estado. Eso fabricó dos anomalías que se informaron como hallazgos antes de detectarlo. Los bancos de n=3 y n=4 son **completos** y no admiten este defecto; n=6 tiene **una** entrada de doce restringida, efecto menor y acotado. n=8 se está rehaciendo con un paso coprimo verificado, y la fase se cierra con **tres** puntos de escala, no cuatro.
2. **Dos defectos de instrumento, corregidos y declarados.** Un tope de estados declarado que nunca se aplicó —lo que produjo una conclusión falsa que se afirmó y se retiró— y un contador de coste que medía la distancia retrocedida en vez del trabajo. Las funciones de medida se probaron byte a byte idénticas tras las correcciones; las filas medidas antes siguen válidas.
3. **Un solo lector por fuente.** Nuestra revisión de literatura no completó su verificación adversarial: ninguna afirmación tomada de ella pasa de SOURCE-VERIFIED por un lector. Las fuentes clásicas citadas aquí están verificadas **a nivel de metadatos** (Crossref) y, donde fue posible, de resumen; los textos completos de Elsevier, ACM y Springer no son accesibles desde el entorno de trabajo.
4. **Una única salida observable.** Todo depende del bit de cambio `[x′ ≠ x]`. No sabemos cuánto de la ley de reversibilidad y de la asimetría entre letras es propiedad del mundo y cuánto de esta proyección.
5. **Tamaños pequeños.** n ≤ 8 estados, dos letras. No afirmamos nada sobre alfabetos mayores ni sobre mundos estocásticos.

**Lo que preguntaríamos a un lector externo:**

- La implicación de §4 —«la vida admite una máquina menor» ⇒ «el mundo tiene un transitorio estructural»— ¿es un teorema conocido? Nos parece demostrable y no hemos encontrado el enunciado. Y la pregunta que de verdad nos interesa: **¿bajo qué condiciones sobre el itinerario** el transitorio pasa a ser suficiente y no sólo necesario? Eso es lo que decide si la Fase 2 tiene fundamento.
- ¿Hay una razón estructural para la **asimetría entre letras** a `n_min` = 2, o es un artefacto de la salida observable?
- Para la pregunta de §7, ¿conocen alguna demostración —aunque sea parcial— de que una distinción adquirida abarate la siguiente, en cualquier sistema? Nuestra búsqueda dice que no existe, y preferiríamos estar equivocados.
- La decisión de la marca (§7): ¿cuál de las dos versiones consideran la pregunta científicamente más informativa?

---

## 9 · Reproducibilidad

Sin `random` en ningún punto; dos corridas producen un hash idéntico y el único campo que difiere es el reloj de pared. Cada artefacto lleva el sha256 del código que lo produjo, la versión exacta del intérprete (Python 3.14.4) y todos los parámetros. Los bancos se enumeran canónicamente, nunca por muestreo aleatorio. Las corridas largas escriben fila a fila con `fsync` y se reanudan tras un corte: la reanudación está **probada** matando el proceso con `SIGKILL` a mitad de escritura y comprobando que ninguna fila se pierde, ninguna se repite y el conjunto final coincide campo a campo con una corrida sin interrupción.

Todo criterio de aceptación se escribió **antes** de medir, con su falsador; todo criterio se probó con mutantes —incluido un oráculo que debe pasar— antes de la corrida real; y las predicciones que fallaron se dejan escritas como se escribieron. Existe un registro versionado de 32 errores con su guarda, 24 de ellas mecánicas, que incluye los dos defectos de instrumento y el de muestreo descritos en §8.
