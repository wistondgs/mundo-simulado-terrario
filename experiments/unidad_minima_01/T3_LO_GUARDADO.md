# T3 · lo que ya estaba guardado dice · 29-oct-2026

Piezas 4 y 6 de `ORIENTACIONES_TRABAJO_DESDE_EL_CORPUS.md`, **con las correcciones de la revisión externa**. Análisis sobre artefactos existentes: ninguna corrida nueva.

## Pieza 4 · la medida de Wolf, condicionada al mundo

**Estimador declarado:** la familia es la variable de condicionamiento; con una observación por historia, I(H; C | W) = H(C | W), la entropía de la conducta entre las historias de esa familia. Techo **1 bit** porque los artefactos traen **dos** historias: ninguna (F1) y vida en W₁ con el itinerario fijo. Conducta = (identifica@64, identifica@256, repertorio).

### `08` · heredar la traza (prototipo exploratorio) · I(historia; conducta en W₂ | W₂), techo 1 bit

| clase | historias comparadas | familias | **bits de historia** | exactitud sin historia | exactitud con historia | lectura |
|---|---|---|---|---|---|---|
| componible | F1 → C1 | 766 | **0.2663** | 1.0000 | 1.0000 | se nota en la conducta y **no cambia la exactitud** |
| componible | F1 → C2 | 766 | **0.2663** | 1.0000 | 1.0000 | se nota en la conducta y **no cambia la exactitud** |
| no_componible | F1 → C1 | 1368 | **0.1879** | 1.0000 | 1.0000 | se nota en la conducta y **no cambia la exactitud** |
| no_componible | F1 → C2 | 1368 | **0.1879** | 1.0000 | 1.0000 | se nota en la conducta y **no cambia la exactitud** |

### `09` · heredar la máquina sin la traza (C5) · I(historia; conducta en W₂ | W₂), techo 1 bit

| clase | historias comparadas | familias | **bits de historia** | exactitud sin historia | exactitud con historia | lectura |
|---|---|---|---|---|---|---|
| componible | F1 → C5 | 766 | **0.0379** | 1.0000 | 1.0000 | se nota en la conducta y **no cambia la exactitud** |
| no_componible | F1 → C5 | 1368 | **0.0417** | 1.0000 | 1.0000 | se nota en la conducta y **no cambia la exactitud** |

## Pieza 6 · la descomposición de Hartmanis · **BLOQUEADA**

Necesita la **máquina aprendida** de cada celda para trasladar la congruencia generadora de W₁ por el isomorfismo canónico. Las filas de `08`, `09` y `10` **no la serializan**; las de `05` y `07` sí —es la lección **E-21**, aplicada en la Fase 1 y no en la Fase 2—. Sin la máquina no hay isomorfismo, y sin isomorfismo «aparece una congruencia» no dice nada, que es justo lo que la revisión externa precisó. **Arreglo, en una línea:** añadir `maquina=[[q, a, t[0], t[1]] for (q, a), t in sorted(u.trans.items())]` a la fila y volver a correr `09` (249 s). No se simula ni se estima: se declara bloqueada y se deja el arreglo escrito.
