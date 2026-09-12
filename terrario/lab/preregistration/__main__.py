"""Local human-facing CLI for preregistration governance."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from terrario.lab.api import LabAPI


def _json_arg(value: str | None) -> dict:
    if not value: return {}
    path = Path(value)
    return json.loads(path.read_text() if path.is_file() else value)


def _emit(value) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m terrario.lab.preregistration")
    parser.add_argument("--root", default=".")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("list", "show", "validate", "create", "derive", "readiness", "prepare-review",
                 "submit", "review", "lock", "verify", "diff", "exposures", "amend",
                 "deviation", "supersede", "withdraw", "export", "import", "audit"):
        command = sub.add_parser(name)
        command.add_argument("id", nargs="?")
        command.add_argument("--json")
        command.add_argument("--reason")
        command.add_argument("--expected-hash")
    args = parser.parse_args(argv)
    api = LabAPI(Path(args.root))
    service, actor = api.preregistrations, os.environ.get("USER", "local-user")
    p = _json_arg(getattr(args, "json", None)); cmd = args.command
    if cmd == "list": value = service.list()
    elif cmd == "show": value = service.get(args.id)
    elif cmd == "validate": value = service.validate_request(p)
    elif cmd == "create": value = service.create(p, actor)
    elif cmd == "derive": value = service.derive(args.id, args.expected_hash or p["expected_hash"], p.get("changes", p), args.reason or p.get("reason", "CLI derivation"), actor)
    elif cmd == "readiness": value = service.readiness(args.id)
    elif cmd == "prepare-review": value = service.prepare_review(args.id, args.expected_hash or p["expected_hash"], actor, args.reason or "CLI review preparation")
    elif cmd == "submit": value = service.submit(args.id, actor, args.reason or "CLI review submission")
    elif cmd == "review": value = service.decide(p["review_id"], p["artifact_hash"], p["decision"], args.reason or p["reason"], tuple(p.get("warning_acceptances", ())), actor)
    elif cmd == "lock":
        current = service.get(args.id); root = args.expected_hash or p.get("expected_hash") or current["scientific_hash"]
        package = service.review_package(args.id)
        print(f"Root: {root}\nTrials: {package['readiness']['trial_count']}\nPrimary endpoints: {package['summary']['primary_endpoints']}")
        print(f"Warnings: {[x['finding_hash'] for x in package['readiness']['findings'] if not x['blocking']]}")
        confirmation = input(f"Type LOCK {root[:12]}: ")
        if confirmation != f"LOCK {root[:12]}": raise SystemExit("lock confirmation rejected")
        reason = args.reason or input("Reason: ").strip()
        if not reason: raise SystemExit("lock reason is required")
        value = service.lock(args.id, root, p["decision_id"], reason, actor, p.get("idempotency_key"))
    elif cmd == "verify": value = service.verify(args.id)
    elif cmd == "diff": value = service.get(args.id)["payload"].get("scientific_diff", {})
    elif cmd == "exposures": value = service.exposure_records(p.get("scenario_id"), p.get("world_seed"))
    elif cmd in {"amend", "deviation"}: value = service.add_postlock_record(args.id, "PreregistrationAmendment" if cmd == "amend" else "ProtocolDeviation", p, actor)
    elif cmd == "withdraw": value = service.withdraw(args.id, args.reason or p["reason"], actor)
    elif cmd == "export": value = service.export(args.id)
    elif cmd == "import": value = service.import_portable(p, actor)
    elif cmd == "supersede": raise SystemExit("supersede requires a separately reviewed and locked descendant; no unsafe shortcut exists")
    elif cmd == "audit": value = service.audit_chain(args.id)
    else: raise SystemExit("unsupported command")
    _emit(value); return 0


if __name__ == "__main__":
    raise SystemExit(main())
