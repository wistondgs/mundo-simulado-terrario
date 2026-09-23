# Gate A — auditoría de cierre de procedencia

Fecha de auditoría: 2026-09-23. Alcance: exclusivamente Gate A y su
atestación. No se inspeccionó, ejecutó, preparó ni usó Gate B como evidencia.

## Resultado

`ATTESTATION = NOT_FULLY_CONFIRMABLE`.

Se marcaron únicamente las tres limitaciones objetivas cuya formulación tiene
soporte literal. No se firma el formulario ni se convierten logs en una
atestación personal. Las once casillas restantes no se marcan.

`GATE_A_MATH = PASS` permanece como cierre matemático/computacional. No es un
cierre de procedencia. Para el conjunto elegible A1+A2b: `G0 =
PENDING_PROVENANCE`, `G5 = PENDING_PROVENANCE` y `GATE_A =
PENDING_PROVENANCE`. A2 histórica es corroboración dependiente y no satisface
la segunda réplica independiente; A2b está preparada pero no ejecutada.

G0 exige evidencia de aislamiento inicial; G5 exige evidencia sobre la
comunicación de hashes/referencia antes de la declaración. Los rollouts dan
`CLEAN_BY_LOG` y `LOG_SUPPORTS_G5`, respectivamente, pero la propia política
de Gate A los clasifica como evidencia documental, no como atestación externa.

## Matriz de evidencia

| attestation_item | exact_claim | evidence_file | evidence_location | git_commit_if_applicable | hash_if_applicable | custody_relation | verdict | rationale |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1-1 | El rollout A1 corresponde a la sesión que produjo A1 final. | `SESSION_FORENSIC_AUDIT.json` | `A1.attribution=ATTRIBUTED`; `A1.record` | N/A: Gate A no está versionado en Git | `04078…fe08e` | Rollout sellado, atribución documental | INSUFFICIENT_EVIDENCE | Atribuye el registro, pero no prueba la confirmación factual del investigador. |
| A1-2 | A1 era distinta del intento previo descartado por `BLINDNESS_COMPROMISED`. | `ATTESTATION_FINAL_TO_CONFIRM.md` | líneas 29–30; no hay atestación firmada | N/A | N/A | Ninguna cadena primaria que relacione ambos hechos y la declaración del investigador | INSUFFICIENT_EVIDENCE | La casilla está vacía; la documentación revisada no aporta la confirmación solicitada. |
| A1-3 | No se suministró manualmente a A1 referencia, código, hashes esperados ni A2 antes del resultado. | `BLINDNESS_GATE.json` | `A1.G0.status=PENDING`, `evidence_level=NONE` | N/A | N/A | Log de sesión, no testimonio externo | INSUFFICIENT_EVIDENCE | La ausencia en el log no prueba los canales manuales fuera del log. |
| A1-4 | El investigador recibió el output A1 y no suministró referencia antes de declararlo. | `GATE_A_FINAL_PROVENANCE.json` | `A1.G5=PENDING_INVESTIGATOR_ATTESTATION` | N/A | `04078…fe08e`, ordinal 174 | Rollout sellado; declaración de hash documentada | INSUFFICIENT_EVIDENCE | G5 documental no sustituye el hecho personal de recepción/no suministro. |
| A2-1 | El rollout A2 corresponde a la sesión que produjo A2 final. | `SESSION_FORENSIC_AUDIT.json` | `A2.attribution=ATTRIBUTED`; `A2.record` | N/A | `04078…fe08e` | Rollout sellado, atribución documental | INSUFFICIENT_EVIDENCE | Falta la confirmación factual requerida por la casilla. |
| A2-2 | A2 fue una sesión separada de A1. | `CUSTODY_REQUIREMENTS_AUDIT.json` | `A2.lineage`: hijo `/root/a2_blind_replica` de A1; `SESSION_FORENSIC_AUDIT.json` dice `SAME_FAMILY_SEPARATE_SESSIONS` | N/A | N/A | Metadata primaria preservada, contexto heredado no legible | NOT_CONFIRMABLE | Hay rollout distinto, pero también linaje hijo no auditable; no se puede elevar a independencia ni a una confirmación del investigador. |
| A2-3 | No se suministró manualmente a A2 información de A1 o referencia antes de su resultado. | `BLINDNESS_GATE.json` | `A2.G0.status=PENDING_LINEAGE_ADJUDICATION` | N/A | N/A | Log documental; contexto heredado no preservado legiblemente | INSUFFICIENT_EVIDENCE | Ni el log ni la metadata excluyen los canales manuales ni el contexto heredado. |
| A2-4 | No se suministraron outputs A1 a A2 por tarea u otro canal antes de la declaración. | `PROVENANCE_BLOCKER_A2_LINEAGE.md` | sección “Hecho verificado” y “Consecuencia” | N/A | N/A | Contexto de subagente cifrado/no legible | INSUFFICIENT_EVIDENCE | El contenido heredado no puede reconstruirse; no hay atestación externa. |
| A2-5 | El investigador acepta clasificar A2 hija como insuficiente para réplica independiente. | `ATTESTATION_FINAL_TO_CONFIRM.md` | líneas 79–81, casilla vacía | N/A | N/A | Formulario no firmado | NOT_CONFIRMABLE | Es una aceptación del investigador, no un hecho inferible por auditoría. |
| A2-6 | El investigador recibió el output A2 y no suministró A1/referencia antes de declararlo. | `GATE_A_FINAL_PROVENANCE.json` | `A2.G5=NOT_ELIGIBLE_FOR_INDEPENDENT_GATE` | N/A | `04078…fe08e`, ordinal 155 | Rollout sellado; no elegible por linaje | INSUFFICIENT_EVIDENCE | La evidencia documental no prueba el suministro manual ni la recepción personal. |
| M-1 | A1 y A2 fueron sesiones separadas de la misma familia de modelo. | `CUSTODY_REQUIREMENTS_AUDIT.json` | `A1/A2.model=gpt-5.6-terra`; `SESSION_FORENSIC_AUDIT.json` `SAME_FAMILY_SEPARATE_SESSIONS` | N/A | N/A | `session_meta` preservado | NOT_CONFIRMABLE | Los metadatos apoyan el hecho técnico, pero no son una confirmación firmada del investigador; tampoco prueban independencia experimental de A2. |
| L-1 | A2 no preservó `FREEZE_MANIFEST.sha256` y no será reconstruido retrospectivamente. | `FREEZE_AUDIT.json`; `GATE_A_REPORT.md` | `A2.status=FAIL`, `manifest=MISSING`; “A2 histórica se conserva sin modificar” | N/A | N/A | Auditoría reproducible del árbol A2 | CONFIRMABLE | Ausencia verificada y política explícita de no reconstrucción retrospectiva. Casilla marcada. |
| L-2 | A1 y A2 preservaron sólo hashes precalibración, no bytes ejecutables precalibración. | `CUSTODY_REQUIREMENTS_AUDIT.json` | `A1.precalibration=HASH_ONLY`, `A2.precalibration=HASH_ONLY`; definición de `HASH_ONLY` | N/A | N/A | Auditoría de custodia | CONFIRMABLE | La definición literal de `HASH_ONLY` establece hash histórico sin bytes correspondientes. Casilla marcada. |
| L-3 | No existe listado histórico externo de directorios iniciales; listados actuales no lo sustituyen. | `CUSTODY_REQUIREMENTS_AUDIT.json` | `A1/A2.initial_directory_external_listing.status=NOT_FOUND`, clasificación `NO_REGISTRADO_EN_EL_ARMADO` | N/A | N/A | Auditoría de custodia | CONFIRMABLE | El archivo enuncia literalmente la ausencia y que un listado actual sería retrospectivo. Casilla marcada. |

