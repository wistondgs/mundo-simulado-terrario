"""Contratos de la arquitectura de 1.7 · los dos invariantes y la frontera nueva."""

from __future__ import annotations

import ast
import pathlib

import numpy as np
import pytest

from terrario.level1.world import ALL_OBSERVATIONS, Direction
from terrario.level16.arms import full
from terrario.level16.life import live
from terrario.level16.temporal import TemporalModel
from terrario.level17.contingency import (
    ActionContingencyModel, ContingencyContractError,
)
from terrario.level17.efference import (
    CommandToken, EfferenceContractError, EfferenceCopy,
)
from terrario.level17.wiring import ActuatorWiring, wiring_stream

SEMILLA = 150000011      # banco de CALIBRACIÓN · las 160xxxxxx siguen ciegas


@pytest.fixture(scope="module")
def heredado():
    """Fase P: el mecanismo de 1.6 instanciado en ESTE mundo, y congelado."""
    return full(live(SEMILLA, steps=1024, post_steps=256))


# --- los dos invariantes ----------------------------------------------------

def test_invariante_de_nacimiento_M1_es_M0_para_toda_accion(heredado):
    """`C_17 = 0` ⇒ 1.7 predice exactamente lo que predecía 1.6."""
    modelo = ActionContingencyModel(heredado)
    for observacion in ALL_OBSERVATIONS:
        base = heredado.predict(observacion)
        for comando in CommandToken:
            fila = modelo.predict(observacion, EfferenceCopy(comando))
            assert np.array_equal(fila, base), (observacion, comando)


def test_invariante_de_lesion_devuelve_al_nivel_anterior_no_a_cero(heredado):
    """Lesionar 1.7 no destruye al ser: lo devuelve a 1.6, bit a bit."""
    modelo = ActionContingencyModel(heredado)
    vida = live(SEMILLA, steps=512, post_steps=128)
    generador = np.random.default_rng([SEMILLA, 77])
    for anterior, siguiente in zip(vida.previous, vida.following):
        comando = list(CommandToken)[int(generador.integers(4))]
        modelo.observe(anterior, EfferenceCopy(comando), siguiente)
    assert modelo.updates == len(vida.previous)

    # ha aprendido algo: ya no coincide con M_0
    distinto = any(
        not np.array_equal(modelo.predict(o, EfferenceCopy(c)), heredado.predict(o))
        for o in ALL_OBSERVATIONS for c in CommandToken)
    assert distinto

    modelo.lesion()
    for observacion in ALL_OBSERVATIONS:
        base = heredado.predict(observacion)
        for comando in CommandToken:
            assert np.array_equal(
                modelo.predict(observacion, EfferenceCopy(comando)), base)
    assert modelo.updates == len(vida.previous)     # la lesión no borra la historia


def test_el_componente_nuevo_no_toca_lo_heredado(heredado):
    modelo = ActionContingencyModel(heredado)
    huella = modelo.inherited_fingerprint
    vida = live(SEMILLA, steps=256, post_steps=64)
    for anterior, siguiente in zip(vida.previous, vida.following):
        modelo.observe(anterior, EfferenceCopy(CommandToken.A2), siguiente)
    assert modelo.inherited_is_intact()
    assert modelo.inherited_fingerprint == huella == heredado.fingerprint()


def test_M0_tiene_que_llegar_congelado():
    """Fixture negativa: si la fase predecesora sigue aprendiendo, una mejora de
    1.7 podría ser sólo que siguió aprendiendo mejor P(O'|O)."""
    with pytest.raises(ContingencyContractError):
        ActionContingencyModel(TemporalModel())


# --- la frontera del canal nuevo --------------------------------------------

@pytest.mark.parametrize("intruso", [
    Direction.UP, 0, 2, "A0", (0, 1, 0, 1), CommandToken.A0, None,
])
def test_la_copia_eferente_solo_admite_un_comando_opaco(intruso, heredado):
    modelo = ActionContingencyModel(heredado)
    with pytest.raises(ContingencyContractError):
        modelo.observe((0, 0, 0, 0), intruso, (0, 0, 0, 1))


def test_un_comando_que_no_es_token_no_construye_copia():
    with pytest.raises(EfferenceContractError):
        EfferenceCopy(Direction.UP)          # type: ignore[arg-type]
    with pytest.raises(EfferenceContractError):
        EfferenceCopy(0)                     # type: ignore[arg-type]


