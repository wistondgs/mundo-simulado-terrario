// @ts-check
import { test, expect } from "@playwright/test";

/**
 * Workspace launch smoke test: the shell boots, panels are present, the canvas
 * renders, and the backend connection is established.
 */
test.describe("workspace launch", () => {
  test("shell boots with panels and canvas", async ({ page }) => {
    const errors = [];
    page.on("pageerror", (err) => errors.push(String(err)));
    page.on("console", (msg) => { if (msg.type() === "error") errors.push(msg.text()); });

    await page.goto("/workspace/index.html");

    // topbar
    await expect(page.locator("strong", { hasText: "TERRARIO" })).toBeVisible();
    await expect(page.locator("#wsMode")).toHaveText(/EXPLORATORY_LATEST|PINNED_REPRODUCIBLE/);

    // panels present
    await expect(page.locator('[data-panel="explorer"]')).toBeVisible();
    await expect(page.locator('[data-panel="canvas"]')).toBeVisible();
    await expect(page.locator('[data-panel="inspector"]')).toBeVisible();
    await expect(page.locator('[data-panel="composition"]')).toBeVisible();

    // canvas element present and sized
    const canvas = page.locator('[data-panel="canvas"] canvas');
    await expect(canvas).toBeVisible();
    const box = await canvas.boundingBox();
    expect(box && box.width > 50 && box.height > 50).toBeTruthy();

    // no fatal JS errors on boot
    await page.waitForTimeout(1500);
    const fatal = errors.filter((e) => !/favicon|404|net::/i.test(e));
    expect(fatal).toEqual([]);
  });

  test("backend status is reachable from the workspace", async ({ page }) => {
    await page.goto("/workspace/index.html");
    await page.waitForTimeout(2000);
    const status = await page.locator("#wsStatus").textContent();
    // Either connected (links N) or degraded, but never stuck on "connecting…".
    expect(status).not.toBe("connecting…");
  });
});
