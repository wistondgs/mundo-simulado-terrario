/** Scientific live observation: explicit state machine, reducer, and SSE client.
 * Transport only — it never mutates a trial and never fabricates provenance. */
export const SCIENTIFIC_LIVE_SCHEMA = "terrario.scientific-live/v1";

// One canonical observation state; no parallel booleans.
export const OBSERVATION_STATES = ["IDLE", "CONNECTING", "LIVE", "RESYNCING", "TERMINAL", "PLAYBACK", "LOST", "ERROR"];

const TRANSITIONS = {
  IDLE: ["CONNECTING"],
  CONNECTING: ["LIVE", "RESYNCING", "TERMINAL", "ERROR", "LOST", "IDLE"],
  LIVE: ["RESYNCING", "TERMINAL", "LOST", "ERROR", "IDLE"],
  RESYNCING: ["LIVE", "TERMINAL", "LOST", "ERROR", "IDLE"],
  TERMINAL: ["PLAYBACK", "IDLE"],
  PLAYBACK: ["IDLE", "ERROR"],
  LOST: ["CONNECTING", "IDLE"],
  ERROR: ["CONNECTING", "IDLE"],
};

export function initialObservationState() {
  return { status: "IDLE", frameSequence: -1, frame: null, identity: null, terminal: null,
    artifactState: "NONE", earliestRetained: 0, latestSequence: -1, gap: null, error: null };
}

export function transition(state, next) {
  if (!OBSERVATION_STATES.includes(next)) throw new Error(`UNKNOWN_OBSERVATION_STATE:${next}`);
  if (!(TRANSITIONS[state.status] || []).includes(next)) throw new Error(`ILLEGAL_OBSERVATION_TRANSITION:${state.status}->${next}`);
  return { ...state, status: next };
}

export function validateScientificFrame(frame) {
  if (!frame || frame.schema_version !== "terrario.scientific-frame/v1") throw new Error("SCIENTIFIC_FRAME_SCHEMA_MISMATCH");
  const identity = frame.identity || {};
  for (const key of ["execution_id", "trial_intent_id", "attempt_id", "plan_hash"]) {
    if (!identity[key]) throw new Error(`FRAME_IDENTITY_MISSING:${key}`);
  }
  if (!Number.isInteger(frame.frame_sequence) || frame.frame_sequence < 0) throw new Error("INVALID_FRAME_SEQUENCE");
  if (!Number.isInteger(frame.tick) || frame.tick < 0) throw new Error("INVALID_TICK");
  for (const view of ["world_truth", "agent_observation", "observer_view"]) {
    if (!frame[view] || typeof frame[view] !== "object") throw new Error(`INCOMPLETE_ATOMIC_FRAME:${view}`);
  }
  if (frame.cognitive_state !== undefined && (!frame.cognitive_state || typeof frame.cognitive_state !== "object" || Array.isArray(frame.cognitive_state))) {
    throw new Error("INVALID_COGNITIVE_STATE");
  }
  return frame;
}

function bindIdentity(state, identity) {
  if (!state.identity) return identity;
  for (const key of ["execution_id", "trial_intent_id", "attempt_id", "plan_hash"]) {
    if (String(state.identity[key]) !== String(identity[key])) throw new Error(`PROVENANCE_MISMATCH:${key}`);
  }
  return state.identity;
}

/** Reduce one transport event into the canonical observation state. */
export function reduceScientificEvent(state, event) {
  const type = event.type;
  if (type === "SNAPSHOT") {
    const frame = validateScientificFrame(event.frame);
    const identity = bindIdentity(state, frame.identity);
    return { ...state, status: event.terminal ? "TERMINAL" : "LIVE", frame, identity,
      frameSequence: frame.frame_sequence, artifactState: event.artifact_state || "LIVE_UNSEALED",
      terminal: event.terminal ? (event.terminal_state_payload || { runtime_state: frame.runtime_state }) : null,
      earliestRetained: event.earliest_retained_sequence ?? 0, latestSequence: event.latest_sequence ?? frame.frame_sequence,
      gap: null, error: null };
  }
  if (type === "FRAME") {
    const frame = validateScientificFrame(event.frame);
    const identity = bindIdentity(state, frame.identity);
    if (frame.frame_sequence <= state.frameSequence) return state; // duplicate is inert
    if (state.frameSequence >= 0 && frame.frame_sequence !== state.frameSequence + 1) {
      return { ...state, identity, status: "RESYNCING",
        gap: { expected: state.frameSequence + 1, received: frame.frame_sequence } };
    }
    return { ...state, identity, status: "LIVE", frame, frameSequence: frame.frame_sequence,
      latestSequence: Math.max(state.latestSequence, frame.frame_sequence), gap: null, error: null };
  }
  if (type === "TERMINAL") {
    return { ...state, status: "TERMINAL", artifactState: event.artifact_state || "CAS_SEALED",
      terminal: { runtime_state: event.runtime_state, artifact_state: event.artifact_state,
        frame_sequence: event.frame_sequence }, gap: null };
  }
  if (type === "RESYNC_REQUIRED") {
    return { ...state, status: "RESYNCING", gap: { reason: event.code || "RESYNC_REQUIRED", message: event.message } };
  }
  if (type === "HEARTBEAT") return state;
  if (type === "LOST") return { ...state, status: "LOST" };
  if (type === "ERROR") return { ...state, status: "ERROR", error: event.message || "UNKNOWN" };
  return state;
}

