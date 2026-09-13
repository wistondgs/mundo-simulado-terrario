// @ts-check
import { test, expect } from "@playwright/test";

test.describe("WorldStream live sandbox", () => {
  test("creates a real session, streams tick zero, and steps atomically", async ({ page }) => {
    await page.goto("/workspace/index.html"); await page.waitForTimeout(1200);
    const panel = page.locator('[data-panel="world"]'); await panel.locator("#w2dLive").click();
    await expect(panel.locator("#w2dMode")).toHaveText("LIVE SANDBOX"); await expect(panel.locator("#w2dConnection")).toHaveText("CONNECTED", { timeout: 10_000 });
    await expect(panel.locator("#w2dStepLabel")).toContainText("tick 0"); await panel.locator("#w2dNext").click();
    await expect(panel.locator("#w2dStepLabel")).toContainText("tick 1", { timeout: 10_000 });
    for (const kind of ["WORLD_TRUTH_PRIVILEGED", "AGENT_OBSERVATION", "OBSERVER_VIEW"]) await expect(panel.locator(`[data-status="${kind}"]`)).toHaveText("SYNCHRONIZED");
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
});
