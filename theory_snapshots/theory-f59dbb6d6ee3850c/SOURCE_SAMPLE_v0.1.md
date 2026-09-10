# SOURCE_SAMPLE_v0.1

## Alcance y método

Inventario completo del archivo `Teoria_Inteligencia_Corpus_v1.zip` antes de la selección. La muestra contiene exactamente **30 fuentes**: **26 utilizables para extracción**, dos recuperadas parcialmente por OCR y cuatro controles de hueco/integridad sin claims. La selección busca contraste histórico y disciplinario; no se usó afinidad con Genesis/RNFE.

## Inventario del corpus

- Registros bibliográficos: **152**.
- Títulos catalogados distintos: **152**; autorías nominales distintas: **162** (las entradas “et al.” no se expanden sin metadatos adicionales).
- Registros con ruta a texto completo: **65**.
- Archivos físicos únicos: **65**.
- Periodo: **350 a. C.–2026**.
- Idiomas catalogados: **en: 146, eng: 3, eng;grc: 1, zxx: 1, fr: 1**.
- Tipos principales: **paper: 71, book: 68, review: 3, monograph: 2, chapter: 2, proposal: 1, thesis: 1, position paper: 1, edited book: 1, dataset specification: 1, perspective: 1**.
- Categorías: **16**.

| Categoría | Registros | Con archivo | Sin archivo |
|---|---:|---:|---:|
| 01_Filosofia | 8 | 8 | 0 |
| 02_Evolucion_Inteligencia_Animal | 8 | 6 | 2 |
| 03_Psicologia_Psicometria | 14 | 3 | 11 |
| 04_Desarrollo_Cognitivo | 8 | 0 | 8 |
| 05_Neurociencia | 8 | 1 | 7 |
| 06_Cibernetica_Sistemas | 8 | 1 | 7 |
| 07_Ciencia_Cognitiva | 8 | 1 | 7 |
| 08_IA_Clasica | 8 | 2 | 6 |
| 09_Inteligencia_Formal_AGI | 11 | 8 | 3 |
| 10_Aprendizaje_Metaaprendizaje | 14 | 14 | 0 |
| 11_Agencia_Decision_Accion | 11 | 3 | 8 |
| 12_Creatividad_Problemas | 8 | 1 | 7 |
| 13_Inteligencia_Social_Colectiva | 8 | 2 | 6 |
| 14_Filosofia_Mente_Semantica | 8 | 1 | 7 |
| 15_Medicion_Benchmarks | 14 | 12 | 2 |
| 16_Revisiones_Contemporaneas | 8 | 2 | 6 |

## Auditoría de integridad

La verificación comparó título/autor catalogados con el encabezado extraído de los 65 registros con archivo. Se inspeccionaron manualmente los casos dudosos.

- **Seis desajustes confirmados:** TI-0046 contiene un artículo de relatividad; TI-0098 uno de comunicaciones de banda ancha; TI-0116 uno de patrones puntuales; TI-0126 una medida estadística de complejidad; TI-0127 cuadrados latinos; TI-0144 física de protonterapia.
- **Un archivo incompleto:** TI-0064 es sólo una página índice de 535 caracteres, no el artículo de McCarthy.
- **Escaneos sin capa textual útil:** TI-0001, TI-0017 y TI-0102; TI-0012 tiene capa mínima. Para TI-0012 y TI-0102 se aplicó OCR selectivo y se verificó contra imágenes de página. TI-0001 no se usa para claims.
- **Hueco estructural:** desarrollo cognitivo tiene 0/8 textos completos. Por ello TI-0031 se conserva en la muestra como ausencia documentada, no como evidencia.

## Muestra seleccionada

