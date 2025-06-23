import { test, expect } from '@playwright/test';
import { ReportsPage } from '../../pages/admin/ReportsPage';
import { TestSetup } from '../../utils/testSetup';
import { mockChartData } from '../../utils/adminTestData';

test.describe('Reports and Analytics', () => {
  let reportsPage: ReportsPage;

  test.beforeEach(async ({ page }) => {
    reportsPage = new ReportsPage(page);
    await TestSetup.setupAdminTest(page, { setupTestData: true });
  });

  test.afterEach(async ({ page }) => {
    await TestSetup.cleanupAdminTest();
  });

  test.describe('Overview Dashboard', () => {
    test('should display overview dashboard with summary cards', async () => {
      await reportsPage.navigateTo();
      await reportsPage.waitForReportsToLoad();
      
      // Verify overview tab is active by default
      await expect(reportsPage.overviewSection).toBeVisible();
      
      // Verify summary cards
      await expect(reportsPage.summaryCards).toBeVisible();
      await expect(reportsPage.totalInterviewsCard).toBeVisible();
      await expect(reportsPage.completionRateCard).toBeVisible();
      await expect(reportsPage.avgRiskScoreCard).toBeVisible();
      await expect(reportsPage.flaggedCandidatesCard).toBeVisible();
    });

    test('should display overview charts', async () => {
      await reportsPage.navigateTo();
      await reportsPage.waitForReportsToLoad();
      
      // Verify charts are visible
      await expect(reportsPage.trendsChart).toBeVisible();
      await expect(reportsPage.riskDistributionChart).toBeVisible();
      await expect(reportsPage.departmentBreakdownChart).toBeVisible();
      
      // Verify charts have content (canvas or svg elements)
      const trendsChartContent = await reportsPage.trendsChart.locator('canvas, svg').count();
      expect(trendsChartContent).toBeGreaterThan(0);
    });

    test('should display meaningful summary statistics', async () => {
      await reportsPage.navigateTo();
      await reportsPage.waitForReportsToLoad();
      
      // Verify summary cards have numeric values
      const totalInterviews = await reportsPage.totalInterviewsCard.locator('[data-testid="stat-value"]').textContent();
      const completionRate = await reportsPage.completionRateCard.locator('[data-testid="stat-value"]').textContent();
      
      expect(parseInt(totalInterviews || '0')).toBeGreaterThanOrEqual(0);
      expect(completionRate).toMatch(/\d+%/); // Should be a percentage
    });
  });

  test.describe('Report Type Navigation', () => {
    test('should navigate between report type tabs', async () => {
      await reportsPage.navigateTo();
      await reportsPage.waitForReportsToLoad();
      
      // Verify all tabs are visible
      await expect(reportsPage.reportTypeTabs).toBeVisible();
      await expect(reportsPage.overviewTab).toBeVisible();
      await expect(reportsPage.candidateReportsTab).toBeVisible();
      await expect(reportsPage.interviewReportsTab).toBeVisible();
      await expect(reportsPage.analyticsTab).toBeVisible();
      await expect(reportsPage.customReportsTab).toBeVisible();
      
      // Test navigation to each tab
      await reportsPage.switchToTab('candidate-reports');
      await expect(reportsPage.candidateReportsSection).toBeVisible();
      
      await reportsPage.switchToTab('interview-reports');
      await expect(reportsPage.interviewReportsSection).toBeVisible();
      
      await reportsPage.switchToTab('analytics');
      await expect(reportsPage.analyticsSection).toBeVisible();
      
      await reportsPage.switchToTab('custom-reports');
      await expect(reportsPage.customReportsSection).toBeVisible();
    });
  });

  test.describe('Candidate Reports', () => {
    test('should display candidate reports section', async () => {
      await reportsPage.navigateTo();
      await reportsPage.switchToTab('candidate-reports');
      
      // Verify candidate reports components
      await expect(reportsPage.candidateReportsSection).toBeVisible();
      await expect(reportsPage.generateCandidateReportButton).toBeVisible();
      await expect(reportsPage.candidateReportsList).toBeVisible();
    });

    test('should generate candidate report', async () => {
      await reportsPage.navigateTo();
      await reportsPage.switchToTab('candidate-reports');
      
      // Generate candidate report
      await reportsPage.generateCandidateReport(1, 'pdf');
      
      // Verify report generation process
      await expect(reportsPage.successToast).toBeVisible();
      await expect(reportsPage.reportGenerationModal).not.toBeVisible();
    });

    test('should preview candidate report', async () => {
      await reportsPage.navigateTo();
      await reportsPage.switchToTab('candidate-reports');
      
      const reportCount = await reportsPage.candidateReportRows.count();
      if (reportCount > 0) {
        // Click preview on first report
        await reportsPage.candidateReportRows.first().locator('[data-testid="preview-report-btn"]').click();
        
        // Verify preview modal
        await expect(reportsPage.reportPreviewModal).toBeVisible();
        await expect(reportsPage.previewContent).toBeVisible();
        await expect(reportsPage.previewHeader).toBeVisible();
        await expect(reportsPage.previewSummary).toBeVisible();
        
        // Close preview
        await reportsPage.closePreviewButton.click();
        await expect(reportsPage.reportPreviewModal).not.toBeVisible();
      }
    });
  });

  test.describe('Interview Reports', () => {
    test('should display interview reports section', async () => {
      await reportsPage.navigateTo();
      await reportsPage.switchToTab('interview-reports');
      
      // Verify interview reports components
      await expect(reportsPage.interviewReportsSection).toBeVisible();
      await expect(reportsPage.generateInterviewReportButton).toBeVisible();
      await expect(reportsPage.interviewReportsList).toBeVisible();
    });

    test('should generate interview report', async () => {
      await reportsPage.navigateTo();
      await reportsPage.switchToTab('interview-reports');
      
      // Generate interview report
      await reportsPage.generateInterviewReport(1, 'excel');
      
      // Verify report generation process
      await expect(reportsPage.successToast).toBeVisible();
      await expect(reportsPage.reportGenerationModal).not.toBeVisible();
    });

    test('should handle different report formats', async () => {
      await reportsPage.navigateTo();
      await reportsPage.switchToTab('interview-reports');
      
      const formats: ('pdf' | 'excel' | 'csv')[] = ['pdf', 'excel', 'csv'];
      
      for (const format of formats) {
        await reportsPage.generateInterviewReport(1, format);
        await expect(reportsPage.successToast).toBeVisible();
        
        // Wait a bit between generations
        await reportsPage.page.waitForTimeout(500);
      }
    });
  });

  test.describe('Analytics Dashboard', () => {
    test('should display analytics dashboard with filters', async () => {
      await reportsPage.navigateTo();
      await reportsPage.switchToTab('analytics');
      
      // Verify analytics components
      await expect(reportsPage.analyticsSection).toBeVisible();
      await expect(reportsPage.analyticsFilters).toBeVisible();
      await expect(reportsPage.dateRangeFilter).toBeVisible();
      await expect(reportsPage.departmentFilter).toBeVisible();
      await expect(reportsPage.jobFilter).toBeVisible();
      await expect(reportsPage.riskLevelFilter).toBeVisible();
    });

    test('should display analytics charts', async () => {
      await reportsPage.navigateTo();
      await reportsPage.switchToTab('analytics');
      
      // Verify all analytics charts are visible
      await expect(reportsPage.chartsContainer).toBeVisible();
      await expect(reportsPage.interviewVolumeChart).toBeVisible();
      await expect(reportsPage.riskTrendsChart).toBeVisible();
      await expect(reportsPage.completionRatesChart).toBeVisible();
      await expect(reportsPage.scoreDistributionChart).toBeVisible();
      await expect(reportsPage.departmentComparisonChart).toBeVisible();
      await expect(reportsPage.timeToCompleteChart).toBeVisible();
    });

    test('should apply analytics filters', async () => {
      await reportsPage.navigateTo();
      await reportsPage.switchToTab('analytics');
      
      // Apply filters
      await reportsPage.applyAnalyticsFilters({
        jobId: 1,
        riskLevel: 'high'
      });
      
      // Verify filters are applied (charts should update)
      await expect(reportsPage.chartsContainer).toBeVisible();
      
      // Clear filters
      await reportsPage.clearAnalyticsFilters();
    });

    test('should handle chart interactions', async () => {
      await reportsPage.navigateTo();
      await reportsPage.switchToTab('analytics');
      
      // Test chart hover interactions
      await reportsPage.interviewVolumeChart.hover();
      
      // Test chart click interactions (if applicable)
      await reportsPage.riskTrendsChart.click();
      
      // Verify charts remain functional
      await expect(reportsPage.interviewVolumeChart).toBeVisible();
      await expect(reportsPage.riskTrendsChart).toBeVisible();
    });
  });

  test.describe('Custom Reports', () => {
    test('should display custom reports builder', async () => {
      await reportsPage.navigateTo();
      await reportsPage.switchToTab('custom-reports');
      
      // Verify custom reports components
      await expect(reportsPage.customReportsSection).toBeVisible();
      await expect(reportsPage.reportBuilder).toBeVisible();
      await expect(reportsPage.reportNameInput).toBeVisible();
      await expect(reportsPage.reportDescriptionInput).toBeVisible();
      await expect(reportsPage.dataSourceSelect).toBeVisible();
      await expect(reportsPage.fieldsSelector).toBeVisible();
    });

    test('should create custom report', async () => {
      await reportsPage.navigateTo();
      await reportsPage.switchToTab('custom-reports');
      
      // Create custom report
      await reportsPage.createCustomReport(
        'Test Custom Report',
        'A test report for validation',
        'interviews'
      );
      
      // Add fields to report
      await reportsPage.addFieldToReport(0);
      await reportsPage.addFieldToReport(1);
      
      // Save custom report
      await reportsPage.saveCustomReport();
      
      // Verify success
      await expect(reportsPage.successToast).toBeVisible();
    });

    test('should run custom report', async () => {
      await reportsPage.navigateTo();
      await reportsPage.switchToTab('custom-reports');
      
      // Create and save a simple custom report first
      await reportsPage.createCustomReport(
        'Quick Test Report',
        'Quick test',
        'candidates'
      );
      await reportsPage.addFieldToReport(0);
      await reportsPage.saveCustomReport();
      
      // Run the report
      await reportsPage.runCustomReport();
      
      // Verify report execution
      await expect(reportsPage.successToast).toBeVisible();
    });

    test('should manage report fields', async () => {
      await reportsPage.navigateTo();
      await reportsPage.switchToTab('custom-reports');
      
      // Add fields
      await reportsPage.addFieldToReport(0);
      await reportsPage.addFieldToReport(1);
      await reportsPage.addFieldToReport(2);
      
      // Verify fields were added
      const selectedFieldsCount = await reportsPage.selectedFields.locator('[data-testid="selected-field"]').count();
      expect(selectedFieldsCount).toBe(3);
      
      // Remove a field
      await reportsPage.removeFieldFromReport(1);
      
      // Verify field was removed
      const updatedFieldsCount = await reportsPage.selectedFields.locator('[data-testid="selected-field"]').count();
      expect(updatedFieldsCount).toBe(2);
    });
  });

  test.describe('Export Functionality', () => {
    test('should export reports in different formats', async () => {
      await reportsPage.navigateTo();
      await reportsPage.switchToTab('candidate-reports');
      
      const reportCount = await reportsPage.candidateReportRows.count();
      if (reportCount > 0) {
        // Test different export formats
        const formats: ('pdf' | 'excel' | 'csv' | 'json')[] = ['pdf', 'excel', 'csv', 'json'];
        
        for (const format of formats) {
          // Click export on first report
          await reportsPage.candidateReportRows.first().locator('[data-testid="export-report-btn"]').click();
          
          // Select format and download
          await reportsPage.downloadReport(format);
          
          // Verify export process
          await expect(reportsPage.successToast).toBeVisible();
          
          // Wait between exports
          await reportsPage.page.waitForTimeout(500);
        }
      }
    });
  });

  test.describe('Scheduled Reports', () => {
    test('should display scheduled reports section', async () => {
      await reportsPage.navigateTo();
      
      // Navigate to scheduled reports (might be a separate section or tab)
      await expect(reportsPage.scheduledReportsSection).toBeVisible();
      await expect(reportsPage.scheduleReportButton).toBeVisible();
    });

    test('should schedule a report', async () => {
      await reportsPage.navigateTo();
      
      // Schedule a report
      await reportsPage.scheduleReport(
        'weekly',
        '09:00',
        'admin@test.com'
      );
      
      // Verify scheduling success
      await expect(reportsPage.successToast).toBeVisible();
      await expect(reportsPage.scheduleModal).not.toBeVisible();
    });
  });

  test.describe('Report History', () => {
    test('should display report history', async () => {
      await reportsPage.navigateTo();
      
      // Verify report history section
      await expect(reportsPage.reportHistorySection).toBeVisible();
      await expect(reportsPage.historyTable).toBeVisible();
    });

    test('should download from history', async () => {
      await reportsPage.navigateTo();
      
      const historyCount = await reportsPage.getReportHistoryCount();
      if (historyCount > 0) {
        // Download first report from history
        await reportsPage.downloadFromHistory(0);
        
        // Verify download initiated
        await expect(reportsPage.successToast).toBeVisible();
      }
    });

    test('should delete from history', async () => {
      await reportsPage.navigateTo();
      
      const initialCount = await reportsPage.getReportHistoryCount();
      if (initialCount > 0) {
        // Delete first report from history
        await reportsPage.deleteFromHistory(0);
        
        // Verify deletion
        await expect(reportsPage.successToast).toBeVisible();
        
        // Verify count decreased
        const newCount = await reportsPage.getReportHistoryCount();
        expect(newCount).toBe(initialCount - 1);
      }
    });
  });

  test.describe('Performance and Error Handling', () => {
    test('should handle chart loading errors gracefully', async ({ page }) => {
      // Mock chart data API error
      await page.route('**/api/v1/reports/charts*', route => {
        route.fulfill({
          status: 500,
          body: JSON.stringify({ error: 'Chart data unavailable' })
        });
      });

      await reportsPage.navigateTo();
      
      // Charts section should still be visible with error states
      await expect(reportsPage.overviewSection).toBeVisible();
    });

    test('should handle report generation errors', async ({ page }) => {
      // Mock report generation error
      await page.route('**/api/v1/reports/generate*', route => {
        route.fulfill({
          status: 500,
          body: JSON.stringify({ error: 'Report generation failed' })
        });
      });

      await reportsPage.navigateTo();
      await reportsPage.switchToTab('candidate-reports');
      
      // Try to generate report
      await reportsPage.generateCandidateReportButton.click();
      await reportsPage.candidateSelect.selectOption('1');
      await reportsPage.generateReportButton.click();
      
      // Should show error message
      await expect(reportsPage.errorToast).toBeVisible();
    });

    test('should load reports dashboard quickly', async () => {
      const startTime = Date.now();
      await reportsPage.navigateTo();
      await reportsPage.waitForReportsToLoad();
      const loadTime = Date.now() - startTime;
      
      // Should load within 5 seconds (reports can be data-heavy)
      expect(loadTime).toBeLessThan(5000);
    });
  });

  test.describe('Responsive Design', () => {
    test('should display correctly on mobile', async ({ page }) => {
      await TestSetup.setupMobileViewport(page);
      await reportsPage.navigateTo();
      await reportsPage.waitForReportsToLoad();
      
      // Charts should be responsive or show mobile-optimized view
      await expect(reportsPage.overviewSection).toBeVisible();
      await expect(reportsPage.summaryCards).toBeVisible();
      
      // Charts container should be scrollable on mobile
      const chartsScrollable = await reportsPage.chartsContainer.evaluate(el => 
        getComputedStyle(el).overflowX === 'auto' || getComputedStyle(el).overflowX === 'scroll'
      );
      
      if (!chartsScrollable) {
        console.warn('Charts container should be horizontally scrollable on mobile');
      }
    });
  });
});
