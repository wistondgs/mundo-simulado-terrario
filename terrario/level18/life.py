"""La ruta única de 1.8. Calibración y campaña recorren ESTO, no una copia.

En 1.7 el «13/13» se construyó en un script posterior a abrir las semillas, y en
1.8 acabamos de descubrir dos defectos que vivían en la ruta de medida mientras
81 tests seguían verdes. Las dos lecciones apuntan al mismo sitio: si la
calibración y la campaña recorren caminos distintos, lo auditado no es lo medido.

Una vida produce, sobre la MISMA evidencia del MISMO mundo, el log-loss de:

    C17-ONLY     el baseline continuo --sigue aprendiendo, Enmienda 01
    FIXED-DEPTH-1 retención de un tick SUMINISTRADA, sin aprender partición
    FULL          C18: el mecanismo halla su propia organización
    ORACLE        la situación verdadera · TECHO DIAGNÓSTICO, jamás objetivo

La lesión de merge es un BRAZO, no una bandera del learner: el learner queda
byte a byte como se congeló, y la lesión no puede alcanzar al brazo FULL.
"""
from __future__ import annotations

import time

import numpy as np

from terrario.level1.world import DELTA, Direction
from terrario.level16.motor import EndogenousMotor
from terrario.level16.temporal import OBSERVATION_INDEX, TemporalModel
from terrario.level16.world import build_world, motor_stream
from terrario.level17.contingency import ActionContingencyModel
from terrario.level17.efference import ALL_COMMANDS, EfferenceCopy
from terrario.level17.wiring import ActuatorWiring
from terrario.level18.predictive_state import PredictiveStateModel

PREDECESSOR = 4096          # P0 · heredado sellado de 1.7
CONTINGENCY = 1024          # P1 · heredado sellado de 1.7
POST = 2048                 # banco de evaluación


class ObservedModel(PredictiveStateModel):
    """Instrumentación pura: registra el marcador prequencial en el instante en
    que decide, y no altera ninguna decisión.

    Enmienda 05 §2. Sin esto, `refuted` sólo puede leerse DESPUÉS del paso, y
    para entonces `_favour` ya fue retirado: el único marcador disponible sería
    «¿fusionó?», que es la acción, y el gate mediría su propia definición.
    """

    def __init__(self, inherited_counts) -> None:
        super().__init__(inherited_counts)
        self.favour_at_collapse: dict[int, list[float]] = {}
        self.undone: set[int] = set()
        #: Episodios cuya contabilidad fue DESCARTADA por un re-split del mismo
        #: estado antes de que se resolvieran. No son refutados ni fusionados:
        #: no tienen estatus. Se cuentan y se reportan; no se esconden.
        self.orphaned: set[int] = set()

    def _refine(self, state: int) -> None:
        if self._children.get(state):
            for index, episode in enumerate(self._episodes):
                if (episode["parent"] == state and index not in self.undone
                        and index not in self.orphaned):
                    self.orphaned.add(index)
        super()._refine(state)

    def _collapse(self, state: int) -> None:
        if self._descendants(state):
            # CABLE 1 · la evidencia: cuánto valía el marcador prequencial.
            self.favour_at_collapse.setdefault(state, []).append(
                float(self._favour.get(state, float("nan"))))
            # CABLE 2 · la acción: qué episodio deja de existir. No se infiere de
            # los ids de los hijos, porque `born = max(prior) + 1` los RECICLA:
            # tras un colapso un split posterior reusa los mismos números y un
            # episodio deshecho parecería vivo.
            for index, episode in enumerate(self._episodes):
                if episode["parent"] == state and index not in self.undone:
                    self.undone.add(index)
        super()._collapse(state)


class MergeSuppressedModel(ObservedModel):
    """M1 de la Enmienda 05 · juzga igual, acumula el marcador igual, NO fusiona.

    Existe sólo para falsificar `L18-17`: si este mutante no pudiera construirse,
    el gate seguiría midiendo su propia definición.
    """

    def _collapse(self, state: int) -> None:
        return None


