"""Memory systems — episodic and long-term memory for agents.

EpisodicMemory: circular buffer of experience tuples with cosine-similarity retrieval.
LongTermMemory: learnable memory matrix with attention read and gated write.
"""

from __future__ import annotations

from typing import Any

import torch
import torch.nn as nn
import torch.nn.functional as F


class EpisodicMemory:
    """Circular buffer storing experience tuples.

    Each entry: {embedding, action, energy_delta, prediction_error, timestamp}.
    Retrieval via cosine similarity against stored embeddings.
    """

    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self._buffer: list[dict[str, Any]] = []
        self._write_idx: int = 0
        self._trace: list[dict[str, Any]] = []

    @property
    def size(self) -> int:
        return len(self._buffer)

    def write(
        self,
        embedding: torch.Tensor,
        action: int,
        energy_delta: float,
        prediction_error: float,
        timestamp: int,
    ) -> dict[str, Any]:
        """Store an experience tuple. Returns trace info."""
        entry = {
            "embedding": embedding.detach().clone(),
            "action": action,
            "energy_delta": energy_delta,
            "prediction_error": prediction_error,
            "timestamp": timestamp,
        }

        if len(self._buffer) < self.capacity:
            self._buffer.append(entry)
        else:
            self._buffer[self._write_idx] = entry
        self._write_idx = (self._write_idx + 1) % self.capacity

        trace = {
            "op": "episodic_write",
            "memory_size": self.size,
            "embedding_norm": embedding.norm().item(),
            "timestamp": timestamp,
        }
        self._trace.append(trace)
        return trace

    def read(
        self,
        query_embedding: torch.Tensor,
        k: int = 5,
    ) -> tuple[torch.Tensor, torch.Tensor, dict[str, Any]]:
        """Retrieve top-k most similar entries by cosine similarity.

        Args:
            query_embedding: (dim,) query vector.
            k: number of entries to retrieve.

        Returns:
            (retrieved_embeddings, weights, trace_info)
            retrieved_embeddings: (k, dim) tensor (zero-padded if fewer entries).
            weights: (k,) attention weights.
        """
        dim = query_embedding.shape[-1]

        if self.size == 0:
            empty = torch.zeros(k, dim, device=query_embedding.device, dtype=query_embedding.dtype)
            weights = torch.zeros(k, device=query_embedding.device, dtype=query_embedding.dtype)
            trace = {
                "op": "episodic_read",
                "memory_size": 0,
                "k": k,
                "query_norm": query_embedding.norm().item(),
                "result_norm": 0.0,
            }
            self._trace.append(trace)
            return empty, weights, trace

        # Stack stored embeddings
        stored = torch.stack([e["embedding"] for e in self._buffer])  # (N, dim)

        # Cosine similarity
        query_norm = F.normalize(query_embedding.unsqueeze(0), dim=-1)  # (1, dim)
        stored_norm = F.normalize(stored, dim=-1)  # (N, dim)
        similarities = (query_norm @ stored_norm.T).squeeze(0)  # (N,)

        # Top-k
        actual_k = min(k, self.size)
        top_vals, top_idx = similarities.topk(actual_k)

        retrieved = stored[top_idx]  # (actual_k, dim)
        weights = F.softmax(top_vals, dim=0)  # (actual_k,)

        # Pad if needed
        if actual_k < k:
            pad_emb = torch.zeros(k - actual_k, dim, device=query_embedding.device, dtype=query_embedding.dtype)
            retrieved = torch.cat([retrieved, pad_emb], dim=0)
            pad_w = torch.zeros(k - actual_k, device=query_embedding.device, dtype=query_embedding.dtype)
            weights = torch.cat([weights, pad_w], dim=0)

        trace = {
            "op": "episodic_read",
            "memory_size": self.size,
            "k": k,
            "actual_k": actual_k,
            "query_norm": query_embedding.norm().item(),
            "result_norm": retrieved.norm().item(),
            "top_similarity": top_vals[0].item() if actual_k > 0 else 0.0,
        }
        self._trace.append(trace)
        return retrieved, weights, trace

    def get_trace(self) -> list[dict[str, Any]]:
        """Return and clear accumulated trace events."""
        events = list(self._trace)
        self._trace.clear()
        return events

    def reset(self) -> None:
        self._buffer.clear()
        self._write_idx = 0
        self._trace.clear()


