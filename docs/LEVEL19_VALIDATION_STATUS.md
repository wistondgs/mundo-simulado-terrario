# L19 · estado de validación

## Estado de validación

* Fuente compilada estáticamente con `python3 -m py_compile`; `git diff --check`
  no reportó errores de espacios.
* Pruebas L19 ejecutadas: **11 passed**.
* Campaña sellada: 32 semillas retenidas, 256 episodios de exploración uniforme
  y 256 de evaluación pasiva por vida.
* Entrenamiento y evaluación usaron pares disjuntos sellados
  `310001…310032 → 320001…320032`; no se compartió identificador de semilla.
* Resultado: `CAPACIDAD_DEMOSTRADA` bajo el criterio predefinido. Los límites
  inferiores pareados al 95 % fueron `+0.5114138656840121` (predicción),
  `+0.48996616892268824` (decisión tras lesión) y
  `+0.38970055881010335` (decisión bajo perturbación de señal).
* 32 checkpoints fueron restaurados y verificados mediante sus huellas.
* `level18/` no fue modificado: `LEARNER-18-v1 = INSUFICIENTE` permanece
  intacto.

## Entorno de ejecución

El worktree no poseía un entorno listo. Se usó una instalación local e ignorada
por Git, `.deps-level19/`, limitada a `numpy 2.5.4` y `pytest 9.1.1`; no se
instaló Torch ni se modificó el sistema. El artefacto registra Python, plataforma,
NumPy, `PYTHONPATH`, hashes del source, runner y pruebas.

## Ejecución autorizada cuando el entorno exista

```bash
<python-con-numpy-y-pytest> -m pytest tests/test_level19_predictive_state.py tests/test_level19_experiment.py -q
<python-con-numpy> scripts/run_level19_predictive_state_v1.py
```

El segundo comando crea `artifacts/level19_predictive_state_v1.json` y
checkpoints por semilla. El artefacto registra SHA, suciedad del árbol, versiones
de Python/NumPy, hashes de código, semillas, configuración, métricas y el
dictamen predefinido.
