#!/usr/bin/env python
"""G2 — un registro científico tiene que poder re-derivarse de lo que se guardó.

El fallo que este gate previene no es que un hash esté mal calculado: es que la
función que lo calcula viva en el código de hoy y el registro en el disco de
ayer. Cuando se añade un campo a un contrato, el códec lo materializa con su
valor por defecto al releer un registro antiguo, el payload canónico cambia, y
la identidad científica que se selló deja de ser derivable del propio registro.
Nada falla: el borrador se relee, la verificación pasa —compara el manifiesto
ALMACENADO contra el hash ALMACENADO— y la enmienda que se construya encima
hereda campos que el protocolo bloqueado nunca comprometió, sin que el delta de
la enmienda los mencione.

Medido el 2026-09-21 sobre `.terrario/terrario.db`: 285 de 285 versiones de
preregistro y 62 de 147 borradores de experimento no se re-derivan.

Este comprobador recorre cada versión almacenada, la reconstruye con su códec,
recomputa su identidad científica, y la compara con la declarada en
`tests/fixtures/reconstruccion_ledger.json`. La discontinuidad histórica está
declarada ahí registro a registro, con su hash almacenado y su hash
recomputado: es el acta de lo que ya ocurrió, no una excepción que silencie.
Por eso el gate sigue teniendo dientes:

  · un registro nuevo que no se re-derive          → DIVERGENCIA_NO_DECLARADA
  · un campo nuevo en cualquier contrato           → RECONSTRUCCION_MOVIDA
                                                     (cambia el recomputado de
                                                      los 347 registros del acta)
  · un hash almacenado que cambie                  → HISTORIA_REESCRITA
  · un registro del acta que desaparezca           → REGISTRO_AUSENTE

    python scripts/reconstruccion_check.py               comprueba; sale != 0 si algo diverge
    python scripts/reconstruccion_check.py --write       re-declara la discontinuidad
    python scripts/reconstruccion_check.py --root RUTA   otra raíz de datos
    python scripts/reconstruccion_check.py --detalle     imprime las rutas que divergen

`--write` no es «arreglar»: reescribe el acta con lo que se mide hoy. Sólo se
corre cuando la diferencia se ha entendido y se quiere dejar declarada, y el
informe que la acompaña dice por qué. Regenerarlo para poner el gate en verde
es exactamente el fallo que existe para impedir.
"""

from __future__ import annotations

import argparse
import collections
import json
import sqlite3
import sys
import tempfile
from datetime import date
from pathlib import Path
from typing import Any, Callable, Iterator, Mapping

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.lab.persistence.canonical import content_hash, plain  # noqa: E402
from terrario.lab.persistence.codecs import (  # noqa: E402
    experiment_draft_from_payload,
    preregistration_draft_from_payload,
    world_draft_from_payload,
)

LEDGER = PROJECT_ROOT / "tests" / "fixtures" / "reconstruccion_ledger.json"
LEDGER_SCHEMA = "terrario.lab.reconstruction-ledger/v1"

BUNDLE_SCHEMA = "terrario.lab.preregistration-bundle/v1"

#: Kind almacenado → códec que lo relee, e identidad científica tal y como la
#: computó quien lo escribió. La identidad NO es uniforme y no se puede adivinar
#: desde el objeto: `PreregistrationDraft` y `ExperimentDraft` la llevan encima
#: (`scientific_payload()`), pero la de `WorldDraft` vive en el sitio de llamada
#: —[api.py:206](terrario/lab/api.py:206) recorta `draft_id` y `provenance` a
#: mano—. Reproducirla aquí a ojo sería inventar un tercer cálculo; queda
#: escrita al lado del códec, que es donde se ve si se desincroniza.
#:
#: `TrialMatrix` no aparece porque no tiene códec: no se relee nunca a objeto,
#: así que no puede sufrir esta clase de deriva. Su ausencia es un hecho del
#: árbol, no un olvido.
def _world_draft_identity(draft: Any) -> str:
    value = plain(draft)
    return content_hash({key: item for key, item in value.items() if key not in {"draft_id", "provenance"}})


