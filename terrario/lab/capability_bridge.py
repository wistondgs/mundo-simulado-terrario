"""The one link the integration audit found missing: a passport to real code.

Everything else was already there, as data.  A capability resolves to an
operationalization record, that record names an algorithm AND an import path --
`terrario.agent.agents.a4_advanced:A4Advanced.learn` for LEARN-A1 -- and the
endpoint it declares is computed by `run_measures`.  What did not exist was a
function that walks it: nothing in the tree resolves `capability_id` to an
implementation, and no consumer of `CapabilityPassport` configures an agent.

The resolution keys on `(algorithm_id, algorithm_version)` rather than on the
capability's operationalization id, and that is the whole care of this module.
A v2 passport has no operationalization id on purpose -- inheriting one would
have made it claim a corpus link naming another capability -- so reaching the
implementation through that record would smuggle back exactly what the
migration refused.  Which algorithm a path implements is a fact about the
algorithm; which claims a capability descends from is a human decision.  This
reads the first and never the second.

Scope, deliberately narrow: it demonstrates addressing and correspondence for
one capability.  It does not build an agent, does not run anything, and does
not touch the algorithm or the experiment.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Any, Mapping

from terrario.lab import mechanism_spec as mechanisms
from terrario.lab.capability_operationalization import REGISTRY as OPERATIONALIZATIONS
from terrario.lab.capability_passport import REGISTRY as PASSPORTS, CapabilityPassport
from terrario.lab.capability_plan import validate

BRIDGE_SCHEMA = "terrario.lab.capability-bridge/v1"


class BridgeRefused(ValueError):
    """Carries codes, because each way of being wrong needs a different repair."""

    def __init__(self, codes: tuple[str, ...]):
        self.codes = tuple(sorted(set(codes)))
        super().__init__("; ".join(self.codes))


@dataclass(frozen=True)
class ResolvedCapability:
    """What a capability addresses, once every reference has been walked."""

    capability_id: str
    mechanism: mechanisms.MechanismSpec
    algorithm_id: str
    algorithm_version: str
    implementation_path: str
    implementation: Any
    agent_configuration: Mapping[str, Any]
    endpoint_id: str
    schema_version: str = BRIDGE_SCHEMA


def algorithm_index() -> dict[tuple[str, str], str]:
    """`(algorithm_id, version)` to import path, and refuses an ambiguity.

    Derived from the operationalization records because that is where the paths
    are written, but only that field is read.  Two records disagreeing about
    what implements one algorithm is not something to resolve by picking one:
    measured today, five algorithms and zero conflicts.
    """
    index: dict[tuple[str, str], str] = {}
    conflicts: list[str] = []
    for record in OPERATIONALIZATIONS.values():
        key = (record.algorithm.algorithm_id, record.algorithm.algorithm_version)
        path = record.implementation.implementation_id
        if index.setdefault(key, path) != path:
            conflicts.append(f"AMBIGUOUS_IMPLEMENTATION:{key[0]}@{key[1]}")
    if conflicts:
        raise BridgeRefused(tuple(conflicts))
    return index


def _import_target(path: str) -> Any:
    """`module:attr.attr` or `module.attr`, resolved or refused.

    An import path that does not import is the failure this whole indirection
    would otherwise hide: a binding can name anything, and only loading it says
    whether the name still points at code.
    """
    module_name, _, attribute_path = path.partition(":")
    if not attribute_path:
        module_name, _, attribute_path = path.rpartition(".")
    try:
        target: Any = importlib.import_module(module_name)
    except ImportError as exc:
        raise BridgeRefused((f"IMPLEMENTATION_MODULE_ABSENT:{module_name}",)) from exc
    for part in filter(None, attribute_path.split(".")):
        try:
            target = getattr(target, part)
        except AttributeError as exc:
            raise BridgeRefused((f"IMPLEMENTATION_ATTRIBUTE_ABSENT:{path}",)) from exc
    return target


def _agent_configuration(passport: CapabilityPassport) -> Mapping[str, Any]:
    """The configuration the passport itself dictates.

    The composition flag turns the mechanism on; the supplied parameters name
    the keys the implementation reads.  Nobody rewrites here which algorithm
    corresponds to which capability -- that is the point of the exercise.
    """
    from terrario.lab.capability_passport import ElementKind

    configuration: dict[str, Any] = {}
    if passport.composition_flag:
        configuration[passport.composition_flag] = True
    for element in passport.supplied:
        if element.kind is ElementKind.PARAMETER:
            configuration.setdefault(element.identity, None)
    return configuration


def resolve_capability(capability_id: str) -> ResolvedCapability:
    """Walk passport -> mechanism -> algorithm -> implementation, or refuse.

    Fail closed at every step: a plan that resolves half its references is more
    dangerous than one that resolves none, because it looks actionable.
    """
    passport = PASSPORTS.get(capability_id)
    if passport is None:
        raise BridgeRefused((f"UNKNOWN_CAPABILITY:{capability_id}",))
    findings = validate(passport)
    if findings:
        raise BridgeRefused(findings)

    # El endpoint tiene que ser suyo y estar registrado. Un `PENDIENTE-*` de
    # otra capacidad es un nombre que el registro no resuelve, y dejarlo pasar
    # dirigiría una construcción hacia un instrumento que no existe.
    from terrario.lab import instrument_registry
    if instrument_registry.REGISTRY.get(passport.primary_endpoint) is None:
        raise BridgeRefused((f"ENDPOINT_NOT_REGISTERED:{passport.primary_endpoint}",))

    mechanism = mechanisms.resolve(passport.formalization_ref)
    key = (passport.algorithm_id, passport.algorithm_version)
    path = algorithm_index().get(key)
    if path is None:
        raise BridgeRefused((f"NO_IMPLEMENTATION_FOR_ALGORITHM:{key[0]}@{key[1]}",))

    return ResolvedCapability(
        capability_id=passport.capability_id, mechanism=mechanism,
        algorithm_id=passport.algorithm_id, algorithm_version=passport.algorithm_version,
        implementation_path=path, implementation=_import_target(path),
        agent_configuration=_agent_configuration(passport),
        endpoint_id=passport.primary_endpoint)


def assert_configuration_is_read_by_the_implementation(
        resolved: ResolvedCapability) -> tuple[str, ...]:
    """The correspondence, checked against the source rather than asserted.

    A passport that says it supplies `learning_rate` while the implementation
    reads `lr` is a contract nobody can act on, and the mismatch would be
    invisible: both names are plausible and neither side would complain.
    """
    import inspect

    owner = resolved.implementation
    module = inspect.getmodule(owner)
    if module is None:
        return (f"IMPLEMENTATION_SOURCE_UNAVAILABLE:{resolved.implementation_path}",)
    source = inspect.getsource(module)
    missing = tuple(
        f"CONFIG_KEY_NOT_READ_BY_IMPLEMENTATION:{key}"
        for key in resolved.agent_configuration
        if f'config["{key}"]' not in source and f"config['{key}']" not in source
        and f'config.get("{key}"' not in source)
    return missing
