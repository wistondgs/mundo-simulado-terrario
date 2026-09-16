"""Calibration phase for the viability-recovery instrument: fix eta and dwell_k.

Ashby gives the CONCEPT -- essential variables inside the viable set -- but not
the number.  Choosing eta by looking at the result you want is the failure this
phase exists to prevent, so the calibration seeds are DECLARED here and are
disjoint from the confirmatory set reserved below.  Nothing produced here is
evidence: the chain is signed by a script, and the report says so.

What it answers: across a grid of eta, which boundaries DISCRIMINATE between
architectures and which SATURATE (every arm survives, or none does).  A
saturated boundary measures nothing.

Usage:
    scripts/calibrate_viability_eta.py <sandbox root ABSOLUTE> [--steps N]
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.lab.persistence import ArtifactRepository
from terrario.lab.persistence.canonical import content_hash
from terrario.lab.viability_recovery_metric import evaluate_scientific_trace

#: Declared here so the choice cannot be made after seeing the confirmatory run.
CALIBRATION_SEEDS = (9001, 9002, 9003)
CONFIRMATORY_SEEDS_RESERVED = (8001, 8002, 8003, 8004)
assert not set(CALIBRATION_SEEDS) & set(CONFIRMATORY_SEEDS_RESERVED)

AGENTS = ("A1", "A2", "A3")
SCENARIO = "D4S"
# La primera rejilla iba de 0.20 a 0.80 en pasos de 0.10 y devolvió 0 celdas
# discriminantes y 21 saturadas. El defecto era la rejilla, no el detector: con
# E_inicial = 60 y decaimiento fijo, las energías finales observadas caen entre
# 21 y 26, así que η = 0.20 deja el umbral (12.0) por debajo de todo y η = 0.30
# lo deja (18.0) por encima de nada. Toda la señal vive en una ventana de 0.05
# de ancho que el paso de 0.10 saltaba entera.
#
# Al re-barrer sobre las mismas trazas a resolución fina: la ventana útil es
# η ∈ [0.21, 0.255], con máximo en 0.230-0.235 (spread 1.00: A1 3/3, A2 0/3,
# A3 2/3). Fuera de [0.205, 0.260] el instrumento está ciego por saturación.
#
# Se conservan dos puntos gruesos en los extremos a propósito: son el control
# que deja ver la saturación en el informe en vez de esconderla.
ETA_GRID = (
    0.150,
    0.205, 0.210, 0.215, 0.220, 0.225, 0.230, 0.235, 0.240, 0.245, 0.250, 0.255, 0.260,
    0.400,
)
DWELL_GRID = (3, 10, 25)
VARIETY_BIN = 1.0


def run_chain(root: Path, agent: str, seed: int, steps: int) -> Path:
    target = root / f"{agent}-{seed}"
    proc = subprocess.run(
        [str(PROJECT_ROOT / ".venv/bin/python"), "scripts/tutorial_scientific_chain.py",
         str(target), SCENARIO, agent, str(steps), str(seed)],
        cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=1800)
    if proc.returncode != 0:
        raise SystemExit(f"chain failed for {agent}/{seed}:\n{proc.stdout[-800:]}\n{proc.stderr[-400:]}")
    return target


def load_trace(root: Path):
    con = sqlite3.connect(f"file:{root / 'terrario.db'}?mode=ro", uri=True)
    try:
        row = con.execute("SELECT blob_hash FROM scientific_execution_artifacts "
                          "WHERE artifact_type='SCIENTIFIC_TRACE' LIMIT 1").fetchone()
    finally:
        con.close()
    if not row:
        raise SystemExit(f"no sealed trace in {root}")
    return json.loads(ArtifactRepository(root).blobs.read(row[0]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sandbox", type=Path)
    ap.add_argument("--steps", type=int, default=600)
    args = ap.parse_args()
    sandbox = args.sandbox.resolve()
    if sandbox == (PROJECT_ROOT / ".terrario").resolve():
        raise SystemExit("refusing to calibrate against the live scientific data root")
    sandbox.mkdir(parents=True, exist_ok=True)

    traces = {}
    for agent in AGENTS:
        for seed in CALIBRATION_SEEDS:
            print(f"  corriendo {agent} semilla {seed}…", flush=True)
            traces[(agent, seed)] = load_trace(run_chain(sandbox, agent, seed, args.steps))

    cells = []
    for eta in ETA_GRID:
        for dwell in DWELL_GRID:
            per_agent = {}
            for agent in AGENTS:
                survived = relapsed = censored = 0
                for seed in CALIBRATION_SEEDS:
                    r = evaluate_scientific_trace(traces[(agent, seed)], viable_floor=eta,
                                                  dwell_k=dwell, variety_bin=VARIETY_BIN)
                    survived += bool(r.viable_at_end)
                    relapsed += bool(r.relapse)
                    censored += bool(r.censored)
                per_agent[agent] = {"survived": survived, "relapsed": relapsed,
                                    "censored": censored, "n": len(CALIBRATION_SEEDS)}
            rates = {a: per_agent[a]["survived"] / per_agent[a]["n"] for a in AGENTS}
            spread = max(rates.values()) - min(rates.values())
            # A boundary where every arm survives, or none does, cannot separate them.
            saturated = spread == 0.0
            cells.append({"eta": eta, "dwell_k": dwell, "per_agent": per_agent,
                          "survival_rates": rates, "spread": spread, "saturated": saturated})

    discriminating = sorted((c for c in cells if not c["saturated"]),
                            key=lambda c: (-c["spread"], c["eta"]))
    report = {
        "schema_version": "terrario.lab.viability-calibration/v1",
        "scope": "CALIBRATION_NOT_EVIDENCE",
        "scenario": SCENARIO, "agents": list(AGENTS), "steps": args.steps,
        "calibration_seeds": list(CALIBRATION_SEEDS),
        "confirmatory_seeds_reserved": list(CONFIRMATORY_SEEDS_RESERVED),
        "seed_sets_disjoint": True,
        "eta_grid": list(ETA_GRID), "dwell_grid": list(DWELL_GRID),
        "cells": cells,
        "discriminating_count": len(discriminating),
        "saturated_count": sum(1 for c in cells if c["saturated"]),
        "note": ("Gates signed by a script; no EvidenceGraph written. The human chooses "
                 "eta and dwell_k against this report; this file recommends nothing."),
    }
    out = sandbox / "viability_calibration_report.json"
    out.write_text(json.dumps(report | {"report_hash": content_hash(report)}, indent=1))

    print(f"\n{'eta':>6} {'dwell':>6}  " + "  ".join(f"{a:>10}" for a in AGENTS) + "   spread")
    for c in cells:
        marks = "  ".join(f"{c['per_agent'][a]['survived']}/{c['per_agent'][a]['n']:<8}" for a in AGENTS)
        flag = "  SATURADA" if c["saturated"] else ""
        print(f"{c['eta']:6.2f} {c['dwell_k']:6d}  {marks}   {c['spread']:.2f}{flag}")
    print(f"\ndiscriminan: {report['discriminating_count']} · saturadas: {report['saturated_count']}")
    print(f"informe -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
