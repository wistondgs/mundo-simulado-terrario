# Recuperación del ZIP de control

Fecha de registro: 2026-09-22.

El objeto de control actualmente custodiado es
`control/PRIMITIVO_N2_EXPERIMENT_CONTROL.zip`. Su SHA-256 fue verificado
directamente como:

```text
79dc8eeadc9190220d66f21eeb002b1f72c8d274d6f74ed07398a667722d05a7
```

Coincide con el hash histórico declarado y el archivo contiene 11 entradas.
Por tanto su clasificación actual es `RECOVERED_BYTE_EXACT` / `VERIFIED`.
La extracción de lectura no sustituye el ZIP congelado.

La ausencia inicial del objeto en el staging local fue reportada en la
conversación de trabajo anterior a su recuperación. Ese texto no se preservó
como artefacto inmutable dentro de este árbol, por lo que la afirmación de
ausencia pertenece a la categoría `ATESTADO`, no a `VERIFIED`. No se recreó
ni se hizo pasar por evidencia histórica. La presencia y el hash actuales sí
son verificables reproduciblemente.

La recuperación no altera `FREEZE_MANIFEST.json`, ni inserta retrospectivamente
los hashes de los ZIPs A1/A2 en dicho manifest. Esos hashes pertenecen al
registro contemporáneo externo del armado.
