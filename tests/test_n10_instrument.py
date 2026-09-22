"""N1.0 · el aparato, con sus mutantes.

Nothing here learns. These are the contracts the bench has to satisfy before
anything that learns is allowed to exist, and every one of them has a fixture
or a mutant that makes it capable of failing.
"""

from __future__ import annotations

from collections import Counter

import pytest

from terrario.lab import world_generator as gen, world_oracles as wo
from terrario.lab.n10_instrument import (
    ApparatusNormalization, DecisionRow, GateResult, InstrumentRefused,
    answer_bearing_channels, check_channel_contract, feedback_channel_gate,
    feedback_of, history_of, informational_sufficiency, n1_run,
    observable_object_channels, observation_signature, present_without_energy,
    reset_isolation, same_present, shuffle_report, shuffled_tokens,
)

ECONOMIA = gen.Economy(initial_energy=250.0, max_energy=400.0,
                       step_energy_cost=0.15, gain=4.0, loss=4.0,
                       safe=0.0, low_energy=0.0)
NORMALIZA = ApparatusNormalization(enabled=True, baseline_energy=250.0)
SIN_NORMALIZAR = ApparatusNormalization()


def mundo(stations: int = 32, seed: int = 0):
    w = gen.world_for(['EPMEM-A1'], seed=seed, stations=stations, economy=ECONOMIA)
    w.scenario['expose_time_fraction'] = False
    return w


def corrida(fac=wo.FULL, *, norm=NORMALIZA, stations=32, seed=0, w=None):
    w = w if w is not None else mundo(stations, seed)
    return w, n1_run(w, wo.Oracle(w, fac), arm="x", seed=seed, normalization=norm)


# --- G_CHANNEL_SCHEMA · estructural, no por valor ------------------------------------

def test_the_answer_channel_is_outside_the_observable_schema_at_four():
    w = mundo()
    informe = check_channel_contract(w)
    assert informe["num_channels"] == 4
    assert informe["observable_object_channels"] == [0, 1, 2]
    assert informe["answer_bearing_channels"] == [3]
    assert informe["leaking_channels"] == []
    assert informe["result"] == GateResult.PASS.value


def test_five_channels_put_the_answer_in_the_observation_and_is_refused():
    """The mutant the old guard let through silently.

    It asked whether the float 0.9 appeared in the window — exact equality
    against a value that has round-tripped through float32 — so it could
    never fail. This asks about the schema instead."""
    w = mundo()
    w.scenario['num_channels'] = 5
    informe = check_channel_contract(w)
    assert informe["observable_object_channels"] == [0, 1, 2, 3]
    assert informe["leaking_channels"] == [3]
    assert informe["result"] == GateResult.FAIL.value
    assert informe["code"] == "OBSERVATIONAL_ALIASING_VIOLATED"


def test_the_runner_refuses_to_run_a_leaking_world():
    """Not truncated at run time to save the experiment."""
    w = mundo()
    w.scenario['num_channels'] = 5
    with pytest.raises(InstrumentRefused, match="OBSERVATIONAL_ALIASING_VIOLATED"):
        n1_run(w, wo.Oracle(w, wo.FULL), arm="leaky", normalization=NORMALIZA)


def test_a_world_that_shows_the_answer_has_two_answer_channels():
    from dataclasses import replace
    visible = replace(mundo().demand, hidden=False)
    assert answer_bearing_channels(visible) == (2, 3)
    assert set(answer_bearing_channels(visible)) & set(observable_object_channels(4))


# --- G_OBSERVATION_SIGNATURE ----------------------------------------------------------

def test_the_signature_covers_every_field_the_organism_receives():
    import dataclasses

    from terrario.core.types import Observation
    assert tuple(f.name for f in dataclasses.fields(Observation)) == (
        "channels", "mask", "agent_energy", "time_fraction")


def test_the_signature_refuses_an_observation_that_grew_a_field():
    """A field added later that obs_hash did not cover would loosen
    SAME_PRESENT silently, so the signature refuses rather than hashes."""
    import dataclasses

    import terrario.core.types as tipos
    from terrario.core.types import Observation

    @dataclasses.dataclass
    class ObservacionCrecida:
        channels: object = None
        mask: object = None
        agent_energy: float = 0.0
        time_fraction: float = 0.0
        nuevo_campo: int = 0

        def obs_hash(self):
            return "no debería llegar aquí"

    original = tipos.Observation
    try:
        tipos.Observation = ObservacionCrecida
        with pytest.raises(InstrumentRefused, match="los cuatro campos"):
            observation_signature(ObservacionCrecida())
    finally:
        tipos.Observation = original
    assert len(dataclasses.fields(Observation)) == 4