DECODERS: Mapping[str, tuple[Callable[[Mapping[str, Any]], Any], Callable[[Any], str]]] = {
    "Preregistration": (preregistration_draft_from_payload, lambda d: content_hash(d.scientific_payload())),
    "ExperimentDraft": (experiment_draft_from_payload, lambda d: content_hash(d.scientific_payload())),
    "WorldDraft": (world_draft_from_payload, _world_draft_identity),
}


#: Las raíces del grafo de contratos que participan en una identidad científica
#: almacenada. Todo lo que cuelgue de ellas queda vigilado por construcción.
CONTRACT_ROOTS = ("PreregistrationDraft", "ExperimentDraft", "WorldDraft")


def contract_surface() -> dict[str, list[str]]:
    """El conjunto de campos de cada contrato que entra en un hash almacenado.

    Es la mitad del gate que no necesita base de datos, y la única que salta el
    día en que se añade el campo —no meses después, cuando alguien intenta
    re-derivar—. Se recorre el grafo de dataclasses en vez de mantener una
    lista: un contrato anidado nuevo queda cubierto por el hecho de estar
    referenciado, que es la misma regla que usa el gate de cartografía.
    """
    import dataclasses
    import typing

    from terrario.lab.experiment_composer import ExperimentDraft
    from terrario.lab.preregistration.domain import PreregistrationDraft
    from terrario.lab.world_authoring import WorldDraft

    found: dict[str, list[str]] = {}

    def walk(kind: type) -> None:
        if not dataclasses.is_dataclass(kind) or kind.__name__ in found:
            return
        hints = typing.get_type_hints(kind)
        found[kind.__name__] = sorted(field.name for field in dataclasses.fields(kind))
        for field in dataclasses.fields(kind):
            pending = [hints.get(field.name, field.type)]
            while pending:
                annotation = pending.pop()
                pending.extend(typing.get_args(annotation))
                if isinstance(annotation, type):
                    walk(annotation)

    for root in (PreregistrationDraft, ExperimentDraft, WorldDraft):
        walk(root)
    return dict(sorted(found.items()))


def contract_surface_hash() -> str:
    return content_hash(contract_surface())


def divergences(stored: Any, rebuilt: Any, path: str = "$") -> list[str]:
    """Las diferencias entre el payload guardado y el que produce el códec.

    Los índices de lista se colapsan a `[*]`: interesa qué clave se movió, no en
    qué métrica concreta. Un registro con dos métricas que ganan el mismo campo
    es el mismo hecho contado una vez.
    """
    found: list[str] = []
    if isinstance(stored, dict) and isinstance(rebuilt, dict):
        for key in sorted(set(stored) | set(rebuilt)):
            where = f"{path}.{key}"
            if key not in stored:
                found.append(f"ANADIDA {where}")
            elif key not in rebuilt:
                found.append(f"PERDIDA {where}")
            else:
                found.extend(divergences(stored[key], rebuilt[key], where))
    elif isinstance(stored, list) and isinstance(rebuilt, list):
        if len(stored) != len(rebuilt):
            found.append(f"LONGITUD {path}")
        else:
            for left, right in zip(stored, rebuilt):
                found.extend(divergences(left, right, f"{path}[*]"))
    elif stored != rebuilt:
        found.append(f"VALOR {path}")
    return sorted(set(found))


class BundleRoots:
    """Recomputa el manifiesto raíz de un bundle con el constructor real.

    Se apoya en `CommitmentBuilder` en vez de replicar su forma: si el sellado
    cambia, este comprobador cambia con él. El constructor escribe al CAS, así
    que se le da una raíz temporal; la raíz viva se abre siempre en sólo lectura.
    """

    def __init__(self) -> None:
        self._directory = tempfile.TemporaryDirectory(prefix="reconstruccion-")
        from terrario.lab.persistence import ArtifactRepository
        from terrario.lab.preregistration.commitments import CommitmentBuilder

        self._builder = CommitmentBuilder(ArtifactRepository(Path(self._directory.name) / ".terrario"))

    def root_hash(self, draft: Any) -> str:
        return self._builder.build(draft).bundle_root_hash

    def close(self) -> None:
        self._directory.cleanup()


