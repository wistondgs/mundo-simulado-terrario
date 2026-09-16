// @ts-check
import { test, expect } from "@playwright/test";

test.describe("Compose to preregistration handoff", () => {
  test("keeps exact durable version IDs in the human workflow without asking for manual copying", async ({ page }) => {
    await page.goto("/");
    await page.evaluate(() => {
      sessionStorage.setItem("terrario:experiment-draft-version", "version-experiment-exact");
      sessionStorage.setItem("terrario:trial-matrix-version", "version-matrix-exact");
    });
    await page.reload();

    await page.getByRole("button", { name: "Compose", exact: true }).click();
    await expect(page.getByRole("button", { name: "Guardar ExperimentDraft durable" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Crear TrialMatrix durable" })).toBeVisible();

    await page.getByRole("button", { name: "Preregistros", exact: true }).click();
    await page.getByRole("button", { name: "Nuevo", exact: true }).click();
    await expect(page.locator('input[name="experiment_draft_version_id"]')).toHaveValue("version-experiment-exact");
    await expect(page.locator('input[name="trial_matrix_version_id"]')).toHaveValue("version-matrix-exact");
  });
});
