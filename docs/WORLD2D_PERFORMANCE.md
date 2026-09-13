# World2D performance

Targets are 30 FPS at 10k entities, command-to-visible p50 under 75 ms and p95 under 200 ms, and indexed seek at 100k under 250 ms. Measurements must report decode/apply/render/presentation, queue depth, memory, visual drops, and long tasks.

The trace index makes seek O(log n) plus one bounded file read. The stream and UI rings are bounded. rAF can coalesce paints but not logical transitions/events.

Executed 1k synthetic trace result on this machine: 256.6 durable appends/s (fsync per record), median indexed seek 0.236 ms, maximum sampled seek 0.306 ms, 354,670 bytes, hash-chain valid. The complete 100/1k/10k/50k three-view and 10k/100k/1M trace matrix has not been executed in this delivery. Performance acceptance is therefore PARTIAL, not a fabricated PASS.
