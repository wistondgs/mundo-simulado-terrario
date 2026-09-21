"""D2 y D3 · Instancias renovables, y su gemelo automático.

    D2  InstanceGenerator   infinitas variantes del mismo kernel
    D3  TwinGenerator       cada exigente trae su control, compartiendo todo
                            salvo la dimensión causal

QUÉ SE REUSA Y QUÉ NO. La física, la economía y las tres reglas de resultado
se importan de `terrario.lab.world_generator`: duplicarlas sería peor que
importarlas, porque dos copias de una física divergen. Lo que NO se reusa es
`generate`, y la razón es concreta: su geometría es única para todo el mundo
--un `delay`, un `span`, un `pitch`-- y la variación renovable necesita que
cada estación tenga la suya.

EL CAMBIO QUE HACE RENOVABLE AL MUNDO

    diagnóstico    values = (0.9,) if designated == "up" else (0.1,)
                   el valor del cue lo decide la respuesta. Dos situaciones.

    desarrollo     value = sorteo del vocabulario (81 valores)
                   thr = CUE_BOUNDARY if boundary_of is None else float(boundary_of(j))
        designated = "up" if value > thr else "down"
                   la respuesta la decide una REGLA sobre el valor.

Invertir esa dependencia es todo. En el primero hay dos pares que memorizar;
en el segundo hay un umbral que inducir, y valores de cue que se pueden
retirar para preguntar si de verdad lo indujo.

EL GEMELO, Y POR QUÉ ES QUIRÚRGICO

`relax="cue_at_door"` mueve el cue de `door_col - delay` a `door_col - 1`, y
nada más. Mismo objeto, mismo valor, misma marca, misma fila. Mismos
distractores en las mismas casillas. Mismas puertas con los mismos canales.
Misma anchura y misma duración, así que el gasto metabólico también es igual.

    I+ menos I-  =  una coordenada x de un objeto  =  exactamente el eje causal

`twin_difference` lo comprueba objeto a objeto en vez de afirmarlo.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator, Sequence

import numpy as np

from terrario.lab import world_generator as gen
from terrario.devworld.kernel import (
    CUE_BOUNDARY, TaskKernel, cue_vocabulary, side_of_cue,
)

SEMANTICS_VERSION = "terrario.devworld/v1"

#: Flujos por propósito, misma disciplina que el generador diagnóstico: que
#: sortear de más en un propósito no desplace lo que decide otro.
_PURPOSES = ("delay", "cue", "ndistractors", "distractors")


def _stream(seed: int, station: int, purpose: str) -> np.random.Generator:
    return np.random.default_rng([seed, station, _PURPOSES.index(purpose), 0xDE7])


@dataclass(frozen=True)
class DevStation:
    """Una instancia. `z` es la estructura; el resto es `n`."""
    index: int
    door_column: int
    cue_column: int
    cue_value: float
    delay: int
    distractor_columns: tuple[int, ...]
    distractor_values: tuple[float, ...]
    up_id: int
    down_id: int
    cue_id: int
    designated: str          # = la regla aplicada al valor. Es `z` aplicado.
    boundary: float = CUE_BOUNDARY   # la frontera VIGENTE en esta estación

    @property
    def cognitive_signature(self) -> tuple[str, ...]:
        """`z`: qué relación hay que resolver. Estable entre instancias."""
        return ("cue_value -> side", "umbral")

    @property
    def incidental_signature(self) -> tuple[Any, ...]:
        """`n`: cómo se ve esta vez. Es lo que debe variar sin límite."""
        return (round(self.cue_value, 4), self.delay,
                len(self.distractor_columns), self.distractor_values)


@dataclass(frozen=True)
class DevWorld:
    scenario: dict[str, Any]
    kernel: TaskKernel
    economy: gen.Economy
    seed: int
    stations: tuple[DevStation, ...]
    relaxed: bool            # True si es el gemelo de control

    @property
    def duration(self) -> int:
        return int(self.scenario["duration"])

    @property
    def width(self) -> int:
        return int(self.scenario["grid_size"][0])

    def correct_side(self, station: DevStation) -> str:
        return station.designated

    def describe(self) -> str:
        tag = "control" if self.relaxed else "exigente"
        return (f"{SEMANTICS_VERSION} · {self.kernel.name} · {tag} · "
                f"{len(self.stations)} estaciones · ancho {self.width}")


def generate(kernel: TaskKernel, *, seed: int, stations: int = 8,
             economy: gen.Economy = gen.DEFAULT_ECONOMY,
             relaxed: bool = False,
             boundary_of: Any = None) -> DevWorld:
    """Un mundo del kernel. `relaxed=True` devuelve el gemelo de control.

    Los dos comparten cada sorteo: el gemelo no vuelve a sortear nada, sólo
    coloca el cue en otra columna.
    """
    vocab = cue_vocabulary()
    lo_d, hi_d = kernel.causal["delay"]
    lo_n, hi_n = kernel.incidental.get("distractors", (0.0, 0.0))

    objects: list[dict[str, Any]] = []
    key: list[DevStation] = []

    def add(pos: tuple[int, int], channels: Sequence[float]) -> int:
        objects.append({"pos": list(pos), "channels": [float(c) for c in channels],
                        "movable": False, "energy_value": 0.0})
        return len(objects) - 1

    column = 1
    for j in range(stations):
        delay = int(_stream(seed, j, "delay").integers(int(lo_d), int(hi_d) + 1))
        value = float(_stream(seed, j, "cue").choice(vocab))
        n_dis = int(_stream(seed, j, "ndistractors").integers(int(lo_n), int(hi_n) + 1))
        n_dis = min(n_dis, max(delay - 2, 0))   # han de caber sin pisar el cue
        dis_rng = _stream(seed, j, "distractors")

        cue_col_demanding = column
        door_col = column + delay
        # EL ÚNICO CAMBIO DEL GEMELO. Dentro del radio de visión al elegir.
        cue_col = (door_col - 1) if relaxed else cue_col_demanding

        thr = CUE_BOUNDARY if boundary_of is None else float(boundary_of(j))
        designated = "up" if value > thr else "down"
        cue_id = add((gen.ROW_CUE, cue_col), (value, gen.MARK_CUE, 0.5, gen.CH3_INERT))

        dis_cols = tuple(cue_col_demanding + 1 + i for i in range(n_dis))
        dis_vals = tuple(float(dis_rng.choice(vocab)) for _ in range(n_dis))
        for c, v in zip(dis_cols, dis_vals):
            add((gen.ROW_ALT, c), (v, gen.MARK_DISTRACTOR, 0.5, gen.CH3_INERT))

        up_ch3 = gen.CH3_GOOD if designated == "up" else gen.CH3_BAD
        dn_ch3 = gen.CH3_BAD if designated == "up" else gen.CH3_GOOD
        up_id = add((gen.ROW_CUE, door_col), (0.5, gen.MARK_DOOR, 0.5, up_ch3))
        down_id = add((gen.ROW_ALT, door_col), (0.5, gen.MARK_DOOR, 0.5, dn_ch3))

        key.append(DevStation(j, door_col, cue_col, value, delay,
                              dis_cols, dis_vals, up_id, down_id, cue_id,
                              designated, thr))
        column = door_col + gen.VIEW_RADIUS + 1

    width = key[-1].door_column + gen.VIEW_RADIUS + 2
    e = economy
    scenario = {
        "grid_size": [width, 3],
        "duration": 2 * width,
        "num_channels": gen.NUM_CHANNELS,
        "view_radius": gen.VIEW_RADIUS,
        "objects": objects,
        "initial_energy": e.initial_energy,
        "max_energy": e.max_energy,
        "step_energy_cost": e.step_energy_cost,
        "low_energy_threshold": e.low_energy,
        "agent_start": [gen.ROW_PATH, 0],
        **gen._rules(e.gain, -e.loss, e.safe),
    }
    return DevWorld(scenario, kernel, economy, seed, tuple(key), relaxed)


def twin(kernel: TaskKernel, *, seed: int, stations: int = 8,
         economy: gen.Economy = gen.DEFAULT_ECONOMY) -> tuple[DevWorld, DevWorld]:
    """La pareja. Siempre se piden juntas: un exigente sin su control no vale."""
    return (generate(kernel, seed=seed, stations=stations, economy=economy, relaxed=False),
            generate(kernel, seed=seed, stations=stations, economy=economy, relaxed=True))


def twin_difference(a: DevWorld, b: DevWorld) -> tuple[str, ...]:
    """En qué difieren de verdad dos gemelos. Se comprueba, no se afirma.

    Devuelve una descripción por diferencia encontrada. Un gemelo correcto
    difiere SÓLO en la columna del cue.
    """
    diffs: list[str] = []
    if a.width != b.width:
        diffs.append(f"anchura {a.width} vs {b.width}")
    if a.duration != b.duration:
        diffs.append(f"duración {a.duration} vs {b.duration}")
    oa, ob = a.scenario["objects"], b.scenario["objects"]
    if len(oa) != len(ob):
        diffs.append(f"número de objetos {len(oa)} vs {len(ob)}")
        return tuple(diffs)
    for i, (x, y) in enumerate(zip(oa, ob)):
        if x["channels"] != y["channels"]:
            diffs.append(f"objeto {i}: canales {x['channels']} vs {y['channels']}")
        if x["pos"] != y["pos"]:
            cue_ids = {st.cue_id for st in a.stations}
            what = "cue" if i in cue_ids else "NO-CUE"
            diffs.append(f"objeto {i} ({what}): posición {x['pos']} vs {y['pos']}")
    if a.scenario["rules"] != b.scenario["rules"]:
        diffs.append("reglas distintas")
    return tuple(diffs)


def instances(kernel: TaskKernel, *, seed: int, stations: int) -> Iterator[DevStation]:
    yield from generate(kernel, seed=seed, stations=stations).stations
