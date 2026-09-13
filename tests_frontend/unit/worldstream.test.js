import test from "node:test";
import assert from "node:assert/strict";
import { BoundedFrameRing, initialTemporalState, reduceEnvelope, validateWorldFrame } from "../../terrario/lab/static/workspace/world2d/protocol.js";
import { diffFrames } from "../../terrario/lab/static/workspace/world2d/timeline.js";

const view = (kind, tick = 0, payload = {}) => ({ kind, tick, simulation_time: tick, status: "SYNCHRONIZED", payload, provenance: {} });
const frame = (tick = 0) => ({ schema_version: "terrario.worldstream/v1", session_id: "s", world_instance_id: "w", scenario_id: "D2", world_seed: 1, agent_identity: {}, tick, sequence: tick, simulation_time: tick, frame_origin: "TRANSITION_RESULT", trace_id: "t", views: [view("WORLD_TRUTH_PRIVILEGED", tick, { objects: {} }), view("AGENT_OBSERVATION", tick, { channels: [], mask: [], agent_energy: 1, time_fraction: 0 }), view("OBSERVER_VIEW", tick, { world: { objects: {} } })] });
const envelope = (sequence, message_type, payload) => ({ schema_version: "terrario.worldstream/v1", session_id: "s", trace_id: "t", sequence, tick: 0, emitted_at: "now", message_type, payload });

test("contract rejects a non-atomic three-view frame", () => {
  const broken = frame(); broken.views[1].tick = 4;
  assert.throws(() => validateWorldFrame(broken), /UNSYNCHRONIZED/);
});

test("reducer rejects a delta with the wrong base and requests resync", () => {
  let state = reduceEnvelope(initialTemporalState("s"), envelope(0, "SNAPSHOT", { frame: frame(0) }));
  state = reduceEnvelope(state, envelope(1, "DELTA", { base_sequence: 99, frame: frame(1), operations: [] }));
  assert.equal(state.status, "RESYNCING"); assert.equal(state.frame.tick, 0);
});

test("duplicate and out-of-order messages never replay effects", () => {
  const state = reduceEnvelope(initialTemporalState("s"), envelope(0, "EVENT", { event: { event_type: "ACTION" } }));
  const duplicate = reduceEnvelope(state, envelope(0, "EVENT", { event: { event_type: "ACTION" } }));
  assert.equal(duplicate.events.length, 1);
});

test("bounded ring reports overflow without evicting authoritative frames", () => {
  const ring = new BoundedFrameRing(1, 10000); assert.equal(ring.push({ n: 1 }), true); assert.equal(ring.push({ n: 2 }), false); assert.equal(ring.shift().n, 1);
});

test("wrong-session data is inert and visible as local error", () => {
  const wrong = { ...envelope(0, "EVENT", { event: {} }), session_id: "wrong" };
  assert.equal(reduceEnvelope(initialTemporalState("s"), wrong).error, "WRONG_SESSION");
});

test("diff labels calculated state changes as non-causal", () => {
  const left = frame(0), right = frame(1); left.views[0].payload.objects = { "1": { pos: [0, 0], properties: {} } }; right.views[0].payload.objects = { "1": { pos: [1, 0], properties: {} }, "2": { pos: [2, 0] } };
  const diff = diffFrames(left, right); assert.deepEqual(diff.added, ["2"]); assert.deepEqual(diff.moved, ["1"]); assert.match(diff.explanation, /NOT CAUSAL/);
});
