"""Contratos de A1 · qué entra, qué no, y qué prueba que aprendió."""

from __future__ import annotations

import numpy as np
import pytest

from terrario.level1.world import ALL_OBSERVATIONS, Direction
from terrario.level16.temporal import PRIOR, TemporalContractError, TemporalModel

UNO, DOS = ALL_OBSERVATIONS[0], ALL_OBSERVATIONS[5]


def test_sin_experiencia_predice_uniforme_y_su_perdida_es_log_16():
    """El valor analítico del que cuelga el brazo FROZEN."""
    modelo = TemporalModel.naive()
    fila = modelo.predict(UNO)
    assert np.allclose(fila, 1 / 16)
    assert abs(-float(np.log(fila[0])) - float(np.log(16))) < 1e-12
    assert abs(float(np.log(16)) - 2.7726) < 1e-4


def test_contar_una_transicion_mueve_solo_su_celda():
    modelo = TemporalModel()
    antes = modelo.snapshot()
    modelo.observe(UNO, DOS)
    delta = modelo.snapshot() - antes
    assert delta.sum() == 1.0
    assert delta[0, 5] == 1.0


def test_el_prior_es_uno():
    assert PRIOR == 1.0
    assert np.all(TemporalModel().snapshot() == 1.0)


# --- la frontera: lo que A1 no puede recibir --------------------------------

@pytest.mark.parametrize("intruso, nombre", [
    (Direction.UP, "un acto"),
    (0, "un bit de cambio"),
    (1, "una copia eferente"),
    ((3, 4), "una posición"),
    ((0, 1, 0), "tres bits"),
    ((0, 1, 0, 2), "algo que no es un bit"),
    ([0, 1, 0, 1], "una lista"),
])
def test_a1_rechaza_todo_lo_que_no_sea_observacion(intruso, nombre):
    """Fixture negativa de L16-4, una por vía de fuga."""
    modelo = TemporalModel()
    with pytest.raises(TemporalContractError):
        modelo.observe(UNO, intruso)
    with pytest.raises(TemporalContractError):
        modelo.observe(intruso, UNO)


def test_predict_no_puede_insertar_estados_nuevos():
    """La tabla es de tamaño fijo: predecir no crea filas."""
    modelo = TemporalModel()
    with pytest.raises(TemporalContractError):
        modelo.predict((9, 9, 9, 9))
    assert modelo.snapshot().shape == (16, 16)


# --- congelado y estado ------------------------------------------------------

def test_congelada_no_admite_una_actualizacion_mas():
    """Fixture negativa de la separación adquisición/evaluación."""
    modelo = TemporalModel()
    modelo.observe(UNO, DOS)
    modelo.freeze()
    with pytest.raises(TemporalContractError):
        modelo.observe(UNO, DOS)
    assert modelo.updates == 1


def test_la_huella_distingue_haber_vivido_de_no_haberlo_hecho():
    virgen = TemporalModel()
    vivido = TemporalModel()
    vivido.observe(UNO, DOS)
    assert virgen.fingerprint() != vivido.fingerprint()
    assert virgen.fingerprint() == TemporalModel().fingerprint()


def test_sustituir_el_estado_no_toca_las_actualizaciones_vividas():
    """`load` es la intervención causal, no una forma de rehacer la vida."""
    modelo = TemporalModel()
    for _ in range(7):
        modelo.observe(UNO, DOS)
    aprendido = modelo.snapshot()
    modelo.load(TemporalModel.naive().snapshot())
    assert modelo.updates == 7
    assert np.allclose(modelo.predict(UNO), 1 / 16)
    modelo.load(aprendido)
    assert modelo.probability(UNO, DOS) > 1 / 16


def test_load_rechaza_un_estado_con_otra_forma():
    with pytest.raises(TemporalContractError):
        TemporalModel().load(np.ones((4, 4)))


def test_un_prior_no_positivo_no_define_prediccion():
    with pytest.raises(TemporalContractError):
        TemporalModel(prior=0.0)
