/**
 * World2D panel: synchronized World Truth / Agent View / Observer View, a
 * timeline with scrub/step, and engineering-sandbox control. Uses the real
 * backend (WorldDefinition, WorldInstance, seed, Preview); it never implements
 * a second simulator in the frontend. World Truth is never shown as if it were
 * the agent's observation; the sandbox is always labelled ENGINEERING_SANDBOX /
 * NOT EVIDENCE, and there is no scientific-execution button.
 */
import { transientState } from "../core/state.js";

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

export class World2DPanel {
  constructor(api, { onError } = {}) {
    this.api = api;
    this.onError = onError || (() => {});
    this.container = null;
    this.worldId = "D2";
    this.seed = 42;
    this.step = 0;
    this.maxSteps = 100;
    this.playing = false;
    this._timer = null;
    this.preview = null;
  }

  render(container) {
    this.container = container;
    container.innerHTML = `
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;flex-wrap:wrap">
        <label>World <select id="w2dWorld"><option>D2</option><option>D3</option><option>D4</option></select></label>
        <label>Seed <input id="w2dSeed" type="number" value="42" style="width:70px"></label>
        <button id="w2dLoad">Load preview</button>
        <span class="ws-sandbox-badge">ENGINEERING_SANDBOX · NOT EVIDENCE</span>
        <span style="flex:1"></span>
        <div class="ws-sandbox-controls">
          <button id="w2dPrev" title="Step back">‹</button>
          <button id="w2dPlay" title="Play/Pause">▶</button>
          <button id="w2dNext" title="Step forward">›</button>
          <input id="w2dScrub" type="range" min="0" max="100" value="0" style="width:160px" aria-label="Timeline scrub">
          <span id="w2dStepLabel">step 0</span>
        </div>
      </div>
      <div class="ws-world-views">
        <div class="ws-world-view truth"><header>World Truth · privileged</header><canvas id="w2dTruth"></canvas></div>
        <div class="ws-world-view agent"><header>Agent View</header><canvas id="w2dAgent"></canvas></div>
        <div class="ws-world-view observer"><header>Observer View · private truth</header><canvas id="w2dObserver"></canvas></div>
      </div>
      <div id="w2dMeta" style="font-size:11px;color:var(--ws-muted);margin-top:4px"></div>`;
    container.querySelector("#w2dLoad").onclick = () => this.openWorld(
      container.querySelector("#w2dWorld").value, Number(container.querySelector("#w2dSeed").value));
    container.querySelector("#w2dPrev").onclick = () => this.stepTo(this.step - 1);
    container.querySelector("#w2dNext").onclick = () => this.stepTo(this.step + 1);
    container.querySelector("#w2dPlay").onclick = () => this.togglePlay();
    container.querySelector("#w2dScrub").oninput = (e) => this.stepTo(Number(e.target.value));
  }

  async openWorld(worldId, seed = 42) {
    this.worldId = worldId;
    this.seed = seed;
    try {
      const preview = await this.api.worldPreview(worldId, seed);
      this.preview = preview;
      this.maxSteps = Math.max(1, (preview.steps || 1) - 1);
      this.container.querySelector("#w2dScrub").max = this.maxSteps;
      this.step = 0;
      this._renderAll();
      this._meta(`Loaded ${worldId} · seed ${seed} · preview (RECORDED)`);
    } catch (error) {
      this.onError("DOMAIN_UNAVAILABLE", error.message, `world ${worldId}`);
    }
  }

  stepTo(step) {
    this.step = Math.max(0, Math.min(this.maxSteps, step));
    this.container.querySelector("#w2dScrub").value = this.step;
    this.container.querySelector("#w2dStepLabel").textContent = `step ${this.step}`;
    this._renderAll();
  }

  togglePlay() {
    this.playing = !this.playing;
    this.container.querySelector("#w2dPlay").textContent = this.playing ? "Ⅱ" : "▶";
    if (this.playing) {
      this._timer = setInterval(() => {
        if (this.step >= this.maxSteps) { this.togglePlay(); return; }
        this.stepTo(this.step + 1);
      }, 200);
    } else {
      clearInterval(this._timer);
    }
  }

  _renderAll() {
    // The three views are always distinctly labelled; World Truth is privileged
    // ground truth, never the agent's observation.
    this._renderView("w2dTruth", this._truthState(), "truth");
    this._renderView("w2dAgent", this._agentState(), "agent");
    this._renderView("w2dObserver", this._observerState(), "observer");
  }

  _truthState() {
    return this.preview && this.preview.truth ? this.preview.truth : this.preview;
  }

  _agentState() {
    return this.preview && this.preview.agent_view ? this.preview.agent_view : this.preview;
  }

  _observerState() {
    return this.preview && this.preview.observer_view ? this.preview.observer_view : this.preview;
  }

  _renderView(canvasId, view, kind) {
    const canvas = this.container.querySelector(`#${canvasId}`);
    if (!canvas) return;
    const scale = devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * scale;
    canvas.height = Math.max(120, rect.height) * scale;
    const ctx = canvas.getContext("2d");
    ctx.setTransform(scale, 0, 0, scale, 0, 0);
    ctx.fillStyle = kind === "truth" ? "#0f1a14" : "#101714";
    ctx.fillRect(0, 0, rect.width, rect.height);
    if (!view) {
      ctx.fillStyle = "#5a5f6a";
      ctx.font = "11px sans-serif";
      ctx.fillText("No data", 8, 16);
      return;
    }
    const gw = view.grid_width || view.width || 10;
    const gh = view.grid_height || view.height || 10;
    const cell = Math.min(rect.width / gw, rect.height / gh);
    // grid
    ctx.strokeStyle = "rgba(60,70,64,0.6)";
    for (let i = 0; i <= gw; i++) { ctx.beginPath(); ctx.moveTo(i * cell, 0); ctx.lineTo(i * cell, gh * cell); ctx.stroke(); }
    for (let i = 0; i <= gh; i++) { ctx.beginPath(); ctx.moveTo(0, i * cell); ctx.lineTo(gw * cell, i * cell); ctx.stroke(); }
    // objects
    for (const obj of Object.values(view.objects || {})) {
      const [r, c] = obj.pos || [0, 0];
      ctx.fillStyle = obj.properties && obj.properties.causal_class === "A" ? "#d9a441" : "#3f91a1";
      ctx.fillRect(c * cell + 1, r * cell + 1, cell - 2, cell - 2);
    }
    // agents
    for (const agent of Object.values(view.agents || {})) {
      const [r, c] = agent.pos || [0, 0];
      ctx.fillStyle = "#55b993";
      ctx.beginPath();
      ctx.arc(c * cell + cell / 2, r * cell + cell / 2, cell * 0.35, 0, Math.PI * 2);
      ctx.fill();
    }
    // agent observation mask (agent view only)
    if (kind === "agent" && view.mask) {
      ctx.fillStyle = "rgba(0,0,0,0.55)";
      view.mask.forEach((row, r) => row.forEach((visible, c) => {
        if (!visible) ctx.fillRect(c * cell, r * cell, cell, cell);
      }));
    }
  }

  _meta(message) {
    const el = this.container.querySelector("#w2dMeta");
    if (el) el.textContent = message;
  }
}
