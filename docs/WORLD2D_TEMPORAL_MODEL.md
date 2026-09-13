# World2D temporal model

Tick 0 is the initial world snapshot. A transition consumes the exact pending `observation_t`, runs scheduler/action/physics/rules/learning, obtains `observation_t1`, and publishes a frame at `t+1`. Network time never substitutes for logical tick or world simulation time.

Every `WorldFrame` validates exactly three views at one tick: privileged truth, exact agent observation, and configured Observer capture. Agent payload is limited to channels, mask, energy, and time fraction. Explicit cell/object provenance is Observer-only; Agent View states `NO DIRECT IDENTITY MAPPING`.

Lifecycle is `CREATED → READY → RUNNING ↔ PAUSED → STOPPING → TERMINATED`, with `COMPLETED` and `FAILED` terminal outcomes. Legacy `VALIDATED/INVALIDATED` remain internal compatibility states.
