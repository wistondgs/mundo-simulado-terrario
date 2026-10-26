# PRIOR-ART GATE · escalar sin azar, de 3 a 8 estados (Fase 1)

**Fecha:** 2026-10-25 · **Veredicto:** `MULTIPLE_NEAR_SOLUTIONS` · **Fuentes que responden desde aquí:** arXiv API, Crossref API, PyPI. **GitHub API devolvió 403 por límite de tasa**, así que la vitalidad de los repos se toma de las fechas de subida a PyPI y se declara así.

## Qué dice la literatura ≠ qué tenemos comprobado

| Qué dice la literatura | Nivel | Qué tenemos comprobado |
|---|---|---|
| **Aprender máquinas con entrada y salida desde trazas de ejemplo, sin consultas de pertenencia ni de equivalencia, está resuelto.** Giantamidis & Tripakis, *Learning Moore Machines from Input-Output Traces*, arXiv 1605.07805 (2016, rev. sep-2016): tres algoritmos —PTAP, PRPNI y MooreMI—, y **MooreMI identifica en el límite**. | SOURCE-VERIFIED (resumen leído) | Nada: no hemos corrido ninguno de los tres. |
| Identificación exacta de DFA con SAT: Heule & Verwer, *Exact DFA Identification Using SAT Solvers*, LNCS, `10.1007/978-3-642-15488-1_7` (ICGI 2010). La cita del plano era de memoria y **es correcta**. Implementación viva en Python: **`dfa-identify` 3.13.0**, sobre `python-sat 1.*`, última subida a PyPI 2024-03-18. | SOURCE-VERIFIED a metadatos (LNCS es Springer, bloqueado) + paquete verificado en PyPI | Nada. Es el candidato a **referencia exacta** si el retroceso de 01 no alcanza. |
| Inferencia regular incremental: Dupont, *Incremental regular inference*, LNCS, `10.1007/bfb0033357` (1996). La cita del plano era de memoria y **es correcta**. | SOURCE-VERIFIED a metadatos | Nada. No hemos encontrado una versión **Mealy incremental** publicada ni implementada. |
| **AALpy 2.0.0, subida a PyPI hoy mismo (2026-10-25)** — el plano decía 1.6.2 de agosto, así que acaba de haber cambio de versión mayor. Cubre Mealy con algoritmos activos L*, KV, **L#** y **hW**, y pasivos por fusión de estados generalizada (marco Red-Blue). | SOURCE-VERIFIED (metadatos y descripción del paquete) | Nada instalado ni corrido. |
| Minimización por refinamiento de particiones: Hopcroft, *An n log n algorithm for minimizing states in a finite automaton*, `10.1016/b978-0-12-417750-5.50022-1` (1971). Es de libro y se implementa de libro. | SOURCE-VERIFIED a metadatos | Nada aún; se implementa en esta fase como **verdad de referencia**, no como hallazgo. |
| Aprendizaje pasivo con identificación en el límite, extendido a autómatas simbólicos: Loulergue & Habermehl, arXiv 2606.06050 (jun-2026), algoritmo SAI sobre el marco RPNI. | SOURCE-VERIFIED (resumen) | Nada. Referencia de marco, alfabeto equivocado para nosotros. |
| Aprender sin reset, con maestro y garantías: Rivest & Schapire 1993 (secuencias de *homing*), y **`hW` ya implementado en AALpy**. | LITERATURE-CLAIM para el artículo (no re-verificado hoy); SOURCE-VERIFIED para que AALpy lo lista | Nada. |

## Lo que no hemos encontrado

- `all:"Mealy" AND all:"without reset"` en arXiv: **cero resultados**, igual que ayer. Repetida la búsqueda como pedía la orientación.
- `passive Mealy machine learning` desde **una sola traza continua**: nada pertinente. Lo que existe (PRPNI, MooreMI, RPNI, GSM) parte de un **conjunto** de trazas, lo que presupone un reset entre ellas, y trabaja fuera de línea sobre el conjunto entero.
- Una cota publicada que fije la **longitud de vida** necesaria para identificar desde una sola traza sin reset: no la hemos encontrado. Consecuencia directa para la ficha: la longitud L se declara **a ojo con un suelo estructural**, y se dice que es a ojo (§3.3 de las orientaciones).

No decimos que nada de esto exista o no exista; decimos que no lo hemos encontrado.

## Dónde queda nuestro residuo, dicho con precisión

Lo más cercano que existe es MooreMI: aprende una máquina con salida, desde trazas, sin oráculo, e identifica en el límite. Las diferencias con lo nuestro no son de adorno y son tres:

1. **Moore, no Mealy.** La salida va en el estado, no en la transición. Nuestra salida es el bit de cambio `[x′ ≠ x]`, que es de la transición.
2. **Conjunto de trazas, no una vida.** Un conjunto presupone poder volver al principio. Nuestra unidad no tiene reset: vive una sola vez, y el estado en que empieza cada palabra es el que dejó la anterior.
3. **Fuera de línea, no paso a paso.** Nadie mide ahí lo que a nosotros nos interesa: **predecir antes de actuar** y el paso del último error. Eso no es un algoritmo distinto, es una medida distinta.

## Qué se integra y qué se escribe

- **Se integra como verdad de referencia, de libro y citada:** la minimización por refinamiento de particiones (Hopcroft 1971) para calcular la máquina mínima verdadera de cada sistema del banco. No se redescubre nada.
- **No se integra código de aprendizaje.** Ni AALpy ni `dfa-identify` se instalan por ahora, por una razón que no es pereza: lo que esta fase pregunta es si **el mecanismo que ya existe** (02) escala. Envolver una biblioteca contestaría otra pregunta. Si 02 no escala, la §3.7 de las orientaciones se activa y entonces AALpy entra con su propia ficha.
- **`dfa-identify` queda en reserva** como referencia exacta para |S| ≥ 4 si el retroceso de 01 se queda corto, con semilla y versión fijas, instalado en `.deps-unidad/` con `pip install --target`, declarado como disposición suministrada.
- **Se escribe:** el banco enumerado, la minimización de referencia, la comparación por forma canónica, la medida de identificabilidad, y los contadores. Nada de aprendizaje nuevo mientras 02 no haya fallado.