class LongTermMemory(nn.Module):
    """Learnable memory matrix with attention read and gated write.

    M: (memory_slots, memory_dim) — persistent storage.
    Read: attention-weighted sum over slots.
    Write: gated update M = M * (1 - w_gate) + outer(write_weights, value) * w_gate.
    """

    def __init__(self, memory_slots: int = 64, memory_dim: int = 128, input_dim: int | None = None):
        super().__init__()
        self.memory_slots = memory_slots
        self.memory_dim = memory_dim
        self.input_dim = input_dim or memory_dim

        self.M = nn.Parameter(torch.randn(memory_slots, memory_dim) * 0.1)

        # Learnable projections for read/write
        self.query_proj = nn.Linear(self.input_dim, memory_dim)
        self.key_proj = nn.Linear(memory_dim, memory_dim)
        self.write_key_proj = nn.Linear(self.input_dim, memory_dim)
        self.value_proj = nn.Linear(self.input_dim, memory_dim)
        self.write_gate = nn.Linear(self.input_dim, 1)

        self._trace: list[dict[str, Any]] = []

    def read(self, query: torch.Tensor) -> tuple[torch.Tensor, dict[str, Any]]:
        """Attention-weighted read from memory.

        Args:
            query: (memory_dim,) or (batch, memory_dim).

        Returns:
            (context, trace_info) — context is same shape as query.
        """
        squeeze = query.dim() == 1
        if squeeze:
            query = query.unsqueeze(0)

        q = self.query_proj(query)  # (batch, dim)
        k = self.key_proj(self.M)   # (slots, dim)

        # Attention scores
        scores = q @ k.T / (self.memory_dim ** 0.5)  # (batch, slots)
        attn = F.softmax(scores, dim=-1)  # (batch, slots)

        context = attn @ self.M  # (batch, dim)

        if squeeze:
            context = context.squeeze(0)

        trace = {
            "op": "longterm_read",
            "query_norm": query.norm().item(),
            "context_norm": context.norm().item(),
            "max_attention": attn.max().item(),
            "memory_slots": self.memory_slots,
        }
        self._trace.append(trace)
        return context, trace

    def write(self, key: torch.Tensor, value: torch.Tensor) -> dict[str, Any]:
        """Gated write to memory.

        M = M * (1 - w_gate) + outer(write_weights, value) * w_gate

        Args:
            key: (memory_dim,) — determines which slots to write to.
            value: (memory_dim,) — what to write.

        Returns:
            trace_info dict.
        """
        if key.dim() > 1:
            key = key.squeeze(0)
        if value.dim() > 1:
            value = value.squeeze(0)

        # This state is updated outside the optimizer. Keep a corrupted or
        # runaway write from poisoning every later read and policy decision.
        with torch.no_grad():
            self.M.data.nan_to_num_(nan=0.0, posinf=10.0, neginf=-10.0)

        k = self.write_key_proj(key)  # (dim,)
        v = self.value_proj(value)  # (dim,)

        # Write weights: similarity of key to each slot
        mk = self.key_proj(self.M)  # (slots, dim)
        scores = mk @ k / (self.memory_dim ** 0.5)  # (slots,)
        write_weights = F.softmax(scores, dim=0)  # (slots,)

        # Gate
        w_gate = torch.sigmoid(self.write_gate(key))  # (1,)

        # Update: M = M * (1 - w_gate) + outer(write_weights, value) * w_gate
        update = torch.outer(write_weights, v)  # (slots, dim)
        write_accepted = False
        with torch.no_grad():
            proposed = self.M * (1.0 - w_gate) + update * w_gate
            if torch.isfinite(proposed).all():
                self.M.data.copy_(proposed.clamp(-10.0, 10.0))
                write_accepted = True

        trace = {
            "op": "longterm_write",
            "key_norm": key.norm().item(),
            "value_norm": value.norm().item(),
            "gate_value": w_gate.item(),
            "max_write_weight": write_weights.max().item(),
            "write_accepted": write_accepted,
        }
        self._trace.append(trace)
        return trace

    def get_trace(self) -> list[dict[str, Any]]:
        """Return and clear accumulated trace events."""
        events = list(self._trace)
        self._trace.clear()
        return events

    def reset_memory(self) -> None:
        """Re-initialize memory matrix."""
        with torch.no_grad():
            self.M.data = torch.randn_like(self.M) * 0.1
        self._trace.clear()
