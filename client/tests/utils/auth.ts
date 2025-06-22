import { Page, expect } from '@playwright/test';
import { TEST_USERS, TEST_URLS } from './testData';

export type UserType = keyof typeof TEST_USERS;

/**
 * Clear authentication state from the browser
 */
export async function clearAuth(page: Page) {
  await page.context().clearCookies();
  await page.goto('/');
  await page.evaluate(() => {
    localStorage.clear();
    sessionStorage.clear();
  });
}

/**
 * Clear authentication state but preserve remembered email
 */
export async function clearAuthKeepRemembered(page: Page) {
  await page.context().clearCookies();
  await page.goto('/');
  await page.evaluate(() => {
    // Save remembered email before clearing
    const rememberedEmail = localStorage.getItem('rememberedEmail');
    localStorage.clear();
    sessionStorage.clear();
    // Restore remembered email if it existed
    if (rememberedEmail) {
      localStorage.setItem('rememberedEmail', rememberedEmail);
    }
  });
}

/**
 * Login as a specific user type
 */
export async function loginAs(page: Page, userType: UserType) {
  const user = TEST_USERS[userType];

  // Clear any existing auth state
  await clearAuth(page);

  // Navigate to login page
  await page.goto(TEST_URLS.LOGIN);

  // Wait for login form to be visible
  await expect(page.locator('form')).toBeVisible();

  // Debug: Log the current page content
  console.log('Current URL:', page.url());

  // Wait for input fields to be visible and enabled
  await expect(page.locator('input#email')).toBeVisible();
  await expect(page.locator('input#password')).toBeVisible();

  // Fill credentials with more explicit waits
  await page.locator('input#email').fill(user.email);
  await page.locator('input#password').fill(user.password);

  // Verify values were filled correctly
  await expect(page.locator('input#email')).toHaveValue(user.email);
  await expect(page.locator('input#password')).toHaveValue(user.password);

  // Submit form and wait for navigation
  await Promise.all([
    page.waitForURL(TEST_URLS.DASHBOARD, { timeout: 15000 }),
    page.locator('button[type="submit"]').click()
  ]);
}

/**
 * Check if user is authenticated by checking for dashboard access
 */
export async function isAuthenticated(page: Page): Promise<boolean> {
  try {
    await page.goto(TEST_URLS.DASHBOARD);
    await page.waitForURL(TEST_URLS.DASHBOARD, { timeout: 5000 });
    return true;
  } catch {
    return false;
  }
}

/**
 * Logout user (if logout functionality exists)
 */
export async function logout(page: Page) {
  try {
    // Try to find and click logout button
    const logoutButton = page.locator('button:has-text("Logout"), button:has-text("Sign Out"), [data-testid="logout"]');
    if (await logoutButton.isVisible()) {
      await logoutButton.click();
    }
  } catch {
    // If logout button not found, clear auth manually
    await clearAuth(page);
  }
}
