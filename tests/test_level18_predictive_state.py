"""Contratos del mecanismo de estado predictivo.

El primero es la fixture del defecto encontrado: un autómata que, por faltarle una
entrada explícita, se declaraba a sí mismo absorbente.
"""

from __future__ import annotations

import numpy as np
import pytest

from terrario.level16.temporal import OBSERVATION_INDEX
from terrario.level17.efference import ALL_COMMANDS, EfferenceCopy
from terrario.level18.predictive_state import (
    PredictiveStateError, PredictiveStateModel, ROOT,
)

OBSERVACIONES = [(0, 0, 0, 0), (0, 0, 0, 1), (0, 0, 1, 0), (0, 1, 0, 0)]


def _tabla():
    return np.full((16, 4, 16), 4.0)


def _alimentar(modelo, pasos, justificado, semilla=7):
    """Alimentar con su propio criterio intacto.

    `justificado=True` produce datos donde la consecuencia depende de veras del
    comando ANTERIOR, así que la distinción paga su complejidad y sobrevive.
    `justificado=False` produce ruido: la distinción queda refutada y el mecanismo
    debe deshacerla.
    """
    generador = np.random.default_rng(semilla)
    anterior = 0
    for _ in range(pasos):
        antes = OBSERVACIONES[0]
        indice = int(generador.integers(4))
        comando = ALL_COMMANDS[indice]
        if justificado:
            despues = OBSERVACIONES[anterior % len(OBSERVACIONES)]
        else:
            despues = OBSERVACIONES[int(generador.integers(len(OBSERVACIONES)))]
        modelo.observe(antes, EfferenceCopy(comando), despues)
        anterior = indice
    return modelo


def _forzar_split(modelo, pasos=400):
    _alimentar(modelo, pasos, justificado=True)
    return modelo.refinements > 0 and len(modelo.states()) > 2


# --- el defecto: UNKNOWN ROUTE ≠ STAY ---------------------------------------

def test_entrar_en_un_hijo_no_deja_al_ser_atrapado_en_el():
    """La fixture del autómata absorbente.

    Tras separar la raíz, estar dentro de un hijo no puede impedir la transición
    que la dinámica heredada del padre sí define. Antes de la reparación, la
    ausencia de una entrada explícita se leía como «quédate», y el organismo
    entraba en un hijo y no salía nunca.
    """
    modelo = PredictiveStateModel(_tabla())
    modelo.begin()
    assert _forzar_split(modelo), "el criterio no separó; la fixture no aplica"

    hijos = [z for z in modelo.states() if modelo.parent_of(z) is not None]
    assert len(hijos) >= 2, modelo.states()

    destinos = set()
    for comando in range(4):
        for siguiente in range(16):
            destinos.add(modelo._next_state(hijos[0], comando, siguiente))
    assert destinos != {hijos[0]}, (
        "desde un hijo toda transición vuelve a él: el autómata es absorbente")


def test_un_hijo_hereda_la_dinamica_de_salida_de_su_padre():
    modelo = PredictiveStateModel(_tabla())
    modelo.begin()
    assert _forzar_split(modelo)
    for hijo in [z for z in modelo.states() if modelo.parent_of(z) is not None]:
        padre = modelo.parent_of(hijo)
        for comando in range(4):
            for siguiente in range(16):
                propia = (hijo, comando, siguiente) in modelo._routing
                if not propia:
                    assert modelo._next_state(hijo, comando, siguiente) == \
                        modelo._next_state(padre, comando, siguiente)


def test_la_funcion_de_transicion_es_semanticamente_total():
    """No hace falta materializar la tabla; hace falta que δ esté siempre definida."""
    modelo = PredictiveStateModel(_tabla())
    modelo.begin()
    _forzar_split(modelo)
    assert modelo.routing_is_total()


def test_la_raiz_sola_si_se_queda_en_si_misma():
    """Con un solo estado, toda transición conduce a él. Eso NO es absorción."""
    modelo = PredictiveStateModel(_tabla())
    modelo.begin()
    assert modelo.states() == [ROOT]
    assert all(modelo._next_state(ROOT, c, o) == ROOT
               for c in range(4) for o in range(16))


# --- los invariantes del oráculo ---------------------------------------------

