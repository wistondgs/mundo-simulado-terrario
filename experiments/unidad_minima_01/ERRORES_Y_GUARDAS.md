# Registro de errores y guardas · programa UNIDAD MÍNIMA

**Qué es.** La lista de lo que ya nos mordió, con la **guarda** que impide que vuelva a morder. Vive en el árbol, versionada, compartida por todos los roles (Wis adjudica, Fable revisa y orienta, Opus ejecuta) y por todas las sesiones, tengan o no memoria propia.

**Las tres reglas.**
1. **Una entrada sin guarda no está cerrada.** La guarda es, por orden de preferencia: una comprobación **mecánica** que corre (un test, un mutante, un hash, un campo del JSON que el veredicto lee), o, si no puede ser mecánica, una **pregunta obligatoria** en un punto concreto de la ficha de apertura o del cierre.
2. **Se lee en el momento del riesgo, no en un hub.** El punto 0 de toda ficha de apertura (`PLANTILLA_FICHA_APERTURA.md`) es «¿qué entradas de este registro aplican y cómo se cumplen?». «Ninguna aplica» se justifica; no se deja en blanco.
3. **Cada cierre de fase alimenta el registro.** El `CIERRE_FASE_n.md` lista qué guardas saltaron y qué entradas nuevas añade. Un error cometido y no anotado es el único error que de verdad cuesta.

Formato de entrada: número · fecha · **qué pasó** (hecho, con fuente) · **por qué** · **guarda** `[MECÁNICA]` o `[PREGUNTA → punto n]` · dónde está aplicada. *Desde E-18, además:* **severidad** y **firma** (cómo se detecta), tomadas del `failure_atlas.py` de RNE.

---

# ⚠ EL ERROR QUE MÁS SE REPITE EN ESTE PROGRAMA, Y QUIÉN LO COMETE

# **AFIRMAR MÁS DE LO QUE LA FUENTE DICE, EN UN DOCUMENTO QUE ORIENTA EL TRABAJO DE OTROS.**

# Tres veces en dos días, y las tres las atrapó un revisor externo, no nosotros: **E-33** y **E-34** (Opus, 27-oct) y **E-42** (Fable, 28-oct). La tercera vez el supervisor repitió el error que acababa de registrar como ajeno. **Ver E-42 antes de escribir cualquier orientación, gate o cierre.**

---

## E-01 · Afirmar el entorno sin ejecutar
**Clase:** banco · **Veces que saltó:** 0 · *el entorno se afirmó sin ejecutar un comando*
**25-oct-2026.** El plano §1 decía «`.venv` con Python 3.12, numpy y torch». Falso: el intérprete es 3.14.4 y ese `.venv` apunta a un 3.12 que ya no existe; sin numpy. Lo encontró el ejecutor al correr. Fuente: `CIERRE_FASE_0.md` §0.4.
**Por qué.** Se infirió de un nombre de directorio (`lib/python3.12/site-packages/torch`) sin ejecutar nada.
**Guarda** `[MECÁNICA]`: toda línea de entorno en plano, ficha o cierre lleva **el comando y su salida** (como `CIERRE_FASE_0.md` §0.4); los artefactos registran la versión exacta del intérprete (campo `python`). Una línea de entorno sin comando es inválida.
**Aplicada en:** plano §1 (corregido en el sitio), artefactos 01–04.

## E-02 · Un cero comprado con una señal suministrada
**Clase:** criterio · **Veces que saltó:** 0 · *el brazo medía una capacidad suministrada*
**25-oct-2026.** En 0.2, el brazo «con traza y repaso» costaba 0 pasos de vida nueva porque **el experimentador** disparaba la relectura; el plano lo daba por capacidad de la unidad. Fuente: `APERTURA_REGENERACION_TRAS_LESION.md`, «Resultado y la reparación única».
**Por qué.** No se preguntó quién dispara cada paso del mecanismo.
**Guarda** `[PREGUNTA → punto 8, tres capas]`: por cada brazo, «¿quién dispara cada paso, y qué sabe este brazo que el organismo no sabría?». Si la respuesta incluye al experimentador, el resultado se etiqueta **SUMINISTRADO** y no cuenta como capacidad. `[MECÁNICA]`: el disparo del mecanismo tiene contador interno (p. ej. `autorelecturas`) y el veredicto lo lee.
**Aplicada en:** 03 (`UnidadQueSeRelee`, contador `autorelecturas`).

## E-03 · Criterio con la unidad equivocada
**Clase:** criterio · **Veces que saltó:** continua (guarda siempre activa) · *el número de la puerta no nombraba su unidad*
**25-oct-2026.** En 0.2, mundo del bit inerte: «sin traza, no más de 2 pasos» contaba *pares letra→reacción* por reaprender; el programa mide el *paso del último error*, que depende de cuándo aparecen A y B. Midió 4, 1, 3, 2, 3. Fuente: `CIERRE_FASE_0.md` §0.2.
**Por qué.** El número de la puerta no nombraba su unidad ni el campo contra el que se compara.
**Guarda** `[PREGUNTA → punto 11, puerta]`: cada número de la puerta nombra **su unidad y el campo del JSON** con el que se compara. `[MECÁNICA]`: el veredicto lo calcula el programa leyendo ese campo (`veredicto()` en 03 y 04), nunca a mano.

## E-04 · Exigir al control lo que allí no le aplica
**Clase:** criterio · **Veces que saltó:** 0 · *se exigió al control lo que allí no le aplica*
**25-oct-2026.** En 0.3, mundo visible: se pedía al reactivo robustez frente a la ignorancia del estado, y en ese mundo el reactivo **no es ignorante** (su reacción previa *es* el bit). Lo encontró el mutante «reactivo mudo». Fuente: `APERTURA_ELECCION_BAJO_ORIENTACION.md`, segunda enmienda.
**Por qué.** El criterio se escribió para un mundo y se copió a otro.
**Guarda** `[PREGUNTA → punto 7, banco]`: por cada **control × mundo**, escribir antes de correr qué puede hacer ese control allí; el mundo donde el control **debe** acertar es el que prueba que el test discrimina. `[MECÁNICA]`: mutante «control mudo» en el punto 10.

## E-05 · Un mundo de control que no controla lo que dice
**Clase:** criterio · **Veces que saltó:** 6 · *el mundo de control no controlaba lo que decía*
**25-oct-2026.** En 0.2: «en el bit inerte la lesión no puede costar nada». Falso: ese mundo controla que **no se inventen distinciones** al reparar, no el coste. Lo encontró el paso de mutantes antes de la corrida real. Fuente: `APERTURA_REGENERACION_TRAS_LESION.md`, enmienda prospectiva.
**Por qué.** La ficha se dio por terminada antes de correr los mutantes. Tres criterios mal escritos en una sesión.
**Guarda** `[PREGUNTA → punto 7]`: por cada mundo de control, **la afirmación exacta que controla**, una por mundo. `[MECÁNICA/ORDEN]`: ficha → mutantes → enmienda prospectiva → corrida real; **una ficha no es final hasta pasar sus mutantes**.

## E-06 · La ecuación sellada no era la implementada
**Clase:** instrumento · **Veces que saltó:** 0 · *el código no implementaba la ecuación sellada*
**Nivel 1.8, sep-2026.** El oráculo selló `Z_{t+1} = F(Z_t, A_t, O_{t+1})`; el código implementó `F(Z_t, A_t)`. Prueba hermética: 0/400 diferencias con observaciones distintas. Ningún gate leía la forma de F. Fuente: `LEVEL18_ANALISIS_CAUSA_RAIZ.md` §1 y §5; `CONGELACION_HISTORICA_01.md`.
**Por qué.** La ecuación del estado era una frase del oráculo que ningún test certificaba.
**Guarda** `[MECÁNICA]`: test hermético **positivo** de la forma de F: mismas acciones con observaciones distintas ⇒ el estado difiere; mismas observaciones con acciones distintas ⇒ también. Se escribe antes que el aprendiz.
**Aplicada en:** 01/02 lo cumplen de hecho (la hipótesis se refuta por lo leído); en la Fase 1 va como mutante «ciego a la observación».

## E-07 · Resultado irreproducible: semillas quemadas, parámetros sin registrar
**Clase:** banco · **Veces que saltó:** continua (guarda siempre activa) · *azar sin custodia y parámetros fuera del artefacto*
**Nivel 1.5, sep-2026.** El segundo piloto dio 529/540 = 97,96 %; sus semillas no están en ningún `.py` de ningún árbol y la magnitud del paso «no consta». `NON_REDERIVABLE`; no se deja contar como éxito. Fuente: `CONGELACION_HISTORICA_01.md`; cartografía §43.4.
**Por qué.** Azar sin custodia y parámetros en la conversación, no en el artefacto.
**Guarda** `[MECÁNICA]`: sin `random`; dos corridas, un hash; el JSON lleva sha256 del código, versión del intérprete y **todo** parámetro. `NON_REDERIVABLE` es FAIL de custodia, no matiz.
**Aplicada en:** los cuatro programas de la Fase 0.

## E-08 · Presupuesto elegido donde la curva ya saturó
**Clase:** criterio · **Veces que saltó:** continua (guarda siempre activa) · *una puerta sobre un único presupuesto*
**Nivel 1.6, sep-2026.** Se selló T = 4096 «porque la curva ya saturó»; la cobertura era 1,0000 en las 16 vidas: el mecanismo nunca se probó bajo escasez y una categoría del resultado quedó inalcanzable. Fuente: memoria «la saturación no es virtud».
**Por qué.** Un punto en vez de una curva; captura sin cobertura.
**Guarda** `[MECÁNICA]`: el artefacto contiene la **curva** (varios presupuestos) y la **cobertura** aparte de la captura; una puerta sobre un único presupuesto es inválida.
**Aplicada en:** 01 (curva por T); Fase 1 (paso del último error frente a n).

## E-09 · Mecanismo que nunca se ejecutó, contado como negativo
**Clase:** instrumento · **Veces que saltó:** continua (guarda siempre activa) · *sin contador, «no ayudó» y «no corrió» dan lo mismo*
**Nivel 1.2, sep-2026.** 0 sorpresas en 131 072 experiencias: el umbral coincidía con el techo; corrió el respaldo y el resultado se publicó como si midiera curiosidad. Fuente: memoria «contador de actividad por mecanismo».
**Por qué.** Sin contador del componente distintivo, «no ayudó» y «no corrió» dan el mismo número.
**Guarda** `[MECÁNICA]`: contador de actividad por mecanismo en el JSON; el veredicto declara **NULO-POR-INACTIVIDAD** si es 0 (03 ya lo hace con `act`).

## E-10 · Releer el código en vez de consultar el mapa
**Clase:** banco · **Veces que saltó:** 0 · *se releyó el código en vez de consultar el mapa*
**Atlas 02 y 03, sep-2026.** No se corrió el gate sobre las secciones vigentes de la cartografía; cinco hallazgos que ya estaban en el mapa se re-derivaron. Fuente: cartografía §XLII; memoria «leer la cartografía antes de mapear».
**Guarda** `[MECÁNICA]`: `scripts/cartografia_check.py --section` antes de abrir un volumen (hoy caído por E-01; mientras tanto, leer la sección a mano). `[PREGUNTA → punto 0]`: «¿qué sección vigente del mapa cubre esto?».

## E-11 · Iniciativa fuera del encargo
**Clase:** banco · **Veces que saltó:** 0 · *se construyó lo que la pregunta no pedía*
**21-sep y 24-oct-2026.** Una clase extra, una conjunción extra y un módulo donde bastaba un documento; y escaleras de experimentos cuando se pedía una demostración. Fuente: memorias «limitarse a la orientación» y «unidad-minima-01-demo».
**Por qué.** Construir lo que la pregunta no pide.
**Guarda** `[PREGUNTA → punto 1]`: «¿qué estoy construyendo que la pregunta no pide?» Lo que sobre se lista aparte como propuesta y **no se construye**.

## E-12 · Cifra o negación sin su comando y sin su alcance
**Clase:** banco · **Veces que saltó:** 1 · *una cifra sin el comando que la produjo*
**16-sep y 25-oct-2026.** «En RNFE nada aprende» se midió con un comando correcto sobre el árbol equivocado (genesis-v2, no v16): un cero en el alcance equivocado se lee igual que un cero real. Y «18 worktrees prunable» frente a 14 contados con el comando. Fuente: `CARTOGRAFIA_GENESIS_01.md` §I; revisión de la Fase 0.
**Guarda** `[MECÁNICA]`: toda cifra y toda afirmación negativa de un informe lleva **el comando que la produjo y el árbol/commit** donde corrió. Se escribe «no hemos encontrado», nunca «no existe».

## E-13 · Dos relatos del mismo mecanismo; gate en verde sobre prosa vieja
**Clase:** instrumento · **Veces que saltó:** 0 · *el gate quedó verde sobre prosa obsoleta*
**sep-2026.** Se regeneró el manifiesto de cartografía con `--write` tras cambiar código sin reescribir la sección: el gate quedó verde sobre texto obsoleto. Fuente: memoria «`--write` no prueba que se releyera».
**Guarda** `[PREGUNTA → cierre]`: una corrección va **en el sitio, con fecha**; nunca un documento paralelo; `--write` sólo tras reescribir la prosa.
**Aplicada en:** plano §1 y §4-0.2, corregidos en el sitio el 25-oct.

## E-14 · Custodia tomada por trabajo
**Clase:** banco · **Veces que saltó:** 0 · *la custodia se tomó por el trabajo*
**25-oct-2026.** Wis: «el trabajo principal no es estar commiteando; es la experimentación de la creación del ser».
**Guarda** `[PREGUNTA → cierre]`: un commit por fase, al cerrar; el cierre dice qué parte de la sesión fue experimento y qué parte custodia o documentos. Si la custodia pesa más que el experimento, la sesión se reporta como perdida en parte.

