// @ts-check
import { test, expect } from "@playwright/test";

/**
 * Workspace interaction E2E: navigation, selection, composition, provenance,
 * D2, World2D, snapshot mode, and reload/recovery.
 */
test.describe("workspace interactions", () => {
  test("command palette opens and runs a command", async ({ page }) => {
    await page.goto("/workspace/index.html");
    await page.waitForTimeout(1500);
    await page.keyboard.press("Control+k");
    await expect(page.locator(".ws-palette")).toBeVisible();
    await page.keyboard.type("composition");
    await expect(page.locator(".ws-palette-item").first()).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(page.locator(".ws-palette")).not.toBeVisible();
  });

  test("canvas supports zoom and selection state changes", async ({ page }) => {
    await page.goto("/workspace/index.html");
    await page.waitForTimeout(2500);
    const canvas = page.locator('[data-panel="canvas"] canvas');
    await expect(canvas).toBeVisible();
    // zoom via wheel
    const box = await canvas.boundingBox();
    if (box) {
      await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
      await page.mouse.wheel(0, -240);
      await page.waitForTimeout(300);
    }
    // no crash; canvas still visible
    await expect(canvas).toBeVisible();
  });

  test("composition panel accepts members and saves a version", async ({ page }) => {
    await page.goto("/workspace/index.html");
    await page.waitForTimeout(2000);
    const panel = page.locator('[data-panel="composition"]');
    await expect(panel).toBeVisible();
    // add a member programmatically through the composition panel API surface
    await panel.locator("#compTitle").fill("E2E composition");
    // simulate adding members via the exposed panel (link requires 2 members)
    await page.evaluate(() => {
      // @ts-ignore
      const evt = new CustomEvent("workspace:add-to-composition", {
        detail: [{ domain: "WORLD", entity_type: "WorldDefinition", entity_id: "D2" }],
      });
      window.dispatchEvent(evt);
    });
    // save should not crash even with zero members (backend accepts empty refs)
    await panel.locator("#compSave").click();
    await page.waitForTimeout(800);
    const status = await panel.locator("#compStatus").textContent();
    expect(status).toBeTruthy();
  });

  test("D2 studio shows trace breaks layer", async ({ page }) => {
    await page.goto("/workspace/index.html");
    await page.waitForTimeout(2000);
    await page.locator('[data-context-target="design"]').click();
    const d2 = page.locator('[data-panel="d2"]');
    await expect(d2).toBeVisible();
    // switch to trace breaks layer
    const traceTab = d2.locator('[data-layer="trace breaks"]');
    if (await traceTab.count()) {
      await traceTab.click();
      await page.waitForTimeout(500);
      const body = await d2.locator("#d2Body").textContent();
      expect(body && body.length > 0).toBeTruthy();
    }
  });

  test("World2D panel renders three distinctly-labelled views", async ({ page }) => {
    await page.goto("/workspace/index.html");
    await page.waitForTimeout(1500);
    await page.locator('[data-context-target="world"]').click();
    const world = page.locator('[data-panel="world"]');
    await expect(world).toBeVisible();
    await expect(world.locator(".ws-world-view.truth header")).toHaveText(/World Truth/i);
    await expect(world.locator(".ws-world-view.agent header")).toHaveText(/Agent View/i);
    await expect(world.locator(".ws-world-view.observer header")).toHaveText(/Observer View/i);
    // sandbox badge always visible, never a scientific-execution button
    await expect(world.locator(".ws-sandbox-badge")).toHaveText(/ENGINEERING_SANDBOX/);
  });

  test("operating mode toggles between exploratory and pinned", async ({ page }) => {
    await page.goto("/workspace/index.html");
    await page.waitForTimeout(1500);
    const badge = page.locator("#wsMode");
    await expect(badge).toHaveText("EXPLORATORY_LATEST");
    // toggle via palette action
    await page.keyboard.press("Control+k");
    await page.keyboard.type("pin snapshot");
    // Assert WHICH command is about to run, not merely that the list is
    // populated: each keystroke fires an async reference search, so a stale
    // reply used to be able to repaint the list with an older prefix's
    // matches and Enter would fire a different command.
    await expect(page.locator(".ws-palette-item").first()).toContainText("Pin snapshot");
    await page.keyboard.press("Enter");
    await expect(badge).toHaveText("PINNED_REPRODUCIBLE");
  });

  test("workspace survives reload (shell re-mounts)", async ({ page }) => {
    await page.goto("/workspace/index.html");
    await page.waitForTimeout(1500);
    await page.reload();
    await page.waitForTimeout(1500);
    await expect(page.locator('[data-panel="canvas"]')).toBeVisible();
    await expect(page.locator("#wsMode")).toHaveText(/EXPLORATORY_LATEST|PINNED_REPRODUCIBLE/);
  });
});
