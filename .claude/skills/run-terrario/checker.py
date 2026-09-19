#!/usr/bin/env python3
"""Comprobador · verifica lo que un informe afirma sobre el linaje de agentes.

El objeto son los **Agentes de Nivel 1, 2, … n**: código nuevo. Lo anterior
--los organismos con nombre de índice, sus mundos y sus instrumentos-- es
documentación histórica y no se toca.

Existe porque los informes de este proyecto se han equivocado, repetidamente, de
una sola manera: **afirmar sobre el código sin ejecutarlo.** Cada subcomando
impide una de esas formas, y todas ocurrieron de verdad:

    params      citar los valores del constructor cuando el experimento los
                sobrescribe, y describir así un organismo distinto del medido
    consumers   decir que una señal llega a la conducta, o que no llega, sin
                separar lo que decide de lo que sólo aparece en una traza
    passivity   una sonda que inserta la celda que lee: medir cambiaba al ser
    suite       repetir «N fallos preexistentes, ninguno nuevo» hasta que el
                rojo deja de leerse
    level1      dar por bueno un gate que sólo podía aprobar por vacío

Uso, desde la raíz del repositorio:

    python .claude/skills/run-terrario/checker.py params
    python .claude/skills/run-terrario/checker.py consumers predict
    python .claude/skills/run-terrario/checker.py passivity
    python .claude/skills/run-terrario/checker.py suite
    python .claude/skills/run-terrario/checker.py level1 --semillas 4
    python .claude/skills/run-terrario/checker.py all --semillas 4

Código de salida 0 si todo lo comprobado se sostiene, 1 si algo no.
"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

BASELINE = Path(__file__).resolve().parent / "suite_baseline.json"
OK, BAD = "  ok   ", "  FALLA"


# --- config -------------------------------------------------------------------

def cmd_params(_args) -> int:
    """Los parámetros EFECTIVOS del experimento, no los de la firma.

    `Experiment` es un dataclass congelado con valores por defecto, y el guion
    lo construye sobrescribiendo algunos. Citar los de la firma describe una
    corrida que no ocurrió -- que es exactamente el error que se cometió con el
    organismo histórico, donde el constructor decía 128 y lo medido usaba 16.
    """
    import dataclasses

    from terrario.level1.measurement import Experiment
    from terrario.level1.world import ALL_OBSERVATIONS, Direction

    defaults = Experiment()
    print("AGENTE DE NIVEL 1 · parámetros efectivos del experimento\n")
    print(f"  {'parámetro':<28}{'valor':>12}")
    print("  " + "-" * 40)
    for field in dataclasses.fields(defaults):
        print(f"  {field.name:<28}{str(getattr(defaults, field.name)):>12}")

    train = defaults.train_layouts * defaults.train_steps_per_layout
    cells = len(ALL_OBSERVATIONS) * len(Direction)
    print("\n  DERIVADO — esto es lo que hay que citar en un informe\n")
    print(f"    repertorio motor           {len(Direction)} direcciones")
    print(f"    espacio sensorial          {len(ALL_OBSERVATIONS)} situaciones "
          f"(2^{len(Direction)})")
    print(f"    celdas de una tabla        {cells} pares (situación, dirección)")
    print(f"    transiciones por semilla   {train}")
    print(f"    muestras por celda         ~{train // cells}")
    print("\n    Con el espacio sensorial cubierto entero, un gate de")
    print("    generalización sobre mundos nuevos NO puede fallar: hay que")
    print("    retirar situaciones del entrenamiento para que signifique algo.")
    return 0


# --- consumers ----------------------------------------------------------------

class _Parents(ast.NodeVisitor):
    def __init__(self) -> None:
        self.parent: dict[ast.AST, ast.AST] = {}

    def generic_visit(self, node: ast.AST) -> None:
        for child in ast.iter_child_nodes(node):
            self.parent[child] = node
        super().generic_visit(node)


def _enclosing_statement(parents: dict, node: ast.AST) -> ast.stmt | None:
    cur = node
    while cur is not None:
        if isinstance(cur, ast.stmt):
            return cur
        cur = parents.get(cur)
    return None


#: Funciones cuyo cuerpo entero es contabilidad: lo que devuelven se mira, no
#: se usa para decidir. Sin esto, un `return {...}` dentro de `get_state` parece
#: un consumidor causal -- y así fue como este comprobador falló su primera
#: ejecución, diciendo que `drive` tenía uno.
_BOOKKEEPING_FUNCTIONS = frozenset({
    "get_state", "get_trace", "get_trace_events", "to_dict", "describe",
    "summary", "__repr__", "__str__", "snapshot", "report",
})

_BOOKKEEPING_MARKS = ("_trace.append", "trace = {", "events.append",
                      "logger.", "print(")


def _is_bookkeeping(statement: ast.stmt, function_name: str | None) -> bool:
    """¿La aparición vive dentro de una traza, un log o un dict de estado?

    Un símbolo que sólo aparece ahí es un OBSERVABLE, no una causa. Ésa es
    exactamente la distinción que se falló al decir que la homeostasis regulaba
    conducta cuando lo único que hacía era aparecer en la traza.
    """
    if function_name in _BOOKKEEPING_FUNCTIONS:
        return True
    source = ast.unparse(statement)
    return any(mark in source for mark in _BOOKKEEPING_MARKS)


def _enclosing_function(parents: dict, node: ast.AST) -> str | None:
    cur = node
    while cur is not None:
        if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return cur.name
        cur = parents.get(cur)
    return None


def cmd_consumers(args) -> int:
    """Quién LEE un símbolo, separando causa de contabilidad. Con ast, no grep.

    Un grep cuenta apariciones; esto imprime la sentencia entera en la que cada
    aparición vive, que es lo único que distingue `temperature = 1 + bias` de
    `trace["bias"] = bias`.
    """
    symbol = args.symbol
    roots = [ROOT / (args.path or "terrario/level1")]
    causal, book = [], []

    for base in roots:
        for path in sorted(base.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            try:
                tree = ast.parse(path.read_text())
            except SyntaxError:
                continue
            parents = _Parents()
            parents.visit(tree)
            for node in ast.walk(tree):
                name = (node.attr if isinstance(node, ast.Attribute)
                        else node.id if isinstance(node, ast.Name) else None)
                if name != symbol:
                    continue
                statement = _enclosing_statement(parents.parent, node)
                if statement is None:
                    continue
                function = _enclosing_function(parents.parent, node)
                entry = (str(path.relative_to(ROOT)), node.lineno,
                         ast.unparse(statement).splitlines()[0][:96])
                (book if _is_bookkeeping(statement, function)
                 else causal).append(entry)

    print(f"CONSUMIDORES DE `{symbol}`\n")
    print(f"  CAUSALES ({len(causal)}) — llegan a un tensor, una decisión o un estado\n")
    for path, line, text in causal:
        print(f"    {path}:{line}\n        {text}")
    if not causal:
        print("    (ninguno)")
    print(f"\n  CONTABILIDAD ({len(book)}) — traza, log o dict de estado; "
          f"observables, no causas\n")
    for path, line, text in book:
        print(f"    {path}:{line}\n        {text}")
    if not book:
        print("    (ninguno)")
    print(f"\n  VEREDICTO · {'tiene consumidor causal' if causal else 'SIN CONSUMIDOR CAUSAL'}")
    return 0


# --- passivity ----------------------------------------------------------------

def cmd_passivity(_args) -> int:
    """Leer no puede cambiar lo leído.

    Este proyecto ya pagó dos veces por romperlo: una sonda que se contaminó e
    infló dos magnitudes ×18.6 y ×10, y un `predict` que insertaba la celda que
    consultaba. Lo segundo no cambiaba ningún número y aun así habría envenenado
    cualquier huella del estado adaptativo.
    """
    import numpy as np

    from terrario.level1.measurement import Experiment, motor_babbling
    from terrario.level1.models import ContingencyTable, FactoredContingency, TabularQ
    from terrario.level1.world import ALL_OBSERVATIONS, Direction

    cfg = Experiment(train_layouts=8, train_steps_per_layout=32)
    stream, violations = motor_babbling(cfg, 20260919)

    cases, features, td = ContingencyTable(), FactoredContingency(), TabularQ()
    for tr in stream:
        cases.observe(tr.observation, tr.direction, tr.moved)
        features.observe(tr.observation, tr.direction, tr.moved)
        td.observe(tr)

    before = (cases.visited_cells, features.visited_cells, len(td.q))
    rng = np.random.default_rng(1)
    for observation in ALL_OBSERVATIONS:
        for direction in Direction:
            cases.predict(observation, direction)
            features.predict(observation, direction)
        cases.act(observation, rng)
        features.act(observation, rng)
        td.act(observation, rng)
    after = (cases.visited_cells, features.visited_cells, len(td.q))

    failures = 0
    print("PASIVIDAD · ¿preguntar cambia al ser?\n")
    for label, b, a in zip(("aprende por casos", "aprende por rasgos",
                            "td (techo externo)"), before, after):
        good = b == a
        failures += not good
        print(f"{OK if good else BAD}  {label:<22} celdas {b} -> {a}")

    good = violations == 0
    failures += not good
    print(f"{OK if good else BAD}  contrato físico        "
          f"{violations} violaciones en {len(stream)} transiciones")
    return 1 if failures else 0


# --- suite --------------------------------------------------------------------

def _run_suite() -> set[str]:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q", "--no-header",
         "-p", "no:cacheprovider"],
        cwd=ROOT, capture_output=True, text=True, timeout=3600)
    # El orden importa: quitar el prefijo PRIMERO y partir después. Al revés
    # --partir por espacio y luego quitar el prefijo-- se queda con la palabra
    # "FAILED" para toda línea, y el registro aprueba pase lo que pase. Ocurrió.
    return {line.removeprefix("FAILED ").split(" ")[0].strip()
            for line in proc.stdout.splitlines() if line.startswith("FAILED ")}


def cmd_suite(args) -> int:
    """El conjunto de fallos, contra uno registrado. No un recuento.

    Decir «5 preexistentes, ninguno nuevo» cinco veces seguidas es cómo se
    ignora el rojo. Aquí un fallo nuevo Y uno que se arregló sin actualizar el
    registro salen los dos, porque los dos son información.
    """
    current = _run_suite()
    if args.record:
        BASELINE.write_text(json.dumps({"known_failures": sorted(current)},
                                       indent=2) + "\n")
        print(f"registrados {len(current)} fallos conocidos en {BASELINE.name}")
        return 0
    if not BASELINE.exists():
        print(f"no hay registro. Créalo con:  checker.py suite --record")
        return 1
    known = set(json.loads(BASELINE.read_text())["known_failures"])

    print(f"SUITE · {len(current)} fallos ahora, {len(known)} registrados\n")
    new, fixed = sorted(current - known), sorted(known - current)
    for name in new:
        print(f"{BAD}  NUEVO      {name}")
    for name in fixed:
        print(f"{BAD}  ARREGLADO  {name}   (actualiza el registro)")
    for name in sorted(current & known):
        print(f"  conocido   {name}")
    if not new and not fixed:
        print("\n  el conjunto de fallos no se movió")
        return 0
    return 1


# --- level1 -------------------------------------------------------------------

def cmd_level1(args) -> int:
    """El experimento del Agente de Nivel 1, de punta a punta."""
    proc = subprocess.run(
        [sys.executable, "-u", "scripts/level1_sensorimotor_contingency.py",
         "--semillas", str(args.semillas)],
        cwd=ROOT, capture_output=True, text=True, timeout=3600)
    print(proc.stdout)
    if "ESTADO · PASA" not in proc.stdout:
        print(proc.stderr[-2000:])
        return 1
    return 0


def cmd_all(args) -> int:
    failures = 0
    for name, fn in (("params", cmd_params), ("passivity", cmd_passivity),
                     ("suite", cmd_suite)):
        print("=" * 72)
        failures += fn(args)
        print()
    print("=" * 72)
    failures += cmd_level1(args)
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("params").set_defaults(fn=cmd_params)
    c = sub.add_parser("consumers")
    c.add_argument("symbol")
    c.add_argument("--path", default=None,
                   help="por defecto terrario/level1; pasar otra para el histórico")
    c.set_defaults(fn=cmd_consumers)
    sub.add_parser("passivity").set_defaults(fn=cmd_passivity)
    s = sub.add_parser("suite")
    s.add_argument("--record", action="store_true")
    s.set_defaults(fn=cmd_suite)
    lv = sub.add_parser("level1")
    lv.add_argument("--semillas", type=int, default=8)
    lv.set_defaults(fn=cmd_level1)
    a = sub.add_parser("all")
    a.add_argument("--semillas", type=int, default=4)
    a.add_argument("--record", action="store_true")
    a.set_defaults(fn=cmd_all)
    args = parser.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
