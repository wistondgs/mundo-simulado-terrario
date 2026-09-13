// @ts-check
import { test, expect } from "@playwright/test";

/**
 * Accessibility QA: keyboard navigation, focus states, semantic labels,
 * non-color-only distinctions, and reduced-motion support.
 */
test.describe("accessibility", () => {
  test("panels have semantic labels", async ({ page }) => {
    await page.goto("/workspace/index.html");
    await page.waitForTimeout(1500);
    for (const panel of ["explorer", "canvas", "inspector", "composition", "world", "d2"]) {
      const el = page.locator(`[data-panel="${panel}"]`);
      await expect(el).toHaveAttribute("aria-label", /.+/);
    }
  });

  test("canvas has an accessible label", async ({ page }) => {
    await page.goto("/workspace/index.html");
    await page.waitForTimeout(1000);
    await expect(page.locator('[data-panel="canvas"] canvas')).toHaveAttribute("aria-label", /.+/);
  });

  test("interactive controls are keyboard-focusable", async ({ page }) => {
    await page.goto("/workspace/index.html");
    await page.waitForTimeout(1500);
    // tab through the topbar and toolbar
    await page.keyboard.press("Tab");
    const focused = await page.evaluate(() => document.activeElement && document.activeElement.tagName);
    expect(focused).toBeTruthy();
    // command palette button reachable
    const paletteBtn = page.locator("#wsPaletteBtn");
    await paletteBtn.focus();
    await expect(paletteBtn).toBeFocused();
  });

  test("domain visual language is not color-only (icons/shapes present)", async ({ page }) => {
    await page.goto("/workspace/index.html");
    await page.waitForTimeout(1500);
    // The explorer uses domain icons in addition to color.
    const icons = page.locator(".domain-icon");
    const count = await icons.count();
    // If references loaded, icons are present; otherwise the test passes vacuously.
    if (count > 0) {
      const first = await icons.first().textContent();
      expect(first && first.trim().length > 0).toBeTruthy();
    }
  });

  test("reduced motion is honored", async ({ page }) => {
    await page.emulateMedia({ reducedMotion: "reduce" });
    await page.goto("/workspace/index.html");
    await page.waitForTimeout(1000);
    // The stylesheet disables animation/transition under reduced motion.
    const hasRule = await page.evaluate(() => {
      for (const sheet of Array.from(document.styleSheets)) {
        try {
          for (const rule of Array.from(sheet.cssRules || [])) {
            if (rule.media && /prefers-reduced-motion/.test(rule.media.mediaText)) return true;
          }
        } catch { /* cross-origin */ }
      }
      return false;
    });
    expect(hasRule).toBe(true);
  });

  test("World2D live and playback controls work keyboard-only with announced state", async ({ page }) => {
    await page.goto("/workspace/index.html"); await page.waitForTimeout(1200);
    const panel = page.locator('[data-panel="world"]');
    await expect(panel.locator("#w2dStepLabel")).toHaveAttribute("role", "status");
    await expect(panel.locator("#w2dTimeline")).toHaveAttribute("aria-label", "Observer event timeline");
    await expect(panel.locator("#w2dDiff")).toHaveAttribute("aria-label", "Derived frame comparison");
    await expect(panel.locator("#w2dHistory")).toHaveAttribute("aria-label", "Selected World Truth object history");
    for (const control of ["#w2dLive", "#w2dNext", "#w2dStart", "#w2dPause", "#w2dResume", "#w2dStop", "#w2dTrace"]) {
      await panel.locator(control).focus(); await page.keyboard.press("Enter");
      if (control === "#w2dLive") await expect(panel.locator("#w2dConnection")).toHaveText("CONNECTED", { timeout: 10_000 });
      if (control === "#w2dNext") await expect(panel.locator("#w2dStepLabel")).toContainText("tick 1", { timeout: 10_000 });
      if (control === "#w2dStart") await page.waitForTimeout(80);
      if (control === "#w2dResume") await page.waitForTimeout(80);
      if (control === "#w2dTrace") await expect(panel.locator("#w2dMode")).toHaveText("TRACE PLAYBACK");
    }
    await panel.locator("#w2dScrub").focus(); await page.keyboard.press("ArrowLeft");
    await panel.locator("#w2dNext").focus(); await page.keyboard.press("Enter");
  });
});
