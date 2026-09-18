# Terrario

**Documento canónico · versión 2.1 · 2026-09-17**

> **Terrario no está diseñado para descubrir desde cero qué habilidades debería inventarse un
> agente. Está diseñado para convertir el conocimiento acumulado sobre inteligencia en un espacio
> computacional experimental, otorgar esos mecanismos a organismos artificiales, someterlos a
> presión controlada y descubrir mediante evidencia qué arquitectura de capacidades produce el tipo
> de ser cibernético buscado.**

---

## La misión canónica

> Terrario es un **sistema científico de síntesis experimental de inteligencia**. Parte de
> conceptos candidatos extraídos del corpus científico; los convierte en **operacionalizaciones
> computacionales**; implementa esas operacionalizaciones como **capacidades otorgables**; las
> instala individualmente y en combinaciones controladas sobre agentes; somete esos agentes a
> **familias progresivas y dinámicas de mundos**; mide **causalmente** sus efectos; y acumula
> evidencia para descubrir qué mecanismos, implementaciones, interacciones y composiciones producen
> el **fenotipo de inteligencia** requerido para el ser cibernético objetivo.

Terrario **no** tiene como misión esperar que el agente descubra por sí mismo las capacidades del
catálogo. El catálogo conceptual procede del corpus. El laboratorio construye, otorga, combina,
perturba y evalúa esas capacidades.

El agente **sí** puede aprender contenido, estrategias, representaciones y conocimiento mediante
las capacidades que posee, y puede producir conductas emergentes que nadie programó. Eso es
distinto de inventar el catálogo desde cero.

---

## La ley terminológica

Cinco cosas que no son la misma, y cuya confusión produjo casi todos los errores de interpretación
de este proyecto:

```
Concepto ≠ Operacionalización ≠ Algoritmo ≠ Capacidad otorgada
         ≠ Contenido adquirido ≠ Conducta emergente
```

### Concepto

Viene del **corpus**. Memoria, previsión, curiosidad, creatividad, resiliencia, atención,
imaginación, causalidad, metacognición. Es un **constructo candidato** identificado en literatura,
teoría, neurociencia, cibernética, psicología, ciencia cognitiva o IA.

**Todavía no es código.**

### Operacionalización

Responde a: *¿qué tendría que hacer un sistema observable para afirmar que posee una realización
computacional de este concepto?*

«Memoria» es demasiado general. Se operacionaliza como

```
retener información → recuperarla → utilizarla después
```

bajo condiciones determinadas. Aquí se fijan **entradas, salidas, estado interno, qué información
puede usar, qué conducta debería permitir, controles, falsadores y métricas**.

Éste es el puente central de todo el sistema y el que más se salta.

### Algoritmo

Una **implementación candidata** de esa operacionalización. Un mismo concepto tiene varias:

```
Concepto C → { A₁, A₂, A₃, …, Aₙ }
```

De aquí se sigue una prohibición dura. Que una implementación concreta no produzca efecto **no**
autoriza a decir «memoria no sirve». La conclusión válida es:

> esta operacionalización/algoritmo de memoria, bajo estas condiciones, no produjo el efecto
> predicho.

### Capacidad otorgada

Cuando un algoritmo cumple su contrato y puede instalarse en el organismo, se vuelve una
**capacidad experimental otorgable**. Entonces se puede comparar

```
Agent(Cᵢ = OFF)   contra   Agent(Cᵢ = ON)
```

y también entre realizaciones distintas del mismo concepto:

```
Agent(Cᵢ = A₁),  Agent(Cᵢ = A₂),  Agent(Cᵢ = A₃)
```

Terrario no pregunta sólo si la memoria existe: pregunta **qué tipo de memoria produce qué efecto**.

### Contenido adquirido

**La capacidad se la damos nosotros. El contenido lo adquiere el organismo.**

| Le damos | No le damos |
|---|---|
| memoria | qué recordar |
| aprendizaje | qué relación aprender |
| imaginación | qué representación generar |
| metacognición | qué descubrirá sobre sí mismo |

Aquí estuvo la confusión del 17 de septiembre. `CAPABILITY-ACQUISITION` conserva todo su valor y
queda correctamente situado: **no investiga de dónde sale el concepto de aprendizaje; investiga si
el mecanismo de aprendizaje que le otorgamos puede adquirir contenido útil.**

