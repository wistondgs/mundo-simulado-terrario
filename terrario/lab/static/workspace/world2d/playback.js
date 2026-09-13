/** Read-only trace playback. This module intentionally imports no command client. */
export class TracePlayback {
  constructor(api) { this.api = api; }
  async open(traceId) {
    const rows = await this.api.get(`/api/v1/world-stream/traces/${encodeURIComponent(traceId)}/events?after_sequence=-1&limit=10000`);
    const frames = new Map(), events = [];
    for (const row of rows) {
      const envelope = row.payload;
      if (["SNAPSHOT", "DELTA", "RESYNC"].includes(envelope.message_type)) {
        const frame = envelope.payload.frame; if (frame) frames.set(frame.tick, frame);
      } else if (envelope.message_type === "EVENT" && envelope.payload.event) events.push(envelope.payload.event);
    }
    return { traceId, frames, events, truncated: rows.length === 10000 };
  }
  async frameAt(traceId, tick) {
    const result = await this.api.get(`/api/v1/world-stream/traces/${encodeURIComponent(traceId)}/seek?tick=${encodeURIComponent(tick)}`);
    return result.frame?.frame || null;
  }
  async compare(traceId, left, right) {
    return this.api.get(`/api/v1/world-stream/traces/${encodeURIComponent(traceId)}/compare?left=${encodeURIComponent(left)}&right=${encodeURIComponent(right)}`);
  }
}
