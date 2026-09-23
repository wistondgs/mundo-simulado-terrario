# Gate A — actualización forense

## Custodia y atribución

La custodia de seis rollouts candidatos y la copia SQLite/WAL/SHM verificó el manifest `SESSION_RAW_CUSTODY.sha256`. A1 queda atribuido a `rollout-2026-09-22T14-39-25-01a0cad8-4198-7c50-b3c6-f819f50cbe23.jsonl` y A2 a `rollout-2026-09-22T14-57-33-01a0cae8-db17-7343-8e24-e062f914c26a.jsonl`; la atribución combina el prompt, `REPLICA_ID`, operaciones sobre el workspace, reporte COMPLETE y hash declarado. Ambas sesiones registran cwd inicial de raíz del proyecto; eso es una limitación de contexto, no una lectura por sí misma.

## G0/G5 documental

Antes de la primera declaración de hash, el log resulta `CLEAN_BY_LOG` para G0 y `LOG_SUPPORTS_G5` para ambas réplicas. Los hashes extraídos literalmente son `04078dfd296f43679c97dab57e7578684c98893e43730e9573e5b244d0cfe08e` (A1, evento 174) y `04078dfd296f43679c97dab57e7578684c98893e43730e9573e5b244d0cfe08e` (A2, evento 155). No se observó revelación de referencia previa en esos logs.

Esto es evidencia documental, no atestación ni timestamp criptográfico externo. Por ello G0/G5 siguen en `PENDING` hasta una confirmación factual del investigador; `ATTESTATION_TEMPLATE.md` se generó sin firma.

## Reejecución

Cada source final se copió sin outputs a un entorno limpio del verificador y se ejecutó allí. Ambos regeneraron byte a byte `por_sistema.jsonl` con SHA-256 común `04078dfd296f43679c97dab57e7578684c98893e43730e9573e5b244d0cfe08e`. `FROZEN_CODE_COMPUTATION=VERIFIED`.

## Estado

`GATE_A_MATH=PASS`; `GATE_A_BLINDNESS=PENDING`; `GATE_A_OVERALL=PENDING_PROVENANCE`. A2 conserva `FREEZE_MANIFEST_NOT_PRESERVED`; no se reconstruyó. Los sources precalibración quedan `HASH_ONLY`. SPEC B se rehasheó como freeze estático (`677c5764eb4a519be089171404825ccc454fe8dc29771c2f577db88799f39e94`) y no se ejecutó. B queda `READY_AFTER_PROVENANCE`.
