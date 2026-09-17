#!/usr/bin/env python
"""T0 against T1 on the same state, one step, with the world held still.

A closed-loop comparison could not answer this. T changes the trajectory, the
trajectory changes which opportunities exist, consuming removes the objects that
made them, and locomotion follows whichever action the policy collapsed onto.
Three versions of the contract were confounded that way and none raised an
error.

Here the loop cannot close. ONE agent is built, holding both heads, and asked to
decide twice on the SAME state: once addressing a direction, once addressing an
entity. Cognition, memory, world model, planner and operation are not merely
matched -- they are the same objects, evaluated once. The two arms draw their
selector from the same uniform variate, so they differ by representation and by
nothing else, and the world never advances between them.

The states come from a bank no policy produced, so the comparison is not
conditioned on either arm's past behaviour.

What this can and cannot settle
-------------------------------
Representability is already known to be 1.0 under both contracts: every
physically realisable intention is expressible either way, so v1 was not
expressively deficient. What remains is whether the two parameterisations make
that realisation equally easy to FIND. With behavioural parity at
initialisation, a difference at step zero would have to come from the
representation itself rather than from a differently-initialised head.

Engineering sandbox. Not evidence.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import torch
import torch.nn.functional as F

from terrario.agent.agents import create_agent
from terrario.core.action_contract import (
    ActionIntent, AddressingMode, SelectorType, TargetStatus,
    perceive_targets, resolve,
)
from terrario.core.types import ActionType, Direction, Observation
from terrario.lab.measurement_status import Status, ratio
from terrario.lab.selector_isolation import PairedStep, isolation_verdict
from terrario.lab.snapshot_bank import (
    build_bank, exogenous_affordance_rate, intention_representability,
)
from terrario.lab.world_authoring import compile_registry_world
from terrario.lab.world_registry import WorldScenarioRegistry

SCHEMA = "terrario.lab.selector-isolation/v1"
CLASSIFICATION = "ENGINEERING_SANDBOX_NOT_EVIDENCE"


def _observation(state, view_size: int, channels: int) -> Observation:
    """A window centred on the agent, built from the snapshot's own channels."""
    half = view_size // 2
    agent = state.agents[0]
    window = np.zeros((channels, view_size, view_size), dtype=np.float32)
    for obj in state.objects.values():
        dx, dy = obj.pos.x - agent.pos.x, obj.pos.y - agent.pos.y
        if abs(dx) <= half and abs(dy) <= half:
            values = np.asarray(obj.channels, dtype=np.float32)[:channels]
            window[:len(values), dx + half, dy + half] = values
    return Observation(channels=window, mask=np.ones((view_size, view_size), dtype=np.float32),
                       agent_energy=0.5, time_fraction=0.0)


