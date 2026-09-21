"""La regla de consumo del intervalo de semillas (Enmienda 01).

El oráculo reservó 32 semillas para 16 vidas y prometió una «regla
preregistrada» de reemplazo que no llegó a escribir. Ese hueco valía dieciséis
grados de libertad que se habrían resuelto mirando resultados. La regla es ésta,
y su mitad importante es la segunda:

* se recorre el intervalo **ascendente**, sin saltos, y se para en la
  decimosexta vida válida; las semillas restantes quedan sin usar;
* **sólo** `N-MUNDO` --estructural, anterior a la vida-- provoca reemplazo.
  `N-EXPERIENCIA`, `N-PLASTICIDAD`, `NEGATIVO VERDADERO` y `POSITIVO` son
  categorías posteriores y permanecen entre las 16, en el denominador.
  Sustituir cualquiera de ellas sería seleccionar vidas favorables.

`INVÁLIDO` no aparece aquí porque no es categoría de semilla: es un defecto de
cableado que invalida la campaña entera y obliga a recorrer el intervalo de
nuevo desde el principio.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field

from terrario.level16.structure import WorldStructure, describe_world, is_nonworld
from terrario.level16.world import build_world

#: Intervalo reservado en el oráculo §16. Disjunto del resto del linaje.
SEED_WINDOW: tuple[int, ...] = tuple(range(140000011, 140000043))

#: Vidas estructuralmente válidas que la campaña confirmatoria necesita.
LIVES_REQUIRED = 16


class SeedVerdict(enum.Enum):
    """Lo único que el predicado estructural puede decir de una semilla."""

    VALID = "VALID"
    NONWORLD = "N-MUNDO"


class SeedPoolExhausted(RuntimeError):
    """Se agotó el intervalo sin reunir las vidas pedidas.

    Con la tasa medida de degeneración esto tiene probabilidad ~1.6e-20, así que
    si llega a ocurrir no es mala suerte: es un defecto en el generador de
    mundos o en el predicado. La condición de parada funciona como detector de
    error, no como riesgo estadístico.
    """


@dataclass(frozen=True)
class SeedEntry:
    """Una semilla tocada, con su veredicto y los descriptores de su mundo."""

    seed: int
    verdict: SeedVerdict
    structure: WorldStructure

    @property
    def is_life(self) -> bool:
        return self.verdict is SeedVerdict.VALID


@dataclass(frozen=True)
class SeedLedger:
    """El recorrido del intervalo, reconstruible sin acceso al código."""

    entries: tuple[SeedEntry, ...] = field(default_factory=tuple)
    unconsumed: tuple[int, ...] = field(default_factory=tuple)

    @property
    def lives(self) -> tuple[int, ...]:
        return tuple(e.seed for e in self.entries if e.is_life)

    @property
    def discarded(self) -> tuple[int, ...]:
        return tuple(e.seed for e in self.entries if not e.is_life)


def consume_seeds(window: tuple[int, ...] = SEED_WINDOW,
                  required: int = LIVES_REQUIRED) -> SeedLedger:
    """Recorrer el intervalo y devolver el libro completo, descartes incluidos."""
    entries: list[SeedEntry] = []
    lives = 0
    for index, seed in enumerate(window):
        structure = describe_world(seed, build_world(seed))
        verdict = (SeedVerdict.NONWORLD if is_nonworld(structure)
                   else SeedVerdict.VALID)
        entries.append(SeedEntry(seed, verdict, structure))
        if verdict is SeedVerdict.VALID:
            lives += 1
            if lives == required:
                return SeedLedger(tuple(entries), tuple(window[index + 1:]))
    raise SeedPoolExhausted(
        f"{len(window)} semillas consumidas y sólo {lives} vidas válidas; "
        f"se pedían {required}. El intervalo no se amplía sobre la marcha: "
        "exige una enmienda fechada emitida antes de mirar resultado alguno."
    )