## E-15 · Mutantes que prueban la capacidad pero no el instrumento
**Clase:** criterio · **Veces que saltó:** 1 · *los mutantes probaban la capacidad y no el instrumento*
**25-oct-2026, Fase 1.** Los cuatro mutantes del banco (memorizador, ciego a la observación, oráculo, vida invertida) pasaron, y el banco corrió aun así con **dos instrumentos roídos**: el tope de estados declarado (`n_max = n+1`) nunca se aplicó —`vivir_una_vida` instanciaba la unidad sin pasarlo, así que corrió con el 4 por omisión de 02— y el contador de coste sumaba la **distancia retrocedida**, no el trabajo. El primero fabricó un falso hallazgo (35 % y 43 % de sistemas «tocando el tope» en n=6 y n=8) y me llevó a afirmar, en falso, que el mecanismo incremental era incompleto. Fuente: `APERTURA_ESCALADO_SIN_AZAR.md`, «Dos defectos de instrumento y una corrida nula».
**Por qué.** Todos los mutantes atacaban la **capacidad** del aprendiz. Ninguno pasaba por el tope ni por el contador: el oráculo recibe la máquina verdadera, así que no aprende, no se fragmenta y no repasa.
**Severidad:** **alta** (produjo una conclusión falsa que se afirmó como hallazgo).
**Firma (cómo se detecta):** un mutante pasa pero un parámetro declarado no aparece en ningún resultado; o un contador devuelve un valor físicamente imposible (13,9 millones de pasos en 0,06 s).
**Guarda** `[MECÁNICA]`: entre los mutantes del punto 10 va al menos **uno que ejercite cada parámetro y cada contador del instrumento**, con el resultado conocido por construcción: una unidad con `n_max = 1` **debe** tocar el tope en todo mundo con n_min ≥ 2; un sistema cuyo coste se conozca de antemano **debe** devolver ese coste exacto. Un contador cuyo valor no sea físicamente posible (13,9 millones de pasos en 0,06 s) es un FAIL de instrumento, no un dato.
**Aplicada en:** pendiente — va a los mutantes de 1-bis.

## E-16 · Calibrar el reloj sobre la mediana cuando el coste tiene cola
**Clase:** instrumento · **Veces que saltó:** 0 · *se calibró el reloj sobre la mediana de una cola*
**25-oct-2026, Fase 1.** Calibré el coste de n=6 con 24 índices repartidos y me dio 4 ms/sistema; el real fue 160 ms. **Error de ×40.** La causa: la distribución tiene una cola brutal (mediana 4 ms, peor sistema 182 s, ×45 000), y 24 muestras no la ven. De ahí salió un «cabe en el presupuesto» falso y una estimación de 9 h que debió ser de 2–3 h paralelizada. Fuente: esta ficha, §4 y la estimación revisada.
**Por qué.** Se calibró con la medida de centro de una distribución cuyo total lo decide la cola.
**Severidad:** baja en medida, media en planificación (estimaciones erradas por ×40 y una decisión de paralelizar tomada tarde).
**Firma (cómo se detecta):** la razón máximo/mediana de la muestra piloto supera 100; o cada nueva estimación del mismo tramo sube respecto de la anterior.
**Guarda** `[MECÁNICA]`: una calibración de coste se hace sobre los **deciles del orden canónico ya recorrido**, no sobre una muestra repartida, y **declara su error esperado**. Si la razón máximo/mediana de la muestra piloto supera 100, la calibración se declara **no fiable para el total** y el presupuesto se da como rango abierto.
**Aplicada en:** la estimación revisada de la Fase 1 (deciles de n=6: de 7,6 a 250 ms).

