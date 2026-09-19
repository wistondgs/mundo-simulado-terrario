"""Banco de sondas diagnósticas · medir el órgano sin dejar huella.

El criterio F1 anterior —«la ventaja cruza de negativo a positivo»— estaba mal
especificado: el modelo nace con un sesgo levemente positivo (+0.00099 medido
sobre 32 nacimientos), así que en la mayoría de los pares no hay nada que
cruzar. El instrumento contaba cruces y se perdía la señal: sobre esos mismos 32
la ventaja de NORMAL creció +0.00852 y la de FULL +0.00089, diez veces menos.

La magnitud correcta es la **ganancia**, medida sobre estados idénticos:

    G^A_i = Ventaja_post − Ventaja_pre          (por brazo A, por par i)
    ΔG_NF = G^N − G^F                            (el estimando de F1)

Y «estados idénticos» importa más de lo que parece. Si cada organismo se mide
sobre los estados que su propia trayectoria visitó, después de divergir
conductualmente las distribuciones de estado difieren y parte de la diferencia
de ventaja sería desplazamiento de distribución, no aprendizaje. Aquí los tres
brazos reciben **las mismas observaciones diagnósticas**, construidas del mundo
y no de la historia.

**Pasividad.** Sondar no puede cambiar lo sondado: ni el azar, ni el estado
recurrente, ni una sola pieza adaptativa. `passive_probe` toma instantánea de
todo lo que tocar una sonda podría mover y lo restituye al salir. La sonda
anterior de esta familia infló dos magnitudes ×18.6 y ×10 por contaminarse, y no
se vio hasta una verificación adversarial.
"""

from __future__ import annotations

import statistics
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Iterator, Mapping, Sequence

import torch

from terrario.core.types import NUM_DIRECTIONS, ActionType, TOTAL_ACTIONS
from terrario.world.state import WorldStateManager
from terrario.world.transition import build_world_state

PROBE_BANK_VERSION = "terrario.lab.diagnostic-probes/v1"

#: Campos que sondar puede mover. Ninguno es adaptativo -- son TRANSIENT por la
#: clasificación de `FRONTERA_ESTADO_APRENDIDO_01` -- pero moverlos cambiaría la
#: trayectoria posterior, así que la sonda los restituye.
_VOLATILE = ("_last_state", "_last_latent", "_last_log_prob", "_last_logits",
             "_last_probs", "_last_uncertainty", "_hidden", "_last_hidden",
             "_last_action", "_last_prediction", "last_prediction_error", "_step")


@contextmanager
def passive_probe(agent: Any) -> Iterator[None]:
    """Sondar sin dejar rastro: azar, recurrente y transitorios se restituyen."""
    rng_state = agent._generator.get_state().clone()
    saved: dict[str, Any] = {}
    for name in _VOLATILE:
        value = getattr(agent, name, None)
        saved[name] = value.detach().clone() if torch.is_tensor(value) else value
    homeostasis_energy = float(agent.homeostasis.energy)
    trace_length = len(getattr(agent, "_trace", []))
    try:
        yield
    finally:
        agent._generator.set_state(rng_state)
        for name, value in saved.items():
            setattr(agent, name, value)
        agent.homeostasis._energy = homeostasis_energy
        trace = getattr(agent, "_trace", None)
        if trace is not None and len(trace) > trace_length:
            del trace[trace_length:]


# --- Las situaciones diagnósticas -------------------------------------------

@dataclass(frozen=True)
class Probe:
    """Una situación, no una trayectoria. La misma para los tres brazos."""

    probe_id: str
    observation: Any
    favourable: bool
    rationale: str


def _observation(grid: int, radius: int, channels: int, agent_pos: Sequence[int],
                 food: Sequence[Sequence[int]]) -> Any:
    scenario = {
        "name": "probe", "grid_size": [grid, grid], "duration": 10, "seed": 0,
        "view_radius": radius, "num_channels": channels,
        "max_energy": 60.0, "step_energy_cost": 0.15, "expose_time_fraction": True,
        "objects": [{"pos": list(p), "channels": [0.9, 0.9, 0.9, 0.9],
                     "movable": False, "energy_value": 0.0} for p in food],
        "agent_start": {"pos": list(agent_pos), "energy": 30.0},
        "rules": {}, "changes": [],
    }
    manager = WorldStateManager(build_world_state(scenario), 10, 60.0, 0.15, True)
    return manager.get_observation(0, radius, channels)


