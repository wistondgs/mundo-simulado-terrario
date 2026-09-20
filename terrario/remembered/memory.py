"""El registro temporal del Nivel 1.3 · un token, un tick, y nada más.

**Guarda el token, no la dirección.** Si guardara `Direction`, el Nivel 1.3
estaría suplantando la semántica que es el mecanismo del Nivel 1.1, y el nivel
dejaría de medir persistencia para medir otra cosa. La cadena causal correcta es
`g → M → Q(M,a) → a`.

**Leer antes del tick devuelve nada.** Es la decisión que hace falsable al nivel:
si `peek` a edad cero devolviera el cue, un arnés que se saltara `tick()` pasaría
los gates de retención y de uso de historia igual de verde, y «persistencia a
través de un intervalo» no quedaría probada en ninguna parte.

**Leer no consume.** La consulta es pura y sólo `reset()` borra. Tres de las seis
métricas leen el mismo slot; si la primera lo vaciara, la segunda mediría sobre
una memoria vacía y la pasividad caería contra el uso de historia en la misma
corrida.

**Escribir sólo acepta `CueToken`.** «No hay cue» se expresa **no llamando a
`write`**, nunca llamándolo con nada: así el borrado temprano deja de ser
expresable. El cuidado no es teórico --`CueToken` y `Direction` son los dos
`IntEnum` con los mismos valores, así que `CueToken.C0 == Direction.UP` es cierto
al comparar; sólo `isinstance` los distingue.
"""

from __future__ import annotations

import enum
import hashlib

from terrario.level11.cue import CueToken


class MemoryPhase(enum.Enum):
    """Los tres estados. `HELD_0` **no** es consultable; `HELD_1` sí."""

    EMPTY = "EMPTY"
    HELD_0 = "HELD_0"
    HELD_1 = "HELD_1"


class MemoryContractError(TypeError):
    """`SEMANTIC_MEMORY_LEAKAGE` o `MEMORY_EARLY_ERASURE`, según el caso."""


class OneStepCueMemory:
    """Capacidad uno, TTL uno. Sin secuencia, sin pila, sin buffer, sin replay."""

    def __init__(self) -> None:
        self._slot: CueToken | None = None
        self._age: int | None = None

    # --- escritura -----------------------------------------------------------

    def write(self, cue: CueToken) -> None:
        """Sobrescribe siempre: gana el último cue válido. Nunca vacía."""
        if not isinstance(cue, CueToken):
            raise MemoryContractError(
                f"la memoria sólo acepta CueToken; recibió {type(cue).__name__}"
                f" ({cue!r}). La ausencia de señal se expresa NO llamando a write.")
        self._slot = cue
        self._age = 0

    # --- tiempo ---------------------------------------------------------------

    def tick(self) -> None:
        if self._slot is None:
            return
        if self._age == 0:
            self._age = 1
        else:
            self._slot = None
            self._age = None

    # --- lectura pura ----------------------------------------------------------

    def peek(self) -> CueToken | None:
        """`R(c,1) = c` · `R(c,0) = NONE` · `R(∅) = NONE`. No muta nada."""
        if self._slot is None or self._age != 1:
            return None
        return self._slot

    # --- borrado explícito ------------------------------------------------------

    def reset(self) -> None:
        self._slot = None
        self._age = None

    # --- introspección pasiva ----------------------------------------------------

    @property
    def phase(self) -> MemoryPhase:
        if self._slot is None:
            return MemoryPhase.EMPTY
        return MemoryPhase.HELD_0 if self._age == 0 else MemoryPhase.HELD_1

    def fingerprint(self) -> str:
        h = hashlib.sha256()
        h.update(repr((self._slot, self._age)).encode())
        return h.hexdigest()


class NoMemory:
    """El control sin persistencia. No hay canal: `peek` siempre devuelve nada."""

    def write(self, cue: CueToken) -> None:
        return None

    def tick(self) -> None:
        return None

    def peek(self) -> CueToken | None:
        return None

    def reset(self) -> None:
        return None

    @property
    def phase(self) -> MemoryPhase:
        return MemoryPhase.EMPTY

    def fingerprint(self) -> str:
        return "sin-memoria"


class WriteDisabledMemory(OneStepCueMemory):
    """La arquitectura existe y `write` es no-op. Preregistrado: **igual a
    `NoMemory`**. Se conserva sólo como control de la causalidad de la escritura,
    no como contraste independiente."""

    def write(self, cue: CueToken) -> None:
        if not isinstance(cue, CueToken):
            raise MemoryContractError("la memoria sólo acepta CueToken")
        return None


class UnlimitedMemory(OneStepCueMemory):
    """FIXTURE NEGATIVA de L13-12: no expira nunca hasta `reset`.

    No es «mejor»: es `LEVEL13_SCOPE_EXPANSION`. Existe para que el contrato de
    contención del horizonte pueda fallar.
    """

    def tick(self) -> None:
        if self._slot is not None and self._age == 0:
            self._age = 1


class ImmediateMemory(OneStepCueMemory):
    """FIXTURE NEGATIVA de L13-13: consultable sin haber atravesado el tick.

    Es exactamente el registro que el nivel NO quiere demostrar: almacenamiento
    accesible al instante en vez de persistencia a través de un intervalo.
    """

    def peek(self) -> CueToken | None:
        return self._slot
