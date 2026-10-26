# Registro de errores y guardas · programa UNIDAD MÍNIMA

**Qué es.** La lista de lo que ya nos mordió, con la **guarda** que impide que vuelva a morder. Vive en el árbol, versionada, compartida por todos los roles (Wis adjudica, Fable revisa y orienta, Opus ejecuta) y por todas las sesiones, tengan o no memoria propia.

**Las tres reglas.**
1. **Una entrada sin guarda no está cerrada.** La guarda es, por orden de preferencia: una comprobación **mecánica** que corre (un test, un mutante, un hash, un campo del JSON que el veredicto lee), o, si no puede ser mecánica, una **pregunta obligatoria** en un punto concreto de la ficha de apertura o del cierre.
2. **Se lee en el momento del riesgo, no en un hub.** El punto 0 de toda ficha de apertura (`PLANTILLA_FICHA_APERTURA.md`) es «¿qué entradas de este registro aplican y cómo se cumplen?». «Ninguna aplica» se justifica; no se deja en blanco.
3. **Cada cierre de fase alimenta el registro.** El `CIERRE_FASE_n.md` lista qué guardas saltaron y qué entradas nuevas añade. Un error cometido y no anotado es el único error que de verdad cuesta.

Formato de entrada: número · fecha · **qué pasó** (hecho, con fuente) · **por qué** · **guarda** `[MECÁNICA]` o `[PREGUNTA → punto n]` · dónde está aplicada. *Desde E-18, además:* **severidad** y **firma** (cómo se detecta), tomadas del `failure_atlas.py` de RNE.

---

## E-01 · Afirmar el entorno sin ejecutar
**25-oct-2026.** El plano §1 decía «`.venv` con Python 3.12, numpy y torch». Falso: el intérprete es 3.14.4 y ese `.venv` apunta a un 3.12 que ya no existe; sin numpy. Lo encontró el ejecutor al correr. Fuente: `CIERRE_FASE_0.md` §0.4.
**Por qué.** Se infirió de un nombre de directorio (`lib/python3.12/site-packages/torch`) sin ejecutar nada.
**Guarda** `[MECÁNICA]`: toda línea de entorno en plano, ficha o cierre lleva **el comando y su salida** (como `CIERRE_FASE_0.md` §0.4); los artefactos registran la versión exacta del intérprete (campo `python`). Una línea de entorno sin comando es inválida.
**Aplicada en:** plano §1 (corregido en el sitio), artefactos 01–04.

## E-02 · Un cero comprado con una señal suministrada
**25-oct-2026.** En 0.2, el brazo «con traza y repaso» costaba 0 pasos de vida nueva porque **el experimentador** disparaba la relectura; el plano lo daba por capacidad de la unidad. Fuente: `APERTURA_REGENERACION_TRAS_LESION.md`, «Resultado y la reparación única».
**Por qué.** No se preguntó quién dispara cada paso del mecanismo.
**Guarda** `[PREGUNTA → punto 8, tres capas]`: por cada brazo, «¿quién dispara cada paso, y qué sabe este brazo que el organismo no sabría?». Si la respuesta incluye al experimentador, el resultado se etiqueta **SUMINISTRADO** y no cuenta como capacidad. `[MECÁNICA]`: el disparo del mecanismo tiene contador interno (p. ej. `autorelecturas`) y el veredicto lo lee.
**Aplicada en:** 03 (`UnidadQueSeRelee`, contador `autorelecturas`).

## E-03 · Criterio con la unidad equivocada
**25-oct-2026.** En 0.2, mundo del bit inerte: «sin traza, no más de 2 pasos» contaba *pares letra→reacción* por reaprender; el programa mide el *paso del último error*, que depende de cuándo aparecen A y B. Midió 4, 1, 3, 2, 3. Fuente: `CIERRE_FASE_0.md` §0.2.
**Por qué.** El número de la puerta no nombraba su unidad ni el campo contra el que se compara.
**Guarda** `[PREGUNTA → punto 11, puerta]`: cada número de la puerta nombra **su unidad y el campo del JSON** con el que se compara. `[MECÁNICA]`: el veredicto lo calcula el programa leyendo ese campo (`veredicto()` en 03 y 04), nunca a mano.

