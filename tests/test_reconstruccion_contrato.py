"""Un registro científico tiene que poder re-derivarse de lo que se guardó.

La identidad científica de un artefacto es un hash de su payload canónico. Si la
función que lo calcula vive en el código de hoy y el registro en el disco de
ayer, añadir un campo a un contrato rompe la identidad de todo lo ya escrito sin
que nada se queje: el códec materializa el campo con su valor por defecto al
releer, el payload canónico cambia, y el hash sellado deja de derivarse del
propio registro. Ocurrió, 347 veces, y se declaró en
`tests/fixtures/reconstruccion_ledger.json`.

Estas pruebas son las dos mitades del guardián:

  · la superficie de contratos está clavada — salta el día en que se añade el
    campo, sin base de datos, en cualquier árbol;
  · cada versión almacenada coincide con el acta — salta donde vive la raíz
    de datos, que es donde la historia puede moverse.

La mitad sin base de datos existe precisamente porque los árboles de trabajo no
llevan `.terrario/`: sin ella, el guardián estaría dormido justo donde se
escriben los contratos.
"""
from __future__ import annotations

import copy
import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from reconstruccion_check import (  # noqa: E402
    compare,
    contract_surface,
    contract_surface_hash,
    load_ledger,
    measure,
    reproduces,
)

#: Las claves que la discontinuidad declarada puede haber ganado. Cualquier otra
#: forma de divergencia —un valor distinto, una clave perdida, una lista de otra
#: longitud— no es crecimiento de esquema: es contenido que no cuadra, y no
#: entra en el acta sin que alguien lo mire.
CRECIMIENTO_DECLARADO = {
    "ANADIDA $.metrics[*].instrument_ref",
    "ANADIDA $.metrics[*].specification_hash",
    "ANADIDA $.metrics[*].calibration_report_id",
    "ANADIDA $.metrics[*].calibration_report_hash",
    "ANADIDA $.metrics[*].calibration_seed_set",
    "ANADIDA $.metrics[*].confirmatory_seed_set",
    "ANADIDA $.hypothesis_mapping",
    "ANADIDA $.hypothesis_mapping.conditions[*].agent_config",
}


def data_root() -> Path | None:
    """La raíz viva, si este árbol la tiene."""
    declared = os.environ.get("TERRARIO_DATA_ROOT")
    candidate = Path(declared) if declared else PROJECT_ROOT / ".terrario"
    return candidate if (candidate / "terrario.db").is_file() else None


@pytest.fixture(scope="module")
def ledger() -> dict:
    return load_ledger()


# --------------------------------------------------------------------------
# Mitad uno · sin base de datos. Salta el día en que se toca el contrato.
# --------------------------------------------------------------------------

def test_la_superficie_de_contratos_no_se_mueve_sin_redeclarar(ledger):
    """Añadir un campo a cualquier contrato cambia la identidad de lo ya escrito.

    Es la prueba que habría atrapado `instrument_ref` el día que se añadió, en
    vez de meses después al intentar re-derivar un protocolo bloqueado. No dice
    que el campo esté mal: dice que su coste está sin declarar.
    """
    esperado = ledger["superficie_de_contratos"]
    actual = contract_surface_hash()
    if actual != esperado:
        diferencias = []
        declarados = ledger["contratos"]
        vivos = contract_surface()
        for nombre in sorted(set(declarados) | set(vivos)):
            antes, ahora = set(declarados.get(nombre, ())), set(vivos.get(nombre, ()))
            if antes != ahora:
                diferencias.append(f"{nombre}: +{sorted(ahora - antes)} -{sorted(antes - ahora)}")
        pytest.fail(
            "la superficie de contratos cambió y la discontinuidad no se ha re-declarado:\n  "
            + "\n  ".join(diferencias)
            + "\n\nUn campo nuevo cambia el payload canónico de TODO registro histórico al releerlo."
            "\nO el campo es ausente-equivalente y se poda del payload científico —quitar la"
            "\nclave cuando vale None, para que un registro sin ella hashee como antes de que"
            "\nexistiera— o se acepta la discontinuidad y se vuelve a declarar:"
            "\n  python scripts/reconstruccion_check.py --root <raíz> --write"
            "\ny se explica en docs/INFORME_RECONSTRUCCION_PREREGISTRO_01.md")


