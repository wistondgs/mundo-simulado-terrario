"""Misma definición de mundo, misma semilla, misma secuencia de acciones, mismo resultado.

Es la Fase 0 de TCS-01. Hasta que esto pase, ninguna corrida produce evidencia:
un nivel «superado» bajo una superficie y reprobado bajo la otra no es un nivel
superado, es una pregunta sin respuesta.

La secuencia de acciones es FIJA y no viene de A4. Un agente real introduciría
sus propias diferencias —inicialización, generador, orden de muestreo— y
entonces una divergencia no distinguiría «las físicas didieren» de «los agentes
difieren». Con acciones guionizadas sólo queda el mundo.

El fallo nombra el PRIMER paso y el PRIMER campo que divergen. Un test que diga
«las trayectorias son distintas» obliga a reconstruir a mano dónde empezó, que
es precisamente el trabajo que este test existe para ahorrar.
"""

from __future__ import annotations

import pytest

from terrario.core.types import Action, ActionType, Direction
# Hay DOS `load_scenario` en el árbol: `world/scenario.py:97` devuelve un
# `ScenarioSpec` y `experiment/controller.py:32` devuelve el dict que la
# materialización consume. El segundo es el que usa la ruta real.
from terrario.experiment.controller import load_scenario, materialize_scenario
from terrario.world.transition import build_episode_components, run_step

#: Un guion que toca las cinco operaciones y se repite. PUSH y MOVE mueven al
#: organismo, CONSUME resuelve objetivo, INSPECT y NOOP no hacen nada: entre las
#: cinco recorren todos los caminos de `physics.step`.
GUION = [
    Action(ActionType.MOVE, Direction.RIGHT), Action(ActionType.CONSUME, Direction.UP),
    Action(ActionType.PUSH, Direction.DOWN), Action(ActionType.INSPECT, Direction.NONE),
    Action(ActionType.MOVE, Direction.DOWN), Action(ActionType.CONSUME, Direction.RIGHT),
    Action(ActionType.NOOP, Direction.NONE), Action(ActionType.MOVE, Direction.LEFT),
    Action(ActionType.CONSUME, Direction.DOWN), Action(ActionType.PUSH, Direction.RIGHT),
]


class OrganismoGuionizado:
    """Emite el guion y nada más. No aprende, no percibe, no muestrea."""

    def __init__(self, guion, pasos):
        self._acciones = [guion[i % len(guion)] for i in range(pasos)]
        self._i = 0
        self.config = {"hidden_dim": 1}

    def perceive(self, observation): pass
    def offer_targets(self, targets): pass
    def get_internal_state(self): return {}
    def learn(self, transition): pass

    def decide(self):
        accion = self._acciones[self._i]
        self._i += 1
        return Action(accion.action_type, accion.direction)


def _campos(componentes, outcome, paso):
    """Lo que no puede diferir entre superficies. La lista es del contrato de TCS-01."""
    verdad = componentes.world._mutable_state()
    agente = verdad.agents[0]
    ciclo = componentes.lifecycle
    return {
        "time": verdad.time,
        "rules_version": verdad.rules_version,
        "agent_position": (agente.pos.x, agente.pos.y),
        "agent_energy": round(agente.energy, 9),
        "alive": agente.alive,
        "object_set": tuple(sorted(verdad.objects)),
        "object_positions": tuple(sorted((k, v.pos.x, v.pos.y) for k, v in verdad.objects.items())),
        "state_hash": verdad.state_hash(),
        "world_events": tuple(outcome.consequence.observer_events),
        "energy_delta": round(outcome.energy_delta, 9),
        "terminated": outcome.terminated,
        # El linaje no entra en `state_hash` -- éste excluye `properties` -- así
        # que un respawn con generación equivocada pasaría inadvertido si no se
        # comparase aparte.
        "opportunity_lineage": tuple(sorted(ciclo._lineage.items())) if ciclo else (),
        "opportunity_pending": tuple(sorted(
            (p["lineage_root"], p["generation"], p["due_step"]) for p in ciclo._pending)
        ) if ciclo else (),
        "respawn_events": tuple(
            (e.kind, e.opportunity_id, e.step) for e in outcome.respawn_events),
    }


def _trayectoria(escenario, *, semilla, pasos, con_lifecycle):
    componentes = build_episode_components(
        escenario, duration_fallback=pasos, with_lifecycle=con_lifecycle, world_seed=semilla)
    agente = OrganismoGuionizado(GUION, pasos)
    historia = []
    for paso in range(pasos):
        if not componentes.world._mutable_state().agents[0].alive:
            break
        outcome = run_step(componentes, agente, paso, world_seed=semilla,
                           agent_seed=semilla + 1_000_003, max_steps=pasos)
        historia.append(_campos(componentes, outcome, paso))
    return historia


def _primera_divergencia(izquierda, derecha):
    """El primer paso y el primer campo. No «son distintas»."""
    for paso, (a, b) in enumerate(zip(izquierda, derecha)):
        for campo in a:
            if a[campo] != b[campo]:
                return paso, campo, a[campo], b[campo]
    if len(izquierda) != len(derecha):
        return min(len(izquierda), len(derecha)), "longitud", len(izquierda), len(derecha)
    return None


def _escenario(nombre, semilla):
    return materialize_scenario(load_scenario(f"scenarios/{nombre}"), semilla)


# ── PARITY-9 · determinismo ──────────────────────────────────────────────

