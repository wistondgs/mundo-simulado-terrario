// @ts-check
import { test, expect } from "@playwright/test";

const REVIEW_ID = "review-82c0a332b5524f1f9907aa0d5ce2c067";
const DRAFT_HASH = "ac03a38f909efab73cea98efa1cc439215464d4b43ab2bc07dcb8f0150b21770";

test.describe("CL-7 human review entry", () => {
  test("binds the pending design decision to the exact draft and requires a ceremony", async ({ page }) => {
    await page.goto("/review-center.html");
    const review = page.locator("article.review.pending", { hasText: REVIEW_ID });
    await expect(review).toContainText(DRAFT_HASH);
    await expect(review.getByRole("button", { name: "Registrar decisión auditada" })).toBeDisabled();

    await review.locator("textarea").fill("I reviewed the exact version and will decide explicitly.");
    await expect(review.getByRole("button", { name: "Registrar decisión auditada" })).toBeDisabled();
    await review.locator("input").fill(`REVIEW ${DRAFT_HASH.slice(0, 12)}`);
    await expect(review.getByRole("button", { name: "Registrar decisión auditada" })).toBeEnabled();
  });
});
