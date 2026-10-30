# Cobertura, restricciones y contradicciones conservadas

## Cobertura conseguida

Se indexaron las fuentes de arquitectura existentes, refs locales/remotas, los
dos worktrees existentes, y expedientes de capacidades, fusiones, niveles,
Unidad Mínima y PRIMITIVO. La cobertura no afirma haber leído cada byte de los
directorios locales de 954 MB (`runs/`) y 2.5 GB (`.terrario/`): quedan
preservados e indexados como conjuntos locales pendientes de clasificación por
procedencia.

## Evidencia remota y local

| Estado | Qué significa |
|---|---|
| `PUBLISHED_GIT` | Un revisor remoto puede abrir la ref y ruta citadas. |
| `LOCAL_ONLY` | Se conserva localmente y se identifica por clase, hash o configuración disponible; no permite auditoría remota plena. |
| `RECOVERY_CANDIDATE` | Objeto Git inalcanzable; no se atribuye ni publica hasta revisar su procedencia. |

## Contradicciones que deben permanecer visibles

1. **1.8 no es L19.** El cierre insuficiente de `LEARNER-18-v1` permanece; L19
   es una línea nueva con criterio retenido y resultado positivo.
2. **Cierre científico N1.0 no implica paquete completo.** El análisis se
   reconstruye, pero faltan filas primitivas, la lesión B no es independiente y
   el gate de paridad es incapaz de fallar.
3. **Dos contabilidades de capacidad.** Los pasaportes A4/A5 y las campañas de
   niveles no se conectan automáticamente.
4. **C5 no mostró beneficio en su banco original.** El resultado fue techo de
   diseño, no ausencia de reparación ni éxito de herencia.
5. **Los artefactos locales de Unidad Mínima no son código confirmado.** T2,
   T2c, 13 y 14 deben citar su hash de archivo y su procedencia local, no
   reasignarse a `d643be1`.

## Suficiencia de recuperación

El expediente contesta con refs y rutas qué capacidades tienen veredicto, qué
fusiones se ejecutaron y qué defectos invalidaron inferencias. No puede
contestar remotamente el detalle de una traza local no publicada ni reconstruir
las 32.768 decisiones N1.0 que no se preservaron. Esos límites son parte del
resultado del inventario, no huecos que deban ocultarse.
