---
name: run-terrario
description: Run, drive and verify the Terrario agent lineage (Agente de Nivel 1, 2, ... n). Use this to run the Level 1 sensorimotor contingency experiment, check the effective experiment parameters before quoting them, find which code actually consumes a symbol, verify that probes do not mutate what they measure, and detect test-suite drift. Keywords: run, start, build, test, verify, check, experiment, gates, contingency, level 1.
---

# Terrario · run and verify the agent lineage

Research code. No GUI, no server: the thing you drive is an **experiment**, and
the thing that goes wrong is an **assertion about the code that nobody ran**.

Everything is driven by one script:

```
.claude/skills/run-terrario/checker.py
```

**Scope.** The live lineage is `terrario/level1/` — Agente de Nivel 1, and the
levels after it. The rest of `terrario/` is historical: earlier organisms, their
world engine and their instruments. It is read for reference and not modified.

All paths below are relative to the repository root. The interpreter is the
project venv, whose path contains spaces, so quote it:

```bash
PY="/home/wis/mundo simulado terrario/.venv/bin/python"
```

## Prerequisites

The venv already exists and carries everything needed. Verified:

```bash
"/home/wis/mundo simulado terrario/.venv/bin/python" -V
"/home/wis/mundo simulado terrario/.venv/bin/python" -c "import numpy,torch,pytest;print('numpy',numpy.__version__,'| torch',torch.__version__,'| pytest',pytest.__version__)"
```

```
Python 3.12.3
numpy 2.5.2 | torch 2.5.1+cu121 | pytest 9.1.1
```

The system `python3` does **not** work — it has no numpy. Nothing was installed
with `apt-get` in this container; none was needed.

Always prefix runs with `OMP_NUM_THREADS=2`. Unset, torch opens one thread per
core per process, and three concurrent campaigns once put this machine at load
18.8 on 12 cores.

## Run · the checker (agent path)

Everything at once, exit 0 if every check holds:

```bash
cd /home/wis/causal-bench-01
OMP_NUM_THREADS=2 "/home/wis/mundo simulado terrario/.venv/bin/python" .claude/skills/run-terrario/checker.py all --semillas 4
```

Or one at a time.

### `params` — what the run actually used

Prints the effective experiment parameters and the quantities derived from
them. Read this **before quoting any number in a report**.

```bash
OMP_NUM_THREADS=2 "/home/wis/mundo simulado terrario/.venv/bin/python" .claude/skills/run-terrario/checker.py params
```

```
    repertorio motor           4 direcciones
    espacio sensorial          16 situaciones (2^4)
    celdas de una tabla        64 pares (situación, dirección)
    transiciones por semilla   8192
    muestras por celda         ~128
```

### `consumers` — who actually reads a symbol

Parses with `ast`, not grep, and splits occurrences into **causal** (reach a
tensor, a decision or stored state) and **bookkeeping** (live inside a trace, a
log, or a `get_state` return). Defaults to `terrario/level1`; pass `--path` for
anything else.

```bash
OMP_NUM_THREADS=2 "/home/wis/mundo simulado terrario/.venv/bin/python" .claude/skills/run-terrario/checker.py consumers predict
```

```
  CAUSALES (3) — llegan a un tensor, una decisión o un estado
  CONTABILIDAD (0) — traza, log o dict de estado; observables, no causas
  VEREDICTO · tiene consumidor causal
```

On the historical tree it is what separates a real coupling from an observable:

```bash
OMP_NUM_THREADS=2 "/home/wis/mundo simulado terrario/.venv/bin/python" .claude/skills/run-terrario/checker.py consumers exploration_bias --path terrario/agent
```

```
  CAUSALES (1) — llegan a un tensor, una decisión o un estado
    terrario/agent/agents/a4_advanced.py:427
        temperature = 1.0 + self.homeostasis.exploration_bias if self._use_homeostasis else 1.0
  CONTABILIDAD (4) — traza, log o dict de estado; observables, no causas
```

### `passivity` — reading must not change the read

```bash
OMP_NUM_THREADS=2 "/home/wis/mundo simulado terrario/.venv/bin/python" .claude/skills/run-terrario/checker.py passivity
```

```
  ok     aprende por casos      celdas 47 -> 47
  ok     aprende por rasgos     celdas 36 -> 36
  ok     td (techo externo)     celdas 12 -> 12
  ok     contrato físico        0 violaciones en 256 transiciones
```

### `suite` — the failure **set**, against a record

Not a count. A new failure and a fixed-but-unrecorded one both come out,
because both are information. Takes about 8 minutes.

