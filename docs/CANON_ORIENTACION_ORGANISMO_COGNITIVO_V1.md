# Canon de Orientación del Organismo Cognitivo — v1.0

**Fecha de canonización:** 2026-09-21  
**Proyecto:** Teoría de la Inteligencia / Terrario / Génesis  
**Estado:** CANÓNICO  
**Tipo:** Orientación arquitectónica y experimental  
**Relación con otros cánones:** Complementa, pero no sustituye, el *Canon del Ser — Premisas Fundacionales* del 2026-09-20.

---

## 0. Declaración canónica breve

La orientación inicial del programa es estudiar la construcción de inteligencia como un proceso de **composición progresiva de unidades cognitivas simples**, usando como analogía organizativa el paso desde un organismo unicelular con proto-órganos funcionales hacia una organización pluricelular especializada.

La analogía es deliberada, pero **no es una afirmación biológica literal**. Terrario no presupone que la inteligencia artificial deba copiar células, tejidos, órganos o cerebros biológicos. La biología sirve aquí como fuente de una idea estructural: **partes heterogéneas, especializadas y relativamente autónomas pueden coordinarse de tal forma que aparezcan capacidades que ninguna de ellas posee por separado**.

La orientación experimental es, por tanto:

> **partir de capacidades y mecanismos simples; medir sus composiciones; identificar cuándo la composición abre posibilidades funcionales nuevas; y estudiar si esas unidades pueden organizarse progresivamente en estructuras cognitivas de nivel superior.**

---

# I. La analogía del organismo unicelular

En la primera etapa, el sistema debe entenderse **como si fuera un organismo unicelular cognitivo extremadamente simple**.

Esta formulación no significa que el agente sea una célula artificial ni que deba reproducir bioquímica celular. Significa únicamente que, experimentalmente, tratamos al organismo como una **unidad integrada única** que contiene un número pequeño de mecanismos funcionales elementales.

Esos mecanismos pueden compararse, por analogía, con **proto-órganos**: piezas funcionales simples que participan en procesos como percibir, conservar información, aprender regularidades, modificar una acción, regular una variable interna, explorar, actualizar una predicción o seleccionar una respuesta.

En esta fase importa saber, para cada unidad:

1. qué función puede expresar;
2. qué mecanismo se le suministra;
3. qué contenido u organización debe adquirir;
4. bajo qué mundo y condiciones funciona;
5. qué recursos necesita;
6. qué falla cuando se amputa;
7. qué capacidades no posee;
8. qué ocurre cuando se combina con otras unidades.

La prioridad no es maximizar rendimiento global. La prioridad es **construir una cartografía causal y composicional del organismo simple**.

---

# II. Distinción fundamental: analogía biológica ≠ ontología biológica

Esta distinción es obligatoria en todo el proyecto.

## II.1 Lo que SÍ afirma el canon

La biología ofrece una analogía fértil para estudiar:

- especialización funcional;
- división de trabajo;
- coordinación entre unidades;
- dependencia mutua;
- redundancia;
- inhibición;
- cooperación;
- sustitución parcial;
- regulación;
- acoplamiento;
- organización jerárquica;
- aparición de funciones colectivas;
- transición desde unidades relativamente simples hacia organizaciones superiores.

Estas propiedades pueden inspirar preguntas experimentales sobre sistemas artificiales.

## II.2 Lo que NO afirma el canon

El canon **no afirma** que:

- una primitiva cognitiva sea literalmente una célula;
- un módulo sea literalmente un órgano;
- una colección de agentes constituya automáticamente un organismo pluricelular;
- la inteligencia artificial deba imitar la anatomía humana;
- la evolución biológica sea el único camino posible hacia inteligencia;
- las redes neuronales deban reproducir neuronas biológicas;
- el cerebro humano sea la arquitectura objetivo;
- la cognición artificial deba tener tejidos, metabolismo o genética;
- toda propiedad útil de organismos biológicos deba transferirse al sistema artificial.

La correspondencia es **funcional y organizativa**, no literal.

## II.3 Regla de lenguaje

Cuando se usen términos como:

> célula, órgano, organismo, tejido, pluricelular, cerebro

se entenderán como **analogías de organización**, salvo que un documento indique explícitamente que está hablando de biología real.

No se utilizará la analogía para declarar una equivalencia ontológica que los experimentos no hayan demostrado.

---

# III. Qué representa una “primitiva” en esta orientación

Una primitiva no debe entenderse automáticamente como el átomo último de la inteligencia.

En el programa actual, una primitiva es mejor definida como:

> **una unidad funcional suficientemente acotada para ser manipulada, suministrada, lesionada, combinada y evaluada experimentalmente dentro del vocabulario vigente.**

