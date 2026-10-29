# Orientaciones · Fase 3 · dos que viven, uno que observa, y el hijo del observador

**Fecha:** 2026-10-28 · **Para:** Opus 5.5 · **De:** Fable, mezclando lo medido en las Fases 1–2 con el diseño de Wis · **Adjudica:** Wis, que fijó el tercer elemento: «un observador que observa qué hace uno y qué hace otro, copia las dos cosas, evita la mala, conserva la buena, y tiene su propio hijo para reproducir el experimento».

**Qué es.** Un solo experimento que mezcla lo que la Fase 2 dejó entendido: el mundo tiene que ser **caro** para que heredar signifique algo; tiene que haber **algo en juego** para que exista lo bueno y lo malo; tiene que haber **asimetría** entre los que viven para que haya qué transmitir; enseñar funciona por el **disparo**; y lo que pasa entre vidas son **capacidades certificadas**, no memoria. El tercer elemento añade lo que ninguna unidad sola puede tener: **la comparación**. Un actor sólo conoce las consecuencias de lo que él hizo; el observador ve dos vidas a la vez y puede aprender qué daña **sin haberlo sufrido**.

**Criterio de la ficha (regla nueva de Wis, 28-oct):** antes de correr, qué cambia en el ser si sale sí y qué si sale no. **Sí:** el ser existe a escala mínima: desarrollo entre generaciones con algo en juego, y lo que sigue es alfabeto, tamaño y cómputo. **No:** sabremos cuál de los tres ingredientes (algo en juego, otro que enseña, otro que observa) no produce nada, porque cada uno tiene su celda de control.

---

## 1 · El mundo

- **Madre cara.** W₁ de **6 u 8 estados** con `n_min ≥ 4`, elegidos del banco de la Fase 1 entre los que la fresca tarda **más de 256 pasos** en identificar o no identifica en 3 586. (Lección de C5: en el banco de 3 estados vivir cuesta 18 pasos y heredar no puede valer más que eso.) **Puerta previa:** medir ese tiempo y exigirlo antes de correr.
- **Cerrojo encima** (cascada, clase componible; la control no componible como banco paralelo).
- **La variable esencial V**, una por unidad, en [0, 1]. El mundo fija por familia, de forma canónica y desconocida para las unidades: un conjunto de reacciones que la bajan (δ⁻) y un conjunto de palabras cortas que la reponen (δ⁺). V **entra en lo observado**: cada unidad ve su propia V como una coordenada más, y las ve también de los otros (es pública: ver §3). Innato, y nada más: límites [v_min, v_max]; si V cruza v_min, un parámetro de disposición salta por una lista fija (orden del itinerario → elegir on/off → ventana); si V = 0, la vida termina.

## 2 · Los tres elementos

| | **Actor A** | **Actor B** | **Observador O** |
|---|---|---|---|
| arranca | vértice x_A, itinerario base | vértice x_B ≠ x_A, itinerario desplazado un paso | **no actúa** durante la primera fase; sólo recibe |
| aprende de | su propia vida | su propia vida | las dos corrientes `(acción, reacción, ΔV)` de A y de B, con marca de quién |
| enseña | a B, disparo «siempre» (medido en 10: es el disparo lo que enseña) | a A, igual | a nadie, todavía |
| hereda al morir | el **genoma del linaje** (escrito por O) → su hijo | idem | escribe el genoma; su hijo nace con él y **sí actúa** |

**Lo que hace O, exactamente.** Lleva **una hipótesis por corriente** (dos máquinas, construidas con el mecanismo de 02 sobre experiencia **prestada**: la de A y la de B) y un **libro de palabras con consecuencia**: para cada palabra corta ejecutada por A o por B, cuántas veces precedió a una caída de V (mala) y cuántas a una subida o a una predicción correcta sostenida (buena), por situación. Al final de la fase de observación, O **compone**: toma las relaciones certificadas de las dos máquinas que **coinciden**, marca como **a evitar** las palabras que bajaron V en cualquiera de los dos, y como **a conservar** las que la repusieron o predijeron bien en los dos. Eso es «copia las dos cosas, evita la mala, conserva la buena», con contadores. No hay azar en nada: empates por shortlex.

