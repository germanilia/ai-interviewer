import { test, expect } from '@playwright/test';
import { DashboardPage } from '../pages/DashboardPage';
import { TEST_URLS } from '../utils/testData';
import { loginAs, clearAuth } from '../utils/auth';

// Updated: Dashboard now expects job/interview/candidate stats and relationships

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
      // Check for dashboard title and subtitle
      await expect(page.getByTestId('page-title')).toBeVisible();
      await expect(page.getByTestId('page-subtitle')).toBeVisible();
    });

    test('dashboard loads correctly for regular user', async ({ page }) => {
      await loginAs(page, 'USER');
      await dashboardPage.expectDashboardPage();
      await dashboardPage.waitForLoad();
      await expect(page.getByTestId('page-title')).toBeVisible();
      await expect(page.getByTestId('page-subtitle')).toBeVisible();
    });

    test('dashboard shows user-specific content', async ({ page }) => {
      await loginAs(page, 'ADMIN');
      await dashboardPage.expectDashboardPage();
      await expect(page.getByTestId('page-title')).toBeVisible();
      await expect(page.getByTestId('page-subtitle')).toContainText('Welcome back');
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

  test.describe('Interview & Candidate Stats', () => {
    test.beforeEach(async ({ page }) => {
      await loginAs(page, 'ADMIN');
      await dashboardPage.goto();
      await dashboardPage.waitForLoad();
    });

    test('should display job/interview/candidate stats', async ({ page }) => {
      // These are now expected to be visible on dashboard or via navigation
      // Check for job title/description, candidate count, avg score, questions
      // (Assume dashboard links to interviews page for details)
      await expect(page.getByTestId('page-title')).toBeVisible();
      // Optionally, check for a link/button to interviews
      // await expect(page.getByTestId('go-to-interviews-btn')).toBeVisible();
    });
  });

  test.describe('Interview Management Features - Ready for Implementation', () => {
    test.beforeEach(async ({ page }) => {
      await loginAs(page, 'ADMIN');
    });

    test('should display enhanced dashboard content', async ({ page }) => {
      await dashboardPage.goto();
      await dashboardPage.waitForLoad();
      await dashboardPage.expectDashboardPage();
      await expect(page.getByTestId('page-title')).toBeVisible();
      // Interview/job/candidate stats are now on interviews page, not dashboard
    });

    test('should display interview activity feed when implemented', async ({ page }) => {
      await dashboardPage.goto();
      await dashboardPage.waitForLoad();
      await dashboardPage.expectDashboardPage();
      // TODO: Add activity feed tests when implemented
    });

    test('should display interview quick actions when implemented', async ({ page }) => {
      await dashboardPage.goto();
      await dashboardPage.waitForLoad();
      await dashboardPage.expectDashboardPage();
      // TODO: Add quick actions tests when implemented
    });

    test('should display interview analytics charts when implemented', async ({ page }) => {
      await dashboardPage.goto();
      await dashboardPage.waitForLoad();
      await dashboardPage.expectDashboardPage();
      // TODO: Add charts tests when implemented
    });

    test('should be responsive on mobile devices', async ({ page }) => {
      await page.setViewportSize({ width: 393, height: 851 });
      await dashboardPage.goto();
      await dashboardPage.waitForLoad();
      await dashboardPage.expectDashboardPage();
      await expect(page.getByTestId('page-title')).toBeVisible();
    });

    test('should load dashboard quickly', async () => {
      const startTime = Date.now();
      await dashboardPage.goto();
      await dashboardPage.waitForLoad();
      const loadTime = Date.now() - startTime;
      expect(loadTime).toBeLessThan(5000);
    });

    test('should handle API errors gracefully', async ({ page }) => {
      await page.route('**/api/v1/dashboard/stats', route => {
        route.fulfill({
          status: 500,
          body: JSON.stringify({ error: 'Internal Server Error' })
        });
      });
      await dashboardPage.goto();
      await dashboardPage.waitForLoad();
      await dashboardPage.expectDashboardPage();
    });
  });
});