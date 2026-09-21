"""Contratos de la vida · procedencia, continuidad y separación del banco POST."""

from __future__ import annotations

import numpy as np

from terrario.level16.life import ACQUISITION_STEPS, POST_STEPS, live
from terrario.level16.seeds import consume_seeds

SEMILLA = 140000011


def test_todos_los_actos_salieron_de_la_fuente_del_ser():
    """L16-1 medido, no asumido: tantas emisiones como pasos vividos."""
    vida = live(SEMILLA)
    assert vida.instruments.motor_emitted == ACQUISITION_STEPS + POST_STEPS
    assert len(vida.previous) == ACQUISITION_STEPS
    assert len(vida.post_previous) == POST_STEPS


def test_el_banco_post_continua_la_misma_vida_en_el_mismo_mundo():
    """Congelar y seguir: la primera observación del POST es la última vivida."""
    vida = live(SEMILLA)
    assert vida.post_previous[0] == vida.following[-1]


def test_la_misma_semilla_da_la_misma_vida_hasta_el_ultimo_bit():
    a, b = live(SEMILLA), live(SEMILLA)
    assert a.instruments.trajectory_hash == b.instruments.trajectory_hash
    assert a.post == b.post


def test_semillas_distintas_dan_vidas_distintas():
    huellas = {live(s, steps=256, post_steps=128).instruments.trajectory_hash
               for s in (140000011, 140000012, 140000013)}
    assert len(huellas) == 3


def test_la_vida_no_conoce_la_tabla():
    """Paridad estructural: si el cuerpo pudiera leer A1, la trayectoria podría
    depender de lo aprendido y habría que *imponer* la igualdad entre brazos en
    vez de demostrarla.

    Se camina el árbol sintáctico y no el texto. Un `grep` daría positivo contra
    esta misma docstring, que es el defecto que ya apareció cuatro veces en el
    linaje.
    """
    import ast
    import pathlib

    arbol = ast.parse(pathlib.Path("terrario/level16/life.py").read_text())
    importados = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            importados.update(alias.name for alias in nodo.names)
        elif isinstance(nodo, ast.ImportFrom):
            importados.add(nodo.module or "")
    assert not any("temporal" in nombre for nombre in importados), importados
    nombres = {n.id for n in ast.walk(arbol) if isinstance(n, ast.Name)}
    nombres |= {n.attr for n in ast.walk(arbol) if isinstance(n, ast.Attribute)}
    assert not (nombres & {"TemporalModel", "predict", "observe_pair", "counts"})


def test_lo_que_el_oraculo_predijo_del_mundo_se_cumple_en_las_vidas_reales():
    """§4 describía la población; aquí se comprueba sobre las 16 vidas reales.

    La banda sale de la dispersión de §4, no del resultado: la sd entre réplicas
    de 200 mundos es 0.0065, luego para una media de 16 vidas es
    `0.0065 * sqrt(200/16) = 0.023`, y se admiten cuatro de ésas. Ajustarla más
    convertiría el test en un acta de lo que salió.
    """
    libro = consume_seeds()
    vidas = [live(s, steps=1024, post_steps=256) for s in libro.lives]
    cambio = np.array([v.instruments.change_rate for v in vidas])
    movimiento = np.array([v.instruments.move_rate for v in vidas])
    assert 0.40 < cambio.mean() < 0.62, cambio.mean()
    assert 0.48 < movimiento.mean() < 0.68, movimiento.mean()
    assert all(v.instruments.reachable_observations >= 2 for v in vidas)
    assert all(v.instruments.changing_transitions > 0 for v in vidas)
