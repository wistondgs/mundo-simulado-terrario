// @ts-check
import { test, expect } from "@playwright/test";
import { execFileSync } from "node:child_process";

/**
 * The human review ceremony gate.
 *
 * This test seeds its own pending EXPERIMENT_DESIGN review in the E2E data
 * root.  It previously hard-coded the review id and design hash of the real
 * CL-7 design, so it only passed while the suite ran against the live
 * `.terrario` -- and it typed into a real pending human-review form.  It also
 * broke the moment the scientist actually decided that review.
 */
function seedPendingReview() {
  const dataRoot = process.env.TERRARIO_E2E_DATA_ROOT;
  if (!dataRoot) throw new Error("TERRARIO_E2E_DATA_ROOT is unset; refusing to seed into the live .terrario");
  const out = execFileSync(".venv/bin/python", ["scripts/seed_pending_design_review_e2e.py", dataRoot],
    { encoding: "utf8", env: { ...process.env, PYTHONPATH: "." } });
  return JSON.parse(out.trim().split("\n").pop());
}

test.describe("CL-7 human review entry", () => {
  test("binds the pending design decision to the exact draft and requires a ceremony", async ({ page }) => {
    const seeded = seedPendingReview();

    await page.goto("/review-center.html");
    const review = page.locator("article.review.pending", { hasText: seeded.review_id });
    await expect(review).toContainText(seeded.artifact_hash);
    const record = review.getByRole("button", { name: "Registrar decisión auditada" });
    await expect(record).toBeDisabled();

    await review.locator("textarea").fill("I reviewed the exact version and will decide explicitly.");
    await expect(record).toBeDisabled();
    await review.locator("input").fill(`REVIEW ${seeded.artifact_hash.slice(0, 12)}`);
    await expect(record).toBeEnabled();
  });

  test("shows what is being decided, including what the metric does not measure", async ({ page }) => {
    // The gate is only a gate if the reviewer can see the object.  This card
    // used to show five identifiers and a free-text reason -- no scenario, no
    // seeds, no metric semantics -- and the reviewer's recorded answer was
    // "no le entiendo".
    const seeded = seedPendingReview();
    await page.goto("/review-center.html");
    const review = page.locator("article.review.pending", { hasText: seeded.review_id });

    const design = review.locator("details.design");
    await expect(design).toContainText("Qué estás decidiendo");
    await expect(design).toContainText("Semillas de mundo");
    await expect(design).toContainText("Repeticiones");

    // The metric block must state the construct AND its declared limits.
    const metric = design.locator("ul.metrics > li").first();
    await expect(metric).toContainText("Mide");
    await expect(metric).toContainText("NO mide");
    await expect(metric.locator("ul.not-measured li").first()).not.toBeEmpty();
  });
});
