# Control de recuperación documental

Este control responde preguntas representativas usando únicamente este
directorio y las refs/rutas que enumera. No sustituye la ejecución científica.

| Pregunta | Ruta de recuperación | Resultado recuperable |
|---|---|---|
| ¿Qué capacidades están demostradas y bajo qué condiciones? | `capability_matrix.md` → `experiment_registry.json` | La matriz separa scope, controles y limitaciones por capacidad. |
| ¿Qué fusiones funcionales ya se probaron? | Registro `RB-01` | Remembered-binding conserva B+Q+H+M+ψ en una instancia, con diez gates. |
| ¿Qué refutó o invalidó resultados? | Registros `L18-RC`, `UM-09`; `coverage_and_limits.md` | 1.8 fue insuficiente; C5 quedó nulo por techo de diseño; no se reinterpretan como falsaciones generales. |
| ¿Qué evidencia hay sobre memoria y acción? | Registro `N10` | Hay cierre confirmatorio, pero faltan filas primitivas y la lesión B no es independiente. |
| ¿Qué cambió entre 1.8 y L19? | Registros `L18-RC` y `L19-V1` | Son mecanismos y contratos distintos; L19 no rescata 1.8. |
| ¿Qué sigue sólo local? | `source_inventory.json`, `trace_evidence.md` | T2/T2c/13/14 de Unidad Mínima, `runs/`, `.terrario/`, objetos inalcanzables y trazas no revisadas. |
| ¿Qué ocurrió en una corrida H-ADAPT concreta? | `executions/h_adapt_001_pilot_execution_catalog.json` → `executions/h_adapt_001_behavioral_windows_all.json` | Se puede seleccionar cualquier `run_id`, comprobar clasificación, hash de fuente, ventana ordinal y eventos registrados; las incógnitas quedan explícitas. |

## Resultado

Las preguntas anteriores son contestables por ref, commit y ruta. Una pregunta
que exija las decisiones individuales N1.0, una traza íntegra no publicada o
el contenido de un objeto Git inalcanzable se marca **no recuperable
remotamente**; este expediente no fabrica una respuesta para aprobar el
control.
