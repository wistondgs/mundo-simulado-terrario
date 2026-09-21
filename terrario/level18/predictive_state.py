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
        # --- fusión (Enmienda 02). El criterio y el momento del split NO cambian.
        self._children: dict[int, list[int]] = {}      # splits abiertos
        self._favour: dict[int, float] = {}            # balance colapsado − refinado
        self._shadow: dict[int, np.ndarray] = {}       # evidencia de la hipótesis colapsada
        self._collapsed_prior: dict[int, np.ndarray] = {}
        self._episodes: list[dict] = []

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

    def _advance(self, command: int, after: int) -> None:
        self._here = self._next_state(self._here, command, after)

    def follow(self, efference, following) -> None:
        """Seguir la propia dinámica sin aprender nada.

        Predecir exige estar en el estado correcto, y el estado es recursivo:
        `Z_t = F(Z_{t-1}, A_{t-1}, O_t)`. Seguirlo consume sólo la copia eferente
        y la observación --nada que el organismo no tenga ya-- y no toca ni una
        cuenta: seguir no es aprender. Sin esto, puntuar un banco deja al modelo
        clavado donde empezó, y lo que se mide es la raíz de un árbol cuya
        evidencia se marchó a las hojas.
        """
        self._advance(_command_index(efference),
                      _observation_index(following, "la observación siguiente"))

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

        self._judge_open_split(here, before, command, after)

        self._came_from = (self._here, command)
        self._advance(command, after)

    # --- refinamiento --------------------------------------------------------

    def _ancestor_with_open_split(self, state: int) -> int | None:
        node: int | None = state
        while node is not None:
            if node in self._children:
                return node
            node = self._parent[node]
        return None

    def _judge_open_split(self, state: int, before: int, command: int,
                          after: int) -> None:
        """Enmienda 02 · la misma hipótesis, juzgada a lo largo del tiempo.

        `favor` NO se reinicia tras separar: arranca con el balance que justificó
        el split y sigue acumulando. Si empezara de cero, la penalización de
        complejidad desharía casi todo refinamiento de inmediato y el mecanismo
        oscilaría sin que la evidencia tuviera nada que ver.

            favor > 0   la distinción paga su complejidad   → mantener
            favor ≤ 0   ya no la paga                       → fusionar

        El `≤` resuelve el empate a favor del modelo más simple. No es un umbral.
        """
        ancestor = self._ancestor_with_open_split(state)
        if ancestor is None:
            return
        collapsed = (self._collapsed_prior[ancestor][before, command]
                     + self._shadow[ancestor][before, command])
        refined = self._weights(state, before, command)
        self._favour[ancestor] += (
            -float(np.log(collapsed[after] / collapsed.sum()))
            + float(np.log(refined[after] / refined.sum())))
        self._shadow[ancestor][before, command, after] += 1.0
        if self._favour[ancestor] <= 0.0:
            self._collapse(ancestor)

    def _descendants(self, state: int) -> list[int]:
        found = []
        pending = list(self._children.get(state, ()))
        while pending:
            node = pending.pop()
            found.append(node)
            pending.extend(self._children.get(node, ()))
        return found

    def _collapse(self, state: int) -> None:
        """Deshacer un split. La masa se suma; nada se borra para que luzca bien."""
        family = self._descendants(state)
        if not family:
            return
        self._prior[state] = self._collapsed_prior[state].copy()
        pooled = self._evidence[state].copy()
        for node in family:
            pooled += self._evidence[node]
        self._evidence[state] = pooled
        for node in family:
            for key, arrow in list(self._routing.items()):
                if arrow == node or key[0] == node:
                    del self._routing[key]
            for store in (self._prior, self._evidence, self._incoming,
                          self._arrivals, self._code, self._parent):
                store.pop(node, None)
            for store in (self._children, self._favour, self._shadow,
                          self._collapsed_prior):
                store.pop(node, None)
        self._children.pop(state, None)
        self._favour.pop(state, None)
        self._shadow.pop(state, None)
        self._collapsed_prior.pop(state, None)
        self._incoming[state] = {}
        self._arrivals[state] = {}
        self._code[state] = [0.0, 0.0]
        if self._here in family:
            self._here = state
        for episode in self._episodes:
            if episode["parent"] == state and not episode["merged"]:
                episode["merged"] = True
        self._merges += 1

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
        born_here: list[int] = []

        for share, signature in zip(shares[:-1], signatures):
            born = max(self._prior) + 1
            born_here.append(born)
            self._prior[born] = parent * share
            self._evidence[born] = self._incoming[state][signature].copy()
            self._incoming[born] = {}
            self._arrivals[born] = {}
            self._code[born] = [0.0, 0.0]
            self._parent[born] = state
            for following in range(16):
                self._routing[(signature[0], signature[1], following)] = born

        # --- contabilidad de la Enmienda 02. NO cambia criterio, momento ni prior.
        self._children[state] = list(born_here)
        self._favour[state] = self._code[state][0] - self._code[state][1]
        self._shadow[state] = self._evidence[state].copy()
        self._collapsed_prior[state] = parent.copy()
        self._episodes.append({"parent": state, "children": list(born_here),
                               "merged": False})

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

    @property
    def collapses(self) -> int:
        return self._merges

    def episodes(self) -> list[dict]:
        """Lo que `L18-17` audita: cada split y si llegó a deshacerse."""
        return [dict(e) for e in self._episodes]

    def dangling_routes(self) -> list[tuple[int, int, int]]:
        """Rutas que apuntan a un estado que ya no existe. Debe estar vacía."""
        return [key for key, arrow in self._routing.items()
                if arrow not in self._prior or key[0] not in self._prior]

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
                self._advance(command, following)
            landing[name] = self._here
        self.begin()
        return landing
