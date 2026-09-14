import test from "node:test";
import assert from "node:assert/strict";

import { CAPABILITY, capabilityValue, deriveCognitiveDeltas }
  from "../../terrario/lab/static/workspace/world2d/cognitive.js";

const identity = { execution_id: "e", trial_intent_id: "t", attempt_id: "a", plan_hash: "p" };
const frame = (sequence, cognitive_state, overrides = {}) => ({
  identity: { ...identity, ...(overrides.identity || {}) }, frame_sequence: sequence, cognitive_state, ...overrides,
});

test("capability renderer distinguishes absent, non-finite and bounded projections", () => {
  assert.equal(capabilityValue(undefined).state, CAPABILITY.UNAVAILABLE);
  assert.equal(capabilityValue("NOT_APPLICABLE").state, CAPABILITY.UNSUPPORTED);
  assert.equal(capabilityValue("NON_FINITE").state, CAPABILITY.NON_FINITE);
  const projected = capabilityValue({ kind: "ARRAY_PROJECTION", shape: [4096], count: 4096, finite_count: 4096, non_finite_count: 0, preview: [0] });
  assert.equal(projected.state, CAPABILITY.VALUE);
  assert.match(projected.text, /array \[4096\]/);
});

test("deltas require an adjacent frame in the identical scientific attempt", () => {
  const first = frame(3, { uncertainty: 0.2, prediction_error: 1, memory_summary: { episodic_size: 4 }, learning_summary: { update_count: 1 } });
  const adjacent = frame(4, { uncertainty: 0.5, prediction_error: 0.25, memory_summary: { episodic_size: 6 }, learning_summary: { update_count: 2 } });
  assert.deepEqual(deriveCognitiveDeltas(first, adjacent), { uncertainty: 0.3, predictionError: -0.75, memory: 2, updates: 1 });
  const otherAttempt = frame(4, adjacent.cognitive_state, { identity: { attempt_id: "other" } });
  assert.deepEqual(deriveCognitiveDeltas(first, otherAttempt),
    { uncertainty: "UNAVAILABLE", predictionError: "UNAVAILABLE", memory: "UNAVAILABLE", updates: "UNAVAILABLE" });
});
