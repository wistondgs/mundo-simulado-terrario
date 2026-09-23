# Gate A — informe de auditoría externa

## Hechos verificados

- Las tres copias de la SPEC A tienen SHA-256
  `f19324cd5039cc6f83176a77afe8ff23b07e817e1a1471e5e56d05823515a430`.
- La referencia fue ejecutada en `gate_a_verifier/reference_generated/`, sin
  modificar su fuente. Los tres `por_sistema.jsonl` tienen 256 líneas,
  codificación canónica, orden normativo y el mismo SHA-256:
  `04078dfd296f43679c97dab57e7578684c98893e43730e9573e5b244d0cfe08e`.
  La igualdad es también byte a byte.
- El verificador recalculó desde JSONL los conteos §11, H, I, E[I], AMI_max,
  simetría entre cortes, puntos fijos de scheduler, máscaras y la guardia
  intrínseca. Todos pasan. El tipo S4 observado tiene cardinalidad 19,
  consistente con A001372 para n=4.
- RUN1, RUN2 y el resultado final de cada réplica son iguales por hash para
  los dos artefactos deterministas declarados.
- A1 tiene un freeze interno íntegro: todas sus entradas rehacen correctamente
  y el hash del freeze coincide con el declarado. No contiene
  `manifest_replica.json`, por lo que no se observó circularidad.

## Claims autorreportados

`blindness_candidate`, los resultados de calibración y los estados de freeze
de cada réplica son claims hasta que exista custodia del investigador. A1 y A2
declaran pruebas y calibradores en PASS; los datos matemáticos finales fueron
verificados independientemente como se describe arriba.

## Attestaciones externas pendientes

G0 y G5 permanecen **PENDING** para A1 y A2. Los manifests internos, el
registro de acceso de A2 y los ZIP de custodia no sustituyen una atestación
externa del investigador sobre aislamiento inicial y comunicación de hashes
antes de revelar la referencia.

## Diferencias formales

Hay 31 diferencias formales en `resumen.json`: precisión de impresión de
reales (F2) y dos categorías de conteo cero omitidas por la referencia (F3).
La normalización es expresamente permitida por §14 y todos los valores quedan
dentro de 1e-6 de la recomputación. La ambigüedad informada por A1 pertenece a
la variante preregistrada de anidamiento F1. No se encontraron diferencias de
valor ni ambigüedades value-affecting.

## Defectos de protocolo

A2 no contiene `FREEZE_MANIFEST.sha256`. Por tanto su freeze interno no puede
rehacerse ni verificarse, y su `manifest_replica.json` tampoco contiene el
campo de hash de freeze requerido. Es un **PROTOCOL_DEFECT** de custodia, no
un defecto matemático: su JSONL final y sus corridas deterministas sí fueron
verificados externamente. No se encontró `FREEZE_SELF_REFERENCE` en A1; en
A2 no hay manifest que pueda evaluarse para esa circularidad.

El nuevo `INPUT_CUSTODY_MANIFEST.sha256` es el sello externo no circular de
los inputs recibidos; su SHA-256 es
`892eee89a7c4529b47e9a9203aee2eb026266fcb877126ae0cc8f688fe7ae80a`.

## Interpretación

`GATE_A_MATH=PASS`: bajo SPEC A v0.1, C1–C11 quedan verificados para N=2 en
sentido matemático/computacional. Esto no certifica la ontología, una unidad,
generalización a N mayor ni sensibilidad a convenciones. Dado que G0/G5 no
están certificados y A2 carece de freeze interno, `GATE_A_OVERALL` es
`PENDING_PROVENANCE` y B sigue bloqueada hasta adjudicación del investigador.

## Actualización forense de sesiones

Las copias selladas de los seis rollouts y de la base de estado atribuyen A1
al rollout de las 14:39 y A2 al subagente de las 14:57. Antes de sus primeras
declaraciones del hash por-sistema, el log registra `CLEAN_BY_LOG` para G0 y
`LOG_SUPPORTS_G5` para ambas; no registra revelación previa de referencia.
Los logs no reemplazan una atestación factual del investigador, por lo que
G0/G5 siguen en `PENDING`.

La reejecución aislada de cada source final —sin outputs ni referencia—
regeneró byte a byte el JSONL congelado: `FROZEN_CODE_COMPUTATION=VERIFIED`.
SPEC B no fue ejecutada.

## Addendum de provenance — 2026-09-22

El metadata preservado de A2 identifica la ejecución como subagente de A1
(`agent_path=/root/a2_blind_replica`, `parent_thread_id` de A1 y
`subagent_history_start_ordinal=160`). El payload inicial heredado está
cifrado/no legible en la custodia disponible. En consecuencia, los resultados
forenses `CLEAN_BY_LOG` y `LOG_SUPPORTS_G5` se conservan, pero no bastan para
certificar que A2 fue una segunda sesión ciega independiente.

`GATE_A_OVERALL` pasa a
`BLOCKED_PENDING_A2_LINEAGE_ADJUDICATION_AND_ATTESTATION`. Esta es una
limitación de provenance, no una discrepancia de A: matemáticas, outputs y
reejecuciones permanecen verificados. B queda `BLOCKED_PENDING_GATE_A`.

Para futuras réplicas ciegas rige
`BLIND_WORKSPACE_POLICY=OUTSIDE_REPOSITORY_REQUIRED`.

## Decisión de reemplazo A2 — 2026-09-22

Se adoptó el criterio estricto: A2 histórica se conserva sin modificar como
`DEPENDENT_CORROBORATION · LINEAGE_NOT_AUDITABLE` y no integra el conjunto
independiente de Gate A. Se preparó A2b en `/home/wis/primitivo_blind/A2b`,
fuera del repositorio, con exactamente la SPEC A y `TASK_A2B.txt`; su
inventario y hashes previos constan en `A2B_CUSTODY/`. A2b no fue abierta ni
ejecutada por el custodio. El conjunto requerido pasa a ser `A1 + A2b`.