def test_la_copia_eferente_tiene_exactamente_un_campo():
    """El contrato es el tipo: no hay dónde escribir `moved` sin cambiarlo."""
    import dataclasses
    campos = [f.name for f in dataclasses.fields(EfferenceCopy)]
    assert campos == ["command"]


def test_el_token_no_se_puede_confundir_con_una_direccion():
    """`Enum` y no `IntEnum`: tipos disjuntos, sin comparación accidental."""
    assert CommandToken.A0 != Direction.UP
    assert not isinstance(CommandToken.A0, int)
    with pytest.raises(TypeError):
        _ = CommandToken.A0 < CommandToken.A1


def test_el_aprendiz_no_nombra_consecuencia(heredado):
    """AST, no texto: `contingency.py` no puede nombrar el resultado."""
    arbol = ast.parse(pathlib.Path("terrario/level17/contingency.py").read_text())
    nombres = {n.id for n in ast.walk(arbol) if isinstance(n, ast.Name)}
    nombres |= {n.attr for n in ast.walk(arbol) if isinstance(n, ast.Attribute)}
    nombres |= {a.arg for a in ast.walk(arbol) if isinstance(a, ast.arg)}
    prohibidos = {"moved", "movement", "succeeded", "success", "collision",
                  "collided", "displacement", "direction", "directions",
                  "position", "actuate", "grid", "cells", "reward", "value"}
    assert not (nombres & prohibidos), sorted(nombres & prohibidos)


# --- el cableado opaco ------------------------------------------------------

def test_el_cableado_no_altera_la_trayectoria_de_la_fase_predecesora():
    """`[semilla, 64]` es disjunto de mundo `0`, motor `1`, baraja `2`, nulas `3..10`."""
    antes = live(SEMILLA, steps=256, post_steps=64).instruments.trajectory_hash
    ActuatorWiring.sampled(SEMILLA)
    wiring_stream(SEMILLA).permutation(4)
    assert live(SEMILLA, steps=256, post_steps=64).instruments.trajectory_hash == antes


def test_el_cableado_es_una_biyeccion_y_las_24_son_alcanzables():
    vistas = set()
    for seed in range(150000011, 150000211):
        cableado = ActuatorWiring.sampled(seed)
        assert set(cableado.mapping) == set(Direction)
        vistas.add(cableado.mapping)
    assert len(vistas) == 24, len(vistas)


def test_actuar_e_invertir_son_consistentes():
    cableado = ActuatorWiring.sampled(SEMILLA)
    for comando in CommandToken:
        assert cableado.command_for(cableado.actuate(comando)) is comando


# --- el baseline que desconfunde --------------------------------------------

def test_no_action_ve_las_mismas_transiciones_y_no_el_comando():
    """`NO-ACTION` parte de `M_0^W` y sigue aprendiendo `P(o'|o)` en la fase A."""
    from terrario.level17.life import live_two_phase
    vida = live_two_phase(SEMILLA, 256, 512, post_steps=128)
    assert vida.no_action.updates == 512
    assert vida.no_action.frozen
    assert vida.inherited.updates == 256
    # partió del mismo sitio, pero ya no es el mismo modelo
    assert vida.no_action.fingerprint() != vida.inherited.fingerprint()
    assert vida.acquired.inherited_fingerprint == vida.inherited.fingerprint()


def test_en_el_mundo_gemelo_la_ventaja_contra_no_action_no_es_positiva():
    """Fixture del control: sin información de acción, más parámetros no compran.

    Contra `M_0^W` congelado la ventaja SÍ sale positiva (+0.075 a T_17=1024),
    y ésa es exactamente la confusión que este brazo existe para deshacer.
    """
    import terrario.level17.life as modulo
    from terrario.level17.efference import EfferenceCopy
    from terrario.level17.twin import MarginalisedBody, twin_stream

    real = modulo.build_world
    ventajas = []
    try:
        modulo.build_world = lambda s: MarginalisedBody(real(s), twin_stream(s))
        for seed in range(150000011, 150000019):
            vida = modulo.live_two_phase(seed, 512, 1024, post_steps=256)
            perdida = lambda f: -np.mean([np.log(f(a, k, c)) for a, k, c in vida.post])
            ventajas.append(
                perdida(lambda a, k, c: vida.no_action.probability(a, c))
                - perdida(lambda a, k, c: vida.acquired.probability(a, EfferenceCopy(k), c)))
    finally:
        modulo.build_world = real
    assert np.mean(ventajas) < 0.0, np.mean(ventajas)
