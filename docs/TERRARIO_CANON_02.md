# Terrario

**Documento canónico · versión 2 · 2026-09-17**

La versión 1 (`Terrario_Mision_Arquitectura_Cientifica_v1`) está organizada como doctrina: misión,
límites, objeto, corpus, ontología, operacionalización. Esta versión está organizada como **el
proceso**, en el orden en que Wis lo describió, porque ese orden es el que se ejecuta. Los
elementos de la v1 que aportan están absorbidos en el punto del proceso donde actúan, no en un
capítulo aparte.

**Autoridad:** la descripción de Wis es la referencia. La v1 aporta. La cartografía del código
(`CARTOGRAFIA_TERRARIO_01.md`, HEAD `427f8428`) aporta el estado medido, y sólo el estado medido.

---

## 0 · Qué entrega Terrario

Todo lo demás está construido. RNFE aporta la ecología de razonamiento; Genesis es el andamiaje
donde el ser va montado, con su red neuronal y sus hiperparámetros. **Lo que falta es el motor de
inteligencia, y eso es lo que Terrario produce.**

Eso fija el listón: Terrario no entrega un informe de qué resultó significativo. Entrega **qué
habilidades, en qué composición, con qué roles**, con evidencia causal detrás y su dominio
declarado — precisa como para construirla.

Consecuencia práctica: una habilidad que gane contra su control pero **no componga** con las demás
no sirve. Lo que se busca son propiedades de sistema —transferencia, robustez, persistencia,
recuperación, reorganización sin perder viabilidad— y ésas no se infieren sumando banderas.

### La pregunta madre

> ¿Cuántas habilidades y de qué tipo hacen falta para un ser cibernético **autopoiético,
> metacognitivo, autoevolutivo y persistente**?

---

## 1 · El corpus: de dónde salen los conceptos

La inteligencia no es un elemento. Es un **cúmulo**: memoria, conocimiento, curiosidad,
creatividad, acción, imaginación, previsión, formación de hipótesis. El corpus es de donde se
sacan los candidatos a ser parte de ese cúmulo.

Su función es impedir que el proyecto invente toda su teoría desde una sola intuición
arquitectónica. Fue construido **independientemente de RNFE y Genesis**, precisamente para reducir
el sesgo de confirmación.

**Corpus v1:** 152 referencias en 16 categorías, 65 copias completas, provenance criptográfica.
Filosofía, evolución e inteligencia animal, psicología, desarrollo cognitivo, neurociencia,
cibernética, ciencia cognitiva, IA clásica, AGI formal, aprendizaje y metaaprendizaje, agencia,
creatividad, inteligencia social, filosofía de la mente, medición.

### Lo que el corpus decide y lo que no

**Decide:** qué conceptos son candidatos, qué significa cada uno en su fuente, qué mecanismos
propone cada tradición, qué controles metodológicos existen contra falsos positivos — y,
crucialmente, **qué combinaciones vale la pena probar**.

Esto último es lo que hace tratable el problema. Cuando una teoría propone memoria + modelo del
mundo + planificación como un sistema funcional con roles distintos, esa conjunción entra al
espacio confirmatorio **con un motivo**. Las demás quedan como exploración etiquetada.

**No decide:** que una teoría sea correcta. La autoridad sobre el comportamiento del ser viene del
experimento, no del prestigio de la fuente.

### Estado medido

| | |
|---|---|
| Corpus físico | **existe** — 42 PDFs en `/home/wis/Documentos/teoria de la inteligencia/` |
| Grafo de referencias | **vacío** — 0 filas en 22 tablas |
| Formato que el importador espera | **no existe en disco** — no hay `CORPUS_MANIFEST.jsonl` |
| Catálogo de fuentes | existe en otro formato: `SOURCE_PROVENANCE_v0.3.csv` del snapshot de teoría, 44 fuentes |

**El eslabón corpus → grafo está roto.** Hay dos sistemas paralelos que nunca se tocaron.

---

## 2 · De concepto a algoritmo

Un concepto es una unidad teórica. Un agente sólo puede ejecutar mecanismos. Operacionalizar es
traducir lo primero a lo segundo de forma que su presencia, ausencia y variantes se puedan
intervenir y medir.

**No hay traducción uno a uno.** «Memoria» puede volverse buffer episódico, memoria asociativa,
memoria de trabajo o consolidación paramétrica. Y un mismo algoritmo puede materializar varios
conceptos. El enlace concepto ↔ algoritmo es **muchos a muchos**.

### La ficha mínima

