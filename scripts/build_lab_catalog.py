#!/usr/bin/env python
"""Rebuild the persistent Terrario Lab metadata catalog."""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from terrario.lab.read_model import LabReadModel


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default="runs/lab_catalog.json")
    args = parser.parse_args()
    target = LabReadModel(args.root).catalog().save(Path(args.root) / args.output)
    print(target)


if __name__ == "__main__": main()
