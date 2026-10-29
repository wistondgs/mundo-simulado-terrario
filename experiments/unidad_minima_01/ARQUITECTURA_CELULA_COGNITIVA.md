# La célula cognitiva · arquitectura de seis órganos

**Fecha:** 2026-10-28 · **Adjudicado por Wis:** cambio de centro. El identificador exacto (01/02) **deja de dirigir** la arquitectura y queda como **referencia científica** (vara de minimalidad y de verdad). El núcleo pasa a ser una unidad que mantiene una **comprensión parcial** de su mundo y de sí misma, actúa con ella, la repara donde falla, la reorganiza, y **conserva lo que ha aprendido a hacer**. · **Escribe:** Fable · **Ejecuta:** Opus · **Reemplaza** a `ORIENTACIONES_FASE_2_RECETA.md` como documento de arquitectura; no reemplaza ninguna ficha ni cambia el orden de trabajo.

**Principio (del registro de decisión):** modelo parcial del mundo y de sí misma → predicción → acción → consecuencia → contradicción → reparación local → reorganización → conservación y reutilización de lo válido. No se exige saber todo antes de actuar; se exige que lo aprendido tenga consecuencias funcionales y pueda corregirse.

## Tres correcciones de Wis (28-oct), que rigen todo el documento

1. **Esto es un andamio, no un plano.** El proyecto es flexible y modular porque nada de esto está inventado: cada órgano se puede reemplazar, duplicar, partir o quitar según lo que se mida. «Seis» es lo que hoy distinguimos, no una cifra del ser. Lo rígido son las normas de medida (determinismo, nadie le resuelve las relaciones, contadores, mutantes), no la arquitectura.
2. **Los alfabetos son parámetros.** Dos letras y un bit son la instancia **más chica** del experimento, no una propiedad del ser. El alfabeto de acciones puede ser las letras de todos los idiomas, los símbolos de un atlas, las cuatro bases de un genoma; el de observaciones puede ser un bit, un abecedario o lo que haga falta. Los mecanismos (predecir, refutar, dividir, fundir, certificar, olvidar, elegir) no dependen del tamaño del alfabeto; **el código sí** (`LETTERS` es una constante en 01 y el bit de cambio está cableado), y abrirlo es trabajo de la Fase 2-bis, no una reescritura.
3. **Ni lo mínimo ni el cómputo son techo.** Lo mínimo es el punto de partida de la pregunta. Hay toda la información del mundo y toda la capacidad de cómputo, y se van a usar: mundos grandes, vidas largas, GPU si hace falta, y un sustrato abierto: el autómata de 02 es la **primera instancia** del núcleo, no el núcleo; Genesis va encima de una red, y el ser puede ser lo que la medición diga que funciona, mientras sea determinista y nadie le resuelva las relaciones. **Y antes de maestro, alumno:** nadie enseña lo que no aprendió. Opus y Fable son parte del mundo del ser desde el principio como maestros, y lo son porque fueron alumnos de todo lo que la humanidad ya sabe; el ser, cuando haya aprendido, enseñará al siguiente. Lo único que viene «ya dado» sin haberse aprendido es lo que trae el genoma, y eso tiene su lugar exacto en nuestras tres capas: la **disposición** (los límites de V, la ventana inicial, el orden de las letras) es el genoma de la unidad; lo **adquirido** es su cultura. Dos canales de herencia, como en biología (Laland 2010, `X09`, `LC`): el linaje de Genesis transmite los dos y los mide por separado.

**Nivel de evidencia al lado de cada fuente** (E-42): `PV` = PROJECT-VERIFIED (medido aquí con ficha), `M` = medido aquí sin ficha (exploratorio), `SV` = SOURCE-VERIFIED (texto leído), `LC` = LITERATURE-CLAIM, `H` = hipótesis nuestra.

---

## 0 · La unidad de crecimiento: la relación funcional verificable

No es la máquina. Es cada **relación** que la unidad sostiene, con todo lo que hace falta para usarla, dudar de ella y repararla. En la unidad actual una relación es una transición `(q, a) → (q′, o)`; lo que se añade es su **ficha viva**:

