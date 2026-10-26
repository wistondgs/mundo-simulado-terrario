# PRIOR-ART GATE · fusión de estados polinómica sin maestro y sin reset (1-bis)

**Fecha:** 2026-10-25 · **Veredicto:** `SOLVED` para el mecanismo, `OPEN_UNDER_CURRENT_SEARCH` para el acoplamiento con una vida continua · **Fuentes que responden desde aquí:** arXiv, Crossref, PyPI. GitHub devolvió 403 por límite de tasa.

**Por qué existe este gate.** La Fase 1 midió que el mecanismo de 02 identifica bien y tiene una **cola de coste explosiva** (p99 del trabajo por paso de vida: 5,5 en n=3 → 25 en n=4 → 1 181 en n=6; máximo 132 573). 1-bis es la reparación única de la fase: cambiar el mecanismo por uno **polinómico**, con el mismo banco y la misma puerta.

## Fila nueva, obligatoria desde E-17 · la complejidad del problema

| Qué dice la literatura | Nivel | Qué tenemos comprobado |
|---|---|---|
| Hallar la **máquina mínima consistente con los datos** es NP-difícil. Gold, *Complexity of automaton identification from given data*, Information and Control **37**(3):302–320, 1978, `10.1016/s0019-9958(78)90562-4`. Angluin, *On the complexity of minimum inference of regular sets*, ibíd. **39**(3):337–350, 1978, `10.1016/s0019-9958(78)90683-6`. | SOURCE-VERIFIED a metadatos (Elsevier; el texto completo no se lee desde aquí) | Nuestra propia cola, medida: el trabajo por paso de vida tiene p99 de 1 181 y máximo de 132 573 en n=6, con mediana 1,70. COMPUTATIONALLY-REPRODUCED. |
| Y **no es aproximable dentro de ningún polinomio**: Pitt & Warmuth, *The minimum consistent DFA problem cannot be approximated within any polynomial*, JACM **40**(1):95–142, 1993, `10.1145/138027.138042` (precursores en STOC'89 `10.1145/73007.73048` y SCT'89 `10.1109/sct.1989.41829`). | SOURCE-VERIFIED a metadatos | Nada propio; no hace falta medirlo, es teoría. |

**Lo que esto obliga, y es la decisión de 1-bis.** La cola de la Fase 1 **no es un defecto de implementación**: es el precio de exigir el mínimo exacto sin maestro, y estaba en la literatura antes de que lo midiéramos (E-17). Por tanto ningún mecanismo polinómico puede conservar la garantía de exactitud. 1-bis no «arregla» 02: **cambia de pregunta**, cambiando garantía exacta por coste acotado. Eso se declara en la ficha con números antes de correr, o no vale.

## El mecanismo

| Qué dice la literatura | Nivel | Qué tenemos comprobado |
|---|---|---|
| **RPNI**: fusión de estados en tiempo polinómico, identifica en el límite dada una muestra característica. Oncina & García, *Inferring regular languages in polynomial updated time*, 1992, `10.1142/9789812797902_0004`; y *Identifying regular languages in polynomial time*, 1993, `10.1142/9789812797919_0007`. | SOURCE-VERIFIED a metadatos | Nada. Es el esqueleto de 1-bis. |
| **EDSM / Blue-Fringe**: la rama heurística práctica, polinómica, que ganó Abbadingo. Lang, Pearlmutter & Price, LNCS, 1998, pp. 1–12, `10.1007/bfb0054059`. | SOURCE-VERIFIED a metadatos | Nada. Referencia de orden de fusión. |
| **MooreMI**: PTAP + fusión de estados sobre máquinas **con salida**, aprendidas de trazas y sin oráculo, con identificación en el límite demostrada. Giantamidis & Tripakis, arXiv 1605.07805, 2016. | SOURCE-VERIFIED (resumen leído en el gate de la Fase 1) | Nada. Es el antecedente más cercano, y es el que 1-bis instancia. |
| **AALpy 2.0.0** (PyPI, 2026-10-25) trae una rama pasiva por **fusión de estados generalizada** sobre el marco rojo-azul (arXiv 2506.06333, CAV 2025), para DFA, Mealy y Moore. | SOURCE-VERIFIED (metadatos y descripción) | Nada instalado. |

## El residuo, y es estructural, no de adorno

Todo lo anterior parte de un **conjunto** de trazas, lo que presupone poder volver al principio. Nuestra unidad vive **una sola vez y sin reset**. Y eso cambia la forma del dato de entrada:

> con un conjunto de trazas, los prefijos forman un **árbol**; con una sola vida continua, forman un **camino** de longitud T.

La fusión de estados sobre un camino es el caso degenerado del marco rojo-azul y es de libro, pero no hemos encontrado publicado el acoplamiento concreto: fusión polinómica sobre un camino único, **prediciendo antes de actuar**, con la medida del paso del último error. No decimos que no exista; decimos que no lo hemos encontrado (búsquedas de la Fase 1: `all:"Mealy" AND all:"without reset"` sigue vacío; `passive Mealy learning single trace` sin resultados pertinentes).

## Qué se integra y qué se escribe

- **Se integra**: el esquema RPNI (orden canónico de fusión, prueba de compatibilidad, determinización por propagación) y el criterio de fusión por consistencia de salida. Citados, no redescubiertos.
- **No se instala AALpy**, por dos razones medidas y no por pereza: su rama pasiva espera un conjunto de secuencias, y nuestro dato es un camino —envolverla exigiría inventar los cortes, que es precisamente lo que la unidad no tiene—; y su orden interno de fusión no es nuestro orden canónico, lo que rompería el determinismo declarado. Queda como comparación futura, no como dependencia.
- **Se escribe**: la fusión sobre el camino, en orden canónico, determinista, con sus contadores. Es implementación de libro de un algoritmo publicado, y así se declara: el residuo propio es el acoplamiento con la vida continua y la medida, no el algoritmo.
- **`hW` de AALpy queda fuera de 1-bis.** Aprende sin reset, pero **actuando para preguntar**: elige sus propias entradas para resolver la ambigüedad. Eso no es un cambio de mecanismo de aprendizaje, es darle a la unidad la facultad de elegir qué vivir, que es otra fase.
