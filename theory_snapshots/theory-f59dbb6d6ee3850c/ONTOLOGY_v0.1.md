# ONTOLOGY_v0.1

## Estatus epistemológico

Ontología **descriptiva, comparativa y provisional** construida sobre 171 afirmaciones de 26 fuentes utilizables dentro de una muestra de 30. No define “nuestra inteligencia”, no fusiona escuelas y no convierte frecuencia en causalidad. Cada fila del CSV preserva autor, obra, localización, tipo de evidencia, explicitud y confianza.

## 1. Familias conceptuales

### A. Adquisición y cambio

`learning`, `adaptation`, `fast adaptation`, `continual learning`, `learning-to-learn`, `meta-learning`, `plasticity`, `retention`, `knowledge transfer`, `self-improvement`, `self-rewrite`.

Esta familia contiene al menos tres escalas que no deben fusionarse: cambio de conducta/conocimiento, cambio de velocidad o estrategia de aprendizaje y cambio del propio programa.

### B. Inferencia, razonamiento e investigación

`factual inference`, `causal relation`, `perceptual inference`, `conceptual analysis`, `reflective thought`, `ordered inquiry`, `eduction of relations`, `reasoning`, `analogical reasoning`, `proof search`.

Hume, Morgan, Dewey, Spearman y los sistemas formales no usan “inferencia” en el mismo nivel. La ontología conserva esas diferencias.

### C. Representación y semántica

`belief`, `symbolic representation`, `iconic representation`, `categorical representation`, `causal world model`, `predictive world model`, `collective mental map`, `policy`, `value function`, `generative model`.

Aquí aparecen tanto contenidos como estructuras computacionales. `REPRESENTACION` no implica que dos objetos sean equivalentes funcionalmente.

### D. Memoria, experiencia y conocimiento

`memory`, `short-term memory`, `notebook memory`, `shared external memory`, `experience`, `prior knowledge`, `knowledge accumulation`.

Memoria queda como `RECURSO` provisional, pero James la trata también como proceso autobiográfico y Clark–Chalmers extiende su soporte fuera del organismo. Debe revisarse en T2.

### E. Atención, selección y control

`attention`, `selection`, `policy selection`, `exploration-exploitation balance`, `executive control`, `configurator`, `regulation`, `feedback`, `requisite variety`, `precision`.

La recurrencia transversal no demuestra identidad: selección atencional, selección de acción, selección natural y selección de políticas son homónimos parciales.

### F. Objetivo, valor y motivación

`goal`, `reward`, `intrinsic reward`, `utility function`, `cost module`, `variational free energy`, `action preference`, `purpose`.

Las teorías difieren en si el valor es externo, interno, aprendido, dado o axiomático. Ninguna fuente de esta muestra demuestra modificación autónoma abierta de objetivos.

### G. Acción, agencia y entorno

`action`, `epistemic action`, `exploration`, `agent-environment interaction`, `behavior`, `goal achievement`, `planning`, `state sensing`.

Para RL, inteligencia universal e inferencia activa, la acción es estructural. Para Spearman o James no es condición explícita del constructo medido.

### H. Social, distribuido y colectivo

`theory of mind`, `mental-state attribution`, `social prediction`, `coordination`, `stigmergy`, `local interaction`, `global organization`, `collective intelligence`, `coupled system`.

La unidad candidata de inteligencia se desplaza del individuo a sistemas acoplados y colectivos con memoria externa.

### I. Creatividad y generación

`creative thinking`, `preparation`, `incubation`, `illumination`, `verification`, `intimation`, `randomness`, `invention`, `imagination`.

Creatividad aparece como proceso coordinado y verificable en Wallas; la aleatoriedad en Dartmouth es una hipótesis incompleta, no un componente suficiente.

## 2. Conceptos recurrentes por número de relaciones

| Concepto provisional | Incidencias |
|---|---:|
| intelligence | 19 |
| learning | 8 |
| creative thinking | 6 |
| continual learning | 6 |
| reflective thought | 5 |
| invention | 5 |
| goal achievement | 5 |
| skill-acquisition efficiency | 5 |
| action | 5 |
| collective mental map | 5 |
| experience | 4 |
| association | 4 |
| behavior | 4 |
| regulation | 4 |
| predictive world model | 4 |
| configurator | 4 |
| reinforcement learning | 4 |
| reason | 3 |
| memory | 3 |
| spatial knowledge | 3 |