def test_el_acta_declara_solo_crecimiento_aditivo_de_esquema(ledger):
    """Lo declarado es esquema que creció, no contenido que no cuadra.

    Distinguirlos importa: un campo añadido deja intacto lo que el registro
    dice; un valor distinto significaría que el payload guardado y el objeto que
    produce el códec ya no afirman lo mismo, y eso no es una discontinuidad
    declarable sino corrupción.
    """
    inesperadas = {}
    for version_id, entrada in ledger["registros"].items():
        rareza = set(entrada["divergencia"]) - CRECIMIENTO_DECLARADO
        if rareza:
            inesperadas[version_id] = sorted(rareza)
    assert not inesperadas, (
        "el acta declara divergencias que no son crecimiento aditivo de esquema; "
        f"eso es contenido que no cuadra, no un campo nuevo: {inesperadas}")


def test_el_acta_no_declara_registros_que_se_rederivan(ledger):
    """Nada entra en el acta salvo lo que efectivamente no se re-deriva."""
    sanos = [v for v, e in ledger["registros"].items()
             if not e["divergencia"] and e["almacenado"] == e["recomputado"]]
    assert not sanos, f"filas del acta que sí se re-derivan y sobran: {sanos}"


def test_el_conjunto_de_reglas_de_validacion_esta_clavado_a_su_version():
    """`POLICY_VERSION` no se movió cuando el conjunto de reglas sí lo hizo.

    Medido el 2026-09-21 sobre los 141 bundles sellados: tres conjuntos de
    reglas distintos comparten la cadena `preregistration-policy-1.0`. Los
    sellados más antiguos no conocían `PR-INSTRUMENT-001`; 58 tampoco conocían
    `PR-CL7-001`. Como `validation_policy` es uno de los diez componentes del
    manifiesto raíz y se calcula del código vivo —no del registro—, el bundle
    no se re-deriva aunque el borrador esté intacto. Esta es la segunda causa,
    y no hay códec que pueda arreglarla: la entrada que derivó no está guardada.

    La versión declarada queda clavada al contenido que nombra. Añadir una regla
    sin mover `POLICY_VERSION` pone esto en rojo.
    """
    from terrario.lab.persistence.canonical import content_hash
    from terrario.lab.preregistration.validation import POLICY_VERSION, RULES

    assert POLICY_VERSION == "preregistration-policy-1.0"
    assert {rule.rule_id for rule in RULES} >= {"PR-INSTRUMENT-001", "PR-CL7-001"}
    assert content_hash(RULES) == (
        "a0788f71cb72cbbacc6b8e435238589da2e8123c64525bc02b266da94dca99d3"), (
        "el conjunto de reglas de validación cambió sin mover POLICY_VERSION. "
        "`validation_policy` entra en el manifiesto raíz de todo bundle, así que un "
        "conjunto nuevo bajo la misma versión deja irreproducibles los 141 sellados "
        "y no lo dice. Mueve POLICY_VERSION y clava aquí el hash nuevo.")


# --------------------------------------------------------------------------
# Mitad dos · el guardián contra sí mismo. Un criterio que sólo pasa tampoco
# es un criterio: cada código de fallo se demuestra con su mutante.
# --------------------------------------------------------------------------

@pytest.fixture
def medida(ledger):
    """Una medida sintética que reproduce exactamente lo declarado, más un sano."""
    value = copy.deepcopy(ledger["registros"])
    value["version-sano"] = {
        "artifact_id": "sano", "kind": "ExperimentDraft", "form": "draft",
        "schema_version": "terrario.lab.experiment-draft/v1", "locked": False,
        "almacenado": "a" * 64, "recomputado": "a" * 64, "divergencia": []}
    return value


def test_una_medida_que_coincide_con_el_acta_pasa(medida, ledger):
    assert compare(medida, ledger) == []