Abreviatura de hash: `04078…fe08e` =
`04078dfd296f43679c97dab57e7578684c98893e43730e9573e5b244d0cfe08e`.

## Contraste de custodia independiente

- A1: atribuida documentalmente; G0/G5 permanecen pendientes de atestación.
- A2: rollout separado pero hijo de A1 (`agent_path=/root/a2_blind_replica`);
  su contexto heredado no es auditable. Es `DEPENDENT_CORROBORATION ·
  LINEAGE_NOT_AUDITABLE`, no segunda réplica independiente.
- A2b: sólo existe custodia previa externa, con SPEC de hash
  `f19324cd5039cc6f83176a77afe8ff23b07e817e1a1471e5e56d05823515a430`;
  está `WORKSPACE_PREPARED_NOT_EXECUTED`. Por tanto no puede suplir A2 aún.
- No se encontró una fuente primaria firmada que cubra las declaraciones de
  suministro manual, recepción de outputs, identificación personal de sesión o
  aceptación del investigador. Las marcas de log son más débiles que esas
  declaraciones.

## Condición para avanzar

Este documento no habilita Gate B. Gate A sólo podrá cambiar a `PASS` tras
atestación factual verificable de los requisitos A1 y una A2b ejecutada con
custodia independiente que satisfaga G0/G5. Hasta entonces no hay un `FAIL`
causal o matemático: hay `PENDING_PROVENANCE`.
