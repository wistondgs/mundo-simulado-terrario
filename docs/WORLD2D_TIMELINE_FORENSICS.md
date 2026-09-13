# Timeline and forensics

The event timeline virtualizes visible rows and retains authoritative action/runtime events independent of render cadence. Scrub and keyboard navigation select recorded frames without rewinding the live runtime. Browser memory holds only a bounded presentation history; any older tick is fetched through the indexed trace endpoint, so a long live session cannot grow an unbounded frame map.

Frame comparisons can select arbitrary recorded ticks and report added, removed, moved, and property changes. They are always marked `DERIVED STATE DIFF · NOT CAUSAL`. Local bookmarks contain only trace/tick/entity/view metadata and are explicitly not `EvidenceRecord`s. World-object selection follows stable `object_id`, with an in-memory history derived solely from World Truth frames; Agent View offers no identity unless the explicitly labelled observer forensic sidecar provides a mapping.

D2 use is limited to visibility/provenance inspection. The UI does not infer concepts, cognitive binding, or scientific evidence. PNG export is watermarked `DIAGNOSTIC VIEW · NOT SCIENTIFIC EVIDENCE`.
