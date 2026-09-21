"""Contratos de la adquisición de distancia · cada gate con su fixture negativa.

La regla que gobierna este fichero: **un contrato que no puede fallar no es un
contrato**. Por cada propiedad que se exige hay un mundo construido a propósito
donde la propiedad es falsa, y se comprueba que el guardián la detecta.
"""

from __future__ import annotations

import numpy as np
import pytest

from terrario.level11.cue import ALL_CUES, CueSemantics, CueToken
from terrario.level11.world import ALL_OBSERVATIONS, Direction
from terrario.level12.agent import Level12Agent
from terrario.level12.experiment import BlindCore, run_seed
from terrario.level12.inherited import reconstruct
from terrario.level12.metrics import (
    ACCURACY_ORACLE, BS_IGNORANT, BS_JOINT_ORACLE, BS_ORACLE, ORACLE,
    ContextualDistanceModel, balanced_accuracy, body_association,
    body_association_envelope, delta_sensor_separation, direction_class_table,
    empirical_brier, joint_population_brier, max_oracle_deviation,
    population_brier, single_variable_probe,
)
from terrario.level12.proximity import (
    BayesDistanceOracle, ConstantDistance, OrdinalPrior, QualitativeDistanceModel,
)
from terrario.level12.reference import (
    ALL_TOKENS, DELTA_FAR, DELTA_NEAR, EMISSION, SEALED_MARGINAL, DistanceTruth,
    ProximityToken, build_reference, class_of, marginal,
)
from terrario.level12.stream import (
    DistanceObservation, DistanceTrainingRecord, build_stream, factorial_pairs,
    stream_with_false_factorization, train_distance,
)

SEMILLA = 80000011
SEM = CueSemantics.identity()


@pytest.fixture(scope="module")
def stream():
    return build_stream(SEMILLA, SEM)


@pytest.fixture(scope="module")
def aprendido(stream):
    h = QualitativeDistanceModel()
    train_distance(stream, h)
    return h


# --- el sensor y sus constantes selladas --------------------------------------

def test_cada_fila_de_emision_suma_uno():
    for d, fila in EMISSION.items():
        assert abs(sum(fila) - 1.0) < 1e-12, f"δ={d}"


def test_las_marginales_reproducen_las_selladas():
    """La enmienda condicionó el sensor a δ SIN mover las marginales. Si esto
    fallara, todo el oráculo preregistrado dejaría de aplicar."""
    for truth, sellada in SEALED_MARGINAL.items():
        assert marginal(truth) == pytest.approx(sellada, abs=1e-12)


def test_el_margen_no_se_genera_nunca(stream):
    deltas = {r.reference.delta for r in stream.records}
    assert 3 not in deltas and 0 not in deltas
    assert deltas <= set(DELTA_NEAR) | set(DELTA_FAR)


def test_el_sensor_depende_de_delta(stream):
    """L12-11. Sin esto la geometría sería decorativa: se podría borrar y el
    experimento daría exactamente lo mismo."""
    assert delta_sensor_separation(stream) >= 0.10


def test_un_sensor_ciego_a_delta_suspende_el_contrato():
    """La fixture negativa de L12-11."""
    ciego = build_stream(SEMILLA, SEM, delta_blind=True)
    assert delta_sensor_separation(ciego) < 0.10


def test_toda_lectura_ocurre_en_ambas_clases(stream):
    cobertura = stream.coverage()
    for s in ALL_TOKENS:
        assert cobertura[(DistanceTruth.NEAR, s)] > 0
        assert cobertura[(DistanceTruth.FAR, s)] > 0


# --- el aprendizaje ------------------------------------------------------------

def test_el_prior_es_un_medio_en_los_cuatro():
    h = QualitativeDistanceModel()
    assert h.posteriors() == (0.5, 0.5, 0.5, 0.5)


def test_cerca_solo_mueve_alfa_y_lejos_solo_beta():
    h = QualitativeDistanceModel()
    h.observe(ProximityToken.S1, DistanceTruth.NEAR)
    assert h.predict_near(ProximityToken.S1) == pytest.approx(2 / 3)
    assert h.posteriors()[0] == 0.5 and h.posteriors()[2] == 0.5
    h2 = QualitativeDistanceModel()
    h2.observe(ProximityToken.S1, DistanceTruth.FAR)
    assert h2.predict_near(ProximityToken.S1) == pytest.approx(1 / 3)


