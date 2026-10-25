# PRIOR-ART GATE · regeneración tras lesión (ítem 0.2)

**Fecha:** 2026-10-25 · **Veredicto:** `PARTIALLY_SOLVED` · **Buscado desde:** este host (Springer/ACM/ScienceDirect bloqueados; arXiv y Crossref funcionan)

## Qué dice la literatura ≠ qué tenemos comprobado

| Qué dice la literatura | Nivel | Qué tenemos comprobado |
|---|---|---|
| Un autómata ya aprendido puede **reutilizarse y actualizarse** cuando el sistema cambia, en vez de reaprenderse de cero. Ferreira, van Heerdt & Silva, *Tree-Based Adaptive Model Learning* (arXiv 2209.00122, 2022-08-31, rev. 2022-11-17): extienden Kearns–Vazirani, implementan en LearnLib (`github.com/UCL-PPLV/learnlib`) y baten al KV clásico y al adaptativo del estado del arte sobre ejemplos grandes con ajustes pequeños entre dos corridas. | SOURCE-VERIFIED (resumen leído por la API de arXiv) | Nada: no hemos corrido LearnLib ni su algoritmo. |
| Misma línea, con reutilización como objetivo declarado: Damasceno, Mousavi & da Silva Simão, *Learning to Reuse: Adaptive Model Learning for Evolving Systems*, LNCS, `10.1007/978-3-030-34968-4_8` (2019). Tesis del mismo autor, *Learning finite state machine models of evolving systems*, USP 2020, `10.11606/t.55.2020.tde-02092020-091958`. | SOURCE-VERIFIED sólo a nivel de metadatos (Crossref; el texto está en Springer, bloqueado) | Nada. La cita del plano era de memoria y **es correcta**: autores, título y año coinciden. |
| Reparación por redundancia de estructura: decodificación por síndrome sobre un código de repetición, mayoría de tres. | PROJECT-VERIFIED en PRIMITIVO (320/320 intervenciones, 84/84 shams) | Es nuestro, medido, y **no es de este ítem**: va a la Fase 3. |

## Lo que no hemos encontrado

Búsquedas corridas hoy en arXiv (`all:"automata learning"` cruzado con `relearning`, `"model repair"`, `"model damage"`; y `"automata learning" AND "evolving systems"`): **cero resultados**.

El hueco no es casual, y es la razón del ítem. La literatura adaptativa resuelve la dirección **contraria** a la nuestra:

- *ellos*: el **sistema** cambia, el modelo aprendido sobrevive y se actualiza;
- *nosotros*: el **sistema no cambia**, y lo que se destruye es el **modelo**, mientras la experiencia vivida puede seguir ahí o no.

No decimos que nadie lo haya hecho; decimos que no lo hemos encontrado. Lo que sí trae la literatura, y se incorpora como marco y no como código, es que la reutilización de un modelo aprendido es más barata que reaprender, lo cual es la hipótesis de nuestro brazo «con traza».

## Qué se integra y qué se escribe

- **Se integra**: nada de código. LearnLib es Java y su algoritmo supone maestro y reset; la unidad no tiene ninguno de los dos. Se cita como antecedente de «conservar abarata».
- **Se escribe**: sólo la lesión y la contabilidad. La reparación **no se escribe**: la unidad ya tiene su vía de reparación (refutación → retroceso → repaso), y el experimento consiste precisamente en hacerla pasar por ahí. Escribir un «cargar desde respaldo» sería construir el resultado.