def test_nace_siendo_1_7_bit_a_bit():
    tabla = np.random.default_rng(3).random((16, 4, 16)) * 10 + 1
    modelo = PredictiveStateModel(tabla)
    modelo.begin()
    peor = 0.0
    for observacion in OBSERVACIONES:
        indice = OBSERVATION_INDEX[observacion]       # NO la posición en la lista
        referencia = tabla[indice] / tabla[indice].sum(axis=1, keepdims=True)
        for j, comando in enumerate(ALL_COMMANDS):
            peor = max(peor, float(np.abs(
                modelo.predict(observacion, EfferenceCopy(comando)) - referencia[j]).max()))
    assert peor == 0.0, peor


def test_la_masa_heredada_se_conserva_tras_separar():
    tabla = _tabla()
    modelo = PredictiveStateModel(tabla)
    modelo.begin()
    _forzar_split(modelo)
    assert np.allclose(sum(modelo.inherited_mass()), tabla, rtol=0, atol=1e-9)


def test_la_lesion_devuelve_exactamente_a_1_7():
    tabla = np.random.default_rng(5).random((16, 4, 16)) * 10 + 1
    modelo = PredictiveStateModel(tabla)
    modelo.begin()
    _forzar_split(modelo)
    modelo.lesion()
    modelo.begin()
    peor = 0.0
    for observacion in OBSERVACIONES:
        indice = OBSERVATION_INDEX[observacion]
        referencia = tabla[indice] / tabla[indice].sum(axis=1, keepdims=True)
        for j, comando in enumerate(ALL_COMMANDS):
            peor = max(peor, float(np.abs(
                modelo.predict(observacion, EfferenceCopy(comando)) - referencia[j]).max()))
    assert peor == 0.0, peor
    assert modelo.states() == [ROOT]


def test_F1_una_distincion_refutada_se_deshace():
    """Enmienda 02 · con ruido, la separación deja de pagar y el mecanismo la
    retira. Un split irreversible es exactamente el defecto de `acb6b14`."""
    modelo = PredictiveStateModel(_tabla())
    modelo.begin()
    _alimentar(modelo, 600, justificado=False)
    assert modelo.refinements > 0, "no llegó a separar; la fixture no aplica"
    assert modelo.collapses > 0
    episodios = modelo.episodes()
    assert any(e["merged"] for e in episodios)


def test_F2_una_distincion_justificada_sobrevive():
    """Y no debe deshacer lo que la evidencia sí sostiene."""
    modelo = PredictiveStateModel(_tabla())
    modelo.begin()
    _alimentar(modelo, 600, justificado=True)
    assert modelo.refinements > 0
    assert len(modelo.states()) > 2, "colapsó una distinción que la evidencia sostiene"


def test_F3_la_fusion_conserva_la_masa_heredada():
    tabla = _tabla()
    modelo = PredictiveStateModel(tabla)
    modelo.begin()
    _alimentar(modelo, 600, justificado=False)
    assert np.allclose(sum(modelo.inherited_mass()), tabla, rtol=0, atol=1e-9)


def test_F4_tras_fusionar_no_queda_ninguna_ruta_colgante():
    modelo = PredictiveStateModel(_tabla())
    modelo.begin()
    _alimentar(modelo, 600, justificado=False)
    assert modelo.collapses > 0
    assert modelo.dangling_routes() == []
    assert modelo.routing_is_total()


def test_el_canal_solo_admite_una_copia_eferente():
    modelo = PredictiveStateModel(_tabla())
    for intruso in (0, "A0", None, ALL_COMMANDS[0]):
        with pytest.raises(PredictiveStateError):
            modelo.observe(OBSERVACIONES[0], intruso, OBSERVACIONES[1])


# --- el segundo defecto: puntuar sin seguir ---------------------------------

def test_F5_puntuar_un_banco_mueve_el_estado():
    """Predecir exige estar donde el estado recursivo dice.

    `probability` no muta a propósito --puntuar no debe aprender--, así que
    seguir la dinámica es del llamador. Cuando nadie lo hacía, un modelo con
    30 estados se puntuaba entero desde la raíz, cuya evidencia se había
    marchado a las hojas, y lo medido no era su organización.
    """
    modelo = PredictiveStateModel(_tabla())
    modelo.begin()
    _alimentar(modelo, 600, justificado=True)
    assert len(modelo.states()) > 2, "no separó; la fixture no aplica"

    modelo.begin()
    visitados = set()
    generador = np.random.default_rng(11)
    for _ in range(200):
        antes = OBSERVACIONES[0]
        indice = int(generador.integers(4))
        despues = OBSERVACIONES[indice % len(OBSERVACIONES)]
        modelo.probability(antes, EfferenceCopy(ALL_COMMANDS[indice]), despues)
        visitados.add(modelo._here)
        modelo.follow(EfferenceCopy(ALL_COMMANDS[indice]), despues)
    assert len(visitados) > 1, (
        f"puntuar 200 pasos no movió el estado: siempre {visitados}")


