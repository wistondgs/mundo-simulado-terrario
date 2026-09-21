"""Contratos de K-SOMBRA y de la intervención causal."""

from __future__ import annotations

import ast
import pathlib

import numpy as np

from terrario.level16.arms import full
from terrario.level16.causal import probe
from terrario.level16.life import live
from terrario.level16.metrics import log_loss
from terrario.level16.seeds import consume_seeds
from terrario.level16.shadow import AnalyticShadow, teachability
from terrario.level16.temporal import TemporalModel
from terrario.level16.world import build_world

SEMILLA = 140000011


# --- K-SOMBRA ----------------------------------------------------------------

def test_la_sombra_es_una_distribucion_en_cada_fila():
    sombra = AnalyticShadow(build_world(SEMILLA))
    assert np.allclose(sombra.as_table().sum(axis=1), 1.0)


def test_la_sombra_es_el_suelo_y_el_ser_se_le_acerca():
    """Si el contador bajara del cálculo exacto, el cálculo estaría mal."""
    for semilla in consume_seeds().lives:
        vida = live(semilla, steps=2048, post_steps=512)
        suelo = log_loss(AnalyticShadow(build_world(semilla)), vida.post)
        aprendido = log_loss(full(vida), vida.post)
        assert suelo <= aprendido + 1e-9, (semilla, suelo, aprendido)
        assert aprendido - suelo < 0.35, (semilla, aprendido - suelo)


def test_la_sombra_no_mira_la_vida_ni_al_organismo():
    """L16-6: es instrumento científico, no un brazo ni un maestro."""
    arbol = ast.parse(pathlib.Path("terrario/level16/shadow.py").read_text())
    modulos = {n.module or "" for n in ast.walk(arbol) if isinstance(n, ast.ImportFrom)}
    modulos |= {a.name for n in ast.walk(arbol) if isinstance(n, ast.Import)
                for a in n.names}
    assert not any(x in m for m in modulos for x in ("life", "arms", "motor", "seeds"))


def test_construir_la_sombra_no_toca_la_vida():
    vida = live(SEMILLA, steps=512, post_steps=256)
    AnalyticShadow(build_world(SEMILLA))
    assert live(SEMILLA, steps=512, post_steps=256).instruments.trajectory_hash \
        == vida.instruments.trajectory_hash


def test_un_mundo_valido_tiene_nats_que_ensenar():
    """El discriminante entre N-EXPERIENCIA y N-PLASTICIDAD."""
    for semilla in consume_seeds().lives[:6]:
        vida = live(semilla, steps=512, post_steps=256)
        assert teachability(AnalyticShadow(build_world(semilla)), vida.post) > 0.3


# --- la intervención ---------------------------------------------------------

def test_quitar_el_estado_se_lleva_la_competencia_y_devolverlo_la_trae():
    vida = live(SEMILLA, steps=2048, post_steps=512)
    resultado = probe(full(vida), vida.post)
    assert resultado.state_is_causal
    assert abs(resultado.ablated - float(np.log(16))) < 1e-12
    assert resultado.restored == resultado.learned
    assert resultado.fingerprint_before == resultado.fingerprint_after


def test_un_ser_sin_estado_aprendido_no_pasa_la_prueba_causal():
    """Fixture negativa de L16-9: sin nada que ablacionar, nada cambia."""
    vida = live(SEMILLA, steps=512, post_steps=256)
    resultado = probe(TemporalModel.naive(), vida.post)
    assert resultado.ablated == resultado.learned
    assert not resultado.state_is_causal


def test_evaluar_es_pasivo():
    """L16-10: puntuar no actualiza, no cuenta y no consume actos."""
    vida = live(SEMILLA, steps=512, post_steps=256)
    modelo = full(vida)
    huella, actualizaciones = modelo.fingerprint(), modelo.updates
    for _ in range(3):
        log_loss(modelo, vida.post)
    assert modelo.fingerprint() == huella
    assert modelo.updates == actualizaciones
