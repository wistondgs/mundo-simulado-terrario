# Environment baseline

- Recorded: 2026-09-09
- Python: 3.12.3
- PyTorch: 2.5.1+cu121
- Torch CUDA runtime: 12.1
- `torch.cuda.is_available()`: false
- Installed driver: NVIDIA proprietary 595.84
- H-ADAPT requested device: CUDA
- H-ADAPT device pre-flight: BLOCKED
- Test baseline: 146 passed, 1 CUDA smoke test skipped, 1 CUDA-platform warning

Terrario now supports consistent CPU/CUDA tensor placement and records the
resolved device in agent identity. CUDA remains unavailable because the host
driver reports `Failed to copy vbios to system memory`; campaign pre-flight
therefore refuses GPU execution instead of falling back silently.
