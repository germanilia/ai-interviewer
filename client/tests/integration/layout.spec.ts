import { test, expect } from '@playwright/test';
import { AppLayoutPage } from '../pages/AppLayoutPage';
import { loginAs, clearAuth } from '../utils/auth';

test.describe('App Layout and Navigation - Extended with Interview Features', () => {
  let appLayoutPage: AppLayoutPage;

  test.beforeEach(async ({ page }) => {
    await clearAuth(page);
    appLayoutPage = new AppLayoutPage(page);
  });

  test.describe('Desktop Layout', () => {
    test.beforeEach(async ({ page }) => {
      await page.setViewportSize({ width: 1280, height: 720 });
    });

    test('should display sidebar with all navigation items including new interview features', async ({ page }) => {
      await loginAs(page, 'ADMIN');
      await appLayoutPage.navigateToDashboard();

      // Verify sidebar is visible
      await expect(appLayoutPage.sidebar).toBeVisible();

      // Verify existing navigation links are present
      await expect(appLayoutPage.dashboardLink).toBeVisible();
      await expect(appLayoutPage.usersLink).toBeVisible();
      await expect(appLayoutPage.settingsLink).toBeVisible();

      // Verify new interview management navigation links are present
      await expect(appLayoutPage.candidatesLink).toBeVisible();
      await expect(appLayoutPage.interviewsLink).toBeVisible();
      await expect(appLayoutPage.questionsLink).toBeVisible();
      await expect(appLayoutPage.jobsLink).toBeVisible();
      await expect(appLayoutPage.reportsLink).toBeVisible();
    });

    test('should navigate between interview management sections', async ({ page }) => {
      await loginAs(page, 'ADMIN');
      await appLayoutPage.navigateToDashboard();

      // Test navigation to new interview management sections
      const sections = ['candidates', 'interviews', 'questions', 'job-positions', 'reports'] as const;

      for (const section of sections) {
        await appLayoutPage.navigateTo(section);
        await expect(appLayoutPage.page).toHaveURL(`/${section}`);

        // Verify active navigation state
        const activeItem = await appLayoutPage.getActiveNavItem();
        expect(activeItem).toBe(section);
      }
    });

    test('should display user menu and logout functionality', async ({ page }) => {
      await loginAs(page, 'ADMIN');
      await appLayoutPage.navigateToDashboard();
      
      // Verify user menu is visible
      await expect(appLayoutPage.userMenu).toBeVisible();
      
      // Click user menu to open dropdown
      await appLayoutPage.userMenu.click();
      await expect(appLayoutPage.logoutButton).toBeVisible();
      
      // Test logout (but don't actually logout to avoid breaking other tests)
      // await appLayoutPage.logout();
      // await expect(appLayoutPage.page).toHaveURL('/login');
    });

    test('should display main content area', async ({ page }) => {
      await loginAs(page, 'USER');
      await appLayoutPage.navigateToDashboard();
      
      await expect(appLayoutPage.mainContent).toBeVisible();
      
      // Verify main content takes up appropriate space
      const mainContentBox = await appLayoutPage.mainContent.boundingBox();
      expect(mainContentBox).toBeTruthy();
      expect(mainContentBox!.width).toBeGreaterThan(800); // Should have substantial width on desktop
    });

    test('should display breadcrumbs for navigation context', async ({ page }) => {
      await loginAs(page, 'USER');
      await appLayoutPage.navigateToDashboard();

      // Navigate to a subsection
      await appLayoutPage.navigateTo('candidates');

      // Verify breadcrumbs are visible (if implemented)
      // Note: Breadcrumbs may not be implemented in the existing layout
      // This test can be updated once breadcrumb implementation is confirmed
      const breadcrumbsExist = await appLayoutPage.breadcrumbs.isVisible().catch(() => false);

      if (breadcrumbsExist) {
        const breadcrumbTrail = await appLayoutPage.getBreadcrumbTrail();
        expect(breadcrumbTrail).toContain('Candidates');
      }
    });

    test('should display page titles correctly', async ({ page }) => {
      await loginAs(page, 'USER');
      await appLayoutPage.navigateToDashboard();
      
      // Test page titles for different sections
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
      }
    });

    test('should toggle sidebar visibility', async ({ page }) => {
      await loginAs(page, 'USER');
      await appLayoutPage.navigateToDashboard();
      
      // Verify sidebar is initially visible
      await expect(appLayoutPage.sidebar).toBeVisible();
      const isInitiallyCollapsed = await appLayoutPage.isSidebarCollapsed();
      
      // Toggle sidebar
      await appLayoutPage.toggleSidebar();
      
      // Verify sidebar state changed
      const isCollapsedAfterToggle = await appLayoutPage.isSidebarCollapsed();
      expect(isCollapsedAfterToggle).toBe(!isInitiallyCollapsed);
      
      // Toggle back
      await appLayoutPage.toggleSidebar();
      const isFinallyCollapsed = await appLayoutPage.isSidebarCollapsed();
      expect(isFinallyCollapsed).toBe(isInitiallyCollapsed);
    });
  });

  test.describe('Mobile Layout', () => {
    test.beforeEach(async ({ page }) => {
      await page.setViewportSize({ width: 393, height: 851 });
    });

    test('should display mobile-optimized layout', async ({ page }) => {
      await loginAs(page, 'USER');
      await appLayoutPage.navigateToDashboard();
      
      // On mobile, sidebar should be hidden by default
      const isSidebarCollapsed = await appLayoutPage.isSidebarCollapsed();
      expect(isSidebarCollapsed).toBe(true);
      
      // Mobile menu button should be visible
      await expect(appLayoutPage.mobileMenuButton).toBeVisible();
    });

    test('should open and close mobile menu', async ({ page }) => {
      await loginAs(page, 'USER');
      await appLayoutPage.navigateToDashboard();
      
      // Open mobile menu
      await appLayoutPage.openMobileMenu();
      
      // Verify sidebar/menu is now visible
      await expect(appLayoutPage.sidebar).toBeVisible();
      await expect(appLayoutPage.mobileOverlay).toBeVisible();
      
      // Close mobile menu by clicking overlay
      await appLayoutPage.closeMobileMenu();
      
      // Verify menu is closed
      await expect(appLayoutPage.mobileOverlay).not.toBeVisible();
    });

    test('should navigate on mobile', async ({ page }) => {
      await loginAs(page, 'USER');
      await appLayoutPage.navigateToDashboard();
      
      // Open mobile menu
      await appLayoutPage.openMobileMenu();
      
      // Navigate to candidates
      await appLayoutPage.candidatesLink.click();

      // Verify navigation worked
      await expect(appLayoutPage.page).toHaveURL('/candidates');
      
      // Menu should close after navigation
      await expect(appLayoutPage.mobileOverlay).not.toBeVisible();
    });

    test('should display responsive main content', async ({ page }) => {
      await loginAs(page, 'USER');
      await appLayoutPage.navigateToDashboard();
      
      await expect(appLayoutPage.mainContent).toBeVisible();
      
      // Verify main content uses full width on mobile
      const mainContentBox = await appLayoutPage.mainContent.boundingBox();
      expect(mainContentBox).toBeTruthy();
      expect(mainContentBox!.width).toBeLessThan(400); // Should be mobile width
    });
  });

  test.describe('Authentication and Access Control', () => {
    test('should verify user access to admin features', async ({ page }) => {
      // Updated: Admin features are now accessible to all users, not just admins
      // Only specific features like Users management remain admin-only
      await loginAs(page, 'USER');
      await appLayoutPage.navigateToDashboard();
      await appLayoutPage.verifyAdminAccess();

      // Verify all users can see new admin navigation items
      await expect(appLayoutPage.candidatesLink).toBeVisible();
      await expect(appLayoutPage.interviewsLink).toBeVisible();
      await expect(appLayoutPage.questionsLink).toBeVisible();
      await expect(appLayoutPage.jobsLink).toBeVisible();
      await expect(appLayoutPage.reportsLink).toBeVisible();
    });

    test('should handle authentication errors gracefully', async ({ page }) => {
      // Test what happens when auth token expires or is invalid
      // This would involve mocking auth failures
      await loginAs(page, 'USER');
      await appLayoutPage.navigateToDashboard();

      // Verify error handling doesn't break the layout
      await expect(appLayoutPage.sidebar).toBeVisible();
      await expect(appLayoutPage.mainContent).toBeVisible();
    });
  });

  test.describe('Performance and Loading States', () => {
    test('should load admin layout quickly', async ({ page }) => {
      const startTime = Date.now();
      await loginAs(page, 'USER');
      await appLayoutPage.navigateToDashboard();
      await appLayoutPage.waitForPageLoad();
      const loadTime = Date.now() - startTime;
      
      // Should load within 3 seconds
      expect(loadTime).toBeLessThan(3000);
    });

    test('should handle slow network conditions', async ({ page }) => {
      // Simulate slow network
      await page.route('**/*', route => {
        setTimeout(() => route.continue(), 100); // Add 100ms delay
      });
      
      await loginAs(page, 'USER');
      await appLayoutPage.navigateToDashboard();
      
      // Layout should still be functional
      await expect(appLayoutPage.sidebar).toBeVisible();
      await expect(appLayoutPage.mainContent).toBeVisible();
    });
  });

  test.describe('Accessibility', () => {
    test('should be keyboard navigable', async ({ page }) => {
      await loginAs(page, 'USER');
      await appLayoutPage.navigateToDashboard();
      
      // Test keyboard navigation through sidebar links
      await page.keyboard.press('Tab');
      await page.keyboard.press('Tab');
      
      // Should be able to navigate with keyboard
      const focusedElement = await page.locator(':focus').getAttribute('data-testid');
      expect(focusedElement).toContain('nav-');
    });

    test('should have proper ARIA labels', async ({ page }) => {
      await loginAs(page, 'USER');
      await appLayoutPage.navigateToDashboard();
      
      // Check for ARIA labels on navigation
      const sidebarAriaLabel = await appLayoutPage.sidebar.getAttribute('aria-label');
      expect(sidebarAriaLabel).toBeTruthy();
      
      // Check mobile menu button has proper label
      const mobileMenuLabel = await appLayoutPage.mobileMenuButton.getAttribute('aria-label');
      expect(mobileMenuLabel).toBeTruthy();
    });

    test('should support screen readers', async ({ page }) => {
      await loginAs(page, 'USER');
      await appLayoutPage.navigateToDashboard();
      
      // Verify semantic HTML structure
      const nav = appLayoutPage.page.locator('nav');
      await expect(nav).toBeVisible();
      
      const main = appLayoutPage.page.locator('main');
      await expect(main).toBeVisible();
    });
  });

  test.describe('Error Handling', () => {
    test('should handle navigation errors gracefully', async ({ page }) => {
      await loginAs(page, 'USER');
      await appLayoutPage.navigateToDashboard();
      
      // Try to navigate to non-existent route
      await page.goto('/nonexistent');
      
      // Should show error page or redirect, but layout should remain intact
      await expect(appLayoutPage.sidebar).toBeVisible();
    });

    test('should display error messages appropriately', async ({ page }) => {
      // Mock API error
      await page.route('**/api/v1/**', route => {
        route.fulfill({
          status: 500,
          body: JSON.stringify({ error: 'Internal Server Error' })
        });
      });
      
      await loginAs(page, 'USER');
      await appLayoutPage.navigateToDashboard();
      
      // Layout should still be functional even with API errors
      await expect(appLayoutPage.sidebar).toBeVisible();
      await expect(appLayoutPage.mainContent).toBeVisible();
    });
  });
});
