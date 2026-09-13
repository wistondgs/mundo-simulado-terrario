# World2D renderer

The native interface is `initialize`, `resize`, `setCamera`, `renderFrame`, `pick`, `dispose`, and `metrics`. Canvas2D is the permanent fallback and renders exact agent channel zero plus mask rather than pretending the observation contains world objects. WebGL2 uses reusable GPU resources and point rendering for world entities.

Context loss or local renderer failure replaces only the affected renderer with Canvas2D. rAF presents the newest logical frame; authoritative events remain in the reducer/timeline. Canvas is currently primary: no reproducible three-view 10k benchmark has yet demonstrated the required ≥20% WebGL2 p95 win with visual/picking parity.