Cada operacionalización debe responder: concepto fuente y provenance · constructo · mecanismo ·
entrada/salida · estado que conserva · **autoridad causal** (dónde puede cambiar una decisión) ·
variantes · **ablación** (cómo se retira sin tocar otras capacidades) · métrica · **control
negativo** (qué caso debe dar cero) · **control positivo** (qué caso construido debe detectar) ·
**mundos requeridos**.

### El principio que gobierna este paso

> **El nombre del módulo no es evidencia.** Un componente llamado `Planner`, `WorldModel`,
> `Memory` o `Uncertainty` sólo cuenta como operacionalización de ese concepto si su ruta causal y
> su comportamiento medido cumplen la definición que se está probando.

Medido, y por eso el principio importa: el `Planner` actual hace **random shooting** sobre un
modelo del mundo que no predice —`energy_head` tiene dispersión 0.0037 sobre una cantidad que
varía 2.0— así que funciona como fuente de exploración aleatoria, no como planificación. Y el
`WorldModel` no ha demostrado predicción energética útil.

### Estado medido

10 conceptos en el catálogo (`agent_composition.CONCEPTS`), cada uno con `key`, `label`, `purpose`,
`without_it`, `block`, `corpus_block`.

**`corpus_block` es un entero que ningún fichero lee.** No hay `reference_id`, ni `claim_id`, ni
locator. El puente corpus → algoritmo no existe. El propio código lo admite para el único concepto
sin bloque: *«saying it did would be a fabricated citation»*.

El **ciclo de madurez de concepto** que la v1 declara —RAW → DEFINED → RELATED → OPERATIONALIZABLE
→ IMPLEMENTED → INSTRUMENTED → TESTED → RETAINED/REVISED/REJECTED— **no está implementado**. Los
224 conceptos canónicos son CSV congelados en un snapshot, sin estado y sin transición.

---

## 3 · De algoritmo a habilidad otorgada

**Otorgar una habilidad** es incorporar al organismo un mecanismo candidato que representa un
concepto. No garantiza que el organismo lo use bien. Hay que comprobar tres cosas distintas: si el
mecanismo tiene **autoridad causal**, si **se integra** con los demás, y si su presencia cambia la
conducta **en un mundo que realmente exija** la capacidad.

### Los tres niveles que no se pueden confundir

| Nivel | Origen | Pregunta experimental |
|---|---|---|
| **Capacidad otorgada** | decisión humana desde el corpus | ¿qué ocurre al instalarla, retirarla o variarla? |
| **Contenido adquirido** | interacción del organismo con el mundo | ¿qué aprende o conserva gracias a ella? |
| **Conducta emergente** | interacción entre mecanismos, historia y mundo | ¿es robusta, causal y transferible? |

Confundirlos impide saber qué se descubrió. **Terrario no espera que el organismo invente el
catálogo de habilidades: lo construye y lo prueba.** El aprendizaje es una habilidad más que se
otorga y se mide, no un milagro que se espera.

### Estado medido

Este eslabón **funciona**. `agent_composition` → `sandbox_runtime` es la única parte de la capa de
conocimiento dentro del bucle de ejecución, con validación fail-closed: una clave desconocida
levanta `CompositionError`.

---

## 4 · El agente: quién recibe la habilidad

Los agentes son **especímenes**, no identidades sagradas. A0 es control aleatorio; A4 es el
espécimen actual con 1 351 617 parámetros; familias futuras pueden tener arquitecturas totalmente
distintas.

Se controla: composición de capacidades y variantes, estado inicial y parámetros, sensores y
actuadores, recursos y límites, memorias y persistencia, reglas de aprendizaje, semillas, historia
previa y exposición.

### Lo que A4 es hoy, sin los nombres

```
encoder convolucional → núcleo SSM lineal → estado de 640 dims
  (latente 128 + hidden 256 + contexto episódico 128 + contexto largo plazo 128)
    ↓
política lineal sobre 25 acciones, temperatura por energía
    ↓
con probabilidad ½: el planner propone una de 10 secuencias aleatorias de 5 pasos,
                     puntuadas por un modelo del mundo que no predice
```

Medido: 300 pasos producen **300 actualizaciones del optimizador** y **3 eventos informativos**.
El 99 % del gradiente es el coste metabólico constante. Y con 1536 ejemplos informativos **puros**
—256 veces la exposición de una vida— la cabeza de energía no se separa del azar.

---

## 5 · El mundo: quien impone la demanda

Los mundos no son escenarios para entretener al agente. Son **instrumentos de demanda**.

> **Si el mundo no exige la capacidad, una ablación sin efecto no prueba nada.**

