# Índice de fuentes y procedencia

| id | fuente | uso permitido | límite |
| --- | --- | --- | --- |
| S0 | solicitud/context card suministrada al abrir la rama | A, B, resultados cerrados y requisitos ETP-PRE-00 | contexto heredado; no reemplaza trazas ni los tres MD ausentes. |
| S1 | `experiments/primitivo_discovery02/discovery02.py` | instrumento DISCOVERY-02 y su alcance | no ejecutado; no genera resultado nuevo. |
| S2 | `experiments/primitivo_discovery03/discovery03.py` | instrumento DISCOVERY-03 y C4 histórico | no ejecutado; no genera resultado nuevo. |
| S3 | `experiments/primitivo_n2/README.md` | custodia de N=2 | línea separada, no evidencia de A. |
| S4 | `experiments/primitivo_n2/gate_a_verifier/GATE_A_REPORT.md` | advertencia de procedencia, B N=2 no ejecutada | no trasladable a A. |
| S5 | `docs/NIVEL_15_CIERRE_PREIMPLEMENTACION_01.md`; `docs/INFORME_CIERRE_PENDIENTES_01.md` | confirmar que no son los cierres PRIMITIVO requeridos | excluidos de claims PRIMITIVO. |

## Matriz de resultados importados

| resultado | procedencia actual | estatus |
| --- | --- | --- |
| DISCOVERY-00..03 / NO_LOCAL_SOLUTION | S0; S1/S2 sólo instrumentos | heredado cerrado; informe no localizado. |
| FULL_STATE_INTERNALIZATION | S0 | heredado; soporte de cierre no localizado. |
| RAAC | S0 | heredado cerrado; traza/intervención no localizada. |
| RDDA | S0 | heredado cerrado; informe no localizado. |
| PROJECTED/STARTUP/HEADROOM APD | S0 | heredado según rótulo; informe no localizado. |
| P-DATA, P-FULL, SELF_START/HALT, D/E/L/P | S0 | hechos heredados A; trazas no localizadas. |

Todo uso posterior añade fuente primaria localizable o conserva `UNKNOWN`.

## PRE-01: estatus de claim frente a procedencia

ETP-PRE-01 recupera el instrumento de DISCOVERY-02/03 y su commit de entrada
`41fccbf…`, pero esos scripts no emiten artefactos de resultado. Por ello los
claims heredados conservan `RESEARCHER_SUPPLIED_CONTEXT` como procedencia de
claim, aunque los instrumentos sean `SOURCE_LOCATED_IN_GIT_HISTORY`. Los tres
MD de 660 preguntas son `RESEARCHER_SUPPLIED / RAW FILE NOT LOCAL`; no son
`UNKNOWN` ni `MISSING_SOURCE` como claims. El detalle está en
ETP_PRE_01_BASELINE_CAUSAL_ATLAS.md.
