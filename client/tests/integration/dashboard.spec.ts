import { test, expect } from '@playwright/test';
import { DashboardPage } from '../pages/DashboardPage';
import { TEST_URLS } from '../utils/testData';
import { loginAs, clearAuth } from '../utils/auth';

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Clear authentication state before each test
    await clearAuth(page);
  });

  test('dashboard loads correctly for admin user @regression', async ({ page }) => {
    // Login as admin
    await loginAs(page, 'ADMIN');

    const dashboardPage = new DashboardPage(page);
    await dashboardPage.expectDashboardPage();
    await dashboardPage.waitForLoad();
  });

  test('dashboard loads correctly for regular user', async ({ page }) => {
    // Login as regular user
    await loginAs(page, 'USER');

    const dashboardPage = new DashboardPage(page);
    await dashboardPage.expectDashboardPage();
    await dashboardPage.waitForLoad();
  });

  test('dashboard shows user-specific content', async ({ page }) => {
    // Login as admin
    await loginAs(page, 'ADMIN');

    const dashboardPage = new DashboardPage(page);
    await dashboardPage.expectDashboardPage();

    // Check for dashboard title or content
    await expect(dashboardPage.title).toBeVisible();
  });

  test('dashboard navigation works correctly @regression', async ({ page }) => {
    await loginAs(page, 'ADMIN');

    // Test navigation within dashboard
    await page.goto(TEST_URLS.DASHBOARD);
    await expect(page).toHaveURL(TEST_URLS.DASHBOARD);

    const dashboardPage = new DashboardPage(page);
    await dashboardPage.expectDashboardPage();
  });

  test('dashboard handles page refresh correctly', async ({ page }) => {
    await loginAs(page, 'ADMIN');

    const dashboardPage = new DashboardPage(page);
    await dashboardPage.expectDashboardPage();

    // Refresh the page
    await page.reload();

    // Should still be on dashboard (if session is maintained)
    await dashboardPage.expectDashboardPage();
  });

  test('dashboard redirects to login when not authenticated', async ({ page }) => {
    // Try to access dashboard without authentication
    await page.goto(TEST_URLS.DASHBOARD);

    // Should be redirected to login
    await expect(page).toHaveURL(TEST_URLS.LOGIN);
  });
});
