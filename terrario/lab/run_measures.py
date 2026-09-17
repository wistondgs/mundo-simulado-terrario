"""Several ways of looking at the same run, computed from one sealed trace.

An experiment with a single measure can only find what that measure was built
to see.  So a run is not summarised by one number here: the trace is sealed and
every mesh is a projection over it, which means choosing between them is free
-- one run, all of them.

Two rules the repository already applies to its scientific instruments, applied
here too:

    a mesh that cannot be evaluated says so and is NOT coerced to zero
    a mesh that stops being defined when a concept is ablated cannot screen it

The second one disqualifies the two most obvious candidates.  Prediction error
vanishes without the world model and the planned-action pathway vanishes
without the planner -- so the one construct-validated metric in the repository
is a confirmation instrument, not a mesh.  Every measure below stays defined
across all 2^8 mixes, which is what makes them usable for screening.

Nothing here is evidence.  These are sandbox projections; the scientific path
runs through preregistration and the sealed METRIC_RESULT.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import log
from typing import Any, Iterable, Mapping, Sequence

MEASURES_SCHEMA = "terrario.lab.run-measures/v1"
NOT_EVALUABLE = "RECORD_NOT_EVALUABLE_DO_NOT_COERCE_TO_ZERO"


@dataclass(frozen=True)
class Measure:
    key: str
    label: str
    value: float | int | bool | None
    unit: str
    means: str
    evaluable: bool = True
    reason: str | None = None


def _agents(step: Mapping[str, Any]) -> Mapping[str, Any]:
    agents = (step.get("observer_world") or {}).get("agents") or {}
    entries = list(agents.values()) if isinstance(agents, Mapping) else list(agents)
    return entries[0] if entries else {}


def _scientific(step: Mapping[str, Any]) -> Mapping[str, Any]:
    return step.get("scientific_state") or {}


def _entropy(counts: Sequence[int]) -> float:
    total = sum(counts)
    if total <= 0:
        return 0.0
    return -sum((n / total) * log(n / total, 2) for n in counts if n)


def _eating(rows: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
    """Did a CONSUME gain or lose energy, judged against the step's own cost.

    The per-step cost is not assumed: it is read as the median change over the
    steps where the organism did NOT consume, so the same code works in a world
    that declares no decay at all.  An effect smaller than half an energy unit
    is a consume that reached nothing, which is a third outcome and not a miss.
    """
    levels, actions = [], []
    for row in rows:
        agent = _agents(row)
        if not isinstance(agent.get("energy"), (int, float)):
            return {"effective": 0, "hit_rate": None, "best_segment": None}
        levels.append(float(agent["energy"]))
        actions.append((row.get("agent_action") or {}).get("action_type"))

    deltas = [b - a for a, b in zip(levels, levels[1:])]
    idle = sorted(d for d, act in zip(deltas, actions[1:]) if act != "CONSUME")
    baseline = idle[len(idle) // 2] if idle else 0.0

    revisions = [(r.get("observer_world") or {}).get("rules_version") for r in rows]
    segment, per_segment = 0, {}
    hits = effective = 0
    for index, (delta, action) in enumerate(zip(deltas, actions[1:]), start=1):
        if revisions[index] != revisions[index - 1]:
            segment += 1
        if action != "CONSUME":
            continue
        effect = delta - baseline
        if abs(effect) <= 0.5:
            continue          # reached nothing: neither hit nor miss
        effective += 1
        hit = effect > 0
        hits += hit
        got, total = per_segment.get(segment, (0, 0))
        per_segment[segment] = (got + hit, total + 1)

    rates = [got / total for got, total in per_segment.values() if total >= 3]
    return {"effective": effective,
            "hit_rate": round(hits / effective, 3) if effective else None,
            "best_segment": round(max(rates), 3) if rates else None}


def _updates(step: Mapping[str, Any]) -> int:
    summary = _scientific(step).get("learning_summary") or {}
    count = summary.get("update_count")
    return int(count) if isinstance(count, (int, float)) and not isinstance(count, bool) else 0


def _numbers(rows: Sequence[Mapping[str, Any]], key: str) -> list[float]:
    values = []
    for row in rows:
        value = _scientific(row).get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        values.append(float(value))
    return values


def measure_run(steps: Iterable[Mapping[str, Any]]) -> Mapping[str, Any]:
    """Every mesh that stays defined for every mix, over one sandbox trace."""
    rows = list(steps)
    if not rows:
        return {"schema_version": MEASURES_SCHEMA, "measures": (), "evaluable": False,
                "reason": "NO_STEPS"}

    last, first = rows[-1], rows[0]
    final_agent, initial_agent = _agents(last), _agents(first)
    max_energy = float((last.get("observer_world") or {}).get("max_energy") or 0.0)

    actions = [(s.get("agent_action") or {}).get("action_type") for s in rows]
    used = {a for a in actions if a}
    tally = [actions.count(a) for a in sorted(used)]

    # The runtime reports "NOT_APPLICABLE" rather than a number when a channel
    # does not apply to the mix -- a frozen organism has no parameter delta.
    # That string is a fact, not a zero, so it is dropped from the sample and
    # the measure reports itself as not evaluable if nothing numeric remains.
    entropies = _numbers(rows, "policy_entropy")
    deltas = _numbers(rows, "parameter_delta_norm")

    revisions = [(s.get("observer_world") or {}).get("rules_version") for s in rows]
    disturbances = sum(1 for a, b in zip(revisions, revisions[1:]) if a != b and b is not None)

    energy = final_agent.get("energy")
    start = initial_agent.get("energy")
    eating = _eating(rows)
    # Any movement at all, not just net movement: an organism that spent and ate
    # back to par is in a live world; one whose energy never changed is not.
    levels = {round(float(_agents(row)["energy"]), 6) for row in rows
              if isinstance(_agents(row).get("energy"), (int, float))}
    moved = len(levels) > 1

    measures = [
        Measure("pasos_vividos", "Pasos vividos", len(rows), "pasos",
                "Cuánto duró antes de terminar el episodio o morir."),
        Measure("sigue_vivo", "Seguía vivo al final",
                bool(final_agent.get("alive")) if "alive" in final_agent else None, "sí/no",
                "Si llegó al final del episodio en pie.",
                evaluable="alive" in final_agent, reason=None if "alive" in final_agent else NOT_EVALUABLE),
        Measure("energia_final", "Energía al final",
                round(float(energy), 2) if energy is not None else None,
                f"de {max_energy:g}" if max_energy else "energía",
                "Cuánto le quedaba. Es rendimiento, no un constructo cognitivo.",
                evaluable=energy is not None, reason=None if energy is not None else NOT_EVALUABLE),
        Measure("balance_energia", "Ganó o perdió energía",
                round(float(energy) - float(start), 2) if None not in (energy, start) else None,
                "energía", "Diferencia contra como empezó: negativo es que se fue consumiendo.",
                evaluable=None not in (energy, start),
                reason=None if None not in (energy, start) else NOT_EVALUABLE),
        Measure("acciones_distintas", "Acciones distintas que usó", len(used), "de 5",
                "Cuánta de su variedad conductual llegó a ejercer. Tener acciones y usarlas no es lo mismo."),
        Measure("variedad_conductual", "Reparto entre acciones", round(_entropy(tally), 3), "bits",
                "Alto: reparte entre varias acciones. Cero: repite siempre la misma."),
        # Averaged, not summed: a longer run would otherwise look more undecided
        # for no reason other than being longer.
        Measure("indecision_media", "Indecisión media al elegir",
                round(sum(entropies) / len(entropies), 3) if entropies else None, "bits",
                "Cuán repartida estaba su política entre acciones al decidir.",
                evaluable=bool(entropies), reason=None if entropies else NOT_EVALUABLE),
        # Summed, not averaged: this is how much the organism changed over its
        # whole life, and the total is the quantity of interest.
        #
        # It is declared even though it is currently never evaluable, rather
        # than quietly dropped. A4 computes parameter_delta_norm inside learn()
        # and puts it in its trace events; get_scientific_state() does not carry
        # it, so the transport fills the declared field with NOT_APPLICABLE and
        # the finest measure of self-change never reaches the sandbox. Hiding
        # that would leave the most theory-relevant mesh silently missing.
        Measure("cambio_propio", "Cuánto se cambió a sí mismo",
                round(sum(deltas), 4) if deltas else None, "norma acumulada",
                "Cuánto movió sus propios parámetros viviendo.",
                evaluable=bool(deltas),
                reason=None if deltas else "EL AGENTE LO CALCULA PERO NO LO EXPONE AL SANDBOX"),
        Measure("actualizaciones", "Veces que se actualizó", _updates(last), "actualizaciones",
                "Cuántas veces cambió sus parámetros. Es lo grueso de lo anterior: "
                "cuenta los cambios, no su tamaño. Cero con el aprendizaje apagado."),
        Measure("perturbaciones_vistas", "Perturbaciones que alcanzó a vivir", disturbances, "cambios de regla",
                "Si es 0 en un mundo que las tiene, el episodio terminó antes de la primera."),
        # Sentinel. It exists because a six-step smoke run passed clean while the
        # sandbox was building D4T as an empty grid with no energy cost: the
        # organism could not eat, could not decay, and -- since energy_delta is
        # also its reward -- trained for 1200 steps with no reinforcement at
        # all. Every other mesh reported plausible numbers throughout. This one
        # would have said no in seconds.
        # Whether the organism ever learns the channel->sign mapping at all.
        # Nine meshes reported plausible numbers for 1200 steps while net intake
        # was zero, and none of them could say whether that was "eats a lot,
        # badly" or "eats almost nothing" -- different organisms.
        Measure("comidas_efectivas", "Veces que comió algo", eating["effective"], "consumos",
                "Acciones CONSUME que de verdad tocaron un objeto. Intentar y no alcanzar nada no cuenta."),
        Measure("aciertos_al_comer", "Proporción de aciertos al comer",
                eating["hit_rate"], "de 1",
                "Fracción de lo que comió que le sumó energía. 0.5 sostenido es la firma de no "
                "distinguir las clases: en D4T el mapeo se invierte tres veces, así que aprender "
                "se vería como tramos claramente por encima de 0.5, no como un promedio alto.",
                evaluable=eating["hit_rate"] is not None,
                reason=None if eating["hit_rate"] is not None else NOT_EVALUABLE),
        Measure("mejor_tramo_al_comer", "Mejor tramo de aciertos",
                eating["best_segment"], "de 1",
                "El mejor acierto dentro de un tramo con reglas estables. Si nunca sube de 0.5 "
                "en NINGÚN tramo, no aprendió el mapeo en ninguna de sus versiones.",
                evaluable=eating["best_segment"] is not None,
                reason=None if eating["best_segment"] is not None else NOT_EVALUABLE),
        Measure("el_mundo_actua", "La energía se movió alguna vez", bool(moved), "sí/no",
                "Si es 'no', el mundo no le está haciendo NADA al organismo y ninguna "
                "medida de viabilidad o adaptación significa nada. Mirá esto primero."),
    ]
    return {"schema_version": MEASURES_SCHEMA, "evaluable": True,
            "measures": tuple(m.__dict__ for m in measures)}
