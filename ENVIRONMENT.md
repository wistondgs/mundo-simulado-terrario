# Environment baseline

- Recorded: 2026-09-08
- Python: 3.12.3
- PyTorch: 2.5.1+cu121
- Torch CUDA runtime: 12.1
- `torch.cuda.is_available()`: false
- Execution device for SANITIZE-01: CPU
- Test baseline: 84 passed, 1 CUDA-platform warning

CUDA is unavailable on this host despite an installed CUDA-enabled PyTorch
wheel. This document records the condition only; it is not a driver repair
instruction.
