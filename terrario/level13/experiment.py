"""`LEVEL1.3-ONE-STEP-REFERENCE-PERSISTENCE-01` · una realización completa.

Los valores positivos están determinados por la arquitectura: el registro se
suministró, no se descubrió. Lo que la verificación mide de verdad es la lista de
fallos posibles --cue borrado antes de leer, semántica filtrada a la memoria,
horizonte excedido, tick omitido sin detectar, azar acoplado entre brazos--, y
cada uno tiene su fixture.

Las ocho semillas **no son una muestra poblacional**: comprueban que el mecanismo
se reproduce sobre ocho cuerpos y orientaciones heredados distintos.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from terrario.level11.cue import ALL_CUES, CueSemantics
from terrario.level13.agent import Level13Agent, PresentCueAgent
from terrario.level13.inherited import reconstruct
from terrario.level13.memory import (
    ImmediateMemory, MemoryPhase, NoMemory, OneStepCueMemory,
    WriteDisabledMemory,
)
from terrario.level13.metrics import (
    body_sensitivity, history_use_rate, memory_fidelity, memory_information,
    mutual_information, policy_parity,
)
from terrario.level13.trials import (
    O_PRESENT, O_QUERY, critical_bank, leaky_bank, parity_bank, shuffled_bank,
)

#: Sellado: el suelo de toda política que ignore la historia.
FLOOR = 0.25


@dataclass
class SeedReport:
    seed: int
    fingerprint_before: str
    fingerprint_after: str
    rate: dict[str, float] = field(default_factory=dict)
    fidelity: float = 0.0
    parity: float = 0.0
    leakage_query: float = 0.0
    leakage_present: float = 0.0
    retention_exact: bool = False
    horizon_contained: bool = False
    reset_integrity: float = 0.0
    memory_passive: bool = False
    body: dict[str, float] = field(default_factory=dict)
    temporal_observability: bool = False
    presentation_isolated: bool = False
    shortcuts_falsifiable: bool = False

    @property
    def inherited_intact(self) -> bool:
        return self.fingerprint_before == self.fingerprint_after

    def gates(self) -> dict[str, bool]:
        """Las catorce del preregistro sellado, con sus nombres y sus números.

        La primera versión evaluaba once. `L13-1`, `L13-2` y `L13-10` sí
        estaban verificados --en `tests/test_level13_lineage.py` los dos
        primeros, en `tests/test_level13_memory.py` el tercero-- pero no
        aparecían en el informe de ejecución, y un inventario que no coincide
        con su sello deja dos taxonomías al siguiente que lea. Ningún número
        medido cambia por esto.
        """
        return {
            "L13-0 linaje": self.inherited_intact,
            "L13-1 observabilidad temporal": self.temporal_observability,
            "L13-2 aislamiento de la presentación": self.presentation_isolated,
            "L13-3 sin fuga del presente": (self.leakage_query == 0.0
                                            and self.leakage_present == 0.0),
            "L13-4 retención de un paso": self.retention_exact,
            "L13-5 uso de la historia": (
                self.rate["FULL_13"] == self.rate["PRESENT_CUE"]
                and self.rate["NO_MEMORY"] == FLOOR),
            "L13-6 uso del presente": (self.body["libre"] > self.body["bloqueada"]
                                       and self.body["delta_q"] == 0.0),
            "L13-7 historia barajada": self.rate["SHUFFLED_HISTORY"] == FLOOR,
            "L13-8 preservación 1.1": self.parity == 0.0 and self.inherited_intact,
            "L13-9 reset y sobrescritura": self.reset_integrity == 1.0,
            "L13-10 falsabilidad de atajos": self.shortcuts_falsifiable,
            "L13-11 pasividad": self.memory_passive,
            "L13-12 horizonte contenido": self.horizon_contained,
            "L13-13 el tick es necesario": self.rate["TICK_OMITIDO"] == FLOOR,
        }

    @property
    def passes(self) -> bool:
        return all(self.gates().values())


def run_seed(seed: int, *, semantics: CueSemantics | None = None) -> SeedReport:
    semantics = semantics or CueSemantics.identity()
    core = reconstruct(seed, semantics=semantics)
    antes = core.fingerprint()

    critico, barajado = critical_bank(), shuffled_bank()
    full = Level13Agent(core, OneStepCueMemory())

    brazos: dict[str, Any] = {
        "FULL_13": full,
        "PRESENT_CUE": PresentCueAgent(core),
        "NO_MEMORY": Level13Agent(core, NoMemory(), name="NO_MEMORY"),
        "FROZEN_13": Level13Agent(core, WriteDisabledMemory(), name="FROZEN_13"),
    }

    rate = {n: history_use_rate(a, critico, semantics) for n, a in brazos.items()}
    rate["SHUFFLED_HISTORY"] = history_use_rate(full, barajado, semantics)
    rate["TICK_OMITIDO"] = history_use_rate(full, critico, semantics, skip_tick=True)

    # --- retención exacta, horizonte y reset ---------------------------------
    retencion = True
    horizonte = True
    for c in ALL_CUES:
        full.reset()
        full.present(O_PRESENT, c)
        full.tick()
        retencion = retencion and full.memory.peek() == c
        full.tick()
        horizonte = horizonte and full.memory.phase is MemoryPhase.EMPTY
        full.reset()

    inicios = 0
    for t in critico:
        full.reset()
        inicios += int(full.memory.phase is MemoryPhase.EMPTY)

    # --- pasividad: leer no consume -------------------------------------------
    full.reset()
    full.present(O_PRESENT, ALL_CUES[0])
    full.tick()
    huella = full.memory.fingerprint()
    for _ in range(5):
        full.query(O_QUERY)
        full.memory.peek()
    pasiva = full.memory.fingerprint() == huella
    full.reset()

    observabilidad = _temporal_observability()
    aislamiento = _presentation_isolated(core)
    atajos = _shortcuts_falsifiable(core, semantics)

    reporte = SeedReport(
        seed, antes, core.fingerprint(), rate,
        memory_fidelity(full, critico),
        policy_parity(full, core, parity_bank(), O_PRESENT),
        mutual_information([(t.true_cue, t.o_query) for t in critico]),
        mutual_information([(t.true_cue, t.o_present) for t in critico]),
        retencion, horizonte, inicios / len(critico), pasiva,
        body_sensitivity(full, semantics),
        observabilidad, aislamiento, atajos)
    return reporte


# ── L13-1, L13-2 y L13-10 ────────────────────────────────────────────────────

def _temporal_observability() -> bool:
    """`L13-1` · el cue llega en PRESENT y no en QUERY.

    La garantía es la firma: si `query` aceptara un `CueToken` no habría nada
    que recordar, y el nivel entero mediría otra cosa. Puede fallar --basta
    añadir el parámetro--, que es lo que lo hace gate.
    """
    import inspect

    if list(inspect.signature(Level13Agent.query).parameters) != [
            "self", "observation"]:
        return False
    return list(inspect.signature(Level13Agent.present).parameters) == [
        "self", "observation", "cue"]


def _presentation_isolated(core) -> bool:
    """`L13-2` · `present` devuelve `None` y no hay camino de `present` a `act`.

    Es auditoría de la superficie de API, no del mundo: el banco se enumera, así
    que no hay `Grid` que mutar. Queda dicho aquí igual que en el sello, para
    que nadie lo lea como prueba de que el mundo no se movió.
    """
    import ast
    import inspect
    import textwrap

    agente = Level13Agent(core, OneStepCueMemory())
    if agente.present(O_PRESENT, ALL_CUES[0]) is not None:
        return False
    if hasattr(agente, "act") or hasattr(agente, "step"):
        return False
    arbol = ast.parse(textwrap.dedent(inspect.getsource(Level13Agent.present)))
    llamadas = {n.func.attr for n in ast.walk(arbol)
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    return llamadas <= {"write"}


def _shortcuts_falsifiable(core, semantics: CueSemantics) -> bool:
    """`L13-10` · los dos mundos de atajo hacen caer el gate que les toca.

    Un banco cuyo `o_query` codifica el cue sube `I(G ; o_query)` a 2 bits y
    hunde `L13-3`; una memoria consultable al instante recupera sin tick y hunde
    `L13-13`. Sin este par, los dos gates aprobarían por ausencia de prueba.
    """
    fuga = leaky_bank(semantics)
    filtra = mutual_information(
        [(t.true_cue, t.o_query) for t in fuga]) == 2.0

    inmediata = Level13Agent(core, ImmediateMemory(), name="INMEDIATA")
    sin_intervalo = history_use_rate(
        inmediata, critical_bank(), semantics, skip_tick=True) == 1.0

    return filtra and sin_intervalo
