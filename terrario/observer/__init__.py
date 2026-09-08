"""Terrario observer subsystem — first-class scientific instrumentation."""

from terrario.observer.trace import (
    ConsequenceTrace,
    DecisionTrace,
    LearningTrace,
    MemoryTrace,
    PerceptionTrace,
    PredictionTrace,
    ProvenanceTrace,
    SensationTrace,
    TemporalTrace,
    WorldTrace,
    TRACE_REGISTRY,
)
from terrario.observer.storage import StorageManager
from terrario.observer.logger import ScientificObserver
from terrario.observer.checkpoints import CheckpointManager
from terrario.observer.probes import ProbeInterface, LinearProbe

__all__ = [
    "ConsequenceTrace",
    "DecisionTrace",
    "LearningTrace",
    "MemoryTrace",
    "PerceptionTrace",
    "PredictionTrace",
    "ProvenanceTrace",
    "SensationTrace",
    "TemporalTrace",
    "WorldTrace",
    "TRACE_REGISTRY",
    "StorageManager",
    "ScientificObserver",
    "CheckpointManager",
    "ProbeInterface",
    "LinearProbe",
]
