# CIERRE DE LA FASE 1 · escalar sin azar

**Fecha:** 2026-10-26 · **Árbol:** `experiment/unidad-minima-01` · **Base:** `master` = `bc05def` · **Cómputo:** 16,85 h de CPU sobre 184 686 mundos

---

## 0 · El veredicto, en cuatro líneas

**La puerta da FAIL**, en el criterio de coste (iii), y no se suaviza. La unidad de 02 **identifica bien y a coste impracticable**: su trabajo mediano es una pasada de la vida, y su cola llega a **132 573 veces la vida** en el peor mundo.

**Y la fase entrega dos resultados que valen más que la puerta**: una ley estructural sobre qué mundos puede aprender una vida no elegida, y la constatación de que **más vida no compra cobertura**.

**Y un error de muestreo mío invalida n=8** como estimación de su banco. Eso se explica en §6 y es la razón por la que esta fase no tiene cuarto punto de escala.

---

## 1 · Lo que se midió

| n | banco | medidos | vida | con distinción | identificados | no determinados |
|---|---|---|---|---|---|---|
| 3 | 729 | **729 (completo)** | 258 | 530 | 368 · 69,4 % | 162 · 30,6 % |
| 4 | 65 536 | **65 536 (completo)** | 642 | 51 222 | 32 040 · 62,6 % | 19 182 · 37,4 % |
| 6 | 2 176 782 336 | 108 840 · 1-de-20 000 | 3 586 | 86 361 | 48 052 · 55,6 % | 38 309 · 44,4 % |
| 8 | 281 474 976 710 656 | 9 581 · **muestra inválida, §6** | 18 434 | 1 793 | 78,3 % | — |

Determinismo: sin `random`; dos corridas del banco completo de n=3 difieren **sólo** en el campo del reloj de pared. Python 3.14.4.

---

## 2 · La ley: lo que decide si una vida no elegida basta

**Si las dos letras son permutaciones de la parte alcanzable, la identificación es 100 %. Cero excepciones en 2 037 mundos**, de los cuales 1 200 vienen de los bancos completos de n=3 y n=4, que no tienen muestreo y por tanto no tienen el defecto de §6.

El gradiente, a igual `n_min`, es monótono:

| estructura de las letras | identificación |
|---|---|
| ninguna es permutación | 46–70 % |
| sólo B es permutación | 61–71 % |
| sólo A es permutación | 68–80 % |
| **las dos son permutaciones** | **100 %** |

Dicho en una frase: **lo que decide si una sola vida basta es si el mundo destruye información.** Una letra que no es inyectiva colapsa estados, y lo colapsado no se recupera recorriendo más.

**Es un reencuentro, no un hallazgo**, y así se presenta. Angluin probó en 1982 (*Inference of Reversible Languages*, JACM 29:741–765) que los lenguajes reversibles son identificables **sólo con ejemplos positivos**; una vida sin maestro es exactamente un flujo de positivos. Y la dicotomía permutación/reset es clásica desde Ginzburg (1968). Lo nuestro es la misma ley medida en nuestro objeto, con la unidad que teníamos.

**Una asimetría que no habría adivinado:** a `n_min`=2, tener **B** reversible *empeora* (−21,5 puntos en n=4, −18,2 en n=6). En esos mundos B es la letra que escribe, y su irreversibilidad es justamente lo que hace observable la distinción. Las dos letras no son intercambiables.

---

## 3 · Más vida no compra cobertura

La fracción no determinada crece con n (30,6 % → 37,4 % → 44,4 %) y **no se mueve al alargar la vida**, probado en dos rangos:

| prueba | vida | resultado |
|---|---|---|
| n=3, una letra más | 258 → 642 pasos | **0 de 162** se resuelven |
| n=4, una letra más | 642 → 1 538 pasos | **6 de 19 182** se resuelven (0,03 %) |
| n=6, la vida de n=8 | 3 586 → 18 434 pasos | **0 cambios**, en los cinco estratos de `n_min`, ni un decimal |

