"""Las medidas del Nivel 1.3 · todas cerradas, ninguna consume azar.

No se muestrea el desempate: se promedia. En el Nivel 1.1 muestrearlo devolvió
`0.5000` donde la esperanza era `0.4688`, y eso habría levantado una discrepancia
falsa contra el propio oráculo. Aquí, además, el suelo resulta ser **inmune al
umbral de detección de empates** --ver `expected_target_share`--, así que ni
siquiera esa elección puede mover el número.
"""

from __future__ import annotations

import math
from collections import Counter
from typing import Any, Iterable, Sequence

from terrario.level11.cue import ALL_CUES, CueSemantics
from terrario.level11.world import Direction, Observation
from terrario.level13.trials import Trial

TOLERANCIA_EMPATE = 1e-12


def expected_target_share(scores: Sequence[float], target: Direction) -> float:
    """Probabilidad de elegir `target` promediando el desempate en cerrado.

    Para una política que ignora la historia, `R = ¼ Σ_a P(a|o) = ¼` sea cual sea
    la forma de `P`: con empate perfecto cada acción vale `¼`, con máximo único la
    masa está en una sola y el cue verdadero la acierta una vez de cada cuatro.
    **El suelo no se mueve con el umbral de empate.**
    """
    maximo = max(scores)
    empatados = [d for d, v in zip(Direction, scores)
                 if math.isclose(v, maximo, rel_tol=1e-9, abs_tol=TOLERANCIA_EMPATE)]
    return sum(1 for d in empatados if d == target) / len(empatados)


def run_trial(agent: Any, trial: Trial, *, skip_tick: bool = False) -> tuple[float, ...]:
    """`present → tick → query`. El `reset` lo hace quien llama, después de medir."""
    agent.present(trial.o_present, trial.stored_cue)
    if not skip_tick:
        agent.tick()
    return agent.query(trial.o_query)


def history_use_rate(agent: Any, trials: Iterable[Trial],
                     semantics: CueSemantics, *, skip_tick: bool = False) -> float:
    """`R_history`: acertar en la consulta la dirección del cue **presentado**."""
    trials = list(trials)
    total = 0.0
    for t in trials:
        agent.reset()
        scores = run_trial(agent, t, skip_tick=skip_tick)
        total += expected_target_share(scores, t.target(semantics))
        agent.reset()
    return total / len(trials)


def memory_fidelity(agent: Any, trials: Iterable[Trial]) -> float:
    """`F_M = P(M_{t+1} = G_t)`. Lee el slot sin consumirlo."""
    trials = list(trials)
    aciertos = 0
    for t in trials:
        agent.reset()
        agent.present(t.o_present, t.stored_cue)
        agent.tick()
        aciertos += int(agent.memory.peek() == t.true_cue)
        agent.reset()
    return aciertos / len(trials)


def policy_parity(agent: Any, core: Any, pairs: Iterable[tuple[Observation, Any]],
                  o_present: Observation) -> float:
    """`D_π = max |J_memory − J_present|` sobre las 64 combinaciones × 4 acciones.

    Si `peek` devuelve exactamente el token, las dos rutas son la misma llamada
    con los mismos argumentos y la diferencia es **cero bit a bit**, no «cero
    dentro de tolerancia».
    """
    peor = 0.0
    for o, g in pairs:
        agent.reset()
        agent.present(o_present, g)
        agent.tick()
        memoria = agent.query(o)
        agent.reset()
        presente = core.joint_scores(o, g)
        peor = max(peor, max(abs(a - b) for a, b in zip(memoria, presente)))
    return peor


def mutual_information(pairs: Iterable[tuple[Any, Any]]) -> float:
    """`I(X;Y)` en bits, sobre el banco enumerado. Sin estimador: son conteos."""
    pairs = list(pairs)
    n = len(pairs)
    px, py = Counter(x for x, _ in pairs), Counter(y for _, y in pairs)
    pxy = Counter(pairs)
    return sum((c / n) * math.log2((c / n) / ((px[x] / n) * (py[y] / n)))
               for (x, y), c in pxy.items())


def memory_information(fidelity: float) -> float:
    """`I(G;M)` con cues uniformes. `2 bits` si la fidelidad es 1."""
    return 2.0 * fidelity


def body_sensitivity(agent: Any, semantics: CueSemantics) -> dict[str, float]:
    """Sonda del presente: cue recordado fijo, cambia sólo `o`.

    `Q(g,a)` debe quedar **idéntico** y `B(o,a)` debe moverse. Mide el score de
    la dirección recordada con esa dirección libre y bloqueada.
    """
    peor_q = 0.0
    libre_total = bloqueada_total = 0.0
    for g in ALL_CUES:
        d = semantics.direction_of(g)
        libre = tuple(0 for _ in Direction)
        bloqueada = tuple(1 if i == int(d) else 0 for i in range(4))
        q_libre = agent.predict_orientation(g, d)
        q_bloq = agent.predict_orientation(g, d)
        peor_q = max(peor_q, abs(q_libre - q_bloq))
        libre_total += agent.predict_body(libre, d) * q_libre
        bloqueada_total += agent.predict_body(bloqueada, d) * q_bloq
    n = len(ALL_CUES)
    return {"libre": libre_total / n, "bloqueada": bloqueada_total / n,
            "delta_q": peor_q}
