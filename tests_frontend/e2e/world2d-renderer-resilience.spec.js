// @ts-check
import { test, expect } from "@playwright/test";

test("WebGL context loss falls back locally and high-density picking retains identity", async ({ page }) => {
  await page.goto("/workspace/index.html");
  const result = await page.evaluate(async () => {
    const { Canvas2DRenderer, ResilientRenderer } = await import("/workspace/world2d/renderers.js");
    const canvas = document.createElement("canvas"); document.body.append(canvas);
    const view = { kind: "WORLD_TRUTH_PRIVILEGED", payload: { grid_width: 2, grid_height: 2, objects: { x: { object_id: "x", pos: [1, 1], properties: {} } }, agents: {} } };
    const fallbacks = [], resilient = new ResilientRenderer();
    resilient.initialize(canvas, { preferWebGL: true, onFallback: (error) => fallbacks.push(error.message) }); resilient.resize(100, 100); resilient.renderFrame(view);
    const before = resilient.metrics().renderer;
    canvas.dispatchEvent(new Event("webglcontextlost", { cancelable: true })); resilient.renderFrame(view);
    const after = resilient.metrics().renderer; resilient.dispose(); canvas.remove();

    const denseCanvas = document.createElement("canvas"); document.body.append(denseCanvas);
    const objects = {}, side = 100;
    for (let index = 0; index < 10_000; index++) { const row = Math.floor(index / side), column = index % side; objects[`object-${index}`] = { object_id: `object-${index}`, pos: [row, column], properties: {} }; }
    const dense = new Canvas2DRenderer(); dense.initialize(denseCanvas); dense.resize(500, 500, 2); dense.renderFrame({ kind: "WORLD_TRUTH_PRIVILEGED", payload: { grid_width: side, grid_height: side, objects, agents: {} } });
    const picked = dense.pick(62, 367)?.object_id; dense.dispose(); denseCanvas.remove();
    return { before, after, fallbacks, picked };
  });
  expect(result.before).toBe("WebGL2");
  expect(result.after).toBe("Canvas2D");
  expect(result.fallbacks).toContain("WEBGL_CONTEXT_LOST");
  expect(result.picked).toBe("object-7312");
});