Por eso deben mantenerse separadas las siguientes propiedades:

- `BOUNDARY_KNOWN`: conocemos suficientemente qué incluye y qué excluye la unidad;
- `MINIMAL_UNDER_CURRENT_VOCABULARY`: no conocemos actualmente una descomposición experimentalmente relevante más fina;
- `NOT_ESTABLISHED`: la minimalidad no ha sido demostrada.

Una unidad puede ser útil experimentalmente sin ser ontológicamente indivisible.

---

# IV. El paso hacia la analogía pluricelular

La transición importante del programa no consiste simplemente en añadir más módulos.

Un sistema con cien módulos desconectados sigue siendo, en esta analogía, una colección de partes; no necesariamente una organización pluricelular cognitiva.

La transición comienza cuando aparecen unidades que:

1. conservan identidad funcional;
2. poseen funciones parcialmente especializadas;
3. interactúan mediante interfaces identificables;
4. modifican el espacio de posibilidades de otras unidades;
5. pueden cooperar o competir;
6. pueden inhibirse, facilitarse, sustituirse o regularse;
7. pueden formar composiciones estables;
8. permiten que el conjunto exprese capacidades no disponibles a las partes aisladas.

Por tanto:

> **pluricelularidad, en esta analogía, significa organización funcional de múltiples unidades especializadas, no simple multiplicidad.**

---

# V. El foco “cerebral” de la analogía

El organismo futuro no pretende reproducir un cuerpo biológico completo.

El proyecto está interesado principalmente en el equivalente funcional de un **sistema nervioso/cognitivo en desarrollo**: mecanismos capaces de adquirir, conservar, transformar, coordinar y utilizar capacidades.

Por eso, aunque Terrario pueda contener variables de viabilidad, perturbaciones, sensores, actuadores y condiciones ambientales, el objetivo principal no es modelar todos los órganos de un animal.

La pregunta central es:

> **¿cómo puede una colección de unidades cognitivas simples organizarse progresivamente hasta formar una arquitectura capaz de adquirir y coordinar capacidades cada vez más generales?**

La analogía con el “cerebro” señala el foco funcional del proyecto; **no prescribe una copia del cerebro humano**.

---

# VI. El centro experimental: composición

El objeto científico central de esta etapa es la **composición de capacidades o mecanismos**.

Para una colección de primitivas:

\[
P_1, P_2, \ldots, P_n
\]

no basta preguntar qué hace cada una individualmente.

Debemos estudiar composiciones:

\[
S \subseteq \{P_1,\ldots,P_n\}
\]

bajo un scope experimental explícito:

\[
\Omega = (W, O, A, B, R, V, I, \ldots)
\]

que incluya, según corresponda:

- mundo;
- organismo/agente;
- presupuesto;
- recursos;
- sensores;
- actuadores;
- versión de implementación;
- instrumento;
- protocolo;
- controles;
- perturbaciones.

La misma composición puede producir resultados diferentes bajo scopes distintos sin constituir contradicción.

---

# VII. Lo que buscamos: nuevos grados de libertad

La orientación del programa no es buscar únicamente:

- más reward;
- más accuracy;
- más supervivencia;
- más cobertura;
- más memoria;
- menor error;
- mayor velocidad.

Esas mejoras pueden ser importantes, pero no prueban por sí mismas que haya surgido una capacidad cualitativamente nueva.

La pregunta más fuerte es:

> **¿la composición abre una posibilidad funcional que el organismo no podía realizar antes?**

A esa posibilidad nueva la tratamos provisionalmente como un **nuevo grado de libertad funcional/cognitivo**.

Este canon fija la pregunta, pero **no fija todavía la definición operacional de grado de libertad**. Esa definición pertenece a una fase experimental posterior y deberá ser construida y falsificada explícitamente.

Por tanto, en el estado actual:

```text
DOF histórico no medido → NOT_MEASURED
DOF medido sin aumento   → MEASURED_ZERO
DOF con aumento          → sólo después de un instrumento válido
```

`NOT_MEASURED` nunca equivale a cero.

---

# VIII. Emergencia: significado permitido

En este programa, “emergencia” no debe utilizarse como palabra decorativa.

Una capacidad emergente candidata debe satisfacer una afirmación del tipo:

> **la composición de ciertas unidades, bajo un scope determinado, hace accesible una función o posibilidad que no estaba accesible para las unidades relevantes por separado bajo condiciones comparables.**

Esto exige controles.

Como mínimo, para una composición de dos unidades `P_i` y `P_j`, el programa debería poder distinguir:

```text
sin P_i ni P_j
P_i sola
P_j sola
P_i + P_j
```

además de ablaciones y scopes comparables cuando corresponda.