**El hijo de O (O′).** Nace con lo certificado por O (relaciones + palabras con marca buena/mala + clase del monoide) y **sin traza**, y **actúa** en el mismo mundo desde un vértice canónico, con su propia V. Es la prueba de que lo aprendido mirando sirve al actuar: «reproduce el experimento» de sus padres sin haberlo pagado.

## 2-bis · Corrección de Wis (28-oct, noche): el observador escribe el genoma

Lo que yo había escrito dejaba al observador como un copiador de palabras. Wis lo corrigió: **nada sin linaje sobrevive; nada sin código heredado sobrevive; y si las mutaciones no se aplican, no hay evolución.** El observador es quien dice «esto pasó», y lo que pasó **se escribe en el código genético** del linaje, poco a poco. Eso cambia el diseño en una cosa y la hace evolución:

**Dos capas heredables, no una.**
- **Genoma** = la capa de **disposición** de la unidad: con qué nace. Hoy: límites de V, ventana inicial, orden de las letras del itinerario, elegir on/off, y desde ahora también **relaciones innatas** (transiciones con las que el hijo nace ya certificadas) y **palabras innatas a evitar / a conservar**. El hijo no las aprende: las trae.
- **Adquirido** = lo que esa vida construye encima.

**Segunda corrección de Wis, la misma noche: el genoma es antes que nada la libreta de lo que mata.** Yo había llenado el genoma de lo que beneficia: relaciones innatas, palabras buenas. Wis: «solamente le estás otorgando las cosas que le dan beneficio, pero no las que le dan la muerte, la restricción, la negatividad». Y tiene una razón que no es moral sino lógica: **lo que mata no se puede aprender viviendo**, porque el que lo aprende muere; sólo el linaje puede saberlo. Lo que beneficia, en cambio, cada vida lo puede redescubrir. Por eso el orden de escritura del genoma es: **primero lo que mató** (la palabra o la situación que llevó V a cero en un actor), **después lo que restringió** (lo que hizo saltar un parámetro, los transitorios de los que nadie volvió), **y sólo al final lo que benefició**. El tope del genoma se reparte así: las prohibiciones no se borran mientras el mundo no cambie; las relaciones innatas sí. Es exactamente lo que es `ERRORES_Y_GUARDAS.md` para este programa: una lista de lo que no hay que hacer, que se lee en el momento del riesgo. El hijo nace con la libreta de sus muertos.

**Medida añadida:** `muertes_evitadas`: situaciones que mataron a un ancestro y que el hijo, por genoma, no vuelve a pisar; y su control: el hijo con genoma **sin la parte negativa** (sólo lo bueno), que debe morir donde murió su abuelo.

**Esto ya existe en Genesis, y se declara (cartografía del 28-oct):** `runtime/organism/teacher.py`, clase `Teacher`: tras una herida, la propia IA del organismo destila una lección `{avoid, prefer, lesson}`, atendiendo **las heridas más profundas primero**, y la graba como experiencia reforzada que el sesgo de decisión recoge. Es la libreta de lo que mató, escrita por el organismo. La Fase 3 **no la reinventa**: la extiende en tres cosas exactas: (1) el que reflexiona es **otra unidad**, no un 7B; (2) es **determinista**; (3) lee **dos vidas** y escribe en el **genoma del linaje**, no sólo en la experiencia del mismo organismo. Lo demás, el orden «primero lo que dañó», es herencia directa del Teacher.

**El observador es el único que escribe el genoma.** Los actores viven y mueren; O mira las dos vidas, compara, y por cada generación aplica al genoma del linaje **una mutación dirigida**, determinista, derivada de la diferencia entre las dos vidas:
- una palabra que bajó V en los dos actores → pasa al genoma como **innata a evitar**;
- una relación certificada en los dos → pasa como **relación innata**;
- un parámetro de disposición que saltó en uno y precedió a sobrevivir más → pasa como **valor inicial**;
- lo que estaba en el genoma y no se usó en dos generaciones → **se borra** (el genoma tiene tope: cuello de botella).

