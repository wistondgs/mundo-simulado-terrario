"""CAUSAL-CAPABILITY-BENCH-01 · el laboratorio contrafactual del organismo.

La unidad experimental deja de ser «dos corridas con la misma semilla». Pasa a
ser **un nacimiento y sus gemelos contrafactuales**:

    UN ORGANISMO MATERIALIZADO  →  GEMELOS  →  INTERVENCIONES AISLADAS

Por qué el cambio. El piloto de forrajeo midió, sobre siete semillas, que un
brazo CONGELADO -- que no aprende nada -- consumía `[1, 97, 2, 7, 2, 0, 0]`:
varianza 1110, pura suerte de inicialización. Con ese suelo de ruido, «misma
semilla» no parea nada: dos construcciones independientes desde la misma
semilla comparten el sorteo, no el organismo. Aquí se materializa **uno** y se
lo clona, de modo que la igualdad al nacer es una propiedad del objeto y no una
esperanza sobre el generador.

`InitialStateFingerprint` del compositor existente declara nueve hashes de
estado inicial compartido. Eso es un **certificado**, y sigue sirviendo como
tal; lo que no puede es sustituir a la clonación, porque verifica a posteriori
que dos nacimientos coincidieron en vez de garantizar que hubo uno solo.

Cuatro fases explícitas, y no se mezclan en un solo número:

    BIRTH        estado compartido, verificado adversarialmente
    ACQUISITION  la intervención actúa; cada brazo aprende según su régimen
    FREEZE       se cierra el aprendizaje en TODOS
    PROBE        examen autónomo, sin adquisición nueva

Y dos protocolos que convierten la correlación en causa:

    TRANSPLANTE  un gemelo ingenuo recibe SÓLO los parámetros aprendidos
    RESTAURACIÓN al aprendido se le devuelven SÓLO los parámetros iniciales

Si la competencia viaja con los parámetros en un sentido y desaparece en el
otro, el portador de la capacidad queda localizado.
"""

from __future__ import annotations

import copy
import hashlib
import statistics
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Callable, Iterable, Mapping, Sequence

import torch

from terrario.agent.adaptive_freeze import (
    ADAPTIVE_FINGERPRINT_VERSION, AdaptiveFreeze, AdaptiveRegime,
    adaptive_components, adaptive_fingerprint, regime_of,
)
from terrario.agent.agents import create_agent
from terrario.core.rng import RNGManager

SCHEMA_VERSION = "terrario.lab.causal-bench/v1"


class Phase(StrEnum):
    BIRTH = "BIRTH"
    ACQUISITION = "ACQUISITION"
    FREEZE = "FREEZE"
    PROBE = "PROBE"
    CHALLENGE = "CHALLENGE"


class BirthEquivalenceError(AssertionError):
    """`COUNTERFACTUAL_BIRTH_INVALID`. Falla cerrado, siempre."""

    code = "COUNTERFACTUAL_BIRTH_INVALID"


# --- Qué es «el estado causal» de un organismo -------------------------------
#
# No se enumeran campos por nombre bonito: cada uno está aquí porque se
# demostró que una diferencia en él cambia el futuro. `_generator` entra porque
# la política muestrea de él; `planner._generator` NO entra por separado porque
# **es el mismo objeto** (`a4_advanced.py:200` le pasa `self._generator`), de
# modo que la búsqueda del planner y el muestreo de la política consumen un
# único stream -- medido, no supuesto.

def causal_state_digest(agent: Any) -> dict[str, str]:
    """Huella por pieza del estado causal, adaptativo y no adaptativo."""
    out: dict[str, str] = {}
    for name, blob in adaptive_components(agent).items():
        out[f"adaptive.{name}"] = hashlib.sha256(blob).hexdigest()[:16]

    out["rng.agent"] = hashlib.sha256(
        agent._generator.get_state().numpy().tobytes()).hexdigest()[:16]
    out["rng.planner_is_agent_stream"] = str(
        getattr(getattr(agent, "planner", None), "_generator", None) is agent._generator)

    hidden = getattr(agent, "_hidden", None)
    out["recurrent.hidden"] = ("—" if hidden is None else hashlib.sha256(
        hidden.detach().cpu().contiguous().numpy().tobytes()).hexdigest()[:16])

    out["homeostasis.energy"] = f"{float(agent.homeostasis.energy):.12g}"
    out["homeostasis.threshold"] = f"{float(agent.homeostasis.threshold):.12g}"

    optimizer = getattr(getattr(agent, "learner", None), "_optimizer", None)
    if optimizer is None:
        out["optimizer"] = "—"
    else:
        state = optimizer.state_dict()
        h = hashlib.sha256()
        h.update(str(state["param_groups"]).encode())
        for key in sorted(state["state"]):
            entry = state["state"][key]
            h.update(str(key).encode())
            for field_name in sorted(entry):
                value = entry[field_name]
                h.update(field_name.encode())
                h.update(value.detach().cpu().contiguous().numpy().tobytes()
                         if torch.is_tensor(value) else str(value).encode())
        out["optimizer"] = h.hexdigest()[:16]

    out["config"] = hashlib.sha256(
        str(sorted(agent.config.items())).encode()).hexdigest()[:16]
    return out


