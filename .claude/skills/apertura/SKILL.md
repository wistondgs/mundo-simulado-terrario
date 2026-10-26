---
name: apertura
description: Abrir la ficha de apertura de un experimento del programa UNIDAD MÍNIMA sin repetir errores ya cometidos — lee el registro de errores y guardas, rellena la plantilla de 13 puntos, corre los mutantes antes de dar la ficha por final, y recuerda qué no se hace. Úsala antes de escribir código de cualquier experimento, ítem o fase de la unidad. Palabras clave, apertura, ficha, experimento, gate, mutantes, guardas, errores, preregistro, puerta.
---

# Apertura · cómo se abre un experimento sin repetir errores

La fuente de verdad son dos ficheros del árbol, no este skill:

- `experiments/unidad_minima_01/ERRORES_Y_GUARDAS.md` — lo que ya nos mordió y su guarda.
- `experiments/unidad_minima_01/PLANTILLA_FICHA_APERTURA.md` — la ficha de 13 puntos (0 + 12).

## Pasos, en este orden

1. **Leer el registro entero** (`ERRORES_Y_GUARDAS.md`). No es largo. Anotar qué entradas aplican a lo que se va a abrir: van en el **punto 0** de la ficha con cómo se cumple cada una (campo del JSON, mutante o pregunta contestada). «Ninguna aplica» se justifica.
2. **Confirmar que el gate de antecedentes existe** (`PRIOR_ART_<nombre>.md`) con veredicto y las dos columnas. Sin gate no hay ficha: la norma cero es *no inventar lo inventado*.
3. **Copiar la plantilla** a `APERTURA_<nombre_descriptivo>.md` y rellenar los 13 puntos. Nombres descriptivos, no índices. Cada número de la puerta con su unidad y el campo del JSON que lo mide.
4. **Correr los mutantes del punto 10 antes de la corrida real.** Si un mutante refuta un criterio, enmienda prospectiva con fecha, debajo de la ficha. La ficha no es final hasta aquí.
5. **Corrida real**, dos veces, hash idéntico, sin `random`. El veredicto lo calcula el programa.
6. **Si FAIL:** se deja como FAIL; una sola reparación, declarada antes de correrla, con su propio falsador. Dos FAIL cierran la fase y se informa.
7. **Al cerrar la fase:** el `CIERRE_FASE_n.md` dice qué guardas saltaron, qué entradas nuevas añade al registro (con su guarda; sin guarda quedan ABIERTAS), qué parte de la sesión fue experimento y qué parte custodia, y termina con **una sola pregunta para Wis**.

## Lo que este skill prohíbe

- Escribir código antes del punto 4.
- Corregir la puerta después de ver un resultado.
- Afirmar entorno, cifra o negación sin el comando que lo probó y el árbol donde corrió.
- Un presupuesto único donde la curva ya saturó.
- Construir lo que la pregunta no pide: se lista aparte como propuesta.
- Commitear a mitad de fase. El trabajo es el experimento.
