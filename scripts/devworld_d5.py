#!/usr/bin/env python
"""D5 · Los seis contratos, contra el motor real y la observación completa.

    python scripts/devworld_d5.py --estaciones 512 --semillas 6
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np                                        # noqa: E402
from terrario.devworld import exposure, instances, oracles  # noqa: E402
from terrario.devworld.kernel import MEMORY                # noqa: E402


def entropy(labels) -> float:
    if not len(labels):
        return 0.0
    _, c = np.unique(np.asarray([str(v) for v in labels]), return_counts=True)
    p = c / c.sum()
    return float(-(p * np.log2(p)).sum())


def decoder_accuracy(records, *, seed: int = 0) -> tuple[float, float]:
    """Vecino más próximo sobre la observación COMPLETA, con reserva.

    Más fuerte que la información mutua aquí: con 100 canales cada
    observación es única y condicionar sobre ella da entropía cero por
    memorización, no por fuga. Un decodificador con partición reservada sólo
    acierta si la fuga GENERALIZA, que es lo que importa.

    Devuelve (acierto reservado, tasa base de la clase mayoritaria).
    """
    X = np.array([r.observation for r in records], dtype=float)
    y = np.array([r.correct for r in records])
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(y))
    cut = int(0.7 * len(y))
    tr, te = idx[:cut], idx[cut:]
    if len(te) == 0 or len(np.unique(y[tr])) < 2:
        return float("nan"), float("nan")
    d = ((X[te][:, None, :] - X[tr][None, :, :]) ** 2).sum(-1)
    pred = y[tr][d.argmin(1)]
    base = max((y[te] == c).mean() for c in np.unique(y))
    return float((pred == y[te]).mean()), float(base)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--estaciones", type=int, default=512)
    ap.add_argument("--semillas", type=int, default=6)
    a = ap.parse_args()

    eco = oracles.instrument_economy(a.estaciones)
    rows: dict[tuple[str, bool], list[float]] = {}
    leak: dict[str, list[tuple[float, float, float]]] = {"exigente": [], "control": []}
    hstar: dict[str, list[float]] = {"exigente": [], "control": []}
    ndec: dict[tuple[str, bool], list[int]] = {}

    for s in range(a.semillas):
        w, c = instances.twin(MEMORY, seed=s, stations=a.estaciones, economy=eco)
        for label, world in (("exigente", w), ("control", c)):
            for mem in (True, False):
                o = oracles.run(world, memory=mem, seed=s)
                rows.setdefault((label, mem), []).append(oracles.accuracy(o))
                ndec.setdefault((label, mem), []).append(len(o.records))
                if mem:
                    dec, base = decoder_accuracy(o.records, seed=s)
                    leak[label].append((dec, base, entropy([r.correct for r in o.records])))
                    hstar[label].append(entropy([r.correct for r in o.records]))

    m = lambda xs: float(np.mean(xs))
    print(f"D5 · MEM-DEV · {a.semillas} semillas × {a.estaciones} estaciones · "
          f"motor real, física estricta\n")
    print(f"  {'':34}{'acierto':>10}{'decisiones':>13}")
    todos = a.estaciones
    c1 = m(rows[("exigente", True)]);   print(f"  1 exigente, memoria PRESENTE {'':5}{c1:>10.4f}"
                                              f"{m(ndec[('exigente',True)]):>13.1f}/{todos}")
    c2 = m(rows[("exigente", False)]);  print(f"  2 exigente, memoria AMPUTADA {'':5}{c2:>10.4f}"
                                              f"{m(ndec[('exigente',False)]):>13.1f}/{todos}")
    c3 = m(rows[("control", False)]);   print(f"  3 control,  memoria AMPUTADA {'':5}{c3:>10.4f}"
                                              f"{m(ndec[('control',False)]):>13.1f}/{todos}")
    print(f"  {'(control, memoria presente)':34}{m(rows[('control',True)]):>10.4f}")

    print(f"\n  4-5 · FUGA POR LA OBSERVACIÓN COMPLETA (4x5x5 canales + energía)")
    print(f"      decodificador de vecino más próximo, 30% reservado")
    print(f"      {'mundo':14}{'reservado':>11}{'tasa base':>11}{'H(A*)':>9}")
    for label in ("exigente", "control"):
        dec = m([x[0] for x in leak[label]]); base = m([x[1] for x in leak[label]])
        print(f"      {label:14}{dec:>11.4f}{base:>11.4f}{m(hstar[label]):>9.4f}")

    d_ex = m([x[0] for x in leak['exigente']]); b_ex = m([x[1] for x in leak['exigente']])
    d_ct = m([x[0] for x in leak['control']])
    h_ex, h_ct = m(hstar['exigente']), m(hstar['control'])

    print(f"\n  6 · episodic_information del CONTROL debe renovar = False")
    w0, c0 = instances.twin(MEMORY, seed=0, stations=a.estaciones, economy=eco)
    e_ex = exposure.episodic_information(oracles.run(w0, memory=True, seed=0).records)
    e_ct = exposure.episodic_information(oracles.run(c0, memory=True, seed=0).records)
    print(f"      exigente: decodificador={e_ex.decoder_heldout:.4f} base={e_ex.base_rate:.4f}"
          f"  fuga={e_ex.leak_at_decision:.4f}  renueva={e_ex.renews}")
    print(f"      control : decodificador={e_ct.decoder_heldout:.4f} base={e_ct.base_rate:.4f}"
          f"  fuga={e_ct.leak_at_decision:.4f}  renueva={e_ct.renews}")

    checks = {
        "1 exigente+memoria -> 1":      c1 >= 0.95,
        "2 exigente-memoria -> azar":   abs(c2 - 0.5) <= 0.10,
        "3 control-memoria -> 1":       c3 >= 0.95,
        "4 exigente: sin fuga":         d_ex <= b_ex + 0.05,
        "5 control: la fuga ES la vía": d_ct >= 0.95,
        "6 control no renueva":         (not e_ct.renews) and e_ex.renews,
        "H(A*) pareado":                abs(h_ex - h_ct) <= 0.02,
    }
    print(f"\n  CONTRATOS")
    for k, v in checks.items():
        print(f"      {k:34}{'PASA' if v else 'FALLA':>8}")
    ok = all(checks.values())
    print(f"\n  D5 · {'PASA' if ok else 'FALLA'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
