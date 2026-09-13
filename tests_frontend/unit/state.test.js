// @ts-check
/**
 * Frontend unit tests: state model, command journal, and store separation.
 * Run with `node --test` (no browser required).
 */
import { test } from "node:test";
import assert from "node:assert/strict";

import { Store, CommandJournal } from "../../terrario/lab/static/workspace/core/state.js";
import { DOMAIN_VISUAL, CLAIM_TYPE_LABEL, OPERATING_MODE, ERROR_CLASS } from "../../terrario/lab/static/workspace/core/contracts.js";

test("Store notifies subscribers and keeps immutability of previous snapshot", () => {
  const store = new Store({ a: 1 });
  const seen = [];
  store.subscribe((state) => seen.push(state.a));
  const before = store.get();
  store.set({ a: 2 });
  assert.equal(store.get().a, 2);
  assert.equal(before.a, 1, "previous snapshot must not mutate");
  assert.deepEqual(seen, [2]);
});

test("Store unsubscribe stops notifications", () => {
  const store = new Store({ a: 1 });
  let count = 0;
  const unsub = store.subscribe(() => count++);
  store.set({ a: 2 });
  unsub();
  store.set({ a: 3 });
  assert.equal(count, 1);
});

test("CommandJournal undo/redo for composition ops", () => {
  const journal = new CommandJournal();
  const state = { value: 0 };
  journal.push({
    label: "increment", kind: "COMPOSITION",
    undo: () => { state.value -= 1; },
    redo: () => { state.value += 1; },
  });
  state.value = 1;
  journal.undo();
  assert.equal(state.value, 0);
  journal.redo();
  assert.equal(state.value, 1);
});

test("CommandJournal rejects canonical operations (append-only, not undoable)", () => {
  const journal = new CommandJournal();
  assert.throws(
    () => journal.push({ label: "x", kind: "CANONICAL", undo: () => {}, redo: () => {} }),
    /append-only/,
  );
});

test("domain visual language never relies on color alone", () => {
  for (const [domain, visual] of Object.entries(DOMAIN_VISUAL)) {
    assert.ok(visual.shape, `${domain} must have a shape`);
    assert.ok(visual.icon, `${domain} must have an icon`);
    assert.ok(visual.label, `${domain} must have a label`);
    assert.ok(visual.color, `${domain} must have a color`);
  }
});

test("claim type classification is always present", () => {
  for (const key of ["SOURCE_TEXT", "SOURCE_REPORTED_CLAIM", "ANALYST_INTERPRETATION",
                     "MACHINE_EXTRACTION_UNVERIFIED", "USER_NOTE"]) {
    assert.ok(CLAIM_TYPE_LABEL[key], `claim type ${key} must be labelled`);
  }
});

test("operating modes are distinct", () => {
  assert.notEqual(OPERATING_MODE.EXPLORATORY_LATEST, OPERATING_MODE.PINNED_REPRODUCIBLE);
});

test("error classes cover the UI error model", () => {
  for (const key of ["DOMAIN_UNAVAILABLE", "STALE_REFERENCE", "HASH_MISMATCH",
                     "TRACE_BREAK", "UNREVIEWED_CANDIDATE", "INTEGRITY_FAILURE",
                     "QUERY_BUDGET_EXCEEDED"]) {
    assert.ok(ERROR_CLASS[key], `error class ${key} must exist`);
  }
});
