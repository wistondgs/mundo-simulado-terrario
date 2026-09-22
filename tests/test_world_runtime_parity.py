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
    # `CausalRuntime.step` lo llama y `run_step` no: el banco exige del
    # organismo una pieza de interfaz que la ruta autoritativa no pide.
    def get_trace_events(self): return []

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

    Hoy la garantía ya no depende de que cada superficie se acuerde: la da
    `create_agent`, que sostiene el RNG global en su `seed` mientras construye
    y lo restaura al salir (`tests/test_agent_factory.py`). Esta prueba sigue
    porque comprueba otra cosa —que el spec entero llega intacto al organismo,
    no sólo la semilla— y porque es la que fallaría si alguna superficie
    volviera a construir por su cuenta.
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
        "dos creaciones del mismo spec dieron organismos distintos; algo entre "
        "el spec y los pesos no está gobernado por la semilla del agente")


# ── PARITY-10 · conformidad ENTRE SUPERFICIES ────────────────────────────
#
# Lo que hay arriba prueba que `run_step` es determinista: lo ejecuta dos veces.
# Eso no es lo que el encabezado de este fichero promete. «Un nivel superado
# bajo una superficie y reprobado bajo la otra» exige comparar DOS superficies,
# y la tercera ruta del árbol --`CausalRuntime.step`-- no llama a `run_step`:
# reimplementa la secuencia, sin contrato de acción, sin lifecycle y con el RNG
# exógeno derivado de la semilla del AGENTE en vez de la del mundo.
#
# El Atlas 03 dejó eso como K2 porque nadie lo había medido. Esto lo mide.

from pathlib import Path

from terrario.lab.causal import CausalRuntime
from terrario.lab.execution.runtime import ScientificTrialIdentity

#: El banco se cualifica sólo para este escenario y sin ciclo de oportunidades
#: (`CausalRuntime.capability`), así que la comparación se hace donde él mismo
#: dice ser exacto. Comparar fuera de su alcance declarado sería reprocharle
#: algo que nunca prometió.
ESCENARIO_CUALIFICADO = "d0_differences.yaml"


def _campos_comunes(verdad, terminado):
    """El subconjunto que las DOS superficies pueden ofrecer sin tocarlas.

    `run_step` devuelve un `StepOutcome` y el banco un `record`, así que no
    comparten forma. Lo que sí comparten es la VERDAD DEL MUNDO después del
    paso, que es donde cualquier divergencia de física, reglas, coste o
    lifecycle tiene que aparecer -- y el `state_hash`, que las resume.
    """
    agente = verdad.agents[0]
    return {
        "time": verdad.time,
        "rules_version": verdad.rules_version,
        "agent_position": (agente.pos.x, agente.pos.y),
        "agent_energy": round(agente.energy, 9),
        "alive": agente.alive,
        "object_set": tuple(sorted(verdad.objects)),
        "object_positions": tuple(sorted(
            (k, v.pos.x, v.pos.y) for k, v in verdad.objects.items())),
        "state_hash": verdad.state_hash(),
        "terminated": terminado,
    }


def _ruta_autoritativa(escenario, *, semilla, pasos):
    componentes = build_episode_components(
        escenario, duration_fallback=pasos, with_lifecycle=False, world_seed=semilla)
    agente = OrganismoGuionizado(GUION, pasos)
    historia = []
    for paso in range(pasos):
        if not componentes.world._mutable_state().agents[0].alive:
            break
        outcome = run_step(componentes, agente, paso, world_seed=semilla,
                           agent_seed=semilla + 1_000_003, max_steps=pasos)
        historia.append(
            _campos_comunes(componentes.world._mutable_state(), outcome.terminated))
    return historia


def _ruta_del_banco(escenario, *, semilla, pasos):
    identidad = ScientificTrialIdentity(
        execution_id="parity", trial_intent_id="parity", attempt_id="parity",
        plan_hash="parity", preregistration_root_hash="parity",
        software_identity="parity", scenario_identity=ESCENARIO_CUALIFICADO,
        agent_identity="A0_RANDOM", world_seed=semilla, agent_seed=semilla + 1_000_003)
    runtime = CausalRuntime(
        identidad, Path(f"scenarios/{ESCENARIO_CUALIFICADO}"), dict(escenario))
    # El mismo guion, instancia propia: el organismo del banco lo construye él,
    # y dejarlo sortear devolvería la comparación a dos trayectorias distintas.
    runtime.agent = OrganismoGuionizado(GUION, pasos)
    historia = []
    for _ in range(pasos):
        if runtime.terminal:
            break
        record = runtime.step()
        if record.get("terminal") and "world_hash" not in record:
            break
        historia.append(
            _campos_comunes(runtime.world._mutable_state(), bool(record["terminal"])))
    return historia


def test_las_dos_superficies_recorren_la_misma_trayectoria():
    """`run_step` contra `CausalRuntime.step`, misma condición inicial y guion.

    Si diverge, el fallo nombra el primer paso y el primer campo. Una
    divergencia aquí no es un test roto: es la respuesta al K2 del Atlas 03.
    """
    escenario = _escenario(ESCENARIO_CUALIFICADO, 4242)
    autoritativa = _ruta_autoritativa(escenario, semilla=4242, pasos=40)
    banco = _ruta_del_banco(escenario, semilla=4242, pasos=40)

    assert autoritativa, "la ruta autoritativa no produjo ningún paso"
    divergencia = _primera_divergencia(autoritativa, banco)
    assert divergencia is None, (
        f"paso {divergencia[0]}, campo {divergencia[1]!r}: "
        f"run_step={divergencia[2]!r} · CausalRuntime={divergencia[3]!r}")


def test_el_banco_no_puede_configurarse_en_T1():
    """Por qué la divergencia del contrato de acción es hoy inalcanzable.

    El Atlas 03 midió que `CausalRuntime.step` no aplica `apply_action_contract`
    y que su cualificación --agente, escenario, lifecycle-- no mira el modo de
    direccionamiento, así que un brazo T1 se habría clasificado `EXACT_FORKABLE`
    sin poder consumir nada. Ese hueco existe en `capability` y **no es
    alcanzable**, por dos puertas distintas, y conviene que se rompa ruidosamente
    el día que alguna se abra:

    1. `ScientificTrialIdentity` sólo admite claves `use_*` booleanas, así que
       `addressing_mode` no cabe en la identidad de la corrida;
    2. el banco construye su organismo con el `agent_config` del controlador
       --vacío-- más `num_channels` y `view_size`, así que tampoco entra por el
       escenario.
    """
    base = dict(
        execution_id="x", trial_intent_id="x", attempt_id="x", plan_hash="x",
        preregistration_root_hash="x", software_identity="x", scenario_identity="x",
        agent_identity="A0_RANDOM", world_seed=1, agent_seed=2)

    with pytest.raises(ValueError, match="use_"):
        ScientificTrialIdentity(**base, agent_config={"addressing_mode": "T1_ENTITY"})

    # Y la segunda puerta: lo que el banco entrega al constructor del organismo.
    escenario = _escenario(ESCENARIO_CUALIFICADO, 4242)
    runtime = CausalRuntime(
        ScientificTrialIdentity(**base), Path(f"scenarios/{ESCENARIO_CUALIFICADO}"),
        dict(escenario))
    assert runtime.agent._addressing_mode.value == "T0_DIRECTIONAL"