Ésa es la regla más violada del proyecto. Medí que el núcleo temporal, la incertidumbre y las dos
memorias «no mueven nada» en D4T. Pero D4T es esencialmente markoviano: la consecuencia de
consumir depende del canal del objeto adyacente, visible en el instante. Eso no dice nada sobre la
memoria — dice que D4T no la exige.

### Cada nivel necesita dos mundos, no uno

| | |
|---|---|
| **Mundo exigente** | donde la capacidad es necesaria |
| **Mundo de control** | donde **no** debería ayudar |

Sin el segundo, un efecto no se distingue de un artefacto.

### Principio de variedad

Nada relevante tiene por qué permanecer estático: el mundo, las perturbaciones, las variables
esenciales, la región de viabilidad, sensores, actuadores, representaciones, memorias, estrategias,
recursos, otros agentes, objetivos, grado de observabilidad y ritmo de cambio. Una capacidad que
funciona en una sola configuración no se eleva a principio de inteligencia.

---

## 6 · La escalera: niveles, dificultad creciente, habilidades que se suman

El proceso es **evolutivo**. Se empieza con una o dos habilidades. Se mide. Sube la dificultad y
entran más habilidades. Se mide otra vez. **Los mundos se diseñan cuando se pasa el nivel**, no por
adelantado.

### Por qué esto hace el problema tratable

| Habilidades presentes | Factorial completo |
|---|---|
| 2 | 4 corridas |
| 3 | 8 |
| 4 | 16 |
| 10 | 1024 |
| 46 | astronómico |

Con dos o tres habilidades **se corre el factorial completo y se miden todas las interacciones
exactamente**. No hay que asumir aditividad ni estimar nada.

No es teórico: el tamizado usó un diseño de efectos principales porque 2⁸ era inasumible, y sus
residuos de interacción salieron **ininterpretables por saturación**. Con la escalera nunca se
llega a esa posición.

Así que el nivel hace tres cosas a la vez:

```
nivel N  →  dificultad del mundo ↑
            habilidades presentes ↑
            espacio de combinaciones todavía agotable
```

### La forma de un nivel

```
NIVEL N
  premisa           qué capacidad afirma este nivel que es necesaria, y qué fuente lo propone
  habilidades       qué algoritmos se otorgan
  mundo exigente    dónde la capacidad es necesaria
  mundo de control  donde NO debería ayudar
  aprobación        qué hay que demostrar para pasar al nivel siguiente
```

### La escalera declarada

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

Los mundos existen como escenarios. **Lo que falta de cada peldaño es la premisa, el mundo de
control y el criterio de aprobación.** Sin criterio de aprobación no hay escalera: hay una lista de
escenarios.

### Estado medido, y es incómodo

**Ningún nivel ha sido superado.** `scientific_results = 0` tras 240 intentos de ejecución.

Y todo el trabajo reciente —tamizado, P0, gemelos, adquisición de capacidad— corrió en **D4T**, una
variante del peldaño 4, cuyo estado declarado es `PROTOCOL_NOT_CONFIRMED`, sobre una escalera cuyos
peldaños 0 a 3 nunca se certificaron.

Se estaba midiendo adaptación en un organismo del que no se sabe si distingue diferencias.

### Ejemplo de nivel 1

> **Premisa** — un organismo no puede hacer nada más si no distingue que las cosas difieren.
> **Habilidad** — el encoder perceptivo.
> **Mundo exigente** — D0, donde la conducta correcta depende de la diferencia.
> **Mundo de control** — D0 con todos los objetos idénticos.
> **Aprobación** — la conducta difiere entre ambos mundos, y esa diferencia **desaparece** al
> ablacionar el encoder.

---

## 7 · La combinación: qué pasa cuando se juntan

El objetivo no es coleccionar módulos que individualmente suben una métrica. La inteligencia puede
depender de composiciones donde un mecanismo **habilita, estabiliza, regula o modifica** a otro.

### Tipos de relación entre capacidades

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

El hipergrafo existe para representar esto: una conjunción de tres elementos **con roles distintos**
no se representa fielmente como tres aristas binarias.

### La trampa medida

Una ablación que apaga dos cosas no mide ninguna. El tamizado reportó «modelo del mundo +6.33
comidas» y «planificador +6.67» como dos hallazgos. **Son la misma intervención**: la rama está
condicionada a ambos flags, y con `use_world_model=False` el planner se invoca 0 de 40 veces.

Barrido completo: **8 de 10 intervenciones son puras**; las 2 impuras son exactamente esas.

---

## 8 · La medición: cómo sabemos qué pasó

Hacen falta **dos valideces distintas**:

- **Validez experimental** — ¿la intervención está aislada?
- **Validez de instrumento** — ¿la métrica detecta el constructo que dice medir?

