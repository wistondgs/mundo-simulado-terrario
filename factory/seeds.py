"""Registro de semillas · una sola lista, y las colisiones se calculan.

Hoy cada linaje reescribe a mano la unión de todo lo ya gastado. En
`test_level14_lineage.py` eso es una expresión de seis términos que hay que
ampliar en cada nivel, y que además tiene que acordarse de los desplazamientos
derivados --`s + 7`, `+10_000_003`, `+20_000_003`--, porque dos bases disjuntas
pueden colisionar después de sumarles sus offsets. Mantenerlo a mano es O(n²)
de atención y falla en silencio: una semilla repetida no rompe nada, sólo
convierte dos medidas independientes en la misma medida.

Aquí el universo de cada campaña se declara una vez y el solapamiento se
consulta.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

DATA = Path(__file__).parent / "data" / "seeds.yaml"


@dataclass(frozen=True)
class Campaign:
    id: str
    ranges: tuple[tuple[int, int], ...]     # [inicio, fin) como en `range`
    offsets: tuple[int, ...] = ()           # semillas derivadas de las propias
    note: str = ""

    def universe(self) -> frozenset[int]:
        base = {s for a, b in self.ranges for s in range(a, b)}
        derivadas = {s + d for s in base for d in self.offsets}
        return frozenset(base | derivadas)

    def size(self) -> int:
        return len(self.universe())


class SeedRegistry:
    def __init__(self, campaigns: list[Campaign]):
        self.campaigns = {c.id: c for c in campaigns}

    @classmethod
    def load(cls, path: Path | str = DATA) -> "SeedRegistry":
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        return cls([Campaign(id=k,
                             ranges=tuple((r[0], r[1]) for r in v["ranges"]),
                             offsets=tuple(v.get("offsets", ())),
                             note=v.get("note", ""))
                    for k, v in raw["campaigns"].items()])

    def collisions(self) -> dict[tuple[str, str], tuple[int, ...]]:
        """Pares de campañas que comparten al menos una semilla.

        Incluye las derivadas: ése es el caso que un `range` a ojo no ve.
        """
        ids = sorted(self.campaigns)
        universos = {i: self.campaigns[i].universe() for i in ids}
        choques: dict[tuple[str, str], tuple[int, ...]] = {}
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                comun = universos[a] & universos[b]
                if comun:
                    choques[(a, b)] = tuple(sorted(comun))
        return choques

    def used(self) -> frozenset[int]:
        u: set[int] = set()
        for c in self.campaigns.values():
            u |= c.universe()
        return frozenset(u)

    def reserve(self, n: int, *, offsets: tuple[int, ...] = (),
                step: int = 10_000_000) -> tuple[int, int]:
        """Propone el siguiente bloque libre de `n` semillas.

        `step` mantiene la convención visible del linaje --cada nivel empieza
        una década por encima del anterior--, y el bloque devuelto está libre
        contando ya sus propias derivadas.
        """
        if n <= 0:
            raise ValueError("un bloque vacío no se reserva")
        usadas = self.used()
        bases = [min(c.universe()) for c in self.campaigns.values()] or [0]
        inicio = (max(bases) // step + 1) * step + 11
        while True:
            propuesto = set(range(inicio, inicio + n))
            propuesto |= {s + d for s in propuesto for d in offsets}
            if not (propuesto & usadas):
                return inicio, inicio + n
            inicio += step