## E-04 · Exigir al control lo que allí no le aplica
**25-oct-2026.** En 0.3, mundo visible: se pedía al reactivo robustez frente a la ignorancia del estado, y en ese mundo el reactivo **no es ignorante** (su reacción previa *es* el bit). Lo encontró el mutante «reactivo mudo». Fuente: `APERTURA_ELECCION_BAJO_ORIENTACION.md`, segunda enmienda.
**Por qué.** El criterio se escribió para un mundo y se copió a otro.
**Guarda** `[PREGUNTA → punto 7, banco]`: por cada **control × mundo**, escribir antes de correr qué puede hacer ese control allí; el mundo donde el control **debe** acertar es el que prueba que el test discrimina. `[MECÁNICA]`: mutante «control mudo» en el punto 10.

## E-05 · Un mundo de control que no controla lo que dice
**25-oct-2026.** En 0.2: «en el bit inerte la lesión no puede costar nada». Falso: ese mundo controla que **no se inventen distinciones** al reparar, no el coste. Lo encontró el paso de mutantes antes de la corrida real. Fuente: `APERTURA_REGENERACION_TRAS_LESION.md`, enmienda prospectiva.
**Por qué.** La ficha se dio por terminada antes de correr los mutantes. Tres criterios mal escritos en una sesión.
**Guarda** `[PREGUNTA → punto 7]`: por cada mundo de control, **la afirmación exacta que controla**, una por mundo. `[MECÁNICA/ORDEN]`: ficha → mutantes → enmienda prospectiva → corrida real; **una ficha no es final hasta pasar sus mutantes**.

## E-06 · La ecuación sellada no era la implementada
**Nivel 1.8, sep-2026.** El oráculo selló `Z_{t+1} = F(Z_t, A_t, O_{t+1})`; el código implementó `F(Z_t, A_t)`. Prueba hermética: 0/400 diferencias con observaciones distintas. Ningún gate leía la forma de F. Fuente: `LEVEL18_ANALISIS_CAUSA_RAIZ.md` §1 y §5; `CONGELACION_HISTORICA_01.md`.
**Por qué.** La ecuación del estado era una frase del oráculo que ningún test certificaba.
**Guarda** `[MECÁNICA]`: test hermético **positivo** de la forma de F: mismas acciones con observaciones distintas ⇒ el estado difiere; mismas observaciones con acciones distintas ⇒ también. Se escribe antes que el aprendiz.
**Aplicada en:** 01/02 lo cumplen de hecho (la hipótesis se refuta por lo leído); en la Fase 1 va como mutante «ciego a la observación».

## E-07 · Resultado irreproducible: semillas quemadas, parámetros sin registrar
**Nivel 1.5, sep-2026.** El segundo piloto dio 529/540 = 97,96 %; sus semillas no están en ningún `.py` de ningún árbol y la magnitud del paso «no consta». `NON_REDERIVABLE`; no se deja contar como éxito. Fuente: `CONGELACION_HISTORICA_01.md`; cartografía §43.4.
**Por qué.** Azar sin custodia y parámetros en la conversación, no en el artefacto.
**Guarda** `[MECÁNICA]`: sin `random`; dos corridas, un hash; el JSON lleva sha256 del código, versión del intérprete y **todo** parámetro. `NON_REDERIVABLE` es FAIL de custodia, no matiz.
**Aplicada en:** los cuatro programas de la Fase 0.

## E-08 · Presupuesto elegido donde la curva ya saturó
**Nivel 1.6, sep-2026.** Se selló T = 4096 «porque la curva ya saturó»; la cobertura era 1,0000 en las 16 vidas: el mecanismo nunca se probó bajo escasez y una categoría del resultado quedó inalcanzable. Fuente: memoria «la saturación no es virtud».
**Por qué.** Un punto en vez de una curva; captura sin cobertura.
**Guarda** `[MECÁNICA]`: el artefacto contiene la **curva** (varios presupuestos) y la **cobertura** aparte de la captura; una puerta sobre un único presupuesto es inválida.
**Aplicada en:** 01 (curva por T); Fase 1 (paso del último error frente a n).

## E-09 · Mecanismo que nunca se ejecutó, contado como negativo
**Nivel 1.2, sep-2026.** 0 sorpresas en 131 072 experiencias: el umbral coincidía con el techo; corrió el respaldo y el resultado se publicó como si midiera curiosidad. Fuente: memoria «contador de actividad por mecanismo».
**Por qué.** Sin contador del componente distintivo, «no ayudó» y «no corrió» dan el mismo número.
**Guarda** `[MECÁNICA]`: contador de actividad por mecanismo en el JSON; el veredicto declara **NULO-POR-INACTIVIDAD** si es 0 (03 ya lo hace con `act`).