La tabla mide presencia en los claims seleccionados, no importancia ontológica ni centralidad del corpus completo.

## 3. Relaciones recurrentes

| Relación | Conteo |
|---|---:|
| FACILITA | 38 |
| PARTE_DE | 24 |
| PRODUCE | 21 |
| REQUIERE | 18 |
| DEPENDE_DE | 14 |
| ASOCIADO_CON | 13 |
| MODULA | 11 |
| RELACION_INCIERTA | 10 |
| USA | 8 |
| INHIBE | 6 |
| CONTRADICE | 3 |
| ACTUALIZA | 2 |
| SELECCIONA | 2 |
| EVIDENCIA_A_FAVOR | 1 |

`FACILITA` domina porque muchas fuentes proponen condiciones contribuyentes sin demostrar necesidad. `REQUIERE` se reservó para condiciones explícitas; `RELACION_INCIERTA` codifica insuficiencia o cautela cuando el vocabulario inicial no dispone de `NO_ES_SUFICIENTE`.

## 4. Conceptos raros pero potencialmente fundamentales

- **Reconocimiento de ignorancia:** no aparece como constructo central en la muestra. La duda de Dewey y los límites de demostrabilidad de Schmidhuber son vecinos, no equivalentes.
- **Provability limit:** limita la auto-mejora incluso cuando una modificación podría ser útil.
- **Developer-aware generalization:** atribuye priors al sistema ampliado con su desarrollador; corrige falsas apariencias de generalidad.
- **Epistemic action:** muestra que actuar puede modificar el problema cognitivo, no sólo el mundo como objetivo final.
- **Requisite variety:** formaliza un límite estructural de regulación, pero no basta para llamar inteligente al regulador.
- **Intimation:** propone un estado preconsciente parcialmente accesible antes de la iluminación creativa.
- **Intrinsic meaning:** introduce autonomía semántica como criterio no capturado por rendimiento.

## 5. Conceptos difíciles de clasificar

| Concepto | Ambigüedad |
|---|---|
| intelligence | Capacidad, medida, propiedad disposicional, factor latente o propiedad organizacional según la fuente. |
| general factor g | Constructo estadístico, causa latente o resumen correlacional; T1 no decide. |
| memory | Recurso, proceso reconstructivo, representación autobiográfica o componente externo. |
| attention | Mecanismo de selección, recurso limitado o control ejecutivo. |
| adaptation | Capacidad, resultado conductual, proceso evolutivo o regulación. |
| creativity | Capacidad, proceso multietapa o resultado novedoso; la muestra no permite fijar tipo único. |
| collective intelligence | Capacidad del grupo, resultado comparativo o propiedad emergente de organización. |
| precision | Exactitud conductual en Morgan; parámetro/confianza en inferencia activa. Es homónimo técnico. |

## 6. Respuestas a las 12 preguntas analíticas

### 1. Propiedades en tradiciones independientes

Aprendizaje/adaptación, selección entre alternativas, memoria/experiencia, representación de estados, anticipación/predicción, objetivos/valor y coordinación aparecen en filosofía, psicología, cibernética, IA y agencia. La convergencia es funcional; los mecanismos no son idénticos.

### 2. Conceptos confundidos con inteligencia

Rendimiento, habilidad adquirida, conocimiento acumulado, precisión, previsión instintiva, racionalidad, escolaridad, reconocimiento de patrones y mera simulación. Morgan y Chollet ofrecen los controles de insuficiencia más explícitos.

### 3. Facultades que pueden existir sin sistema inteligente

Precisión y previsión instintiva (Morgan), habilidad fija (Chollet), reflejos/conexiones conductuales (Thorndike), regulación (Ashby, inferencia analítica), patrón reconocible y símbolos no fundamentados (Lake/Harnad). La conclusión es por criterio de autor o contraste, no universal.

### 4. Teorías que necesitan acción vs. sólo cognición

Acción estructural: Legg–Hutter, Sutton–Barto, Friston et al., LeCun, Pathak, Heylighen y Clark–Chalmers. Acción no explícitamente necesaria: Spearman, Terman, James y parte de Dewey/Hume. Morgan incluye conducta como evidencia, pero separa inteligencia perceptiva de acción precisa.

### 5. Creatividad como componente necesario

