"""Contratos de los brazos · paridad, destrucción real y el control que no compite arriba."""

from __future__ import annotations

import numpy as np
import pytest

from terrario.level16.arms import (
    StaticBitcount, audit_shuffle, frozen, full, temporal_shuffled,
)
from terrario.level16.life import live
from terrario.level16.metrics import (
    PrimaryMetricNotApplicable, brier_change, log_loss,
)
from terrario.level16.seeds import consume_seeds
from terrario.level16.temporal import OBSERVATION_INDEX

SEMILLA = 140000011


def test_el_brazo_congelado_pierde_exactamente_log_16():
    """Valor analítico: sin experiencia, las dieciséis son equiprobables."""
    vida = live(SEMILLA, steps=512, post_steps=256)
    assert abs(log_loss(frozen(vida), vida.post) - float(np.log(16))) < 1e-12
    assert frozen(vida).updates == 0
    assert frozen(vida).frozen


def test_los_tres_brazos_comparten_la_vida_entera():
    """Paridad: no hay nada que igualar porque nunca se separó."""
    vida = live(SEMILLA, steps=512, post_steps=256)
    brazos = [full(vida), frozen(vida), temporal_shuffled(vida)]
    assert all(m.frozen for m in brazos)
    assert full(vida).updates == len(vida.previous)
    assert temporal_shuffled(vida).updates == len(vida.previous)
    # construir los brazos no toca la vida: volver a vivirla da la misma huella
    assert live(SEMILLA, steps=512, post_steps=256).instruments.trajectory_hash \
        == vida.instruments.trajectory_hash


def test_barajar_conserva_los_marginales_y_rompe_el_emparejamiento():
    vida = live(SEMILLA, steps=1024, post_steps=256)
    aprendido, barajado = full(vida), temporal_shuffled(vida)
    assert np.allclose(aprendido.snapshot().sum(axis=0),
                       barajado.snapshot().sum(axis=0))
    assert np.allclose(aprendido.snapshot().sum(axis=1),
                       barajado.snapshot().sum(axis=1))
    assert not np.allclose(aprendido.snapshot(), barajado.snapshot())


def test_la_destruccion_se_mide_y_las_coincidencias_de_valor_no_son_defecto():
    vida = live(SEMILLA, steps=2048, post_steps=256)
    auditoria = audit_shuffle(vida, full(vida), temporal_shuffled(vida))
    assert auditoria.destructive
    assert auditoria.shuffled_distance_to_marginal < 0.2
    assert auditoria.full_distance_to_marginal > 0.4
    assert auditoria.fixed_points <= 6          # esperanza 1, Poisson
    # las coincidencias de valor son el alfabeto, no la baraja
    assert abs(auditoria.value_coincidences
               - auditoria.expected_coincidences) < 4 * np.sqrt(
                   auditoria.expected_coincidences)


def test_una_baraja_que_no_baraja_no_pasa_la_auditoria(monkeypatch):
    """Fixture negativa de SHUFFLE_NOT_DESTRUCTIVE."""
    import terrario.level16.arms as modulo

    class Identidad:
        @staticmethod
        def permutation(n):
            return np.arange(n)

    vida = live(SEMILLA, steps=1024, post_steps=256)
    monkeypatch.setattr(modulo, "shuffle_stream", lambda _seed: Identidad())
    falso = modulo.temporal_shuffled(vida)
    auditoria = modulo.audit_shuffle(vida, full(vida), falso)
    assert auditoria.fixed_points == len(vida.previous)
    assert not auditoria.destructive


# --- el control estático ----------------------------------------------------

def test_el_bitcount_no_puede_entrar_en_el_endpoint_primario():
    """Estructural, no una regla escrita: no tiene distribución que ofrecer."""
    vida = live(SEMILLA, steps=512, post_steps=256)
    control = StaticBitcount.fitted(vida)
    assert not hasattr(control, "probability")
    with pytest.raises(PrimaryMetricNotApplicable):
        log_loss(control, vida.post)


def test_el_bitcount_si_compite_en_la_metrica_secundaria():
    """Y ésa es la razón de que la secundaria sea secundaria."""
    vida = live(SEMILLA, steps=2048, post_steps=512)
    control = StaticBitcount.fitted(vida)
    assert 0.0 <= control.beta <= 1.2
    assert brier_change(control, vida.post) < 0.25      # mejor que la constante
    assert abs(brier_change(control, vida.post)
               - brier_change(full(vida), vida.post)) < 0.02


# --- el contraste que el nivel afirma ---------------------------------------

def test_full_gana_a_frozen_y_a_shuffled_en_las_semillas_de_la_campana():
    vidas = [live(s, steps=1024, post_steps=512) for s in consume_seeds().lives]
    perdidas = [(log_loss(full(v), v.post), log_loss(frozen(v), v.post),
                 log_loss(temporal_shuffled(v), v.post)) for v in vidas]
    contra_frozen = np.array([z - f for f, z, _ in perdidas])
    contra_shuffled = np.array([s - f for f, _, s in perdidas])
    assert (contra_frozen > 0).all()
    assert contra_shuffled.mean() > 0
    assert (contra_shuffled > 0).sum() >= 15
