// @ts-check
import { test, expect } from "@playwright/test";

const workloads = [100, 1000, 10_000, 50_000];
const renderers = ["Canvas2D", "WebGL2"];
const surfaces = [1, 3];

/**
 * Sustained renderer characterization.  It deliberately drives the actual
 * World2D renderer rather than the cross-graph renderer.  Synthetic frame
 * payloads make workload deterministic; when three surfaces are requested
 * they exercise the actual World Truth, Agent Observation, and Observer view
 * shapes. They are instrumentation data, never a scientific run.
 */
for (const renderer of renderers) for (const entityCount of workloads) for (const viewCount of surfaces) {
  test(`${renderer}: ${entityCount} entities across ${viewCount} surface(s)`, async ({ page }, testInfo) => {
    test.setTimeout(120_000);
    await page.goto("/workspace/index.html");
    const metrics = await page.evaluate(async ({ renderer, entityCount, viewCount }) => {
      const mod = await import("/workspace/world2d/renderers.js");
      const Renderer = renderer === "WebGL2" ? mod.WebGL2Renderer : mod.Canvas2DRenderer;
      const side = Math.ceil(Math.sqrt(entityCount)), objects = {};
      for (let index = 0; index < entityCount; index++) {
        const row = Math.floor(index / side), column = index % side;
        objects[`synthetic-${index}`] = { object_id: `synthetic-${index}`, pos: [row, column], properties: { causal_class: index % 2 ? "A" : "B" } };
      }
      const world = { grid_width: side, grid_height: side, objects, agents: {} };
      const channels = Array.from({ length: side }, (_, row) => Array.from({ length: side }, (_, column) => (row + column) % 2));
      const mask = Array.from({ length: side }, () => Array.from({ length: side }, () => true));
      const views = [
        { kind: "WORLD_TRUTH_PRIVILEGED", tick: 0, simulation_time: 0, status: "SYNCHRONIZED", payload: world },
        { kind: "AGENT_OBSERVATION", tick: 0, simulation_time: 0, status: "SYNCHRONIZED", payload: { channels: [channels], mask, agent_energy: 1, time_fraction: 0 } },
        { kind: "OBSERVER_VIEW", tick: 0, simulation_time: 0, status: "SYNCHRONIZED", payload: { world } },
      ];
      const activeViews = viewCount === 1 ? [views[0]] : views;
      const canvases = [], instances = [];
      let observer = null, longTasks = 0;
      try { observer = new PerformanceObserver((entries) => { longTasks += entries.getEntries().length; }); observer.observe({ type: "longtask", buffered: true }); } catch { /* unsupported by this browser */ }
      try {
        for (let index = 0; index < viewCount; index++) {
          const canvas = document.createElement("canvas"); canvas.width = 640; canvas.height = 360; canvas.style.cssText = "width:640px;height:360px;position:fixed;left:-10000px;top:0";
          document.body.append(canvas); const instance = new Renderer(); instance.initialize(canvas); instance.resize(640, 360); canvases.push(canvas); instances.push(instance);
        }
      } catch (error) {
        instances.forEach((instance) => instance.dispose()); canvases.forEach((canvas) => canvas.remove()); observer?.disconnect();
        return { renderer, entityCount, viewCount, unsupported: String(error?.message || error) };
      }
      const raf = () => new Promise((resolve) => requestAnimationFrame(resolve));
      for (let index = 0; index < 8; index++) { for (const [surface, instance] of instances.entries()) instance.renderFrame(activeViews[surface]); await raf(); }
      const cpuSamples = [], frameIntervals = []; let prior = performance.now();
      for (let index = 0; index < 36; index++) {
        await raf(); const started = performance.now();
        for (const [surface, instance] of instances.entries()) instance.renderFrame(activeViews[surface]);
        cpuSamples.push(performance.now() - started); const now = performance.now(); frameIntervals.push(now - prior); prior = now;
      }
      const percentile = (values, q) => { const sorted = [...values].sort((a, b) => a - b); return sorted[Math.min(sorted.length - 1, Math.floor((sorted.length - 1) * q))]; };
      const result = {
        renderer, entityCount, viewCount, view_kinds: activeViews.map((view) => view.kind), samples: cpuSamples.length,
        cpu_p50_ms: percentile(cpuSamples, .5), cpu_p95_ms: percentile(cpuSamples, .95), cpu_max_ms: Math.max(...cpuSamples),
        frame_p50_ms: percentile(frameIntervals, .5), frame_p95_ms: percentile(frameIntervals, .95),
        sustained_fps: 1000 / percentile(frameIntervals, .5), dropped_visual_frames: frameIntervals.filter((value) => value > 1000 / 30 * 1.5).length,
        long_tasks: longTasks, js_heap_bytes: performance.memory?.usedJSHeapSize ?? null,
        renderer_metrics: instances.map((instance) => instance.metrics()), device_pixel_ratio: devicePixelRatio,
      };
      instances.forEach((instance) => instance.dispose()); canvases.forEach((canvas) => canvas.remove()); observer?.disconnect();
      return result;
    }, { renderer, entityCount, viewCount });
    await testInfo.attach("world2d-render-metrics.json", { body: JSON.stringify(metrics, null, 2), contentType: "application/json" });
    console.log("WORLD2D_RENDER_BENCH", JSON.stringify(metrics));
    expect(metrics.unsupported).toBeUndefined();
    expect(metrics.samples).toBe(36);
  });
}
