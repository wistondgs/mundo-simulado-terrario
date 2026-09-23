# Control report — réplica ciega A2

| Control obligatorio | Estado | Evidencia |
|---|---|---|
| Finitud | PASS | 256/256 dinámicas con al menos un atractor |
| Puntos fijos y scheduler | PASS | 256/256; el conteo de diferencias es 0 |
| Simetría entre cortes | PASS | Conteos `(16,144,96)`, H e I idénticos para C12/C13/C23 |
| OEIS A001372, n=4 | PASS | Consulta directa de `https://oeis.org/A001372/b001372.txt`: `4 19`; A2 calcula 19 tipos S4 |
| Guardia de consecuencias intrínsecas | PASS | La robustez con máscaras {1,2,3} es constante en cada clase tipo_S4 |
| Máscaras derivadas | PASS | C12=(2,1), C13=(3,1), C23=(3,2) |
| Pruebas estructurales | PASS | Estado/bits, máscaras, ciclos, scheduler y cardinalidades de S4/C12 |
| Calibradores de la sección 9 | PASS | Ambos objetos canónicos coinciden exactamente |
| Validación independiente | PASS | Recomputó C3–C8 sobre los 256 registros sin importar la implementación principal |
| Reejecución determinista | PASS | RUN1/RUN2 byte-equivalentes para `por_sistema.jsonl` y `resumen.json` |

No se utilizó Monte Carlo. Los valores `E_I_permutacion_exacta_bits` de C11 se obtuvieron directamente de la suma hipergeométrica especificada, usando log-factoriales; se reportan en `resumen.json`.