def birth_certificate(agent: Any) -> str:
    """Un hash sobre el estado causal entero. El certificado del nacimiento."""
    digest = causal_state_digest(agent)
    h = hashlib.sha256()
    h.update(SCHEMA_VERSION.encode())
    h.update(ADAPTIVE_FINGERPRINT_VERSION.encode())
    for key in sorted(digest):
        h.update(key.encode())
        h.update(digest[key].encode())
    return h.hexdigest()


# --- La intervención ---------------------------------------------------------

@dataclass(frozen=True)
class Intervention:
    """Lo que distingue a un brazo de su gemelo. Una sola cosa, declarada.

    Sustituye al vocabulario cerrado de `TreatmentArm`, que sólo sabe expresar
    `PLANNER_PRESERVED` / `PLANNER_ABLATED` y por tanto no puede representar los
    regímenes adaptativos ni nada de E1-E9. Aquí un brazo es
    **espécimen compartido + intervención declarada**, y la intervención lleva
    su propia procedencia para que después se pueda auditar qué se tocó.
    """

    intervention_id: str
    target_component: str
    phase: Phase
    before: Mapping[str, Any]
    after: Mapping[str, Any]
    rationale: str

    @property
    def provenance(self) -> str:
        return hashlib.sha256(str({
            "id": self.intervention_id, "target": self.target_component,
            "phase": str(self.phase), "before": dict(self.before),
            "after": dict(self.after),
        }).encode()).hexdigest()[:16]


#: Los tres regímenes adaptativos, expresados como intervenciones sobre la
#: configuración del espécimen. `NORMAL` es la ausencia de intervención.
REGIME_INTERVENTIONS: dict[str, Intervention] = {
    "NORMAL": Intervention(
        "regime.normal", "adaptive_freeze", Phase.ACQUISITION, {}, {},
        "sin intervención: el organismo adapta"),
    "PARAMETRIC": Intervention(
        "regime.parametric_freeze", "learner.optimizer.step", Phase.ACQUISITION,
        {"learning_commit_enabled": True}, {"learning_commit_enabled": False},
        "congela theta y deja mutar memorias y línea base"),
    "FULL": Intervention(
        "regime.full_adaptive_freeze", "adaptive_freeze", Phase.ACQUISITION,
        {"full_adaptive_freeze": False}, {"full_adaptive_freeze": True},
        "congela la frontera adaptativa entera, certificada en OCF-G3"),
}


@dataclass
class Arm:
    arm_id: str
    specimen: Any
    intervention: Intervention
    birth: str
    regime: AdaptiveRegime


# --- El nacimiento y sus gemelos --------------------------------------------

@dataclass
class BirthSnapshot:
    """Un organismo materializado una sola vez, y los clones que salen de él."""

    pair_id: str
    prototype: Any
    certificate: str
    digest: Mapping[str, str]

    @classmethod
    def materialize(cls, pair_id: str, config: Mapping[str, Any], *,
                    seed: int, agent_type: str = "A4_ADVANCED") -> "BirthSnapshot":
        RNGManager.set_global_determinism(seed)
        prototype = create_agent(agent_type, dict(config), seed=seed)
        return cls(pair_id, prototype, birth_certificate(prototype),
                   causal_state_digest(prototype))

    def twin(self, arm_id: str, intervention: Intervention) -> Arm:
        """Un gemelo del MISMO nacimiento, con una intervención encima.

        `deepcopy` y no reconstrucción: dos construcciones desde la misma
        semilla comparten el sorteo, no el objeto, y ahí es donde se cuela la
        varianza que el piloto midió.
        """
        specimen = clone_specimen(self.prototype)
        if birth_certificate(specimen) != self.certificate:
            raise BirthEquivalenceError(
                f"{BirthEquivalenceError.code}: el clon {arm_id} no nació igual que su prototipo")

        for key, value in intervention.after.items():
            specimen.config[key] = value
        if intervention.after.get("full_adaptive_freeze"):
            specimen.adaptive_freeze = AdaptiveFreeze(enabled=True)
        if "learning_commit_enabled" in intervention.after:
            specimen._learning_commit_enabled = bool(
                intervention.after["learning_commit_enabled"])
        return Arm(arm_id, specimen, intervention, self.certificate, regime_of(specimen))

    def triplet(self) -> dict[str, Arm]:
        return {name: self.twin(name, REGIME_INTERVENTIONS[name])
                for name in ("NORMAL", "PARAMETRIC", "FULL")}


