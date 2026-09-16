"""The live-data-root guard in conftest.py must notice every kind of leak it claims to.

It watches a real path, so this test exercises the detection logic against a
scratch copy rather than the live root: a guard that has never been seen to
fire is an assumption, not a safeguard.
"""
from __future__ import annotations

import sqlite3

import tests.conftest as guard


def _scratch_root(tmp_path):
    root = tmp_path / ".terrario"
    (root / "runtime").mkdir(parents=True)
    with sqlite3.connect(root / "terrario.db") as con:
        con.execute("CREATE TABLE t(x)"); con.execute("INSERT INTO t VALUES (1)")
    return root


def test_guard_is_quiet_when_nothing_changes(tmp_path, monkeypatch):
    monkeypatch.setattr(guard, "LIVE_ROOT", _scratch_root(tmp_path))
    assert guard._fingerprint() == guard._fingerprint()


def test_guard_sees_a_write_to_the_database(tmp_path, monkeypatch):
    root = _scratch_root(tmp_path); monkeypatch.setattr(guard, "LIVE_ROOT", root)
    before = guard._fingerprint()
    with sqlite3.connect(root / "terrario.db") as con:
        con.execute("INSERT INTO t VALUES (2)")
    assert guard._fingerprint() != before


def test_guard_sees_a_write_parked_in_the_wal(tmp_path, monkeypatch):
    root = _scratch_root(tmp_path); monkeypatch.setattr(guard, "LIVE_ROOT", root)
    before = guard._fingerprint()
    (root / "terrario.db-wal").write_bytes(b"uncheckpointed")
    assert guard._fingerprint() != before


def test_guard_sees_a_new_runtime_attempt(tmp_path, monkeypatch):
    root = _scratch_root(tmp_path); monkeypatch.setattr(guard, "LIVE_ROOT", root)
    before = guard._fingerprint()
    (root / "runtime" / "execution-leak").mkdir()
    assert guard._fingerprint() != before


def test_guard_is_absent_not_wrong_without_a_live_root(tmp_path, monkeypatch):
    monkeypatch.setattr(guard, "LIVE_ROOT", tmp_path / "missing")
    assert guard._fingerprint() is None
