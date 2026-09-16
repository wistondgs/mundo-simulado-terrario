# CORPUS-ACQUISITION-LIST-01

**Para qué:** qué hace falta leer y tener para poder preregistrar una hipótesis de ontogenia
defendible, y **a qué escalón de la escalera A×D sirve cada pieza**.

**Cómo usarla:** el Nivel 1 se resuelve esta semana y es gratis. El Nivel 2 es el que de verdad
desbloquea la pregunta del proyecto. El Nivel 3 espera.

**Regla:** solo rutas legales. Repositorio de autor, PMC, repositorio universitario, préstamo
interbibliotecario o compra. Cada entrada lleva su DOI para que la procedencia quede anclada.

---

## Nivel 1 — ~~Recuperables~~ **RECUPERADAS el 2026-09-16** (10 obras)

> **Hecho.** Las diez se descargaron de sus URL legales registradas y están en
> `Documentos/teoria de la inteligencia/documents_v0.3/`. Siete con sha256 idéntico al original;
> tres (X03, X07, X08) son HTML de PMC con el texto completo del artículo pero hash nuevo por la
> fecha embebida. X09 sigue siendo solo resumen. Nada que descargar aquí.

Estaban en la expansión v0.3, se verificaron una vez y sus bytes se perdieron al desaparecer la
máquina donde se descargaron. **Las URL legales quedaron registradas.** Es la mejor relación
esfuerzo/resultado del proyecto entero.

| id | Obra | Sirve a | DOI |
|---|---|---|---|
| **X16** | Smith & Thelen (2003) *Development as a dynamic system* | **marco general de ontogenia** · D4 | `10.1016/S1364-6613(03)00156-6` |
| **X03** | Adolph & Hoch (2019) *Motor Development: Embodied, Embedded, Enculturated, Enabling* | **desarrollo como habilitación** · D1→D2 | `10.1146/annurev-psych-010418-102836` |
| **X06** | Oudeyer, Kaplan & Hafner (2007) *Intrinsic Motivation Systems for Autonomous Mental Development* | **A4 homeostasis/exploración** · motivación intrínseca | `10.1109/TEVC.2006.890271` |
| **X07** | Piloto et al. (2022) *Intuitive physics learning in a deep-learning model inspired by developmental psychology* | **A3 modelo del mundo** · D2 | `10.1038/s41562-022-01394-8` |
| **X08** | Squire et al. (2015) *Memory Consolidation* | **A2→A4 memoria** | `10.1101/cshperspect.a021766` |
| **X02** | O'Regan & Noë (2001) *A sensorimotor account of vision and visual consciousness* | percepción acoplada a la acción · D0→D1 | `10.1017/S0140525X01000115` |
| **X11** | Mesoudi & Thornton (2018) *What is cumulative cultural evolution?* | criterios de acumulación (futuro multi-agente) | `10.1098/rspb.2018.0712` |
| **X12** | Derex et al. (2019) *Causal understanding is not necessary for the improvement of culturally evolving technology* | **D3: mejora sin comprensión causal** — control conceptual clave | `10.1038/s41562-019-0567-9` |
| **X13** | Derex et al. (2025) *Social learning preserves both useful and useless theories* | canalización de la exploración | `10.1098/rspb.2024.2499` |
| **X14** | Galesic et al. (2023) *Beyond collective intelligence: Collective adaptation* | adaptación colectiva | `10.1098/rsif.2022.0736` |

> **X12 merece atención especial.** Demuestra que una tecnología puede mejorar **sin** comprensión
> causal. Es el contraargumento directo a cualquier lectura ingenua de D3: si un agente mejora en
> `d3_causality`, X12 obliga a descartar antes que haya mejorado por acumulación ciega. Es una
> hipótesis rival obligatoria, no lectura de fondo.

*(X09 Laland 2010 `10.1038/nrg2734` quedó como `ABSTRACT_KEYPOINTS_PREVIEW_ONLY`; solo hay
resumen. Requiere acceso institucional.)*

**Al recuperarlos:** ponerlos bajo la ruta estable del corpus y re-anclar
`SOURCE_PROVENANCE_v0.3.csv`, sustituyendo las rutas `/workspace/scratch/...` por las locales.
El SHA-256 de cada uno ya está registrado: si el archivo descargado coincide, la verificación
queda cerrada sola.

