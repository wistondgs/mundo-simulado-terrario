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
    from terrario.level16.campaign import read_life
    vidas = [live(s, steps=1024, post_steps=512) for s in consume_seeds().lives]
    salidas = [read_life(v)[0] for v in vidas]
    return vidas, salidas, {
        "full": np.array([log_loss(full(v), v.post) for v in vidas]),
        "frozen": np.array([log_loss(frozen(v), v.post) for v in vidas]),
        "shuffled": np.array([log_loss(temporal_shuffled(v), v.post) for v in vidas]),
    }


class _VidaConBarajaIntacta:
    """Una vida cuya baraja no destruyó nada, con todo lo demás correcto."""

    def __init__(self, seed, destructiva):
        self.seed = seed
        self.shuffle_destructive = destructiva
        self.shuffle_distance_full = 0.55
        self.shuffle_distance_shuffled = 0.06 if destructiva else 0.54


def _uno(funcion, *args) -> gates.GateResult:
    reporte = GateReport()
    funcion(reporte, *args)
    return reporte.results[0]


# --- los doce en positivo ----------------------------------------------------

def test_los_doce_gates_pasan_sobre_el_paquete_real(vida, perdidas):
    vidas, salidas, L = perdidas
    reporte = GateReport()
    gates.gate_lineage_isolation(reporte)
    gates.gate_action_provenance(reporte, vida)
    gates.gate_motor_serialisation(reporte, SEMILLA)
    gates.gate_no_reward_signals(reporte)
    gates.gate_learner_is_blind(reporte)
    gates.gate_trajectory_parity(reporte, vida)
    gates.gate_experience_was_sufficient(reporte, vida)
    gates.gate_beats_its_own_past(reporte, L)
    gates.gate_beats_shuffled(reporte, L, salidas)
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
    sanas = [_VidaConBarajaIntacta(s, True) for s in range(4)]
    assert not _uno(gates.gate_beats_shuffled, L, sanas).passed


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


# --- AN-1 reparada: la precondición de L16-8 ---------------------------------

def test_l16_8_falla_si_la_baraja_no_destruyo_aunque_full_gane():
    """Fixture negativa de AN-1, por la vía real del verificador.

    Las pérdidas son las de una campaña que gana con holgura: sin la
    precondición, este gate pasaría con un control que no es un control.
    """
    L = {"full": np.full(4, 1.0), "shuffled": np.full(4, 2.2)}
    sanas = [_VidaConBarajaIntacta(s, True) for s in range(4)]
    assert _uno(gates.gate_beats_shuffled, L, sanas).passed

    rotas = [_VidaConBarajaIntacta(0, False)] + sanas[1:]
    resultado = _uno(gates.gate_beats_shuffled, L, rotas)
    assert not resultado.passed
    assert "BARAJA NO DESTRUCTIVA" in resultado.evidence


def test_l16_8_falla_si_no_hay_auditoria_de_baraja():
    """Y no puede aprobarse por omisión: sin auditoría tampoco pasa."""
    L = {"full": np.full(4, 1.0), "shuffled": np.full(4, 2.2)}
    assert not _uno(gates.gate_beats_shuffled, L, []).passed


# --- AN-5 · las fixtures prometidas por el oráculo §13 -----------------------

def test_l16_7_falla_si_a_full_se_le_congela_antes_de_contar():
    """La fixture que el oráculo prometía para L16-7, por la vía real.

    Un FULL congelado antes de la adquisición ES el brazo FROZEN, así que la
    ganancia es cero en todas las vidas y el gate cae. Se computa con pérdidas
    reales sobre bancos POST reales, no con un diccionario sintético.
    """
    from terrario.level16.temporal import TemporalModel
    vidas = [live(s, steps=256, post_steps=256) for s in consume_seeds().lives[:4]]
    congelado = TemporalModel()
    congelado.freeze()
    L = {"full": np.array([log_loss(congelado, v.post) for v in vidas]),
         "frozen": np.array([log_loss(frozen(v), v.post) for v in vidas])}
    assert np.allclose(L["full"], L["frozen"])
    assert not _uno(gates.gate_beats_its_own_past, L).passed


def test_la_fixture_prometida_para_l16_5_es_imposible_por_construccion():
    """«Cambiar una acción de un brazo» no puede ocurrir: no hay acciones por brazo.

    Los brazos reciben una `Life` ya vivida; ninguno produce actos. La paridad de
    trayectoria no es un invariante que pueda romperse desde un brazo, sino una
    consecuencia de que sólo exista una trayectoria. Se declara **redundancia
    lógica** y se ataca en su lugar la única precondición que sí puede caer: que
    el cuerpo llegue a leer la tabla.
    """
    import ast
    import pathlib
    arbol = ast.parse(pathlib.Path("terrario/level16/arms.py").read_text())
    nombres = {n.id for n in ast.walk(arbol) if isinstance(n, ast.Name)}
    nombres |= {n.attr for n in ast.walk(arbol) if isinstance(n, ast.Attribute)}
    assert not (nombres & {"next", "EndogenousMotor", "motor_stream", "step",
                           "Direction", "integers"})
    vida = live(140000011, steps=128, post_steps=64)
    assert full(vida).updates == temporal_shuffled(vida).updates == len(vida.previous)


def test_la_fixture_prometida_para_l16_6_queda_excluida_aguas_arriba():
    """«Mundo estático» no puede llegar a una vida: el consumo de semillas lo corta.

    Un mundo sin transiciones que cambien es `N-MUNDO` por el predicado
    estructural, y la regla de consumo lo descarta **antes** de vivirlo. Por eso
    la fixture real inyecta la condición en el gate en vez de fabricar el mundo.
    """
    import numpy as np_

    from terrario.level1.world import Grid
    from terrario.level16.structure import describe_world, is_nonworld
    celdas = np_.array([[1, 1, 1, 1, 1], [1, 1, 0, 1, 1], [1, 1, 1, 1, 1],
                        [1, 1, 1, 1, 1], [1, 1, 1, 1, 1]], dtype=np_.uint8)
    estatico = Grid(celdas, (1, 2))
    assert is_nonworld(describe_world(0, estatico))
