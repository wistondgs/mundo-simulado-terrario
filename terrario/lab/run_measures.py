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


def _cadena(rows: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
    """The five rates, so a failure can be LOCATED instead of narrated.

    "It died" names no component.  These separate the links of the chain that
    runs from an opportunity existing to a decision changing, and each drop
    between consecutive rates accuses a different part of the system:

        opportunity -> addressing   the action channel could not EXPRESS it
        addressing  -> interaction  the policy chose not to
        interaction -> informative  the world returned nothing to learn from
        informative -> conversion   the learner did not use what it got

    Measured entirely from sealed observer data.  `objects` and `agents` are
    world truth, which the laboratory may read and the policy may not.
    """
    def entidades(x):
        return list(x.values()) if isinstance(x, Mapping) else list(x or [])

    def punto(p):
        return (p["x"], p["y"]) if isinstance(p, Mapping) else tuple(p)

    oportunidad = direccionable = interaccion = 0
    # The world in a trace step is recorded AFTER that step's action, so an
    # object successfully consumed is already gone from it. Pairing a step's
    # action with its own recorded world scored every successful consume as
    # "did not point at anything" -- the rate came out 0.0 even for the random
    # agent that was demonstrably eating. The action at step i was chosen
    # against the world left by step i-1, and that is the pairing below.
    for anterior, row in zip(rows, rows[1:]):
        mundo = anterior.get("observer_world") or {}
        agentes = entidades(mundo.get("agents"))
        if not agentes or not isinstance(agentes[0], Mapping) or "pos" not in agentes[0]:
            # A trace without positions cannot say whether anything was
            # adjacent.  Skipped rather than counted as "no opportunity",
            # which would report a channel failure where there is only a
            # missing field.
            continue
        ax, ay = punto(agentes[0]["pos"])
        vecinos = [o for o in entidades(mundo.get("objects"))
                   if abs(punto(o["pos"])[0] - ax) + abs(punto(o["pos"])[1] - ay) == 1]
        accion = row.get("agent_action") or {}
        consume = accion.get("action_type") == "CONSUME"
        contrato = accion.get("action_contract")
        if vecinos:
            oportunidad += 1
            # Addressable: the action as emitted actually referred to one of them.
            #
            # How that is decided depends on the addressing contract, and the two
            # must not be confused. Under T0 the referent IS the direction, so
            # the check is geometric and NONE points nowhere. Under T1 the
            # referent is an entity and the direction is pinned to NONE by
            # construction -- reading `direction` there would have scored every
            # T1 run at exactly 0.000, an instrument reporting the absence of the
            # thing it was built to measure. When the step carries Action
            # Contract v2 provenance, the resolver has already answered the
            # question and its verdict is authoritative.
            if contrato:
                if consume and contrato.get("target_status") == "VALID":
                    direccionable += 1
            else:
                delta = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}
                d = delta.get(accion.get("direction"))
                if consume and d and any(punto(o["pos"]) == (ax + d[0], ay + d[1]) for o in vecinos):
                    direccionable += 1
        if consume:
            interaccion += 1
    return {"oportunidad": oportunidad, "direccionable": direccionable,
            "intentos": interaccion, "pasos": max(len(rows) - 1, 0)}


