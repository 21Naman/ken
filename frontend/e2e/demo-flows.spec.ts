import { expect, test } from "@playwright/test";

test("the dashboard creates household memory without demo controls", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("Create a household")).toBeVisible();
  await expect(page.getByRole("navigation", { name: "Application pages" })).toBeVisible();
});