---

## Nivel 2 — Las ocho de desarrollo cognitivo (restringidas)

`04_Desarrollo_Cognitivo` está catalogada con 8 obras y **ninguna se pudo obtener legalmente**.
Es la única categoría con 0 de cobertura, y es la categoría de la pregunta del proyecto.

| id | Obra | Sirve a | Prioridad |
|---|---|---|---|
| **TI-0035** | Karmiloff-Smith (1992) *Beyond Modularity* | **la escalera A0→A4 misma**: redescripción representacional es la tesis de que el desarrollo añade niveles sobre lo ya funcional | **1ª** |
| **TI-0037** | Carey (2009) *The Origin of Concepts* | **D2→D3**: cómo se adquieren conceptos nuevos, no solo asociaciones | **2ª** |
| **TI-0038** | Siegler (1991) *Children's Thinking* | **D4**: olas superpuestas — la adaptación no sustituye estrategias, las solapa | **3ª** |
| TI-0031 | Piaget (1936) *The Origins of Intelligence in Children* | D0→D1, estadios sensomotores | 4ª |
| TI-0033 | Vygotsky (1934) *Thought and Language* | andamiaje social (futuro multi-agente) | 5ª |
| TI-0036 | Gopnik, Meltzoff & Kuhl (1999) *The Scientist in the Crib* | **D3**: el niño como científico causal | 6ª |
| TI-0032 | Piaget (1947) *The Psychology of Intelligence* | complemento de TI-0031 | 7ª |
| TI-0034 | Bruner (1960) *The Process of Education* | currículo y secuencia de exigencia | 8ª |

**Con las tres primeras basta para preregistrar.** Karmiloff-Smith fundamenta por qué la escalera
de agentes es aditiva; Carey fundamenta el salto D2→D3; Siegler fundamenta qué esperar en D4.

Rutas legales, por coste creciente: préstamo interbibliotecario o biblioteca universitaria ·
capítulos de autor (Gopnik y Carey publican capítulos sueltos en sus páginas) · edición usada ·
compra digital. Karmiloff-Smith y Carey son los dos que yo compraría si hubiera que comprar.

---

## Nivel 3 — Huecos de prioridad alta que el propio sistema ya declaró

De `CORPUS_GAPS_v0.3.md`, sin fuente suficiente todavía:

- **Número y cantidad** (`WEAK_COVERAGE`, sin fuente nueva): Dehaene *The Number Sense*;
  Feigenson, Dehaene & Spelke *Core systems of number*; Gallistel & Gelman. Relevante si alguna
  vez se añade un mundo de cantidad.
- **Cognición animal**: navegación, uso de herramientas, metacognición, numerosidad. Shettleworth
  *Cognition, Evolution and Behavior* (TI-0015, restringida) es la referencia canónica.
- **Evolución biológica de la cognición**: la única fuente (X09) es solo resumen.
- **Creatividad y generación**: insight y recombinación conceptual. Hoy solo Wallas (1926).

Ninguno bloquea la primera hipótesis. Anotarlos como límite declarado es suficiente por ahora.

---

## Lo que NO hace falta comprar

- **Percepción de objetos / D0–D1**: Spelke *Principles of Object Perception* (X01) ya está
  presente y verificado por hash.
- **Toda la rama de aprendizaje automático**: 14/14 obtenidas — MAML, World Models, Dreamer,
  curiosidad, RND, POET.
- **Medición y benchmarks**: 12/14, incluidos Chollet, ARC-AGI 2 y 3.
- **Filosofía clásica**: 8/8 en dominio público.
- **Diseño de mundos**: 29 documentos `WORLD-REF-*` completos con procedencia.

---

## Orden sugerido

1. Recuperar los **10 del Nivel 1** (una tarde, gratis) y re-anclar la procedencia.
2. Conseguir **Karmiloff-Smith, Carey y Siegler**.
3. Con eso: escribir el marco teórico de la hipótesis de ontogenia y preregistrarla.
4. El Nivel 3 queda como límite declarado del preregistro, no como bloqueo.
