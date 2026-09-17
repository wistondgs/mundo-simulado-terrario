#!/usr/bin/env python
"""CAPABILITY-ACQUISITION-01 — experience -> internal change -> new capability.

Not more reward. Not more food. Not "the weights moved". A capability the
organism did not have, acquired from its own experience, demonstrated on
entities it never met, with each of the three links breakable on purpose.

    experience  ->  internal change  ->  new capability

PHASE A  Freeze A0. Sit the held-out exam with no updating. This is the real
         starting competence, and every later claim is relative to it.

PHASE B  Duplicate A0 exactly into three twins that receive the SAME experience:

           L  LEARNER          parameter updates ON
           F  FROZEN           parameter updates OFF
           S  SHUFFLED-CREDIT  updates ON, but (x_t, a_t) <-> y_t broken

         The stream is generated once, by L, and replayed into F and S with the
         recorded action forced and its log-probability recomputed under each
         twin's own policy. So Experience_L = Experience_F = Experience_S
         literally, not approximately, and the only difference is the update.

         S is the control that asks whether the mechanism is learning the causal
         relation we think it is. If S improves as much as L, it is not.

PHASE C  Sit the same exam again, learning off, and compute

           G = [Score(L,H) - Score(L0,H)] - [Score(F,H) - Score(F0,H)]

         The double difference matters: the frozen twin's score can move on its
         own, because its recurrent state and its memories advanced through the
         same experience without a single parameter changing. Crediting that
         drift to learning is exactly the error this design exists to avoid.

WHAT COUNTS AS THE CAPABILITY
    Learn which perceptual class yields a favourable consequence, and apply it
    where it was never experienced. Unsolvable from coordinates, identifiers,
    position, seed, direction, order of appearance or a scenario rule: the probe
    entities carry channel values disjoint from every value in training, and the
    only thing shared is the latent relation.

    Memory WRITES are not blocked in F. That is deliberate and it sharpens the
    claim rather than weakening it: G isolates what PARAMETER updates
    contributed, since anything carried by episodic or long-term memory appears
    in both arms and cancels. Where a capability physically lives is
    CAPABILITY-LOCALIZATION-01, not this.

Engineering sandbox. Not evidence.
"""

from __future__ import annotations

import argparse
import copy
import json
import random
import sys
import time
from dataclasses import replace
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import torch
import torch.nn.functional as F_

from terrario.agent.agents import create_agent
from terrario.core.contracts import Transition
from terrario.core.types import NUM_DIRECTIONS, Action, ActionType, Consequence, Direction
from terrario.lab.agent_composition import validate_selection
from terrario.lab.capability_exam import (
    TEST_BANDS, TRAIN_BANDS, build_probes, causal_gain, sit_exam,
)
from terrario.lab.measurement_status import Reading
from terrario.lab.models import thaw
from terrario.lab.sandbox_runtime import (
    ExecutionClassification, SandboxService, derive_sandbox, make_spec,
)
from terrario.lab.world_authoring import compile_registry_world
from terrario.lab.world_registry import WorldScenarioRegistry, configuration_for

SCHEMA = "terrario.lab.capability-acquisition/v1"
CLASSIFICATION = "ENGINEERING_SANDBOX_NOT_EVIDENCE"
EXAMS = ("prediction", "selection", "realisation")


def force_action(agent, action_int: int) -> None:
    """Make a twin's update use the action the stream actually contained.

    Replaying a stream is only faithful if the policy gradient is taken on the
    RECORDED action, evaluated under THIS twin's current policy -- not on
    whatever this twin would have chosen. Letting each twin act for itself would
    give three different experiences and turn the comparison back into two
    trajectories, which is precisely what this design replaces.
    """
    state = getattr(agent, "_last_state", None)
    if state is None:
        return
    agent._last_action = action_int
    if getattr(agent, "_use_factored_action", False):
        operation = action_int // NUM_DIRECTIONS
        selector = action_int % NUM_DIRECTIONS
        op_logits = agent.operation_head(state)
        op_log = torch.log(F_.softmax(op_logits, dim=-1)[operation] + 1e-8)
        head = getattr(agent, "direction_head", None) or agent.selector_head
        sel_logits = head(state)
        index = min(selector, sel_logits.numel() - 1)
        sel_log = torch.log(F_.softmax(sel_logits, dim=-1)[index] + 1e-8)
        agent._last_log_prob = op_log + sel_log
    else:
        logits = agent.policy_head(state)
        agent._last_log_prob = torch.log(F_.softmax(logits, dim=-1)[action_int] + 1e-8)


