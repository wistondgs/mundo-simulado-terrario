# Literatura pendiente · lo que hay que leer entero para que ninguna orientación afirme más de lo que su fuente dice

**Fecha:** 2026-10-28 · **Para:** Wis (baja los PDF) y Opus (los lee y actualiza el nivel) · **De:** Fable · **Motivo:** E-42. Desde esta máquina no se leen ScienceDirect, ACM, Springer, OUP ni AMS; sí arXiv, PDF de autor, PLOS, bioRxiv, AAAI, JAIR, PMLR.

**Corrección del 28-oct (E-43).** Escribí esta lista sin consultar el corpus de Wis en `/home/wis/Documentos/teoria de la inteligencia/` (329 ficheros, 103 PDF, con manifiestos, SHA-256 y procedencia; corpus maestro TI-, ADOA v0.1.1 de 65 documentos, HEA v0.1 con 21 afirmaciones validadas, SCI/WORLD-REF de Terrario, adquisiciones v0.4/v0.5). Buena parte de lo que las orientaciones del maestro, la escalera y la viabilidad necesitan **ya está ahí**, y lo que falta de verdad es más corto de lo que decía. La sección 0 lo ordena; las secciones A–D quedan como estaban, con lo que sigue faltando marcado.

---

## 0 · Lo que YA está en el corpus de Wis y hay que leer antes de pedir nada

Regla: en los gates se cita con el **identificador del corpus** (TI-, ADOA-, HEA-, X, HD-, H-, WORLD-REF-, SCI-) y el nivel; una fuente del corpus se lee de su PDF o de su `extracted_text`, no de memoria.