### Conducta emergente

Otro nivel todavía. Aparece por interacción de capacidades:

```
C₁ + C₂ + C₃  →  B      sin que exista un módulo llamado B
```

Memoria + predicción + incertidumbre + curiosidad + planificación podrían producir una estrategia
que nadie programó. **Eso sí sería un hallazgo de Terrario**: no descubrió una habilidad del corpus
dentro del agente, descubrió una **propiedad emergente de una composición**.

### Los cuatro niveles

| Nivel | Quién lo produce | Ejemplo |
|---|---|---|
| **Capacidad otorgada** | Terrario / el diseñador | memoria, planificación, curiosidad |
| **Contenido adquirido** | el organismo durante la experiencia | asociación, modelo, estrategia |
| **Conducta emergente** | interacción organismo–capacidades–mundo | estrategia no programada, adaptación compuesta |
| **Transformación de la propia arquitectura** | el organismo sobre sí mismo | reorganización, autoevolución |

El cuarto no contradice la misión: **nosotros proporcionamos inicialmente los mecanismos que hacen
posible la autoevolución**, y después estudiamos qué ocurre cuando el organismo empieza a usarlos
sobre sí mismo.

---

## La cadena

No es una línea. Es un **ciclo de acumulación científica**.

```
Corpus → Concepto → Definición operacional → Algoritmo(s) → Capacidad
       → Composición → Agente → Mundo → Conducta → Medición
       → Inferencia causal → Hipergrafo → Nueva composición / nuevo mundo
       ↺
```

Y la estructura profunda que gobierna todo el documento:

```
literatura → constructos → mecanismos → organismos → presiones
           → fenotipos → evidencia → teoría computacional de inteligencia
```

Cada etapa **transforma un objeto científico distinto**. El canon nombra cuál es en cada paso,
porque describir sólo el flujo operativo es lo que permitió confundir cinco cosas durante un día
entero.

---

## Las cinco leyes canónicas

| | |
|---|---|
| **L-1 · Procedencia conceptual** | Ninguna capacidad entra al espacio experimental sin conexión explícita con corpus y concepto. |
| **L-2 · Operacionalización** | Ningún concepto se considera implementado sólo porque existe un módulo con su nombre. |
| **L-3 · Separación de niveles** | Capacidad otorgada, contenido adquirido y conducta emergente nunca se tratan como equivalentes. |
| **L-4 · Composición** | La inteligencia se estudia como propiedad potencialmente sistémica y relacional, no como suma de banderas independientes. |
| **L-5 · Progresión experimental** | Un nuevo mundo o nivel nace de la evidencia del anterior, pero constituye **un nuevo ciclo experimental** con contrato y criterios propios. |

---

# 0 · Qué entrega Terrario

Todo lo demás está construido. RNFE aporta la ecología de razonamiento; Genesis es el andamiaje
donde el ser va montado, con su red neuronal y sus hiperparámetros. **Lo que falta es el motor de
inteligencia, y eso es lo que Terrario produce.**

## 0.1 · El producto final

Terrario **no** entrega «el agente que ganó más», ni «la mejor semilla», ni «un A4 mejorado».

Su producto científico es:

> **Una teoría computacional, causal y ejecutable de la arquitectura de inteligencia del ser
> objetivo.**

Con evidencia de qué capacidades son **necesarias**, cuáles **prescindibles**, cuáles
**redundantes**, cuáles **complementarias**, cuáles **se interfieren**, cuáles son
**habilitadoras**, cuáles sirven **sólo bajo determinadas condiciones**, qué **implementaciones**
funcionan, qué capacidades **requieren otras**, qué propiedades aparecen **sólo como emergencia**, y
cuáles sostienen **persistencia, adaptación, reorganización, metacognición y autoevolución**.

```
Terrario → arquitectura validada → motor de inteligencia que RNFE/Genesis necesita
```

## 0.2 · Fenotipo objetivo del ser

El norte **no es un agente concreto** y **no es recompensa máxima**. Es aproximarse progresivamente
al comportamiento de un ser:

```
autopoiético + persistente + adaptativo + metacognitivo + autoevolutivo
```

