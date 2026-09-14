from dataclasses import replace
from pathlib import Path

import pytest

from terrario.lab.causal import (
    CausalForkService, CausalRuntime, ForkError, Forkability, InterventionSpec,
    canonical_trace_hash, first_divergence,
)
from terrario.lab.execution.runtime import ScientificTrialIdentity
from terrario.lab.persistence import ArtifactRepository


ROOT = Path(__file__).parents[1]


def identity():
    return ScientificTrialIdentity("execution-test", "trial-test", "attempt-test", "a" * 64, "b" * 64,
                                   "software-test", "d0-test", "A0_RANDOM", 1729, 1001732)


def runtime(tmp_path):
    return CausalRuntime.create(tmp_path, identity(), ROOT / "scenarios" / "d0_differences.yaml")


def test_exact_restore_and_double_restore_are_equivalent(tmp_path):
    source = runtime(tmp_path)
    source.step(); source.step()
    service = CausalForkService(ArtifactRepository(tmp_path / ".terrario"), ROOT)
    snapshot = service.seal_snapshot(source)
    direct = source.run_terminal()
    restored_a = service.restore(snapshot, identity(), ROOT / "scenarios" / "d0_differences.yaml").run_terminal()
    restored_b = service.restore(snapshot, identity(), ROOT / "scenarios" / "d0_differences.yaml").run_terminal()
    assert canonical_trace_hash(direct) == canonical_trace_hash(restored_a) == canonical_trace_hash(restored_b)
    assert first_divergence(restored_a, restored_b) is None


def test_fork_c00_c01_and_test_only_active_intervention(tmp_path):
    source = runtime(tmp_path); source.step()
    service = CausalForkService(ArtifactRepository(tmp_path / ".terrario"), ROOT)
    snapshot = service.seal_snapshot(source)
    sham = InterventionSpec("C01_SHAM", "CONTROL", "NONE", "NOOP", {})
    sham_result = service.execute(snapshot, identity(), ROOT / "scenarios" / "d0_differences.yaml", sham)
    assert sham_result["verified"] is True
    assert sham_result["control_trace_hash"] == sham_result["intervention_trace_hash"]
    active = InterventionSpec("TEST_ENERGY_DELTA", "TEST_ONLY", "WORLD.AGENT_ENERGY", "ADD", {"delta": -1.0})
    active_result = service.execute(snapshot, identity(), ROOT / "scenarios" / "d0_differences.yaml", active)
    assert active_result["verified"] is True
    assert active_result["first_divergence"]["tick"] == snapshot.tick


def test_snapshot_tamper_and_unsupported_runtime_fail_closed(tmp_path):
    source = runtime(tmp_path); source.step()
    service = CausalForkService(ArtifactRepository(tmp_path / ".terrario"), ROOT)
    snapshot = service.seal_snapshot(source)
    with pytest.raises(ForkError, match="SNAPSHOT_CORRUPT"):
        service.restore(replace(snapshot, payload_hash="0" * 64), identity(), ROOT / "scenarios" / "d0_differences.yaml")
    altered = replace(identity(), agent_identity="A1_REACTIVE")
    candidate = CausalRuntime.create(tmp_path, altered, ROOT / "scenarios" / "d0_differences.yaml")
    assert candidate.capability.classification is Forkability.NOT_FORKABLE
    with pytest.raises(ForkError, match="FORK_NOT_SUPPORTED"):
        service.seal_snapshot(candidate)
