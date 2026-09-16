# CL7_PAIRED_SCRATCH_RUN_01 — corrida de borrador del diseño pareado, y dos defectos encontrados

Fecha: 2026-09-16
Clasificación: **ENGINEERING_SCRATCH_RUN · NOT_EVIDENCE**. Root de datos `.sandbox/tutorial-data-root`
(gitignored). Compuertas humanas firmadas por script. Nada de esto entra en el registro científico.

## 1. Qué se corrió

El diseño real de CL‑7 (`EXPERIMENT-DRAFT-20b807bf16cf7ff4`, hipótesis `HYPOTHESIS-b1c155f9304067f0`)
**derivado** con `ExperimentDraft.derive`: cambian solo `world_seeds` y `agent_seeds`; el mapeo de
hipótesis, los dos brazos, la métrica y el chequeo de manipulación viajan intactos y la procedencia
registra padre y campos cambiados.

| | valor |
| --- | --- |
| Semillas de mundo × agente | `(41, 42) × (61, 62)` — **distintas** de las preregistradas `(11, 12) × (21, 22)`, a propósito |
| Celdas | 8 = 4 pares × 2 brazos (`PLANNER_PRESERVED` `use_planner=true`; `PLANNER_ABLATED` `use_planner=false`; `use_world_model=true` en ambos) |
| Pasos por celda | 100 · 101 frames sellados por intento |
| Ejecución | `execution-143065932c1b4aca969a7bbfac3728d0` · 8 ensayos · `COMPLETED` en 71 s con un solo `dispatch` · verificación `PASS`, 0 avisos |

Guion reutilizable: `scripts/run_cl7_paired_scratch.py` (exige root absoluto, rechaza el root vivo y
**rechaza las semillas preregistradas**). Extracción sin reejecutar: `--extract-only <execution_id>`.

## 2. Resultados (borrador, no evidencia)

Métrica CL‑7 `planned-action-evaluation-pathway` = propuestas del planificador / decisiones, leída de
la traza sellada por el instrumento `evaluate_scientific_trace`, que no recibe la etiqueta del brazo:

| Par | Preservado | Ablacionado |
| --- | --- | --- |
| P1 (w41, a61) | 1.00 (100/100) | 0.00 (0/100) |
| P2 (w41, a62) | 1.00 (100/100) | 0.00 (0/100) |
| P3 (w42, a61) | 1.00 (100/100) | 0.00 (0/100) |
| P4 (w42, a62) | 1.00 (100/100) | 0.00 (0/100) |

Separación total y sin excepción en las cuatro parejas: la vía de propuesta/evaluación **está** cuando
el interruptor está y **no está** cuando no. Eso es exactamente lo que el constructo dice medir —
*disponibilidad de la vía* — y nada más: no dice que el planificador planifique bien.

Series por tick (medias por brazo; la página HTML lleva las 8 celdas):

| Medida | Preservado | Ablacionado | Lectura prudente |
| --- | --- | --- | --- |
| Energía final | 0.97–1.00 | 1.00 | ambos brazos terminan casi llenos; la energía no discrimina en 100 pasos |
| Error de predicción ε (media) | ≈ 0.67 | ≈ 0.60–0.65 | el modelo de mundo está activo en ambos; ε no es la variable dependiente |
| Incertidumbre (media) | 0.33–1.21 | 0.53–0.55 | mayor dispersión con planificador; una sola semilla por celda, no concluir |
| Entropía de la política | baja en ~20 ticks a una meseta ≈ 0.3–0.7 (cae a 0 en el último tick) | decae a ≈ 0.03 | el brazo ablacionado colapsa a una política casi determinista; el preservado conserva dispersión |

Lo que **no** se puede afirmar con esto: aprendizaje, competencia, superioridad de un brazo, ni
efecto causal. Una semilla por celda, `repetitions: 1`, ejecución fuera del preregistro. La página
`cl7-pareado-resultados.html` lo dice en su primera línea.

