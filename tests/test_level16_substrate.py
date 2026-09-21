"""Contratos del sustrato de 1.6 · S0, predicado estructural y consumo de semillas."""

from __future__ import annotations

import hashlib

import numpy as np
import pytest

from terrario.level1.measurement import Experiment
from terrario.level1.world import Direction, Grid
from terrario.level16.motor import EndogenousMotor, MotorContractError
from terrario.level16.seeds import (
    LIVES_REQUIRED, SEED_WINDOW, SeedPoolExhausted, SeedVerdict, consume_seeds,
)
from terrario.level16.structure import describe_world, is_nonworld
from terrario.level16.world import (
    GRID_SIZE, WALL_PROBABILITY, build_world, motor_stream, shuffle_stream,
    world_stream,
)


# --- los parámetros se heredan, no se eligen --------------------------------

def test_los_parametros_son_los_del_nivel_1_0_leidos_del_codigo():
    """Enmienda 02: la densidad no se ajustó, se leyó del experimento canónico."""
    canonico = Experiment()
    assert (GRID_SIZE, WALL_PROBABILITY) == (
        canonico.grid_size, canonico.wall_probability)


# --- cuarentena de flujos ---------------------------------------------------

def test_los_tres_flujos_de_una_semilla_son_distintos():
    s = 140000011
    muestras = [tuple(f(s).integers(0, 1_000_000, size=8))
                for f in (world_stream, motor_stream, shuffle_stream)]
    assert len(set(muestras)) == 3


def _trayectoria(seed: int, pasos: int = 256) -> str:
    grid = build_world(seed)
    motor = EndogenousMotor(motor_stream(seed))
    huella = hashlib.sha256()
    for _ in range(pasos):
        direccion = motor.next()
        _, observacion = grid.step(direccion)
        huella.update(bytes([int(direccion), *observacion]))
    return huella.hexdigest()


def test_evaluar_el_predicado_no_altera_la_vida_que_la_semilla_produce():
    """El corolario exigible de la Enmienda 01 §5.

    Si mirar si un mundo sirve cambiara la vida que ese mundo da, la regla de
    consumo dejaría de ser determinista y el veredicto pasaría a depender de
    haberlo consultado.
    """
    seed = 140000011
    sin_mirar = _trayectoria(seed)
    estructura = describe_world(seed, build_world(seed))
    assert not is_nonworld(estructura)
    assert _trayectoria(seed) == sin_mirar


# --- S0 ---------------------------------------------------------------------

def test_el_motor_exige_un_generador_propio():
    with pytest.raises(MotorContractError):
        EndogenousMotor(np.random.RandomState(0))  # type: ignore[arg-type]


def test_el_estado_del_motor_reproduce_los_actos_futuros():
    motor = EndogenousMotor(motor_stream(140000011))
    [motor.next() for _ in range(37)]
    foto = motor.state()
    esperado = [motor.next() for _ in range(64)]

    gemelo = EndogenousMotor(motor_stream(999))
    gemelo.restore(foto)
    assert [gemelo.next() for _ in range(64)] == esperado
    assert gemelo.emitted == motor.emitted


def test_una_foto_sin_el_azar_no_restaura():
    """Fixture negativa de L16-2: serializar sólo la cuenta no reproduce nada."""
    motor = EndogenousMotor(motor_stream(140000011))
    with pytest.raises(MotorContractError):
        motor.restore({"emitted": 10})


def test_la_cuenta_de_emisiones_es_la_prueba_de_procedencia():
    motor = EndogenousMotor(motor_stream(140000011))
    for _ in range(128):
        motor.next()
    assert motor.emitted == 128


# --- el predicado -----------------------------------------------------------

def _rejilla(filas: list[str]) -> Grid:
    celdas = np.array([[1 if c == "#" else 0 for c in fila] for fila in filas],
                      dtype=np.uint8)
    libre = np.argwhere(celdas == 0)[0]
    return Grid(celdas, (int(libre[0]), int(libre[1])))


def test_una_celda_aislada_es_n_mundo():
    grid = _rejilla(["#####", "##.##", "#####", "#####", "#####"])
    estructura = describe_world(0, grid)
    assert estructura.component_size == 1
    assert len(estructura.observations) == 1
    assert is_nonworld(estructura)


def test_la_segunda_rama_del_predicado_esta_implicada_por_la_primera():
    """Las dos condiciones del oráculo §12 son la misma sobre un componente conexo.

    Demostración: si `|O| >= 2`, existen dos celdas alcanzables con firmas
    distintas; como el componente es conexo, algún camino entre ellas cruza un
    par **adyacente** cuyas firmas difieren, y recorrer ese par es una transición
    alcanzable con `o' != o`. Contrarrecíproco: si ninguna transición cambia,
    entonces `|O| < 2`.

    Queda escrito porque el oráculo enunció las dos como disyunción, y sin esta
    nota alguien podría tratarlas como guardianes independientes --o intentar
    escribirle una fixture negativa a la segunda, que no puede existir.
    """
    solo_segunda = 0
    for seed in range(3000):
        estructura = describe_world(seed, build_world(seed))
        pocas = len(estructura.observations) < 2
        quieto = estructura.changing_transitions == 0
        assert quieto == pocas
        solo_segunda += quieto and not pocas
    assert solo_segunda == 0


def test_un_bolsillo_pequeno_pero_con_estructura_no_se_descarta():
    """No se excluye por tamaño: eso sería seleccionar mundos favorables."""
    grid = _rejilla(["#####", "#..##", "#####", "#####", "#####"])
    grid.position = (1, 1)
    estructura = describe_world(0, grid)
    assert estructura.component_size == 2
    assert estructura.stratum == "<=3"
    assert estructura.changing_transitions > 0
    assert not is_nonworld(estructura)


# --- consumo del intervalo --------------------------------------------------

def test_el_consumo_asciende_sin_saltos_y_para_en_la_decimosexta():
    libro = consume_seeds()
    assert len(libro.lives) == LIVES_REQUIRED
    tocadas = [e.seed for e in libro.entries]
    assert tocadas == sorted(tocadas)
    assert tocadas[0] == SEED_WINDOW[0]
    assert tuple(tocadas) == SEED_WINDOW[:len(tocadas)]
    assert libro.unconsumed == SEED_WINDOW[len(tocadas):]


def test_las_descartadas_quedan_en_el_libro_y_no_en_las_vidas(monkeypatch):
    """Una N-MUNDO se publica igual; no desaparece del recorrido."""
    import terrario.level16.seeds as modulo
    real = modulo.is_nonworld
    monkeypatch.setattr(
        modulo, "is_nonworld",
        lambda e: e.seed in (140000012, 140000015) or real(e))
    libro = consume_seeds()
    assert libro.discarded == (140000012, 140000015)
    assert len(libro.lives) == LIVES_REQUIRED
    assert 140000012 not in libro.lives
    assert all(e.verdict is SeedVerdict.NONWORLD
               for e in libro.entries if e.seed in libro.discarded)


def test_agotar_el_intervalo_levanta_en_vez_de_ampliarlo():
    """Fixture negativa: la parada no puede resolverse pidiendo más semillas."""
    with pytest.raises(SeedPoolExhausted):
        consume_seeds(window=SEED_WINDOW[:4], required=LIVES_REQUIRED)
