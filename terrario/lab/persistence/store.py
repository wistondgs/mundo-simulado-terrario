"""SQLite artifact repository with immutable versions and hash-signed bundles."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Mapping

from terrario.lab.persistence.blobs import BlobManifest, ContentAddressedBlobStore
from terrario.lab.persistence.canonical import canonical_json, content_hash, plain
from terrario.lab.persistence.migrations import MIGRATIONS


class PersistenceError(RuntimeError):
    code = "PERSISTENCE_ERROR"


class ArtifactNotFound(PersistenceError):
    code = "ARTIFACT_NOT_FOUND"


class ProvenanceConflict(PersistenceError):
    code = "PROVENANCE_CONFLICT"


class DuplicateArtifact(PersistenceError):
    code = "DUPLICATE_ARTIFACT"


class ArtifactBundleError(PersistenceError):
    code = "INVALID_ARTIFACT_BUNDLE"


@dataclass(frozen=True)
class ArtifactRecord:
    artifact_id: str
    kind: str
    created_at: str
    created_by: str


@dataclass(frozen=True)
class ArtifactVersionRecord:
    version_id: str
    artifact_id: str
    version_number: int
    kind: str
    schema_version: str
    scientific_hash: str
    scientific_payload: Mapping[str, Any] | list[Any] | Any
    payload: Mapping[str, Any] | list[Any] | Any
    classification: str
    parent_version_id: str | None
    parent_hash: str | None
    delta: Mapping[str, Any] | list[Any] | Any
    reason: str
    created_at: str
    created_by: str
    sealed: bool
    deduplicated: bool = False


class ArtifactRepository:
    """Durable local repository; connections are short-lived and process-safe."""

    BUNDLE_SCHEMA = "terrario.artifact-bundle/v1"

    def __init__(self, data_root: str | Path):
        self.data_root = Path(data_root).resolve()
        self.data_root.mkdir(parents=True, exist_ok=True)
        for name in ("backups", "exports", "locks", "runtime"):
            (self.data_root / name).mkdir(parents=True, exist_ok=True)
        self.database_path = self.data_root / "terrario.db"
        self.blobs = ContentAddressedBlobStore(self.data_root)
        self.recovered_staging = self.blobs.recover_staging()
        self._migrate()

    @staticmethod
    def now() -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _identifier(prefix: str) -> str:
        safe = re.sub(r"[^a-z0-9]+", "-", prefix.casefold()).strip("-") or "artifact"
        return f"{safe}-{uuid.uuid4().hex}"

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=5.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout=5000")
        connection.execute("PRAGMA foreign_keys=ON")
        current_mode = str(connection.execute("PRAGMA journal_mode").fetchone()[0]).casefold()
        if current_mode != "wal":
            for attempt in range(20):
                try:
                    connection.execute("PRAGMA journal_mode=WAL")
                    break
                except sqlite3.OperationalError as exc:
                    if "locked" not in str(exc).casefold() or attempt == 19:
                        connection.close()
                        raise
                    time.sleep(0.05 * (attempt + 1))
        connection.execute("PRAGMA synchronous=FULL")
        return connection

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _migrate(self) -> None:
        preexisting_tables = False
        if self.database_path.exists() and self.database_path.stat().st_size:
            connection = sqlite3.connect(self.database_path)
            try:
                preexisting_tables = bool(connection.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' LIMIT 1"
                ).fetchone())
            finally:
                connection.close()

        applied: dict[int, tuple[str, str]] = {}
        connection = self._connect()
        try:
            exists = connection.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name='schema_migrations'"
            ).fetchone()
            if exists:
                applied = {
                    int(row["version"]): (str(row["name"]), str(row["checksum"]))
                    for row in connection.execute("SELECT version,name,checksum FROM schema_migrations")
                }
        finally:
            connection.close()

        pending = [migration for migration in MIGRATIONS if migration.version not in applied]
        for migration in MIGRATIONS:
            checksum = hashlib.sha256(migration.sql.encode("utf-8")).hexdigest()
            if migration.version in applied and applied[migration.version] != (migration.name, checksum):
                raise PersistenceError(f"migration checksum mismatch: {migration.version}")
        if pending and preexisting_tables:
            self.backup(label="pre-migration")

        for migration in pending:
            checksum = hashlib.sha256(migration.sql.encode("utf-8")).hexdigest()
            name = migration.name.replace("'", "''")
            applied_at = self.now().replace("'", "''")
            script = (
                "BEGIN IMMEDIATE;\n"
                f"{migration.sql}\n"
                "INSERT OR IGNORE INTO schema_migrations(version,name,checksum,applied_at) "
                f"VALUES({migration.version},'{name}','{checksum}','{applied_at}');\n"
                "COMMIT;"
            )
            connection = self._connect()
            try:
                connection.executescript(script)
            except Exception:
                try:
                    connection.execute("ROLLBACK")
                except sqlite3.OperationalError:
                    pass
                raise
            finally:
                connection.close()
        verified = {row["version"]: (row["name"], row["checksum"]) for row in self.migration_status()}
        for migration in MIGRATIONS:
            checksum = hashlib.sha256(migration.sql.encode("utf-8")).hexdigest()
            if verified.get(migration.version) != (migration.name, checksum):
                raise PersistenceError(f"migration was not applied atomically: {migration.version}")

    def migration_status(self) -> tuple[dict[str, Any], ...]:
        with self._connect() as connection:
            return tuple(dict(row) for row in connection.execute(
                "SELECT version,name,checksum,applied_at FROM schema_migrations ORDER BY version"
            ))

    def backup(self, label: str = "manual") -> Path:
        target = self.data_root / "backups" / f"terrario-{label}-{self.now().replace(':', '')}-{uuid.uuid4().hex[:8]}.db"
        source = self._connect()
        destination = sqlite3.connect(target)
        try:
            source.execute("PRAGMA wal_checkpoint(FULL)")
            source.backup(destination)
            destination.commit()
        finally:
            destination.close()
            source.close()
        return target

    def create_artifact(
        self,
        kind: str,
        payload: Any,
        schema_version: str,
        *,
        scientific_payload: Any | None = None,
        artifact_id: str | None = None,
        classification: str = "UNCLASSIFIED",
        created_by: str = "lab-user",
        reason: str = "artifact creation",
        initial_state: str | None = None,
        sealed: bool = False,
        deduplicate: bool = False,
        correlation_id: str | None = None,
    ) -> ArtifactVersionRecord:
        artifact_id = artifact_id or self._identifier(kind)
        version_id = self._identifier("version")
        created_at = self.now()
        payload_value = plain(payload)
        scientific_value = plain(payload_value if scientific_payload is None else scientific_payload)
        payload_json = canonical_json(payload_value)
        scientific_json = canonical_json(scientific_value)
        digest = content_hash(scientific_value)
        delta_json = canonical_json({})
        with self.transaction() as connection:
            duplicate = connection.execute(
                "SELECT * FROM artifact_versions WHERE kind=? AND scientific_hash=?", (kind, digest)
            ).fetchone()
            if duplicate:
                if deduplicate:
                    return self._version_from_row(duplicate, deduplicated=True)
                raise DuplicateArtifact(f"{kind} with scientific hash {digest} already exists")
            existing = connection.execute(
                "SELECT kind FROM artifacts WHERE artifact_id=?", (artifact_id,)
            ).fetchone()
            if existing:
                raise ProvenanceConflict(f"artifact id already exists: {artifact_id}")
            connection.execute(
                "INSERT INTO artifacts(artifact_id,kind,created_at,created_by) VALUES(?,?,?,?)",
                (artifact_id, kind, created_at, created_by),
            )
            connection.execute(
                """INSERT INTO artifact_versions(
                    version_id,artifact_id,version_number,kind,schema_version,scientific_hash,
                    scientific_payload_json,payload_json,classification,parent_version_id,parent_hash,
                    delta_json,reason,created_at,created_by,sealed
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    version_id, artifact_id, 1, kind, schema_version, digest, scientific_json,
                    payload_json, classification, None, None, delta_json, reason, created_at,
                    created_by, int(sealed),
                ),
            )
            if initial_state is not None:
                self._insert_state_event(
                    connection, version_id, 1, None, initial_state, created_by, reason, created_at,
                )
            self._insert_audit(
                connection, correlation_id or self._identifier("correlation"), created_by,
                "ARTIFACT_CREATED", kind, artifact_id,
                {"version_id": version_id, "scientific_hash": digest}, created_at,
            )
        return self.get_version(version_id)

    def create_version(
        self,
        artifact_id: str,
        payload: Any,
        schema_version: str,
        *,
        scientific_payload: Any | None = None,
        classification: str | None = None,
        created_by: str = "lab-user",
        reason: str,
        delta: Any,
        parent_version_id: str | None = None,
        state: str | None = None,
        sealed: bool = False,
        deduplicate: bool = False,
        correlation_id: str | None = None,
    ) -> ArtifactVersionRecord:
        payload_value = plain(payload)
        scientific_value = plain(payload_value if scientific_payload is None else scientific_payload)
        digest = content_hash(scientific_value)
        created_at = self.now()
        version_id = self._identifier("version")
        with self.transaction() as connection:
            artifact = connection.execute("SELECT * FROM artifacts WHERE artifact_id=?", (artifact_id,)).fetchone()
            if artifact is None:
                raise ArtifactNotFound(artifact_id)
            latest = connection.execute(
                "SELECT * FROM artifact_versions WHERE artifact_id=? ORDER BY version_number DESC LIMIT 1",
                (artifact_id,),
            ).fetchone()
            parent = latest if parent_version_id is None else connection.execute(
                "SELECT * FROM artifact_versions WHERE version_id=? AND artifact_id=?",
                (parent_version_id, artifact_id),
            ).fetchone()
            if parent is None:
                raise ProvenanceConflict("parent version does not belong to artifact")
            duplicate = connection.execute(
                "SELECT * FROM artifact_versions WHERE kind=? AND scientific_hash=?",
                (artifact["kind"], digest),
            ).fetchone()
            if duplicate:
                if deduplicate:
                    return self._version_from_row(duplicate, deduplicated=True)
                raise DuplicateArtifact(f"{artifact['kind']} with scientific hash {digest} already exists")
            version_number = int(latest["version_number"]) + 1
            connection.execute(
                """INSERT INTO artifact_versions(
                    version_id,artifact_id,version_number,kind,schema_version,scientific_hash,
                    scientific_payload_json,payload_json,classification,parent_version_id,parent_hash,
                    delta_json,reason,created_at,created_by,sealed
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    version_id, artifact_id, version_number, artifact["kind"], schema_version,
                    digest, canonical_json(scientific_value), canonical_json(payload_value),
                    classification or latest["classification"], parent["version_id"],
                    parent["scientific_hash"], canonical_json(delta), reason, created_at,
                    created_by, int(sealed),
                ),
            )
            if state is not None:
                self._insert_state_event(connection, version_id, 1, None, state, created_by, reason, created_at)
            self._insert_audit(
                connection, correlation_id or self._identifier("correlation"), created_by,
                "ARTIFACT_VERSION_CREATED", artifact["kind"], artifact_id,
                {"version_id": version_id, "parent_version_id": parent["version_id"], "scientific_hash": digest},
                created_at,
            )
        return self.get_version(version_id)

    def append_state(
        self, version_id: str, to_state: str, *, actor_id: str, reason: str, decision_id: str | None = None,
    ) -> dict[str, Any]:
        created_at = self.now()
        with self.transaction() as connection:
            version = connection.execute(
                "SELECT artifact_id,kind FROM artifact_versions WHERE version_id=?", (version_id,)
            ).fetchone()
            if version is None:
                raise ArtifactNotFound(version_id)
            last = connection.execute(
                "SELECT sequence,to_state FROM artifact_state_events WHERE version_id=? ORDER BY sequence DESC LIMIT 1",
                (version_id,),
            ).fetchone()
            sequence = int(last["sequence"]) + 1 if last else 1
            from_state = str(last["to_state"]) if last else None
            self._insert_state_event(
                connection, version_id, sequence, from_state, to_state, actor_id, reason, created_at, decision_id,
            )
            self._insert_audit(
                connection, self._identifier("correlation"), actor_id, "ARTIFACT_STATE_APPENDED",
                version["kind"], version["artifact_id"],
                {"version_id": version_id, "from": from_state, "to": to_state}, created_at,
            )
        return {"version_id": version_id, "sequence": sequence, "from_state": from_state, "to_state": to_state}

    def current_state(self, version_id: str) -> str | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT to_state FROM artifact_state_events WHERE version_id=? ORDER BY sequence DESC LIMIT 1",
                (version_id,),
            ).fetchone()
        return str(row["to_state"]) if row else None

    def get_artifact(self, artifact_id: str) -> ArtifactRecord:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM artifacts WHERE artifact_id=?", (artifact_id,)).fetchone()
        if row is None:
            raise ArtifactNotFound(artifact_id)
        return ArtifactRecord(**dict(row))

    def current(self, artifact_id: str, kind: str | None = None) -> ArtifactVersionRecord:
        query = "SELECT * FROM artifact_versions WHERE artifact_id=?"
        values: list[Any] = [artifact_id]
        if kind is not None:
            query += " AND kind=?"
            values.append(kind)
        query += " ORDER BY version_number DESC LIMIT 1"
        with self._connect() as connection:
            row = connection.execute(query, values).fetchone()
        if row is None:
            raise ArtifactNotFound(artifact_id)
        return self._version_from_row(row)

    def get_version(self, version_id: str) -> ArtifactVersionRecord:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM artifact_versions WHERE version_id=?", (version_id,)).fetchone()
        if row is None:
            raise ArtifactNotFound(version_id)
        return self._version_from_row(row)

    def versions(self, artifact_id: str) -> tuple[ArtifactVersionRecord, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM artifact_versions WHERE artifact_id=? ORDER BY version_number", (artifact_id,)
            ).fetchall()
        if not rows:
            raise ArtifactNotFound(artifact_id)
        return tuple(self._version_from_row(row) for row in rows)

    def list_artifacts(self, kind: str | None = None) -> tuple[ArtifactVersionRecord, ...]:
        query = """SELECT versions.* FROM artifact_versions versions
            JOIN (SELECT artifact_id,MAX(version_number) AS latest FROM artifact_versions GROUP BY artifact_id) current
            ON current.artifact_id=versions.artifact_id AND current.latest=versions.version_number"""
        values: tuple[Any, ...] = ()
        if kind is not None:
            query += " WHERE versions.kind=?"
            values = (kind,)
        query += " ORDER BY versions.created_at,versions.artifact_id"
        with self._connect() as connection:
            rows = connection.execute(query, values).fetchall()
        return tuple(self._version_from_row(row) for row in rows)

    def count(self, kind: str | None = None) -> int:
        query = "SELECT COUNT(*) FROM artifacts"
        values: tuple[Any, ...] = ()
        if kind is not None:
            query += " WHERE kind=?"
            values = (kind,)
        with self._connect() as connection:
            return int(connection.execute(query, values).fetchone()[0])

    def register_blob(self, payload: bytes, media_type: str = "application/octet-stream") -> BlobManifest:
        manifest = self.blobs.put_bytes(payload, media_type)
        with self.transaction() as connection:
            connection.execute(
                """INSERT INTO blob_manifests(blob_hash,relative_path,size_bytes,media_type,created_at)
                VALUES(?,?,?,?,?) ON CONFLICT(blob_hash) DO NOTHING""",
                (manifest.blob_hash, manifest.relative_path, manifest.size_bytes, manifest.media_type, self.now()),
            )
        return manifest

    def blob_manifest(self, digest: str) -> BlobManifest:
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM blob_manifests WHERE blob_hash=?", (digest,)).fetchone()
        if row is None:
            raise ArtifactNotFound(digest)
        return BlobManifest(row["blob_hash"], row["relative_path"], row["size_bytes"], row["media_type"], True)

    def unregistered_blobs(self) -> tuple[Path, ...]:
        with self._connect() as connection:
            registered = {str(row[0]) for row in connection.execute("SELECT blob_hash FROM blob_manifests")}
        return tuple(
            path for path in sorted(self.blobs.blobs_root.glob("*/*/*"))
            if path.is_file() and path.name not in registered
        )

    def audit_events(self) -> tuple[dict[str, Any], ...]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM audit_events ORDER BY created_at,audit_id").fetchall()
        return tuple({**dict(row), "details": json.loads(row["details_json"])} for row in rows)

    def export_bundle(self, version_id: str) -> dict[str, Any]:
        version = self.get_version(version_id)
        artifact = self.get_artifact(version.artifact_id)
        envelope = {
            "schema_version": self.BUNDLE_SCHEMA,
            "artifact": plain(artifact),
            "version": plain(version),
        }
        envelope["bundle_hash"] = content_hash(envelope)
        return envelope

    @classmethod
    def validate_bundle(cls, bundle: Mapping[str, Any]) -> dict[str, Any]:
        value = plain(bundle)
        if value.get("schema_version") != cls.BUNDLE_SCHEMA:
            raise ArtifactBundleError("unsupported bundle schema")
        supplied = value.pop("bundle_hash", None)
        if supplied != content_hash(value):
            raise ArtifactBundleError("bundle hash mismatch")
        version = value.get("version") or {}
        if version.get("scientific_hash") != content_hash(version.get("scientific_payload")):
            raise ArtifactBundleError("scientific payload hash mismatch")
        artifact = value.get("artifact") or {}
        if artifact.get("artifact_id") != version.get("artifact_id") or artifact.get("kind") != version.get("kind"):
            raise ArtifactBundleError("artifact/version identity mismatch")
        return {**value, "bundle_hash": supplied}

    def import_bundle(self, bundle: Mapping[str, Any], actor_id: str = "bundle-import") -> ArtifactVersionRecord:
        value = self.validate_bundle(bundle)
        artifact, version = value["artifact"], value["version"]
        try:
            existing = self.current(artifact["artifact_id"])
        except ArtifactNotFound:
            return self.create_artifact(
                artifact["kind"], version["payload"], version["schema_version"],
                scientific_payload=version["scientific_payload"], artifact_id=artifact["artifact_id"],
                classification=version["classification"], created_by=actor_id,
                reason=f"imported bundle {value['bundle_hash']}", sealed=bool(version["sealed"]),
                deduplicate=True,
            )
        if existing.scientific_hash == version["scientific_hash"]:
            return ArtifactVersionRecord(**{**existing.__dict__, "deduplicated": True})
        return self.create_version(
            artifact["artifact_id"], version["payload"], version["schema_version"],
            scientific_payload=version["scientific_payload"], classification=version["classification"],
            created_by=actor_id, reason=f"imported bundle {value['bundle_hash']}",
            delta={"imported_parent_version_id": version.get("parent_version_id"), "bundle_hash": value["bundle_hash"]},
            sealed=bool(version["sealed"]), deduplicate=True,
        )

    def integrity_check(self) -> str:
        with self._connect() as connection:
            return str(connection.execute("PRAGMA integrity_check").fetchone()[0])

    @staticmethod
    def _version_from_row(row: sqlite3.Row, deduplicated: bool = False) -> ArtifactVersionRecord:
        return ArtifactVersionRecord(
            str(row["version_id"]), str(row["artifact_id"]), int(row["version_number"]),
            str(row["kind"]), str(row["schema_version"]), str(row["scientific_hash"]),
            json.loads(row["scientific_payload_json"]), json.loads(row["payload_json"]),
            str(row["classification"]), row["parent_version_id"], row["parent_hash"],
            json.loads(row["delta_json"]), str(row["reason"]), str(row["created_at"]),
            str(row["created_by"]), bool(row["sealed"]), deduplicated,
        )

    def _insert_state_event(
        self, connection: sqlite3.Connection, version_id: str, sequence: int, from_state: str | None,
        to_state: str, actor_id: str, reason: str, created_at: str, decision_id: str | None = None,
    ) -> None:
        connection.execute(
            """INSERT INTO artifact_state_events(
                event_id,version_id,sequence,from_state,to_state,actor_id,reason,decision_id,created_at
            ) VALUES(?,?,?,?,?,?,?,?,?)""",
            (
                self._identifier("state-event"), version_id, sequence, from_state, to_state,
                actor_id, reason, decision_id, created_at,
            ),
        )

    def _insert_audit(
        self, connection: sqlite3.Connection, correlation_id: str, actor_id: str, action: str,
        target_type: str, target_id: str, details: Any, created_at: str,
    ) -> None:
        connection.execute(
            """INSERT INTO audit_events(
                audit_id,correlation_id,actor_id,action,target_type,target_id,details_json,created_at
            ) VALUES(?,?,?,?,?,?,?,?)""",
            (
                self._identifier("audit"), correlation_id, actor_id, action, target_type,
                target_id, canonical_json(details), created_at,
            ),
        )
