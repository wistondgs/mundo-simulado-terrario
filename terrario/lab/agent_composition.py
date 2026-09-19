"""What the organism can be made of, in words a person can choose from.

The A4 lineage carries switches that turn modules on and off.  Each one is a
corpus concept made algorithm, and until this catalogue existed none of them
could be reached: the lab contract carried an agent *id* and nothing else, so
every screen could name an architecture and none could compose one.

The catalogue lives here rather than in the page because a description that
drifts from the code is worse than no description.  `key` is the literal
config key an agent reads, so a concept that stops existing stops being
offerable, and `validate_selection` refuses an unknown key instead of ignoring
it -- a misspelling that silently changes nothing is the worst failure mode a
composition screen can have.

**Whose catalogue this is.**  It used to be A4's: every default was resolved
against `a4_advanced.DEFAULT_CONFIG`, which quietly made "a concept the
organism can be made of" mean "a key this one specimen happens to carry".  A5
broke that reading by existing.  A5 is A4's descendant and differs in exactly
one faculty -- `use_curiosity` -- so under the old reading the one thing that
makes A5 an organism of its own was the one thing the lab could not compose.
Refusing the concept would have been worse: it would have deleted the ablation
that CURIO-A1's passport declares as its own falsification control.

So the catalogue is of the LINEAGE, not of a specimen.  `introduced_by` names
the architecture that introduces the key; descendants read what their ancestor
reads, which is a fact about the class hierarchy and not a second list to
maintain.  The default is still never restated here -- it is read from the
default config of the architecture that introduces it, so the anti-drift
property that made the catalogue reach into A4 survives, pointed at the right
agent.

**And composing is per-agent.**  A catalogue that offers everything to
everyone would hand an A4 a curiosity switch that changes nothing, which is
the failure this module exists to prevent, one level up.  `catalogue` and
`validate_selection` therefore take an agent reference: what that organism
does not read is not offered, and if it is asked for anyway it is refused
rather than accepted and dropped.

`purpose` answers "what is this for", in one sentence, without jargon.
`without_it` answers the question a person actually asks when deciding whether
to switch something off.  Neither claims the module works: `block` points at
the concept in the map, and whether the implementation earns the name is what
the experiments are for.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from terrario.agent.agents import architecture_id
from terrario.agent.agents.a4_advanced import DEFAULT_CONFIG as A4_DEFAULT_CONFIG
from terrario.agent.agents.a5_cybernetic import DEFAULT_CONFIG as A5_DEFAULT_CONFIG
from terrario.core.action_contract import IMPLEMENTED_MODES

CATALOGUE_SCHEMA = "terrario.lab.agent-composition/v2"


@dataclass(frozen=True)
class Concept:
    key: str
    label: str
    purpose: str
    without_it: str
    block: str
    corpus_block: int
    #: Architecture that introduces the key.  Its descendants read it too; no
    #: ancestor does.  It is declared rather than searched for because "which
    #: organism is this a faculty of" is a claim, and a claim gets an author.
    introduced_by: str


class CompositionError(ValueError):
    code = "AGENT_COMPOSITION_ERROR"


#: The default configuration of each architecture that has one, which is what
#: `introduced_by` resolves against.  Nothing is copied out of these dicts into
#: the catalogue: a default restated here is a default that can drift.
DEFAULTS_OF: Mapping[str, Mapping[str, Any]] = {
    "A4_ADVANCED": A4_DEFAULT_CONFIG,
    "A5_CYBERNETIC": A5_DEFAULT_CONFIG,
}

#: What each architecture actually reads from the configuration it is handed.
#:
#: For the A4 lineage this is not a list but the specimen's own default config,
#: so it cannot fall behind the code.  A0 is written out because it has no
#: default config: the factory hands it exactly one value
#: ([agents/__init__.py:96](terrario/agent/agents/__init__.py:96)).  A1, A2 and
#: A3 read NOTHING -- their constructors take explicit arguments and the
#: factory forwards no composition key to them -- so composing one of them is
#: refused, not quietly ignored.  An empty set here is a measured fact about
#: those agents, not a gap waiting to be filled.
READS: Mapping[str, frozenset[str]] = {
    "A0_RANDOM": frozenset({"addressing_mode"}),
    "A1_REACTIVE": frozenset(),
    "A2_GRU": frozenset(),
    "A3_WORLD_MODEL": frozenset(),
    "A4_ADVANCED": frozenset(A4_DEFAULT_CONFIG),
    "A5_CYBERNETIC": frozenset(A5_DEFAULT_CONFIG),
}


#: Ordered as the organism processes: it perceives, remembers, models,
#: doubts, plans, regulates, and changes.  The order is the reading order of
#: the screen, not a claim about the architecture.
CONCEPTS: tuple[Concept, ...] = (
    Concept("use_temporal", "Memoria del momento",
            "Recuerda lo que acaba de pasar, para que una decisión pueda depender de los pasos anteriores y no sólo de lo que ve ahora.",
            "Cada paso se decide como si fuera el primero.",
            "dinámica temporal", 4, "A4_ADVANCED"),
    Concept("use_episodic_memory", "Memoria de episodios",
            "Guarda situaciones concretas que vivió y las vuelve a encontrar cuando se parece la actual.",
            "Puede repetir el mismo error sin reconocer que ya lo vivió.",
            "memoria episódica", 4, "A4_ADVANCED"),
    Concept("use_longterm_memory", "Memoria a largo plazo",
            "Acumula lo aprendido a lo largo de toda la vida del organismo, no sólo del episodio en curso.",
            "Lo aprendido se pierde al terminar el episodio.",
            "memoria persistente", 4, "A4_ADVANCED"),
    Concept("use_world_model", "Modelo del mundo",
            "Predice qué va a pasar si actúa, en vez de descubrirlo sólo actuando.",
            "Sólo aprende por consecuencia consumada.",
            "modelo del mundo", 8, "A4_ADVANCED"),
    Concept("use_uncertainty", "Estimación de incertidumbre",
            "Calcula cuánta confianza tiene en su propia predicción.",
            "Trata por igual lo que sabe bien y lo que apenas conoce.",
            "incertidumbre", 38, "A4_ADVANCED"),
    # El único concepto que A4 no lee. Lo introduce A5, que es A4 más esta
    # faculty y nada más, así que ofrecerlo sobre un A4 sería ofrecer un
    # interruptor desconectado -- y quitarlo del catálogo sería borrar la
    # ablación que el pasaporte de CURIO-A1 declara como su propio control de
    # falsación. Por eso el catálogo es del linaje y la oferta es por agente.
    Concept("use_curiosity", "Curiosidad",
            "Convierte el error de su propia predicción en motivo para actuar.",
            "Sólo se mueve si algo externo le paga; sin pago externo, no tiene hacia dónde.",
            "exploración", 28, "A5_CYBERNETIC"),
    Concept("use_planner", "Planificación",
            "Imagina varias secuencias de acciones y compara sus consecuencias antes de moverse.",
            "Actúa paso a paso, sin anticipar la secuencia.",
            "planificación", 27, "A4_ADVANCED"),
    Concept("use_online_learning", "Aprendizaje en marcha",
            "Cambia sus parámetros durante la propia vida, no sólo entre corridas.",
            "Queda congelado: hará lo mismo al principio y al final.",
            "aprendizaje", 15, "A4_ADVANCED"),
    Concept("use_entropy_regularization", "No cerrarse en una sola opción",
            "Paga por mantener abiertas varias acciones, en vez de fijarse en la primera que pareció servir.",
            "Se cierra pronto sobre una sola forma de actuar y deja de probar las demás — aunque sea mala.",
            "plasticidad frente a estabilidad", 17, "A4_ADVANCED"),
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
            "intención dirigida · reparación de canal, sin bloque de corpus", 0, "A4_ADVANCED"),
    Concept("use_homeostasis", "Presión de viabilidad",
            "Su energía interna modula cuánto explora: con poca energía se vuelve más urgente.",
            "Explora igual estando lleno que al borde de morir.",
            "viabilidad", 1, "A4_ADVANCED"),
)

#: Numbers, not switches.  They change the organism rather than switching a
#: module off, so a screen must present them apart or someone will read a
#: different threshold as a different reading of the same organism.
#:
#: A5's `curiosity_scale` and `curiosity_floor_decay` are deliberately NOT
#: here.  A tuning needs a range, and no calibrated range for them exists;
#: inventing a minimum and a maximum so the screen looks complete would be
#: fabricating the one thing a person reads off it.  They are reachable as
#: configuration -- that is what putting them in A5's default config bought --
#: and they become offerable the day someone measures a range.
TUNINGS: tuple[Mapping[str, Any], ...] = (
    {"key": "entropy_coefficient", "label": "Cuánto paga por no cerrarse",
     "purpose": "El precio que le ponemos a mantenerse indeciso. Alto: prueba de todo y no se "
                "compromete. Cero: equivale a apagar la casilla de arriba.",
     "minimum": 0.0, "maximum": 1.0, "default": A4_DEFAULT_CONFIG["entropy_coefficient"],
     "introduced_by": "A4_ADVANCED",
     "warning": "No está calibrado. Es una elección científica sin preregistrar, no un valor conocido."},
    {"key": "homeostasis_threshold", "label": "Umbral de necesidad",
     "purpose": "Por debajo de qué nivel de energía el organismo empieza a sentir urgencia.",
     "minimum": 0.0, "maximum": 1.0, "default": A4_DEFAULT_CONFIG["homeostasis_threshold"],
     "introduced_by": "A4_ADVANCED",
     "warning": "No es el umbral del detector de viabilidad. Cambiar éste cambia el ORGANISMO; "
                "cambiar el del detector cambia sólo cómo lo miramos."},
)

_KEYS = {c.key for c in CONCEPTS}
_TUNING_KEYS = {t["key"] for t in TUNINGS}


def architecture_of(agent_reference: str) -> str:
    """The architecture a reference names, refusing one no agent answers to.

    Fail-closed like the rest: validating a mix against an agent that does not
    exist would either pass everything or refuse everything, and both are a
    wrong answer dressed as an answer.
    """
    architecture = architecture_id(agent_reference)
    if architecture is None:
        raise CompositionError(f"no agent answers to {agent_reference!r}")
    if architecture not in READS:
        raise CompositionError(
            f"{architecture} does not declare what it reads; add it to READS "
            f"before composing it")
    return architecture


def keys_read_by(agent_reference: str) -> frozenset[str]:
    """Which composition keys actually reach the organism that reference names."""
    return READS[architecture_of(agent_reference)]


def default_of(concept: Concept, architecture: str | None = None) -> bool:
    """What this concept ships as, on the organism that carries it."""
    return bool(DEFAULTS_OF[architecture or concept.introduced_by][concept.key])


def concepts_for(agent_reference: str | None = None) -> tuple[Concept, ...]:
    """The concepts one organism can be made of, or all of them if none is named."""
    if agent_reference is None:
        return CONCEPTS
    readable = keys_read_by(agent_reference)
    return tuple(c for c in CONCEPTS if c.key in readable)


def catalogue(agent_reference: str | None = None) -> Mapping[str, Any]:
    """Everything a screen needs to offer the choice, defaults included.

    Name the agent and only what it reads is offered, with that agent's own
    defaults.  Name nobody and the whole lineage comes back, each concept
    carrying the architecture that introduces it -- which is the honest answer
    to "what can an organism here be made of", and not an offer to any one
    specimen.
    """
    architecture = architecture_of(agent_reference) if agent_reference else None
    readable = READS[architecture] if architecture else None
    concepts = concepts_for(agent_reference)
    return {
        "schema_version": CATALOGUE_SCHEMA,
        "agent_reference": agent_reference,
        "architecture": architecture,
        "concepts": tuple({**c.__dict__, "default": default_of(c, architecture)}
                          for c in concepts),
        "tunings": tuple(t for t in TUNINGS if readable is None or t["key"] in readable),
        "note": ("Cada concepto es un módulo que existe en el organismo que lo declara. Que "
                 "exista no demuestra que haga lo que su nombre dice: para eso están los "
                 "experimentos."),
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
                       agent_reference: str | None = None) -> Mapping[str, Any]:
    """Refuse an unknown, ill-typed or unreachable key instead of dropping it.

    With an agent named, a key that agent does not read is refused on the same
    grounds as a misspelling: both are a choice a person made that the organism
    will never see.  Callers that do not know which organism they are composing
    keep the lineage-wide check they had.
    """
    if not selection:
        return {}
    unknown = sorted(set(selection) - _KEYS - _TUNING_KEYS - _CHOICE_KEYS)
    if unknown:
        raise CompositionError(f"unknown agent concept keys: {unknown}")
    if agent_reference is not None:
        architecture = architecture_of(agent_reference)
        deaf = sorted(set(selection) - READS[architecture])
        if deaf:
            raise CompositionError(
                f"{architecture} does not read {deaf}: composing it would change nothing")
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
                       agent_reference: str | None = None) -> tuple[str, ...]:
    """A plain-language summary of a mix, for the screen and for the trace."""
    architecture = architecture_of(agent_reference) if agent_reference else None
    concepts = concepts_for(agent_reference)
    resolved = {**{c.key: default_of(c, architecture) for c in concepts}, **dict(selection)}
    on = [c.label for c in concepts if resolved.get(c.key)]
    off = [c.label for c in concepts if not resolved.get(c.key)]
    lines = [f"Con: {', '.join(on) if on else 'nada'}"]
    if off:
        lines.append(f"Sin: {', '.join(off)}")
    return tuple(lines)
