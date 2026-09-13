/**
 * Explorer panel: browse Corpus / References / Claims / Theory / Hypergraph /
 * Hypotheses / Worlds / Experiments. Typed results; homonymous entities are
 * always labelled with their domain.
 */
import { DOMAIN_VISUAL } from "../core/contracts.js";

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

export class ExplorerPanel {
  constructor(api, { onOpen } = {}) {
    this.api = api;
    this.onOpen = onOpen || (() => {});
    this.references = [];
    this.container = null;
  }

  render(container) {
    this.container = container;
    container.innerHTML = `
      <input type="search" id="explorerSearch" placeholder="Search references, concepts, worlds…"
             aria-label="Search explorer" style="width:100%;margin-bottom:6px;padding:4px 6px">
      <div id="explorerTree"></div>`;
    container.querySelector("#explorerSearch").oninput = (e) => this._filter(e.target.value);
    this._renderTree();
  }

  setReferences(references) {
    this.references = references;
    this._renderTree();
  }

  _filter(query) {
    const q = query.trim().toLowerCase();
    this._renderTree(q);
  }

  _renderTree(query = "") {
    const tree = this.container.querySelector("#explorerTree");
    if (!tree) return;
    const matches = (text) => !query || String(text).toLowerCase().includes(query);
    const refs = this.references.filter((r) =>
      matches(r.reference_id) || matches(r.reference_type) ||
      (r.constructs || []).some(matches));

    const groups = [
      { key: "references", title: `References (${refs.length})`, items: refs.map((r) => ({
        kind: "reference", id: r.reference_id, domain: "REFERENCE",
        label: r.reference_id, sub: r.reference_type })) },
      { key: "worlds", title: "Worlds / Scenarios", items: ["D0", "D1", "D2", "D3", "D4"].map((id) => ({
        kind: "world", id, domain: "WORLD", label: id, sub: "scenario" })) },
    ];

    tree.innerHTML = groups.map((group) => `
      <div class="ws-tree-group">${escapeHtml(group.title)}</div>
      ${group.items.map((item) => {
        const visual = DOMAIN_VISUAL[item.domain] || DOMAIN_VISUAL.ONTOLOGY;
        return `<div class="ws-tree-item" data-kind="${escapeHtml(item.kind)}" data-id="${escapeHtml(item.id)}" tabindex="0" role="button">
          <span class="domain-icon" style="color:${visual.color}">${visual.icon}</span>
          <span class="item-label">${escapeHtml(item.label)}</span>
          <small style="color:var(--ws-muted)">${escapeHtml(item.sub || "")}</small>
        </div>`;
      }).join("")}`).join("");

    tree.querySelectorAll(".ws-tree-item").forEach((el) => {
      const open = () => this.onOpen({ kind: el.dataset.kind, id: el.dataset.id });
      el.onclick = open;
      el.onkeydown = (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(); } };
    });
  }
}
