# Orientaciones · el maestro entra al programa · Fase 2 (celdas nuevas) y lo que se retoma de la investigación profunda

> **Revisión externa del 28-oct, incorporada en el sitio.** El revisor atribuyó este documento a Opus; es de Fable. Cedí en todo lo que verifiqué: dos sobreafirmaciones bibliográficas (Angluin/K–V como explicación del FAIL de coste; «sólo permutación sin maestro», falsa por Bender–Slonim 1994), el nombre de la medida (coste empírico de enseñanza, no dimensión formal), la definición operativa de T2, la predicción sobre accesibilidad del contraejemplo y no sobre clase estructural, los presupuestos igualados de los mutantes, y los dos exámenes de retención y transferencia. Cada cambio lleva la fecha donde está. Lo que no acepté sin ver: Angluin 1990 sigue LITERATURE-CLAIM hasta que se lea aquí.

**Fecha:** 2026-10-28 · **Para:** Opus 5.5 · **De:** Fable · **Adjudica:** Wis. Este paquete **añade** a la ficha `APERTURA_FASE_2_ACUMULACION.md`; no la reemplaza. C5 y los seis mutantes siguen primero.

**La decisión de Wis que lo motiva (28-oct).** «A mí nadie me enseña a leer. No puedo aprender a leer solo.» Un humano criado entre chimpancés actúa como chimpancé: las capacidades no se descubren solas, se desarrollan en un entorno que ya las contiene. Por tanto **«sin maestro» deja de ser principio del ser** y queda como lo que fue: una restricción del problema de identificación de la Fase 1 (sin oráculo ni reset escondidos). La norma que sí rige es la otra: **nadie le resuelve las relaciones.** El maestro dice dónde mirar, qué intentar, qué importa, y nombra; nunca entrega una transición ni una máquina. El ser construye la relación con su propia experiencia.

---

## 1 · Lo que la investigación profunda ya tenía sobre maestros, y se retoma

Todo esto está en el journal del deep-research del 25-oct y en el informe de literatura; se había dejado de lado por la norma «sin maestro». Nivel de evidencia según el informe.

| fuente | qué dice | qué retomamos | nivel |
|---|---|---|---|
| **Angluin 1987, L\*** y **Kearns–Valiant 1994, Teorema 5** | con un maestro que responde consultas de **pertenencia y equivalencia** (las dos, con reset), identificar un DFA es polinómico; K–V prueban dureza criptográfica del aprendizaje **pasivo** en su modelo PAC y que añadir consultas cambia la clase | *(corregido el 28-oct tras revisión externa: la versión anterior decía «el FAIL de coste es el precio de no tener maestro», y eso es más de lo que las fuentes dicen)* Nuestro FAIL es el coste del **mínimo exacto desde una traza pasiva** (Gold, Angluin 1978, Pitt–Warmuth). Que un maestro lo cure **en nuestro modelo sin reset** es la **hipótesis** que T1 prueba, no un teorema heredado: el camino formal más cercano es Rivest–Schapire (homing + L\*) | SOURCE-VERIFIED (K–V); la transferencia a nuestro modelo es HIPÓTESIS |
| **Rivest & Schapire 1993** (homing sequences) y **Bender & Slonim 1994** (dos robots) | los algoritmos de Rivest–Schapire se apoyan en un maestro de contraejemplos salvo el de autómatas de permutación; **pero Bender–Slonim muestran que dos robots cooperantes aprenden grafos dirigidos fuertemente conexos sin maestro**, y Bender 1998 que uno con guijarros también, dada una cota de n | *(corregido el 28-oct: la versión anterior generalizaba «sólo lo de permutación se aprende sin maestro», y es falso)* Lo reversible se identifica solo; lo demás necesita elegir, **cooperar**, maestro o linaje. La cooperación entre unidades queda como hipótesis posterior (es nuestra línea de dos unidades) | SOURCE-VERIFIED (Bender 1998, texto); Bender–Slonim 1994 a metadatos |
| **Angluin 1990**, *Negative results for equivalence queries* | con **sólo** equivalencia (sin pertenencia) hay clases que no se aprenden en polinómico | el maestro de contraejemplos no basta solo: se combina con **elegir** (que hace de consulta de pertenencia sobre el mundo) | LITERATURE-CLAIM desde aquí (Springer bloqueado); la revisión externa del 28-oct dice haberlo verificado: pasa a SOURCE-VERIFIED cuando Wis baje el PDF y Opus lo lea |
| **hW-inference, Groz 2019** | «avoids almost all equivalence queries»; el oráculo es un paseo aleatorio | sustituir ese oráculo por el maestro programático; hW vuelve a ser candidato de 1-bis **con maestro** | SOURCE-VERIFIED |
| **Tadepalli & Natarajan 1996** | el maestro (oráculo de problemas resueltos) **puede ser reemplazado por la búsqueda propia del agente**, pero no gratis: la búsqueda se llama sólo para la celda que falta | es la idea 6: **el alumno se vuelve maestro**; una unidad que identificó un mundo da contraejemplos a la siguiente desde su propia máquina | SOURCE-VERIFIED |
| **OOPS, Schmidhuber 2004** | la aceleración viene de una **secuencia ordenada de tareas** externa; una secuencia mal elegida cuesta más que resolver la tarea final sola | la escalera la pone el maestro, y **puede equivocarse**: el control es una escalera invertida | SOURCE-VERIFIED (resumen) |
| **Guerin 2008; Prince et al. 2005** | el paso al nivel siguiente lo dispara **una relación nueva hecha visible en el mundo**, no un umbral interno; las habilidades nuevas deben ser base de las siguientes | criterio para el peldaño: el mundo siguiente es la cascada más chica que la máquina actual **no explica** | LITERATURE-CLAIM |
| **Kirby, Dowman & Griffiths 2007; Kirby, Griffiths & Smith 2014** (aprendizaje iterado) | en cadenas de transmisión con **aprendices deterministas**, la cadena «converges to a distribution that exaggerates the prior»; los datos se lavan entre generaciones según el cuello de botella | **advertencia para «el linaje es el libro»**: una cadena alumno→maestro→alumno pierde información salvo que lo transmitido esté certificado; medir la fidelidad a lo largo de la cadena | SOURCE-VERIFIED (2014) |
| **Goldman & Kearns 1995** (dimensión de enseñanza) | medida **combinatoria**: el mínimo de ejemplos con que el mejor maestro identifica un concepto dentro de una clase | *(precisado el 28-oct)* lo que nosotros contamos es el **coste empírico de enseñanza** de un maestro concreto, no la dimensión formal; la fuente da el nombre del concepto y la cota inferior contra la que comparar | verificada por la revisión externa a metadatos; leer antes de citar en un cierre |
| **Ernest, Georgeon 2012** | sin maestro, proclividades fijas | sigue como **control**: lo que se logra sin nadie | SOURCE-VERIFIED |