# --- G_SAME_PRESENT + G_FEEDBACK_NONZERO ----------------------------------------------

def test_without_the_reset_the_present_differs_at_every_decision():
    """T1. The leak, reproduced: paying for the right door lands in the
    visible energy."""
    _, filas = corrida(norm=SIN_NORMALIZAR)
    sp = same_present(filas)
    assert sp["n_decisions"] == 32
    assert sp["n_obs_hash"] == 32
    assert sp["result"] == GateResult.FAIL.value
    assert sp["code"] == "NO_HASH_HOLDS_TWO_HISTORIES"


def test_with_the_reset_one_present_holds_both_histories_and_feedback_survives():
    """T3."""
    _, filas = corrida()
    sp = same_present(filas)
    assert sp["n_obs_hash"] == 1
    assert sp["result"] == GateResult.PASS.value
    assert len(next(iter(sp["mixed_hashes"].values()))) == 2
    assert all(abs(f.consequence) > 1e-9 for f in filas)


def test_the_arm_that_errs_keeps_one_present_and_gets_both_signs():
    """T4. The oracle never errs, so the control that matters is the lesioned
    arm — the one whose losses would move the visible energy."""
    _, filas = corrida(wo.without("memory"))
    sp = same_present(filas)
    assert sp["n_obs_hash"] == 1
    assert sp["result"] == GateResult.PASS.value
    signos = {f.consequence > 0 for f in filas}
    assert signos == {True, False}


# --- G_RESET_ISOLATION -----------------------------------------------------------------

def test_the_reset_moves_the_energy_and_nothing_else():
    _, sin = corrida(norm=SIN_NORMALIZAR)
    _, con = corrida(norm=NORMALIZA)
    informe = reset_isolation(sin, con)
    assert informe["result"] == GateResult.PASS.value, informe["differing_fields"]
    assert informe["n_decisions"] == 32
    assert informe["distinct_energy_without_reset"] == 32
    assert informe["distinct_energy_with_reset"] == 1


def test_the_non_energy_present_is_identical_with_and_without_the_reset():
    """Read through a signature that omits energy on purpose — used only here,
    never as the SAME_PRESENT gate."""
    _, sin = corrida(norm=SIN_NORMALIZAR)
    _, con = corrida(norm=NORMALIZA)
    assert [r.station_id for r in sin] == [r.station_id for r in con]
    assert [r.correct_action for r in sin] == [r.correct_action for r in con]
    assert [r.consequence for r in sin] == [r.consequence for r in con]


def test_reset_isolation_catches_a_run_with_fewer_decisions():
    _, con = corrida()
    informe = reset_isolation(con[:-1], con)
    assert informe["result"] == GateResult.FAIL.value
    assert informe["code"] == "DECISION_COUNT_CHANGED"


# --- G_FEEDBACK_CHANNEL · el contrato que sustituye a T2 -------------------------------

def test_the_consequence_channel_separates_a_win_from_a_loss():
    """CF2 in hermetic form: no world, no organism, no campaign."""
    informe = feedback_channel_gate(lambda d: round(0.5 * d, 6))
    assert informe["result"] == GateResult.PASS.value
    assert informe["update_positive"] != informe["update_negative"]


def test_an_update_that_reads_the_level_instead_of_the_delta_is_caught():
    """The mutant that replaces the retired T2. After the apparatus restores
    the energy, the level is the same whether the door was right or wrong, so
    a learner reading it is blind and no accuracy metric would say so."""
    nivel_tras_reposicion = 250.0
    informe = feedback_channel_gate(lambda d: round(0.5 * nivel_tras_reposicion, 6))
    assert informe["result"] == GateResult.FAIL.value
    assert informe["code"] == "CONSEQUENCE_NOT_CAUSAL"


def test_an_update_that_raises_is_invalid_not_passing():
    def rompe(_d):
        raise RuntimeError("boom")
    assert feedback_channel_gate(rompe)["result"] == GateResult.INVALID.value