## E-10 · Releer el código en vez de consultar el mapa
**Atlas 02 y 03, sep-2026.** No se corrió el gate sobre las secciones vigentes de la cartografía; cinco hallazgos que ya estaban en el mapa se re-derivaron. Fuente: cartografía §XLII; memoria «leer la cartografía antes de mapear».
**Guarda** `[MECÁNICA]`: `scripts/cartografia_check.py --section` antes de abrir un volumen (hoy caído por E-01; mientras tanto, leer la sección a mano). `[PREGUNTA → punto 0]`: «¿qué sección vigente del mapa cubre esto?».

## E-11 · Iniciativa fuera del encargo
**21-sep y 24-oct-2026.** Una clase extra, una conjunción extra y un módulo donde bastaba un documento; y escaleras de experimentos cuando se pedía una demostración. Fuente: memorias «limitarse a la orientación» y «unidad-minima-01-demo».
**Por qué.** Construir lo que la pregunta no pide.
**Guarda** `[PREGUNTA → punto 1]`: «¿qué estoy construyendo que la pregunta no pide?» Lo que sobre se lista aparte como propuesta y **no se construye**.

## E-12 · Cifra o negación sin su comando y sin su alcance
**16-sep y 25-oct-2026.** «En RNFE nada aprende» se midió con un comando correcto sobre el árbol equivocado (genesis-v2, no v16): un cero en el alcance equivocado se lee igual que un cero real. Y «18 worktrees prunable» frente a 14 contados con el comando. Fuente: `CARTOGRAFIA_GENESIS_01.md` §I; revisión de la Fase 0.
**Guarda** `[MECÁNICA]`: toda cifra y toda afirmación negativa de un informe lleva **el comando que la produjo y el árbol/commit** donde corrió. Se escribe «no hemos encontrado», nunca «no existe».

## E-13 · Dos relatos del mismo mecanismo; gate en verde sobre prosa vieja
**sep-2026.** Se regeneró el manifiesto de cartografía con `--write` tras cambiar código sin reescribir la sección: el gate quedó verde sobre texto obsoleto. Fuente: memoria «`--write` no prueba que se releyera».
**Guarda** `[PREGUNTA → cierre]`: una corrección va **en el sitio, con fecha**; nunca un documento paralelo; `--write` sólo tras reescribir la prosa.
**Aplicada en:** plano §1 y §4-0.2, corregidos en el sitio el 25-oct.

## E-14 · Custodia tomada por trabajo
**25-oct-2026.** Wis: «el trabajo principal no es estar commiteando; es la experimentación de la creación del ser».
**Guarda** `[PREGUNTA → cierre]`: un commit por fase, al cerrar; el cierre dice qué parte de la sesión fue experimento y qué parte custodia o documentos. Si la custodia pesa más que el experimento, la sesión se reporta como perdida en parte.

## E-15 · Mutantes que prueban la capacidad pero no el instrumento
**25-oct-2026, Fase 1.** Los cuatro mutantes del banco (memorizador, ciego a la observación, oráculo, vida invertida) pasaron, y el banco corrió aun así con **dos instrumentos roídos**: el tope de estados declarado (`n_max = n+1`) nunca se aplicó —`vivir_una_vida` instanciaba la unidad sin pasarlo, así que corrió con el 4 por omisión de 02— y el contador de coste sumaba la **distancia retrocedida**, no el trabajo. El primero fabricó un falso hallazgo (35 % y 43 % de sistemas «tocando el tope» en n=6 y n=8) y me llevó a afirmar, en falso, que el mecanismo incremental era incompleto. Fuente: `APERTURA_ESCALADO_SIN_AZAR.md`, «Dos defectos de instrumento y una corrida nula».
**Por qué.** Todos los mutantes atacaban la **capacidad** del aprendiz. Ninguno pasaba por el tope ni por el contador: el oráculo recibe la máquina verdadera, así que no aprende, no se fragmenta y no repasa.
**Severidad:** **alta** (produjo una conclusión falsa que se afirmó como hallazgo).
**Firma (cómo se detecta):** un mutante pasa pero un parámetro declarado no aparece en ningún resultado; o un contador devuelve un valor físicamente imposible (13,9 millones de pasos en 0,06 s).
**Guarda** `[MECÁNICA]`: entre los mutantes del punto 10 va al menos **uno que ejercite cada parámetro y cada contador del instrumento**, con el resultado conocido por construcción: una unidad con `n_max = 1` **debe** tocar el tope en todo mundo con n_min ≥ 2; un sistema cuyo coste se conozca de antemano **debe** devolver ese coste exacto. Un contador cuyo valor no sea físicamente posible (13,9 millones de pasos en 0,06 s) es un FAIL de instrumento, no un dato.
**Aplicada en:** pendiente — va a los mutantes de 1-bis.

