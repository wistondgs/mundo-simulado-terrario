"""L19: experimental predictive-state acquisition with causal action use.

This namespace is intentionally independent from ``level18``.  In particular,
it does not alter LEARNER-18-v1 or reinterpret its negative verdict.
"""

from .predictive_state import PredictiveStateLearner, PredictiveStateError

__all__ = ["PredictiveStateLearner", "PredictiveStateError"]
