"""Session guard: the live scientific data root must not change under a test run.

`.terrario/` holds locked preregistrations, executions, CAS blobs and audit
chains. It was found carrying 282 review requests and 141 executions that were
test exhaust, next to a single real human decision. Tests that need a data root
must build one under `tmp_path`; this guard turns any leak into a red run with
the evidence attached, instead of a slow contamination nobody notices.

The database runs in WAL mode, so a write can sit in `terrario.db-wal` while the
main file is untouched; both files and the runtime directory are fingerprinted.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

LIVE_ROOT = Path(__file__).resolve().parent.parent / ".terrario"
_WATCHED = ("terrario.db", "terrario.db-wal")


def _fingerprint() -> dict[str, object] | None:
    if not LIVE_ROOT.exists():
        return None
    out: dict[str, object] = {}
    for name in _WATCHED:
        path = LIVE_ROOT / name
        if path.exists():
            out[name] = (path.stat().st_size, hashlib.sha256(path.read_bytes()).hexdigest()[:16])
        else:
            out[name] = None
    runtime = LIVE_ROOT / "runtime"
    out["runtime_entries"] = len(list(runtime.iterdir())) if runtime.exists() else None
    return out


def pytest_configure(config: pytest.Config) -> None:
    config._terrario_live_before = _fingerprint()  # type: ignore[attr-defined]
    config._terrario_live_after = None  # type: ignore[attr-defined]


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    config = session.config
    before = getattr(config, "_terrario_live_before", None)
    after = _fingerprint()
    config._terrario_live_after = after  # type: ignore[attr-defined]
    if before is not None and before != after:
        session.exitstatus = pytest.ExitCode.TESTS_FAILED


def pytest_terminal_summary(terminalreporter: pytest.TerminalReporter, exitstatus: int, config: pytest.Config) -> None:
    before = getattr(config, "_terrario_live_before", None)
    after = getattr(config, "_terrario_live_after", None)
    if after is None:
        after = _fingerprint()
    if before is None:
        terminalreporter.write_line("terrario live data root: absent, nothing to guard")
        return
    if before == after:
        terminalreporter.write_line("terrario live data root: unchanged (guard passed)")
        return
    terminalreporter.write_sep("=", "LIVE SCIENTIFIC DATA ROOT CHANGED DURING THIS RUN", red=True, bold=True)
    for key in sorted(set(before) | set(after)):
        if before.get(key) != after.get(key):
            terminalreporter.write_line(f"  {key}: {before.get(key)}  ->  {after.get(key)}", red=True)
    terminalreporter.write_line("  A test wrote to .terrario instead of a tmp_path data root. Fix the test; never the manifest.", red=True)
