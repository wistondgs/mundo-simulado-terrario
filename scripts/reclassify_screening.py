#!/usr/bin/env python
"""Re-file the earlier screening against instruments that did not exist when it ran.

The 39 runs are not discarded and they are not marked false. The experiment was
carried out correctly under the instrument available at the time; what changed
afterwards is the laboratory's ability to say which readings were identified.
Deleting them would hide that change. Keeping them, correctly filed, makes the
growth of the lab's own measuring capacity part of the record.

Three verdicts are assigned per reading:

  CONFIRMED_UNDER_CALIBRATED_INSTRUMENT
      the metric now has falsification controls and passes them, and nothing
      about the reading depended on a defect found later.

  SUPERSEDED_BY_INSTRUMENT_CALIBRATION
      the number was produced by an instrument since shown not to identify the
      quantity it was read as. The measurement stands as a record; the
      INTERPRETATION is withdrawn.

  NON_IDENTIFIABLE_BY_SATURATION
      the additive interaction model was asked to predict past the floor of a
      bounded variable, so the residual describes the scale and not the
      conjunction.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.lab.instrument_registry import REGISTRY, state_of

REPORTS = ("runs/noche/tamizado/D4T-1200steps-3seeds.report.json",
           "runs/screening/D4T-1200steps-2seeds-3concepts.report.json")

#: Meshes whose instrument was later found not to identify what it was read as.
#: `aciertos_al_comer` and `mejor_tramo_al_comer` both come out of the eating
#: baseline, which defaulted to zero when an arm had no idle steps -- and an arm
#: whose policy collapsed onto CONSUME has none, so its whole metabolic drain was
#: counted as failed consumes. That is exactly the arm a screening produces.
SUPERSEDED = {
    "aciertos_al_comer": "read as discrimination, but P(hit | consume) has almost no "
                         "support in an arm that barely consumes, and the baseline "
                         "defaulted to zero where no idle step existed",
    "mejor_tramo_al_comer": "same baseline defect: the best stable-rule segment "
                            "inherits whatever the baseline got wrong",
}

FLOOR_TOLERANCE = 0.5


def _conjunction_members() -> dict[str, tuple[str, ...]]:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_screen", PROJECT_ROOT / "scripts" / "screen_concepts.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # The dict is already keyed "sin:nucleo_lecun"; prefixing again produced
    # "sin:sin:..." and every lookup missed, so the gate silently never fired.
    return {name: tuple(spec_["keys"]) for name, spec_ in module.CONJUNCTIONS.items()}


CONJUNCTION_MEMBERS = _conjunction_members()


def verdict_for_effect(effect: dict) -> dict:
    mesh = effect["mesh"]
    if mesh in SUPERSEDED:
        return {"evidence_status": "SUPERSEDED_BY_INSTRUMENT_CALIBRATION",
                "reason": SUPERSEDED[mesh]}
    return {"evidence_status": "CONFIRMED_UNDER_CALIBRATED_INSTRUMENT"
            if mesh not in REGISTRY or state_of(mesh) == "REPORTABLE"
            else "UNREGISTERED_INSTRUMENT",
            "reason": "the reading did not depend on a defect found since"}


def verdict_for_interaction(inter: dict, effects: list[dict]) -> dict:
    mesh = inter["mesh"]
    if mesh in SUPERSEDED:
        return {"interaction_identifiability": "SUPERSEDED_BY_INSTRUMENT_CALIBRATION",
                "reason": SUPERSEDED[mesh]}
    # A component at the floor makes the additive prediction run past the bound
    # -- but only THIS conjunction's own components count. Checking every effect
    # on the mesh flagged all three conjunctions at once, because world model and
    # planner are at the floor of `comidas_efectivas` and appear there whatever
    # the conjunction is. That buried a real sub-additive result in
    # `memoria_completa`, whose two components are nowhere near the floor. A gate
    # that fires everywhere is not a gate.
    members = CONJUNCTION_MEMBERS.get(inter["conjunction"], ())
    saturated = [e["concept"] for e in effects
                 if e["mesh"] == mesh and e.get("evaluable")
                 and e["concept"] in members
                 and abs(e.get("without", 0.0)) <= FLOOR_TOLERANCE
                 and abs(e.get("with", 0.0)) > FLOOR_TOLERANCE]
    if saturated:
        return {"interaction_identifiability": "NON_IDENTIFIABLE_BY_SATURATION",
                "saturated_components": saturated,
                "reason": "a single-concept arm already sits at the floor of this mesh, "
                          "so `observed - predicted_if_additive` measures the bound"}
    residual = inter.get("residual")
    if isinstance(residual, (int, float)) and residual < 0:
        # Sub-additive, and the mechanism is NOT read off the sign. Substitutes
        # would cost little singly and a lot jointly, each covering for the
        # other. Here removing both rescues the damage done by removing one,
        # which is the opposite shape -- antagonism, compensatory
        # reconfiguration, or an interaction between the flags themselves. The
        # label records what was seen and withholds why.
        return {"interaction_identifiability": "NEGATIVE_NONADDITIVE_INTERACTION",
                "mechanism": "UNRESOLVED",
                "reason": "removing both components together costs less than removing "
                          "either alone; the shape is identifiable, the mechanism is not"}
    return {"interaction_identifiability": "IDENTIFIABLE",
            "reason": "no component arm is at the floor of this mesh"}


def main() -> int:
    for relative in REPORTS:
        path = PROJECT_ROOT / relative
        if not path.exists():
            print(f"  skipped (absent): {relative}")
            continue
        report = json.loads(path.read_text(encoding="utf-8"))
        for effect in report.get("effects", []):
            effect.update(verdict_for_effect(effect))
        for inter in report.get("interactions", []):
            inter.update(verdict_for_interaction(inter, report.get("effects", [])))
        report["reclassification"] = {
            "reclassified_at_commit": "action-contract-v2",
            "rule": "The experiment ran correctly under the instrument then available. "
                    "A reading is superseded when the instrument has since been shown "
                    "not to identify the quantity it was read as -- the measurement "
                    "stands, the interpretation is withdrawn.",
            "instrument_states": {m: state_of(m).value for m in sorted(REGISTRY)},
        }
        out = path.with_suffix(".reclassified.json")
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        counts: dict[str, int] = {}
        for effect in report.get("effects", []):
            counts[effect["evidence_status"]] = counts.get(effect["evidence_status"], 0) + 1
        icounts: dict[str, int] = {}
        for inter in report.get("interactions", []):
            key = inter["interaction_identifiability"]
            icounts[key] = icounts.get(key, 0) + 1
        print(f"\n{relative}")
        for key, value in sorted(counts.items()):
            print(f"    effects       {key:<42} {value}")
        for key, value in sorted(icounts.items()):
            print(f"    interactions  {key:<42} {value}")
        print(f"    -> {out.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
