#!/usr/bin/env python
"""G4 — una ablación que apaga dos cosas no mide ninguna.

El tamizado reportó dos hallazgos significativos: «modelo del mundo +6.33
comidas» y «planificador +6.67». Son la misma intervención. La rama del planner
está condicionada a los DOS flags

    if self._use_planner and self._use_world_model:

así que `use_world_model=False` deja al planificador sin invocar. Medido: 40 de
40 llamadas con la configuración completa, 0 de 40 con cualquiera de los dos
flags apagados. La conjunción `anticipacion` elimina esa misma ruta, que es por
qué su residuo salía fuertemente sub-aditivo.

Nada de eso era visible desde el resultado. El número era plausible, el efecto
grande y el signo el esperado. Lo único que lo delata es contar quién se ejecuta.

Este comprobador cuenta las invocaciones de cada mecanismo bajo la configuración
base y bajo la ablación, con la misma semilla y las mismas observaciones. Si
cambia el conteo de un mecanismo que no es el declarado, la intervención es
impura y su efecto no es atribuible: es NON_IDENTIFIABLE, no un hallazgo.

    python scripts/purity_check.py use_world_model
    python scripts/purity_check.py --all
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import torch

from terrario.agent.agents import create_agent
from terrario.agent.agents.a4_advanced import DEFAULT_CONFIG
from terrario.core.contracts import Transition
from terrario.core.types import Action, Consequence, Observation

#: Qué mecanismo declara apagar cada flag. Un flag cuya ablación cambie el
#: conteo de OTRO mecanismo no está midiendo lo que su nombre dice.
#: `use_entropy_regularization` no tiene módulo: altera un término de la pérdida,
#: así que ningún conteo debería moverse.
DECLARED_TARGET = {
    "use_temporal": {"temporal_core"},
    "use_episodic_memory": {"episodic_memory"},
    "use_longterm_memory": {"longterm_memory"},
    "use_world_model": {"world_model"},
    "use_uncertainty": {"uncertainty_estimator"},
    "use_planner": {"planner"},
    "use_online_learning": {"learner"},
    "use_homeostasis": {"homeostasis"},
    "use_entropy_regularization": set(),
    "use_factored_action": {"operation_head", "selector_head"},
}

#: mecanismo -> (atributo del agente, métodos a contar)
WATCHED = {
    "encoder": ("encoder", ("forward", "encode_observation")),
    "temporal_core": ("temporal_core", ("forward",)),
    "episodic_memory": ("episodic_memory", ("read", "write")),
    "longterm_memory": ("longterm_memory", ("read", "write")),
    "world_model": ("world_model", ("forward", "loss")),
    "uncertainty_estimator": ("uncertainty_estimator", ("predict",)),
    "planner": ("planner", ("plan",)),
    "policy_head": ("policy_head", ("forward", "sample")),
    "homeostasis": ("homeostasis", ("update",)),
    "learner": ("learner", ("step",)),
    "operation_head": ("operation_head", ("forward",)),
    "selector_head": ("selector_head", ("forward",)),
}


def instrument(agent) -> dict[str, int]:
    """Envuelve los métodos vigilados y devuelve el contador vivo."""
    counts: dict[str, int] = {}
    for mechanism, (attribute, methods) in WATCHED.items():
        holder = getattr(agent, attribute, None)
        if holder is None:
            continue
        counts[mechanism] = 0
        for method in methods:
            original = getattr(holder, method, None)
            if not callable(original):
                continue

            def wrapper(*args, _m=mechanism, _f=original, **kwargs):
                counts[_m] += 1
                return _f(*args, **kwargs)

            try:
                setattr(holder, method, wrapper)
            except (AttributeError, TypeError):
                # Un módulo que no admite atributos de instancia se queda sin
                # contar y se dice, en vez de reportarse como cero invocaciones.
                counts[mechanism] = -1
    return counts


def exercise(agent, steps: int, seed: int) -> None:
    """Percibir, decidir y aprender con entrada idéntica para ambos brazos."""
    rng = np.random.RandomState(seed)
    channels = rng.rand(4, 5, 5).astype(np.float32)
    observation = Observation(
        channels=channels, mask=np.ones((5, 5), dtype=np.float32),
        agent_energy=0.6, time_fraction=0.0)
    for step in range(steps):
        agent.perceive(observation)
        action = agent.decide()
        agent.learn(Transition(
            observation_t=observation, internal_state_ref=None,
            action_t=action if isinstance(action, Action) else Action.noop(),
            consequence_t1=Consequence(energy_delta=-0.06, events=[],
                                       new_observation=observation, done=False),
            observation_t1=observation, terminated=False, truncated=False,
            step=step, seed=seed))


def counts_for(config: dict, steps: int, seed: int) -> dict[str, int]:
    torch.manual_seed(seed)
    agent = create_agent({"agent_id": "A4", "config": config},
                         {"num_channels": 4, "view_size": 5}, seed=seed)
    counts = instrument(agent)
    exercise(agent, steps, seed)
    return counts


def audit(flag: str, steps: int, seed: int) -> bool:
    if flag not in DEFAULT_CONFIG:
        print(f"no existe el flag {flag!r}")
        return False
    default = bool(DEFAULT_CONFIG[flag])
    base = counts_for({}, steps, seed)
    ablated = counts_for({flag: not default}, steps, seed)

    target = DECLARED_TARGET.get(flag, set())
    mechanisms = sorted(set(base) | set(ablated))
    disabled: list[str] = []
    diverted: list[str] = []
    reduced: list[str] = []

    print(f"\n{flag}  ({default} -> {not default})   {steps} decisiones, semilla {seed}")
    print(f"  objetivo declarado: {', '.join(sorted(target)) or '(ninguno: cambia una pérdida)'}")
    print(f"  {'mecanismo':<24}{'base':>8}{'ablado':>8}   ")
    for mechanism in mechanisms:
        before, after = base.get(mechanism, 0), ablated.get(mechanism, 0)
        if before == -1 or after == -1:
            print(f"  {mechanism:<24}{'?':>8}{'?':>8}   no instrumentable")
            continue
        mark = ""
        if mechanism in target:
            mark = "objetivo declarado"
        elif after == 0 and before > 0:
            # Otro mecanismo queda enteramente sin ejecutar. Eso no es una
            # consecuencia de quitar el objetivo: es que su ejecución estaba
            # condicionada al mismo flag. Es el caso de `planner`, gateado por
            # `use_planner AND use_world_model`.
            mark = "<-- DESACTIVADO"
            disabled.append(mechanism)
        elif after > before:
            # Sube: otra ruta tomó el relevo. Sin el planner, cada decisión
            # muestrea de la política en vez de la mitad de las veces.
            mark = "<-- DESVIADO"
            diverted.append(mechanism)
        elif after < before:
            mark = "(menos llamadas)"
            reduced.append(mechanism)
        print(f"  {mechanism:<24}{before:>8}{after:>8}   {mark}")

    if reduced:
        # Compatible con pureza, no prueba de ella: un objetivo que llama a otro
        # mecanismo dentro de su propio trabajo deja de llamarlo al desaparecer.
        # El instrumento NO puede distinguir eso de una ruta compartida que se
        # atenúa, y decirlo es parte de la lectura.
        print(f"\n  menos llamadas (compatible con pureza, no prueba de ella): "
              f"{', '.join(reduced)}")

    if disabled or diverted:
        if disabled:
            print(f"\n  IMPURA: la ablación DESACTIVA por completo {', '.join(disabled)}.")
        if diverted:
            print(f"\n  IMPURA: la ablación DESVÍA conducta hacia {', '.join(diverted)}.")
        print("  El efecto no es atribuible al mecanismo declarado: NON_IDENTIFIABLE.")
        return False

    print("\n  pura: ningún otro mecanismo queda desactivado ni recibe el relevo.")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("flag", nargs="?", help="por ejemplo use_world_model")
    parser.add_argument("--all", action="store_true", help="audita todos los flags")
    parser.add_argument("--steps", type=int, default=40)
    parser.add_argument("--seed", type=int, default=5)
    args = parser.parse_args()

    if not args.all and not args.flag:
        parser.error("indica un flag o --all")

    flags = sorted(DECLARED_TARGET) if args.all else [args.flag]
    impure = [flag for flag in flags if not audit(flag, args.steps, args.seed)]

    if impure:
        print(f"\n{len(impure)} de {len(flags)} intervenciones impuras: {', '.join(impure)}")
        return 1
    print(f"\n{len(flags)} intervención(es), todas puras")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
