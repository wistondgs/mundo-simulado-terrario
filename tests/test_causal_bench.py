"""Los gemelos nacen idénticos, o el banco no sirve para nada.

Esto existe porque el piloto de forrajeo midió que un brazo congelado -- que no
aprende nada -- consumía `[1, 97, 2, 7, 2, 0, 0]` entre semillas. Varianza 1110,
suerte de inicialización pura. «Misma semilla» no parea: dos construcciones
independientes comparten el sorteo, no el organismo.

La mitad adversarial es la que importa: cada pieza del estado causal, movida a
mano, tiene que hacer saltar `COUNTERFACTUAL_BIRTH_INVALID`. Sin eso, la
comprobación de equivalencia sería una comprobación de que no comprobamos nada.
"""

from __future__ import annotations

import copy

import pytest
import torch

from terrario.agent.adaptive_freeze import AdaptiveRegime
from terrario.lab.causal_bench import (
    BirthEquivalenceError, BirthSnapshot, Intervention, Phase, PairedResult,
    REGIME_INTERVENTIONS, assert_birth_equivalence, birth_certificate,
    causal_state_digest, restore_parameters, transplant_parameters,
    variance_components,
)

CONFIG = {
    "use_planner": True, "use_world_model": True, "use_uncertainty": True,
    "use_episodic_memory": True, "use_longterm_memory": True, "use_temporal": True,
    "use_online_learning": True, "view_size": 5,
    "latent_dim": 16, "hidden_dim": 24, "memory_dim": 8, "memory_slots": 4,
    "memory_capacity": 16, "ensemble_size": 2,
    "planner_horizon": 5, "planner_candidates": 10,
}


def snapshot(pair_id: str = "p0", seed: int = 0) -> BirthSnapshot:
    return BirthSnapshot.materialize(pair_id, CONFIG, seed=seed)


# --- El nacimiento -----------------------------------------------------------

def test_a_clone_is_born_identical_to_its_prototype():
    birth = snapshot()
    arm = birth.twin("NORMAL", REGIME_INTERVENTIONS["NORMAL"])
    assert birth_certificate(arm.specimen) == birth.certificate


def test_the_triplet_shares_one_birth():
    arms = snapshot().triplet()
    assert len({a.birth for a in arms.values()}) == 1
    assert_birth_equivalence(arms)


def test_the_regimes_are_what_they_say():
    arms = snapshot().triplet()
    assert arms["NORMAL"].regime is AdaptiveRegime.NORMAL
    assert arms["PARAMETRIC"].regime is AdaptiveRegime.PARAMETRIC_FREEZE
    assert arms["FULL"].regime is AdaptiveRegime.FULL_ADAPTIVE_FREEZE


def test_clones_are_independent():
    birth = snapshot()
    a = birth.twin("A", REGIME_INTERVENTIONS["NORMAL"])
    b = birth.twin("B", REGIME_INTERVENTIONS["NORMAL"])
    with torch.no_grad():
        b.specimen.policy_head.net[0].weight.add_(1.0)
    assert birth_certificate(a.specimen) == birth.certificate
    assert birth_certificate(b.specimen) != birth.certificate


def test_two_births_from_the_same_seed_are_not_the_same_object():
    """El punto entero del banco: la semilla compartida no basta, y por eso se
    materializa uno y se clona en vez de construir tres."""
    one, other = snapshot(seed=3), snapshot(seed=3)
    assert one.prototype is not other.prototype


# --- La mitad adversarial ----------------------------------------------------

def _mutate_parameters(agent):
    with torch.no_grad():
        agent.policy_head.net[0].weight.add_(1.0)


def _mutate_longterm_M(agent):
    agent.longterm_memory.M.data.add_(1.0)


def _mutate_episodic(agent):
    agent.episodic_memory.write(embedding=torch.zeros(CONFIG["latent_dim"]), action=1,
                                energy_delta=0.5, prediction_error=0.1, timestamp=0)


def _mutate_baseline_value(agent):
    agent._energy_baseline = float(agent._energy_baseline) + 42.0


