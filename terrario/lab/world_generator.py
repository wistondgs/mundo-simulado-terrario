"""Generador de mundos diagnósticos: CUE → DEMORA → ELECCIÓN.

Un mundo no se escribe por capacidad: se genera a partir de lo que exige. La
entrada es un CONJUNTO de capacidades. Cada una declara una exigencia sobre un
eje; las exigencias se funden por el máximo; y el mundo resultante no se pasa
sin todas ellas. Con un solo elemento es el mundo de esa habilidad. Con varios,
el mundo varía para exigirlas juntas -- que es la composición de la Fase 3 sin
mundos nuevos.

El control de una capacidad es el mismo mundo con SU eje apagado y nada más.
Exigente y control difieren en exactamente una dimensión por construcción, no
por cuidado; `axis_difference` lo comprueba.

Sustrato: un pasillo de tres filas. El organismo avanza por la fila central y
encuentra estaciones. Cada estación tiene un CUE en la fila 0 y, `delay`
columnas después, dos PUERTAS en las filas 0 y 2 -- idénticas en los canales
que el organismo ve y distintas en el canal 3, que `get_observation` trunca y
`RuleEngine` sí lee. El cue dice cuál de las dos tiene el canal 3 bueno.

Eso apoya en un hecho del motor: con `num_channels = 4` el organismo recibe
`obs[0] = ocupación, obs[1..3] = canales 0..2`, y el canal 3 no aparece. Este
módulo lo convierte en contrato (`NUM_CHANNELS`) y `channel_3_is_hidden` lo
comprueba contra el runtime real, no contra esta docstring.

Lo que el generador usa del motor y nada más: objetos explícitos con `pos` y
`channels`, reglas sobre `(object_channel, CONSUME)`, `changes` para la
inversión, y las cuatro claves de economía que `strict_physics` exige. No usa
`procedural_layout` ni `opportunity_lifecycle`: la repetición de ensayos dentro
de una vida la dan las estaciones, no el respawn.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from terrario.core.types import ObjectSpec, Position

SEMANTICS_VERSION = "terrario.lab.world_generator/v1"

# --- Contrato con el motor -------------------------------------------------

#: Con 4 canales el organismo ve 3 canales de objeto; el cuarto queda oculto.
NUM_CHANNELS = 4
VIEW_RADIUS = 2
HIDDEN_CHANNEL = 3

ROW_CUE, ROW_PATH, ROW_ALT = 0, 1, 2

#: Canal 1 dice QUÉ es un objeto. El organismo lo ve.
MARK_CUE, MARK_DISTRACTOR, MARK_NOVEL, MARK_DOOR = 0.9, 0.6, 0.3, 0.1

#: Canal 3 dice QUÉ HACE una puerta. El organismo no lo ve; las reglas sí.
CH3_GOOD, CH3_BAD, CH3_SAFE, CH3_INERT = 0.9, 0.1, 0.5, 0.35

#: Canal 0 del cue: su valor. Con un cue el vocabulario es binario; con dos,
#: ternario, porque un par de un vocabulario binario lo decide el último cue y
#: no habría orden que recordar.
CUE_VOCABULARY = {1: (0.1, 0.9), 2: (0.1, 0.5, 0.9)}
NOVEL_VALUE = 0.5

#: Dos cues nunca coinciden en la ventana: la separación supera su diámetro.
CUE_GAP = 2 * VIEW_RADIUS + 1


@dataclass(frozen=True)
class Economy:
    """Lo que vale cada cosa. Es un parámetro y no una constante para que la
    calibración se pueda cambiar sin tocar la geometría."""

    initial_energy: float = 20.0
    max_energy: float = 60.0
    step_energy_cost: float = 0.15
    gain: float = 8.0
    loss: float = 6.0
    #: Menor que la esperanza de la arriesgada, (gain − loss) / 2: elegirla
    #: cuesta algo, y sólo la energía baja lo justifica.
    safe: float = 0.5
    #: Umbral homeostático. La energía inicial queda a una pérdida de él, para
    #: que una vida cruce el umbral en los dos sentidos y haya decisiones a
    #: ambos lados que comparar.
    low_energy: float = 14.0


DEFAULT_ECONOMY = Economy()


# --- Los ejes --------------------------------------------------------------

@dataclass(frozen=True)
class Demand:
    """Lo que un mundo exige, eje por eje.

    delay        columnas entre el cue y las puertas. Hasta 2 el cue sigue en
                 la ventana al elegir; desde 3 hay que haberlo retenido.
    hidden       True: la bondad de la puerta va en el canal 3 y sólo el cue la
                 revela. False: va también en el canal 2, a la vista.
    distractors  cues falsos (marcados distinto) entre el cue y las puertas.
    sequence     cues cuyo ORDEN decide. 1: uno solo. 2: dos, ascendente ↑.
    risk         True: la puerta señalada da +gain o -loss; la otra +safe seguro.
    novelty      fracción de estaciones cuyo cue no pertenece al vocabulario y
                 cuyas puertas tienen consecuencia IRREDUCIBLE: canal 3 al azar
                 en cada una. No basta con que el cue sea nuevo; si ambas
                 puertas fueran seguras la consecuencia sería cierta y una
                 incertidumbre bien calibrada debería ser BAJA, no alta. La
                 incertidumbre necesita un referente en el mundo: aquí lo hay.
    inversion    fracción de la vida a la que el mapeo se invierte; None nunca.
                 Con 0.3 y duración 2×ancho, un organismo que avanza una
                 columna por paso la encuentra hacia la mitad del pasillo.
    """

    delay: int = 1
    hidden: bool = True
    distractors: int = 0
    sequence: int = 1
    risk: bool = False
    novelty: float = 0.0
    inversion: float | None = None


AXES: tuple[str, ...] = tuple(f.name for f in fields(Demand))

#: El valor de cada eje cuando está apagado. No coincide con `Demand()` en
#: `hidden`: la base sobre la que se enciende un eje esconde la verdad, pero
#: apagar el eje de LEARN es precisamente dejar de esconderla.
OFF = Demand(delay=1, hidden=False, distractors=0, sequence=1,
             risk=False, novelty=0.0, inversion=None)


def merge(demands: Iterable[Demand]) -> Demand:
    """La exigencia de un conjunto: por eje, la más exigente."""
    ds = list(demands)
    if not ds:
        return Demand()
    inversions = [d.inversion for d in ds if d.inversion is not None]
    return Demand(
        delay=max(d.delay for d in ds),
        hidden=any(d.hidden for d in ds),
        distractors=max(d.distractors for d in ds),
        sequence=max(d.sequence for d in ds),
        risk=any(d.risk for d in ds),
        novelty=max(d.novelty for d in ds),
        inversion=min(inversions) if inversions else None,
    )


def switch_off(demand: Demand, axis: str) -> Demand:
    if axis not in AXES:
        raise KeyError(f"eje desconocido {axis!r}; hay {AXES}")
    return replace(demand, **{axis: getattr(OFF, axis)})


def axis_difference(a: Demand, b: Demand) -> tuple[str, ...]:
    return tuple(ax for ax in AXES if getattr(a, ax) != getattr(b, ax))


#: Qué exige cada capacidad y sobre qué eje. Los demás ejes quedan en base.
#: Las tres de memoria comparten `delay=5`: LTMEM y TEMP son EPMEM más un
#: eje, y el control de cada una es exactamente el mundo exigente de EPMEM.
DEMAND_OF: dict[str, tuple[str, Demand]] = {
    "LEARN-A1": ("hidden", Demand(hidden=True)),
    "EPMEM-A1": ("delay", Demand(delay=5)),
    "LTMEM-A1": ("distractors", Demand(delay=5, distractors=3)),
    "TEMP-A1": ("sequence", Demand(delay=5, sequence=2)),
    "HOMEO-A1": ("risk", Demand(hidden=False, risk=True)),
    "UNC-A1": ("novelty", Demand(novelty=0.3)),
    "PLAST-A1": ("inversion", Demand(inversion=0.3)),
}


def demanding_world_id(capability_id: str) -> str | None:
    """Con qué mundo cuenta una capacidad, o None si el generador no tiene
    exigencia declarada para ella. Es lo que el pasaporte lee. Que el mundo
    exija de verdad lo que declara no lo dice este identificador: lo dice
    `world_oracles.verdict_for`, y `scripts/world_demand_check.py` lo corre."""
    if capability_id not in DEMAND_OF:
        return None
    axis, demand = DEMAND_OF[capability_id]
    return f"{SEMANTICS_VERSION} · eje {axis} · {generate(demand, seed=0, stations=1).describe().split(' · ', 2)[2]}"


#: Ejes que una capacidad necesita CLAVADOS, más allá de su eje exigente, para
#: que su endpoint signifique algo. No son «menos exigencia»: son precondición
#: de la medida, y por eso `merge` no puede pisarlos con su máximo.
#:
#: HOMEO-A1 mide `Score.modulation` = P(segura | energía baja) − P(segura |
#: energía alta). Con `hidden=True` las dos puertas son idénticas en los
#: canales que el organismo ve, así que no puede elegir la segura aunque quiera
#: y la métrica mide una moneda al aire. Medido: componer HOMEO-A1 con
#: EPMEM-A1 volvía ambas puertas [0.5, 0.1, 0.5] frente a [0.5, 0.1, 0.9] y
#: [0.5, 0.1, 0.1] cuando HOMEO va sola.
PINNED: dict[str, Mapping[str, Any]] = {
    "HOMEO-A1": {"hidden": False},
}


def demand_for(capabilities: Iterable[str]) -> Demand:
    caps = list(capabilities)
    unknown = [c for c in caps if c not in DEMAND_OF]
    if unknown:
        raise KeyError(f"sin exigencia declarada: {unknown}; hay {sorted(DEMAND_OF)}")
    merged = merge(DEMAND_OF[c][1] for c in caps)
    broken = [(cap, ax, want, getattr(merged, ax))
              for cap in caps for ax, want in PINNED.get(cap, {}).items()
              if getattr(merged, ax) != want]
    if broken:
        detail = "; ".join(f"{cap} necesita {ax}={want!r} y la fusión da {got!r}"
                           for cap, ax, want, got in broken)
        raise ValueError(
            f"exigencias incompatibles en {sorted(set(caps))}: {detail}. "
            "No es un eje que se pueda ceder: sin él el endpoint de esa "
            "capacidad mide ruido. Componer este conjunto exige decidir a mano "
            "qué endpoint se abandona, y eso no lo decide el generador.")
    return merged


# --- La clave de verdad ----------------------------------------------------

@dataclass(frozen=True)
class Station:
    index: int
    door_column: int
    cue_ids: tuple[int, ...]
    cue_values: tuple[float, ...]
    distractor_ids: tuple[int, ...]
    up_id: int
    down_id: int
    #: Lado que el cue señala: "up" | "down".
    designated: str
    #: Canal 3 de la puerta señalada y de la otra.
    designated_ch3: float
    other_ch3: float
    novel: bool

    def side_of(self, object_id: int) -> str | None:
        if object_id == self.up_id:
            return "up"
        if object_id == self.down_id:
            return "down"
        return None


@dataclass(frozen=True)
class GeneratedWorld:
    scenario: dict[str, Any]
    demand: Demand
    economy: Economy
    seed: int
    stations: tuple[Station, ...]
    inversion_step: int | None
    # ``generate(Demand(...))`` legitimately has no capability origin.  Worlds
    # made through ``world_for`` carry the normalized set so the boundary can
    # reconstruct why this diagnostic world was requested.
    capabilities: tuple[str, ...] = ()

    @property
    def duration(self) -> int:
        return int(self.scenario["duration"])

    @property
    def width(self) -> int:
        return int(self.scenario["grid_size"][0])

    def station_of(self, object_id: int) -> Station | None:
        for st in self.stations:
            if object_id in (st.up_id, st.down_id):
                return st
        return None

    def inverted_at(self, step: int) -> bool:
        return self.inversion_step is not None and step >= self.inversion_step

    def correct_side(self, station: Station, step: int) -> str | None:
        """El lado que conviene en `step`, o None si da igual (estación novedosa
        o ambas puertas iguales)."""
        if station.novel:
            return None
        if station.designated_ch3 == station.other_ch3:
            return None
        d_good = station.designated_ch3 >= 0.8
        o_good = station.other_ch3 >= 0.8
        if self.inverted_at(step):
            d_good, o_good = station.designated_ch3 <= 0.2, station.other_ch3 <= 0.2
        if d_good and not o_good:
            return station.designated
        if o_good and not d_good:
            return _other(station.designated)
        # ninguna es +gain: la segura es la que no pierde
        d_loss = station.designated_ch3 <= 0.2 if not self.inverted_at(step) else station.designated_ch3 >= 0.8
        return _other(station.designated) if d_loss else station.designated

    def describe(self) -> str:
        on = [f"{ax}={getattr(self.demand, ax)}" for ax in AXES
              if getattr(self.demand, ax) != getattr(Demand(), ax)]
        return (f"{SEMANTICS_VERSION} · {len(self.stations)} estaciones · "
                f"{', '.join(on) if on else 'base'}")


#: Un flujo de azar por propósito, para que encender un eje no desplace lo que
#: otro decide. El orden de esta tupla es parte de la semántica del mundo.
_PURPOSES = ("designated", "novel", "cues", "distractors", "doors")


def _stream(seed: int, station: int, purpose: str) -> np.random.Generator:
    """El azar de una estación es función de (semilla, estación, propósito).

    Con un flujo único compartido, un eje que sortea de más corría el flujo y
    regeneraba todo lo sorteado después: el control de `distractors`, de
    `sequence`, de `risk` o de `novelty` cambiaba `designated`, que ningún eje
    debería tocar. Medido antes de esta reparación: 40 sorteos frente a 16 en
    LTMEM sobre 8 estaciones, y `designated` divergía en las semillas 0..5.
    """
    return np.random.default_rng([seed, station, _PURPOSES.index(purpose)])


def _other(side: str) -> str:
    return "down" if side == "up" else "up"


# --- Generación -------------------------------------------------------------

def generate(demand: Demand, *, seed: int, stations: int = 8,
             economy: Economy = DEFAULT_ECONOMY,
             duration: int | None = None) -> GeneratedWorld:
    """Un mundo que exige `demand`, con su clave de verdad.

    La geometría es determinista dada la exigencia; lo que la semilla decide
    es el contenido de cada estación: lado señalado, valores de los cues,
    resultado de la puerta arriesgada, qué estaciones son novedosas.

    `duration` fija la vida en vez de derivarla de la anchura. Existe porque
    `delay` y `sequence` alargan el pasillo, y con `duration = 2 × ancho` la
    vida --y por tanto el gasto metabólico-- se alargaba con ellos: el mundo
    exigente de EPMEM gastaba 19.80 de una energía inicial de 20.00 y su
    control 10.20. `control_for` la iguala a la del mundo exigente para que el
    contraste sea de un solo eje también en la física, no sólo en el `Demand`.
    """
    _validate(demand)

    span = (demand.sequence - 1) * CUE_GAP + demand.delay
    pitch = span + VIEW_RADIUS + 1          # el cue siguiente no cabe en la ventana
    objects: list[dict[str, Any]] = []
    key: list[Station] = []

    def add(pos: tuple[int, int], channels: Sequence[float]) -> int:
        objects.append({"pos": list(pos), "channels": [float(c) for c in channels],
                        "movable": False, "energy_value": 0.0})
        return len(objects) - 1

    for j in range(stations):
        start = 1 + j * pitch
        door_col = start + span
        # Un flujo por propósito y por estación. Con un flujo único, encender un
        # eje consumía más azar y desplazaba TODO lo que se sorteaba después:
        # el control de `distractors`, `sequence`, `risk` o `novelty` regeneraba
        # `designated` y dejaba de ser el mismo mundo. Medido: 40 vs 16 sorteos
        # en LTMEM. Aquí el contenido de una estación es función de (semilla,
        # estación, propósito) y de nada más.
        designated = "up" if _stream(seed, j, "designated").random() < 0.5 else "down"
        novel = _stream(seed, j, "novel").random() < demand.novelty
        cue_rng = _stream(seed, j, "cues")
        dis_rng = _stream(seed, j, "distractors")
        door_rng = _stream(seed, j, "doors")

        # cues: su orden a lo largo del pasillo es su orden en el tiempo
        if novel:
            values = (NOVEL_VALUE,) * demand.sequence
            mark = MARK_NOVEL
        else:
            vocab = CUE_VOCABULARY[demand.sequence]
            if demand.sequence == 1:
                values = (0.9,) if designated == "up" else (0.1,)
            else:
                pair = sorted(cue_rng.choice(len(vocab), size=2, replace=False))
                values = tuple(vocab[i] for i in (pair if designated == "up" else pair[::-1]))
            mark = MARK_CUE
        cue_ids = tuple(add((ROW_CUE, start + i * CUE_GAP), (v, mark, 0.5, CH3_INERT))
                        for i, v in enumerate(values))

        # distractores: en la fila opuesta, entre el último cue y las puertas
        dis_ids = tuple(
            add((ROW_ALT, door_col - demand.delay + 1 + i),
                (float(dis_rng.choice(CUE_VOCABULARY[1])), MARK_DISTRACTOR, 0.5, CH3_INERT))
            for i in range(demand.distractors))

        # puertas: iguales a la vista salvo que `hidden` sea False
        if novel:
            d_ch3 = CH3_GOOD if door_rng.random() < 0.5 else CH3_BAD
            o_ch3 = CH3_GOOD if door_rng.random() < 0.5 else CH3_BAD
        elif demand.risk:
            d_ch3 = CH3_GOOD if door_rng.random() < 0.5 else CH3_BAD
            o_ch3 = CH3_SAFE
        else:
            d_ch3, o_ch3 = CH3_GOOD, CH3_BAD
        d_ch2, o_ch2 = (0.5, 0.5) if demand.hidden else (0.9, 0.1)
        up_ch2, dn_ch2 = (d_ch2, o_ch2) if designated == "up" else (o_ch2, d_ch2)
        up_ch3, dn_ch3 = (d_ch3, o_ch3) if designated == "up" else (o_ch3, d_ch3)
        up_id = add((ROW_CUE, door_col), (0.5, MARK_DOOR, up_ch2, up_ch3))
        down_id = add((ROW_ALT, door_col), (0.5, MARK_DOOR, dn_ch2, dn_ch3))

        key.append(Station(j, door_col, cue_ids, values, dis_ids, up_id, down_id,
                           designated, d_ch3, o_ch3, novel))

    width = key[-1].door_column + VIEW_RADIUS + 2
    duration = 2 * width if duration is None else int(duration)
    inversion_step = (int(duration * demand.inversion)
                      if demand.inversion is not None else None)

    e = economy
    rules = _rules(e.gain, -e.loss, e.safe)
    scenario: dict[str, Any] = {
        "name": f"cdc_{seed}",
        "description": "cue → demora → elección; generado, no escrito",
        "generator": {"semantics": SEMANTICS_VERSION, "seed": seed,
                      "demand": {ax: getattr(demand, ax) for ax in AXES}},
        "grid_size": [width, 3],
        "duration": duration,
        "seed": seed,
        "view_radius": VIEW_RADIUS,
        "num_channels": NUM_CHANNELS,
        # El techo no puede morder al oráculo perfecto. Estos mundos son
        # INSTRUMENTOS: si el techo mordiera, las últimas estaciones valdrían
        # menos que las primeras y la energía dejaría de ser una medida lineal
        # del acierto. Medido con el techo plano de 60.0: un oráculo FULL sobre
        # 8 estaciones cobraba [7.85 ×5, 7.50, 1.20, 1.20] de los 7.85
        # declarados por acierto -- las tres últimas a una sexta parte.
        # `Economy.max_energy` queda como suelo, no como techo efectivo.
        "max_energy": max(e.max_energy, e.initial_energy + len(key) * e.gain),
        "step_energy_cost": e.step_energy_cost,
        "expose_time_fraction": True,
        "objects": objects,
        "agent_start": {"pos": [ROW_PATH, 0], "energy": e.initial_energy},
        "rules": rules,
        "changes": ([{"at_step": inversion_step, "rules": _rules(-e.loss, e.gain, e.safe)}]
                    if inversion_step is not None else []),
    }
    return GeneratedWorld(scenario, demand, economy, seed, tuple(key), inversion_step)


def _rules(good_delta: float, bad_delta: float, safe_delta: float) -> dict[str, Any]:
    """Tres reglas sobre el canal oculto. Los deltas entran ya con su signo:
    en el conjunto base `good` paga +gain y `bad` cobra −loss; invertido, al
    revés. `safe` no se invierte. Que cada puerta produzca el delta declarado
    lo comprueba `door_deltas` contra la física, no esta docstring."""
    return {"rules": [
        {"id": "door_good",
         "condition": {"object_channel": {"index": HIDDEN_CHANNEL, "min": 0.8},
                       "action": "CONSUME"},
         "effect": {"energy_delta": float(good_delta), "destroy_object": True}},
        {"id": "door_bad",
         "condition": {"object_channel": {"index": HIDDEN_CHANNEL, "max": 0.2},
                       "action": "CONSUME"},
         "effect": {"energy_delta": float(bad_delta), "destroy_object": True}},
        {"id": "door_safe",
         "condition": {"object_channel": {"index": HIDDEN_CHANNEL, "min": 0.45, "max": 0.55},
                       "action": "CONSUME"},
         "effect": {"energy_delta": float(safe_delta), "destroy_object": True}},
    ]}


def _validate(demand: Demand) -> None:
    if demand.delay < 1:
        raise ValueError("delay ≥ 1: el cue no puede ocupar la columna de las puertas")
    if demand.sequence not in CUE_VOCABULARY:
        raise ValueError(f"sequence ∈ {sorted(CUE_VOCABULARY)}")
    if demand.distractors and demand.distractors > demand.delay - 1:
        raise ValueError(f"{demand.distractors} distractores no caben en delay={demand.delay}; "
                         f"hacen falta delay ≥ {demand.distractors + 1}")
    if not 0.0 <= demand.novelty <= 1.0:
        raise ValueError("novelty ∈ [0, 1]")
    if demand.inversion is not None and not 0.0 < demand.inversion < 1.0:
        raise ValueError("inversion ∈ (0, 1) o None")


def world_for(capabilities: Iterable[str], *, seed: int, stations: int = 8,
              economy: Economy = DEFAULT_ECONOMY) -> GeneratedWorld:
    """El mundo que exige el conjunto entero."""
    caps=tuple(sorted(set(capabilities)))
    world=generate(demand_for(caps), seed=seed, stations=stations, economy=economy)
    return _with_capability_provenance(world,caps)


def control_for(capabilities: Iterable[str], capability: str, *, seed: int,
                stations: int = 8, economy: Economy = DEFAULT_ECONOMY) -> GeneratedWorld:
    """El mismo mundo con el eje de `capability` apagado.

    Dos igualdades, y las dos se comprueban en `tests/test_world_generator.py`:
    misma semilla ⇒ mismo contenido de estación en todo lo que el eje no toca
    (lo garantiza `_stream`), y misma duración ⇒ mismo presupuesto metabólico
    (lo garantiza fijar `duration` a la del mundo exigente). Sin la segunda,
    apagar `delay` o `sequence` acortaba el pasillo y con él la vida, y el
    contraste de memoria era a la vez un contraste de viabilidad.
    """
    caps = list(capabilities)
    if capability not in caps:
        raise ValueError(f"{capability} no está en {caps}")
    axis, _ = DEMAND_OF[capability]
    demanding = generate(demand_for(caps), seed=seed, stations=stations, economy=economy)
    world=generate(switch_off(demand_for(caps), axis), seed=seed,
                   stations=stations, economy=economy, duration=demanding.duration)
    return _with_capability_provenance(world,tuple(sorted(set(caps))),control_axis=axis)


def _with_capability_provenance(world: GeneratedWorld, capabilities: tuple[str,...],
                                *, control_axis: str | None = None) -> GeneratedWorld:
    """Attach origin metadata without changing diagnostic-world physics."""
    scenario=dict(world.scenario)
    generator=dict(scenario["generator"])
    generator.update({"capability_set":list(capabilities),
                      "merge_semantics":"terrario.lab.world_generator.merge/v1"})
    if control_axis is not None: generator["control_axis"]=control_axis
    scenario["generator"]=generator
    return replace(world,scenario=scenario,capabilities=capabilities)


# --- Puntuación -------------------------------------------------------------

@dataclass(frozen=True)
class Consumption:
    step: int
    object_id: int
    energy_before: float


@dataclass(frozen=True)
class Viability:
    """Lo que le pasó al organismo, no a sus aciertos.

    Ashby define la conducta adaptativa en S.5/3 como mantener las variables
    esenciales dentro de límites fisiológicos, y la supervivencia en S.3/15
    como «una línea de conducta que no saca ninguna variable esencial fuera de
    los límites dados». Esta es la única variable esencial que el motor tiene
    -- `AgentState.energy` -- y hasta ahora `Score` la tiraba: `life_score`
    recibía los `StepOutcome` con `terminated` y energía por paso y devolvía
    sólo aciertos. Medido sobre 420 vidas de oráculo, 7 vidas MUERTAS puntuaban
    accuracy 1.0, y en el mismo mundo la semilla 2 moría en el paso 61 con
    accuracy 1.0 mientras la 1 sobrevivía los 212 pasos con 0.6: la métrica
    ponía al cadáver por encima del superviviente.
    """

    steps_lived: int
    survived: bool
    final_energy: float
    min_energy: float
    steps_below_threshold: int = 0


def viability_from(world: "GeneratedWorld", outcomes: Sequence[Any]) -> Viability:
    """La viabilidad de una vida, leída de su traza de energía."""
    if not outcomes:
        return Viability(0, True, float(world.economy.initial_energy),
                         float(world.economy.initial_energy))
    energies = [float(o.observation_t.agent_energy) * world.economy.max_energy
                for o in outcomes]
    last = outcomes[-1]
    below = sum(1 for e in energies if e <= world.economy.low_energy)
    return Viability(len(outcomes), not bool(last.terminated),
                     energies[-1], min(energies), below)


@dataclass(frozen=True)
class Score:
    """Lo que el mundo puede decir de una vida, con la clave en la mano.

    Una DECISIÓN es la primera puerta consumida en una estación; la segunda no
    cuenta, y las estaciones novedosas se cuentan aparte porque en ellas no hay
    lado correcto. `accuracy` es None sin decisiones: un organismo que no llegó
    a ninguna estación no eligió mal, no eligió.
    """

    decisions: int
    correct: int
    before_inversion: tuple[int, int]
    after_inversion: tuple[int, int]
    safe_when_low: tuple[int, int]
    safe_when_high: tuple[int, int]
    novel_decisions: int
    #: None cuando la puntuación se calculó sin traza -- `score(world, cons)`
    #: no la puede saber. `world_oracles.life_score` sí la rellena.
    viability: Viability | None = None

    @property
    def accuracy(self) -> float | None:
        return self.correct / self.decisions if self.decisions else None

    @property
    def died(self) -> bool | None:
        """None si nadie midió la viabilidad. Un `accuracy` alto con `died`
        True no es un buen resultado: es una vida corta y afortunada."""
        return None if self.viability is None else not self.viability.survived

    @staticmethod
    def _rate(pair: tuple[int, int]) -> float | None:
        return pair[0] / pair[1] if pair[1] else None

    @property
    def accuracy_before(self) -> float | None:
        return self._rate(self.before_inversion)

    @property
    def accuracy_after(self) -> float | None:
        return self._rate(self.after_inversion)

    @property
    def modulation(self) -> float | None:
        """P(segura | energía baja) − P(segura | energía alta). Lo que la
        homeostasis debe producir y nada más produce."""
        low, high = self._rate(self.safe_when_low), self._rate(self.safe_when_high)
        return None if low is None or high is None else low - high


def score(world: GeneratedWorld, consumptions: Sequence[Consumption]) -> Score:
    decided: set[int] = set()
    scored = 0
    correct = 0
    before = [0, 0]
    after = [0, 0]
    low = [0, 0]
    high = [0, 0]
    novel = 0
    for c in sorted(consumptions, key=lambda c: c.step):
        st = world.station_of(c.object_id)
        if st is None or st.index in decided:
            continue
        decided.add(st.index)
        side = st.side_of(c.object_id)
        if st.novel:
            novel += 1
            continue
        scored += 1
        want = world.correct_side(st, c.step)
        ok = want is not None and side == want
        correct += ok
        bucket = after if world.inverted_at(c.step) else before
        bucket[0] += ok
        bucket[1] += 1
        if world.demand.risk:
            b = low if c.energy_before <= world.economy.low_energy else high
            b[0] += side != st.designated
            b[1] += 1
    return Score(scored, correct, tuple(before), tuple(after),
                 tuple(low), tuple(high), novel)


def consumptions_from(world: GeneratedWorld, outcomes: Iterable[Any]) -> list[Consumption]:
    """De una secuencia de `StepOutcome` a lo que `score` necesita. La
    observación trae la energía normalizada a [0, 1]; aquí vuelve a unidades."""
    out = []
    for o in outcomes:
        if o.target is not None and o.effects:
            out.append(Consumption(o.step, o.target.object_id,
                                   float(o.observation_t.agent_energy) * world.economy.max_energy))
    return out


# --- El contrato con el motor, comprobado ----------------------------------

def channel_3_is_hidden() -> bool:
    """Que el runtime real trunque el canal 3 con `NUM_CHANNELS = 4`. Si esto
    deja de ser cierto, todo mundo generado degenera en «lee la puerta»."""
    from terrario.world.transition import build_world_state
    from terrario.world.state import WorldStateManager

    probe = {"grid_size": [3, 3],
             "objects": [{"pos": [0, 1], "channels": [0.5, 0.5, 0.5, CH3_GOOD]}],
             "agent_start": {"pos": [1, 1], "energy": 10.0}}
    m = WorldStateManager(build_world_state(probe), 10, 10.0, 0.0, True)
    obs = m.get_observation(0, VIEW_RADIUS, NUM_CHANNELS)
    seen = obs.channels[:, VIEW_RADIUS - 1, VIEW_RADIUS]
    return seen.shape[0] == NUM_CHANNELS and float(seen[0]) == 1.0 and CH3_GOOD not in seen[1:].tolist()


def door_deltas(world: GeneratedWorld, *, step: int = 0) -> dict[str, float]:
    """El delta que la física produce al consumir cada tipo de puerta en
    `step`, medido con `RuleEngine` sobre el conjunto de reglas vigente. Es la
    comprobación de que la economía declarada es la ejecutada."""
    from terrario.world.transition import build_episode_components
    from terrario.core.types import Action, ActionType, Direction

    comps = build_episode_components(world.scenario, duration_fallback=world.duration,
                                     strict_physics=True, world_seed=world.seed)
    comps.scheduler.check(comps.world, step)
    out: dict[str, float] = {}
    for name, ch3 in (("good", CH3_GOOD), ("bad", CH3_BAD), ("safe", CH3_SAFE), ("inert", CH3_INERT)):
        probe = ObjectSpec(object_id=-1, pos=Position(0, 0),
                           channels=np.array([0.5, MARK_DOOR, 0.5, ch3], dtype=np.float32),
                           movable=False, energy_value=0.0, properties={})
        effects = comps.rules.evaluate(comps.world, 0, Action(ActionType.CONSUME, Direction.UP), probe)
        out[name] = float(sum(e.energy_delta for e in effects))
    return out
