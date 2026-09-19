"""Contratos del carril externo · qué tiene que ser cierto para que compare.

La vecino más próximo (externo) sólo sirve si la única diferencia con el ser propio
es el mecanismo de aprendizaje. Cada test de aquí fija una de las formas en que
esa igualdad podría romperse en silencio: que reciba otra experiencia, que su
salida dependa del orden de inserción, que preguntarle la cambie, o que
añadirla mueva los números de los brazos que ya estaban.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

from terrario.level1.comparison import (
    NOT_REACHED, brier_by_pattern, checkpoints, exemplar_cost, learning_curve,
    n_star, seen_pairs,
)
from terrario.level1.external import FEATURE_WIDTH, NearestNeighborForwardModel, encode
from terrario.level1.measurement import (
    Experiment, brier, motor_babbling, situation_bank,
)
from terrario.level1.world import Direction

CFG = Experiment(train_layouts=8, train_steps_per_layout=32,
                 test_layouts=8, test_positions_per_layout=16)
SEED = 20260919


def _campaign():
    """El script de campaña, cargado como módulo para poder medirlo."""
    path = Path(__file__).resolve().parents[1] / "scripts" / "level1_sensorimotor_contingency.py"
    spec = importlib.util.spec_from_file_location("_level1_campaign", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["_level1_campaign"] = module
    spec.loader.exec_module(module)
    return module


# --- el estado inicial: no inventar conocimiento ------------------------------

def test_without_experience_the_answer_is_exactly_one_half():
    """Sin ejemplares no hay voto. `1/2` exacto, la misma condición
    epistemológica inicial que el prior `Beta(1,1)` del ser propio."""
    model = NearestNeighborForwardModel()
    for direction in Direction:
        assert model.predict((0, 0, 0, 0), direction) == 0.5
        assert model.predict((1, 1, 1, 1), direction) == 0.5


def test_one_exact_match_answers_with_that_outcome():
    model = NearestNeighborForwardModel()
    model.observe((0, 0, 0, 0), Direction.UP, 1)
    assert model.predict((0, 0, 0, 0), Direction.UP) == 1.0


def test_contradictory_exact_matches_average_to_one_half():
    """Dos ejemplares idénticos con resultados opuestos empatan a distancia 0.
    El voto es `1/2`, y no porque haya un prior: porque los vecinos discrepan."""
    model = NearestNeighborForwardModel()
    model.observe((0, 0, 0, 0), Direction.UP, 1)
    model.observe((0, 0, 0, 0), Direction.UP, 0)
    assert model.predict((0, 0, 0, 0), Direction.UP) == 0.5


# --- el empate, que es la decisión de protocolo -------------------------------

def test_every_tied_neighbour_votes_and_the_order_does_not_matter():
    """Con ocho bits binarios los empates son la norma. Si sólo votara uno, el
    resultado dependería del orden de inserción, que es azar de implementación
    entrando en el resultado por la puerta de atrás.
    """
    experiences = [((1, 0, 0, 0), Direction.UP, 0),
                   ((0, 1, 0, 0), Direction.UP, 1),
                   ((0, 0, 1, 0), Direction.UP, 1)]
    query = ((0, 0, 0, 0), Direction.UP)  # a distancia 1 de los tres

    forward = NearestNeighborForwardModel()
    for item in experiences:
        forward.observe(*item)
    backward = NearestNeighborForwardModel()
    for item in reversed(experiences):
        backward.observe(*item)

    assert forward.predict(*query) == pytest.approx(2 / 3)
    assert forward.predict(*query) == backward.predict(*query)


def test_a_nearer_neighbour_outvotes_a_crowd_of_farther_ones():
    """Sólo participan los de distancia MÍNIMA: un ejemplar exacto gana a
    cualquier número de vecinos a distancia mayor."""
    model = NearestNeighborForwardModel()
    for _ in range(20):
        model.observe((1, 1, 1, 1), Direction.UP, 0)
    model.observe((0, 0, 0, 0), Direction.UP, 1)
    assert model.predict((0, 0, 0, 0), Direction.UP) == 1.0


# --- la acción no es un número ordinal ----------------------------------------

def test_the_action_is_one_hot_so_no_two_actions_are_nearer_than_others():
    """Como entero ordinal, `UP=0` y `RIGHT=3` dirían que derecha está tres
    veces más lejos de arriba que abajo. Con one-hot todas las acciones
    distintas están a la misma distancia: exactamente 2 bits."""
    observation = (0, 0, 0, 0)
    vectors = {d: encode(observation, d) for d in Direction}
    assert all(len(v) == FEATURE_WIDTH for v in vectors.values())
    for a in Direction:
        for b in Direction:
            expected = 0 if a == b else 2
            assert int(np.count_nonzero(vectors[a] != vectors[b])) == expected


def test_changing_only_the_action_changes_the_prediction():
    """El acto entra en la distancia: dos consultas que sólo difieren en la
    dirección no pueden recuperar el mismo vecino como más próximo."""
    model = NearestNeighborForwardModel()
    model.observe((1, 0, 0, 0), Direction.UP, 0)
    model.observe((1, 0, 0, 0), Direction.RIGHT, 1)
    assert model.predict((1, 0, 0, 0), Direction.UP) == 0.0
    assert model.predict((1, 0, 0, 0), Direction.RIGHT) == 1.0


# --- la sonda no altera lo sondado --------------------------------------------

def test_predicting_never_mutates_the_model():
    """Medir no puede cambiar lo medido. Dos pasadas idénticas, y la memoria
    intacta: es el defecto que este proyecto ya pagó una vez."""
    model = NearestNeighborForwardModel()
    stream, _ = motor_babbling(CFG, SEED)
    for tr in stream:
        model.observe(tr.observation, tr.direction, tr.moved)
    items = model.memory_items
    bank = situation_bank(CFG, SEED, require_exit=False)
    first, _ = brier(model, bank)
    second, _ = brier(model, bank)
    assert first == second
    assert model.memory_items == items


def test_growing_the_store_does_not_change_any_answer():
    """La duplicación de capacidad es administración de memoria, no algoritmo:
    las respuestas no pueden depender de cuándo tocó crecer."""
    stream, _ = motor_babbling(CFG, SEED)
    small = NearestNeighborForwardModel(initial_capacity=1)
    large = NearestNeighborForwardModel(initial_capacity=4096)
    for tr in stream:
        small.observe(tr.observation, tr.direction, tr.moved)
        large.observe(tr.observation, tr.direction, tr.moved)
    bank = situation_bank(CFG, SEED, require_exit=False)
    assert small.memory_items == large.memory_items == len(stream)
    assert brier(small, bank) == brier(large, bank)


# --- la salida nativa se conserva ---------------------------------------------

def test_the_native_hard_label_is_kept_beside_the_probability():
    """El algoritmo externo produce una etiqueta dura. No alimenta Brier
    --mezclaría mecanismo con forma de salida-- pero no se oculta."""
    model = NearestNeighborForwardModel()
    model.observe((0, 0, 0, 0), Direction.UP, 1)
    model.observe((0, 0, 0, 0), Direction.UP, 0)
    model.observe((0, 0, 0, 0), Direction.UP, 1)
    assert model.predict((0, 0, 0, 0), Direction.UP) == pytest.approx(2 / 3)
    assert model.native_predict((0, 0, 0, 0), Direction.UP) == 1


# --- misma experiencia que el resto del banco ---------------------------------

def test_the_external_arm_receives_exactly_the_shared_stream():
    """El brazo nuevo no genera experiencia propia. Reconstruido aparte desde
    el mismo manoteo motor, tiene que dar el mismo número que dentro de la
    campaña -- si generase el suyo, no coincidiría."""
    campaign = _campaign()
    result = campaign.run_seed(CFG, SEED)

    stream, _ = motor_babbling(CFG, SEED)
    outside = NearestNeighborForwardModel()
    for tr in stream:
        outside.observe(tr.observation, tr.direction, tr.moved)
    bank = situation_bank(CFG, SEED + campaign.EVAL_OFFSET, require_exit=False)
    assert outside.memory_items == len(stream)
    assert brier(outside, bank)[0] == result.brier_external


def test_the_same_seed_gives_the_same_result_twice():
    campaign = _campaign()
    assert vars(campaign.run_seed(CFG, SEED)) == vars(campaign.run_seed(CFG, SEED))


# --- aislamiento: los brazos que ya estaban no se movieron --------------------

#: Medido en `cc562e0`, ANTES de añadir el carril externo. Si añadir un brazo
#: mueve un número de otro, la comparación deja de ser pareada y el experimento
#: mide la integración en vez del aprendizaje.
BASELINE_BEFORE_THE_COPY = {
    "violations": 0,
    "brier_cases": 0.050452116113, "brier_features": 0.006878054232,
    "brier_frozen": 0.25, "brier_permuted": 0.244462582855,
    "move_cases": 0.921875, "move_features": 1.0, "move_frozen": 0.546875,
    "move_permuted": 0.65625, "move_td": 0.921875, "move_oracle": 1.0,
    "traj_cases": 0.7578125, "traj_frozen": 0.5234375, "traj_permuted": 0.7890625,
    "held_brier_cases": 0.25, "held_brier_features": 0.019745948787,
    "held_move_cases": 0.55, "held_move_features": 1.0, "held_move_td": 0.55,
    "held_move_frozen": 0.55, "held_move_oracle": 1.0,
}


def test_adding_the_external_arm_moved_no_number_of_any_previous_arm():
    campaign = _campaign()
    measured = vars(campaign.run_seed(CFG, SEED))
    for field, expected in BASELINE_BEFORE_THE_COPY.items():
        assert round(float(measured[field]), 12) == expected, field


# --- los instrumentos añadidos ------------------------------------------------

def test_the_curve_starts_at_the_analytic_floor_for_every_mechanism():
    """Con cero experiencias todos valen exactamente `0.25`. Si alguno no lo
    hiciera, partiría con conocimiento que nadie le dio."""
    bank = situation_bank(CFG, SEED, require_exit=False)
    stream, _ = motor_babbling(CFG, SEED)
    curve = learning_curve(NearestNeighborForwardModel, stream, bank, (0, 16))
    assert curve[0] == (0, pytest.approx(0.25, abs=1e-12))


def test_the_checkpoints_cover_the_horizon_and_nothing_beyond():
    assert checkpoints(0) == (0,)
    assert checkpoints(10) == (0, 1, 2, 4, 8, 10)
    assert checkpoints(16) == (0, 1, 2, 4, 8, 16)
    assert max(checkpoints(8192)) == 8192


def test_a_curve_that_never_crosses_reports_not_reached():
    """No se extrapola: una curva que no cruzó el umbral no dice dónde lo
    habría cruzado."""
    assert n_star(((0, 0.25), (1, 0.30)), 0.01) == NOT_REACHED
    assert n_star(((0, 0.25), (1, 0.30), (2, 0.005)), 0.01) == 2


def test_the_two_generalisation_conditions_are_counted_apart():
    """G-A y G-B no son la misma pregunta, y una media sobre cero casos no es
    un cero: por eso cada una lleva su recuento."""
    stream, _ = motor_babbling(CFG, SEED)
    held = frozenset({(1, 1, 0, 0)})
    partial = [tr for tr in stream if tr.observation not in held]
    model = NearestNeighborForwardModel()
    for tr in partial:
        model.observe(tr.observation, tr.direction, tr.moved)
    bank = situation_bank(CFG, SEED, require_exit=False)
    split = brier_by_pattern(model, bank, seen_pairs(partial))
    assert split.known_count + split.novel_count == 4 * len(bank)
    assert split.novel_count > 0
    assert all((o, d) not in seen_pairs(partial)
               for o in held for d in Direction)


def test_the_cost_report_counts_exemplars_and_never_mutates():
    model = NearestNeighborForwardModel()
    stream, _ = motor_babbling(CFG, SEED)
    for tr in stream:
        model.observe(tr.observation, tr.direction, tr.moved)
    bank = situation_bank(CFG, SEED, require_exit=False)[:64]
    cost = exemplar_cost(model, bank)
    assert cost.units == len(stream) == model.memory_items
    assert cost.payload_bytes == len(stream) * (FEATURE_WIDTH + 1)
    assert cost.queries == 4 * len(bank)
    assert model.memory_items == len(stream)