@pytest.mark.parametrize("nombre,lifecycle", [
    ("d0_differences.yaml", False),
    ("d4_temporal_variety.yaml", True),
])
def test_dos_ejecuciones_independientes_dan_la_misma_trayectoria(nombre, lifecycle):
    escenario = _escenario(nombre, 4242)
    primera = _trayectoria(escenario, semilla=4242, pasos=60, con_lifecycle=lifecycle)
    segunda = _trayectoria(escenario, semilla=4242, pasos=60, con_lifecycle=lifecycle)
    divergencia = _primera_divergencia(primera, segunda)
    assert divergencia is None, (
        f"dos ejecuciones con la misma semilla divergen en el paso {divergencia[0]}, "
        f"campo {divergencia[1]!r}: {divergencia[2]!r} contra {divergencia[3]!r}")


def test_semillas_distintas_si_divergen():
    """El control negativo: si todo coincidiera siempre, el test no mediría nada."""
    a = _trayectoria(_escenario("d4_temporal_variety.yaml", 1), semilla=1, pasos=60,
                     con_lifecycle=True)
    b = _trayectoria(_escenario("d4_temporal_variety.yaml", 2), semilla=2, pasos=60,
                     con_lifecycle=True)
    assert _primera_divergencia(a, b) is not None, (
        "dos mundos con semillas distintas produjeron trayectorias idénticas; "
        "la semilla del mundo no está materializando nada")


# ── PARITY-2 · el ciclo de oportunidades es física, no adorno ────────────

def test_el_ciclo_de_oportunidades_cambia_la_trayectoria_en_D4T():
    """Si encenderlo no cambiara nada, el escenario lo declararía en vano.

    Éste es el test que convierte «el banco no ejecuta el lifecycle» en una
    divergencia demostrada en lugar de una diferencia de código. Lo que mide es
    el tamaño del defecto que la Fase 0 repara.
    """
    escenario = _escenario("d4_temporal_variety.yaml", 4242)
    sin = _trayectoria(escenario, semilla=4242, pasos=120, con_lifecycle=False)
    con = _trayectoria(escenario, semilla=4242, pasos=120, con_lifecycle=True)
    divergencia = _primera_divergencia(sin, con)
    assert divergencia is not None, (
        "el ciclo de oportunidades no cambió la trayectoria en 120 pasos de D4T; "
        "o no se consumió nada, o el escenario no lo declara")


def test_sin_lifecycle_declarado_encenderlo_no_cambia_nada():
    """D0 no declara `opportunity_lifecycle`, así que la bandera debe ser inerte.

    Es lo que permite llevar el ciclo a la superficie que no lo tenía sin tocar
    los mundos que nunca lo pidieron.
    """
    escenario = _escenario("d0_differences.yaml", 77)
    sin = _trayectoria(escenario, semilla=77, pasos=60, con_lifecycle=False)
    con = _trayectoria(escenario, semilla=77, pasos=60, con_lifecycle=True)
    divergencia = _primera_divergencia(sin, con)
    assert divergencia is None, (
        f"encender el ciclo cambió un mundo que no lo declara, en el paso "
        f"{divergencia[0] if divergencia else '?'}, campo "
        f"{divergencia[1] if divergencia else '?'}")


# ── PARITY-9 bis · el mismo spec produce el mismo organismo ──────────────

def test_el_banco_siembra_el_rng_global_antes_de_construir_el_agente(tmp_path):
    """Dos creaciones del mismo spec deben dar el mismo organismo.

    `create_agent` siembra un `torch.Generator` por agente, pero los pesos de los
    módulos salen del RNG GLOBAL de torch -- `memory.py:156` llama a `torch.randn`
    sin generator, y lo mismo hace cada `nn.Linear`. Así que dos corridas del
    mismo spec en un proceso producían organismos distintos, y el
    `initial_parameters_hash` no era reproducible entre procesos.

    Los bancos lo compensaban a mano con `torch.manual_seed` antes de cada
    `create`. La ruta científica llama a `set_global_determinism` desde siempre.
    Ésa era la asimetría que hacía que «la misma semilla» significara cosas
    distintas en cada superficie.
    """
    from dataclasses import replace

    from terrario.lab.agent_composition import validate_selection
    from terrario.lab.sandbox_runtime import (
        ExecutionClassification, SandboxService, derive_sandbox, make_spec,
    )
    from terrario.lab.world_authoring import compile_registry_world
    from terrario.lab.world_registry import WorldScenarioRegistry, configuration_for

    entrada = WorldScenarioRegistry(".").get("D4T")
    compilado = compile_registry_world("D4T", entrada.source)
    base = replace(derive_sandbox(configuration_for(entrada)), agent_reference="A4")

    hashes = []
    for intento in range(2):
        servicio = SandboxService(tmp_path / f"banco{intento}")
        spec = make_spec(base, compilado, 42, 777, 2,
                         ExecutionClassification.ENGINEERING_SANDBOX,
                         validate_selection({}))
        run = servicio.create(spec, base, compilado)
        hashes.append(run.timeline[0].agent_identity["initial_parameters_hash"]
                      if run.timeline else
                      servicio._runtime[run.run_id]["agent"]
                      .agent_identity["initial_parameters_hash"])

    assert hashes[0] == hashes[1], (
        "dos creaciones del mismo spec dieron organismos distintos; el banco no "
        "está sembrando el RNG global antes de construir el agente")