y los atributos adicionales que el propio corpus vaya justificando.

Cada pieza del programa responde a una pregunta distinta sobre ese fenotipo:

| | Pregunta |
|---|---|
| Cada concepto candidato | ¿qué parte del fenotipo podría contribuir a producir? |
| Cada experimento | ¿realmente contribuyó? |
| Cada combinación | ¿qué ocurre al integrarla con otras? |
| Cada mundo | ¿bajo qué presión esa propiedad se vuelve necesaria o se rompe? |

Consecuencia operativa: una capacidad que gane contra su control pero **no componga** no sirve. Lo
que se busca son propiedades de sistema, y ésas no se infieren sumando banderas.

## 0.3 · La pregunta madre

> ¿Qué conceptos candidatos, bajo qué operacionalizaciones y algoritmos, en qué combinaciones, bajo
> qué condiciones ambientales y temporales, **producen, sostienen, degradan, recuperan o
> transforman** las propiedades de inteligencia requeridas del ser objetivo?

La respuesta probablemente **no** tendrá la forma `inteligencia = memoria + creatividad +
curiosidad + planificación`. Tendrá más bien la forma: *C₁ es útil sólo cuando existen C₄ y C₇, es
perjudicial bajo W₃, y se vuelve imprescindible cuando la dificultad supera D\**.

---

# 1 · El corpus: de dónde salen los conceptos

La inteligencia no es un elemento. Es un **cúmulo**: memoria, conocimiento, curiosidad,
creatividad, acción, imaginación, previsión, formación de hipótesis.

## 1.1 · Lo que el corpus NO es

> **El corpus no es un dataset de entrenamiento para A4.**

Es el **reservorio epistemológico del laboratorio**: lo que múltiples disciplinas han observado,
propuesto, definido, discutido o experimentado sobre fenómenos relacionados con inteligencia.

Fue construido **independientemente de RNFE y Genesis**, para reducir el sesgo de confirmación.

**Corpus v1:** 152 referencias, 16 categorías, 65 copias completas, provenance criptográfica.

## 1.2 · Qué debe conservar

No basta con producir candidatos. Cada concepto arrastra su cadena:

```
Concepto → Fuente → Definición → Evidencia → Limitaciones → Relaciones
```

**La procedencia importa porque dos autores pueden usar la palabra «memoria» para fenómenos
distintos.** Terrario no debe colapsarlos por nombre. Ésa es la forma más barata de fabricar una
contradicción y creerla un hallazgo.

## 1.3 · Qué decide el corpus, y qué no

**Decide:** qué conceptos son candidatos, qué significa cada uno en su fuente, qué mecanismos
propone cada tradición, qué controles metodológicos existen — y, crucialmente, **qué combinaciones
vale la pena probar**.

Esto último es lo que hace tratable el problema. Cuando una teoría propone memoria + modelo del
mundo + planificación como sistema funcional con **roles distintos**, esa conjunción entra al
espacio confirmatorio con un motivo. Las demás quedan como exploración etiquetada.

**No decide:** que una teoría sea correcta. La autoridad sobre el comportamiento del ser viene del
experimento, no del prestigio de la fuente.

## 1.4 · La ontología: de documentos a constructos comparables

El corpus contiene **documentos**. La ontología los convierte en **objetos conceptuales
comparables**.

```
Documento A ─┐
Documento B ─┼→ concepto normalizado: MEMORIA EPISÓDICA
Documento C ─┘
```

Y permite distinguir memoria episódica, de trabajo, asociativa, semántica, persistencia, retención
y recuperación — **en lugar de meterlo todo bajo `memory=True`**.

De ahí se sigue el requisito más importante para la escala futura:

> **La unidad experimental de Terrario no debe ser el nombre de una bandera. Debe ser un constructo
> operacionalizado y versionado.**

## 1.5 · Estado medido

| | |
|---|---|
| Corpus físico | **existe** — 42 PDFs |
| Grafo de referencias | **vacío** — 0 filas en 22 tablas |
| Formato que el importador espera | **no existe en disco** |
| Catálogo de fuentes | existe en otro formato: 44 fuentes en el snapshot de teoría |

**Eslabón roto.** Dos sistemas paralelos que nunca se tocaron.

---

