"""Contratos del Agente de Nivel 1 · lo que no puede cambiar sin avisar.

Cada uno fija algo que ya se midió y que, de romperse, haría que el experimento
midiera otra cosa sin fallar ruidosamente.
"""

from __future__ import annotations

import numpy as np
import pytest

from terrario.level1.measurement import (
    Experiment, brier, motor_babbling, movement_rate, situation_bank,
)
from terrario.level1.models import ContingencyTable, oracle_policy
from terrario.level1.world import (
    ALL_OBSERVATIONS, DELTA, Direction, Grid, physics_contract,
)

CFG = Experiment(train_layouts=8, train_steps_per_layout=32,
                 test_layouts=8, test_positions_per_layout=16)
SEED = 20260919


# --- GATE 0 · el contrato físico ---------------------------------------------

def test_the_sensed_bit_decides_the_movement_exactly():
    """`movido = 1 − bloqueado`, sin excepción. Es el GATE 0.

    Si esto deja de cumplirse el experimento no mide aprendizaje: mide un
    defecto de instrumentación, y hay que pararlo antes de analizar nada.
    """
    _, violations = motor_babbling(CFG, SEED)
    assert violations == 0


def test_direction_deltas_match_the_engine_vocabulary():
    """Mismos índices y mismos deltas que el motor del mundo grande.

    Si divergen, un resultado de aquí deja de significar lo mismo cuando el ser
    se mude allí, y la divergencia sería silenciosa.
    """
    assert [int(d) for d in Direction] == [0, 1, 2, 3]
    assert DELTA[Direction.UP] == (-1, 0)
    assert DELTA[Direction.DOWN] == (1, 0)
    assert DELTA[Direction.LEFT] == (0, -1)
    assert DELTA[Direction.RIGHT] == (0, 1)


# --- referencias analíticas ---------------------------------------------------

def test_the_ignorant_predictor_scores_exactly_one_quarter():
    """El congelado predice siempre 1/2 y el resultado es binario, luego
    `(1/2 − y)² = 0.25` siempre. No es una estimación: es el suelo analítico
    contra el que se lee todo lo demás."""
    frozen = ContingencyTable(frozen=True)
    bank = situation_bank(CFG, SEED, require_exit=False)
    score, total = brier(frozen, bank)
    assert total == 4 * len(bank)
    assert score == pytest.approx(0.25, abs=1e-12)


def test_freezing_blocks_the_write_not_the_computation():
    """El brazo congelado calcula lo mismo y no lo guarda. Es la diferencia
    entre bloquear y revertir."""
    frozen = ContingencyTable(frozen=True)
    before = frozen.predict((0, 0, 0, 0), Direction.UP)
    frozen.observe((0, 0, 0, 0), Direction.UP, 1)
    assert frozen.predict((0, 0, 0, 0), Direction.UP) == before == 0.5


def test_the_oracle_reaches_the_ceiling_exactly():
    """En toda situación con salida el oráculo se mueve. Si no da 1.0, el fallo
    es del mundo o de la medición, no del ser."""
    bank = situation_bank(CFG, SEED, require_exit=True)
    assert movement_rate(oracle_policy, bank, SEED) == pytest.approx(1.0, abs=1e-12)


# --- el límite del modelo, declarado ------------------------------------------

def test_an_unseen_pair_returns_the_prior_and_nothing_else():
    """Las celdas son independientes: un par nunca visto devuelve el prior.

    Este ser **no puede generalizar**, sólo memorizar, y por eso un resultado
    suyo no autoriza a decir «adquirió la regla». Medido sobre 32 semillas: el
    Brier de las observaciones retiradas sale `0.250000`, idéntico al del
    congelado.
    """
    table = ContingencyTable()
    for _ in range(500):
        table.observe((0, 0, 0, 0), Direction.UP, 1)
    assert table.predict((0, 0, 0, 0), Direction.UP) > 0.99
    assert table.predict((1, 1, 1, 1), Direction.UP) == 0.5
    assert table.predict((0, 0, 0, 0), Direction.DOWN) == 0.5


# --- los dos bancos no son el mismo -------------------------------------------

def test_the_two_banks_differ_exactly_in_the_enclosed_situations():
    """Filtrar las posiciones encerradas del Brier lo mejora sin que nadie haya
    aprendido nada: son las más raras y las peor aprendidas. Medido: bajaba de
    `0.000826` a `0.000070`."""
    every = situation_bank(CFG, SEED, require_exit=False)
    with_exit = situation_bank(CFG, SEED, require_exit=True)
    enclosed = [o for o in every if all(bit == 1 for bit in o)]
    assert len(every) - len(with_exit) == len(enclosed)
    assert all(any(bit == 0 for bit in o) for o in with_exit)


