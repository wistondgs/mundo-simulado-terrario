"""La vida de dos fases · predecesora congelada, luego el canal del comando.

```
mundo W
   │
   ├── fase P · T_P pasos · el mecanismo de 1.6 adquiere M_0^W
   │            FREEZE · su huella no vuelve a cambiar
   │
   ├── fase A · T_17 pasos · se abre E_t = A_t^command · adquiere C_17
   │            en paralelo, NO-ACTION ve las MISMAS transiciones sin el comando
   │
   └── banco POST · transiciones nuevas · M_0^W y M_1 se puntúan sobre el mismo
```

`NO-ACTION` no es `M_0^W` y no es un brazo duplicado: es el baseline que
desconfunde. `M_0^W` se congela al acabar la fase P, así que compararle `M_1`
mezcla *información de la acción* con *simplemente más datos*. Medido en el mundo
gemelo B --donde no hay ninguna información de acción-- la ventaja contra `M_0`
congelado es `+0.105` y crece con el presupuesto; contra `NO-ACTION` es `-0.007`,
que es lo que debe ser cuando cuatro veces más parámetros no compran nada.

Una sola fuente motora para las dos fases: `EndogenousMotor` de 1.6, sin
modificar. Lo que cambia es la interpretación de su sorteo --un índice de comando
opaco en vez de una dirección-- y que el cuerpo lo actúa a través del cableado
`φ`. S0 sigue siendo exactamente el mismo sustrato.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np

from terrario.level1.world import Observation
from terrario.level16.motor import EndogenousMotor
from terrario.level16.temporal import OBSERVATION_INDEX, TemporalModel
from terrario.level16.world import build_world, motor_stream
from terrario.level17.contingency import ActionContingencyModel
from terrario.level17.efference import ALL_COMMANDS, CommandToken, EfferenceCopy
from terrario.level17.wiring import ActuatorWiring


@dataclass(frozen=True)
class TwoPhaseLife:
    seed: int
    wiring: ActuatorWiring
    inherited: TemporalModel
    acquired: ActionContingencyModel
    no_action: TemporalModel
    acquisition: tuple[tuple[Observation, CommandToken, Observation], ...]
    all_commands: tuple[CommandToken, ...]
    visits: np.ndarray
    post: tuple[tuple[Observation, CommandToken, Observation], ...]
    trajectory_hash: str
    motor_emitted: int


def live_two_phase(seed: int, predecessor_steps: int, acquisition_steps: int,
                   post_steps: int = 2048,
                   wiring: ActuatorWiring | None = None) -> TwoPhaseLife:
    """Vivir las dos fases en el mismo mundo, con un solo flujo motor."""
    grid = build_world(seed)
    phi = wiring if wiring is not None else ActuatorWiring.sampled(seed)
    motor = EndogenousMotor(motor_stream(seed))
    huella = hashlib.sha256()

    observation = grid.observe()
    emitted: list[CommandToken] = []

    def paso() -> tuple[Observation, CommandToken, Observation]:
        nonlocal observation
        command = ALL_COMMANDS[int(motor.next())]
        emitted.append(command)
        moved, following = grid.step(phi.actuate(command))
        huella.update(bytes([ALL_COMMANDS.index(command), moved,
                             *observation, *following]))
        anterior, observation = observation, following
        return anterior, command, following

    # --- fase P · el mecanismo de 1.6, sin ver el comando
    inherited = TemporalModel()
    for _ in range(predecessor_steps):
        anterior, _command, siguiente = paso()
        inherited.observe(anterior, siguiente)
    inherited.freeze()

    # --- fase A · se abre el canal
    acquired = ActionContingencyModel(inherited)
    no_action = TemporalModel()
    no_action.load(inherited.snapshot())          # parte del mismo sitio...
    visits = np.zeros((16, 4))
    acquisition: list[tuple[Observation, CommandToken, Observation]] = []
    for _ in range(acquisition_steps):
        anterior, command, siguiente = paso()
        acquisition.append((anterior, command, siguiente))
        acquired.observe(anterior, EfferenceCopy(command), siguiente)
        no_action.observe(anterior, siguiente)    # ...pero sigue aprendiendo sin el comando
        visits[OBSERVATION_INDEX[anterior], ALL_COMMANDS.index(command)] += 1
    no_action.freeze()

    # --- banco POST
    post = tuple(paso() for _ in range(post_steps))

    return TwoPhaseLife(seed, phi, inherited, acquired, no_action,
                        tuple(acquisition), tuple(emitted), visits, post,
                        huella.hexdigest(), motor.emitted)
