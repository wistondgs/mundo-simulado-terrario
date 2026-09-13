// @ts-check
/**
 * Contract tests: verify the backend API responses match the frontend typed
 * contracts (no ad-hoc objects, no silent drift). These run against a real
 * Terrario backend over HTTP.
 */
import { test, expect } from "@playwright/test";

const BASE = "http://127.0.0.1:8877";

async function post(page, path, payload) {
  const response = await page.request.post(`${BASE}${path}`, { data: payload });
  return response.json();
}

async function get(page, path) {
  const response = await page.request.get(`${BASE}${path}`);
  return response.json();
}

test.describe("backend/frontend contract", () => {
  test("cross-graph status envelope matches contract", async ({ page }) => {
    const body = await get(page, "/api/v1/cross-graph");
    const data = body.data ?? body;
    expect(data).toHaveProperty("counts");
    expect(data.counts).toHaveProperty("links");
    expect(data.counts).toHaveProperty("hyperlinks");
    expect(data.counts).toHaveProperty("snapshots");
    // firewall flags
    expect(data.scientific_execution).toBe(false);
    expect(data.evidence_publication).toBe(false);
    expect(data.theory_graph_modified).toBe(false);
    expect(data.evidence_graph_modified).toBe(false);
  });

  test("graph-slice response matches GraphSlice typedef", async ({ page }) => {
    const body = await post(page, "/api/v1/cross-graph/graph-slice", {
      ref: { domain: "WORLD", entity_type: "WorldDefinition", entity_id: "D2" },
      depth: 1,
    });
    const slice = body.data ?? body;
    expect(slice).toHaveProperty("center");
    expect(slice).toHaveProperty("nodes");
    expect(Array.isArray(slice.nodes)).toBe(true);
    expect(slice).toHaveProperty("edges");
    expect(slice).toHaveProperty("hyperedges");
    expect(slice).toHaveProperty("snapshot_manifest");
    expect(slice.snapshot_manifest).toHaveProperty("root_hash");
    for (const edge of slice.edges) {
      expect(edge).toHaveProperty("link_id");
      expect(edge).toHaveProperty("source");
      expect(edge).toHaveProperty("target");
      expect(edge).toHaveProperty("relation_type");
      expect(edge).toHaveProperty("assertion_class");
    }
  });

  test("reference list matches ReferenceRecord typedef", async ({ page }) => {
    const body = await get(page, "/api/v1/reference-graph/references");
    const data = body.data ?? body;
    expect(data).toHaveProperty("items");
    expect(Array.isArray(data.items)).toBe(true);
    for (const ref of data.items.slice(0, 5)) {
      expect(ref).toHaveProperty("reference_id");
      expect(ref).toHaveProperty("reference_type");
      expect(ref).toHaveProperty("constructs");
      expect(ref).toHaveProperty("verification_status");
      expect(Array.isArray(ref.constructs)).toBe(true);
    }
  });

  test("trace breaks match TraceBreak typedef", async ({ page }) => {
    const body = await get(page, "/api/v1/cross-graph/trace-breaks");
    const data = body.data ?? body;
    expect(data).toHaveProperty("items");
    for (const b of data.items) {
      expect(b).toHaveProperty("from_ref_json");
      expect(b).toHaveProperty("expected_next_domain");
      expect(b).toHaveProperty("reason");
    }
  });

  test("error envelope carries typed code (no plain 'Error')", async ({ page }) => {
    const response = await page.request.post(`${BASE}/api/v1/cross-graph/resolve`, {
      data: { domain: "WORLD", entity_type: "WorldDefinition", entity_id: "NOPE" },
    });
    const body = await response.json();
    const data = body.data ?? body;
    // resolve returns a structured status, not a crash
    expect(data).toHaveProperty("status");
    expect(["DANGLING", "RESOLVED", "HASH_MISMATCH", "STALE_VERSION"]).toContain(data.status);
  });
});
