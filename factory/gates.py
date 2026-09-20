"""Reconciliación del inventario de gates · sellado contra ejecutado.

El defecto que origina esto ocurrió en 1.4 y se reparó en `68d852d`: el guion
evaluaba **siete** gates donde el preregistro sellaba **once**, y además usaba
`L14-11` para las sondas cuando el preregistro le asigna ese número a la
pasividad. Los cinco que faltaban estaban verificados --en contratos-- pero el
informe de ejecución dejaba dos taxonomías para el mismo experimento, y quien
leyera después heredaba la equivocada.

Nada de esto es opinable. El oráculo sellado tiene una tabla y el código tiene
un diccionario: o son el mismo conjunto con los mismos nombres, o no lo son.

Se lee el oráculo del documento y el inventario del AST. Buscar los
identificadores por texto en el fuente cazaría los que aparecen en comentarios
y docstrings --el propio docstring de `gates()` nombra `L14-11` para explicar
que estuvo mal usado--, y ese error ya se cometió aquí antes.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

#: `## 15 · Gates`, `## 11 · Gates`, `## Gates`…
_ENCABEZADO = re.compile(r"^#{2,3}\s+.*\bgates\b", re.IGNORECASE)
#: `| **L14-0** linaje | criterio |`
_FILA = re.compile(r"^\|\s*\*\*(?P<id>[^*]+)\*\*\s*(?P<name>[^|]*)\|")


@dataclass(frozen=True)
class Reconciliation:
    sealed: dict[str, str]
    implemented: dict[str, str]
    missing: tuple[str, ...]      # sellados que el código no evalúa
    extra: tuple[str, ...]        # evaluados que el oráculo no selló
    renamed: tuple[tuple[str, str, str], ...]   # (id, sellado, implementado)

    @property
    def ok(self) -> bool:
        return not (self.missing or self.extra or self.renamed)

    def report(self) -> str:
        if self.ok:
            return (f"inventario conciliado · {len(self.sealed)} gates, "
                    "mismos identificadores y mismos nombres")
        lineas = [f"sellados {len(self.sealed)} · evaluados {len(self.implemented)}"]
        for g in self.missing:
            lineas.append(f"  FALTA      {g} · {self.sealed[g]}")
        for g in self.extra:
            lineas.append(f"  NO SELLADO {g} · {self.implemented[g]}")
        for g, sellado, puesto in self.renamed:
            lineas.append(f"  RENOMBRADO  {g} · sellado «{sellado}» · evaluado «{puesto}»")
        return "\n".join(lineas)


def sealed_gates(oracle: Path | str) -> dict[str, str]:
    """Los gates de la tabla de la sección «Gates» del oráculo sellado."""
    lineas = Path(oracle).read_text(encoding="utf-8").splitlines()
    dentro, encontrados = False, {}
    for linea in lineas:
        if linea.startswith("#"):
            dentro = bool(_ENCABEZADO.match(linea))
            continue
        if not dentro:
            continue
        m = _FILA.match(linea)
        if m:
            encontrados[m.group("id").strip()] = m.group("name").strip()
    if not encontrados:
        raise ValueError(f"{oracle}: no hay tabla de gates con identificadores en negrita")
    return encontrados


def implemented_gates(module: Path | str, function: str = "gates") -> dict[str, str]:
    """Las claves del diccionario que devuelve `gates()`, por AST.

    Se acepta cualquier función así llamada en el módulo. Cada clave es
    `«<id> <nombre>»`: el identificador es el primer token.
    """
    arbol = ast.parse(Path(module).read_text(encoding="utf-8"))
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.FunctionDef) and nodo.name == function:
            for hijo in ast.walk(nodo):
                if isinstance(hijo, ast.Dict) and hijo.keys:
                    claves = [k for k in hijo.keys
                              if isinstance(k, ast.Constant) and isinstance(k.value, str)]
                    if len(claves) == len(hijo.keys):
                        return {k.value.split(" ", 1)[0]:
                                (k.value.split(" ", 1)[1] if " " in k.value else "")
                                for k in claves}
    raise ValueError(f"{module}: no encuentro un `def {function}` que devuelva un dict literal")


def reconcile(oracle: Path | str, module: Path | str,
              function: str = "gates") -> Reconciliation:
    sellados = sealed_gates(oracle)
    puestos = implemented_gates(module, function)
    renombrados = tuple((g, sellados[g], puestos[g])
                        for g in sorted(set(sellados) & set(puestos))
                        if sellados[g] != puestos[g])
    return Reconciliation(
        sealed=sellados,
        implemented=puestos,
        missing=tuple(sorted(set(sellados) - set(puestos))),
        extra=tuple(sorted(set(puestos) - set(sellados))),
        renamed=renombrados,
    )
