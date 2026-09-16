# CORPUS-ACQUISITION-LIST-02 · el objetivo real

**Objetivo declarado el 2026-09-16:** no replicar la inteligencia humana, sino **aplicar
inteligencia en un ser cibernético autopoiético, metacognitivo y autoevolutivo**, cuyo
desarrollo pertenece al artefacto y no al investigador.

Eso es **robótica del desarrollo y cibernética**, no psicología cognitiva. La lista 01 servía a
la pregunta anterior («qué considera la gente que es inteligente»). Ésta sirve a ésta.

**Método:** se auditó `CORPUS_MASTER.csv` (152 fichas) contra los tres pilares. Lo marcado
`[PROPUESTA]` **no está en tu catálogo** — lo aporto yo y hay que verificar DOI al catalogarlo.

> **CORRECCIÓN 2026-09-16 (tarde) · `CORPUS_GAPS_v0.4`.** La recomendación de compra n.º 1 de
> este documento quedó obsoleta el mismo día. **Ashby *Design for a Brain* ya está en el corpus**
> —2.ª ed. 1960, `ARC-001` = `ADOA-001`, 304 pp., verificada— y lo que estaba mal era el
> registro: `MISSING_AND_RESTRICTED.md` marca TI-0048 como `RESTRICTED` por un 404. No había que
> comprarlo: había que corregir la ficha. Las correcciones puntuales van marcadas abajo; el texto
> original se conserva. Análisis completo en
> [CORPUS_V04_ANALISIS_01.md](CORPUS_V04_ANALISIS_01.md).

---

## 0. Primero: lo que YA tienes y sirve al objetivo real

Esto me sorprendió. Tu corpus cubre el objetivo **nuevo** mejor que el anterior.

| id | Obra | Por qué es central aquí |
|---|---|---|
| **TI-0148** | Schmidhuber, *Gödel Machines: Fully Self-Referential Self-Improvement* | **metacognitivo + autoevolutivo en un solo paper**: un sistema que reescribe su propio código cuando puede *probar* la mejora |
| **TI-0099** | Parr & Friston, *Active Inference: A Process Theory* | el puente formal moderno hacia la autopoiesis: mantas de Markov, autoorganización, un sistema que minimiza sorpresa para conservar su forma |
| **TI-0049** | Ashby, *An Introduction to Cybernetics* | variedad requisita — cuánta variedad interna exige un ambiente dado |
| **X06** | Oudeyer, Kaplan & Hafner, *Intrinsic Motivation Systems for Autonomous Mental Development* | tu tradición, literalmente: desarrollo mental autónomo |
| **TI-0092** | POET | generación abierta de entornos **y** soluciones |
| TI-0090 · TI-0091 | Pathak curiosidad · Burda RND | motivación intrínseca implementable |
| TI-0087 · TI-0088 | World Models · Dreamer | el sustrato de A3/A4 |

**Gödel Machine y Active Inference están en tu disco y son las dos piezas más pertinentes de
todo el corpus para lo que quieres hacer.** Si esta semana solo lees dos cosas, léelas.

---

## Pilar 1 · AUTOPOIÉTICO — el hueco más grave

`06_Cibernetica_Sistemas`: **8 catalogadas, 1 obtenida.** Siete de ocho faltan, todas
`RESTRICTED`.

| Prio | id | Obra | Qué aporta a Terrario |
|:--:|---|---|---|
| **1** | TI-0052 | Maturana & Varela (1980) *Autopoiesis and Cognition* | el texto fundacional de la palabra que usaste; define clausura operacional y qué cuenta como sistema que se produce a sí mismo |
| ~~**2**~~ **OBTENIDA** | TI-0048 | Ashby *Design for a Brain* | **ultraestabilidad**: un sistema que cambia sus propios parámetros cuando sus variables esenciales salen del rango viable. Es **exactamente `d4_change`** — las reglas se invierten y el agente debe re-estabilizarse. **v0.4: presente como 2.ª ed. 1960 (`ARC-001`/`ADOA-001`), no la 1.ª de 1952. La ficha TI-0048 sigue diciendo `RESTRICTED` y hay que corregirla.** |
| **3** | TI-0054 | Powers (1973) *Behavior: The Control of Perception* | controlar la percepción, no la conducta. Se mapea directo sobre el estado homeostático de A4 |
| 4 | TI-0122 | Varela, Thompson & Rosch (1991) *The Embodied Mind* | enacción: la cognición como acoplamiento, no como representación |
| 5 | TI-0047 | Wiener (1948) *Cybernetics* | la fuente; retroalimentación y propósito |
| 6 | TI-0050 | Rosenblueth, Wiener & Bigelow (1943) *Behavior, Purpose and Teleology* | 12 páginas; define conducta teleológica sin invocar mente |
| 7 | TI-0123 | Clark (1997) *Being There* | mente extendida y acoplamiento con el mundo |
| 8 | TI-0051 · TI-0053 | Bateson · Beer | contexto de sistemas; prescindibles al principio |