La tercera prueba es la que importa: **cinco veces más vida, cero efecto.** Y no es un bug: verificado que la vida larga se usa (`trabajo` 18 594 frente a 3 746 en el mismo mundo) y que el sistema termina con los mismos estados y sigue sin identificarse.

Informado contra la **longitud de vida** y no contra n, que es lo que separa los ejes: a igual vida (642 pasos) n=3 da 30,6 % y n=4 da 37,4 %; a igual n, duplicar o quintuplicar la vida no mueve nada.

**Corregido el 26-oct · la cobertura la fija el par mundo × itinerario, no el mundo.** Escribí «la fija el mundo» y era de más. Las tres pruebas de arriba alargan **el mismo** itinerario shortlex, así que lo único que prueban es que *más de lo mismo* no sirve. Y hay evidencia de que **otro** itinerario sí cambia qué mundos se identifican: el mutante de vida invertida de esta misma fase mostró que **54** de los 567 mundos identificados hacia delante dan otra máquina hacia atrás, y en los 54 la unidad aprendió la mínima de la traza que de hecho vivió. Un itinerario distinto identifica mundos distintos.

Eso cambia lo que §3 concluye. No dice «este mundo es inaprendible desde una vida»; dice **«esta unidad no elige qué vivir»**. Y ésa sí es la pregunta de la Fase 2.

**Y la escala no degrada.** Estratificando por `n_min` —la única comparación que no mezcla dificultad con estructura— la identificación es **plana** en n: 76,7 / 76,3 / 77,1 % en `n_min`=2 y 63,8 / 62,7 / 65,3 % en `n_min`=3 para n=3/4/6. La curva decreciente de la tabla de §1 era **composición**: los mundos grandes tienen `n_min` grande. Esto corrige lo que yo mismo informé como curva de escala durante la corrida.

---

## 4 · El FAIL: la cola de coste

El trabajo real por paso de vida, en los tres n de muestra válida:

| n | p50 | p90 | p99 | máximo |
|---|---|---|---|---|
| 3 | 1,15 | 2,22 | 5,5 | 9,0 |
| 4 | 1,17 | 5,51 | 25,4 | **185,8** |
| 6 | 1,86 | 88,96 | 1 485 | **132 573** |

La mediana se queda en una pasada de la vida; el máximo se multiplica por **14 730** entre n=3 y n=6. El criterio (iii) exigía máximo ≤ 100× y **falla en n=4 y revienta en n=6**. En n=8, 35 mundos de 6 032 consumieron el **80 %** del cómputo, y 37 mundos agotaron el tope declarado de 900 s.

**El criterio de muerte que escribí estaba sobre la mediana, que es exactamente donde esto no se ve.** Lo digo porque es el tipo de error que el banco entero no habría detectado.

**La cola tiene nombre y estaba en la literatura antes de que la midiéramos.** Hallar la máquina mínima consistente con los datos es NP-difícil (Gold 1978, *Information and Control* 37:302–320; Angluin 1978, ibíd. 39:337–350) y **no aproximable dentro de ningún polinomio** (Pitt & Warmuth 1993, *JACM* 40:95–142). La cola no es un defecto de implementación: es **el precio de exigir el mínimo exacto sin maestro**. Por eso la fase no declara PASS por la mediana y nombra la cola como su problema abierto.

---

## 5 · Los controles, limpios

- **No sobrefragmentación:** en los 36 992 mundos con `n_min`=1 —inertes bajo esta salida— la unidad abrió **cero** distinciones y terminó con **un** estado. Sin excepciones.
- **Cruce contra el retroceso exhaustivo de 01:** los **19 344** mundos no coincidentes de n=3 y n=4 cruzados uno a uno, **19 344/19 344 de acuerdo**, cero discrepancias. Era el falsador de la reparación del clasificador y no se cumplió.
- **Futuro:** perfecto en 729/729 (n=3), 65 512/65 536 (n=4) y 108 837/108 840 (n=6).
- **Mutantes del gate:** el memorizador falla la identidad en 729/729; el ciego a la observación falla en los 530 con distinción y no abre ni una distinción; el oráculo pasa 729/729. El gate puede fallar, que es lo que lo hace criterio.

