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

## ADR-001 — Variedad dinámica

- **Estado:** PROPOSED — requiere firma humana
- **Fecha:** 2026-09-16
- **Decisión:** nada relevante se supone estático salvo que un experimento lo congele deliberadamente como control declarado. `E, 𝒱, D, R` pasan a `Eₜ, 𝒱ₜ, Dₜ, Rₜ`, con seis clases de variedad y `VARIEDAD Y CAMBIO` como eje transversal de los 64 bloques.
- **Consecuencia:** cae sobre `viability-recovery-profile` antes de su firma. Introduce una tercera causa de `recovery_steps = None` —recuperación dentro de una región viable distinta— que hoy se informaría como fracaso.
- **Evidencia:** [[ADR-001 Variedad dinamica|el ADR completo]] y [docs/CORPUS_A_ALGORITMO_01.md](../../docs/CORPUS_A_ALGORITMO_01.md).

## Nueva decisión

Duplica [[knowledge/90 Recursos/Plantillas/Decisión|la plantilla de decisión]] en esta carpeta y enlázala desde aquí. No borres entradas: márcalas `SUPERSEDED` y enlaza la decisión que las reemplaza.
