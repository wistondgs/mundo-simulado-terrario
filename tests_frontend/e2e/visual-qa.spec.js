// @ts-check
import { test, expect } from "@playwright/test";

/**
 * Visual QA: stable screenshot baselines for the workspace shell, graph,
 * inspector, D2 Studio, and World2D. Not all tests rely on screenshots; these
 * are structural baselines only.
 */
test.describe("visual QA", () => {
  test("workspace shell baseline", async ({ page }) => {
    await page.goto("/workspace/index.html");
    await page.waitForTimeout(2000);
    await expect(page).toHaveScreenshot("workspace-shell.png", {
      maxDiffPixelRatio: 0.02,
    });
  });

  test("world2d panel baseline", async ({ page }) => {
    await page.goto("/workspace/index.html");
    await page.waitForTimeout(1500);
    await page.locator('[data-context-target="world"]').click();
    const world = page.locator('[data-panel="world"]');
    await expect(world).toHaveScreenshot("world2d-panel.png", {
      maxDiffPixelRatio: 0.02,
    });
  });

  test("d2 studio baseline", async ({ page }) => {
    await page.goto("/workspace/index.html");
    await page.waitForTimeout(1500);
    await page.locator('[data-context-target="design"]').click();
    const d2 = page.locator('[data-panel="d2"]');
    await expect(d2).toHaveScreenshot("d2-studio.png", {
      maxDiffPixelRatio: 0.02,
    });
  });
});