| campo | qué guarda | de dónde sale |
|---|---|---|
| `relacion` | en la situación q, la acción a produce la reacción o y deja en q′ | `trans` de 02 (`PV`) |
| `condiciones` | desde qué situaciones se ha comprobado; con qué palabras se llega a q | el monoide de 01 (`PV`) |
| `anticipa` | qué predice para el paso siguiente | `predecir` de 02 (`PV`) |
| `evidencia` | cuántas veces predijo bien desde que se adoptó; última vez que se usó | contador nuevo (`H`); es la **certificación por transición** |
| `refutacion` | qué observación la refuta; cómo se repara (revisar destino, dividir q) | pila de decisiones de 02 + reparación local de C5 (`H`) |
| `depende_de` | de qué otras relaciones depende (la cascada: qué coordenada mueve) | congruencias de Hartmanis 1962 (`SV`, raíz del corpus) |

**Un contador, varios órganos.** El campo `evidencia` es el hilo: decide qué se repara primero (órgano 1), qué se olvida primero (órgano 2), qué se hereda (órgano 5) y qué puede nombrarse (órgano 6). No son cuatro mecanismos: es **uno** leído desde cuatro funciones, y así se declara para no inventar módulos.

---

## 1 · Modelar y reparar · el modelo parcial con reparación local

**Función.** Sostener un modelo del mundo y de sí misma que **nunca está completo**, usarlo para predecir, y cuando una relación falla, **dividir o revisar sólo esa relación**, no rehacer la vida.
**Mecanismo real.** La `Unidad` de 02 (estados, transiciones, pila de decisiones) con la reparación local de C5: una transición heredada o certificada que falla se vuelve **revisable en el paso actual** (se intenta otro destino; si se agotan, se **divide** el estado q en dos), en vez de disparar la relectura global. La fusión es la de Moore: dos estados que predicen igual sobre la ventana se funden. Dividir y fundir **ya existen** en 02 en forma global (`PV`); lo nuevo es hacerlos locales (`H`).
**Integración.** Adaptive model checking: reutilizar la conjetura y reparar donde falla, Groce–Peled–Yannakakis 2002 (`LC`, por leer); diferenciación de estados por contradicción: McCallum U-Tree 1996 y Holmes–Isbell 2006 (`SV` el segundo); hW-inference como forma de refinar sin reset (`SV`).
**Referencia (vara).** El identificador exacto de 01 recomputa la mínima sobre la ventana: `c5_consistente` (debe ser 1,000), `c5_minima`, `c5_estados_sobre_minimo`. **Lo que se cede** es la minimalidad garantizada; **lo que se mide** es cuánto.
**Experimento.** C5 en la ficha de la Fase 2 (`APERTURA_FASE_2_ACUMULACION.md` §5-bis) con su mutante «hereda pero ignora».
**Falsador.** C5 ≈ F1 en el hito 64 de la clase componible con `transiciones_heredadas_revisadas` > 0; o `c5_consistente` < 1,000 (defecto, no resultado).

## 2 · Olvidar y conservar · lo que no sirve se suelta, lo certificado se queda

**Función.** Vivir en un mundo que cambia sin ahogarse: soltar lo que ya no explica y conservar lo que sigue prediciendo.
**Mecanismo real.** Hoy: ventana de 512 pasos y **olvido por fracaso** (agotar el presupuesto de explicar ⇒ conservar los últimos 64 pasos y empezar sobre ellos), medido en `08` (`M`: sin él, 100 % de ahogo; con él, 99–100 % de identificación). Lo que se añade: el olvido deja de ser **por antigüedad** y pasa a ser **por certificación**: se sueltan primero las relaciones con `evidencia` baja; las certificadas sobreviven a la ventana. Poda de palabras por no servir, no por costar.
**Integración.** La memoria óptima depende del ritmo del entorno, Lambert & Kussell 2014 (`SV`, `HD-006`): la ventana es una **variable a medir**, no una constante. Olvidar para seguir aprendiendo, Cropper 2020 (`LC`); olvido catastrófico y su contrario en redes, Kirkpatrick 2017 / Abel 2023 (`ADOA-061`, `-069`, `LC`).
**Experimento.** Pieza 5 (`ORIENTACIONES_TRABAJO_DESDE_EL_CORPUS.md`): ventana × período de cambio; después, el olvido por certificación contra el olvido por antigüedad, pareado.
**Falsador.** El máximo de alcance **no** se desplaza con el período (la ventana no es del ser); o el olvido por certificación no supera al de antigüedad en ningún período.

## 3 · Elegir qué vivir · la acción epistémica

