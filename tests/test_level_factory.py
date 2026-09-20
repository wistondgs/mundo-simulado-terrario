"""Contratos de la fábrica · cada comprobador con lo que lo hace fallar.

Un comprobador que sólo puede aprobar es exactamente el defecto que esta
fábrica dice cazar. Así que aquí cada uno tiene su fixture negativa, y dos de
ellos tienen además su regresión histórica: el commit real, anterior a la
reparación, donde el defecto existía.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml

from factory.catalog import Catalog, CatalogError
from factory.gates import implemented_gates, reconcile, sealed_gates
from factory.seeds import Campaign, SeedRegistry
from factory.vacuity import scan_source

RAIZ = Path(__file__).resolve().parent.parent
L14 = Path("/home/wis/level14-binding-01")


def _catalogo(nodos: list[dict], tmp_path: Path) -> Catalog:
    p = tmp_path / "c.yaml"
    p.write_text(yaml.safe_dump({"capabilities": nodos}), encoding="utf-8")
    return Catalog.load(p)


# ── catálogo ─────────────────────────────────────────────────────────────

def test_el_catalogo_real_carga_y_es_acíclico():
    c = Catalog.load()
    assert c.nodes["level14"].verified
    assert c.holds("level14") == {"sensorimotor", "direction", "proximity", "binding"}


def test_la_composicion_se_deduce_del_grafo_y_no_se_declara():
    """El hallazgo que se hizo a mano tras 1.4, ahora como consulta.

    `change_detection` exige `binding` y `one_tick_memory`; el primero está en
    el árbol de 1.4 y el segundo en el de la fusión, y ningún árbol tiene los
    dos. No es un decimal todavía.
    """
    p = Catalog.load().plan()
    assert "change_detection" not in p.ready
    assert p.needs_composition["change_detection"] == ("fusion_hm", "level14")


def test_un_ciclo_de_dependencias_suspende_la_carga(tmp_path):
    with pytest.raises(CatalogError, match="ciclo"):
        _catalogo([
            {"id": "a", "name": "A", "status": "PROPOSED", "acquires": "x",
             "requires": ["y"]},
            {"id": "b", "name": "B", "status": "PROPOSED", "acquires": "y",
             "requires": ["x"]},
        ], tmp_path)


def test_una_capacidad_que_nadie_adquiere_suspende_la_carga(tmp_path):
    """La propuesta nombraba `multiple_references` sin definirla. Eso se ve."""
    with pytest.raises(CatalogError, match="que ningún nodo adquiere"):
        _catalogo([{"id": "a", "name": "A", "status": "PROPOSED",
                    "acquires": "x", "requires": ["fantasma"]}], tmp_path)


def test_exigir_y_prohibir_la_misma_capacidad_suspende_la_carga(tmp_path):
    with pytest.raises(CatalogError, match="exigido y prohibido"):
        _catalogo([
            {"id": "a", "name": "A", "status": "PROPOSED", "acquires": "x"},
            {"id": "b", "name": "B", "status": "PROPOSED", "acquires": "y",
             "requires": ["x"], "forbidden": ["x"]},
        ], tmp_path)


def test_una_composicion_no_puede_adquirir(tmp_path):
    with pytest.raises(CatalogError, match="sólo un decimal adquiere"):
        _catalogo([{"id": "f", "name": "F", "kind": "composition",
                    "status": "PROPOSED", "acquires": "x"}], tmp_path)


def test_el_estado_sin_su_artefacto_sale_como_hueco(tmp_path):
    c = _catalogo([{"id": "a", "name": "A", "status": "VERIFIED", "acquires": "x",
                    "artifacts": {"oracle": "abc", "implementation": "def"}}],
                  tmp_path)
    assert c.gaps()["a"] == ("DESIGNED:design", "AUDITED:audit", "VERIFIED:report")


def test_con_todos_los_artefactos_no_hay_hueco(tmp_path):
    """El contraste que hace informativo al caso anterior."""
    c = _catalogo([{"id": "a", "name": "A", "status": "VERIFIED", "acquires": "x",
                    "artifacts": {"design": "d", "audit": "a", "oracle": "o",
                                  "implementation": "i", "report": "r"}}],
                  tmp_path)
    assert "a" not in c.gaps()


def test_dos_hermanos_verificados_no_hacen_un_arbol(tmp_path):
    """La distinción sin la cual una fusión se declara resuelta sin estarlo.

    Las dos capacidades están verificadas, y aun así el nodo no está listo:
    verificado no es lo mismo que disponible en el mismo organismo.
    """
    hecho = {"design": "d", "audit": "a", "oracle": "o",
             "implementation": "i", "report": "r"}
    c = _catalogo([
        {"id": "a1", "name": "A1", "status": "VERIFIED", "acquires": "x",
         "artifacts": hecho},
        {"id": "a2", "name": "A2", "status": "VERIFIED", "acquires": "y",
         "artifacts": hecho},
        {"id": "c", "name": "C", "status": "PROPOSED", "acquires": "z",
         "requires": ["x", "y"]},
    ], tmp_path)
    plan = c.plan()
    assert "c" not in plan.ready and "c" not in plan.blocked
    assert plan.needs_composition["c"] == ("a1", "a2")


def test_cuando_un_solo_arbol_las_tiene_el_nodo_esta_listo(tmp_path):
    """El contraste: mismas capacidades, un solo árbol, y ya no hay fusión."""
    hecho = {"design": "d", "audit": "a", "oracle": "o",
             "implementation": "i", "report": "r"}
    c = _catalogo([
        {"id": "a1", "name": "A1", "status": "VERIFIED", "acquires": "x",
         "artifacts": hecho},
        {"id": "a2", "name": "A2", "status": "VERIFIED", "acquires": "y",
         "inherits": ["a1"], "artifacts": hecho},
        {"id": "c", "name": "C", "status": "PROPOSED", "acquires": "z",
         "requires": ["x", "y"]},
    ], tmp_path)
    assert "c" in c.plan().ready
    assert c.plan().needs_composition == {}


# ── semillas ─────────────────────────────────────────────────────────────

def test_el_registro_real_no_tiene_colisiones():
    assert SeedRegistry.load().collisions() == {}


def test_dos_bases_disjuntas_colisionan_por_sus_offsets():
    """El caso que un `range` mirado a ojo no ve, y que el registro sí ve."""
    r = SeedRegistry([
        Campaign("a", ((1000, 1008),), offsets=(10_000,)),
        Campaign("b", ((11000, 11008),)),
    ])
    assert r.collisions()[("a", "b")] == tuple(range(11000, 11008))


def test_sin_el_offset_las_mismas_bases_no_colisionan():
    r = SeedRegistry([Campaign("a", ((1000, 1008),)),
                      Campaign("b", ((11000, 11008),))])
    assert r.collisions() == {}


def test_el_bloque_reservado_esta_libre():
    r = SeedRegistry.load()
    inicio, fin = r.reserve(8, offsets=(7,))
    propuesto = set(range(inicio, fin)) | {s + 7 for s in range(inicio, fin)}
    assert not (propuesto & r.used())


# ── gates ────────────────────────────────────────────────────────────────

ORACULO = """
## 3 · Gates