def assert_birth_equivalence(arms: Mapping[str, Arm], *,
                             allowed: Mapping[str, set[str]] | None = None) -> None:
    """Antes del tratamiento los brazos son idénticos salvo su intervención.

    Falla CERRADO: cualquier diferencia no declarada es
    `COUNTERFACTUAL_BIRTH_INVALID`. Es la propiedad de la que cuelga todo lo
    demás, así que no admite advertencia -- admite excepción.
    """
    allowed = allowed or {}
    reference_name, reference = next(iter(arms.items()))
    reference_digest = causal_state_digest(reference.specimen)
    for name, arm in arms.items():
        if name == reference_name:
            continue
        digest = causal_state_digest(arm.specimen)
        differing = {k for k in reference_digest if digest.get(k) != reference_digest[k]}
        undeclared = differing - allowed.get(name, set()) - {"config"}
        if undeclared:
            raise BirthEquivalenceError(
                f"{BirthEquivalenceError.code}: {name} difiere de {reference_name} "
                f"en {sorted(undeclared)}, que ninguna intervención declaró")


# --- Clonar un organismo que ya vivió ----------------------------------------

#: Tensores con historia de grafo que `deepcopy` rechaza. Son TRANSIENT por la
#: clasificación de `FRONTERA_ESTADO_APRENDIDO_01`: se reconstruyen en cada paso
#: (`perceive` fija el latente, `decide` el estado), así que desprenderlos no
#: quita estado adquirido. Ninguno pertenece a la frontera adaptativa.
_TRANSIENT_GRAPH_FIELDS = (
    "_last_state", "_last_latent", "_last_log_prob", "_last_logits",
    "_last_probs", "_last_uncertainty", "_hidden", "_last_hidden",
)


def detach_transients(agent: Any) -> Any:
    """Dejar al organismo clonable sin tocar nada adaptativo.

    Al nacer estos campos son `None` y el clon sale directo. Tras vivir cargan
    grafo y `deepcopy` falla con «Only Tensors created explicitly by the user
    support the deepcopy protocol». Se desprenden, y la huella adaptativa
    --parámetros, `M`, buffer, línea base-- queda intacta, que es lo que el
    certificado de nacimiento comprueba.
    """
    for name in _TRANSIENT_GRAPH_FIELDS:
        value = getattr(agent, name, None)
        if torch.is_tensor(value):
            setattr(agent, name, value.detach().clone())
        elif value is not None and name != "_hidden":
            setattr(agent, name, None)
    return agent


def clone_specimen(agent: Any) -> Any:
    """Un clon independiente de un organismo, haya vivido o no."""
    return copy.deepcopy(detach_transients(agent))


# --- Transplante y restauración ---------------------------------------------

#: `longterm_memory.M` ES un `nn.Parameter` y `get_parameters()` lo devuelve,
#: pero NO lo gobierna el optimizador: se escribe con `M.data.copy_()`. Un
#: transplante que use `set_parameters` tal cual mueve **theta Y M a la vez**, y
#: entonces lo único concluible es `(theta, M) -> capacidad`, jamás
#: `theta -> capacidad`. Justo la distinción que los tres brazos habían puesto
#: en duda, porque `M` se movía sin aportar conducta.
M_PARAMETER = "longterm_memory.M"


class Carrier(StrEnum):
    """Qué porción del estado aprendido se mueve en un transplante."""

    THETA = "THETA"          # parámetros del optimizador, SIN M
    M = "M"                  # sólo la memoria a largo plazo
    THETA_AND_M = "THETA_AND_M"


def _select(parameters: Mapping[str, torch.Tensor], carrier: Carrier
            ) -> dict[str, torch.Tensor]:
    if carrier is Carrier.THETA:
        return {k: v.clone() for k, v in parameters.items() if k != M_PARAMETER}
    if carrier is Carrier.M:
        return {k: v.clone() for k, v in parameters.items() if k == M_PARAMETER}
    return {k: v.clone() for k, v in parameters.items()}