def test_predecir_no_escribe(aprendido):
    """El defecto del Nivel 1.0: la sonda modificaba lo sondeado. Aquí es
    imposible por tipo --arrays fijos, no diccionario-- y se comprueba igual."""
    antes = aprendido.digest()
    for s in ALL_TOKENS:
        aprendido.predict_near(s)
    assert aprendido.digest() == antes


def test_el_aprendiz_se_acerca_al_oraculo(aprendido):
    assert max_oracle_deviation(aprendido.predict_near) <= 0.10
    assert population_brier(aprendido.predict_near) <= 0.1480


def test_congelado_permanece_en_el_prior(stream):
    h = QualitativeDistanceModel(frozen=True)
    train_distance(stream, h)
    assert h.posteriors() == (0.5, 0.5, 0.5, 0.5)
    assert population_brier(h.predict_near) == BS_IGNORANT


# --- el oráculo ----------------------------------------------------------------

def test_el_oraculo_da_los_cuatro_posteriores_cerrados():
    o = BayesDistanceOracle()
    assert o.posteriors() == pytest.approx(ORACLE, abs=1e-12)


def test_el_oraculo_alcanza_ocho_cincuentaycinco():
    o = BayesDistanceOracle()
    assert population_brier(o.predict_near) == pytest.approx(8 / 55, abs=1e-12)
    assert balanced_accuracy(o.predict_near) == pytest.approx(4 / 5, abs=1e-12)


def test_el_techo_no_es_cero():
    """Lo genuinamente nuevo del 1.2: ni el mejor predictor acierta siempre."""
    assert BS_ORACLE > 0
    assert ACCURACY_ORACLE < 1.0


def test_el_ignorante_puntua_un_cuarto():
    assert population_brier(ConstantDistance(0.5).predict_near) == BS_IGNORANT


# --- el generador --------------------------------------------------------------

def test_el_factorial_esta_exactamente_balanceado():
    pares = factorial_pairs(2048)
    from collections import Counter
    assert set(Counter(pares).values()) == {256}


def test_la_direccion_no_predice_la_distancia(stream):
    """L12-5. Exacto, porque el balance factorial lo fija."""
    assert all(v == 0.5 for v in direction_class_table(stream).values())


def test_un_generador_confundido_en_direccion_suspende_el_contrato():
    malo = build_stream(SEMILLA, SEM, confound="direction")
    assert not all(v == 0.5 for v in direction_class_table(malo).values())


def test_el_cuerpo_no_predice_la_distancia(stream):
    """L12-6. NO es identidad muestral: el balance fija `P(D|G)`, pero los
    conteos dentro de cada observación fluctúan. Por eso, envelope nulo."""
    envelope = body_association_envelope(
        stream, rng=np.random.default_rng([SEMILLA, 25]), permutations=2000)
    assert body_association(stream) <= float(np.percentile(envelope, 99.9))


def test_un_generador_confundido_en_cuerpo_suspende_el_contrato():
    malo = build_stream(SEMILLA, SEM, confound="body")
    envelope = body_association_envelope(
        malo, rng=np.random.default_rng([SEMILLA, 25]), permutations=2000)
    assert body_association(malo) > float(np.percentile(envelope, 99.9))


def test_la_misma_senal_aparece_con_ambas_distancias(stream):
    visto = {(r.view.cue, r.truth) for r in stream.records}
    for c in ALL_CUES:
        assert (c, DistanceTruth.NEAR) in visto and (c, DistanceTruth.FAR) in visto


def test_la_misma_observacion_aparece_con_ambas_distancias(stream):
    visto = {(r.view.observation, r.truth) for r in stream.records}
    observaciones = {o for o, _ in visto}
    ambas = {o for o in observaciones
             if (o, DistanceTruth.NEAR) in visto and (o, DistanceTruth.FAR) in visto}
    assert len(ambas) >= 0.8 * len(observaciones)


def test_la_cobertura_puede_fallar():
    """El gate de dosis tiene que poder disparar, o no es un gate."""
    corto = build_stream(SEMILLA, SEM, n=64)
    assert corto.informative_minimum < 30


# --- el atajo del nombre -------------------------------------------------------

