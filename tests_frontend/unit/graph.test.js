// @ts-check
/**
 * Frontend unit tests: graph transformations and GraphSlice mapping.
 * Run with `node --test` (no browser required).
 */
import { test } from "node:test";
import assert from "node:assert/strict";

// Minimal reimplementation of the mergeSlice transform for unit testing
// (kept in sync with main.js; the E2E suite exercises the real path).
function keyToRef(key) {
  const [domain, entity_type, ...rest] = key.split(":");
  return { domain, entity_type, entity_id: rest.join(":") };
}

function mergeSlice(graph, slice) {
  const existing = new Map(graph.nodes.map((n) => [n.key, n]));
  for (const key of slice.nodes) {
    if (!existing.has(key)) {
      const [domain, entity_type, ...rest] = key.split(":");
      existing.set(key, { key, domain, entity_type, entity_id: rest.join(":"),
                          label: rest.join(":"), x: 0, y: 0 });
    }
  }
  const edgeKeys = new Set(graph.edges.map((e) => e.link_id));
  const newEdges = (slice.edges || []).filter((e) => !edgeKeys.has(e.link_id));
  const hyperKeys = new Set(graph.hyperedges.map((h) => h.hyperlink_id));
  const newHyper = (slice.hyperedges || []).filter((h) => !hyperKeys.has(h.hyperlink_id));
  return {
    nodes: [...existing.values()],
    edges: [...graph.edges, ...newEdges],
    hyperedges: [...graph.hyperedges, ...newHyper],
  };
}

test("keyToRef parses canonical keys", () => {
  assert.deepEqual(keyToRef("REFERENCE:ScientificReferenceRecord:WORLD-REF-001"), {
    domain: "REFERENCE", entity_type: "ScientificReferenceRecord", entity_id: "WORLD-REF-001",
  });
  assert.deepEqual(keyToRef("THEORY:RawConceptRecord:P3C-0052"), {
    domain: "THEORY", entity_type: "RawConceptRecord", entity_id: "P3C-0052",
  });
});

test("mergeSlice adds new nodes and dedupes edges/hyperedges", () => {
  const graph = { nodes: [{ key: "WORLD:WorldDefinition:D2" }],
                  edges: [{ link_id: "l1" }], hyperedges: [{ hyperlink_id: "h1" }] };
  const slice = {
    nodes: ["WORLD:WorldDefinition:D2", "SCENARIO:ScenarioDefinition:D2"],
    edges: [{ link_id: "l1" }, { link_id: "l2", source: "a", target: "b" }],
    hyperedges: [{ hyperlink_id: "h1" }, { hyperlink_id: "h2", members: ["a", "b"] }],
  };
  const merged = mergeSlice(graph, slice);
  assert.equal(merged.nodes.length, 2, "adds the new node, keeps existing");
  assert.equal(merged.edges.length, 2, "dedupes edge l1, adds l2");
  assert.equal(merged.hyperedges.length, 2, "dedupes hyperedge h1, adds h2");
});

test("mergeSlice derives domain/entity_type from node keys", () => {
  const graph = { nodes: [], edges: [], hyperedges: [] };
  const merged = mergeSlice(graph, { nodes: ["THEORY:RawConceptRecord:P3C-0052"], edges: [], hyperedges: [] });
  assert.equal(merged.nodes[0].domain, "THEORY");
  assert.equal(merged.nodes[0].entity_type, "RawConceptRecord");
  assert.equal(merged.nodes[0].entity_id, "P3C-0052");
});