## E-16 · Calibrar el reloj sobre la mediana cuando el coste tiene cola
**25-oct-2026, Fase 1.** Calibré el coste de n=6 con 24 índices repartidos y me dio 4 ms/sistema; el real fue 160 ms. **Error de ×40.** La causa: la distribución tiene una cola brutal (mediana 4 ms, peor sistema 182 s, ×45 000), y 24 muestras no la ven. De ahí salió un «cabe en el presupuesto» falso y una estimación de 9 h que debió ser de 2–3 h paralelizada. Fuente: esta ficha, §4 y la estimación revisada.
**Por qué.** Se calibró con la medida de centro de una distribución cuyo total lo decide la cola.
**Severidad:** baja en medida, media en planificación (estimaciones erradas por ×40 y una decisión de paralelizar tomada tarde).
**Firma (cómo se detecta):** la razón máximo/mediana de la muestra piloto supera 100; o cada nueva estimación del mismo tramo sube respecto de la anterior.
**Guarda** `[MECÁNICA]`: una calibración de coste se hace sobre los **deciles del orden canónico ya recorrido**, no sobre una muestra repartida, y **declara su error esperado**. Si la razón máximo/mediana de la muestra piloto supera 100, la calibración se declara **no fiable para el total** y el presupuesto se da como rango abierto.
**Aplicada en:** la estimación revisada de la Fase 1 (deciles de n=6: de 7,6 a 250 ms).

