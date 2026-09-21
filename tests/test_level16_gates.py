"""Los doce gates y sus fixtures negativas.

Un gate cuyo único comportamiento posible es PASS no es un gate. Aquí cada uno
tiene al menos una fuente fabricada o un estado fabricado que lo hace fallar
**por la vía real del verificador**, no por una excepción levantada a mano.
"""

from __future__ import annotations

import numpy as np
import pytest

from terrario.level16 import gates
from terrario.level16.arms import StaticBitcount, frozen, full, temporal_shuffled
from terrario.level16.causal import probe
from terrario.level16.gates import GateReport
from terrario.level16.life import live
from terrario.level16.metrics import log_loss
from terrario.level16.seeds import consume_seeds

SEMILLA = 140000011


@pytest.fixture(scope="module")
def vida():
    return live(SEMILLA, steps=2048, post_steps=512)


@pytest.fixture(scope="module")
def perdidas():
    vidas = [live(s, steps=1024, post_steps=512) for s in consume_seeds().lives]
    return vidas, {
        "full": np.array([log_loss(full(v), v.post) for v in vidas]),
        "frozen": np.array([log_loss(frozen(v), v.post) for v in vidas]),
        "shuffled": np.array([log_loss(temporal_shuffled(v), v.post) for v in vidas]),
    }


def _uno(funcion, *args) -> gates.GateResult:
    reporte = GateReport()
    funcion(reporte, *args)
    return reporte.results[0]


# --- los doce en positivo ----------------------------------------------------

def test_los_doce_gates_pasan_sobre_el_paquete_real(vida, perdidas):
    vidas, L = perdidas
    reporte = GateReport()
    gates.gate_lineage_isolation(reporte)
    gates.gate_action_provenance(reporte, vida)
    gates.gate_motor_serialisation(reporte, SEMILLA)
    gates.gate_no_reward_signals(reporte)
    gates.gate_learner_is_blind(reporte)
    gates.gate_trajectory_parity(reporte, vida)
    gates.gate_experience_was_sufficient(reporte, vida)
    gates.gate_beats_its_own_past(reporte, L)
    gates.gate_beats_shuffled(reporte, L)
    gates.gate_state_is_causal(reporte, [probe(full(v), v.post) for v in vidas[:4]])
    gates.gate_measurement_is_passive(reporte, vida)
    gates.gate_bitcount_cannot_explain_primary(reporte, vida)
    assert len(reporte.results) == 12
    assert reporte.all_passed, [(r.name, r.evidence) for r in reporte.failures]


# --- fixtures negativas ------------------------------------------------------

def test_l16_0_falla_si_una_capacidad_posterior_aparece_en_el_arbol(monkeypatch, tmp_path):
    monkeypatch.setattr(gates, "PACKAGE", tmp_path / "level16")
    (tmp_path / "level13").mkdir(parents=True)
    (tmp_path / "level16").mkdir()
    assert not _uno(gates.gate_lineage_isolation).passed


def test_l16_1_falla_si_los_actos_vienen_de_fuera(vida):
    """Una cinta externa emite tantos actos como pasos, y el gate lo ve igual."""
    class VidaConCinta:
        previous, post_previous = vida.previous, vida.post_previous
        seed = vida.seed

        class instruments:
            motor_emitted = 0        # el motor del ser no produjo nada
    assert not _uno(gates.gate_action_provenance, VidaConCinta).passed


def test_l16_1_falla_si_otro_modulo_tambien_emite_actos(monkeypatch):
    """Fuente fabricada: un segundo emisor rompe la unicidad de la procedencia."""
    reales = gates._package_sources()
    monkeypatch.setattr(gates, "_package_sources",
                        lambda: {**reales, "curriculum.py": "def f(r):\n    return r.integers(4)\n"})
    reporte = GateReport()
    gates.gate_action_provenance(reporte, live(SEMILLA, steps=64, post_steps=32))
    assert not reporte.results[0].passed


def test_l16_2_falla_si_la_foto_no_lleva_el_azar(monkeypatch):
    """Serializar sólo la cuenta de emisiones no reproduce ninguna vida."""
    import terrario.level16.motor as motor
    monkeypatch.setattr(motor.EndogenousMotor, "state",
                        lambda self: {"emitted": self.emitted})
    with pytest.raises(motor.MotorContractError):
        _uno(gates.gate_motor_serialisation, SEMILLA)