**Los 24 mundos de n=4 con futuro imperfecto son un solo fenómeno.** Todos con `n_min`=4, todos aprendiendo 4 estados, todos fallando **exactamente 6 de 896** pasos, todos sobre la letra B y todos prediciendo 0 donde la realidad es 1. La diferencia entre la máquina aprendida y la verdadera es **una sola transición y dónde vive**: el único «B reacciona 0» está domiciliado en otro estado. No es una máquina equivocada, es la misma estructura con un domicilio distinto.

**Añadido el 26-oct · con una letra más de vida se identifican 6 de los 24**, y son exactamente los mismos seis índices (25868, 29954, 42544, 44545, 64800, 65028) que la variante de cobertura resolvió en toda la clase de 19 182. Es decir: los únicos seis mundos de la clase «dos máquinas del mismo tamaño» que una letra más de vida resuelve son precisamente seis de estos veinticuatro.

**Y la lección, que es la definición operativa de la clase recurrente:** la palabra que separa las dos máquinas, `AABAABB`, **ya está en la vida** con L=7 — se recorre nueve veces, desde tres estados distintos — y dieciocho de los veinticuatro siguen sin identificarse. *Una palabra separadora presente en la vida no es experiencia si no se ejecuta desde el estado que discrimina.* En una vida sin reset no se elige desde dónde se la recorre, y eso es exactamente lo que la Fase 2 va a atacar.

---

## 6 · Los dos datos de n=8 que no sabía explicar, y su explicación

Durante la corrida informé dos cosas de n=8 que no cuadraban y dije que no las sabía explicar:

1. **n=8 identificaba 20 puntos por encima de n=6 a igual `n_min`** (81,3 % frente a 57,1 % en `n_min`=4), con mundos del mismo tamaño alcanzable (4,53 frente a 4,38 estados).
2. **Su tasa era plana en `n_min`** —76 a 82 % desde `n_min`=2 hasta `n_min`=8— en vez de decreciente como en n=3, n=4 y n=6.

**Las dos tienen la misma causa, y es un error mío de muestreo.** El banco se indexa como `2n` dígitos en base `n`, y la submuestra se tomó como `range(0, total, k)` con `k` elegido por ser un número redondo del presupuesto de reloj. Para n=8, `k = 10¹⁰ = 2¹⁰·5¹⁰`, y `2¹⁰ = 1024 = 2·8³`: **todo índice muestreado es múltiplo de 8³**, así que los tres últimos dígitos base-8 son cero. En los 28 148 mundos del conjunto, **`B[5] = B[6] = B[7] = 0` siempre**, y `B[4]` toma 4 de 8 valores. **Cuatro de las dieciséis entradas de las tablas están restringidas.**

Con tres de los ocho estados mandando a 0 bajo B, esos mundos colapsan hacia el estado 0 y son estructuralmente **mucho más simples** que un mundo de ocho estados cualquiera. De ahí el salto y de ahí la planitud. **No era un hallazgo sobre la escala: era mi muestra.**

Demostrado de las dos formas, aritmética y empíricamente sobre mil rangos repartidos por todo el conjunto. Y el alcance exacto del daño:

| n | muestreo | entradas restringidas | estado |
|---|---|---|---|
| 3 | banco completo | — | **limpio** |
| 4 | banco completo | — | **limpio** |
| 6 | 1-de-20 000 | 1 de 12 (`B[5]` con 3 de 6 valores) | **asterisco**: el efecto es menor y acotado |
| 8 | 1-de-10¹⁰ | 4 de 16 | **inválido como estimación del banco** |

