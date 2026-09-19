#!/usr/bin/env python
"""E2 confirmatoria · nacimientos frescos, F1 reparado, matriz de portadores.

PREREGISTRO. Se fija aquí, antes de correr, y no se toca después.

  Estimando primario de F1
      ΔG_NF = G^N − G^F,  con  G = discriminación_post − discriminación_pre
      medida sobre el MISMO banco de sondas diagnósticas para los tres brazos.
      Discriminación = ventaja(CONSUME−MOVE) en situaciones favorables menos la
      misma ventaja en los controles: un sesgo uniforme se cancela, de modo que
      lo que se mide es distinguir tener recurso de no tenerlo, no valorar
      CONSUME más en abstracto.
      F1 se declara si el IC95% pareado de ΔG_NF excluye el cero por arriba y
      ningún par domina el signo.

  F2
      La adquisición RELEVANTE persiste: G medida tras la congelación y al
      empezar el probe conductual sigue ≈ la medida tras adquisición.
      Se declara si |G_frozen − G_post| < 0.25·|G_post| y G_post > 0.

  F3
      Δ(NORMAL − FULL) en consumos del probe congelado, IC95% pareado que
      excluya el cero por arriba y sin dominación de un par.

  Parada por precisión
      n mínimo 32 nacimientos FRESCOS (semillas 1000+, disjuntas de
      DISCOVERY-32). Se continúa mientras el IC de ΔG_NF sea ambiguo; techo 128.

  Las 32 de DISCOVERY no entran aquí. Nacieron la hipótesis que esto confirma o
  refuta, y usarlas para confirmarla sería usar los datos dos veces.

Análisis mecanístico secundario: la matriz de portadores, evaluada en dos
niveles -- conocimiento (banco de sondas) y conducta (probe congelado) -- para
preguntar si el conocimiento viaja con theta, con M, o con ninguno por separado.

    python scripts/bench_e2_confirmatory.py --pares 32
"""

from __future__ import annotations

import argparse
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.agent.agents import create_agent  # noqa: E402
from terrario.core.rng import RNGManager  # noqa: E402
from terrario.lab.causal_bench import (  # noqa: E402
    REGIME_INTERVENTIONS, BirthSnapshot, PairedResult, assert_birth_equivalence,
    carrier_matrix, variance_components,
)
from terrario.lab.diagnostic_probes import (  # noqa: E402
    build_probe_bank, gain, read_bank,
)
from terrario.world.transition import build_episode_components, run_step  # noqa: E402

sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from exp_adaptive_foraging_01 import (  # noqa: E402
    BASE, force_action, live, rich_world, ring_world,
)

#: Disjuntas de DISCOVERY-32, que usó 0..31.
FRESH_SEED_BASE = 1000
CARRIERS = ("BIRTH", "THETA", "M", "THETA_M", "NONPARAM", "FULL_LEARNED")


@dataclass
class PairRecord:
    pair_id: str
    informative: int
    gain_discrimination: dict[str, float] = field(default_factory=dict)
    gain_favourable: dict[str, float] = field(default_factory=dict)
    frozen_discrimination: dict[str, float] = field(default_factory=dict)
    post_discrimination: dict[str, float] = field(default_factory=dict)
    consumes: dict[str, int] = field(default_factory=dict)
    survived: dict[str, bool] = field(default_factory=dict)
    carrier_knowledge: dict[str, float] = field(default_factory=dict)
    carrier_behaviour: dict[str, int] = field(default_factory=dict)