def _choose(probabilities: torch.Tensor, u: float) -> int:
    """Inverse-CDF sampling, so both arms consume the SAME random variate."""
    cumulative = torch.cumsum(probabilities, dim=-1)
    return int(torch.searchsorted(cumulative, torch.tensor(u, dtype=cumulative.dtype)).clamp(
        max=probabilities.numel() - 1).item())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--world", default="D4T")
    ap.add_argument("--seeds", type=int, default=12)
    ap.add_argument("--per-seed", type=int, default=100)
    ap.add_argument("--agent-seed", type=int, default=1000041)
    ap.add_argument("--out", default="artifacts/selector_isolation.json")
    args = ap.parse_args()

    entry = WorldScenarioRegistry(PROJECT_ROOT).get(args.world)
    template = dict(compile_registry_world(args.world, entry.source).runtime_template)
    view_size = 2 * int(template.get("view_radius", 2)) + 1
    channels = int(template.get("num_channels", 4))

    bank = build_bank(template, seeds=list(range(42, 42 + args.seeds)),
                      per_seed=args.per_seed)
    print(f"bank: {len(bank)} exogenous states  "
          f"affordance={exogenous_affordance_rate(bank)}")

    representability = {
        mode.value: intention_representability(bank, mode, view_size=view_size)
        for mode in (AddressingMode.T0_DIRECTIONAL, AddressingMode.T1_ENTITY)
    }
    for mode, result in representability.items():
        print(f"  representability {mode:<16} {result['representability']['value']}  "
              f"over {result['intentions']} realisable intentions")

    # ONE agent, holding both heads, deciding twice on each state.
    torch.manual_seed(args.agent_seed)
    agent = create_agent({"agent_id": "A4", "config": {"addressing_mode": "T1_ENTITY"}},
                         {"num_channels": channels, "view_size": view_size},
                         seed=args.agent_seed)
    rng = np.random.default_rng(args.agent_seed)

    pairs, rows = [], []
    for index, snapshot in enumerate(bank):
        state = snapshot.state
        observation = _observation(state, view_size, channels)
        agent.perceive(observation)
        if agent._last_latent is None:
            continue
        targets, _ = perceive_targets(state, 0, view_size, salt=snapshot.label, step=0)
        agent.offer_targets(targets)

        latent = agent._last_latent
        hidden = torch.zeros(agent.config["hidden_dim"], device=latent.device,
                             dtype=latent.dtype)
        cognition = agent._build_state(latent, hidden)          # evaluated ONCE
        u = float(rng.random())

        direction_probs = F.softmax(agent.direction_head(cognition), dim=-1)
        slot_probs = F.softmax(agent._slot_logits(cognition, 1.0), dim=-1)
        direction = _choose(direction_probs, u)
        slot = _choose(slot_probs, u)

        t0 = resolve(ActionIntent(ActionType.CONSUME, SelectorType.DIRECTION, direction),
                     [], state, 0)
        t1 = resolve(ActionIntent(ActionType.CONSUME, SelectorType.TARGET_ID, slot),
                     targets, state, 0)

        shared = {"observation_hash": observation.obs_hash(),
                  "world_model_state": float(cognition.sum()),
                  "memory_state": len(agent._offered_targets),
                  "planner_state": "not_consulted_identically_for_both",
                  "operation": ActionType.CONSUME.name,
                  "pre_selector_intention": "consume_something"}
        pairs.append(PairedStep(snapshot.label,
                                {**shared, "selector_representation": ("DIRECTION", direction)},
                                {**shared, "selector_representation": ("TARGET_ID", slot)}))
        rows.append({
            "snapshot": snapshot.label, "had_affordance": bool(targets) and any(
                t.adjacent for t in targets),
            "t0_status": t0.status.value, "t1_status": t1.status.value,
            "t0_resolved": t0.status is TargetStatus.VALID,
            "t1_resolved": t1.status is TargetStatus.VALID,
            "t0_entity": t0.entity_id, "t1_entity": t1.entity_id,
        })
        if index % 200 == 0:
            print(f"  ...{index}/{len(bank)}", flush=True)

    isolation = isolation_verdict(pairs)
    with_affordance = [r for r in rows if r["had_affordance"]]
    summary = {
        "decisions": len(rows), "with_affordance": len(with_affordance),
        "t0_resolvability": ratio(sum(r["t0_resolved"] for r in with_affordance),
                                  len(with_affordance), what="T0 resolvability").as_record(),
        "t1_resolvability": ratio(sum(r["t1_resolved"] for r in with_affordance),
                                  len(with_affordance), what="T1 resolvability").as_record(),
        # Paired discordance. Both arms saw the same state and drew the same
        # uniform variate, so the informative quantity is not two marginal rates
        # but the cases where they DISAGREED. McNemar's statistic uses only
        # those, which is exactly what common random numbers were for.
        "discordant_t0_only": sum(1 for r in with_affordance
                                  if r["t0_resolved"] and not r["t1_resolved"]),
        "discordant_t1_only": sum(1 for r in with_affordance
                                  if r["t1_resolved"] and not r["t0_resolved"]),
        "concordant_both": sum(1 for r in with_affordance
                               if r["t0_resolved"] and r["t1_resolved"]),
        "concordant_neither": sum(1 for r in with_affordance
                                  if not r["t0_resolved"] and not r["t1_resolved"]),
        "agreed_on_the_same_entity": sum(
            1 for r in with_affordance
            if r["t0_entity"] is not None and r["t0_entity"] == r["t1_entity"]),
        "t0_status_counts": _counts(rows, "t0_status"),
        "t1_status_counts": _counts(rows, "t1_status"),
    }

    out = {"schema_version": SCHEMA, "classification": CLASSIFICATION,
           "world": args.world, "bank_size": len(bank),
           "exogenous_affordance_rate": exogenous_affordance_rate(bank).as_record(),
           "intention_representability": representability,
           "intervention_isolation": isolation, "summary": summary, "rows": rows[:200]}
    path = PROJECT_ROOT / args.out
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nINTERVENTION_ISOLATION: {isolation['INTERVENTION_ISOLATION']}  "
          f"({isolation['failures']} failures of {isolation['pairs']} pairs)")
    print(f"decisions with an entity in contact: {summary['with_affordance']}")
    print(f"  T0 resolvability {summary['t0_resolvability']['value']}")
    print(f"  T1 resolvability {summary['t1_resolvability']['value']}")
    b, c = summary["discordant_t0_only"], summary["discordant_t1_only"]
    if b + c:
        statistic = (abs(b - c) - 1) ** 2 / (b + c)   # McNemar, continuity-corrected
        summary["mcnemar_chi2"] = round(statistic, 3)
        # chi2 with 1 df: 3.84 at 0.05, 6.63 at 0.01, 10.83 at 0.001
        summary["mcnemar_verdict"] = ("DIFFERENT_p<0.001" if statistic > 10.83 else
                                      "DIFFERENT_p<0.01" if statistic > 6.63 else
                                      "DIFFERENT_p<0.05" if statistic > 3.84 else
                                      "NOT_DISTINGUISHABLE")
        print(f"  discordant: T0 only {b}, T1 only {c}  "
              f"chi2={summary['mcnemar_chi2']}  {summary['mcnemar_verdict']}")
    print(f"  same entity chosen: {summary['agreed_on_the_same_entity']}")
    print(f"\nwrote {path}")
    return 0


def _counts(rows, key):
    counts: dict[str, int] = {}
    for row in rows:
        counts[row[key]] = counts.get(row[key], 0) + 1
    return counts


if __name__ == "__main__":
    raise SystemExit(main())