| para qué fase | fuente | id en el corpus | qué da |
|---|---|---|---|
| **maestro / transmisión** | Derex, Bonnefon, Boyd, McElreath & Mesoudi 2025, *Social learning preserves both useful and useless theories by canalizing learners' exploration* | `X13` (documents_v0.3) | **es nuestra medida del maestro con signo**: la instrucción canaliza la exploración, para bien y para mal; es lo que vimos con elegir (ayuda con esqueleto correcto, estorba con el falso) |
| | Derex et al. 2019, *Causal understanding is not necessary for the improvement of culturally evolving technology* | `X12` | las cadenas de transmisión mejoran sin que ningún individuo entienda: el **linaje acumula lo que el individuo no** |
| | Mesoudi & Thornton 2018, *What is cumulative cultural evolution?* | `X11` | los **criterios** de acumulación cultural: lo que «el cúmulo que produce más información» tiene que cumplir para llamarse así |
| | Galesic et al. 2023, *Beyond collective intelligence: collective adaptation* | `X14` | adaptación colectiva vs. inteligencia colectiva |
| | Laland, Odling-Smee & Myles 2010 | `X09` | cultura y herencia |
| | **Harlow 1949**, *The formation of learning sets* (comentario Citation Classic) | `ADOA-080` = `HEA-020` = `ARC-002S` | **el experimento original de «lo vivido amplía lo siguiente»** entre problemas: la curva de aprendizaje se vuelve un paso con la experiencia; es la Fase 2 en monos, 1949 |
| | Carey 2009 *The Origin of Concepts* y Précis 2011 | `TI-0037`, `X17` | **bootstrapping quineano**: cómo nacen conceptos nuevos a partir de símbolos marcadores que se llenan de contenido: la base de «enseñar a leer es dar nombres» |
| | BabyAI (Chevalier-Boisvert et al. 2018) | `WORLD-REF-005B` | maestro por demostración y currículo en lenguaje con fundamento; mide **eficiencia de muestra con y sin maestro** |
| **escalera (T3)** | PAIRED (Dennis et al. 2020), *Emergent complexity and zero-shot transfer via unsupervised environment design* | `WORLD-REF-017` = `ADOA-045` | **la zona de desarrollo próximo hecha operativa**: el siguiente entorno es el de máximo arrepentimiento entre el alumno y un antagonista; en nuestro banco el arrepentimiento es la diferencia pareada fresca/heredera por mundo |
| | ACCEL (Parker-Holder et al. 2022) | `WORLD-REF-019` = `ADOA-048` | currículo por edición mínima de niveles ordenados por arrepentimiento: **un bit más, nunca dos**, ya formulado |
| | PLR (Jiang et al. 2021) | `WORLD-REF-018` = `ADOA-047` | repetir los mundos que más enseñan |
| | POET / Enhanced POET (Wang et al. 2019/2020) | `TI-0092` = `ADOA-066`, `ADOA-044` | coevolución con **criterio mínimo** (ni trivial ni imposible): el peldaño |
| | XLand (2021) | `WORLD-REF-022` = `ADOA-046` | aprendizaje abierto a escala; control de lo que no queremos copiar (estocástico, GPU) |
| | IMGEP con currículo automático (Forestier, Oudeyer) · autotélicos · CURIOUS · motivación intrínseca 2007 y tipología · competencia | `ADOA-073`, `-074`, `-075`, `-035` (= `X06`), `-036`, `-039`, `-037`, `-038` | **el alumno se pone su propia escalera**: progreso de aprendizaje como señal; todo estocástico, se toma el principio y no el mecanismo |
| | Weng et al. 2001 *Autonomous Mental Development* · Lungarella 2003 · Asada 2009 | `ADOA-032`, `-033`, `-034` | el programa de robótica del desarrollo: lo que ya se intentó y por qué se estancó |
| **viabilidad (beneficio / peligro / riesgo)** | **Ashby 1960 *Design for a Brain*** (2.ª ed., 304 pp.) | `ADOA-001` = `ARC-001` = `HEA-014` | **ultraestabilidad**: variables esenciales + funciones escalón: el mecanismo determinista mínimo de «esto me daña, cambio»; es la variable interna que la fase siguiente necesita, y es de 1952 |
| | Ashby 1956 *Introduction to Cybernetics* · Conant & Ashby 1970 | `TI-0049` = `ADOA-002`, `ADOA-004` = `HEA-015` | variedad requerida; el buen regulador es modelo (ya citado por nosotros vía Virgo 2025) |
| | Maturana *Biology of Cognition* · Di Paolo 2005 *Autopoiesis, adaptivity, teleology, agency* · Beer *Autopoiesis and cognition in the Game of Life* · Barandiaran, Di Paolo & Rohde 2009 *Defining agency* | `HEA-016`, `HEA-007` = `ADOA-008`, `ADOA-009`, `ADOA-070` | la capa que el informe de literatura marcó como hueco (van Duijn): **ya está en casa** |
| | Di Paolo 2000, Iizuka & Di Paolo 2008, Manicka & Di Paolo 2009 | `H-011`, `H-012`, `H-013` | **ultraestabilidad ashbiana implementada en robots**: la referencia directa para la variable interna de la unidad |
| | HRRL Keramati & Gutkin · CTCS-HRRL · meta-RL homeostático · acoplamiento empático · impulsos en competencia | `ADOA-012`, `HEA-001`…`HEA-005` | homeostasis como fuente de valor sin recompensa externa: lo que **no** hay que copiar (estocástico) y el principio que sí (la desviación de la variable esencial es la señal) |
| | Klyubin et al. *Empowerment* | `ADOA-071` | medida de control del agente sobre su futuro: candidata a «beneficio» sin recompensa |
| | *Mortal computation* (Ororbia & Friston) · *Agent cybernetics* 2026 · Holling 1973 resiliencia | `HEA-011`, `HEA-010`, `V-001` | frontera 2024–2026 y el concepto de resiliencia para la fase de viabilidad |
| | corpus de homeostasis fisiológica (Bernard, Sterling, Billman, Fitzgerald & Bean) | `H-001`…`H-009` | el rival obligatorio: **regulación sin punto fijo** (Fitzgerald & Bean 2018) |
| **la célula como unidad mínima que recuerda** | Wolf et al. 2008, *Memory in microbes: quantifying history-dependent behavior* | `HD-005` | **una medida informacional de cuánto revela la respuesta sobre la historia**: es la medida de «lo vivido se acumula» en biología |
| | Mitchell et al. 2009, *Adaptive prediction of environmental changes by microorganisms* | `HD-009` | *E. coli* anticipa la **secuencia** de entornos (lactosa → maltosa): nuestro W₁ → W₂ ya ocurre en bacterias, y se pierde si la secuencia deja de darse |
| | Lambert & Kussell 2014, *Memory and fitness optimization in fluctuating environments* | `HD-006` | **la longitud óptima de memoria depende del entorno**: la justificación de que nuestra ventana (512) no sea una constante sino una variable a medir |
| | Gershman et al. 2021 · Biswas, Levin et al. 2021 · Netea 2016/2020 · Crisp 2016 | `HD-004`, `HD-015`, `HD-011/012`, `HD-013` | aprendizaje unicelular, memoria en redes génicas, inmunidad entrenada, memoria vegetal: la biología como inspiración, con sus controles declarados |
| **formal (cascadas, congruencias)** | **Hartmanis 1962, *Loop-free structure of sequential machines*** (bajado por Wis el 27-sep) | `1-s2.0-S0019995862901936` (raíz) | **la matemática exacta de nuestro generador de W₂**: particiones con propiedad de sustitución = congruencias; realización en cascada; **flujo de información entre componentes**. Es también la base formal de «mitosis por congruencia» |
| | Xie, Hunt & Stearns 2025, complejidad de lenguajes multi-patrón | `1-s2.0-S0304397525000015` (raíz) | por leer: no sé aún qué quería Wis de ella |
| **olvido y conservación** | Kirkpatrick 2017 EWC · Parisi 2019 · De Lange · Khetarpal · Kudithipudi 2022 · Abel 2023 *A definition of continual RL* · Progressive nets | `TI-0085` = `ADOA-061`, `ADOA-060`, `-056`, `-058`, `-059`, `-069`, `TI-0086` = `ADOA-062` | el problema del olvido catastrófico en redes: lo que nuestra «certificación por transición» resuelve en chico y determinista; **Abel 2023** da una definición formal de aprendizaje continuo |
| **metacognición / elegir** | Flavell 1979 · Nelson & Narens · Fleming *How to measure metacognition* · Russell & Wefald *Principles of metareasoning* · Griffiths 2019 *Doing more with less* · Lieder *Learning to select computations* | `ADOA-021`…`-031`, `-072`, `-077`, `-078` | **«saber que no sabe»** es nuestro empate entre hipótesis; «elegir qué vivir» es metarrazonamiento; la literatura de medir metacognición da los controles |
| **desarrollo** | Smith & Thelen 2003 · Karmiloff-Smith 2010–2017 · Spelke 1990 y el corpus SCI-D2 · Sternberg 2019 | `X16`, `DEV-014…018`, `X01` = `SCI-D2-001…006`, `C4-003A` | desarrollo como sistema dinámico; neuroconstructivismo; conocimiento nuclear; inteligencia adaptativa |
| **medida de inteligencia** | Legg & Hutter · Chollet 2019 · Hernández-Orallo · Lake 2017 · LeCun 2022 | `TI-0071…0077`, `TI-0126/0127` | Chollet: **la competencia final no dice cuánta inteligencia costó adquirirla**: es exactamente la norma de Wis «desarrollo, no economía» vista desde la medición |

