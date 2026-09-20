"""Una realización · los diez gates evaluados desde el primer día.

En el Nivel 1.4 el guion informaba siete gates donde el preregistro sellaba once,
y hubo que reconciliar el inventario después. Aquí las diez filas se evalúan en
ejecución desde el principio.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from terrario.level11.cue import ALL_CUES, CueSemantics, CueToken
from terrario.level14.carriers import CANONICAL_PSI
from terrario.remembered.agent import NoMemory, RememberedBindingAgent
from terrario.remembered.core import reconstruct
from terrario.remembered.memory import MemoryPhase, OneStepCueMemory
from terrario.remembered.metrics import (
    ORDEN, SEALED, carrier_invariance, interaction, joint_population_brier,
    scene_bank,
)

O_PRESENT = (1, 0, 0, 0)
RAIZ = Path(__file__).resolve().parent.parent.parent
BLOB_M = "705239c:terrario/level13/memory.py"


@dataclass
class SeedReport:
    seed: int
    fingerprints_before: dict[str, str]
    fingerprints_after: dict[str, str]
    single_core: bool
    memory_literal: bool
    memory_semantics: bool
    psi_intact: bool
    binder_passive: bool
    invariance: float
    skip_tick: float
    joint: dict = field(default_factory=dict)

    @property
    def lineage_intact(self) -> bool:
        return self.fingerprints_before == self.fingerprints_after

    @property
    def psi_alone(self) -> float:
        return self.joint[("OFF", "OFF")] - self.joint[("OFF", "ON")]

    def gates(self) -> dict[str, bool]:
        return {
            "RB-0 un solo núcleo": self.single_core,
            "RB-1 linaje intacto": self.lineage_intact,
            "RB-2 M sin deriva": self.memory_literal,
            "RB-3 semántica de M": self.memory_semantics,
            "RB-4 ψ intacta": self.psi_intact,
            "RB-5 coexistencia": len(self.joint) == 4,
            "RB-6 uso conjunto": all(
                abs(self.joint[k] - SEALED[k]) < 1e-3 for k in ORDEN),
            "RB-7 dependencia total": self.psi_alone == 0.0,
            "RB-8 el tick hace falta": abs(
                self.skip_tick - self.joint[("OFF", "OFF")]) < 1e-12,
            "RB-9 pasividad": self.binder_passive and self.invariance < 1e-12,
        }

    @property
    def passes(self) -> bool:
        return all(self.gates().values())


def run_seed(seed: int, *, semantics: CueSemantics | None = None) -> SeedReport:
    semantics = semantics or CueSemantics.identity()
    organismo = reconstruct(seed, semantics=semantics)
    antes = organismo.fingerprints()
    banco = scene_bank()

    brazos = {
        ("ON", "ON"): RememberedBindingAgent(organismo, OneStepCueMemory()),
        ("ON", "OFF"): RememberedBindingAgent(organismo, OneStepCueMemory(),
                                              use_psi=False, name="M sin ψ"),
        ("OFF", "ON"): RememberedBindingAgent(organismo, NoMemory(), name="ψ sin M"),
        ("OFF", "OFF"): RememberedBindingAgent(organismo, NoMemory(), use_psi=False,
                                               name="ninguna"),
    }
    unico = all(a.organism is organismo for a in brazos.values())
    joint = {k: joint_population_brier(a, semantics, O_PRESENT, banco)
             for k, a in brazos.items()}
    sin_tick = joint_population_brier(brazos[("ON", "ON")], semantics, O_PRESENT,
                                      banco, skip_tick=True)

    literal = (subprocess.run(["git", "show", BLOB_M], cwd=RAIZ,
                              capture_output=True, text=True, check=True).stdout
               == (RAIZ / "terrario" / "remembered" / "memory.py").read_text("utf-8"))

    m = OneStepCueMemory(); m.write(CueToken.C1)
    ok = m.peek() is None
    m.tick(); ok = ok and m.peek() is CueToken.C1
    hu = m.fingerprint(); m.peek(); ok = ok and m.fingerprint() == hu
    m.tick(); ok = ok and m.phase is MemoryPhase.EMPTY

    x0 = next(iter(CANONICAL_PSI))
    psi_ok = abs(organismo.association(x0, CANONICAL_PSI[x0]) - 0.85) < 1e-12
    huella_psi = organismo.fingerprints()["psi"]
    invar = carrier_invariance(brazos[("ON", "ON")], semantics, O_PRESENT)
    pasivo = organismo.fingerprints()["psi"] == huella_psi

    return SeedReport(seed, antes, organismo.fingerprints(), unico, literal, ok,
                      psi_ok, pasivo, invar, sin_tick, joint)
