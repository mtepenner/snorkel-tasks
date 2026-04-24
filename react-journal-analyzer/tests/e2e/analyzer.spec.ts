import { test, expect } from "@playwright/test";

test("home page loads and processes long-context document correctly", async ({ page }) => {
  await page.goto("/");
  
  // Wait for the app to parse the 50k+ text and render the output JSON block
  const statsOutput = page.locator('#stats-output');
  await expect(statsOutput).toBeVisible({ timeout: 10000 });

  const jsonText = await statsOutput.textContent();
  expect(jsonText).not.toBeNull();

  const stats = JSON.parse(jsonText as string);

  // Assertions against the generated mock file in test.sh
  expect(stats.citations).toBe(2001);
  expect(stats.keywords.quantum).toBe(2001);
  expect(stats.keywords.entanglement).toBe(2001);
  
  expect(stats.headers).toContain("Abstract");
  expect(stats.headers).toContain("Conclusion");
  expect(stats.headers.length).toBe(2);
});
