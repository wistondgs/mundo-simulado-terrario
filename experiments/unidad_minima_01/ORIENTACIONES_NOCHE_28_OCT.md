# Orientaciones para la noche del 28 al 29 de octubre · Opus trabaja solo, Wis duerme

**De:** Fable, 23:30 · **Estado al escribir:** `unidad_minima_12_mundo_caro.py` corre con 11 trabajadores (carga 16 en 12 núcleos); n=8 lleva 2 376 de 4 000 con tope de reloj de 3 600 s, así que termina por reloj en menos de una hora. `CIERRE_FASE_2.md` escrito, nada commiteado, 68 ficheros sin custodia. Memoria libre 14 GB, disco 315 GB.

**Reglas de la noche, todas ya en la libreta:** salida a fichero y reanudable (E-29, E-31, campaña que sobrevive cortes); ningún `break` en un bucle de vida (E-39); matar sólo por PID (E-26); hashes del artefacto, no de la terminal (E-40); una sustitución por escritura (E-41); nivel de evidencia al lado de cada cita (E-42); cada error nuevo a la libreta con guarda antes de seguir. Máximo 11 trabajadores y **una cosa pesada a la vez**: lo siguiente arranca cuando lo anterior termina. Nada que necesite una decisión de Wis se corre como confirmatorio: se construye, se prueba con mutantes y se pilota como **exploratorio**.

**Custodia:** una sola vez, al final de la noche, un commit `chore: custodia nocturna 29-oct, nada cerrado` con los 68 ficheros. No cierra nada y Wis puede revertirlo; perderlos por un corte sería peor. El cierre de la Fase 2 sigue esperando su OK.

---

## T1 · Cuando 12 termine: las dos columnas del mundo caro (una hora)

Verifiqué que la muestra de n=8 de `12` es **subconjunto exacto** de las 5 000 filas limpias de `07` (2 376 de 2 376 por `idx`). El coste intrínseco de cada mundo ya existe: en `07`, con el identificador exacto sin olvido, `ultimo_error` y `igual_salvo_isomorfismo`.
1. Cruzar por `idx`: `caro_mundo` = no identificado en `07` o `ultimo_error` > 256; `caro_olvido` = `caro` de `12`. Tabla 2×2 por `n_min`, para n=6 (si `07` no tiene n=6 limpio, usar el banco de `05` con la misma regla) y n=8.
2. **Banco madre** = `caro_mundo` ∧ `n_min ≥ 4`, listado por `idx` con su clase de `07`, en `artifacts/banco_madre_n8.json`, con hash. Lo que es caro sólo por olvido **no** entra al banco: es defecto de disposición, y va a T2.
3. Reescribir la tabla de la puerta en `CIERRE_FASE_2.md` con las dos columnas, y la frase: «el 97 % de lo caro en n=8 lo es por el olvido de esta unidad, no por el mundo» con el número exacto que salga.

## T2 · La disposición del olvido, medida antes de que Wis elija (el grueso de la noche)

La pregunta de Wis del cierre es «¿se cambia el órgano o se cambia el mundo?». Hay una tercera opción que no está medida y es la más barata: **cambiar la disposición** (ventana, núcleo, presupuesto por intento) sin tocar el mecanismo. Hay que medirla esta noche para que la decisión de mañana tenga los tres caminos con número.
- **Banco:** los 174 W₁ de n=3 con sus W₂ (barato, control de que no se pierde nada) **y** el banco madre de T1 (donde el olvido se dispara 31–86 veces por vida).
- **Factores:** ventana ∈ {128, 512, 2048, ∞}; núcleo ∈ {64, 256, «conservar la máquina y soltar la traza» (la opción «cambiar el órgano» de Wis, aquí como disposición)}; presupuesto por intento ∈ {200 000, 2 000 000}. Ventana ∞ con presupuesto ∞ es M-c y debe reproducir el ahogo: es el mutante.
- **Medidas:** olvidos por vida, alcance en la curva (64, 128, 256), exactitud final, y el **coste para la unidad** frente al **intrínseco** de `07` (la diferencia es lo que el olvido cuesta).
- **Predicción, escrita antes:** en n=3 ninguna celda cambia el alcance (todo satura); en el banco madre, el núcleo «conservar la máquina» reduce los olvidos por debajo de 2 por vida sin perder exactitud, y es la única celda donde eso pasa. Si no pasa, la opción «cambiar la disposición» muere con número y quedan las dos de Wis.
- **Parada por información** por celda (criterio de E-18, el de `05b`), no por reloj. Reanudable por fila.

## T3 · Los dos análisis sobre lo guardado (en paralelo con T2 si queda núcleo; si no, después)

Piezas 4 y 6 de `ORIENTACIONES_TRABAJO_DESDE_EL_CORPUS.md` **con las correcciones** de la revisión externa: bits de historia **condicionados al mundo** (dos historias hoy: ninguna y W₁ fija; las otras tres se corren con T2 porque usan las mismas celdas); congruencia generadora **trasladada por el isomorfismo** sólo en las identificadas, con las cuatro salidas de B₀ y el diagnóstico de grupo. Sobre `08` y `09`. Entregable: dos tablas en el cierre, sección nueva «lo que ya estaba guardado dice».

## T4 · Las tres comprobaciones del cierre, si alguna sigue abierta

Curvas de K frente a alcance final (0,929 vs 1,000); comparaciones sobre la **intersección** de familias; P4 partido en función y estructura. Si ya están resueltas en `CIERRE_FASE_2.md`, una línea que lo diga y dónde.

## T5 · El esqueleto de la Fase 3, construido y mutado, no corrido como confirmatorio