# 2 · De concepto a algoritmo

Es el núcleo científico del sistema, no un trámite de implementación. Aquí se convierten
**constructos científicos humanos** en **mecanismos computacionales falsables**.

## 2.1 · El error que hay que impedir

```
MEMORIA  →  escribimos memory.py  →  listo
```

## 2.2 · La tubería real

```
CONCEPTO
    ↓
propiedades esenciales
    ↓
predicciones conductuales
    ↓
condiciones necesarias
    ↓
falsadores
    ↓
contrato computacional
    ↓
algoritmos candidatos
    ↓
controles
    ↓
capacidad otorgable
```

**No hay traducción uno a uno.** Un concepto tiene varias implementaciones, y un mismo algoritmo
puede materializar varios conceptos. El enlace concepto ↔ algoritmo es **muchos a muchos**.

## 2.3 · La ficha mínima

Concepto fuente y provenance · constructo · mecanismo · entrada/salida · estado que conserva ·
**autoridad causal** · variantes · **ablación** · métrica · **control negativo** · **control
positivo** · **mundos requeridos**.

## 2.4 · El principio que gobierna este paso — L-2

> **El nombre del módulo no es evidencia.** Un componente llamado `Planner`, `WorldModel`, `Memory`
> o `Uncertainty` sólo cuenta como operacionalización de ese concepto si su ruta causal y su
> comportamiento medido cumplen la definición que se está probando.

Medido: el `Planner` hace **random shooting** sobre un modelo del mundo que no predice —
`energy_head` tiene dispersión 0.0037 sobre una cantidad que varía 2.0 — así que funciona como
fuente de exploración aleatoria, no como planificación.

## 2.5 · Estado medido

10 conceptos en el catálogo. **`corpus_block` es un entero que ningún fichero lee**: sin
`reference_id`, sin `claim_id`, sin locator. El puente corpus → algoritmo no existe, y **L-1 está
incumplida hoy para las diez capacidades**.

El **ciclo de madurez de concepto** —RAW → DEFINED → RELATED → OPERATIONALIZABLE → IMPLEMENTED →
INSTRUMENTED → TESTED → RETAINED/REVISED/REJECTED— **no está implementado**. Los 224 conceptos
canónicos son CSV congelados, sin estado y sin transición.

---

# 3 · De algoritmo a capacidad otorgada

**Otorgar una capacidad** es incorporar al organismo un mecanismo candidato que representa un
concepto. No garantiza que lo use bien. Hay que comprobar tres cosas distintas: si tiene
**autoridad causal**, si **se integra** con las demás, y si su presencia cambia la conducta **en un
mundo que realmente la exija**.

Los cuatro niveles de la ley terminológica se aplican aquí sin excepción (**L-3**).

## 3.1 · Estado medido

Este eslabón **funciona**: `agent_composition` → `sandbox_runtime`, con validación fail-closed.

---

# 4 · El agente: portador experimental de capacidades

Los agentes **no** son versiones progresivamente «más inteligentes» por definición. Son
**portadores** de capacidades:

```
A(S)   donde   S = { C₁, C₅, C₁₇, … }
```

A0…A4 son **especímenes o configuraciones históricas**, no la ontología final del proyecto
(**I-14**).

## 4.1 · La forma que debería tener

```
AgentSpec
  capability: episodic_memory_v3
  capability: curiosity_v2
  capability: prediction_v5
  capability: metacognition_v1
```

Sin que «capacidad» sea sinónimo de «bandera interna de A4».

## 4.2 · Deuda de código medida

Hoy **no es así**. `agent_composition.py` importa `DEFAULT_CONFIG` desde `a4_advanced`, de modo que
el catálogo de composición está acoplado a la configuración concreta de A4. La cartografía lo
identifica como el acoplamiento que impediría probar otra arquitectura bajo el mismo laboratorio.

Esto es `EXPERIMENTAL-COMPOSITION-MODEL` en el backlog doctrinal.

## 4.3 · Lo que A4 es hoy, sin los nombres

```
encoder convolucional → núcleo SSM lineal → estado de 640 dims
    ↓
política lineal sobre 25 acciones, temperatura por energía
    ↓
con probabilidad ½: el planner propone una de 10 secuencias aleatorias de 5 pasos,
                     puntuadas por un modelo del mundo que no predice
```