## E-17 · Gate de antecedentes sin la complejidad del problema
**25-oct-2026, Fase 1.** El gate de la fase buscó **mecanismos** (AALpy, MooreMI, RPNI, L#, `dfa-identify`) y no buscó la **complejidad del problema** que el mecanismo resuelve. El problema que 02 resuelve es «la máquina mínima consistente con los datos», que es NP-difícil (Gold 1978, *Information and Control* 37:302–320, `10.1016/s0019-9958(78)90562-4`; Angluin 1978, ibíd. 39:337–350, `10.1016/s0019-9958(78)90683-6`) y no aproximable dentro de ningún polinomio (Pitt & Warmuth 1993, *JACM* 40:95–142, `10.1145/138027.138042`). La cola de la Fase 1 no es un defecto de implementación: es el precio de exigir el mínimo exacto sin maestro, y **estaba en la literatura antes de medirlo**.
**Por qué.** Se preguntó «¿quién lo ha hecho?» y no «¿cuánto cuesta hacerlo, en teoría?».
**Severidad:** **alta** (se midió durante horas algo que la teoría ya acotaba).
**Firma (cómo se detecta):** el gate cita implementaciones y ningún resultado de complejidad; o aparece una cola de coste que nadie había predicho en un problema clásico.
**Guarda** `[PREGUNTA → gate de antecedentes]`: todo gate incluye una fila para la **complejidad del problema** que el mecanismo resuelve (clase, cotas de aproximación, resultados de imposibilidad), con cita verificada. Si el problema es NP-difícil o inaproximable, la ficha lo dice en la puerta y **la cola se mide y se declara desde el principio**, no se descubre.
**Aplicada en:** pendiente — va al gate de 1-bis, que es donde el mecanismo cambia de clase de complejidad.

---

## E-18 · Correr sin criterio de parada por información
**25-oct-2026, Fase 1 (error de Fable, en el paquete; y de Opus, al no parar).** El paquete `ORIENTACIONES_FASE_1_PARALELIZAR_Y_CERRAR.md` fijó un **tope de sesión** (horas) y ninguna **parada por información**. Cuando n=6 terminó y los primeros miles de n=8 mostraron que el coste es `f(n_min)` y explota en 7–8, el veredicto (FAIL de iii) y la forma de la respuesta ya estaban; se siguió corriendo horas a 11 s/mundo, con 35 sistemas comiéndose el 80 % del cómputo y truncados por el tope de 900 s. Wis lo vio: «si ya sé lo que va a pasar, gastar energía en balde». Fuente: esta conversación, 25-oct.
**Por qué.** Es E-08 en el eje del tiempo: seguir midiendo donde la curva ya habló. Se declaró un límite de **reloj** y no un límite de **información**.
**Severidad:** media (gastó horas de máquina y de sesión; no contaminó ninguna medida).
**Firma (cómo se detecta):** la estadística que decide la puerta deja de moverse entre estratos consecutivos del banco mientras el reloj por sistema sube; o el veredicto ya no puede cambiar con lo que queda.
**Guarda** `[PREGUNTA → punto 11, puerta]`: toda campaña declara **antes de correr** su criterio de parada por información (qué estadística, qué tolerancia, sobre qué estratos), además del tope de reloj; y el cierre informa **en qué punto quedó determinado el veredicto** frente a cuándo se detuvo la corrida. `[MECÁNICA]` **implementada el 25-oct**, ya no es pendiente: el corredor evalúa el criterio por bloques y se detiene solo. En `unidad_minima_05b_paralelo.py`, funciones `_stats_bloque` y `_estable`: bloques de 1 000 sistemas, identificación por `n_min` y proporción de clases, parada cuando dos bloques consecutivos difieren menos de **3 puntos** en todos los estratos con más de **50** sistemas. Declarada en `APERTURA_ESCALADO_SIN_AZAR.md` antes de aplicarla. Va acompañada de la segunda mitad sin la cual no sirve: los pendientes se recorren en **orden esparcido** (permutación por inversión de bits del rango, verificada exacta), porque pararse pronto en el orden canónico no daba una muestra sino la parte fácil — medido: **17 a 28 puntos** de identificación a igual `n_min` entre el primer tercio y los otros dos, en n=4 y n=6 completos.
**Aplicada en:** 1-bis (banco: n=3 y n=4 completos; n=6 y n=8 por muestra estratificada por n_min, chica y declarada; parada cuando la curva coste(n_min) e identificación(n_min) se estabilicen).

## E-19 · El supervisor orientó proceso mientras el experimento corría
**25-oct-2026 (error de Fable).** Con el banco ya corriendo, el supervisor dedicó varios turnos a registro, plantilla y skill, y Wis tuvo que preguntar «sobre el avance del experimento no te enfocaste nada; sólo me estás diciendo cosmética». El estado del experimento estaba en el JSONL todo el tiempo.
**Por qué.** Lo pedido (el registro) se construyó alrededor del experimento en vez de leer primero el experimento. Es E-11 y E-14 en el rol de supervisor.
**Severidad:** baja en medida, alta en coste de atención de Wis.
**Firma:** un turno del supervisor sin una cifra del artefacto en curso.
**Guarda** `[PREGUNTA → cada revisión]`: la primera acción del supervisor en cada turno es **leer el artefacto en curso** (filas, clases, colas, proceso vivo) y abrir con su estado; el proceso y la custodia van después y sólo si queda espacio.

## E-20 · Parada que arrastra: el tope detiene el envío pero no cancela lo encolado
**25-oct-2026, Fase 1 (error de Opus).** El corredor paralelo mantenía una ventana de 32 futuros para no dejar trabajadores ociosos. Al morder un tope, dejaba de **enviar** sistemas nuevos pero **no cancelaba los ya encolados y sin empezar**, así que la parada podía arrastrar un drenaje de hasta 32/4 × 900 s = **2 h** después de haber decidido parar. Lo detecté yo al estimar el tiempo restante y lo dije antes de que mordiera; Wis no tuvo que verlo.
**Por qué.** La ventana se dimensionó para el rendimiento (que el pool no se vacíe) sin pensar en la terminación (que la parada sea un corte). Son dos requisitos distintos sobre el mismo número.
**Severidad:** baja (no contamina ninguna medida; gasta máquina después de la decisión de parar).
**Firma (cómo se detecta):** el tiempo entre «se decide parar» y «el proceso termina» crece con el tamaño de la ventana en vez de con el coste de un solo elemento.
**Guarda** `[MECÁNICA]`: al detenerse por cualquier motivo —tope de reloj, tope de sesión o parada por información—, el corredor **cancela los futuros encolados que no han empezado** y sólo espera a los que ya corrían; informa cuántos canceló. Todo mecanismo de parada declara **qué cancela y a qué espera**.
**Aplicada en:** `unidad_minima_05b_paralelo.py`, bloque `if motivo_parada:` (`fut.cancel()`, cuenta `canceladas`), declarada en `APERTURA_ESCALADO_SIN_AZAR.md`.

## E-21 · La fila no guarda el objeto medido, sólo lo que se le calculó
**25-oct-2026, Fase 1 (error de Opus).** Las filas del banco guardan los números **sobre** la máquina aprendida —estados, identidad salvo isomorfismo, clase, coste, acierto en el futuro— pero **no la máquina**. Consecuencia concreta y ya pagada: el acierto en el futuro se midió con una ventana de 2 048 pasos (`FUTURO_MAX`) y **no se puede recalcular con una ventana mayor sin volver a correr el sistema entero**, que en n=8 cuesta hasta 900 s. Lo mismo vale para cualquier pregunta nueva sobre la máquina adquirida. La pregunta de la estructura cíclica (`unidad_minima_05d_estructura.py`) se pudo contestar en segundos **sólo porque las tablas A y B del mundo sí estaban en la fila**; si hubiera dependido de la máquina aprendida, habría costado otra campaña.
**Por qué.** Se guardó lo que la puerta de entonces necesitaba leer, no el objeto del que se derivan las preguntas siguientes. El coste de re-derivar no se estimó.
**Severidad:** media (no contamina ninguna medida; impide preguntas nuevas sin repetir el cómputo).
**Firma (cómo se detecta):** una pregunta nueva sobre el artefacto exige volver a correr en vez de releer; o un parámetro de ventana (`FUTURO_MAX`, un tope, un presupuesto) aparece en el resumen sin que el objeto al que se aplicó esté guardado.
**Guarda** `[MECÁNICA]`: toda fila guarda **el objeto adquirido serializado** —la máquina como lista de `(estado, letra) → (estado, salida)` más el estado final—, no sólo los estadísticos. Son decenas de bytes frente a horas de re-cómputo. Regla corta: **si re-derivar cuesta más que guardar, se guarda.**
**Aplicada en:** obligatoria en las filas de 1-bis (`APERTURA_FUSION_POLINOMICA.md` §12). En la Fase 1 queda **ABIERTA**: las filas ya grabadas no la tienen y no se van a repetir 11 h de cómputo para añadirla.

---

## Ejes no vigilados (agujeros declarados)

*Tomado del `failure_atlas.py` de RNE (`unmeasured_axes`): un registro sin eventos pero con ejes no vigilados no es un certificado de salud, es un certificado con agujeros declarados.*

- ~~**Parada por información (E-18):** sólo la detecta un humano leyendo el JSONL.~~ **Cerrado el 25-oct**: el corredor la evalúa por bloques y se detiene solo (`_estable` en `unidad_minima_05b_paralelo.py`), sobre un recorrido esparcido que hace representativo cualquier prefijo.
- **Sesgo del supervisor hacia proceso (E-19):** sólo lo detecta Wis. Sin detector mecánico; la guarda es de conducta.
- **Fuentes que caen a mitad de un gate:** arXiv dejó de responder XML desde este host durante la Fase 1 (Crossref siguió bien), así que la mitad arXiv de dos búsquedas quedó **incompleta y declarada** en vez de completada. Sin detector: hoy depende de que el ejecutor lo diga en vez de dar la búsqueda por hecha.
- **Citas «de memoria» que nunca se verifican:** el registro exige verificar antes de citar en un entregable, pero nada comprueba que se hizo. Detector posible: toda cita en un cierre lleva DOI o URL y la fecha en que se abrió.

## Cómo añadir una entrada

Al cerrar una fase, o en el momento en que un mutante, un ejecutor o Wis encuentren un error: número siguiente, fecha, los cuatro campos, y la guarda con su tipo. Si la guarda no puede ser mecánica, decir por qué y en qué punto de la ficha va la pregunta. Sin guarda, la entrada queda marcada **ABIERTA** y aparece en la pregunta final del cierre para Wis.