def _mutate_baseline_count(agent):
    agent._baseline_count = int(agent._baseline_count) + 17


def _mutate_agent_rng(agent):
    torch.randint(0, 10, (5,), generator=agent._generator)


def _mutate_hidden(agent):
    agent._hidden = torch.ones_like(agent._hidden)


def _mutate_homeostasis(agent):
    agent.homeostasis._energy = 0.123


MISMATCHES = {
    "parameters": _mutate_parameters,
    "longterm_M": _mutate_longterm_M,
    "episodic_buffer": _mutate_episodic,
    "baseline value": _mutate_baseline_value,
    "baseline count": _mutate_baseline_count,
    "RNG del agente": _mutate_agent_rng,
    "recurrente": _mutate_hidden,
    "homeostasis": _mutate_homeostasis,
}


@pytest.mark.parametrize("piece", sorted(MISMATCHES))
def test_an_undeclared_mismatch_fails_closed(piece):
    arms = snapshot().triplet()
    MISMATCHES[piece](arms["FULL"].specimen)
    with pytest.raises(BirthEquivalenceError, match="COUNTERFACTUAL_BIRTH_INVALID"):
        assert_birth_equivalence(arms)


def test_the_planner_shares_the_policy_rng_stream():
    """Medido, no supuesto: `a4_advanced.py:200` pasa `self._generator` al
    planner, así que la búsqueda del planner y el muestreo de la política salen
    del MISMO stream. Un tratamiento que cambie cuántas veces se planifica
    desplaza también el azar de la política."""
    agent = snapshot().prototype
    assert agent.planner._generator is agent._generator
    assert causal_state_digest(agent)["rng.planner_is_agent_stream"] == "True"


# --- Transplante y restauración ---------------------------------------------

def test_a_transplant_moves_parameters_and_nothing_else():
    birth = snapshot()
    donor = birth.twin("NORMAL", REGIME_INTERVENTIONS["NORMAL"])
    _mutate_parameters(donor.specimen)
    _mutate_episodic(donor.specimen)

    host = transplant_parameters(donor, birth)
    donor_digest = causal_state_digest(donor.specimen)
    host_digest = causal_state_digest(host.specimen)

    assert host_digest["adaptive.parameters"] == donor_digest["adaptive.parameters"]
    assert host_digest["adaptive.longterm_M"] == donor_digest["adaptive.longterm_M"]
    # lo NO transplantado se queda como nació
    assert host_digest["adaptive.episodic_buffer"] == birth.digest["adaptive.episodic_buffer"]
    assert host_digest["adaptive.baseline"] == birth.digest["adaptive.baseline"]


def test_a_restore_returns_initial_parameters_and_keeps_the_rest():
    birth = snapshot()
    learned = birth.twin("NORMAL", REGIME_INTERVENTIONS["NORMAL"])
    _mutate_parameters(learned.specimen)
    _mutate_episodic(learned.specimen)
    _mutate_baseline_value(learned.specimen)

    restored = restore_parameters(learned, birth)
    restored_digest = causal_state_digest(restored.specimen)
    learned_digest = causal_state_digest(learned.specimen)

    assert restored_digest["adaptive.parameters"] == birth.digest["adaptive.parameters"]
    assert restored_digest["adaptive.episodic_buffer"] == learned_digest["adaptive.episodic_buffer"]
    assert restored_digest["adaptive.baseline"] == learned_digest["adaptive.baseline"]


def test_the_transplant_host_is_frozen():
    birth = snapshot()
    donor = birth.twin("NORMAL", REGIME_INTERVENTIONS["NORMAL"])
    assert transplant_parameters(donor, birth).specimen.adaptive_freeze.enabled
    assert restore_parameters(donor, birth).specimen.adaptive_freeze.enabled


# --- La intervención declara lo que toca ------------------------------------

