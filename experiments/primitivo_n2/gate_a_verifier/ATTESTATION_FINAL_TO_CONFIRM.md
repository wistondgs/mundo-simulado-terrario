------------------------------------------------------------
INVESTIGATOR PROVENANCE ATTESTATION
PRIMITIVO N=2 — GATE A
------------------------------------------------------------

Esta plantilla no está firmada. Sus datos documentales proceden de los
rollouts preservados bajo `session_custody/raw/` y de
`SESSION_FORENSIC_AUDIT.json`.

## Alcance actualizado (2026-09-22)

A2 histórica queda preservada como `DEPENDENT_CORROBORATION ·
LINEAGE_NOT_AUDITABLE` y ya no puede cerrar Gate A como segunda réplica
independiente. Los checkbox de su sección se conservan como historia de
custodia; no cambian ese estado. Gate A requerirá A1 y la futura A2b.
A2b aún no fue ejecutada, por lo que no se atesta en este documento todavía.

## A1

**SESSION:**

`rollout-2026-09-22T14-39-25-01a0cad8-4198-7c50-b3c6-f819f50cbe23.jsonl`

**LOG RESULT:** `CLEAN_BY_LOG`

[ ] Confirmo que este rollout corresponde a la sesión que produjo la réplica
    A1 final.

[ ] Confirmo que esa sesión A1 era distinta del intento anterior descartado
    por `BLINDNESS_COMPROMISED`.

[ ] Confirmo que no proporcioné manualmente a esa sesión resultados de
    referencia, código de referencia, hashes esperados ni resultados de A2
    antes de que produjera su resultado.

**G5 DOCUMENTARY EVIDENCE**

- rollout: el archivo A1 indicado arriba, en custodia sellada;
- evento/ordinal: `174`;
- timestamp: `2026-09-22T20:48:48.184Z`;
- declared hash (extraído del rollout):
  `04078dfd296f43679c97dab57e7578684c98893e43730e9573e5b244d0cfe08e`;
- reference disclosure before declaration: `NONE_FOUND_IN_LOG`.

[ ] Confirmo que recibí ese resultado como salida de esa sesión y que no
    suministré manualmente a A1 el resultado de referencia antes de esa
    declaración.

------------------------------------------------------------

## A2

**SESSION:**

`rollout-2026-09-22T14-57-33-01a0cae8-db17-7343-8e24-e062f914c26a.jsonl`

**LOG RESULT:** `CLEAN_BY_LOG`

[ ] Confirmo que este rollout corresponde a la sesión que produjo la réplica
    A2 final.

[ ] Confirmo que A2 fue una sesión separada de A1.

[ ] Confirmo que no proporcioné manualmente a A2 resultados, hashes, código
    ni conclusiones de A1 o de la referencia antes de que produjera su
    resultado.

**LIMITACIÓN DE LINAJE DOCUMENTADA**

El rollout de A2 registra `agent_path=/root/a2_blind_replica`,
`parent_thread_id` igual a la sesión A1 y `subagent_history_start_ordinal=160`.
El contenido exacto del mensaje/contexto heredado no es legible en la
custodia. Por ello, este formulario no presupone que A2 fuera una sesión
independiente: esa decisión sigue pendiente.

[ ] Confirmo que no proporcioné manualmente a A2 resultados u outputs de A1
    mediante el mensaje de tarea ni otro canal antes de su declaración.

[ ] Declaro que acepto que la procedencia hija de A2 se clasifique como
    evidencia insuficiente para una réplica independiente, salvo que pueda
    aportarse evidencia externa verificable sobre el contexto heredado.

**G5 DOCUMENTARY EVIDENCE**

- rollout: el archivo A2 indicado arriba, en custodia sellada;
- evento/ordinal: `155`;
- timestamp: `2026-09-22T21:03:03.928Z`;
- declared hash (extraído del rollout):
  `04078dfd296f43679c97dab57e7578684c98893e43730e9573e5b244d0cfe08e`;
- A1/reference disclosure before declaration: `NONE_FOUND_IN_LOG`.

[ ] Confirmo que recibí ese resultado como salida de esa sesión y que no
    suministré manualmente resultados de A1 o de la referencia antes de esa
    declaración.

------------------------------------------------------------

## Modelo/familia

[ ] Confirmo que A1 y A2 fueron sesiones separadas de Codex Local de la misma
    familia, no dos familias de modelos distintas.

## Limitaciones reconocidas

[x] A2 no preservó `FREEZE_MANIFEST.sha256` y no será reconstruido
    retrospectivamente.

[x] A1 y A2 preservaron sólo hashes precalibración, no los bytes ejecutables
    precalibración.

[x] Reconozco que no se preservó un listado histórico externo de los
    directorios iniciales de A1/A2; los listados actuales no sustituyen ese
    requisito de custodia.

## Investigador

INVESTIGATOR:
____________________

DATE:
____________________