300 pasos producen **300 actualizaciones** y **3 eventos informativos**. Con 1536 ejemplos
informativos **puros** la cabeza de energía no se separa del azar.

---

# 5 · El mundo: instrumento de presión selectiva y diagnóstico

Los mundos **no** son escenarios donde el agente actúa. Son **instrumentos experimentales**. Un
mundo se diseña para **hacer visible una propiedad**.

## 5.1 · La regla, con su ejemplo

Para probar memoria:

```
Observation_t  debe contener información necesaria para  Action_{t+k}
                 y esa información NO debe estar disponible en t+k
```

Si el mundo deja la respuesta visible todo el tiempo, la memoria es innecesaria. Entonces que
`use_memory=False` no cambie nada **no dice nada sobre la memoria**. Dice:

> **el mundo no exigía memoria.**

Medido: el núcleo temporal, la incertidumbre y las dos memorias «no mueven nada» en D4T. Pero D4T
es esencialmente markoviano. Eso es un hallazgo **sobre D4T**, no sobre la memoria.

## 5.2 · Cada nivel necesita dos mundos

| | |
|---|---|
| **Mundo exigente** | donde la capacidad es necesaria |
| **Mundo de control** | donde **no** debería ayudar |

Sin el segundo, un efecto no se distingue de un artefacto.

## 5.3 · Principio de variedad

Nada relevante tiene por qué permanecer estático: mundo, perturbaciones, variables esenciales,
región de viabilidad, sensores, actuadores, representaciones, memorias, estrategias, recursos,
otros agentes, objetivos, observabilidad y ritmo de cambio.

---

# 6 · La escalera: niveles, dificultad creciente, capacidades que se suman

Se empieza con una o dos capacidades. Se mide. Sube la dificultad y entran más. Se mide otra vez.
**Los mundos se diseñan cuando se pasa el nivel**, no por adelantado.

## 6.1 · Por qué hace el problema tratable

| Capacidades presentes | Factorial completo |
|---|---|
| 2 | 4 corridas |
| 3 | 8 |
| 4 | 16 |
| 10 | 1024 |
| 46 | astronómico |

Con dos o tres se corre el factorial completo y **se miden todas las interacciones exactamente**.

No es teórico: el tamizado usó efectos principales porque 2⁸ era inasumible, y sus residuos de
interacción salieron **ininterpretables por saturación**.

## 6.2 · La formalización — L-5

La progresión adaptativa **no puede destruir la trazabilidad**. La distinción es exacta:

**Correcto:**
```
Nivel_n → criterio de dominio → cierre → análisis → diseño del Nivel_{n+1} → nuevo preregistro
```

**Prohibido:**
```
resultado → muevo las reglas → sigo llamándolo el mismo experimento
```

**Cada nivel nuevo es una generación experimental nueva**, con su propio contrato, sus propios
criterios y su propio preregistro.

## 6.3 · La forma de un nivel

```
NIVEL N
  premisa            qué capacidad afirma que es necesaria, y qué fuente lo propone
  capacidades        qué algoritmos se otorgan, en qué versión
  mundo exigente     dónde la capacidad es necesaria
  mundo de control   donde NO debería ayudar
  criterio de dominio qué hay que demostrar para cerrar el nivel
```

## 6.4 · La escalera declarada

```
D0   differences                  IMPLEMENTED_LEGACY
D1   objects_and_persistence      IMPLEMENTED_LEGACY
D2   properties_and_binding       IMPLEMENTED_STUDIO
D3   causality                    IMPLEMENTED
D4   adaptation                   IMPLEMENTED_PROTOCOL_NOT_CONFIRMED
D5   tools_and_composition        FUTURE_DESIGN
D6   planning                     FUTURE_DESIGN
D7   uncertainty_and_exploration  FUTURE_DESIGN
D8   signs_and_semantics          FUTURE_DESIGN
D9   social_world                 FUTURE_DESIGN
D10  inheritance_and_lineage      FUTURE_DESIGN
D11  cumulative_culture           FUTURE_DESIGN
```

Los mundos existen como escenarios. Falta de cada peldaño la **premisa**, el **mundo de control** y
el **criterio de dominio**. Sin criterio no hay escalera: hay una lista de escenarios.

