"""Aserciones que no pueden fallar, y guardianes que leen texto.

Dos familias, las dos con instancias reales en este repositorio:

**Vacuidad.** «Escribí una aserción vacua: `assert sin_asignar == sin_asignar`
en el contrato de `BINDING_NOT_NECESSARY`; compara una lista consigo misma y no
puede fallar» --informe 1.4, §7--. Y en el oráculo de 1.4: «el gate de orden es
invacuable con `frozenset`: dos conjuntos con los mismos elementos son iguales
por construcción». Un contrato cuyo único comportamiento posible es aprobar no
es un contrato; es documentación con `assert`.

**Guardián textual.** «Escanear texto hace que un guardián cace su propia
documentación: la cabecera que explica qué semillas están contaminadas las
nombra, y un `str(s) in fuente` las encuentra ahí. Ya ocurrió dos veces hoy»
--`test_level11_lineage.py`--. Un contrato estructural se comprueba sobre el
árbol sintáctico, donde los comentarios no son nodos.

Ninguna de las dos es una heurística de estilo: las dos describen aserciones
cuyo resultado es independiente del sistema que dicen medir.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

LECTORES = ("read_text", "read")


def _contiene_llamada(nodo: ast.expr) -> bool:
    """`f(x) == f(x)` no es una tautología: puede medir determinismo.

    `adaptive_fingerprint(agent()) == adaptive_fingerprint(agent())` construye
    dos organismos distintos y exige que den la misma huella; eso sí puede
    fallar. `sin_asignar == sin_asignar` no. La diferencia decidible es si hay
    una llamada de por medio, y en la duda este comprobador calla: un linter
    con más ruido que señal se apaga, y entonces no comprueba nada.
    """
    return any(isinstance(n, ast.Call) for n in ast.walk(nodo))


def _menciona_python(fn: ast.AST) -> bool:
    """¿El ámbito lee ficheros `.py`?

    La prohibición del proyecto es concreta: un contrato **estructural sobre
    fuente Python** no se comprueba por texto, porque caza su propia
    documentación. Un contrato sobre el HTML o el JS servidos sí tiene que leer
    texto --no hay árbol sintáctico de Python que mirar-- y no se señala.
    """
    for nodo in ast.walk(fn):
        if isinstance(nodo, ast.Constant) and isinstance(nodo.value, str):
            if nodo.value.endswith(".py") or "*.py" in nodo.value:
                return True
    return False


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    #: `self_comparison` y `constant` son ciertos: la aserción no puede fallar.
    #: `self_comparison_call` es informativo --suele ser una prueba de
    #: determinismo-- y no se muestra salvo que se pidan todos.
    kind: str
    code: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line} · {self.kind} · {self.code}"


def _igual(a: ast.expr, b: ast.expr) -> bool:
    """Misma expresión escrita dos veces, sin mirar posiciones."""
    return ast.dump(a, annotate_fields=True, include_attributes=False) == \
        ast.dump(b, annotate_fields=True, include_attributes=False)


def _vacio(nodo: ast.expr) -> bool:
    if isinstance(nodo, (ast.List, ast.Tuple, ast.Set)):
        return not nodo.elts
    if isinstance(nodo, ast.Dict):
        return not nodo.keys
    if isinstance(nodo, ast.Constant) and isinstance(nodo.value, (str, bytes)):
        return not nodo.value
    return False


def _fuentes_textuales(fn: ast.AST) -> set[str]:
    """Nombres que dentro de esta función guardan el texto de un fichero."""
    nombres: set[str] = set()
    for nodo in ast.walk(fn):
        if isinstance(nodo, ast.Assign) and isinstance(nodo.value, ast.Call):
            f = nodo.value.func
            if isinstance(f, ast.Attribute) and f.attr in LECTORES:
                for destino in nodo.targets:
                    if isinstance(destino, ast.Name):
                        nombres.add(destino.id)
    return nombres


def _es_texto_de_fuente(nodo: ast.expr, nombres: set[str]) -> bool:
    if isinstance(nodo, ast.Name) and nodo.id in nombres:
        return True
    if isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Attribute):
        return nodo.func.attr in LECTORES
    return False


def scan_source(source: str, path: Path | str = "<memoria>") -> list[Finding]:
    arbol = ast.parse(source)
    lineas = source.splitlines()
    ruta = Path(path)
    hallazgos: list[Finding] = []

    def texto(nodo: ast.AST) -> str:
        bruto = lineas[nodo.lineno - 1].strip() if nodo.lineno <= len(lineas) else ""
        return bruto if len(bruto) <= 100 else bruto[:97] + "…"

    # Nombres con contenido de fichero, por función; fuera de función, global.
    ambito: dict[ast.AST, set[str]] = {arbol: _fuentes_textuales(arbol)}
    for nodo in ast.walk(arbol):
        if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
            ambito[nodo] = _fuentes_textuales(nodo) | ambito[arbol]

    def envolvente(nodo: ast.AST) -> ast.AST:
        for fn in ambito:
            if fn is arbol:
                continue
            if any(n is nodo for n in ast.walk(fn)):
                return fn
        return arbol

    def contenedor(nodo: ast.AST) -> set[str]:
        return ambito[envolvente(nodo)]

    for nodo in ast.walk(arbol):
        if not isinstance(nodo, ast.Assert):
            continue
        prueba = nodo.test
        objetivos = [prueba]
        if isinstance(prueba, ast.UnaryOp) and isinstance(prueba.op, ast.Not):
            objetivos.append(prueba.operand)
        if isinstance(prueba, ast.BoolOp):
            objetivos.extend(prueba.values)

        for t in objetivos:
            if isinstance(t, ast.Compare) and len(t.ops) == 1:
                izq, der = t.left, t.comparators[0]
                if _igual(izq, der):
                    clase = ("self_comparison_call" if _contiene_llamada(izq)
                             else "self_comparison")
                    hallazgos.append(Finding(ruta, nodo.lineno, clase, texto(nodo)))
                elif isinstance(t.ops[0], (ast.In, ast.NotIn)) and \
                        _es_texto_de_fuente(der, contenedor(nodo)) and \
                        _menciona_python(envolvente(nodo)):
                    hallazgos.append(Finding(ruta, nodo.lineno,
                                             "source_grep", texto(nodo)))
            elif isinstance(t, ast.Constant) and t is prueba:
                if bool(t.value):
                    hallazgos.append(Finding(ruta, nodo.lineno,
                                             "constant", texto(nodo)))
            elif isinstance(t, ast.Call) and isinstance(t.func, ast.Name) \
                    and t.func.id in ("all", "any") and t.args:
                arg = t.args[0]
                if isinstance(arg, (ast.GeneratorExp, ast.ListComp)) and \
                        len(arg.generators) == 1 and _vacio(arg.generators[0].iter) \
                        and t.func.id == "all":
                    hallazgos.append(Finding(ruta, nodo.lineno,
                                             "empty_quantifier", texto(nodo)))
    return hallazgos


#: Lo que no puede fallar nunca. El resto es informativo.
CIERTOS = ("self_comparison", "constant", "empty_quantifier", "source_grep")


def scan(path: Path | str, *, todos: bool = False) -> list[Finding]:
    """Un fichero, o todos los `.py` de un directorio."""
    p = Path(path)
    ficheros = sorted(p.rglob("*.py")) if p.is_dir() else [p]
    hallazgos: list[Finding] = []
    for f in ficheros:
        if "__pycache__" in f.parts:
            continue
        try:
            hallazgos.extend(scan_source(f.read_text(encoding="utf-8"), f))
        except SyntaxError:
            continue
    return hallazgos if todos else [f for f in hallazgos if f.kind in CIERTOS]
