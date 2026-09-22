"""N1.0 · el aparato, antes de que exista ningún organismo que aprenda.

What N1.0 asks is whether an acquired history can govern a present decision
under an observably identical present.  Nothing here learns anything; this
module is the bench that would make such a claim checkable, and it is built
first on purpose, because an instrument assembled after the result is an
instrument shaped by it.

Four things are structural rather than documented.

**The channel contract is about the schema, not about a value.**  The guard it
replaces asked whether the float `0.9` appeared in the window, which is exact
float equality against a value that has round-tripped through `float32`:
`float(np.float32(0.9))` is `0.8999999761581421`, so the check could never
fail.  Measured with five channels, the doors were visibly different --
`[…, 0.5, 0.1]` against `[…, 0.5, 0.9]` -- and it still reported them hidden.
What matters is not the value but whether the physics channel that encodes the
answer is inside the observable schema at all.

**The history label comes from the world, never from the organism.**  A probe
written before this module read the token from the oracle's own memory, which
in the lesioned arm is empty by construction: every row came back unlabelled
and a gate would have compared nothing against nothing.  Stations carry their
cue values and their designated side in `GeneratedWorld.key`, decided when the
world was generated, and that is the only admissible source.

**Energy is restored between decisions, and it is declared as an intervention
on the apparatus.**  A world that pays for the right door teaches, and the
payment lands in the visible energy, so the next present is no longer the same
one -- measured, the informative economy gives 32 distinct observations across
32 decisions and none of them holds both histories.  A world that pays nothing
keeps one single present and teaches nothing.  So the consequence is delivered
to `learn` and *then* the apparatus puts the energy back, after the learning
and before the next observation.  This is not a mechanism of the organism and
is not described as one.

**The order of those two is itself a contract.**  Restoring before `learn`
would hand the learner a consequence the apparatus had already erased, so
there is a test that builds exactly that and requires it to be caught.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Callable, Iterable, Mapping, Sequence

import numpy as np

from terrario.core.types import ActionType, Direction, Observation
from terrario.lab import world_generator as gen
from terrario.world.transition import build_episode_components, run_step

SCHEMA_VERSION = "terrario.lab.n10-instrument/v1"
OBSERVATION_SIGNATURE_VERSION = "n10.observation-signature/v1"

#: Los canales de objeto que el motor expone. `get_observation` escribe
#: `channels[1 : 1 + min(4, num_channels - 1)]`, así que con cuatro canales
#: quedan visibles los de objeto 0, 1 y 2, y el 3 no.
MAX_OBJECT_CHANNELS = 4

#: El canal de objeto donde vive la física que decide la consecuencia de una
#: puerta. No es un percepto: lo lee `RuleEngine` y nadie más.
ANSWER_OBJECT_CHANNEL = 3

#: Con `hidden=True` el canal de objeto 2 se iguala entre las dos puertas, de
#: modo que el único discriminador físico es el 3.
DISCRIMINATING_OBJECT_CHANNEL_WHEN_HIDDEN = 2


class InstrumentRefused(ValueError):
    """Algo que el aparato no sostiene, y por qué."""


class GateResult(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    INVALID = "INVALID"


# --- FASE 1 · el contrato de canales, por estructura ------------------------

def observable_object_channels(num_channels: int) -> tuple[int, ...]:
    """Qué canales de objeto llegan de verdad a `Observation.channels`."""
    if num_channels < 1:
        raise InstrumentRefused(f"num_channels={num_channels} no deja ni ocupación")
    return tuple(range(min(MAX_OBJECT_CHANNELS, num_channels - 1)))


def answer_bearing_channels(demand: Any) -> tuple[int, ...]:
    """Los canales de objeto que codifican la respuesta en este mundo.

    Con `hidden=False` el canal 2 la lleva a la vista y el mundo no está
    aliased en absoluto; con `hidden=True` sólo la lleva el 3.
    """
    if getattr(demand, "hidden", True):
        return (ANSWER_OBJECT_CHANNEL,)
    return (DISCRIMINATING_OBJECT_CHANNEL_WHEN_HIDDEN, ANSWER_OBJECT_CHANNEL)


def check_channel_contract(world: Any) -> Mapping[str, Any]:
    """`answer_channels ∩ observable_channels = ∅`, o el experimento no existe.

    Se lee la clave del escenario y no el global del módulo: subir
    `gen.NUM_CHANNELS` después de generar el mundo no cambia lo que este
    escenario declara, y subir la clave sí.
    """
    declarado = int(world.scenario.get("num_channels", MAX_OBJECT_CHANNELS))
    visibles = observable_object_channels(declarado)
    respuesta = answer_bearing_channels(world.demand)
    fuga = tuple(sorted(set(visibles) & set(respuesta)))
    return {"num_channels": declarado, "observable_object_channels": list(visibles),
            "answer_bearing_channels": list(respuesta),
            "leaking_channels": list(fuga),
            "result": (GateResult.FAIL if fuga else GateResult.PASS).value,
            "code": "OBSERVATIONAL_ALIASING_VIOLATED" if fuga else ""}


def require_channel_contract(world: Any) -> None:
    informe = check_channel_contract(world)
    if informe["result"] != GateResult.PASS.value:
        raise InstrumentRefused(
            f"{informe['code']}: con num_channels={informe['num_channels']} el "
            f"canal de objeto {informe['leaking_channels']} llega a la "
            f"observación y lleva la respuesta. No se trunca en ejecución para "
            f"salvar el experimento")


# --- FASE 2 · la firma observable -------------------------------------------

def observation_fields() -> tuple[str, ...]:
    return tuple(f.name for f in dataclasses.fields(Observation))


def observation_signature(obs: Observation) -> str:
    """`obs_hash`, reutilizado tras comprobar que cubre la observación entera.

    No se crea un hash nuevo: el del motor ya cubre los cuatro campos, y
    duplicarlo daría dos respuestas a una pregunta. Lo que sí se comprueba es
    que sigan siendo cuatro -- un campo añadido a `Observation` que el hash no
    mirase haría el gate de mismo-presente más laxo sin que nada avisara.
    """
    campos = observation_fields()
    if campos != ("channels", "mask", "agent_energy", "time_fraction"):
        raise InstrumentRefused(
            f"Observation ya no tiene los cuatro campos que obs_hash cubre: "
            f"{campos}. El gate de SAME_PRESENT dejaría de ver algo que el "
            f"organismo sí ve")
    return obs.obs_hash()


# --- FASE 3/4 · la normalización de aparato ---------------------------------

@dataclass(frozen=True)
class ApparatusNormalization:
    """Devolver la energía a su línea base entre oportunidades de decisión.

    Es una intervención sobre el aparato y se declara como tal. Ocurre después
    de `learn`, nunca antes: el orden es lo que separa «la consecuencia llegó y
    después se repuso el estado» de «se repuso el estado y el aprendiz no vio
    nada».
    """

    enabled: bool = False
    baseline_energy: float = 0.0
    #: Sólo para el mutante de la fase 5: repone ANTES de learn y debe cazarse.
    before_learn: bool = False

    def as_record(self) -> Mapping[str, Any]:
        return {"apparatus_energy_normalization": self.enabled,
                "baseline_energy": self.baseline_energy,
                "applied_before_learn": self.before_learn,
                "kind": "APPARATUS_INTERVENTION"}


# --- el registro por decisión -----------------------------------------------

@dataclass(frozen=True)
class DecisionRow:
    run_id: str
    seed: int
    arm: str
    station_id: int
    decision_id: int
    step: int
    #: Verdad del mundo. NUNCA de la memoria del organismo.
    history_id: str
    correct_action: str
    chosen_action: str
    obs_hash: str
    energy_visible: float
    consequence: float | None

    @property
    def correct(self) -> bool:
        return self.chosen_action == self.correct_action

    def as_record(self) -> Mapping[str, Any]:
        return dataclasses.asdict(self)


def history_of(station: Any) -> str:
    """La etiqueta de historia, decidida al generar el mundo."""
    return "|".join(f"{v:.2f}" for v in station.cue_values)


def ground_truth(world: Any) -> Mapping[int, Any]:
    """Estaciones por columna de puerta, tal como el generador las selló."""
    return {st.door_column: st for st in world.stations}


# --- el runner de N1.0 ------------------------------------------------------

def n1_run(world: Any, agent: Any, *, arm: str, seed: int = 0,
           learning_enabled: bool = False,
           normalization: ApparatusNormalization = ApparatusNormalization(),
           token_source: Callable[[int, str], Any] | None = None,
           run_id: str = "n1") -> tuple[DecisionRow, ...]:
    """Una vida, registrada por decisión, con la normalización declarada.

    Deliberadamente NO es `run_life`: aquél fija `learning_enabled=False` como
    literal y cambiar su significado movería campañas históricas. Éste es el
    carril experimental de N1.0 y dice en su firma lo que hace.

    `token_source(decision_id, history_id)` es el brazo C: sustituye el token
    que el organismo puede leer sin tocar el mundo, la consecuencia ni los
    parámetros aprendidos.
    """
    require_channel_contract(world)
    comps = build_episode_components(world.scenario, duration_fallback=world.duration,
                                     strict_physics=True, with_lifecycle=False,
                                     world_seed=world.seed)
    estaciones = ground_truth(world)
    filas: list[DecisionRow] = []

    for step in range(world.duration):
        estado = comps.world._mutable_state()
        # `Position` es (x, y) y el generador coloca por (fila, columna), así
        # que la columna del pasillo es `y`.
        columna = estado.agents[0].pos.y
        estacion = estaciones.get(columna)
        pendiente: dict[str, Any] | None = None

        if estacion is not None:
            obs = comps.world.get_observation(0, comps.view_radius, comps.num_channels)
            pendiente = {"station": estacion, "obs_hash": observation_signature(obs),
                         "energy": round(float(obs.agent_energy), 9), "step": step}
            if token_source is not None and hasattr(agent, "override_token"):
                agent.override_token(token_source(len(filas), history_of(estacion)))

        if normalization.enabled and normalization.before_learn:
            comps.world.set_agent_energy(0, normalization.baseline_energy)

        out = run_step(comps, agent, step, world_seed=world.seed, agent_seed=seed,
                       max_steps=world.duration, learning_enabled=learning_enabled)

        # Después de learn, nunca antes. El orden es el contrato.
        if normalization.enabled and not normalization.before_learn:
            comps.world.set_agent_energy(0, normalization.baseline_energy)

        if pendiente is not None and out.action.action_type is ActionType.CONSUME:
            est = pendiente["station"]
            elegido = "up" if out.action.direction is Direction.UP else "down"
            filas.append(DecisionRow(
                run_id=run_id, seed=seed, arm=arm, station_id=est.index,
                decision_id=len(filas), step=pendiente["step"],
                history_id=history_of(est), correct_action=est.designated,
                chosen_action=elegido, obs_hash=pendiente["obs_hash"],
                energy_visible=pendiente["energy"],
                consequence=round(float(out.energy_delta), 6)))

        if out.terminated or out.truncated:
            break
    return tuple(filas)


# --- FASE 9 · SAME_PRESENT --------------------------------------------------

def same_present(rows: Sequence[DecisionRow]) -> Mapping[str, Any]:
    """Identidad observable exacta, no un clasificador en azar.

    Cuando la igualdad puede demostrarse, demostrarla es mejor que estimarla;
    el decodificador queda como detector secundario para cuando no pueda.
    """
    if not rows:
        return {"result": GateResult.INVALID.value, "code": "NO_DECISIONS",
                "n_decisions": 0, "n_obs_hash": 0, "histories_per_hash": {}}
    por_hash: dict[str, set[str]] = {}
    for r in rows:
        por_hash.setdefault(r.obs_hash, set()).add(r.history_id)
    historias = {h for r_ in rows for h in (r_.history_id,)}
    if len(historias) < 2:
        return {"result": GateResult.INVALID.value, "code": "SINGLE_HISTORY_CLASS",
                "n_decisions": len(rows), "n_obs_hash": len(por_hash),
                "histories_per_hash": {k: sorted(v) for k, v in por_hash.items()}}
    mezclados = {k: sorted(v) for k, v in por_hash.items() if len(v) > 1}
    return {"result": (GateResult.PASS if mezclados else GateResult.FAIL).value,
            "code": "" if mezclados else "NO_HASH_HOLDS_TWO_HISTORIES",
            "n_decisions": len(rows), "n_obs_hash": len(por_hash),
            "n_histories": len(historias),
            "histories_per_hash": {k: sorted(v) for k, v in por_hash.items()},
            "mixed_hashes": mezclados}


# --- FASE 10/11 · el brazo C ------------------------------------------------

def shuffled_tokens(rows: Sequence[DecisionRow], *, seed: int) -> Mapping[int, str]:
    """Permutación determinista de los tokens, sellada por semilla propia.

    Conserva el multiconjunto de historias y rompe la correspondencia. Usa su
    propio generador: tomarlo del mundo acoplaría el brazo C al sorteo de las
    estaciones y dejaría de variar una sola cosa.
    """
    etiquetas = [r.history_id for r in rows]
    rng = np.random.default_rng(seed)
    orden = list(rng.permutation(len(etiquetas)))
    barajado = {i: etiquetas[j] for i, j in enumerate(orden)}
    if len(set(etiquetas)) > 1 and barajado == {i: e for i, e in enumerate(etiquetas)}:
        # Una permutación que no permuta no es un control; se busca otra antes
        # de devolver un brazo C que no interviene en nada.
        for intento in range(1, 64):
            rng2 = np.random.default_rng(seed * 1000 + intento)
            orden = list(rng2.permutation(len(etiquetas)))
            barajado = {i: etiquetas[j] for i, j in enumerate(orden)}
            if barajado != {i: e for i, e in enumerate(etiquetas)}:
                break
        else:
            raise InstrumentRefused(
                "no se encontró permutación que rompiera la correspondencia; "
                "un brazo C que no baraja nada no es un control")
    return barajado


def shuffle_report(rows: Sequence[DecisionRow], *, seed: int) -> Mapping[str, Any]:
    from collections import Counter
    barajado = shuffled_tokens(rows, seed=seed)
    original = {i: r.history_id for i, r in enumerate(rows)}
    return {"marginals_preserved":
                Counter(original.values()) == Counter(barajado.values()),
            "correspondence_broken": original != barajado,
            "n": len(rows),
            "deterministic": barajado == dict(shuffled_tokens(rows, seed=seed))}