**Lo que de verdad NO está en el corpus** y sigue en las secciones A–D: toda la teoría de autómatas aprendibles (Angluin 1978/1982/1987/1990, Gold 1978, Pitt–Warmuth, Rivest–Schapire, Bender–Slonim, Kearns–Valiant, Goldman–Kearns), la reparación de modelos (Groce, Damasceno), macros (Korf), aprendizaje iterado (Kirby), Guerin, Prince, Drescher, Shen, Perotto, Cropper, Hinton–Nowlan, Whitehead–Ballard. El corpus de Wis es de inteligencia, desarrollo, viabilidad y cultura; **la pata de autómatas es la que falta**, y es la que sostiene la Fase 1 y la mitad de la Fase 2.

---

**Dónde dejarlos:** `experiments/unidad_minima_01/literatura/` con el nombre `Autor_Año_titulo-corto.pdf`. Opus los lee con `pdftotext` y pone en el gate correspondiente la fecha de lectura y el nivel (`SOURCE-VERIFIED`). Una fuente que no esté aquí no se cita en una orientación con más fuerza que `LITERATURE-CLAIM`.

---

## A · Las que sostienen las orientaciones de la Fase 2 y del maestro, y nadie ha leído enteras

| # | fuente | dónde | por qué la necesitamos | qué hay que verificar al leerla |
|---|---|---|---|---|
| A1 | **Angluin, D.** (1987). *Learning regular sets from queries and counterexamples.* Information and Computation 75(2):87–106. doi 10.1016/0890-5401(87)90052-6 | ScienceDirect (bloqueado) | base de T1: qué pregunta exactamente el maestro y qué garantía da | que L\* exige **pertenencia y equivalencia con reset**; qué pasa sin reset; la cota polinómica exacta |
| A2 | **Angluin, D.** (1990). *Negative results for equivalence queries.* Machine Learning 5:121–150. doi 10.1007/BF00115603 | Springer (bloqueado) | dice si un maestro de **sólo** contraejemplos basta | qué clases no se aprenden con equivalencia sola; si los DFA están entre ellas |
| A3 | **Rivest, R. & Schapire, R.** (1993). *Inference of finite automata using homing sequences.* Information and Computation 103(2):299–347. doi 10.1006/inco.1993.1021 | ScienceDirect (bloqueado); hay versión STOC 1989 | el camino formal de L\* **sin reset**, que es nuestro modelo | qué papel tiene el maestro; qué se aprende sin él; el caso de permutaciones |
| A4 | **Bender, M. & Slonim, D.** (1994). *The power of team exploration: two robots can learn unlabeled directed graphs.* FOCS 1994, pp. 75–85. doi 10.1109/SFCS.1994.365703 | IEEE (probablemente bloqueado); buscar PDF de autor en MIT | corrige mi E-42: dos unidades aprenden sin maestro | condiciones exactas (fuertemente conexo, grado conocido, cota de n), y qué comunican los dos robots |
| A5 | **Goldman, S. & Kearns, M.** (1995). *On the complexity of teaching.* JCSS 50(1):20–31. doi 10.1006/jcss.1995.1003 | ScienceDirect (bloqueado); hay versión COLT 1991 | el nombre correcto de lo que medimos y la cota contra la que compararlo | definición de la dimensión de enseñanza; si se puede calcular para autómatas de 6 estados |
| A6 | **Kearns, M. & Valiant, L.** (1994). *Cryptographic limitations on learning Boolean formulae and finite automata.* JACM 41(1):67–95. doi 10.1145/174644.174647 | ACM (bloqueado); el informe lo dio por verificado a partir de una versión abierta: confirmar cuál | el Teorema 5 que cité | que la dureza es **pasiva y PAC**; qué consultas rompen la barrera; que **no** habla de nuestro modelo |
| A7 | **Groce, A., Peled, D. & Yannakakis, M.** (2002). *Adaptive model checking.* TACAS 2002, LNCS 2280. doi 10.1007/3-540-46002-0_25 | Springer (bloqueado) | la reparación local de C5 se le atribuye | cómo reparan la conjetura: qué conservan, qué rehacen, y si exige reset |
| A8 | **Damasceno, C., Mousavi, M. & Simão, A.** (2019). *Learning to reuse: adaptive model learning for evolving systems.* IFM 2019, LNCS 11918. doi 10.1007/978-3-030-34968-4_8 | Springer (bloqueado) | segunda fuente de C5 | qué parte del modelo viejo sobrevive y cómo se mide |
| A9 | **Korf, R.** (1985). *Macro-operators: a weak method for learning.* Artificial Intelligence 26(1):35–77. doi 10.1016/0004-3702(85)90012-8 | ScienceDirect (bloqueado) | heredar palabras como macroacciones | condiciones de la tabla de macros (serializabilidad) y si se cumplen en nuestros monoides |
| A10 | **Kirby, S., Dowman, M. & Griffiths, T.** (2007). *Innateness and culture in the evolution of language.* PNAS 104(12):5241–5245. doi 10.1073/pnas.0608222104 | PNAS (abierto; **no leído**) | la advertencia sobre el linaje como libro | el resultado con aprendices deterministas (MAP) y el papel del cuello de botella |
| A11 | **Guerin, F.** (2011). *Learning like a baby: a survey of artificial intelligence approaches.* Knowledge Engineering Review 26(2):209–236. doi 10.1017/S0269888911000038 | Cambridge (bloqueado) | el criterio de «emergencia continuada» que usamos para la escalera | la lista exacta de criterios y qué sistemas revisa |
| A12 | **Prince, C., Helder, N. & Hollich, G.** (2005). *Ongoing emergence: a core concept in epigenetic robotics.* EpiRob 2005 | actas abiertas (Lund); **no leído** | mismo uso que A11 | los seis criterios y cuál falta en los sistemas revisados |