| gate | criterio |
|---|---|
| **X-0** linaje | huellas idénticas |
| **X-1** pasividad | medir no escribe |
"""

MODULO_BIEN = '''
class R:
    def gates(self):
        return {"X-0 linaje": True, "X-1 pasividad": True}
'''

MODULO_MAL = '''
class R:
    def gates(self):
        return {"X-0 linaje": True, "X-1 sondas exactas": True}
'''


def test_el_inventario_conciliado_aprueba(tmp_path):
    (tmp_path / "o.md").write_text(ORACULO)
    (tmp_path / "m.py").write_text(MODULO_BIEN)
    assert reconcile(tmp_path / "o.md", tmp_path / "m.py").ok


def test_gastar_un_numero_sellado_en_otro_gate_suspende(tmp_path):
    """El defecto exacto de 1.4: `L14-11` sellado para pasividad, usado en las
    sondas."""
    (tmp_path / "o.md").write_text(ORACULO)
    (tmp_path / "m.py").write_text(MODULO_MAL)
    r = reconcile(tmp_path / "o.md", tmp_path / "m.py")
    assert not r.ok
    assert r.renamed == (("X-1", "pasividad", "sondas exactas"),)


def test_un_gate_sellado_que_no_se_evalua_suspende(tmp_path):
    (tmp_path / "o.md").write_text(ORACULO)
    (tmp_path / "m.py").write_text(
        'class R:\n    def gates(self):\n        return {"X-0 linaje": True}\n')
    assert reconcile(tmp_path / "o.md", tmp_path / "m.py").missing == ("X-1",)


def test_el_inventario_se_lee_del_AST_y_no_del_texto(tmp_path):
    """Un identificador nombrado en el docstring no cuenta como evaluado.

    El docstring real de `gates()` en 1.4 explica que `L14-11` estuvo mal
    usado: buscarlo por texto lo encontraría ahí.
    """
    (tmp_path / "m.py").write_text(
        'class R:\n    def gates(self):\n        """Antes X-9 estaba mal."""\n'
        '        return {"X-0 linaje": True}\n')
    assert implemented_gates(tmp_path / "m.py") == {"X-0": "linaje"}


@pytest.mark.skipif(not L14.exists(), reason="el árbol de 1.4 no está montado")
def test_regresion_historica_el_comprobador_caza_el_defecto_de_a4eef15(tmp_path):
    """Contra el commit real anterior a la reparación `68d852d`.

    Es la fixture negativa que ningún fixture inventado puede sustituir: el
    defecto existió, en este fichero, y el comprobador tiene que verlo.
    """
    blob = subprocess.run(["git", "show", "a4eef15:terrario/level14/experiment.py"],
                          cwd=L14, capture_output=True, text=True, check=True).stdout
    (tmp_path / "m.py").write_text(blob, encoding="utf-8")
    r = reconcile(L14 / "docs/LEVEL14_ORACULO_PREREGISTRADO.md", tmp_path / "m.py")
    assert r.missing == ("L14-1", "L14-4", "L14-6/7", "L14-9")
    assert r.renamed == (("L14-11", "pasividad", "probes exactos"),)


@pytest.mark.skipif(not L14.exists(), reason="el árbol de 1.4 no está montado")
def test_y_aprueba_el_commit_que_lo_reparo():
    """El contraste. Sin él, el caso anterior no demuestra que el comprobador
    discrimine: sólo que sabe decir que no."""
    assert reconcile(L14 / "docs/LEVEL14_ORACULO_PREREGISTRADO.md",
                     L14 / "terrario/level14/experiment.py").ok


# ── vacuidad ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("fuente,clase", [
    ("def t(a):\n    x = [1]\n    assert x == x\n", "self_comparison"),
    ("def t():\n    assert True\n", "constant"),
    ("def t():\n    assert all(y > 0 for y in [])\n", "empty_quantifier"),
    ('from pathlib import Path\n'
     'def t():\n    s = Path("terrario/level13/a.py").read_text()\n'
     '    assert "level12" not in s\n', "source_grep"),
])
def test_cada_clase_de_asercion_invacuable_se_detecta(fuente, clase):
    assert [f.kind for f in scan_source(fuente, "fx.py")] == [clase]


@pytest.mark.parametrize("fuente", [
    "def t(a, b):\n    assert a == b\n",
    'def t():\n    s = open("static/index.html").read()\n'
    '    assert "ANALYST" not in s\n',
    "def t():\n    assert all(y > 0 for y in datos())\n",
])
def test_lo_que_si_puede_fallar_no_se_señala(fuente):
    """Un linter con más ruido que señal se apaga, y entonces no comprueba nada.

    Leer texto es correcto cuando lo leído no es fuente Python: del HTML
    servido no hay árbol sintáctico que mirar.
    """
    assert scan_source(fuente, "fx.py") == []


def test_la_comparacion_con_llamada_se_separa_porque_mide_determinismo():
    """`fingerprint(mk()) == fingerprint(mk())` construye dos organismos y
    exige la misma huella: eso sí puede fallar."""
    hallazgos = scan_source("def t():\n    assert f(mk()) == f(mk())\n", "fx.py")
    assert [h.kind for h in hallazgos] == ["self_comparison_call"]


def test_la_fabrica_no_se_exime_a_si_misma():
    """Sus propios ficheros pasan por su propio comprobador."""
    from factory.vacuity import scan
    assert scan(RAIZ / "factory") == []
