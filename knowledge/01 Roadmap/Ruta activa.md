---
kind: roadmap
---

# Ruta activa

La ruta se deriva de las dependencias declaradas en [[knowledge/_generated/Estado tecnico|Estado técnico]]. Este documento evita convertir documentación histórica en una lista de tareas activa.

## Ahora

1. Resolver la QA de navegador de `PREREGISTRATION-CORE-01`; está bloqueada por disponibilidad del runner, no por un cambio científico pendiente.
2. Mantener separadas las decisiones que exigen revisión humana de las tareas técnicas. La autorización de piloto no se infiere de una prueba que pase.
3. Tras cerrar la QA, continuar por `REGISTRY-HARDENING-01` → `INTERACTION-KERNEL-01` → `DEVICE-RUNTIME-01`.

## Carriles bloqueados

- `GPU-RECOVERY-01` depende de una condición del sistema operativo/CUDA; no debe simularse ni rebajarse silenciosamente a CPU.
- `SCIENTIFIC-PILOT-01` exige autorización humana; no se desbloquea por implementación o automatización.

## Regla de actualización

Los cambios de estado se hacen primero donde sean técnicamente ciertos (`project_manifest.json` y la evidencia que corresponda) y luego se regenera [[knowledge/_generated/Estado tecnico|Estado técnico]]. Las decisiones de priorización y los motivos humanos se registran en [[knowledge/00 Control/Registro de decisiones|Registro de decisiones]].