def _connect(root: Path) -> sqlite3.Connection:
    """La raíz viva se abre en sólo lectura, siempre.

    Vía URI, no por ruta: es lo que hace que `mode=ro` sea del motor y no una
    promesa de este fichero. La ruta se escapa con `as_uri()` —hay espacios en
    el nombre del proyecto— y se le quita el prefijo `file://` que SQLite no
    quiere ver duplicado.
    """
    database = root / "terrario.db"
    escaped = database.as_uri().removeprefix("file://")
    connection = sqlite3.connect(f"file:{escaped}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def measure(root: Path) -> dict[str, dict[str, Any]]:
    """Cada versión almacenada con códec, reconstruida y recomputada."""
    connection = _connect(root)
    locked = {row["bundle_version_id"] for row in connection.execute(
        "SELECT bundle_version_id FROM preregistration_locks")}
    roots = BundleRoots()
    measured: dict[str, dict[str, Any]] = {}
    try:
        for row in connection.execute(
            "SELECT version_id,artifact_id,version_number,kind,schema_version,scientific_hash,payload_json "
            "FROM artifact_versions WHERE kind IN (%s) ORDER BY artifact_id,version_number"
            % ",".join("?" * len(DECODERS)), tuple(DECODERS)
        ):
            payload = json.loads(row["payload_json"])
            is_bundle = row["schema_version"] == BUNDLE_SCHEMA
            source = payload.get("draft", payload) if is_bundle else payload
            record: dict[str, Any] = {
                "artifact_id": row["artifact_id"],
                "kind": row["kind"],
                "form": "bundle" if is_bundle else "draft",
                "schema_version": row["schema_version"],
                "locked": row["version_id"] in locked,
                "almacenado": row["scientific_hash"],
            }
            decode, identity = DECODERS[row["kind"]]
            try:
                rebuilt = decode(source)
            except Exception as error:  # el códec ya no acepta el registro: peor que divergir
                record["recomputado"] = None
                record["divergencia"] = [f"CODEC {type(error).__name__}"]
                measured[row["version_id"]] = record
                continue
            record["divergencia"] = divergences(source, plain(rebuilt))
            record["recomputado"] = roots.root_hash(rebuilt) if is_bundle else identity(rebuilt)
            measured[row["version_id"]] = record
    finally:
        roots.close()
        connection.close()
    return measured


def reproduces(record: Mapping[str, Any]) -> bool:
    return not record["divergencia"] and record["recomputado"] == record["almacenado"]


FIELDS = ("artifact_id", "kind", "form", "schema_version", "locked", "almacenado", "recomputado", "divergencia")


def compare(measured: Mapping[str, Mapping[str, Any]], ledger: Mapping[str, Any]) -> list[str]:
    """Los fallos del contrato. Vacío es verde."""
    declared = ledger.get("registros", {})
    failures: list[str] = []
    for version_id, record in sorted(measured.items()):
        entry = declared.get(version_id)
        if reproduces(record):
            if entry is not None:
                failures.append(
                    f"ACTA_OBSOLETA {version_id} — el acta lo declara divergente y hoy se re-deriva; "
                    "la historia no se repara, se re-declara con --write y se explica")
            continue
        if entry is None:
            failures.append(
                f"DIVERGENCIA_NO_DECLARADA {version_id} ({record['kind']}/{record['form']}"
                f"{', BLOQUEADO' if record['locked'] else ''}) — {', '.join(record['divergencia']) or 'hash distinto'}")
            continue
        if entry.get("almacenado") != record["almacenado"]:
            failures.append(f"HISTORIA_REESCRITA {version_id} — hash almacenado "
                            f"{entry.get('almacenado')} → {record['almacenado']}")
        if entry.get("recomputado") != record["recomputado"]:
            failures.append(f"RECONSTRUCCION_MOVIDA {version_id} — un contrato cambió desde la declaración: "
                            f"recomputado {entry.get('recomputado')} → {record['recomputado']}")
        if list(entry.get("divergencia", ())) != list(record["divergencia"]):
            failures.append(f"FORMA_DE_DIVERGENCIA_CAMBIADA {version_id} — "
                            f"{sorted(set(record['divergencia']) ^ set(entry.get('divergencia', ())))}")
    for version_id in sorted(set(declared) - set(measured)):
        failures.append(f"REGISTRO_AUSENTE {version_id} — está en el acta y ya no en la base")
    return failures


def load_ledger() -> dict[str, Any]:
    if not LEDGER.is_file():
        return {"schema": LEDGER_SCHEMA, "registros": {}}
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def write_ledger(measured: Mapping[str, Mapping[str, Any]], declared_at: str) -> dict[str, Any]:
    diverging = {version_id: {field: record[field] for field in FIELDS}
                 for version_id, record in sorted(measured.items()) if not reproduces(record)}
    ledger = {
        "schema": LEDGER_SCHEMA,
        "declarado_el": declared_at,
        "informe": "docs/INFORME_RECONSTRUCCION_PREREGISTRO_01.md",
        "superficie_de_contratos": contract_surface_hash(),
        "contratos": contract_surface(),
        "que_es": (
            "Acta de la discontinuidad: cada versión almacenada cuya identidad científica ya no se "
            "deriva de su propio payload. No es una lista de excepciones perdonadas; es el estado "
            "congelado contra el que se compara. Cambiar cualquier contrato mueve el hash recomputado "
            "de estas filas y pone el gate en rojo, que es lo que se quiere."),
        "medido_sobre": {"versiones_con_codec": len(measured), "divergentes": len(diverging)},
        "registros": diverging,
    }
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps(ledger, ensure_ascii=False, indent=1, sort_keys=False) + "\n", encoding="utf-8")
    return ledger


