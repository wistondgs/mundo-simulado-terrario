/**
 * Command palette + federated search. Frequent operations (open reference,
 * find concept, add to composition, show provenance, expand neighborhood, pin
 * snapshot, open World2D) plus federated typed search across references, DOI,
 * authors, claims, concepts, theory nodes, hyperedges, scenarios, worlds, and
 * experiments. Keyboard-first.
 */
import { transientState } from "../core/state.js";

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

const COMMANDS = [
  { id: "open-reference", label: "Open reference", kind: "command", needsArg: true, hint: "reference id" },
  { id: "find-concept", label: "Find concept", kind: "command", needsArg: true, hint: "construct" },
  { id: "add-to-composition", label: "Add selection to composition", kind: "command" },
  { id: "show-provenance", label: "Show provenance", kind: "command" },
  { id: "expand-neighborhood", label: "Expand neighborhood", kind: "command" },
  { id: "pin-snapshot", label: "Pin snapshot / toggle mode", kind: "command" },
  { id: "open-world", label: "Open World2D", kind: "command", needsArg: true, hint: "world id (D2)" },
];

export class CommandPalette {
  constructor(api, { onAction } = {}) {
    this.api = api;
    this.onAction = onAction || (() => {});
    this.element = null;
    this.open = false;
    this.activeIndex = 0;
    this.results = [];
  }

  toggle() {
    this.open ? this.close() : this.show();
  }

  show() {
    if (this.open) return this.close();
    this.open = true;
    transientState.set({ paletteOpen: true });
    this.element = document.createElement("div");
    this.element.className = "ws-palette";
    this.element.setAttribute("role", "dialog");
    this.element.setAttribute("aria-label", "Command palette");
    this.element.innerHTML = `
      <input type="text" placeholder="Type a command or search…" aria-label="Command palette input">
      <div class="ws-palette-results" role="listbox"></div>`;
    document.body.append(this.element);
    const input = this.element.querySelector("input");
    input.focus();
    input.oninput = () => this._update(input.value);
    input.onkeydown = (e) => this._keydown(e, input.value);
    this._update("");
    document.addEventListener("pointerdown", this._outside = (e) => {
      if (this.element && !this.element.contains(e.target)) this.close();
    });
  }

  close() {
    if (!this.open) return;
    this.open = false;
    transientState.set({ paletteOpen: false });
    if (this.element) this.element.remove();
    this.element = null;
    document.removeEventListener("pointerdown", this._outside);
  }

  async _update(query) {
    const q = query.trim();
    const commandMatches = COMMANDS.filter((c) =>
      c.label.toLowerCase().includes(q.toLowerCase()));
    let searchResults = [];
    if (q.length >= 2) {
      try {
        const refs = await this.api.findReferences({ title: q });
        searchResults = (refs.items || []).slice(0, 6).map((r) => ({
          id: "open-reference", label: r.reference_id, kind: "reference", arg: r.reference_id,
        }));
      } catch { /* degrade */ }
    }
    this.results = [
      ...commandMatches.map((c) => ({ ...c, arg: c.needsArg ? q : undefined })),
      ...searchResults,
    ];
    this.activeIndex = 0;
    this._render();
  }

  _render() {
    if (!this.element) return;
    const list = this.element.querySelector(".ws-palette-results");
    list.innerHTML = this.results.map((r, i) => `
      <div class="ws-palette-item ${i === this.activeIndex ? "active" : ""}" data-index="${i}" role="option" aria-selected="${i === this.activeIndex}">
        <span>${escapeHtml(r.label)}</span>
        <span class="cmd-kind">${escapeHtml(r.kind)}</span>
      </div>`).join("") || `<div class="ws-palette-item">No results</div>`;
    list.querySelectorAll(".ws-palette-item[data-index]").forEach((el) => {
      el.onclick = () => this._run(this.results[Number(el.dataset.index)]);
    });
  }

  _keydown(event, value) {
    if (event.key === "Escape") { this.close(); return; }
    if (event.key === "ArrowDown") { event.preventDefault(); this.activeIndex = Math.min(this.results.length - 1, this.activeIndex + 1); this._render(); return; }
    if (event.key === "ArrowUp") { event.preventDefault(); this.activeIndex = Math.max(0, this.activeIndex - 1); this._render(); return; }
    if (event.key === "Enter") {
      event.preventDefault();
      const command = this.results[this.activeIndex];
      if (command) this._run(command, value);
    }
  }

  _run(command, value) {
    this.close();
    const arg = command.needsArg ? (command.arg || value) : command.arg;
    switch (command.id) {
      case "open-reference": this.onAction({ kind: "open-reference", id: arg }); break;
      case "find-concept": this.onAction({ kind: "find-concept", query: arg }); break;
      case "add-to-composition": this.onAction({ kind: "add-to-composition" }); break;
      case "show-provenance": this.onAction({ kind: "show-provenance" }); break;
      case "expand-neighborhood": this.onAction({ kind: "expand-neighborhood" }); break;
      case "pin-snapshot": this.onAction({ kind: "pin-snapshot" }); break;
      case "open-world": this.onAction({ kind: "open-world", id: arg || "D2" }); break;
      default: break;
    }
  }
}
