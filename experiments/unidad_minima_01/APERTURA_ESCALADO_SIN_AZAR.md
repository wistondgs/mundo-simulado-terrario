# FICHA DE APERTURA · escalar sin azar, de 3 a 8 estados (Fase 1)

**Fecha:** 2026-10-25 · **Veredicto: `OPEN`** (autoriza código) · **Gate previo:** `MULTIPLE_NEAR_SOLUTIONS`, ver `PRIOR_ART_ESCALADO_SIN_AZAR.md`

1. **Pregunta.** ¿La unidad de 02 —una sola vida, sin maestro, sin reset, sin probabilidad— identifica la máquina mínima de mundos ocultos de 3 a 8 estados, con un coste que crece polinomialmente y no exponencialmente?

2. **Qué se construye.** Nada de aprendizaje. El gate dejó claro que lo más cercano publicado (MooreMI, Giantamidis & Tripakis 2016) aprende Moore desde un **conjunto** de trazas y fuera de línea, y que nuestro residuo es la vida continua con predicción previa. Esta fase mide si **el mecanismo que ya existe** basta. Se escribe sólo el banco, la verdad de referencia (minimización por refinamiento de particiones, Hopcroft 1971, de libro y citada), la comparación salvo isomorfismo y los contadores. Si 02 basta, **el mejor desenlace es no escribir ningún algoritmo**.

3. **El banco, antes que el umbral.** Un sistema son dos mapas arbitrarios `A, B: S → S` sobre `{0..n−1}`; hay `n^(2n)`. Orden canónico: los `2n` dígitos en base `n`, letra A primero, el último variando más rápido — **verificado** idéntico a `itertools.product` en los 729 sistemas de n=3. Ese orden se indexa directamente, así que la fracción 1-de-k se toma sin enumerar lo que no se usa. Estado inicial 0; sólo cuenta la parte alcanzable desde 0. Salida observable: **sólo el bit de cambio** `o = [x′ ≠ x]`, decisión adjudicada, disposición suministrada.

4. **Cobertura declarada antes de correr**, con el reloj medido sobre 24 índices repartidos por todo el banco y desplazados +1 para no caer en la muestra:

   | n | banco | k | a medir | L | vida | ms/sistema | reloj previsto |
   |---|---|---|---|---|---|---|---|
   | 3 | 729 | 1 (completo) | 729 | 5 | 258 | ~2,7 | 2 s |
   | 4 | 65 536 | 1 (completo) | 65 536 | 6 | 642 | 1,4 | ~92 s |
   | 6 | 2 176 782 336 | 20 000 | 108 839 | 8 | 3 586 | 4,4 | ~480 s |
   | 8 | 281 474 976 710 656 | 10 000 000 000 | 28 147 | 10 | 18 434 | 13,1 | ~369 s |

5. **Longitud de vida L(n) = n + 2.** Suelo estructural: en una máquina mínima de n estados, dos estados cualesquiera se separan con una palabra de longitud < n y cualquier estado se alcanza con una de longitud < n, y la vida shortlex hasta L contiene toda palabra de longitud ≤ L como bloque; así que L ≥ n−1 es el suelo. El margen de +3 es **a ojo y se declara como tal**: el gate buscó y **no encontró** ninguna cota publicada para una sola traza sin reset. Si un sistema no se identifica por vida corta, saldrá en la clasificación como «presupuesto»; **no se sube L a mitad de corrida.**

6. **La unidad:** la de 02 tal cual, `n_max = n + 1` como tope de seguridad. Si lo toca, se registra: es hallazgo, no excepción. La política de relectura es la de 02 —relee sólo al refutar—; el disparador interno de 03 **no se usa**, porque aquí no hay lesiones. Declarado como disposición.

7. **Identidad salvo isomorfismo**, por forma canónica: renumerar por BFS desde el estado inicial con orden fijo de letras y comparar. Etiquetas distintas con la misma conducta no son fallo (ya se vio en 0.2, t=512 y 1024).

