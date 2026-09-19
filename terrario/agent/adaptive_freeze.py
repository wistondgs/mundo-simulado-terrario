"""OCF-G3 · La autoridad única sobre el conjunto adaptativo.

`learning_commit_enabled` suprime `optimizer.step()` y nada más. Medido en
`docs/FRONTERA_ESTADO_APRENDIDO_01.md`: el brazo suprimido conserva tres piezas
de conocimiento adquirido, y una de ellas recorre decenas de veces su magnitud
inicial. `LEARNING_COMMIT_IS_COMPLETE_FREEZE = NO`.

Esto congela la frontera entera y ya adoptada:

    A = { θ, EpisodicBuffer, M, energy_baseline }

y nada más. El estado recurrente ordinario, la física del mundo, el paso, la
percepción y las cachés operativas siguen evolucionando: están declarados fuera
de `adaptive_state` y ampliar la frontera aquí convertiría esto en otra
auditoría general.

**Bloquea escrituras; no restaura instantáneas.** La diferencia es causal y no
cosmética: `escribir → leer → revertir` no equivale a `no escribir → leer`,
aunque las dos terminen con el mismo hash. Lo que se quiere demostrar es la
AUSENCIA de adaptación, no su apariencia al final de la corrida. Por eso cada
llamada a `allow` ocurre *antes* de que la escritura suceda y, cuando devuelve
False, la escritura no llega a ejecutarse.

**Registra los intentos.** Un brazo congelado que termina idéntico no prueba
nada si nadie intentó escribir. El libro mayor distingue

    congelado, ningún writer lo intentó          -- no es evidencia
    congelado, cuatro writers intentaron y se bloquearon   -- sí lo es

y es lo que exige OCF-G3.4.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable

#: Las cuatro piezas de la frontera adoptada, con el sitio que las escribe.
COMPONENTS: dict[str, str] = {
    "parameters": "learner.py optimizer.step()",
    "episodic_buffer": "memory.py EpisodicMemory.write()",
    "longterm_M": "memory.py LongTermMemory.write() -> M.data.copy_()",
    "energy_baseline": "a4_advanced.py learn() media corrida de la consecuencia",
}

BLOCKED_REASON = "FULL_ADAPTIVE_FREEZE"


@dataclass(frozen=True)
class WriteAttempt:
    """Un intento de escritura sobre el conjunto adaptativo."""

    component: str
    writer: str
    phase: str
    step: int
    attempted: bool
    committed: bool
    blocked_reason: str | None
    before_digest: str | None
    after_digest: str | None


class AdaptiveFreeze:
    """Quién puede escribir el conjunto adaptativo, y qué se intentó.

    `enabled=False` es el organismo de siempre: todo intento se concede y el
    coste es un registro por intento. `enabled=True` es FULL_ADAPTIVE_FREEZE.

    `witness` es opcional y sólo lo usa el arnés de OCF-G3: una función
    `(component) -> str` que da la huella de una pieza. Con ella, cada intento
    guarda la huella de antes y la de después, que es lo que permite demostrar
    que ninguna pieza mutó y volvió (OCF-G3.5). Sin ella no se calcula nada:
    una autoridad que costara un hash por paso en la corrida normal dejaría de
    ser pasiva.
    """

    def __init__(self, *, enabled: bool = False,
                 witness: Callable[[str], str] | None = None) -> None:
        self._enabled = bool(enabled)
        self._witness = witness
        self._attempts: list[WriteAttempt] = []
        self._step = 0

    # --- estado ------------------------------------------------------------

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def attempts(self) -> tuple[WriteAttempt, ...]:
        return tuple(self._attempts)

    def set_witness(self, witness: Callable[[str], str] | None) -> None:
        self._witness = witness

    def set_step(self, step: int) -> None:
        """El paso al que atribuir los intentos siguientes."""
        self._step = int(step)

    # --- la decisión -------------------------------------------------------

    def allow(self, component: str, *, phase: str = "learn") -> bool:
        """¿Puede escribirse `component` ahora? Registra el intento siempre.

        Devuelve True cuando la escritura puede proceder. El llamante DEBE
        omitir la escritura cuando esto devuelve False -- ésa es la diferencia
        entre bloquear y revertir.
        """
        if component not in COMPONENTS:
            raise KeyError(f"componente fuera de la frontera adaptativa: {component!r}; "
                           f"hay {sorted(COMPONENTS)}")
        committed = not self._enabled
        before = self._witness(component) if self._witness else None
        self._attempts.append(WriteAttempt(
            component=component, writer=COMPONENTS[component], phase=phase,
            step=self._step, attempted=True, committed=committed,
            blocked_reason=None if committed else BLOCKED_REASON,
            before_digest=before, after_digest=None))
        return committed

    def settle(self) -> None:
        """Cerrar las huellas `after` de los intentos del paso en curso.

        Se llama tras la fase, cuando las escrituras concedidas ya ocurrieron.
        Sin `witness` no hace nada.
        """
        if self._witness is None:
            return
        for i, a in enumerate(self._attempts):
            if a.after_digest is None and a.before_digest is not None:
                self._attempts[i] = WriteAttempt(
                    **{**a.__dict__, "after_digest": self._witness(a.component)})

    # --- lectura -----------------------------------------------------------

    def summary(self) -> dict[str, dict[str, int]]:
        """Por componente: intentos, concedidos, bloqueados."""
        out = {c: {"attempted": 0, "committed": 0, "blocked": 0} for c in COMPONENTS}
        for a in self._attempts:
            out[a.component]["attempted"] += 1
            out[a.component]["committed" if a.committed else "blocked"] += 1
        return out

    def mutated_under_block(self) -> tuple[WriteAttempt, ...]:
        """Intentos bloqueados en los que la pieza cambió de todos modos.

        Si esto no está vacío, algún writer esquivó el interruptor (condición
        de parada 6) o el freeze se implementó como reversión (OCF-G3.5).
        """
        return tuple(a for a in self._attempts
                     if not a.committed and a.before_digest is not None
                     and a.after_digest is not None
                     and a.before_digest != a.after_digest)

    def reset(self) -> None:
        self._attempts.clear()
        self._step = 0

    def get_trace(self) -> list[dict[str, Any]]:
        """Eventos para el observador. Vacía el libro mayor, como los demás."""
        events = [{"op": "adaptive_freeze_attempt", **a.__dict__} for a in self._attempts]
        self._attempts.clear()
        return events


def combine(freeze: AdaptiveFreeze | None, component: str, *,
            also: Iterable[bool] = ()) -> bool:
    """`freeze.allow(component)` evaluado SIEMPRE, y luego combinado.

    Existe para que un `and` de cortocircuito no se coma el registro del
    intento: si `learning_commit_enabled` ya era False, sin esto el intento de
    escribir parámetros no aparecería en el libro mayor y OCF-G3.4 no tendría
    con qué distinguir «bloqueado» de «nadie lo intentó».
    """
    allowed = True if freeze is None else freeze.allow(component)
    return allowed and all(also)