Una mutación por generación: **un decimal, una adquisición** (norma de la casa). La **selección** la hace V: el hijo que llega a cero antes termina su línea. La **variación** no viene del azar: viene de la **asimetría** entre A y B (vértices e itinerarios distintos), que es lo que le da a O dos vidas distintas que comparar. Evolución determinista: variación por asimetría, mutación dirigida por el observador, selección por viabilidad, herencia por genoma. Lo adquirido pasa al genoma **sólo** a través de O.

**Parámetros (todos declarados en la ficha, con su valor inicial y su mutante):**

| parámetro | valor inicial | qué lo mueve |
|---|---|---|
| contenido del genoma | límites de V, ventana, orden de letras, elegir, relaciones innatas = ∅, palabras innatas = ∅ | O, una edición por generación |
| tope del genoma | 8 relaciones + 8 palabras | fijo; mutante: sin tope (Kirby: debe degradar) |
| regla de escritura | coincidencia en los **dos** actores | mutante O-uno: coincidencia en uno (debe escribir ruido) |
| regla de borrado | no usado en 2 generaciones | mutante: nunca borra |
| mutaciones por generación | 1 | mutante: todas a la vez |
| asimetría A/B | vértice distinto + itinerario desplazado 1 | mutante simétrico: 0 variación |
| selección | V = 0 termina la vida; el linaje continúa por el hijo del que vivió más | mutante: sin V (TRES−V) |
| generaciones | 5 (10 si el reloj lo permite) | — |
| mundo | madre cara (6–8 estados, fresca > 256 pasos) + cerrojo | puerta previa |

**Medida nueva, la que mide evolución:** `genoma_k` por generación (qué contiene), **fracción de lo innato que el hijo usa** (una relación innata que nunca se usa es lastre, no herencia), y **cuánto de la supervivencia de la generación k se explica por lo innato**: el hijo con genoma frente al hijo con genoma vacío (celda **hijo-sin-genoma**), pareado.

**Predicción añadida:** la supervivencia sube de generación en generación **sólo** en las celdas donde O escribe el genoma; con O que copia sin escribir (O-todo) o sin O (DOS), el hijo arranca igual que su padre arrancó. **Falsador del linaje:** el genoma crece y la supervivencia no: el observador escribe cosas que no sirven, y se dice.

## 2-ter · Lo que el mapa basal y primordial cambia en este diseño (28-oct, tras releer `BASAL_DECOMPOSITION_AUDIT`, `CURRENT_STATE_AUDIT`, `PLAN_TRABAJO_PRIMITIVO_BASAL_v1`, `FICHA_CONTRATO_B0` y `P4_REFORMULADO`)

