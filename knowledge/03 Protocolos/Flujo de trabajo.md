---
kind: operating-protocol
---

# Flujo de trabajo

## Regla de una pantalla

Antes de investigar, consulta [[knowledge/_generated/Estado tecnico|Estado técnico]], [[knowledge/01 Roadmap/Ruta activa|Ruta activa]] y el último ítem pertinente en [[knowledge/00 Control/Registro de decisiones|Registro de decisiones]]. Es suficiente para orientar el trabajo corriente; abre código o documentación especializada únicamente para el cambio seleccionado.

## Actualizar estado técnico

Cuando cambie el manifiesto, el snapshot activo o sus conteos:

```bash
./.venv/bin/python scripts/sync_obsidian_vault.py --write
./.venv/bin/python scripts/sync_obsidian_vault.py --check
```

`--check` no modifica archivos y falla si el dashboard no coincide exactamente con la fuente técnica.

## Clasificar antes de actuar

| Tipo | Dónde se registra | Regla |
| --- | --- | --- |
| Prioridad, criterio humano, autorización | [[knowledge/00 Control/Registro de decisiones]] | Append-only; enlaza evidencia. |
| Estado técnico, dependencia, bloqueo | `project_manifest.json` | Regenerar dashboard. |
| Resultado experimental | Artefacto/versionado del Lab | Nunca resumirlo como evidencia nueva en una nota. |
| Hipótesis o interpretación | Revisión/snapshot correspondiente | No promocionar desde una nota. |

## Cierre de cambio

1. Ejecuta las pruebas pertinentes.
2. Si el manifiesto cambió, sincroniza y verifica el dashboard.
3. Actualiza o añade la decisión humana si cambió alcance, riesgo o autorización.
4. Enlaza el archivo/artefacto concreto desde la nota de trabajo; evita copiarlo.