def summary(measured: Mapping[str, Mapping[str, Any]]) -> Iterator[str]:
    by_kind: dict[tuple[str, str], list[int]] = collections.defaultdict(lambda: [0, 0])
    paths: collections.Counter[str] = collections.Counter()
    locked_bad = 0
    for record in measured.values():
        slot = by_kind[(record["kind"], record["form"])]
        if reproduces(record):
            slot[0] += 1
        else:
            slot[1] += 1
            locked_bad += bool(record["locked"])
            paths.update(record["divergencia"])
    for (kind, form), (ok, bad) in sorted(by_kind.items()):
        yield f"  {kind:16s} {form:7s} se re-deriva {ok:4d}   no {bad:4d}"
    yield f"  {'BLOQUEADOS que no se re-derivan':<32s} {locked_bad:4d}"
    for path, count in paths.most_common():
        yield f"    {count:4d} versiones  {path}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=None, help="raíz de datos; por defecto .terrario del repositorio")
    parser.add_argument("--write", action="store_true", help="re-declara la discontinuidad en el acta")
    parser.add_argument("--detalle", action="store_true", help="imprime el desglose por contrato")
    parser.add_argument("--declarado-el", default=None, help="fecha a escribir en el acta con --write")
    arguments = parser.parse_args(argv)

    root = arguments.root or PROJECT_ROOT / ".terrario"
    if not (root / "terrario.db").is_file():
        print(f"sin raíz de datos en {root} — nada que medir.\n"
              f"Usa --root para apuntar a la raíz viva; el acta vive en {LEDGER.relative_to(PROJECT_ROOT)}.")
        return 2

    measured = measure(root)
    if arguments.detalle or arguments.write:
        print(f"raíz: {root}")
        for line in summary(measured):
            print(line)
        print()

    if arguments.write:
        ledger = write_ledger(measured, arguments.declarado_el or date.today().isoformat())
        print(f"acta re-declarada: {ledger['medido_sobre']['divergentes']} de "
              f"{ledger['medido_sobre']['versiones_con_codec']} versiones → {LEDGER.relative_to(PROJECT_ROOT)}")
        return 0

    failures = compare(measured, load_ledger())
    if failures:
        print(f"RECONSTRUCCIÓN ROTA — {len(failures)} fallo(s) fuera de lo declarado:\n")
        for failure in failures[:40]:
            print(f"  {failure}")
        if len(failures) > 40:
            print(f"  … y {len(failures) - 40} más")
        return 1
    declared = len(load_ledger().get("registros", {}))
    print(f"reconstrucción al día: {len(measured)} versiones con códec, "
          f"{declared} en el acta de discontinuidad, 0 divergencias nuevas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