## 6.5 · Estado medido, y es incómodo

**Ningún nivel ha sido superado.** `scientific_results = 0` tras 240 intentos.

Todo el trabajo reciente corrió en **D4T**, variante del peldaño 4, con protocolo
`NOT_CONFIRMED`, sobre una escalera cuyos peldaños 0–3 nunca se certificaron. Se estaba midiendo
adaptación en un organismo del que no se sabe si distingue diferencias.

## 6.6 · Ejemplo de nivel 1

> **Premisa** — un organismo no puede hacer nada más si no distingue que las cosas difieren.
> **Capacidad** — el encoder perceptivo.
> **Mundo exigente** — D0, donde la conducta correcta depende de la diferencia.
> **Mundo de control** — D0 con todos los objetos idénticos.
> **Criterio de dominio** — la conducta difiere entre ambos mundos, y esa diferencia **desaparece**
> al ablacionar el encoder.

---

# 7 · La combinación — L-4

La inteligencia puede depender de composiciones donde un mecanismo **habilita, estabiliza, regula o
modifica** a otro.

| Relación | Interpretación |
|---|---|
| Complementaria | aportan funciones distintas y juntas superan a cada una |
| **Habilitante** | A sólo produce efecto cuando B existe |
| Jerárquica | A regula cuándo o cómo B puede actuar |
| Redundante | A o B cumplen funciones solapadas |
| Antagonista | la presencia conjunta degrada una propiedad |
| Compensatoria | la pérdida de A cambia B de forma que recupera parte de la función |
| Secuencial | el efecto depende de que A actúe antes que B |
| Contextual | la relación cambia según mundo, recursos o historia |

## 7.1 · La trampa medida

Una ablación que apaga dos cosas no mide ninguna. El tamizado reportó «modelo del mundo +6.33» y
«planificador +6.67» como dos hallazgos. **Son la misma intervención.** Barrido completo: **8 de 10
puras**, y las 2 impuras son exactamente ésas.

---

# 8 · La medición

Hacen falta **dos valideces**: experimental (¿la intervención está aislada?) y de instrumento (¿la
métrica detecta el constructo?).

## 8.1 · Las cuatro semánticas

```
0              hubo soporte, se calculó, salió cero
NOT_EVALUABLE  no existe soporte — el denominador está vacío
MISSING        falta un dato que el cálculo necesita
INVALID        el dato existe y viola el contrato
```

`conversion = 0` con `N_informative = 0` y con `N_informative = 40` son **hallazgos opuestos
vistiendo el mismo dígito**. El laboratorio ya produjo tres por accidente.

## 8.2 · Falsación de instrumentos

Oráculo (techo), anti-oráculo (suelo), caso nulo (`NOT_EVALUABLE`), azar analítico, invariantes de
contabilidad. Y el control debe falsar también **la entrada**, no sólo la salida: el examen de
capacidad tenía los tres controles verdes mientras entregaba observaciones en un formato que el
organismo nunca vio entrenando.

## 8.3 · Medir cadenas

```
oportunidad → percepción → intención → referencia → alcance → ejecución
            → consecuencia → discriminación → aprendizaje → retención → transferencia
```

Supervivencia o recompensa son demasiado distales para decir **dónde** se rompió.

## 8.4 · Estado medido

22 mallas, **6** con control de falsación. Dos sistemas de validez de métricas que **no se
comunican**, con identificadores disjuntos. **Una** métrica `VALIDATED_FOR_CONSTRUCT`.

---

# 9 · El veredicto y la memoria relacional

## 9.1 · Evidencia mínima para afirmar una capacidad

- Definición del constructo y **provenance al corpus** (L-1).
- Al menos una operacionalización ejecutable y una ablación **interpretable**.
- El mundo **exige** la capacidad y existen controles donde no debe ser necesaria.
- Instrumentos **calibrados contra casos conocidos**.
- Efecto reproducible entre semillas, no dependiente de un artefacto del runtime.
- **La primera divergencia ocurre en la intervención declarada.**
- Cambio **funcional**, no sólo interno.
- Dominio declarado: mundo, recursos, historia, versión del algoritmo, métricas.

