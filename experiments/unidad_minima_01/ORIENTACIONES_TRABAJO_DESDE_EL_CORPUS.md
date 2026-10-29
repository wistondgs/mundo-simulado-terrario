# Trabajo · ocho piezas que salen de la biblioteca de Wis y qué se construye con cada una

**Fecha:** 2026-10-28 · **Para:** Opus 5.5 · **De:** Fable, tras leer los textos (no los títulos) · **Adjudica:** Wis.
**Revisión externa del 28-oct incorporada:** tres correcciones (Wolf: información condicionada al mundo, no marginal; Hartmanis: congruencia trasladada por el isomorfismo, no cualquier congruencia; Mitchell: recuperación y anticipación son dos medidas). Y una distinción que rige el documento: **retener información, conservar una capacidad y desarrollar una capacidad nueva son tres fenómenos distintos**; Wolf mide el primero, Hartmanis la materia prima del segundo, Harlow el tercero, y ninguno vale por los otros.

Cada pieza es un **experimento o un órgano** de la unidad: qué mecanismo da la fuente, qué se construye, qué se mide, qué se predice, qué lo controla, y cuándo entra. Nada de esto reemplaza a C5 y los seis mutantes; dice qué va después y qué puede correr ya sobre lo que existe.

---

## 1 · La medida de Harlow: la curva a lo largo de vidas, no dentro de una vida

**Lo que da la fuente (Harlow 1949, `ADOA-080`).** Monos resolviendo cientos de problemas del mismo tipo: en los primeros 100 problemas no dominan ninguno; con la experiencia, el acierto **en el segundo ensayo** de cada problema nuevo sube de 50 % a 95 %. «La información del ensayo uno bastaba.» El aprendizaje por tanteo se vuelve inmediato **entre problemas**, no dentro de uno.
**Qué se construye.** El protocolo de la cadena: la unidad vive una **serie** de mundos nuevos, uno tras otro, sin aviso de cambio. La medida de desarrollo es la **exactitud en los primeros 64 pasos del mundo k** como función de k. Dos series: (a) **cascadas compatibles** (W₁, W₁+cerrojo, +cerrojo, …), donde la máquina puede heredarse; (b) **mundos de 3 estados sin relación** (la serie de Harlow), donde la máquina no sirve y sólo pueden transferirse **disposiciones** (ventana, elegir, confianza en lo heredado).
**Predicción.** En (a) la curva sube si C5 funciona. En (b) la curva de la unidad actual es **plana** (no tiene nada que transferir entre mundos ajenos): ése es el resultado que dice qué órgano falta para un *learning set*. Control: fresca en cada mundo, plana por construcción.
**Cuándo.** Es el **marco de la fase siguiente**; se construye en cuanto C5 cierre, sobre `08`. Sin esto, «de poco en poco» no tiene curva.

## 2 · La variable esencial de Ashby: beneficio y peligro sin recompensa

**Lo que da la fuente (Ashby 1960, `ADOA-001`, cap. 7 y 8).** Un sistema **ultraestable** tiene variables esenciales con límites, y parámetros que cambian **a saltos** (funciones escalón) sólo cuando una esencial sale de sus límites; el cambio de parámetro cambia el campo de comportamiento hasta que la esencial vuelve a su zona. Nada le dice al sistema qué está bien: lo único innato son los límites.
**Qué se construye.** La unidad recibe **una variable interna V** que el mundo mueve (ciertas reacciones la bajan, ciertas palabras la reponen; regla fija por mundo, desconocida para la unidad) y **V entra en lo observado**: la unidad modela su propia V como un bit más del mundo. Lo único innato: si V sale de sus límites, un parámetro de disposición cambia a salto por una lista fija (orden de letras del itinerario, elegir on/off, ventana); si V llega a cero, la vida termina.
**Qué se mide.** (i) **Peligro descubierto:** ¿la máquina de la unidad predice qué palabras bajan V? (ii) **Riesgo:** en los empates entre hipótesis, ¿cuántas veces una rama baja V, y la unidad la ejecuta o no? (iii) Vidas completadas frente a una unidad con V inerte.
**Predicción.** La unidad que modela V predice sus caídas antes que el reactivo; el salto de parámetro ocurre sólo cuando V sale de límites (contador; cero ⇒ nulo). Control: V inerte (nunca sale de límites) ⇒ cero saltos y misma identificación que hoy.
**Cuándo.** **Fase 3** (beneficio/peligro/riesgo), después de la cadena. Es el mecanismo determinista más viejo y más probado que existe para esto, y estaba en casa.

## 3 · La anticipación de Mitchell: el libro de dos páginas