8. **Clasificación obligatoria de todo no coincidente**, sin excepción: *no identificable desde la vida* (≥ 2 mínimas, con `minimal_mealy` y `count_cap=2`) · *presupuesto* (la vida se acabó antes del último error) · *tope de estados tocado* · **SIN EXPLICACIÓN**, que es defecto del mecanismo y es FAIL. Para n ≤ 4 la identificabilidad se calcula en todos; para n = 6 y 8, sólo en los no coincidentes.

9. **Tres capas.** *Programado*: el banco y su orden, la verdad de referencia, la comparación. *Disposición*: la salida observable, L(n), el tope n+1, el segmento de futuro (palabras de longitud L+1, cortadas a 2048 pasos), el orden shortlex y la política de relectura. *Adquirido*: la máquina de cada sistema, cuándo dejó de errar, y lo que costó.

10. **Contadores de actividad.** Por sistema: refutaciones, distinciones abiertas, pasos repasados, repaso máximo, predicciones sin ruta y veces que la distinción decidió en el futuro. Refutaciones totales en **0** sobre la clase n_min ≥ 2 ⇒ nulo por inactividad.

11. **La puerta, numérica y escrita antes de correr.**
    - (i) **Identificación:** para todo n, de los sistemas con n_min ≥ 2, los no coincidentes están **todos** clasificados, y **cero** casos «SIN EXPLICACIÓN» en el banco entero.
    - (ii) **No sobrefragmentación:** en la clase n_min = 1, cero distinciones abiertas y cero sistemas con más de un estado, en todo n.
    - (iii) **Coste acotado:** la mediana de pasos repasados no excede **5×** la longitud de la vida en ningún n, y el máximo no excede **100×**.
    - (iv) **Criterio de muerte, como número:** FAIL si en n=8 la mediana de `repasados / vida` es más de **10×** la de n=3; o si más del **20 %** de los sistemas con n_min ≥ 2 de n=8 quedan sin identificar por causa distinta de «no identificable desde la vida»; o si el tope de estados se toca en más del **1 %** de los sistemas.
    - (v) **Falsador escrito:** el resultado concreto que diría «02 no escala y hace falta otro mecanismo» es que el coste de repaso **por paso de vida** crezca monótonamente con n y más de ×10 entre n=3 y n=8. Que el coste absoluto crezca no es falsador: la vida también crece.

12. **Custodia.** `unidad_minima_05_banco.py`; una línea por sistema en `artifacts/unidad_minima_05_banco.jsonl`, escrita y volcada en el momento, de modo que la corrida **se reanuda** tras un corte saltando lo ya hecho; resumen en `artifacts/unidad_minima_05_banco.json` con el sha256 del código, la versión del intérprete, y sin `random`. Un commit al cerrar, sólo si Wis lo autoriza.

---

## Mutantes del gate · corridos sobre el banco completo de n=3 ANTES de la corrida real

| mutante | debe | resultado |
|---|---|---|
| **memorizador** (un estado por paso vivido, nunca generaliza) | FALLAR | falla la identidad en 729/729 y el futuro en 530/729 |
| **ciego a la observación** (el fallo de 1.8: el estado nunca ve una observación) | FALLAR donde n_min ≥ 2 | falla en 530/530, y no abre ni una distinción en todo el banco |
| **oráculo** (se le da la máquina verdadera) | PASAR | pasa identidad 729/729 y futuro 729/729 |
| **vida invertida** (la misma vida al revés, determinista) | cambiar el último error y no el mecanismo | cambia el último error en 440 sistemas; ver la enmienda |

**EL GATE SIRVE:** los tres mutantes malos fallan y el bueno pasa.

### Enmienda prospectiva · 2026-10-25, hallada en el paso de mutantes y antes de la corrida real

