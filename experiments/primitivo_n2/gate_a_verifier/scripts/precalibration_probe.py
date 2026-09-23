#!/usr/bin/env python3
"""Pre-calibration byte-preservation probe; invoked by verify_gate_a.py without mutating replicas."""
from verify_gate_a import precal, A1, A2
import json
if __name__ == "__main__": print(json.dumps({"A1":precal(A1,"A1"),"A2":precal(A2,"A2")}, indent=2))
