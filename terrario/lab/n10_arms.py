"""Las tres intervenciones de N1.0, sobre un mismo snapshot aprendido.

Sealed preregistration V2 described arms B and C and sealed code that could
not run them: the runner carried an `override_token` hook and nothing
implemented it, and there was no read lesion anywhere.  Caught before a
single confirmatory seed was spent, which is the only reason it is cheap.

The three arms differ in exactly one thing each and in nothing else.  They
share a world, a snapshot and a set of decision opportunities; what changes
is what the policy can read at the moment of choosing.

**Arm B is a read lesion and is not called an ablation.**  The token keeps
being written on every perception -- that path is untouched and observable
-- and only the read is blocked.  Calling it an ablation would claim the
mechanism was removed when it is still running.

**Arm C substitutes the token and touches nothing else.**  Not the world,
not the consequences, not the learned table, not the decision ids.  The
permutation is sealed by its own seed, and its strength is measured rather
than assumed: a permutation that left most tokens in place would make this
arm into arm A with noise.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from terrario.lab.n10_u1 import U1Agent, U1Config
from terrario.lab.n10_u1_spec import EMPTY

ARMS_VERSION = "terrario.lab.n10-arms/v1"


class Arm(StrEnum):
    NAIVE = "N"
    COMPLETE = "A"
    MEMORY_READ_LESION = "B"
    HISTORY_SHUFFLED = "C"


class CompleteArm(U1Agent):
    """`A`. Sin intervención: expresa lo adquirido."""

    arm = Arm.COMPLETE


class MemoryReadLesionArm(U1Agent):
    """`B`. El token se sigue escribiendo; la política no puede consumirlo.

    La escritura permanece observable en `core.memory` entre decisiones, así
    que la intervención se puede comprobar en vez de creerse: lo que se
    bloquea es la lectura en el instante de elegir, y sólo eso.
    """

    arm = Arm.MEMORY_READ_LESION

    def decide(self) -> Any:
        retenido = self.core.memory
        self.core.memory = EMPTY
        try:
            return super().decide()
        finally:
            self.core.memory = retenido


class HistoryShuffledArm(U1Agent):
    """`C`. La política lee un token de otra decisión comparable."""

    arm = Arm.HISTORY_SHUFFLED

    def __init__(self, world: Any, config: U1Config | None = None) -> None:
        super().__init__(world, config)
        self._sustituto: str | None = None
        self.substitutions: list[tuple[str, str]] = []

    def override_token(self, token: str) -> None:
        """Lo llama el runner antes de cada decisión comparable."""
        self._sustituto = token

    def decide(self) -> Any:
        if self._sustituto is None:
            return super().decide()
        real = self.core.memory
        self.core.memory = self._sustituto
        self.substitutions.append((real, self._sustituto))
        try:
            return super().decide()
        finally:
            self.core.memory = real
            self._sustituto = None


ARM_CLASSES = {Arm.COMPLETE: CompleteArm,
               Arm.MEMORY_READ_LESION: MemoryReadLesionArm,
               Arm.HISTORY_SHUFFLED: HistoryShuffledArm}


def build_arm(arm: Arm, world: Any, snapshot: Any, config: U1Config) -> U1Agent:
    """Un brazo nace de un clon del MISMO snapshot, ya congelado.

    Tres entrenamientos independientes están prohibidos: los brazos tienen
    que diferir en la intervención y en nada más, y eso sólo se puede afirmar
    si los parámetros son bit a bit los mismos antes de intervenir.
    """
    agente = ARM_CLASSES[arm](world, config)
    agente.core = snapshot.clone(config)
    agente.core.freeze()
    return agente