Un aumento cuantitativo no debe etiquetarse automáticamente como emergencia.

---

# IX. De proto-órganos a órganos cognitivos

La jerarquía conceptual de trabajo es:

```text
mecanismos / primitivas
        ↓
composiciones locales
        ↓
capacidades compuestas
        ↓
subestructuras especializadas
        ↓
coordinación entre subestructuras
        ↓
organización cognitiva de nivel superior
```

No se presupone que cada peldaño exista.

El propósito de Terrario es someter esas transiciones a prueba.

Una capacidad superior sólo debe incorporarse al mapa como capacidad real cuando exista evidencia que permita distinguirla de:

- suma aditiva de rendimiento;
- duplicación;
- artefacto instrumental;
- incremento de recursos;
- mayor exposición;
- shortcut;
- información suministrada;
- cambio de mundo;
- cambio accidental de implementación.

---

# X. Heterogeneidad y especialización

El organismo futuro no tiene por qué estar formado por copias idénticas de una misma unidad.

La orientación admite —y probablemente requerirá estudiar— unidades heterogéneas con:

- mecanismos distintos;
- memorias distintas;
- escalas temporales distintas;
- representaciones distintas;
- recursos distintos;
- funciones distintas;
- políticas de actualización distintas;
- diferentes grados de autonomía;
- diferentes relaciones con otras unidades.

La organización superior puede depender precisamente de esa heterogeneidad.

Por tanto, el programa no debe imponer homogeneidad arquitectónica como condición de elegancia.

---

# XI. Identidad antes de integración

Para poder estudiar composición, cada unidad debe conservar suficiente identidad como para responder:

- qué es;
- qué mecanismo utiliza;
- qué se le suministró;
- qué adquirió;
- qué puede hacer aislada;
- qué no puede hacer aislada;
- de qué recursos depende;
- con qué otras unidades interactúa;
- qué cambia al lesionarla;
- qué cambia al combinarla.

Si al integrar unidades se pierde completamente la capacidad de atribuir función o intervención, la composición deja de ser científicamente interpretable.

La integración no debe destruir la trazabilidad causal.

---

# XII. El organismo no es la suma de sus módulos

El canon rechaza dos simplificaciones opuestas.

## XII.1 Reduccionismo trivial

No se asumirá que:

\[
Capability(S)=\sum_{P_i\in S} Capability(P_i)
\]

La composición puede producir:

- redundancia;
- interferencia;
- inhibición;
- dependencia;
- complementariedad;
- sinergia;
- nuevas posibilidades;
- pérdida de posibilidades.

## XII.2 Emergentismo gratuito

Tampoco se asumirá que toda conducta compleja es una propiedad emergente inexplicable.

Siempre que sea posible, Terrario debe buscar:

- mecanismos;
- dependencias;
- intervenciones;
- ablaciones;
- condiciones necesarias;
- condiciones suficientes bajo scope;
- rutas causales.

“Emergente” no sustituye una explicación causal.

---

# XIII. Función del hipergrafo

El hipergrafo debe actuar como memoria causal y composicional del programa.

Debe poder expresar relaciones del tipo:

\[
\{P_a,P_b,P_c\}
\xrightarrow[\Omega]{evidencia}
C_x
\]

sin destruir información sobre:

- scope;
- mundo;
- versiones;
- resultados negativos;
- desconocidos;
- supplied/acquired;
- instrumentos;
- evidencia;
- provenance.

Una misma composición puede tener múltiples aristas bajo diferentes mundos o condiciones.

El hipergrafo no debe convertir automáticamente una observación local en una ley universal.

---

# XIV. Función de Terrario

Terrario es el aparato experimental donde esta orientación se somete a prueba.

No debe decidir por definición que una combinación constituye una nueva capacidad.

Debe permitir:

1. construir la composición;
2. mantener constantes los controles pertinentes;
3. ejecutar mundos adecuados;
4. medir cambios;
5. lesionar componentes;
6. comparar composiciones;
7. preservar evidencia negativa;
8. determinar el scope del resultado;
9. alimentar posteriormente el hipergrafo con evidencia trazable.

La teoría propone relaciones; Terrario las confronta con comportamiento.

---

# XV. Función del corpus

El corpus proporciona conceptos, mecanismos, hipótesis, antecedentes y evidencia externa.

No determina automáticamente la ontología final del organismo.

Debe distinguirse siempre:

```text
concepto extraído de una fuente
≠
descomposición analítica del proyecto
≠
implementación
≠
capacidad adquirida
≠
capacidad demostrada experimentalmente
```

Esta distinción es especialmente importante para las primitivas derivadas del inventario conceptual.

---