def observed_episodes(learner) -> list[dict]:
    """`refuted` y `merged` leídos por cables DISTINTOS.

    `refuted` viene del marcador prequencial --el favor en el momento de juzgar--
    y `merged` del cambio REAL de organización: los hijos ya no están vivos.
    """
    pending = {k: list(v) for k, v in
               getattr(learner, "favour_at_collapse", {}).items()}
    undone = getattr(learner, "undone", set())
    orphaned = getattr(learner, "orphaned", set())
    records = []
    for index, episode in enumerate(learner.episodes()):
        if index in orphaned:
            continue            # sin estatus · su cuenta la contabiliza `orphaned`
        parent = episode["parent"]
        if index in undone and pending.get(parent):
            favour = pending[parent].pop(0)
        else:
            favour = float(learner._favour.get(parent, 1.0))
        records.append({"refuted": favour <= 0.0, "merged": index in undone})
    return records


class ObservationHistoryModel(PredictiveStateModel):
    """O-HISTORY-ONLY · el mismo mecanismo, ciego al comando.

    Séptimo brazo de §7: estado construido SÓLO de observaciones. Se implementa
    tapándole el comando en la firma de entrada, no reescribiendo el mecanismo,
    para que la diferencia causal sea exactamente «usa la copia eferente o no».
    """

    def _advance(self, command: int, after: int) -> None:
        self._here = self._next_state(self._here, 0, after)

    def observe(self, previous, efference, following) -> None:
        super().observe(previous, EfferenceCopy(ALL_COMMANDS[0]), following)


class MergeDisabledModel(PredictiveStateModel):
    """El brazo lesionado. Separa igual; no puede deshacer nada."""

    def _judge_open_split(self, state, before, command, after) -> None:
        return None


def situations(grid):
    """Las situaciones VERDADERAS. Instrumento de medida; el learner no las ve."""
    reachable = {grid.position}
    stack = [grid.position]
    while stack:
        here, there = stack.pop()
        for direction in Direction:
            step = (here + DELTA[direction][0], there + DELTA[direction][1])
            if grid.cells[step] == 0 and step not in reachable:
                reachable.add(step)
                stack.append(step)
    ordered = sorted(reachable)
    return ordered, {c: i for i, c in enumerate(ordered)}


def _conditional_entropy(pairs) -> float:
    """H(X|Y) empírica en nats. `pairs` son (y, x)."""
    from collections import Counter
    joint = Counter(pairs)
    marginal = Counter(y for y, _ in pairs)
    total = float(len(pairs))
    accumulated = 0.0
    for (y, x), n in joint.items():
        accumulated -= (n / total) * np.log(n / marginal[y])
    return float(accumulated)


