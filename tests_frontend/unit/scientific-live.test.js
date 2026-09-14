import test from "node:test";
import assert from "node:assert/strict";

import { initialObservationState, reduceScientificEvent, transition, validateScientificFrame,
  OBSERVATION_STATES } from "../../terrario/lab/static/workspace/world2d/scientific-protocol.js";

const identity = { execution_id: "e1", trial_intent_id: "t1", attempt_id: "a1", plan_hash: "ph",
  preregistration_root_hash: "root", software_identity: "sw", scenario_identity: "sc",
  agent_identity: "agent", world_seed: 7, agent_seed: 99, schema_version: "terrario.scientific-trial-identity/v1" };

const frame = (sequence, tick = sequence) => ({ schema_version: "terrario.scientific-frame/v1", identity,
  tick, simulation_time: tick, world_revision: 0, frame_sequence: sequence,
  world_truth: { time: tick }, agent_observation: { channels: [] }, observer_view: { events: [] },
  runtime_state: "RUNNING", trace_cursor: sequence });

test("state machine allows only deterministic transitions", () => {
  const idle = initialObservationState();
  assert.equal(idle.status, "IDLE");
  assert.equal(transition(idle, "CONNECTING").status, "CONNECTING");
  assert.throws(() => transition(idle, "LIVE"), /ILLEGAL_OBSERVATION_TRANSITION/);
  assert.throws(() => transition(idle, "BOGUS"), /UNKNOWN_OBSERVATION_STATE/);
  for (const state of OBSERVATION_STATES) assert.ok(typeof state === "string");
});

test("IDLE -> CONNECTING -> LIVE via snapshot with tick 0", () => {
  let state = transition(initialObservationState(), "CONNECTING");
  state = reduceScientificEvent(state, { type: "SNAPSHOT", frame: frame(0), terminal: false,
    artifact_state: "LIVE_UNSEALED", earliest_retained_sequence: 0, latest_sequence: 0 });
  assert.equal(state.status, "LIVE");
  assert.equal(state.frameSequence, 0);
  assert.equal(state.artifactState, "LIVE_UNSEALED");
  assert.equal(state.identity.plan_hash, "ph");
});

test("contiguous frames stay LIVE and monotonic", () => {
  let state = reduceScientificEvent(transition(initialObservationState(), "CONNECTING"),
    { type: "SNAPSHOT", frame: frame(0), terminal: false });
  state = reduceScientificEvent(state, { type: "FRAME", frame: frame(1) });
  state = reduceScientificEvent(state, { type: "FRAME", frame: frame(2) });
  assert.equal(state.status, "LIVE");
  assert.equal(state.frameSequence, 2);
});

test("frame gap forces RESYNCING with explicit gap info", () => {
  let state = reduceScientificEvent(transition(initialObservationState(), "CONNECTING"),
    { type: "SNAPSHOT", frame: frame(100), terminal: false });
  state = reduceScientificEvent(state, { type: "FRAME", frame: frame(103) });
  assert.equal(state.status, "RESYNCING");
  assert.deepEqual(state.gap, { expected: 101, received: 103 });
});

test("RESYNCING -> LIVE after authoritative snapshot", () => {
  let state = reduceScientificEvent(transition(initialObservationState(), "CONNECTING"),
    { type: "SNAPSHOT", frame: frame(100), terminal: false });
  state = reduceScientificEvent(state, { type: "FRAME", frame: frame(103) });
  state = reduceScientificEvent({ ...state, frameSequence: -1 },
    { type: "SNAPSHOT", frame: frame(103), terminal: false, artifact_state: "LIVE_UNSEALED" });
  assert.equal(state.status, "LIVE");
  assert.equal(state.frameSequence, 103);
});

