import pytest
import torch

from terrario.agent.agents import AgentFactoryError, _parameter_hash, create_agent


@pytest.mark.parametrize("requested, klass", [
    ("A1_REACTIVE", "A1Reactive"), ("A2_GRU", "A2GRUBaseline"),
    ("A3_WORLD_MODEL", "A3WorldModel"), ("A4_ADVANCED", "A4Advanced"),
])
def test_factory_never_substitutes_requested_agent(requested, klass):
    agent = create_agent(requested, {"use_planner": False}, seed=7, device="cpu")
    assert type(agent).__name__ == klass
    assert agent.agent_identity["requested_agent_id"] == requested
    assert agent.agent_identity["initial_parameters_hash"]


def test_factory_fails_loudly_for_unknown_or_unavailable_device(monkeypatch):
    with pytest.raises(AgentFactoryError):
        create_agent("not-an-agent", seed=1)
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    with pytest.raises(AgentFactoryError):
        create_agent("A4_ADVANCED", {"use_planner": False}, seed=1, device="cuda")


def test_factory_auto_device_resolves_to_cpu_when_cuda_is_unavailable(monkeypatch):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)

    agent = create_agent("A2_GRU", seed=1, device="auto")

    assert agent.agent_identity["device"] == "cpu"
    assert agent._hidden.device.type == "cpu"


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA host required")
def test_a4_cuda_pipeline_keeps_runtime_tensors_on_gpu():
    import numpy as np

    from terrario.core.types import Observation

    agent = create_agent("A4_ADVANCED", {"use_planner": False}, seed=1, device="cuda")
    observation = Observation(
        channels=np.zeros((4, 5, 5), dtype=np.float32), mask=np.ones((5, 5), dtype=np.float32),
        agent_energy=0.5, time_fraction=0.0,
    )
    agent.perceive(observation)
    agent.decide()

    assert agent._hidden.device.type == "cuda"
    assert agent._last_state.device.type == "cuda"
    assert all(parameter.device.type == "cuda" for parameter in agent.get_parameters().values())


# ── La semilla determina el organismo, no sólo su muestreo ──────────────────
#
# `create_agent` construye un `torch.Generator` con la semilla y lo pasa a los
# agentes, pero ese generador gobierna sólo el MUESTREO. Los pesos salen del RNG
# GLOBAL de torch: cada `nn.Linear` lo lee, y también `memory.py:156` y
# `temporal.py:81-83`, que llaman a `torch.randn` sin generador. Así que la firma
# aceptaba una semilla y devolvía un objeto que la semilla no determinaba: dos
# llamadas idénticas daban pesos distintos y nada se quejaba.
#
# El determinismo lo ponía el llamante, sembrando a mano en la línea de arriba.
# Un llamante que se fiara del argumento obtenía un organismo distinto en cada
# construcción, y eso contamina cualquier afirmación de reproducibilidad
# levantada sobre esa ruta.
#
# A0 queda fuera de la parametrización a propósito: no tiene parámetros, así que
# su hash es el del vacío y pasaría las dos pruebas —la positiva por trivial y la
# negativa por falsa—. Añadirlo obligaría a borrar el control negativo.


@pytest.mark.parametrize("requested", ["A1_REACTIVE", "A2_GRU", "A3_WORLD_MODEL", "A4_ADVANCED"])
def test_two_agents_built_with_the_same_seed_are_the_same_organism(requested):
    first = create_agent(requested, {"use_planner": False}, seed=4242, device="cpu")
    second = create_agent(requested, {"use_planner": False}, seed=4242, device="cpu")

    assert _parameter_hash(first) == _parameter_hash(second)
    # El hash que se sella en la evidencia es el mismo que se compara aquí.
    assert first.agent_identity["initial_parameters_hash"] == _parameter_hash(first)
    assert second.agent_identity["initial_parameters_hash"] == _parameter_hash(second)


@pytest.mark.parametrize("requested", ["A1_REACTIVE", "A2_GRU", "A3_WORLD_MODEL", "A4_ADVANCED"])
def test_two_seeds_still_give_two_organisms(requested):
    """El control negativo: un criterio que no puede fallar no es criterio.

    Sin esto, sembrar con una constante pasaría la prueba de arriba tan bien
    como sembrar con la semilla.
    """
    first = create_agent(requested, {"use_planner": False}, seed=4242, device="cpu")
    other = create_agent(requested, {"use_planner": False}, seed=4243, device="cpu")

    assert _parameter_hash(first) != _parameter_hash(other)


def test_the_seed_survives_whatever_the_process_drew_in_between():
    """Éste es el caso real, no el de laboratorio.

    El llamante que sembraba a mano quedaba a merced de cuánto RNG global
    consumiera cualquier cosa entre su `manual_seed` y su `create_agent`.
    """
    reference = create_agent("A4_ADVANCED", {"use_planner": False}, seed=4242, device="cpu")

    torch.manual_seed(999)
    torch.randn(1237)
    after = create_agent("A4_ADVANCED", {"use_planner": False}, seed=4242, device="cpu")

    assert _parameter_hash(after) == _parameter_hash(reference)


def test_building_an_agent_does_not_spend_the_callers_global_rng():
    """La fábrica fija su azar en vez de gastar el del llamante.

    Antes, construir un agente adelantaba el RNG global del proceso, y cuánto
    dependía de la arquitectura. Quien sembraba para el mundo y construía el
    agente después corría sobre un flujo desplazado por el tamaño del organismo.
    """
    torch.manual_seed(7)
    before = torch.random.get_rng_state().clone()

    create_agent("A4_ADVANCED", {"use_planner": False}, seed=4242, device="cpu")

    assert torch.equal(before, torch.random.get_rng_state())
