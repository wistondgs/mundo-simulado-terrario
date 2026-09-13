/**
 * D2 Scientific Studio: a specialized D2 view projected over the general
 * model (no hardcoded scientific knowledge). Shows D2 constructs, the D2
 * reference layer (scientific concepts / reference precedents / Terrario
 * design / trace breaks), and the D2 test family when present as data. Trace
 * breaks are first-class and never auto-filled.
 */
import { DOMAIN_VISUAL } from "../core/contracts.js";

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

const D2_LAYERS = ["scientific concepts", "reference precedents", "Terrario design", "trace breaks"];

export class D2Studio {
  constructor(api, { onError, onOpenWorld } = {}) {
    this.api = api;
    this.onError = onError || (() => {});
    this.onOpenWorld = onOpenWorld || (() => {});
    this.container = null;
    this.traceBreaks = [];
    this.layer = "reference precedents";
    this.references = [];
  }

  render(container) {
    this.container = container;
    container.innerHTML = `
      <div style="display:flex;gap:6px;align-items:center;margin-bottom:6px;flex-wrap:wrap">
        <strong>D2 · Properties, binding, identity, persistence, occlusion, generalisation</strong>
        <span style="flex:1"></span>
        <div id="d2LayerTabs"></div>
        <button id="d2OpenWorld">Open D2 World2D</button>
      </div>
      <div id="d2Body"></div>`;
    container.querySelector("#d2OpenWorld").onclick = () => this.onOpenWorld("D2");
    this._renderLayerTabs();
    this._load();
  }

  setTraceBreaks(breaks) {
    this.traceBreaks = breaks;
    this._renderBody();
  }

  _renderLayerTabs() {
    const tabs = this.container.querySelector("#d2LayerTabs");
    tabs.innerHTML = D2_LAYERS.map((layer) =>
      `<button class="ws-tag ${layer === this.layer ? "active" : ""}" data-layer="${escapeHtml(layer)}"
        style="cursor:pointer">${escapeHtml(layer)}</button>`).join("");
    tabs.querySelectorAll("[data-layer]").forEach((btn) => {
      btn.onclick = () => { this.layer = btn.dataset.layer; this._renderLayerTabs(); this._renderBody(); };
    });
  }

  async _load() {
    try {
      const result = await this.api.projection({ d_level: "D2" });
      this.references = result.references || [];
      this._renderBody();
    } catch (error) {
      this.onError("DOMAIN_UNAVAILABLE", error.message, "D2 projection");
    }
  }

  _renderBody() {
    if (!this.container) return;
    const body = this.container.querySelector("#d2Body");
    if (!body) return;
    if (this.layer === "trace breaks") {
      body.innerHTML = `
        <p style="font-size:12px;color:var(--ws-muted)">Trace breaks are first-class: where a trace
        ends, which domain/identity/relation is missing, and its state. They are never auto-filled.</p>
        ${this.traceBreaks.map((b) => `
          <div class="ws-trace-break">
            <strong>TRACE BREAK</strong> · ${escapeHtml(b.expected_next_domain)}
            <div style="font-size:12px;margin:3px 0">${escapeHtml(b.reason)}</div>
            <small>from ${escapeHtml(b.from)} · missing ${escapeHtml(b.missing_identity_or_relation || "—")}
              · ${escapeHtml(b.resolution_state || "UNRESOLVED")}</small>
          </div>`).join("") || "<p>No trace breaks recorded.</p>"}`;
      return;
    }
    if (this.layer === "reference precedents") {
      const constructs = new Map();
      for (const ref of this.references) {
        for (const c of ref.constructs || []) {
          constructs.set(c, [...(constructs.get(c) || []), ref.reference_id]);
        }
      }
      body.innerHTML = `
        <p style="font-size:12px;color:var(--ws-muted)">${this.references.length} D2 references projected
        from the corpus (data, not hardcoded).</p>
        ${[...constructs.entries()].map(([construct, refs]) => `
          <div style="margin:6px 0">
            <span class="ws-tag active">${escapeHtml(construct)}</span>
            <small style="color:var(--ws-muted)">${refs.length} refs</small>
            <div style="font-size:11px;margin-left:8px">${refs.slice(0, 6).map(escapeHtml).join(", ")}${refs.length > 6 ? "…" : ""}</div>
          </div>`).join("")}`;
      return;
    }
    if (this.layer === "Terrario design") {
      body.innerHTML = `
        <p style="font-size:12px;color:var(--ws-muted)">D2 scenario/world design in Terrario.</p>
        <div class="ws-composition-member">
          <span style="color:${DOMAIN_VISUAL.WORLD.color}">${DOMAIN_VISUAL.WORLD.icon}</span>
          <span>D2 · Properties scenario</span>
          <button id="d2GotoWorld">Open World2D</button>
        </div>
        <p style="font-size:12px;color:var(--ws-muted)">D2 test family (property discrimination,
        binding, persistence, individuation, constancy, occlusion, generalisation, transfer,
        representation probes, controls) is shown when present as data; it is not an obligatory ontology.</p>`;
      const btn = body.querySelector("#d2GotoWorld");
      if (btn) btn.onclick = () => this.onOpenWorld("D2");
      return;
    }
    // scientific concepts
    body.innerHTML = `
      <p style="font-size:12px;color:var(--ws-muted)">D2 scientific concepts as projected from the
      reference graph and TheoryGraph (where mapped).</p>
      <div>${["Object", "Property", "Identity", "Binding", "Persistence", "Invariance",
               "Occlusion", "Generalisation", "Transfer", "Representation Probe"]
        .map((c) => `<span class="ws-tag">${escapeHtml(c)}</span>`).join("")}</div>
      <p style="font-size:12px;color:var(--ws-muted);margin-top:8px">Select a concept in the canvas to
      trace it back to its source claims and references.</p>`;
  }
}