def learned_parameters(arm: Arm, carrier: Carrier = Carrier.THETA_AND_M
                       ) -> dict[str, torch.Tensor]:
    return _select(arm.specimen.get_parameters(), carrier)


def transplant(donor: Arm, host_snapshot: BirthSnapshot, carrier: Carrier,
               arm_id: str | None = None) -> Arm:
    """Un gemelo INGENUO del mismo nacimiento recibe SÓLO `carrier`.

    Todo lo demás -- buffer episódico, línea base, RNG, recurrente -- se queda
    como nació. Con los tres portadores por separado la matriz distingue
    portador paramétrico, portador memorial e interacción; con uno solo no
    distingue nada.
    """
    arm_id = arm_id or f"TRANSPLANT_{carrier.value}"
    host = host_snapshot.twin(arm_id, Intervention(
        f"transplant.{carrier.value.lower()}", "parameters", Phase.PROBE,
        {"carrier": "initial"}, {"carrier": carrier.value},
        f"host ingenuo que recibe exclusivamente {carrier.value} del donante"))
    host.specimen.adaptive_freeze = AdaptiveFreeze(enabled=True)
    host.specimen.set_parameters(learned_parameters(donor, carrier))
    return host


def restore(arm: Arm, snapshot: BirthSnapshot, carrier: Carrier,
            arm_id: str | None = None) -> Arm:
    """La inversa, con la MISMA semántica: al aprendido se le devuelve sólo
    `carrier` en su valor inicial, conservando el resto de lo adquirido.

    Si al devolver theta desaparece la competencia y el transplante de theta la
    hace aparecer en otro organismo, la evidencia causal es bidireccional.
    """
    arm_id = arm_id or f"RESTORE_{carrier.value}"
    restored = clone_specimen(arm.specimen)
    restored.set_parameters(_select(snapshot.prototype.get_parameters(), carrier))
    restored.adaptive_freeze = AdaptiveFreeze(enabled=True)
    return Arm(arm_id, restored, Intervention(
        f"restore.{carrier.value.lower()}", "parameters", Phase.PROBE,
        {"carrier": "learned"}, {"carrier": "initial"},
        f"devuelve {carrier.value} inicial conservando el resto de lo adquirido"),
        arm.birth, regime_of(restored))


# --- Compatibilidad: el transplante de un solo portador ----------------------

def transplant_parameters(donor: Arm, host_snapshot: BirthSnapshot,
                          arm_id: str = "TRANSPLANT") -> Arm:
    """Mueve theta Y M. Conserva el nombre histórico y dice lo que hace: con
    esto sólo se puede concluir `(theta, M) -> capacidad`."""
    return transplant(donor, host_snapshot, Carrier.THETA_AND_M, arm_id)


def restore_parameters(arm: Arm, snapshot: BirthSnapshot,
                       arm_id: str = "RESTORE") -> Arm:
    return restore(arm, snapshot, Carrier.THETA_AND_M, arm_id)


# --- Estadística pareada -----------------------------------------------------

@dataclass
class PairedResult:
    name: str
    deltas: list[float]

    @property
    def mean(self) -> float:
        return statistics.fmean(self.deltas) if self.deltas else float("nan")

    @property
    def median(self) -> float:
        return statistics.median(self.deltas) if self.deltas else float("nan")

    @property
    def positive_fraction(self) -> float:
        return (sum(1 for d in self.deltas if d > 0) / len(self.deltas)
                if self.deltas else float("nan"))

    def bootstrap(self, *, draws: int = 20000, rng_seed: int = 20260918) -> tuple[float, float]:
        import random
        rng = random.Random(rng_seed)
        means = sorted(statistics.fmean(rng.choices(self.deltas, k=len(self.deltas)))
                       for _ in range(draws))
        return means[int(0.025 * draws)], means[int(0.975 * draws)]

    def leave_one_out(self) -> list[float]:
        """Sensibilidad: la media quitando cada par. Un único par que mueva el
        signo es exactamente el modo de fallo que el piloto produjo."""
        return [statistics.fmean(self.deltas[:i] + self.deltas[i + 1:])
                for i in range(len(self.deltas))] if len(self.deltas) > 1 else []

    @property
    def dominated_by_one_pair(self) -> bool:
        loo = self.leave_one_out()
        if not loo:
            return True
        return any((m > 0) != (self.mean > 0) for m in loo)


