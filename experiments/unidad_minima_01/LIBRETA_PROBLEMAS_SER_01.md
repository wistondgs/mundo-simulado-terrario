# Libreta de problemas · Ser Integrado 01

## P-01 · Cadena de cinco cambios no materializada

**Estado:** pendiente, no bloquea la matriz W1→W2 abierta como replicación.
`PROYECTO_SER_INTEGRADO_01.md` pide cascadas de hasta cinco mundos, pero sólo
existen constructores ejecutables de la transición `W1→W2` (`mundo_2`) y una
cadena histórica de cinco *generaciones* sobre W2. No son equivalentes.

**Decisión aplicada:** no inventar una cascada de 8→16→32→64 estados ni llamar
«cinco cambios» a cinco generaciones. La matriz que se ejecuta mide un cambio
componible/control por fila; no certifica continuidad de cinco cambios ni Harlow.

## P-02 · Actividad no implica beneficio

Los contadores de A6 y de la matriz prueban que un contrato se actualizó. No
prueban que L19 elija acciones ni que la energía de Terrario sea meta 04. Se
conserva la traza y se deja esa transferencia como no verificada.

## P-03 · Encabezado Git de árbol sucio

El observador de Terrario registra `d643be18…`, que no incluye los archivos
nuevos no comprometidos. Las corridas deben añadir SHA-256 por archivo ejecutado;
el informe nunca debe presentar el HEAD solo como procedencia completa.

## P-04 · Coste real del primer preflight

**Estado:** observado durante ejecución. El primer recorrido completo de un W1
del banco n=6 y su W2 de 12 estados activa la búsqueda/reparación histórica a
escala suficiente para ocupar un núcleo de CPU sostenidamente. No se reduce
silenciosamente `L_de`, presupuesto, ventana ni núcleo para «hacer caber» la
matriz. La corrida conserva el mismo proceso y se medirá el tiempo antes de
abrir concurrencia sobre las 3 315 filas.
