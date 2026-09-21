"""Turning a capability into runtime configuration, and refusing to turn the rest.

The bridge addressed an implementation.  This one writes configuration, which
is where the schema can be destroyed rather than merely described: if what the
organism was supposed to acquire arrives as a parameter, the experiment still
runs, still produces numbers, and no longer measures anything.  The separation
would have been documentation.

So exactly one of the four v2 fields may reach the runtime:

    supplied              MAY materialise -- that is what supplying means
    acquisition_target    MUST NOT -- writing it is handing over the answer
    non_claims            MUST NOT -- a scope limit is not a parameter
    formalization_ref     describes and resolves; it configures nothing

And `supplied` only authorises *keys*, never values.  The passport says which
parameters we are the ones providing; what they are worth is the experiment's
business, and inventing a number here would be a silent scientific default
wearing a provenance badge.

The base configuration is preserved and the overlay is deliberately thin:
nothing is added that the base did not already carry, because a capability that
can introduce keys can introduce the one nobody authorised.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from terrario.lab.capability_bridge import BridgeRefused, ResolvedCapability
from terrario.lab.capability_passport import REGISTRY as PASSPORTS, ElementKind

MATERIALIZATION_SCHEMA = "terrario.lab.capability-materialization/v1"


class MaterializationRefused(ValueError):
    def __init__(self, codes: tuple[str, ...]):
        self.codes = tuple(sorted(set(codes)))
        super().__init__("; ".join(self.codes))


@dataclass(frozen=True)
class MaterializedExecution:
    """A runtime configuration and the provenance of every authorised key."""

    capability_id: str
    agent_type: str
    agent_config: Mapping[str, Any]
    authorised_keys: tuple[str, ...]
    activation_flag: str | None
    mechanism_id: str
    mechanism_version: int
    mechanism_spec_hash: str
    implementation_path: str
    endpoint_id: str
    schema_version: str = MATERIALIZATION_SCHEMA


def authorised_configuration_keys(capability_id: str) -> tuple[str, ...]:
    """Every key a capability is allowed to write, and nothing else.

    Split out so the invariant can be tested without materialising anything:
    the question "may this key be written?" has one answer and one place.
    """
    passport = PASSPORTS.get(capability_id)
    if passport is None:
        raise MaterializationRefused((f"UNKNOWN_CAPABILITY:{capability_id}",))
    keys = [element.identity for element in passport.supplied
            if element.kind is ElementKind.PARAMETER]
    if passport.composition_flag:
        keys.append(passport.composition_flag)
    return tuple(sorted(keys))


def forbidden_configuration_keys(capability_id: str) -> tuple[str, ...]:
    """What must never reach the runtime, named so a test can point at it."""
    passport = PASSPORTS.get(capability_id)
    if passport is None:
        raise MaterializationRefused((f"UNKNOWN_CAPABILITY:{capability_id}",))
    return tuple(sorted({element.identity for element in passport.acquisition_target}
                        | set(passport.non_claims)))


def materialize_execution(resolved: ResolvedCapability,
                          base_agent_config: Mapping[str, Any],
                          *, agent_type: str) -> MaterializedExecution:
    """Apply only what the capability is authorised to apply.

    `base_agent_config` supplies the values; the capability supplies the
    permission.  A key the capability authorises but the base does not define
    is refused rather than defaulted -- the passport is not a place to decide
    what a learning rate should be.
    """
    autorizadas = authorised_configuration_keys(resolved.capability_id)
    prohibidas = forbidden_configuration_keys(resolved.capability_id)
    refusals: list[str] = []

    # El gate científico. Que una clave prohibida esté ya en la base no es
    # excusa: materializarla bajo el nombre de esta capacidad la convierte en
    # algo que suministramos, y eso es exactamente lo que no ocurrió.
    for key in prohibidas:
        if key in autorizadas:
            refusals.append(f"ACQUIRED_DECLARED_AS_SUPPLIED:{key}")
        if key in base_agent_config:
            refusals.append(f"ACQUISITION_TARGET_IN_RUNTIME_CONFIG:{key}")

    # La bandera la escribimos nosotros; los parámetros no. Un parámetro
    # autorizado que la base no define no se inventa ni se deja pasar: el
    # pasaporte no es el sitio donde se decide cuánto vale una tasa de
    # aprendizaje.
    passport = PASSPORTS[resolved.capability_id]
    parametros = [e.identity for e in passport.supplied
                  if e.kind is ElementKind.PARAMETER]
    refusals.extend(f"AUTHORISED_KEY_ABSENT_FROM_BASE:{key}"
                    for key in parametros if key not in base_agent_config)

    no_consumidas = _keys_the_implementation_ignores(resolved, autorizadas)
    refusals.extend(no_consumidas)

    if refusals:
        raise MaterializationRefused(tuple(refusals))

    config = dict(base_agent_config)
    if passport.composition_flag:
        config[passport.composition_flag] = True

    return MaterializedExecution(
        capability_id=resolved.capability_id, agent_type=agent_type,
        agent_config=config, authorised_keys=autorizadas,
        activation_flag=passport.composition_flag,
        mechanism_id=resolved.mechanism.mechanism_id,
        mechanism_version=int(resolved.mechanism.version),
        mechanism_spec_hash=resolved.mechanism.spec_hash,
        implementation_path=resolved.implementation_path,
        endpoint_id=resolved.endpoint_id)


def _keys_the_implementation_ignores(resolved: ResolvedCapability,
                                     keys: tuple[str, ...]) -> tuple[str, ...]:
    """A key nobody reads is a promise nobody keeps."""
    import inspect

    module = inspect.getmodule(resolved.implementation)
    if module is None:
        return (f"IMPLEMENTATION_SOURCE_UNAVAILABLE:{resolved.implementation_path}",)
    source = inspect.getsource(module)
    return tuple(f"CONFIG_KEY_NOT_READ_BY_IMPLEMENTATION:{key}" for key in keys
                 if f'config["{key}"]' not in source
                 and f"config['{key}']" not in source
                 and f'config.get("{key}"' not in source)