**Lo que no hemos encontrado** (y el gate debe buscar antes de construir): un maestro que **sólo** elija qué vive el alumno, sin etiquetar ni corregir, medido contra el alumno que elige solo, en autómatas sin reset. Y la operacionalización de Vygotsky sobre congruencias de autómatas. Buscar: *teaching dimension finite automata*, *curriculum automata learning*, *active teaching Mealy*, *iterated learning deterministic agents fidelity*.

---

## 2 · El maestro programático: tres formas, de la más débil a la más fuerte

Las tres son **deterministas**, conocen el mundo verdadero (eso es lo que las hace maestro) y **nunca entregan una transición**. Cada una es una celda nueva en la ficha de la Fase 2, pareada con F1, F3 y C5 sobre las mismas familias.

- **T1 · contraejemplo.** Cuando la hipótesis del alumno predice mal, el maestro le da **la palabra más corta desde el estado actual del mundo** en la que su hipótesis y el mundo discrepan, y el alumno la vive. Es el análogo en vida continua de la consulta de equivalencia. **La palabra lleva información privilegiada** aunque no lleve la transición (el maestro conoce el mundo): se registra por intervención su longitud y cuántas transiciones nuevas expone, y el control de «información del maestro» es F3, cuyo elegir va al agujero más cercano de la propia hipótesis **sin conocer el mundo**. Si no existe palabra desde aquí, el maestro **no puede ayudar** y se cuenta: `contraejemplos_imposibles`. Predicción, **sobre la medida y no sobre la clase estructural** (precisado el 28-oct): T1 > F1 en las familias con `contraejemplos_imposibles` = 0 y T1 ≈ F1 en las que > 0; la clase transitoria se informa aparte como descriptor, porque no todo transitorio es inenseñable, sólo lo que ya no se alcanza desde el estado actual.
- **T2 · itinerario.** El maestro no espera al error. **Definición operativa exacta** (precisada el 28-oct): desde el estado verdadero actual x y el estado q que el alumno cree ocupar, el maestro simula la hipótesis H contra el mundo M sobre las palabras en orden shortlex y da la **primera** en la que H predice distinto de M o no tiene ruta; el alumno la vive. Sin reset, vivir esa palabra puede cerrar otras (el mundo se mueve): por eso `T2 ≥ T1 ≥ F3 ≥ F1` es **hipótesis falsable**, no relación garantizada, y se preregistra como tal. La cifra que se informa es el **coste empírico de enseñanza**: intervenciones hasta identificar, por estrato y clase, contra la cota de Goldman–Kearns si se puede calcular en mundos de 6 estados.
- **T3 · escalera.** El maestro elige el **mundo siguiente**: la cascada más chica que la máquina actual del alumno no explica. Es la idea 4 y la de Guerin. Control: escalera invertida (el mundo más grande primero), que según OOPS debe costar más que no tener escalera. **T3 no entra en la Fase 2**: es la cadena de mundos de la fase siguiente, junto con C5 certificado.

