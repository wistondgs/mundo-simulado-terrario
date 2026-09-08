"""RNG Manager — synchronized seeds for reproducibility across Python, NumPy, and PyTorch."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

import numpy as np
import torch


@dataclass
class RNGState:
    """Serializable snapshot of all RNG states."""
    python_state: tuple
    numpy_state: dict[str, Any]
    torch_cpu_state: bytes
    torch_cuda_state: bytes | None


class RNGManager:
    """Manages deterministic random number generation across all subsystems."""

    def __init__(self, master_seed: int):
        self.master_seed = master_seed
        self._python_rng = random.Random(master_seed)
        self._numpy_rng = np.random.default_rng(master_seed)
        self._torch_generator = torch.Generator()
        self._torch_generator.manual_seed(master_seed)

        # Sub-seeds for different subsystems
        self.world_seed = self._python_rng.randint(0, 2**31 - 1)
        self.agent_seed = self._python_rng.randint(0, 2**31 - 1)
        self.observer_seed = self._python_rng.randint(0, 2**31 - 1)

        # Subsystem RNGs
        self._world_rng = random.Random(self.world_seed)
        self._world_np = np.random.default_rng(self.world_seed)
        self._agent_rng = random.Random(self.agent_seed)
        self._agent_np = np.random.default_rng(self.agent_seed)
        self._agent_torch = torch.Generator()
        self._agent_torch.manual_seed(self.agent_seed)

    @property
    def python(self) -> random.Random:
        return self._python_rng

    @property
    def numpy(self) -> np.random.Generator:
        return self._numpy_rng

    @property
    def torch_gen(self) -> torch.Generator:
        return self._torch_generator

    @property
    def world_python(self) -> random.Random:
        return self._world_rng

    @property
    def world_numpy(self) -> np.random.Generator:
        return self._world_np

    @property
    def agent_python(self) -> random.Random:
        return self._agent_rng

    @property
    def agent_numpy(self) -> np.random.Generator:
        return self._agent_np

    @property
    def agent_torch(self) -> torch.Generator:
        return self._agent_torch

    def get_state(self) -> RNGState:
        cuda_state = None
        if torch.cuda.is_available():
            cuda_state = torch.cuda.get_rng_state().cpu().numpy().tobytes()
        return RNGState(
            python_state=self._python_rng.getstate(),
            numpy_state={
                "bit_generator": self._numpy_rng.bit_generator.state,
            },
            torch_cpu_state=self._torch_generator.get_state().numpy().tobytes(),
            torch_cuda_state=cuda_state,
        )

    def set_state(self, state: RNGState) -> None:
        self._python_rng.setstate(state.python_state)
        self._numpy_rng.bit_generator.state = state.numpy_state["bit_generator"]
        self._torch_generator.set_state(
            torch.from_numpy(np.frombuffer(state.torch_cpu_state, dtype=np.uint8).copy())
        )
        if state.torch_cuda_state is not None and torch.cuda.is_available():
            torch.cuda.set_rng_state(
                torch.from_numpy(np.frombuffer(state.torch_cuda_state, dtype=np.uint8).copy())
            )

    @staticmethod
    def set_global_determinism(seed: int) -> None:
        """Set global seeds for maximum reproducibility."""
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
