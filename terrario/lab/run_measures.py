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
    ]
    return {"schema_version": MEASURES_SCHEMA, "evaluable": True,
            "measures": tuple(m.__dict__ for m in measures)}
