"""Las escenas y los bancos · enumerados, sin azar.

**Conjuntos, no posiciones.** La entrada no puede expresar
`directions[0] ↔ proximities[0]` como convención, así que la escena nominal usa
`frozenset`.

Pero eso tiene una consecuencia que hay que decir: con `frozenset`, la
invariancia al orden es cierta **por construcción** y el contrato que la exige no
puede fallar nunca. Por eso existe además `OrderedScene`: el atajo de índice
necesita una representación donde sea expresable para poder ser rechazado.

Y `frozenset` colapsa duplicados: si los dos elementos direccionales
compartieran `(portador, cue)` la escena tendría **una** referencia en silencio,
que es justo lo que invalida el constructo. De ahí el contrato de cardinalidad.
"""

from __future__ import annotations

from dataclasses import dataclass

from terrario.level11.cue import ALL_CUES, CueToken
from terrario.level12.reference import ALL_TOKENS, ProximityToken
from terrario.level14.carriers import (
    ALL_X, ALL_Y, DirectionCarrier, ProximityCarrier, Psi,
)


@dataclass(frozen=True)
class DirectionItem:
    carrier: DirectionCarrier
    cue: CueToken


@dataclass(frozen=True)
class ProximityItem:
    carrier: ProximityCarrier
    sensor: ProximityToken


@dataclass(frozen=True)
class BindingObservation:
    """Lo único que llega al agente. Sin índices y sin verdad."""

    directions: frozenset[DirectionItem]
    proximities: frozenset[ProximityItem]

    def __post_init__(self) -> None:
        if len(self.directions) != len(self.proximities):
            raise ValueError("las dos modalidades deben tener el mismo tamaño")
        if len(self.directions) not in (1, 2):
            raise ValueError(
                f"escena de {len(self.directions)} referencias; se esperaban 1 o 2. "
                "Recuerda que frozenset colapsa duplicados.")


@dataclass(frozen=True)
class OrderedScene:
    """Sólo para la fixture del atajo de índice. **No es la escena nominal.**"""

    directions: tuple[DirectionItem, ...]
    proximities: tuple[ProximityItem, ...]

    def as_set(self) -> BindingObservation:
        return BindingObservation(frozenset(self.directions),
                                  frozenset(self.proximities))


@dataclass(frozen=True)
class BindingTruth:
    """Del experimentador. **Nunca** se pasa a `bind()`."""

    pairs: frozenset[tuple[DirectionItem, ProximityItem]]


# --- los bancos ------------------------------------------------------------------

def acquisition_bank(psi: Psi) -> list[tuple[DirectionItem, ProximityItem]]:
    """64 escenas de UNA referencia: para cada `x`, las 16 combinaciones `(g,s)`.

    Con una sola referencia la co-presencia es inequívoca y basta contar. Por
    construcción `P(G|X) = P(S|X) = 1/4`, así que el portador no puede aprender
    semántica de atributo.
    """
    return [(DirectionItem(x, g), ProximityItem(psi[x], s))
            for x in ALL_X for g in ALL_CUES for s in ALL_TOKENS]


def shuffled_acquisition_bank() -> list[tuple[DirectionItem, ProximityItem]]:
    """Cada `x` coocurre EXACTAMENTE cuatro veces con cada `y`.

    No baraja registros: construye la independencia. `A_xy = 5` en las dieciséis
    celdas, `C(y|x) = 1/4` exacto, y por tanto varianza cero — mejor que el
    barajado muestreado de 1.1 y 1.2.
    """
    return [(DirectionItem(x, ALL_CUES[k]), ProximityItem(y, ALL_TOKENS[k]))
            for x in ALL_X for y in ALL_Y for k in range(4)]


def _ordered_pairs(valores):
    return [(a, b) for a in valores for b in valores if a != b]


def evaluation_bank(psi: Psi) -> list[tuple[BindingObservation, BindingTruth]]:
    """1728 escenas de dos referencias · `12 × 12 × 12`.

    Enumerar el par de sensores **ordenado** es exactamente la paridad `A`/`B`:
    sin ella, emparejar por índice acertaría siempre y la métrica no podría
    distinguirlo de un binder de verdad.
    """
    banco = []
    for x1, x2 in _ordered_pairs(ALL_X):
        for g1, g2 in _ordered_pairs(ALL_CUES):
            for sa, sb in _ordered_pairs(ALL_TOKENS):
                d1, d2 = DirectionItem(x1, g1), DirectionItem(x2, g2)
                p1, p2 = ProximityItem(psi[x1], sa), ProximityItem(psi[x2], sb)
                banco.append((
                    BindingObservation(frozenset((d1, d2)), frozenset((p1, p2))),
                    BindingTruth(frozenset(((d1, p1), (d2, p2))))))
    return banco


def ordered_evaluation_bank(psi: Psi) -> list[tuple[OrderedScene, BindingTruth]]:
    """6912 · el banco anterior con ambos órdenes de listado de cada modalidad.

    Sobre él, emparejar por índice acierta **exactamente la mitad**.
    """
    fuera = []
    for obs, verdad in evaluation_bank(psi):
        ds = sorted(obs.directions, key=lambda d: d.carrier.value)
        ps = sorted(obs.proximities, key=lambda p: p.carrier.value)
        # el orden canónico empareja por posición; hay que romperlo en ambos sentidos
        correcto = {d: p for d, p in verdad.pairs}
        ds = [d for d in ds]
        ps = [correcto[d] for d in ds]
        for od in (False, True):
            for op in (False, True):
                fuera.append((OrderedScene(tuple(ds[::-1] if od else ds),
                                           tuple(ps[::-1] if op else ps)), verdad))
    return fuera


def single_reference_bank(psi: Psi) -> list[tuple[BindingObservation, BindingTruth]]:
    """FIXTURE NEGATIVA: una sola referencia. La tarea se resuelve por
    cardinalidad y cualquier arquitectura parecería competente."""
    fuera = []
    for x in ALL_X:
        for g in ALL_CUES:
            for s in ALL_TOKENS:
                d, p = DirectionItem(x, g), ProximityItem(psi[x], s)
                fuera.append((BindingObservation(frozenset((d,)), frozenset((p,))),
                              BindingTruth(frozenset(((d, p),)))))
    return fuera
