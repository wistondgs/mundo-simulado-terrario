"""El catálogo como grafo, y el planificador que responde «¿cuál sigue?».

La lista no basta. El linaje real no es `1.0 → 1.1 → 1.2 → 1.3`: 1.2 y 1.3 son
hermanos que forkean de 1.1, y una capacidad que necesite las dos no puede
nacer como decimal porque **no existe ningún árbol que las tenga**. Eso se
descubrió a mano después de 1.4. Aquí es una consulta.

Dos relaciones distintas, y confundirlas es el error que el grafo evita:

* `requires` — qué capacidades necesita el organismo para que el experimento
  tenga sentido. Es una afirmación científica.
* `inherits` — de qué árbol se forkea. Es un hecho de git.

`holds` se calcula por `inherits`, nunca por `requires`. Un nodo puede exigir
una capacidad que su árbol no contiene: eso no es un error del catálogo, es
exactamente la condición que obliga a una campaña de composición.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import yaml

DATA = Path(__file__).parent / "data" / "capabilities.yaml"

#: Orden del ciclo. Ningún nodo puede saltarse un estado: para estar en uno hay
#: que tener los artefactos de todos los anteriores.
PIPELINE = ("PROPOSED", "DESIGNED", "AUDITED", "SEALED",
            "IMPLEMENTED", "VERIFIED", "FROZEN")

#: Estados fuera de la línea. `BLOCKED` es reversible; `NON_EVALUABLE` declara
#: que la capacidad, tal como está escrita, no se puede falsar.
OFF_PIPELINE = ("BLOCKED", "NON_EVALUABLE")

#: Qué artefacto hace verdadero cada estado. Declarar el estado sin el artefacto
#: es la forma barata de mentirse.
REQUIRED_ARTIFACT = {
    "DESIGNED": "design",
    "AUDITED": "audit",
    "SEALED": "oracle",
    "IMPLEMENTED": "implementation",
    "VERIFIED": "report",
    "FROZEN": "frozen_at",
}


class CatalogError(Exception):
    """El catálogo se contradice a sí mismo. No es un fallo de una campaña."""


@dataclass(frozen=True)
class Node:
    id: str
    name: str                       # la frase legible, no el índice
    kind: str                       # "decimal" | "composition"
    status: str
    decimal: str | None = None
    acquires: str | None = None     # exactamente una, o ninguna si es composición
    requires: tuple[str, ...] = ()
    forbidden: tuple[str, ...] = ()
    inherits: tuple[str, ...] = ()
    claim_max: str = ""
    branch: str | None = None
    worktree: str | None = None
    artifacts: dict[str, str] = field(default_factory=dict)
    seeds: str | None = None
    note: str = ""          # por qué el nodo está como está, si no es obvio
    gate_sources: dict[str, str] = field(default_factory=dict)

    @property
    def verified(self) -> bool:
        return self.status in ("VERIFIED", "FROZEN")


@dataclass(frozen=True)
class Plan:
    """Lo que la fábrica puede decir sin ejecutar nada."""
    ready: tuple[str, ...]
    needs_composition: dict[str, tuple[str, ...]]   # nodo → árboles a reunir
    blocked: dict[str, tuple[str, ...]]             # nodo → dependencias que faltan
    done: tuple[str, ...]


class Catalog:
    def __init__(self, nodes: Iterable[Node]):
        nodes = list(nodes)
        self.nodes: dict[str, Node] = {n.id: n for n in nodes}
        if len(self.nodes) != len(nodes):
            raise CatalogError("identificadores repetidos")
        self._validate()

    # ── carga ────────────────────────────────────────────────────────────
    @classmethod
    def load(cls, path: Path | str = DATA) -> "Catalog":
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        vistos: set[str] = set()
        nodos = []
        for item in raw["capabilities"]:
            if item["id"] in vistos:
                raise CatalogError(f"identificador repetido: {item['id']}")
            vistos.add(item["id"])
            nodos.append(Node(
                id=item["id"],
                name=item["name"],
                kind=item.get("kind", "decimal"),
                status=item["status"],
                decimal=item.get("decimal"),
                acquires=item.get("acquires"),
                requires=tuple(item.get("requires", ())),
                forbidden=tuple(item.get("forbidden", ())),
                inherits=tuple(item.get("inherits", ())),
                claim_max=item.get("claim_max", ""),
                branch=item.get("branch"),
                worktree=item.get("worktree"),
                artifacts=dict(item.get("artifacts", {})),
                seeds=item.get("seeds"),
                note=item.get("note", ""),
                gate_sources=dict(item.get("gate_sources", {})),
            ))
        return cls(nodos)

    # ── validación ───────────────────────────────────────────────────────
    def _validate(self) -> None:
        for n in self.nodes.values():
            if n.status not in PIPELINE and n.status not in OFF_PIPELINE:
                raise CatalogError(f"{n.id}: estado desconocido {n.status!r}")
            adquiridas = self._acquired_by()
            for cap in n.requires:
                if cap not in adquiridas:
                    raise CatalogError(
                        f"{n.id}: exige la capacidad {cap!r}, que ningún nodo adquiere")
            for padre in n.inherits:
                if padre not in self.nodes:
                    raise CatalogError(
                        f"{n.id}: forkea de {padre!r}, que no es un nodo del catálogo")
            solapan = set(n.requires) & set(n.forbidden)
            if solapan:
                raise CatalogError(
                    f"{n.id}: {sorted(solapan)} está exigido y prohibido a la vez")
            if n.kind not in ("decimal", "composition", "probe"):
                raise CatalogError(f"{n.id}: clase desconocida {n.kind!r}")
            if n.kind == "decimal" and n.status in PIPELINE and not n.acquires:
                raise CatalogError(f"{n.id}: un decimal adquiere exactamente una")
            if n.kind != "decimal" and n.acquires:
                raise CatalogError(
                    f"{n.id}: sólo un decimal adquiere; {n.kind} declara {n.acquires!r}")
        self._validate_acyclic()

    def gaps(self) -> dict[str, tuple[str, ...]]:
        """Estados declarados sin el artefacto que los sostiene.

        No es una contradicción del catálogo --por eso no levanta--: es la
        contabilidad del ciclo, y hay campañas reales que se verificaron sin
        auditoría adversarial registrada. El catálogo lo dice en voz alta en
        lugar de rellenarlo o de negarse a cargar.
        """
        faltas: dict[str, tuple[str, ...]] = {}
        for n in self.nodes.values():
            if n.status in OFF_PIPELINE:
                continue
            alcanzado = PIPELINE.index(n.status)
            sin = tuple(f"{estado}:{REQUIRED_ARTIFACT[estado]}"
                        for estado in PIPELINE[1:alcanzado + 1]
                        if not n.artifacts.get(REQUIRED_ARTIFACT[estado]))
            if sin:
                faltas[n.id] = sin
        return faltas

    def _validate_acyclic(self) -> None:
        """El ciclo puede pasar por una capacidad, no sólo por un fork.

        `requires` nombra capacidades y `inherits` nombra nodos; si sólo se
        siguieran los forks, `a` exige lo que adquiere `b` y `b` exige lo que
        adquiere `a` sería un ciclo invisible.
        """
        adquiridas = self._acquired_by()
        color: dict[str, int] = {}

        def aristas(nodo: Node) -> tuple[str, ...]:
            por_capacidad = tuple(adquiridas[c] for c in nodo.requires
                                  if c in adquiridas)
            return por_capacidad + nodo.inherits

        def visita(nid: str, camino: tuple[str, ...]) -> None:
            if color.get(nid) == 2:
                return
            if color.get(nid) == 1:
                ciclo = " → ".join(camino[camino.index(nid):] + (nid,))
                raise CatalogError(f"ciclo de dependencias: {ciclo}")
            color[nid] = 1
            nodo = self.nodes.get(nid)
            if nodo is not None:
                for dep in aristas(nodo):
                    if dep in self.nodes and dep != nid:
                        visita(dep, camino + (nid,))
            color[nid] = 2

        for nid in self.nodes:
            visita(nid, ())

    def _acquired_by(self) -> dict[str, str]:
        """capacidad adquirida → nodo que la adquirió."""
        return {n.acquires: n.id for n in self.nodes.values() if n.acquires}

    # ── consultas ────────────────────────────────────────────────────────
    def holds(self, nid: str) -> frozenset[str]:
        """Qué capacidades tiene EN EL ÁRBOL el nodo `nid`.

        Por `inherits`, que es git, y no por `requires`, que es una intención.
        """
        nodo = self.nodes[nid]
        propio = {nodo.acquires} if nodo.acquires else set()
        for padre in nodo.inherits:
            if padre in self.nodes:
                propio |= self.holds(padre)
        return frozenset(propio)

    def plan(self) -> Plan:
        adquirida = self._acquired_by()
        verificadas = {cap for cap, nid in adquirida.items()
                       if self.nodes[nid].verified}
        arboles = {nid: self.holds(nid) for nid, n in self.nodes.items()
                   if n.verified}

        ready, composicion, bloqueados, hechos = [], {}, {}, []
        for nid, n in self.nodes.items():
            if n.verified:
                hechos.append(nid)
                continue
            if n.status in OFF_PIPELINE:
                bloqueados[nid] = (n.status,)
                continue
            faltan = tuple(sorted(set(n.requires) - verificadas))
            if faltan:
                bloqueados[nid] = faltan
                continue
            necesarias = set(n.requires)
            if any(necesarias <= tiene for tiene in arboles.values()):
                ready.append(nid)
            else:
                composicion[nid] = self._minimal_merge(necesarias, arboles)
        return Plan(tuple(sorted(ready)), composicion,
                    dict(sorted(bloqueados.items())), tuple(sorted(hechos)))

    def _minimal_merge(self, necesarias: set[str],
                       arboles: dict[str, frozenset[str]]) -> tuple[str, ...]:
        """Conjunto mínimo de árboles verificados que cubre lo que hace falta.

        Voraz por cobertura: el tamaño del catálogo no justifica exactitud NP.
        A igual cobertura gana el árbol que ya es una composición --extender un
        organismo que ya reunió capacidades cuesta menos que volver a fusionar
        desde las ramas sueltas--, y después el que más tenga.
        """
        restantes, elegidos = set(necesarias), []
        candidatos = dict(arboles)
        while restantes and candidatos:
            def clave(nid: str) -> tuple[int, int, int, str]:
                """Más cobertura primero; a igual cobertura, la composición que
                ya existe; luego el árbol más completo; y el nombre al final,
                sólo para que el resultado sea el mismo en cada ejecución."""
                return (-len(candidatos[nid] & restantes),
                        0 if self.nodes[nid].kind == "composition" else 1,
                        -len(candidatos[nid]),
                        nid)
            mejor = min(candidatos, key=clave)
            if not (candidatos[mejor] & restantes):
                break
            elegidos.append(mejor)
            restantes -= candidatos[mejor]
            del candidatos[mejor]
        return tuple(elegidos)
