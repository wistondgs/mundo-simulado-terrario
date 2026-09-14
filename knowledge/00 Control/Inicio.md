---
kind: operational-home
---

# Terrario — centro operativo

Esta es la puerta de entrada del proyecto en Obsidian. Aquí se decide y se sigue el trabajo sin volver a recorrer todo el repositorio.

> [!important] Qué es verdad aquí
> - La **verdad operativa humana** son esta nota, el [[knowledge/00 Control/Registro de decisiones|Registro de decisiones]] y las notas de trabajo enlazadas.
> - La **verdad técnica verificable** sigue siendo `project_manifest.json`, los snapshots versionados y los artefactos inmutables. [[knowledge/_generated/Estado tecnico|Estado técnico]] se deriva de ellos; no los reemplaza ni puede alterar su significado científico.

## Navegación

- [[knowledge/_generated/Estado tecnico|Estado técnico actual]] — fases, dependencias, bloqueos y cobertura del snapshot, generado y verificable.
- [[knowledge/01 Roadmap/Ruta activa|Ruta activa]] — secuencia mínima para avanzar sin reauditar.
- [[knowledge/00 Control/Registro de decisiones|Registro de decisiones]] — decisiones humanas, reversibles o no, con su evidencia.
- [[knowledge/02 Arquitectura/Mapa del sistema|Mapa del sistema]] — límites de dominio y puntos de entrada.
- [[knowledge/02 Arquitectura/Informe de estado verificable 2026-09-14|Informe verificable del sistema]] — arquitectura, capacidades, Fork Core, límites y trabajo pendiente a `f105eb2`.
- [[knowledge/03 Protocolos/Flujo de trabajo|Flujo de trabajo]] — cómo mantener este vault como interfaz de control.

## Ritual de inicio

1. Abre [[knowledge/_generated/Estado tecnico|Estado técnico actual]].
2. Elige el siguiente ítem no bloqueado de [[knowledge/01 Roadmap/Ruta activa|Ruta activa]].
3. Registra una decisión antes de cambiar una frontera científica, protocolo o fase.
4. Al cambiar `project_manifest.json`, ejecuta:

```bash
./.venv/bin/python scripts/sync_obsidian_vault.py --write
./.venv/bin/python scripts/sync_obsidian_vault.py --check
```

## Acceso en Obsidian

Abre esta carpeta raíz (`mundo simulado terrario`) como vault. La configuración compartible está en `.obsidian/`; el layout personal queda ignorado por Git.