**Lo que da la fuente (Mitchell et al. 2009, `HD-009`).** *E. coli* expuesta siempre a lactosa y después maltosa **pre-induce** los genes de maltosa al ver lactosa; la anticipación mejora la aptitud, y **se pierde** en cepas evolucionadas sólo con el primer estímulo. La secuencia temporal del entorno queda grabada en el cableado.
**Qué se construye.** La unidad vive W₁ → W₂ → W₁ → W₂ … con cambios sin aviso. El linaje conserva **dos máquinas** (dos páginas). Hay **dos capacidades distintas** y se miden por separado *(corregido el 28-oct tras revisión externa: yo las había mezclado)*:
- **Recuperación:** al primer error tras el cambio, la unidad cambia de página en vez de reaprender. Medida: errores entre el cambio y la página correcta.
- **Anticipación** (lo que Mitchell mide en *E. coli*): la unidad cambia de página **antes del primer error**, usando una regularidad temporal aprendida: el número de pasos desde el último cambio, o una palabra-señal que el mundo emite antes de cambiar (en Mitchell, la lactosa anuncia la maltosa). Medida: cambios de página correctos **sin error previo**, y falsos cambios.
**Qué se mide.** Las dos curvas como función del número de ciclos. Y la **pérdida**: tras n ciclos de sólo W₁, ¿la página W₂ se poda y la anticipación desaparece antes que la recuperación?
**Predicción.** La recuperación aparece en el segundo ciclo; la anticipación sólo si el período es regular, y aparece más tarde; la pérdida sigue a los ciclos sin uso. Control: período variable determinista (1, 2, 3 vidas): la anticipación debe degradarse y la recuperación no.
**Cuándo.** Entra con **C5 certificado**, porque necesita heredar máquina sin traza. Es la forma más chica del «libro del linaje».

## 4 · La medida de Wolf: cuántos bits del pasado hay en la conducta

**Lo que da la fuente (Wolf et al. 2008, `HD-005`).** Marco informacional para medir memoria **sin conocer el mecanismo**: cuánta información sobre la historia de la célula está codificada en su respuesta presente, y cuánto persiste.
**Qué se construye.** *(Corregido el 28-oct tras revisión externa: yo había escrito «una fresca da 0 bits por construcción», y es falso: W₂ se genera desde W₁, así que la conducta de cualquier unidad en W₂ lleva información sobre W₁ aunque nunca lo haya vivido. Medir I(W₁; conducta) mide la correlación entre mundos, no la herencia.)* Lo que se mide es la información **condicionada al mundo**: para un mismo W₂, se hacen variar las **historias previas** y se mide I(historia; conducta en W₂ | W₂). Historias: ninguna (fresca), vida en W₁ con el itinerario fijo, vida en W₁ con el itinerario invertido (A↔B), vida en W₁ corta (64 pasos), vida en **otro** W₁′ sin relación con W₂. Conducta: predicciones de los primeros 64 pasos y palabras ejecutadas. Sobre las filas existentes sólo hay dos historias (ninguna y W₁ fija): sirven para la primera versión; las otras tres exigen una corrida corta, pareada, en los mismos W₂.
**Qué se mide.** Bits de **historia** en la conducta, dado el mundo, por clase y por brazo; y aparte, como descriptor, la correlación entre mundos que la fresca ya muestra.
**Predicción.** Fresca: 0 bits condicionados, por definición (una sola historia). Heredera con traza: > 0 en las dos clases (la historia se nota aunque estorbe). C5: > 0 en la componible con exactitud mayor que la fresca (información **útil**), y en la control bits > 0 **con** exactitud menor (información **que estorba**): es la distinción entre retener información y conservar una capacidad, que el revisor pide separar y que esta medida separa justamente al cruzarla con la exactitud.
**Cuándo.** **Ya**, la primera versión sobre artefactos existentes; la versión con cinco historias, tras C5 (misma corrida que la pieza 5).

## 5 · La ventana de Lambert y Kussell: la memoria óptima depende del entorno

**Lo que da la fuente (Lambert & Kussell 2014, `HD-006`).** Dos memorias no genéticas en *E. coli*; la **ventaja de cada una depende de la escala temporal de la fluctuación** del entorno: una sirve si el entorno cambia cada 1–10 generaciones, la otra si cambia en menos de una. Hay una memoria óptima para cada ritmo.
**Qué se construye.** En `08`, la ventana (hoy 512 a ojo) y el período de cambio de mundo como **variables cruzadas**: ventana ∈ {64, 128, 256, 512, 1024} × período ∈ {128, 256, 512, 1024, 2048} pasos. Luego el órgano: la ventana **se ajusta a saltos** (la función escalón de Ashby, pieza 2) según los olvidos acumulados.
**Qué se mide.** Alcance en la curva por celda; **dónde está el máximo** de la ventana para cada período.
**Predicción.** El máximo se desplaza con el período (ventana corta para cambios rápidos, larga para lentos); si no se desplaza, la ventana no es una variable del ser sino un detalle del instrumento, y se dice. Control: mundo que **no cambia**, donde la ventana más larga debe ganar siempre.
**Cuándo.** Inmediatamente después de C5, en el mismo script. Es lo que convierte «512 a ojo» en «512 medido».

