#!/usr/bin/env python
"""Plasticidad residual · el endpoint que no teníamos.

Medimos rendimiento retenido. No medimos si el organismo sigue pudiendo
aprender. De la metalurgia: un metal deformado repetidamente rinde igual o
mejor y pierde ductilidad. Traducido: el organismo podría forrajear
perfectamente y tardar cada vez más en adquirir lo siguiente.

Dos lecturas con signos OPUESTOS, y es lo que las hace separables:

    CANALIZACIÓN    más práctica previa ⇒ lo adquirido es más robusto, y la
                    adquisición siguiente cuesta lo mismo o menos.
    ENDURECIMIENTO  más práctica previa ⇒ menos plasticidad, y la adquisición
                    siguiente cuesta MÁS, aunque el rendimiento no baje.

Protocolo: el mismo nacimiento recibe dosis distintas de adquisición sobre el
primer mundo, y después TODOS reciben la misma segunda adquisición sobre un
mundo con la contingencia invertida. Se mide qué gana cada uno en el segundo
--con el banco de sondas, no con conducta-- y si lo del primero sigue ahí.

    python scripts/test_residual_plasticity.py --nacimientos 8
"""

from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.agent.agents import create_agent  # noqa: E402
from terrario.core.rng import RNGManager  # noqa: E402
from terrario.lab.causal_bench import (  # noqa: E402
    REGIME_INTERVENTIONS, BirthSnapshot, PairedResult,
)
from terrario.lab.diagnostic_probes import build_probe_bank, gain, read_bank  # noqa: E402
from terrario.world.transition import build_episode_components, run_step  # noqa: E402

sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from exp_adaptive_foraging_01 import (  # noqa: E402
    BASE, MAX_ENERGY, force_action, rich_world,
)

SEED_BASE = 7000
#: Dosis de la PRIMERA adquisición. La segunda es idéntica para todos.
DOSES = (0, 75, 150, 300)
SECOND_DOSE = 150


def hostile_world(seed: int, duration: int) -> dict[str, Any]:
    """Segundo mundo: la misma comida, la contingencia invertida.

    El canal 3 alto ahora CUESTA en vez de pagar. Aprender esto exige revisar
    lo que el primer mundo enseñó, que es justo lo que pone a prueba la
    plasticidad residual en vez de la acumulación."""
    scenario = rich_world(seed, duration=duration)
    scenario = dict(scenario)
    scenario["name"] = f"invertido_{seed}"
    scenario["rules"] = {"rules": [{
        "id": "castigo",
        "condition": {"object_channel": {"index": 3, "min": 0.8}, "action": "CONSUME"},
        "effect": {"energy_delta": -6.0}}]}
    return scenario


def _record(seed: int, scenario: dict[str, Any], steps: int) -> list[dict[str, Any]]:
    comps = build_episode_components(scenario, duration_fallback=steps,
                                     strict_physics=True, with_lifecycle=False,
                                     world_seed=seed)
    RNGManager.set_global_determinism(seed)
    recorder = create_agent("A4_ADVANCED", dict(BASE), seed=seed)
    stream = []
    for step in range(steps):
        out = run_step(comps, recorder, step, world_seed=seed, agent_seed=seed,
                       max_steps=steps, learning_enabled=True)
        stream.append({"observation": out.observation_t,
                       "action_int": out.action.to_int(), "transition": out.transition})
        if out.terminated or out.truncated:
            break
    return stream


def _feed(agent: Any, stream: list[dict[str, Any]]) -> None:
    for i, entry in enumerate(stream):
        agent.adaptive_freeze.set_step(i)
        agent.perceive(entry["observation"])
        agent.decide()
        force_action(agent, entry["action_int"])
        agent.learn(entry["transition"])


def run_birth(index: int, *, probe_distance: int):
    seed = SEED_BASE + index
    bank = build_probe_bank()
    birth = BirthSnapshot.materialize(f"plast-{index:03d}", BASE, seed=seed)

    first = _record(seed, rich_world(seed, duration=max(DOSES) or 1), max(DOSES))
    second = _record(seed + 500_000, hostile_world(seed + 500_000, SECOND_DOSE), SECOND_DOSE)
    if not first or not second:
        return None

    out: dict[int, dict[str, float]] = {}
    for dose in DOSES:
        arm = birth.twin(f"dose-{dose}", REGIME_INTERVENTIONS["NORMAL"])
        agent = arm.specimen
        pre_first = read_bank(agent, bank)
        if dose:
            _feed(agent, first[:dose])
        pre_second = read_bank(agent, bank)
        _feed(agent, second)
        post_second = read_bank(agent, bank)
        out[dose] = {
            "gain_first": gain(pre_first, pre_second)["discrimination"],
            "gain_second": gain(pre_second, post_second)["discrimination"],
            "retained_first": pre_second.discrimination,
            "final": post_second.discrimination,
        }
    return {"birth": birth.pair_id, "by_dose": out}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--nacimientos", type=int, default=8)
    parser.add_argument("--distancia", type=int, default=3)
    args = parser.parse_args()

    print("PLASTICIDAD RESIDUAL · ¿la práctica previa abarata o encarece lo siguiente?\n")
    print("  CANALIZACIÓN    más dosis previa ⇒ ganancia segunda IGUAL o MAYOR")
    print("  ENDURECIMIENTO  más dosis previa ⇒ ganancia segunda MENOR\n")

    runs = []
    for index in range(args.nacimientos):
        result = run_birth(index, probe_distance=args.distancia)
        if result is None:
            continue
        runs.append(result)
        row = " ".join(f"{result['by_dose'][d]['gain_second']:+.5f}" for d in DOSES)
        print(f"  {result['birth']}: ganancia en la segunda por dosis → {row}")

    if not runs:
        print("\n  sin datos")
        return 2

    n = len(runs)
    print(f"\n\n  n = {n} nacimientos · la segunda adquisición es IDÉNTICA para todas las dosis\n")
    print(f"  {'dosis previa':<14}{'ganancia 1ª':>15}{'ganancia 2ª':>15}"
          f"{'retenido de la 1ª':>20}")
    print("  " + "-" * 64)
    for dose in DOSES:
        print(f"  {dose:<14}"
              f"{statistics.fmean(r['by_dose'][dose]['gain_first'] for r in runs):>+15.6f}"
              f"{statistics.fmean(r['by_dose'][dose]['gain_second'] for r in runs):>+15.6f}"
              f"{statistics.fmean(r['by_dose'][dose]['retained_first'] for r in runs):>+20.6f}")

    low, high = DOSES[0], DOSES[-1]
    contrast = PairedResult(
        "ganancia 2ª: dosis alta − dosis nula",
        [r["by_dose"][high]["gain_second"] - r["by_dose"][low]["gain_second"] for r in runs])
    lo, hi = contrast.bootstrap()
    print(f"\n  {contrast.name}: {contrast.mean:+.6f}  IC95% [{lo:+.6f}, {hi:+.6f}]  "
          f"signo − en {sum(1 for d in contrast.deltas if d < 0) / n:.0%}")

    print("\n  LECTURA")
    if hi < 0:
        print("    La práctica previa ENCARECE la adquisición siguiente.")
        print("    Compatible con ENDURECIMIENTO: hay degradación que el rendimiento no muestra.")
    elif lo > 0:
        print("    La práctica previa ABARATA la adquisición siguiente.")
        print("    Compatible con CANALIZACIÓN; incompatible con endurecimiento.")
    else:
        print("    El intervalo cruza el cero: con esta n no se separan las dos lecturas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