def test_an_intervention_carries_its_own_provenance():
    one = Intervention("i1", "target", Phase.ACQUISITION, {"a": 1}, {"a": 2}, "por qué")
    same = Intervention("i1", "target", Phase.ACQUISITION, {"a": 1}, {"a": 2}, "otra prosa")
    other = Intervention("i1", "target", Phase.ACQUISITION, {"a": 1}, {"a": 3}, "por qué")
    assert one.provenance == same.provenance      # la prosa no cambia la identidad
    assert one.provenance != other.provenance     # lo que se toca, sí


def test_every_regime_declares_what_it_changes():
    for name, intervention in REGIME_INTERVENTIONS.items():
        assert intervention.rationale
        if name != "NORMAL":
            assert intervention.before and intervention.after


# --- Estadística -------------------------------------------------------------

def test_one_pair_dominating_the_sign_is_detected():
    """El monstruo de 97 consumos tiene que salir como sensibilidad, no como
    efecto de tratamiento."""
    dominated = PairedResult("d", [1.0, -1.0, 1.0, -1.0, 97.0])
    assert dominated.mean > 0
    assert dominated.dominated_by_one_pair

    solid = PairedResult("s", [3.0, 4.0, 5.0, 3.5, 4.5])
    assert not solid.dominated_by_one_pair


def test_between_pair_variance_is_reported():
    components = variance_components({
        "N": [1.0, 100.0, 2.0], "F": [1.1, 100.2, 2.1],
    })
    assert components["between_fraction"] > 0.99   # la inicialización lo domina


# --- El portador: theta separado de M ---------------------------------------

def test_a_theta_transplant_leaves_M_at_birth():
    """`set_parameters` copia por nombre TODO lo de `get_parameters()`, y `M`
    está ahí dentro aunque el optimizador no la gobierne. Sin separar, un
    transplante sólo permite concluir `(theta, M) -> capacidad`."""
    from terrario.lab.causal_bench import Carrier, transplant

    birth = snapshot()
    donor = birth.twin("NORMAL", REGIME_INTERVENTIONS["NORMAL"])
    _mutate_parameters(donor.specimen)
    _mutate_longterm_M(donor.specimen)

    host = transplant(donor, birth, Carrier.THETA)
    host_digest = causal_state_digest(host.specimen)
    donor_digest = causal_state_digest(donor.specimen)

    assert host_digest["adaptive.parameters"] == donor_digest["adaptive.parameters"]
    assert host_digest["adaptive.longterm_M"] == birth.digest["adaptive.longterm_M"]
    assert host_digest["adaptive.longterm_M"] != donor_digest["adaptive.longterm_M"]


def test_an_M_transplant_leaves_theta_at_birth():
    from terrario.lab.causal_bench import Carrier, transplant

    birth = snapshot()
    donor = birth.twin("NORMAL", REGIME_INTERVENTIONS["NORMAL"])
    _mutate_parameters(donor.specimen)
    _mutate_longterm_M(donor.specimen)

    host = transplant(donor, birth, Carrier.M)
    host_digest = causal_state_digest(host.specimen)

    assert host_digest["adaptive.longterm_M"] == causal_state_digest(
        donor.specimen)["adaptive.longterm_M"]
    assert host_digest["adaptive.parameters"] == birth.digest["adaptive.parameters"]


def test_restore_is_symmetric_with_transplant():
    """Devolver theta inicial conservando M aprendida es la inversa exacta de
    transplantar theta conservando M inicial."""
    from terrario.lab.causal_bench import Carrier, restore

    birth = snapshot()
    learned = birth.twin("NORMAL", REGIME_INTERVENTIONS["NORMAL"])
    _mutate_parameters(learned.specimen)
    _mutate_longterm_M(learned.specimen)
    _mutate_baseline_value(learned.specimen)

    undone = restore(learned, birth, Carrier.THETA)
    undone_digest = causal_state_digest(undone.specimen)
    learned_digest = causal_state_digest(learned.specimen)

    assert undone_digest["adaptive.parameters"] == birth.digest["adaptive.parameters"]
    assert undone_digest["adaptive.longterm_M"] == learned_digest["adaptive.longterm_M"]
    assert undone_digest["adaptive.baseline"] == learned_digest["adaptive.baseline"]
