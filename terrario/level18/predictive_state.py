"""C_18 · estado predictivo, por refinamiento incremental.

Austero a propósito. Ni red recurrente, ni embeddings, ni búsqueda global sobre
historias, ni número de estados prefijado.

**Nace siendo 1.7.** `Z = {z_0}` y el prior de `z_0` es la tabla heredada entera,
así que al nacer `P_18(o'|o,a,z_0) = P_17(o'|o,a)` sin aproximación.

**La memoria es recursiva, no una ventana.**

    z_t = F(z_{t-1}, a_{t-1}, o_t)

Un estado se refina separándolo por su **firma de entrada** `(z_anterior,
a_anterior)`. Cada separación añade un paso de profundidad histórica, y ocho
separaciones sucesivas dan lo que una tabla sobre historias de longitud ocho
--4.5·10¹⁵ contextos-- no puede dar con ningún presupuesto.

**El criterio no tiene constantes.** Nada de `if divergencia > 0.07`. Se lleva la
longitud de código **prequencial** de las dos hipótesis --el estado unificado y el
estado separado-- prediciendo siempre antes de actualizar. El código prequencial ya
paga la complejidad por su cuenta: un modelo con más parámetros predice peor al
principio y sólo recupera esa deuda si la distinción es real. Separamos cuando la
hipótesis separada ha acumulado menos código que la unificada.

    un estado existe porque compra predicción suficiente para pagar su propia
    complejidad — no porque nosotros sepamos cuántas situaciones hay

**La masa heredada se conserva.** Al separar, el prior del padre se reparte entre
los hijos de forma proporcional a la evidencia que cada firma trajo, suavizada, y
la suma es exactamente la del padre.
"""

from __future__ import annotations

import numpy as np

from terrario.level16.temporal import OBSERVATION_INDEX
from terrario.level17.efference import ALL_COMMANDS, EfferenceCopy

#: Índice del estado raíz. No es un número de estados: es un nombre.
ROOT = 0


class PredictiveStateError(RuntimeError):
    """Se violó el contrato del mecanismo de estado."""


def _observation_index(candidate: object, role: str) -> int:
    if not isinstance(candidate, tuple) or len(candidate) != 4:
        raise PredictiveStateError(
            f"{role} debe ser una observación de cuatro bits; llegó "
            f"{type(candidate).__name__}")
    found = OBSERVATION_INDEX.get(candidate)  # type: ignore[arg-type]
    if found is None:
        raise PredictiveStateError(f"{role} fuera del espacio sensorial: {candidate!r}")
    return found


def _command_index(candidate: object) -> int:
    if not isinstance(candidate, EfferenceCopy):
        raise PredictiveStateError(
            "el canal admite una EfferenceCopy y nada más; llegó "
            f"{type(candidate).__name__}")
    return candidate.index


