"""Append-only, hash-chained JSONL trace with a rebuildable SQLite index."""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import threading
from pathlib import Path
from typing import Any, Iterable

from .contracts import TRACE_SCHEMA


class TraceIntegrityError(RuntimeError):
    code = "TRACE_INTEGRITY_FAILURE"


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


class TraceArchive:
    """The JSONL is authoritative; every other artifact is disposable."""

    def __init__(self, root: str | Path, trace_id: str, checkpoint_interval: int = 256):
        self.root = Path(root) / trace_id
        self.root.mkdir(parents=True, exist_ok=True)
        self.trace_id = trace_id
        self.trace_path = self.root / "trace.v2.jsonl"
        self.index_path = self.root / "trace.index.sqlite3"
        self.checkpoint_dir = self.root / "checkpoints"
        self.checkpoint_dir.mkdir(exist_ok=True)
        self.checkpoint_interval = checkpoint_interval
        self._lock = threading.RLock()
        self._previous_hash, self._last_sequence = self._tail()
        self._ensure_index()

    def _tail(self) -> tuple[str, int]:
        previous, sequence = "0" * 64, -1
        if not self.trace_path.exists():
            return previous, sequence
        with self.trace_path.open("rb") as handle:
            for raw in handle:
                if raw.strip():
                    row = json.loads(raw)
                    previous, sequence = row["hash"], int(row["sequence"])
        return previous, sequence

    def _connect(self):
        db = sqlite3.connect(self.index_path)
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("CREATE TABLE IF NOT EXISTS records(sequence INTEGER PRIMARY KEY,tick INTEGER NOT NULL,event_type TEXT,entity_id TEXT,checkpoint INTEGER NOT NULL,offset INTEGER NOT NULL,length INTEGER NOT NULL,hash TEXT NOT NULL)")
        db.execute("CREATE INDEX IF NOT EXISTS records_tick ON records(tick,sequence)")
        db.execute("CREATE INDEX IF NOT EXISTS records_event ON records(event_type,sequence)")
        db.execute("CREATE INDEX IF NOT EXISTS records_entity ON records(entity_id,sequence)")
        return db

    def _ensure_index(self):
        try:
            with self._connect() as db:
                indexed = db.execute("SELECT COALESCE(MAX(sequence),-1) FROM records").fetchone()[0]
            if indexed != self._last_sequence:
                self.rebuild_index()
        except sqlite3.DatabaseError:
            if self.index_path.exists():
                self.index_path.unlink()
            self.rebuild_index()

    def append(self, *, sequence: int, tick: int, record_type: str, payload: dict[str, Any], entity_id: str | None = None, checkpoint: bool = False) -> dict[str, Any]:
        with self._lock:
            if sequence != self._last_sequence + 1:
                raise ValueError(f"trace sequence gap: expected {self._last_sequence + 1}, got {sequence}")
            unsigned = {"trace_schema_version": TRACE_SCHEMA, "trace_id": self.trace_id, "sequence": sequence, "tick": tick, "record_type": record_type, "entity_id": entity_id, "previous_hash": self._previous_hash, "payload": payload}
            digest = hashlib.sha256(self._previous_hash.encode("ascii") + _canonical(unsigned)).hexdigest()
            row = {**unsigned, "hash": digest}
            encoded = _canonical(row) + b"\n"
            with self.trace_path.open("ab") as handle:
                offset = handle.tell(); handle.write(encoded); handle.flush(); os.fsync(handle.fileno())
            with self._connect() as db:
                db.execute("INSERT INTO records VALUES(?,?,?,?,?,?,?,?)", (sequence, tick, record_type, entity_id, int(checkpoint), offset, len(encoded), digest))
            self._previous_hash, self._last_sequence = digest, sequence
            return row

    def checkpoint(self, tick: int, sequence: int, frame: dict[str, Any], reason: str) -> Path:
        target = self.checkpoint_dir / f"tick-{tick:012d}.json"
        payload = {"trace_schema_version": TRACE_SCHEMA, "trace_id": self.trace_id, "tick": tick, "sequence": sequence, "reason": reason, "frame": frame}
        temp = target.with_suffix(".tmp")
        temp.write_bytes(_canonical(payload)); os.replace(temp, target)
        return target

    def read(self, *, after_sequence: int = -1, limit: int = 10_000, tick: int | None = None, event_type: str | None = None, entity_id: str | None = None) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), 10_000))
        clauses, args = ["sequence>?"], [after_sequence]
        if tick is not None: clauses.append("tick=?"); args.append(tick)
        if event_type is not None: clauses.append("event_type=?"); args.append(event_type)
        if entity_id is not None: clauses.append("entity_id=?"); args.append(entity_id)
        sql = f"SELECT offset,length FROM records WHERE {' AND '.join(clauses)} ORDER BY sequence LIMIT ?"
        args.append(limit)
        with self._connect() as db:
            spans = db.execute(sql, args).fetchall()
        rows = []
        with self.trace_path.open("rb") as handle:
            for offset, length in spans:
                handle.seek(offset); rows.append(json.loads(handle.read(length)))
        return rows

    def seek(self, tick: int) -> dict[str, Any] | None:
        with self._connect() as db:
            span = db.execute("SELECT offset,length FROM records WHERE tick<=? ORDER BY tick DESC,sequence DESC LIMIT 1", (tick,)).fetchone()
        if not span: return None
        with self.trace_path.open("rb") as handle:
            handle.seek(span[0]); return json.loads(handle.read(span[1]))

    def verify(self) -> dict[str, Any]:
        previous, count, last_sequence = "0" * 64, 0, -1
        if not self.trace_path.exists():
            return {"valid": True, "records": 0, "last_sequence": -1}
        with self.trace_path.open("rb") as handle:
            for raw in handle:
                row = json.loads(raw)
                supplied = row.pop("hash")
                expected = hashlib.sha256(previous.encode("ascii") + _canonical(row)).hexdigest()
                if row.get("previous_hash") != previous or supplied != expected or int(row["sequence"]) != last_sequence + 1:
                    raise TraceIntegrityError(f"TRACE_INTEGRITY_FAILURE at sequence {row.get('sequence')}")
                previous, last_sequence, count = supplied, int(row["sequence"]), count + 1
        return {"valid": True, "records": count, "last_sequence": last_sequence, "last_hash": previous}

    def rebuild_index(self):
        self.verify()
        if self.index_path.exists(): self.index_path.unlink()
        with self._connect() as db:
            if not self.trace_path.exists(): return
            with self.trace_path.open("rb") as handle:
                while True:
                    offset = handle.tell(); raw = handle.readline()
                    if not raw: break
                    row = json.loads(raw)
                    db.execute("INSERT INTO records VALUES(?,?,?,?,?,?,?,?)", (row["sequence"], row["tick"], row["record_type"], row.get("entity_id"), int(row["record_type"] == "CHECKPOINT"), offset, len(raw), row["hash"]))