def run_pair(index: int, *, acquisition_steps: int, probe_distance: int) -> PairRecord | None:
    seed = FRESH_SEED_BASE + index
    bank = build_probe_bank()

    birth = BirthSnapshot.materialize(f"fresh-{index:03d}", BASE, seed=seed)
    arms = birth.triplet()
    assert_birth_equivalence(arms)

    # --- stream informativo, uno solo para los tres ---------------------------
    scenario = rich_world(seed, duration=acquisition_steps)
    comps = build_episode_components(scenario, duration_fallback=acquisition_steps,
                                     strict_physics=True, with_lifecycle=False,
                                     world_seed=seed)
    RNGManager.set_global_determinism(seed)
    recorder = create_agent("A4_ADVANCED", dict(BASE), seed=seed)
    stream, informative = [], 0
    for step in range(acquisition_steps):
        out = run_step(comps, recorder, step, world_seed=seed, agent_seed=seed,
                       max_steps=acquisition_steps, learning_enabled=True)
        stream.append({"observation": out.observation_t,
                       "action_int": out.action.to_int(), "transition": out.transition})
        if out.target is not None and out.effects and out.energy_delta > 0:
            informative += 1
        if out.terminated or out.truncated:
            break
    if informative == 0:
        return None

    record = PairRecord(birth.pair_id, informative)

    # --- momento 1: pre-adquisición ------------------------------------------
    pre = {name: read_bank(arm.specimen, bank) for name, arm in arms.items()}

    # --- ACQUISITION ----------------------------------------------------------
    for name, arm in arms.items():
        agent = arm.specimen
        for i, entry in enumerate(stream):
            agent.adaptive_freeze.set_step(i)
            agent.perceive(entry["observation"])
            agent.decide()
            force_action(agent, entry["action_int"])
            agent.learn(entry["transition"])

    # --- momento 2: post-adquisición -----------------------------------------
    post = {name: read_bank(arm.specimen, bank) for name, arm in arms.items()}
    for name in arms:
        g = gain(pre[name], post[name])
        record.gain_discrimination[name] = g["discrimination"]
        record.gain_favourable[name] = g["favourable"]
        record.post_discrimination[name] = post[name].discrimination

    # --- momento 3: tras la congelación (nada debe moverse) -------------------
    frozen = {name: read_bank(arm.specimen, bank) for name, arm in arms.items()}
    for name in arms:
        record.frozen_discrimination[name] = frozen[name].discrimination

    # --- PROBE conductual congelado ------------------------------------------
    probe = ring_world(probe_distance, seed)
    for name, arm in arms.items():
        life = live(arm.specimen, probe, seed=seed, learning=False)
        record.consumes[name] = life.effective_consumes
        record.survived[name] = life.survived

    # --- matriz de portadores, en los dos niveles ----------------------------
    hosts = carrier_matrix(arms["NORMAL"], birth)
    for name, host in hosts.items():
        reading = read_bank(host.specimen, bank)
        record.carrier_knowledge[name] = reading.discrimination
        life = live(host.specimen, ring_world(probe_distance, seed), seed=seed, learning=False)
        record.carrier_behaviour[name] = life.effective_consumes
    return record


