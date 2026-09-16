// @ts-check
import { test, expect } from "@playwright/test";

test.describe("human entry points", () => {
  test("the manual routes a reviewer to the hypergraph and Composer", async ({ page }) => {
    await page.goto("/");

    await page.getByRole("button", { name: "Manual", exact: true }).click();
    await expect(page.locator("#manual h1")).toHaveText("Manual de uso");
    await expect(page.locator("#manual")).toContainText("Del hipergrafo a un diseño reproducible");

    await page.locator('#manual [data-go-view="graph"]').click();
    await expect(page.locator("#graph")).toHaveClass(/active/);
    await expect(page.locator("#graphCanvas")).toBeVisible();

    await page.getByRole("button", { name: "Manual", exact: true }).click();
    await page.locator('#manual [data-go-view="composer"]').click();
    await expect(page.locator("#composer")).toHaveClass(/active/);
    await expect(page.locator("#experimentSource")).toBeVisible();
  });
});