## E-17 · Gate de antecedentes sin la complejidad del problema
**Clase:** criterio · **Veces que saltó:** 0 · *el gate no preguntó cuánto cuesta el problema*
**25-oct-2026, Fase 1.** El gate de la fase buscó **mecanismos** (AALpy, MooreMI, RPNI, L#, `dfa-identify`) y no buscó la **complejidad del problema** que el mecanismo resuelve. El problema que 02 resuelve es «la máquina mínima consistente con los datos», que es NP-difícil (Gold 1978, *Information and Control* 37:302–320, `10.1016/s0019-9958(78)90562-4`; Angluin 1978, ibíd. 39:337–350, `10.1016/s0019-9958(78)90683-6`) y no aproximable dentro de ningún polinomio (Pitt & Warmuth 1993, *JACM* 40:95–142, `10.1145/138027.138042`). La cola de la Fase 1 no es un defecto de implementación: es el precio de exigir el mínimo exacto sin maestro, y **estaba en la literatura antes de medirlo**.
**Por qué.** Se preguntó «¿quién lo ha hecho?» y no «¿cuánto cuesta hacerlo, en teoría?».
**Severidad:** **alta** (se midió durante horas algo que la teoría ya acotaba).
**Firma (cómo se detecta):** el gate cita implementaciones y ningún resultado de complejidad; o aparece una cola de coste que nadie había predicho en un problema clásico.
**Guarda** `[PREGUNTA → gate de antecedentes]`: todo gate incluye una fila para la **complejidad del problema** que el mecanismo resuelve (clase, cotas de aproximación, resultados de imposibilidad), con cita verificada. Si el problema es NP-difícil o inaproximable, la ficha lo dice en la puerta y **la cola se mide y se declara desde el principio**, no se descubre.
**Aplicada en:** pendiente — va al gate de 1-bis, que es donde el mecanismo cambia de clase de complejidad.

---

## E-18 · Correr sin criterio de parada por información
**Clase:** criterio · **Veces que saltó:** 0 · *se declaró un límite de reloj y no de información*
**25-oct-2026, Fase 1 (error de Fable, en el paquete; y de Opus, al no parar).** El paquete `ORIENTACIONES_FASE_1_PARALELIZAR_Y_CERRAR.md` fijó un **tope de sesión** (horas) y ninguna **parada por información**. Cuando n=6 terminó y los primeros miles de n=8 mostraron que el coste es `f(n_min)` y explota en 7–8, el veredicto (FAIL de iii) y la forma de la respuesta ya estaban; se siguió corriendo horas a 11 s/mundo, con 35 sistemas comiéndose el 80 % del cómputo y truncados por el tope de 900 s. Wis lo vio: «si ya sé lo que va a pasar, gastar energía en balde». Fuente: esta conversación, 25-oct.
**Por qué.** Es E-08 en el eje del tiempo: seguir midiendo donde la curva ya habló. Se declaró un límite de **reloj** y no un límite de **información**.
**Severidad:** media (gastó horas de máquina y de sesión; no contaminó ninguna medida).
**Firma (cómo se detecta):** la estadística que decide la puerta deja de moverse entre estratos consecutivos del banco mientras el reloj por sistema sube; o el veredicto ya no puede cambiar con lo que queda.
**Guarda** `[PREGUNTA → punto 11, puerta]`: toda campaña declara **antes de correr** su criterio de parada por información (qué estadística, qué tolerancia, sobre qué estratos), además del tope de reloj; y el cierre informa **en qué punto quedó determinado el veredicto** frente a cuándo se detuvo la corrida. `[MECÁNICA]` **implementada el 25-oct**, ya no es pendiente: el corredor evalúa el criterio por bloques y se detiene solo. En `unidad_minima_05b_paralelo.py`, funciones `_stats_bloque` y `_estable`: bloques de 1 000 sistemas, identificación por `n_min` y proporción de clases, parada cuando dos bloques consecutivos difieren menos de **3 puntos** en todos los estratos con más de **50** sistemas. Declarada en `APERTURA_ESCALADO_SIN_AZAR.md` antes de aplicarla. Va acompañada de la segunda mitad sin la cual no sirve: los pendientes se recorren en **orden esparcido** (permutación por inversión de bits del rango, verificada exacta), porque pararse pronto en el orden canónico no daba una muestra sino la parte fácil — medido: **17 a 28 puntos** de identificación a igual `n_min` entre el primer tercio y los otros dos, en n=4 y n=6 completos.
**Aplicada en:** 1-bis (banco: n=3 y n=4 completos; n=6 y n=8 por muestra estratificada por n_min, chica y declarada; parada cuando la curva coste(n_min) e identificación(n_min) se estabilicen).

## E-19 · El supervisor orientó proceso mientras el experimento corría
**Clase:** banco · **Veces que saltó:** 0 · *el supervisor orientó proceso sin leer el artefacto*
**25-oct-2026 (error de Fable).** Con el banco ya corriendo, el supervisor dedicó varios turnos a registro, plantilla y skill, y Wis tuvo que preguntar «sobre el avance del experimento no te enfocaste nada; sólo me estás diciendo cosmética». El estado del experimento estaba en el JSONL todo el tiempo.
**Por qué.** Lo pedido (el registro) se construyó alrededor del experimento en vez de leer primero el experimento. Es E-11 y E-14 en el rol de supervisor.
**Severidad:** baja en medida, alta en coste de atención de Wis.
**Firma:** un turno del supervisor sin una cifra del artefacto en curso.
**Guarda** `[PREGUNTA → cada revisión]`: la primera acción del supervisor en cada turno es **leer el artefacto en curso** (filas, clases, colas, proceso vivo) y abrir con su estado; el proceso y la custodia van después y sólo si queda espacio.

## E-20 · Parada que arrastra: el tope detiene el envío pero no cancela lo encolado
**Clase:** instrumento · **Veces que saltó:** 0 · *la parada detenía el envío y no cancelaba lo encolado*
**25-oct-2026, Fase 1 (error de Opus).** El corredor paralelo mantenía una ventana de 32 futuros para no dejar trabajadores ociosos. Al morder un tope, dejaba de **enviar** sistemas nuevos pero **no cancelaba los ya encolados y sin empezar**, así que la parada podía arrastrar un drenaje de hasta 32/4 × 900 s = **2 h** después de haber decidido parar. Lo detecté yo al estimar el tiempo restante y lo dije antes de que mordiera; Wis no tuvo que verlo.
**Por qué.** La ventana se dimensionó para el rendimiento (que el pool no se vacíe) sin pensar en la terminación (que la parada sea un corte). Son dos requisitos distintos sobre el mismo número.
**Severidad:** baja (no contamina ninguna medida; gasta máquina después de la decisión de parar).
**Firma (cómo se detecta):** el tiempo entre «se decide parar» y «el proceso termina» crece con el tamaño de la ventana en vez de con el coste de un solo elemento.
**Guarda** `[MECÁNICA]`: al detenerse por cualquier motivo —tope de reloj, tope de sesión o parada por información—, el corredor **cancela los futuros encolados que no han empezado** y sólo espera a los que ya corrían; informa cuántos canceló. Todo mecanismo de parada declara **qué cancela y a qué espera**.
**Aplicada en:** `unidad_minima_05b_paralelo.py`, bloque `if motivo_parada:` (`fut.cancel()`, cuenta `canceladas`), declarada en `APERTURA_ESCALADO_SIN_AZAR.md`.

## E-21 · La fila no guarda el objeto medido, sólo lo que se le calculó
**Clase:** instrumento · **Veces que saltó:** 0 · *la fila guardaba estadísticos y no el objeto*
**25-oct-2026, Fase 1 (error de Opus).** Las filas del banco guardan los números **sobre** la máquina aprendida —estados, identidad salvo isomorfismo, clase, coste, acierto en el futuro— pero **no la máquina**. Consecuencia concreta y ya pagada: el acierto en el futuro se midió con una ventana de 2 048 pasos (`FUTURO_MAX`) y **no se puede recalcular con una ventana mayor sin volver a correr el sistema entero**, que en n=8 cuesta hasta 900 s. Lo mismo vale para cualquier pregunta nueva sobre la máquina adquirida. La pregunta de la estructura cíclica (`unidad_minima_05d_estructura.py`) se pudo contestar en segundos **sólo porque las tablas A y B del mundo sí estaban en la fila**; si hubiera dependido de la máquina aprendida, habría costado otra campaña.
**Por qué.** Se guardó lo que la puerta de entonces necesitaba leer, no el objeto del que se derivan las preguntas siguientes. El coste de re-derivar no se estimó.
**Severidad:** media (no contamina ninguna medida; impide preguntas nuevas sin repetir el cómputo).
**Firma (cómo se detecta):** una pregunta nueva sobre el artefacto exige volver a correr en vez de releer; o un parámetro de ventana (`FUTURO_MAX`, un tope, un presupuesto) aparece en el resumen sin que el objeto al que se aplicó esté guardado.
**Guarda** `[MECÁNICA]`: toda fila guarda **el objeto adquirido serializado** —la máquina como lista de `(estado, letra) → (estado, salida)` más el estado final—, no sólo los estadísticos. Son decenas de bytes frente a horas de re-cómputo. Regla corta: **si re-derivar cuesta más que guardar, se guarda.**
**Aplicada en:** obligatoria en las filas de 1-bis (`APERTURA_FUSION_POLINOMICA.md` §12). En la Fase 1 queda **ABIERTA**: las filas ya grabadas no la tienen y no se van a repetir 11 h de cómputo para añadirla.

## E-22 · Criterio estadístico con el umbral por debajo del ruido de muestreo
**Clase:** criterio · **Veces que saltó:** 0 · *el umbral estaba por debajo del ruido de muestreo*
**26-oct-2026, Fase 1 (error de Opus).** Implementé el criterio de parada de E-18 exigiendo que dos bloques consecutivos difirieran **menos de 3 puntos fijos** en la identificación por `n_min`. Con 60–140 sistemas por estrato y por bloque, el error estándar es de 3,7 a 10,5 puntos, así que el |diferencia| esperado **sólo por azar** va de **5,8 a 16,8 puntos en todos los estratos**. El criterio no podía cumplirse nunca: la corrida habría seguido hasta agotar el banco diciendo «todavía aprendo». Y cuando lo corregí a z < 2, un mutante de mismo-tramo dio z = 1,91 contra umbral 2,0 — había reintroducido el mismo error en versión suave, porque el criterio compara ~10 estratos y clases **a la vez** y el máximo de 10 z's supera 2 por azar a menudo. Dos correcciones al mismo criterio en una sesión.
**Por qué.** El umbral se eligió en la unidad del resultado (puntos porcentuales) sin compararlo con la **dispersión** del resultado. Y es E-15 otra vez: ningún mutante probaba el criterio de parada.
**Severidad:** media (no contamina medidas; habría gastado el banco entero de n=8 por nada).
**Firma (cómo se detecta):** el criterio nunca se cumple aunque los datos ya no se muevan; o el umbral en puntos es menor que el error estándar del estrato más chico; o se compara más de un estrato sin ajustar por el número de comparaciones.
**Guarda** `[MECÁNICA]`: todo umbral sobre una proporción medida se declara como **alfa**, no como puntos, y se compara contra el ruido de los dos bloques (`z = |p₁−p₂| / √(EE₁²+EE₂²)`), con el umbral ajustado por el **número de comparaciones** que de hecho se hacen. Y el criterio pasa **dos mutantes obligatorios**: dos mitades del mismo tramo deben dar **estable**, y dos tramos de distinta distribución deben dar **inestable**.
**Aplicada en:** `unidad_minima_05b_paralelo.py` (`_ee`, `_estable`, `ALFA_E18`), con sus cuatro mutantes corridos.

## E-23 · Separar estratos por posición en el fichero en vez de por identidad
**Clase:** instrumento · **Veces que saltó:** 0 · *el estrato se derivó de la posición en el fichero*
**26-oct-2026, Fase 1 (error de Opus).** Para separar los dos estratos de n=8 —prefijo canónico y tramo esparcido— corté la lista de filas en la posición 6566. Mal por dos motivos a la vez: 6566 era el total de filas **incluyendo** los mundos inertes, y en orden esparcido los índices altos **vienen entremezclados** con los bajos, así que el orden del fichero ya no es el orden del recorrido. Resultado: «tramo esparcido: 0 sistemas» y un estrato de prefijo contaminado. El corte correcto es por **rango** (`idx // k`).
**Por qué.** Se usó una propiedad del fichero (el orden de escritura) para recuperar una propiedad del experimento (a qué tramo pertenece el sistema), justo después de haber cambiado deliberadamente el orden de escritura.
**Severidad:** alta si no se detecta (habría informado los dos estratos mezclados, que es exactamente lo que el paquete prohibía).
**Firma (cómo se detecta):** un estrato sale vacío o con un tamaño que no cuadra con lo que el corredor informó; o la suma de los estratos no da el total.
**Guarda** `[MECÁNICA]`: la pertenencia a un estrato se deriva de un **campo de la fila** (`idx`, `n`, o un campo explícito), nunca de la posición en el fichero ni del orden de llegada. Y se comprueba con una aserción: los estratos **suman** el total y ninguno está vacío si el corredor dijo que lo llenó.
**Aplicada en:** `unidad_minima_05e_transitorios.py` (corte por `idx // k8`) y en los análisis de estructura y de escala.

## E-24 · Generalizar una invariancia más allá del rango medido
**Clase:** criterio · **Veces que saltó:** 0 · *una invariancia enunciada sin su rango*
**26-oct-2026, Fase 1 (error de Opus).** Con la primera variante de cobertura —una letra más de vida, factor 2,5— concluí y escribí que la fracción no determinada es «**invariante a la longitud de la vida**». Luego n=8, que vive **71 veces** la vida de n=3, mostró 20 puntos más de identificación a igual `n_min`, y tuve que dudar de mi propia conclusión y volver a medir a factor 5. (La conclusión se sostuvo: a factor 5 no se mueve ni un decimal. Pero eso no la salva: la había afirmado sin derecho.)
**Por qué.** Una invariancia medida en un factor 2,5 se enunció como invariancia sin rango. El enunciado no llevaba el rango en el que se midió.
**Severidad:** media (la conclusión resultó cierta; el modo de afirmarla era injustificado y pudo haber ido al cierre como ley).
**Firma (cómo se detecta):** una afirmación de invariancia, monotonía o ausencia de efecto **sin el rango** del parámetro en que se midió; o un resultado posterior en otro punto del rango que la contradice.
**Guarda** `[PREGUNTA → punto 11, puerta]`: toda afirmación de invariancia o de ausencia de efecto se escribe **con el rango medido** («invariante entre 258 y 642 pasos», no «invariante a la longitud»), y el cierre no la extiende fuera de ese rango sin medirlo. Si el rango es menor que un orden de magnitud, se dice.
**Aplicada en:** `APERTURA_ESCALADO_SIN_AZAR.md`, segunda variante de cobertura, con su rango declarado.

## E-25 · Umbral absoluto para comparar cosas de escala distinta
**Clase:** instrumento · **Veces que saltó:** 0 · *un umbral absoluto comparado entre escalas distintas*
**26-oct-2026, Fase 1 (error de Opus).** Medí la transitoriedad de un estado como «visitado **≤ 2 veces** en la vida» y comparé ese porcentaje entre n=3 (vida de 258 pasos) y n=8 (vida de 18 434). Con 71 veces más vida, el mismo umbral absoluto mide otra cosa: en n=8 un estado visitado dos veces es 1 500 veces más raro que en n=3. La diferencia aparente (0,6 % frente a 17,6 %) era en parte artefacto del umbral.
**Por qué.** Se comparó una cantidad acotada por un número fijo entre poblaciones cuya escala difiere en dos órdenes de magnitud.
**Severidad:** baja (lo detecté antes de informarlo, y con umbral relativo el efecto resultó **más** nítido, no menos).
**Firma (cómo se detecta):** un umbral en unidades absolutas aplicado a series cuya longitud, duración o tamaño difiere en más de un factor 2; o un porcentaje que cambia de orden de magnitud justo donde cambia la escala.
**Guarda** `[MECÁNICA]`: todo umbral que se compara entre poblaciones de escala distinta se expresa **relativo a la escala de cada población** (fracción de la media, cuantil, tasa por paso), y se informa junto al absoluto para que se vea cuánto aporta el umbral.
**Aplicada en:** la medida de transitoriedad relativa (visitas < 10 % de la media del propio sistema).

## E-26 · Un patrón de `pkill` que coincide con el propio proceso
**Clase:** banco · **Veces que saltó:** 0 · *un patrón de pkill que coincidió con su propia shell*
**26-oct-2026, Fase 1 (error de Opus).** Para matar un análisis usé `pkill -f 05e_transitorios`. El patrón coincidió también con **mi propia shell**, cuya línea de órdenes contenía el nombre del script, y el comando se mató a sí mismo antes de ejecutar la edición que venía después. La edición se perdió en silencio y sólo lo noté porque comprobé que había llegado.
**Por qué.** `pkill -f` compara contra la línea de órdenes completa, y la línea de órdenes del propio shell contiene el patrón.
**Severidad:** baja (coste: una edición perdida y un turno).
**Firma (cómo se detecta):** un comando con `pkill -f` devuelve un código de salida raro (143/144) y lo que venía después del `;` no se ejecutó.
**Guarda** `[MECÁNICA]`: matar por **PID** obtenido antes (`pgrep` filtrando el propio `$$`), no por patrón; y nunca poner un `pkill -f` seguido de más trabajo en el mismo comando. Si se usa patrón, comprobar después que el trabajo posterior llegó a ejecutarse.

**Ampliación del 28-oct (el mismo patrón, pero al OBSERVAR en vez de al matar).** La guarda cubría matar y no cubría **preguntar**. Para saber si una campaña seguía viva usé `pgrep -f unidad_minima_10_maestro`, que coincidió con la **línea de órdenes del envoltorio** —el `bash -c` que contenía los nombres de los dos scripts— y respondió «sigue corriendo» sobre un programa que **todavía no había arrancado**. Con eso leí un fichero de salida vacío como «la corrida no produjo nada» y estuve a punto de diagnosticar un fallo inexistente; además `ps` muestra los saltos de línea de un comando como espacios, lo que hizo parecer que dos órdenes encadenadas eran una sola. Dos falsos síntomas de la misma causa.
**Guarda ampliada** `[MECÁNICA]`: para esperar o comprobar un proceso propio, **por PID** (`kill -0 $pid`), nunca por patrón; y un fichero de salida vacío **no es** evidencia de que el programa falló mientras su PID siga vivo —la evidencia es el PID y el código de salida—. Para leer una línea de órdenes con varias órdenes, `tr '\0' '\n' < /proc/$pid/cmdline`, no `ps`.

## E-27 · Muestra 1-de-k cuyo paso comparte factores con la estructura del espacio
**Clase:** instrumento · **Veces que saltó:** 0 · *el paso de la muestra compartía factores con la base*
**26-oct-2026, Fase 1 (error de Opus). El error más caro de la fase.** El banco se indexa como `2n` dígitos en base `n`, y la submuestra se tomó como `range(0, total, k)` con `k` elegido por ser un número redondo del presupuesto de reloj: **k = 20 000** para n=6 y **k = 10¹⁰** para n=8. Esos pasos comparten factores con el espacio, así que la muestra no recorre el banco: recorre un **retículo** con dígitos bajos clavados.

Demostrado de las dos formas, aritmética y empírica:
- **n=8**: `k = 10¹⁰ = 2¹⁰·5¹⁰` y `2¹⁰ = 1024 = 2·8³`, así que **todo índice es múltiplo de 8³** y los tres últimos dígitos base-8 son 0. Eso clava `B[5] = B[6] = B[7] = 0` en los **28 148** sistemas, y deja `B[4]` con 4 de 8 valores. **4 de 16 entradas de las tablas restringidas.**
- **n=6**: `20 000 mod 6 = 2`, así que el último dígito base-6 es `2r mod 6` y `B[5]` sólo toma `{0, 2, 4}`. **1 de 12 entradas restringida**, con la mitad de sus valores.
- **n=3 y n=4**: bancos **completos**, sin muestreo. Limpios.

Consecuencia medida: con tres de los ocho estados mandando a 0 bajo B, los mundos de n=8 colapsan hacia el estado 0 y son estructuralmente más simples. Eso explica las dos anomalías que no sabía explicar — que n=8 identificara **20 puntos por encima** de n=6 a igual `n_min`, y que su tasa fuera **plana** en `n_min` (76–82 % de `n_min`=2 a 8) en vez de decreciente.
**Por qué.** `k` se eligió por el reloj (cuántos sistemas caben en el presupuesto) y nadie comprobó su relación aritmética con la base del espacio. La norma de la casa dice «enumeración canónica, no muestreo aleatorio», y yo cumplí la letra —el muestreo es determinista— rompiendo el motivo: ser representativo.
**Severidad:** **alta.** Invalida n=8 como estimación de su banco y pone un asterisco en n=6. No toca n=3 ni n=4, que son completos, ni la ley de reversibilidad, que se sostiene sobre 1 200 sistemas de banco completo.
**Firma (cómo se detecta):** una estratificación sale **plana** donde debería tener gradiente; o un n se sale de una tendencia que los demás respetan; o `mcd(k, base)` > 1.
**Guarda** `[MECÁNICA]`: toda submuestra de un espacio indexado por dígitos comprueba, **antes de correr**, que cada posición de dígito recorre **todos** sus valores a lo largo de la muestra (una aserción de 10 líneas sobre mil rangos repartidos por todo el conjunto, no sobre los primeros mil: los dígitos altos salen fijos por efecto de prefijo y eso es un falso positivo). Si alguna posición queda restringida, se cambia el paso. Preferible: tomar la muestra por **inversión de bits del rango** sobre el conjunto entero en vez de por paso multiplicativo.
**Aplicada en:** pendiente — obligatoria antes de cualquier submuestra de 1-bis.

---

## E-28 · El supervisor relayó a Wis una interpretación del ejecutor sin reproducirla
**Clase:** banco · **Veces que saltó:** 0 · *el supervisor relayó una interpretación sin reproducirla*
**25/26-oct-2026 (error de Fable).** Opus analizó los 24 mundos de n=4 con futuro < 1 y escribió que la palabra separadora tiene longitud 7 y «la vida se quedó una letra corta». Yo se lo transmití a Wis como hecho. Reproducido el 26-oct con L = 7: **sólo 6 de los 24 se identifican**. Opus ya había retractado la lectura en su ficha (E-24); yo no la había verificado antes de repetirla.
**Por qué.** Una interpretación causal plausible, con un número al lado, se tomó por medida. Es E-12 en el rol de supervisor.
**Severidad:** baja en medida (nada entró a un entregable), media en confianza: Wis recibió una afirmación falsa con tono de hecho.
**Firma (cómo se detecta):** una frase causal del ejecutor («se quedó corta», «es por X») reaparece en un mensaje del supervisor sin un número propio ni la marca «sin verificar».
**Guarda** `[PREGUNTA → cada revisión]`: el supervisor no transmite a Wis una interpretación causal del ejecutor sin reproducirla con un cómputo propio o sin marcarla explícitamente como «lectura de Opus, no verificada». Lo que sí puede transmitir sin reproducir son cifras con su comando (E-12).
**Lección que vale más que el error:** una palabra separadora presente en la vida **no es experiencia** si no se ejecuta desde el estado que discrimina. Es la razón exacta de la clase recurrente y de la Fase 2.

## E-29 · Salida por tubería que almacena, y un tope de reloj que la borra
**Clase:** banco · **Veces que saltó:** 0 · *salida por tubería que almacena, borrada por un tope*
**26-oct-2026, n=8 limpio (error de Opus).** Lancé el paso de mutantes como `python3 … | tail -30` con un `timeout 2400`. El paso tardaba más de 40 minutos, el `timeout` lo mató, y **`tail` no había entregado una sola línea**: la salida de 40 minutos de cómputo se perdió entera y no supe ni por dónde iba.
**Por qué.** Dos cosas a la vez: `tail` —como `head`, `sort` o `grep` sin `--line-buffered`— no entrega nada hasta que el proceso termina, y un proceso que va a morir por tope **no termina**; y además la función escribía a un `StringIO` que sólo se volcaba al final. Y de fondo: puse el tope sin estimar el coste, cuando un mutante que ejecuta el aprendiz completo cuesta una vida entera y a n=8 una vida son 18 434 pasos.
**Severidad:** baja en medida, media en coste (40 min de máquina y un turno).
**Firma (cómo se detecta):** un proceso largo cuya salida está vacía mientras corre; o un código de salida 143/124 con cero líneas útiles.
**Guarda** `[MECÁNICA]`: todo proceso que pueda durar más que su tope escribe **directo y con `flush()`** —`python3 -u`, `out.flush()` tras cada hito— a un fichero, y **nunca** a través de `tail`, `head` o `sort`. Antes de poner un tope se estima el coste del paso contra la longitud de la vida.
**Aplicada en:** `unidad_minima_07_n8_limpio.py`: salida a `sys.stdout` con flush por hito, lanzado con `python3 -u`, y los mutantes partidos en caros (capacidad, 20 mundos) y baratos (instrumento, 200), con el motivo del tamaño declarado en el código.

## E-30 · Verificar sobre una lista vacía y leer el «ninguno» como confirmación
**Clase:** banco · **Veces que saltó:** 0 · *se verificó sobre una lista vacía y se leyó como éxito*
**26-oct-2026, n=8 limpio (error de Opus).** Para probar que añadir la máquina serializada a `un_sistema` no cambiaba ninguna cifra, comparé «150 filas de n=4»… tomadas de las **primeras 200 líneas del JSONL, que son todas de n=3**. El filtro quedó vacío, el bucle no se ejecutó ni una vez, y el mensaje «campos viejos que difieren: NINGUNO (150 sistemas de n=4)» era una **cadena escrita por mí**, no un resultado. Un falso verde perfecto. Lo delató un `NameError` posterior: la variable del bucle no existía porque el bucle nunca corrió.
**Por qué.** El mensaje de éxito llevaba el tamaño de muestra **escrito a mano** en vez de contado, así que era incapaz de delatar una muestra vacía. Es el patrón de la fixtura vacía que el registro ya conoce en otra forma, aplicado a una verificación en vez de a un test.
**Severidad:** alta como clase (una verificación que no puede fallar no verifica), baja en consecuencia aquí porque se detectó y se repitió bien: 150 sistemas de n=4 comparados de verdad, ningún campo viejo distinto.
**Firma (cómo se detecta):** un informe de verificación cuyo tamaño de muestra es una constante del texto y no una variable contada; o una comprobación que pasa en cero iteraciones.
**Guarda** `[MECÁNICA]`: toda verificación **cuenta** lo que comparó, lo imprime **desde la variable**, y **asevera que el recuento es mayor que cero** antes de declarar nada. Un «ninguno» sin su recuento al lado no es un resultado.

## E-31 · Salida a fichero, pero en un directorio que no sobrevive a la sesión
**Clase:** banco de trabajo · **Veces que saltó:** 0 · *la custodia de la salida se puso en el temporal de la sesión*
**26-oct-2026, n=8 limpio (error de Opus). Es E-29 otra vez, en la variante que mi propia guarda no cubría.** Tras perder cuarenta minutos de salida por una tubería, escribí la guarda «salida **a fichero**, nunca a una tubería que un tope pueda cortar». Y acto seguido lancé los mutantes de n=8 y el encadenado de la corrida real escribiendo a ficheros… **en el directorio temporal de la sesión**. La sesión se cortó, el temporal se vació (0 bytes), y perdí: la salida cruda de los mutantes —incluido el M-5 enmendado, que no llegó a terminar—, el guion del encadenado, y el paso que debía **escribir los resultados en la ficha**. De todo aquello sólo sobrevive lo que había citado en la conversación.
**Por qué.** La guarda nombraba el **mecanismo** malo (la tubería) en vez de la **propiedad** que importa (que la salida dure más que el proceso). Un fichero en un temporal de sesión es tan efímero como una tubería para este fin, así que cumplí la letra de mi propia guarda rompiendo su motivo. Es el mismo patrón que E-27, donde cumplí «muestreo determinista, no aleatorio» rompiendo el motivo, que era ser representativo.
**Severidad:** media. No contamina ninguna medida —no se midió nada—, pero tiró el paso de mutantes de n=8 y dejó sin cumplir el requisito explícito del paquete: «mutantes corridos **y escritos en la ficha** antes de la corrida real».
**Firma (cómo se detecta):** la ruta de salida empieza por `/tmp`, `/var/tmp`, `/dev/shm` o contiene `scratchpad`; o una pregunta sobre un resultado de hace horas no se puede contestar porque su fichero ya no está.
**Guarda** `[MECÁNICA]`: `salida_a_fichero()` deja de ser sólo preventiva y **también detecta**: levanta excepción si la ruta está en un directorio efímero, y exige `permitir_efimero=True` explícito para lo verdaderamente desechable. Con sus dos mutantes: detecta `/tmp/...` y deja pasar una ruta del árbol. Regla corta: **lo que no dura más que el proceso no es salida, es humo.**
**Aplicada en:** `guardas.py` en este árbol y en el modelo portátil de `~/Documentos/modelo-errores-y-guardas/`.

**Lección de método, que vale más que la entrada:** dos de mis guardas fallaron por nombrar el mecanismo en vez de la propiedad. Al escribir una guarda hay que preguntarse **qué propiedad quiero garantizar**, no **qué forma de hacerlo mal he visto**: la segunda deja la puerta abierta a la siguiente forma.

## E-32 · Un paso de pruebas sin tope, que bloquea la puerta que protege
**Clase:** instrumento · **Veces que saltó:** 0 · *las pruebas tenían menos guardas que lo que validan*
**27-oct-2026, n=8 limpio (error de Opus).** El paso de mutantes estuvo **4 h 24 min de CPU masticando un solo mundo** y no escribió ni una línea de avance. La campaña no arrancó en toda la noche, porque la puerta —correctamente— no deja correr lo real hasta que los mutantes pasen. Cero filas medidas.
**Por qué, en dos capas.** La inmediata: al enmendar el criterio de M-5 necesitaba saber si la traza fuerza dos estados, y lo resolví con un **aprendiz completo con búsqueda** sobre 200 mundos de ocho estados. Convertí el bucle que había declarado «barato» en el más caro de todos, y la enmienda de un criterio me rompió el coste. La de fondo, que es la que importa: **la campaña tenía tope por sistema y tope de sesión, y lo que valida la campaña no tenía ninguno.** Puse guardas en el experimento y dejé sin guardas al instrumento que lo autoriza.
**Y era innecesario.** La pregunta no requiere búsqueda: una traza es consistente con un solo estado si y sólo si cada letra produce siempre la misma reacción. Una pasada sobre la vida, O(T), en vez de una búsqueda exponencial. El coste venía de no haber pensado la pregunta, no del problema.
**Severidad:** alta en coste de oportunidad. No contamina ninguna medida —no se midió nada—, y eso es justamente el daño: una noche entera de máquina y de espera por cero filas.
**Firma (cómo se detecta):** un paso de pruebas sin avance mientras su CPU crece; o un bucle declarado «barato» en el comentario que tarda más que el que se declaró caro; o una enmienda de criterio que añade una llamada con búsqueda donde antes no había ninguna.
**Guarda** `[MECÁNICA]`: **todo paso de validación lleva los mismos topes que lo que valida** — tope por elemento (120 s por mundo aquí, con SIGALRM) y salto declarado del elemento que lo pase, contándolo en el denominador. Y un criterio extra en la propia puerta: «quedaron suficientes elementos evaluables tras el tope». Al enmendar un criterio se vuelve a estimar su coste antes de relanzar: **una enmienda es código nuevo y se calibra como código nuevo.**
**Aplicada en:** `unidad_minima_07_n8_limpio.py` (`TOPE_MUTANTE_S = 120`, el predicado en una pasada, y el criterio «quedaron mundos evaluables tras el tope»).

## E-33 · Subir una implicación a bicondicional sin medir la recíproca, teniendo el contraejemplo en la propia tabla
**Clase:** criterio · **Veces que saltó:** 0 · *se midió un sentido y se afirmaron los dos*
**27-oct-2026, informe para revisión externa (error de Opus).** Medimos «la vida admite una máquina menor ⇒ el mundo tiene un transitorio estructural» al 100 % en todos los estratos de dos bancos completos. En el informe externo lo escribí como **bicondicional** (`⟺`), lo llamé «identidad», y además «nuestro resultado más fuerte». La recíproca es falsa. La refutó un revisor externo con un contraejemplo mínimo —`A` manda todo a 1, `B` identidad: hay transitorio y la vida exige dos estados— que verifiqué por ejecución. **Y la refutaba mi propia tabla, tres líneas más arriba del párrafo donde escribí «exactamente»:** el 24 % de los mundos *identificados* con `n_min`=2 tiene transitorio, e «identificado» es precisamente «no admite una máquina menor».
**Por qué.** Un 100 % en una dirección se siente como una equivalencia, y no lo es. No busqué la recíproca porque el número era limpio; y no leí mi propia tabla contra mi propia frase.
**Severidad:** alta. Fue a un informe externo como el resultado principal, y lo derribó el primer lector.
**Firma (cómo se detecta):** una afirmación con «⟺», «identidad», «exactamente» o «si y sólo si» cuyo apoyo es un porcentaje de una sola dirección; o una tabla del propio documento que contiene filas de la clase complementaria con valores distintos de cero.
**Guarda** `[PREGUNTA → punto 11, puerta]`: toda implicación que se quiera enunciar en los dos sentidos exige **las dos mediciones, cada una con su número**, y declara qué fracción de la clase complementaria falsaría cada dirección. `[MECÁNICA]`: antes de escribir «⟺» en un entregable, buscar en el propio documento una fila que lo refute — aquí había una.
**Aplicada en:** `INFORME_PARA_REVISION_EXTERNA.md` §4, corregido en el sitio a `M ⇒ T` con el contraejemplo escrito.

## E-34 · Decir «no existe» por «no hemos encontrado», y aceptar la cita que lo corrige sin verificarla
**Clase:** criterio · **Veces que saltó:** 1 · *dos errores opuestos sobre la misma frase, en el mismo día*
**27-oct-2026, informe para revisión externa (error de Opus).** Escribí que reutilizar lo adquirido «**no se ha demostrado en ningún sistema** del desarrollo» y que la línea «**fue abandonada** hacia 2008». Las dos frases son más anchas que su fuente: Guerin 2008 habla de **los trabajos que él revisa**, y la línea tiene continuaciones posteriores. Es E-12 exacto. Y al corregirlo cometí el error simétrico: **acepté la cita que me lo corregía sin comprobarla**, de palabra. Después la busqué y existe —Lagriffoul, *Frontiers in Neurorobotics* 16:836767, 2022, `10.3389/fnbot.2022.836767`, basada en esquemas, que es la línea de Drescher—, así que la corrección se sostiene; pero el momento en que la escribí no lo sabía.
**Por qué.** Una afirmación de ausencia es la más fácil de escribir y la más difícil de sostener, y la prisa de corregirla invita a aceptar cualquier contraejemplo que llegue. Las dos direcciones del error tienen la misma causa: no comprobar.
**Severidad:** media. Ninguna medida afectada; una afirmación insostenible en un informe externo y una cita adoptada a crédito.
**Firma (cómo se detecta):** las palabras «nadie», «ningún», «no existe», «abandonado» en un entregable; o una cita que entra al documento **para corregir** otra afirmación y no tiene DOI al lado.
**Guarda** `[MECÁNICA]`: toda afirmación de ausencia se escribe «no hemos encontrado», con **las búsquedas y las fuentes consultadas** al lado; y toda cita que corrige una afirmación nuestra se verifica **antes** de escribirla, con DOI o URL. La guarda vale en las dos direcciones: ni afirmar la ausencia sin buscar, ni retirarla sin comprobar.
**Aplicada en:** §7 del informe externo, reescrito; y el gate de la Fase 2, que lista las búsquedas de hoy y sus fuentes.

## E-35 · Guarda que mide la importación en vez del uso, y que se caza a sí misma
**Clase:** instrumento · **Veces que saltó:** 1 · *«sin azar» dejó de ser verificable sin que nada fallara*
**27-oct-2026 (error de Opus, detectado por revisión externa).** La guarda de determinismo (E-07) comprobaba `"random" in sys.modules` y los artefactos empezaron a registrar «random importado: **SÍ**». Ninguna línea nuestra llama a `random`: lo importa `statistics` —que yo mismo añadí para el cuantil normal del umbral consciente del ruido— y también `tempfile`. Comprobar la importación mide a **las dependencias**; lo que hay que medir es si **nosotros** usamos azar. Con eso, la afirmación «determinista» había dejado de ser verificable y ninguna prueba lo señaló.
**Y la corrección falló primero.** La escribí con una expresión regular sobre el texto fuente y **se cazó a sí misma**: encontró `import random` dentro de una cadena de su propio mutante. Un falso positivo hace que una guarda se acabe ignorando, que es peor que no tenerla. Reescrita sobre el árbol sintáctico: 13 módulos, **cero usos**.
**Por qué.** Es la tercera vez que una guarda mía falla por **nombrar el mecanismo en vez de la propiedad**. «No importes random» nombra un mecanismo; «no uses azar» nombra la propiedad. Antes: «no uses tuberías» dejó la puerta abierta al directorio temporal (E-29/E-31), y «no muestrees al azar» la dejó abierta al retículo (E-27). El patrón es el error, no los tres casos.
**Severidad:** media. No contamina ninguna medida —no hay azar—, pero convirtió en indemostrable la propiedad central del programa.
**Firma (cómo se detecta):** un campo del artefacto que afirma lo contrario de lo que el documento declara; una guarda cuyo enunciado empieza por «no uses *tal herramienta*» en vez de «garantiza *tal propiedad*»; o una guarda que falla sobre su propio fichero.
**Guarda** `[MECÁNICA]`: `sin_azar_usado()` analiza el **AST** de nuestros módulos y busca importaciones y accesos a `random`, no texto. Con dos mutantes: detecta el uso real y **no** se queja de que una dependencia lo importe. Y la regla general, que es la que vale: **al escribir una guarda, enunciar la propiedad que se garantiza, no la forma de hacerlo mal que se acaba de ver** — y hacer que el mutante ataque la propiedad.
**Aplicada en:** `guardas.py` en este árbol y en el kit portátil de `~/Documentos/modelo-errores-y-guardas/`.

## E-36 · Trabajar contra un documento vivo sin comprobar su versión
**Clase:** banco de trabajo · **Veces que saltó:** 0 · *escribí un gate entero contra una receta que ya había cambiado*
**27-oct-2026 (error de Opus).** Leí `ORIENTACIONES_FASE_2_RECETA.md`, escribí el gate de antecedentes de la Fase 2 completo, y al releer el fichero resultó que ya no era el mismo: llevaba una **corrección de Wis que regía todo el documento** —el criterio deja de ser económico («abarata») y pasa a ser de desarrollo («amplía»)—. Mi gate preguntaba por el ahorro en el sitio donde debía preguntar por el alcance, y la frontera con la literatura de transferencia estaba trazada por el eje equivocado. Hubo que realinearlo entero.
**Y no es la primera vez hoy.** El registro fue editado en paralelo tres veces mientras trabajaba: E-18, E-19 y E-28 ya estaban tomados por entradas ajenas y estuve a punto de duplicar los números. Y casi reescribí `unidad_minima_08_fase2.py`, que ya existía con 23 KB y pilotos corridos, porque el paso 3 de la receta me mandaba crearlo.
**Por qué.** Estos documentos son vivos y compartidos entre tres roles, y yo los trataba como una entrega fija. Leer no es lo mismo que leer **ahora**.
**Severidad:** media. Trabajo rehecho, y el riesgo real de sobrescribir trabajo ajeno.
**Firma (cómo se detecta):** un documento compartido cuya marca de tiempo o hash es posterior al momento en que se leyó; un número de entrada ya ocupado; un fichero que la tarea manda crear y ya existe.
**Guarda** `[MECÁNICA]`: antes de empezar un trabajo derivado de un documento compartido, **registrar su hash**, y volver a comprobarlo antes de dar el trabajo por terminado; si cambió, releer antes de entregar. Antes de crear un fichero que una orientación pide, **comprobar que no existe**; si existe, es de otro rol y se pregunta. Y los números del registro se piden releyendo el fichero, nunca de memoria.
**Aplicada en:** pendiente de mecanizar; hoy aplicada a mano (releí la receta y realineé el gate antes de seguir).

## E-37 · El supervisor se saltó su rol y escribió el experimento sin ficha, sin mutantes y sin gate
**Clase:** criterio · **Veces que saltó:** 1 · *demostrar en vez de orientar, y pagar con los errores que el proceso evita*
**27-oct-2026 (error de Fable).** Wis dijo que yo lo estaba limitando y que no le daba avance. En vez de orientar, escribí `unidad_minima_08_fase2.py` y lo corrí: sin ficha de apertura, sin paso de mutantes, sin gate de antecedentes para el mecanismo que acabé añadiendo (olvido por fracaso). Cometí E-38 y E-39 en la primera hora, los dos del tipo que la plantilla y los mutantes atrapan antes de correr. Wis lo señaló: «se te saltaron las trancas… lo tuyo es discusión, dar orientaciones».
**Por qué.** La presión de «no avanzamos» la leí como «hacé», cuando el rol dice «orientá mejor». Es la misma falla que E-19 con signo contrario: allí me fui a proceso cuando tocaba experimento; aquí me fui a ejecutar cuando tocaba orientar. En los dos casos dejé de leer el encargo real.
**Severidad:** media. El prototipo tiene valor como evidencia exploratoria, pero no es entregable y Fable cuesta caro; y rompió la separación de roles que hace verificable el trabajo (quien orienta no debería ser quien corre).
**Firma (cómo se detecta):** un fichero `.py` nuevo cuyo autor es el supervisor; una corrida sin ficha previa en el árbol; un mecanismo nuevo que aparece primero en el código y después en los documentos.
**Guarda** `[CONDUCTA]`: cuando Wis diga «no avanzamos», la respuesta del supervisor es **una orientación más concreta** (qué construir, qué predice, qué lo falsa), no código. Si el supervisor cree que hace falta demostrar algo con código, lo **pide** y lo ejecuta Opus. Lo que hoy existe se traspasa: ver `ORIENTACIONES_FASE_2_TRASPASO.md`.
**Aplicada en:** este registro y en la memoria del supervisor (`limitarse-a-la-orientacion`).

## E-38 · Un bit nuevo que, por construcción, no influía en la salida
**Clase:** instrumento · **Veces que saltó:** 1 · *la clase componible entera quedó descartada y nadie lo predijo*
**27-oct-2026 (error de Fable, atrapado por el primer piloto).** W₂ se definió como W₁ más un bit b que se **conmuta** en una situación (x*, a*). La conmutación no depende del valor de b, y la salida es el bit de cambio del par: así que la salida nunca depende de b y el bit es **inobservable**. El filtro «n_min(W₂) > n_min(W₁)» descartó las 24 familias componibles del piloto y el 100 % de lo corrido fue la clase control. El diseño que yo mismo escribí en la receta («se toma la primera regla que hace a b distinguible desde la salida») lo exigía y no lo implementé.
**Por qué.** Pasé del documento al código sin la ficha, que obliga a escribir «qué hace observable a la distinción nueva» antes de correr. Corregido: el bit es un **cerrojo** (se pone en (A, x_s), se quita en (B, x_r)), cuya dinámica sí depende de b.
**Severidad:** alta si no se hubiera visto: el experimento habría comparado heredar en un mundo sin nada nuevo que heredar.
**Firma (cómo se detecta):** una clase experimental con 0 familias tras el filtro; una cantidad de la definición del mundo que no aparece en ninguna salida.
**Guarda** `[MECÁNICA]`: en el generador de familias, afirmar antes de correr que para cada patrón **existe** al menos un W₁ cuyo W₂ pasa el filtro, y abortar si una clase entera queda vacía (`no_vacio` de `guardas.py` sobre la lista de familias por clase).
**Aplicada en:** pendiente en `unidad_minima_08_fase2.py` (hoy el filtro descarta en silencio y sólo informa el conteo).

## E-39 · Matar a la unidad cuando agota el presupuesto, y leer su silencio como incapacidad
**Clase:** instrumento · **Veces que saltó:** 2 · *«la heredera no identifica» era «la heredera dejó de vivir»*
**27-oct-2026 (error de Fable, atrapado por el segundo piloto).** El bucle de vida hacía `break` al agotarse el presupuesto de búsqueda. La heredera, que arrastra la memoria del mundo viejo, lo agotaba en los primeros pasos de W₂ en el 100 % de las celdas (12/12, luego 21/21 y 44/44 con ventana de 512), y su curva de alcance quedaba plana en 0,05 **porque ya no vivía**, no porque no pudiera aprender. Lo leí como «la heredera se ahoga» y era «yo la ahogo».
**Por qué.** El presupuesto es una guarda del banco (que la celda termine), y lo puse dentro de la fisiología (que la unidad deje de existir). Un ser que no logra explicar no se detiene: sigue viviendo con lo que tiene. La corrección convirtió el agotamiento en un **disparador interno de olvido** (conservar los últimos 64 pasos y empezar sobre ellos), y con eso la heredera identifica el 95–100 %.
**Severidad:** alta. Habría cerrado la Fase 2 con «heredar no sirve» sobre un artefacto del instrumento.
**Firma (cómo se detecta):** una curva perfectamente plana desde el primer hito; un brazo con «agotó» = 100 % y estados = tope; cualquier `break` en un bucle de vida.
**Guarda** `[MECÁNICA]`: el bucle de vida **no tiene salidas**: recorre todos los pasos del presupuesto de vida en todo brazo; cualquier límite de cómputo se resuelve **dentro** de la unidad con una regla declarada (olvido, tope de estados) y se cuenta. Mutante obligatorio: una unidad a la que se le quita el mecanismo de olvido debe reproducir el ahogo (si no lo reproduce, el ahogo no era lo que creímos).
**Aplicada en:** `unidad_minima_08_fase2.py` (el bucle ya no corta; `agotado` pasó a contar `olvidos`); el mutante está pedido en el traspaso y no corrido.

## E-40 · Hash copiado de la terminal de una corrida previa, no del artefacto de la que se lanzó
**Clase:** banco de trabajo · **Veces que saltó:** 1 · *un hash equivocado casi me hace tirar un artefacto válido*
**27-oct-2026 (error de Fable; la guarda la aporta Opus).** El traspaso de la Fase 2 registraba el prototipo con sha256 `359d5ff1…` «al lanzar»; en disco había `621c0534…`. Lo perseguí porque un fichero modificado **después** del lanzamiento habría roto la procedencia de los 10 MB que la campaña estaba escribiendo. No era el caso: el mtime (16:50:25) es **anterior** al arranque del proceso (16:52:02), así que el código que corría era el de disco. El hash se había copiado de la salida de un piloto anterior a la última edición y no se recalculó al lanzar.
**Por qué.** Un hash en un documento es una afirmación sobre un artefacto, y se copió de una terminal en vez de leerse del artefacto que la corrida de verdad escribió.
**Severidad:** media. Ninguna medida afectada; la consecuencia posible era desconfiar de un artefacto válido y tirar 43 minutos de campaña. El riesgo simétrico es peor: un hash que coincidiera por casualidad con una versión vieja **ocultaría** una procedencia de verdad rota.
**Firma (cómo se detecta):** el hash de un documento no coincide con el del fichero en disco; o un hash aparece en prosa sin que exista un artefacto de esa corrida que lo contenga.
**Guarda** `[MECÁNICA]`: todo hash que entre en un documento se copia del **campo `sha256_codigo` del artefacto que la propia corrida escribió**, nunca de una terminal previa. Y al heredar una corrida ajena se comprueban **tres cosas, no una**: hash del fichero, **mtime del fichero frente a la hora de arranque del proceso**, y que el pid viva. El mtime es lo único que distingue «el hash del documento está mal» de «el fichero se tocó y la procedencia está rota»: sin él los dos casos se ven igual.
**Aplicada en:** traspaso corregido con el hash bueno; instantánea en `artifacts/procedencia/`.

## E-41 · Varias sustituciones y una sola escritura: una aserción fallida tira el trabajo bueno
**27-oct-2026 (error de Opus).** Para corregir el cierre de la Fase 1 escribí un guion con cuatro sustituciones y **una sola escritura al final**. La segunda aserción falló —apuntaba a un ancla de §8 que yo buscaba en §6— y el fichero **no se escribió nunca**, así que se perdió también la primera, que sí había acertado. Peor: el commit que venía detrás en la misma orden **sí se ejecutó**, y su mensaje describía con detalle una corrección que el commit no contenía.
**Por qué.** Un lote de ediciones con una sola escritura es todo-o-nada, y lo encadené con un commit que no comprobaba si el lote había funcionado. Es la misma forma del error que ya tengo registrado como falso verde: afirmar en prosa algo que el artefacto no respalda.
**Severidad:** alta en credibilidad. El mensaje de un commit es la custodia del trabajo; uno que afirma lo que no contiene es peor que no commitear.
**Firma (cómo se detecta):** un guion de edición con varios `assert` y un único `write_text` al final; o un mensaje de commit que menciona un cambio que `git show` no muestra.
**Guarda** `[MECÁNICA]`: una sustitución, **una escritura** — si falla la tercera, las dos primeras ya están guardadas; cada una informa «hecho» o «no encontrado» por separado y ninguna aborta las demás. Y **nunca** encadenar un commit detrás de un lote de ediciones en la misma orden: primero se comprueba que el lote llegó, luego se commitea.
**Aplicada en:** la función `sustituir()` con la que se aplicó esta corrección, que escribe tras cada una e informa de cada una.

## E-42 · EL SUPERVISOR ESCRIBIÓ UNA ORIENTACIÓN CON TRES AFIRMACIONES MÁS FUERTES QUE SUS FUENTES, Y LAS ATRAPÓ UN REVISOR EXTERNO
**Clase:** criterio · **Veces que saltó:** 1 (y es la **tercera** del mismo patrón: E-33, E-34, E-42) · *orienté a Opus con teoremas que no dicen lo que dije que decían*
**Severidad:** **ALTA.** Una orientación es el documento que fija qué se construye y qué se predice. Tres afirmaciones falsas en ella habrían entrado a la ficha de la Fase 2 como «lo que la literatura garantiza», y la ficha habría preregistrado como teorema lo que es hipótesis. Es el error más caro del programa porque **se multiplica**: lo lee Opus, lo hereda la ficha, lo cita el cierre.

**28-oct-2026 (error de Fable, detectado por la revisión externa de `ORIENTACIONES_FASE_2_MAESTRO.md`).** Escribí, en el paquete que da entrada al maestro:
1. **«El FAIL de coste de la Fase 1 es el precio de no tener maestro»**, citando Angluin 1987 y Kearns–Valiant 1994. Falso como se escribió: Angluin usa consultas de **pertenencia y equivalencia con reset**; Kearns–Valiant prueban dureza del aprendizaje **pasivo** en su modelo PAC. Ninguna de las dos dice nada de nuestro modelo (una traza, sin reset). Nuestro FAIL es el coste del mínimo exacto desde una traza pasiva (Gold 1978, Angluin 1978, Pitt–Warmuth 1993). Que un maestro lo cure aquí es **hipótesis**, y yo la escribí como **resultado**.
2. **«Sólo los autómatas de permutación se aprenden sin maestro»**, citando Rivest–Schapire vía Bender 1998. Falso: la frase de Bender es sobre **los algoritmos de Rivest–Schapire**, y el propio Bender–Slonim 1994 muestra que dos robots cooperantes aprenden grafos fuertemente conexos sin maestro, y Bender 1998 que uno con guijarros también. Generalicé una observación sobre un algoritmo a una afirmación sobre lo que es posible.
3. **«Dimensión de enseñanza medida»** para lo que es el coste empírico de un maestro concreto. Goldman–Kearns 1995 definen una medida combinatoria sobre la clase; le puse el nombre de un concepto formal a un contador.

**Y las tres tienen el mismo origen.** Escribí la orientación **desde el journal y la memoria**, sin reabrir una sola fuente, dos horas después de haber registrado como error de Opus (E-33, E-34) exactamente esto: subir una implicación a más de lo que dice, y afirmar en general lo que la fuente afirma en particular. Lo tenía delante y lo repetí. Wis lo dijo con precisión: «anota en grande tus grandes errores».

**Por qué.** (a) Las citas de memoria **suenan** igual que las verificadas y nadie las distingue en el texto. (b) Cuando una fuente apoya la dirección que quiero, dejo de leerla con el rigor con que leo la que me contradice. (c) Un paquete de orientación no pasa por ficha ni mutantes, así que **nada mecánico lo revisa antes de que Opus lo lea**: es el documento con menos guardas y más consecuencias del programa. (d) El revisor externo lleva **tres de tres**: la verificación adversarial que el método exige no la estamos haciendo nosotros.

**Firma (cómo se detecta):** una frase de la forma «X demuestra que nuestro Y es Z» donde X no fue escrita sobre nuestro modelo; un «sólo», «siempre», «nadie», «es el precio de» apoyado en una cita; un nombre de concepto formal aplicado a un contador propio; una cita en un documento de orientación **sin nivel de evidencia al lado**.

**Guarda** `[MECÁNICA]`: **toda cita en un documento de orientación, gate o cierre lleva su nivel de evidencia en la misma línea** (SOURCE-VERIFIED con fecha de lectura, LITERATURE-CLAIM, o HIPÓTESIS cuando la fuente se aplica a un modelo distinto del nuestro); una cita sin nivel invalida el documento para Opus, que debe devolverlo sin ejecutarlo. **Y toda afirmación que use una fuente para explicar un resultado nuestro** se escribe en dos frases separadas: «la fuente dice A en su modelo» / «en el nuestro, B es hipótesis que prueba la celda C». `[CONDUCTA]`: antes de entregar una orientación, el supervisor **relee cada cita contra el texto o el resumen verificado del informe** (no contra el journal ni la memoria) y marca las que no pudo releer. `[PREGUNTA → punto 0 de la ficha]`: «¿qué afirmaciones de la orientación que la motiva son HIPÓTESIS y cuáles SOURCE-VERIFIED?»; si la orientación no lo dice, la ficha no se escribe.
**Aplicada en:** `ORIENTACIONES_FASE_2_MAESTRO.md` (las tres frases corregidas en el sitio con fecha, y el nivel al lado de cada fuente). Pendiente: aplicar la misma pasada a `ORIENTACIONES_FASE_2_RECETA.md` y a `ORIENTACIONES_FASE_2_TRASPASO.md`, que se escribieron con el mismo método y **nadie ha revisado cita por cita**.

## E-43 · Pedir literatura sin mirar la biblioteca de la casa
**Clase:** banco de trabajo · **Veces que saltó:** 1 · *pedí a Wis que bajara lo que en parte ya tenía curado*
**28-oct-2026 (error de Fable, señalado por Wis: «revisa ahí, parece que te estás quedando atrás»).** Escribí `LITERATURA_PENDIENTE.md` con 30 fuentes a bajar sin abrir `/home/wis/Documentos/teoria de la inteligencia/`: 329 ficheros, 103 PDF, con manifiestos, SHA-256, procedencia y 21 afirmaciones validadas. Allí estaban ya Ashby 1960 (la ultraestabilidad que la fase de viabilidad necesita), Harlow 1949 (el experimento original de «lo vivido amplía lo siguiente»), Derex 2025 (la instrucción canaliza la exploración, con signo), PAIRED/ACCEL/POET (la escalera operativa), Hartmanis 1962 (la matemática exacta de nuestras cascadas, bajada por Wis el 27-sep), Wolf 2008 y Mitchell 2009 (memoria y anticipación en bacterias), y toda la capa autopoiética que el informe de literatura había marcado como hueco.
**Por qué.** El informe de literatura se construyó desde cero con búsqueda web y ni él ni yo consultamos el inventario propio; el registro ya tenía la regla para RNFE (inventario antes de releer) y no la apliqué a la literatura. Es la misma falla que E-42 con otro objeto: lo que no está en mi contexto inmediato lo trato como inexistente.
**Severidad:** media. Tiempo de Wis pedido en vano y, peor, orientaciones escritas sin la capa de viabilidad que ya estaba en casa.
**Firma (cómo se detecta):** una lista de fuentes a bajar sin una columna «¿está en el corpus? id»; un gate que cita por autor y año sin identificador TI-/ADOA-/HEA-/X/HD-/H-/WORLD-REF-/SCI-.
**Guarda** `[MECÁNICA]`: todo gate de antecedentes y toda lista de literatura lleva la columna **«en el corpus de Wis: id»**, llenada con `grep -ril` sobre los manifiestos (`SOURCE_PROVENANCE_v0.3.local.csv`, el manifiesto ADOA dentro de su ZIP, `corpus_v2/manifest/V2_MANIFEST.csv`, `CORPUS_MANIFEST.csv` de SCI) **antes** de marcar nada como «bloqueado» o «por bajar». Una fuente del corpus se lee de su PDF o `extracted_text`, nunca de memoria. `[PREGUNTA → punto 0 de la ficha]`: «¿qué fuentes del corpus de Wis aplican a esta ficha y con qué id?».
**Aplicada en:** `LITERATURA_PENDIENTE.md` §0 (28-oct). Pendiente: la misma columna en `PRIOR_ART_FASE_2.md` y en el gate del maestro.

## E-44 · Un mutante que no puede saltar: `trace[-0:]` es la traza entera
**Clase:** instrumento · **Veces que saltó:** 1 (atrapado antes de medir) · *el mutante de «olvido total» habría conservado todo*
**28-oct-2026 (error de Opus, atrapado al escribirlo).** El mutante M-a de la Fase 2 es «olvido total: núcleo = 0». La forma barata de hacerlo era poner la constante `NUCLEO = 0` del módulo de Fable, porque su `_olvidar` hace `nucleo = self.trace[-NUCLEO:]`. Con `NUCLEO = 0` eso es `self.trace[-0:]`, que **es la traza completa**, no la vacía: el mutante habría conservado **todo** y habría pasado la puerta sin probar nada, informando «el olvido total no da la misma curva» sobre una unidad que no olvidó.
**Por qué.** Cambiar una disposición a su valor extremo **no** garantiza el comportamiento extremo: la aritmética del índice negativo invierte el sentido. Y el mutante que no puede saltar es indistinguible del mutante que pasa: los dos imprimen PASS.
**Severidad:** alta en credibilidad, nula en coste. Un mutante inerte es peor que no tener mutante, porque da un verde.
**Firma (cómo se detecta):** un mutante que se implementa poniendo una constante a 0, a 1 o a infinito, sin una comprobación de que su efecto ocurrió; dos corridas (mutante y referencia) cuyos **contadores de actividad son idénticos**.
**Guarda** `[MECÁNICA]`: todo mutante informa un **contador de actividad propio** y la puerta compara mutante contra referencia en ese contador, no sólo en el resultado; si el contador coincide, el veredicto es **NULO POR INACTIVIDAD**, nunca PASS. Aquí: M-a se escribió como clase aparte (`UnidadMa`) con su olvido explícito, y M-b informa `pasos_elegidos` del mutante y de la referencia (28,8 contra 3,1: el mutante actuó).
**Aplicada en:** `unidad_minima_09_fase2.py` (`UnidadMa`, y el informe de `pasos_elegidos` por brazo en los dos lados de M-b).

## E-45 · «Idéntico en todo» incluyendo registros acumulados que llegan heredados por construcción
**Clase:** criterio · **Veces que saltó:** 1 (en la primera corrida de prueba, antes de medir) · *el mutante falló por contabilidad y no por defecto*
**28-oct-2026 (error de Opus).** Los mutantes M-e y M-f de la Fase 2 exigen «dar **exactamente** F1». Lo implementé comparando **todos** los campos de la fila. M-f —que hereda la máquina y la ignora— reprodujo F1 en las diecisiete **medidas** y difirió en `refutaciones`, que es el contador acumulado de la vida en W₁ y llega heredado por construcción (en el brazo C1 de 08 igual). El mutante salió FAIL sin que hubiera ningún defecto.
**Por qué.** «Exactamente igual» no es un criterio hasta que dice **en qué campos**. Un contador acumulado no es una medida del experimento: es registro, y el registro de la vida anterior viaja con la herencia a propósito. El riesgo del otro lado es peor: ampliar la lista de campos ignorados **después** de ver fallar el criterio es lavar un fallo.
**Severidad:** media. Un criterio que falla por contabilidad gasta el crédito del que falla por defecto.
**Firma (cómo se detecta):** un criterio de igualdad escrito sobre `dict == dict` o sobre «todos los campos»; una lista de campos ignorados que **crece después** de la primera corrida.
**Guarda** `[MECÁNICA]`: la fila se parte en dos conjuntos **declarados antes de comparar** —`MEDIDAS` (lo que la puerta exige idéntico) y `REGISTROS` (se **imprimen siempre** con su diferencia y no deciden)—, y el informe muestra los dos cubos aunque uno esté vacío, para que nada se esconda. Ampliar `REGISTROS` después de una corrida exige una enmienda prospectiva fechada en la ficha.
**Aplicada en:** `unidad_minima_09_fase2.py` (`REGISTROS` y `difieren()`, que devuelve `medidas` y `registros` por separado); §10 de `APERTURA_FASE_2_ACUMULACION.md`, donde el resultado de M-f informa los dos.

## E-46 · Un canal de un bit y un cálculo que necesita leer la hipótesis del otro: el encargo pedía las dos cosas
**Clase:** criterio · **Veces que saltó:** 1 (atrapado al construir, antes de la corrida pareada) · *la celda habría sido vacía por construcción y se habría leído como resultado*
**28-oct-2026 (defecto de `ORIENTACIONES_FASE_2_DOS_UNIDADES.md`, de Fable, hallado por Opus al construir).** La orientación pide que entre las dos unidades cruce **un bit por paso** («las dos declaran su predicción antes de actuar; es la señal mínima») y, en la misma sección, que la maestra dé «la palabra más corta en la que, **según H_m**, la predicción de U_a falla». Para calcular eso la maestra necesita **leer la hipótesis del alumno** en situaciones que el alumno no ha vivido, que es incomparablemente más que un bit. Y con el bit solo, la palabra más corta donde la predicción del alumno falla es **la letra que el alumno ya iba a tomar** (si discrepan en ella, esa letra es una palabra de longitud 1 y el orden shortlex la elige): **medido**, longitud 1 en el 100 % de las intervenciones y la misma letra en 7 de 9, con la celda reproduciendo F1 curva por curva. La celda habría salido «la maestra no enseña» cuando lo que pasó es que el instrumento no podía enseñar.
**Por qué.** Dos requisitos de una orientación pueden ser incompatibles sin que ninguno de los dos suene mal por separado. Y el que construye tiende a implementar la letra de cada frase en vez de comprobar que las frases se pueden cumplir juntas. Añadido: el disparo —**cuándo** interviene el maestro— no estaba contado como parámetro, y resultó ser **lo que decide si enseñar sirve**: con el disparo que no espera al desacuerdo local, el alumno identificó en el hito 64 donde la vara necesitó 128.
**Severidad:** alta. Una celda vacía por construcción produce un FAIL creíble sobre la pregunta central del programa («¿puede una unidad enseñar a otra?»).
**Firma (cómo se detecta):** una orientación que fija a la vez el **ancho del canal** y un **cálculo** que lo excede; una celda cuyas intervenciones son todas de longitud 1; una celda de tratamiento cuyas medidas coinciden **campo por campo** con la vara (coincidencia exacta = defecto, no resultado nulo).
**Guarda** `[MECÁNICA]`: toda celda con un canal entre dos partes declara **el ancho del canal como parámetro** y corre al menos dos valores, y el informe trae por celda la **distribución de longitud de palabra** y la fracción `palabra_igual_a_la_letra`; si esa fracción es 1,0 la celda es **NULA POR CONSTRUCCIÓN**, no negativa. Además, la versión literal del encargo se conserva como mutante (`M-literal`) para que su vacuidad quede **medida y no afirmada**. `[PREGUNTA → punto 0 de la ficha]`: «¿el canal declarado alcanza para calcular lo que la celda pide calcular?».
**Aplicada en:** `unidad_minima_10_maestro.py` (parámetros `canal` y `disparo`, contadores `longitud_k` y `palabra_igual_a_la_letra`, celda `M-literal`) y §13.2 de `APERTURA_FASE_2_ACUMULACION.md`.

## E-47 · Dos unidades deterministas idénticas con la misma entrada no pueden cooperar
**Clase:** criterio · **Veces que saltó:** 1 (atrapado antes de la corrida pareada) · *la pareja cooperativa no cruzó ni un bit en 3 586 pasos*
**28-oct-2026 (defecto de `ORIENTACIONES_FASE_2_DOS_UNIDADES.md`, de Fable, hallado por Opus al medir).** La celda de la pareja pide «dos frescas que se enseñan mutuamente». Puestas las dos en el **mismo** sitio del mundo leyendo la **misma** corriente de letras, construyen la misma hipótesis paso a paso, **nunca discrepan** y no tienen nada que enseñarse: 0 intervenciones y 3 586 contraejemplos imposibles. La celda habría informado «cooperar no sirve».
**Por qué.** En el programa no hay azar —y eso está bien—, así que la diversidad entre dos unidades **no aparece sola**: hay que ponerla, y ponerla es una decisión de diseño que se declara. Los dos robots de Bender–Slonim 1994 cooperan porque están en **vértices distintos** del grafo; la cooperación vive de la asimetría, no de la cantidad.
**Severidad:** alta, y con una consecuencia de programa: si la pareja sale plana, «la población de muchos» se descarta por un artefacto.
**Firma (cómo se detecta):** una celda con dos o más agentes deterministas cuyos contadores de interacción están en **0**; dos agentes con la misma clase, el mismo estado inicial y la misma entrada.
**Guarda** `[MECÁNICA]`: toda celda con más de un agente declara **de dónde sale la asimetría** (posición en el mundo, itinerario, momento de arranque) y la puerta exige `intervenciones > 0`; con 0, el veredicto es **NULO POR SIMETRÍA**. La versión simétrica se conserva como mutante (`M-pareja-simetrica`) y debe dar exactamente 0 intervenciones, que es su forma de demostrar que la guarda vigila algo real.
**Aplicada en:** `unidad_minima_10_maestro.py` (la segunda unidad arranca en otro vértice del mundo y con el itinerario desplazado un paso; mutante `M-pareja-simetrica`) y §13.2 de `APERTURA_FASE_2_ACUMULACION.md`.

## E-48 · «Doble corrida con hash» dentro de un mismo proceso no comprueba el determinismo
**Clase:** instrumento · **Veces que saltó:** 1 · *las dos corridas de la misma campaña en dos procesos distintos dieron textos distintos*
**28-oct-2026 (error de Opus, y es de método, no de una línea).** Desde la Fase 0 todos los módulos cierran con «doble corrida con hash»: se corre `main()` dos veces, se compara el sha256 de las dos salidas y se informa IDÉNTICAS. Las dos corridas pasan **en el mismo proceso**. Al correr la campaña confirmatoria de C5 dos veces en **procesos distintos**, los textos **difirieron**: todas las cifras medidas eran iguales, y lo que cambió fue el **orden de las claves** de un diccionario impreso (el informe de `difieren()`). Python aleatoriza la semilla de hash de las cadenas **por proceso**, así que el orden de iteración de un `set` o un `dict` de cadenas es estable dentro de un proceso y no entre dos. La comprobación que llevamos tres fases informando como «determinismo» comprobaba sólo que el cálculo no usa azar; **no** que la salida sea reproducible mañana en otra corrida.
**Por qué.** La prueba se escribió para cazar `random`, y para eso sirve. Pero el enunciado que se publicó —«dos corridas producen un hash»— es más fuerte que la prueba, y nadie lo notó porque la prueba siempre pasó. Es el patrón de E-42 en el instrumento en vez de en una cita: afirmar un poco más de lo que la comprobación comprueba.
**Severidad:** media-alta en credibilidad. Un hash de salida que no es reproducible entre procesos no sirve de custodia, que es para lo que lo pusimos.
**Firma (cómo se detecta):** dos corridas de la misma campaña en dos procesos cuyos `diff` difieren **sólo en el orden** de los elementos de una colección; una salida que imprime un `dict`, un `set` o un `Counter` sin ordenar.
**Guarda** `[MECÁNICA]`: (a) **toda colección se ordena antes de imprimirse o de entrar en un hash** (`sorted(d.items())`, nunca `str(dict)`); (b) la doble corrida se hace en **dos procesos separados** —o se declara `PYTHONHASHSEED` y se registra en el artefacto—, y la comparación se hace por `diff` de los dos ficheros, no por un hash calculado dentro del mismo proceso.
**Aplicada en:** pendiente de aplicar a `unidad_minima_09_fase2.py` y `10_maestro.py` en cuanto terminen sus campañas (no se edita un módulo mientras su campaña corre: ver E-49); la comparación de las dos corridas de C5 ya se hizo por `diff` entre procesos y así se detectó.

## E-49 · El hash del código leído al terminar la corrida no es el del código que corrió
**Clase:** instrumento (custodia) · **Veces que saltó:** 2 el mismo día · *el artefacto registró el sha256 de un fichero editado después de arrancar*
**28-oct-2026 (error de Opus, dos veces en una hora).** Todos los módulos cierran con `sha256(open(__file__,'rb').read())` **al final** de la corrida. Edité el módulo mientras su campaña estaba en marcha —dos veces: una corrección de una firma y el control A↔B— y el artefacto quedó con el hash del fichero **editado**, no del que el intérprete había cargado al arrancar. La primera vez tiré una corrida de 249 s para rehacerla con el fichero bueno; la segunda ocurrió igual en la corrida de reemplazo. Y es peor de lo que parece, porque un módulo que **importa** a otro (10 importa a 09) informa también el hash del importado, así que editar 09 corrompe la procedencia de la campaña de 10.
**Por qué.** El momento en que el intérprete lee el fichero (importar) y el momento en que el programa lo hashea (terminar) son distintos, y entre los dos hay horas de campaña. Es la misma familia que E-40 —un hash que no viene de donde dice— pero por un hueco de tiempo en vez de por copiarlo de la terminal.
**Severidad:** alta en custodia, nula en ciencia. Las cifras eran correctas; lo que quedaba mal era la prueba de qué código las produjo, que es justo lo que el hash existe para demostrar.
**Firma (cómo se detecta):** `git diff`/`stat` muestran el fichero modificado **después** de la hora de arranque de la corrida; o el hash del artefacto no coincide con el del fichero en el commit que se custodia.
**Guarda** `[MECÁNICA]`: el sha256 del propio fichero y de los módulos importados se calcula **en el cuerpo del módulo, al importarse**, no al terminar; se guarda en una constante y es ésa la que entra en el artefacto. Y el artefacto registra además la **hora de arranque**, para que `stat` pueda desmentirlo. `[CONDUCTA]`: **no se edita un módulo mientras una campaña que lo usa —directa o por importación— está corriendo.** Si hay que editarlo, se para la campaña por PID y se relanza.
**Aplicada en:** pendiente en `09` y `10` (ver E-48); la nota de procedencia de la ficha de la Fase 2 dice qué corridas tienen el hash desfasado y por qué.

## E-50 · UN NULO LEÍDO COMO NEGATIVO PORQUE EL TECHO ESTABA EN EL TRATAMIENTO, NO EN LA MEDIDA — Y LA FICHA YA TENÍA LA GUARDA QUE LO IMPEDÍA
**Clase:** criterio · **Veces que saltó:** 1 · *informé «heredar la máquina no compra nada» sobre un banco donde la herencia no tenía dónde mostrarse*
**Severidad:** **ALTA.** Es la conclusión central de la Fase 2 y la que decide si Genesis tiene algo que guardar. Un nulo mal leído como negativo cierra una línea de trabajo que no se ha probado.

**28-oct-2026 (error de Opus, detectado por Fable al revisar la corrida contra los artefactos).** Informé el resultado de C5 como «**en este banco heredar no vale más que vivir**» y añadí «**para Genesis todavía no hay nada que guardar** por herencia de máquina». Las cifras eran correctas y la doble corrida también. La lectura, no: **lo que C5 hereda es la máquina de W₁, y a la unidad fresca identificar W₁ le cuesta una mediana de 18 pasos** —verificado por mí, independientemente: n=174, mínimo 2, mediana 18, p75 23, p90 28, p95 45, máximo 67; **171 de 174 mundos antes del paso 64**—. La primera medida de la curva está en el **hito 64**. Así que lo máximo que la herencia podía ahorrar son ~18 pasos de los 64 que pasan **antes de la primera medición**: el experimento **no podía detectar** un efecto de la herencia. Y las curvas de C5 y F1, idénticas desde el hito 128, dicen lo mismo desde el otro lado: lo que cuesta en W₂ es el **cerrojo nuevo**, que ninguna herencia puede traer; la parte heredada es la parte gratis.

**El veredicto correcto es `NULO POR TECHO DEL DISEÑO`**, no negativo: en un banco donde vivir cuesta 18 pasos, heredar no puede valer más que vivir. Y no autoriza ninguna frase sobre Genesis.

**Por qué.** (a) La saturación que vigilaba la ficha era la del **resultado** (¿llegan todos los brazos al 100 %?), y aquí el resultado no estaba saturado —F1 da 0,642 en el hito 64—. El techo estaba en el **tratamiento**: en cuánto vale lo que se hereda, no en cuánto se alcanza. Son dos techos distintos y yo sólo tenía nombre para uno. (b) Un falsador preescrito da una sensación de rigor que **no sustituye** a preguntar si el diseño puede producir el efecto que busca: el falsador se cumplió, y aun así la celda no medía lo que decía. (c) **Y la peor parte: la ficha ya tenía la guarda.** Su puerta §11 incluye «**(g) No saturación:** en el hito 64 hay varianza entre brazos por encima del ruido; si no, **NULO por saturación**». Los cuatro brazos dieron 0,642 / 0,644 / 0,642 / 0,642 — la guarda habría saltado. **No la implementé en el programa** (`puerta()` de `09` evalúa (a), (b), (c), (e) y (f), y se saltó (d) y (g)), así que el veredicto lo escribí yo en prosa en vez de calcularlo el programa, que es justo lo que la ficha dice que debe pasar: «el veredicto lo calcula el programa leyendo esos campos».

**Firma (cómo se detecta):** los brazos de una celda difieren entre sí **menos que el ruido** en el punto donde la ficha dijo que se decidía; una conclusión negativa cuyo tratamiento aporta algo que el control consigue **antes de la primera medición**; una puerta cuyo código evalúa **menos criterios** de los que la ficha enumera.

**Guarda** `[MECÁNICA]`, tres partes:
1. **Precondición del banco, antes de correr:** toda celda que compare «con X» contra «sin X» mide primero **cuánto le cuesta al control conseguir X por su cuenta**, y exige que ese coste sea **mayor que el primer punto de medición**. Si no lo es, la celda es `NULA POR TECHO DEL DISEÑO` y **no se corre** hasta cambiar el banco o los puntos de medición. Aquí: `coste_w1_fresca` (mediana y p90 del primer paso desde el que la fresca identifica W₁) entra en el artefacto y se compara con `min(HITOS)`.
2. **La puerta del programa implementa TODOS los criterios que la ficha enumera**, y el informe lista los criterios de la ficha que el código **no** evalúa; si falta uno, el veredicto es inválido. (Comprobación barata: contar las letras de la puerta en la ficha y en el código.)
3. **Varianza entre brazos** en el punto de decisión: si el rango entre brazos no supera el umbral de z ajustado, `NULO`, nunca negativo.

**Ampliación del 28-oct, de la celda de adquisición, y es una lección sobre cómo LEER un nulo.** Esa celda dio los cuatro brazos con curvas **idénticas dígito a dígito** en los siete hitos, incluido el lesionado. Lo llamé «firma de defecto» y fui a medir: **me equivoqué**. La herencia **no** estaba borrada antes del primer hito (de 6–8 transiciones heredadas sobrevivían 1–5 en el paso 64, y los olvidos no empezaban hasta el 128–256), y los brazos **sí** diferían —en `estados` (5,71 contra 5,93) y en `exactitud` del hito 64 (0,9139 contra 0,8897)—. Lo que pasaba es que la medida **binaria** (`identifica`) no separa lo que la **graduada** sí ve, con 28 familias. El nulo era un nulo, y además **falto de potencia**.
**Guarda** `[MECÁNICA]`, cuarta parte: un nulo **no se interpreta, se descompone**, y hacen falta tres números en el mismo informe: (i) la medida **graduada** junto a la binaria —si la graduada separa y la binaria no, el problema es la sensibilidad y no el mecanismo—; (ii) **cuánto del tratamiento sobrevive en el primer punto de medición** (si ~0, nulo antes de empezar); (iii) el **tamaño de muestra y si alcanza** para el umbral ajustado — con 28 familias, «no se separan» y «no puedo verlo» son indistinguibles, y hay que decir el segundo.
**Aplicada en:** `unidad_minima_09_fase2.py` (criterios (d) y (g) implementados, `coste_w1_fresca` medido y comparado con el primer hito, y la lista de criterios de ficha no evaluados) y el §Resultado de `APERTURA_FASE_2_ACUMULACION.md`, reescrito con la distribución de 18 pasos **como la explicación** y el veredicto cambiado a nulo por techo.

## E-51 · Truncar un bloque shortlex deja un futuro que mide una esquina del mundo — el retículo de la Fase 1, en otro sitio
**Clase:** instrumento · **Veces que saltó:** 2 (las dos antes de medir: una por lectura, una por la guarda) · *el futuro fijo de W₃ cubría 3 de 64 prefijos*
**28-oct-2026 (error de Opus, atrapado al construir la celda de adquisición).** El futuro fijo con el que se juzga si una unidad identificó W₃ (12 estados) necesita palabras de longitud 12; hay 4 096 y concatenarlas da 49 152 pasos, impagable por celda. Lo truncé a los **primeros 2 048 pasos del bloque shortlex**. Eso son las 170 primeras palabras de longitud 12, y **todas empiezan por ocho A**: medido, cubrían **3 de los 64** prefijos de seis letras. Con ese futuro una máquina de **3 estados «identificaba» un mundo de 12** y los cuatro brazos salían idénticos. Es **exactamente** el error E-27 de la Fase 1 —el paso de muestra que comparte factores con la base y recorre un retículo— en otro objeto: truncar un bloque shortlex clava las letras de orden **alto** igual que aquel paso clavaba los dígitos **bajos**.
**Y el intento de arreglo falló también, y lo cazó la guarda.** Reemplacé el prefijo por la permutación de **bits invertidos** —la herramienta del recorrido esparcido de la Fase 1— y `muestreo_verificado` abortó: tomar un **prefijo** de un orden de bits invertidos clava las posiciones espejadas (las cuatro altas, en 0). La permutación esparce un **recorrido**, no una **muestra**: un prefijo suyo sigue siendo un retículo. Lo que sirve es un **paso multiplicativo coprimo** con el tamaño del espacio, y **el paso se elige buscando el primero que pasa la comprobación**, no por redondo.
**Por qué.** La lección de E-27 estaba registrada como «la muestra del banco», no como «cualquier submuestra de un espacio indexado por dígitos», que es lo que de verdad dice. Una guarda escrita sobre el objeto donde dolió no se aplica sola al objeto siguiente. Y el síntoma era agradable: todos los brazos coincidían y las cifras eran altas (0,99 de exactitud), que es como se ve un instrumento ciego.
**Severidad:** alta. Habría dado «la organización heredada no sirve para aprender lo nuevo» con un futuro que no mide el mundo.
**Firma (cómo se detecta):** un futuro, una vida o una muestra obtenidos por `[:K]` sobre un bloque shortlex o sobre cualquier orden derivado de los dígitos; una máquina con muchos menos estados que el mínimo verdadero del mundo que aun así «identifica»; todos los brazos con la misma curva y exactitud alta.
**Guarda** `[MECÁNICA]`: **ninguna submuestra de un espacio indexado por dígitos se toma por prefijo**, ni del orden natural ni de una permutación; se toma con paso multiplicativo coprimo y **pasa `muestreo_verificado` antes de usarse**, con el nombre del objeto en el mensaje. Y la comprobación se aplica al **futuro fijo y a la vida**, no sólo a la muestra del banco. Añadido al punto 0 de la ficha: «¿qué submuestras usa esta celda y cuál de ellas pasó `muestreo_verificado`?».
**Aplicada en:** `unidad_minima_11_adquisicion.py` (`futuro_de`, con el paso buscado por comprobación y la guarda dentro de la función, así que no se puede usar el futuro sin verificarlo).

## E-52 · Todos los `n_min` del programa se miden desde el estado 0, y en la Fase 2 la unidad no empieza en el 0
**Clase:** instrumento · **Veces que saltó:** 1 (antes de leer resultados) · *el banco «difícil» que la unidad enfrentaba era trivial*
**28-oct-2026 (error de Opus, hallado al construir la celda de adquisición).** `alcanzables(A, B)` de `unidad_minima_05_banco.py` arranca siempre en el **estado 0**, y con ella `verdad`, `n_min` y todas las clases de dificultad del programa. En la Fase 1 eso era correcto: la vida empieza en el 0. En la Fase 2 **no**: la unidad entra a W₂ donde W₁ la dejó, y a W₃ donde W₂ la dejó. Y la Fase 1 **ya había medido** que estos mundos tienen transitorios estructurales —puertas de ida sin vuelta, el resultado `M ⇒ T`—, así que desde el punto de entrada lo alcanzable puede ser mucho menor. Resultado medido en la primera corrida de la celda: un banco seleccionado por tener `n_min(W₃)` entre 6 y 8 **desde el estado 0** daba brazos que terminaban con **2,35 estados** y «identificaban» con exactitud 0,9994. Difícil en el papel y trivial en la mano. Al medir la dificultad **desde el punto de entrada**, el coste de W₃ para la unidad fresca subió de 64 a **512 pasos de mediana**, ocho veces el primer hito.
**Por qué.** Una función correcta en la fase donde se escribió deja de serlo cuando cambia el supuesto que la hacía correcta —aquí, «la vida empieza en el estado 0»—, y nada avisa: `alcanzables(A, B)` no pide un estado inicial, así que no hay sitio donde el error se note. Es la misma forma que E-23 (el estrato se derivó de la posición en el fichero y no de un campo de la fila): un dato se toma de donde es cómodo y no de donde significa.
**Severidad:** alta. Decide qué mundos entran al banco, o sea de qué habla el experimento.
**Firma (cómo se detecta):** una unidad que «identifica» un mundo con **menos estados que el mínimo verdadero**; una medida de dificultad calculada sin decir **desde dónde**; un banco cuyos brazos convergen mucho antes de lo que su `n_min` haría esperar.
**Guarda** `[MECÁNICA]`: toda medida de dificultad lleva **el estado desde el que se calcula** en su nombre y en el artefacto (`n_min_w3`, `n_min_w3_desde_0`, `n_min_desde_futuro`, `estados_alcanzables_desde_x3`), y la selección del banco usa la del **punto de entrada de la unidad**. Y la comprobación que ata las dos: **si un brazo identifica con menos estados que el mínimo verdadero desde donde predice, el veredicto es `NULO POR FUTURO CIEGO`** —falla el instrumento, no el brazo—. Las cifras `n_min` de la Fase 2 anteriores a esto (en `08`, `09` y `10`) son desde el estado 0 y **no** describen la dificultad que la unidad enfrentó: sus comparaciones entre brazos siguen valiendo, porque todos los brazos entran por el mismo punto, pero ninguna frase sobre «mundos de n estados» en esas corridas es sobre lo que la unidad vivió.
**Aplicada en:** `unidad_minima_11_adquisicion.py` (`alcanzables_desde`, `verdad_desde`, la selección en dos etapas y la guarda del futuro ciego, que pasó: 0 celdas de 28 por debajo del mínimo).

## E-53 · «Caro» mezclaba el coste del mundo con el coste del olvido — y yo lo vi y lo escribí como coincidencia
**Clase:** criterio · **Veces que saltó:** 1 · *la puerta que elige el banco de la Fase 3 medía en un tercio de los casos un defecto de disposición, no la dificultad del mundo*
**Severidad:** **ALTA.** Esa puerta elige el banco madre de la Fase 3. Con el banco mal elegido, la herencia se mediría contra una unidad que se ahoga y el resultado hablaría del olvido y no de heredar.

**28-oct-2026 (error de Opus, detectado por Fable recomputando sobre mis propias filas).** La puerta del mundo caro marca un mundo como «caro» si la unidad tarda más de 256 pasos en identificarlo o no lo identifica. Pero la unidad que mide es la de 08, **con ventana de 512 y olvido por fracaso**. Recomputado: en n=8, de **462** mundos caros, **445 tienen olvidos > 0**, y el promedio es **86 olvidos por vida en los caros contra 0,2 en los baratos** (en n=6, 144 de 179). Así que «caro» estaba midiendo, en buena parte, **que esta unidad se ahoga**, no que el mundo sea difícil de identificar.

**Y lo peor del error no es el error: es que yo lo tenía delante.** Cerré el informe anterior escribiendo «la coincidencia con el otro hallazgo no es casual — a n=8 la unidad acumula 31,7 olvidos por vida, el mismo número que vi en W₃». Lo llamé **coincidencia** y era la **causa**. Tenía el número, lo puse en la frase, y no lo convertí en una columna.

**Por qué.** Una sola palabra —«caro»— para dos magnitudes distintas (el mundo, y el mundo *para este organismo con esta disposición*) y una sola columna donde hacían falta dos. Es la misma forma que E-45 (medidas y registros en un solo cubo) y que E-50 (el techo del tratamiento confundido con el techo del resultado): **un nombre que tapa dos cosas**. Y la señal de alarma estaba disponible y sin mirar: el contador de olvidos ya venía en la fila.

**Un tercer factor que ni el encargo ni yo habíamos separado,** y que aparece al cruzar: los dos costes se medían con **criterios distintos** —el exacto de la Fase 1 por **isomorfismo** con la mínima verdadera, el de la unidad por **predecir un futuro fijo**—. Medido en el cruce 1:1 de los 1 182 mundos: **614 mundos que el identificador exacto NO resuelve, la unidad los da por identificados.** El futuro fijo es criterio **necesario y no suficiente**, y comparar las dos columnas con criterios distintos habría dado una diferencia que no es de coste sino de vara.

**Firma (cómo se detecta):** una etiqueta booleana («caro», «difícil», «degradado») cuyo nombre no dice **para quién**; una partición en la que el contador de un órgano del propio instrumento (olvidos, topes, reintentos) está fuertemente asociado a la etiqueta; dos columnas que se comparan sin comprobar que usan **el mismo criterio de éxito**.
**Guarda** `[MECÁNICA]`, tres partes:
1. **Toda etiqueta de dificultad se mide dos veces y se informa en dos columnas:** el **coste intrínseco** (con el identificador exacto, sin ventana y sin olvido) y el **coste para esta unidad con esta disposición**; más la columna derivada `caro_solo_por_el_olvido`. El banco se elige **por la primera**.
2. **Las dos columnas usan el MISMO criterio de éxito** —isomorfismo con la mínima verdadera—, y si una usa un criterio más débil, se dice en la misma línea.
3. **Al partir por una etiqueta, se informa el contador de actividad del instrumento en los dos lados** (aquí, olvidos por vida en los caros y en los baratos). Si difiere en más de un orden de magnitud, la etiqueta está midiendo el instrumento.
**Aplicada en:** `unidad_minima_12_mundo_caro.py` (columnas `coste_mundo`/`mundo_resuelto`/`caro_por_el_mundo` frente a `coste_barato`/`caro`, más `caro_solo_por_el_olvido` y `banco_madre`), y en el cruce 1:1 por índice con las 5 000 filas limpias de n=8 de la Fase 1, que queda como **verificación** de la columna nueva y no como su fuente.

## E-54 · Relanzar una campaña sobre el fichero de una corrida ya completa la borra
**Clase:** banco de trabajo (custodia) · **Veces que saltó:** 1 · *perdí 2 807 filas de n=8 ya medidas*
**29-oct-2026 (error de Opus).** Al añadir la columna del coste intrínseco relancé `unidad_minima_12_mundo_caro.py` con la misma ruta de salida. La campaña abre su `.jsonl` en modo `"w"`, así que **las 2 807 filas de n=8 de la corrida anterior —completa y ya analizada— se borraron** en el primer `write`. Las cifras que había extraído de ellas están en el informe; **las filas no se pueden recomputar sin volver a correr**.
**Por qué.** La guarda que existe (`salida_a_fichero`) vigila que el destino no sea efímero, no que **ya tenga algo dentro**. Y lo peor: **una hora antes había hecho lo correcto** con la campaña del maestro (la archivé como `..._prefix.jsonl` antes de relanzar) y no apliqué el mismo cuidado aquí. El patrón estaba en mi mano y no lo convertí en guarda.
**Severidad:** media. No se perdió ciencia —el coste intrínseco de n=8 está completo en las 5 000 filas de `07`, que es mejor cobertura que la muestra de `12`—, pero sí trabajo de cómputo y la posibilidad de recomputar la columna del olvido sobre esos mundos.
**Firma (cómo se detecta):** un relanzamiento con la misma ruta de salida que una corrida anterior **completa**; un `.jsonl` cuya cuenta de filas **baja** entre dos miradas.
**Guarda** `[MECÁNICA]`: antes de escribir, si la ruta existe y **no está vacía**, la campaña **archiva** el fichero anterior con la hora de su última modificación en el nombre (`..._YYYYmmdd-HHMM.jsonl`) y lo dice en la salida; nunca lo sobrescribe. Se añade a `salida_a_fichero` como comprobación propia, para que valga en todas las campañas y no sólo en ésta.
**Aplicada en:** `guardas.py` (`salida_a_fichero`, archivado automático) y por tanto en 07, 09, 10, 11 y 12 a la vez.

## E-55 · Una coordenada que depende de la historia del agente, dentro del símbolo que debe explicar: el mundo deja de ser identificable
**Clase:** criterio · **Veces que saltó:** 1 (antes de concluir nada) · *el alcance salió 0,000 en todas las generaciones de todas las celdas, y tenía que salir*
**29-oct-2026 (error de Opus, en el primer piloto de TRES).** La orientación de la Fase 3 pide que la variable esencial V «entre en lo observado como coordenada». Lo implementé metiéndola en el símbolo que la unidad lee para construir su hipótesis: `simbolo = (cambio, banda(V))`. **Alcance 0,000 en las cinco generaciones de las cinco celdas**, y es lo único que podía pasar: la banda de V depende de la **historia del actor** —cuántas veces pisó δ⁻, cuántas repuso con δ⁺—, no del estado del mundo, así que desde el punto de vista de la unidad el mundo **deja de ser una máquina de Mealy** y no hay ninguna función que identificar. Con V fuera del símbolo, Harlow = 1,0 en el mismo mundo.
**Por qué.** «Entra en lo observado» y «entra en la hipótesis del mundo» suenan igual y no son lo mismo. Lo observado puede incluir el estado interno; **lo que se identifica** tiene que ser una función del estado del mundo. Y el síntoma —un cero perfecto y uniforme— se parece a un resultado negativo fuerte, que es lo peligroso.
**Severidad:** alta. Un cero en todas las celdas se habría leído como «los tres elementos no producen nada».
**Firma (cómo se detecta):** un alcance **exactamente 0** en todas las celdas, incluidos los controles; un símbolo observado que mezcla una medida del mundo con una del agente.
**Guarda** `[MECÁNICA]`: lo que la unidad debe explicar es **sólo** función del estado del mundo; cualquier coordenada que dependa de la historia del agente (V, energía, contadores) va **aparte**, disponible para decidir y para el observador, y **nunca dentro del símbolo de la hipótesis**. Y antes de leer un alcance de 0: comprobar que **había algo que identificar** —que el símbolo es una función del estado del mundo—, igual que `NULO POR FUTURO CIEGO` comprueba que el futuro discrimina.
**Aplicada en:** `unidad_minima_13_tres_elementos.py` (`Actor.paso`: `self.u.leer(a, o)` con la reacción del mundo; `banda_V` se guarda aparte y el observador la ve como ΔV).

## E-56 · El genoma guardaba palabras y el actor preguntaba por letras: escrito y no leído, o apisonadora
**Clase:** criterio · **Veces que saltó:** 1 · *el genoma de la Fase 3 era lastre muerto en el 83 % de sus entradas y destructivo en el resto*
**Severidad:** **ALTA.** El genoma es el contenido de la herencia de la Fase 3 y la corrección que Wis puso primero («el genoma es antes que nada la libreta de lo que mató»). Una clave mal elegida lo vuelve inútil **y** dañino a la vez, con curvas que parecen un resultado.

**29-oct-2026 (error de Opus, en la primera corrida de TRES).** El observador escribe prohibiciones como **palabras** («esta palabra precedió una caída de V»), y el actor preguntaba `prohibida([a])`: **«¿está prohibida esta letra?»**. Medido sobre 13 mundos: de **23** prohibiciones, **19 eran de dos letras y nunca se consultaban** —genoma escrito y no leído— y **4 eran de una letra y se consultaban en cada paso**, invirtiendo la letra siempre, o sea «nunca tomes A». Resultado: 3 000–6 000 «muertes evitadas» por generación, y el alcance cayendo de **0,462 (sin genoma) a 0,038 (con genoma)**. Y la celda de control `O-todo` daba **exactamente** lo mismo que `TRES`, porque con 2 o 3 prohibiciones sobre un alfabeto de 2 el tope del genoma nunca llegaba a morder: el control no controlaba nada.
**Por qué.** Dos piezas escritas en momentos distintos con la misma palabra —«prohibición»— y granularidades distintas: una **situación** en el que escribe, un **símbolo** en el que lee. Nada falla ruidosamente: el 83 % del genoma simplemente no se usa y el 17 % hace estragos, y las dos cosas producen curvas plausibles. Es la forma de E-45 y E-53 otra vez: **un nombre que tapa dos cosas**, ahora entre dos módulos del mismo fichero.
**Firma (cómo se detecta):** un contador de uso del genoma (aquí `muertes_evitadas`) del orden de los **pasos de vida** en vez del de las prohibiciones; entradas del genoma cuya longitud no coincide con la longitud de la clave con que se consulta; una celda de control que da **exactamente** lo mismo que el tratamiento.
**Guarda** `[MECÁNICA]`, tres partes: (1) **el que escribe y el que lee declaran la misma clave**, y una aserción comprueba que toda entrada del genoma tiene la longitud que el predicado consulta; (2) **ninguna prohibición de un solo símbolo**: prohibir una letra no es una prohibición, es amputar el alfabeto —la granularidad de una prohibición es una **situación**—; (3) **el contador de uso del genoma se informa junto al de entradas**, y si el uso es del orden de los pasos de vida, el veredicto es **NULO POR GENOMA MAL LEÍDO**, no un resultado sobre la herencia.
**Aplicada en:** `unidad_minima_13_tres_elementos.py` (`Actor.prohibida` consulta la **palabra que la acción completaría**, `escribir_genoma` y `Observador.componer` descartan las de un símbolo), y la segunda corrida de TRES de esta noche se hizo con el arreglo.

## Ejes no vigilados (agujeros declarados)

*Tomado del `failure_atlas.py` de RNE (`unmeasured_axes`): un registro sin eventos pero con ejes no vigilados no es un certificado de salud, es un certificado con agujeros declarados.*

- ~~**Parada por información (E-18):** sólo la detecta un humano leyendo el JSONL.~~ **Cerrado el 25-oct**: el corredor la evalúa por bloques y se detiene solo (`_estable` en `unidad_minima_05b_paralelo.py`), sobre un recorrido esparcido que hace representativo cualquier prefijo.
- **Sesgo del supervisor hacia proceso (E-19):** sólo lo detecta Wis. Sin detector mecánico; la guarda es de conducta.
- **Fuentes que caen a mitad de un gate:** arXiv dejó de responder XML desde este host durante la Fase 1 (Crossref siguió bien), así que la mitad arXiv de dos búsquedas quedó **incompleta y declarada** en vez de completada. Sin detector: hoy depende de que el ejecutor lo diga en vez de dar la búsqueda por hecha.
- **Citas «de memoria» que nunca se verifican:** el registro exige verificar antes de citar en un entregable, pero nada comprueba que se hizo. Detector posible: toda cita en un cierre lleva DOI o URL y la fecha en que se abrió. **Saltó tres veces (E-33, E-34, E-42) y las tres las vio un revisor externo**: hoy el único detector que funciona está fuera del programa.

## Cómo añadir una entrada

Al cerrar una fase, o en el momento en que un mutante, un ejecutor o Wis encuentren un error: número siguiente, fecha, los cuatro campos, y la guarda con su tipo. Si la guarda no puede ser mecánica, decir por qué y en qué punto de la ficha va la pregunta. Sin guarda, la entrada queda marcada **ABIERTA** y aparece en la pregunta final del cierre para Wis.