@pytest.mark.parametrize("nombre,mutacion,codigo", [
    ("registro nuevo que no se re-deriva",
     lambda m, l: m.update({"version-nuevo": {
         "artifact_id": "n", "kind": "Preregistration", "form": "draft",
         "schema_version": "terrario.lab.preregistration/v1", "locked": False,
         "almacenado": "b" * 64, "recomputado": "c" * 64,
         "divergencia": ["ANADIDA $.metrics[*].umbral"]}}),
     "DIVERGENCIA_NO_DECLARADA"),
    ("hash almacenado reescrito",
     lambda m, l: m.__setitem__(next(iter(l["registros"])),
                                {**m[next(iter(l["registros"]))], "almacenado": "d" * 64}),
     "HISTORIA_REESCRITA"),
    ("reconstrucción movida por un contrato",
     lambda m, l: m.__setitem__(next(iter(l["registros"])),
                                {**m[next(iter(l["registros"]))], "recomputado": "e" * 64}),
     "RECONSTRUCCION_MOVIDA"),
    ("forma de divergencia distinta",
     lambda m, l: m.__setitem__(next(iter(l["registros"])),
                                {**m[next(iter(l["registros"]))], "divergencia": ["VALOR $.metrics[*].unit"]}),
     "FORMA_DE_DIVERGENCIA_CAMBIADA"),
    ("registro del acta desaparecido",
     lambda m, l: m.pop(next(iter(l["registros"]))),
     "REGISTRO_AUSENTE"),
    ("el acta declara algo que hoy se re-deriva",
     lambda m, l: m.__setitem__(next(iter(l["registros"])),
                                {**m[next(iter(l["registros"]))], "divergencia": [],
                                 "recomputado": m[next(iter(l["registros"]))]["almacenado"]}),
     "ACTA_OBSOLETA"),
    ("fila borrada del acta a mano",
     lambda m, l: l["registros"].pop(next(iter(l["registros"]))),
     "DIVERGENCIA_NO_DECLARADA"),
])
def test_el_guardian_nombra_cada_forma_de_romperse(medida, ledger, nombre, mutacion, codigo):
    mutado = copy.deepcopy(ledger)
    mutacion(medida, mutado)
    fallos = compare(medida, mutado)
    assert fallos, f"el mutante «{nombre}» pasó desapercibido"
    assert any(fallo.startswith(codigo) for fallo in fallos), f"{nombre}: esperaba {codigo}, salió {fallos[:2]}"


# --------------------------------------------------------------------------
# Mitad tres · lo que se escriba a partir de hoy sí se re-deriva.
# --------------------------------------------------------------------------

def test_un_preregistro_escrito_hoy_se_rederiva_de_lo_que_se_guardo(tmp_path):
    """La invariante hacia adelante, sobre la ruta real de sellado.

    Se crea un borrador y se sella su bundle en una raíz nueva, y se corre el
    MISMO comprobador que audita la raíz viva. Cero divergencias: lo que se
    escribe hoy vuelve a salir de lo que se guardó.
    """
    from terrario.lab.api import LabAPI
    from tests.test_preregistration_core import approve_upstream, create_request, sources

    root = tmp_path / ".terrario"
    api = LabAPI(Path("."), data_root=root)
    experiment, matrix = sources(api)
    status, created = api.dispatch("POST", "/api/v1/preregistrations", create_request(experiment, matrix))
    assert status == 201
    approve_upstream(api, experiment)
    status, candidate = api.dispatch("POST", "/api/v1/preregistrations/PR-CORE-1/prepare-review", {
        "expected_hash": created["data"]["scientific_hash"], "reason": "sellar para medir reconstrucción"})
    assert status == 201

    medido = measure(root)
    formas = {(x["kind"], x["form"]) for x in medido.values()}
    assert ("Preregistration", "draft") in formas and ("Preregistration", "bundle") in formas
    rotos = {version_id: record["divergencia"] or f"{record['almacenado']} != {record['recomputado']}"
             for version_id, record in medido.items() if not reproduces(record)}
    assert not rotos, f"un registro escrito ahora mismo ya no se re-deriva: {rotos}"


# --------------------------------------------------------------------------
# Mitad cuatro · la raíz viva, donde la historia puede moverse.
# --------------------------------------------------------------------------

def test_cada_registro_almacenado_coincide_con_el_acta(ledger):
    root = data_root()
    if root is None:
        pytest.skip(
            "este árbol no lleva raíz de datos; la mitad con base de datos se corre donde vive:\n"
            "  TERRARIO_DATA_ROOT=<ruta>/.terrario pytest tests/test_reconstruccion_contrato.py\n"
            "  python scripts/reconstruccion_check.py --root <ruta>/.terrario")
    fallos = compare(measure(root), ledger)
    assert not fallos, "\n".join(["la reconstrucción de la raíz viva no coincide con lo declarado:"] + fallos[:30])