## 6 · La descomposición de Hartmanis: mitosis sobre lo que ya está guardado

**Lo que da la fuente (Hartmanis 1962, raíz del corpus).** Toda realización **sin bucles** de una máquina a partir de máquinas menores corresponde a un conjunto de **particiones con propiedad de sustitución** (congruencias) cuyo producto es la partición cero, y al revés; el orden entre ellas describe el **flujo de información** entre componentes.
**Qué se construye.** Análisis sobre las máquinas **ya serializadas** de `08` (clase componible), **sólo sobre las identificadas**, porque ahí existe el isomorfismo canónico entre la máquina aprendida y la verdadera, y con él la congruencia generadora de W₁ (la proyección (x, b) ↦ x) se **traslada estado a estado** a la máquina aprendida *(precisado el 28-oct tras revisión externa: sin esa correspondencia demostrada, «aparece una congruencia» no dice nada)*. Entonces: (i) ¿la partición trasladada tiene la propiedad de sustitución en la máquina aprendida? (ii) ¿las componentes (el cociente y el resto de la cascada) **predicen por separado** su parte del futuro fijo? (iii) ¿cuántas otras congruencias tiene la máquina aprendida que la verdadera no tiene (estructura espuria)? En la clase control la proyección **no** debe ser congruencia.
**Qué se mide.** Fracción de máquinas identificadas donde la congruencia generadora se conserva; exactitud de cada componente en su cociente; número de congruencias espurias.
**Predicción.** Componible: la congruencia generadora se conserva en el 100 % de las identificadas (si no, el isomorfismo o el generador tienen un defecto); control: en casi ninguna. **Lo que esto demuestra y lo que no:** demuestra que la estructura del mundo está **en** la máquina aprendida y es separable; **no** demuestra que la unidad la use ni que pueda partirse a sí misma. Eso es la Fase 3, y esta pieza sólo dice si tiene materia prima.
**Cuándo.** **Ya**, como análisis; es la prueba previa a la Fase 3 y no cuesta una corrida.

## 7 · La escalera de PAIRED y ACCEL: el siguiente mundo es el de máximo arrepentimiento

**Lo que da la fuente (Dennis et al. 2020, `WORLD-REF-017`; Parker-Holder et al. 2022, `WORLD-REF-019`).** El entorno siguiente se elige donde **más difiere el desempeño del alumno del óptimo** (arrepentimiento): ni trivial ni imposible; ACCEL lo hace por **edición mínima** de niveles ya vistos.
**Qué se construye.** T3 con número: para cada cascada un peldaño encima del mundo actual, arrepentimiento = exactitud(con maestro T1) − exactitud(sin maestro) en los primeros 64 pasos. El maestro elige **el peldaño de máximo arrepentimiento**; control: el de mínimo (trivial) y el de máximo tamaño (imposible, la escalera invertida de OOPS).
**Qué se mide.** Curva de Harlow (pieza 1) con las tres escaleras.
**Predicción.** Máximo arrepentimiento > mínimo > invertida. Si no, la escalera no importa en este banco y se dice.
**Cuándo.** Después de T1/T2, porque usa a T1 para medir el arrepentimiento.

## 8 · La canalización de Derex: qué cierra el maestro, no sólo qué abre

**Lo que da la fuente (Derex et al. 2025, `X13`).** La información social **canaliza** la exploración: el alumno explora menos del espacio y conserva tanto teorías útiles como inútiles que le dieron. Es el signo que vimos en «elegir» con esqueleto falso.
**Qué se construye.** En T1/T2: el conjunto de **hipótesis distintas** (máquinas canónicas) que el alumno visita en su vida, con y sin maestro.
**Qué se mide.** Tamaño del conjunto visitado; si la verdad está dentro; exactitud final.
**Predicción.** El maestro reduce el conjunto; cuando el maestro es del mundo correcto la verdad queda dentro y la exactitud sube; con el maestro del mundo equivocado (mutante M-t2) la verdad queda **fuera** y el alumno no la alcanza aunque siga viviendo. Eso es lo que Derex mide en humanos, y es el **coste** del maestro, que hay que poner al lado del beneficio.
**Cuándo.** Con T1/T2.

---

## Orden de trabajo

| ya, sobre lo que existe | tras C5 | con T1/T2 | Fase 3 |
|---|---|---|---|
| 4 (bits de Wolf) · 6 (congruencias de Hartmanis) | 5 (ventana × período) · 3 (dos páginas) · 1 (cadena de Harlow, marco) | 7 (escalera) · 8 (canalización) | 2 (variable esencial de Ashby) |

Las piezas 4 y 6 se pueden empezar hoy sin tocar a C5 ni a los mutantes: son análisis sobre artefactos guardados. Las demás van en el orden de la tabla, cada una con ficha corta y mutantes, como todo.