1. **Es la misma matemática, y hay que decirlo.** El mundo del ser es el objeto basal de PRIMITIVO: E₀ = (S, {F_a}) con letras con identidad y estados **sin nombre**. Nuestras cascadas son los pares de particiones de Hartmanis–Stearns que P4 ya auditó; «parte-cociente = congruencia; componente producto = par factor; componente direccional = cascada» es la decisión canónica del 25-sep, y es exactamente lo que el generador de W₂ y el análisis de la pieza 6 usan. Lo que UNIDAD MÍNIMA hace y PRIMITIVO se niega a hacer es **suministrar la unidad**: aquí la unidad es el aprendiz, por declaración. Eso no es un error, pero es un SUMINISTRADO que la ficha debe marcar con el nombre que B₀ le da, y toda afirmación de la Fase 3 es «relativa a esa unidad suministrada», nunca intrínseca.
2. **Naturalidad: el genoma puede nombrar letras, nunca estados.** Por el contrato B₀ (condición 5), las letras tienen identidad física y los estados no: un procedimiento legítimo debe conmutar con todo renombramiento de estados. Por tanto una regla heredable como «lo que te bajó la vida en esa situación no lo repetís» es **ambigua** si «situación» es un estado con nombre; es legítima si se expresa en lo que la unidad construye (su cociente, su hipótesis) o en palabras (letras). Las cinco reglas que escribí el 28-oct tienen ese defecto y se reescriben así: el genoma guarda **palabras** (secuencias de letras) y **relaciones del cociente propio**, nunca índices de estado del mundo. Mutante: un genoma con nombres de estado debe fallar la prueba de renombramiento (correr sobre una copia renombrada del mundo y exigir la misma salida).
3. **La pregunta de Terrario-Ontogeny es la de esta fase, y es más estricta que mi V.** El plan basal la fija como meta de siguiente escala: «¿cómo adquiere un sistema ya constituido una regulación nueva durante su propia historia, **sin recibir del diseñador el blanco, la política correctiva ni la etiqueta de qué debe proteger**?». Mi variable esencial con límites innatos **es una etiqueta de qué proteger**, suministrada. Wis la aceptó como lo único innato, y así se declara; pero el mapa basal ofrece la versión sin etiqueta, que ya estaba en DISCOVERY-00: **restricción relacional mantenida o restaurada**: una región R ⊂ S con F(R) ⊆ R (invariancia) y la vuelta a R tras perturbación. Vivir = permanecer en una región invariante de la propia dinámica; morir = salir de ella sin retorno. No hace falta un escalar ni un límite: la región la define la dinámica del organismo, no el diseñador. Es también Ashby (variables esenciales dentro de límites) y es el cierre de restricciones de Moreno–Mossio que el gate de individualidad causal ya leyó. **Brazo nuevo, V-basal:** la viabilidad como invariancia de región sobre (S_org, {F_a}), medida por I_R y la latencia de retorno de DISCOVERY-00, frente al brazo con V escalar e innata. Si los dos dan lo mismo, la etiqueta no hacía falta; si sólo el escalar produce desarrollo, la etiqueta era necesaria y se dice.
4. **Las cuatro salidas obligatorias de B₀ valen aquí.** Todo resultado sobre «qué heredó», «qué aprendió» o «qué unidad emergió» se informa como una de: identificada · familia equivalente (órbita bajo el grupo declarado) · no identificable con la estructura disponible · ninguna. Y con el diagnóstico: grupo efectivo, |Σ|, tamaño de órbita. Sin eso, «aprendió la máquina» es una afirmación con nombres.
5. **Lo que PRIMITIVO ya cerró y no se reabre aquí:** qué partes determina (S, F) es clásico (congruencias, pares factor, Aut(F)); no hay selectividad no trivial en (S, F) cerrado; con entradas, el enmascaramiento por continuación es la única vía conocida; la unidad queda NO ADJUDICADA como frontera. La Fase 3 no la adjudica: la **supone** y lo dice.

## 3 · Lo que cruza y lo que no (declarado, E-46/E-47)

- **Canal público:** acción, reacción y V de cada unidad son visibles para las demás (como en biología: lo que un organismo hace y si prospera se ve; lo que piensa, no). **Nadie lee la hipótesis de nadie.** O construye sus máquinas desde las corrientes, no las copia.
- **Canal de enseñanza entre A y B:** la palabra más corta que separa dos estados de la propia máquina, disparo «siempre» (de 10). Se registra longitud y `palabra_igual_a_la_letra`.
- **Asimetría declarada:** vértices distintos e itinerario desplazado (E-47). Mutante: A y B simétricos ⇒ 0 intercambio.
- **Herencia:** sólo relaciones con `evidencia ≥ k` y palabras con marca; **nunca** la traza (medido: ahoga).

## 4 · Celdas

| celda | qué separa |
|---|---|
| **TRES** · A, B, O y sus hijos | el experimento |
| **DOS** · A y B sin O (sus hijos heredan de sus padres) | qué añade **observar** |
| **UNO+V** · un actor solo con V, sin maestro | qué añaden **el otro** y el observador |
| **TRES−V** · los tres sin variable esencial (V inerte) | qué añade **algo en juego** |
| **O-todo** · O copia **todo** sin evitar lo malo | qué añade la **selección** |
| **O-ciego** · O recibe las corrientes de **otra** familia | mutante: observar lo ajeno ⇒ su hijo ≤ fresca |
| **O-uno** · O observa sólo a A | qué añade la **comparación** entre dos |
| **herencia-traza** · los hijos heredan la traza | el control ya medido: debe ahogar |
| **simétrico** · A = B | NULO POR SIMETRÍA si no da 0 intercambio |

Mismo mundo, mismos vértices, mismo presupuesto de vida por unidad; pareado por familia. El cómputo se registra y no decide.

## 5 · Medidas, a lo largo de generaciones