**Qué sobrevive:** todo lo de §2 a §5 que no dependa de n=8. La ley de reversibilidad se sostiene sobre 1 200 mundos de banco completo. La planitud por `n_min` se sostiene sobre n=3, n=4 y n=6. La cola se sostiene sobre n=3, n=4 y n=6. La invariancia a la longitud de vida se probó en n=3, n=4 y n=6, no en n=8.

**Qué no sobrevive:** cualquier afirmación sobre mundos de ocho estados. La fase se queda con **tres** puntos de escala, no cuatro.

---

## 7 · La partición que define la Fase 2 y la Fase 3

**Corregido el 26-oct · el criterio pasa a ser estructural, sin umbral.** Un estado es **transitorio** si por debajo de él hay **ida sin vuelta**: existe otro estado alcanzable desde él desde el que no se puede volver. Es una propiedad del mundo, no de cuánto se lo visitó, y no necesita ningún umbral — que es lo que hacía frágil la versión anterior (E-25: un umbral absoluto no es comparable entre vidas que difieren ×71, y el relativo seguía siendo una elección mía).

Medido sobre los **bancos completos** de n=3 y n=4, que no tienen muestreo ni defecto posible — porcentaje de mundos **con al menos un transitorio estructural**:

| clase | n=3, n_min 2 / 3 | n=4, n_min 2 / 3 / 4 |
|---|---|---|
| **admite una máquina menor** | — / **100 %** | **100 % / 100 % / 100 %** |
| dos máquinas del mismo tamaño | 95,8 / 58,1 % | 94,1 / 57,9 / 32,9 % |
| identificados | 20,2 / 6,3 % | 23,6 / 10,8 / 5,3 % |

**No es correlación, es identidad:** la clase «la vida admite una máquina menor» es, en los dos bancos completos y en todos sus estratos, **exactamente** la clase de mundos con una puerta de ida sin vuelta. Si el mundo no devuelve, la vida no fuerza la distinción. El conteo de visitas queda como descriptor secundario, no como criterio.

(Como descriptor: con umbral relativo al 10 % de la media del propio sistema, n=3, n=4 y n=6 tienen 13,7 a 18,2 % de estados alcanzables infravisitados, fracción constante en n y en `n_min`.)

Eso parte la no identificabilidad en dos, y las dos partes tienen dueños distintos:

- **Recurrente.** El mundo visita el estado muchas veces y la unidad sigue sin separarlo. No lo cura vivir más: probado a factor 2,5 y a factor 5, cero efecto. **Es el objetivo de la Fase 2**: elegir qué vivir.
- **Transitoria.** La unidad apenas estuvo allí. Queda documentada como **lo que una sola vida no puede aprender por mucho que dure**, y es el argumento de la Fase 3: si una vida no alcanza, hacen falta más vidas — copiarse.

---

## 8 · Lo que la fase gastó, y en qué

**16,85 h de CPU** sobre 184 686 mundos. Repartidas con honestidad:

- **Experimento:** el banco, la verdad de referencia por refinamiento de particiones, la comparación salvo isomorfismo, los cuatro mutantes, y cinco análisis derivados (cobertura, estructura cíclica, transitoriedad, vida larga, retículo de muestreo).
- **Instrumento:** una corrida nula completa tirada (0,18 h, barata **porque estaba rota**), dos paralelizaciones con su prueba de identidad cada una, y siete defectos míos corregidos.
- **Custodia:** tres commits, el registro y las fichas.

**El coste real de un instrumento defectuoso no fue la CPU, fueron las afirmaciones falsas.** Dije que el mecanismo incremental era incompleto —falso, comparaba dos configuraciones distintas—; informé una curva de escala decreciente que era composición; informé una invariancia sin su rango; e informé dos anomalías de n=8 como hallazgos cuando eran mi muestra. Las cuatro las corregí yo, ninguna llegó a un entregable, y las cuatro están en el registro.

**El registro pasó de 14 a 27 entradas.** Nueve son mías: E-20 a E-27, más E-15 a E-17. Cuatro tienen guarda mecánica ya implementada.

