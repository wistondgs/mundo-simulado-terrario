#!/usr/bin/env python3
"""Freeze manifest for the historical experimental programme.

The scientific question changed.  The old programme asked *does this organism
acquire this concrete capability*; the new one will ask what happens when
minimal capabilities accumulate against systematically varied worlds.  Mixing
them would contaminate the interpretation, so this draws the boundary.

Freezing here means preserve, identify, classify, close interpretation and
separate.  It does not mean delete, deprecate, declare wrong, migrate, rewrite
a result, or turn a historical test green.

Two rules govern what goes in:

**Revisions are read, never typed.**  Every campaign's commit comes out of the
worktree it lives in.  The project's own catalogued failure mode is a campaign
that seals by transcribing values into constants with nothing checking the
transcription against the document, and a manifest that repeated it would be
the same defect wearing a boundary's clothes.

**What is not known stays UNKNOWN.**  No provenance is reconstructed by
inference and no gap is filled to make the new programme's story tidier.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCHEMA_VERSION = "terrario.congelacion-historica/v1"
RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "docs" / "CONGELACION_MANIFIESTO.json"

#: Por qué se congela. No convierte problemas antiguos en éxitos.
RAZONES = {
    "QUESTION_RETIRED",
    "SUPERSEDED_RESEARCH_PROGRAM",
    "HISTORICAL_REFERENCE",
    "INSTRUMENT_LIMITATION",
    "UNRESOLVED_HISTORICAL_ANOMALY",
}

UNKNOWN = "UNKNOWN"
NO_REDERIVABLE = "NON_REDERIVABLE"

#: Lo que TODAS las campañas comparten, medido en §46.8 y no repetido por fila:
#: ninguna usa el carril de archivo direccionado por contenido. Sellan
#: commiteando un markdown y transcribiendo los valores a constantes.
ARCHIVO_COMUN = ("markdown committed in its own worktree; the content-addressed "
                 "archive lane (ArtifactRepository / seal_metric_result / "
                 "admit_evidence) is NOT used by any campaign · cartografia §46.8")

#: Y el instrumento: ningún nivel importa el registro canónico de instrumentos.
#: Cada uno lleva sus propios gates. Medido en §43.1 sobre los ocho árboles.
INSTRUMENTO_COMUN = ("own per-level gates; no level imports capability_passport, "
                     "instrument_registry or measurement_status · cartografia §43.1")

CAMPANAS = [
    dict(experiment_id="LEVEL-1.0-SENSORIMOTOR-CONTINGENCY",
         worktree="/home/wis/causal-bench-01", linaje="A",
         scientific_question="does the organism acquire sensorimotor contingency?",
         scope="one world, one organism, one mechanism family",
         worlds="level1 grid", agents="Agente de Nivel 1",
         gates="own sealed gates, negative fixture per gate",
         result_status="FROZEN · demostrada en su mundo",
         known_limitations="scope is one world; no cross-world claim",
         reason_for_freeze="SUPERSEDED_RESEARCH_PROGRAM",
         source="cartografia §43.3, §43.7"),
    dict(experiment_id="LEVEL-1.0-MOTOR-MAP-REVERSAL-PROBE",
         worktree="/home/wis/causal-bench-01", linaje="A",
         scientific_question="probe, not an acquisition: does the motor map reverse?",
         scope="probe attached to 1.0", worlds="level1 grid",
         agents="Agente de Nivel 1", gates="own sealed gates",
         result_status="FROZEN",
         known_limitations="explicitly not an acquisition; not a rung of the ladder",
         reason_for_freeze="HISTORICAL_REFERENCE",
         source="cartografia §43.3"),
    dict(experiment_id="LEVEL-1.1-DIRECTIONAL-ORIENTATION",
         worktree="/home/wis/causal-bench-01", linaje="A",
         scientific_question="does the organism acquire directional orientation "
                             "from the external signal g_t?",
         scope="one world, one organism", worlds="level1 grid",
         agents="descendant of Agente de Nivel 1",
         gates="own sealed gates, negative control",
         result_status="FROZEN · demostrada",
         known_limitations="the learning mechanism was left undecided on purpose",
         reason_for_freeze="SUPERSEDED_RESEARCH_PROGRAM",
         source="cartografia §43.3, §43.7"),
    dict(experiment_id="LEVEL-1.2-QUALITATIVE-PROXIMITY",
         worktree="/home/wis/causal-bench-01", linaje="A",
         scientific_question="does the organism acquire qualitative proximity?",
         scope="one world, one organism", worlds="level1 grid",
         agents="descendant of Agente de Nivel 1",
         gates="12 sealed gates · reconciled 2026-09-21 (script ran 10, header "
               "said 11, report said «the ten evaluable»); L12-1 and L12-9 were "
               "in contracts",
         result_status="FROZEN · demostrada y reconciliada · ceiling 8/55",
         known_limitations="thresholds do not carry across decimals; the false "
                           "fixture of L12-9 had been duplicated",
         reason_for_freeze="SUPERSEDED_RESEARCH_PROGRAM",
         source="cartografia §43.3, §43.7"),
    dict(experiment_id="LEVEL-1.3-ONE-STEP-REFERENCE-PERSISTENCE",
         worktree="/home/wis/level13-persistence-01", linaje="A",
         scientific_question="does the organism hold one reference for one step?",
         scope="one world, one organism", worlds="level1 grid",
         agents="descendant of Agente de Nivel 1",
         gates="14 sealed gates · reconciled 2026-09-21 (script ran 11); "
               "L13-1, L13-2 and L13-10 were in contracts",
         result_status="VERIFIED · demostrada y reconciliada",
         known_limitations=UNKNOWN,
         reason_for_freeze="SUPERSEDED_RESEARCH_PROGRAM",
         source="cartografia §43.3, §43.7"),
    dict(experiment_id="LEVEL-1.4-CONJUNCTIVE-BINDING",
         worktree="/home/wis/level14-binding-01", linaje="A",
         scientific_question="does the organism bind two references conjunctively?",
         scope="one world, one organism", worlds="level1 grid",
         agents="descendant of Agente de Nivel 1",
         gates="own sealed gates · 12 fixtures",
         result_status="VERIFIED · demostrada y reconciliada",
         known_limitations=UNKNOWN,
         reason_for_freeze="SUPERSEDED_RESEARCH_PROGRAM",
         source="cartografia §43.3, §43.7"),
    dict(experiment_id="ORGANISM-FUSION-BQHM",
         worktree="/home/wis/organism-fusion-hm-01", linaje="A",
         scientific_question="what does composing B+Q+H+M produce? (no new "
                             "acquisition of its own)",
         scope="one world, one organism, 2x2 factorial",
         worlds="level1 grid", agents="composed organism B+Q+H+M",
         gates="10 sealed gates · reconciled 2026-09-21 (script ran 9); F-2 was "
               "in contracts and F-9 was a usurped number: the script used F-9 "
               "for «the tick is needed» and the seal assigns it to passivity",
         result_status="VERIFIED · superadditive interaction · reconciled",
         known_limitations="measured in one world with one mechanism family; a "
                           "local interaction, not a law",
         reason_for_freeze="SUPERSEDED_RESEARCH_PROGRAM",
         source="cartografia §43.3, §43.7"),
    dict(experiment_id="LEVEL-1.5-SELECTIVE-MEMORY",
         worktree="/home/wis/organism-remembered-binding-01", linaje="A",
         scientific_question="can the organism acquire selective memory when "
                             "useful experience exceeds the capacity to keep it?",
         scope="design only · the confirmatory campaign never ran",
         worlds=UNKNOWN, agents="precondition organism B+Q+H+M+psi exists and its "
                                "campaign runs today with ten gates green",
         gates="ten gates green on the precondition organism, not on 1.5",
         result_status="CONGELADO · design only · no code, no branch, no campaign",
         known_limitations=(
             "the confirmatory never ran; TWO PILOTS did, and the second gave "
             "529/540 = 97.96%. The pilot is NON_REDERIVABLE: no .py file in any "
             "tree carries its seeds (20260920, 777, 31337 · BURNED) or any "
             "level15 marker, and the step magnitude «does not appear in the "
             "textual evidence preserved here». Between the two pilots the "
             "budget grid, the repetition structure AND the seeds all changed, "
             "so attributing the jump to the optimizer is not identified. The "
             "WITHDRAWAL of the 21 failures as a property of the problem stands "
             "on its own. alpha, the exploration schedule and the classifier "
             "remain UNKNOWN. psi alone contributes exactly zero (RB-7), so psi "
             "needs M. Pre-existing unfreeze condition, written before this "
             "freeze: «useful experience generated by the organism > capacity "
             "available to keep it»."),
         reason_for_freeze="UNRESOLVED_HISTORICAL_ANOMALY",
         source="cartografia §43.4 · AUDITORIA_FORENSE_NIVEL_15_01.md"),
    dict(experiment_id="LEVEL-1.6-OBSERVATIONAL-TEMPORAL-REGULARITY",
         worktree="/home/wis/level16-sensory-change-01", linaje="B",
         scientific_question="does the organism acquire P(o_{t+1} | o_t)?",
         scope="one world · tabular learner · T=4096 · POST bank 2048 new transitions",
         worlds="level16 world; inherits from level1.world only body and world "
                "primitives (Grid, Direction, DELTA, Observation, "
                "ALL_OBSERVATIONS) and NOTHING from level11..level14",
         agents="tabular learner · deliberate restart, body inherited, cognition not",
         gates="FROZEN · TEMPORAL-SHUFFLED · STATIC-BITCOUNT · K-SOMBRA (instrument)",
         result_status="POSITIVO",
         known_limitations="`observe` rejects in execution an act, a change bit, "
                           "an efferent copy and a position: it acquires the "
                           "observational regularity and nothing else",
         reason_for_freeze="SUPERSEDED_RESEARCH_PROGRAM",
         source="cartografia §43.5, §43.7"),
    dict(experiment_id="LEVEL-1.7-OWN-ACTION-CONTINGENCY",
         worktree="/home/wis/level17-action-contingency-01", linaje="B",
         scientific_question="does the organism acquire C_17(O, A, O'), the "
                             "deviation per action over the temporal expectation?",
         scope="one world · 16/16 pairs · 13/13 gates",
         worlds="level17 world · H(O'|O) varies 0.5623-1.5464 across worlds",
         agents="inherits the MECHANISM of 1.6 instantiated in W and frozen, not "
                "a foreign table",
         gates="13 gates · 4 controls · twin A/B with I_B(A;O'|O) = 0 EXACTLY",
         result_status="POSITIVO",
         known_limitations="does NOT acquire the causal relevance or generality "
                           "of the concept «action». NO-ACTION is deliberately "
                           "not the frozen predecessor: against a frozen M_0 a "
                           "false advantage appears that GROWS with the budget",
         reason_for_freeze="SUPERSEDED_RESEARCH_PROGRAM",
         source="cartografia §43.5, §43.7"),
    dict(experiment_id="LEVEL-1.8-PREDICTIVE-STATE",
         worktree="/home/wis/level18-predictive-state-01", linaje="B",
         scientific_question="can the organism acquire an internal representation "
                             "that disambiguates perceptually identical situations "
                             "whose consequences under the same action differ?",
         scope="round C · confirmatory seeds 180000011-180000074, SEALED AND INTACT",
         worlds="level18 world", agents="tabular learner with routing key",
         gates="own gates · ladder control · instrument repaired twice",
         result_status="BUDGET SELECTION = NONE · FAMILY_MISMATCH, not a "
                       "SCIENTIFIC_NEGATIVE: the partition family was wrongly "
                       "chosen, so the experiment did not falsify the hypothesis "
                       "-- it measured something else",
         known_limitations=(
             "root cause named and verified in code: the oracle sealed "
             "Z_{t+1} = F(Z_t, A_t, O_{t+1}) and what was implemented is the "
             "degenerate Z_{t+1} = F(Z_t, A_t) "
             "(level18/predictive_state.py:168 and :336, 16 identical routes). "
             "Hermetic proof: same 400 actions with three different observation "
             "sequences give 0/400 differences in Z. Amendment 04 §6 stopped the "
             "statistics rather than hunting for a budget that wins. Confirmatory "
             "seeds 130000011-130000026 are RESERVED AND MUST NOT BE RUN."),
         reason_for_freeze="UNRESOLVED_HISTORICAL_ANOMALY",
         source="cartografia §43.5, §43.6, §43.7"),
    dict(experiment_id="LEVEL-1.8-ADJUDICATION",
         worktree="/home/wis/level18-adjudication-01", linaje="B",
         scientific_question="does the successor need the predecessor?",
         scope=UNKNOWN, worlds="level18 world", agents=UNKNOWN,
         gates=UNKNOWN, result_status=UNKNOWN,
         known_limitations="not covered by the audited cartography sections; "
                           "its facts were not re-verified for this freeze",
         reason_for_freeze="HISTORICAL_REFERENCE",
         source="worktree head only · scope NOT audited"),
    dict(experiment_id="EXP-ADAPTIVE-FORAGING-01",
         worktree="/home/wis/exp-foraging-01", linaje="behavioural",
         scientific_question="does the organism use what it learned about foraging?",
         scope="7 seeds · paired bootstrap on the primary estimand",
         worlds="existing machinery, no new generator",
         agents="A4 unchanged; acquisition replays one recorded stream into three "
                "twins so they share the experience exactly; probe runs with "
                "learning_enabled=False",
         gates=UNKNOWN,
         result_status="BOTH VERDICTS INSUFFICIENT_INFORMATION · neither "
                       "falsified nor demonstrated",
         known_limitations="NORMAL-FULL = -3.86, 95% interval [-37.29, +18.29]; "
                           "in the autonomous campaign the whole advantage is "
                           "carried by a single seed in each condition",
         reason_for_freeze="INSTRUMENT_LIMITATION",
         source="worktree head 6d41a95 commit body"),
    dict(experiment_id="OCF-G1-G3-ORGANISM-CAUSAL-FOUNDATION",
         worktree="/home/wis/ocf-g3-close", linaje="foundation",
         scientific_question="which mechanism produced which change? can state "
                             "ownership and an adaptive freeze boundary be "
                             "demonstrated rather than declared?",
         scope="21 states probed by intercepting __setattr__",
         worlds="A4 runtime", agents="A4",
         gates="OCF-G1 (state authority) · OCF-G3 (FULL_ADAPTIVE_FREEZE)",
         result_status="OCF-G1 did NOT pass as first measured: of 21 states, one "
                       "(homeostasis._energy) has two writers. OCF-G3 built, one "
                       "canonical adaptive boundary, closed in this tree",
         known_limitations="homeostasis._threshold is written by nobody; "
                           "_energy_baseline moves 45 of 68 times, so its drift "
                           "counts policies produced, not steps lived",
         reason_for_freeze="HISTORICAL_REFERENCE",
         source="cartografia §XXXVII"),
    dict(experiment_id="AGENT-LEVEL1-COPY-EXPERIENCED-D5",
         worktree=str(RAIZ / ".claude/worktrees/sweet-dirac-968e1e"),
         linaje="probe",
         scientific_question="does the D5 dissociation hold against the real engine?",
         scope=UNKNOWN, worlds=UNKNOWN, agents=UNKNOWN, gates=UNKNOWN,
         result_status="the dissociation holds against the real engine; the "
                       "complete observation caught a projection in the instrument",
         known_limitations="not covered by the audited cartography sections; "
                           "its facts were not re-verified for this freeze",
         reason_for_freeze="HISTORICAL_REFERENCE",
         source="worktree head only · scope NOT audited"),
    dict(experiment_id="CAPABILITY-PASSPORTS-A4-A5",
         worktree=str(RAIZ), linaje="passports",
         scientific_question="none of its own: a passport is a CANDIDACY, not a "
                             "campaign. It declares what should happen when the "
                             "module is removed and which world would demand it",
         scope="10 passports for A4/A5 modules",
         worlds="declared `demanding_world` per passport, never run",
         agents="A4/A5 modules", gates="none · no campaign executes the ablation",
         result_status="1 of 10 certifiable (LEARN-A1) · 0 of 10 have an "
                       "experiment of their own",
         known_limitations="8 of 10 declare a PENDIENTE-* endpoint the registry "
                           "does not resolve ON PURPOSE, so the hole stays "
                           "visible instead of being replaced by a similar metric",
         reason_for_freeze="HISTORICAL_REFERENCE",
         source="cartografia §43.1, §43.2, §39.2"),
]

#: Lo que NO se congela, y por qué. El diseñador cruza la frontera; los mundos
#: que produjo, no.
VIVOS = [
    dict(asset="World Designer / world generator machinery",
         where="terrario/lab/world_generator.py, world_authoring.py, "
               "world_contracts.py, world_oracles.py",
         why="generator machinery is an instrument of discovery, not a result. "
             "WORLD INSTANCE (historical configuration) is FROZEN; WORLD DESIGNER "
             "is ACTIVE"),
    dict(asset="LEVEL-FACTORY-01",
         where="/home/wis/level-factory-01 · factory/",
         why="machinery for producing levels, whose admission criterion is «only "
             "what already failed». The concrete level oracles and reports it "
             "holds are copies of frozen campaign artefacts"),
    dict(asset="Hypergraph",
         where="terrario/lab/hypergraph/, terrario/lab/crossgraph/",
         why="becomes the register of the new programme: microcapabilities, "
             "observed requirements, compositions, alternatives, inhibitions, "
             "redundancies, degrees of freedom, world conditions, evidence and "
             "UNKNOWN. Historical results may be referenced, keeping HISTORICAL "
             "as provenance"),
    dict(asset="Corpus and knowledge layer",
         where="knowledge/, terrario/lab/theory/",
         why="source of mechanisms and agent behaviours, not of hypotheses"),
    dict(asset="Generic experimental infrastructure",
         where="terrario/lab/preregistration/, metric_result_sealing.py, "
               "evidence_admission.py, persistence/",
         why="the content-addressed archive lane. Built, verified, exercised 141 "
             "times, and used by ZERO campaigns. It is an instrument the new "
             "programme can use, not a historical result"),
    dict(asset="Developmental engine (A1-A3b.1)",
         where="terrario/lab/relation_ledger.py, developmental.py, "
               "developmental_signal.py, question_type.py, "
               "signature_decomposer.py, task_contract.py",
         why="built after the question changed, and built to serve it"),
]


def revision(worktree: str) -> str:
    """Leída de git, nunca tecleada."""
    try:
        salida = subprocess.run(["git", "-C", worktree, "rev-parse", "HEAD"],
                                capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return NO_REDERIVABLE
    if salida.returncode != 0:
        return NO_REDERIVABLE
    return salida.stdout.strip() or NO_REDERIVABLE


def construir() -> dict:
    filas = []
    for campana in CAMPANAS:
        if campana["reason_for_freeze"] not in RAZONES:
            raise SystemExit(f"razón desconocida: {campana['reason_for_freeze']}")
        fila = dict(campana)
        fila["status"] = "FROZEN_HISTORICAL"
        fila["revision"] = revision(campana["worktree"])
        fila["artifacts"] = ARCHIVO_COMUN
        fila.setdefault("instruments", INSTRUMENTO_COMUN)
        fila["provenance"] = (f"declared from {campana['source']}; revision read "
                              f"from the worktree, not transcribed")
        filas.append(fila)
    return {
        "schema_version": SCHEMA_VERSION,
        "boundary_commit": revision(str(RAIZ)),
        "boundary_semantics": (
            "boundary_commit is the LAST commit of the historical programme: the "
            "state this freeze was computed against. The commit that introduces "
            "this manifest is the first of the new regime. Everything at or "
            "before the boundary belongs to the historical programme; everything "
            "after belongs to the new one unless explicitly declared otherwise."),
        "git_marker": (
            "NOT created. The repository has ZERO tags, so there is no tagging "
            "convention to follow and inventing one is a repo-level decision. "
            "The authoritative boundary is this manifest."),
        "boundary_branch": subprocess.run(
            ["git", "-C", str(RAIZ), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True).stdout.strip(),
        "historical_program": "FROZEN",
        "new_microcapability_program": "NOT_YET_STARTED",
        "freeze_means": ["preserve", "identify", "classify",
                         "close interpretation", "separate from the new programme"],
        "freeze_does_not_mean": ["delete", "deprecate", "declare incorrect",
                                 "migrate", "rewrite results",
                                 "turn historical tests green"],
        "frozen_count": len(filas),
        "frozen": filas,
        "remains_active": VIVOS,
    }


if __name__ == "__main__":
    manifiesto = construir()
    if "--write" in sys.argv:
        DESTINO.write_text(json.dumps(manifiesto, indent=2, ensure_ascii=False) + "\n")
        print(f"manifiesto escrito: {manifiesto['frozen_count']} campañas congeladas, "
              f"{len(manifiesto['remains_active'])} activos vivos")
        print(f"frontera: {manifiesto['boundary_commit'][:12]} "
              f"({manifiesto['boundary_branch']})")
    else:
        print(json.dumps(manifiesto, indent=2, ensure_ascii=False))
