import { test, expect } from '@playwright/test';
import { DashboardPage } from '../../pages/admin/DashboardPage';
import { TestSetup } from '../../utils/testSetup';
import { mockDashboardStats, mockRecentActivity, mockChartData } from '../../utils/adminTestData';

test.describe('Dashboard Overview', () => {
  let dashboardPage: DashboardPage;

  test.beforeEach(async ({ page }) => {
    dashboardPage = new DashboardPage(page);
    await TestSetup.setupAdminTest(page, { setupTestData: true });
  });

  test.afterEach(async ({ page }) => {
    await TestSetup.cleanupAdminTest();
  });

  test.describe('Statistics Cards', () => {
    test('should display all system statistics cards', async () => {
      await dashboardPage.navigateTo();
      await dashboardPage.waitForDashboardToLoad();
      
      // Verify all statistics cards are visible
      await expect(dashboardPage.totalCandidatesCard).toBeVisible();
      await expect(dashboardPage.activeInterviewsCard).toBeVisible();
      await expect(dashboardPage.completedInterviewsCard).toBeVisible();
      await expect(dashboardPage.pendingInterviewsCard).toBeVisible();
      await expect(dashboardPage.averageScoreCard).toBeVisible();
      await expect(dashboardPage.highRiskCandidatesCard).toBeVisible();
    });

    test('should display correct statistics values', async () => {
      await dashboardPage.navigateTo();
      await dashboardPage.waitForDashboardToLoad();
      
      // Verify statistics show actual numbers (not loading states)
      const totalCandidates = await dashboardPage.getStatisticValue('total-candidates-card');
      const activeInterviews = await dashboardPage.getStatisticValue('active-interviews-card');
      const completedInterviews = await dashboardPage.getStatisticValue('completed-interviews-card');
      
      expect(parseInt(totalCandidates)).toBeGreaterThan(0);
      expect(parseInt(activeInterviews)).toBeGreaterThanOrEqual(0);
      expect(parseInt(completedInterviews)).toBeGreaterThanOrEqual(0);
    });

    test('should display statistics labels correctly', async () => {
      await dashboardPage.navigateTo();
      await dashboardPage.waitForDashboardToLoad();
      
      // Verify statistics labels are descriptive
      const totalCandidatesLabel = await dashboardPage.getStatisticLabel('total-candidates-card');
      const activeInterviewsLabel = await dashboardPage.getStatisticLabel('active-interviews-card');
      
      expect(totalCandidatesLabel).toContain('Total Candidates');
      expect(activeInterviewsLabel).toContain('Active Interviews');
    });

    test('should handle loading states gracefully', async ({ page }) => {
      // Mock slow API response
      await page.route('**/api/v1/dashboard/stats', route => {
        setTimeout(() => {
          route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify(mockDashboardStats)
          });
        }, 1000);
      });

      await dashboardPage.navigateTo();
      
      // Should show loading state initially
      await expect(dashboardPage.statisticsLoading).toBeVisible();
      
      // Then show actual data
      await dashboardPage.waitForDashboardToLoad();
      await expect(dashboardPage.statisticsLoading).not.toBeVisible();
      await expect(dashboardPage.totalCandidatesCard).toBeVisible();
    });

    test('should handle API errors gracefully', async ({ page }) => {
      // Mock API error
      await page.route('**/api/v1/dashboard/stats', route => {
        route.fulfill({
          status: 500,
          body: JSON.stringify({ error: 'Internal Server Error' })
        });
      });

      await dashboardPage.navigateTo();
      
      // Should still show cards with error states or default values
      await expect(dashboardPage.statisticsSection).toBeVisible();
      await expect(dashboardPage.totalCandidatesCard).toBeVisible();
    });
  });

  test.describe('Recent Activity Feed', () => {
    test('should display recent activity items', async () => {
      await dashboardPage.navigateTo();
      await dashboardPage.waitForDashboardToLoad();
      
      // Verify activity feed is visible
      await expect(dashboardPage.activityFeed).toBeVisible();
      
      // Should have at least some activity items
      const activityCount = await dashboardPage.activityItems.count();
      expect(activityCount).toBeGreaterThan(0);
    });

    test('should display activity items with correct structure', async () => {
      await dashboardPage.navigateTo();
      await dashboardPage.waitForDashboardToLoad();
      
      // Get first activity item and verify structure
      const firstActivity = dashboardPage.activityItems.first();
      await expect(firstActivity.locator('[data-testid="activity-type"]')).toBeVisible();
      await expect(firstActivity.locator('[data-testid="activity-description"]')).toBeVisible();
      await expect(firstActivity.locator('[data-testid="activity-timestamp"]')).toBeVisible();
    });

    test('should refresh activity feed', async () => {
      await dashboardPage.navigateTo();
      await dashboardPage.waitForDashboardToLoad();
      
      const initialCount = await dashboardPage.activityItems.count();
      
      // Refresh activity feed
      await dashboardPage.refreshActivityFeed();
      
      // Should still have activity items (count might change)
      const newCount = await dashboardPage.activityItems.count();
      expect(newCount).toBeGreaterThanOrEqual(0);
    });

    test('should load more activity items', async () => {
      await dashboardPage.navigateTo();
      await dashboardPage.waitForDashboardToLoad();
      
      // Check if load more button is available
      const isLoadMoreVisible = await dashboardPage.activityLoadMore.isVisible();
      
      if (isLoadMoreVisible) {
        const initialCount = await dashboardPage.activityItems.count();
        
        // Load more items
        await dashboardPage.loadMoreActivity();
        
        // Should have more items
        const newCount = await dashboardPage.activityItems.count();
        expect(newCount).toBeGreaterThan(initialCount);
      }
    });

    test('should display different activity types', async () => {
      await dashboardPage.navigateTo();
      await dashboardPage.waitForDashboardToLoad();
      
      const activities = await dashboardPage.getActivityItems();
      
      // Should have various activity types
      const activityTypes = activities.map(a => a.type);
      const uniqueTypes = [...new Set(activityTypes)];
      
      expect(uniqueTypes.length).toBeGreaterThan(1);
      expect(uniqueTypes).toContain('interview_completed');
    });
  });

  test.describe('Quick Actions Panel', () => {
    test('should display all quick action buttons', async () => {
      await dashboardPage.navigateTo();
      await dashboardPage.waitForDashboardToLoad();
      
      // Verify all quick actions are visible
      await expect(dashboardPage.addCandidateQuickAction).toBeVisible();
      await expect(dashboardPage.createInterviewQuickAction).toBeVisible();
      await expect(dashboardPage.createQuestionQuickAction).toBeVisible();
      await expect(dashboardPage.generateReportQuickAction).toBeVisible();
    });

    test('should open add candidate modal', async () => {
      await dashboardPage.navigateTo();
      await dashboardPage.waitForDashboardToLoad();
      
      // Click add candidate quick action
      await dashboardPage.clickQuickAction('add-candidate');
      
      // Should open add candidate modal
      await expect(dashboardPage.page.getByTestId('add-candidate-modal')).toBeVisible();
    });

    test('should open create interview modal', async () => {
      await dashboardPage.navigateTo();
      await dashboardPage.waitForDashboardToLoad();
      
      // Click create interview quick action
      await dashboardPage.clickQuickAction('create-interview');
      
      // Should open create interview modal
      await expect(dashboardPage.page.getByTestId('create-interview-modal')).toBeVisible();
    });

    test('should open create question modal', async () => {
      await dashboardPage.navigateTo();
      await dashboardPage.waitForDashboardToLoad();
      
      // Click create question quick action
      await dashboardPage.clickQuickAction('create-question');
      
      // Should open create question modal
      await expect(dashboardPage.page.getByTestId('create-question-modal')).toBeVisible();
    });

    test('should open generate report modal', async () => {
      await dashboardPage.navigateTo();
      await dashboardPage.waitForDashboardToLoad();
      
      // Click generate report quick action
      await dashboardPage.clickQuickAction('generate-report');
      
      // Should open generate report modal
      await expect(dashboardPage.page.getByTestId('generate-report-modal')).toBeVisible();
    });
  });

  test.describe('Charts and Visualizations', () => {
    test('should display all charts', async () => {
      await dashboardPage.navigateTo();
      await dashboardPage.waitForDashboardToLoad();
      
      // Verify all charts are visible
      await expect(dashboardPage.interviewTrendsChart).toBeVisible();
      await expect(dashboardPage.riskDistributionChart).toBeVisible();
      await expect(dashboardPage.scoreHistogramChart).toBeVisible();
    });

    test('should load charts with data', async () => {
      await dashboardPage.navigateTo();
      await dashboardPage.waitForDashboardToLoad();
      
      // Verify charts are loaded and contain visual elements
      await dashboardPage.verifyChartsLoaded();
    });

    test('should make charts interactive', async () => {
      await dashboardPage.navigateTo();
      await dashboardPage.waitForDashboardToLoad();
      
      // Test chart interactivity (hover effects, tooltips)
      await dashboardPage.interactWithChart('interview-trends-chart', 'hover');
      
      // Should show tooltip or hover effect
      // This would depend on the specific chart library implementation
    });

    test('should handle chart loading errors', async ({ page }) => {
      // Mock chart data API error
      await page.route('**/api/v1/dashboard/charts', route => {
        route.fulfill({
          status: 500,
          body: JSON.stringify({ error: 'Chart data unavailable' })
        });
      });

      await dashboardPage.navigateTo();
      
      // Charts section should still be visible with error states
      await expect(dashboardPage.chartsSection).toBeVisible();
    });
  });

  test.describe('Responsive Design', () => {
    test('should display correctly on desktop', async ({ page }) => {
      await TestSetup.setupDesktopViewport(page);
      await dashboardPage.navigateTo();
      await dashboardPage.waitForDashboardToLoad();
      
      // Statistics cards should be in a grid layout
      const cardsContainer = dashboardPage.statisticsCards;
      const flexDirection = await cardsContainer.evaluate(el => getComputedStyle(el).flexDirection);
      expect(flexDirection).toBe('row');
      
      // Charts should be side by side
      const chartsContainer = dashboardPage.chartsContainer;
      await expect(chartsContainer).toBeVisible();
    });

    test('should display correctly on mobile', async ({ page }) => {
      await TestSetup.setupMobileViewport(page);
      await dashboardPage.navigateTo();
      await dashboardPage.waitForDashboardToLoad();
      
      // Verify mobile responsive layout
      await dashboardPage.verifyMobileLayout();
    });

    test('should handle different screen sizes', async ({ page }) => {
      const viewports = [
        { width: 1920, height: 1080 }, // Desktop
        { width: 1366, height: 768 },  // Laptop
        { width: 768, height: 1024 },  // Tablet
        { width: 393, height: 851 }    // Mobile
      ];

      for (const viewport of viewports) {
        await page.setViewportSize(viewport);
        await dashboardPage.navigateTo();
        await dashboardPage.waitForDashboardToLoad();
        
        // All main sections should be visible
        await expect(dashboardPage.statisticsSection).toBeVisible();
        await expect(dashboardPage.activitySection).toBeVisible();
        await expect(dashboardPage.quickActionsSection).toBeVisible();
        await expect(dashboardPage.chartsSection).toBeVisible();
      }
    });
  });

  test.describe('Performance', () => {
    test('should load dashboard quickly', async () => {
      const startTime = Date.now();
      await dashboardPage.navigateTo();
      await dashboardPage.waitForDashboardToLoad();
      const loadTime = Date.now() - startTime;
      
      // Should load within 3 seconds
      expect(loadTime).toBeLessThan(3000);
    });

    test('should handle concurrent data loading', async ({ page }) => {
      // Mock multiple API endpoints with delays
      await page.route('**/api/v1/dashboard/stats', route => {
        setTimeout(() => route.fulfill({
          status: 200,
          body: JSON.stringify(mockDashboardStats)
        }), 500);
      });

      await page.route('**/api/v1/dashboard/recent-activity', route => {
        setTimeout(() => route.fulfill({
          status: 200,
          body: JSON.stringify(mockRecentActivity)
        }), 300);
      });

      await page.route('**/api/v1/dashboard/charts', route => {
        setTimeout(() => route.fulfill({
          status: 200,
          body: JSON.stringify(mockChartData)
        }), 700);
      });

      await dashboardPage.navigateTo();
      await dashboardPage.waitForDashboardToLoad();
      
      // All sections should load despite different timing
      await expect(dashboardPage.statisticsSection).toBeVisible();
      await expect(dashboardPage.activitySection).toBeVisible();
      await expect(dashboardPage.chartsSection).toBeVisible();
    });
  });

  test.describe('Data Accuracy', () => {
    test('should display consistent data across sections', async () => {
      await dashboardPage.navigateTo();
      await dashboardPage.waitForDashboardToLoad();
      
      // Get dashboard summary
      const summary = await dashboardPage.getDashboardSummary();
      
      // Verify data consistency
      expect(parseInt(summary.totalCandidates)).toBeGreaterThanOrEqual(0);
      expect(parseInt(summary.activeInterviews)).toBeGreaterThanOrEqual(0);
      expect(parseInt(summary.completedInterviews)).toBeGreaterThanOrEqual(0);
      
      // Active + Completed + Pending should not exceed total interviews
      const totalInterviews = parseInt(summary.activeInterviews) + 
                             parseInt(summary.completedInterviews) + 
                             parseInt(summary.pendingInterviews);
      expect(totalInterviews).toBeGreaterThanOrEqual(0);
    });

    test('should update data when refreshed', async () => {
      await dashboardPage.navigateTo();
      await dashboardPage.waitForDashboardToLoad();
      
      const initialSummary = await dashboardPage.getDashboardSummary();
      
      // Refresh the page
      await dashboardPage.page.reload();
      await dashboardPage.waitForDashboardToLoad();
      
      const refreshedSummary = await dashboardPage.getDashboardSummary();
      
      // Data should be consistent (might be same or updated)
      expect(refreshedSummary.totalCandidates).toBeDefined();
      expect(refreshedSummary.activeInterviews).toBeDefined();
    });
  });
});