La segunda es la que faltaba. Una métrica plausible puede estar equivocada y producir números
creíbles indefinidamente.

### Las cuatro semánticas que no pueden confluir

```
0              hubo soporte, se calculó, salió cero
NOT_EVALUABLE  no existe soporte — el denominador está vacío
MISSING        falta un dato que el cálculo necesita
INVALID        el dato existe y viola el contrato
```

`conversion = 0` afirma que el organismo tuvo exposiciones informativas y no convirtió ninguna. Con
`N_informative = 0` el mismo 0 no afirma nada. **Son hallazgos opuestos vistiendo el mismo dígito**,
y el laboratorio ya produjo tres por accidente.

### Falsación de instrumentos

Toda métrica pasa controles con respuesta conocida antes de entrar a evidencia: **oráculo**
(techo), **anti-oráculo** (suelo), **caso nulo** (`NOT_EVALUABLE`), **azar analítico**, invariantes
de contabilidad.

Y — lección cara — **el control debe falsar también la entrada, no sólo la salida**. El examen de
capacidad tenía oráculo 1.0, anti-oráculo 0.0 y empate `NOT_EVALUABLE`, los tres verdes, mientras
entregaba observaciones en un formato que el organismo nunca vio entrenando.

### Medir cadenas, no resultados finales

Descomponer la conducta en: oportunidad → percepción → intención → **referencia** → **alcance** →
ejecución → consecuencia → **discriminación** → aprendizaje → retención → transferencia.

Supervivencia o recompensa son demasiado distales para decir dónde se rompió la inteligencia. La
descomposición medida:

```
N_consume = N_nonexistent + N_out_of_range + N_valid + N_other
N_valid   = N_beneficial  + N_harmful      + N_neutral
```

separa tres preguntas que vivían dentro de una sola tasa de fracaso, y hace formulable una cuarta.

### Estado medido

| | |
|---|---|
| Mallas de medición | 22 |
| Con control de falsación | **6** |
| Métricas registradas con controles | 8, con 24 controles |
| **Consumidores de ese registro en producción** | **ninguno** — `assert_reportable` no lo llama nada |
| Registro que sí alimenta el preregistro | otro, con 15 métricas, **ninguna con controles** |
| Métricas `VALIDATED_FOR_CONSTRUCT` | **1** |

Hay **dos sistemas de validez de métricas que no se comunican**, con conjuntos de identificadores
disjuntos.

---

## 9 · El veredicto: qué habilidad es necesaria

### Evidencia mínima para afirmar una capacidad

- Existe definición del constructo y provenance al corpus.
- Existe al menos una operacionalización ejecutable y una ablación **interpretable**.
- El mundo **exige** la capacidad y existen controles donde no debe ser necesaria.
- Los instrumentos están **calibrados contra casos conocidos**.
- El efecto es reproducible entre semillas y no depende de un artefacto del runtime.
- **La primera divergencia ocurre en la intervención declarada.**
- La capacidad produce un cambio **funcional**, no sólo un cambio interno sin consecuencia.
- La afirmación declara su dominio: mundo, recursos, historia, versión del algoritmo, métricas.

### Estados de una afirmación

`EXPLORATORY` · `CONFIRMATORY` · `SUPPORTED` · `REFUTED` · `NON_IDENTIFIABLE` · `SUPERSEDED` ·
`REPLICATION_PENDING`

Una reinterpretación nueva **no borra** resultados anteriores: los reclasifica.

### Reclasificación pendiente de lo ya corrido

| Resultado | Estado propuesto | Razón |
|---|---|---|
| Tamizado: modelo del mundo y planificador | `NON_IDENTIFIABLE` | misma ruta de código |
| Examen de adquisición | `SUPERSEDED` | formato perceptivo inválido |
| P0 · T0 vs T1 | `SUPPORTED`, dominio declarado | válido bajo «runtime Sandbox pre-parity» |
| Curva de eficiencia muestral | `EXPLORATORY` | sin preregistro |
| **Representabilidad R = 1.0** | **limpio** | no construye observaciones ni usa el ciclo de oportunidades |

---

## 10 · El reparto

| Componente | Responsabilidad |
|---|---|
| **Corpus** | conceptos, teorías, relaciones, controles metodológicos |
| **Ontología / hipergrafo** | estructura, roles, dependencias, provenance, hipótesis de composición |
| **Terrario** | materializar, variar, someter a prueba y medir — **produce el motor de inteligencia** |
| **RNFE** | ecología de razonamiento; el ser consume inteligencia de ahí |
| **Genesis** | el andamiaje donde el ser va montado: la red neuronal con sus hiperparámetros |