def test_every_sensory_configuration_is_reachable():
    """Las dieciséis aparecen. Por eso el gate de mundos no vistos no puede
    fallar por generalización: no queda ninguna observación fuera."""
    stream, _ = motor_babbling(Experiment(train_layouts=256), SEED)
    assert {t.observation for t in stream} == set(ALL_OBSERVATIONS)


# --- la sonda no altera lo sondado --------------------------------------------

def test_the_probe_leaves_no_trace_on_the_model():
    """Medir no puede cambiar lo medido: `brier` sólo lee."""
    table = ContingencyTable()
    stream, _ = motor_babbling(CFG, SEED)
    for tr in stream:
        table.observe(tr.observation, tr.direction, tr.moved)
    cells = table.visited_cells
    bank = situation_bank(CFG, SEED, require_exit=False)
    first, _ = brier(table, bank)
    second, _ = brier(table, bank)
    assert first == second
    assert table.visited_cells == cells


def test_relocating_never_lands_on_a_wall():
    rng = np.random.default_rng(SEED)
    grid = Grid.random(9, 0.3, rng)
    for _ in range(200):
        grid.relocate(rng)
        assert grid.cells[grid.position] == 0
        row, col = grid.position
        for d in Direction:
            expected = int(grid.cells[row + DELTA[d][0], col + DELTA[d][1]] == 1)
            assert grid.observe()[int(d)] == expected
            assert physics_contract(grid.observe(), d) == 1 - expected


# --- el ser que aprende por rasgos --------------------------------------------

def test_features_reach_an_unseen_situation_and_cases_do_not():
    """Una situación nunca vista, compuesta de bits sí vistos.

    El que aprende por CASOS devuelve el prior: su celda no existe. El que
    aprende por RASGOS la puntúa con estadística de otras situaciones que
    compartían bits. Ésa es la diferencia entre una tabla y una regla, y es el
    discriminador del experimento.
    """
    from terrario.level1.models import FactoredContingency

    stream, _ = motor_babbling(Experiment(train_layouts=64), SEED)
    held = (1, 1, 0, 0)
    cases, features = ContingencyTable(), FactoredContingency()
    for tr in stream:
        if tr.observation == held:
            continue
        cases.observe(tr.observation, tr.direction, tr.moved)
        features.observe(tr.observation, tr.direction, tr.moved)

    assert cases.predict(held, Direction.UP) == 0.5
    assert cases.predict(held, Direction.RIGHT) == 0.5
    # arriba está bloqueado en (1,1,0,0); derecha no.
    assert features.predict(held, Direction.UP) < 0.05
    assert features.predict(held, Direction.RIGHT) > 0.95


def test_neither_learner_writes_while_predicting():
    """Preguntar no puede cambiar al ser. Ninguno de los dos, ni el externo."""
    from terrario.level1.models import FactoredContingency, TabularQ

    cases, features, td = ContingencyTable(), FactoredContingency(), TabularQ()
    stream, _ = motor_babbling(CFG, SEED)
    for tr in stream:
        cases.observe(tr.observation, tr.direction, tr.moved)
        features.observe(tr.observation, tr.direction, tr.moved)
        td.observe(tr)

    sizes = (cases.visited_cells, features.visited_cells, len(td.q))
    rng = np.random.default_rng(SEED)
    for observation in ALL_OBSERVATIONS:
        for direction in Direction:
            cases.predict(observation, direction)
            features.predict(observation, direction)
        cases.act(observation, rng)
        features.act(observation, rng)
        td.act(observation, rng)
    assert (cases.visited_cells, features.visited_cells, len(td.q)) == sizes


def test_the_external_ceiling_is_also_a_table():
    """Q tabular indexa por observación completa: tampoco puede generalizar.

    Medido: sobre las cuatro situaciones retiradas, el techo externo da
    exactamente lo mismo que el brazo congelado y que el que aprende por casos.
    No es un defecto de la implementación: es lo que significa ser una tabla.
    """
    from terrario.level1.models import TabularQ

    td = TabularQ()
    stream, _ = motor_babbling(Experiment(train_layouts=64), SEED)
    held = (1, 1, 0, 0)
    for tr in stream:
        if tr.observation != held:
            td.observe(tr)
    assert held not in td.q
