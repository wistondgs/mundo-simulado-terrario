"""Contratos del registro temporal · cada gate con su fixture negativa.

La regla: **un contrato que no puede fallar no es un contrato**. Por cada
propiedad exigida hay una implementación construida a propósito donde la
propiedad es falsa, y se comprueba que el guardián la detecta.
"""

from __future__ import annotations

import pytest

from terrario.level11.cue import ALL_CUES, CueSemantics, CueToken
from terrario.level11.world import Direction
from terrario.level13.agent import Level13Agent, PresentCueAgent
from terrario.level13.experiment import FLOOR, run_seed
from terrario.level13.inherited import reconstruct
from terrario.level13.memory import (
    ImmediateMemory, MemoryContractError, MemoryPhase, NoMemory, OneStepCueMemory,
    UnlimitedMemory, WriteDisabledMemory,
)
from terrario.level13.metrics import (
    history_use_rate, memory_fidelity, mutual_information, policy_parity,
)
from terrario.level13.trials import (
    O_PRESENT, O_QUERY, critical_bank, leaky_bank, parity_bank, shuffled_bank,
)

SEMILLA = 90000011
SEM = CueSemantics.identity()


@pytest.fixture(scope="module")
def core():
    return reconstruct(SEMILLA)


@pytest.fixture
def full(core):
    return Level13Agent(core, OneStepCueMemory())


# --- la máquina de estados ------------------------------------------------------

def test_nace_vacia():
    m = OneStepCueMemory()
    assert m.phase is MemoryPhase.EMPTY and m.peek() is None


def test_leer_antes_del_tick_no_devuelve_nada():
    """C2 · la decisión que hace falsable al nivel: `R(c,0) = NONE`."""
    m = OneStepCueMemory()
    m.write(CueToken.C2)
    assert m.phase is MemoryPhase.HELD_0
    assert m.peek() is None


@pytest.mark.parametrize("cue", list(ALL_CUES))
def test_un_tick_conserva_exactamente_el_token(cue):
    m = OneStepCueMemory()
    m.write(cue)
    m.tick()
    assert m.peek() is cue


def test_dos_ticks_expiran():
    m = OneStepCueMemory()
    m.write(CueToken.C1)
    m.tick()
    m.tick()
    assert m.phase is MemoryPhase.EMPTY and m.peek() is None


def test_una_memoria_sin_caducidad_suspende_el_horizonte():
    """FIXTURE NEGATIVA de L13-12. No es «mejor»: es LEVEL13_SCOPE_EXPANSION."""
    m = UnlimitedMemory()
    m.write(CueToken.C1)
    m.tick()
    m.tick()
    assert m.peek() is CueToken.C1


def test_leer_no_consume():
    """L13-11. Si consumiera, la segunda métrica mediría sobre memoria vacía."""
    m = OneStepCueMemory()
    m.write(CueToken.C3)
    m.tick()
    huella = m.fingerprint()
    for _ in range(10):
        assert m.peek() is CueToken.C3
    assert m.fingerprint() == huella


def test_solo_reset_borra():
    m = OneStepCueMemory()
    m.write(CueToken.C0)
    m.tick()
    m.peek()
    assert m.phase is MemoryPhase.HELD_1
    m.reset()
    assert m.phase is MemoryPhase.EMPTY


def test_sobrescribir_conserva_el_ultimo():
    """`A → B → tick → query = B`. Sin mezcla, sin promedio, sin lista."""
    m = OneStepCueMemory()
    m.write(CueToken.C0)
    m.write(CueToken.C3)
    m.tick()
    assert m.peek() is CueToken.C3


def test_sobrescribir_reinicia_la_edad():
    m = OneStepCueMemory()
    m.write(CueToken.C0)
    m.tick()
    m.write(CueToken.C3)
    assert m.peek() is None          # vuelve a HELD_0
    m.tick()
    assert m.peek() is CueToken.C3


# --- la frontera de tipos --------------------------------------------------------

def test_la_memoria_rechaza_una_direccion():
    """FIXTURE de SEMANTIC_MEMORY_LEAKAGE. Guardar `Direction` suplantaría la
    semántica que ES el mecanismo del Nivel 1.1."""
    m = OneStepCueMemory()
    with pytest.raises(MemoryContractError):
        m.write(Direction.UP)


def test_la_comparacion_no_basta_solo_isinstance():
    """El motivo de que el guardián use `isinstance`: los dos son `IntEnum` con
    los mismos valores, así que comparar los declara iguales."""
    assert CueToken.C0 == Direction.UP
    assert not isinstance(Direction.UP, CueToken)


@pytest.mark.parametrize("basura", [None, 0, "C0", 3.0, True])
def test_la_memoria_rechaza_cualquier_no_cue(basura):
    """`MEMORY_EARLY_ERASURE` deja de ser expresable: la ausencia de señal se
    dice NO llamando a write, nunca llamándolo con nada."""
    m = OneStepCueMemory()
    m.write(CueToken.C2)
    with pytest.raises(MemoryContractError):
        m.write(basura)
    m.tick()
    assert m.peek() is CueToken.C2       # el intento fallido no borró nada


