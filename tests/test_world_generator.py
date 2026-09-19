"""El generador de mundos diagnósticos se falsea a sí mismo.

Tres capas, de la más barata a la más cara:

1. Estructura: exigente y control difieren en exactamente un eje; el conjunto
   funde por el máximo; el canal 3 sigue oculto en el runtime real.
2. Física: cada tipo de puerta produce el delta que la economía declara, y la
   inversión los cruza. Esta capa no existía en la primera versión y por eso
   la puerta mala pagó +6 durante una hora sin que la clave lo notara.
3. Exigencia: el oráculo completo resuelve cada mundo, el oráculo sin la
   facultad que el eje exige cae, y ese mismo oráculo resuelve el control.
"""

from __future__ import annotations

import pytest

from terrario.lab import world_generator as gen
from terrario.lab import world_oracles as orc

CAPS = sorted(gen.DEMAND_OF)


# --- 1 · estructura ----------------------------------------------------------

def test_channel_3_is_hidden_in_the_real_runtime():
    assert gen.channel_3_is_hidden()


@pytest.mark.parametrize("cap", CAPS)
def test_control_differs_from_demanding_in_exactly_its_axis(cap):
    axis, _ = gen.DEMAND_OF[cap]
    d = gen.world_for([cap], seed=1)
    c = gen.control_for([cap], cap, seed=1)
    assert gen.axis_difference(d.demand, c.demand) == (axis,)
    assert getattr(c.demand, axis) == getattr(gen.OFF, axis)


def test_a_set_of_capabilities_merges_by_the_most_demanding_value():
    d = gen.demand_for(["EPMEM-A1", "LTMEM-A1", "PLAST-A1"])
    assert d.delay == 5 and d.distractors == 3 and d.inversion == 0.3
    assert d.hidden is True


def test_a_pinned_axis_cannot_be_merged_away():
    """HOMEO-A1 necesita `hidden=False` para que `modulation` signifique algo:
    si las puertas no se distinguen a la vista, el organismo no puede elegir la
    segura y la métrica mide una moneda. Antes, la fusión por máximo se lo
    llevaba en silencio y un test lo daba por bueno."""
    with pytest.raises(ValueError, match="incompatibles"):
        gen.demand_for(["EPMEM-A1", "HOMEO-A1"])
    # Sola sigue funcionando, y con las puertas distinguibles.
    w = gen.world_for(["HOMEO-A1"], seed=3)
    st = w.stations[0]
    up = w.scenario["objects"][st.up_id]["channels"][:3]
    down = w.scenario["objects"][st.down_id]["channels"][:3]
    assert up != down


def test_control_of_one_capability_in_a_set_keeps_the_others_on():
    caps = ["EPMEM-A1", "PLAST-A1"]
    c = gen.control_for(caps, "PLAST-A1", seed=1)
    assert c.demand.inversion is None and c.demand.delay == 5


@pytest.mark.parametrize("cap", CAPS)
@pytest.mark.parametrize("seed", [0, 3, 9])
def test_same_seed_same_station_content_when_the_axis_does_not_touch_it(cap, seed):
    """Esto sólo probaba EPMEM-A1, uno de los tres ejes que no consumían azar
    de más, y por eso pasaba. Generalizado, fallaba en `distractors`,
    `sequence`, `risk` y `novelty`: el eje corría el flujo compartido y
    regeneraba `designated`, que ningún eje debe tocar."""
    d = gen.world_for([cap], seed=seed)
    c = gen.control_for([cap], cap, seed=seed)
    assert [s.designated for s in d.stations] == [s.designated for s in c.stations]


@pytest.mark.parametrize("cap", CAPS)
def test_demanding_and_control_have_the_same_metabolic_budget(cap):
    """«Difieren en exactamente una dimensión» tiene que valer también en la
    física. `delay` y `sequence` alargan el pasillo y con él la vida: EPMEM
    gastaba 19.80 de 20.00 iniciales y su control 10.20, así que el brazo
    exigente moría por caminar y el contraste de memoria era un contraste de
    viabilidad. `axis_difference` no podía verlo: compara el `Demand`, no el
    mundo."""
    d = gen.world_for([cap], seed=0)
    c = gen.control_for([cap], cap, seed=0)
    assert d.duration == c.duration
    assert d.economy.step_energy_cost == c.economy.step_energy_cost
    assert d.economy.initial_energy == c.economy.initial_energy


def test_distractors_need_room():
    with pytest.raises(ValueError):
        gen.generate(gen.Demand(delay=1, distractors=2), seed=0)


def test_cue_leaves_the_window_only_when_delay_exceeds_the_radius():
    from terrario.world.transition import build_world_state
    from terrario.world.state import WorldStateManager

    def cue_visible_at_choice(delay: int) -> bool:
        w = gen.generate(gen.Demand(delay=delay), seed=0, stations=1)
        st = w.stations[0]
        sc = dict(w.scenario, agent_start={"pos": [gen.ROW_PATH, st.door_column], "energy": 1.0})
        m = WorldStateManager(build_world_state(sc), 10, 10.0, 0.0, True)
        obs = m.get_observation(0, gen.VIEW_RADIUS, gen.NUM_CHANNELS)
        marks = obs.channels[2][obs.channels[0] > 0].tolist()
        return any(abs(mk - gen.MARK_CUE) < 1e-6 for mk in marks)

    assert cue_visible_at_choice(1) and cue_visible_at_choice(2)
    assert not cue_visible_at_choice(3) and not cue_visible_at_choice(5)


