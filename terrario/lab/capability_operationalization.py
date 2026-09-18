"""Human-approved bridges from capabilities to immutable corpus claims.

This registry is not corpus data.  It records a Terrario human decision and
keeps source claims, the operational projection, algorithm, implementation,
and endpoint as separate typed layers.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import csv
import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping

from terrario.lab.persistence.canonical import content_hash


SCHEMA_VERSION = "terrario.lab.capability-operationalization/v1"
DECISION_STATUS = "HUMAN_OPERATIONALIZATION"
SNAPSHOT_ID = "theory-f59dbb6d6ee3850c"
SNAPSHOT_HASH = "f59dbb6d6ee3850c7fa366f087f51f0a0dc69d8ef2ea973e33ad8681eb692b68"
SNAPSHOT_MANIFEST_SHA256 = "44cac69a0fa6e6f057881365de2f95bdd1d95c4aaa94e245061e9fe92ee7de98"


def snapshot_root() -> Path:
    return Path(__file__).resolve().parents[2] / "theory_snapshots" / SNAPSHOT_ID


@dataclass(frozen=True)
class CorpusClaimReference:
    """An exact claim/source/locator address within an immutable snapshot."""

    claim_id: str
    source_id: str
    locator: str
    claim_artifact: str
    claim_artifact_sha256: str
    source_artifact: str
    source_artifact_sha256: str
    snapshot_id: str = SNAPSHOT_ID
    snapshot_hash: str = SNAPSHOT_HASH
    snapshot_manifest_sha256: str = SNAPSHOT_MANIFEST_SHA256

    def validate(self, root: str | Path | None = None) -> None:
        root = Path(root) if root is not None else snapshot_root()
        manifest_path = root / "snapshot_manifest.json"
        if not manifest_path.is_file():
            raise ValueError("corpus snapshot is unavailable")
        if hashlib.sha256(manifest_path.read_bytes()).hexdigest() != self.snapshot_manifest_sha256:
            raise ValueError("corpus snapshot manifest hash mismatch")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if (manifest.get("snapshot_id"), manifest.get("snapshot_hash")) != (
                self.snapshot_id, self.snapshot_hash):
            raise ValueError("corpus snapshot identity mismatch")
        artifacts = {item["filename"]: item["sha256"] for item in manifest.get("artifacts", ())}
        if artifacts.get(self.claim_artifact) != self.claim_artifact_sha256:
            raise ValueError("claim artifact hash mismatch")
        if artifacts.get(self.source_artifact) != self.source_artifact_sha256:
            raise ValueError("source artifact hash mismatch")
        with (root / self.claim_artifact).open(encoding="utf-8-sig", newline="") as stream:
            claim = next((row for row in csv.DictReader(stream)
                          if row.get("claim_id") == self.claim_id), None)
        if claim is None:
            raise ValueError("unknown claim id")
        if f"[{self.source_id}]" not in claim.get("fuente", ""):
            raise ValueError("claim does not resolve to declared source")
        if claim.get("pagina_seccion") != self.locator:
            raise ValueError("claim locator mismatch")
        if self.source_id not in (root / self.source_artifact).read_text(encoding="utf-8"):
            raise ValueError("unknown source id")


@dataclass(frozen=True)
class HumanOperationalization:
    """Approved projection; its fields are never attributed to the source."""

    decision_id: str
    scope: str
    excluded_scope: tuple[str, ...]
    conceptual_property: str
    observable_property: str
    possible_intervention: str
    status: str = DECISION_STATUS

    def __post_init__(self) -> None:
        required = (self.decision_id, self.scope, self.conceptual_property,
                    self.observable_property, self.possible_intervention)
        if self.status != DECISION_STATUS or not all(required):
            raise ValueError("human operationalization must be explicit and complete")


@dataclass(frozen=True)
class AlgorithmBinding:
    algorithm_id: str
    algorithm_version: str


@dataclass(frozen=True)
class ImplementationBinding:
    implementation_id: str


@dataclass(frozen=True)
class EndpointBinding:
    endpoint_id: str


@dataclass(frozen=True)
class OperationalizationRecord:
    operationalization_id: str
    capability_id: str
    primary_claim: CorpusClaimReference
    supporting_claims: tuple[CorpusClaimReference, ...]
    human_operationalization: HumanOperationalization
    algorithm: AlgorithmBinding
    implementation: ImplementationBinding
    endpoint: EndpointBinding

    def __post_init__(self) -> None:
        if not self.operationalization_id or not self.capability_id:
            raise ValueError("operationalization requires identifiers")
        if not self.supporting_claims:
            raise ValueError("operationalization requires an explicit supporting claim")
        if len(set(self.claim_ids)) != len(self.claim_ids):
            raise ValueError("duplicate claim in operationalization")

    @property
    def claim_ids(self) -> tuple[str, ...]:
        return (self.primary_claim.claim_id,
                *(item.claim_id for item in self.supporting_claims))

    @property
    def semantic_id(self) -> str:
        return "OPERATIONALIZATION-" + content_hash(self._payload())[:16]

    def _payload(self) -> dict:
        return {
            "operationalization_id": self.operationalization_id,
            "capability_id": self.capability_id,
            "primary_claim": asdict(self.primary_claim),
            "supporting_claims": [asdict(item) for item in self.supporting_claims],
            "human_operationalization": asdict(self.human_operationalization),
            "algorithm": asdict(self.algorithm),
            "implementation": asdict(self.implementation),
            "endpoint": asdict(self.endpoint),
        }

    def payload(self) -> dict:
        return {"schema": SCHEMA_VERSION, **self._payload(), "semantic_id": self.semantic_id}

    @classmethod
    def from_payload(cls, payload: Mapping) -> "OperationalizationRecord":
        if payload.get("schema") != SCHEMA_VERSION:
            raise ValueError("unsupported operationalization schema")
        try:
            record = cls(
                operationalization_id=payload["operationalization_id"],
                capability_id=payload["capability_id"],
                primary_claim=CorpusClaimReference(**payload["primary_claim"]),
                supporting_claims=tuple(CorpusClaimReference(**item) for item in payload["supporting_claims"]),
                human_operationalization=HumanOperationalization(**payload["human_operationalization"]),
                algorithm=AlgorithmBinding(**payload["algorithm"]),
                implementation=ImplementationBinding(**payload["implementation"]),
                endpoint=EndpointBinding(**payload["endpoint"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("invalid operationalization payload") from exc
        if payload.get("semantic_id") != record.semantic_id:
            raise ValueError("operationalization identity mismatch after deserialization")
        return record

    def validate(self, root: str | Path | None = None) -> None:
        self.primary_claim.validate(root)
        for claim in self.supporting_claims:
            claim.validate(root)


def _claim(claim_id: str, locator: str, source_id: str = "TI-0097") -> CorpusClaimReference:
    """Una referencia al snapshot sellado; los hashes son los del manifiesto."""
    return CorpusClaimReference(
        claim_id=claim_id, source_id=source_id, locator=locator,
        claim_artifact="CLAIMS_RELATIONS_v0.1.csv",
        claim_artifact_sha256="4bc6a81191e128e0c7e9926d5fdf9a659211799f303b8c961d4b6773ee375340",
        source_artifact="SOURCE_SAMPLE_v0.1.md",
        source_artifact_sha256="efaa7cea49bdce7545215723eeecfab22118252e458b05125c6211b1ecc75c17",
    )


CLAIM_0127 = _claim("CLM-0127", "ch. 1.1, PDF p. 23")
CLAIM_0132 = _claim("CLM-0132", "ch. 1.1, PDF pp. 24–25")
LEARN_A1_OPERATIONALIZATION = OperationalizationRecord(
    operationalization_id="OPR-LEARN-A1-RL-01", capability_id="LEARN-A1",
    primary_claim=CLAIM_0127, supporting_claims=(CLAIM_0132,),
    human_operationalization=HumanOperationalization(
        decision_id="G0-LEARN-A1-2026-09-17",
        scope=("modificación dependiente de experiencia del comportamiento "
               "situación→acción bajo consecuencias de interacción"),
        excluded_scope=("memory", "persistence", "generalization", "transfer",
                        "continual learning", "meta-learning", "few-shot/MAML",
                        "necessarily parametric learning", "necessarily world-model learning"),
        conceptual_property="comportamiento situación→acción bajo consecuencias de interacción",
        observable_property="conducta futura bajo la misma demanda",
        possible_intervention="intervención de aprendizaje declarada por LEARN-A1",
    ),
    algorithm=AlgorithmBinding("OnlineLearner", "v1"),
    implementation=ImplementationBinding("terrario.agent.agents.a4_advanced:A4Advanced.learn"),
    endpoint=EndpointBinding("conversion_aprendizaje"),
)
REGISTRY: dict[str, OperationalizationRecord] = {}


def operationalization_for_capability(capability_id: str) -> OperationalizationRecord:
    matches = tuple(record for record in REGISTRY.values() if record.capability_id == capability_id)
    if len(matches) != 1:
        raise KeyError(f"no unique operationalization for capability: {capability_id}")
    return matches[0]


def operationalization_for_passport(passport: object) -> OperationalizationRecord:
    record_id = getattr(passport, "operationalization_id", None)
    capability_id = getattr(passport, "capability_id", None)
    if not record_id or record_id not in REGISTRY:
        raise KeyError("passport has no registered operationalization")
    record = REGISTRY[record_id]
    if record.capability_id != capability_id:
        raise ValueError("passport capability and operationalization disagree")
    return record


def reverse_lookup(claim_id: str) -> tuple[OperationalizationRecord, ...]:
    matches = tuple(record for record in REGISTRY.values() if claim_id in record.claim_ids)
    if not matches:
        raise KeyError(f"unknown or unbound claim: {claim_id}")
    return matches


def validate_registry(records: Iterable[OperationalizationRecord] = REGISTRY.values()) -> None:
    records = tuple(records)
    from terrario.lab.capability_passport import REGISTRY as passport_registry
    for record in records:
        record.validate()
        passport = passport_registry.get(record.capability_id)
        if passport is None or operationalization_for_passport(passport) != record:
            raise ValueError("passport does not round-trip to operationalization")
        if passport.corpus_provenance != record.claim_ids:
            raise ValueError("passport claim ids do not match operationalization")
    linked = {record.capability_id for record in records}
    implicit = [passport.capability_id for passport in passport_registry.values()
                if passport.capability_id not in linked
                and (passport.corpus_provenance or passport.operationalization_id)]
    if implicit:
        raise ValueError("implicit provenance on unlinked passports: " + ", ".join(sorted(implicit)))


# --- HOMEO-A1 · Ashby 1956 ----------------------------------------------------
#
# El pasaporte se registró con `corpus_provenance=()` mientras estos tres claims
# estaban en la capa auditada del corpus, con locator, sin que nadie los mirara.

HOMEO_A1_OPERATIONALIZATION = OperationalizationRecord(
    operationalization_id="OPR-HOMEO-A1-REG-01",
    capability_id="HOMEO-A1",
    primary_claim=_claim("CLM-0056", "part I–III", "TI-0049"),
    supporting_claims=(
        _claim("CLM-0052", "part II, ch. 11, PDF pp. 108–110", "TI-0049"),
        _claim("CLM-0053", "part II, ch. 11", "TI-0049"),
    ),
    human_operationalization=HumanOperationalization(
        decision_id="HD-HOMEO-A1-01",
        scope=("Regulación entendida como restricción de la desviación de una variable "
               "esencial del organismo, no como optimización de recompensa externa."),
        excluded_scope=(
            "No se afirma que el organismo posea variedad requerida suficiente: Ashby da "
            "una cota, no una capacidad.",
            "No se afirma jerarquía de control; CLM-0055 queda fuera de esta decisión.",
            "No se afirma que la regulación observada sea adaptativa ni aprendida."),
        conceptual_property="Restringir la desviación de una variable esencial sostiene estabilidad.",
        observable_property=("Ante la misma observación externa, la decisión difiere según el "
                             "valor de la variable esencial interna."),
        possible_intervention=("Suprimir la lectura de la variable esencial en la selección de "
                               "acción, dejando intacto su cálculo."),
    ),
    algorithm=AlgorithmBinding("HomeostaticState", "v1"),
    implementation=ImplementationBinding("terrario.agent.homeostasis.HomeostaticState"),
    endpoint=EndpointBinding("PENDIENTE-regulacion-condicionada-al-estado"),
)


# --- WM-A1 · Ha & Schmidhuber 2018 --------------------------------------------

WM_A1_OPERATIONALIZATION = OperationalizationRecord(
    operationalization_id="OPR-WM-A1-REPR-01",
    capability_id="WM-A1",
    primary_claim=_claim("CLM-0116", "abstract, PDF p. 1", "TI-0087"),
    supporting_claims=(_claim("CLM-0117", "abstract y §2, PDF pp. 1–2", "TI-0087"),),
    human_operationalization=HumanOperationalization(
        decision_id="HD-WM-A1-01",
        scope=("Modelo del mundo entendido como representación comprimida que la política "
               "consume, no como simulador fiel del entorno."),
        excluded_scope=(
            "No se afirma simulación latente ni entrenamiento dentro del modelo; "
            "CLM-0118 a CLM-0120 quedan fuera.",
            "No se afirma que la representación sea espaciotemporal en el sentido del "
            "artículo: A4 predice su propio latente, no el mundo. La brecha se declara "
            "aquí en vez de disimularse.",
            "No se afirma transferencia de política."),
        conceptual_property=("Una representación comprimida del mundo es utilizable por una "
                             "política compacta."),
        observable_property=("La predicción del modelo ordena correctamente entidades favorables "
                             "y desfavorables nunca experimentadas."),
        possible_intervention="Desactivar el modelo del mundo dejando intacto el resto del ciclo.",
    ),
    algorithm=AlgorithmBinding("WorldModel", "v1"),
    implementation=ImplementationBinding("terrario.agent.world_model.WorldModel"),
    endpoint=EndpointBinding("examen_prediccion"),
)


# --- UNC-A1 · Pathak 2017 -----------------------------------------------------
#
# Se cita la mitad del artículo que trata del RUIDO INCONTROLABLE, no la que
# define la curiosidad: ésa pertenece a CURIO-A1, y mezclarlas haría de UNC-A1 y
# CURIO-A1 la misma capacidad con dos nombres.

UNC_A1_OPERATIONALIZATION = OperationalizationRecord(
    operationalization_id="OPR-UNC-A1-NOISE-01",
    capability_id="UNC-A1",
    primary_claim=_claim("CLM-0126", "§2, PDF p. 3", "TI-0090"),
    supporting_claims=(_claim("CLM-0125", "§2, PDF p. 3", "TI-0090"),),
    human_operationalization=HumanOperationalization(
        decision_id="HD-UNC-A1-01",
        scope=("Incertidumbre entendida como la parte del error de predicción que procede de "
               "factores que el organismo no controla, y que por tanto no debe perseguir."),
        excluded_scope=(
            "No se afirma curiosidad: CLM-0121 a CLM-0124 pertenecen a CURIO-A1.",
            "No se afirma que el estimador esté calibrado; el endpoint sigue pendiente.",
            "No se afirma dinámica inversa: A4 no la implementa."),
        conceptual_property=("Parte del error de predicción es irreducible, y distinguirla es lo "
                             "que evita perseguir ruido."),
        observable_property=("La varianza estimada es mayor ante consecuencias genuinamente "
                             "estocásticas que ante consecuencias deterministas no aprendidas."),
        possible_intervention="Desactivar el estimador de incertidumbre dejando intacta la política.",
    ),
    algorithm=AlgorithmBinding("UncertaintyEstimator", "v1"),
    implementation=ImplementationBinding("terrario.agent.uncertainty.UncertaintyEstimator"),
    endpoint=EndpointBinding("PENDIENTE-calibracion-de-incertidumbre"),
)


# --- CURIO-A1 · Pathak 2017 ---------------------------------------------------
#
# La mitad del artículo que UNC-A1 no cita. CLM-0121 está tipado
# OPERATIONAL_DEFINITION: el corpus no da un concepto que haya que interpretar,
# da el mecanismo. Y CLM-0123 describe exactamente el fallo que medimos —el
# organismo recorre 2 columnas de 34 porque la recompensa externa es escasa—,
# así que esta capacidad no se elige por elegancia: se elige porque la fuente
# nombra nuestro problema.

CURIO_A1_OPERATIONALIZATION = OperationalizationRecord(
    operationalization_id="OPR-CURIO-A1-PE-01",
    capability_id="CURIO-A1",
    primary_claim=_claim("CLM-0121", "abstract y §2, PDF pp. 1–3", "TI-0090"),
    supporting_claims=(
        _claim("CLM-0122", "§2, PDF pp. 2–3", "TI-0090"),
        _claim("CLM-0123", "abstract y §1, PDF pp. 1–2", "TI-0090"),
    ),
    human_operationalization=HumanOperationalization(
        decision_id="HD-CURIO-A1-01",
        scope=(
            "El error al predecir la consecuencia de la propia acción se devuelve al "
            "organismo como señal de valor, y esa señal entra en la selección de acción."),
        excluded_scope=(
            "La señal NO puede depender de dónde está la comida. Dice «andá donde tu "
            "predicción falla», nunca «las puertas son buenas». Si supiera el mapeo "
            "habríamos construido la respuesta dentro del organismo, que es el problema "
            "del oráculo entrando por la puerta de atrás.",
            "No se afirma dinámica inversa ni rasgos condicionados a la acción: CLM-0125 "
            "pertenece a UNC-A1 y A4 no la implementa, así que el ruido incontrolable "
            "(CLM-0126) queda como confusor declarado y no resuelto.",
            "No se afirma que las habilidades resultantes sean útiles después: CLM-0124 "
            "queda fuera hasta que exista con qué medirlo."),
        conceptual_property=(
            "El error de predicción sobre las propias consecuencias es una fuente de valor "
            "que no requiere recompensa externa."),
        observable_property=(
            "Con recompensa externa escasa, el organismo visita más estados cuya "
            "consecuencia predice peor que uno idéntico sin la señal."),
        possible_intervention=(
            "Suprimir la entrada de la señal intrínseca en la selección de acción, dejando "
            "intacto el cálculo del error de predicción."),
    ),
    algorithm=AlgorithmBinding("IntrinsicPredictionError", "v1"),
    implementation=ImplementationBinding("terrario.agent.curiosity.IntrinsicPredictionError"),
    endpoint=EndpointBinding("PENDIENTE-exploracion-dirigida-por-error"),
)


REGISTRY.update({record.operationalization_id: record for record in (
    LEARN_A1_OPERATIONALIZATION,
    HOMEO_A1_OPERATIONALIZATION,
    WM_A1_OPERATIONALIZATION,
    UNC_A1_OPERATIONALIZATION,
    CURIO_A1_OPERATIONALIZATION,
)})