@pytest.mark.parametrize("orden", [(3, 2, 1, 0), (1, 3, 0, 2)])
def test_permutar_los_tokens_no_rompe_el_aprendizaje(orden):
    """El agente aprende de lo que le pasa, no de cómo se llaman las cosas."""
    base = build_stream(SEMILLA, SEM)
    permutados = [
        DistanceTrainingRecord(
            DistanceObservation(r.view.observation, r.view.cue,
                                ProximityToken(orden[int(r.view.sensor)])),
            r.truth, r.reference)
        for r in base.records]
    base.records = permutados
    h = QualitativeDistanceModel()
    train_distance(base, h)
    for k, destino in enumerate(orden):
        assert abs(h.predict_near(ProximityToken(destino)) - ORACLE[k]) <= 0.10


def test_un_prior_ordinal_suspende_el_contrato_de_permutacion():
    """La fixture negativa de L12-4: presuponer que `S3 > S2 > S1 > S0`."""
    orden = (3, 2, 1, 0)
    base = build_stream(SEMILLA, SEM)
    base.records = [
        DistanceTrainingRecord(
            DistanceObservation(r.view.observation, r.view.cue,
                                ProximityToken(orden[int(r.view.sensor)])),
            r.truth, r.reference)
        for r in base.records]
    h = OrdinalPrior()
    train_distance(base, h)
    peor = max(abs(h.predict_near(ProximityToken(orden[k])) - ORACLE[k])
               for k in range(4))
    assert peor > 0.10


# --- el control barajado --------------------------------------------------------

def test_barajar_el_sensor_destruye_la_informacion(stream):
    h = QualitativeDistanceModel()
    train_distance(stream, h, shuffle_rng=np.random.default_rng([SEMILLA, 24]))
    assert max_oracle_deviation(h.predict_near) > 0.30
    assert population_brier(h.predict_near) == pytest.approx(0.25, abs=0.01)


def test_barajar_sensor_y_verdad_JUNTOS_no_destruye_nada(stream, aprendido):
    """El defecto exacto del Nivel 1.1, replicado aquí para que no vuelva.

    Reordenar los registros enteros conserva cada pareja `(s, D)`: es un
    reetiquetado consistente y el control acabaría empatando con el brazo que
    controla. La delación es justamente ese empate.
    """
    rng = np.random.default_rng(1)
    reordenado = build_stream(SEMILLA, SEM)
    idx = rng.permutation(len(reordenado.records))
    reordenado.records = [reordenado.records[i] for i in idx]
    h = QualitativeDistanceModel()
    train_distance(reordenado, h)
    assert h.posteriors() == pytest.approx(aprendido.posteriors(), abs=1e-12)


# --- integración ----------------------------------------------------------------

@pytest.fixture(scope="module")
def agente(aprendido):
    return Level12Agent(reconstruct(SEMILLA), aprendido)


def test_cada_entrada_mueve_su_factor_y_solo_el_suyo(agente):
    p = single_variable_probe(agente)
    assert p.by_input["o"]["B"] > 0.5 and p.by_input["o"]["Q"] == 0.0 and p.by_input["o"]["H"] == 0.0
    assert p.by_input["g"]["Q"] > 0.5 and p.by_input["g"]["B"] == 0.0 and p.by_input["g"]["H"] == 0.0
    assert p.by_input["s"]["H"] > 0.5 and p.by_input["s"]["B"] == 0.0 and p.by_input["s"]["Q"] == 0.0
    assert p.zeros_exact()


def test_la_composicion_triple_es_el_producto(agente):
    for o in ALL_OBSERVATIONS[:4]:
        for g in ALL_CUES:
            for s in ALL_TOKENS:
                for a in Direction:
                    jn, jf = agente.predict_joint(o, g, s, a)
                    base = agente.predict(o, g, a)
                    h = agente.predict_near(s)
                    assert jn == pytest.approx(base * h)
                    assert jf == pytest.approx(base * (1 - h))
                    assert jn + jf == pytest.approx(base)


def test_el_brier_conjunto_no_baja_del_techo(agente):
    jn, jf = joint_population_brier(agente, SEM)
    assert jn >= BS_JOINT_ORACLE and jf >= BS_JOINT_ORACLE


