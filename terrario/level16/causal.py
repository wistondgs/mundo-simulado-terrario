"""La intervención que separa «sabe» de «acertó».

Que el brazo FULL pierda menos no demuestra todavía que la competencia **resida**
en lo aprendido: podría venir de cualquier otra diferencia entre brazos. La
prueba es sustituir el estado y ver si la competencia se va con él, y devolverlo
y ver si vuelve.

    congelar -> guardar M_T -> poner M_0 -> reevaluar -> restaurar M_T -> reevaluar

Las tres evaluaciones usan **el mismo banco POST inmutable**. Volver a correr el
mundo introduciría ruido de trayectoria y la única variable dejaría de ser el
estado aprendido.
"""

from __future__ import annotations

from dataclasses import dataclass

from terrario.level16.metrics import log_loss
from terrario.level16.temporal import TemporalModel


@dataclass(frozen=True)
class CausalProbe:
    """Las tres pérdidas y la huella que prueba que se volvió al mismo sitio."""

    learned: float
    ablated: float
    restored: float
    fingerprint_before: str
    fingerprint_after: str

    @property
    def state_is_causal(self) -> bool:
        return (self.ablated > self.learned
                and abs(self.restored - self.learned) < 1e-12
                and self.fingerprint_before == self.fingerprint_after)


def probe(model: TemporalModel, bank) -> CausalProbe:
    """Ablacionar y restaurar sobre un banco fijo. No toca nada más del ser."""
    huella_antes = model.fingerprint()
    aprendido = model.snapshot()
    perdida_aprendida = log_loss(model, bank)

    model.load(TemporalModel.naive().snapshot())
    perdida_ablacionada = log_loss(model, bank)

    model.load(aprendido)
    perdida_restaurada = log_loss(model, bank)

    return CausalProbe(perdida_aprendida, perdida_ablacionada, perdida_restaurada,
                       huella_antes, model.fingerprint())
