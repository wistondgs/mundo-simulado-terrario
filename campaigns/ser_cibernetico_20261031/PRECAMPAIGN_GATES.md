# SER-CIBERNETICO-20261031 · compuertas previas

Base inmutable de desarrollo: `66320133429942b86f6931770d8f4c4765fba9ca`.
Este directorio pertenece al clon aislado `campaign/ser-cibernetico-20261031`.
No contiene una campaña científica ni reemplaza los artefactos históricos.

| Compuerta | Criterio operacional | Estado inicial |
|---|---|---|
| K01 | codec A6 sólo de canales/máscara; invarianza a energía/tiempo y aliasing declarado | PASS · `test_k01...` |
| K02 | no presentar pendiente energético como adquisición ni cero por defecto como predicción | PASS · `test_k02...` |
| K03 | L16, L17 y L19 deben influir una decisión pre-consecuencia | PASS · `test_k03...` |
| K04 | consumo remoto rechazado no evalúa regla ni modifica energía | PASS · `test_controller_remote_target_gate.py` |
| K05 | checkpoint A6 restaura estado simbólico exacto, con versión | PASS · `test_k05...` |
| K06 | límites vida/episodio/mundo explícitos; reset no borra aprendizaje | PASS · `test_k06...` |
| K07 | pruebas A6 entran en la suite general y sólo CPU | PASS · 112 pruebas de `tests/` en CPU |
| K08 | factorial C04 se materializa sólo después de congelar su unidad estadística | BLOCKED · el preregistro dice 3 315 W1→W2 y a la vez exige control componible/no componible por celda; no determina si éste duplica recorridos |
| K09 | ninguna campaña larga sin lanzador durable, PID verificable y recuperación | READY_FOR_PREFLIGHT · `run_canonical_preflight.py` deja PID, SHA, estado atómico y resultado, pero aún no se ha lanzado una corrida |
| K10 | linajes se conservan como referencias; no se fusionan worktrees históricos | satisfecho por aislamiento |

La política predictiva A6 es una conexión de ingeniería: emplea distribuciones
pre-consecuencia de L16/L17/L19 y no afirma rendimiento adaptativo ni transferencia.

Validación histórica C03 (clon separado en `f69815f...`): 239 pruebas de
L16/L17/L18/L19 pasaron; `test_l17_0_pasa_sobre_el_arbol_real` falló porque su
guarda exige que no exista un directorio `level18`. Es una incompatibilidad de
linaje declarada; no se corrigió el artefacto histórico ni se usó como evidencia
de transferencia a A6.
