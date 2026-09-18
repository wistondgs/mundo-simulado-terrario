"""A5 — A4 con un motivo propio para moverse.

No es A4 con una bandera. Es su descendiente: mismo sustrato, mismos módulos,
misma física, y una diferencia que cabe en un método. A4 permanece intacto como
ancestro **y como brazo de control**, lo que hace de la comparación A4 vs A5 la
intervención causal más limpia que este proyecto puede montar — no un flag
dentro de un organismo, sino dos organismos que difieren en una cosa nombrada.

Lo que cambia, y es todo lo que cambia: A4 se refuerza sobre la consecuencia
metabólica y nada más; A5 suma la señal intrínseca de CURIO-A1. Toda la
superficie causal de la capacidad es `_policy_reward`, que es exactamente lo que
la hace ablacionable: apagar `use_curiosity` devuelve A4, bit a bit.

Procedencia: `CLM-0122` (Pathak 2017, TI-0090, §2, pp. 2–3) — «El error del
modelo directo se entrega al agente como señal de recompensa intrínseca». La
señal entra por la **recompensa**, no por los logits. Esa distinción no es
estilística: el pasaporte de CURIO-A1 declara que sumarla a los logits haría que
`purity_check` la declarase PURE por construcción y el gate pasara en vacío.
"""

from __future__ import annotations

from typing import Any

from terrario.agent.agents.a4_advanced import A4Advanced
from terrario.agent.curiosity import IntrinsicPredictionError
from terrario.core.contracts import Transition


class A5Cybernetic(A4Advanced):
    """A4 cuyo lazo de predicción llega a la conducta en vez de a la libreta."""

    def __init__(self, config: dict[str, Any] | None = None, generator=None):
        super().__init__(config=config, generator=generator)
        self._use_curiosity: bool = bool(self.config.get("use_curiosity", True))
        self.curiosity = IntrinsicPredictionError(
            scale=float(self.config.get("curiosity_scale", 1.0)),
            floor_decay=float(self.config.get("curiosity_floor_decay", 0.01)),
        )

    def _policy_reward(self, consequence: Transition) -> float:
        """Consecuencia metabólica más el error de la propia predicción.

        `last_prediction_error` ya fue escrito por `learn()` para ESTE paso
        antes de llegar aquí, así que la señal es del paso que se está
        reforzando y no del anterior. Con `use_curiosity` apagado esto es
        idéntico a A4, que es la ablación.
        """
        extrinsic = super()._policy_reward(consequence)
        if not self._use_curiosity:
            return extrinsic
        return extrinsic + self.curiosity.signal(self.last_prediction_error)

    def get_internal_state(self) -> dict[str, Any]:
        state = super().get_internal_state()
        state["curiosity"] = self.curiosity.state()
        return state

    def reset(self) -> None:
        super().reset()
        self.curiosity.reset()