---

## 8-bis · Qué guardas saltaron, y cuáles callaron

La libreta no se mide sola. Esto es lo que de verdad hizo en la Fase 1.

**Saltaron, con su cuenta:**

| guarda | veces | qué atrapó |
|---|---|---|
| **E-05** · la ficha no es final hasta pasar sus mutantes | **6** | cuatro criterios mal escritos en la Fase 0; el de la vida invertida, que confundía «el mecanismo depende del orden» con «la vida invertida es otra experiencia»; y M-5 de n=8, que preguntaba por el mundo cuando el tope depende de lo que la traza fuerza |
| **E-15** · mutantes que ejerciten el instrumento | **1** | es la razón de que existan M-4, M-5 y M-6; M-5 atrapó un criterio mío antes de la corrida real |
| **E-12** · toda cifra con su comando | **1** | reproduje las cifras del criterio estructural en vez de copiarlas: coincidieron, pero la guarda es que se comprueba |
| **E-03** · cada número de la puerta con su campo | continua | los tres veredictos los calculó el programa leyendo campos, nunca yo a ojo |
| **E-07** · sin azar, dos corridas un hash | continua | el único campo que difiere entre corridas es el reloj de pared |

**Callaron, y hay que decirlo:** ninguna de mis **once** entradas nuevas de estos dos días fue **prevenida** por la libreta. Todas eran clases nuevas y se anotaron después. La libreta impide la segunda vez, no la primera.

**Y hay un patrón en dónde callaron.** Clasificados los 30 errores del registro en tres clases —*criterio* (mal pedido), *instrumento* (mide otra cosa), *banco de trabajo* (comando suelto)—, mis once se reparten casi todos en **instrumento** y **banco**. Es decir: **el método de fichas y mutantes funciona para el criterio y no llega a lo que ocurre entre fichas.** Tres de mis errores —el `pkill` que se mató a sí mismo, la tubería que se tragó cuarenta minutos de salida y el «ninguno» sobre una lista vacía— ocurrieron en comandos sueltos, donde ninguna ficha se abre y ninguna guarda se lee.

De ahí sale el `guardas.py` de §5 del paquete de orientaciones: las guardas de banco de trabajo **no se leen, se importan**, porque una guarda que vive en código actúa aunque nadie abra la libreta.

## 9 · La reparación única: 1-bis, abierta

La regla de cierre permite una reparación. No es tocar 02: es cambiar de mecanismo y medir qué cuesta. **Fusión de estados polinómica, sin maestro y sin reset** (RPNI, Oncina & García 1992; EDSM, Lang, Pearlmutter & Price 1998; MooreMI, Giantamidis & Tripakis 2016). Gate y ficha escritos.

Lo que se suelta y lo que se conserva, dicho en una línea: **se suelta la minimalidad exacta; se conservan sin maestro y sin reset.** Por Pitt & Warmuth ningún mecanismo polinómico puede conservar la exactitud, así que el intercambio está declarado con números **antes** de correr: máximo de trabajo/vida ≤ 50 y p99 ≤ 10, a cambio de no más de **15 puntos** de identificación perdidos, comparado **pareado por índice** contra la fila de 02 del mismo mundo.

Y un detalle estructural que decide el diseño: con una sola vida sin reset, los prefijos no forman un árbol sino **un camino**. La fusión va sobre un camino, que es el caso degenerado del marco rojo-azul.

`hW` de AALpy queda fuera: aprende **actuando para preguntar**, y eso es la Fase 2, no un cambio de aprendiz.

---

## 10 · Una sola pregunta para Wis

n=8 hay que rehacerlo con una muestra sin retículo, y eso cuesta otra campaña. **¿Se rehace ahora, antes de 1-bis, o se cierra la Fase 1 con tres puntos de escala y n=8 se mide ya con el mecanismo de 1-bis, que es polinómico y lo haría mucho más barato?**
