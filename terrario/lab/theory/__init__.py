"""Immutable corpus snapshot and theory-graph integration."""

from terrario.lab.theory.compiler import HypothesisCompiler
from terrario.lab.theory.ingestion import TheoryIngestor
from terrario.lab.theory.snapshot import TheorySnapshotBuilder
from terrario.lab.theory.store import TheoryGraphStore
from terrario.lab.theory.factory import (
    ExperimentDesignCompiler, HypothesisFamily, RivalHypothesisGenerator,
    build_portfolio,
)

__all__ = ["HypothesisCompiler", "TheoryIngestor", "TheorySnapshotBuilder", "TheoryGraphStore", "ExperimentDesignCompiler", "HypothesisFamily", "RivalHypothesisGenerator", "build_portfolio"]
