"""Sealing a campaign without asking a person, and without loosening anything.

The rail closes a preregistration with `create -> submit -> review -> decide ->
lock`, and `lock` refuses unless a review decision approves that exact bundle
root and the accepted warnings match the current ones exactly.  What makes that
sound is the binding to the hash and to the warning set -- not that a human
produced it.

So the two things it currently conflates come apart here:

    preregistered immutability  !=  human approval

A campaign seals deterministically, and it earns that by being *unable to
waive*.  The human path may accept a non-blocking finding by enumerating it;
this path refuses to seal while any finding exists at all.  That makes the
autonomous seal strictly stricter than the reviewed one, which is the only
version of "no human required" worth having: the gate is not being skipped, it
is being made impossible to argue with.

A campaign must also seal what its gates certify.  That is the one commitment
with no equivalent anywhere in the rail, and the one whose absence let the
fusion evaluate `F-9` as the tick while the preregistration gave that number to
passivity.
"""

from __future__ import annotations

from typing import Any, Mapping

from terrario.lab.preregistration.domain import ReviewDecisionValue

#: Not a person, and it must never look like one.  The rail records five human
#: gates under the literal `"local-user"`; an autonomous seal that borrowed that
#: string would be indistinguishable from a review that never happened.
DETERMINISTIC_ACTOR = "deterministic-campaign-seal"

CAMPAIGN_SEAL_SCHEMA = "terrario.lab.campaign-seal/v1"


class CampaignSealRefused(RuntimeError):
    """Refusal to seal, with the codes that caused it.

    Carries them rather than a message so a caller can act on the reason: a
    blocking finding is a draft to fix, a warning is a human decision to ask
    for, and an absent gate manifest is a campaign that has not said what it
    intends to certify.
    """

    def __init__(self, codes: tuple[str, ...]):
        self.codes = tuple(sorted(set(codes)))
        super().__init__("; ".join(self.codes))


def seal_campaign(service, *, preregistration_id: str, expected_hash: str,
                  reason: str, idempotency_key: str | None = None) -> Mapping[str, Any]:
    """Take an existing draft from DRAFT to LOCKED with no human in the path.

    Every check the reviewed path performs still runs -- readiness, the rebuild
    of the bundle root, the hash comparison in `lock` -- and two more that only
    apply here: no warnings at all, and a sealed gate manifest.
    """
    refusals: list[str] = []

    report = service.readiness(preregistration_id)
    blocking = tuple(f["finding_hash"] for f in report.get("findings", ()) if f.get("blocking"))
    warnings = tuple(f["finding_hash"] for f in report.get("findings", ()) if not f.get("blocking"))
    if blocking:
        refusals.extend(f"BLOCKING_FINDING:{h}" for h in blocking)
    if warnings:
        # The reviewed path can accept these by enumerating them.  This one
        # cannot: a deterministic actor waiving a scientific warning would be
        # the rubber stamp the whole boundary exists to prevent.
        refusals.extend(f"WARNING_REQUIRES_HUMAN_ACCEPTANCE:{h}" for h in warnings)

    draft = service._draft_from_record(
        service.artifacts.current(preregistration_id, "Preregistration"))
    if draft.gates is None:
        refusals.append("GATE_MANIFEST_ABSENT")
    refusals.extend(_construct_validation_drift(service, draft))

    if refusals:
        raise CampaignSealRefused(tuple(refusals))

    prepared = service.prepare_review(preregistration_id, expected_hash,
                                      DETERMINISTIC_ACTOR, reason)
    root_hash = prepared["bundle_root_hash"]
    request = service.submit(preregistration_id, DETERMINISTIC_ACTOR, reason)
    decision = service.decide(
        request["review_id"], root_hash,
        ReviewDecisionValue.APPROVE_PREREGISTRATION.value, reason,
        # Empty, and it has to be: `lock` compares this against the current
        # warnings, so an autonomous seal can only succeed when there are none.
        (), DETERMINISTIC_ACTOR)
    attestation = service.lock(preregistration_id, root_hash, decision["decision_id"],
                               reason, DETERMINISTIC_ACTOR, idempotency_key)
    return {
        "schema_version": CAMPAIGN_SEAL_SCHEMA,
        "preregistration_id": preregistration_id,
        "bundle_root_hash": root_hash,
        "gate_manifest_hash": draft.gates.manifest_hash,
        "sealed_gates": len(draft.gates.gates),
        "decision_id": decision["decision_id"],
        "approved_by": DETERMINISTIC_ACTOR,
        "accepted_warnings": [],
        "attestation": attestation,
    }


def _construct_validation_drift(service, draft) -> tuple[str, ...]:
    """Refuse a draft whose metrics claim a validation the registry does not grant.

    Measured while building this path: `validate_preregistration` reads
    `metric.validation_status` off the draft, and `derive` lets a client set any
    key the draft already has.  So a caller could mark a metric
    `VALIDATED_FOR_CONSTRUCT` and `PR-PROXY-001` would simply stop firing --
    which would make "this door cannot waive a warning" theatre, since the
    warning could be removed upstream of the door.

    The registry is the authority on what a metric is validated for, exactly as
    `instrument_registry` is for instruments, so the claim is compared against it
    rather than believed.  Scoped to the autonomous path: the reviewed one has a
    person who can be shown the discrepancy, and tightening the shared validator
    changes what 141 stored preregistrations report.
    """
    drift: list[str] = []
    for metric in draft.metrics:
        try:
            definition = service.metrics.get(metric.metric_id)
        except Exception:
            drift.append(f"METRIC_NOT_IN_REGISTRY:{metric.metric_id}")
            continue
        granted = getattr(definition, "construct_validation_status", None)
        granted = getattr(granted, "value", granted)
        if granted is not None and str(metric.validation_status) != str(granted):
            drift.append(f"CONSTRUCT_VALIDATION_DRIFT:{metric.metric_id}:"
                         f"draft={metric.validation_status}:registry={granted}")
    return tuple(drift)