**Función.** No esperar a que la vida le traiga la experiencia que separa dos hipótesis: ir a buscarla. Es lo que ataca la clase recurrente de la Fase 1 (`PV`: la cobertura la fija mundo × itinerario).
**Mecanismo real.** 04: elegir la palabra mínima que cumple una meta externa (`PV`). 08: ir a la transición no vista más cercana de la propia hipótesis (`M`: ayuda con esqueleto correcto, 43 vs 22 pareado; estorba con esqueleto falso, 63 vs 95). Lo que se añade: elegir **sólo desde relaciones certificadas** (`evidencia` alta), porque elegir desde conjeturas amplifica el error (`H`, es la predicción del signo).
**Integración.** Añadir consultas cambia la clase del problema en el modelo de Angluin / Kearns–Valiant (`SV` K–V; **la transferencia a nuestro modelo es `H`**); procedimientos distinguidores, Bender 1998 (`SV`); la acción como pregunta en LIVE y CALM (`LC`); metarrazonamiento: elegir qué computar, Russell–Wefald, Griffiths 2019 (`ADOA-028`, `-031`, `LC`).
**Experimento.** Ya corrido en 08 (exploratorio); confirmatorio en la ficha de la Fase 2; la versión «sólo desde certificadas» tras C5. Mutante: elegir desde la más lejana.
**Falsador.** Elegir desde certificadas no mejora el signo: sigue estorbando con esqueleto falso.

## 4 · Mantenerse · la variable esencial

**Función.** Que algunas consecuencias **no sean errores de predicción sino condiciones de seguir existiendo**. De aquí nacen beneficio, peligro y riesgo sin que nadie los programe.
**Mecanismo real.** Una variable interna V que el mundo mueve (regla fija por mundo, desconocida para la unidad) y que **entra en lo observado**: la unidad modela su propia V como una coordenada más. Lo único innato: límites; si V los cruza, un parámetro de disposición cambia **a salto** por una lista fija (orden del itinerario, elegir on/off, ventana); si V llega a cero, la vida termina.
**Integración.** Ultraestabilidad: variables esenciales + funciones escalón, Ashby 1960 cap. 7–8 (`SV`, `ADOA-001`); implementada en robots, Di Paolo 2000, Iizuka & Di Paolo 2008 (`H-011/012`, `LC`); regulación sin punto fijo como rival, Fitzgerald & Bean 2018 (`H-009`, `LC`); empowerment como medida de control propio (`ADOA-071`, `LC`); el buen regulador es modelo, Conant & Ashby 1970 (`SV`).
**Experimento.** Pieza 2: **Fase 3**. Medidas: peligro descubierto (la máquina predice qué baja V), riesgo (empates donde una rama baja V, y si la ejecuta), vidas completadas frente a V inerte.
**Falsador.** La unidad que modela V no predice sus caídas antes que el reactivo; o los saltos de parámetro ocurren sin que V salga de límites (contador).

## 5 · Heredar y anticipar · el linaje

**Función.** Que lo aprendido pase a la vida siguiente **como capacidad y no como recuerdo**, y que la unidad llegue a prepararse para lo que viene.
**Mecanismo real.** Lo que se hereda son **relaciones certificadas y palabras con su clase** (el monoide de 01: «escribe», «permuta»), nunca la traza (`M`: la traza es lastre, 35 vs 112 pareado en el hito 64). El libro de dos páginas (recuperación: cambiar de página al primer error) y la anticipación (cambiar **antes** del error por una regularidad temporal aprendida), medidas por separado. La **curva de Harlow** como medida: acierto en los primeros 64 pasos del mundo k según k.
**Integración.** Learning sets, Harlow 1949 (`SV`, `ADOA-080`); anticipación de secuencias en bacterias y su pérdida sin uso, Mitchell 2009 (`SV`, `HD-009`); memoria medida en bits de historia, Wolf 2008 (`SV`, `HD-005`); las cadenas de transmisión exageran lo previo, Kirby 2007/2014 (`LC`/`SV` 2014): por eso se hereda **sólo lo certificado** y se mide la fidelidad a lo largo de la cadena; acumulación cultural y sus criterios, Mesoudi & Thornton 2018, Derex 2019 (`X11`, `X12`, `LC`). **Genesis** es donde vive el libro: tipo de artefacto = relaciones certificadas + palabras con clase + contadores; herencia bajo certificación es su canon.
**Experimento.** C5 (primer eslabón) → pieza 4 (bits condicionados al mundo) → pieza 3 (dos páginas, recuperación y anticipación) → pieza 1 (cadena de Harlow, series compatible y ajena).
**Falsador.** Curva de Harlow **plana** en la serie compatible con todos los contadores activos: nada pasa entre vidas; la célula es un aprendiz.