def test_hidden_doors_are_identical_to_the_organism_and_visible_ones_are_not():
    hidden = gen.generate(gen.Demand(hidden=True), seed=0, stations=1).scenario["objects"]
    shown = gen.generate(gen.Demand(hidden=False), seed=0, stations=1).scenario["objects"]
    st = gen.generate(gen.Demand(hidden=True), seed=0, stations=1).stations[0]
    up, dn = hidden[st.up_id]["channels"], hidden[st.down_id]["channels"]
    assert up[:3] == dn[:3] and up[3] != dn[3]
    up, dn = shown[st.up_id]["channels"], shown[st.down_id]["channels"]
    assert up[:3] != dn[:3]


def test_novelty_produces_novel_stations_at_about_the_declared_rate():
    n = sum(s.novel for seed in range(20)
            for s in gen.generate(gen.Demand(novelty=0.3), seed=seed, stations=8).stations)
    assert 0.2 <= n / 160 <= 0.4
    w = gen.generate(gen.Demand(novelty=1.0), seed=0, stations=40)
    for st in w.stations:
        assert st.novel and st.designated_ch3 in (gen.CH3_GOOD, gen.CH3_BAD)
        assert w.scenario["objects"][st.cue_ids[0]]["channels"][1] == gen.MARK_NOVEL
    # la consecuencia es irreducible: dado el percepto, ambas puertas son moneda al aire
    good_up = sum(st.designated_ch3 == gen.CH3_GOOD for st in w.stations) / 40
    assert 0.3 <= good_up <= 0.7
    assert any(st.designated_ch3 != st.other_ch3 for st in w.stations)
    assert any(st.designated_ch3 == st.other_ch3 for st in w.stations)


# --- 2 · física ---------------------------------------------------------------

@pytest.mark.parametrize("cap", CAPS)
def test_each_door_kind_yields_the_declared_delta(cap):
    w = gen.world_for([cap], seed=0)
    e = w.economy
    assert gen.door_deltas(w) == {"good": e.gain, "bad": -e.loss, "safe": e.safe, "inert": 0.0}


def test_inversion_crosses_good_and_bad_and_leaves_safe_alone():
    w = gen.world_for(["PLAST-A1"], seed=0)
    e = w.economy
    assert w.inversion_step is not None
    assert gen.door_deltas(w, step=w.inversion_step - 1) == {"good": e.gain, "bad": -e.loss, "safe": e.safe, "inert": 0.0}
    assert gen.door_deltas(w, step=w.inversion_step) == {"good": -e.loss, "bad": e.gain, "safe": e.safe, "inert": 0.0}


def test_the_full_oracle_collects_the_declared_energy():
    """La clave y la física cuentan lo mismo: cada acierto vale +gain."""
    w = gen.world_for(["EPMEM-A1"], seed=2)
    o = orc.Oracle(w, orc.FULL, seed=2)
    outs = orc.run_life(w, o)
    eaten = [x.energy_delta for x in outs if x.target is not None and x.effects]
    assert len(eaten) == len(w.stations)
    assert all(abs(d - (w.economy.gain - w.economy.step_energy_cost)) < 1e-6 for d in eaten)


# --- 3 · exigencia --------------------------------------------------------------

@pytest.mark.parametrize("cap", [c for c in CAPS if orc.FACULTY_OF_AXIS[gen.DEMAND_OF[c][0]]])
def test_the_world_demands_the_faculty_its_axis_names(cap):
    v = orc.verdict_for(cap, seeds=range(4))
    assert v.demands, v


def test_novelty_has_no_faculty_and_says_so():
    v = orc.verdict_for("UNC-A1", seeds=range(2))
    assert v.faculty is None and v.demands is None and v.full_on_demanding == 1.0


def test_a_combined_world_needs_every_faculty_at_once():
    caps = ["EPMEM-A1", "TEMP-A1", "PLAST-A1"]
    accs = {}
    for seed in range(3):
        w = gen.world_for(caps, seed=seed)
        accs.setdefault("full", []).append(orc.life_score(w, orc.FULL, seed=seed).accuracy)
        for fac in ("memory", "order", "inversion"):
            accs.setdefault(fac, []).append(orc.life_score(w, orc.without(fac), seed=seed).accuracy)
    mean = lambda xs: sum(xs) / len(xs)
    assert mean(accs["full"]) == 1.0
    for fac in ("memory", "order", "inversion"):
        assert mean(accs[fac]) <= 0.8, (fac, accs[fac])


def test_score_records_viability_not_only_accuracy():
    """Un cadáver no puede puntuar mejor que un superviviente sin que se note.
    `life_score` recibía la traza con `terminated` y la energía de cada paso y
    devolvía sólo aciertos; medido sobre 420 vidas de oráculo, 7 vidas muertas
    puntuaban accuracy 1.0."""
    w = gen.world_for(["LEARN-A1"], seed=0)
    s = orc.life_score(w, orc.FULL, seed=0)
    assert s.viability is not None
    assert s.died is False and s.viability.survived
    assert s.viability.steps_lived > 0
    assert s.viability.min_energy <= s.viability.final_energy + 1e-9

    # Sin traza no se puede saber, y la puntuación lo dice en vez de suponerlo.
    bare = gen.score(w, [])
    assert bare.viability is None and bare.died is None