El criterio de la vida invertida, tal como venía escrito —«no debe cambiar la máquina final en los identificables»— **confundía dos cosas distintas**: que el *mecanismo* dependa del orden, que sería un defecto, y que la vida invertida sea una *experiencia* distinta y a veces más pobre, que es lo esperado.

Medido: de 567 sistemas identificados hacia delante, **54 dan otra máquina hacia atrás**. Y en **los 54**, la máquina aprendida es la mínima de su propia traza invertida; 18 de ellos no son siquiera identificables desde esa vida, y 8 nunca vieron la distinción. El mecanismo hizo exactamente su trabajo.

Lo que prueba independencia del orden es que el aprendiz devuelva **la mínima de lo que vivió**, no que vivir otra cosa dé lo mismo. El criterio pasa a ser ése, y las diferencias con la verdad se clasifican como cualquier otra (§8). Se declara aquí y no se vuelve a tocar.

*Es la cuarta vez en dos sesiones que el paso de mutantes corrige un criterio mío antes de medir. Sigue siendo para lo que sirve, y sigue diciendo que los escribo demasiado rápido.*

---

## Primera medición: FAIL del criterio (i), y la reparación única · 2026-10-25

**Medido, y queda en el registro:** n=3 completo dio **44** casos `SIN EXPLICACIÓN` de 530 con distinción, y n=4 completo dio **5946** de 51 222. El criterio (i) de la puerta exigía cero. **FAIL.**

**Diagnóstico, medido sobre los 44 de n=3.** En **los 44** la unidad aprendió la máquina mínima **única** consistente con su propia traza (`nsol = 1` y `estados aprendidos = tamaño mínimo`). En **38** de ellos esa mínima única tiene **menos estados que la verdad** (2 frente a 3, o 1 frente a 2): la vida no contiene la información que forzaría la verdad, y el criterio de retención declarado —la máquina más chica compatible con toda la experiencia— prefiere correctamente la pequeña. En los 6 restantes el tamaño coincide y la máquina es otra, igualmente mínima y única para esa traza.

**El mecanismo hizo exactamente lo que su criterio declarado le manda.** Lo que falló es mi prueba de identificabilidad: preguntaba «¿hay ≥ 2 mínimas?», y eso es sólo **una** de las dos formas en que una vida puede no determinar la verdad. La otra es «hay exactamente una mínima y no es la verdad». Llamar a eso defecto del mecanismo sería falso.

**La reparación única** (la que permite la regla de cierre) no afloja la puerta: la **endurece**, y además elimina una búsqueda exponencial que no habría escalado a n = 8. La clasificación pasa a decidirse por comparación de tamaños, que es exacta y no requiere búsqueda alguna:

- **estados aprendidos > n_min** ⇒ `SIN EXPLICACIÓN`, y es un defecto real: la verdad, de tamaño n_min, es consistente con la traza, así que existía una máquina más chica y la unidad no la encontró. **Sobrefragmentó.**
- **estados aprendidos < n_min** ⇒ *la vida no determina la verdad: admite una máquina menor*. Cobertura, no mecanismo.
- **estados aprendidos = n_min y no isomorfa a la verdad** ⇒ *la vida no determina la verdad: dos máquinas del mismo tamaño la explican*. Es demostrable sin buscar: la verdad y la aprendida son ambas consistentes con la traza y del mismo tamaño.

Y se añade el **cruce obligatorio** que la orientación pide para |S| ≤ 4: en n = 3 y n = 4, todo sistema no coincidente se comprueba además contra `minimal_mealy` (el retroceso exhaustivo de 01). Si las dos vías discrepan, **se para y se informa**.

**Predicción, escrita antes de volver a medir:** cero casos `SIN EXPLICACIÓN` en todo el banco, porque ningún sistema tendrá más estados aprendidos que n_min; y el cruce con el retroceso exhaustivo coincidirá en el 100 % de los no coincidentes de n = 3 y n = 4.

**Falsador de la reparación:** cualquier sistema con más estados aprendidos que n_min, o cualquier discrepancia en el cruce. Las dos cosas serían defectos reales del mecanismo, no de la medida.

