/** Structured, read-only cognitive observatory for ScientificFrame payloads. */

export const CAPABILITY = Object.freeze({
  VALUE: "VALUE", NULL: "NULL", UNAVAILABLE: "UNAVAILABLE", UNSUPPORTED: "UNSUPPORTED", NON_FINITE: "NON_FINITE", MALFORMED: "MALFORMED",
});

export function capabilityValue(value) {
  if (value === undefined || value === "UNAVAILABLE") return { state: CAPABILITY.UNAVAILABLE, text: "UNAVAILABLE" };
  if (value === null) return { state: CAPABILITY.NULL, text: "NULL" };
  if (value === "NON_FINITE") return { state: CAPABILITY.NON_FINITE, text: "NON-FINITE" };
  if (value === "MALFORMED") return { state: CAPABILITY.MALFORMED, text: "MALFORMED" };
  if (value === "NOT_APPLICABLE" || value === "UNSUPPORTED") return { state: CAPABILITY.UNSUPPORTED, text: "UNSUPPORTED" };
  if (value?.kind === "ARRAY_PROJECTION") {
    const shape = `[${(value.shape || []).join("×")}]`;
    const stats = `n=${value.count} finite=${value.finite_count} non-finite=${value.non_finite_count}`;
    return { state: CAPABILITY.VALUE, text: `array ${shape} · ${stats}`, detail: JSON.stringify(value.preview) };
  }
  if (value?.kind === "MAPPING_PROJECTION") return { state: CAPABILITY.VALUE, text: `mapping · ${Object.keys(value.entries || {}).length} entries`, detail: JSON.stringify(value.entries) };
  if (typeof value === "number") return { state: CAPABILITY.VALUE, text: Number.isFinite(value) ? String(Number(value.toPrecision(6))) : String(value) };
  if (Array.isArray(value)) return { state: CAPABILITY.VALUE, text: `[${value.length} values]` };
  if (typeof value === "object") return { state: CAPABILITY.VALUE, text: "AVAILABLE" };
  return { state: CAPABILITY.VALUE, text: String(value) };
}

const path = (state, keys) => keys.reduce((value, key) => value == null ? undefined : value[key], state);

function sameScientificLineage(previousFrame, currentFrame) {
  const before = previousFrame?.identity, after = currentFrame?.identity;
  if (!before || !after || currentFrame.frame_sequence !== previousFrame.frame_sequence + 1) return false;
  return ["execution_id", "trial_intent_id", "attempt_id", "plan_hash"].every((key) => String(before[key]) === String(after[key]));
}

export function deriveCognitiveDeltas(previousFrame, currentFrame) {
  if (!sameScientificLineage(previousFrame, currentFrame)) {
    return { uncertainty: "UNAVAILABLE", predictionError: "UNAVAILABLE", memory: "UNAVAILABLE", updates: "UNAVAILABLE" };
  }
  const previousState = previousFrame.cognitive_state, currentState = currentFrame.cognitive_state;
  const delta = (keys) => {
    const before = path(previousState, keys), after = path(currentState, keys);
    if (before === "NOT_APPLICABLE" || after === "NOT_APPLICABLE" || before === "UNSUPPORTED" || after === "UNSUPPORTED") return "NOT_APPLICABLE";
    if (before === undefined || after === undefined || before === "UNAVAILABLE" || after === "UNAVAILABLE") return undefined;
    if (before === null || after === null) return null;
    return typeof before === "number" && typeof after === "number" ? after - before : undefined;
  };
  return {
    uncertainty: delta(["uncertainty"]),
    predictionError: delta(["prediction_error"]),
    memory: delta(["memory_summary", "episodic_size"]),
    updates: delta(["learning_summary", "update_count"]),
  };
}

const GROUPS = [
  ["Identity & policy", [["Architecture", ["architecture_id"]], ["Step", ["step"]], ["Selected action", ["selected_action"]], ["Selected action probability", ["selected_action_probability"]], ["Policy entropy", ["policy_entropy"]], ["Policy logits · projection", ["policy_logits"]], ["Action probabilities · projection", ["policy_probabilities"]]]],
  ["Prediction", [["Prediction · projection", ["prediction"]], ["Uncertainty", ["uncertainty"]], ["Prediction error ε", ["prediction_error"]], ["Current loss", ["current_loss"]]]],
  ["Memory & learning", [["Episodic memory", ["memory_summary", "episodic_size"]], ["Long-term norm", ["memory_summary", "longterm_norm"]], ["Gradient norm", ["gradient_norm"]], ["Parameter update norm", ["parameter_delta_norm"]], ["Update count", ["learning_summary", "update_count"]]]],
];

function appendCell(container, label, value) {
  const cell = document.createElement("div"), title = document.createElement("dt"), detail = document.createElement("dd");
  const display = capabilityValue(value);
  cell.className = "w2d-cognitive-cell"; title.textContent = label; detail.textContent = display.text;
  detail.dataset.capability = display.state; if (display.detail) detail.title = display.detail;
  cell.append(title, detail); container.append(cell);
}

export function renderCognitiveState(container, currentFrame, previousFrame) {
  container.replaceChildren();
  const state = currentFrame?.cognitive_state || {};
  for (const [title, fields] of GROUPS) {
    const group = document.createElement("section"), heading = document.createElement("h4"), grid = document.createElement("dl");
    group.className = "w2d-cognitive-group"; heading.textContent = title; grid.className = "w2d-cognitive-grid";
    for (const [label, keys] of fields) appendCell(grid, label, path(state, keys));
    group.append(heading, grid); container.append(group);
  }
  const deltas = deriveCognitiveDeltas(previousFrame, currentFrame);
  const group = document.createElement("section"), heading = document.createElement("h4"), grid = document.createElement("dl");
  group.className = "w2d-cognitive-group w2d-cognitive-derived"; heading.textContent = "Observer-derived deltas · NOT CAUSAL"; grid.className = "w2d-cognitive-grid";
  appendCell(grid, "ΔU", deltas.uncertainty); appendCell(grid, "Δε", deltas.predictionError);
  appendCell(grid, "ΔMemory", deltas.memory); appendCell(grid, "ΔUpdates", deltas.updates);
  group.append(heading, grid); container.append(group);
}