def _realizacion(rows: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
    """Deciding correctly and executing correctly are different failures.

    Until now the chain ran opportunity -> addressing -> outcome, and everything
    between "the organism named a real, reachable thing" and "the world did
    something to that thing" was one undifferentiated gap. An intention that
    resolves and then is not carried out looks identical, from the outside, to an
    intention that never resolved.

        P(executed target == intended target | the intention resolved)

    Defined only where v2 provenance exists, because v1 records no intention to
    compare against -- and NOT_EVALUABLE is the correct answer there, not 1.0.
    """
    validas = realizadas = 0
    for row in rows:
        contrato = (row.get("agent_action") or {}).get("action_contract")
        if not contrato or contrato.get("target_status") != "VALID":
            continue
        validas += 1
        if (contrato.get("executed_target") is not None
                and contrato.get("executed_target") == contrato.get("intended_target")):
            realizadas += 1
    return {"validas": validas, "realizadas": realizadas}


def _energy_ledger(rows: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
    """Every change in energy must be attributable to a declared flow.

    The metabolic baseline used to be RECONSTRUCTED after the fact, as the median
    idle delta, and a reconstruction is only as good as its assumption that the
    declared flows are the only ones. If a scenario later adds a cost or a gain,
    the median absorbs it silently and every downstream reading shifts without
    anything failing.

    So this checks the ledger directly: on a step where nothing was consumed, the
    energy change must equal minus the declared step cost. A step that does not
    reconcile is an undeclared flow, and it is reported rather than smoothed --
    the source of truth should be the ledger of metabolic transitions, not a
    later inference about what probably happened.
    """
    declarado = (rows[0].get("observer_world") or {}).get("step_energy_cost") if rows else None
    if not isinstance(declarado, (int, float)) or isinstance(declarado, bool):
        return {"checked": 0, "reconciled": 0, "unexplained": (),
                "reason": "NO_DECLARED_STEP_COST"}
    niveles = []
    for row in rows:
        agent = _agents(row)
        if not isinstance(agent.get("energy"), (int, float)):
            return {"checked": 0, "reconciled": 0, "unexplained": (),
                    "reason": "NO_ENERGY_SERIES"}
        niveles.append(float(agent["energy"]))
    revisados = conciliados = 0
    sin_explicar = []
    for index, (antes, despues) in enumerate(zip(niveles, niveles[1:]), start=1):
        eventos = list(rows[index].get("agent_events") or ())
        if any("consume" in str(e) for e in eventos):
            continue  # a declared interaction flow; judged by _eating, not here
        revisados += 1
        if abs((despues - antes) + float(declarado)) <= 1e-6:
            conciliados += 1
        elif len(sin_explicar) < 5:
            sin_explicar.append({"step": index, "observed_delta": round(despues - antes, 6),
                                 "predicted_delta": -float(declarado)})
    return {"checked": revisados, "reconciled": conciliados,
            "unexplained": tuple(sin_explicar), "reason": None}


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
    # The baseline is the energy change a step costs when nothing is eaten, and
    # every consume is judged against it. Reading it as the median idle delta
    # fails for exactly the organism we care about most: one whose policy has
    # collapsed onto CONSUME has no idle steps at all, the median of an empty
    # list used to default to 0.0, and then the whole metabolic drain was scored
    # as hundreds of failed consumes -- a hit rate of 0.000 manufactured out of
    # the step cost. So the declared cost wins when the world states one, the
    # median is the fallback, and when neither exists the reading is refused
    # rather than coerced.
    declared = (rows[0].get("observer_world") or {}).get("step_energy_cost")
    if isinstance(declared, (int, float)) and not isinstance(declared, bool) and declared > 0:
        baseline = -float(declared)
    elif idle:
        baseline = idle[len(idle) // 2]
    else:
        return {"effective": 0, "hit_rate": None, "best_segment": None,
                "baseline": None, "baseline_source": "NO_IDLE_STEPS_AND_NO_DECLARED_COST"}

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
            "best_segment": round(max(rates), 3) if rates else None,
            "baseline": baseline,
            "baseline_source": "DECLARED" if declared else "MEDIAN_IDLE"}


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
    cadena = _cadena(rows)
    realizacion = _realizacion(rows)
    ledger = _energy_ledger(rows)
    n = len(rows)
    tasa = lambda num, den: round(num / den, 4) if den else None
    decisiones = cadena["pasos"]
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
        # The five rates of §8. Read them in order: the first drop names the
        # broken link, and every one of them is defined for every mix.
        Measure("tasa_oportunidad", "Tuvo algo al lado", tasa(cadena["oportunidad"], decisiones), "de 1",
                "Fracción de pasos con un objeto adyacente. Si es baja, el problema es el mundo."),
        Measure("tasa_direccionamiento", "Pudo APUNTAR a lo que tenía al lado",
                tasa(cadena["direccionable"], cadena["oportunidad"]), "de 1",
                "De las oportunidades, cuántas la acción llegó a señalar. Una caída aquí acusa al "
                "CANAL DE ACCIÓN, no al organismo: con 25 acciones hay que acertar 1 de 5 "
                "direcciones y NONE no apunta a ninguna casilla.",
                evaluable=cadena["oportunidad"] > 0,
                reason=None if cadena["oportunidad"] else NOT_EVALUABLE),
        Measure("tasa_interaccion", "Quiso interactuar", tasa(cadena["intentos"], decisiones), "de 1",
                "Fracción de pasos en que eligió CONSUME, haya o no algo. Alta con "
                "direccionamiento bajo es un organismo que quiere y no puede."),
        Measure("tasa_informativa", "Recibió algo que enseñe",
                tasa(eating["effective"], n), "de 1",
                "Fracción de pasos que devolvieron consecuencia discriminativa. Es el eje X "
                "real del aprendizaje: sin exposiciones no hay nada que aprender, por mucho "
                "tiempo que pase."),
        Measure("conversion_aprendizaje", "Convirtió evidencia en acierto",
                eating["best_segment"], "de 1",
                "Mejor acierto dentro de un tramo de reglas estables. Con exposiciones "
                "suficientes y esto en 0.5, el fallo es del aprendizaje y no del canal.",
                evaluable=eating["best_segment"] is not None,
                reason=None if eating["best_segment"] is not None else NOT_EVALUABLE),
        Measure("tasa_realizacion", "Ejecutó lo que había resuelto",
                tasa(realizacion["realizadas"], realizacion["validas"]), "de 1",
                "De las intenciones que SÍ resolvieron a una entidad real y alcanzable, "
                "cuántas el mundo ejecutó contra esa misma entidad. Separa decidir bien "
                "de ejecutar bien. Sin contrato v2 en la traza no hay intención que "
                "comparar, y eso es no evaluable, no un 1.0.",
                evaluable=realizacion["validas"] > 0,
                reason=None if realizacion["validas"] else NOT_EVALUABLE),
        Measure("contabilidad_energetica", "La energía cuadra con lo declarado",
                tasa(ledger["reconciled"], ledger["checked"]), "de 1",
                "Fracción de pasos sin consumo cuyo cambio de energía es exactamente el "
                "coste declarado. Por debajo de 1 hay un flujo que el escenario no "
                "declara, y entonces cualquier línea base reconstruida está midiendo "
                "ese flujo sin saberlo.",
                evaluable=ledger["checked"] > 0,
                reason=None if ledger["checked"] else NOT_EVALUABLE),
        Measure("el_mundo_actua", "La energía se movió alguna vez", bool(moved), "sí/no",
                "Si es 'no', el mundo no le está haciendo NADA al organismo y ninguna "
                "medida de viabilidad o adaptación significa nada. Mirá esto primero."),
    ]
    return {"schema_version": MEASURES_SCHEMA, "evaluable": True,
            "measures": tuple(m.__dict__ for m in measures)}