---

## Dos defectos de instrumento y una corrida nula · 2026-10-25

Entre la primera medición y la definitiva aparecieron dos defectos **míos, en la medida**, no en el mecanismo. Ninguno es un FAIL de la puerta: una corrida que no ejecuta su propia ficha no es un resultado, es una corrida nula. Quedan aquí porque el registro de lo que salió mal es parte del entregable.

### Defecto 1 · el tope de estados declarado nunca se aplicó

`vivir_una_vida` instanciaba la unidad con `clase()`, **sin pasar `n_max`**, así que toda la campaña corrió con el tope por omisión de 02 —**4 estados**— y no con el `n + 1` que esta ficha declara en §6.

Lo que eso produjo: en n=6, 38 291 de 108 840 sistemas «tocaron el tope» (35,2 %), y en n=8, 12 180 de 28 148 (43,3 %), contra el 1 % declarado. Parecía el hallazgo de la fase y no era ninguno: con n=6 y n=8 la unidad estaba atada a 4 estados, de modo que cualquier mundo de 5 o 6 estados distinguibles era imposible por construcción.

**Las corridas de n=6 y n=8 hechas así quedan NULAS.** n=3 y n=4 se sostienen: allí el tope declarado era 4 y 5 respectivamente, y ningún sistema llegó a tocar 4, así que el defecto no cambió nada medible.

**Una conclusión que saqué y era falsa, y lo digo aquí porque la dije:** al ver que el retroceso exhaustivo de 01 hallaba 5 estados donde la unidad incremental abortaba, concluí que el mecanismo incremental era **incompleto**. No lo es. El retroceso corría con `n_max = 7` y la unidad con 4: comparé dos configuraciones distintas y leí la diferencia como un defecto del mecanismo.

### Defecto 2 · el contador de coste no mide el coste

El contador `pasos_repasados` de 02 suma, en cada refutación, la **distancia retrocedida** (`len(traza) − i`), no los pasos que de hecho se vuelven a recorrer. Si al reanudar la unidad refuta en el primer paso, el contador anota un repaso completo que nunca ocurrió.

Cómo salió a la luz: un sistema de n=6 declaraba **13 898 742** pasos repasados en **0,06 s** de reloj, que es imposible. En n=2 el mismo contador daba 79 y la discrepancia no se veía.

Esto importa porque **los criterios de coste (iii) y (iv) de esta ficha estaban construidos sobre ese contador**. Se corrige sin tocar 02, que está congelado y commiteado: una subclase cuenta las llamadas reales a `_avanzar`, que es el trabajo que la unidad hace. Los dos números se informan **separados**: el trabajo real es el coste, y la distancia retrocedida sigue siendo un dato (dice cuánto deshace), pero no es el coste. Los umbrales de (iii) y (iv) se mantienen tal como se declararon, aplicados ahora al trabajo real.

### Lo que esto dice del método

Cuatro criterios mal escritos en la Fase 0 y ahora dos instrumentos defectuosos, los dos hallados sólo porque un número era físicamente imposible o porque un diagnóstico no cuadraba. El paso de mutantes atrapó los criterios pero **no atrapó ninguno de los dos defectos de instrumento**: el oráculo pasaba porque recibe la máquina verdadera y no pasa por el tope ni por el contador. Un mutante que habría atrapado el primero es trivial de escribir y no estaba: *un mundo con n_min > n_max declarado debe tocar el tope, y uno con n_min ≤ n_max no debe tocarlo nunca*. Queda escrito para la siguiente fase.

---

## Paralelización · 2026-10-25 · no cambia ninguna medida

Cada sistema del banco se calcula sólo desde `(n, idx)`, sin estado compartido y de forma determinista, así que repartirlos entre procesos no puede cambiar una cifra: cambia el reloj y el orden en que las filas caen al fichero.

