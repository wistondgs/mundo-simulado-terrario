/** WorldStream v1 validators, bounded buffers, reducer, and authenticated SSE. */
export const STREAM_SCHEMA = "terrario.worldstream/v1";
export const VIEW_KINDS = ["WORLD_TRUTH_PRIVILEGED", "AGENT_OBSERVATION", "OBSERVER_VIEW"];

export function validateEnvelope(value) {
  if (!value || value.schema_version !== STREAM_SCHEMA) throw new Error("WORLDSTREAM_SCHEMA_MISMATCH");
  if (!Number.isInteger(value.sequence) || value.sequence < 0) throw new Error("INVALID_SEQUENCE");
  if (!value.session_id || !value.message_type || !value.payload) throw new Error("MALFORMED_ENVELOPE");
  return value;
}

export function validateWorldFrame(frame) {
  if (!frame || frame.schema_version !== STREAM_SCHEMA) throw new Error("WORLD_FRAME_SCHEMA_MISMATCH");
  const kinds = new Set((frame.views || []).map((view) => view.kind));
  if (VIEW_KINDS.some((kind) => !kinds.has(kind)) || frame.views.length !== 3) throw new Error("INCOMPLETE_ATOMIC_FRAME");
  if (frame.views.some((view) => view.tick !== frame.tick)) throw new Error("UNSYNCHRONIZED_FRAME");
  return frame;
}

export class BoundedFrameRing {
  constructor(maxFrames = 512, maxBytes = 64 * 1024 * 1024) {
    this.maxFrames = maxFrames; this.maxBytes = maxBytes; this.items = []; this.bytes = 0;
  }
  push(value) {
    const bytes = new TextEncoder().encode(JSON.stringify(value)).byteLength;
    if (bytes > this.maxBytes || this.items.length >= this.maxFrames || this.bytes + bytes > this.maxBytes) return false;
    this.items.push({ value, bytes }); this.bytes += bytes; return true;
  }
  shift() { const item = this.items.shift(); if (!item) return null; this.bytes -= item.bytes; return item.value; }
  clear() { this.items.length = 0; this.bytes = 0; }
  get length() { return this.items.length; }
}

// Presentation history is intentionally bounded. The append-only server trace,
// not browser memory, is the authority for older frames and arbitrary seeks.
export class BoundedFrameHistory {
  constructor(maxFrames = 512) { this.maxFrames = maxFrames; this.frames = new Map(); this.order = []; }
  set(tick, frame) {
    if (this.frames.has(tick)) this.order.splice(this.order.indexOf(tick), 1);
    this.frames.set(tick, frame); this.order.push(tick);
    while (this.order.length > this.maxFrames) this.frames.delete(this.order.shift());
    return this;
  }
  get(tick) { return this.frames.get(tick); }
  has(tick) { return this.frames.has(tick); }
  clear() { this.frames.clear(); this.order.length = 0; }
  keys() { return this.frames.keys(); }
  entries() { return this.frames.entries(); }
  get size() { return this.frames.size; }
}

export function initialTemporalState(sessionId = null) {
  return { sessionId, sequence: -1, frameSequence: -1, frame: null, status: "STALE", events: [], gap: null, error: null };
}

export function reduceEnvelope(state, raw) {
  const envelope = validateEnvelope(raw);
  if (state.sessionId && envelope.session_id !== state.sessionId) return { ...state, error: "WRONG_SESSION" };
  if (envelope.sequence <= state.sequence) return state; // duplicate/out-of-order is inert
  if (state.sequence >= 0 && envelope.sequence !== state.sequence + 1) {
    return { ...state, sequence: envelope.sequence, status: "RESYNCING", gap: { expected: state.sequence + 1, received: envelope.sequence } };
  }
  const next = { ...state, sessionId: envelope.session_id, sequence: envelope.sequence, error: null };
  if (envelope.message_type === "GAP") return { ...next, status: "RESYNCING", gap: envelope.payload };
  if (envelope.message_type === "EVENT") return { ...next, events: [...state.events, envelope.payload.event] };
  if (["SNAPSHOT", "RESYNC"].includes(envelope.message_type)) {
    return { ...next, frame: validateWorldFrame(envelope.payload.frame), frameSequence: envelope.sequence, status: "SYNCHRONIZED", gap: null };
  }
  if (envelope.message_type === "DELTA") {
    if (envelope.payload.base_sequence !== state.frameSequence) return { ...next, status: "RESYNCING", gap: { expectedBase: state.frameSequence, receivedBase: envelope.payload.base_sequence } };
    return { ...next, frame: validateWorldFrame(envelope.payload.frame), frameSequence: envelope.sequence, status: "SYNCHRONIZED", gap: null };
  }
  return next;
}

export class WorldStreamClient {
  constructor(api, { onEnvelope, onStatus, onError } = {}) {
    this.api = api; this.onEnvelope = onEnvelope || (() => {}); this.onStatus = onStatus || (() => {});
    this.onError = onError || (() => {}); this.controller = null; this.retry = 250; this.after = -1;
  }
  async create(payload) { return this.api.post("/api/v1/world-stream/sessions", payload, { mutation: true }); }
  async command(sessionId, command, revision, parameters = {}) {
    return this.api.post(`/api/v1/world-stream/sessions/${encodeURIComponent(sessionId)}/commands`, {
      command_id: crypto.randomUUID(), command, expected_session_revision: revision, parameters,
    }, { mutation: true });
  }
  async resync(sessionId, lastFrameSequence, reason) {
    return this.api.post(`/api/v1/world-stream/sessions/${encodeURIComponent(sessionId)}/resync`, {
      after_sequence: this.after, last_frame_sequence: lastFrameSequence, reason,
    }, { mutation: true });
  }
  close() { if (this.controller) this.controller.abort(); this.controller = null; }
  async connect(sessionId) {
    this.close(); this.controller = new AbortController(); const signal = this.controller.signal;
    while (!signal.aborted) {
      try {
        this.onStatus("CONNECTING");
        const response = await fetch(`${this.api.base}/api/v1/world-stream/sessions/${encodeURIComponent(sessionId)}/stream?after_sequence=${this.after}`, {
          headers: { "X-CSRF-Token": this.api.csrfToken }, signal,
        });
        if (!response.ok || !response.body) throw new Error(`STREAM_HTTP_${response.status}`);
        this.retry = 250; this.onStatus("CONNECTED");
        await this._consume(response.body, signal);
      } catch (error) {
        if (signal.aborted) break;
        this.onStatus("STALE"); this.onError(error);
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
        const data = block.split("\n").find((line) => line.startsWith("data: "));
        if (!data) continue;
        const envelope = validateEnvelope(JSON.parse(data.slice(6))); this.after = Math.max(this.after, envelope.sequence); this.onEnvelope(envelope);
      }
    }
  }
}