La evidencia fluye en ambos sentidos sin fusionar los roles. Terrario puede medir partes de
Genesis; Genesis puede incorporar mecanismos respaldados por Terrario.

---

## 11 · Invariantes de gobierno

| | |
|---|---|
| **I-01** | Corpus ≠ verdad — origina candidatos; el experimento decide soporte contextual |
| **I-02** | Módulo ≠ capacidad — un nombre de clase no es evidencia |
| **I-03** | Capacidad otorgada ≠ contenido aprendido — se miden por separado |
| **I-04** | Reward ≠ inteligencia — el resultado agregado no sustituye el diagnóstico causal |
| **I-05** | **Mundo declarado = mundo ejecutado** — semántica única y **versionada** |
| **I-06** | Observador pasivo — instrumentación, UI y almacenamiento no cambian trayectoria |
| **I-07** | Instrumento falsable — ninguna métrica entra a evidencia sin controles conocidos |
| **I-08** | Ausencia ≠ cero — `NOT_EVALUABLE`, `MISSING`, `INVALID` se conservan |
| **I-09** | Intervención pura — la primera divergencia causal ocurre en el mecanismo declarado |
| **I-10** | Provenance extremo a extremo — de fuente a conclusión |
| **I-11** | Variedad real — ni mundo, ni ser, ni relaciones son estáticos |
| **I-12** | Historia preservada — una reinterpretación reclasifica, no borra |
| **I-13** | Exploratorio ≠ confirmatorio — la búsqueda automática no se vuelve hipótesis preregistrada |
| **I-14** | Ser reemplazable — ningún agente actual es sinónimo de Terrario ni de Genesis |

---

## 12 · Gates de trabajo

Los invariantes dicen qué cuenta como conocimiento. Los gates dicen **en qué orden trabajar** para
no fabricarlo por accidente. Cada uno tiene un comando; un gate que dependa de recordarlo no es un
gate. Detalle en `GATES_DE_TRABAJO_01.md`.

| | | comando |
|---|---|---|
| **G1** | Documentación antes que construcción | `scripts/cartografia_check.py` |
| **G2** | Alcance del defecto antes de la reparación | `grep` de los sitios que lo alcanzan |
| **G3** | El instrumento se falsa por su **entrada**, no sólo por su salida | un test por instrumento |
| **G4** | Intervención pura antes de atribuir | `scripts/purity_check.py` |
| **G5** | Declarar ruta de ejecución y versión de semántica | en cada artefacto |
| **G6** | Staging explícito | nunca `git add -A` |

---

## 13 · Estado real del proceso

El ciclo completo está **construido** y **conectado en un solo punto**.

| Eslabón | Estado |
|---|---|
| corpus → conceptos | **roto** — grafo de referencias vacío; el formato que el importador espera no existe |
| concepto → algoritmo | **roto** — `corpus_block` es un entero decorativo; sin provenance |
| algoritmo → habilidad otorgada | ✅ **funciona** |
| habilidad → agente → mundo | **ambiguo** — dos físicas: el banco no ejecuta el ciclo de oportunidades que el escenario declara |
| combinación → reacción | **parcial** — 8 de 10 intervenciones puras |
| reacción → qué habilidad importa | **bloqueado** — 16 de 22 mallas sin control; `scientific_results = 0` |

### Orden de conexión

1. **Paridad de física** — que «lo que pasó» tenga una sola respuesta. Sin esto, superar un nivel
   no es una afirmación comprobable.
2. **Nivel 1 completo** — premisa, mundo de control, criterio de aprobación. Y correrlo.
3. **Corpus → concepto → algoritmo** — en paralelo: toca ficheros disjuntos.
4. **Instrumentos** — calibrar las 16 mallas sin control; unificar los dos registros.
5. **Cruzar el cortafuegos** — publicar la primera evidencia de la historia del proyecto.

### Lo que no cambia

Que un experimento falle no significa que Terrario haya fallado. Significa que **una composición
concreta, bajo un mundo y un mecanismo concretos, no produjo la capacidad medida**. Se registra y
se sigue explorando conceptos y composiciones.

---

> **En una frase.** Tomar la inteligencia descrita por la humanidad como espacio de hipótesis;
> convertir sus conceptos en algoritmos; otorgarlos como habilidades a organismos experimentales;
> soltarlos en mundos de dificultad creciente; medir causalmente su reacción nivel por nivel; y
> usar la evidencia acumulada para construir el motor de inteligencia de un ser cibernético
> autopoiético, metacognitivo, autoevolutivo y persistente.