## 6 · Ser enseñada y nombrar · el maestro

**Función.** Que el entorno contenga a alguien que ya sabe y que **no le resuelva las relaciones**: le diga dónde mirar, qué intentar, y ponga nombre a lo que la unidad ya hace. «Nadie aprende a leer solo.»
**Mecanismo real.** Maestro programático determinista T1 (contraejemplo: la palabra más corta donde la hipótesis falla, desde el estado actual), T2 (itinerario: la primera palabra donde la hipótesis falla o no tiene ruta, antes del error), T3 (escalera: el mundo siguiente por máximo arrepentimiento). Nombres: el maestro asocia un símbolo a una **clase de palabras** del monoide (`escribe` ≠ «BA»: cualquier palabra que escribe). Lo que se registra siempre: qué cierra el maestro, no sólo qué abre.
**Integración.** Consultas y contraejemplos, Angluin 1987/1990, Rivest–Schapire 1993 (`LC`, por leer; la aplicación a nuestro modelo es `H`); coste empírico de enseñanza frente a la dimensión de Goldman–Kearns 1995 (`LC`); el entorno siguiente por arrepentimiento, PAIRED 2020 y ACCEL 2022 (`SV`, `WORLD-REF-017/019`); la instrucción canaliza la exploración, Derex 2025 (`SV`, `X13`); nombres como marcadores que se llenan de contenido, Carey 2009 (`TI-0037`, `LC`); dos unidades cooperando aprenden sin maestro, Bender–Slonim 1994 (`LC`): la cooperación es la hipótesis posterior.
**Experimento.** T1/T2 en la enmienda de la ficha de la Fase 2 con sus tres mutantes y los dos exámenes (retención con hipótesis congelada; transferencia a W₃); T3 y nombres con la cadena.
**Falsador.** T1 ≈ F1 en las familias con `contraejemplos_imposibles` = 0: el contraejemplo no enseña a esta unidad; o el alumno pierde exactitud al retirarse el maestro (sostuvo, no enseñó).

---

## 7 · Dónde los seis son menos de seis

- **1 y 2 comparten el contador** `evidencia`: reparar y olvidar son la misma lectura del mismo número, hacia arriba y hacia abajo.
- **3 y 6 son la misma función con dos fuentes:** qué vivir elegido desde adentro (hipótesis propia) o desde afuera (maestro). Por eso el control de «información del maestro» es F3.
- **5 depende de 1 y 2:** sólo se hereda lo certificado, y heredar sin reparación local se borra (ahogo del 27-oct).
- **4 cambia a los otros cinco:** con V, una refutación puede costar la vida; la reparación, el olvido y la elección pasan a tener consecuencia. Por eso es la última fase y no la primera.

## 8 · Lo que la Fase 1 queda siendo

El identificador exacto no se tira. Es la **vara**: da la máquina mínima y la verdad del mundo contra las que se mide todo lo anterior (`c5_minima`, identificación, isomorfismo en Hartmanis). Sus tres leyes (`PV`: reversibilidad ⇒ identificación; cobertura = mundo × itinerario; degrada en 8) siguen siendo las cotas dentro de las que la célula vive.

## 9 · Orden de trabajo (sin cambios)

1. C5 y sus seis mutantes (órgano 1). 2. En paralelo: bits condicionados de Wolf y congruencias de Hartmanis sobre lo guardado (órganos 5 y 0). 3. Ventana × período y olvido por certificación (órgano 2). 4. T1/T2 con retención y transferencia (órgano 6). 5. Dos páginas y cadena de Harlow (órgano 5). 6. Escalera y nombres (órgano 6). 7. Variable esencial (órgano 4). Cada paso con ficha corta, mutantes antes de la corrida, y una pregunta para Wis al cierre.

**Falsador de la arquitectura entera:** la curva de Harlow plana en la serie compatible con los seis contadores activos. Entonces no hay célula: hay un aprendiz con órganos, y se dice así.