- **Corredor aparte, no una reescritura.** `unidad_minima_05b_paralelo.py` **importa** `un_sistema` de `unidad_minima_05_banco.py` y la llama tal cual. 05 no se toca. Así «paralelizar no cambió la medida» no es una afirmación mía: la función que mide es literalmente el mismo objeto.
- **Prueba de identidad, antes de parar la corrida en serie.** 200 índices de n=4 ya medidos en serie, recalculados en paralelo con 4 trabajadores: **idénticos campo a campo** en los 22 campos medidos, **cero diferencias**. El único campo excluido es `reloj_s`, que es reloj de pared y ya estaba declarado como la única fuente de variación (dos corridas del banco de n=3 difieren sólo en él).
- **4 trabajadores, no 6.** Con un solo hilo el paquete ya estaba a 92 °C de 100. Medido con cuatro: paquete **92 °C** (igual, no peor), núcleos entre 67 y 92 °C, y la frecuencia baja de 4,1 a **3,6 GHz** por el límite de turbo multinúcleo. No se estrangula, así que se quedan cuatro.
- **Un solo escritor**, el proceso padre, que añade cada fila y la vuelca en el momento: la corrida sigue siendo reanudable. Olas de 4000 sistemas con `as_completed`, para que un sistema de 182 s no bloquee la custodia de los que ya terminaron. **Consecuencia declarada:** el orden del fichero deja de ser canónico, así que el resumen, la puerta y el hash se calculan **siempre** sobre las filas ordenadas por `(n, idx)`, nunca sobre el orden del fichero.
- **Sin tope de tiempo por sistema.** Descartar los lentos sería seleccionar contra la cola, y la cola es parte de la respuesta de la fase.
- Ritmo medido: 42 ms/sistema en n=6 frente a 160 ms en serie, **×3,8**.

No se cambió L, ni k, ni la salida observable, ni la puerta, ni ninguna predicción.

---

## Variante declarada · cobertura por longitud frente a cobertura por itinerario · 2026-10-25

**Antes de correrla.** La clase «la vida no determina la verdad» crece con n (30,6 % en n=3; 37,4 % en n=4; 39,5 % en n=6 parcial) y es el hallazgo de cobertura de la fase. Pero «la vida no determinó la verdad» tiene **dos causas distintas** y los números de arriba las mezclan:

- **por longitud**: la palabra que separa las dos máquinas es más larga que cualquiera de la vida. Medido en el caso de n=4 que lo exhibe: la palabra separadora es `AABAABB`, de longitud **7**, y la vida de n=4 llega a longitud **6**. La vida se quedó **una letra corta**.
- **por itinerario**: la palabra separadora cabe en la longitud vivida, pero el orden shortlex nunca puso a la unidad en el estado desde el que esa palabra separa. Es un límite de **qué** se vivió, no de **cuánto**.

La variante las separa al coste de una corrida barata: los sistemas no determinados de n=3 y n=4 se vuelven a vivir con **L = n + 3** en vez de n + 2 (es decir, 6 y 7 en vez de 5 y 6), sin tocar nada más. Todo lo demás —banco, salida observable, tope, orden canónico, clasificador— idéntico.

**Lectura declarada:** el que pasa a identificado con una letra más de vida estaba limitado **por longitud**; el que sigue no determinado está limitado **por itinerario**.

**Predicción, escrita antes de correr.** La mayoría de la clase «dos máquinas del mismo tamaño la explican» pasará a identificada (es el caso de la palabra separadora un poco más larga), y buena parte de «admite una máquina menor» **no**, porque ahí falta haber visitado el estado que obliga a la distinción, no longitud. En números: más del 50 % de «mismo tamaño» se resuelve, y menos del 50 % de «admite menor».

**Falsador de la lectura:** que la fracción no determinada no se mueva casi nada al alargar la vida una letra. Eso diría que el límite es de itinerario en casi todos los casos, y entonces la Fase 2 —elegir qué vivir— es la única salida y no una mejora.

