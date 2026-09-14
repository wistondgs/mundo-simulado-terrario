---
kind: generated-status
generated_from: project_manifest.json
manifest_sha256: 03abceab66a89b89e95d4817a4a2f4b0e0ba07bb3ffd8369dec39a14fb1bd3eb
active_snapshot: theory-f59dbb6d6ee3850c
---

# Estado técnico de Terrario

> [!warning] Nota generada
> No editar esta nota a mano. Ejecuta `./.venv/bin/python scripts/sync_obsidian_vault.py --write` tras un cambio deliberado de manifiesto. Comprueba vigencia con `--check`.

[[knowledge/00 Control/Inicio|← Inicio]] · [[knowledge/00 Control/Registro de decisiones|Decisiones]] · [[knowledge/01 Roadmap/Ruta activa|Ruta activa]]

## Fuente verificada

- Manifiesto: [project_manifest.json](../../project_manifest.json) (`03abceab66a89b89e95d4817a4a2f4b0e0ba07bb3ffd8369dec39a14fb1bd3eb`)
- Snapshot activo: `theory-f59dbb6d6ee3850c` (`f59dbb6d6ee3850c7fa366f087f51f0a0dc69d8ef2ea973e33ad8681eb692b68`)
- Resumen de ingestión: [ingestion_summary.json](../../theory_snapshots/theory-f59dbb6d6ee3850c/ingestion_summary.json)
- Conteo de fuentes confirmado: `44`

## Bloqueos activos

- `CUDA_OS_BLOCKED`
- `PREREGISTRATION_BROWSER_QA_RUNNER_UNAVAILABLE`
- `PREREGISTRATION_REQUIRES_HUMAN_DECISIONS_PER_BUNDLE`
- `SCIENTIFIC_EXECUTION_WORKER_CHECKPOINT_CERTIFICATION_PENDING`
- `SCIENTIFIC_EXECUTION_BROWSER_QA_PENDING`
- `H_ADAPT_HUMAN_REVIEW_NOT_APPROVED`

## Fases

| Fase | Estado | Depende de |
| --- | --- | --- |
| SYSTEM-BASELINE-01 | COMPLETE | — |
| LAB-PERSISTENCE-01 | COMPLETE | SYSTEM-BASELINE-01 |
| PREREGISTRATION-CORE-01 | ACTIVE_BROWSER_QA_BLOCKED | LAB-PERSISTENCE-01 |
| REGISTRY-HARDENING-01 | PLANNED | PREREGISTRATION-CORE-01 |
| INTERACTION-KERNEL-01 | PLANNED | REGISTRY-HARDENING-01 |
| DEVICE-RUNTIME-01 | PLANNED | INTERACTION-KERNEL-01 |
| GPU-RECOVERY-01 | BLOCKED_OS | — |
| EXECUTION-ORCHESTRATOR-01 | PLANNED | PREREGISTRATION-CORE-01, DEVICE-RUNTIME-01 |
| SCIENTIFIC-EXECUTION-GATE-01 | IMPLEMENTED_RAW_ARTIFACT_GATE | PREREGISTRATION-CORE-01 |
| CAUSAL-INTERVENTION-FORK-CORE-01 | PARTIAL_A0_D0_QUALIFIED | SCIENTIFIC-EXECUTION-GATE-01 |
| EVIDENCE-PIPELINE-02 | PLANNED | EXECUTION-ORCHESTRATOR-01 |
| API-V1-UX-CONTRACT-01 | PLANNED | EVIDENCE-PIPELINE-02 |
| D2-D4-QUALIFICATION-01 | PLANNED | API-V1-UX-CONTRACT-01 |
| LAB-UX-03 | DEFERRED | D2-D4-QUALIFICATION-01 |
| SCIENTIFIC-PILOT-01 | HUMAN_AUTHORIZATION_REQUIRED | D2-D4-QUALIFICATION-01 |

## Componentes

| Componente | Estado | Depende de |
| --- | --- | --- |
| CORPUS | ADVANCED | — |
| ONTOLOGY | IMPLEMENTED | CORPUS |
| THEORY_GRAPH | IMPLEMENTED | CORPUS, ONTOLOGY |
| HYPERGRAPH | CANDIDATES_ONLY | THEORY_GRAPH |
| HYPOTHESIS_FACTORY | IMPLEMENTED | HYPERGRAPH |
| SCIENTIFIC_REVIEW | READY_FOR_HUMAN_REVIEW | HYPOTHESIS_FACTORY |
| TERRARIO_CORE | IMPLEMENTED | — |
| WORLD_STUDIO | PARTIAL_D2_D4 | TERRARIO_CORE |
| EXPERIMENT_COMPOSER | PREREGISTRATION_READY_BOUNDARY | SCIENTIFIC_REVIEW, WORLD_STUDIO |
| DURABLE_STORAGE | IMPLEMENTED_V1 | EXPERIMENT_COMPOSER |
| PREREGISTRATION | IMPLEMENTED_AWAITING_BROWSER_QA | DURABLE_STORAGE |
| EXECUTION_ORCHESTRATOR | IMPLEMENTED_SCIENTIFIC_GATE_01 | PREREGISTRATION |
| CAUSAL_FORK_CORE | PARTIAL_A0_D0_QUALIFIED | EXECUTION_ORCHESTRATOR |
| EVIDENCE_FIREWALL | EXECUTION_RAW_ARTIFACT_FIREWALL | EXECUTION_ORCHESTRATOR |
| EVIDENCE_GRAPH | HISTORICAL_READ_MODEL | EVIDENCE_FIREWALL |
| TERRARIO_LAB | FOUNDATION | THEORY_GRAPH, EXPERIMENT_COMPOSER, EVIDENCE_GRAPH |

## Niveles del mundo

| Nivel | Nombre | Estado |
| --- | --- | --- |
| D0 | differences | IMPLEMENTED_LEGACY |
| D1 | objects_and_persistence | IMPLEMENTED_LEGACY |
| D2 | properties_and_binding | IMPLEMENTED_STUDIO |
| D3 | causality | IMPLEMENTED |
| D4 | adaptation | IMPLEMENTED_PROTOCOL_NOT_CONFIRMED |
| D5 | tools_and_composition | FUTURE_DESIGN |
| D6 | planning | FUTURE_DESIGN |
| D7 | uncertainty_and_exploration | FUTURE_DESIGN |
| D8 | signs_and_semantics | FUTURE_DESIGN |
| D9 | social_world | FUTURE_DESIGN |
| D10 | inheritance_and_lineage | FUTURE_DESIGN |
| D11 | cumulative_culture | FUTURE_DESIGN |

## Conteos del snapshot

| Medida | Valor |
| --- | --- |
| sources | 44 |
| claims | 189 |
| raw concepts | 283 |
| canonical candidates | 224 |
| relations | 206 |
| hyperedges | 8 |
| theory nodes | 1035 |
| theory edges | 956 |
| evidence nodes | 141 |
| evidence edges | 136 |

## Invariantes científicos

- source claim != our claim
- raw concept != canonical concept
- association != causation
- hyperedge candidate != demonstrated mechanism
- hypothesis != evidence
- sandbox run != scientific evidence
- experimental support != universal truth
