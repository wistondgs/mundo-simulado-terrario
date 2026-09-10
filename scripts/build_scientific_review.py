"""Freeze the portfolio input and write a deterministic, non-executing scientific review."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import fields, is_dataclass
from enum import Enum
from pathlib import Path
from typing import Mapping

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from terrario.lab.api import LabAPI
from terrario.lab.theory.scientific_review import canonical_portfolio_payload, payload_bytes, review_portfolio


def plain(value):
    if is_dataclass(value): return {f.name:plain(getattr(value,f.name)) for f in fields(value)}
    if isinstance(value,Mapping): return {str(k):plain(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)): return [plain(v) for v in value]
    if isinstance(value,Enum): return value.value
    return value


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--root",default="."); args=parser.parse_args()
    root=Path(args.root).resolve(); portfolio=LabAPI(root).experiment_portfolio
    if portfolio is None: raise SystemExit("No frozen theory portfolio is available")
    payload=canonical_portfolio_payload(portfolio); raw=payload_bytes(payload); digest=hashlib.sha256(raw).hexdigest()
    out=root/"scientific_reviews"/f"review-{digest[:16]}"; out.mkdir(parents=True,exist_ok=True)
    (out/"portfolio_review_input.json").write_bytes(raw)
    report=review_portfolio(portfolio)
    (out/"scientific_review.json").write_text(json.dumps(plain(report),sort_keys=True,ensure_ascii=False,indent=2)+"\n")
    manifest={"portfolio_input_sha256":digest,"theory_snapshot":portfolio.snapshot_id,"reviewer_version":report.reviewer_version,"portfolios":len(report.reviews),"top_candidates":report.top_candidates,"scientific_evidence":False,"experiments_executed":False}
    (out/"review_manifest.json").write_text(json.dumps(plain(manifest),sort_keys=True,indent=2)+"\n")
    print(out); print(digest)


if __name__ == "__main__": main()