Esta variante **no cambia la puerta de la fase**: es un hallazgo de cobertura y se informa como tal.

### Resultado de la variante · 2026-10-25 · la predicción falló y el falsador se cumplió

| clase de partida | sistemas | pasan a identificada con L = n+3 |
|---|---|---|
| n=3 · «dos máquinas del mismo tamaño» | 110 | **0** |
| n=3 · «admite una máquina menor» | 52 | **0** |
| n=4 · «dos máquinas del mismo tamaño» | 10 680 | **6** (0,06 %) |
| n=4 · «admite una máquina menor» | 8 502 | **0** |

**Predije más del 50 % de la clase «mismo tamaño» y salió 0,03 %.** El falsador escrito antes de correr era: «que la fracción no determinada no se mueva casi nada al alargar la vida una letra». Se cumplió. No se enmienda: la predicción queda como se escribió y la lectura cambia.

Y la letra extra no es poca cosa: la vida **más que se duplica** (258 → 642 pasos en n=3; 642 → 1538 en n=4), y la vida larga contiene la corta como prefijo, así que es experiencia estrictamente añadida.

**Una lectura mía anterior queda refutada, y era mía.** Había escrito que en el caso analizado de n=4 «la vida se quedó una letra corta», porque la palabra más corta que separa la máquina aprendida de la verdadera es `AABAABB`, de longitud 7, y la vida llegaba a longitud 6. Medido ahora: con L = 7 esa palabra se recorre **nueve veces, desde tres estados distintos**, y el sistema **sigue sin identificarse**. Además esa palabra da la misma salida `1111111` desde **los cuatro** estados de la máquina verdadera: no separa estados del mundo, separaba las dos hipótesis desde el estado en que cada una había quedado. La longitud de la palabra separadora era un espejismo.

**Lo que queda medido, y es el hallazgo de cobertura de la fase.** La clase no determinada es **estable al alargar la vida**: no es escasez de longitud, es el itinerario. En una vida continua sin reset, tener la palabra en la vida no basta, porque no se elige **desde dónde** se la recorre; y el orden shortlex decide eso por la unidad. Vivir más de lo mismo no compra casi nada.

**Consecuencia para la Fase 2, dicha con el número que la respalda:** elegir qué vivir no es una mejora sobre vivir más, es **la única salida**. Queda escrito como hallazgo; aquí no se diseña nada.

---

## Topes de reloj y pool continuo · declarados el 2026-10-25 ANTES de aplicarlos

**Pool continuo.** La primera versión paralela repartía por olas de 4 000 con un pool nuevo por ola, así que al final de cada ola los demás trabajadores esperaban al más lento. En n=8 el más lento medido lleva **1 080 s**, de modo que la espera no era despreciable. Se sustituye por una **ventana fija de 32 futuros pendientes que se rellena en cuanto uno termina**: el pool no se queda vacío nunca. Vuelto a probar: 200 índices de n=4 recalculados con el corredor nuevo, **idénticos campo a campo**.

**Dos topes, que son logística y no ciencia, con su coste epistémico dicho.**

1. **Tope por sistema: 900 s.** Un sistema que lo pase se registra en la clase **`sin terminar por reloj (900 s)`**, que **cuenta en el denominador como no identificado** y se **excluye de los estadísticos de coste**, porque su coste es un corte y no una medida. Consecuencia que hay que decir: es la **única clasificación no determinista** de la campaña, porque depende del reloj de la máquina. Por eso los índices afectados **se listan en el artefacto**, y una corrida posterior puede acabarlos sin tope.
2. **Tope de sesión: 4 h** para el tramo pendiente. Al pasarlo se deja de **enviar** sistemas nuevos y los en vuelo terminan. Los no enviados **no se clasifican**: quedan sin medir, y entonces la muestra de ese n pasa a ser un **prefijo del orden canónico**, que está sesgado —los índices bajos tienen n_min más bajo y coste menor, medido en los deciles de n=6: de 7,6 a 250 ms/sistema—. **Todo número que salga de una muestra así lleva esa advertencia**, y el cierre no informa ninguna cifra de n=8 sin ella.