## 3. Defecto 1 — el gate de ejecución bloqueaba todo diseño pareado (corregido)

**Síntoma.** Tras aprobar el diseño, preregistrar, revisar y bloquear, `bind-authorization` respondió
`422 EXECUTION_NOT_READY · UNRESOLVED_VARIANT_BINDING`.

**Causa.** Dos contratos en contradicción:
- `experiment_composer.py:71-81` (`TreatmentArm`): *«`variant` is descriptive metadata of an arm,
  never a second factorial axis»*. Los brazos son fijos (`"preserved"`, `"ablated"`) y
  `build_trial_matrix` escribe ese valor en el `variant_id` de cada celda.
- `execution/service.py:328` (`_readiness`): por cada celda, `variant_id ∈ {scenario, scenario-base}`;
  si no, `UNRESOLVED_VARIANT_BINDING`.

Por construcción, **ninguna matriz pareada podía ejecutarse**. Las dos matrices pareadas reales del
data root vivo (`TM-252f4041…`, `TM-e4cf621e…`) tienen `{preserved: 4, ablated: 4}`. El informe
`demonstrate_cl7_runtime_readiness.py` no lo detecta porque nunca evalúa esa regla. Ningún test
llevaba un diseño pareado más allá del lock.

**Corrección aplicada (opción A, elegida por la persona responsable).** `_readiness` acepta una celda
cuyo `arm_id` es uno de los dos brazos y trae `agent_config`: su intervención está ligada en la
configuración del agente y corre sobre el escenario base. No cambia ninguna identidad científica —
ni `trial_matrix_hash` ni roots de preregistro. La alternativa B (escribir `D2-base` en las celdas)
habría cambiado los hashes y dejado obsoletas las dos matrices reales.

**Pruebas.** `tests/test_paired_design_execution_readiness.py` (nuevo): construye un diseño pareado
con los objetos de dominio de `test_cl7_paired_preregistration.py`, lo lleva hasta lock en
`tmp_path` y exige `ready` y `bind` = 200. Rojo antes del parche; verde después. Con
`test_scientific_execution_gate.py`, `test_cl7_paired_preregistration.py` y
`test_preregistration_core.py`: **26 passed**, guardián del root vivo en silencio.

## 4. Defecto 2 — `verify()` no es idempotente (propuesto, no aplicado)

`execution/service.py:222` inserta siempre en `scientific_execution_verifications`, cuyo
`report_hash` es `UNIQUE` y cuya tabla prohíbe `UPDATE`. Verificar dos veces una ejecución cuyo
informe no cambió devuelve **500 `UNIQUE constraint failed`**. En la UI, el segundo clic en
«Verify integrity» falla. Propuesta mínima, coherente con la inmutabilidad (no actualiza nada):

```python
existing = con.execute("SELECT report_json FROM scientific_execution_verifications WHERE execution_id=? AND report_hash=?",
                       (execution_id, report.report_hash)).fetchone()
if existing:
    return json.loads(existing["report_json"])   # same report already sealed: idempotent
con.execute("INSERT INTO scientific_execution_verifications(...) VALUES(?,?,?,?,?)", ...)
```

Un informe **distinto** (nuevas desviaciones, CAS corrupto después) sigue insertándose: eso es lo que
la tabla quiere conservar.

## 5. Trazabilidad del root vivo durante este trabajo

La huella de `.terrario/terrario.db` pasó de `05e6cb13…` a `5527cf7b…` durante la corrida. No fue
una fuga: fue **una decisión humana real** registrada en el Centro de revisión —
`review-82c0a332…` → `REQUEST_CHANGES` por `local-user`, 2026-09-16 05:59 UTC. `runtime/` (140) y
`scientific_executions` (141) no cambiaron. Nota para el guardián de `tests/conftest.py`: una suite
lanzada mientras una persona usa el lab vivo disparará el guardián; es un falso positivo esperado
y la salida del guardián muestra qué tabla cambió.
