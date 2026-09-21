#!/usr/bin/env python3
"""Censo de orfandad · qué módulo no importa nadie, medido y no supuesto.

    python scripts/censo_orfandad.py <raíz> <paquetes separados por coma>
    python scripts/censo_orfandad.py . terrario

Distingue tres estados, y la distinción es la que importa:

    sin ningún importador     ni producción ni tests lo tocan
    sólo importado por tests  construido, probado, sin consumidor
    vivo                      alguien fuera de tests lo usa

**Lo que costó que dijera la verdad.** Cuatro versiones publicaban un censo
falso con total aplomo, y cada punto ciego era un idioma normal de Python:

    1. contar `__init__.py` como destino     → paquetes enteros «huérfanos»
    2. ignorar `from paquete import modulo`  → `instrument_registry` huérfano
                                               cuando `evidence_admission` lo importa
    3. excluir `__init__.py` como IMPORTADOR → A0–A5 «huérfanos», y la factoría
                                               que los crea vive precisamente ahí
    4. no resolver reexportaciones           → `from runtime.life import LifeKernel`
                                               no alcanzaba `runtime.life.kernel`:
                                               el lazo de vida entero salía «sólo tests»

Ninguna versión fallaba: todas respondían. Por eso el guion lleva esta lista.
"""
import ast, sys, pathlib, collections

raiz = pathlib.Path(sys.argv[1]); paquetes = sys.argv[2].split(",")
mods = {}
for p in paquetes:
    for f in (raiz/p).rglob("*.py"):
        if "__pycache__" in f.parts or "/archive/" in str(f): continue
        mods[str(f.relative_to(raiz)).removesuffix(".py").replace("/", ".")] = f

# Reexportaciones: `from runtime.life import LifeKernel` alcanza
# `runtime.life.kernel` porque el `__init__` lo reexporta. Sin resolverlo, el
# idioma más común de Python hace parecer huérfano a medio árbol.
reexport = {}   # "paquete.Nombre" -> "paquete.modulo"
for nombre, f in mods.items():
    if f.name != "__init__.py": continue
    paquete = nombre.removesuffix(".__init__")
    try: arbol = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError: continue
    for n in ast.walk(arbol):
        if isinstance(n, ast.ImportFrom) and n.level == 1 and n.module:
            for a in n.names:
                reexport[f"{paquete}.{a.asname or a.name}"] = f"{paquete}.{n.module}"

importadores = collections.defaultdict(set)
# Importadores: los propios módulos, los tests, los scripts y los entrypoints
# de la raíz. Sin estos últimos el lazo de vida parece importado sólo por tests.
extra = [f for d in ("tests", "scripts") if (raiz/d).is_dir() for f in (raiz/d).rglob("*.py")]
extra += [f for f in raiz.glob("*.py")]
todos = list(mods.items()) + [(("tests." if "tests" in f.parts else "") +
                               str(f.relative_to(raiz)).removesuffix(".py").replace("/", "."), f)
                              for f in extra if "__pycache__" not in f.parts]
for nombre, f in todos:
    try: arbol = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError: continue
    for n in ast.walk(arbol):
        destinos = []
        if isinstance(n, ast.Import): destinos = [a.name for a in n.names]
        elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
            # `from paquete import modulo` importa el MÓDULO, no sólo el paquete.
            destinos = [n.module] + [f"{n.module}.{a.name}" for a in n.names]
        destinos = [reexport.get(d, d) for d in destinos]
        for d in destinos:
            for cand in mods:
                if d == cand or d.startswith(cand + "."): importadores[cand].add(nombre)

# Un `__init__.py` se importa al importar su paquete, nunca por su nombre
# completo, así que nunca aparece como destino: excluirlo del INFORME. Pero
# sigue contando como IMPORTADOR — la factoría de agentes vive en uno, y sin
# él A0–A5 parecerían huérfanos.
huerfanos, solo_tests = [], []
for m, f in sorted(mods.items()):
    if f.name == "__init__.py": continue
    quien = {x for x in importadores[m] if x != m}
    externos = {x for x in quien if not x.startswith("tests")}
    lineas = len(f.read_text(encoding="utf-8", errors="replace").splitlines())
    if not quien: huerfanos.append((lineas, m))
    elif not externos: solo_tests.append((lineas, m))

def tabla(t, xs):
    tot = sum(l for l, _ in xs)
    print(f"\n{t}: {len(xs)} módulos · {tot} líneas")
    for l, m in sorted(xs, reverse=True)[:12]: print(f"   {l:>5}  {m}")

print(f"== {raiz.name} · {len(mods)} módulos en {paquetes}")
tabla("SIN NINGÚN IMPORTADOR (ni tests)", huerfanos)
tabla("SÓLO IMPORTADOS POR TESTS", solo_tests)