def replay(agent, stream, *, shuffle_credit: bool = False, seed: int = 7) -> None:
    """Feed one twin the recorded stream, step for step."""
    energies = [record["energy_delta"] for record in stream]
    if shuffle_credit:
        # Same experience, same marginal distribution of consequences, and the
        # correspondence between (state, action) and outcome destroyed.
        rng = random.Random(seed)
        rng.shuffle(energies)
    for record, energy in zip(stream, energies):
        agent.perceive(record["observation"])
        agent.decide()                      # advances internal state as it did
        force_action(agent, record["action_int"])
        agent.learn(Transition(
            observation_t=record["observation"],
            internal_state_ref=None,
            action_t=Action.from_int(record["action_int"]),
            consequence_t1=Consequence(energy_delta=energy, events=list(record["events"]),
                                       new_observation=record["next_observation"],
                                       done=record["done"]),
            observation_t1=record["next_observation"],
            terminated=record["done"], truncated=False,
            step=record["step"], seed=record["seed"],
        ))


class Bench:
    def __init__(self, root: Path):
        self.registry = WorldScenarioRegistry(root)
        self.service = SandboxService(root / ".sandbox-capability")

    def experience(self, world: str, steps: int, seed: int, config, agent):
        """Run the learner and RECORD everything a twin would need to relive it."""
        entry = self.registry.get(world)
        compiled = compile_registry_world(world, entry.source)
        base = replace(derive_sandbox(configuration_for(entry)), agent_reference="A4")
        spec = make_spec(base, compiled, 42, seed, steps + 1,
                         ExecutionClassification.ENGINEERING_SANDBOX,
                         validate_selection(config))
        torch.manual_seed(seed)
        run = self.service.create(spec, base, compiled)
        self.service.run_bounded(run.run_id, steps)
        return [thaw(step) for step in run.timeline], compiled


def stream_from(trace, view_size: int, channels: int):
    """Reconstruct the transition stream from the sealed trace."""
    import numpy as np
    from terrario.core.types import Observation
    records = []
    for index in range(len(trace) - 1):
        step, nxt = trace[index], trace[index + 1]
        obs = step.get("agent_observation") or {}
        nxt_obs = nxt.get("agent_observation") or {}
        if "channels" not in obs or "channels" not in nxt_obs:
            continue
        action = step.get("agent_action") or nxt.get("agent_action") or {}
        if "action_type" not in action:
            continue
        action_int = (int(ActionType[action["action_type"]]) * NUM_DIRECTIONS
                      + int(Direction[action.get("direction", "NONE")]))
        before = _energy(step)
        after = _energy(nxt)
        records.append({
            "observation": Observation(
                channels=np.asarray(obs["channels"], dtype=np.float32),
                mask=np.asarray(obs["mask"], dtype=np.float32),
                agent_energy=float(obs.get("agent_energy", 0.5)),
                time_fraction=float(obs.get("time_fraction", 0.0))),
            "next_observation": Observation(
                channels=np.asarray(nxt_obs["channels"], dtype=np.float32),
                mask=np.asarray(nxt_obs["mask"], dtype=np.float32),
                agent_energy=float(nxt_obs.get("agent_energy", 0.5)),
                time_fraction=float(nxt_obs.get("time_fraction", 0.0))),
            "action_int": action_int,
            "energy_delta": (after - before) if before is not None and after is not None else 0.0,
            "events": tuple(step.get("agent_events") or ()),
            "done": bool(nxt.get("terminated")), "step": index, "seed": 0,
        })
    return records


def _energy(step):
    world = step.get("observer_world") or {}
    agents = world.get("agents") or {}
    entries = list(agents.values()) if isinstance(agents, dict) else list(agents)
    if entries and isinstance(entries[0].get("energy"), (int, float)):
        return float(entries[0]["energy"])
    return None