```bash
OMP_NUM_THREADS=2 "/home/wis/mundo simulado terrario/.venv/bin/python" .claude/skills/run-terrario/checker.py suite
```

```
SUITE · 5 fallos ahora, 5 registrados

  conocido   tests/test_agent_composition.py::test_every_offered_concept_is_a_key_the_agent_actually_reads
  conocido   tests/test_agent_composition.py::test_the_catalogue_carries_what_a_person_needs_to_choose
  conocido   tests/test_agent_composition.py::test_the_mix_reads_as_a_sentence_not_as_flags
  conocido   tests/test_system_baseline_characterization.py::test_d2_d3_d4_a0_a1_a4_match_checked_in_behavior
  conocido   tests/test_system_baseline_characterization.py::test_protected_source_and_historical_artifact_hashes_match_baseline

  el conjunto de fallos no se movió
```

All five belong to the historical lineage. Re-record only on purpose:

```bash
OMP_NUM_THREADS=2 "/home/wis/mundo simulado terrario/.venv/bin/python" .claude/skills/run-terrario/checker.py suite --record
```

### `level1` — the experiment end to end

```bash
OMP_NUM_THREADS=2 "/home/wis/mundo simulado terrario/.venv/bin/python" .claude/skills/run-terrario/checker.py level1 --semillas 4
```

```
    GATE_0_INTEGRIDAD_FISICA        PASA
    GATE_1_ADQUISICION              PASA
    GATE_2_DEPENDENCIA_CAUSAL       PASA
    GATE_3_GENERALIZACION           PASA
    GATE_4_USO_CONDUCTUAL           PASA
    GATE_5_CONTROL_POSITIVO         PASA
    GATE_6_USO_DE_LA_REGLA          PASA

  ESTADO · PASA
```

## Run · the experiment directly

Full campaign, 32 seeds, about one minute:

```bash
OMP_NUM_THREADS=2 "/home/wis/mundo simulado terrario/.venv/bin/python" -u scripts/level1_sensorimotor_contingency.py --semillas 32
```

Its contracts:

```bash
OMP_NUM_THREADS=2 "/home/wis/mundo simulado terrario/.venv/bin/python" -m pytest tests/test_level1_contingency.py -q --no-header -p no:cacheprovider
```

## Gotchas

Every one of these produced a wrong claim in a real report.

- **Quoting the constructor instead of the run.** The historical organism's
  `DEFAULT_CONFIG` says `latent_dim: 128`; the experiments override it to 16, so
  its state vector is 64-dimensional and not 640. `params` exists so nobody has
  to remember which is which.
- **Configuration by string.** The historical temporal core is selected with
  `"temporal_core": "ssm"`, and the class only becomes a GRU if that string says
  `"gru"`. Reading the file that defines `GRUCore` tells you nothing about what
  runs.
- **A probe that inserts the cell it reads.** `predict` used to create the entry
  it looked up. Values were unchanged, so no number moved — and any digest of
  the being's state was contaminated by the act of measuring it. `passivity`
  exists for exactly this.
- **Behaviour measured along each policy's own trajectory.** A deterministic
  policy holding wrong knowledge picks a blocked direction, stays, re-observes
  the same thing and is trapped. Measured: the negative control reads 0.2682 that
  way and 0.6150 on situations identical for every arm. Only that one arm moves;
  the other four agree to four decimals.
- **Reusing one bank for two measures.** The behaviour bank filters out enclosed
  positions. Reusing it for prediction dropped the Brier from 0.000826 to
  0.000070 — by selection, not by learning, since the enclosed situation is the
  rarest and worst learned.
- **grep for consumers.** A `return {...}` inside `get_state` looks causal from
  the statement alone; the function name is what marks it as bookkeeping. This
  checker got it wrong on its first run and said `drive` had a causal consumer.
- **Counting failures instead of naming them.** "5 pre-existing, none new"
  reported five times in a row is how a red suite stops being read.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `ModuleNotFoundError: No module named 'numpy'` | You used the system `python3`. Use the venv path above. |
| `UserWarning: CUDA initialization: CUDA unknown error` | Harmless. There is no GPU here and nothing in these paths needs one. |
| `suite` reports `known_failures: ["FAILED"]` | A stale baseline written by the broken parser. Delete `suite_baseline.json` and re-record. |
| `suite` says nothing moved while tests clearly fail | Same stale baseline. Check the file holds test node ids, not the word `FAILED`. |
| Machine load spikes during a campaign | `OMP_NUM_THREADS` was unset. |