@pytest.mark.parametrize("fuente, porque", [
    ("def paso(reward):\n    return reward\n", "recompensa como parámetro"),
    ("novelty = 0.5\n", "novedad como variable"),
    ("class M:\n    def target(self):\n        return 1\n", "target como método"),
    ("x = modelo.q_value\n", "valor como atributo"),
    ("values = [1]\n", "valor genérico como identificador propio"),
])
def test_l16_3_falla_ante_cada_forma_de_senal(monkeypatch, fuente, porque):
    monkeypatch.setattr(gates, "_package_sources", lambda: {"intruso.py": fuente})
    assert not _uno(gates.gate_no_reward_signals).passed, porque


@pytest.mark.parametrize("fuente", [
    "# reward\n'''novelty y value y target'''\nx = 1\n",
    "d = {'a': 1}\nfor k in d.values():\n    pass\n",
    "def f(etiqueta):\n    return etiqueta\n",
])
def test_l16_3_no_se_dispara_contra_prosa_ni_python_corriente(monkeypatch, fuente):
    """El gate tiene que distinguir `dict.values()` de una señal de valor."""
    monkeypatch.setattr(gates, "_package_sources", lambda: {"inocente.py": fuente})
    assert _uno(gates.gate_no_reward_signals).passed


def test_l16_4_falla_si_el_aprendiz_nombra_el_acto(monkeypatch, tmp_path):
    falso = tmp_path / "level16"
    falso.mkdir()
    (falso / "temporal.py").write_text(
        "def observe(previous, following, direction):\n    return direction\n")
    monkeypatch.setattr(gates, "PACKAGE", falso)
    assert not _uno(gates.gate_learner_is_blind).passed


def test_l16_5_falla_si_el_cuerpo_pudiera_leer_la_tabla(monkeypatch, tmp_path):
    falso = tmp_path / "level16"
    falso.mkdir()
    (falso / "life.py").write_text("from terrario.level16.temporal import TemporalModel\n")
    monkeypatch.setattr(gates, "PACKAGE", falso)
    vida = live(SEMILLA, steps=64, post_steps=32)
    assert not _uno(gates.gate_trajectory_parity, vida).passed


def test_l16_6_falla_en_un_mundo_que_no_ensena(monkeypatch, vida):
    import terrario.level16.shadow as shadow
    monkeypatch.setattr(shadow, "teachability", lambda *_: 0.0)
    assert not _uno(gates.gate_experience_was_sufficient, vida).passed


def test_l16_7_falla_si_alguna_vida_no_mejora():
    L = {"full": np.array([1.0, 1.0, 3.0]), "frozen": np.full(3, 2.7726)}
    assert not _uno(gates.gate_beats_its_own_past, L).passed


def test_l16_8_falla_si_el_intervalo_toca_el_cero():
    L = {"full": np.array([1.0, 1.0, 1.0, 1.0]),
         "shuffled": np.array([1.4, 0.6, 1.5, 0.5])}
    assert not _uno(gates.gate_beats_shuffled, L).passed


def test_l16_9_falla_si_ablacionar_no_cambia_nada(vida):
    from terrario.level16.temporal import TemporalModel
    assert not _uno(gates.gate_state_is_causal,
                    [probe(TemporalModel.naive(), vida.post)]).passed


def test_l16_10_falla_si_evaluar_actualiza(monkeypatch, vida):
    import terrario.level16.metrics as metrics
    real = metrics.log_loss

    def entrometido(model, bank):
        model._updates += 1
        return real(model, bank)

    monkeypatch.setattr(metrics, "log_loss", entrometido)
    assert not _uno(gates.gate_measurement_is_passive, vida).passed


def test_l16_11_falla_si_al_control_se_le_fabrica_una_distribucion(monkeypatch, vida):
    monkeypatch.setattr(StaticBitcount, "probability",
                        lambda self, a, b: 1 / 16, raising=False)
    assert not _uno(gates.gate_bitcount_cannot_explain_primary, vida).passed