| # | ID | Autor(es) | Año | Obra | Disciplina | Tipo | Estado T1 | Justificación |
|---:|---|---:|---:|---|---|---|---|---|
| 1 | TI-0001 | Aristotle | 350 BCE | De Anima | Philosophy | book | LIMITED_SCAN | Ancla antigua para distinguir percepción, imaginación e intelecto; el PDF carece de capa textual y no se usa para claims. |
| 2 | TI-0004 | David Hume | 1748 | An Enquiry Concerning Human Understanding | Philosophy | book | USABLE | Empirismo: experiencia, hábito, inducción y causalidad; contrapesa el racionalismo. |
| 3 | TI-0006 | William James | 1890 | The Principles of Psychology | Psychology and philosophy | book | USABLE | Psicología funcional: atención, memoria, hábito, selección y continuidad de la experiencia. |
| 4 | TI-0007 | John Dewey | 1910 | How We Think | Philosophy of education | book | USABLE | Pensamiento reflexivo como investigación controlada por duda, evidencia y consecuencias. |
| 5 | TI-0009 | Charles Darwin | 1871 | The Descent of Man, and Selection in Relation to Sex | Evolutionary biology | book | USABLE | Continuidad evolutiva de facultades humanas y animales; curiosidad, imitación, memoria y razón. |
| 6 | TI-0011 | C. Lloyd Morgan | 1890 | Animal Life and Intelligence | Comparative psychology | book | USABLE | Separa inteligencia perceptiva de razón conceptual y niega que precisión o previsión basten. |
| 7 | TI-0012 | Edward L. Thorndike | 1911 | Animal Intelligence: Experimental Studies | Comparative psychology | monograph | USABLE_OCR | Base experimental del aprendizaje animal y de la lectura conducta-conexión; OCR verificado visualmente. |
| 8 | TI-0016 | David Premack; Guy Woodruff | 1978 | Does the Chimpanzee Have a Theory of Mind? | Comparative psychology | paper | USABLE | Cognición social animal: atribución de estados mentales y predicción de conducta. |
| 9 | TI-0020 | Charles Spearman | 1927 | The Abilities of Man | Psychometrics | book | USABLE | Psicometría factorial: factor general, factores específicos y crítica a la ambigüedad de 'inteligencia'. |
| 10 | TI-0021 | Lewis M. Terman | 1916 | The Measurement of Intelligence | Psychometrics | book | USABLE | Operacionalización histórica mediante edad mental, cociente intelectual y pruebas estandarizadas. |
| 11 | TI-0031 | Jean Piaget | 1936 | The Origins of Intelligence in Children | Developmental psychology | book | UNAVAILABLE | Desarrollo cognitivo constructivista; seleccionado para registrar el hueco: no hay texto completo en el corpus. |
| 12 | TI-0046 | Aron K. Barbey | 2018 | Network Neuroscience Theory of Human Intelligence | Network neuroscience | paper | MISMATCH | Neurociencia de redes; el archivo adjunto es un artículo de relatividad y no puede sostener claims. |
| 13 | TI-0049 | W. Ross Ashby | 1956 | An Introduction to Cybernetics | Cybernetics | book | USABLE | Cibernética formal: regulación, realimentación, variedad y jerarquías de control. |
| 14 | TI-0062 | Andy Clark; David Chalmers | 1998 | The Extended Mind | Philosophy of cognitive science | paper | USABLE | Cognición extendida: sistema acoplado organismo-entorno y acción epistémica. |
| 15 | TI-0064 | John McCarthy | 1959 | Programs with Common Sense | Artificial intelligence | paper | INCOMPLETE_HTML | IA clásica y sentido común; el archivo contiene sólo un índice web, no el artículo completo. |
| 16 | TI-0065 | John McCarthy; Marvin Minsky; Nathaniel Rochester; Claude Shannon | 1955 | A Proposal for the Dartmouth Summer Research Project on Artificial Intelligence | Artificial intelligence | proposal | USABLE | Programa fundacional de IA: lenguaje, abstracción, resolución de problemas, aprendizaje y auto-mejora. |
| 17 | TI-0071 | Shane Legg; Marcus Hutter | 2007 | Universal Intelligence: A Definition of Machine Intelligence | Artificial general intelligence | paper | USABLE | Definición formal comparativa basada en logro de objetivos a través de entornos. |
| 18 | TI-0075 | François Chollet | 2019 | On the Measure of Intelligence | Artificial general intelligence | paper | USABLE | Distingue habilidad de inteligencia y formaliza eficiencia de adquisición bajo alcance, priors y experiencia. |
| 19 | TI-0076 | Brenden M. Lake; Tomer D. Ullman; Joshua B. Tenenbaum; Samuel J. Gershman | 2017 | Building Machines That Learn and Think Like People | Artificial intelligence | paper | USABLE | Síntesis cognitivo-computacional: causalidad, física/psicología intuitivas, composicionalidad y aprender a aprender. |
| 20 | TI-0077 | Yann LeCun | 2022 | A Path Towards Autonomous Machine Intelligence | Artificial intelligence | position paper | USABLE | Arquitectura de agente con modelo del mundo, memoria, coste, actor y control ejecutivo configurador. |
| 21 | TI-0079 | Chelsea Finn; Pieter Abbeel; Sergey Levine | 2017 | Model-Agnostic Meta-Learning for Fast Adaptation of Deep Networks | Machine learning | paper | USABLE | Metaaprendizaje operacional: parámetros preparados para adaptación rápida a nuevas tareas. |
| 22 | TI-0084 | German I. Parisi et al. | 2019 | Continual Lifelong Learning with Neural Networks: A Review | Continual learning | review | USABLE | Aprendizaje continuo: adquisición, transferencia, retención y dilema estabilidad-plasticidad. |
| 23 | TI-0087 | David Ha; Jürgen Schmidhuber | 2018 | World Models | Model-based learning | paper | USABLE | Representaciones espacio-temporales comprimidas y entrenamiento de políticas en simulación aprendida. |
| 24 | TI-0090 | Deepak Pathak et al. | 2017 | Curiosity-driven Exploration by Self-supervised Prediction | Exploration | paper | USABLE | Curiosidad computacional como recompensa intrínseca derivada del error de predicción. |
| 25 | TI-0097 | Richard S. Sutton; Andrew G. Barto | 2018 | Reinforcement Learning: An Introduction (Second Edition) | Reinforcement learning | book | USABLE | Agencia y decisión secuencial: metas, recompensa, política, valor y exploración-explotación. |
| 26 | TI-0099 | Thomas Parr; Karl J. Friston | 2017 | Active Inference: A Process Theory | Theoretical neuroscience | paper | USABLE | Inferencia activa: actualización de creencias y selección de políticas bajo un modelo generativo. |
| 27 | TI-0102 | Graham Wallas | 1926 | The Art of Thought | Creativity studies | book | USABLE_OCR | Creatividad como proceso multietapa: preparación, incubación, iluminación y verificación; OCR verificado visualmente. |
| 28 | TI-0115 | Francis Heylighen | 1999 | Collective Intelligence and its Implementation on the Web | Complex systems | paper | USABLE | Inteligencia colectiva como ventaja de resolución mediante memoria compartida, coordinación y autoorganización. |
| 29 | TI-0119 | Stevan Harnad | 1990 | The Symbol Grounding Problem | Cognitive science | paper | USABLE | Semántica cognitiva: límites del símbolo no fundamentado y arquitectura híbrida sensorio-simbólica. |
| 30 | TI-0148 | Jürgen Schmidhuber | 2006 | Gödel Machines: Fully Self-Referential Optimal Universal Self-Improvers | Artificial general intelligence | paper | USABLE | Auto-modificación formal condicionada por prueba, utilidad, axiomas y límites de demostrabilidad. |

## Cobertura y límites

La muestra cubre filosofía, psicología/psicometría, inteligencia animal, cibernética, ciencia cognitiva, IA clásica, formalización, aprendizaje/metaaprendizaje, agencia, creatividad, semántica e inteligencia colectiva. **No logra cobertura primaria válida de desarrollo cognitivo ni neurociencia de la inteligencia**, porque los archivos faltan o están mal vinculados. Este límite debe corregirse antes de T2; no se rellena con memoria del analista ni con metadatos.
