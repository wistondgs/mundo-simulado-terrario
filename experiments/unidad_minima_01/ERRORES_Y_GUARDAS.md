# Registro de errores y guardas · programa UNIDAD MÍNIMA

**Qué es.** La lista de lo que ya nos mordió, con la **guarda** que impide que vuelva a morder. Vive en el árbol, versionada, compartida por todos los roles (Wis adjudica, Fable revisa y orienta, Opus ejecuta) y por todas las sesiones, tengan o no memoria propia.

**Las tres reglas.**
1. **Una entrada sin guarda no está cerrada.** La guarda es, por orden de preferencia: una comprobación **mecánica** que corre (un test, un mutante, un hash, un campo del JSON que el veredicto lee), o, si no puede ser mecánica, una **pregunta obligatoria** en un punto concreto de la ficha de apertura o del cierre.
2. **Se lee en el momento del riesgo, no en un hub.** El punto 0 de toda ficha de apertura (`PLANTILLA_FICHA_APERTURA.md`) es «¿qué entradas de este registro aplican y cómo se cumplen?». «Ninguna aplica» se justifica; no se deja en blanco.
3. **Cada cierre de fase alimenta el registro.** El `CIERRE_FASE_n.md` lista qué guardas saltaron y qué entradas nuevas añade. Un error cometido y no anotado es el único error que de verdad cuesta.

Formato de entrada: número · fecha · **qué pasó** (hecho, con fuente) · **por qué** · **guarda** `[MECÁNICA]` o `[PREGUNTA → punto n]` · dónde está aplicada. *Desde E-18, además:* **severidad** y **firma** (cómo se detecta), tomadas del `failure_atlas.py` de RNE.

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

## Ejes no vigilados (agujeros declarados)

*Tomado del `failure_atlas.py` de RNE (`unmeasured_axes`): un registro sin eventos pero con ejes no vigilados no es un certificado de salud, es un certificado con agujeros declarados.*

- ~~**Parada por información (E-18):** sólo la detecta un humano leyendo el JSONL.~~ **Cerrado el 25-oct**: el corredor la evalúa por bloques y se detiene solo (`_estable` en `unidad_minima_05b_paralelo.py`), sobre un recorrido esparcido que hace representativo cualquier prefijo.
- **Sesgo del supervisor hacia proceso (E-19):** sólo lo detecta Wis. Sin detector mecánico; la guarda es de conducta.
- **Fuentes que caen a mitad de un gate:** arXiv dejó de responder XML desde este host durante la Fase 1 (Crossref siguió bien), así que la mitad arXiv de dos búsquedas quedó **incompleta y declarada** en vez de completada. Sin detector: hoy depende de que el ejecutor lo diga en vez de dar la búsqueda por hecha.
- **Citas «de memoria» que nunca se verifican:** el registro exige verificar antes de citar en un entregable, pero nada comprueba que se hizo. Detector posible: toda cita en un cierre lleva DOI o URL y la fecha en que se abrió.

## Cómo añadir una entrada

Al cerrar una fase, o en el momento en que un mutante, un ejecutor o Wis encuentren un error: número siguiente, fecha, los cuatro campos, y la guarda con su tipo. Si la guarda no puede ser mecánica, decir por qué y en qué punto de la ficha va la pregunta. Sin guarda, la entrada queda marcada **ABIERTA** y aparece en la pregunta final del cierre para Wis.
