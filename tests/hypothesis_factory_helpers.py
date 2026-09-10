from dataclasses import replace

from terrario.lab.models import EpistemicStatus
from terrario.lab.theory.factory import ExperimentDesignCompiler, RivalHypothesisGenerator, ReviewState
from terrario.lab.theory.models import HyperedgeCandidateRecord


def edge(identifier="HYPERCAND-TEST", components=("memory", "attention", "feedback")):
    return HyperedgeCandidateRecord(id=f"hyperedge:{identifier}", original_id=identifier,
        original_text="candidate conjunction", source_artifact="HYPEREDGE_CANDIDATES_v0.2.md",
        source_version="v0.2", provenance="test fixture", epistemic_status=EpistemicStatus.UNTESTED_HYPOTHESIS,
        components=components, predicted_outcome="adaptive transfer", attribution="candidate synthesis",
        conjunction_explicitness="candidate", necessity="unresolved", sufficiency="unresolved",
        level="individual", discriminating_test="matched ablation", confounders=(), decision="retain")


def family(identifier="HYPERCAND-TEST", components=("memory", "attention", "feedback")):
    return RivalHypothesisGenerator().generate(edge(identifier, components), "snapshot-test", ("claim:1",))


def design():
    reviewed=replace(family(), review_state=ReviewState.APPROVED_FOR_EXPERIMENT_DESIGN)
    return ExperimentDesignCompiler().compile(reviewed)
