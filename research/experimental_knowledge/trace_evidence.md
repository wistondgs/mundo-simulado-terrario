# Evidencia de trazas y comportamiento

## Material publicable ya accesible por Git

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

## Reglas de extracción futura

Antes de publicar cualquier extracto adicional se debe conservar: identificador
de corrida, hash de fuente ejecutada, configuración/semilla, regla de selección
del extracto y orden original de eventos. Se deben incluir al menos un caso
típico, un extremo y un negativo. Este expediente no inventa extractos nuevos
desde datos locales ni copia JSONL masivos sin revisión de divulgación.
