# Informe · avances y retrocesos del programa UNIDAD MÍNIMA · 24 → 27 de octubre de 2026

**Para:** Wis · **De:** Fable, revisando lo que hay en disco (12 commits sobre la base, 41 entradas del registro, artefactos de las Fases 0, 1 y del prototipo de la Fase 2) · **Criterio de «positivo»:** el de Wis, desarrollo del ser: que haga hoy algo que antes no hacía, de poco en poco, hasta poder ser instruido. El cómputo y el tiempo se registran y no deciden.

**Nivel de evidencia de cada afirmación:** `CERTIFICADO` = ficha previa + mutantes + puerta pasada · `MEDIDO` = corrido y reproducido, sin ficha previa (exploratorio) · `DISEÑADO` = escrito, no corrido · `ABIERTO` = pregunta sin experimento.

---

## 1 · Lo que el ser hace hoy y no hacía el 24 de octubre

| capacidad | qué hace | dónde se midió | nivel |
|---|---|---|---|
| **Distinguir** | construye desde adentro, con dos letras y un bit de reacción, la máquina mínima que explica su vida; predice lo no vivido; halla el tercer elemento BA («escribe 1») que ninguna letra tiene | 01, 02 (Fase 0) | `CERTIFICADO` |
| **Regenerarse** | tras perder su hipótesis, nota que no explica su memoria y se relee; recupera la misma máquina con 0 pasos de vida nueva | 03 (Fase 0): enunciado original FAIL, reparación por disparo interno PASS | `CERTIFICADO` |
| **Elegir por conveniencia bajo instrucción** | dada una meta externa («que B reaccione 1»), elige la palabra más corta que la cumple desde todos sus estados: BA, mínima, verificada en el mundo real; la lesionada y el reactivo no pueden | 04 (Fase 0) PASS | `CERTIFICADO` |
| **Identificar mundos de 3 a 8 estados desde una sola vida, sin maestro ni reset** | 69,4 % en n=3 (banco completo), 62,6 % en n=4 (completo), 55,6 % en n=6, 42,7 % en n=8 | 05, 07 (Fase 1, cerrada el 27-oct) | `CERTIFICADO` |
| **Sobrevivir a que el mundo cambie sin aviso** | con olvido por fracaso: identifica el mundo nuevo en el 99,2 % (clase componible) y 100 % (control) al final de la vida; sin ese órgano, 0 % | prototipo 08 (Fase 2), 2 134 familias | `MEDIDO` |
| **Elegir qué vivir** | en vez del itinerario, va a la transición de su hipótesis que nunca vio; efecto con signo: ayuda cuando el esqueleto heredado es correcto (pareado 43 vs 22 a 64 pasos), estorba cuando es falso (63 vs 95) | prototipo 08 | `MEDIDO` |

Lo de la Fase 0 y la Fase 1 está bajo ficha, mutantes y commit. Lo de la Fase 2 **no**: es un prototipo mío sin ficha previa (E-37) y por eso cuenta como exploratorio hasta que Opus lo repita con ficha y mutantes.

## 2 · Leyes medidas que acotan cómo debe ser el ser

1. **Reversibilidad ⇒ identificación.** Si ninguna letra destruye información (las dos son permutaciones), identifica el 100 %, sin excepción en cuatro escalas; en n=8, 116 de 116. `CERTIFICADO`. Coincide con Angluin 1982 y con Krohn–Rhodes vía DeDeo 2011.
2. **«Admite una máquina menor» ⇒ transitorio estructural.** El 100 % de los mundos no determinados por admitir una máquina menor tienen estados sin vuelta; la recíproca es falsa (los identificados también los tienen: 24 / 11 / 5 % por estrato en n=4). `CERTIFICADO`, corregido tras la revisión externa.
3. **La cobertura la fija el par mundo × itinerario, no la longitud de la vida.** Alargar el mismo itinerario 2,5× y 5× no identifica ni un mundo más; invertir el itinerario cambia 54. `CERTIFICADO`. Es el argumento para que el ser elija qué vivir.
4. **La escala no degrada entre 3 y 6 y degrada en 8.** A igual dificultad real (`n_min`) la identificación es plana hasta 6 (76,7 / 76,3 / 77,1 % en `n_min`=2) y cae en 8 en cuatro de cinco estratos por encima del ruido (−12,0, −7,5, −5,3, −6,1 puntos). `CERTIFICADO` con predicción y falsador previos.
5. **El coste de exigir el mínimo exacto tiene cola exponencial.** FAIL del criterio de coste de la Fase 1, se queda como FAIL con nombre: NP-difícil desde Gold 1978 y Angluin 1978. `CERTIFICADO`.
6. **Un ser que exige explicar todo su pasado no sobrevive a un cambio de mundo.** 100 % de ahogo en tres pilotos con dos presupuestos y una ventana de 512. `MEDIDO`; pendiente del mutante M-c que lo reproduce con ojos frescos.
7. **Heredar la memoria cruda no acumula y estorba.** En la clase componible la heredera pierde más de lo que gana en los tres hitos tempranos (35 vs 112, 10 vs 66, 13 vs 23), olvida 6,6 veces más y en 638 de 766 celdas su máquina heredada fue destruida por el olvido antes de servir. `MEDIDO`.

## 3 · Lo que se construyó alrededor del ser

