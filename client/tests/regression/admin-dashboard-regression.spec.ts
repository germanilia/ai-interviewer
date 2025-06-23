import { test, expect } from '@playwright/test';
import { AppLayoutPage } from '../pages/AppLayoutPage';
import { loginAs } from '../utils/auth';

/**
 * Admin Dashboard Regression Test Suite
 *
 * This suite contains essential smoke tests that verify core layout and navigation
 * functionality across the admin dashboard. These tests focus on the implemented
 * features and should run quickly to catch major regressions.
 *
 * Run this suite for:
 * - Pre-deployment validation
 * - Quick smoke testing after changes
 * - CI/CD pipeline validation
 */
test.describe('Admin Dashboard Regression Tests', () => {
  let appLayoutPage: AppLayoutPage;

  test.beforeEach(async ({ page }) => {
    appLayoutPage = new AppLayoutPage(page);
  });

  test.describe('Critical User Paths', () => {
    test('should complete basic admin workflow: login → dashboard → navigate all sections', async ({ page }) => {
      // 1. Login and verify admin layout loads
      await loginAs(page, 'USER');
      await appLayoutPage.navigateToDashboard();
      await appLayoutPage.verifyAdminAccess();

      // 2. Verify dashboard page loads with proper title
      await appLayoutPage.navigateTo('dashboard');
      await expect(appLayoutPage.page).toHaveURL('/dashboard');
      await appLayoutPage.verifyPageHeader('Dashboard');

      // 3. Navigate to all admin sections and verify they load
      const sections = ['candidates', 'interviews', 'questions', 'job-positions', 'reports'] as const;

      for (const section of sections) {
        await appLayoutPage.navigateTo(section);
        await expect(appLayoutPage.page).toHaveURL(`/${section}`);
        await appLayoutPage.waitForPageLoad();
        await expect(appLayoutPage.mainContent).toBeVisible();

        // Verify page title is displayed
        await expect(appLayoutPage.pageTitle).toBeVisible();
      }
    });

    test('should handle navigation between all admin sections', async ({ page }) => {
      await loginAs(page, 'USER');
      await appLayoutPage.navigateToDashboard();

      // Test navigation to each major section
      const sections = ['dashboard', 'candidates', 'interviews', 'questions', 'job-positions', 'reports'] as const;

      for (const section of sections) {
        await appLayoutPage.navigateTo(section);
        await expect(appLayoutPage.page).toHaveURL(`/${section}`);

        // Verify page loads without errors
        await appLayoutPage.waitForPageLoad();
        await expect(appLayoutPage.mainContent).toBeVisible();
      }
    });
  });

  test.describe('Essential UI Components', () => {
    test('should display all page sections with proper titles', async ({ page }) => {
      await loginAs(page, 'USER');
      await appLayoutPage.navigateToDashboard();

      // Test each section has proper page title and content
      const sectionTitles = {
        dashboard: 'Dashboard',
        candidates: 'Candidates',
        interviews: 'Interviews',
        questions: 'Questions',
        'job-positions': 'Job Positions',
        reports: 'Reports'
      };

      for (const [section, expectedTitle] of Object.entries(sectionTitles)) {
        await appLayoutPage.navigateTo(section as any);
        await appLayoutPage.verifyPageHeader(expectedTitle);
        await expect(appLayoutPage.mainContent).toBeVisible();
      }
    });

    test('should display navigation items correctly', async ({ page }) => {
      await loginAs(page, 'USER');
      await appLayoutPage.navigateToDashboard();

      // Check if we're on mobile or desktop
      const isMobile = await appLayoutPage.mobileMenuButton.isVisible().catch(() => false);

      if (isMobile) {
        // On mobile, open menu to see navigation items
        await appLayoutPage.openMobileMenu();
      }

      // Verify all navigation items are visible
      await expect(appLayoutPage.dashboardLink).toBeVisible();
      await expect(appLayoutPage.candidatesLink).toBeVisible();
      await expect(appLayoutPage.interviewsLink).toBeVisible();
      await expect(appLayoutPage.questionsLink).toBeVisible();
      await expect(appLayoutPage.jobsLink).toBeVisible();
      await expect(appLayoutPage.reportsLink).toBeVisible();

      if (isMobile) {
        await appLayoutPage.closeMobileMenu();
      }
    });
  });

  test.describe('Authentication and Access Control', () => {
    test('should maintain admin session across navigation', async ({ page }) => {
      await loginAs(page, 'USER');
      await appLayoutPage.navigateToDashboard();
      await appLayoutPage.verifyAdminAccess();

      // Navigate to different sections
      await appLayoutPage.navigateTo('candidates');
      await appLayoutPage.verifyAdminAccess();

      await appLayoutPage.navigateTo('interviews');
      await appLayoutPage.verifyAdminAccess();

      await appLayoutPage.navigateTo('reports');
      await appLayoutPage.verifyAdminAccess();
    });

    test('should display user menu and logout option', async ({ page }) => {
      await loginAs(page, 'USER');
      await appLayoutPage.navigateToDashboard();

      await expect(appLayoutPage.userMenu).toBeVisible();
      await expect(appLayoutPage.logoutButton).toBeVisible();
    });
  });

  test.describe('Responsive Design', () => {
    test('should display admin interface on mobile devices', async ({ page }) => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });

      await loginAs(page, 'USER');
      await appLayoutPage.navigateToDashboard();

      // Verify mobile layout
      const isSidebarCollapsed = await appLayoutPage.isSidebarCollapsed();
      expect(isSidebarCollapsed).toBe(true);

      // Verify mobile menu works
      await expect(appLayoutPage.mobileMenuButton).toBeVisible();
      await appLayoutPage.openMobileMenu();
      await expect(appLayoutPage.mobileNavigation).toBeVisible();
    });
  });

  test.describe('Integration Points', () => {
    test('should handle navigation without external dependencies', async ({ page }) => {
      // Verify the admin interface loads and navigates properly
      await loginAs(page, 'USER');
      await appLayoutPage.navigateToDashboard();
      await appLayoutPage.verifyAdminAccess();

      // All sections should load properly
      const sections = ['dashboard', 'candidates', 'interviews', 'questions', 'job-positions', 'reports'] as const;

      for (const section of sections) {
        await appLayoutPage.navigateTo(section);
        await expect(appLayoutPage.page).toHaveURL(`/${section}`);
        await appLayoutPage.waitForPageLoad();
        await expect(appLayoutPage.mainContent).toBeVisible();
      }
    });
  });
});
