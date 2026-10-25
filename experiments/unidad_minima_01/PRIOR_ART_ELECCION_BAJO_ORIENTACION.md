# PRIOR-ART GATE · elección por conveniencia bajo orientación externa (ítem 0.3)

**Fecha:** 2026-10-25 · **Veredicto:** `SOLVED` para el objeto matemático, `OPEN_UNDER_CURRENT_SEARCH` para el uso que le damos

## Qué dice la literatura ≠ qué tenemos comprobado

| Qué dice la literatura | Nivel | Qué tenemos comprobado |
|---|---|---|
| Una palabra que lleva el autómata a un estado fijo **desde cualquier estado** es una *palabra sincronizante* o *de reset*. Volkov, *Synchronizing Automata and the Černý Conjecture*, LNCS 5196 (LATA 2008), `10.1007/978-3-540-88282-4_4`, es el survey canónico; la conjetura de Černý (1964) acota la más corta por (n−1)² en un autómata sincronizante de n estados. | SOURCE-VERIFIED a nivel de metadatos (Crossref; LNCS es Springer, bloqueado). La cita del plano era de memoria y **es correcta**. | Que la palabra `BA` de nuestra máquina aprendida es un mapa constante, y `B` también: COMPUTATIONALLY-REPRODUCED en 01 y 02. |
| Hallar la palabra de reset **más corta** es NP-difícil y coNP-difícil, completa para DP, y es NP-difícil aproximar su longitud dentro de un factor n^(1−ε) para todo ε>0. Gawrychowski & Straszak, *Strong inapproximability of the shortest reset word*, arXiv 1408.5248 (2014), citando a Gerbush & Heeringa CIAA'10 y Berlinkov DLT'13 para el O(log n). | SOURCE-VERIFIED (resumen leído) | Nada propio. **Esto cambia el plan**: ver abajo. |
| El lenguaje de las palabras de reset mínimas y su estructura: Rodaro, arXiv 1708.04864 (2017). | SOURCE-VERIFIED (resumen) | Nada. Referencia, no herramienta. |

## Lo que no hemos encontrado

`all:"synchronizing word" AND all:learning` y `all:"learned automaton" AND (planning OR goal)` en arXiv: **sin resultados pertinentes**. Planificar sobre un autómata aprendido es práctica estándar y no es noticia; lo que no hemos encontrado es el caso concreto de una unidad que, sin maestro y sin reset, use su **propia** máquina adquirida para satisfacer una meta impuesta desde fuera, y de los controles que lo discriminan. No decimos que nadie lo haya hecho.

## Lo que el gate cambia en el diseño

1. **La meta no es una palabra de reset cualquiera, es una con imagen prescrita.** `B` es palabra de reset (lleva al estado 0) y es más corta que `BA`; pero la meta «que la próxima reacción a B sea 1» exige aterrizar en el estado donde B reacciona 1, y a ese llega `BA`, no `B`. La cota de Černý para n=2 es (2−1)²=1 y se cumple con `B`: no hay contradicción, porque nuestro problema es reset **al estado objetivo**, no a cualquiera. Esto hay que decirlo con precisión o la cita queda mal usada.
2. **El BFS shortlex es legítimo aquí y no escala.** Con 2 estados y palabras de longitud ≤ 4 la búsqueda exhaustiva es exacta y determinista. Por Gawrychowski & Straszak, pedir «la más corta» en general es inaproximable, así que la puerta del ítem puede exigir minimalidad **a esta escala y sólo a esta escala**; en la Fase 1, con |S| hasta 8, la minimalidad exacta deja de ser gratis y habrá que declarar un algoritmo voraz (y que no da el mínimo) o acotar la longitud. Queda anotado para la ficha de apertura de la Fase 1.

## Qué se integra y qué se escribe

- **Se integra**: el concepto y las citas. Ninguna biblioteca: AALpy y LearnLib traen aprendizaje con maestro y reset, que es lo que la unidad no tiene, y sus desempates internos no son nuestro orden canónico.
- **Se escribe**: el recorrido shortlex sobre las palabras de la máquina propia, la comprobación de la meta por predicción, y los dos controles. Son pocas líneas, y el residuo es la medida, no el algoritmo.
