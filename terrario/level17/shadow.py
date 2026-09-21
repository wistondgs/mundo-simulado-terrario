"""K-SOMBRA condicionada por acción · `P(o'|o,a)` exacta desde la topología.

La extensión que el handoff de 1.6 dejaba anotada. Misma propiedad que la hacía
calculable allí: bajo comandos uniformes la cadena marginal sobre celdas es
simétrica, luego su estacionaria es uniforme sobre el componente natal.

    P(o'|o,a) = (1/|C_o|) · Σ_{c ∈ C_o} 1[firma(aterriza(c, φ(a))) = o']

Da las tres magnitudes del mundo que el decimal necesita **antes** de que exista
aprendiz:

    D_W  = Σ p_ref(o,a) · KL[ P(·|o,a) ‖ P(·|o) ]   = I(A;O'|O)   disponible
    D_E  = Σ p_L(o,a)   · KL[ P(·|o,a) ‖ P(·|o) ]                 experimentada
    ε_K  = Σ p_ref(o,a) · KL[ P(·|o,a) ‖ M_1(·|o,a) ]             error del aprendiz

`D_E` usa la frecuencia de la vida real pero las distribuciones del oráculo: mide
**qué parte de la dependencia disponible visitó S0**, sin depender de si el
aprendiz fue bueno o malo. Es el eje del sustrato, no el del mecanismo.
"""

from __future__ import annotations

import numpy as np

from terrario.level1.world import DELTA, Direction, Grid
from terrario.level16.structure import _signature
from terrario.level16.temporal import OBSERVATION_INDEX
from terrario.level17.efference import ALL_COMMANDS
from terrario.level17.wiring import ActuatorWiring


class AnalyticActionShadow:
    """El kernel exacto del mundo, indexado por comando opaco."""

    def __init__(self, grid: Grid, wiring: ActuatorWiring) -> None:
        reachable = {grid.position}
        stack = [grid.position]
        while stack:
            row, col = stack.pop()
            for direction in Direction:
                destino = (row + DELTA[direction][0], col + DELTA[direction][1])
                if grid.cells[destino] == 0 and destino not in reachable:
                    reachable.add(destino)
                    stack.append(destino)

        table = np.zeros((16, 4, 16))
        per_observation = np.zeros(16)
        for cell in reachable:
            origen = OBSERVATION_INDEX[_signature(grid, cell)]
            per_observation[origen] += 1
            for index, command in enumerate(ALL_COMMANDS):
                direction = wiring.actuate(command)
                destino = (cell[0] + DELTA[direction][0],
                           cell[1] + DELTA[direction][1])
                landing = destino if grid.cells[destino] == 0 else cell
                table[origen, index,
                      OBSERVATION_INDEX[_signature(grid, landing)]] += 1
        for origen in range(16):
            if per_observation[origen]:
                table[origen] /= per_observation[origen]
            else:
                table[origen] = 1.0 / 16

        self._table = table
        self._p_observation = per_observation / per_observation.sum()
        self._marginal = table.mean(axis=1)

    @classmethod
    def marginalised(cls, other: AnalyticActionShadow) -> AnalyticActionShadow:
        """La sombra del mundo B, desde la de A.

        `T_B(s'|s,a) = ¼ Σ_b T_A(s'|s,b)` implica `P_B(o'|o,a) = P_A(o'|o)` para
        toda `a`, luego `D_W^B = 0` exactamente. **No** se obtiene envolviendo la
        rejilla en `MarginalisedBody`: ese envoltorio marginaliza en tiempo de
        ejecución y la rejilla que guarda dentro sigue siendo la de A, así que una
        sombra construida sobre ella devuelve la dependencia de A con otro nombre.
        """
        twin = cls.__new__(cls)
        twin._table = np.repeat(other.marginal()[:, None, :], 4, axis=1)
        twin._p_observation = other._p_observation.copy()
        twin._marginal = other.marginal()
        return twin

    @property
    def p_reference(self) -> np.ndarray:
        """`p_ref(o,a) = p(o) · 1/4`, que es lo que S0 produce."""
        return np.outer(self._p_observation, np.full(4, 0.25))

    def action_conditional(self) -> np.ndarray:
        return self._table.copy()

    def marginal(self) -> np.ndarray:
        return self._marginal.copy()

    # --- las magnitudes ------------------------------------------------------

    def _divergence_to_marginal(self) -> np.ndarray:
        """`KL[P(·|o,a) ‖ P(·|o)]` para cada `(o,a)`."""
        out = np.zeros((16, 4))
        for o in range(16):
            for a in range(4):
                p, q = self._table[o, a], self._marginal[o]
                mask = (p > 0) & (q > 0)
                out[o, a] = float(np.sum(p[mask] * np.log(p[mask] / q[mask])))
        return out

    def available(self) -> float:
        """`D_W = I(A;O'|O)`."""
        return float(np.sum(self.p_reference * self._divergence_to_marginal()))

    def experienced(self, visits: np.ndarray) -> float:
        """`D_E`: la misma divergencia, pesada por lo que la vida realmente visitó."""
        total = visits.sum()
        if total == 0:
            return 0.0
        return float(np.sum((visits / total) * self._divergence_to_marginal()))

    def divergence_matrix(self) -> np.ndarray:
        """`KL[P(·|o,a) ‖ P(·|o)]` por contexto. La usa el instrumento de exposición."""
        return self._divergence_to_marginal()

    def marginal_learner_error(self, model) -> float:
        """`ε_NA = E_p_ref KL[ P(·|o,a) ‖ M_NA(·|o) ]`.

        El baseline NO-ACTION predice lo mismo para las cuatro acciones, así que
        su error incluye toda la dependencia que ignora. La resta
        `D_K_action = ε_NA − ε_A` deja **sólo** el conocimiento atribuible a usar
        el comando, y descuenta los datos extra de la fase A, que NO-ACTION
        también recibió. Es la contraparte interna exacta de
        `D_C = L(NA) − L(M_1)`.
        """
        from terrario.level1.world import ALL_OBSERVATIONS

        p_ref = self.p_reference
        total = 0.0
        for o, observation in enumerate(ALL_OBSERVATIONS):
            if self._p_observation[o] == 0:
                continue
            q = model.predict(observation)
            for a in range(4):
                p = self._table[o, a]
                mask = (p > 0) & (q > 0)
                total += p_ref[o, a] * float(np.sum(p[mask] * np.log(p[mask] / q[mask])))
        return total

    def learner_error(self, model) -> float:
        """`ε_K = Σ p_ref(o,a) KL[ P(·|o,a) ‖ M_1(·|o,a) ]`."""
        from terrario.level1.world import ALL_OBSERVATIONS
        from terrario.level17.efference import EfferenceCopy

        p_ref = self.p_reference
        total = 0.0
        for o, observation in enumerate(ALL_OBSERVATIONS):
            if self._p_observation[o] == 0:
                continue
            for a, command in enumerate(ALL_COMMANDS):
                p = self._table[o, a]
                q = model.predict(observation, EfferenceCopy(command))
                mask = (p > 0) & (q > 0)
                total += p_ref[o, a] * float(np.sum(p[mask] * np.log(p[mask] / q[mask])))
        return total
