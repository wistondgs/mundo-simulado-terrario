"""What the organism can be made of, in words a person can choose from.

A4 carries eight switches that turn modules on and off.  Each one is a corpus
concept made algorithm, and until now none of them could be reached: the lab
contract carries an agent *id* and nothing else, so every screen could name an
architecture and none could compose one.

The catalogue lives here rather than in the page because a description that
drifts from the code is worse than no description.  `key` is the literal
config key A4 reads, so a concept that stops existing stops being offerable,
and `validate_selection` refuses an unknown key instead of ignoring it -- a
misspelling that silently changes nothing is the worst failure mode a
composition screen can have.

`purpose` answers "what is this for", in one sentence, without jargon.
`without_it` answers the question a person actually asks when deciding whether
to switch something off.  Neither claims the module works: `block` points at
the concept in the map, and whether the implementation earns the name is what
the experiments are for.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from terrario.agent.agents.a4_advanced import DEFAULT_CONFIG
from terrario.agent.agents.a5_cybernetic import DEFAULT_CONFIG as A5_DEFAULT_CONFIG
from terrario.core.action_contract import IMPLEMENTED_MODES

#: Qué lee cada organismo del linaje. **El catálogo se deriva de aquí**, no de
#: una lista escrita a mano: un concepto se ofrece para un agente si y sólo si
#: ese agente lee su clave. Cuando no era así, `use_curiosity` --que es de A5--
#: se ofrecía sobre A4, `catalogue()` levantaba `KeyError` y
#: `validate_selection` la aceptaba para un organismo que la ignora. Derivarlo
#: hace estructural lo que antes era disciplina.
#: Claves canónicas, no alias: la tabla de alias es de la factoría y no se
#: duplica aquí --dos tablas de nombres derivan, y ya sabemos cómo acaba eso--.
#: A0…A3 no leen ninguna clave `use_*`; su entrada vacía no es un hueco por
#: rellenar, es la afirmación de que no componen nada.
AGENT_CONFIGS: dict[str, Mapping[str, Any]] = {
    "A0_RANDOM": {},
    "A1_REACTIVE": {},
    "A2_GRU": {},
    "A3_WORLD_MODEL": {},
    "A4_ADVANCED": DEFAULT_CONFIG,
    "A5_CYBERNETIC": A5_DEFAULT_CONFIG,
}
DEFAULT_AGENT = "A4"

CATALOGUE_SCHEMA = "terrario.lab.agent-composition/v1"


@dataclass(frozen=True)
class Concept:
    key: str
    label: str
    purpose: str
    without_it: str
    block: str
    corpus_block: int
    #: El organismo que INTRODUCE el concepto. No es quién puede usarlo: un
    #: descendiente hereda los módulos de su ancestro, y eso se resuelve
    #: mirando su configuración, no esta etiqueta.
    agent: str = "A4"


class CompositionError(ValueError):
    code = "AGENT_COMPOSITION_ERROR"


#: Ordered as the organism processes: it perceives, remembers, models,
#: doubts, plans, regulates, and changes.  The order is the reading order of
#: the screen, not a claim about the architecture.
CONCEPTS: tuple[Concept, ...] = (
    Concept("use_temporal", "Memoria del momento",
            "Recuerda lo que acaba de pasar, para que una decisión pueda depender de los pasos anteriores y no sólo de lo que ve ahora.",
            "Cada paso se decide como si fuera el primero.",
            "dinámica temporal", 4),
    Concept("use_episodic_memory", "Memoria de episodios",
            "Guarda situaciones concretas que vivió y las vuelve a encontrar cuando se parece la actual.",
            "Puede repetir el mismo error sin reconocer que ya lo vivió.",
            "memoria episódica", 4),
    Concept("use_longterm_memory", "Memoria a largo plazo",
            "Acumula lo aprendido a lo largo de toda la vida del organismo, no sólo del episodio en curso.",
            "Lo aprendido se pierde al terminar el episodio.",
            "memoria persistente", 4),
    Concept("use_world_model", "Modelo del mundo",
            "Predice qué va a pasar si actúa, en vez de descubrirlo sólo actuando.",
            "Sólo aprende por consecuencia consumada.",
            "modelo del mundo", 8),
    Concept("use_uncertainty", "Estimación de incertidumbre",
            "Calcula cuánta confianza tiene en su propia predicción.",
            "Trata por igual lo que sabe bien y lo que apenas conoce.",
            "incertidumbre", 38),
    Concept("use_curiosity", "Curiosidad",
            "Convierte el error de su propia predicción en motivo para actuar.",
            "Sólo se mueve si algo externo le paga; sin pago externo, no tiene hacia dónde.",
            "exploración", 28, agent="A5"),
    Concept("use_planner", "Planificación",
            "Imagina varias secuencias de acciones y compara sus consecuencias antes de moverse.",
            "Actúa paso a paso, sin anticipar la secuencia.",
            "planificación", 27),
    Concept("use_online_learning", "Aprendizaje en marcha",
            "Cambia sus parámetros durante la propia vida, no sólo entre corridas.",
            "Queda congelado: hará lo mismo al principio y al final.",
            "aprendizaje", 15),
    Concept("use_entropy_regularization", "No cerrarse en una sola opción",
            "Paga por mantener abiertas varias acciones, en vez de fijarse en la primera que pareció servir.",
            "Se cierra pronto sobre una sola forma de actuar y deja de probar las demás — aunque sea mala.",
            "plasticidad frente a estabilidad", 17),
    Concept("use_factored_action", "Decir qué y decir a qué",
            "Separa la acción en dos decisiones: qué operación hacer y sobre qué dirección hacerla.",
            "Elige entre 25 acciones cerradas sin poder apuntar: acierta el objeto por casualidad.",
            # Corpus block 0 -- meaning NONE. Every other concept here answers to
            # a numbered block of the 64-block map; this one does not, and saying
            # it did would be a fabricated citation. Addressing is not a faculty
            # the corpus describes, it is the CHANNEL through which the others
            # reach the world, and it was broken: the measured addressing rate
            # was chance for every agent including the random one. Block 9 is
            # prediction, not directed intention, and an earlier draft of this
            # line claimed it.
            "intención dirigida · reparación de canal, sin bloque de corpus", 0),
    Concept("use_homeostasis", "Presión de viabilidad",
            "Su energía interna modula cuánto explora: con poca energía se vuelve más urgente.",
            "Explora igual estando lleno que al borde de morir.",
            "viabilidad", 1),
)

#: Numbers, not switches.  They change the organism rather than switching a
#: module off, so a screen must present them apart or someone will read a
#: different threshold as a different reading of the same organism.
TUNINGS: tuple[Mapping[str, Any], ...] = (
    {"key": "entropy_coefficient", "label": "Cuánto paga por no cerrarse",
     "purpose": "El precio que le ponemos a mantenerse indeciso. Alto: prueba de todo y no se "
                "compromete. Cero: equivale a apagar la casilla de arriba.",
     "minimum": 0.0, "maximum": 1.0, "default": DEFAULT_CONFIG["entropy_coefficient"],
     "warning": "No está calibrado. Es una elección científica sin preregistrar, no un valor conocido."},
    {"key": "homeostasis_threshold", "label": "Umbral de necesidad",
     "purpose": "Por debajo de qué nivel de energía el organismo empieza a sentir urgencia.",
     "minimum": 0.0, "maximum": 1.0, "default": DEFAULT_CONFIG["homeostasis_threshold"],
     "warning": "No es el umbral del detector de viabilidad. Cambiar éste cambia el ORGANISMO; "
                "cambiar el del detector cambia sólo cómo lo miramos."},
)

_KEYS = {c.key for c in CONCEPTS}
_TUNING_KEYS = {t["key"] for t in TUNINGS}


def config_for(agent: str) -> Mapping[str, Any]:
    """La configuración que ese organismo lee, resolviendo alias por la factoría.

    Fail-closed ante un agente desconocido: si la factoría no sabe construirlo,
    esto no puede decir qué lee.
    """
    from terrario.agent.agents import _AGENT_IDS
    canonical = _AGENT_IDS.get(agent)
    if canonical is None or canonical not in AGENT_CONFIGS:
        raise CompositionError(
            f"unknown agent {agent!r}; known: {sorted(AGENT_CONFIGS)}")
    return AGENT_CONFIGS[canonical]


def concepts_for(agent: str = DEFAULT_AGENT) -> tuple[Concept, ...]:
    """Los conceptos que ESE organismo lee de verdad.

    Derivado de su configuración, no de una lista: si un concepto deja de
    existir en el agente deja de ofrecerse, y uno que pertenece a otro agente
    no puede colarse.
    """
    config = config_for(agent)
    return tuple(c for c in CONCEPTS if c.key in config)


def catalogue(agent: str = DEFAULT_AGENT) -> Mapping[str, Any]:
    """Everything a screen needs to offer the choice, defaults included."""
    config = config_for(agent)
    offered = concepts_for(agent)
    return {
        "schema_version": CATALOGUE_SCHEMA,
        "agent": agent,
        "concepts": tuple({**c.__dict__, "default": bool(config[c.key])} for c in offered),
        "tunings": TUNINGS,
        "note": (f"Cada concepto es un módulo que existe en el agente {agent}. Que exista no "
                 "demuestra que haga lo que su nombre dice: para eso están los experimentos."),
    }


#: Choices that are not modules and not numbers: the organism's action contract.
#: A concept can be on or off, a tuning has a range, and this has a domain -- so
#: it is validated against an enumerated set rather than squeezed into either.
#: Fail-closed like the rest: an unrecognised mode is refused, never defaulted,
#: because a run that silently fell back to T0 would be reported as a T1 arm.
CHOICES: dict[str, tuple[str, ...]] = {
    "addressing_mode": tuple(m.value for m in IMPLEMENTED_MODES),
}
_CHOICE_KEYS = frozenset(CHOICES)


def validate_selection(selection: Mapping[str, Any] | None,
                       agent: str = DEFAULT_AGENT) -> Mapping[str, Any]:
    """Refuse an unknown or ill-typed key instead of silently dropping it.

    Y también una que es conocida pero **de otro organismo**. Aceptar
    `use_curiosity` para A4 no cambiaba nada y no avisaba, que es precisamente
    el peor modo de fallo que esta pantalla puede tener.
    """
    if not selection:
        return {}
    config = config_for(agent)
    unknown = sorted(set(selection) - _KEYS - _TUNING_KEYS - _CHOICE_KEYS)
    if unknown:
        raise CompositionError(f"unknown agent concept keys: {unknown}")
    ajenas = sorted(k for k in selection if k in _KEYS and k not in config)
    if ajenas:
        duenos = {k: next(c.agent for c in CONCEPTS if c.key == k) for k in ajenas}
        raise CompositionError(
            f"{agent} no lee {ajenas}; pertenecen a "
            f"{sorted(set(duenos.values()))}")
    clean: dict[str, Any] = {}
    for key, value in selection.items():
        if key in _CHOICE_KEYS:
            if value not in CHOICES[key]:
                raise CompositionError(
                    f"{key} must be one of {list(CHOICES[key])}; got {value!r}")
            clean[key] = value
        elif key in _KEYS:
            if not isinstance(value, bool):
                raise CompositionError(f"{key} must be true or false")
            clean[key] = value
        else:
            tuning = next(t for t in TUNINGS if t["key"] == key)
            number = float(value)
            if not tuning["minimum"] <= number <= tuning["maximum"]:
                raise CompositionError(
                    f"{key} must be between {tuning['minimum']} and {tuning['maximum']}")
            clean[key] = number
    return clean


def describe_selection(selection: Mapping[str, Any],
                       agent: str = DEFAULT_AGENT) -> tuple[str, ...]:
    """A plain-language summary of a mix, for the screen and for the trace."""
    config = config_for(agent)
    offered = concepts_for(agent)
    resolved = {**{c.key: bool(config[c.key]) for c in offered}, **dict(selection)}
    on = [c.label for c in offered if resolved.get(c.key)]
    off = [c.label for c in offered if not resolved.get(c.key)]
    lines = [f"Con: {', '.join(on) if on else 'nada'}"]
    if off:
        lines.append(f"Sin: {', '.join(off)}")
    return tuple(lines)