## B · Las que sostienen el FAIL de coste de la Fase 1 (citadas en el cierre, leídas sólo de segunda mano)

| # | fuente | dónde | qué verificar |
|---|---|---|---|
| B1 | **Gold, E. M.** (1978). *Complexity of automaton identification from given data.* Information and Control 37(3):302–320. doi 10.1016/S0019-9958(78)90562-4 | ScienceDirect (bloqueado) | el enunciado exacto de NP-completitud del autómata mínimo consistente |
| B2 | **Angluin, D.** (1978). *On the complexity of minimum inference of regular sets.* Information and Control 39(3):337–350. doi 10.1016/0019-9958(78)90683-6 | ScienceDirect (bloqueado) | idem, para conjuntos regulares |
| B3 | **Pitt, L. & Warmuth, M.** (1993). *The minimum consistent DFA problem cannot be approximated within any polynomial.* JACM 40(1):95–142. doi 10.1145/138027.138042 | ACM (bloqueado) | la inaproximabilidad que citamos |
| B4 | **Angluin, D.** (1982). *Inference of reversible languages.* JACM 29(3):741–765. doi 10.1145/322326.322334 | ACM (bloqueado) | la ley de reversibilidad que medimos: qué dice exactamente y en qué modelo |
| B5 | **Holmes, M. & Isbell, C.** (2006). *Looping suffix tree-based inference of partially observable hidden state.* ICML 2006 | leído del PDF del autor: **basta** | — |

