#!/usr/bin/env python
"""G1 — la cartografía es una caché invalidable, no unas notas que envejecen solas.

El fallo que este gate previene es de ORDEN, no de ignorancia: construir sobre
código que no se ha leído. Costó tres resultados. El examen de P1 entregaba el
canal causal en el índice 0 cuando el runtime lo entrega en el 1; el efecto del
«modelo del mundo» y el del «planificador» resultaron ser la misma rama; toda la
línea experimental corrió sobre la ruta no autoritativa. Las tres cosas eran
legibles antes de escribir una línea de experimento.

Un documento no puede decir por sí solo si sigue siendo cierto. Un hash sí. Este
comprobador recalcula el sha256 de cada fichero que la cartografía cita y lo
compara con el que tenía cuando se escribió esa sección. Si difiere, la sección
queda STALE y no se construye sobre ella hasta releerla.

La lista de ficheros por sección NO se mantiene a mano: se deriva del propio
documento, que ya cita `fichero:línea` en todas partes. Así una sección nueva
queda cubierta por el hecho de estar escrita, y una que deje de citar un fichero
deja de vigilarlo. Un manifiesto mantenido aparte se desincroniza del texto que
describe, que es exactamente el fallo que este gate existe para impedir.

    python scripts/cartografia_check.py            comprueba; sale != 0 si hay algo obsoleto
    python scripts/cartografia_check.py --write    regenera el manifiesto tras releer
    python scripts/cartografia_check.py --section "IX"   limita el alcance
    python scripts/cartografia_check.py --tarea paridad-runtime
                                        filtra la lista de lectura con el registro negativo

Con `--tarea`, el gate deja de ser sólo una alarma y pasa a devolver una lista de
lectura ya filtrada: qué envejeció, menos lo que ya se aprendió que no sirve para
esa clase de tarea. Un gate que nombra cuarenta ficheros es un gate que se
ignora.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.lab.characterization import file_sha256

sys.path.insert(0, str(Path(__file__).resolve().parent))
from registro_negativo import BYTES_POR_TOKEN, veredicto  # noqa: E402

SCHEMA = "terrario.docs.cartography-manifest/v1"
CARTOGRAPHY = PROJECT_ROOT / "docs" / "CARTOGRAFIA_TERRARIO_01.md"
MANIFEST = PROJECT_ROOT / "docs" / "CARTOGRAFIA_MANIFIESTO.json"

#: Sólo se vigilan rutas del árbol real. Un fichero citado que no existe se
#: reporta aparte: puede ser una cita equivocada o un fichero borrado, y ambas
#: cosas invalidan la sección igual que un hash movido.
#:
#: `theory_snapshots/`, `docs/handoff/` y `.csv` entraron el 2026-09-21. Sin
#: ellos el corpus era invisible para este guardián por construcción: creció de
#: 42 a 101 PDFs y ninguna sección quedó obsoleta. El resto de `docs/` sigue
#: fuera a propósito --la cartografía vive ahí y se vigilaría a sí misma--.
REFERENCE = re.compile(
    r"\b((?:terrario|tests|scripts|scenarios|configs|knowledge"
    r"|theory_snapshots|docs/handoff)/[\w./ -]*?[\w.-]+"
    r"\.(?:py|yaml|yml|json|md|csv))"
)


def sections(text: str) -> dict[str, str]:
    """El documento partido por sus encabezados de primer nivel."""
    found: dict[str, str] = {}
    current = "(preámbulo)"
    body: list[str] = []
    for line in text.splitlines():
        if line.startswith("# "):
            found[current] = "\n".join(body)
            current = line[2:].strip()
            body = []
        else:
            body.append(line)
    found[current] = "\n".join(body)
    return found


def referenced(body: str) -> set[str]:
    """Las rutas que una sección cita, sin el sufijo `:línea`."""
    return {match.rstrip("/") for match in REFERENCE.findall(body)}


def head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=PROJECT_ROOT, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def survey() -> dict[str, dict[str, str]]:
    """Estado actual: por sección, el hash de cada fichero que cita."""
    text = CARTOGRAPHY.read_text(encoding="utf-8")
    state: dict[str, dict[str, str]] = {}
    for title, body in sections(text).items():
        paths = referenced(body)
        if not paths:
            continue
        hashes: dict[str, str] = {}
        for relative in sorted(paths):
            path = PROJECT_ROOT / relative
            hashes[relative] = file_sha256(path) if path.is_file() else "ABSENT"
        state[title] = hashes
    return state


def write_manifest() -> int:
    state = survey()
    MANIFEST.write_text(json.dumps({
        "schema_version": SCHEMA,
        "document": "docs/CARTOGRAFIA_TERRARIO_01.md",
        "written_at": date.today().isoformat(),
        "head": head(),
        "sections": {title: {"files": files} for title, files in state.items()},
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    covered = sum(len(files) for files in state.values())
    print(f"manifiesto escrito: {len(state)} secciones, {covered} ficheros vigilados")
    return 0


def check(only: str | None, tarea: str | None = None) -> int:
    if not MANIFEST.is_file():
        print(f"no hay manifiesto: {MANIFEST.relative_to(PROJECT_ROOT)}")
        print("ejecuta --write tras leer el código que la cartografía describe")
        return 2

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    recorded = {title: entry["files"] for title, entry in manifest["sections"].items()}
    current = survey()

    # G1 dice qué envejeció; el registro negativo dice qué de eso no vale la pena
    # abrir para ESTA clase de tarea. Unidos, lo que sale no es «lee estas
    # secciones» sino una lista de lectura ya filtrada — que es lo único que hace
    # accionable un mapa: sin filtro, un gate que nombra cuarenta ficheros es un
    # gate que se ignora.
    stale: dict[str, list[str]] = {}
    descartes: list[tuple[str, str, int]] = []
    for title, files in current.items():
        if only and only.lower() not in title.lower():
            continue
        was = recorded.get(title)
        if was is None:
            stale[title] = ["sección nueva, sin hashes registrados"]
            continue
        reasons = []
        for relative, digest in sorted(files.items()):
            before = was.get(relative)
            if before is None:
                motivo = f"cita nueva: {relative}"
            elif digest == "ABSENT":
                motivo = f"ya no existe: {relative}"
            elif digest != before:
                motivo = f"cambió: {relative}"
            else:
                continue
            if tarea:
                descartado, porque, bytes_ = veredicto(relative, tarea)
                if descartado:
                    descartes.append((relative, porque, bytes_))
                    reasons.append(f"{motivo}  —  DESCARTADO: {porque}")
                    continue
            reasons.append(motivo)
        for relative in sorted(set(was) - set(files)):
            reasons.append(f"dejó de citarse: {relative}")
        if reasons:
            stale[title] = reasons

    scope = f" (sección ~ {only!r})" if only else ""
    if not stale:
        vigilados = sum(len(f) for t, f in current.items()
                        if not only or only.lower() in t.lower())
        print(f"cartografía al día{scope}: {vigilados} ficheros vigilados")
        return 0

    print(f"CARTOGRAFÍA OBSOLETA{scope} — {len(stale)} sección(es):\n")
    for title, reasons in stale.items():
        print(f"  {title}")
        for reason in reasons:
            print(f"      {reason}")
        print()
    if descartes:
        evitados = sum(b for _, _, b in descartes) // BYTES_POR_TOKEN
        unicos = {ruta for ruta, _, _ in descartes}
        print(f"  {len(unicos)} fichero(s) descartado(s) para «{tarea}»: "
              f"hasta ~{evitados} tokens que no hace falta releer.")
        print("  Si alguno resulta que sí hacía falta:")
        print(f"      python scripts/registro_negativo.py falso-descarte <ruta> {tarea}\n")
    print("G1: léelas antes de construir sobre ellas, reescríbelas y corre --write.")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true",
                        help="regenera el manifiesto (sólo tras releer el código)")
    parser.add_argument("--section", default=None,
                        help="limita la comprobación a las secciones que contengan este texto")
    parser.add_argument("--tarea", default=None,
                        help="clase de tarea; filtra la lista de lectura con el registro negativo")
    args = parser.parse_args()
    return write_manifest() if args.write else check(args.section, args.tarea)


if __name__ == "__main__":
    raise SystemExit(main())