> **Ashby 1952 es mi recomendación no obvia.** La ultraestabilidad es el mecanismo formal de
> «autoevolutivo» y es anterior a todo el vocabulario moderno. Y tu D4 la implementa sin saberlo.
>
> **Corregido por v0.4:** el texto ya estaba en el disco. La recomendación acertó en el qué y
> falló en el cómo — no era una compra, era una desincronía de registro. Lo que sigue faltando
> del linaje cibernético es Wiener 1948 (TI-0047), Rosenblueth–Wiener–Bigelow 1943 (`ADOA-003`),
> Powers 1973 (`ADOA-007`) y Maturana–Varela 1980: ninguno con copia legal. Varela 1979 es OA
> con descarga manual.

---

## Pilar 2 · METACOGNITIVO — punto ciego total

Busqué «metacogn» en las 152 fichas: **0 resultados.** No es que esté restringido y documentado.
**No está catalogado.** Es el único hueco de los tres que no es culpa de los muros de pago.

Todo lo que sigue es `[PROPUESTA]` — verificar DOI al catalogar.

| Prio | Obra | Por qué |
|:--:|---|---|
| **1** | Nelson & Narens (1990) *Metamemory: A theoretical framework and new findings*, Psychology of Learning and Motivation 26:125–173 | **Es una especificación de arquitectura, no una teoría psicológica.** Define el nivel-meta como un modelo del nivel-objeto, con flujo de *monitorización* hacia arriba y de *control* hacia abajo. Se puede implementar tal cual sobre A4 |
| **2** | Cox (2005) *Metacognition in computation: A selected research review*, Artificial Intelligence 169(2):104–141 | la revisión desde el lado de la IA: qué se ha intentado y qué falló. Te ahorra reinventar |
| **3** | Smith, Shields & Washburn (2003) *The comparative psychology of uncertainty monitoring and metacognition*, BBS 26(3):317–339 | **metacognición no verbal**, medida en animales. Es la única literatura sobre metacognición sin lenguaje — que es tu caso exacto. Y viene en formato BBS: précis + comentarios + respuesta |
| 4 | Flavell (1979) *Metacognition and cognitive monitoring*, American Psychologist 34(10):906–911 | el paper fundacional, 6 páginas, a menudo en abierto |
| 5 | Shea et al. (2014) *Supra-personal cognitive control and metacognition*, Trends in Cognitive Sciences | metacognición explícita vs implícita; relevante para decidir cuál construyes |

**Nota de diseño:** A4 ya tiene un `UncertaintyEstimator`. Eso es **monitorización** sin
**control** — media metacognición. Nelson & Narens te dan el otro lazo: qué hace el sistema con
su propia estimación de incertidumbre. Es probablemente la extensión más barata y de mayor
rendimiento que le puedes hacer a A4.

---

## Pilar 3 · AUTOEVOLUTIVO — casi cubierto

Ya tienes POET, Gödel Machines, curiosidad y RND. Faltan dos piezas:

| Prio | Obra | Por qué |
|:--:|---|---|
| **1** | `[PROPUESTA]` Lehman & Stanley (2011) *Abandoning objectives: Evolution through the search for novelty alone*, Evolutionary Computation 19(2):189–223 | la búsqueda por novedad supera a la búsqueda por objetivo en dominios engañosos. Directamente aplicable a cómo puntúas tus corridas |
| **2** | `[PROPUESTA]` Clune (2019) *AI-GAs: AI-generating algorithms*, arXiv | el manifiesto del paradigma que estás construyendo sin llamarlo así: aprender el algoritmo de aprendizaje, el entorno y la arquitectura |
| 3 | TI-0111 | Bonabeau, Dorigo & Theraulaz (1999) *Swarm Intelligence* | catalogado, no obtenido; solo si el futuro es multi-agente |

---

## Orden de compra, si hay que elegir

1. ~~**Ashby 1952, *Design for a Brain***~~ — **YA LO TIENES.** v0.4 lo verifica como 2.ª ed.
   1960 (`ARC-001`/`ADOA-001`). Acción: corregir la ficha TI-0048, no comprar.
2. **Maturana & Varela 1980** — el fundamento del primer pilar. Sin copia legal; sigue vigente.
3. **Nelson & Narens 1990** — el capítulo que te dice cómo construir el segundo pilar. **Sigue
   vigente y es ahora la primera de la lista**: v0.4 no tocó metacognición, así que el pilar 2
   continúa en cero.
4. **Powers 1973** — el lazo de control para A4. Sin copia legal; sigue vigente.

Con esos tres, los tres pilares tienen fundamento citable. Los demás son profundidad.

## Lo que NO hace falta comprar

Toda la rama de aprendizaje (14/14), los benchmarks (12/14), la filosofía clásica (8/8), los 29
documentos de diseño de mundos, y —lo más importante— **Gödel Machines y Active Inference**,
que ya tienes y son las dos más pertinentes.

---

## Advertencia de alcance

Autopoiesis, metacognición y autoevolución son **tres literaturas con criterios de éxito
distintos y en disputa**, igual que «inteligencia». Antes de preregistrar cualquier hipótesis
sobre un agente «autopoiético», hay que operacionalizar qué medición decidiría que lo es —o la
afirmación tendrá el mismo problema que los quince benchmarks de tu categoría 15.

La ruta corta: **empezar por la ultraestabilidad de Ashby**, que sí tiene criterio operacional
—variables esenciales dentro de rango viable tras una perturbación— y que D4 ya puede medir.