def test_solo_el_sensor_no_basta_para_la_composicion(aprendido):
    """`BS_distance` empata FULL y SENSOR_ONLY. Lo que los separa es esto."""
    completo = Level12Agent(reconstruct(SEMILLA), aprendido)
    ciego = Level12Agent(BlindCore(), aprendido, name="SENSOR_ONLY")
    assert population_brier(ciego.predict_near) == population_brier(completo.predict_near)
    assert joint_population_brier(ciego, SEM)[0] > 10 * joint_population_brier(completo, SEM)[0]


def test_la_accion_no_cambia_al_variar_el_sensor(agente):
    """`π_1.2(o,g,s) = π_1.1(o,g)`, comprobado y no sólo declarado."""
    for o in ALL_OBSERVATIONS:
        for g in ALL_CUES:
            elegidas = {agente.act(o, g, np.random.default_rng(7))
                        for _ in ALL_TOKENS}
            assert len(elegidas) == 1


# --- factorización falsa ---------------------------------------------------------

def _stream_con_factorizacion_falsa(seed: int):
    """La MISMA fixture que evalúa `L12-9` en el guion de campaña.

    Vivía aquí duplicada. Dos definiciones del mismo mundo falso son dos gates
    con el mismo número: si una se toca y la otra no, el contrato y el informe
    dejan de hablar de lo mismo sin que nada lo señale.
    """
    return stream_with_false_factorization(seed, SEM)


def test_la_fixture_falsa_anula_el_modelo_marginal():
    falso = _stream_con_factorizacion_falsa(SEMILLA)
    h = QualitativeDistanceModel()
    train_distance(falso, h)
    assert empirical_brier(h.predict_near, falso.records) == pytest.approx(0.25, abs=0.01)
    for p in h.posteriors():
        assert abs(p - 0.5) < 0.05


def test_la_baseline_contextual_recupera_todo_en_la_fixture_falsa():
    falso = _stream_con_factorizacion_falsa(SEMILLA)
    ctx = ContextualDistanceModel()
    for r in falso.records:
        ctx.observe(r.view.sensor, r.view.cue, r.truth)
    bs = sum((ctx.predict(r.view.sensor, r.view.cue)
              - (1.0 if r.truth is DistanceTruth.NEAR else 0.0)) ** 2
             for r in falso.records) / len(falso.records)
    assert bs == pytest.approx(8 / 55, abs=0.015)


def test_en_el_mundo_nominal_el_contextual_no_gana(stream, aprendido):
    """El contraste que hace informativa a la fixture: si el contextual ganara
    también aquí, el gate no estaría detectando la falsa factorización sino
    premiando la flexibilidad."""
    ctx = ContextualDistanceModel()
    for r in stream.records:
        ctx.observe(r.view.sensor, r.view.cue, r.truth)
    marginal_bs = empirical_brier(aprendido.predict_near, stream.records)
    ctx_bs = sum((ctx.predict(r.view.sensor, r.view.cue)
                  - (1.0 if r.truth is DistanceTruth.NEAR else 0.0)) ** 2
                 for r in stream.records) / len(stream.records)
    assert ctx_bs > marginal_bs - 0.005


# --- pasividad y reproducibilidad -------------------------------------------------

def test_medir_no_deja_huella(aprendido, agente):
    antes = aprendido.digest()
    population_brier(agente.predict_near)
    max_oracle_deviation(agente.predict_near)
    balanced_accuracy(agente.predict_near)
    single_variable_probe(agente)
    joint_population_brier(agente, SEM)
    assert aprendido.digest() == antes


def test_las_semillas_del_nivel_12_no_pisan_las_anteriores():
    usadas = set(range(20260919, 20260951)) | {31415926} \
        | set(range(31415927, 31415959)) | set(range(70000019, 70000034))
    nuevas = set(range(80000011, 80000019))
    assert not (nuevas & usadas)


# --- L12-9 · el gate de falsabilidad tiene que poder caer ------------------------

def test_el_gate_de_falsabilidad_cae_en_el_mundo_nominal(monkeypatch):
    """Si `L12-9` aprobara también con el mundo nominal, no estaría detectando
    la factorización falsa: estaría midiendo que el contextual es flexible."""
    from terrario.level12 import experiment

    monkeypatch.setattr(experiment, "stream_with_false_factorization",
                        lambda seed, semantics: build_stream(seed, semantics))
    marginal_bs, _ = experiment._false_factorization(SEMILLA, SEM)
    assert abs(marginal_bs - BS_IGNORANT) > experiment.FALSE_FIXTURE_TOLERANCE
