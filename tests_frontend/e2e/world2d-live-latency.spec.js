// @ts-check
import { test, expect } from "@playwright/test";
import { performance } from "node:perf_hooks";

const percentile = (values, quantile) => {
  const ordered = [...values].sort((left, right) => left - right);
  return ordered[Math.min(ordered.length - 1, Math.floor((ordered.length - 1) * quantile))];
};
const summary = (values) => ({ samples: values.length, p50_ms: percentile(values, .5), p95_ms: percentile(values, .95), max_ms: Math.max(...values) });

/**
 * Local end-to-end latency. The single monotonic Node clock brackets browser
 * input and the observed DOM state, so it deliberately includes browser, HTTP,
 * sandbox, SSE, reducer and rAF presentation without comparing host clocks.
 */
test("World2D live command-to-visible latency uses the real sandbox and SSE", async ({ page }, testInfo) => {
  test.setTimeout(120_000);
  await page.goto("/workspace/index.html"); await page.waitForTimeout(1000);
  await page.locator('[data-context-target="world"]').click();
  const panel = page.locator('[data-panel="world"]'), samples = { step: [], start_to_visible: [], pause_ack: [], resume_to_visible: [] };
  const tick = async () => Number((await panel.locator("#w2dStepLabel").textContent()).match(/tick (\d+)/)?.[1]);
  for (let index = 0; index < 10; index++) {
    await panel.locator("#w2dLive").click();
    await expect(panel.locator("#w2dConnection")).toHaveText("CONNECTED", { timeout: 10_000 });
    await expect(panel.locator("#w2dStepLabel")).toContainText("tick 0", { timeout: 10_000 });
    let began = performance.now(); await panel.locator("#w2dNext").click();
    await expect(panel.locator("#w2dStepLabel")).toContainText("tick 1", { timeout: 10_000 }); samples.step.push(performance.now() - began);
    began = performance.now(); await panel.locator("#w2dStart").click();
    await expect.poll(tick, { timeout: 10_000 }).toBeGreaterThan(1); samples.start_to_visible.push(performance.now() - began);
    began = performance.now(); await panel.locator("#w2dPause").click();
    await expect(panel.locator("#w2dRunState")).toHaveText("PAUSED", { timeout: 10_000 }); samples.pause_ack.push(performance.now() - began);
    const beforeResume = await tick(); began = performance.now(); await panel.locator("#w2dResume").click();
    await expect.poll(tick, { timeout: 10_000 }).toBeGreaterThan(beforeResume); samples.resume_to_visible.push(performance.now() - began);
    await panel.locator("#w2dStop").click(); await expect(panel.locator("#w2dRunState")).toHaveText("TERMINATED", { timeout: 10_000 });
  }
  const metrics = { classification: "LOCAL_END_TO_END_ENGINEERING_BENCHMARK", clock: "node:perf_hooks monotonic; browser input through visible DOM state", operations: Object.fromEntries(Object.entries(samples).map(([name, values]) => [name, summary(values)])) };
  await testInfo.attach("world2d-live-latency.json", { body: JSON.stringify(metrics, null, 2), contentType: "application/json" });
  console.log("WORLD2D_LIVE_LATENCY", JSON.stringify(metrics));
  for (const values of Object.values(samples)) expect(values).toHaveLength(10);
});