def test_feedback_of_reads_the_delta_and_not_any_level():
    """Checked over the executable body with the docstring stripped by AST.

    The first version of this test grepped the raw source and caught its own
    docstring, which names `agent_energy` in order to forbid it — the
    text-guard failure this project already catalogued once."""
    import ast
    import inspect
    import textwrap

    arbol = ast.parse(textwrap.dedent(inspect.getsource(feedback_of)))
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Expr) and isinstance(nodo.value, ast.Constant) \
                and isinstance(nodo.value.value, str):
            nodo.value.value = ""
    codigo = ast.unparse(arbol)
    assert "energy_delta" in codigo
    assert "agent_energy" not in codigo


# --- G_HISTORY_GROUND_TRUTH + G_HISTORY_NONLEAKAGE -------------------------------------

def test_the_lesioned_arm_keeps_every_history_label():
    """The defect a probe written before this module had: it read the token
    from the oracle's own memory, which in this arm is empty by construction,
    so every row came back unlabelled and a gate would have compared nothing
    against nothing."""
    _, filas = corrida(wo.without("memory"))
    assert all(f.history_id for f in filas)
    assert len({f.history_id for f in filas}) == 2


def test_the_history_label_comes_from_the_world_and_matches_the_sealed_station():
    w, filas = corrida()
    por_columna = {s.index: s for s in w.stations}
    for f in filas:
        assert f.history_id == history_of(por_columna[f.station_id])
        assert f.correct_action == por_columna[f.station_id].designated


def test_history_cannot_reach_the_actor_because_the_observations_are_identical():
    """The strongest available proof rather than a grep: when SAME_PRESENT
    passes, the two histories arrive at byte-identical observations, so no
    function of the observation can carry the label."""
    _, filas = corrida()
    assert same_present(filas)["result"] == GateResult.PASS.value
    assert len({f.obs_hash for f in filas}) == 1
    assert len({f.history_id for f in filas}) == 2


def test_the_actor_has_no_second_input_channel_on_this_bench():
    """`decide()` takes no arguments, so everything causal arrives through
    `perceive(observation)`. The slot table is the only other path and it is
    gated on an attribute the oracle does not have."""
    import inspect

    from terrario.agent.base import AgentInterface
    assert list(inspect.signature(AgentInterface.decide).parameters) == ["self"]
    assert not hasattr(wo.Oracle(mundo(), wo.FULL), "_addressing_mode")


def test_a_decision_row_carries_the_label_and_the_observation_does_not():
    _, filas = corrida()
    fila = filas[0]
    assert fila.history_id
    assert fila.history_id not in fila.obs_hash


# --- G_SHUFFLE · S1 a S4 ----------------------------------------------------------------

def test_s1_the_shuffle_preserves_the_marginals():
    _, filas = corrida()
    informe = shuffle_report(filas, seed=7)
    assert informe["marginals_preserved"] is True
    barajado = shuffled_tokens(filas, seed=7)
    assert Counter(barajado.values()) == Counter(f.history_id for f in filas)


def test_s2_the_shuffle_breaks_the_correspondence():
    _, filas = corrida()
    barajado = shuffled_tokens(filas, seed=7)
    original = {i: f.history_id for i, f in enumerate(filas)}
    assert barajado != original
    cambiadas = sum(1 for i in original if original[i] != barajado[i])
    assert cambiadas > 0


def test_s3_the_same_seed_gives_the_same_permutation():
    _, filas = corrida()
    assert shuffled_tokens(filas, seed=7) == shuffled_tokens(filas, seed=7)
    assert shuffled_tokens(filas, seed=7) != shuffled_tokens(filas, seed=8)


def test_s4_the_shuffle_touches_only_the_token():
    """It is a mapping over decision ids; it holds no world, no consequence
    and no parameters, so it cannot move them."""
    _, filas = corrida()
    barajado = shuffled_tokens(filas, seed=7)
    assert set(barajado) == {i for i, _ in enumerate(filas)}
    assert [f.obs_hash for f in filas] == [f.obs_hash for f in filas]
    assert [f.consequence for f in filas] == [f.consequence for f in filas]


def test_a_permutation_that_permutes_nothing_is_refused():
    una = (DecisionRow(run_id="r", seed=0, arm="a", station_id=0, decision_id=0,
                       step=0, history_id="0.90", correct_action="up",
                       chosen_action="up", obs_hash="h", energy_visible=0.5,
                       consequence=1.0),)
    assert shuffled_tokens(una, seed=1) == {0: "0.90"}


