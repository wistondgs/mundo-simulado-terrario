// @ts-check
import { test, expect } from "@playwright/test";

test.describe("WorldStream live sandbox", () => {
  test("creates a real session, streams tick zero, and steps atomically", async ({ page }) => {
    await page.goto("/workspace/index.html"); await page.waitForTimeout(1200);
    const panel = page.locator('[data-panel="world"]'); await panel.locator("#w2dLive").click();
    await expect(panel.locator("#w2dMode")).toHaveText("LIVE SANDBOX"); await expect(panel.locator("#w2dConnection")).toHaveText("CONNECTED", { timeout: 10_000 });
    await expect(panel.locator("#w2dStepLabel")).toContainText("tick 0"); await panel.locator("#w2dNext").click();
    await expect(panel.locator("#w2dStepLabel")).toContainText("tick 1", { timeout: 10_000 });
    for (const kind of ["WORLD_TRUTH_PRIVILEGED", "AGENT_OBSERVATION", "OBSERVER_VIEW"]) {
      const status = panel.locator(`[data-status="${kind}"]`); await expect(status).toHaveText("SYNCHRONIZED");
      await expect(status).toHaveAttribute("data-view-tick", "1"); await expect(status).toHaveAttribute("data-frame-tick", "1");
    }
    await expect(panel).toContainText("NO DIRECT IDENTITY MAPPING"); await expect(panel.getByRole("button", { name: /scientific/i })).toHaveCount(0);
    await panel.locator("#w2dStart").click(); await page.waitForTimeout(120); await panel.locator("#w2dPause").click();
    await panel.locator("#w2dResume").click(); await page.waitForTimeout(80); await panel.locator("#w2dStop").click();
    await panel.locator("#w2dTrace").click(); await expect(panel.locator("#w2dMode")).toHaveText("TRACE PLAYBACK");
    await panel.locator("#w2dCompareLeft").fill("0"); await panel.locator("#w2dCompareRight").fill("1"); await panel.locator("#w2dCompare").click();
    await expect(panel.locator("#w2dDiff")).toContainText("DERIVED STATE DIFF · NOT CAUSAL");
    await panel.locator("#w2dBookmark").click(); await expect(panel.locator("#w2dMeta")).toContainText("Local bookmark");
    await panel.locator("#w2dNext").click(); // playback navigation cannot execute a command
  });

  test("stale revision conflicts and duplicate command IDs are backend-safe", async ({ request }) => {
    const sessionEnvelope = await (await request.get("/api/v1/session")).json(), auth = { "X-CSRF-Token": sessionEnvelope.data.csrf_token };
    const created = await (await request.post("/api/v1/world-stream/sessions", { headers: auth, data: { world_id: "D2", step_limit: 3 } })).json();
    const sid = created.session_id, command = { command_id: "e2e-idempotent", command: "STEP", expected_session_revision: 0 };
    const first = await request.post(`/api/v1/world-stream/sessions/${sid}/commands`, { headers: auth, data: command }); expect(first.ok()).toBeTruthy();
    const duplicate = await request.post(`/api/v1/world-stream/sessions/${sid}/commands`, { headers: auth, data: command }); expect(duplicate.ok()).toBeTruthy();
    const stale = await request.post(`/api/v1/world-stream/sessions/${sid}/commands`, { headers: auth, data: { command_id: "stale", command: "STEP", expected_session_revision: 0 } }); expect(stale.status()).toBe(409);
  });

  test("a delayed individual view is visibly STALE and never synchronized", async ({ page }) => {
    await page.goto("/workspace/index.html");
    const result = await page.evaluate(async () => {
      const { World2DPanel } = await import("/workspace/views/world2d.js");
      const host = document.createElement("div"); document.body.append(host);
      const panel = new World2DPanel({}); panel.render(host);
      const frame = { tick: 7, simulation_time: 7, views: [
        { kind: "WORLD_TRUTH_PRIVILEGED", tick: 7, status: "SYNCHRONIZED", payload: { grid_width: 1, grid_height: 1, objects: {}, agents: {} } },
        { kind: "AGENT_OBSERVATION", tick: 6, status: "SYNCHRONIZED", payload: { channels: [[[0]]], mask: [[true]] } },
        { kind: "OBSERVER_VIEW", tick: 7, status: "SYNCHRONIZED", payload: { world: { grid_width: 1, grid_height: 1, objects: {}, agents: {} } } },
      ] };
      panel.frames.set(7, frame); panel.presentedTick = 7; panel._paint();
      const statuses = Object.fromEntries([...host.querySelectorAll("[data-status]")].map((node) => [node.dataset.status, { status: node.textContent, viewTick: node.dataset.viewTick, frameTick: node.dataset.frameTick }]));
      for (const renderer of panel.renderers.values()) renderer.dispose(); host.remove();
      return statuses;
    });
    expect(result.WORLD_TRUTH_PRIVILEGED).toEqual({ status: "SYNCHRONIZED", viewTick: "7", frameTick: "7" });
    expect(result.OBSERVER_VIEW).toEqual({ status: "SYNCHRONIZED", viewTick: "7", frameTick: "7" });
    expect(result.AGENT_OBSERVATION).toEqual({ status: "STALE", viewTick: "6", frameTick: "7" });
  });
});
