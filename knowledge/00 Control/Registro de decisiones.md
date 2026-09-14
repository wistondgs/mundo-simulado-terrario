---
kind: decision-log
---

# Registro de decisiones

Este registro es la fuente operativa de las decisiones humanas. No reescribe evidencia, snapshots ni manifiestos científicos.

## ADR-000 — Gobernanza del vault

- **Estado:** ACCEPTED
- **Fecha:** 2026-09-13
- **Decisión:** Obsidian se usa como interfaz operativa única para navegación, prioridades, bloqueos y decisiones. `project_manifest.json` y artefactos científicos conservan su autoridad técnica e inmutable.
- **Consecuencia:** el estado técnico se genera mediante `scripts/sync_obsidian_vault.py`; una divergencia se detecta con `--check`.
- **Evidencia:** [[knowledge/_generated/Estado tecnico|estado derivado]] y [project_manifest.json](../../project_manifest.json).

## Nueva decisión

Duplica [[knowledge/90 Recursos/Plantillas/Decisión|la plantilla de decisión]] en esta carpeta y enlázala desde aquí. No borres entradas: márcalas `SUPERSEDED` y enlaza la decisión que las reemplaza.
