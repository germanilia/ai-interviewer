import { test, expect } from '@playwright/test';
import { DashboardPage } from '../pages/DashboardPage';
import { TEST_URLS } from '../utils/testData';
import { loginAs, clearAuth } from '../utils/auth';

test.describe('Dashboard Overview - Unified Interview Management Dashboard', () => {
  let dashboardPage: DashboardPage;

  test.beforeEach(async ({ page }) => {
    await clearAuth(page);
    dashboardPage = new DashboardPage(page);
  });

  test.describe('Basic Dashboard Functionality', () => {
    test('dashboard loads correctly for admin user @regression', async ({ page }) => {
      await loginAs(page, 'ADMIN');
      await dashboardPage.expectDashboardPage();
      await dashboardPage.waitForLoad();
    });

    test('dashboard loads correctly for regular user', async ({ page }) => {
      await loginAs(page, 'USER');
      await dashboardPage.expectDashboardPage();
      await dashboardPage.waitForLoad();
    });

    test('dashboard shows user-specific content', async ({ page }) => {
      await loginAs(page, 'ADMIN');
      await dashboardPage.expectDashboardPage();
      await expect(dashboardPage.title).toBeVisible();
    });

    test('dashboard navigation works correctly @regression', async ({ page }) => {
      await loginAs(page, 'ADMIN');
      await page.goto(TEST_URLS.DASHBOARD);
      await expect(page).toHaveURL(TEST_URLS.DASHBOARD);
      await dashboardPage.expectDashboardPage();
    });

    test('dashboard handles page refresh correctly', async ({ page }) => {
      await loginAs(page, 'ADMIN');
      await dashboardPage.expectDashboardPage();
      await page.reload();
      await dashboardPage.expectDashboardPage();
    });

    test('dashboard redirects to login when not authenticated', async ({ page }) => {
      await page.goto(TEST_URLS.DASHBOARD);
      await expect(page).toHaveURL(TEST_URLS.LOGIN);
    });
  });

  test.describe('Interview Management Features - Ready for Implementation', () => {
    test.beforeEach(async ({ page }) => {
      await loginAs(page, 'ADMIN');
    });

    test('should display enhanced dashboard content', async () => {
      await dashboardPage.goto();
      await dashboardPage.waitForLoad();

      // Basic dashboard should load
      await dashboardPage.expectDashboardPage();
      await expect(dashboardPage.title).toBeVisible();

      // TODO: Add interview statistics cards when implemented
      // await expect(page.getByTestId('total-candidates-card')).toBeVisible();
      // await expect(page.getByTestId('active-interviews-card')).toBeVisible();
      // await expect(page.getByTestId('completed-interviews-card')).toBeVisible();
      // await expect(page.getByTestId('pending-interviews-card')).toBeVisible();
    });

    test('should display interview activity feed when implemented', async ({ page }) => {
      await dashboardPage.goto();
      await dashboardPage.waitForLoad();

      // Basic dashboard should work
      await dashboardPage.expectDashboardPage();

      // TODO: Add activity feed tests when implemented
      // await expect(page.getByTestId('activity-feed')).toBeVisible();
      // const activityCount = await page.getByTestId('activity-item').count();
      // expect(activityCount).toBeGreaterThanOrEqual(0);
    });

    test('should display interview quick actions when implemented', async ({ page }) => {
      await dashboardPage.goto();
      await dashboardPage.waitForLoad();

      // Basic dashboard should work
      await dashboardPage.expectDashboardPage();

      // TODO: Add quick actions tests when implemented
      // await expect(page.getByTestId('quick-add-candidate')).toBeVisible();
      // await expect(page.getByTestId('quick-create-interview')).toBeVisible();
      // await expect(page.getByTestId('quick-create-question')).toBeVisible();
      // await expect(page.getByTestId('quick-generate-report')).toBeVisible();
    });

    test('should display interview analytics charts when implemented', async ({ page }) => {
      await dashboardPage.goto();
      await dashboardPage.waitForLoad();

      // Basic dashboard should work
      await dashboardPage.expectDashboardPage();

      // TODO: Add charts tests when implemented
      // await expect(page.getByTestId('interview-trends-chart')).toBeVisible();
      // await expect(page.getByTestId('risk-distribution-chart')).toBeVisible();
      // await expect(page.getByTestId('score-histogram-chart')).toBeVisible();
    });

    test('should be responsive on mobile devices', async ({ page }) => {
      await page.setViewportSize({ width: 393, height: 851 });
      await dashboardPage.goto();
      await dashboardPage.waitForLoad();

      // Basic dashboard should work on mobile
      await dashboardPage.expectDashboardPage();
      await expect(dashboardPage.title).toBeVisible();
    });

    test('should load dashboard quickly', async () => {
      const startTime = Date.now();
      await dashboardPage.goto();
      await dashboardPage.waitForLoad();
      const loadTime = Date.now() - startTime;

      // Should load within 5 seconds
      expect(loadTime).toBeLessThan(5000);
    });

    test('should handle API errors gracefully', async ({ page }) => {
      // Mock API error for future interview statistics
      await page.route('**/api/v1/dashboard/stats', route => {
        route.fulfill({
          status: 500,
          body: JSON.stringify({ error: 'Internal Server Error' })
        });
      });

      await dashboardPage.goto();
      await dashboardPage.waitForLoad();

      // Basic dashboard should still work
      await dashboardPage.expectDashboardPage();
    });
  });
});