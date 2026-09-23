# Esquema semántico de resumen — Gate A

Derivado de SPEC A v0.1, §11 y §14; no de la referencia.

| FIELD_ID | Significado y fuente | Tipo | Regla |
|---|---|---|---|
| `deterministico.n_dinamicas` | Número de registros JSONL | entero / PER_SYSTEM | EXACT_INTEGER |
| `tipos_S4`, `tipos_C12` | Cardinalidad de tipos observados | entero / PER_SYSTEM | EXACT_INTEGER |
| Conteos de cruzada, scheduler, lesión y perfiles | Filtros y conteos de los 256 registros | entero/categoría / PER_SYSTEM | EXACT_INTEGER |
| `H_K_bits`, `H_V_bits` | Entropías de particiones uniformes | real / PER_SYSTEM | REAL_VALUE, tolerancia §14 (1e-6) |
| `I_bits`, `E_I_permutacion_exacta_bits`, `AMI_max` | Fórmulas C11 con marginales fijos | real / PER_SYSTEM | REAL_VALUE, tolerancia §14 (1e-6) |
| Clases, colisiones y garantía por conteo | Particiones V y consecuencias T | entero/booleano / PER_SYSTEM | EXACT_INTEGER / STRUCTURAL |
| Máscaras, finitud, scheduler y simetrías | Controles §12 recalculables | booleano/estructura / DERIVED_CONTROL | STRUCTURAL |
| Monte Carlo opcional | Semilla, R y estimador §11.3 | real / MONTE_CARLO | MONTE_CARLO_TOLERANCE |

Normalizaciones permitidas aplicadas: orden de claves, whitespace, el anidamiento
formal de vocabularios (F1), precisión decimal de reales (F2) y categorías de
conteo cero omitidas (F3). Ninguna normalización modifica un valor matemático.
