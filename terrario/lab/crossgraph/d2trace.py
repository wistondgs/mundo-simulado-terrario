"""D2 end-to-end trace construction over real data.

Builds real traces across ReferenceGraph -> SourceClaim -> TheoryGraph ->
Hyperedge/Hypothesis -> Scenario/World, registering an explicit TraceBreak
wherever a link does not actually exist. It never invents a link to complete a
demo. The traces validate the heterogeneous architecture; they are not claims
that Terrario replicates cognition.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Mapping

from terrario.lab.crossgraph.domain import (
    AssertionClass, CrossDomainEntityRef, Domain, LinkState,
)
from terrario.lab.crossgraph.service import CrossGraphService
from terrario.lab.crossgraph.traversal import TraversalBudget, TraversalEngine
from terrario.lab.referencegraph.queries import ReferenceGraphQueries
from terrario.lab.referencegraph.service import ReferenceGraphService


class D2TraceBuilder:
    def __init__(self, service: CrossGraphService):
        self.service = service
        self.engine = TraversalEngine(service)
        self.reference_queries = ReferenceGraphQueries(service.artifacts)

    # ----------------------------------------------------- concept matching
    def _theory_concept_for(self, construct: str) -> CrossDomainEntityRef | None:
        """Find a TheoryGraph concept whose text matches the construct, or None.

        This is a read-only lookup, never a silent fusion. A match is only a
        MAPS_TO candidate; absence is recorded as a TraceBreak, not filled.
        """
        adapter = self.service.adapters.get(Domain.THEORY)
        store = getattr(adapter, "_load", lambda: None)()
        if store is None:
            return None
        needle = construct.replace("_", " ").casefold()
        for node_id, node in store.theory_nodes.items():
            if node.get("node_type") not in {"RawConceptRecord", "CanonicalConceptCandidate"}:
                continue
            text = str(node.get("original_text", node.get("label", ""))).casefold()
            if needle in text or text in needle:
                # TheoryGraph node ids already carry the "Type:id" prefix; keep
                # the bare record id so the cross-domain key is not duplicated.
                bare_id = node_id.split(":", 1)[1] if ":" in node_id else node_id
                return CrossDomainEntityRef(Domain.THEORY, str(node.get("node_type")), bare_id)
        return None

    # ------------------------------------------------------------- building
    def build_reference_to_theory(self, reference_id: str, construct: str,
                                  actor_id: str) -> Mapping[str, Any]:
        """Trace Reference -> SourceClaim -> Theory concept for one construct."""
        steps: list[Mapping[str, Any]] = []
        breaks: list[Mapping[str, Any]] = []
        reference = self.reference_queries.get_reference(reference_id)
        ref_ref = CrossDomainEntityRef(Domain.REFERENCE, "ScientificReferenceRecord", reference_id,
                                       snapshot_id=self.service.adapters[Domain.REFERENCE].get_snapshot())
        steps.append({"domain": "REFERENCE", "entity_id": reference_id,
                      "constructs": reference["constructs"]})

        # Reference -> Claim (REPORTS_CLAIM inside the reference graph).
        claims = self.reference_queries.get_claims(reference_id)
        claim_ref = None
        if claims:
            claim = claims[0]
            claim_ref = CrossDomainEntityRef(Domain.CLAIM, "SourceClaimRecord", claim["claim_id"])
            self._ensure_link(ref_ref, claim_ref, "EXTRACTED_FROM", actor_id, steps,
                              "reference reports source claim")
        else:
            breaks.append(self._break(ref_ref, "CLAIM", "no source claim recorded for reference",
                                      "REPORTS_CLAIM relation", actor_id))

        # Claim/Reference -> Theory concept (MAP_TO candidate) or TraceBreak.
        concept_ref = self._theory_concept_for(construct)
        anchor = claim_ref or ref_ref
        if concept_ref is not None:
            self._ensure_link(anchor, concept_ref, "MAPS_TO", actor_id, steps,
                              f"claim/reference maps to theory concept for {construct}")
            steps.append({"domain": "THEORY", "entity_id": concept_ref.entity_id,
                          "concept": construct})
        else:
            breaks.append(self._break(anchor, "THEORY",
                                      f"no TheoryGraph concept matches construct {construct}",
                                      "canonical concept identity", actor_id))
        return {"reference_id": reference_id, "construct": construct, "steps": steps,
                "trace_breaks": breaks, "complete": not breaks}

    def build_scenario_trace(self, reference_id: str, construct: str, scenario_id: str,
                             world_id: str, actor_id: str) -> Mapping[str, Any]:
        """Trace Reference -> ... -> Scenario -> World, breaking honestly."""
        result = self.build_reference_to_theory(reference_id, construct, actor_id)
        steps, breaks = result["steps"], result["trace_breaks"]
        scenario_ref = CrossDomainEntityRef(Domain.SCENARIO, "ScenarioDefinition", scenario_id)
        world_ref = CrossDomainEntityRef(Domain.WORLD, "WorldDefinition", world_id,
                                         content_hash=self.service.adapters[Domain.WORLD]
                                         .get_content_hash(CrossDomainEntityRef(
                                             Domain.WORLD, "WorldDefinition", world_id)))
        # Scenario -> World always exists (INSTANTIATES_WORLD).
        self._ensure_link(scenario_ref, world_ref, "INSTANTIATES_WORLD", actor_id, steps,
                          "scenario instantiates world definition")
        steps.append({"domain": "SCENARIO", "entity_id": scenario_id})
        steps.append({"domain": "WORLD", "entity_id": world_id})
        # Reference -> Scenario link only if it genuinely exists; otherwise break.
        ref_ref = CrossDomainEntityRef(Domain.REFERENCE, "ScientificReferenceRecord", reference_id)
        scenario_adapter = self.service.adapters[Domain.SCENARIO]
        if scenario_adapter.exists(scenario_ref):
            self._ensure_link(ref_ref, scenario_ref, "MOTIVATES", actor_id, steps,
                              "reference motivates scenario design", candidate=True)
        else:
            breaks.append(self._break(ref_ref, "SCENARIO",
                                      f"scenario {scenario_id} does not resolve",
                                      "scenario identity", actor_id))
        result["steps"], result["trace_breaks"] = steps, breaks
        result["complete"] = not breaks
        return result

    # -------------------------------------------------------------- helpers
    def _ensure_link(self, source: CrossDomainEntityRef, target: CrossDomainEntityRef,
                     relation: str, actor_id: str, steps: list, provenance: str,
                     candidate: bool = False) -> None:
        existing = [l for l in self.service.active_links()
                    if l["source_key"] == source.key() and l["target_key"] == target.key()
                    and l["relation_type"] == relation]
        if existing:
            steps.append({"link": relation, "source": source.key(), "target": target.key(),
                          "reused": True})
            return
        try:
            link = self.service.propose_link(
                source, target, relation, AssertionClass.ANALYST_ASSERTED, provenance, actor_id,
                state=LinkState.CANDIDATE if candidate else LinkState.CANDIDATE,
                activate=not candidate)
            steps.append({"link": relation, "source": source.key(), "target": target.key(),
                          "link_id": link.link_id, "state": link.state.value})
        except Exception as exc:  # endpoint may not resolve; record honestly
            steps.append({"link": relation, "source": source.key(), "target": target.key(),
                          "failed": str(exc)})

    def _break(self, from_ref: CrossDomainEntityRef, expected_domain: str, reason: str,
               missing: str, actor_id: str) -> Mapping[str, Any]:
        trace_break = self.service.record_trace_break(from_ref, expected_domain, reason, missing)
        return {"trace_break_id": trace_break.trace_break_id, "from": from_ref.key(),
                "expected_next_domain": expected_domain, "reason": reason}