def variance_components(by_arm: Mapping[str, Sequence[float]]) -> dict[str, float]:
    """Entre pares frente a dentro del par. Si la primera domina, el
    experimento está limitado por inicialización y no por tratamiento."""
    names = list(by_arm)
    n = len(by_arm[names[0]])
    pair_means = [statistics.fmean(by_arm[a][i] for a in names) for i in range(n)]
    between = statistics.pvariance(pair_means) if n > 1 else 0.0
    within = statistics.fmean(
        statistics.pvariance([by_arm[a][i] for a in names]) for i in range(n)
    ) if len(names) > 1 else 0.0
    total = between + within
    return {"between_pair": between, "within_pair": within,
            "between_fraction": between / total if total else float("nan")}


# --- Niveles de capacidad ----------------------------------------------------

CAPABILITY_LEVELS = {
    "F0": "no hay adquisición diferenciadora",
    "F1": "el modelo interno adquiere la consecuencia",
    "F2": "lo adquirido persiste y es demostrable en el probe congelado",
    "F3": "lo adquirido CAUSA mejor conducta",
    "F4": "el organismo consigue por sí mismo la experiencia y alcanza F3",
}


# --- El bundle no paramétrico ------------------------------------------------
#
# DISCOVERY-32 encontró que `theta` inicial servido con estado adaptativo no
# paramétrico aprendido es PEOR que congelarlo todo: `Δ PARAMETRIC − FULL =
# −3.47, IC95% [−8.66, −0.34]`, con sólo el 6% de los pares a favor, y
# `Δ NORMAL − RESTORE = +8.09, IC95% [+0.56, +17.22]` dice lo mismo desde el
# otro lado. Eso señala una interacción entre portadores, no una culpable.
# Para saber si `M` sola reproduce el daño hace falta poder mover el bundle
# aparte de `M`, y `set_parameters` no puede: el buffer y la línea base no son
# `nn.Parameter`.

NONPARAMETRIC_PIECES = ("longterm_M", "episodic_buffer", "baseline")


def transplant_nonparametric(donor: Arm, host: Arm, *,
                             pieces: Sequence[str] = NONPARAMETRIC_PIECES) -> Arm:
    """Mover estado adaptativo que NO pasa por `set_parameters`.

    `M` se mueve por tensor, el buffer episódico por copia profunda de su
    contenido, y la línea base es el par `(valor, contador)` -- que va junto,
    porque el contador es el denominador del paso de la media corrida y separar
    uno del otro produce una media que nunca existió.
    """
    source, target = donor.specimen, host.specimen
    if "longterm_M" in pieces:
        with torch.no_grad():
            target.longterm_memory.M.data.copy_(source.longterm_memory.M.data)
    if "episodic_buffer" in pieces:
        target.episodic_memory._buffer = copy.deepcopy(source.episodic_memory._buffer)
        target.episodic_memory._write_idx = source.episodic_memory._write_idx
    if "baseline" in pieces:
        target._energy_baseline = float(source._energy_baseline)
        target._baseline_count = int(source._baseline_count)
    return host


def carrier_matrix(donor: Arm, birth: BirthSnapshot) -> dict[str, Arm]:
    """Los seis brazos que separan portador paramétrico, memorial e interacción.

    Todos nacen del MISMO nacimiento ingenuo y quedan congelados. `M` viaja sola
    en su brazo y nunca dentro de `THETA`, que es la corrección que hacía falta
    antes de interpretar nada: `set_parameters` mueve `theta` Y `M` a la vez
    porque `M` es `nn.Parameter`, y entonces lo único concluible sería
    `(theta, M) -> capacidad`.
    """
    hosts: dict[str, Arm] = {}
    hosts["BIRTH"] = birth.twin("BIRTH", REGIME_INTERVENTIONS["FULL"])
    hosts["BIRTH"].specimen.adaptive_freeze = AdaptiveFreeze(enabled=True)
    hosts["THETA"] = transplant(donor, birth, Carrier.THETA)
    hosts["M"] = transplant(donor, birth, Carrier.M)
    hosts["THETA_M"] = transplant(donor, birth, Carrier.THETA_AND_M)

    nonparam = birth.twin("NONPARAM", REGIME_INTERVENTIONS["FULL"])
    nonparam.specimen.adaptive_freeze = AdaptiveFreeze(enabled=True)
    hosts["NONPARAM"] = transplant_nonparametric(donor, nonparam)

    everything = transplant(donor, birth, Carrier.THETA, arm_id="FULL_LEARNED")
    hosts["FULL_LEARNED"] = transplant_nonparametric(donor, everything)
    return hosts