def live(seed: int, budget: int, *, merge: bool = True, trace: list | None = None,
         predecessor: int = PREDECESSOR, contingency: int = CONTINGENCY,
         post: int = POST) -> dict:
    grid = build_world(seed)
    wiring = ActuatorWiring.sampled(seed)
    motor = EndogenousMotor(motor_stream(seed))
    ordered, index = situations(grid)

    # --- P0 · 1.6 adquiere estructura temporal y se congela -------------------
    temporal = TemporalModel()
    observation = grid.observe()
    for _ in range(predecessor):
        command = ALL_COMMANDS[int(motor.next())]
        _, following = grid.step(wiring.actuate(command))
        temporal.observe(observation, following)
        observation = following
    temporal.freeze()

    # --- P1 · 1.7 adquiere contingencia de acción -----------------------------
    contingent = ActionContingencyModel(temporal)
    for _ in range(contingency):
        command = ALL_COMMANDS[int(motor.next())]
        _, following = grid.step(wiring.actuate(command))
        contingent.observe(observation, EfferenceCopy(command), following)
        observation = following

    table = (np.repeat(contingent._inherited[:, None, :], 4, axis=1) * 0.25
             + contingent.acquired_snapshot())

    # --- los cuatro brazos, misma masa heredada -------------------------------
    baseline = ActionContingencyModel(temporal)
    baseline.load_acquired(contingent.acquired_snapshot())
    depth_prior = {a: table / 4.0 for a in range(4)}
    depth_evidence = {a: np.zeros_like(table) for a in range(4)}
    oracle_prior = {index[c]: table / len(ordered) for c in ordered}
    oracle_evidence = {index[c]: np.zeros_like(table) for c in ordered}
    flat = np.full_like(table, table.sum() / table.size)
    learner = (ObservedModel if merge else MergeDisabledModel)(table)
    learner.begin()
    observation_only = ObservationHistoryModel(table)      # O-HISTORY-ONLY
    observation_only.begin()
    lesioned_prior = PredictiveStateModel(flat)            # C17-LESION
    lesioned_prior.begin()

    # --- P2 · T_18 · sólo aquí nace 1.8 ---------------------------------------
    last = 0
    max_states = len(learner.states())
    started = time.perf_counter()
    born_at: dict[int, int] = {}
    merged_at: dict[int, int] = {}
    for step in range(budget):
        command = ALL_COMMANDS[int(motor.next())]
        action = ALL_COMMANDS.index(command)
        standing = grid.position
        _, following = grid.step(wiring.actuate(command))
        before = OBSERVATION_INDEX[observation]
        after = OBSERVATION_INDEX[following]
        baseline.observe(observation, EfferenceCopy(command), following)
        learner.observe(observation, EfferenceCopy(command), following)
        observation_only.observe(observation, EfferenceCopy(command), following)
        lesioned_prior.observe(observation, EfferenceCopy(command), following)
        depth_evidence[last][before, action, after] += 1
        oracle_evidence[index[standing]][before, action, after] += 1
        last = action
        observation = following
        max_states = max(max_states, len(learner.states()))
        # Supervivencia observada DESDE FUERA: el learner no lleva reloj.
        for i, episode in enumerate(learner.episodes()):
            if i not in born_at:
                born_at[i] = step
            if episode["merged"] and i not in merged_at:
                merged_at[i] = step

    elapsed = time.perf_counter() - started

    # --- banco · nadie aprende aquí -------------------------------------------
    bank = []
    for _ in range(post):
        command = ALL_COMMANDS[int(motor.next())]
        standing = grid.position
        _, following = grid.step(wiring.actuate(command))
        bank.append((observation, command, following, last, index[standing]))
        last = ALL_COMMANDS.index(command)
        observation = following

    def loss(fn) -> float:
        return -float(np.mean([np.log(max(fn(*row), 1e-300)) for row in bank]))

    def supplied(prior, evidence, which):
        def fn(obs, command, nxt, previous_action, situation):
            key = previous_action if which == "depth" else situation
            weights = (prior[key][OBSERVATION_INDEX[obs], ALL_COMMANDS.index(command)]
                       + evidence[key][OBSERVATION_INDEX[obs],
                                       ALL_COMMANDS.index(command)])
            return weights[OBSERVATION_INDEX[nxt]] / weights.sum()
        return fn

    # El único brazo cuyo estado es recursivo: puntuar exige SEGUIRLO, y seguir
    # ocurre DESPUÉS de puntuar. Si se invirtiera, O_{t+1} predeciría O_{t+1}.
    learner.begin()
    def acquired(obs, command, nxt, previous_action, situation):
        state = learner._here
        value = learner.probability(obs, EfferenceCopy(command), nxt)
        learner.follow(EfferenceCopy(command), nxt)
        if trace is not None:
            trace.append({"t": len(trace), "O_t": OBSERVATION_INDEX[obs],
                          "A_t": ALL_COMMANDS.index(command), "Z_t": state,
                          "O_next": OBSERVATION_INDEX[nxt], "P18": value,
                          "Z_next": learner._here, "updates": learner.updates,
                          "splits": learner.refinements})
        return value

    l_full = loss(acquired)

    def tracking(model):
        def fn(obs, command, nxt, previous_action, situation):
            value = model.probability(obs, EfferenceCopy(command), nxt)
            model.follow(EfferenceCopy(command), nxt)
            return value
        return fn

    observation_only.begin()
    l_observation_only = loss(tracking(observation_only))
    lesioned_prior.begin()
    l_c17_lesion = loss(tracking(lesioned_prior))

    # --- lectura congelada de la organización ---------------------------------
    learner.begin()
    readout = []
    # (c) de la Enmienda 03 · hambre: pasos del banco que caen en una celda
    # `(estado, O_t, A_t)` sin NINGUNA evidencia, predichos sólo por el prior.
    hungry_full = 0
    hungry_depth = 0
    for obs, command, following, previous, situation in bank:
        o = OBSERVATION_INDEX[obs]
        a = ALL_COMMANDS.index(command)
        readout.append((o, learner._here, situation))
        if learner._evidence[learner._here][o, a].sum() == 0.0:
            hungry_full += 1
        if depth_evidence[previous][o, a].sum() == 0.0:
            hungry_depth += 1
        learner.follow(EfferenceCopy(command), following)

    states = learner.states()
    support = {z: float(learner._evidence[z].sum()) for z in states}
    cells = sum(int((learner._evidence[z].sum(axis=2) > 0).sum()) for z in states)
    starved = [z for z in states if support[z] == 0.0]
    inherited = {z: float(learner._prior[z].sum()) for z in states}
    total_prior = sum(inherited.values())

    episodes = learner.episodes()
    survival = [merged_at[i] - born_at[i] for i in range(len(episodes))
                if i in merged_at and i in born_at]

    learner.begin()
    h_c_o = _conditional_entropy([(o, c) for o, _z, c in readout])
    h_c_zo = _conditional_entropy([((o, z), c) for o, z, c in readout])
    return {
        "seed": seed, "budget": budget, "merge": merge,
        "l_c17": loss(lambda o, k, n, p, s: baseline.probability(
            o, EfferenceCopy(k), n)),
        "l_depth1": loss(supplied(depth_prior, depth_evidence, "depth")),
        "l_full": l_full,
        "l_oracle": loss(supplied(oracle_prior, oracle_evidence, "oracle")),
        "l_observation_only": l_observation_only,
        "l_c17_lesion": l_c17_lesion,
        "states": len(states), "max_states": max_states,
        "occupied": len({z for _o, z, _c in readout}),
        "splits": learner.refinements, "merges": learner.collapses,
        "first_split": born_at.get(0), "survival": survival,
        "reverted": sum(1 for e in episodes if e["merged"]),
        "updates": learner.updates,
        "cells_supported": cells, "cells_total": 16 * 4 * len(states),
        "signatures": sum(len(learner._arrivals[z]) for z in states),
        "support": sorted(support.values()),
        "starved": len(starved),
        "starved_mass": (sum(inherited[z] for z in starved) / total_prior
                         if total_prior else 0.0),
        "dangling": len(learner.dangling_routes()),
        "hungry_full": hungry_full / len(bank),
        "hungry_depth": hungry_depth / len(bank),
        "seconds": elapsed,
        "cells_held": sum(
            int(a.size) for store in (learner._prior, learner._evidence,
                                      learner._shadow, learner._collapsed_prior)
            for a in store.values())
        + sum(int(p.size) for z in states for p in learner._incoming[z].values()),
        "situations": len(ordered),
        "h_c_o": h_c_o, "h_c_zo": h_c_zo,
        "h_z_co": _conditional_entropy([((o, c), z) for o, z, c in readout]),
        "readout": readout,
    }
