"""Checkpoint manager for the Terrario observer subsystem.

Handles periodic saving and loading of agent checkpoints.
Uses safetensors when available, falls back to numpy NPZ.
"""

from __future__ import annotations

import json
import os
import random
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch

try:
    import safetensors.numpy as st_np
    _HAS_SAFETENSORS = True
except ImportError:
    _HAS_SAFETENSORS = False


class CheckpointManager:
    """Manages periodic checkpoint saves for an agent.

    Checkpoints are stored in:
        checkpoint_dir/step_XXXXXXXX/
            params.safetensors  (or params.npz)
            optimizer.safetensors  (or optimizer.npz, optional)
            metadata.json
    """

    def __init__(self, checkpoint_dir: str, save_every_n: int = 100):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.save_every_n = save_every_n

    def maybe_save(self, agent: Any, step: int, metadata: dict | None = None) -> bool:
        """Save checkpoint if step is a multiple of save_every_n.

        Returns True if a checkpoint was saved.
        """
        if step > 0 and step % self.save_every_n == 0:
            self.save(agent, step, metadata)
            return True
        return False

    def save_world_frame(self, frame: dict[str, Any], step: int, reason: str) -> Path:
        """Save a full, rebuildable WorldFrame checkpoint without agent mutation."""
        target = self.checkpoint_dir / f"frame_{step:08d}.json"
        temp = target.with_suffix(".tmp")
        temp.write_text(json.dumps({"step": step, "reason": reason, "frame": frame}, sort_keys=True, separators=(",", ":"), default=str))
        os.replace(temp, target)
        return target

    def save(self, agent: Any, step: int, metadata: dict | None = None) -> None:
        """Force save a checkpoint.

        Extracts parameters from the agent via ``get_parameters()`` and
        optionally ``get_optimizer_state()``. Never modifies the agent.
        """
        ckpt_dir = self.checkpoint_dir / f"step_{step:08d}"
        ckpt_dir.mkdir(parents=True, exist_ok=True)

        params: dict[str, np.ndarray] = {}
        optimizer_state: dict[str, np.ndarray] = {}

        if hasattr(agent, "get_parameters"):
            params = agent.get_parameters()
        if hasattr(agent, "get_optimizer_state"):
            optimizer_state = agent.get_optimizer_state()

        # Convert to numpy if needed
        params = {k: self._to_numpy(v) for k, v in params.items()}
        optimizer_state = {k: self._to_numpy(v) for k, v in optimizer_state.items()}

        if _HAS_SAFETENSORS:
            st_np.save_file(params, str(ckpt_dir / "params.safetensors"))
            if optimizer_state:
                st_np.save_file(
                    optimizer_state, str(ckpt_dir / "optimizer.safetensors")
                )
        else:
            np.savez_compressed(ckpt_dir / "params.npz", **params)
            if optimizer_state:
                np.savez_compressed(ckpt_dir / "optimizer.npz", **optimizer_state)

        meta = dict(metadata) if metadata else {}
        meta["step"] = step
        meta["saved_at"] = time.time()
        with open(ckpt_dir / "metadata.json", "w") as f:
            json.dump(meta, f, indent=2, default=str)

        # Runtime state is local checkpoint material, separate from portable
        # parameter tensors. It enables deterministic CPU replay.
        optimizer = self._optimizer_for(agent)
        runtime = {
            "python": random.getstate(),
            "numpy": np.random.get_state(),
            "torch": torch.get_rng_state(),
            "agent_generator": agent._generator.get_state() if hasattr(agent, "_generator") else None,
            "optimizer": optimizer.state_dict() if optimizer is not None else None,
        }
        torch.save(runtime, ckpt_dir / "runtime_state.pt")

    def load(self, step: int) -> dict:
        """Load a checkpoint by step number.

        Returns a dict with keys: params, optimizer_state, metadata.
        """
        ckpt_dir = self.checkpoint_dir / f"step_{step:08d}"
        if not ckpt_dir.exists():
            raise FileNotFoundError(f"No checkpoint at step {step} in {self.checkpoint_dir}")

        # Load params
        params: dict[str, np.ndarray] = {}
        params_st = ckpt_dir / "params.safetensors"
        params_npz = ckpt_dir / "params.npz"
        if params_st.exists() and _HAS_SAFETENSORS:
            params = dict(st_np.load_file(str(params_st)))
        elif params_npz.exists():
            data = np.load(params_npz)
            params = {k: data[k] for k in data.files}
        else:
            raise FileNotFoundError(f"No params file found in {ckpt_dir}")

        # Load optimizer state
        optimizer_state: dict[str, np.ndarray] = {}
        opt_st = ckpt_dir / "optimizer.safetensors"
        opt_npz = ckpt_dir / "optimizer.npz"
        if opt_st.exists() and _HAS_SAFETENSORS:
            optimizer_state = dict(st_np.load_file(str(opt_st)))
        elif opt_npz.exists():
            data = np.load(opt_npz)
            optimizer_state = {k: data[k] for k in data.files}

        # Load metadata
        metadata: dict = {}
        meta_path = ckpt_dir / "metadata.json"
        if meta_path.exists():
            with open(meta_path) as f:
                metadata = json.load(f)

        runtime_path = ckpt_dir / "runtime_state.pt"
        runtime_state = torch.load(runtime_path, weights_only=False) if runtime_path.exists() else None
        return {
            "params": params,
            "optimizer_state": optimizer_state,
            "metadata": metadata,
            "runtime_state": runtime_state,
        }

    def restore(self, agent: Any, step: int, world_manager: Any | None = None) -> dict:
        """Restore parameters, RNG, and an optional serialized WorldTruth."""
        checkpoint = self.load(step)
        if hasattr(agent, "set_parameters"):
            agent.set_parameters({k: torch.as_tensor(v) for k, v in checkpoint["params"].items()})
        runtime = checkpoint["runtime_state"]
        if runtime is not None:
            random.setstate(runtime["python"])
            np.random.set_state(runtime["numpy"])
            torch.set_rng_state(runtime["torch"])
            if runtime["agent_generator"] is not None and hasattr(agent, "_generator"):
                agent._generator.set_state(runtime["agent_generator"])
            optimizer = self._optimizer_for(agent)
            if optimizer is not None and runtime.get("optimizer") is not None:
                optimizer.load_state_dict(runtime["optimizer"])
        if world_manager is not None and "world_snapshot" in checkpoint["metadata"]:
            world_manager.restore(checkpoint["metadata"]["world_snapshot"])
        return checkpoint

    def list_checkpoints(self) -> list[int]:
        """List all available checkpoint steps, sorted ascending."""
        steps = []
        for d in self.checkpoint_dir.iterdir():
            if d.is_dir() and d.name.startswith("step_"):
                try:
                    steps.append(int(d.name[len("step_"):]))
                except ValueError:
                    continue
        return sorted(steps)

    def get_latest(self) -> int | None:
        """Get the latest checkpoint step, or None if no checkpoints exist."""
        steps = self.list_checkpoints()
        return steps[-1] if steps else None

    @staticmethod
    def _to_numpy(value: Any) -> np.ndarray:
        """Convert a value to numpy array, handling torch tensors."""
        if isinstance(value, np.ndarray):
            return value
        # Handle torch tensors without importing torch at module level
        if hasattr(value, "detach"):
            return value.detach().cpu().numpy()
        if hasattr(value, "cpu") and hasattr(value, "numpy"):
            return value.cpu().numpy()
        return np.asarray(value)

    @staticmethod
    def _optimizer_for(agent: Any):
        optimizer = getattr(agent, "_optimizer", None)
        if optimizer is not None:
            return optimizer
        learner = getattr(agent, "learner", None)
        return getattr(learner, "_optimizer", None)
