# WORLD2D deep architecture

`LiveSandboxService` is the sole live-runtime authority and extends the existing bounded `SandboxService`; no second simulator exists. `LabAPI` exposes it through `WorldStreamAPI`, while the old `/api/sandbox` surface remains an adapter over the same object.

The frontend remains framework-free ES modules: `protocol.js` owns transport/reduction, `renderers.js` owns presentation, `timeline.js` owns indexed UI projection, and `views/world2d.js` orchestrates modes. `LIVE SANDBOX`, `TRACE PLAYBACK`, and `PREVIEW` are distinct capabilities; playback controls cannot issue commands.

Authority flows `runtime → append-only trace → stream ring → client reducer → latest logical frame → rAF paint`. Dropping a paint is permitted; dropping a transition or event is not.