**Lo que los topes no hacen.** No descartan en silencio y no seleccionan contra la cola: el cortado aparece como clase propia y en el denominador, y el no enviado aparece como muestra incompleta y declarada. La cola es parte de la respuesta de la fase y sigue contándose.

**Asimetría que hay que declarar:** los **3 998** sistemas de n=8 medidos antes de esta decisión corrieron **sin tope**. Los que vienen corren con tope de 900 s. Si alguno se corta, la comparación entre las dos mitades de la muestra no es homogénea y el cierre lo dirá con el número de cortados.

**El cambio en el código es sólo de agregación**, no de medida: `resumen` y `puerta` aprenden a tratar la clase nueva, y las funciones que miden quedan **byte a byte idénticas** — comprobado por el sha256 del código fuente de `un_sistema`, `vivir_una_vida`, `minimizar`, `canonica` y `cociente` antes y después del cambio (`9b4a1191b235a5d4…`, `1166200c4db8090a…`, `80f45db900d5a93f…`, `414299c8507ba62d…`, `4b44c0ad326ed6c3…`). Las 179 103 filas ya medidas siguen válidas.

---

## Recorrido esparcido y parada por información · declarados el 2026-10-25

**El sesgo de prefijo, medido y no supuesto.** Partiendo n=4 y n=6 completos en tercios del orden canónico, la identificación **a igual n_min** difiere entre el primer tercio y los otros dos en **17 a 28 puntos porcentuales, en todos los estratos**:

| n | n_min | tercio 1 | tercio 2 | tercio 3 | rango |
|---|---|---|---|---|---|
| 4 | 2 | 90,1 % | 62,8 % | 65,9 % | 27,3 pts |
| 4 | 3 | 77,9 % | 55,5 % | 54,7 % | 23,2 pts |
| 4 | 4 | 74,9 % | 47,9 % | 46,8 % | 28,1 pts |
| 6 | 2 | 89,8 % | 62,8 % | 71,8 % | 27,0 pts |
| 6 | 4 | 68,4 % | 50,1 % | 53,0 % | 18,3 pts |
| 6 | 6 | 58,7 % | 41,3 % | 43,6 % | 17,4 pts |

No es sesgo de **composición** —eso también lo hay, los índices bajos tienen n_min más bajo—, es sesgo **a igual n_min**: el principio del orden canónico es genuinamente más fácil, y el sesgo se concentra en el primer tercio (los tercios 2 y 3 se parecen entre sí). Consecuencia directa: el 81 % de identificación del prefijo de n=8 está inflado, y la cifra verdadera estará más cerca de la tendencia 69,4 → 62,6 → 58,1.

**Lo que se cambia, y lo que no.** Se cambia **el orden en que se recorren los índices pendientes**: permutación por **inversión de bits del rango**, determinista y sin azar. **No** se cambia el conjunto 1-de-k declarado, ni L, ni la salida observable, ni la puerta, ni `un_sistema`, y cada fila sigue llevando su `idx`. Verificado: la permutación es exacta para M ∈ {10, 1000, 28148}, y cualquier prefijo del recorrido —5 %, 13 %, 26 %— se reparte **33,4 / 33,3 / 33,3** entre los tercios del espacio. Vuelta a probar la identidad de la medida con el corredor nuevo: idéntica campo a campo.

**Consecuencia para el informe:** n=8 queda con **dos estratos declarados que no se mezclan**: el **prefijo canónico** ya medido (los primeros 6 240 índices, 22,2 %, sesgado al alza) y el **tramo esparcido** (aproximadamente uniforme). El cierre informa los dos por separado y usa el esparcido para cualquier afirmación sobre n=8.

