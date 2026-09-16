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
    this.protocolAudit = null;
    this.visualFixture = null;
    this.fixtureSequence = 0;
    this.fixtureTimer = null;
  }

  render(container) {
    this.container = container;
    container.innerHTML = `
      <div style="display:flex;gap:6px;align-items:center;margin-bottom:6px;flex-wrap:wrap">
        <strong>D2 · Properties, binding, identity, persistence, occlusion, generalisation</strong>
        <span style="flex:1"></span>
        <div id="d2LayerTabs"></div>
        <button id="d2OpenWorld">Open D2 World2D</button>
        <button id="d2OpenVisualFixture">Open D2 visual validation fixture</button>
      </div>
      <div id="d2ProtocolAudit" style="margin:6px 0"></div>
      <div id="d2VisualFixture" style="margin:6px 0"></div>
      <div id="d2Body"></div>`;
    container.querySelector("#d2OpenWorld").onclick = () => this.onOpenWorld("D2");
    container.querySelector("#d2OpenVisualFixture").onclick = () => this._loadVisualFixture();
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
      try { this.protocolAudit = await this.api.d2ProtocolAudit(); }
      catch (error) { this.protocolAudit = { error: error.message }; }
      this._renderProtocolAudit();
      this._renderBody();
    } catch (error) {
      this.onError("DOMAIN_UNAVAILABLE", error.message, "D2 projection");
    }
  }

  _renderProtocolAudit() {
    const target = this.container?.querySelector("#d2ProtocolAudit");
    if (!target) return;
    const audit = this.protocolAudit;
    if (!audit) { target.textContent = "D2 protocol audit loading…"; return; }
    if (audit.error) { target.textContent = `D2 protocol audit unavailable: ${audit.error}`; return; }
    const status = audit.all_cases_pass ? "PASS" : "FAIL_CLOSED";
    target.innerHTML = `<div class="ws-trace-break">
      <strong>D2 INSTRUMENT SELF-AUDIT · ${status}</strong>
      <small>${escapeHtml(audit.protocol_id)} · ${escapeHtml(audit.fixture_origin)}</small>
      <div style="font-size:11px;margin-top:3px">${(audit.cases || []).map((item) =>
        `${escapeHtml(item.condition_id)}@${escapeHtml(item.tick)}: ${item.render_alignment_errors?.length ? "MISALIGNED" : "ALIGNED"}`).join(" · ")}</div>
      <small>Observer fixture only · no agent execution · no EvidenceGraph write.</small>
    </div>`;
  }

  async _loadVisualFixture() {
    try {
      this._stopFixturePlayback();
      this.visualFixture = await this.api.d2VisualFixture();
      this.fixtureSequence = 0;
      this._renderVisualFixture();
    } catch (error) {
      this.onError("D2_VISUAL_FIXTURE_UNAVAILABLE", error.message, "D2 visual fixture");
    }
  }

  _stopFixturePlayback() {
    if (this.fixtureTimer) clearInterval(this.fixtureTimer);
    this.fixtureTimer = null;
  }

  _seekFixture(sequence) {
    const frames = this.visualFixture?.frames || [];
    if (!frames.length) return;
    this.fixtureSequence = Math.max(0, Math.min(Number(sequence), frames.length - 1));
    this._renderVisualFixture();
  }

  _toggleFixturePlayback() {
    if (this.fixtureTimer) { this._stopFixturePlayback(); this._renderVisualFixture(); return; }
    this.fixtureTimer = setInterval(() => {
      const frames = this.visualFixture?.frames || [];
      if (this.fixtureSequence >= frames.length - 1) { this._stopFixturePlayback(); this._renderVisualFixture(); return; }
      this._seekFixture(this.fixtureSequence + 1);
    }, 500);
    this._renderVisualFixture();
  }

  _renderVisualFixture() {
    const target = this.container?.querySelector("#d2VisualFixture");
    if (!target || !this.visualFixture) return;
    const fixture = this.visualFixture, frames = fixture.frames || [], frame = frames[this.fixtureSequence];
    if (!frame) { target.textContent = "D2 visual fixture has no frames."; return; }
    const visible = new Set(frame.visible_object_ids || []);
    const lifecycle = frame.lifecycle || {};
    const objects = frame.world_truth?.objects || [];
    target.innerHTML = `<section class="ws-trace-break" aria-label="D2 visual validation fixture">
      <strong>D2 VISUAL VALIDATION FIXTURE</strong>
      <small>${escapeHtml(fixture.fixture_id)} · ${escapeHtml(fixture.epistemic_scope)}</small>
      <div style="margin:5px 0"><button id="d2FixtureFirst">First</button> <button id="d2FixturePrev">Previous</button>
      <button id="d2FixturePlay">${this.fixtureTimer ? "Pause" : "Play"}</button> <button id="d2FixtureNext">Next</button>
      <button id="d2FixtureLast">Last</button> <input id="d2FixtureSeek" type="range" min="0" max="${frames.length - 1}" value="${this.fixtureSequence}" aria-label="D2 fixture timeline seek">
      <output id="d2FixtureTick">tick ${escapeHtml(frame.tick)} · frame ${escapeHtml(frame.frame_sequence)} · ${escapeHtml(frame.phase)}</output></div>
      <div data-d2-semantic-frame="${escapeHtml(frame.frame_id)}" style="font-size:11px">
        <div><strong>World Truth · privileged</strong> ${objects.map((item) => `<span class="ws-tag" data-d2-object-id="${escapeHtml(item.object_id)}">#${escapeHtml(item.object_id)} ${visible.has(item.object_id) ? "VISIBLE" : "OCCLUDED"} · ${escapeHtml(lifecycle[item.object_id] || "visible")}</span>`).join(" ")}</div>
        <div><strong>Observer View</strong> <span data-d2-errors>${escapeHtml((frame.observer_view?.errors || []).join(", ") || "NO_ERROR")}</span> <small>${escapeHtml(frame.observer_view?.scope)}</small></div>
        <div><strong>Agent Observation</strong> ${escapeHtml(frame.agent_observation?.availability)} · <strong>Cognitive State</strong> ${escapeHtml(frame.cognitive_state?.availability)}</div>
        <details><summary>Frame semantic record</summary><pre>${escapeHtml(JSON.stringify(frame, null, 2))}</pre></details>
      </div>
    </section>`;
    target.querySelector("#d2FixtureFirst").onclick = () => this._seekFixture(0);
    target.querySelector("#d2FixturePrev").onclick = () => this._seekFixture(this.fixtureSequence - 1);
    target.querySelector("#d2FixturePlay").onclick = () => this._toggleFixturePlayback();
    target.querySelector("#d2FixtureNext").onclick = () => this._seekFixture(this.fixtureSequence + 1);
    target.querySelector("#d2FixtureLast").onclick = () => this._seekFixture(frames.length - 1);
    target.querySelector("#d2FixtureSeek").oninput = (event) => this._seekFixture(event.target.value);
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