## C · Las que las orientaciones citan de resumen y conviene tener (segunda prioridad)

| # | fuente | dónde | para qué |
|---|---|---|---|
| C1 | **Drescher, G.** (1991). *Made-Up Minds.* MIT Press | libro | el mecanismo de esquemas que nuestra unidad reaparece |
| C2 | **Shen, W.-M.** (1994). *Autonomous Learning from the Environment.* Freeman; tesis CMU 1989 | libro / tesis | LIVE: predecir, sorprenderse, identificar |
| C3 | **Perotto, F. & Álvares, L.** (2006/2007). CALM | Springer (bloqueado) / tesis | la «acción de prueba» |
| C4 | **Schmidhuber, J.** (2004). *Optimal ordered problem solver.* Machine Learning 54:211–254. doi 10.1023/B:MACH.0000015880.99707.b2 | Springer (bloqueado); hay arXiv cs/0207097 | el coste de una escalera mal puesta |
| C5 | **Egri-Nagy, A. & Nehaniv, C.** *Hierarchical coordinate systems for understanding complexity and its evolution* (ALife 2008) y SgpDec | abierto | cascadas, macroacciones por coordenada |
| C6 | **Hinton, G. & Nowlan, S.** (1987). *How learning can guide evolution.* Complex Systems 1:495–502 | abierto; **no leído** | aprendizaje y linaje |
| C7 | **Whitehead, S. & Ballard, D.** (1991). *Learning to perceive and act by trial and error.* Machine Learning 7:45–83 | Springer (bloqueado) | aliasing perceptual, el problema de nuestra Fase 1 |

## D · Lo que no se ha buscado y sí habría que buscar antes de la fase del maestro

*teaching dimension finite automata* · *active teaching Mealy machines* · *curriculum learning automata identification* · *iterated learning deterministic agents fidelity* · *two-agent cooperative exploration automata* (seguimiento de A4) · operacionalizaciones de la zona de desarrollo próximo en robótica del desarrollo (Lungarella 2003, Asada 2009, Weng 2001 *Science*).

---

**Regla desde hoy (E-42):** una fuente de esta lista que no esté en `literatura/` y leída se cita como `LITERATURE-CLAIM` y no sostiene ninguna predicción. Las de la sección A son las que bloquean la enmienda de la ficha del maestro; las de B afinan frases del cierre de la Fase 1 que ya están corregidas en su alcance; las de C y D no bloquean nada.