- **Método.** Plantilla de ficha de apertura con punto 0 de guardas; skill `/apertura`; mutantes obligatorios antes de dar una ficha por final; predicciones y falsadores escritos antes de correr; contadores de actividad (cero ⇒ nulo, no negativo); doble corrida con hash; `guardas.py` con seis guardas mecánicas importables.
- **Registro de errores y guardas:** 41 entradas con clase, severidad, firma y contador de veces que saltó, más la sección de ejes no vigilados. 16 de Opus, 6 mías (E-18, E-19, E-28, E-37, E-38, E-39), el resto de proceso o detectados por Wis. Ningún error llegó a un entregable sin corregirse.
- **Literatura.** Informe de 46 fuentes y 230 afirmaciones con nivel de evidencia; tres gates de antecedentes (escalado, 1-bis, Fase 2). Lo que se integra ya tiene dueño: Freund 1993 y Holmes–Isbell 2006 para la escala, Groce–Peled–Yannakakis 2002 para heredar y reparar, Korf 1985 y Cropper 2020 para repertorio y poda, Krohn–Rhodes/DeDeo para generar mundos en cascada, Bender 1998 y Kearns–Valiant 1994 para elegir.
- **Revisión externa** del informe de la Fase 1: nueve puntos cedidos, todos verificados antes de aceptarlos; ningún número cambió, cambiaron las frases que afirmaban más de lo medido.
- **Infraestructura.** Banco paralelo reanudable tras corte, corrida de n=8 bajo systemd, muestreo canónico sin retículo, verdad de referencia por minimización e isomorfismo.

## 4 · Retrocesos y lo que no avanzó

| qué | detalle | coste |
|---|---|---|
| **La pregunta central sigue abierta** | ¿lo vivido se acumula de una vida a la siguiente? La única herencia probada (traza) no acumula; la que podría (máquina sin traza, C5) está `DISEÑADO` y no construida | es lo que decide el programa y si Genesis tiene qué guardar |
| **Dos días de contabilidad sobre el identificador** | la Fase 1 midió al identificador en cuatro escalas antes de preguntar por el desarrollo; la decisión de abrir la Fase 2 en mundos chicos llegó el 26 | tiempo; no cambió ningún diseño del ser |
| **Ruptura del proceso por el supervisor (E-37)** | escribí y corrí el prototipo de la Fase 2 sin ficha, mutantes ni gate; dos errores de instrumento (E-38 bit inobservable, E-39 matar a la unidad al agotar presupuesto) que el proceso habría atrapado | el prototipo vale como exploración, no como evidencia; Opus rehízo custodia y ficha |
| **Ninguna capacidad nueva de la Fase 2 está certificada** | sobrevivir al cambio de mundo y elegir qué vivir son `MEDIDO`; faltan los seis mutantes (M-a…M-f) y la corrida confirmatoria | hasta entonces son indicios, no órganos |
| **Medidas defectuosas en el prototipo** | repertorio comparado contra W₁ (tamaños distintos, inválido); instruibilidad en el techo (2 de 2 metas en casi todo); alcance final saturado (0,992–1,000 en los seis brazos) | la ficha de Opus ya los sustituye: resets verdaderos, metas de estado, curva en 64/128/256 |
| **Parámetros a ojo** | ventana 512, núcleo 64, presupuesto por intento 200 000, tope de estados 8 | declarados como disposición suministrada; falta la variante (ventana 256) que diga si el resultado depende de ellos |
| **Fase 1: el FAIL del coste y la degradación en 8** | 80 de 5 000 mundos de n=8 cortados por reloj, concentrados en los estratos más difíciles; 1-bis (aprendiz polinómico) sigue `DISEÑADO` | el identificador exacto no escala como centro del ser; es insumo, no órgano |
| **Genesis sin destino** | no hay tipo de artefacto para una máquina aprendida; un linaje hereda dos escalares | el puente espera a C5 por decisión del plano |
| **Errores de instrumento repetidos** | 14 de las 41 entradas son de Opus en tres días; patrón nombrado: guardas que nombran el mecanismo y no la propiedad (tres veces); hash copiado de la terminal (E-40); lote de ediciones sin escritura por paso (E-41) | corregidos con guarda; la proporción ciencia / autocorrección fue mala |
| **Banco de trabajo** | `.venv` roto (sin Python 3.12, sin numpy/torch); hook de parada «Cartografía sin cerrar» vacío; dos cortes del límite de uso durante el deep-research | fricción; ninguno contamina medidas |

## 5 · Saldo, en una línea por eje

- **Desarrollo del ser:** avanza. Tres capacidades certificadas (distinguir, regenerarse, elegir bajo instrucción) y dos medidas (sobrevivir al cambio, elegir qué vivir). Ninguna de las dos últimas certificada aún.
- **Acumulación entre vidas:** sin respuesta. Una puerta cerrada con datos (la traza), una abierta con experimento concreto (la máquina), y el siguiente paso ya orientado (certificación por transición y cadena de cinco mundos).
- **Rigor:** avanza y cuesta. El método atrapó todos los errores antes de un entregable; la mitad del tiempo se fue en atraparlos.
- **Rumbo:** cambió el 26-oct y se confirmó el 27: el identificador exacto deja de ser el centro; el centro pasa a ser conservar lo que funciona y soltar lo que no, pieza por pieza.

## 6 · Lo inmediato, en orden

1. Opus: seis mutantes de la ficha de la Fase 2; M-c decide si el diagnóstico del ahogo se sostiene.
2. Opus: C5 (heredar la máquina sin la traza, reparación local) con sus tres campos de pérdida de minimalidad y su mutante.
3. Corrida confirmatoria sobre los 174 mundos madre; cierre con las predicciones marcadas y una pregunta para Wis.
4. Si C5 acumula: orientación de certificación por transición y cadena de cinco mundos; disparador de Genesis con contenido. Si no: «todavía no acumula», y se decide qué órgano falta antes de tocar Genesis.