**E-18 · criterio de parada por información, declarado antes de aplicarlo.** Por bloques de **1 000** sistemas del tramo esparcido se calculan la identificación por `n_min` y la proporción de clases. Cuando **dos bloques consecutivos** difieran menos de **3 puntos porcentuales** en **todos** los estratos con más de **50** sistemas y en las proporciones de clase, el corredor **se detiene solo**: ha dejado de aprender y seguir sólo gasta la máquina. Si los pendientes se acaban antes, mejor.

**Parada limpia.** Al detenerse —por E-18 o por tope—, se **cancelan los futuros encolados sin empezar** y sólo se espera a los que ya corrían. Eso arregla el defecto de la versión anterior, donde la ventana de 32 podía arrastrar un drenaje de hasta 32/4 × 900 s = 2 h.

**El reloj de sesión se reinicia con el relanzamiento**, y se dice: el tope de 4 h pasa a ser el respaldo, y la regla de parada principal es ahora E-18.

---

## Segunda variante de cobertura · n=6 con la vida de n=8 · declarada el 2026-10-26

**Por qué hace falta, y por qué pone en duda lo que ya escribí.** Estratificando por `n_min` —la única comparación que no mezcla dificultad con estructura— la identificación resulta **plana en n** para n=3, 4 y 6: 76,7 / 76,3 / 77,1 % en `n_min`=2; 63,8 / 62,7 / 65,3 % en `n_min`=3; 54,5 / 57,1 % en `n_min`=4. La caída de la tasa cruda (69,4 → 62,6 → 55,6 %) era **enteramente composición**: los mundos grandes tienen `n_min` grande.

Pero n=8 **salta a 76–82 % en todos los estratos**, y lo hace junto a un colapso de la transitoriedad: con umbral **relativo** (visitas por debajo del 10 % de la media del propio sistema), los estados alcanzables infravisitados son **13,7–18,2 %** en n=3/4/6 y **0,6–3,5 %** en n=8. Esos 14–18 puntos son del mismo orden que la distancia al techo de n=8.

La diferencia entre n=6 y n=8 no es el tamaño del mundo —a igual `n_min` los conjuntos alcanzables son casi iguales: 4,38 frente a 4,53 estados— sino **la longitud de la vida**: 3 586 pasos frente a 18 434, que son 598 frente a 2 304 pasos por estado del mundo.

**Lo que esto le hace a una conclusión mía.** Escribí, con la primera variante, que la fracción no determinada es «invariante a la longitud de la vida». Esa variante añadía **una sola letra** (258→642 y 642→1538 pasos) y no movió nada. Pero n=8 vive **71 veces** la vida de n=3. Una invariancia medida en un factor 2,5 no autoriza a hablar de invariancia en un factor 71, y yo lo hice.

**El test decisivo:** correr **n=6 con L = 10**, la vida de n=8 (18 434 pasos), sobre una submuestra estratificada por `n_min` y declarada. Mismo tamaño de mundo, misma salida observable, mismo aprendiz, mismo tope; **sólo cambia cuánto se vive**.

**Predicción, escrita antes de correr, y contraria a lo que afirmé antes.** La identificación de n=6 a igual `n_min` **sube** hacia el entorno del 75–80 % y la transitoriedad relativa **baja** por debajo del 5 %. Es decir: el hueco de ~20 puntos es **transitorio** y lo cura vivir mucho más, no un poco más.

**Falsador:** que la identificación de n=6 con L=10 se quede en 47–57 % como con L=8. Eso diría que el salto de n=8 no es de la vida y hay que buscarlo en la estructura de su muestra, y entonces sí quedaría en pie que el límite es de itinerario.

**Lo que está en juego.** Si la predicción acierta, el argumento de la Fase 2 cambia de forma: elegir qué vivir dejaría de ser «la única salida» y pasaría a ser **la salida barata** frente a vivir muchísimo más, lo cual es una afirmación distinta y más débil. Si falla, el argumento queda como estaba. En los dos casos, la parte que **no** se cura es la recurrente, y ésa es la que define el objetivo de la Fase 2.
