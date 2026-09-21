"""El pasaporte de una capacidad, y el estado que se calcula en vez de declararse.

TCS-01 fija el pasaporte como la unidad de la campaña: ningún algoritmo entra sin
uno. Veinticuatro campos que responden, para una implementación concreta, de qué
concepto viene, qué significa poseerlo computacionalmente, qué información puede
y no puede ver, qué debería ocurrir al quitarlo, y qué tiene que exigir el mundo
para que sea necesario.

El número estuvo mal desde el primer día y conviene decirlo aquí, porque es
justo lo que este módulo protege: la cabecera decía «veintidós» cuando la
dataclass ya tenía veintitrés --`notes` es texto libre y probablemente no se
contó--, y `operationalization_id` la dejó en veinticuatro sin que nadie
volviera. La autoridad sobre la forma canónica de v1 no es esta frase sino
`V1_FIELDS`, y hay un contrato que la fija literal.

Lo que hace útil al pasaporte no es tenerlo escrito: es que su ESTADO se calcule.
`status_of` no lee un campo `status`, lo deriva de condiciones comprobables --
hay provenance al corpus, la intervención es pura, existe un mundo que lo exige,
el endpoint está calibrado. Un estado que se escribe a mano es una opinión; uno
que se calcula es un gate.

Riesgo conocido y dicho aquí: `instrument_registry.assert_reportable` existe, es
correcto y **no lo llama nada en producción**. Un segundo registro huérfano no
serviría de nada, así que este módulo referencia las claves de
`agent_composition.CONCEPTS` para no poder derivar de ellas en silencio, y
`scripts/passport_check.py` lo hace ejecutable.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from enum import StrEnum
from typing import Any

from terrario.lab.agent_composition import CONCEPTS
from terrario.lab.persistence.canonical import content_hash, plain

SCHEMA_VERSION = "terrario.lab.capability-passport/v1"
#: v2 separates what we supply from what must be acquired, names what cannot be
#: concluded, and points at a versioned mechanism instead of a paragraph.
#:
#: A new version rather than four more fields on v1, and measured before
#: choosing: the ten registered passports declare none of them, so evaluating
#: the separation as a precondition would reclassify 10 of 10 and take the only
#: READY_FOR_CERTIFICATION with it.  A v1 passport therefore keeps its exact
#: historical shape and state; moving one to v2 is an explicit act that mints a
#: new identity, never a silent upgrade of the same record.
SCHEMA_VERSION_V2 = "terrario.lab.capability-passport/v2"
V1_FIELDS: tuple[str, ...] = (
    "concept_id", "corpus_provenance", "operational_definition", "algorithm_id",
    "algorithm_version", "capability_id", "inputs", "outputs", "internal_state",
    "allowed_information", "forbidden_information", "expected_behavior",
    "negative_prediction", "required_world_property", "primary_endpoint",
    "secondary_endpoints", "falsification_controls", "intervention_purity",
    "known_dependencies", "known_confounders", "composition_flag",
    "demanding_world", "notes", "operationalization_id",
)
V2_ONLY_FIELDS: tuple[str, ...] = (
    "supplied", "acquisition_target", "non_claims", "formalization_ref",
)

#: Campos cuya ausencia hace que el pasaporte no exista como contrato. No es la
#: lista entera: `notes` y `secondary_endpoints` pueden estar vacíos sin que el
#: contrato deje de serlo.
MANDATORY = (
    "concept_id", "operational_definition", "algorithm_id", "algorithm_version",
    "capability_id", "inputs", "outputs", "expected_behavior",
    "negative_prediction", "required_world_property", "primary_endpoint",
    "falsification_controls",
)


class ElementKind(StrEnum):
    """Qué clase de cosa es un elemento de `supplied` o de `acquisition_target`.

    Existe para que la separación se compruebe por identidad y no por
    ortografía: `"memory"` y `"episodic_memory"` son cadenas distintas y podrían
    ser la misma cosa, mientras que `(MECHANISM, "onestep-cue-memory")` y
    `(CONTENT, "onestep-cue-memory")` son distintas a propósito -- damos el
    mecanismo, el organismo adquiere su contenido.
    """

    MECHANISM = "MECHANISM"
    CONCEPT = "CONCEPT"
    PARAMETER = "PARAMETER"
    CONTENT = "CONTENT"
    ORGANIZATION = "ORGANIZATION"


@dataclass(frozen=True)
class ElementRef:
    """Una identidad de **entidad**, con su revisión como procedencia.

    Excluir la revisión de `key` no es una comodidad: es la capa en la que este
    tipo vive, y el árbol ya distingue las dos.

        capa de entidad, sin versión
            `concept_id` --declarado sin versión, al lado mismo de
            `algorithm_id` y `algorithm_version`-- y `CorpusConceptReference`

        capa de realización, versionada y NO sustituible
            `algorithm_id` + `algorithm_version`; `InstrumentRef`, que levanta
            `INSTRUMENT_VERSION_DRIFT` en vez de aceptar otra versión; los
            diseños de `theory/factory.py`, inmutables por `(id, version)`;
            `MechanismSpec`, con clave `(mechanism_id, version)`

    `ElementRef` es de la primera y `MechanismRef` de la segunda, y por eso una
    lleva la revisión como dato y la otra la lleva en su identidad.

    La consecuencia buscada: la pregunta «¿lo dimos o debe adquirirlo?» se hace
    de la **entidad**. Dar la versión 1 y exigir que se adquiera la 2 sigue
    siendo dar y pedir lo mismo, porque el organismo recibe la cosa en cualquier
    caso.

    El límite, dicho para que nadie lo generalice de más: esto **no** autoriza a
    sustituir versiones en la capa de realización. Ahí la revisión sí es
    identidad, y cambiarla es deriva.
    """

    kind: ElementKind
    identity: str
    revision: str = ""

    def __post_init__(self) -> None:
        if not str(self.identity).strip():
            raise ValueError("un elemento requiere identidad")

    @property
    def key(self) -> tuple[str, str]:
        return (str(self.kind.value), str(self.identity))


class PassportState(StrEnum):
    """Por qué una capacidad todavía no puede certificarse."""

    SUPPLIED_AND_ACQUIRED_NOT_SEPARATED = "SUPPLIED_AND_ACQUIRED_NOT_SEPARATED"
    PASSPORT_INCOMPLETE = "PASSPORT_INCOMPLETE"
    NO_CORPUS_PROVENANCE = "NO_CORPUS_PROVENANCE"
    INTERVENTION_IMPURE = "INTERVENTION_IMPURE"
    NO_WORLD_DEMANDS_IT = "NO_WORLD_DEMANDS_IT"
    NO_CALIBRATED_ENDPOINT = "NO_CALIBRATED_ENDPOINT"
    READY_FOR_CERTIFICATION = "READY_FOR_CERTIFICATION"


class Purity(StrEnum):
    PURE = "PURE"
    IMPURE = "IMPURE"
    UNMEASURED = "UNMEASURED"


@dataclass(frozen=True)
class CapabilityPassport:
    """Una implementación concreta de un concepto, como candidata experimental.

    Un concepto con tres implementaciones son **tres pasaportes**. Que una falle
    no dice nada del concepto: dice que esa operacionalización, en esa versión,
    bajo ese mundo, no produjo el efecto predicho.
    """

    concept_id: str
    corpus_provenance: tuple[str, ...]
    operational_definition: str
    algorithm_id: str
    algorithm_version: str
    capability_id: str
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    internal_state: tuple[str, ...]
    allowed_information: tuple[str, ...]
    forbidden_information: tuple[str, ...]
    expected_behavior: str
    negative_prediction: str
    required_world_property: str
    primary_endpoint: str
    secondary_endpoints: tuple[str, ...]
    falsification_controls: tuple[str, ...]
    intervention_purity: Purity
    known_dependencies: tuple[str, ...]
    known_confounders: tuple[str, ...]
    #: La bandera de A4 que hoy la enciende. Es deuda declarada, no diseño: una
    #: capacidad no debería ser sinónimo de una bandera interna de un espécimen.
    composition_flag: str | None
    #: Mundo que satisface `required_world_property`, o None si ninguno existe.
    #: No se declara: `register` lo deriva de `world_generator.DEMAND_OF`, y que
    #: el mundo exija de verdad la capacidad lo comprueba
    #: `tests/test_world_generator.py` con oráculos amputados, no este campo.
    demanding_world: str | None
    notes: str = ""
    #: Identificador de una decisión humana en capability_operationalization.
    #: No es una afirmación atribuible al corpus.
    operationalization_id: str | None = None
    #: --- v2 ---------------------------------------------------------------
    #: Declarados al final y con valor vacío, de modo que un pasaporte v1 se
    #: construya y se serialice exactamente como antes de que existieran.
    schema_version: str = SCHEMA_VERSION
    #: El mecanismo o la estructura que NOSOTROS damos.
    supplied: tuple[ElementRef, ...] = ()
    #: El contenido u organización que debe surgir de la experiencia. Si esto
    #: cabe en `supplied`, la capacidad no se está midiendo: se está montando.
    acquisition_target: tuple[ElementRef, ...] = ()
    #: Lo que no se podrá afirmar aunque el experimento salga positivo.
    non_claims: tuple[str, ...] = ()
    #: `MechanismRef` a un `MechanismSpec` registrado. Un párrafo no es
    #: autoridad; una referencia versionada sí.
    formalization_ref: Any | None = None

    def __post_init__(self) -> None:
        if self.composition_flag is not None and self.composition_flag not in {
                concept.key for concept in CONCEPTS}:
            raise ValueError(
                f"{self.capability_id}: la bandera {self.composition_flag!r} no está en "
                f"el catálogo de composición; el pasaporte y el catálogo derivaron")
        if self.schema_version == SCHEMA_VERSION:
            # v1 queda congelado: no puede adquirir semántica v2 por la puerta
            # de atrás, porque entonces su identidad dependería de campos que su
            # versión no declara.
            for name in V2_ONLY_FIELDS:
                if getattr(self, name):
                    raise ValueError(
                        f"{self.capability_id}: {name} es de "
                        f"{SCHEMA_VERSION_V2}; migra el pasaporte en vez de "
                        f"añadirle campos de otra versión")
            return
        if self.schema_version != SCHEMA_VERSION_V2:
            raise ValueError(f"esquema de pasaporte desconocido: {self.schema_version}")
        self._check_v2()

    # ── v2 ───────────────────────────────────────────────────────────────

    def _check_v2(self) -> None:
        falta = [name for name in V2_ONLY_FIELDS if not getattr(self, name)]
        if falta:
            raise ValueError(
                f"{self.capability_id}: {SCHEMA_VERSION_V2} exige {sorted(falta)}")
        dados = {ref.key for ref in self.supplied}
        pedidos = {ref.key for ref in self.acquisition_target}
        comun = dados & pedidos
        if comun:
            # El colapso que borra la pregunta científica: si lo damos y además
            # decimos que debe adquirirse, no hay nada que medir.
            raise ValueError(
                f"{self.capability_id}: {sorted(comun)} aparece a la vez como "
                f"suministrado y como objetivo de adquisición")
        prohibido = {str(x) for x in self.forbidden_information}
        colado = sorted(prohibido & {ref.identity for ref in self.supplied})
        if colado:
            raise ValueError(
                f"{self.capability_id}: {colado} está en forbidden_information y "
                f"aun así se suministra")

    @property
    def is_v2(self) -> bool:
        return self.schema_version == SCHEMA_VERSION_V2

    def separates_supply_from_acquisition(self) -> bool:
        """v1 nunca lo separa, y eso es un hecho sobre su versión, no un defecto.

        Devolver `False` para v1 es lo que permite que `status_of` conserve su
        semántica histórica: la condición sólo se evalúa donde el esquema la
        declara.
        """
        if not self.is_v2:
            return False
        return bool(self.supplied) and bool(self.acquisition_target) and not (
            {r.key for r in self.supplied} & {r.key for r in self.acquisition_target})

    def payload(self) -> dict[str, Any]:
        """Forma canónica. Un pasaporte v1 emite sus campos históricos y nada más.

        Es la condición que hace que añadir v2 no mueva ninguna identidad ya
        existente: los cuatro campos nuevos no aparecen como `null`, no
        aparecen.
        """
        base = {name: plain(getattr(self, name)) for name in V1_FIELDS}
        if not self.is_v2:
            return base
        return {**base, "schema_version": self.schema_version,
                **{name: plain(getattr(self, name)) for name in V2_ONLY_FIELDS}}

    @property
    def content_identity(self) -> str:
        return content_hash(self.payload())

    def missing(self) -> tuple[str, ...]:
        """Campos obligatorios vacíos. Un contrato incompleto no es un contrato."""
        return tuple(name for name in MANDATORY if not getattr(self, name))


def status_of(passport: CapabilityPassport) -> PassportState:
    """El estado se deriva; no se declara.

    El orden es el de las precondiciones: sin contrato no hay nada que juzgar;
    sin procedencia se incumple L-1; con la intervención impura el efecto no es
    atribuible a nadie; sin mundo que lo exija una ablación sin efecto no dice
    nada; y sin instrumento calibrado el número no es reportable.
    """
    if passport.is_v2 and not passport.separates_supply_from_acquisition():
        # Primero porque es la precondición de todo lo demás: sin saber qué
        # dimos y qué debía surgir, un endpoint calibrado mide algo que no
        # sabemos atribuir. Y sólo bajo v2, medido: los diez pasaportes
        # registrados son v1 y evaluarlo en ellos reclasificaría 10 de 10.
        return PassportState.SUPPLIED_AND_ACQUIRED_NOT_SEPARATED
    if passport.missing():
        return PassportState.PASSPORT_INCOMPLETE
    if not passport.corpus_provenance:
        return PassportState.NO_CORPUS_PROVENANCE
    if passport.intervention_purity is not Purity.PURE:
        return PassportState.INTERVENTION_IMPURE
    if passport.demanding_world is None:
        return PassportState.NO_WORLD_DEMANDS_IT
    if not _endpoint_is_reportable(passport.primary_endpoint):
        return PassportState.NO_CALIBRATED_ENDPOINT
    return PassportState.READY_FOR_CERTIFICATION


def _endpoint_is_reportable(metric_id: str) -> bool:
    from terrario.lab import instrument_registry as registry
    return registry.state_of(metric_id) in registry.REPORTABLE_STATES


REGISTRY: dict[str, CapabilityPassport] = {}


def register(passport: CapabilityPassport) -> CapabilityPassport:
    if passport.demanding_world is None:
        from dataclasses import replace
        from terrario.lab.world_generator import demanding_world_id
        passport = replace(passport, demanding_world=demanding_world_id(passport.capability_id))
    if passport.capability_id in REGISTRY:
        raise ValueError(f"pasaporte duplicado: {passport.capability_id}")
    REGISTRY[passport.capability_id] = passport
    return passport


# ── Los pasaportes ───────────────────────────────────────────────────────
#
# Rellenados leyendo el código, no el nombre del módulo. `intervention_purity`
# viene de `scripts/purity_check.py --all`, ejecutado, no supuesto.
#
# `corpus_provenance` queda vacío salvo cuando una decisión humana enlaza una
# capacidad concreta con claims concretos. No es un descuido de redacción:
# `Concept.corpus_block` es un entero que ningún fichero lee, y no existe
# `reference_id`, `claim_id` ni locator en ninguna parte. L-1 está incumplida por
# todas las capacidades del catálogo, y el pasaporte lo hace visible por
# capacidad en vez de como queja general.

register(CapabilityPassport(
    concept_id="REGULACION_HOMEOSTATICA",
    corpus_provenance=("CLM-0056", "CLM-0052", "CLM-0053"),
    operational_definition=(
        "El organismo modula su conducta según el estado de una variable esencial "
        "interna, de modo que la misma observación externa produzca decisiones "
        "distintas según su viabilidad."),
    algorithm_id="HomeostaticState",
    algorithm_version="v1",
    capability_id="HOMEO-A1",
    inputs=("observation.agent_energy",),
    outputs=("exploration_bias", "drive"),
    internal_state=("_energy [0,1]", "_threshold"),
    allowed_information=("su propia energía normalizada",),
    forbidden_information=("energía de otros agentes", "verdad del observador"),
    expected_behavior=(
        "Con energía baja la temperatura de muestreo sube y la política se vuelve "
        "menos determinista; con energía alta se concentra."),
    negative_prediction=(
        "Sin ella la temperatura queda fija en 1.0 y la varianza conductual deja "
        "de depender del estado interno."),
    required_world_property=(
        "Decisiones con compromisos reales entre energía, exploración, riesgo y "
        "oportunidad futura. Un mundo donde siempre convenga lo mismo no la exige."),
    primary_endpoint="PENDIENTE-regulacion-condicionada-al-estado",
    secondary_endpoints=("pasos_vividos", "balance_energia"),
    falsification_controls=("energia_constante_no_modula", "energia_extrema_satura"),
    intervention_purity=Purity.PURE,
    known_dependencies=(),
    known_confounders=(
        "`perceive` asigna `_energy` directamente, así que `update()` sólo alimenta "
        "la traza y nunca se lee para decidir: estado escrito y no leído.",
        "MEDIDO: `drive` se calcula y no lo lee nadie. La única vía a la conducta es "
        "`exploration_bias` → temperatura, que sube el ruido sin dar dirección.",),
    composition_flag="use_homeostasis",
    demanding_world=None,
    notes="Única vía causal: temperatura del muestreo. No toca planner ni pérdida.",
    operationalization_id="OPR-HOMEO-A1-REG-01",
))

register(CapabilityPassport(
    concept_id="MEMORIA_EPISODICA",
    corpus_provenance=(),
    operational_definition=(
        "Retener episodios de experiencia y recuperar los perceptivamente similares "
        "para que entren en la construcción del estado que decide."),
    algorithm_id="EpisodicMemory",
    algorithm_version="v1",
    capability_id="EPMEM-A1",
    inputs=("latent del encoder", "acción", "delta energético", "error de predicción"),
    outputs=("memory_context (128 dims de s_t)",),
    internal_state=("buffer circular de 1000 entradas", "_write_idx"),
    allowed_information=("sus propios episodios",),
    forbidden_information=("episodios de otro organismo", "etiquetas causales del mundo"),
    expected_behavior=(
        "Ante una observación parecida a una vivida, el contexto recuperado desplaza "
        "la decisión hacia lo que funcionó entonces."),
    negative_prediction=(
        "Sin ella 128 de las 640 dimensiones de s_t quedan en cero constante y la "
        "decisión deja de depender de la historia perceptiva."),
    required_world_property=(
        "Un cue en t cuya información sea necesaria en t+k y NO esté observable en "
        "t+k. Si la solución sigue visible durante la decisión, el mundo no la exige."),
    primary_endpoint="PENDIENTE-acierto-condicionado-a-historia-relevante",
    secondary_endpoints=("comidas_efectivas",),
    falsification_controls=("mundo_markoviano_sin_efecto", "cue_oculto_con_efecto"),
    intervention_purity=Purity.PURE,
    known_dependencies=(),
    known_confounders=(
        "La recuperación es sólo por similitud coseno del embedding: el delta "
        "energético y el error de predicción se almacenan y nunca se leen."),
    composition_flag="use_episodic_memory",
    demanding_world=None,
    notes="No es nn.Module: no recibe gradiente. Sobrevive con el aprendizaje apagado.",
))

register(CapabilityPassport(
    concept_id="MEMORIA_PERSISTENTE",
    corpus_provenance=(),
    operational_definition=(
        "Conservar una mezcla continua de experiencia a través de demora e "
        "interferencia, y recuperarla por clave aprendida."),
    algorithm_id="LongTermMemory",
    algorithm_version="v1",
    capability_id="LTMEM-A1",
    inputs=("hidden del núcleo temporal",),
    outputs=("lt_context (128 dims de s_t)",),
    internal_state=("matriz M (64, 128) como nn.Parameter",),
    allowed_information=("su propio estado recurrente",),
    forbidden_information=("verdad del observador",),
    expected_behavior=(
        "Retención a través de demora, interferencia y múltiples eventos: no sólo "
        "almacenó, sino que recuperó y utilizó."),
    negative_prediction=(
        "Sin ella otras 128 dimensiones de s_t quedan en cero y se pierde toda "
        "retención más allá del estado recurrente."),
    required_world_property=(
        "Demora larga con interferencia entre el almacenamiento y el uso."),
    primary_endpoint="PENDIENTE-retencion-tras-interferencia",
    secondary_endpoints=(),
    falsification_controls=("sin_demora_sin_efecto", "demora_con_interferencia_con_efecto"),
    intervention_purity=Purity.PURE,
    known_dependencies=("núcleo temporal: lee `h`, no el latente",),
    known_confounders=(
        "`M` se escribe bajo `no_grad`, así que no la entrena el optimizador; sus "
        "proyecciones sí. Dos mecanismos de cambio en un mismo módulo."),
    composition_flag="use_longterm_memory",
    demanding_world=None,
    notes="Interacción medida con EPMEM-A1: residuo −3.0, sin explicación probada.",
))

register(CapabilityPassport(
    concept_id="APRENDIZAJE_POR_EXPERIENCIA",
    corpus_provenance=("CLM-0127", "CLM-0132"),
    operational_definition=(
        "Modificar parámetros a partir de la consecuencia de la propia acción, de "
        "modo que la conducta futura mejore respecto a la misma demanda."),
    algorithm_id="OnlineLearner",
    algorithm_version="v1",
    capability_id="LEARN-A1",
    inputs=("pérdida del modelo del mundo", "pérdida de política"),
    outputs=("actualización de parámetros",),
    internal_state=("estado Adam", "_step_count"),
    allowed_information=("la consecuencia de su propia acción",),
    forbidden_information=("la regla del mundo", "la consecuencia de acciones no tomadas"),
    expected_behavior=(
        "Una regularidad inicialmente desconocida pero aprendible se adquiere: la "
        "CAPACIDAD se otorga, el CONTENIDO no."),
    negative_prediction=(
        "Sin ella los parámetros quedan en su inicialización y toda mejora "
        "posterior tendría que venir de memoria o de estado recurrente."),
    required_world_property=(
        "Una regla desconocida al inicio y aprendible por experiencia, con "
        "exposición informativa suficiente."),
    primary_endpoint="conversion_aprendizaje",
    secondary_endpoints=("actualizaciones", "cambio_propio"),
    falsification_controls=("non_learning_agent", "oracle_learner"),
    intervention_purity=Purity.PURE,
    known_dependencies=(),
    known_confounders=(
        "Un optimizador único sobre TODOS los módulos: la pérdida de estado de 640 "
        "dims comparte backbone con la de energía de 1 dim. Y hay una actualización "
        "por paso, no por evento informativo: medido 300 actualizaciones y 3 eventos."),
    composition_flag="use_online_learning",
    demanding_world=None,
    notes=(
        "Medido: con 1536 ejemplos informativos PUROS no se separa del azar. El "
        "cuadrante es «ninguna aprende», no «falta exposición»."),
    operationalization_id="OPR-LEARN-A1-RL-01",
))

register(CapabilityPassport(
    concept_id="ESTIMACION_DE_INCERTIDUMBRE",
    corpus_provenance=("CLM-0126", "CLM-0125"),
    operational_definition=(
        "Producir una magnitud CALIBRADA que distinga situaciones familiares, "
        "ambiguas y novedosas, y que modifique la decisión en consecuencia."),
    algorithm_id="UncertaintyEstimator",
    algorithm_version="v1",
    capability_id="UNC-A1",
    inputs=("s_t", "acción one-hot"),
    outputs=("varianza entre 5 cabezas",),
    internal_state=("parámetros de las 5 cabezas",),
    allowed_information=("su propio estado y la acción considerada",),
    forbidden_information=("la consecuencia real antes de actuar",),
    expected_behavior=(
        "Ante observación fuera de distribución la varianza sube y la exploración "
        "se desplaza hacia lo incierto."),
    negative_prediction=(
        "Sin ella los logits dejan de recibir el sesgo de 0.1·varianza y la "
        "exploración deja de depender de la novedad."),
    required_world_property=(
        "Situaciones familiares, ambiguas y novedosas distinguibles entre sí."),
    primary_endpoint="PENDIENTE-calibracion-de-incertidumbre",
    secondary_endpoints=("variedad_conductual",),
    falsification_controls=("familiar_baja", "novedosa_alta", "calibracion_conocida"),
    intervention_purity=Purity.PURE,
    known_dependencies=("modelo del mundo: su pérdida sólo se calcula si existe",),
    known_confounders=(
        "Las 5 cabezas se entrenan con la MISMA pérdida sobre el MISMO objetivo en "
        "cada paso, así que convergen juntas: la varianza mide sobre todo diferencia "
        "de inicialización. No hay calibración conocida ni umbral declarado."),
    composition_flag="use_uncertainty",
    demanding_world=None,
    notes="Cuesta el 43% del tiempo de decisión: 25 acciones × 5 cabezas por paso.",
    operationalization_id="OPR-UNC-A1-NOISE-01"
))

register(CapabilityPassport(
    concept_id="PLASTICIDAD_EXPLORATORIA",
    corpus_provenance=(),
    operational_definition=(
        "Pagar por mantener abiertas varias opciones en vez de fijarse en la primera "
        "que pareció servir, de modo que la política siga muestreando alternativas."),
    algorithm_id="EntropyRegularization",
    algorithm_version="v1",
    capability_id="PLAST-A1",
    inputs=("distribución de política recalculada",),
    outputs=("término añadido a la pérdida de política",),
    internal_state=(),
    allowed_information=("su propia distribución",),
    forbidden_information=("la recompensa de acciones no tomadas",),
    expected_behavior=(
        "La entropía de la política no colapsa; ante un cambio de regla el organismo "
        "conserva el repertorio necesario para re-muestrear la respuesta."),
    negative_prediction=(
        "Sin ella REINFORCE con baseline de media móvil sobre una recompensa que es "
        "el coste por paso apila probabilidad sobre lo que se hizo primero."),
    required_world_property=(
        "Rule_A → Rule_B tras haber aprendido A, para medir resistencia, velocidad de "
        "revisión, olvido, recuperación y nueva estabilización."),
    primary_endpoint="PENDIENTE-velocidad-de-revision-tras-inversion",
    secondary_endpoints=("indecision_media", "colapso_politica"),
    falsification_controls=("sin_inversion_sin_efecto", "inversion_con_revision"),
    intervention_purity=Purity.PURE,
    known_dependencies=("aprendizaje online: es un término de su pérdida",),
    known_confounders=(
        "Es el único candidato que NO es un módulo sino un término. Su ablación no "
        "mueve ningún conteo de invocación, así que `purity_check` la declara pura "
        "por construcción: no puede detectar impureza de pérdida."),
    composition_flag="use_entropy_regularization",
    demanding_world=None,
    notes=(
        "Se registra como candidato de plasticidad SIN asumir equivalencia "
        "conceptual: que regularice entropía no demuestra que sea plasticidad."),
))

register(CapabilityPassport(
    concept_id="INTEGRACION_TEMPORAL",
    corpus_provenance=(),
    operational_definition=(
        "Mantener un estado que integre la historia de observaciones, de modo que "
        "P(y|x_{1:t}) sea distinguible de P(y|x_t)."),
    algorithm_id="SSMCore",
    algorithm_version="v1",
    capability_id="TEMP-A1",
    inputs=("latente del encoder (128)",),
    outputs=("h (256 dims de s_t)",),
    internal_state=("h", "a diagonal", "B", "C"),
    allowed_information=("su propia secuencia de observaciones",),
    forbidden_information=("observaciones futuras",),
    expected_behavior=(
        "En una tarea donde el presente es ambiguo y la historia la desambigua, la "
        "conducta correcta aparece."),
    negative_prediction=(
        "Sin él h queda en ceros: 256 de 640 dimensiones constantes, y toda "
        "dependencia de secuencia desaparece."),
    required_world_property=(
        "P(y|x_t) insuficiente: la respuesta correcta debe depender de x_{1:t}."),
    primary_endpoint="PENDIENTE-desambiguacion-por-historia",
    secondary_endpoints=(),
    falsification_controls=("markoviano_sin_efecto", "ambiguo_con_efecto"),
    intervention_purity=Purity.PURE,
    known_dependencies=(),
    known_confounders=(
        "Sin BPTT: el hidden se detach cada paso, así que sólo aprende a través de "
        "la pérdida de un paso."),
    composition_flag="use_temporal",
    demanding_world=None,
    notes=(
        "CONDICIONAL: entra sólo si el corpus le asigna un constructo explícito. "
        "«Integración temporal» todavía no está normalizado como concepto."),
))

register(CapabilityPassport(
    concept_id="MODELO_PREDICTIVO_DEL_MUNDO",
    corpus_provenance=("CLM-0116", "CLM-0117"),
    operational_definition=(
        "Predecir consecuencias relevantes de una acción antes de tomarla, con "
        "error medible contra el resultado real."),
    algorithm_id="WorldModel",
    algorithm_version="v1",
    capability_id="WM-A1",
    inputs=("s_t (640)", "acción one-hot (25)"),
    outputs=("next_state (640)", "energy (1)", "done (1)"),
    internal_state=("backbone compartido y tres cabezas",),
    allowed_information=("su propio estado y la acción considerada",),
    forbidden_information=("la consecuencia real antes de que ocurra",),
    expected_behavior=(
        "En transiciones que dependen de (estado, acción) y no se resuelven por "
        "reacción instantánea, la predicción anticipa el resultado."),
    negative_prediction=(
        "Sin él desaparece toda anticipación y el planner queda sin puntuación."),
    required_world_property=(
        "Transiciones dependientes de (estado, acción), no resolubles por reacción."),
    primary_endpoint="examen_prediccion",
    secondary_endpoints=(),
    falsification_controls=("exam_oracle", "exam_anti_oracle", "exam_tie"),
    intervention_purity=Purity.IMPURE,
    known_dependencies=(),
    known_confounders=(
        "MEDIDO: `use_world_model=False` desactiva el planner por completo (40 "
        "invocaciones → 0) y desvía conducta a policy_head (97 → 120). Comparten "
        "intervención. Y la pérdida de estado de 640 dims comparte backbone con la "
        "de energía de 1 dim."),
    composition_flag="use_world_model",
    demanding_world=None,
    notes=(
        "BLOQUEADA. Medido: tras 600 pasos `energy_head` tiene dispersión 0.0037 "
        "sobre una cantidad que varía 2.0 — indistinguible de su valor al nacer."),
    operationalization_id="OPR-WM-A1-REPR-01"
))

register(CapabilityPassport(
    concept_id="PLANIFICACION_ANTICIPATORIA",
    corpus_provenance=(),
    operational_definition=(
        "Evaluar secuencias de acción antes de actuar y elegir la primera de la "
        "mejor, de modo que la acción localmente atractiva pueda descartarse."),
    algorithm_id="Planner",
    algorithm_version="v1-random-shooting",
    capability_id="PLAN-A1",
    inputs=("s_t", "modelo del mundo"),
    outputs=("una acción entera del espacio plano de 25",),
    internal_state=(),
    allowed_information=("su propio estado y su modelo",),
    forbidden_information=("la transición real del mundo",),
    expected_behavior=(
        "Donde acción localmente atractiva ≠ secuencia globalmente favorable, elige "
        "la segunda."),
    negative_prediction=(
        "Sin él toda decisión sale de la política; con él, la mitad."),
    required_world_property=(
        "Un problema donde el óptimo local difiera del óptimo de secuencia."),
    primary_endpoint="PENDIENTE-eleccion-no-miope",
    secondary_endpoints=(),
    falsification_controls=("sin_trampa_local_sin_efecto", "con_trampa_local_con_efecto"),
    intervention_purity=Purity.IMPURE,
    known_dependencies=("modelo del mundo: la rama exige AMBOS flags",),
    known_confounders=(
        "MEDIDO: su ablación desvía conducta a policy_head (97 → 120), porque sin "
        "él cada decisión muestrea de la política en vez de la mitad de las veces."),
    composition_flag="use_planner",
    demanding_world=None,
    notes=(
        "BLOQUEADA. Es random shooting: 10 secuencias aleatorias de 5 pasos "
        "puntuadas por un modelo que no predice. Medido, la puntuación la domina la "
        "cabeza de terminación (2.4× la de energía), ambas ruido. Funciona como "
        "fuente de exploración, no como planificación — L-2 en acto."),
))


register(CapabilityPassport(
    concept_id="MOTIVACION_INTRINSECA",
    corpus_provenance=("CLM-0121", "CLM-0122", "CLM-0123"),
    operational_definition=(
        "Convertir el error al predecir la consecuencia de la propia acción en una señal "
        "de valor que entra en la selección de acción, de modo que el organismo tenga "
        "motivo para actuar cuando ninguna recompensa externa se lo da."),
    algorithm_id="IntrinsicPredictionError",
    algorithm_version="v1",
    capability_id="CURIO-A1",
    inputs=("prediccion de consecuencia", "consecuencia observada"),
    outputs=("senal intrinseca de valor",),
    internal_state=("error de prediccion del paso anterior",),
    allowed_information=("su propia prediccion", "la consecuencia que efectivamente ocurrio"),
    forbidden_information=(
        "donde estan las entidades favorables",
        "el canal oculto que decide la consecuencia",
        "cualquier cosa que haga la senal dependiente del mapeo a aprender"),
    expected_behavior=(
        "Con recompensa externa escasa, visita mas estados cuya consecuencia predice peor "
        "que un organismo identico sin la senal."),
    negative_prediction=(
        "Sin ella el organismo no tiene direccion: su unica presion es la temperatura "
        "homeostatica, que aumenta el ruido sin orientarlo. MEDIDO en A4: recorre 2 "
        "columnas de 34 y alcanza 1 estacion de 8 antes de morir de inanicion."),
    required_world_property=(
        "Recompensa externa escasa o ausente, y estados cuya consecuencia el organismo "
        "aun no predice bien. Un mundo que paga en cada paso no la exige."),
    primary_endpoint="PENDIENTE-exploracion-dirigida-por-error",
    secondary_endpoints=("estaciones alcanzadas", "columnas recorridas"),
    falsification_controls=(
        "senal_constante_no_dirige",
        "senal_invertida_reduce_exploracion",
        "ruido_incontrolable_no_la_satura"),
    intervention_purity=Purity.UNMEASURED,
    known_dependencies=(
        "modelo del mundo: sin prediccion no hay error de prediccion",),
    known_confounders=(
        "CLM-0126: predecir directamente puede mantener el error alto por factores "
        "incontrolables, y CLM-0125 (dinamica inversa) es lo que lo reduce. A4 no la "
        "implementa, asi que el confusor queda declarado y NO resuelto.",
        "UNC-A1 ya consume senal con forma de error de prediccion y ya posee el eje "
        "`novelty`. La superficie de intervencion se solapa y hay que separarla antes "
        "de atribuir nada.",
        "Trampa de pureza: si se implementa como termino sumado a los logits en vez de "
        "como modulo, `purity_check` la declarara PURE por construccion y el gate pasara "
        "en vacio."),
    composition_flag="use_curiosity",
    demanding_world=None,
    notes=(
        "A4 YA calcula `last_prediction_error` en learn() y lo entrega solo al observador. "
        "El organo existe y esta cableado a la libreta en vez de a la conducta; esta "
        "capacidad es cerrar ese lazo, no anadir uno nuevo."),
    operationalization_id="OPR-CURIO-A1-PE-01",
))


# ── v1 → v2 · una migración explícita, nunca una actualización silenciosa ──

class NonClaimViolation(ValueError):
    """Se intentó tratar como afirmación algo declarado fuera de alcance."""

    code = "NON_CLAIM_PROMOTED"


def migrate_to_v2(passport: CapabilityPassport, *, capability_id: str,
                  supplied: tuple[ElementRef, ...],
                  acquisition_target: tuple[ElementRef, ...],
                  non_claims: tuple[str, ...],
                  formalization_ref: Any) -> CapabilityPassport:
    """Deriva un pasaporte v2 a partir de uno v1, con identidad nueva.

    Exige `capability_id` distinto a propósito. Migrar en el sitio dejaría dos
    significados bajo un identificador —el que se certificó y el que ahora
    separa suministro de adquisición— y es exactamente el colapso que este
    esquema existe para impedir, cometido sobre el pasaporte en vez de sobre la
    capacidad.
    """
    from dataclasses import replace

    if capability_id == passport.capability_id:
        raise ValueError(
            "migrar a v2 cambia lo que el pasaporte afirma; dale un "
            "capability_id propio en vez de reescribir el que ya se evaluó")
    derivado = replace(
        passport, capability_id=capability_id, schema_version=SCHEMA_VERSION_V2,
        supplied=supplied, acquisition_target=acquisition_target,
        non_claims=non_claims, formalization_ref=formalization_ref,
        # La procedencia al corpus NO se hereda, y esto lo destapó la prueba de
        # `capability_operationalization`: el registro es una decisión humana
        # que nombra un `capability_id` concreto, y arrastrarlo haría que el
        # pasaporte nuevo reclamara un enlace que no lo nombra. Es exactamente
        # la procedencia inventada que esta migración existe para no cometer.
        # El v2 nace sin enlace y lo gana cuando una persona decida para él.
        corpus_provenance=(), operationalization_id=None)
    if derivado.content_identity == passport.content_identity:
        raise ValueError("la migración no produjo una identidad nueva")
    return derivado


def assert_claimable(passport: CapabilityPassport, claim: str) -> str:
    """Los dientes de `non_claims`: una conclusión excluida no vuelve por la puerta.

    Almacenar la lista no impide nada. Lo que impide algo es que exista un punto
    por el que toda afirmación atribuida a esta capacidad tenga que pasar, y que
    ese punto se niegue. Comparación sin distinguir mayúsculas ni espacios de
    borde, porque la exclusión la escribe una persona y la afirmación la escribe
    otra, a veces meses después.
    """
    normal = " ".join(str(claim).split()).casefold()
    if not normal:
        raise ValueError("una afirmación vacía no es una afirmación")
    for excluido in passport.non_claims:
        if " ".join(str(excluido).split()).casefold() == normal:
            raise NonClaimViolation(
                f"{passport.capability_id}: {claim!r} está declarado fuera de "
                f"alcance en non_claims y no puede afirmarse de esta capacidad")
    return claim


# ── El primer pasaporte v2, migrado desde uno productivo ─────────────────
#
# LEARN-A1 es el único de los diez que puede poblar los cuatro campos sin
# inferencias: auditados los diez, sólo él y WM-A1 tienen un endpoint que
# resuelve a un `MetricSpec` con alcance declarado, y WM-A1 es
# INTERVENTION_IMPURE --su efecto no es atribuible a nadie--.
#
# El v1 no se toca. Éste es otro pasaporte, con su propio identificador, y los
# dos coexisten: el que se evaluó y el que además separa lo dado de lo que debe
# adquirirse.

def _learn_a1_v2() -> CapabilityPassport:
    from terrario.lab.mechanism_spec import MechanismRef, REGISTRY as MECHANISMS

    origen = REGISTRY["LEARN-A1"]
    mecanismo = MECHANISMS[("online-gradient-update", 1)]
    return migrate_to_v2(
        origen,
        capability_id="LEARN-A1-V2",
        # VERIFIED_FROM_CODE · el mecanismo entero lo escribimos nosotros:
        # `OnlineLearner` construye el Adam sobre los módulos aprendibles.
        supplied=(
            ElementRef(ElementKind.MECHANISM, "online-gradient-update", "1"),
            ElementRef(ElementKind.PARAMETER, "learning-rate"),
            ElementRef(ElementKind.PARAMETER, "gradient-clip"),
            ElementRef(ElementKind.PARAMETER, "update-frequency"),
        ),
        # VERIFIED_FROM_EXPERIMENT · `experiment_capability_acquisition.py`
        # aísla exactamente esto: los gemelos L y F reciben experiencia
        # LITERALMENTE idéntica y sólo difieren en si el update ocurre, y S
        # --crédito barajado-- pregunta si lo aprendido es la relación causal.
        acquisition_target=(
            ElementRef(ElementKind.CONTENT, "parameter values of the learnable modules"),
        ),
        # VERIFIED_FROM_CODE · el alcance que el propio instrumento declara:
        # `MetricSpec.semantic_definition` lo acota a un segmento de regla
        # estable, y su `notes` separa el cero de NOT_EVALUABLE.
        non_claims=(
            "that the organism learns across a change of rules; the endpoint "
            "measures discrimination inside a stable-rule segment",
            "that a reading of zero means no learning; zero means exposures "
            "existed and none converted, and with no exposures the reading is "
            "NOT_EVALUABLE",
            "that the parameter change is the organism understanding anything",
        ),
        formalization_ref=MechanismRef.to(mecanismo),
    )


register(_learn_a1_v2())
