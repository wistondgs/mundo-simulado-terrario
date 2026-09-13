"""Layered storage manager for the Terrario observer subsystem.

Handles persistence of trace events, tensors, checkpoints, and manifests.
Falls back to JSONL/NPZ when pyarrow/zarr/safetensors are unavailable.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import numpy as np

from terrario.observer.trace import TRACE_REGISTRY

# Optional dependencies — degrade gracefully
try:
    import pyarrow as pa
    import pyarrow.parquet as pq
    _HAS_PARQUET = True
except ImportError:
    _HAS_PARQUET = False

try:
    import zarr
    _HAS_ZARR = True
except ImportError:
    _HAS_ZARR = False

try:
    import safetensors.numpy as st_np
    _HAS_SAFETENSORS = True
except ImportError:
    _HAS_SAFETENSORS = False

try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False


class StorageManager:
    """Manages layered storage for observer data.

    Directory layout:
        run_dir/
            manifest.yaml
            events/       — one file per trace type (parquet or jsonl)
            tensors/      — zarr stores or npz files (forensic_full only)
            checkpoints/  — safetensors + JSON metadata
            derived/      — computed artifacts
    """

    VALID_MODES = ("performance", "scientific_standard", "forensic_full")

    def __init__(self, run_dir: str, mode: str = "scientific_standard"):
        if mode not in self.VALID_MODES:
            raise ValueError(f"Invalid mode '{mode}'. Must be one of {self.VALID_MODES}")

        self.run_dir = Path(run_dir)
        self.mode = mode
        self._buffers: dict[str, list[dict]] = {}
        self._flush_threshold = 100
        self._closed = False

        # Create directory structure
        for subdir in ("events", "tensors", "checkpoints", "derived"):
            (self.run_dir / subdir).mkdir(parents=True, exist_ok=True)

        # Track zarr stores for tensors
        self._zarr_stores: dict[str, Any] = {}

    # ── Manifest ──────────────────────────────────────────────────────

    def save_manifest(self, config: dict) -> None:
        """Save run configuration as manifest."""
        manifest_path = self.run_dir / "manifest.yaml"
        manifest = {
            "config": config,
            "mode": self.mode,
            "created_at": time.time(),
            "storage_backend": {
                "events": "parquet" if _HAS_PARQUET else "jsonl",
                "tensors": "zarr" if _HAS_ZARR else "npz",
                "checkpoints": "safetensors" if _HAS_SAFETENSORS else "npz",
            },
        }
        if _HAS_YAML:
            with open(manifest_path, "w") as f:
                yaml.dump(manifest, f, default_flow_style=False)
        else:
            # Fallback to JSON if yaml unavailable
            manifest_path = self.run_dir / "manifest.json"
            with open(manifest_path, "w") as f:
                json.dump(manifest, f, indent=2, default=str)

    # ── Trace Events ──────────────────────────────────────────────────

    def save_trace_events(self, events: list, step: int) -> None:
        """Buffer trace events and flush when threshold is reached.

        Events are grouped by trace type name (derived from class name).
        """
        for event in events:
            trace_name = self._trace_name(event)
            if trace_name not in self._buffers:
                self._buffers[trace_name] = []
            self._buffers[trace_name].append(event.to_dict())

        # Flush any buffer that has reached the threshold
        for trace_name, buf in self._buffers.items():
            if len(buf) >= self._flush_threshold:
                self._flush_buffer(trace_name)

    def append_authoritative_jsonl(self, name: str, record: dict[str, Any]) -> tuple[int, int]:
        """Durably append one Observer record and return its byte span.

        Live sandbox traces use this primitive instead of buffered Parquet so
        publication can never precede persistence. Derived indexes may safely
        be rebuilt from the resulting JSONL.
        """
        path = self.run_dir / "events" / f"{name}.jsonl"
        encoded = json.dumps(record, sort_keys=True, separators=(",", ":"), default=str).encode() + b"\n"
        with path.open("ab") as handle:
            offset = handle.tell(); handle.write(encoded); handle.flush(); os.fsync(handle.fileno())
        return offset, len(encoded)

    def flush_all(self) -> None:
        """Flush all buffered events to disk."""
        for trace_name in list(self._buffers.keys()):
            self._flush_buffer(trace_name)

    def _flush_buffer(self, trace_name: str) -> None:
        """Write buffered events for a trace type to disk."""
        buf = self._buffers.get(trace_name, [])
        if not buf:
            return

        if _HAS_PARQUET:
            self._write_parquet(trace_name, buf)
        else:
            self._write_jsonl(trace_name, buf)

        self._buffers[trace_name] = []

    def _write_parquet(self, trace_name: str, records: list[dict]) -> None:
        """Append records to a Parquet file."""
        path = self.run_dir / "events" / f"{trace_name}.parquet"

        # Flatten nested dicts/lists to JSON strings for Parquet compatibility
        flat_records = []
        for rec in records:
            flat = {}
            for k, v in rec.items():
                if isinstance(v, (dict, list, tuple)):
                    flat[k] = json.dumps(v, default=str)
                elif v is None:
                    flat[k] = None
                else:
                    flat[k] = v
            flat_records.append(flat)

        new_table = pa.Table.from_pylist(flat_records)

        if path.exists():
            existing = pq.read_table(path)
            combined = pa.concat_tables([existing, new_table])
            pq.write_table(combined, path)
        else:
            pq.write_table(new_table, path)

    def _write_jsonl(self, trace_name: str, records: list[dict]) -> None:
        """Append records to a JSONL file."""
        path = self.run_dir / "events" / f"{trace_name}.jsonl"
        with open(path, "a") as f:
            for rec in records:
                f.write(json.dumps(rec, default=str) + "\n")

    # ── Tensors ───────────────────────────────────────────────────────

    def save_tensor(self, name: str, tensor: np.ndarray, step: int) -> None:
        """Save a tensor. Only active in forensic_full mode."""
        if self.mode != "forensic_full":
            return

        if _HAS_ZARR:
            self._save_tensor_zarr(name, tensor, step)
        else:
            self._save_tensor_npz(name, tensor, step)

    def _save_tensor_zarr(self, name: str, tensor: np.ndarray, step: int) -> None:
        """Save tensor to a Zarr store, appending along the step axis."""
        store_path = str(self.run_dir / "tensors" / f"{name}.zarr")

        if name not in self._zarr_stores:
            if os.path.exists(store_path):
                self._zarr_stores[name] = zarr.open(store_path, mode="a")
            else:
                self._zarr_stores[name] = zarr.open(
                    store_path,
                    mode="w",
                    shape=(0,) + tensor.shape,
                    chunks=(1,) + tensor.shape,
                    dtype=tensor.dtype,
                )

        z = self._zarr_stores[name]
        z.append(tensor[np.newaxis], axis=0)

    def _save_tensor_npz(self, name: str, tensor: np.ndarray, step: int) -> None:
        """Save tensor as an NPZ file (one per step)."""
        tensor_dir = self.run_dir / "tensors" / name
        tensor_dir.mkdir(parents=True, exist_ok=True)
        path = tensor_dir / f"step_{step:08d}.npz"
        np.savez_compressed(path, tensor=tensor, step=step)

    # ── Checkpoints ───────────────────────────────────────────────────

    def save_checkpoint(
        self,
        agent_params: dict[str, np.ndarray],
        optimizer_state: dict[str, np.ndarray],
        step: int,
        metadata: dict | None = None,
    ) -> None:
        """Save a checkpoint with agent parameters and optimizer state."""
        ckpt_dir = self.run_dir / "checkpoints" / f"step_{step:08d}"
        ckpt_dir.mkdir(parents=True, exist_ok=True)

        if _HAS_SAFETENSORS:
            st_np.save_file(agent_params, str(ckpt_dir / "params.safetensors"))
            if optimizer_state:
                st_np.save_file(optimizer_state, str(ckpt_dir / "optimizer.safetensors"))
        else:
            np.savez_compressed(ckpt_dir / "params.npz", **agent_params)
            if optimizer_state:
                np.savez_compressed(ckpt_dir / "optimizer.npz", **optimizer_state)

        meta = metadata or {}
        meta["step"] = step
        meta["saved_at"] = time.time()
        with open(ckpt_dir / "metadata.json", "w") as f:
            json.dump(meta, f, indent=2, default=str)

    def load_checkpoint(
        self, step: int
    ) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], dict]:
        """Load a checkpoint by step number."""
        ckpt_dir = self.run_dir / "checkpoints" / f"step_{step:08d}"
        if not ckpt_dir.exists():
            raise FileNotFoundError(f"No checkpoint at step {step}")

        # Load params
        params_path_st = ckpt_dir / "params.safetensors"
        params_path_npz = ckpt_dir / "params.npz"
        if params_path_st.exists() and _HAS_SAFETENSORS:
            params = st_np.load_file(str(params_path_st))
        elif params_path_npz.exists():
            data = np.load(params_path_npz)
            params = {k: data[k] for k in data.files}
        else:
            raise FileNotFoundError(f"No params file in {ckpt_dir}")

        # Load optimizer state
        optimizer_state: dict[str, np.ndarray] = {}
        opt_path_st = ckpt_dir / "optimizer.safetensors"
        opt_path_npz = ckpt_dir / "optimizer.npz"
        if opt_path_st.exists() and _HAS_SAFETENSORS:
            optimizer_state = st_np.load_file(str(opt_path_st))
        elif opt_path_npz.exists():
            data = np.load(opt_path_npz)
            optimizer_state = {k: data[k] for k in data.files}

        # Load metadata
        meta_path = ckpt_dir / "metadata.json"
        metadata = {}
        if meta_path.exists():
            with open(meta_path) as f:
                metadata = json.load(f)

        return params, optimizer_state, metadata

    # ── Summary ───────────────────────────────────────────────────────

    def get_run_summary(self) -> dict:
        """Get summary statistics for this run."""
        summary: dict[str, Any] = {
            "run_dir": str(self.run_dir),
            "mode": self.mode,
            "storage_backend": {
                "events": "parquet" if _HAS_PARQUET else "jsonl",
                "tensors": "zarr" if _HAS_ZARR else "npz",
                "checkpoints": "safetensors" if _HAS_SAFETENSORS else "npz",
            },
            "event_files": {},
            "checkpoints": [],
            "tensor_stores": [],
        }

        # Event files
        events_dir = self.run_dir / "events"
        if events_dir.exists():
            for f in sorted(events_dir.iterdir()):
                if f.suffix in (".parquet", ".jsonl"):
                    size = f.stat().st_size
                    summary["event_files"][f.stem] = {
                        "file": f.name,
                        "size_bytes": size,
                    }
                    if f.suffix == ".jsonl":
                        with open(f) as fh:
                            summary["event_files"][f.stem]["num_records"] = sum(
                                1 for _ in fh
                            )

        # Checkpoints
        ckpt_dir = self.run_dir / "checkpoints"
        if ckpt_dir.exists():
            for d in sorted(ckpt_dir.iterdir()):
                if d.is_dir() and d.name.startswith("step_"):
                    summary["checkpoints"].append(d.name)

        # Tensor stores
        tensors_dir = self.run_dir / "tensors"
        if tensors_dir.exists():
            for item in sorted(tensors_dir.iterdir()):
                summary["tensor_stores"].append(item.name)

        return summary

    # ── Lifecycle ─────────────────────────────────────────────────────

    def close(self) -> None:
        """Flush all buffers and release resources."""
        if self._closed:
            return
        self.flush_all()
        self._zarr_stores.clear()
        self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    # ── Helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _trace_name(event) -> str:
        """Derive the trace type name from an event instance.

        Uses the TRACE_REGISTRY to map class names to short names.
        """
        cls_name = type(event).__name__
        for name, cls in TRACE_REGISTRY.items():
            if cls.__name__ == cls_name:
                return name
        return cls_name.lower()
