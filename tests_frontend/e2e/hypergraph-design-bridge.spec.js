// @ts-check
import { test, expect } from "@playwright/test";

test.describe("hypergraph to design bridge", () => {
  test("opens the portfolio design bound by the backend, not by a guessed graph key", async ({ page }) => {
    await page.goto("/");
    await page.getByRole("button", { name: "Hipergrafo", exact: true }).click();
    await page.locator("#graphHyperedges").check();
    await expect(page.locator("#graphCount")).toContainText("8 NODES");

    const canvas = page.locator("#graphCanvas");
    // The filtered candidate grid always places its first node at (34, 30).
    await canvas.click({ position: { x: 34, y: 30 } });
    await expect(page.getByRole("button", { name: "Abrir diseño derivado" })).toBeVisible();
    await page.getByRole("button", { name: "Abrir diseño derivado" }).click();

    await expect(page.locator("#design")).toHaveClass(/active/);
    await expect(page.locator("#designDetail")).toContainText("HYPERCAND-01");
    await expect(page.getByRole("button", { name: "Usar como procedencia en Compose" })).toBeVisible();
  });
});
