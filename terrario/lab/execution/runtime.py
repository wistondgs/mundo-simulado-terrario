"""Narrow adapter to the public episode loop for an already-built trial.

No call path here invokes ``ExperimentController.run`` (which derives an agent
seed), the legacy specification runner (which produces evidence), or sandbox code.
The orchestrator supplies the independently committed world and agent seeds.
"""
from __future__ import annotations

from typing import Any, Mapping

from terrario.experiment.controller import ExperimentController


def run_exact_trial(controller: ExperimentController, *, agent: Any, world_state_manager: Any,
                    physics: Any, rule_engine: Any, scheduler: Any, observer: Any,
                    world_seed: int, agent_seed: int, scenario: Mapping[str, Any],
                    learning_enabled: bool = True) -> Mapping[str, Any]:
    """Run one independently seeded attempt through the public episode loop.

    ``world_seed`` must already have been used to materialize the world by the
    caller. The explicit agent seed is passed unmodified to `run_episode`.
    Both are returned in the raw result so artifact sealing can attest them.
    """
    result = controller.run_episode(agent, world_state_manager, physics, rule_engine,
                                    scheduler, observer, int(agent_seed),
                                    scenario=dict(scenario), learning_enabled=learning_enabled,
                                    phase="scientific_execution")
    return {"world_seed": int(world_seed), "agent_seed": int(agent_seed), "episode": result,
            "classification": "SCIENTIFIC_RAW_ARTIFACT"}
