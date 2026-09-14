#!/usr/bin/env python
"""Render and verify Terrario's generated Obsidian operational dashboard.

Human decisions live in ``knowledge/``.  This file only writes the derived
dashboard, whose authoritative inputs are project_manifest.json and the active
theory snapshot.  ``--check`` makes stale generated state visible in CI or
before a hand-off without modifying the worktree.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "project_manifest.json"
OUTPUT_PATH = ROOT / "knowledge" / "_generated" / "Estado tecnico.md"


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _table(rows: list[tuple[str, ...]], headers: tuple[str, ...]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return lines


def render(root: Path = ROOT) -> str:
    manifest_path = root / "project_manifest.json"
    project = _read_json(manifest_path)
    active = project["active_theory_snapshot"]
    summary_path = root / "theory_snapshots" / active["snapshot_id"] / "ingestion_summary.json"
    summary = _read_json(summary_path)
    manifest_digest = _digest(manifest_path)

    component_rows = [
        (item["id"], item["status"], ", ".join(item["depends_on"]) or "—")
        for item in project["components"]
    ]
    phase_rows = [
        (item["id"], item["status"], ", ".join(item["depends_on"]) or "—")
        for item in project["phases"]
    ]
    level_rows = [(item["id"], item["name"], item["status"]) for item in project["world_levels"]]
    blockers = "\n".join(f"- `{blocker}`" for blocker in project["active_blockers"])
    invariants = "\n".join(f"- {invariant}" for invariant in project["scientific_invariants"])
    counts = [(key.replace("_", " "), str(value)) for key, value in active["counts"].items()]

    lines = [
        "---",
        "kind: generated-status",
        f"generated_from: {manifest_path.relative_to(root).as_posix()}",
        f"manifest_sha256: {manifest_digest}",
        f"active_snapshot: {active['snapshot_id']}",
        "---",
        "",
        "# Estado técnico de Terrario",
        "",
        "> [!warning] Nota generada",
        "> No editar esta nota a mano. Ejecuta `./.venv/bin/python scripts/sync_obsidian_vault.py --write` tras un cambio deliberado de manifiesto. Comprueba vigencia con `--check`.",
        "",
        "[[knowledge/00 Control/Inicio|← Inicio]] · [[knowledge/00 Control/Registro de decisiones|Decisiones]] · [[knowledge/01 Roadmap/Ruta activa|Ruta activa]]",
        "",
        "## Fuente verificada",
        "",
        f"- Manifiesto: [{manifest_path.name}](../../{manifest_path.name}) (`{manifest_digest}`)",
        f"- Snapshot activo: `{active['snapshot_id']}` (`{active['snapshot_hash']}`)",
        f"- Resumen de ingestión: [{summary_path.name}](../../{summary_path.relative_to(root).as_posix()})",
        f"- Conteo de fuentes confirmado: `{summary['sources']}`",
        "",
        "## Bloqueos activos",
        "",
        blockers,
        "",
        "## Fases",
        "",
        *_table(phase_rows, ("Fase", "Estado", "Depende de")),
        "",
        "## Componentes",
        "",
        *_table(component_rows, ("Componente", "Estado", "Depende de")),
        "",
        "## Niveles del mundo",
        "",
        *_table(level_rows, ("Nivel", "Nombre", "Estado")),
        "",
        "## Conteos del snapshot",
        "",
        *_table(counts, ("Medida", "Valor")),
        "",
        "## Invariantes científicos",
        "",
        invariants,
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="regenera la nota derivada")
    mode.add_argument("--check", action="store_true", help="falla si la nota derivada está ausente o vencida")
    args = parser.parse_args()

    expected = render()
    if args.check:
        actual = OUTPUT_PATH.read_text(encoding="utf-8") if OUTPUT_PATH.is_file() else None
        if actual != expected:
            print("Obsidian dashboard is stale. Run: ./.venv/bin/python scripts/sync_obsidian_vault.py --write", file=sys.stderr)
            return 1
        print("Obsidian dashboard is current.")
        return 0

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(expected, encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
