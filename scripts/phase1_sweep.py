#!/usr/bin/env python3
"""Phase 1 diagnostic sweep: run every runnable surface and record what breaks.

This is a defect detector, not a scientific run. Nothing it produces is
evidence. It never touches the live `.terrario` root: every step that needs a
data root is handed a fresh one under the sandbox, and any command whose
argv mentions the live root aborts the sweep.
"""
from __future__ import annotations

import argparse, json, os, shutil, subprocess, sys, time
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
if not (PROJECT / "main.py").exists():  # fail closed: a wrong root would aim the guard at the wrong .terrario
    raise SystemExit(f"cannot locate the project root from {__file__}")
LIVE_ROOT = (PROJECT / ".terrario").resolve()
PY = str(PROJECT / ".venv/bin/python")
CORPUS = Path(os.environ.get("TERRARIO_PRIMARY_SOURCE_ROOT", Path.home() / "Documentos/teoria de la inteligencia"))
SNAPSHOT = PROJECT / "theory_snapshots/theory-f59dbb6d6ee3850c"
SCENARIOS = sorted(p.name for p in (PROJECT / "scenarios").glob("*.yaml"))
AGENTS = ["A0_RANDOM", "A1_REACTIVE", "A2_GRU", "A3_WORLD_MODEL", "A4_ADVANCED"]


class LiveRootTouched(RuntimeError):
    pass


def guard(argv: list[str]) -> None:
    for token in argv:
        if str(LIVE_ROOT) in str(token) or token.strip() in {".terrario", "./.terrario"}:
            raise LiveRootTouched(f"step would touch the live root: {token}")


def run(name: str, group: str, argv: list[str], sandbox: Path, timeout: int = 300) -> dict:
    guard(argv)
    started = time.monotonic()
    try:
        proc = subprocess.run(argv, cwd=PROJECT, capture_output=True, text=True, timeout=timeout,
                              env={**os.environ, "TERRARIO_PRIMARY_SOURCE_ROOT": str(CORPUS)})
        code, out, err = proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        code, out, err = -9, (exc.stdout or b"").decode(errors="replace"), f"TIMEOUT after {timeout}s"
    elapsed = time.monotonic() - started
    return {"name": name, "group": group, "argv": argv, "exit": code, "seconds": round(elapsed, 2),
            "ok": code == 0, "stdout_tail": out[-1200:], "stderr_tail": err[-1800:]}