# XVI. Función de la IA de ingeniería

Las IAs externas como Claude Code o Codex pueden actuar como operadores de investigación e ingeniería:

- inspeccionar el código;
- implementar mecanismos;
- construir instrumentos;
- ejecutar campañas;
- analizar fallos;
- devolver evidencia estructurada.

Eso no convierte sus inferencias en evidencia experimental.

Una hipótesis formulada por una IA sigue siendo hipótesis hasta ser contrastada.

---

# XVII. Criterio de progreso del programa

El progreso no se medirá principalmente por cantidad de módulos añadidos.

Una secuencia de progreso más adecuada es:

```text
unidad identificada
→ mecanismo caracterizado
→ frontera conocida
→ composición controlada
→ interacción causal identificada
→ posibilidad nueva medida
→ capacidad compuesta reproducida
→ transferencia/scope estudiado
→ integración superior
```

El objetivo es aumentar **estructura explicada**, no complejidad accidental.

---

# XVIII. Qué no debe confundirse

Quedan canónicamente separadas las siguientes parejas:

```text
analogía biológica          ≠ copia biológica
múltiples unidades          ≠ pluricelularidad funcional
módulo                      ≠ órgano literal
primitiva experimental      ≠ átomo ontológico
mejora de rendimiento       ≠ nuevo grado de libertad
nuevo comportamiento        ≠ capacidad nueva demostrada
composición                 ≠ sinergia
sinergia                    ≠ emergencia automáticamente
supplied                    ≠ acquired
concepto                    ≠ mecanismo
mecanismo                   ≠ implementación
implementación              ≠ capacidad adquirida
capacidad local             ≠ capacidad general
NOT_MEASURED                ≠ MEASURED_ZERO
corpus                      ≠ verdad
hipótesis                   ≠ evidencia
organización cerebral       ≠ imitación del cerebro humano
```

Estas distinciones deben conservarse en documentación, código, hipergrafos y experimentos.

---

# XIX. Dirección de largo plazo

La orientación de largo plazo es investigar si puede construirse un ser cibernético cuya inteligencia no dependa de una única arquitectura monolítica, sino de una **ecología organizada de mecanismos y capacidades** que:

- se especialicen;
- se coordinen;
- se modifiquen;
- aprendan;
- intercambien información;
- formen composiciones;
- creen capacidades superiores;
- preserven funciones útiles;
- regulen conflictos;
- amplíen progresivamente el espacio de posibilidades del organismo.

El equivalente artificial de “pluricelularidad” sólo se considerará alcanzado cuando esa organización tenga consecuencias funcionales y causales demostrables.

---

# XX. Forma breve del canon

> **Empezamos con un organismo cognitivo análogo a una célula: una unidad integrada con proto-órganos funcionales simples. No buscamos acumular módulos, sino descubrir qué ocurre cuando esas unidades se combinan. La dirección de desarrollo es hacia una organización análoga a la pluricelularidad, donde unidades cognitivas heterogéneas y especializadas conservan identidad pero cooperan para abrir posibilidades funcionales que ninguna posee aisladamente. La analogía es organizativa, no biológica literal. El criterio científico central será demostrar, mediante intervención y controles, cuándo una composición abre un nuevo grado de libertad o capacidad, en lugar de confundir mayor rendimiento con emergencia.**

---

# XXI. Invariante de interpretación

Ninguna implementación futura podrá invocar este canon para afirmar que una estructura es “célula”, “tejido”, “órgano”, “cerebro” u “organismo pluricelular” en sentido literal.

Los términos describen una **orientación de organización funcional**.

La transición entre niveles sólo se considerará científicamente sustentada cuando existan observables, controles e intervenciones que demuestren qué nueva organización o posibilidad funcional apareció.

---

# XXII. Estado experimental actual al canonizar

En el momento de esta canonización:

- existe un Mapa de Composición v0.1 en proceso de congelación;
- existen primitivas históricamente operacionalizadas y otras derivadas analíticamente;
- las composiciones históricas importadas no midieron grados de libertad;
- `NOT_MEASURED` se mantiene separado de `MEASURED_ZERO`;
- todavía no existe una definición operacional canónica de grado de libertad;
- N1.0 todavía no debe iniciarse hasta cerrar esa definición;
- la transición hacia organización pluricelular cognitiva es una **dirección de investigación**, no un resultado ya alcanzado.

---

## Regla final

> **Construir primero unidades simples que puedan entenderse causalmente; después estudiar sus composiciones; después medir si esas composiciones abren nuevas posibilidades; y sólo entonces permitir que esas unidades se organicen en estructuras cognitivas superiores. Nunca confundir la analogía con una equivalencia biológica ni la complejidad con inteligencia.**
