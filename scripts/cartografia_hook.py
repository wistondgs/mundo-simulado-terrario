#!/usr/bin/env python3
"""El gate G1, disparado por el arnés en vez de por acordarse.

`cartografia_check.py` ya sabía decir qué secciones envejecieron. El problema
nunca fue el comprobador: era que había que acordarse de ejecutarlo, y el fallo
que G1 previene --construir sobre código que no se ha leído-- ocurre
precisamente cuando uno no se acuerda. Esto lo ata a dos momentos del arnés:

    --sesion    al abrir sesión: ejecuta el gate real y mete su veredicto en el
                contexto. Cuesta ~1,8 s una vez.
    --edicion   después de cada Edit/Write: mira SÓLO el manifiesto y avisa si
                el fichero que se acaba de tocar está citado por alguna sección.
                Milisegundos, sin importar `terrario`, sin tocar disco de más.

La autoridad sigue siendo `cartografia_check.py`. Este guion no decide nada por
su cuenta: en `--sesion` reenvía lo que diga el gate, y en `--edicion` sólo
nombra la sección que acaba de quedar obsoleta y remite al gate.

Nunca falla la sesión: cualquier excepción sale como silencio y código 0. Un
hook que rompe el turno se desactiva, y entonces no comprueba nada.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
MANIFIESTO = RAIZ / "docs" / "CARTOGRAFIA_MANIFIESTO.json"
GATE = RAIZ / "scripts" / "cartografia_check.py"
PYTHON = RAIZ / ".venv" / "bin" / "python"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for bloque in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def _emite(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False))
    return 0


def sesion() -> int:
    """El veredicto del gate real, al contexto del modelo."""
    if not (PYTHON.is_file() and GATE.is_file()):
        return 0
    salida = subprocess.run([str(PYTHON), str(GATE)], cwd=RAIZ,
                            capture_output=True, text=True, timeout=120)
    texto = (salida.stdout or "").strip()
    if not texto:
        return 0
    if salida.returncode == 0:
        contexto = (f"Cartografía (G1): {texto}. El mapa está al día; "
                    "`docs/CARTOGRAFIA_TERRARIO_01.md` puede citarse sin releer.")
    else:
        contexto = (
            "Cartografía (G1) OBSOLETA. No construyas sobre las secciones de "
            "`docs/CARTOGRAFIA_TERRARIO_01.md` que salen abajo sin releer antes "
            "el código que citan; después reescríbelas y corre "
            "`python scripts/cartografia_check.py --write`.\n\n" + texto)
    return _emite({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": contexto,
        },
        "suppressOutput": True,
    })


def edicion() -> int:
    """¿El fichero recién tocado invalida alguna sección? Sólo el manifiesto."""
    try:
        evento = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return 0
    bruto = (evento.get("tool_response") or {}).get("filePath") \
        or (evento.get("tool_input") or {}).get("file_path")
    if not bruto or not MANIFIESTO.is_file():
        return 0

    try:
        relativa = Path(bruto).resolve().relative_to(RAIZ).as_posix()
    except ValueError:
        return 0                      # fuera del repositorio: no es asunto suyo

    manifiesto = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
    afectadas = []
    for titulo, entrada in manifiesto["sections"].items():
        registrado = entrada["files"].get(relativa)
        if registrado is None:
            continue
        destino = RAIZ / relativa
        ahora = _sha256(destino) if destino.is_file() else "ABSENT"
        if ahora != registrado:
            afectadas.append(titulo)

    if not afectadas:
        return 0

    listado = "\n".join(f"  · {t}" for t in afectadas)
    return _emite({
        "systemMessage": (
            f"Cartografía: `{relativa}` deja obsoleta(s) "
            f"{len(afectadas)} sección(es).\n{listado}\n"
            "Reescríbelas y corre `python scripts/cartografia_check.py --write`."),
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": (
                f"La cartografía cita `{relativa}`, que acabas de modificar. "
                f"Queda(n) obsoleta(s):\n{listado}\n"
                "Si el cambio altera lo que esas secciones afirman, corrígelas "
                "antes de cerrar y regenera el manifiesto con "
                "`python scripts/cartografia_check.py --write`."),
        },
    })


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    grupo = ap.add_mutually_exclusive_group(required=True)
    grupo.add_argument("--sesion", action="store_true")
    grupo.add_argument("--edicion", action="store_true")
    args = ap.parse_args()
    try:
        return sesion() if args.sesion else edicion()
    except Exception:                 # noqa: BLE001 — ver la cabecera
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
