// @ts-check
import { test, expect } from "@playwright/test";

test.describe("human review center", () => {
  test("shows the local governance boundary and runs the non-executing D2 check", async ({ page }) => {
    await page.goto("/review-center.html");
    await expect(page.getByRole("heading", { name: "Centro de revisión humana" })).toBeVisible();
    await expect(page.getByText("No ejecución · No evidencia")).toBeVisible();

    await page.getByRole("button", { name: "Comprobar D2" }).click();
    await expect(page.locator("#d2Result")).toContainText("D2 válido");
    await expect(page.locator("#d2Result")).toContainText("sin agente, evidencia ni resultados");
  });
});