Módulo nuevo `unidad_minima_13_tres_elementos.py` que **importa** 08, 09 y 10 y no los toca:
1. **Generador de mundos con V:** por familia, un conjunto canónico de reacciones que bajan V (δ⁻) y de palabras cortas que la reponen (δ⁺), deterministas por índice; V ∈ [0, 1], límites [0,2, 0,9]; V **entra en lo observado** como coordenada. Comprobar contra el hallazgo de Terrario (`VARIABLES_ESENCIALES_Y_REORGANIZACION_01.md`): V **no** es señal de aprendizaje en ningún sitio del código; una aserción lo garantiza.
2. **Actor con ultraestabilidad:** `UnidadFase2` + V + lista fija de saltos de disposición (orden del itinerario → elegir on/off → ventana) cuando V cruza el límite inferior; muerte en V = 0 **sin `break`**: la vida termina como estado, el bucle registra y sigue a la siguiente celda.
3. **Genoma:** estructura con prohibiciones, restricciones, relaciones certificadas y disposiciones; **tope** 8 + 8; **nombra letras y relaciones del cociente propio, nunca estados**; **prueba de renombramiento** (B₀): correr sobre una copia del mundo con los estados permutados y exigir la misma salida; su mutante (genoma con índices de estado) debe fallarla.
4. **Observador** como extensión declarada del `Teacher` de Genesis (`runtime/organism/teacher.py`): lee las dos corrientes, ordena por daño, escribe primero lo que mató; determinista; **no actúa**.
5. **Mutantes y piloto exploratorio** sólo de lo que no depende de las tres decisiones de Wis: `UNO+V` frente a `UNO+V-inerte` en n=3 (¿la que modela V predice sus caídas antes que el reactivo? ¿los saltos ocurren sólo cuando V cruza?). **TRES no se corre.** Todo etiquetado exploratorio.

## T6 · Lecturas que no cuestan CPU

- `runs/screening/D4T-*.report.json` y `runs/noche/tamizado/D4T-*`: qué midieron y si hay algo de recuperación tras cambio que sirva como línea base, ya que H-ADAPT-001 no la dio.
- `ORIENTACIONES_FASE_3_TRES_ELEMENTOS.md` §2-ter y `CARTOGRAFIA_PREVIA_FASE_3.md`: leerlos enteros antes de T5, y anotar en el gate de la Fase 3 la columna «en el corpus de Wis: id».

## El informe de la mañana

Un solo documento, `INFORME_NOCHE_29_OCT.md`, para que Wis lo lea con el café y su batería de revisores lo escrute:
1. Qué corrió, con hash de cada artefacto y hora de fin.
2. T1: la tabla 2×2 y el banco madre con su tamaño.
3. T2: la tabla ventana × núcleo × presupuesto, y **la respuesta medida a la tercera opción**: ¿cambiar la disposición basta para que la unidad deje de ahogarse en el banco madre sin perder exactitud?
4. T3: las dos tablas.
5. T5: qué se construyó, qué mutantes pasaron, qué dio el piloto exploratorio, qué falta para la ficha.
6. Errores de la noche con su número de libreta.
7. **Lo que es de Wis**, en una lista corta: las tres decisiones de la Fase 3 (cuándo actúa el observador, si ve la V de los otros, generaciones), y la pregunta del cierre, ahora con tres opciones y el número de T2 al lado de cada una.

Nada de esto cierra una fase. Todo es para que mañana se decida con datos y no con hambre de avanzar.

---

## ADENDA · 29-oct 00:15 · T5-bis · TRES se corre esta noche, exploratorio, por orden de Wis

**Wis autorizó** («hacelo») que los tres elementos **vivan esta noche**, y esto **sustituye** su instrucción anterior a Opus de no ejecutar TRES. Condiciones:

- **Exploratorio**, etiquetado así en todo artefacto y en el informe: no certifica nada, no cierra nada, no entra a ninguna puerta. Se construye para **verlo funcionar**; la ficha y la corrida confirmatoria vienen después, con mutantes.
- **Las tres decisiones pendientes toman los valores recomendados**, declarados como SUMINISTRADOS POR FABLE y revisables por Wis mañana: el observador **no actúa, actúa su hijo**; la V de los otros **es pública**; **cinco generaciones**.
- **Mundo:** el banco madre de T1 si ya existe cuando T5 termine; si no, los W₂ componibles de n=3 de la Fase 2 con la V añadida (es más chico, pero vive). Se dice cuál se usó.
- **Genoma:** primero lo que mató, después lo que restringió, al final lo que benefició; tope 8 + 8; nombra letras y relaciones del cociente, nunca estados; prueba de renombramiento obligatoria antes de correr.
- **Celdas mínimas para que el resultado tenga lectura:** TRES, DOS (sin observador), hijo-sin-genoma, O-todo, simétrico. Las demás, si hay reloj.
- **Medidas:** Harlow (acierto en los primeros 64 pasos de la generación k), supervivencia por generación, muertes evitadas, genoma por generación, fidelidad función/estructura. Todo a fichero, reanudable, sin `break`.
- **Orden:** después de T5 y sus mutantes; **no desplaza a T1 ni a T2**, que siguen primero porque el banco madre y la disposición del olvido son lo que TRES necesita para no ahogarse. Si el reloj no alcanza para todo, TRES corre en el banco de n=3 y se dice.
- **En el informe de la mañana:** una sección propia, «TRES exploratorio», con las curvas y la frase honesta de qué se vio y qué no, y la lista de lo que Wis puede cambiar de las tres decisiones antes de la ficha.