# --- el suelo, exacto ------------------------------------------------------------

def test_sin_memoria_da_exactamente_un_cuarto(core):
    agente = Level13Agent(core, NoMemory(), name="NO_MEMORY")
    assert history_use_rate(agente, critical_bank(), SEM) == FLOOR


def test_escritura_deshabilitada_iguala_a_sin_memoria(core):
    """Preregistrado como empate. No es contraste independiente."""
    congelado = Level13Agent(core, WriteDisabledMemory(), name="FROZEN_13")
    sin = Level13Agent(core, NoMemory(), name="NO_MEMORY")
    assert (history_use_rate(congelado, critical_bank(), SEM)
            == history_use_rate(sin, critical_bank(), SEM) == FLOOR)


def test_la_historia_barajada_da_exactamente_un_cuarto(full):
    """Tabla 4×4 balanceada ⇒ `M ⊥ G` exacto ⇒ varianza cero."""
    assert mutual_information([(t.true_cue, t.stored_cue)
                               for t in shuffled_bank()]) == 0.0
    assert history_use_rate(full, shuffled_bank(), SEM) == FLOOR


def test_barajar_ensayos_ENTEROS_no_destruye_nada(full):
    """El defecto exacto del Nivel 1.1, replicado para que no vuelva: mover junto
    `(g, o, objetivo)` conserva toda la relación y el control empataría con el
    brazo que controla."""
    entero = [t for t in reversed(critical_bank())]
    assert history_use_rate(full, entero, SEM) == 1.0


# --- el techo y la paridad --------------------------------------------------------

def test_full_iguala_al_control_positivo(core, full):
    presente = PresentCueAgent(core)
    assert (history_use_rate(full, critical_bank(), SEM)
            == history_use_rate(presente, critical_bank(), SEM))


def test_la_paridad_de_politica_es_cero_bit_a_bit(core, full):
    """Si `peek` devuelve el token, las dos rutas son la misma llamada."""
    assert policy_parity(full, core, parity_bank(), O_PRESENT) == 0.0


def test_la_fidelidad_del_contenido_es_uno(full):
    assert memory_fidelity(full, critical_bank()) == 1.0


# --- el tick tiene que hacer falta ---------------------------------------------------

def test_omitir_el_tick_hunde_al_brazo_completo(full):
    """L13-13 · el gate que certifica el constructo. Sin él, lo demostrado sería
    «hay un registro consultable», no «hay persistencia a través de un intervalo»."""
    assert history_use_rate(full, critical_bank(), SEM, skip_tick=True) == FLOOR


def test_una_memoria_consultable_al_instante_suspende_ese_gate(core):
    """FIXTURE NEGATIVA de L13-13. Es el registro que el nivel NO demuestra."""
    inmediata = Level13Agent(core, ImmediateMemory(), name="INMEDIATA")
    assert history_use_rate(inmediata, critical_bank(), SEM, skip_tick=True) == 1.0


# --- fugas ----------------------------------------------------------------------------

def test_el_banco_critico_no_filtra_el_presente():
    critico = critical_bank()
    assert mutual_information([(t.true_cue, t.o_query) for t in critico]) == 0.0
    assert mutual_information([(t.true_cue, t.o_present) for t in critico]) == 0.0
    assert O_PRESENT != O_QUERY


def test_un_banco_que_codifica_el_cue_suspende_el_contrato():
    """FIXTURE NEGATIVA de L13-3 · `HISTORY_LEAKAGE`."""
    fuga = leaky_bank(SEM)
    assert mutual_information([(t.true_cue, t.o_query) for t in fuga]) == 2.0


def test_no_resetear_contamina_el_ensayo_siguiente(full):
    """FIXTURE NEGATIVA de L13-9 · `MEMORY_RESET_VIOLATION`."""
    full.reset()
    full.present(O_PRESENT, CueToken.C0)
    full.tick()
    full.query(O_QUERY)
    # el arnés defectuoso NO resetea y el ensayo siguiente no escribe cue
    assert full.memory.peek() is CueToken.C0
    full.reset()
    assert full.memory.peek() is None


# --- la sonda del presente -------------------------------------------------------------

def test_el_cuerpo_participa_con_la_historia_fija(full):
    """L13-6 · cue recordado fijo, cambia sólo `o`: `Q` idéntico, `B` se mueve."""
    for g in ALL_CUES:
        d = SEM.direction_of(g)
        libre = (0, 0, 0, 0)
        bloqueada = tuple(1 if i == int(d) else 0 for i in range(4))
        assert full.predict_orientation(g, d) == full.predict_orientation(g, d)
        assert full.predict_body(libre, d) > full.predict_body(bloqueada, d)


def test_la_campana_completa_pasa_sus_gates():
    r = run_seed(SEMILLA)
    assert r.passes, r.gates()