Y la forma de la afirmación respeta L-2: nunca «memoria funciona», siempre **«esta
operacionalización de memoria, implementada como A₂, en composición con {…}, bajo el mundo W, con
estas métricas»**.

## 9.2 · El hipergrafo como memoria relacional acumulativa

El hipergrafo **no es una visualización bonita del corpus**. Su función es ser la **memoria
relacional científica** del programa.

Una relación ordinaria `A → B` se queda pequeña. Hace falta representar:

```
{ memoria, predicción, planificación }  ──evidencia──→  adaptación
                                        bajo D4, dificultad > k
```

Eso es una relación **n-aria con roles y contexto**. El hipergrafo debe vincular:

```
fuentes ↔ conceptos ↔ algoritmos ↔ capacidades ↔ composiciones
        ↔ mundos ↔ métricas ↔ resultados ↔ evidencia
```

Entonces, tras 100 000 ejecuciones, Terrario no tendrá 100 000 ficheros. Tendrá **un mapa causal
acumulado del espacio de diseño de inteligencia**.

**Estado medido:** el hipergrafo verifica el sha256 del PDF real y soporta roles — eso funciona. Lo
que **no** puede hacer es adjuntar evidencia (`corroboration_status` sólo sabe negar), registrar
contexto, ni tipar dependencias. Hoy es almacén de estructura, no de conocimiento acumulado.

## 9.3 · Estados de una afirmación

`EXPLORATORY` · `CONFIRMATORY` · `SUPPORTED` · `REFUTED` · `NON_IDENTIFIABLE` · `SUPERSEDED` ·
`REPLICATION_PENDING`

Una reinterpretación **reclasifica**, no borra (**I-12**).

---

# 10 · El reparto

| Componente | Responsabilidad |
|---|---|
| **Corpus** | conceptos, teorías, relaciones, controles metodológicos |
| **Ontología / hipergrafo** | constructos comparables, roles, dependencias, provenance, memoria relacional |
| **Terrario** | operacionalizar, implementar, otorgar, componer, presionar y medir — **produce el motor de inteligencia** |
| **RNFE** | ecología de razonamiento; el ser consume inteligencia de ahí |
| **Genesis** | el andamiaje donde el ser va montado: la red neuronal con sus hiperparámetros |

---

# 11 · Invariantes de gobierno

| | |
|---|---|
| **I-01** | Corpus ≠ verdad |
| **I-02** | Módulo ≠ capacidad |
| **I-03** | Capacidad otorgada ≠ contenido aprendido |
| **I-04** | Reward ≠ inteligencia |
| **I-05** | **Mundo declarado = mundo ejecutado** — semántica única y **versionada** |
| **I-06** | Observador pasivo |
| **I-07** | Instrumento falsable |
| **I-08** | Ausencia ≠ cero |
| **I-09** | Intervención pura |
| **I-10** | Provenance extremo a extremo |
| **I-11** | Variedad real |
| **I-12** | Historia preservada |
| **I-13** | Exploratorio ≠ confirmatorio |
| **I-14** | Ser reemplazable |

---

# 12 · Gates de trabajo

Los invariantes dicen qué cuenta como conocimiento. Los gates dicen **en qué orden trabajar**.
Detalle en `GATES_DE_TRABAJO_01.md`.

| | | comando |
|---|---|---|
| **G1** | Documentación antes que construcción | `scripts/cartografia_check.py --tarea <tipo>` |
| **G2** | Alcance del defecto antes de la reparación | `grep` de los sitios que lo alcanzan |
| **G3** | El instrumento se falsa por su **entrada** | un test por instrumento |
| **G4** | Intervención pura antes de atribuir | `scripts/purity_check.py` |
| **G5** | Declarar ruta de ejecución y versión de semántica | en cada artefacto |
| **G6** | Staging explícito | nunca `git add -A` |

---

# 13 · Estado real del proceso

