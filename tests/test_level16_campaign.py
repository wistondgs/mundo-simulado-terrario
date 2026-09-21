"""Contratos de la campaña · el criterio de clasificación y el diagnóstico prohibido."""

from __future__ import annotations

import ast
import pathlib

import numpy as np
import pytest

from terrario.level16.campaign import (
    CAPTURE_FRACTION, TEACHABLE_FLOOR, classify, read_life, run_campaign,
)
from terrario.level16.life import live
from terrario.level16.seeds import LIVES_REQUIRED


@pytest.mark.parametrize("caso, esperado", [
    (dict(available=2.0, gained=1.5, temporal_gain=0.9, updates=4096, moved=True,
          causal=True), "POSITIVO"),
    (dict(available=2.0, gained=1.5, temporal_gain=0.9, updates=0, moved=False,
          causal=True), "N-PLASTICIDAD"),
    (dict(available=2.0, gained=1.5, temporal_gain=0.9, updates=4096, moved=False,
          causal=True), "N-PLASTICIDAD"),
    (dict(available=0.01, gained=0.0, temporal_gain=0.0, updates=4096, moved=True,
          causal=True), "N-EXPERIENCIA"),
    (dict(available=2.0, gained=0.3, temporal_gain=0.1, updates=4096, moved=True,
          causal=True), "N-EXPERIENCIA"),
    (dict(available=2.0, gained=1.5, temporal_gain=-0.2, updates=4096, moved=True,
          causal=True), "NEGATIVO VERDADERO"),
    (dict(available=2.0, gained=1.5, temporal_gain=0.9, updates=4096, moved=True,
          causal=False), "NEGATIVO VERDADERO"),
])
def test_las_seis_categorias_son_alcanzables(caso, esperado):
    """Una clasificación que sólo puede dar POSITIVO no clasifica nada."""
    assert classify(**caso) == esperado


def test_los_umbrales_son_los_que_la_enmienda_declaro():
    assert (TEACHABLE_FLOOR, CAPTURE_FRACTION) == (0.05, 0.25)


def test_el_orden_de_las_reglas_importa_y_es_el_escrito():
    """Sin plasticidad primero, un mecanismo muerto en un mundo pobre se leería
    como problema de la trayectoria."""
    assert classify(available=0.01, gained=0.0, temporal_gain=0.0, updates=0,
                    moved=False, causal=False) == "N-PLASTICIDAD"


def test_leer_una_vida_devuelve_todo_lo_que_el_informe_debe_publicar():
    salida, prueba = read_life(live(140000011, steps=512, post_steps=256))
    assert salida.trajectory_hash and salida.stratum
    assert salida.reachable_observations >= 2
    assert salida.updates == 512
    assert abs(salida.loss_frozen - float(np.log(16))) < 1e-12
    assert prueba.fingerprint_before == prueba.fingerprint_after


def test_una_campana_reducida_corre_entera_y_pasa_los_doce_gates():
    resultado = run_campaign(steps=512, post_steps=256)
    assert len(resultado.outcomes) == LIVES_REQUIRED
    assert len(resultado.report.results) == 12
    assert resultado.report.all_passed, [
        (r.name, r.evidence) for r in resultado.report.failures]


def test_el_banco_poblacional_no_puede_ser_gate():
    """Oráculo §8: existe como diagnóstico y ningún gate puede leerlo."""
    fuente = pathlib.Path("terrario/level16/campaign.py").read_text()
    arbol = ast.parse(fuente)
    llamadas_en_gates = {
        n.func.id for f in ast.walk(arbol)
        if isinstance(f, ast.FunctionDef) and f.name.startswith("gate")
        for n in ast.walk(f) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert "population_bank_diagnostic" not in llamadas_en_gates
    gates_fuente = pathlib.Path("terrario/level16/gates.py").read_text()
    nombres = {n.id for n in ast.walk(ast.parse(gates_fuente)) if isinstance(n, ast.Name)}
    nombres |= {n.attr for n in ast.walk(ast.parse(gates_fuente))
                if isinstance(n, ast.Attribute)}
    assert "population_bank_diagnostic" not in nombres
