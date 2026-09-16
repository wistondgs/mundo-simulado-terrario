import { test, expect } from "@playwright/test";

async function seek(page, sequence) {
  await page.locator("#d2FixtureSeek").evaluate((node, value) => {
    node.value = String(value);
    node.dispatchEvent(new Event("input", { bubbles: true }));
  }, sequence);
}

test.describe("D2 canonical visual validation fixture", () => {
  test("renders lifecycle, binding scope, and history-independent seek", async ({ page }) => {
    const errors = [];
    page.on("pageerror", (error) => errors.push(String(error)));
    await page.goto("/workspace/index.html");
    await page.locator('[data-context-target="design"]').click();
    await page.getByRole("button", { name: "Open D2 visual validation fixture" }).click();
    await expect(page.locator("#d2FixtureTick")).toHaveText(/tick 0 · frame 0 · INITIAL/);
    await expect(page.locator("[data-d2-errors]")).toHaveText("NO_ERROR");

    await seek(page, 4);
    await expect(page.locator("#d2FixtureTick")).toHaveText(/tick 4 · frame 4 · OCCLUDED/);
    await expect(page.locator('[data-d2-object-id="0"]')).toHaveText(/OCCLUDED · occluded/);

    await seek(page, 5);
    await expect(page.locator('[data-d2-object-id="0"]')).toHaveText(/VISIBLE · visible_again/);
    await expect(page.locator("[data-d2-semantic-frame]")).toContainText("NOT_APPLICABLE");

    await seek(page, 10);
    const directBinding = await page.locator("[data-d2-semantic-frame]").innerText();
    await expect(page.locator("[data-d2-errors]")).toContainText("BINDING_ERROR");
    await expect(page.locator("[data-d2-semantic-frame]")).toContainText("INSTRUMENT_SELF_AUDIT_NOT_AGENT_EVIDENCE");

    await seek(page, 3);
    await expect(page.locator("[data-d2-errors]")).toHaveText("NO_ERROR");
    await expect(page.locator('[data-d2-object-id="0"]')).toHaveText(/OCCLUDED/);
    await seek(page, 10);
    expect(await page.locator("[data-d2-semantic-frame]").innerText()).toBe(directBinding);

    await page.setViewportSize({ width: 900, height: 700 });
    await expect(page.locator("#d2FixtureTick")).toHaveText(/tick 10 · frame 10/);
    expect(errors).toEqual([]);
  });
});