| Eslabón | Estado |
|---|---|
| corpus → conceptos | **roto** — grafo vacío; el formato del importador no existe |
| concepto → operacionalización | **ausente** — no hay ciclo de madurez ni ficha completa |
| operacionalización → algoritmo | **implícito** — los algoritmos existen sin contrato declarado |
| algoritmo → capacidad otorgada | ✅ **funciona** |
| capacidad → agente | **acoplado a A4** (`agent_composition` → `a4_advanced.DEFAULT_CONFIG`) |
| agente → mundo | **en reparación** — `run_step` unificado; falta encender el lifecycle en el banco |
| combinación → conducta | **parcial** — 8 de 10 intervenciones puras |
| conducta → inferencia causal | **bloqueado** — 16 de 22 mallas sin control |
| inferencia → hipergrafo | **roto** — no se puede adjuntar evidencia a una hiperarista |
| hipergrafo → nueva composición | **inexistente** |

## 13.1 · Orden de conexión

1. **Paridad de física** — que «lo que pasó» tenga una sola respuesta.
2. **Nivel 1 completo** — premisa, mundo de control, criterio de dominio. Y correrlo.
3. **Corpus → concepto → algoritmo** — en paralelo: ficheros disjuntos.
4. **Instrumentos** — calibrar las 16 mallas; unificar los dos registros.
5. **Cruzar el cortafuegos** — la primera evidencia de la historia del proyecto.
6. **Cerrar el ciclo** — que la evidencia vuelva al hipergrafo.

## 13.2 · Lo que no cambia

Que un experimento falle no significa que Terrario haya fallado. Significa que **una
operacionalización concreta, implementada de una forma concreta, bajo un mundo y una composición
concretos, no produjo el efecto predicho**. Se registra, se reclasifica y se sigue.

---

# Apéndice A · Formalismo

Sea el conjunto de conceptos candidatos del corpus:

```
𝒞 = { c₁, …, cₙ }
```

Cada concepto admite varias implementaciones:

```
𝒜(cᵢ) = { aᵢ₁, aᵢ₂, … }
```

Un organismo experimental recibe una composición:

```
S = { a_{i₁j₁}, a_{i₂j₂}, … }
```

y se ejecuta en un mundo que puede cambiar con el tiempo:

```
W_k(θ, t)
```

Terrario observa un vector de fenotipo:

```
Φ(S, W_k, t)
```

La misión experimental es estimar la aplicación

```
(S, W, historia) ⟶ Φ
```

y especialmente las **interacciones**:

```
ΔΦ(cᵢ),   ΔΦ(cᵢ, cⱼ),   ΔΦ(cᵢ, cⱼ, c_k),   …
```

hasta construir una teoría de qué composición produce el fenotipo objetivo de manera **robusta,
persistente, transferible y adaptativa**.

Esto describe Terrario con más precisión que «entrenar un agente».

---

# Apéndice B · Especificaciones doctrinales pendientes

Tres piezas que el canon **declara** y todavía no **define**.

## B.1 · `CONCEPT-TO-CAPABILITY-CONTRACT`

Qué artefactos deben existir exactamente entre

```
Corpus → Concepto → Operacionalización → Algoritmo → Capacidad
```

Es la pieza doctrinal más importante que falta. Sin ella, L-1 y L-2 son declaraciones sin
mecanismo, y hoy las diez capacidades del catálogo las incumplen.

## B.2 · `EXPERIMENTAL-COMPOSITION-MODEL`

Cómo una capacidad se **instala, quita, sustituye, combina y versiona** con independencia de A4.
Medido: hoy la composición sigue ligada a `a4_advanced.DEFAULT_CONFIG`, así que la arquitectura de
código no materializa todavía la misión conceptual.

## B.3 · `INTELLIGENCE-EVIDENCE-HYPERGRAPH`

Qué entra al hipergrafo después de cada experimento:

```
concepto + implementación + composición + mundo + condiciones
        + resultado + incertidumbre + provenance
```

Es lo que convierte la ejecución masiva en **conocimiento acumulativo** y no en una colección
creciente de experimentos.

---

> **En una frase.** Convertir el conocimiento acumulado de la humanidad sobre inteligencia en un
> espacio computacional experimental; operacionalizar sus conceptos como mecanismos falsables;
> otorgarlos y combinarlos en organismos artificiales; someterlos a familias progresivas de mundos
> que hagan visible cada propiedad; medir causalmente el fenotipo resultante; y acumular esa
> evidencia en una teoría computacional de la arquitectura de capacidades que produce un ser
> cibernético autopoiético, persistente, adaptativo, metacognitivo y autoevolutivo.
