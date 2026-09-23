# Bloqueo de provenance: linaje de A2

Fecha de registro: 2026-09-22.

La evidencia matemática de A está cerrada; este documento sólo concierne a
ceguera e independencia de A2.

## Hecho verificado

El `session_meta` del rollout atribuido a A2 y su evento de comunicación
inicial registran:

- `agent_path`: `/root/a2_blind_replica`;
- `parent_thread_id`: `01a0cad8-4198-7c50-b3c6-f819f50cbe23` (la sesión A1);
- `subagent_history_start_ordinal`: `160`;
- modelo: `gpt-5.6-terra`;
- cwd inicial: `/home/wis/mundo simulado terrario`.

Fuente reproducible: `session_custody/raw/rollout-2026-09-22T14-57-33-01a0cae8-db17-7343-8e24-e062f914c26a.jsonl`, eventos iniciales 0--9.

El primer hash declarado por A1 consta en el ordinal 174 a
`2026-09-22T20:48:48.184Z`. A2 comienza a `2026-09-22T20:57:36.283Z`.
El contenido exacto del mensaje de tarea heredado por A2 está cifrado en el
rollout y no puede reconstruirse desde esta custodia.

## Consecuencia

Los análisis ya realizados sostienen `CLEAN_BY_LOG` y `LOG_SUPPORTS_G5`:
no hay evidencia de acceso prohibido antes de la declaración de hash. Eso no
demuestra que A2 fuese una sesión nueva e independiente de A1. El linaje de
subagente contradice esa descripción y no permite auditar qué contexto del
padre fue suministrado.

Por ello, bajo el criterio estricto de réplica ciega, A2 queda en
`PENDING_LINEAGE_ADJUDICATION`; no se la marca contaminada ni limpia de forma
concluyente. Una atestación humana puede cubrir lo que el investigador
proporcionó manualmente, pero no puede convertir contenido cifrado/no
preservado del contexto de plataforma en evidencia observada.

## Decisión requerida del investigador

Antes de cerrar G0/G5 de A2 debe decidirse si el experimento acepta una
réplica hija de A1 con contexto no auditable como independiente. Si no se
acepta, A2 conserva valor como reproducción computacional, pero no como la
segunda réplica ciega independiente. B sigue bloqueada en ambos casos hasta
que Gate A tenga una decisión formal.
