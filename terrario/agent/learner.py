"""Online learner — wraps optimizer for all agent modules.

Handles backward pass, gradient clipping, and optimizer step.
Returns LearningEvent with all metrics.
"""

from __future__ import annotations

import hashlib
from typing import Any

import torch
import torch.nn as nn

from terrario.core.events import LearningEvent


class OnlineLearner:
    """Manages optimization for all learnable agent modules.

    Configurable: learning rate, gradient clipping, update frequency.
    Collects gradient norms and parameter norms for observability.
    """

    def __init__(
        self,
        modules: dict[str, nn.Module],
        lr: float = 3e-4,
        grad_clip: float = 1.0,
        update_frequency: int = 1,
    ):
        self.lr = lr
        self.grad_clip = grad_clip
        self.update_frequency = update_frequency
        self._modules = modules
        self._step_count: int = 0
        self._trace: list[dict[str, Any]] = []

        # Collect all parameters
        all_params: list[torch.Tensor] = []
        for module in modules.values():
            all_params.extend(module.parameters())
        self._optimizer = torch.optim.Adam(all_params, lr=lr)

    @property
    def step_count(self) -> int:
        return self._step_count

    def _gradient_hash(self) -> str:
        """Stable diagnostic captured before commit/cleanup, never a control input."""
        digest = hashlib.sha256()
        for module_name, module in self._modules.items():
            for parameter_name, parameter in module.named_parameters():
                digest.update(f"{module_name}.{parameter_name}".encode())
                if parameter.grad is None:
                    digest.update(b"<none>")
                else:
                    digest.update(parameter.grad.detach().cpu().contiguous().numpy().tobytes())
        return digest.hexdigest()

    def step(
        self,
        world_model_loss: torch.Tensor | None = None,
        policy_loss: torch.Tensor | None = None,
        total_loss: torch.Tensor | None = None,
        *,
        commit: bool = True,
    ) -> LearningEvent | None:
        """Perform one optimization step.

        If total_loss is not provided, it is computed as the sum of
        world_model_loss and policy_loss (whichever are not None).

        Respects update_frequency: only steps every update_frequency calls.

        Args:
            world_model_loss: scalar loss from world model.
            policy_loss: scalar loss from policy.
            total_loss: combined loss (overrides sum if provided).

        Args:
            commit: apply the proposed update.  ``False`` deliberately runs the
                same loss and backward pass but suppresses *only* optimizer
                mutation.  Both paths leave the gradient observable afterwards
                and both discard it at the next step, so a suppressed proposal
                is neither hidden from the observer nor carried forward.

        Returns:
            LearningEvent if an update proposal was computed, None otherwise.
        """
        self._step_count += 1

        if total_loss is None:
            losses = []
            if world_model_loss is not None:
                losses.append(world_model_loss)
            if policy_loss is not None:
                losses.append(policy_loss)
            if not losses:
                return None
            total_loss = sum(losses)

        # Check update frequency
        if self._step_count % self.update_frequency != 0:
            return None

        if not torch.isfinite(total_loss).all():
            self._trace.append({
                "op": "learning_skipped_nonfinite",
                "step": self._step_count,
                "reason": "nonfinite_loss",
            })
            return None

        # Backward pass
        self._optimizer.zero_grad()
        total_loss.backward()

        gradients = [
            parameter.grad
            for module in self._modules.values()
            for parameter in module.parameters()
            if parameter.grad is not None
        ]
        if any(not torch.isfinite(gradient).all() for gradient in gradients):
            self._optimizer.zero_grad()
            self._trace.append({
                "op": "learning_skipped_nonfinite",
                "step": self._step_count,
                "reason": "nonfinite_gradient",
            })
            return None

        # Gradient clipping and norm collection
        grad_norms: dict[str, float] = {}
        param_norms: dict[str, float] = {}

        for name, module in self._modules.items():
            module_grad_norm = 0.0
            module_param_norm = 0.0
            for p in module.parameters():
                if p.grad is not None:
                    module_grad_norm += p.grad.norm().item() ** 2
                module_param_norm += p.norm().item() ** 2
            grad_norms[name] = module_grad_norm ** 0.5
            param_norms[name] = module_param_norm ** 0.5

        # Clip gradients
        all_params = []
        for module in self._modules.values():
            all_params.extend(p for p in module.parameters() if p.grad is not None)
        if all_params:
            torch.nn.utils.clip_grad_norm_(all_params, self.grad_clip)
        gradient_hash = self._gradient_hash()

        # The causal boundary.  Adam's parameter writes and optimizer moments
        # are a single commit: the no-commit arm must not advance either.
        if commit:
            self._optimizer.step()

        # Build loss components
        loss_components: dict[str, float] = {}
        if world_model_loss is not None:
            loss_components["world_model"] = world_model_loss.item()
        if policy_loss is not None:
            loss_components["policy"] = policy_loss.item()

        event = LearningEvent(
            step=self._step_count,
            loss_total=total_loss.item(),
            loss_components=loss_components,
            grad_norms=grad_norms,
            param_norms=param_norms,
            learning_rate=self.lr,
        )

        # `.grad` is NOT cleared here, deliberately.  It belongs to the
        # post-learning scientific state of this tick and stays observable
        # until the next update proposal begins: `forensic_full` reads
        # `parameter.grad` after `learn()` returns, and clearing it here made
        # the observer record no gradients at all.
        #
        # Nothing accumulates as a result.  There is exactly one `backward()`
        # in this method and `zero_grad()` runs unconditionally on the line
        # before it, over the same parameter set the optimizer was built from,
        # so a suppressed proposal is discarded at the next step rather than
        # added to it.  `tests/test_learn_a1_intervention_purity.py` proves
        # that over two consecutive steps instead of asserting it here.

        trace = {
            "op": "learning_step",
            "step": self._step_count,
            "commit_applied": commit,
            "loss_total": total_loss.item(),
            "loss_components": loss_components,
            "grad_norms": grad_norms,
            "gradient_hash": gradient_hash,
            "lr": self.lr,
        }
        self._trace.append(trace)

        return event

    def get_trace(self) -> list[dict[str, Any]]:
        """Return and clear accumulated trace events."""
        events = list(self._trace)
        self._trace.clear()
        return events

    def reset(self) -> None:
        self._step_count = 0
        self._trace.clear()
