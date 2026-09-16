# CAREY-BOOTSTRAPPING-VS-TERRARIO-01

**Fuentes:**
- **TI-0037** — Susan Carey, *The Origin of Concepts*, Oxford University Press 2009, 609 pp,
  ISBN 978-0195367638. Aportado por el investigador el 2026-09-16 en Markdown convertido del PDF,
  con los límites de página originales conservados como `<!-- source-pdf-page: N -->`, de modo que
  **se puede citar por página**. Obra con derechos: uso de investigación privada.
- **X17** — *Précis of The Origin of Concepts*, Behavioral and Brain Sciences 34(3):113–167, 2011.
  DOI `10.1017/S0140525X10000919`. Acceso abierto, Version of Record. Útil como síntesis citable
  y por los 30 comentarios abiertos con la respuesta de la autora.

**Qué es este documento:** el contraste entre la teoría de Carey y lo que Terrario puede medir
hoy. Contiene una **hipótesis rival fuerte contra el propio proyecto**, que es exactamente para
lo que sirve leer bien.

---

## 1. Las tres tesis de Carey

1. **Estado inicial.** Los primitivos innatos **no** se limitan a lo sensorial, perceptual o
   sensomotor: hay representaciones innatas **conceptuales** — la *cognición nuclear*. Tres
   sistemas: objetos, agentes y número.
2. **Cambio.** El desarrollo conceptual es **discontinuo**: aparecen sistemas más potentes y a
   veces **inconmensurables** con aquellos de los que se construyeron.
3. **Mecanismo.** La discontinuidad se logra por **bootstrapping quineano**.

### La cognición nuclear, en propiedades

analizadores de entrada innatos y dedicados · larga historia evolutiva · continua durante toda la
vida · formato **icónico/analógico** · contenido conceptual no reducible a vocabulario
espaciotemporal o sensorial · centralmente accesible, representada en **modelos de memoria de
trabajo** que guían decisión y acción.

### El bootstrapping quineano, en pasos

1. Se establecen símbolos mentales que corresponden a **símbolos externos explícitos** recién
   acuñados o aprendidos.
2. Esos símbolos son al principio **marcadores de posición** vacíos: su significado proviene solo
   de sus relaciones con otros símbolos explícitos, no de conceptos previos.
3. Procesos de **modelado** —analogía, experimento mental, análisis de casos límite, inferencia
   inductiva— los llenan de contenido.
4. Al inicio del episodio, **el aprendiz todavía no tiene la capacidad de formular los conceptos
   que esos símbolos acabarán expresando.** Ésa es la definición operacional de discontinuidad.

---

## 2. La objeción de Carey a Terrario, dicha sin suavizar

Carey sostiene que el aprendizaje asociativo sobre primitivos perceptuales puede formar
generalizaciones sobre la entrada, pero que esas generalizaciones **no estarían formuladas en
términos del concepto *objeto***. Y añade que no conoce ninguna propuesta de mecanismo de
aprendizaje, disponible para criaturas **no lingüísticas**, capaz de crear representaciones de
objetos, número, agencia o causalidad a partir de primitivos perceptuales.

Los agentes de Terrario son exactamente eso:

| Requisito del bootstrapping | A0 | A1 | A2 | A3 | A4 |
|---|:-:|:-:|:-:|:-:|:-:|
| Símbolos externos explícitos | — | — | — | — | — |
| Estructura de marcadores de posición | — | — | — | — | — |
| Modelado por analogía / caso límite | — | — | — | — | — |
| Formato no icónico (discreto, simbólico) | — | — | — | — | — |

Entrada: cuatro canales continuos, máscara, energía normalizada y fracción de tiempo. Formato
latente continuo — **icónico/analógico en el sentido de Carey**. Ningún agente tiene canal
simbólico externo.

### La consecuencia, que es una hipótesis rival preregistrable

> **H-RIVAL-CAREY.** Ningún agente A0–A4 puede adquirir los conceptos *objeto* o *causa* en
> D0–D4. Cualquier mejora observada en `d1_objects` o `d3_causality` es generalización
> estadística sobre primitivos perceptuales, no adquisición conceptual — porque falta el
> ingrediente que Carey declara necesario: el andamiaje de símbolos externos.

Esta hipótesis **debe descartarse antes** de cualquier afirmación de que un agente «entendió»
objetos o causalidad. Se suma a la de Derex (X12): mejora sin comprensión causal. Dos rivales
independientes contra la misma lectura ingenua.

---

## 3. La advertencia metodológica que aplica a toda métrica de Terrario

Carey distingue asimetría entre éxito y fracaso: el éxito en una tarea apoya la capacidad
representacional que la tarea requiere; **el fracaso no es buena evidencia de que la capacidad
falte**, porque limitaciones de desempeño pueden enmascarar competencia presente.

Aplicado literalmente: en la matriz A×D, **una celda con puntuación baja no demuestra ausencia de
competencia.** Sólo las celdas altas informan, y sólo sobre la capacidad que la tarea exige.
Esto debe estar escrito en el plan de análisis de cualquier preregistro de la matriz, o la mitad
de las celdas se leerán al revés.

---

## 4. Lo que esto sugiere construir — y es un experimento nuevo, no un parche

Si el argumento de Carey es correcto, hay una predicción arquitectónica nítida y comprobable:

> **Ninguna cantidad de aprendizaje perceptual produce la discontinuidad; un canal de símbolos
> externos sí puede.**

Terrario está arquitectónicamente cerca de poder probarlo. Haría falta:

1. **Un canal de símbolos externos**: un flujo discreto de tokens, inicialmente **sin
   significado**, que el agente pueda ligar. Es el análogo de la lista de numerales memorizada
   antes de significar algo — el marcador de posición de Carey.
2. **Una estructura de marcadores**: relaciones estables entre esos tokens (orden, sucesión)
   independientes de su contenido.
3. **Una condición de control sin símbolos**, idéntica en capacidad y cómputo.

El contraste sería: mismo agente, mismo mundo, misma semilla — **con y sin andamiaje simbólico**.
Si Carey tiene razón, la condición sin símbolos se estanca en generalización perceptual y la
condición con símbolos muestra un salto que no es explicable por más datos.

Eso es un experimento de ontogenia de verdad, no anatomía comparada. Y a diferencia de la
escalera A0→A4, mide **una arquitectura que cambia en el tiempo**, que es lo que el desarrollo
significa.

**Advertencia de pureza obligatoria:** añadir un canal simbólico añade capacidad y cómputo. El
control tiene que igualarlos (p. ej. un canal de tokens aleatorios sin estructura relacional),
o el resultado no es atribuible al andamiaje. Ver `docs/SCIENTIFIC_REVIEW.md`.

---

## 5. Cómo encaja con Karmiloff-Smith

Las dos teorías apuntan al mismo hueco desde lados distintos:

| | Karmiloff-Smith (TI-0035) | Carey (TI-0037 / X17) |
|---|---|---|
| Mecanismo | redescripción representacional | bootstrapping quineano |
| Qué se transforma | representaciones implícitas ya funcionales | marcadores de posición vacíos |
| Disparador | **maestría conductual** en el dominio | símbolos externos + modelado |
| Predicción en D4 | recuperación **conservando** lo anterior | discontinuidad, posible inconmensurabilidad |

Ambas coinciden en lo esencial para Terrario: **el desarrollo no es más aprendizaje del mismo
tipo.** Hay una transformación de formato, y hoy ningún agente de Terrario tiene el mecanismo
para hacerla. Ésa es la brecha real entre el instrumento y la pregunta del proyecto — y ahora
está nombrada, con dos fuentes primarias que la sostienen.

---

## 6. Estatus

Descriptivo y preparatorio. No autoriza ninguna ejecución, no preregistra nada y no afirma
ningún resultado. `H-RIVAL-CAREY` debe entrar como hipótesis rival en cualquier preregistro de
D1 o D3; el experimento de §4 requiere diseño, revisión y firma humanas.


---

## 7. Mapa de capítulos de TI-0037, por relevancia para Terrario

| Cap. | p. | Título | Para qué sirve aquí |
|---:|---:|---|---|
| **6** | 215 | Representations of Cause | **D3** — el capítulo entero es tu escenario |
| **11** | 413 | The Process of Conceptual Change | el mecanismo: bootstrapping quineano |
| **3** | 67 | Core Object Cognition | **D1** — permanencia e individuación de objetos |
| **2** | 27 | The Initial Representational Repertoire: The Empiricist Picture | el argumento **contra** aprender conceptos desde primitivos perceptuales |
| **10** | 361 | Beyond Core Object Cognition | **D4** — cambio conceptual sobre objetos y materia |
| 7 | 247 | Language and Core Cognition | por qué el andamiaje simbólico es el requisito |
| 5 | 157 | Core Cognition: Agency | futuro multi-agente |
| 4 | 117 | Core Cognition: Number | el caso trabajado del bootstrapping |
| 8 · 9 | 287 · 335 | Beyond Core Cognition: Natural Number · Beyond the Numeral List | discontinuidad documentada paso a paso |
| 12 · 13 | 447 · 487 | Conclusiones | teoría de conceptos |

## 8. Un hallazgo de validez de constructo sobre `d3_causality`

El capítulo 6 separa **dos tradiciones distintas** sobre el origen de la representación causal:

1. **Causalidad perceptual michottiana** — el lanzamiento, el arrastre, la expulsión: contacto
   espaciotemporal que produce una impresión causal inmediata. Carey revisa la evidencia de que
   a los 6 meses los bebés ya tienen representaciones causales ricas de estos eventos.
2. **Causalidad por covariación e intervención** — la tradición de redes bayesianas (Gopnik,
   Pearl, Sloman, Spirtes, Tenenbaum, Woodward), que Carey cita explícitamente como la alternativa.

**`scenarios/d3_causality.yaml` implementa la segunda, no la primera.** Su estructura es
covariación con un confundidor:

```
ch0 alto + ch1 alto  ->  +8.0      (ch0 parece predictivo)
ch0 alto + ch1 BAJO  ->  -4.0      (solo ch1 es causal)
```

Eso es discriminación causa/correlación al estilo bayesiano. **No hay contacto, ni transferencia
de impulso, ni evento de lanzamiento** — nada michottiano. Son constructos distintos y el nombre
del escenario no dice cuál.

**Consecuencia práctica:** un preregistro sobre D3 debe declarar cuál de las dos causalidades
mide, o la afirmación resultante será ambigua entre dos literaturas. Y si algún día interesa la
causalidad perceptual —la que los bebés tienen a los 6 meses— haría falta **un escenario nuevo**
con objetos que se contactan y transfieren movimiento, no una variante de D3.

Ese es, por cierto, un escenario que Terrario podría construir sin arquitectura nueva: el mundo
ya tiene objetos móviles e inamovibles y reglas por contacto.