test("LIVE -> TERMINAL -> PLAYBACK keeps provenance identical", () => {
  let state = reduceScientificEvent(transition(initialObservationState(), "CONNECTING"),
    { type: "SNAPSHOT", frame: frame(0), terminal: false });
  state = reduceScientificEvent(state, { type: "FRAME", frame: frame(1) });
  state = reduceScientificEvent(state, { type: "TERMINAL", runtime_state: "COMPLETED", artifact_state: "CAS_SEALED", frame_sequence: 1 });
  assert.equal(state.status, "TERMINAL");
  assert.equal(state.artifactState, "CAS_SEALED");
  state = transition(state, "PLAYBACK");
  assert.equal(state.status, "PLAYBACK");
  assert.equal(state.identity.plan_hash, "ph");
  assert.equal(state.identity.attempt_id, "a1");
});

test("duplicate frames are inert", () => {
  let state = reduceScientificEvent(transition(initialObservationState(), "CONNECTING"),
    { type: "SNAPSHOT", frame: frame(5), terminal: false });
  const again = reduceScientificEvent(state, { type: "FRAME", frame: frame(5) });
  assert.equal(again.frameSequence, 5);
  assert.equal(again.status, "LIVE");
});

test("provenance mismatch fails closed", () => {
  let state = reduceScientificEvent(transition(initialObservationState(), "CONNECTING"),
    { type: "SNAPSHOT", frame: frame(0), terminal: false });
  const forged = frame(1); forged.identity = { ...identity, plan_hash: "FORGED" };
  assert.throws(() => reduceScientificEvent(state, { type: "FRAME", frame: forged }), /PROVENANCE_MISMATCH/);
});

test("frame validation requires atomic views and identity", () => {
  assert.throws(() => validateScientificFrame({ schema_version: "wrong" }), /SCHEMA_MISMATCH/);
  const incomplete = frame(0); delete incomplete.observer_view;
  assert.throws(() => validateScientificFrame(incomplete), /INCOMPLETE_ATOMIC_FRAME/);
  const noIdentity = frame(0); noIdentity.identity = {};
  assert.throws(() => validateScientificFrame(noIdentity), /FRAME_IDENTITY_MISSING/);
});

test("historical frames without additive cognition remain valid", () => {
  const historical = frame(0);
  assert.doesNotThrow(() => validateScientificFrame(historical));
  const cognitive = { ...historical, cognitive_state: { schema_version: "terrario.scientific-cognitive-transport/v1" } };
  assert.doesNotThrow(() => validateScientificFrame(cognitive));
  assert.throws(() => validateScientificFrame({ ...historical, cognitive_state: "forged" }), /INVALID_COGNITIVE_STATE/);
});

test("RESYNC_REQUIRED and ERROR events map to canonical states", () => {
  let state = reduceScientificEvent(transition(initialObservationState(), "CONNECTING"),
    { type: "SNAPSHOT", frame: frame(0), terminal: false });
  state = reduceScientificEvent(state, { type: "RESYNC_REQUIRED", code: "CURSOR_TOO_OLD", message: "stale" });
  assert.equal(state.status, "RESYNCING");
  assert.equal(state.gap.reason, "CURSOR_TOO_OLD");
  state = reduceScientificEvent(state, { type: "ERROR", message: "boom" });
  assert.equal(state.status, "ERROR");
  assert.equal(state.error, "boom");
});

test("resync replaces the whole scientific frame, including cognition", () => {
  const oldFrame = { ...frame(10), cognitive_state: { step: 10, uncertainty: 0.1 } };
  let state = reduceScientificEvent(transition(initialObservationState(), "CONNECTING"),
    { type: "SNAPSHOT", frame: oldFrame, terminal: false });
  state = reduceScientificEvent(state, { type: "FRAME", frame: { ...frame(12), cognitive_state: { step: 12, uncertainty: 0.3 } } });
  assert.equal(state.status, "RESYNCING");
  assert.equal(state.frame.cognitive_state.step, 10);
  const authoritative = { ...frame(12), cognitive_state: { step: 12, uncertainty: 0.3 } };
  state = reduceScientificEvent({ ...state, frameSequence: -1 },
    { type: "SNAPSHOT", frame: authoritative, terminal: false });
  assert.equal(state.status, "LIVE");
  assert.equal(state.frame.tick, 12);
  assert.equal(state.frame.cognitive_state.step, 12);
});