**Lo que el maestro no hace, y es la norma de Wis:** no da la máquina, no da el estado, no da la salida esperada, no dice «esto es bueno». Da palabras para vivir. La relación la construye el alumno con el mecanismo que ya tiene.

**Mutantes del maestro, obligatorios, con presupuestos igualados** (precisado el 28-oct: mismo número de pasos de vida y mismo tope de longitud de palabra, 2·|Q|, en todos; se registra por mutante cuántas transiciones nuevas expone cada intervención, porque una palabra larga puede exponer más): (M-t1) *maestro simulado*: da una palabra donde el alumno **acierta**; debe dar ≈ F1. (M-t2) *maestro del mundo equivocado*: enseña con otro W₂ de la misma clase; predicción **no mejora** respecto de F1 más allá del ruido (empeorar no está garantizado). (M-t3) *maestro de la palabra más larga dentro del tope*: predicción T1 ≥ M-t3; si M-t3 iguala a T1 con más transiciones expuestas, lo que enseña es la exposición y no la corrección, y se dice. Sin azar en ninguno.

---

## 3 · Medidas, en el criterio de desarrollo

- **Alcance** en la curva (64, 128, 256), pareado por familia, como en la ficha.
- **Dimensión de enseñanza medida:** `intervenciones_hasta_identificar` por estrato y clase; es lo que un maestro cuesta en palabras, no en cómputo.
- **Qué deja el maestro cuando se va**, en **dos exámenes separados** (precisado el 28-oct):
  - *Retención:* con el maestro retirado y **la hipótesis congelada** (sin aprender), exactitud sobre el futuro fijo del mismo mundo. Mide lo que quedó almacenado.
  - *Transferencia:* el alumno sigue **sin maestro y aprendiendo** 512 pasos en el mismo mundo y luego en una cascada nueva W₃, contra una fresca y contra F3. Mide si lo enseñado sirve de base para lo siguiente (criterio de Guerin y Prince). Separar los dos es lo que distingue memoria de aprendizaje nuevo, y es requisito antes del libro del linaje.
- **Instruibilidad por nombre** queda para la fase siguiente (idea 3: nombrar palabras); aquí sólo se registra el repertorio.

**Predicciones a preregistrar:** T1 > F1 en los tres hitos en la clase componible y en la control (el maestro no depende de la herencia); T1 ≈ F1 en los mundos **transitorios estructurales** (`contraejemplos_imposibles` > 0 ahí y ≈ 0 en los recurrentes); T2 ≥ T1; el alumno conserva la exactitud al irse el maestro. **Falsador:** T1 ≈ F1 en los recurrentes con `contraejemplos_dados` > 0: entonces el contraejemplo no enseña a esta unidad y el mecanismo de lectura es el que falla, no el maestro.

---

## 4 · Orden

1. C5 y los seis mutantes de la ficha, como está. Nada se adelanta.
2. **Gate de antecedentes del maestro** (la tabla de §1 más las búsquedas de §1): dos columnas, nivel por fuente. Goldman–Kearns y Angluin 1990 quedan LITERATURE-CLAIM si siguen bloqueados y se dice.
3. Enmienda prospectiva de la ficha: celdas T1 y T2, sus tres mutantes, sus medidas y predicciones. Misma campaña, mismas familias, pareado.
4. Cierre único de la Fase 2 con C5 y T1/T2 juntos. La pregunta para Wis que veo venir: si el maestro cura lo recurrente y el linaje tiene que curar lo transitorio, ¿la fase siguiente es la escalera (T3) o el libro (C5 certificado en cadena)? Probablemente las dos son la misma fase.

## 5 · Qué hace cada rol

- **Opus:** §4. El maestro programático lo escribe él; **ni Opus ni Fable enseñan paso a paso** (3 586 pasos × 2 134 familias no es reproducible ni pagable).
- **Fable:** revisa el gate y la enmienda; cuando C5 y T1/T2 cierren, escribe la orientación de la fase siguiente: nombres (idea 3), escalera (T3) y libro (linaje certificado), que es donde Opus enseña en el nivel de arriba con cada decisión registrada.
- **Wis:** adjudica la enmienda y la pregunta del cierre.
