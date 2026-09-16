// @ts-check
import { test, expect } from "@playwright/test";

/** The workspace must expose one focused task context at a time, without dropping its instruments. */
test("workspace contexts provide navigable, focused instrument surfaces", async ({ page }) => {
  await page.goto("/workspace/index.html");
  await expect(page.getByRole("navigation", { name: "Contextos de trabajo" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Guía de uso" })).toHaveAttribute("href", "/?view=manual");

  const expected = {
    explore: ["explorer", "canvas", "inspector", "composition"],
    design: ["operational-hypergraph", "d2"],
    execute: ["execution", "scientific-world"],
    world: ["world"],
  };

  for (const [context, panels] of Object.entries(expected)) {
    await page.locator(`[data-context-target="${context}"]`).click();
    await expect(page.locator(`[data-context-page="${context}"]`)).toBeVisible();
    await expect(page).toHaveURL(new RegExp(`#context=${context}$`));
    for (const panel of panels) await expect(page.locator(`[data-panel="${panel}"]`)).toBeVisible();
  }

  await page.locator('[data-context-target="world"]').click();
  await page.locator('[data-panel="world"] [data-action="fullscreen"]').click();
  await expect(page.locator('[data-panel="world"]')).toHaveClass(/ws-fullscreen/);
  await page.locator('[data-panel="world"] [data-action="fullscreen"]').click();
  await expect(page.locator('[data-panel="world"]')).not.toHaveClass(/ws-fullscreen/);

  await page.locator('[data-context-target="explore"]').focus();
  await page.keyboard.press("ArrowRight");
  await expect(page.locator('[data-context-page="design"]')).toBeVisible();
});
