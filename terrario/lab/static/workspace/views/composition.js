/**
 * Research Composition panel. The user builds a working composition of papers,
 * claims, concepts, theory nodes, hyperedges, hypotheses, scenarios, worlds,
 * and experiments. Composition-local links/hyperedges never modify the
 * canonical graphs; promoting a local relation to a canonical cross-link is a
 * separate reviewed act. Versioning, diff, undo/redo, and autosave are local.
 */
import { compositionState, journal } from "../core/state.js";
import { DOMAIN_VISUAL } from "../core/contracts.js";

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

export class CompositionPanel {
  constructor(api, { onError } = {}) {
    this.api = api;
    this.onError = onError || (() => {});
    this.container = null;
    this.members = [];
    this.localLinks = [];
    this.title = "Untitled composition";
    this.compositionId = null;
    this.version = 0;
  }

  render(container) {
    this.container = container;
    container.innerHTML = `
      <div style="display:flex;gap:6px;margin-bottom:6px">
        <input id="compTitle" value="${escapeHtml(this.title)}" style="flex:1;padding:4px 6px" aria-label="Composition title">
        <button id="compSave" title="Save new version">Save</button>
      </div>
      <div style="display:flex;gap:4px;margin-bottom:6px">
        <button id="compLink" title="Connect selected into a local link">Link</button>
        <button id="compHyper" title="Create local hyperedge from selected">Hyperedge</button>
        <button id="compDiff" title="Compare with previous version">Diff</button>
        <button id="compClear" title="Clear">Clear</button>
      </div>
      <div class="ws-section-title">Members</div>
      <div id="compMembers"></div>
      <div class="ws-section-title">Local links</div>
      <div id="compLinks"></div>
      <div id="compStatus" style="font-size:11px;color:var(--ws-muted);margin-top:6px"></div>`;
    container.querySelector("#compTitle").oninput = (e) => { this.title = e.target.value; this._dirty(); };
    container.querySelector("#compSave").onclick = () => this.save();
    container.querySelector("#compLink").onclick = () => this.createLocalLink();
    container.querySelector("#compHyper").onclick = () => this.createLocalHyperedge();
    container.querySelector("#compDiff").onclick = () => this.showDiff();
    container.querySelector("#compClear").onclick = () => this.clear();
    this._renderMembers();
  }

  addMembers(refs) {
    const added = [];
    for (const ref of refs) {
      const key = `${ref.domain}:${ref.entity_type}:${ref.entity_id}`;
      if (!this.members.some((m) => m.key === key)) {
        this.members.push({ key, ref });
        added.push(key);
      }
    }
    if (added.length) {
      const previous = this.members.filter((m) => !added.includes(m.key)).map((m) => m.key);
      const now = this.members.map((m) => m.key);
      journal.push({ label: "add members", kind: "COMPOSITION",
        undo: () => { this.members = this.members.filter((m) => previous.includes(m.key)); this._renderMembers(); },
        redo: () => { this.members = now.map((k) => this.members.find((m) => m.key === k)).filter(Boolean); this._renderMembers(); } });
      this._dirty();
      this._renderMembers();
    }
  }

  createLocalLink() {
    if (this.members.length < 2) {
      this.onError("UNREVIEWED_CANDIDATE", "Select at least two members to link", "composition");
      return;
    }
    const [a, b] = this.members.slice(-2);
    this.localLinks.push({ kind: "local-link", from: a.key, to: b.key, id: `ll-${Date.now()}` });
    this._dirty();
    this._renderMembers();
  }

  createLocalHyperedge() {
    if (this.members.length < 2) {
      this.onError("UNREVIEWED_CANDIDATE", "Select at least two members for a hyperedge", "composition");
      return;
    }
    this.localLinks.push({ kind: "local-hyperedge", members: this.members.map((m) => m.key),
                           id: `lh-${Date.now()}` });
    this._dirty();
    this._renderMembers();
  }

  clear() {
    this.members = [];
    this.localLinks = [];
    this._dirty();
    this._renderMembers();
  }

  async save() {
    try {
      const payload = {
        title: this.title,
        refs: this.members.map((m) => m.ref),
        local_links: this.localLinks,
        notes: "",
        composition_id: this.compositionId || undefined,
      };
      const result = await this.api.saveComposition(payload);
      this.compositionId = result.composition_id;
      this.version = result.version;
      compositionState.set({ active: result, dirty: false });
      this._status(`Saved v${result.version} · ${result.composition_id.slice(0, 20)}…`);
    } catch (error) {
      this.onError("DOMAIN_UNAVAILABLE", error.message, "save composition");
    }
  }

  async showDiff() {
    if (!this.compositionId) {
      this._status("Save first to compare versions.");
      return;
    }
    try {
      const current = await this.api.getComposition(this.compositionId);
      const currentKeys = new Set((current.refs || []).map((r) => `${r.domain}:${r.entity_type}:${r.entity_id}`));
      const localKeys = new Set(this.members.map((m) => m.key));
      const added = [...localKeys].filter((k) => !currentKeys.has(k));
      const removed = [...currentKeys].filter((k) => !localKeys.has(k));
      this._status(`Diff vs saved v${current.version}: +${added.length} members, -${removed.length} members, links ${this.localLinks.length} local`);
    } catch (error) {
      this.onError("DOMAIN_UNAVAILABLE", error.message, "composition diff");
    }
  }

  _renderMembers() {
    if (!this.container) return;
    const membersEl = this.container.querySelector("#compMembers");
    const linksEl = this.container.querySelector("#compLinks");
    membersEl.innerHTML = this.members.map((m) => {
      const [domain] = m.key.split(":");
      const visual = DOMAIN_VISUAL[domain] || DOMAIN_VISUAL.ONTOLOGY;
      return `<div class="ws-composition-member">
        <span style="color:${visual.color}">${visual.icon}</span>
        <span style="font-size:12px">${escapeHtml(m.key)}</span>
        <button data-remove="${escapeHtml(m.key)}" title="Remove">×</button>
      </div>`;
    }).join("") || `<p style="color:var(--ws-muted);font-size:12px">Empty. Add from the canvas or explorer.</p>`;
    linksEl.innerHTML = this.localLinks.map((l) => {
      if (l.kind === "local-hyperedge") {
        return `<div class="ws-tag candidate">hyperedge · ${l.members.length} members</div>`;
      }
      return `<div class="ws-tag">${escapeHtml(l.from.split(":").pop())} → ${escapeHtml(l.to.split(":").pop())}</div>`;
    }).join("") || `<p style="color:var(--ws-muted);font-size:12px">No local links.</p>`;
    membersEl.querySelectorAll("[data-remove]").forEach((btn) => {
      btn.onclick = () => {
        this.members = this.members.filter((m) => m.key !== btn.dataset.remove);
        this._dirty();
        this._renderMembers();
      };
    });
  }

  _dirty() {
    compositionState.set({ dirty: true });
    this._status("Unsaved changes");
  }

  _status(message) {
    const el = this.container && this.container.querySelector("#compStatus");
    if (el) el.textContent = message;
  }
}
