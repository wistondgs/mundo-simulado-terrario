#!/usr/bin/env python
"""Screening: what does each concept contribute, measured several ways.

Mixing three concepts and watching something happen does not say which of the
three did it.  Measuring each one alone first does: the contribution of a
concept is the difference between the organism that has it and the same
organism without it, everything else held fixed.

    full organism                     the reference
    full organism minus one concept   one condition per concept
    difference, per mesh              that concept's contribution HERE

"Here" carries weight.  A concept's contribution is not a property of the
concept: it depends on the world and on what else is present.  The planner is
worth one thing in D0 and another in D4T.  That is the finding, not the noise.

Nothing here is evidence.  Every run is ENGINEERING_SANDBOX, the firewall
refuses to publish it, and the report says so in its own body.  What it is for
is deciding which of the 2^8 mixes deserve a preregistered experiment.

RESUMABLE BY DESIGN.  A campaign runs for hours and the power does go out, so
every finished run is appended to a JSONL as it completes and a restart skips
what is already there.  Interrupting this costs the run in flight and nothing
else.

    scripts/screen_concepts.py --world D4T --steps 120 --seeds 3
    scripts/screen_concepts.py --world D4T --steps 120 --seeds 3   # continues
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dataclasses import replace

import torch

from terrario.lab.agent_composition import (
    architecture_of, concepts_for, default_of, validate_selection,
)
from terrario.lab.models import thaw
from terrario.lab.run_measures import measure_run
from terrario.lab.sandbox_runtime import (
    ExecutionClassification, SandboxService, derive_sandbox, make_spec,
)
from terrario.lab.world_authoring import compile_registry_world
from terrario.lab.world_registry import WorldScenarioRegistry, configuration_for

SCHEMA = "terrario.lab.concept-screening/v1"
CLASSIFICATION = "ENGINEERING_SANDBOX_NOT_EVIDENCE"

#: The organism this campaign screens. Named once, because "what does this
#: concept ship as" and "which concepts exist at all" are questions about an
#: agent, and screening A4 against a concept only A5 reads would be an arm
#: identical to the reference dressed as an ablation.
AGENT = "A4"
ARCHITECTURE = architecture_of(AGENT)


#: Conjunctions the CORPUS declares, not combinations we picked.  2^9 = 512
#: mixes per world is both unaffordable and unprincipled; choosing at random is
#: no better.  HYPERCAND-08 (LeCun) states a joint architecture and the corpus
#: records its own discriminating test as "component ablation with
#: out-of-distribution control", with necessity explicitly NOT established.
#: That turns "thousands of combinations" into a question with an author.
CONJUNCTIONS = {
    "sin:nucleo_lecun": {
        "keys": ("use_world_model", "use_longterm_memory", "use_planner"),
        "source": "HYPERCAND-08 · LeCun · roles: world model, memory, configurator",
        "claim": "AUTHOR_ARCHITECTURE; joint architecture explicit, necessity not proven",
    },
    "sin:memoria_completa": {
        "keys": ("use_episodic_memory", "use_longterm_memory"),
        "source": "CON-0014/CON-0029 · James, Darwin · memory as a resource",
        "claim": "two memory roles the corpus keeps separate; do they act as one?",
    },
    "sin:anticipacion": {
        "keys": ("use_world_model", "use_planner"),
        "source": "HYPERCAND-08 · predecir el futuro y proponer secuencias",
        "claim": "prediction without planning, and planning without prediction",
    },
}


def conjunction_conditions(names=()):
    """Named multi-concept arms, each traceable to a claim in the corpus."""
    for name in names:
        spec = CONJUNCTIONS[name]
        yield name, {key: False for key in spec["keys"]}


def interactions(rows, meshes_effects):
    """Is the conjunction more than the sum of its parts?

    The residual is what the screening exists for.  If behaviour were a
    weighted sum of concepts no combination would ever produce anything new,
    and the whole programme would have no object.  So the sum is the NULL
    model, and `observed - predicted` is where a conjunction earns its name.
    """
    by_key = {(e["concept"], e["mesh"]): e for e in meshes_effects if e.get("evaluable")}
    out = []
    for name, spec in CONJUNCTIONS.items():
        for mesh in sorted({m for _, m in by_key}):
            partes = [by_key.get((k, mesh)) for k in spec["keys"]]
            conjunto = [r["measures"].get(mesh) for r in rows if r["condition"] == name]
            referencia = [r["measures"].get(mesh) for r in rows if r["condition"] == "completo"]
            conjunto = [v for v in conjunto if isinstance(v, (int, float))]
            referencia = [v for v in referencia if isinstance(v, (int, float))]
            if any(p is None for p in partes) or not conjunto or not referencia:
                continue
            observado = sum(referencia) / len(referencia) - sum(conjunto) / len(conjunto)
            predicho = sum(p["effect"] for p in partes)
            dispersion = max(p["within_arm_spread"] for p in partes)

            # FLOOR / CEILING IDENTIFIABILITY GATE.
            #
            # The additive null model is a statement about an unbounded response.
            # Meals are bounded below by zero, and both of these concepts already
            # drive the arm to the floor on their own, so the additive prediction
            # was 13.33 against an observed 6.33 -- a residual of -7 that reads as
            # a large negative interaction and is nothing of the sort. The model
            # was asked to predict minus seven meals. No cognitive or biological
            # quantity is being estimated there; the geometry of the dependent
            # variable is.
            #
            # The honest answer is neither zero nor negative. It is that the
            # question is not identifiable from this design, and saying so keeps
            # the finding available for a later analysis on a scale that respects
            # the bound -- a count model, given enough mass -- instead of burying
            # it under a number.
            piso = [p for p in partes if _at_floor(p, rows, mesh)]
            entrada = {
                "conjunction": name, "mesh": mesh, "source": spec["source"],
                "observed": round(observado, 4), "predicted_if_additive": round(predicho, 4),
            }
            if piso:
                entrada.update({
                    "interaction_identifiability": "FAILED_FLOOR",
                    "residual": None,
                    "larger_than_seed_spread": None,
                    "saturated_components": [p["concept"] for p in piso],
                    "reason": ("one or more single-concept arms already sit at the floor of "
                               "this mesh, so the additive prediction runs past the bound and "
                               "the residual measures the scale rather than the conjunction"),
                })
            else:
                entrada.update({
                    "interaction_identifiability": "IDENTIFIABLE",
                    "residual": round(observado - predicho, 4),
                    "larger_than_seed_spread": abs(observado - predicho) > dispersion,
                })
            out.append(entrada)
    return out


#: A mesh reading is at the floor when the arm that removed the concept produced
#: essentially nothing left to lose. Half a unit rather than exactly zero,
#: because an arm that scored 0.33 meals out of a reference of 6.7 is saturated
#: for every purpose the additive model has.
FLOOR_TOLERANCE = 0.5


def _at_floor(part, rows, mesh):
    valores = [r["measures"].get(mesh) for r in rows if r["condition"] == part.get("arm")]
    valores = [v for v in valores if isinstance(v, (int, float))]
    if not valores:
        return False
    return abs(sum(valores) / len(valores)) <= FLOOR_TOLERANCE


def conditions(keys):
    """The reference plus one changed concept each: k+1 conditions, not 2^k.

    A condition is always "differs from the default organism in exactly one
    concept". For a concept that ships ON that means switching it off; for one
    that ships OFF -- entropy regularisation, say -- it means switching it on.
    Ablating something already absent would be a condition identical to the
    reference, which measures nothing and quietly wastes a third of a campaign.

    What a concept ships as is asked of THIS campaign's agent, because it is not
    the same answer for every organism: A5 ships curiosity on and A4 has no such
    key at all.
    """
    conceptos = {c.key: c for c in concepts_for(AGENT)}
    yield "completo", {}
    for key in keys:
        encendido = default_of(conceptos[key], ARCHITECTURE)
        prefijo = "sin" if encendido else "con"
        yield f"{prefijo}:{key}", {key: not encendido}


def already_done(path):
    if not path.exists():
        return {}
    done = {}
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue  # a line torn in half by the cut; the run is simply redone
        done[(row["condition"], row["seed"])] = row
    return done


class Bench:
    """The runtime, without the live-streaming layer a campaign does not use.

    Going through the HTTP surface meant every step also wrote a JSONL record,
    an SQLite index row and a captured frame for subscribers that do not exist
    here.  That is the screen's machinery, not the measurement's: it cost time
    per step and it carries an intermittent race in the trace index that killed
    the second trial of a campaign with a UNIQUE violation on a sequence the
    archive had never issued.

    A screening campaign wants the organism, the world and the trace.  This is
    the same runtime the screen drives, entered one layer lower.
    """

    def __init__(self, root: Path):
        self.root = root
        self.registry = WorldScenarioRegistry(root)
        self.service = SandboxService(root / ".sandbox-screening")
        self._compiled: dict[str, object] = {}

    def compiled(self, world: str):
        if world not in self._compiled:
            entry = self.registry.get(world)
            self._compiled[world] = (compile_registry_world(world, entry.source), entry)
        return self._compiled[world]

    def run(self, world, steps, seed, mix):
        compiled, entry = self.compiled(world)
        config = replace(derive_sandbox(configuration_for(entry)), agent_reference=AGENT)
        spec = make_spec(config, compiled, 42, seed, steps + 1,
                         ExecutionClassification.ENGINEERING_SANDBOX,
                         validate_selection(mix, AGENT))
        # The agent seed does NOT determine the agent.  create_agent seeds a
        # torch.Generator that is used only for SAMPLING; module weights come
        # from nn.Module constructors reading the GLOBAL torch RNG, which
        # advances with every construction.  Three agents built from seed
        # 1000045 in one process produced three different initial parameter
        # hashes, so a condition's result depended on its position in the loop
        # and an "ablation effect" was entangled with a different organism.
        #
        # Seeded here rather than in the factory: fixing create_agent would
        # change the initial weights of every agent for a given seed, which
        # moves the golden behavioural characterisation and the protected hash
        # manifest -- both human gates.  The defect is reported, not patched
        # around in the science path.
        torch.manual_seed(seed)
        run = self.service.create(spec, config, compiled)
        self.service.run_bounded(run.run_id, steps)
        return measure_run([thaw(step) for step in run.timeline])


def run_one(bench, world, steps, seed, mix):
    return bench.run(world, steps, seed, mix)


def effects(rows, keys, names=None):
    """Contribution per concept per mesh: reference minus the changed arm."""
    names = names or {key: f"sin:{key}" for key in keys}

    def sample(condition, mesh):
        return [r["measures"][mesh] for r in rows
                if r["condition"] == condition and isinstance(r["measures"].get(mesh), (int, float))]

    meshes = sorted({m for r in rows for m in r["measures"]})
    out = []
    for key in keys:
        for mesh in meshes:
            con, sin = sample("completo", mesh), sample(names[key], mesh)
            if not con or not sin:
                out.append({"concept": key, "mesh": mesh, "evaluable": False,
                            "reason": "NOT_EVALUABLE_IN_ONE_ARM"})
                continue
            mean_con, mean_sin = sum(con) / len(con), sum(sin) / len(sin)
            spread = max(max(con) - min(con), max(sin) - min(sin))
            out.append({
                "concept": key, "arm": names[key], "mesh": mesh, "evaluable": True,
                "with": round(mean_con, 4), "without": round(mean_sin, 4),
                "effect": round(mean_con - mean_sin, 4),
                "within_arm_spread": round(spread, 4),
                # The honest guard against reading noise as a finding: an effect
                # smaller than the spread among seeds of a single arm is not a
                # result, it is the seed.
                "larger_than_seed_spread": abs(mean_con - mean_sin) > spread,
            })
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--world", default="D4T")
    parser.add_argument("--steps", type=int, default=120)
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument("--out", default="runs/screening")
    parser.add_argument("--conjunctions", default=None,
                        help="coma-separado o 'todas': brazos de conjuncion declarados por el "
                             "corpus, para medir el residuo frente a la suma de las partes")
    parser.add_argument("--only", default=None,
                        help="coma-separado: tamiza sólo estos conceptos, para una pasada corta "
                             "de validación antes de comprometer la campaña entera")
    args = parser.parse_args()

    keys = [c.key for c in concepts_for(AGENT)]
    conjunciones = ()
    if args.conjunctions:
        conjunciones = tuple(CONJUNCTIONS) if args.conjunctions == "todas" else tuple(
            x.strip() for x in args.conjunctions.split(",") if x.strip())
        desconocidas = sorted(set(conjunciones) - set(CONJUNCTIONS))
        if desconocidas:
            parser.error(f"conjunciones desconocidas: {desconocidas}")
    if args.only:
        pedidos = [x.strip() for x in args.only.split(",") if x.strip()]
        desconocidos = sorted(set(pedidos) - set(keys))
        if desconocidos:
            parser.error(f"conceptos desconocidos: {desconocidos}")
        keys = [k for k in keys if k in pedidos]
    seeds = [1000045 + i for i in range(args.seeds)]
    out_dir = PROJECT_ROOT / args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    tag = f"{args.world}-{args.steps}steps-{args.seeds}seeds" + (f"-{len(keys)}concepts" if args.only else "")
    ledger = out_dir / f"{tag}.jsonl"

    done = already_done(ledger)
    arms = list(conditions(keys)) + list(conjunction_conditions(conjunciones))
    plan = [(name, mix, seed) for name, mix in arms for seed in seeds]
    pending = [item for item in plan if (item[0], item[2]) not in done]
    print(f"{SCHEMA}  {CLASSIFICATION}")
    print(f"mundo {args.world} · {args.steps} pasos · {len(plan)} corridas · "
          f"{len(done)} ya hechas · {len(pending)} por hacer", flush=True)

    with tempfile.TemporaryDirectory() as tmp:
        bench = Bench(PROJECT_ROOT)
        bench.service.storage.root = Path(tmp) / "sandbox"
        for index, (name, mix, seed) in enumerate(pending, 1):
            started = time.time()
            measured = run_one(bench, args.world, args.steps, seed, mix)
            row = {"condition": name, "seed": seed, "world": args.world, "steps": args.steps,
                   "seconds": round(time.time() - started, 1),
                   "measures": {m["key"]: (m["value"] if m["evaluable"] else None)
                                for m in measured["measures"]}}
            # Appended and flushed per run: a cut costs this one, never the rest.
            with ledger.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                handle.flush()
            print(f"  [{index}/{len(pending)}] {name:28} semilla {seed} "
                  f"{row['seconds']:>6.1f}s", flush=True)

    nombres = {key: name for name, mix in conditions(keys) for key in mix}
    rows = list(already_done(ledger).values())
    efectos = effects(rows, keys, nombres)
    report = {"schema_version": SCHEMA, "classification": CLASSIFICATION,
              "world": args.world, "steps": args.steps, "seeds": seeds,
              "runs": len(rows), "effects": efectos,
              "interactions": interactions(rows, efectos) if conjunciones else [],
              "reading_rule": ("Un efecto menor que la dispersión entre semillas de un mismo "
                               "brazo no es un hallazgo: es la semilla. Mirá "
                               "larger_than_seed_spread antes que effect.")}
    report_path = out_dir / f"{tag}.report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\ninforme: {report_path}")
    for row in report["effects"]:
        if row.get("larger_than_seed_spread"):
            print(f"  {row['concept']:22} {row['mesh']:24} efecto {row['effect']:+.3f}")


if __name__ == "__main__":
    main()