export class ScientificLiveClient {
  constructor(api, { onEvent, onStatus, onError } = {}) {
    this.api = api; this.onEvent = onEvent || (() => {}); this.onStatus = onStatus || (() => {});
    this.onError = onError || (() => {}); this.controller = null; this.after = -1; this.retry = 250;
  }
  close() { if (this.controller) this.controller.abort(); this.controller = null; }
  _path(executionId, trialId, suffix) {
    return `/api/v1/scientific-executions/${encodeURIComponent(executionId)}/trials/${encodeURIComponent(trialId)}${suffix}`;
  }
  async snapshot(executionId, trialId, attemptId) {
    return this.api.get(`${this._path(executionId, trialId, "/live")}?attempt_id=${encodeURIComponent(attemptId)}`);
  }
  async playback(executionId, trialId, attemptId, after = -1) {
    return this.api.get(`${this._path(executionId, trialId, "/frames")}?attempt_id=${encodeURIComponent(attemptId)}&after_sequence=${after}`);
  }
  async connect(executionId, trialId, attemptId) {
    this.close(); this.controller = new AbortController(); const signal = this.controller.signal;
    while (!signal.aborted) {
      try {
        this.onStatus("CONNECTING");
        const response = await fetch(`${this.api.base}${this._path(executionId, trialId, "/live/stream")}?attempt_id=${encodeURIComponent(attemptId)}&after_sequence=${this.after}`, {
          headers: { "X-CSRF-Token": this.api.csrfToken }, signal });
        if (!response.ok || !response.body) throw new Error(`STREAM_HTTP_${response.status}`);
        this.retry = 250; this.onStatus("CONNECTED");
        const terminal = await this._consume(response.body, signal);
        if (terminal) return; // clean terminal end; no reconnect
      } catch (error) {
        if (signal.aborted) break;
        this.onStatus("STALE"); this.onEvent({ type: "LOST" }); this.onError(error);
        await new Promise((resolve) => setTimeout(resolve, this.retry)); this.retry = Math.min(5000, this.retry * 2);
      }
    }
  }
  async _consume(body, signal) {
    const reader = body.getReader(), decoder = new TextDecoder(); let buffer = "";
    while (!signal.aborted) {
      const { done, value } = await reader.read(); if (done) throw new Error("STREAM_DISCONNECTED");
      buffer += decoder.decode(value, { stream: true });
      let boundary;
      while ((boundary = buffer.indexOf("\n\n")) >= 0) {
        const block = buffer.slice(0, boundary); buffer = buffer.slice(boundary + 2);
        const eventLine = block.split("\n").find((line) => line.startsWith("event: "));
        const dataLine = block.split("\n").find((line) => line.startsWith("data: "));
        if (!dataLine) continue;
        const payload = JSON.parse(dataLine.slice(6));
        const kind = eventLine ? eventLine.slice(7).trim() : "FRAME";
        if (kind === "FRAME") {
          this.after = Math.max(this.after, payload.frame_sequence);
          this.onEvent({ type: "FRAME", frame: payload });
        } else if (kind === "TERMINAL") {
          this.onEvent({ type: "TERMINAL", ...payload }); return true;
        } else if (kind === "RESYNC_REQUIRED") {
          this.onEvent({ type: "RESYNC_REQUIRED", ...payload }); return false;
        } else if (kind === "HEARTBEAT") {
          this.onEvent({ type: "HEARTBEAT", ...payload });
        }
      }
    }
    return false;
  }
}