def build_probe_bank(*, grid: int = 7, radius: int = 2, channels: int = 4) -> tuple[Probe, ...]:
    """Situaciones favorables y sus controles, en las cuatro direcciones.

    Favorables: hay recurso al alcance, así que CONSUME debería valer más que
    MOVE. Controles: no lo hay, y una ventaja alta ahí sería sesgo, no
    conocimiento -- es la especificidad de la medida.
    """
    centre = grid // 2
    probes: list[Probe] = []
    for name, delta in (("arriba", (-1, 0)), ("abajo", (1, 0)),
                        ("izquierda", (0, -1)), ("derecha", (0, 1))):
        food = [[centre + delta[0], centre + delta[1]]]
        probes.append(Probe(f"adyacente-{name}",
                            _observation(grid, radius, channels, [centre, centre], food),
                            True, "recurso en contacto: CONSUME debe valer más"))
    for distance in (2, 3):
        food = [[centre, min(centre + distance, grid - 1)]]
        probes.append(Probe(f"distancia-{distance}",
                            _observation(grid, radius, channels, [centre, centre], food),
                            False, "recurso fuera de alcance inmediato"))
    probes.append(Probe("vacio",
                        _observation(grid, radius, channels, [centre, centre], []),
                        False, "control sin recurso: la ventaja aquí sería sesgo"))
    return tuple(probes)


# --- La medición -------------------------------------------------------------

def _state_for(agent: Any, observation: Any) -> torch.Tensor | None:
    """El estado que ESTE organismo construye de esa observación.

    Se replica lo que `decide` hace para armar `s_t`, pero sin muestrear: el
    muestreo consume azar y la sonda tiene que ser pasiva. Que dos brazos con
    parámetros distintos produzcan estados distintos de la misma observación no
    es contaminación: es el órgano que se está midiendo.
    """
    with torch.no_grad():
        latent = agent.encoder.encode_observation(observation.channels)
        if getattr(agent, "_use_temporal", False):
            output, _ = agent.temporal_core(latent.unsqueeze(0), agent._hidden)
            hidden = output.squeeze(0)
        else:
            hidden = torch.zeros(agent.config["hidden_dim"],
                                 device=latent.device, dtype=latent.dtype)
        return agent._build_state(latent, hidden)


def consume_advantage_on(agent: Any, observation: Any) -> float:
    """`E[energía prevista | CONSUME] − E[energía prevista | MOVE]`, misma entrada."""
    state = _state_for(agent, observation)
    if state is None:
        return float("nan")
    with torch.no_grad():
        by_kind: dict[str, list[float]] = {"CONSUME": [], "MOVE": []}
        for action_int in range(TOTAL_ACTIONS):
            kind = ActionType(action_int // NUM_DIRECTIONS).name
            if kind not in by_kind:
                continue
            onehot = torch.zeros(TOTAL_ACTIONS, device=state.device, dtype=state.dtype)
            onehot[action_int] = 1.0
            _, energy_pred, _ = agent.world_model(state, onehot)
            by_kind[kind].append(float(energy_pred.item()))
    return statistics.fmean(by_kind["CONSUME"]) - statistics.fmean(by_kind["MOVE"])


@dataclass(frozen=True)
class ProbeReading:
    """Lo que el banco dice de un organismo en un momento."""

    by_probe: Mapping[str, float]
    favourable: float
    control: float

    @property
    def discrimination(self) -> float:
        """Favorables menos controles. Aprender que CONSUME paga SIEMPRE no es
        aprender: es sesgo. Lo que cuenta es la diferencia entre tener recurso
        al alcance y no tenerlo."""
        return self.favourable - self.control


def read_bank(agent: Any, bank: Sequence[Probe]) -> ProbeReading:
    with passive_probe(agent):
        values = {p.probe_id: consume_advantage_on(agent, p.observation) for p in bank}
    favourable = [values[p.probe_id] for p in bank if p.favourable]
    control = [values[p.probe_id] for p in bank if not p.favourable]
    return ProbeReading(values,
                        statistics.fmean(favourable) if favourable else float("nan"),
                        statistics.fmean(control) if control else float("nan"))


def gain(pre: ProbeReading, post: ProbeReading) -> dict[str, float]:
    """`G = post − pre`, en las tres magnitudes. El estimando de F1 es `ΔG_NF`
    sobre `discrimination`: no cuánto subió la valoración de CONSUME, sino
    cuánto mejoró la distinción entre tener recurso y no tenerlo."""
    return {
        "favourable": post.favourable - pre.favourable,
        "control": post.control - pre.control,
        "discrimination": post.discrimination - pre.discrimination,
    }
