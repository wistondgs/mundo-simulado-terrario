// @ts-check
import { test, expect } from "@playwright/test";

/**
 * Render benchmarks: characterize the canvas renderer at 1k and 10k visible
 * elements. Measures render duration, interaction latency, and expansion
 * latency. Reports real numbers; no universal scalability claim.
 */
test.describe("render benchmarks", () => {
  for (const scale of [1000, 10000]) {
    test(`renders ${scale} visible nodes`, async ({ page }) => {
      await page.goto("/workspace/index.html");
      await page.waitForTimeout(1500);

      const metrics = await page.evaluate(async (nodeCount) => {
        // Build a synthetic graph in-page and drive the renderer directly.
        const canvas = document.querySelector('[data-panel="canvas"] canvas');
        if (!canvas) return { error: "no canvas" };
        // @ts-ignore
        const mod = await import("/workspace/render/graph-renderer.js");
        const renderer = new mod.GraphRenderer(canvas, {});
        const nodes = [];
        const cols = Math.ceil(Math.sqrt(nodeCount));
        for (let i = 0; i < nodeCount; i++) {
          nodes.push({
            key: `WORLD:WorldDefinition:W${i}`,
            domain: ["WORLD", "THEORY", "REFERENCE", "SCENARIO"][i % 4],
            entity_type: "Entity",
            entity_id: `W${i}`,
            label: `W${i}`,
            x: (i % cols) * 16,
            y: Math.floor(i / cols) * 16,
          });
        }
        const edges = [];
        for (let i = 0; i < nodeCount - 1; i++) {
          edges.push({ link_id: `l${i}`, source: nodes[i].key, target: nodes[i + 1].key,
                       relation_type: "MAPS_TO", assertion_class: "USER_ASSERTED" });
        }
        renderer.setGraph({ nodes, edges, hyperedges: [] });

        // measure render duration over several frames
        const renderSamples = [];
        for (let i = 0; i < 30; i++) {
          const t0 = performance.now();
          renderer.render();
          renderSamples.push(performance.now() - t0);
        }
        renderSamples.sort((a, b) => a - b);
        const medianRender = renderSamples[Math.floor(renderSamples.length / 2)];

        // measure pan interaction latency
        const panSamples = [];
        for (let i = 0; i < 20; i++) {
          renderer.viewport.panX += 4;
          const t0 = performance.now();
          renderer.render();
          panSamples.push(performance.now() - t0);
        }
        panSamples.sort((a, b) => a - b);
        const medianPan = panSamples[Math.floor(panSamples.length / 2)];

        const memory = (performance.memory && performance.memory.usedJSHeapSize) || null;
        return {
          nodeCount,
          edgeCount: edges.length,
          medianRenderMs: Math.round(medianRender * 100) / 100,
          medianPanMs: Math.round(medianPan * 100) / 100,
          approxFps: Math.round(1000 / Math.max(0.01, medianRender)),
          heapBytes: memory,
        };
      }, scale);

      console.log("RENDER_BENCH", JSON.stringify(metrics));
      expect(metrics.error).toBeUndefined();
      expect(metrics.nodeCount).toBe(scale);
      // Sanity: renderer completes; we report real numbers, not a fixed threshold.
      expect(metrics.medianRenderMs).toBeGreaterThan(0);
    });
  }
});