# --- las cuatro fixtures ------------------------------------------------------------------

def test_positive_instrument_fixture():
    """The scripted oracle with legitimate access to history. It proves the
    instrument recognises the hinge; it proves nothing about learning."""
    _, filas = corrida(wo.FULL)
    sp = same_present(filas)
    exactitud = sum(f.correct for f in filas) / len(filas)
    por_historia = {h: [f.correct for f in filas if f.history_id == h]
                    for h in {f.history_id for f in filas}}
    assert sp["result"] == GateResult.PASS.value
    assert exactitud == 1.0
    assert len(por_historia) == 2
    assert all(all(v) for v in por_historia.values())


def test_negative_instrument_fixture():
    """Same world, same parity, no causal access to history. The labels stay
    because they come from the world: an agent without history is not the
    same thing as a dataset without history."""
    _, filas = corrida(wo.without("memory"))
    sp = same_present(filas)
    exactitud = sum(f.correct for f in filas) / len(filas)
    assert sp["result"] == GateResult.PASS.value
    assert sp["n_decisions"] == 32
    assert len({f.history_id for f in filas}) == 2
    assert 0.25 <= exactitud <= 0.75, exactitud


def test_leaky_fixture_is_rejected_before_it_can_run():
    w = mundo()
    w.scenario['num_channels'] = 5
    assert check_channel_contract(w)["result"] == GateResult.FAIL.value
    with pytest.raises(InstrumentRefused):
        n1_run(w, wo.Oracle(w, wo.FULL), arm="leaky", normalization=NORMALIZA)


def test_degenerate_fixture_never_passes():
    assert same_present([])["result"] == GateResult.INVALID.value
    assert same_present([])["code"] == "NO_DECISIONS"
    _, filas = corrida()
    una_sola = [f for f in filas if f.history_id == filas[0].history_id]
    informe = same_present(una_sola)
    assert informe["result"] == GateResult.INVALID.value
    assert informe["code"] == "SINGLE_HISTORY_CLASS"


# --- suficiencia informacional, antes de cualquier aprendiz --------------------------------

def test_the_problem_contains_what_the_construct_needs():
    """The defence 1.8 did not have: ask whether the information is there
    before building something to find it."""
    _, filas = corrida()
    informe = informational_sufficiency(filas)
    assert informe["result"] == "INFORMATIONALLY_SUFFICIENT"
    assert informe["bayes_from_O_and_H"] == 1.0
    assert informe["bayes_from_O"] < 1.0
    assert informe["gain"] > 0


def test_sufficiency_says_insufficient_when_the_history_is_irrelevant():
    """The mutant. A gate that cannot report INSUFFICIENT is not a gate."""
    _, filas = corrida()
    import dataclasses
    irrelevante = [dataclasses.replace(f, history_id="0.90" if i % 2 else "0.10",
                                       correct_action="up")
                   for i, f in enumerate(filas)]
    informe = informational_sufficiency(irrelevante)
    assert informe["result"] == "INFORMATIONALLY_INSUFFICIENT"
    assert informe["gain"] == 0.0


def test_sufficiency_is_invalid_with_one_history_or_none():
    assert informational_sufficiency([])["result"] == "INVALID"
    _, filas = corrida()
    una = [f for f in filas if f.history_id == filas[0].history_id]
    assert informational_sufficiency(una)["code"] == "SINGLE_HISTORY_CLASS"


def test_feedback_of_works_on_a_real_transition_and_not_only_in_its_source():
    """The gap that let a wrong field name pass.

    The guard above reads the source and asserts it says `energy_delta`. It
    said so — on a field called `consequence`, which `Transition` does not
    have; the real name is `consequence_t1`. Nothing caught it until the
    adapter ran. A contract that names something the object does not carry is
    the 1.8 failure in miniature, so this one builds a real Transition."""
    from terrario.core.contracts import Transition
    from terrario.core.types import Consequence

    t = Transition(observation_t=None, internal_state_ref=None, action_t=None,
                   consequence_t1=Consequence(energy_delta=-4.15, events=[]),
                   observation_t1=None, terminated=False, truncated=False,
                   step=0, seed=0)
    assert feedback_of(t) == pytest.approx(-4.15)