def _fresh(seed: int, config: dict):
    """One A0, built the same way every time."""
    torch.manual_seed(seed)
    return create_agent({"agent_id": "A4", "config": config},
                        {"num_channels": 4, "view_size": 5}, seed=seed)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--world", default="D4T")
    ap.add_argument("--steps", type=int, default=1200)
    ap.add_argument("--seeds", type=int, default=8)
    ap.add_argument("--probes", type=int, default=400)
    ap.add_argument("--addressing", default="T0_DIRECTIONAL")
    ap.add_argument("--out", default="artifacts/capability_acquisition.json")
    args = ap.parse_args()

    bench = Bench(PROJECT_ROOT)
    held_out = build_probes(args.probes, bands=TEST_BANDS, seed=20260917)
    decorrelated = build_probes(args.probes, bands=TEST_BANDS, seed=20260918,
                                decorrelate_distractors=True)
    seen_values = build_probes(args.probes, bands=TRAIN_BANDS, seed=20260919)

    rows = []
    for offset in range(args.seeds):
        seed = 1000041 + offset
        started = time.time()
        config = {"addressing_mode": args.addressing}
        # Twins are BUILT identically rather than copied. An A4 holds tensors that
        # are graph nodes, which deepcopy refuses -- and building afresh under the
        # same global seed is the stronger option anyway, because the identity is
        # then verified rather than assumed.
        a0 = _fresh(seed, config)
        before = {name: sit_exam(a0, bank)
                  for name, bank in (("held_out", held_out),
                                     ("decorrelated", decorrelated),
                                     ("seen_values", seen_values))}

        learner, frozen, shuffled = (_fresh(seed, config) for _ in range(3))
        frozen._use_online_learning = False
        hashes = {a.agent_identity["initial_parameters_hash"]
                  for a in (a0, learner, frozen, shuffled)}
        if len(hashes) != 1:
            raise RuntimeError(
                f"the three twins are not the same organism: {len(hashes)} distinct "
                f"initial parameter hashes. Every comparison below assumes one A0.")

        trace, _ = bench.experience(args.world, args.steps, seed, config, learner)
        stream = stream_from(trace, 5, 4)
        # The learner that produced the stream is the one in the sandbox; the
        # local twin relives it identically so all three twins are treated alike.
        replay(learner, stream)
        replay(frozen, stream)
        replay(shuffled, stream, shuffle_credit=True, seed=seed)

        after = {}
        for arm, twin in (("L", learner), ("F", frozen), ("S", shuffled)):
            after[arm] = {name: sit_exam(twin, bank)
                          for name, bank in (("held_out", held_out),
                                             ("decorrelated", decorrelated),
                                             ("seen_values", seen_values))}

        gains = {}
        for bank in ("held_out", "decorrelated", "seen_values"):
            gains[bank] = {exam: causal_gain(after["L"][bank], before[bank],
                                             after["F"][bank], before[bank], exam)
                           for exam in EXAMS}
            gains[bank]["shuffled_control"] = {
                exam: causal_gain(after["S"][bank], before[bank],
                                  after["F"][bank], before[bank], exam)
                for exam in EXAMS}

        rows.append({"seed": seed, "stream_length": len(stream),
                     "before": {b: {e: before[b][e].as_record() for e in EXAMS}
                                for b in before},
                     "after": {a: {b: {e: after[a][b][e].as_record() for e in EXAMS}
                                   for b in after[a]} for a in after},
                     "gains": gains, "seconds": round(time.time() - started, 1)})
        g = gains["held_out"]
        print(f"  seed {seed}  stream={len(stream)}  "
              f"G_pred={g['prediction'].get('G')}  "
              f"G_sel={g['selection'].get('G')}  "
              f"G_real={g['realisation'].get('G')}  "
              f"{rows[-1]['seconds']}s", flush=True)

    summary = {}
    for bank in ("held_out", "decorrelated", "seen_values"):
        summary[bank] = {}
        for exam in EXAMS:
            values = [r["gains"][bank][exam]["G"] for r in rows
                      if r["gains"][bank][exam].get("status") == "OK"]
            shuffled_values = [r["gains"][bank]["shuffled_control"][exam]["G"] for r in rows
                               if r["gains"][bank]["shuffled_control"][exam].get("status") == "OK"]
            summary[bank][exam] = {
                "n": len(values),
                "mean_G": round(sum(values) / len(values), 6) if values else None,
                "positive_seeds": sum(1 for v in values if v > 0),
                "negative_seeds": sum(1 for v in values if v < 0),
                "shuffled_mean_G": round(sum(shuffled_values) / len(shuffled_values), 6)
                if shuffled_values else None,
            }

    out = {"schema_version": SCHEMA, "classification": CLASSIFICATION,
           "world": args.world, "steps": args.steps, "probes": args.probes,
           "addressing_mode": args.addressing,
           "train_bands": TRAIN_BANDS, "test_bands": TEST_BANDS,
           "chance_level": 0.5, "summary": summary, "runs": rows}
    path = PROJECT_ROOT / args.out
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    for bank, exams in summary.items():
        print(f"\n{bank}")
        for exam, result in exams.items():
            print(f"  {exam:<14} n={result['n']:>2}  G={result['mean_G']}  "
                  f"+{result['positive_seeds']}/-{result['negative_seeds']}  "
                  f"shuffled_G={result['shuffled_mean_G']}")
    print(f"\nwrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
