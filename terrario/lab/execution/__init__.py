"""Authorized scientific execution.

This package is intentionally unable to import evidence, theory, reference, or
sandbox services.  It produces only raw, content-addressed run artifacts.
"""

from terrario.lab.execution.service import ScientificExecutionService

__all__ = ["ScientificExecutionService"]
