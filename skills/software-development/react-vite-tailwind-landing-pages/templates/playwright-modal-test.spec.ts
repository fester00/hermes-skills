import { test, expect } from "@playwright/test";

/**
 * Starter Playwright test for scrollable product modals on a React + Vite landing page.
 * Copy into `tests/` and adjust selectors to match your markup.
 */

test.describe("Product modal", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    // Wait for loading screen to finish and main content to be visible
    await page.waitForSelector("main", { timeout: 15000 });
    await page.waitForFunction(() => {
      const root = document.getElementById("root");
      const main = root?.querySelector("main");
      return main !== null && getComputedStyle(main).opacity === "1";
    }, { timeout: 15000 });
  });

  // JS click avoids Playwright auto-scroll-to-visible behavior that can shift
  // window.scrollY in tests while still exercising the real React click handler.
  const openModal = async (page: any) => {
    await page.evaluate(() => {
      const btn = document.querySelector("button[title='Подробнее']") as HTMLButtonElement;
      btn?.click();
    });
    await page.waitForTimeout(200);
  };

  test("opens by clicking product info button", async ({ page }) => {
    const infoButton = page.locator("button[title='Подробнее']").first();
    await expect(infoButton).toBeVisible();
    await openModal(page);
    await expect(page.getByText("Характеристики").first()).toBeVisible();
  });

  test("closes by clicking X button", async ({ page }) => {
    await openModal(page);
    await expect(page.getByText("Характеристики").first()).toBeVisible();

    const closeButton = page.locator("[role='dialog'] button").first();
    await expect(closeButton).toBeVisible();
    await closeButton.click();

    await expect(page.getByText("Характеристики").first()).not.toBeVisible();
  });

  test("closes by pressing Escape key", async ({ page }) => {
    await openModal(page);
    await expect(page.getByText("Характеристики").first()).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(page.getByText("Характеристики").first()).not.toBeVisible();
  });

  test("closes by clicking outside", async ({ page }) => {
    await openModal(page);
    await expect(page.getByText("Характеристики").first()).toBeVisible();
    await page.locator("[data-testid='modal-backdrop']").first().click({ position: { x: 10, y: 10 } });
    await expect(page.getByText("Характеристики").first()).not.toBeVisible();
  });

  test("modal scrolls independently from page and restores scroll on close", async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 600 });
    await page.evaluate(() => window.scrollTo(0, 500));
    await page.waitForTimeout(100);
    const pageScrollBefore = await page.evaluate(() => window.scrollY);
    expect(pageScrollBefore).toBe(500);

    await openModal(page);
    const modal = page.locator("[role='dialog']").first();
    await expect(modal).toBeVisible();

    // Internal modal scroll works
    await modal.evaluate((el) => el.scrollTo(0, 200));
    await page.waitForTimeout(100);
    expect(await modal.evaluate((el) => el.scrollTop)).toBeGreaterThan(0);

    // Background stays locked
    expect(await page.evaluate(() => document.body.style.overflow)).toBe("hidden");
    await page.mouse.wheel(0, -500);
    await page.waitForTimeout(200);
    expect(await page.evaluate(() => window.scrollY)).toBe(pageScrollBefore);

    // Close and restore scroll
    await page.keyboard.press("Escape");
    await expect(page.getByText("Характеристики").first()).not.toBeVisible();
    await page.waitForFunction(() => document.body.style.overflow !== "hidden", { timeout: 5000 });
    await page.waitForTimeout(300);
    expect(await page.evaluate(() => window.scrollY)).toBe(pageScrollBefore);
  });
});
