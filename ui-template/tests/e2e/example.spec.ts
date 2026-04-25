import { test, expect } from "@playwright/test";

/**
 * Example E2E test. The fixture page is served by webServer in playwright.config.ts.
 * For real tasks, point webServer to your app (e.g. npm run dev from /app) and update assertions.
 */
test("home page loads and shows expected content", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /hello, ui task/i })).toBeVisible();
});

test("page has a title", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/UI task/);
});
