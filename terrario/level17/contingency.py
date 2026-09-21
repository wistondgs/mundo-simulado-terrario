"""M_1 = M_0^W congelado + C_17 · la única adquisición de 1.7.

El ser no nace con cuatro tablas uniformes independientes: eso le haría olvidar
lo que 1.6 ya sabía de este mundo. Nace sabiendo exactamente lo de antes, y la
experiencia separa después las cuatro filas.

    C_0(o, a, o')  =  N_16(o, o') / 4          prior simétrico entre acciones

    P_17(o'|o,a)  =  [ N_16(o,o')/4 + C_17(o,a,o') ]
                     ─────────────────────────────────
                     Σ_v [ N_16(o,v)/4 + C_17(o,a,v) ]

Con `C_17 = 0` el cuarto se cancela arriba y abajo y queda `N_16(o,o') / Σ_v
N_16(o,v)`, que es literalmente `P_16(o'|o)`. De ahí los dos invariantes:

    nacimiento    C_17 = 0        =>  M_1(o,a) = M_0^W(o)  para toda a
    lesión        C_17_T -> 0     =>  vuelve EXACTAMENTE a M_0^W, no a uniforme

El segundo es lo que hace que la lesión de 1.7 no destruya al ser: lo devuelve al
nivel anterior. `M_0^W` se guarda como copia y su huella se comprueba: el
componente nuevo no puede modificarlo ni por accidente.
"""

from __future__ import annotations

import hashlib

import numpy as np

from terrario.level1.world import Observation
from terrario.level16.temporal import OBSERVATION_INDEX, TemporalModel
from terrario.level17.efference import EfferenceCopy


class ContingencyContractError(RuntimeError):
    """Se violó el contrato de composición o el de la frontera del aprendiz."""


def _observation(candidate: object, role: str) -> int:
    if not isinstance(candidate, tuple) or len(candidate) != 4:
        raise ContingencyContractError(
            f"{role} debe ser una observación de cuatro bits; llegó "
            f"{type(candidate).__name__}")
    index = OBSERVATION_INDEX.get(candidate)  # type: ignore[arg-type]
    if index is None:
        raise ContingencyContractError(
            f"{role} no pertenece al espacio sensorial: {candidate!r}")
    return index


def _command(candidate: object) -> int:
    """La aduana del canal nuevo. Sólo entra una copia eferente."""
    if not isinstance(candidate, EfferenceCopy):
        raise ContingencyContractError(
            "el canal de acción admite una EfferenceCopy y nada más; llegó "
            f"{type(candidate).__name__}. Una dirección, un índice o un "
            "resultado no son un comando opaco.")
    return candidate.index


class ActionContingencyModel:
    """`P(O'|O,A)` construido sobre lo que el ser ya sabía de este mundo."""

    def __init__(self, inherited: TemporalModel) -> None:
        if not inherited.frozen:
            raise ContingencyContractError(
                "M_0^W debe llegar congelado: si la fase predecesora sigue "
                "aprendiendo, una mejora de 1.7 podría explicarse diciendo que "
                "simplemente siguió aprendiendo mejor P(O'|O)")
        self._inherited = inherited.snapshot()
        self._inherited_fingerprint = inherited.fingerprint()
        self._deviations = np.zeros((16, 4, 16))
        self._updates = 0

    # --- la única operación plástica ----------------------------------------

    def observe(self, previous: Observation, efference: EfferenceCopy,
                following: Observation) -> None:
        """Ver `(o_t, comando, o_{t+1})`. Sólo mueve `C_17`."""
        self._deviations[_observation(previous, "la observación anterior"),
                         _command(efference),
                         _observation(following, "la observación siguiente")] += 1.0
        self._updates += 1

    # --- lectura ------------------------------------------------------------

    def _row(self, previous: int, command: int) -> np.ndarray:
        return self._inherited[previous] * 0.25 + self._deviations[previous, command]

    def predict(self, previous: Observation, efference: EfferenceCopy) -> np.ndarray:
        fila = self._row(_observation(previous, "la observación anterior"),
                         _command(efference))
        return fila / fila.sum()

    def probability(self, previous: Observation, efference: EfferenceCopy,
                    following: Observation) -> float:
        return float(self.predict(previous, efference)[
            _observation(following, "la observación siguiente")])

    # --- estado -------------------------------------------------------------

    @property
    def updates(self) -> int:
        return self._updates

    @property
    def inherited_fingerprint(self) -> str:
        """La huella de `M_0^W` tal como llegó. No debe cambiar nunca."""
        return self._inherited_fingerprint

    def inherited_is_intact(self) -> bool:
        return hashlib.sha256(
            np.ascontiguousarray(self._inherited).tobytes()
        ).hexdigest() == self._inherited_fingerprint

    def acquired_snapshot(self) -> np.ndarray:
        """Copia de `C_17`, lo único que 1.7 adquirió."""
        return self._deviations.copy()

    def load_acquired(self, deviations: np.ndarray) -> None:
        if deviations.shape != (16, 4, 16):
            raise ContingencyContractError(
                f"C_17 es 16x4x16; llegó {deviations.shape}")
        self._deviations = deviations.copy()

    def lesion(self) -> None:
        """Borrar sólo lo adquirido en 1.7. Devuelve al ser a `M_0^W`."""
        self._deviations = np.zeros((16, 4, 16))

    def fingerprint(self) -> str:
        return hashlib.sha256(
            np.ascontiguousarray(self._deviations).tobytes()).hexdigest()