1. **Harlow:** acierto en los primeros 64 pasos de la generación k, según k, por linaje (A, B, O).
2. **Supervivencia:** pasos vividos antes de V = 0, por generación y linaje.
3. **Peligro evitado sin sufrirlo:** palabras marcadas malas por O que **O′ nunca ejecuta** y que A y B sí ejecutaron y pagaron. Es la medida propia del observador: aprender el riesgo de otro.
4. **Riesgo:** empates entre hipótesis en los que una rama baja V; cuántas veces O′ elige la otra, frente a A′ y B′.
5. **Kirby, en dos:** fidelidad de **función** (identifica, sobrevive) y de **estructura** (isomorfismo con la máquina del padre) por generación, separadas: la Fase 2 ya mostró que pueden ir en direcciones opuestas.
6. **Contadores de actividad:** intervenciones A↔B, saltos de parámetro por V, palabras marcadas por O, relaciones heredadas, revisadas y supervivientes. Cero en cualquiera ⇒ nulo por inactividad en esa celda.

## 6 · Predicciones, antes de correr

1. **O′ > A′, B′** en Harlow y en supervivencia en la primera generación: el hijo del que miró dos vidas arranca mejor que el hijo del que vivió una. Es la predicción central y la del diseño de Wis.
2. **O-todo < O:** copiar sin seleccionar hereda también lo malo (Derex 2025: lo social conserva lo inútil); **O-uno < O:** sin comparación no se distingue lo que daña de lo que es casualidad.
3. **TRES−V ≈ DOS:** sin algo en juego, el observador no tiene criterio de bueno/malo y se reduce a un segundo maestro.
4. **UNO+V < DOS < TRES** en supervivencia a la tercera generación.
5. **Kirby:** la función se conserva más que la estructura en los tres linajes; en O más que en A y B, porque O hereda lo que coincidió en dos.
6. **herencia-traza** ahoga; **simétrico** da 0 intercambio; **O-ciego** ≤ fresca.

**Falsador del experimento:** Harlow plana y supervivencia plana en TRES a lo largo de cinco generaciones con todos los contadores activos. Entonces ni algo en juego, ni el otro, ni el observador producen desarrollo en este banco, y la mezcla está refutada tal como se mezcló. **Falsador del tercer elemento solo:** O′ ≈ A′ con palabras marcadas > 0: observar no suma a vivir.

## 7 · Lo que hay que decidir antes de la ficha, y es de Wis

- **¿Cuándo empieza a actuar O?** Opción recomendada: O no actúa nunca; actúa su hijo. Alternativa: O actúa tras la primera muerte de un actor. Son dos experimentos distintos.
- **¿Qué ve O de V?** Recomendado: la V de los otros es pública (como el prosperar o decaer de un organismo se ve); si Wis prefiere que sólo vea acciones y reacciones, el riesgo deja de poder aprenderse mirando y hay que decirlo.
- **¿Cuántas generaciones?** Cinco por defecto (como la cadena de 10).

## 8 · Orden

1. Cerrar la Fase 2 con lo que corre (dos unidades) y el cierre honesto de C5 como **nulo por techo** con la distribución de 18 pasos.
2. Puerta previa de mundo caro: medir el tiempo de la fresca en los W₁ candidatos de 6–8 estados; elegir los que superan 256.
3. Gate de antecedentes de los tres elementos (dos columnas, nivel al lado): aprendizaje vicario y por observación (Bandura, `LC`), copia sesgada por éxito y transmisión cultural (Mesoudi & Thornton `X11`, Derex `X12/X13`), ultraestabilidad (Ashby `ADOA-001`), dos robots (Bender–Slonim, A4), imitación en animales y artefactos (Nehaniv & Dautenhahn, por buscar). La columna «en el corpus de Wis: id» obligatoria (E-43).
4. Ficha sobre la plantilla con las celdas de §4, los mutantes, y los dos exámenes de retención/transferencia para los hijos.
5. Mutantes, corrida, cierre con las tres curvas y **una pregunta para Wis**.

**Roles:** Opus construye y corre (reutiliza 08, 09 y 10: el actor es la unidad de 08 con V; el canal de enseñanza es el de 10; la herencia certificada es la de 09 sin traza). Fable revisa gate, ficha y cierre, y escribe la fase siguiente. Nadie enseña paso a paso desde afuera: los maestros son A y B, y el observador es O.