def report(records: Sequence[PairRecord]) -> int:
    n = len(records)
    print(f"\n\nE2 CONFIRMATORIA · {n} nacimientos frescos (semillas "
          f"{FRESH_SEED_BASE}+), disjuntos de DISCOVERY-32\n")

    print("  F1 · ADQUISICIÓN DE CONOCIMIENTO  ·  ganancia de discriminación\n")
    print(f"  {'brazo':<13}{'G media':>12}{'G mediana':>12}{'post > 0':>12}")
    print("  " + "-" * 49)
    for name in ("NORMAL", "PARAMETRIC", "FULL"):
        values = [r.gain_discrimination[name] for r in records]
        positive = sum(1 for r in records if r.post_discrimination[name] > 0)
        print(f"  {name:<13}{statistics.fmean(values):>+12.6f}"
              f"{statistics.median(values):>+12.6f}{f'{positive}/{n}':>12}")

    estimands: dict[str, tuple[PairedResult, float, float]] = {}

    def paired(label: str, values):
        result = PairedResult(label, list(values))
        lo, hi = result.bootstrap()
        estimands[label] = (result, lo, hi)
        print(f"  {label:<26}{result.mean:>+11.6f}{result.median:>+11.6f}"
              f"{f'[{lo:+.6f}, {hi:+.6f}]':>30}{result.positive_fraction:>9.0%}"
              f"{('SÍ' if result.dominated_by_one_pair else 'no'):>10}")

    print(f"\n  {'estimando':<26}{'media':>11}{'mediana':>11}{'IC95%':>30}"
          f"{'signo +':>9}{'domina':>10}")
    print("  " + "-" * 97)
    paired("ΔG NORMAL − FULL", (r.gain_discrimination["NORMAL"]
                                - r.gain_discrimination["FULL"] for r in records))
    paired("ΔG NORMAL − PARAMETRIC", (r.gain_discrimination["NORMAL"]
                                      - r.gain_discrimination["PARAMETRIC"] for r in records))
    paired("ΔG PARAMETRIC − FULL", (r.gain_discrimination["PARAMETRIC"]
                                    - r.gain_discrimination["FULL"] for r in records))

    print("\n\n  F2 · PERSISTENCIA DE LO ADQUIRIDO  ·  ¿sobrevive a la congelación?\n")
    print(f"  {'brazo':<13}{'G post':>14}{'G congelado':>14}{'|deriva| < 25%':>18}")
    print("  " + "-" * 59)
    f2_ok = {}
    for name in ("NORMAL", "PARAMETRIC", "FULL"):
        post = statistics.fmean(r.post_discrimination[name] for r in records)
        froz = statistics.fmean(r.frozen_discrimination[name] for r in records)
        stable = sum(1 for r in records
                     if abs(r.frozen_discrimination[name] - r.post_discrimination[name])
                     < 0.25 * abs(r.post_discrimination[name] or 1e-12))
        f2_ok[name] = stable
        print(f"  {name:<13}{post:>+14.6f}{froz:>+14.6f}{f'{stable}/{n}':>18}")

    print("\n\n  F3 · USO CONDUCTUAL  ·  probe congelado\n")
    print(f"  {'brazo':<13}{'consumos media':>17}{'mediana':>10}{'sobreviven':>13}")
    print("  " + "-" * 53)
    for name in ("NORMAL", "PARAMETRIC", "FULL"):
        values = [r.consumes[name] for r in records]
        print(f"  {name:<13}{statistics.fmean(values):>17.2f}"
              f"{statistics.median(values):>10.1f}"
              f"{f'{sum(r.survived[name] for r in records)}/{n}':>13}")
    print(f"\n  {'estimando':<26}{'media':>11}{'mediana':>11}{'IC95%':>30}"
          f"{'signo +':>9}{'domina':>10}")
    print("  " + "-" * 97)
    paired("Δ NORMAL − FULL", (float(r.consumes["NORMAL"] - r.consumes["FULL"])
                               for r in records))

    print("\n\n  MATRIZ DE PORTADORES  ·  conocimiento y conducta\n")
    print(f"  {'brazo':<15}{'θ':>4}{'M':>4}{'no-param':>10}"
          f"{'conocimiento (G)':>20}{'conducta (consumos)':>22}")
    print("  " + "-" * 75)
    layout = {"BIRTH": ("ini", "ini", "ini"), "THETA": ("APR", "ini", "ini"),
              "M": ("ini", "APR", "ini"), "THETA_M": ("APR", "APR", "ini"),
              "NONPARAM": ("ini", "APR", "APR"), "FULL_LEARNED": ("APR", "APR", "APR")}
    for name in CARRIERS:
        t, m, np_ = layout[name]
        print(f"  {name:<15}{t:>4}{m:>4}{np_:>10}"
              f"{statistics.fmean(r.carrier_knowledge[name] for r in records):>+20.6f}"
              f"{statistics.fmean(r.carrier_behaviour[name] for r in records):>22.2f}")

    components = variance_components({name: [float(r.consumes[name]) for r in records]
                                      for name in ("NORMAL", "PARAMETRIC", "FULL")})
    print(f"\n  varianza entre pares {components['between_pair']:.1f} · "
          f"dentro del par {components['within_pair']:.1f} · "
          f"fracción entre pares {components['between_fraction']:.1%}")

    # --- Veredicto contra el preregistro -------------------------------------
    g_nf, lo_g, hi_g = estimands["ΔG NORMAL − FULL"]
    y_nf, lo_y, _ = estimands["Δ NORMAL − FULL"]
    f1 = lo_g > 0 and not g_nf.dominated_by_one_pair
    f2 = (f2_ok["NORMAL"] >= 0.8 * n
          and statistics.fmean(r.post_discrimination["NORMAL"] for r in records) > 0)
    f3 = lo_y > 0 and not y_nf.dominated_by_one_pair
    level = "F0"
    for flag, name in ((f1, "F1"), (f1 and f2, "F2"), (f1 and f2 and f3, "F3")):
        if flag:
            level = name
    print(f"\n\n  NIVEL MÁXIMO DEMOSTRADO = {level}")
    print(f"    F1 adquiere el conocimiento     {'sí' if f1 else 'no'}   "
          f"ΔG_NF IC [{lo_g:+.6f}, {hi_g:+.6f}]")
    print(f"    F2 persiste tras congelar       {'sí' if f2 else 'no'}   "
          f"{f2_ok['NORMAL']}/{n} estables")
    print(f"    F3 causa mejor conducta         {'sí' if f3 else 'no'}   "
          f"IC {'excluye' if lo_y > 0 else 'incluye'} el cero")

    ambiguous = lo_g < 0 < hi_g
    print(f"\n  Regla de parada: el IC de ΔG_NF "
          f"{'sigue siendo AMBIGUO — continuar' if ambiguous else 'es decisivo — parar'}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--pares", type=int, default=32)
    parser.add_argument("--pasos", type=int, default=300)
    parser.add_argument("--distancia", type=int, default=3)
    args = parser.parse_args()

    print(f"E2 CONFIRMATORIA · {args.pares} nacimientos frescos · preregistro fijado")
    records, skipped = [], 0
    for index in range(args.pares):
        record = run_pair(index, acquisition_steps=args.pasos,
                          probe_distance=args.distancia)
        if record is None:
            skipped += 1
            continue
        records.append(record)
        print(f"  {record.pair_id}: {record.informative} informativos · "
              f"ΔG_NF={record.gain_discrimination['NORMAL'] - record.gain_discrimination['FULL']:+.6f} · "
              f"N={record.consumes['NORMAL']} F={record.consumes['FULL']}")
    if skipped:
        print(f"\n  {skipped} descartados por falta de experiencia informativa")
    if not records:
        print("\n  INSUFFICIENT_INFORMATION")
        return 2
    return report(records)


if __name__ == "__main__":
    raise SystemExit(main())
