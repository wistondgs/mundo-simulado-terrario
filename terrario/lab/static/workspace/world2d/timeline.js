/** Virtualized event timeline; events stay authoritative even when paints drop. */
export class VirtualTimeline {
  constructor(container, { onSeek } = {}) {
    this.container = container; this.onSeek = onSeek || (() => {}); this.events = []; this.rowHeight = 24;
    container.classList.add("w2d-timeline"); container.tabIndex = 0; container.setAttribute("role", "listbox");
    container.setAttribute("aria-label", "Observer event timeline"); container.addEventListener("scroll", () => this.render());
    container.addEventListener("keydown", (event) => { if (event.key === "ArrowRight") this.onSeek(1); if (event.key === "ArrowLeft") this.onSeek(-1); });
  }
  setEvents(events) { this.events = events; this.render(); }
  render() {
    const height = this.container.clientHeight || 120, start = Math.max(0, Math.floor(this.container.scrollTop / this.rowHeight) - 3);
    const end = Math.min(this.events.length, start + Math.ceil(height / this.rowHeight) + 6);
    this.container.replaceChildren();
    const space = document.createElement("div"); space.style.height = `${this.events.length * this.rowHeight}px`; space.style.position = "relative";
    this.events.slice(start, end).forEach((event, index) => {
      const row = document.createElement("button"); row.type = "button"; row.className = "w2d-event"; row.setAttribute("role", "option");
      row.style.top = `${(start + index) * this.rowHeight}px`;
      row.textContent = `t${event.transition?.to_tick ?? event.tick ?? "?"} · ${event.event_type || "EVENT"} · ${event.source || "runtime"}`;
      row.onclick = () => this.onSeek(Number(event.transition?.to_tick ?? event.tick ?? 0)); space.append(row);
    });
    this.container.append(space);
  }
}

export function diffFrames(left, right) {
  const world = (frame) => frame?.views?.find((view) => view.kind === "WORLD_TRUTH_PRIVILEGED")?.payload || {};
  const a = world(left), b = world(right), ao = a.objects || {}, bo = b.objects || {};
  const idsA = new Set(Object.keys(ao)), idsB = new Set(Object.keys(bo));
  return {
    added: [...idsB].filter((id) => !idsA.has(id)), removed: [...idsA].filter((id) => !idsB.has(id)),
    moved: [...idsA].filter((id) => idsB.has(id) && JSON.stringify(ao[id].pos) !== JSON.stringify(bo[id].pos)),
    properties: [...idsA].filter((id) => idsB.has(id) && JSON.stringify(ao[id].properties) !== JSON.stringify(bo[id].properties)),
    explanation: "DERIVED STATE DIFF · NOT CAUSAL",
  };
}