def test_F6_seguir_no_toca_ninguna_cuenta():
    """Y seguir tampoco puede aprender: sería evaluar entrenando."""
    modelo = PredictiveStateModel(_tabla())
    modelo.begin()
    _alimentar(modelo, 600, justificado=True)
    antes_updates = modelo.updates
    antes_splits = modelo.refinements
    antes_evidencia = [e.copy() for e in modelo._evidence.values()]

    for _ in range(50):
        modelo.follow(EfferenceCopy(ALL_COMMANDS[0]), OBSERVACIONES[1])
    assert modelo.updates == antes_updates
    assert modelo.refinements == antes_splits
    for previa, ahora in zip(antes_evidencia, modelo._evidence.values()):
        assert np.array_equal(previa, ahora)


def test_F7_la_organizacion_se_lee_con_la_misma_dinamica():
    """`organization` es lo que L18-6 trasplanta. Llevaba la versión absorbente
    que `1a35caa` reparó en `_next_state`: sin entrada explícita, se quedaba."""
    modelo = PredictiveStateModel(_tabla())
    modelo.begin()
    _alimentar(modelo, 600, justificado=True)
    assert len(modelo.states()) > 2, "no separó; la fixture no aplica"

    generador = np.random.default_rng(13)
    sondas = {f"s{i}": [(int(generador.integers(4)), int(generador.integers(16)))
                        for _ in range(6)] for i in range(8)}

    # No-vacuidad: si ninguna sonda pisara una ruta AUSENTE, el recorrido
    # absorbente y el de backoff coincidirían y el test pasaría sin probar nada.
    desconocidas = 0
    for pasos in sondas.values():
        modelo.begin()
        for comando, siguiente in pasos:
            if (modelo._here, comando, siguiente) not in modelo._routing:
                desconocidas += 1
            modelo._advance(comando, siguiente)
    modelo.begin()
    assert desconocidas > 0, "ninguna sonda pisó una ruta ausente: el test sería vacío"

    leido = modelo.organization(sondas)

    esperado = {}
    for nombre, pasos in sondas.items():
        modelo.begin()
        for comando, siguiente in pasos:
            modelo._advance(comando, siguiente)
        esperado[nombre] = modelo._here
    modelo.begin()
    assert leido == esperado


# --- falsificadores temporales de los dos defectos de medición ---------------

def test_A_seguir_el_estado_tiene_que_COMPRAR_verosimilitud():
    """Falsificador temporal, no de censo.

    Un test que cuente estados o compare huellas pasa con un scoring que nunca
    se mueve. Éste exige que SEGUIR el estado compre verosimilitud: sobre datos
    donde la consecuencia depende del comando anterior, puntuar recorriendo la
    dinámica tiene que batir estrictamente a puntuar clavado en la raíz.
    """
    modelo = PredictiveStateModel(_tabla())
    modelo.begin()
    _alimentar(modelo, 600, justificado=True)
    assert len(modelo.states()) > 2, "no separó; la fixture no aplica"

    banco = []
    generador = np.random.default_rng(23)
    anterior = 0
    for _ in range(300):
        indice = int(generador.integers(4))
        banco.append((OBSERVACIONES[0], ALL_COMMANDS[indice],
                      OBSERVACIONES[anterior % len(OBSERVACIONES)]))
        anterior = indice

    def perdida(siguiendo):
        modelo.begin()
        total = 0.0
        for antes, comando, despues in banco:
            total -= np.log(max(modelo.probability(
                antes, EfferenceCopy(comando), despues), 1e-300))
            if siguiendo:
                modelo.follow(EfferenceCopy(comando), despues)
        return total / len(banco)

    recorriendo = perdida(True)
    clavado = perdida(False)
    modelo.begin()
    assert recorriendo < clavado, (
        f"recorrer el estado no compró nada: {recorriendo:.6f} vs {clavado:.6f}; "
        "el scoring no se está moviendo")