class PredictiveStateModel:
    """`P(O'|O,A,Z)` con `Z` construido de la propia historia sensoriomotora."""

    def __init__(self, inherited_counts: np.ndarray) -> None:
        if inherited_counts.shape != (16, 4, 16):
            raise PredictiveStateError(
                f"la tabla heredada es 16x4x16; llegó {inherited_counts.shape}")
        self._inherited = np.array(inherited_counts, dtype=float)
        self._prior = {ROOT: self._inherited.copy()}      # masa heredada por estado
        self._evidence = {ROOT: np.zeros((16, 4, 16))}    # lo adquirido en 1.8
        self._routing: dict[tuple[int, int, int], int] = {}
        self._parent: dict[int, int | None] = {ROOT: None}
        self._incoming: dict[int, dict[tuple[int, int], np.ndarray]] = {ROOT: {}}
        self._code = {ROOT: [0.0, 0.0]}                   # [unificado, separado]
        self._arrivals: dict[int, dict[tuple[int, int], float]] = {ROOT: {}}
        self._here = ROOT
        self._came_from: tuple[int, int] | None = None
        self._updates = 0
        self._splits = 0
        self._merges = 0

    # --- el ser entra en el mundo -------------------------------------------

    def begin(self) -> None:
        self._here = ROOT
        self._came_from = None

    # --- lectura -------------------------------------------------------------

    def _weights(self, state: int, previous: int, command: int) -> np.ndarray:
        """Masa heredada más evidencia propia. Al nacer es exactamente `C_17`."""
        return self._prior[state][previous, command] \
            + self._evidence[state][previous, command]

    def predict(self, previous, efference) -> np.ndarray:
        weights = self._weights(self._here, _observation_index(previous, "la observación"),
                        _command_index(efference))
        return weights / weights.sum()

    def probability(self, previous, efference, following) -> float:
        return float(self.predict(previous, efference)[
            _observation_index(following, "la observación siguiente")])

    # --- la única operación plástica -----------------------------------------

    def observe(self, previous, efference, following) -> None:
        here = self._here
        before = _observation_index(previous, "la observación")
        command = _command_index(efference)
        after = _observation_index(following, "la observación siguiente")
        signature = self._came_from if self._came_from is not None else (ROOT, 0)

        unified = self._weights(here, before, command)
        self._code[here][0] += -float(np.log(unified[after] / unified.sum()))

        pocket = self._incoming[here].get(signature)
        if pocket is None:
            pocket = np.zeros((16, 4, 16))
            self._incoming[here][signature] = pocket
            self._arrivals[here][signature] = 0.0
        # La hipótesis separada debe puntuarse con el prior que el hijo
        # REALMENTE recibiría --`prior·share`--, no con el del padre entero. Con
        # el prior completo y un cuarto de la evidencia se puntúa un modelo
        # sobre-suavizado que nunca se instanciaría, y que por construcción no
        # puede expresar la distinción: el criterio jamás dispara.
        share = self._share_of(here, signature)
        separate = self._prior[here][before, command] * share + pocket[before, command]
        self._code[here][1] += -float(np.log(separate[after] / separate.sum()))

        self._evidence[here][before, command, after] += 1.0
        pocket[before, command, after] += 1.0
        self._arrivals[here][signature] += 1.0
        self._updates += 1

        if self._code[here][1] < self._code[here][0] and len(self._incoming[here]) > 1:
            self._refine(here)

        self._came_from = (self._here, command)
        self._here = self._next_state(self._here, command, after)

    # --- refinamiento --------------------------------------------------------

    def _next_state(self, state: int, command: int, following: int) -> int:
        """`δ(z, (a, o'))` con **backoff estructural** por la cadena de padres.

        Un hijo hereda la dinámica de salida de su padre, y la evidencia la
        especializa sólo donde el split la justifica. Sin esto, la ausencia de una
        entrada explícita se leía como

            «sé que debo quedarme aquí»

        cuando lo único cierto era

            «no tengo una transición especializada».

        Son afirmaciones distintas, y confundirlas hacía el autómata **absorbente**:
        el organismo entraba en un hijo y no salía nunca --0 % de cambios de estado
        donde una partición de profundidad 1 exige ~75 %.

            UNKNOWN ROUTE  ≠  STAY

        `ROOT` sí se queda en sí mismo por defecto, y eso es correcto: con un solo
        estado toda transición conduce a él. La totalidad semántica de `δ` viene de
        la cadena, no de materializar la tabla entera.
        """
        node: int | None = state
        while node is not None:
            found = self._routing.get((node, command, following))
            if found is not None:
                return found
            node = self._parent[node]
        return ROOT

    def routing_is_total(self) -> bool:
        """Todo estado activo tiene `δ` definida para todo símbolo, por ruta o herencia."""
        for state in self.states():
            for command in range(4):
                for following in range(16):
                    if self._next_state(state, command, following) not in self._prior:
                        return False
        return True

    def parent_of(self, state: int) -> int | None:
        return self._parent[state]

    def _share_of(self, state: int, signature: tuple[int, int]) -> float:
        """La porción del prior heredado que esta firma recibiría al separarse.

        Misma regla que usa `_refine`, para que la contabilidad prequencial
        puntúe exactamente la hipótesis que se instanciaría y no otra.
        """
        arrivals = self._arrivals[state]
        total = sum(arrivals.values()) + len(arrivals) + 1.0
        return (arrivals.get(signature, 0.0) + 1.0) / total

    def _refine(self, state: int) -> None:
        """Separar `state` por firma de entrada, conservando la masa heredada.

        El padre **no se vacía**: conserva una parte y sigue siendo el destino de
        las firmas que todavía no han llegado. Si se quedara a masa cero, una
        firma nueva aterrizaría en un estado sin prior y la predicción estaría
        indefinida.

        El reparto es proporcional a la evidencia que cada firma trajo, suavizado
        con un uno para que ninguna rama nazca vacía, y suma exactamente el prior
        del padre.
        """
        signatures = sorted(self._incoming[state],
                            key=lambda s: (-self._arrivals[state][s], s))
        if len(signatures) < 2:
            return
        amounts = np.array([self._arrivals[state][s] + 1.0 for s in signatures]
                           + [1.0])                       # la última: el padre
        shares = amounts / amounts.sum()
        parent = self._prior[state]

        for share, signature in zip(shares[:-1], signatures):
            born = max(self._prior) + 1
            self._prior[born] = parent * share
            self._evidence[born] = self._incoming[state][signature].copy()
            self._incoming[born] = {}
            self._arrivals[born] = {}
            self._code[born] = [0.0, 0.0]
            self._parent[born] = state
            for following in range(16):
                self._routing[(signature[0], signature[1], following)] = born

        self._prior[state] = parent * shares[-1]
        self._evidence[state] = np.zeros((16, 4, 16))
        self._incoming[state] = {}
        self._arrivals[state] = {}
        self._code[state] = [0.0, 0.0]
        self._splits += 1

    # --- estado, lesión y organización ---------------------------------------

    @property
    def updates(self) -> int:
        return self._updates

    @property
    def refinements(self) -> int:
        return self._splits

    def states(self) -> list[int]:
        return sorted(k for k in self._prior if self._prior[k].sum() > 0)

    def inherited_mass(self) -> list[np.ndarray]:
        """Lo que `L18-4` audita: el reparto del prior heredado."""
        return [self._prior[k] for k in sorted(self._prior)]

    def lesion(self) -> None:
        """Colapsar `Z` a `{z_0}` y borrar SÓLO lo adquirido en 1.8."""
        self._prior = {ROOT: self._inherited.copy()}
        self._evidence = {ROOT: np.zeros((16, 4, 16))}
        self._routing = {}
        self._incoming = {ROOT: {}}
        self._arrivals = {ROOT: {}}
        self._code = {ROOT: [0.0, 0.0]}
        self._here = ROOT
        self._came_from = None

    def organization(self, probes) -> dict:
        """Dónde aterriza cada sonda. `L18-6` lo canoniza por bloques."""
        landing = {}
        for name, steps in probes.items():
            self.begin()
            for command, following in steps:
                self._here = self._routing.get((self._here, command, following),
                                               self._here)
            landing[name] = self._here
        self.begin()
        return landing