Dartmouth la incluye como problema de IA, pero su vínculo con aleatoriedad es incompleto. Wallas describe su proceso, no afirma que toda inteligencia requiera creatividad. En esta muestra **no hay argumento suficiente para creatividad como condición universal**.

### 6. Selección entre alternativas

James: selección en construcción perceptiva; Sutton–Barto: políticas y exploración-explotación; Friston et al.: selección de políticas; Heylighen: preferencias sobre enlaces; Ashby: regulación frente a perturbaciones; Darwin: selección natural. Son mecanismos distintos y no deben fusionarse.

### 7. Reconocimiento de ignorancia

No hay tratamiento directo comparable a una teoría de “sé que no sé”. Dewey exige sostener duda; Schmidhuber reconoce límites de prueba; Pathak usa error de predicción. Son candidatos relacionados, no evidencia de metacognición epistémica.

### 8. Inteligencia como adaptación

Chollet la aproxima a adquisición/generalización eficiente; Legg–Hutter la integra como medio para lograr metas en entornos amplios; Ashby formaliza adaptación/regulación sin identificarla con inteligencia. Morgan impide usar mero ajuste preciso como criterio suficiente.

### 9. Inteligencia como adquisición de capacidades

Chollet es el caso explícito; MAML operacionaliza aprender a adaptarse; Parisi et al. añaden retención y transferencia; Lake et al. explican adquisición rápida mediante priors, causalidad y composicionalidad. Terman mide estados de capacidad más que eficiencia de adquisición.

### 10. Inteligencia como coordinación de subsistemas

LeCun coordina percepción, modelo del mundo, memoria, coste y actor mediante configurador; Wallas coordina fases y procesos conscientes/no conscientes; Ashby construye jerarquías de regulación; Heylighen coordina agentes mediante memoria compartida y estigmergia.

### 11. Relaciones candidatas a hiperaristas

1. `{prior knowledge, compositionality, learning-to-learn, causal world model} → rapid generalization`.
2. `{agent, environment, goal, percept, action, value} → universal-intelligence performance`.
3. `{plasticity, stability, retention, transfer} → continual learning`.
4. `{preparation, incubation, illumination, verification} → creative achievement`.
5. `{problem states, actions, preferences, shared memory, coordination} → collective intelligence`.
6. `{iconic representation, categorical representation, sensory grounding} → intrinsically meaningful symbols`.
7. `{axioms, proof search, utility function, computational resources} → certified self-rewrite`.
8. `{perception, world model, memory, cost, actor, configurator} → autonomous planning/action`.

Ninguna se convierte todavía en hiperarista causal: T1 sólo detecta co-requisitos propuestos.

### 12. Frecuencia vs. argumento causal

Frecuentes por diseño de muestra: learning, intelligence, action, representation. Con soporte causal/formal más fuerte: requisite variety→regulation (derivación), prediction error→intrinsic reward→exploration (algoritmo/experimentos), action→future reward/state (formalización RL), components→symbol grounding (argumento constitutivo), proof→self-rewrite (construcción formal). Frecuencia no sustituye evidencia.

## 7. Huecos disciplinarios y de extracción

1. Desarrollo cognitivo: ninguna de ocho obras tiene texto completo.
2. Neurociencia de inteligencia: el único supuesto texto abierto es un PDF incorrecto.
3. Inteligencia social empírica y swarm intelligence: casi todas las obras están restringidas.
4. Creatividad: sólo Wallas está disponible y requiere OCR; falta contraste contemporáneo.
5. Psicometría: cobertura primaria histórica, pero falta psicometría moderna (CHC, múltiples inteligencias, triárquica) en texto completo.

## 8. Reglas para T2

- No fusionar `adaptation`, `plasticity`, `flexibility`, `accommodation` ni `adjustment` hasta recuperar Piaget y neurociencia.
- Separar homónimos: `selection`, `precision`, `representation`, `value`, `memory`.
- Añadir relación candidata `NO_ES_SUFICIENTE` o conservar una tabla explícita de insuficiencia; `RELACION_INCIERTA` es demasiado general.
- Modelar la frontera del sistema (`individual`, `coupled system`, `collective`) como dimensión propia, no como sinónimo de inteligencia.
- Separar evidencia formal, experimental, psicométrica, filosófica, programática e inferida al calcular centralidad o fuerza.
- Reparar archivos erróneos antes de ampliar el grafo; un hash sólo prueba integridad de bytes, no correspondencia bibliográfica.