def write_config(path: Path, scenario: str, agents: list[str], steps: int, out_dir: Path) -> Path:
    path.write_text(
        "experiment:\n"
        f"  experiment_id: \"{path.stem}\"\n"
        f"  scenario_path: \"scenarios/{scenario}\"\n"
        f"  agent_types: {json.dumps(agents)}\n"
        "  agent_config: {}\n"
        "  seeds: [42]\n"
        "  num_episodes: 1\n"
        f"  max_steps_per_episode: {steps}\n"
        "  observer_mode: \"scientific_standard\"\n"
        "  checkpoint_every: 0\n"
        f"  output_dir: \"{out_dir}\"\n"
        "  device: \"cpu\"\n")
    return path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sandbox", type=Path, default=PROJECT / ".sandbox/phase1")
    ap.add_argument("--groups", default="cli,demo,tutorial,matrix")
    ap.add_argument("--steps", type=int, default=40)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    sandbox = args.sandbox.resolve()
    if sandbox == LIVE_ROOT or LIVE_ROOT in sandbox.parents:
        print("refusing: sandbox is inside the live root", file=sys.stderr); return 2
    if sandbox.exists():
        shutil.rmtree(sandbox)
    (sandbox / "configs").mkdir(parents=True)
    (sandbox / "runs").mkdir()

    groups = {g.strip() for g in args.groups.split(",") if g.strip()}
    results: list[dict] = []

    if "cli" in groups:
        for scenario in SCENARIOS:
            results.append(run(f"verify:{scenario}", "cli",
                               [PY, "main.py", "verify", "--scenario", f"scenarios/{scenario}", "--steps", "10"],
                               sandbox, timeout=300))
        cfg = write_config(sandbox / "configs/cli_run.yaml", SCENARIOS[0], AGENTS, args.steps, sandbox / "runs")
        results.append(run("run:default-agents-cpu", "cli", [PY, "main.py", "run", "--config", str(cfg)], sandbox, 600))
        results.append(run("run:shipped-default-config", "cli",
                           [PY, "main.py", "run", "--config", "configs/default.yaml", "--output", str(sandbox / "runs")],
                           sandbox, 120))
        results.append(run("ablate:default", "cli",
                           [PY, "main.py", "ablate", "--config", str(cfg), "--output", str(sandbox / "runs")], sandbox, 600))

    tutorial_root = sandbox / "tutorial-root"
    if "tutorial" in groups:
        results.append(run("tutorial:scientific-chain", "tutorial",
                           [PY, "scripts/tutorial_scientific_chain.py", str(tutorial_root)], sandbox, 600))

    if "demo" in groups:
        demo_root = tutorial_root
        for n, extra in [
            ("cl2_hypergraph", ["--snapshot", str(SNAPSHOT), "--primary-source-root", str(CORPUS)]),
            ("cl3_hypothesis", ["--snapshot", str(SNAPSHOT), "--primary-source-root", str(CORPUS)]),
            ("cl4_experiment_draft", ["--snapshot", str(SNAPSHOT), "--primary-source-root", str(CORPUS)]),
            ("cl5_d2_protocol", []),
            ("cl6_d2_visual_fixture", []),
            ("cl7_runtime_readiness", ["--data-root", str(demo_root)]),
        ]:
            script = f"scripts/demonstrate_{n}.py"
            results.append(run(f"demo:{n}", "demo", [PY, script, *extra], sandbox, 300))

    if "tools" in groups:
        # Every writer is redirected into the sandbox.  Two scripts regenerate
        # tracked artifacts in place (build_scientific_review, and the theory
        # snapshot builder when left on its default); they are run separately
        # under git verification, not from here.
        tool_root = sandbox / "tools"
        tool_root.mkdir(exist_ok=True)
        for name, argv in [
            ("build_lab_catalog", ["scripts/build_lab_catalog.py", "--root", ".", "--output", str(tool_root / "lab_catalog.json")]),
            ("build_system_baseline", ["scripts/build_system_baseline.py", "--root", ".", "--output", str(tool_root / "baseline")]),
            ("build_theory_snapshot", ["scripts/build_theory_snapshot.py", "--output", str(tool_root / "snapshots"), "--project-root", "."]),
            ("index_lab_history", ["scripts/index_lab_history.py", "--root", ".", "--data-root", str(tool_root / "history-root")]),
            ("sync_obsidian_vault:check", ["scripts/sync_obsidian_vault.py", "--check"]),
            ("simulate_d4_signal", ["scripts/simulate_d4_signal.py"]),
            ("perf:cross_graph", ["scripts/cross_graph_performance.py"]),
            ("perf:reference_graph", ["scripts/reference_graph_performance.py"]),
            ("perf:worldstream", ["scripts/worldstream_performance.py"]),
            ("h_adapt:preflight-cpu", ["scripts/run_h_adapt_001.py", "--stage", "preflight", "--device", "cpu", "--output", str(tool_root / "h_adapt")]),
        ]:
            results.append(run(f"tool:{name}", "tools", [PY, *argv], sandbox, 600))

    if "matrix" in groups:
        for scenario in SCENARIOS:
            for agent in AGENTS:
                tag = f"{agent}-{scenario.replace('.yaml','')}"
                cfg = write_config(sandbox / f"configs/m_{tag}.yaml", scenario, [agent], args.steps, sandbox / "runs")
                results.append(run(f"matrix:{tag}", "matrix",
                                   [PY, "main.py", "run", "--config", str(cfg)], sandbox, 300))

    out = args.out or (sandbox / "phase1_results.json")
    out.write_text(json.dumps(results, indent=1))
    ok = sum(r["ok"] for r in results)
    print(f"\n{'='*70}\nPHASE 1 SWEEP: {ok}/{len(results)} OK")
    for r in results:
        if not r["ok"]:
            first = next((l for l in reversed(r["stderr_tail"].splitlines()) if l.strip()), "")
            print(f"  FAIL [{r['group']:8}] {r['name']:42} exit={r['exit']:<4} {first[:90]}")
    print(f"results -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
