# Evidencia de trazas y comportamiento

## Material publicable ya accesible por Git

* El piloto local H-ADAPT-001 tiene un catálogo de sus 32 corridas en
  `executions/h_adapt_001_pilot_execution_catalog.json` y tres extractos de
  ventanas originales en `executions/h_adapt_001_behavioral_extracts.json`.
  `executions/h_adapt_001_behavioral_windows_all.json` contiene la ventana de
  tres eventos que cruza el cambio causal para cada `run_id`, no sólo para la
  muestra curada.
  La fuente local completa tiene SHA-256
  `bf765f220f153b03b485b5adf700570472a64a4f80ba06ba63afcd39625baf73`.
  El piloto declara `FAIL`: sólo 13/32 corridas fueron experimentalmente
  válidas. No hubo bloqueo de protocolo ni confirmación.

* L19 preserva por semilla hashes de checkpoint, huellas de estado y hashes de
  trazas de decisión en
  `experiment/level18-predictive-state-01:artifacts/level19_predictive_state_v1.json`.
  La selección se hizo por las 32 semillas retenidas del preregistro, no por
  episodios exitosos.
* N1.0 preserva resultados agregados, manifiestos y reanálisis independiente en
  `research/primitivo-entidad-transitoria:docs/N10_EVIDENCE_BUNDLE_V1.json`.
  No existen las filas por decisión: el expediente declara esa pérdida.
* Las campañas remembered-binding preservan un factorial ON/OFF, gates y
  controles de tick en
  `experiment/organism-fusion-remembered-binding-01:terrario/remembered/experiment.py`.

## Material local identificado, no exportado

| Conjunto | Qué conserva | Estado de procedencia |
|---|---|---|
| Unidad Mínima 09 con máquina | JSON/JSONL de familias, reparación y máquina final | El texto de salida registra SHA del 09 local `7251adfb…` y del 08 importado `621c0534…`; local-only. |
| T2 disposición | 1.120 vidas sobre 35 mundos, disposición de olvido | El JSON registra SHA de `unidad_minima_14_disposicion_olvido.py` `82c5ee44…`; exploratorio-medido. |
| T2c más reloj | 175 vidas, cinco celdas, JSONL con orden causal por fila | Configuración y filas presentes; no contiene huella del runner ni de todos sus imports: procedencia parcial. |
| TRES | 65 filas, cinco generaciones y mutante de renombramiento | Marcado explícitamente exploratorio; el flag de exploración no invoca `letra_elegida()`. |

## Clasificación de `runs/` y `.terrario/`

El inventario contó 816 archivos en `runs/` (79 JSON, 3 JSONL y 69
binarios/checkpoints) y 3.640 en `.terrario/` (238 JSON, ocho bases o
sidecars y 238 binarios/checkpoints). Su significado no es uniforme:

| Fuente | Contenido verificado | Clasificación | Publicación |
|---|---|---|---|
| `runs/h_adapt_001_pilot_clean/` | 32 records, manifiestos, checkpoints y streams Parquet por fase | piloto científico identificable; resultado inconcluso | catálogo y extractos acotados |
| `runs/noche/`, `runs/screening/` | 62 filas JSONL de medidas agregadas D4T | screening/operativo; no secuencia conductual | no se presenta como evidencia conductual |
| `.terrario/terrario.db` | 141 ejecuciones, 240 attempts, 1.664 eventos y cero `scientific_results` | runtime/ledger local; no resultado científico publicado | sólo conteo y límite; base no exportada |
| `.terrario/runtime/` | 380 directorios runtime | datos de herramienta, procedencia individual pendiente | no exportado |

La inexistencia de `scientific_results` en la base revisada impide elevar esos
registros runtime a resultados científicos. Ninguna sesión privada o traza
masiva se ha publicado.

## Reglas de extracción futura

Antes de publicar cualquier extracto adicional se debe conservar: identificador
de corrida, hash de fuente ejecutada, configuración/semilla, regla de selección
del extracto y orden original de eventos. Se deben incluir al menos un caso
típico, un extremo y un negativo. Este expediente no inventa extractos nuevos
desde datos locales ni copia JSONL masivos sin revisión de divulgación.
