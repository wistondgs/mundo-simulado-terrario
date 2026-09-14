/** Read-only World2D scientific inspection; it cannot control any runtime.
 * Modes: SCIENTIFIC · LIVE / RESYNCING / TERMINAL / PLAYBACK. Never evidence controls. */
import { ScientificLiveClient, initialObservationState, reduceScientificEvent, transition }
  from "../world2d/scientific-protocol.js";
import { renderCognitiveState } from "../world2d/cognitive.js";

const text = (x) => String(x ?? "").replace(/[&<>"']/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));

export class ScientificWorld2DPanel {
  constructor(api, { onError } = {}) {
    this.api = api; this.onError = onError || (() => {});
    this.state = initialObservationState();
    this.client = new ScientificLiveClient(api, {
      onEvent: (event) => this._event(event),
      onStatus: (value) => this._connection(value),
      onError: (error) => this._streamError(error),
    });
    this.playbackFrames = new Map(); this.presentedSequence = -1; this.lastRenderedFrame = null;
    this.followingLive = true; this.inspectedFrame = null;
  }

  render(el) {
    this.el = el;
    el.innerHTML = `<section aria-label="Scientific World2D"><header><strong>WORLD2D · SCIENTIFIC EXECUTION</strong> <span id="swMode" class="ws-mode-badge pinned">SCIENTIFIC · IDLE</span> <span class="ws-mode-badge">READ-ONLY</span></header><p>Live observation and sealed-CAS playback of scientific attempts. This panel has no start, step, pause, resume, reset, seed, or intervention controls.</p><label>Execution <input id="swExec"></label><label>Trial <input id="swTrial"></label><label>Attempt <input id="swAttempt"></label><button id="swLive">Attach live</button><button id="swResync" disabled>Resync</button><button id="swInspect" disabled>Inspect frame</button><button id="swFollow" disabled>Follow live</button><button id="swOpen" disabled>Open playback</button><button id="swClose" disabled>Disconnect viewer</button><span id="swConn" aria-live="polite">STALE</span></section><div id="swStatus" aria-live="polite"></div><pre id="swProv">No scientific attempt attached.</pre><div id="swSeek" hidden><button id="swPrev">‹</button><input id="swScrub" type="range" min="0" max="0" value="0" aria-label="Playback seek"><button id="swNext">›</button><span id="swSeekLabel"></span></div><section class="w2d-cognitive-observatory" aria-label="Cognitive Observatory"><header>Cognitive state · exact frame <small>instrumented state; projections are not raw tensor evidence</small></header><div id="swCognitive"></div></section><div id="swViews"></div>`;
    el.querySelector("#swLive").onclick = () => this.attachLive();
    el.querySelector("#swResync").onclick = () => this.resync();
    el.querySelector("#swInspect").onclick = () => this.inspectFrame();
    el.querySelector("#swFollow").onclick = () => this.followLive();
    el.querySelector("#swOpen").onclick = () => this.openPlayback();
    el.querySelector("#swClose").onclick = () => this.disconnect();
    el.querySelector("#swPrev").onclick = () => this.seek(this.presentedSequence - 1);
    el.querySelector("#swNext").onclick = () => this.seek(this.presentedSequence + 1);
    el.querySelector("#swScrub").oninput = (event) => this.seek(Number(event.target.value));
  }

  _ids() { const q = (id) => this.el.querySelector(id).value.trim(); return { exec: q("#swExec"), trial: q("#swTrial"), attempt: q("#swAttempt") }; }
  _setMode() { this.el.querySelector("#swMode").textContent = `SCIENTIFIC · ${this.state.status}`; }
  _connection(value) { if (this.el) this.el.querySelector("#swConn").textContent = value; }
  _controls() {
    const status = this.state.status;
    this.el.querySelector("#swResync").disabled = !(status === "LIVE" || status === "RESYNCING" || status === "LOST");
    this.el.querySelector("#swOpen").disabled = status !== "TERMINAL";
    this.el.querySelector("#swInspect").disabled = !(status === "LIVE" && this.state.frame);
    this.el.querySelector("#swFollow").disabled = !(status === "LIVE" && !this.followingLive);
    this.el.querySelector("#swClose").disabled = !(status === "LIVE" || status === "RESYNCING" || status === "CONNECTING");
    this.el.querySelector("#swSeek").hidden = status !== "PLAYBACK";
  }
  _apply(next) { this.state = next; this._setMode(); this._controls(); }

  async attachLive() {
    const { exec, trial, attempt } = this._ids();
    if (!exec || !trial || !attempt) { this.onError("SCIENTIFIC_OBSERVATION_ERROR", "execution, trial and attempt are required", "scientific World2D"); return; }
    try {
      if (!this.api.csrfToken) await this.api.initSession();
      this.client.close(); this.followingLive = true; this.inspectedFrame = null; this.lastRenderedFrame = null;
      this._apply(transition(initialObservationState(), "CONNECTING"));
      const snapshot = await this.client.snapshot(exec, trial, attempt);
      this._apply(reduceScientificEvent(this.state, { type: "SNAPSHOT", ...snapshot }));
      this.client.after = this.state.frameSequence;
      this._renderFrame(this.state.frame);
      this._renderProvenance();
      if (this.state.status === "TERMINAL") { this._status("Attempt already terminal; durable CAS playback is available."); return; }
      void this.client.connect(exec, trial, attempt);
    } catch (error) { this._apply(reduceScientificEvent(this.state, { type: "ERROR", message: error.message })); this.onError("SCIENTIFIC_OBSERVATION_ERROR", error.message, "scientific World2D"); }
  }

  _event(event) {
    const before = this.state;
    this._apply(reduceScientificEvent(before, event));
    if (this.state.status === "RESYNCING" && before.status !== "RESYNCING") {
      this._status(`Gap detected (${this.state.gap?.reason || `expected ${this.state.gap?.expected}, received ${this.state.gap?.received}`}); resyncing from authoritative snapshot.`);
      void this.resync(); return;
    }
    if ((event.type === "FRAME" || event.type === "SNAPSHOT") && this.followingLive) { this._renderFrame(this.state.frame); this._renderProvenance(); }
    if (event.type === "TERMINAL") { this._status("Terminal event received; raw artifacts sealed. Durable CAS playback is available."); this._renderProvenance(); }
    if (event.type === "LOST") this._status("Connection lost; the viewer will reconnect with its cursor.");
  }

  async resync() {
    const { exec, trial, attempt } = this._ids();
    try {
      const snapshot = await this.client.snapshot(exec, trial, attempt);
      this._apply(reduceScientificEvent({ ...this.state, frameSequence: -1 }, { type: "SNAPSHOT", ...snapshot }));
      this.client.after = this.state.frameSequence;
      if (this.followingLive) this._renderFrame(this.state.frame); this._renderProvenance();
      this._status(this.state.status === "TERMINAL" ? "Resynced; attempt is terminal." : "Resynchronized from authoritative snapshot.");
    } catch (error) { this._apply(reduceScientificEvent(this.state, { type: "ERROR", message: error.message })); this.onError("SCIENTIFIC_OBSERVATION_ERROR", error.message, "scientific resync"); }
  }

  async openPlayback() {
    const { exec, trial, attempt } = this._ids();
    try {
      this.client.close();
      this.followingLive = false; this.inspectedFrame = null; this.lastRenderedFrame = null;
      const page = await this.client.playback(exec, trial, attempt);
      if (!page.frames?.length) throw new Error("TRACE_UNAVAILABLE");
      this.playbackFrames.clear();
      for (const frame of page.frames) this.playbackFrames.set(frame.frame_sequence, frame);
      this._apply(reduceScientificEvent(this.state, { type: "SNAPSHOT", frame: page.frames[0], terminal: true, artifact_state: "CAS_SEALED", earliest_retained_sequence: 0, latest_sequence: page.frames[page.frames.length - 1].frame_sequence }));
      this._apply(transition(this.state, "PLAYBACK"));
      const scrub = this.el.querySelector("#swScrub"); scrub.max = Math.max(...this.playbackFrames.keys()); scrub.value = 0;
      this.seek(0); this._renderProvenance();
      this._status(`Durable CAS playback · ${this.playbackFrames.size} frames · provenance identical to live.`);
    } catch (error) { this._apply(reduceScientificEvent(this.state, { type: "ERROR", message: error.message })); this.onError("SCIENTIFIC_OBSERVATION_ERROR", error.message, "scientific playback"); }
  }

  seek(sequence) {
    if (this.state.status !== "PLAYBACK" || !this.playbackFrames.has(sequence)) return;
    this.presentedSequence = sequence;
    this.el.querySelector("#swScrub").value = sequence;
    this.el.querySelector("#swSeekLabel").textContent = `frame ${sequence}`;
    this._renderFrame(this.playbackFrames.get(sequence));
  }

  inspectFrame() {
    if (this.state.status !== "LIVE" || !this.state.frame) return;
    this.followingLive = false; this.inspectedFrame = this.state.frame;
    this._apply(this.state); this._renderFrame(this.inspectedFrame);
    this._status(`VIEWING HISTORICAL FRAME ${this.inspectedFrame.frame_sequence}; the runtime continues.`);
  }

  followLive() {
    if (this.state.status !== "LIVE" || !this.state.frame) return;
    this.followingLive = true; this.inspectedFrame = null;
    this._apply(this.state); this._renderFrame(this.state.frame);
    this._status("FOLLOWING LIVE; the viewer does not control the runtime.");
  }

  disconnect() { this.client.close(); this.followingLive = true; this.inspectedFrame = null; this.lastRenderedFrame = null; this._apply(transition(this.state, "IDLE")); this._connection("STALE"); this._status("Viewer disconnected; the trial is unaffected."); }

  _streamError(error) { this._connection("STALE"); this.onError("WORLDSTREAM_ERROR", error.message, `SCIENTIFIC · ${this.state.status}`); }

  _renderProvenance() {
    const identity = this.state.identity || {};
    this.el.querySelector("#swProv").textContent = JSON.stringify({
      classification: "SCIENTIFIC_OBSERVATION", observation_state: this.state.status,
      execution_id: identity.execution_id, trial_intent_id: identity.trial_intent_id, attempt_id: identity.attempt_id,
      plan_hash: identity.plan_hash, preregistration_root_hash: identity.preregistration_root_hash,
      software_identity: identity.software_identity, scenario_identity: identity.scenario_identity,
      agent_identity: identity.agent_identity, world_seed: identity.world_seed, agent_seed: identity.agent_seed,
      contract_version: identity.schema_version, frame_sequence: this.state.frameSequence,
      artifact_state: this.state.artifactState, terminal: this.state.terminal,
    }, null, 2);
  }

  _renderFrame(frame) {
    if (!frame) return;
    const previous = this.playbackFrames.get(frame.frame_sequence - 1)
      || (this.lastRenderedFrame?.frame_sequence === frame.frame_sequence - 1 ? this.lastRenderedFrame : null);
    renderCognitiveState(this.el.querySelector("#swCognitive"), frame, previous);
    this.lastRenderedFrame = frame;
    this.el.querySelector("#swViews").innerHTML = `<h4>Tick ${text(frame.tick)} · frame ${text(frame.frame_sequence)} · ${text(frame.runtime_state)}</h4><details open><summary>World Truth · privileged</summary><pre>${text(JSON.stringify(frame.world_truth, null, 2))}</pre></details><details><summary>Agent Observation · no truth mapping</summary><pre>${text(JSON.stringify(frame.agent_observation, null, 2))}</pre></details><details><summary>Observer View</summary><pre>${text(JSON.stringify(frame.observer_view, null, 2))}</pre></details>`;
  }

  _status(message) { const el = this.el.querySelector("#swStatus"); if (el) el.textContent = message; }

  async open() { return this.openPlayback(); }
}
