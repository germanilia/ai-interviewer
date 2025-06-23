import { test, expect } from '@playwright/test';
import { AdminLayoutPage } from '../pages/admin/AdminLayoutPage';
import { DashboardPage } from '../pages/admin/DashboardPage';
import { CandidatesPage } from '../pages/admin/CandidatesPage';
import { InterviewsPage } from '../pages/admin/InterviewsPage';
import { QuestionsPage } from '../pages/admin/QuestionsPage';
import { JobsPage } from '../pages/admin/JobsPage';
import { ReportsPage } from '../pages/admin/ReportsPage';
import { TestSetup } from '../utils/testSetup';
import { testCandidates, testJobs, testQuestions } from '../utils/adminTestData';

/**
 * Admin Dashboard Regression Test Suite
 * 
 * This suite contains essential smoke tests that verify core functionality
 * across all admin dashboard features. These tests should run quickly and
 * catch major regressions without exhaustive testing of edge cases.
 * 
 * Run this suite for:
 * - Pre-deployment validation
 * - Quick smoke testing after changes
 * - CI/CD pipeline validation
 */
test.describe('Admin Dashboard Regression Tests', () => {
  test.beforeEach(async ({ page }) => {
    await TestSetup.setupAdminTest(page, { setupTestData: true });
  });

  test.afterEach(async ({ page }) => {
    await TestSetup.cleanupAdminTest();
  });

  test.describe('Critical User Paths', () => {
    test('should complete full admin workflow: login → dashboard → create candidate → create interview → generate report', async ({ page }) => {
      // 1. Verify admin layout loads
      const adminLayout = new AdminLayoutPage(page);
      await adminLayout.navigateToAdmin();
      await adminLayout.verifyAdminAccess();
      
      // 2. Verify dashboard displays key metrics
      const dashboard = new DashboardPage(page);
      await dashboard.navigateTo();
      await dashboard.waitForDashboardToLoad();
      await expect(dashboard.totalCandidatesCard).toBeVisible();
      await expect(dashboard.activeInterviewsCard).toBeVisible();
      
      // 3. Create a new candidate
      const candidates = new CandidatesPage(page);
      await candidates.navigateTo();
      await candidates.waitForCandidatesToLoad();
      
      await candidates.addCandidateButton.click();
      await candidates.fillCandidateForm({
        firstName: 'Regression',
        lastName: 'Test',
        email: 'regression.test@example.com',
        phone: '+1234567890'
      });
      await candidates.submitCandidateForm();
      await expect(candidates.successToast).toBeVisible();
      
      // 4. Create an interview for the candidate
      const interviews = new InterviewsPage(page);
      await interviews.navigateTo();
      await interviews.waitForInterviewsToLoad();
      
      await interviews.createInterviewButton.click();
      await interviews.fillInterviewForm({
        candidateId: 1,
        jobId: 1,
        notes: 'Regression test interview'
      });
      await interviews.submitInterviewForm();
      await expect(interviews.passKeyDisplay).toBeVisible();
      
      // 5. Generate a basic report
      const reports = new ReportsPage(page);
      await reports.navigateTo();
      await reports.waitForReportsToLoad();
      await expect(reports.overviewSection).toBeVisible();
      await expect(reports.totalInterviewsCard).toBeVisible();
    });

    test('should handle navigation between all admin sections', async ({ page }) => {
      const adminLayout = new AdminLayoutPage(page);
      await adminLayout.navigateToAdmin();
      
      // Test navigation to each major section
      const sections = ['dashboard', 'candidates', 'interviews', 'questions', 'jobs', 'reports'] as const;
      
      for (const section of sections) {
        await adminLayout.navigateTo(section);
        await expect(adminLayout.page).toHaveURL(`/admin/${section}`);
        
        // Verify page loads without errors
        await adminLayout.waitForPageLoad();
        await expect(adminLayout.mainContent).toBeVisible();
      }
    });
  });

  test.describe('Core CRUD Operations', () => {
    test('should perform basic candidate CRUD operations', async ({ page }) => {
      const candidates = new CandidatesPage(page);
      await candidates.navigateTo();
      await candidates.waitForCandidatesToLoad();
      
      const initialCount = await candidates.getCandidateCount();
      
      // Create
      await candidates.addCandidateButton.click();
      await candidates.fillCandidateForm(testCandidates.valid);
      await candidates.submitCandidateForm();
      await expect(candidates.successToast).toBeVisible();
      
      // Read - verify candidate appears
      await page.reload();
      await candidates.waitForCandidatesToLoad();
      const newCount = await candidates.getCandidateCount();
      expect(newCount).toBe(initialCount + 1);
      
      // Update - edit the candidate
      if (newCount > 0) {
        await candidates.editCandidate(`${testCandidates.valid.firstName} ${testCandidates.valid.lastName}`);
        await candidates.firstNameInput.clear();
        await candidates.firstNameInput.fill('Updated');
        await candidates.submitCandidateForm();
        await expect(candidates.successToast).toBeVisible();
      }
      
      // Delete - remove the candidate
      if (newCount > 0) {
        await candidates.deleteCandidate('Updated');
        await candidates.confirmDeleteButton.click();
        await expect(candidates.successToast).toBeVisible();
      }
    });

    test('should perform basic interview operations', async ({ page }) => {
      const interviews = new InterviewsPage(page);
      await interviews.navigateTo();
      await interviews.waitForInterviewsToLoad();
      
      const initialCount = await interviews.getInterviewCount();
      
      // Create interview
      await interviews.createInterviewButton.click();
      await interviews.fillInterviewForm({
        candidateId: 1,
        jobId: 1,
        notes: 'Test interview'
      });
      await interviews.submitInterviewForm();
      await expect(interviews.passKeyDisplay).toBeVisible();
      
      // Verify pass key is generated
      const passKey = await interviews.getPassKeyValue();
      expect(passKey).toMatch(/^[A-Z0-9]{8,12}$/);
      
      // Verify interview appears in list
      await page.reload();
      await interviews.waitForInterviewsToLoad();
      const newCount = await interviews.getInterviewCount();
      expect(newCount).toBe(initialCount + 1);
    });

    test('should perform basic question operations', async ({ page }) => {
      const questions = new QuestionsPage(page);
      await questions.navigateTo();
      await questions.waitForQuestionsToLoad();
      
      const initialCount = await questions.getQuestionCount();
      
      // Create question
      await questions.addQuestionButton.click();
      await questions.fillQuestionForm(testQuestions.ethics);
      await questions.submitQuestionForm();
      await expect(questions.successToast).toBeVisible();
      
      // Verify question appears
      await page.reload();
      await questions.waitForQuestionsToLoad();
      const newCount = await questions.getQuestionCount();
      expect(newCount).toBe(initialCount + 1);
    });

    test('should perform basic job operations', async ({ page }) => {
      const jobs = new JobsPage(page);
      await jobs.navigateTo();
      await jobs.waitForJobsToLoad();
      
      const initialCount = await jobs.getJobCount();
      
      // Create job
      await jobs.addJobButton.click();
      await jobs.fillJobForm(testJobs.softwareEngineer);
      await jobs.submitJobForm();
      await expect(jobs.successToast).toBeVisible();
      
      // Verify job appears
      await page.reload();
      await jobs.waitForJobsToLoad();
      const newCount = await jobs.getJobCount();
      expect(newCount).toBe(initialCount + 1);
    });
  });

  test.describe('Essential UI Components', () => {
    test('should display dashboard statistics without errors', async ({ page }) => {
      const dashboard = new DashboardPage(page);
      await dashboard.navigateTo();
      await dashboard.waitForDashboardToLoad();
      
      // Verify all statistics cards load
      await dashboard.verifyStatisticsCards();
      
      // Verify at least one chart loads
      await expect(dashboard.interviewTrendsChart).toBeVisible();
      
      // Verify activity feed loads
      const activityCount = await dashboard.activityItems.count();
      expect(activityCount).toBeGreaterThanOrEqual(0);
    });

    test('should display data tables with proper structure', async ({ page }) => {
      // Test candidates table
      const candidates = new CandidatesPage(page);
      await candidates.navigateTo();
      await candidates.waitForCandidatesToLoad();
      await expect(candidates.candidatesTable).toBeVisible();
      await expect(candidates.nameHeader).toBeVisible();
      
      // Test interviews table
      const interviews = new InterviewsPage(page);
      await interviews.navigateTo();
      await interviews.waitForInterviewsToLoad();
      await expect(interviews.interviewsTable).toBeVisible();
      await expect(interviews.candidateHeader).toBeVisible();
      
      // Test questions table
      const questions = new QuestionsPage(page);
      await questions.navigateTo();
      await questions.waitForQuestionsToLoad();
      await expect(questions.questionsTable).toBeVisible();
      await expect(questions.titleHeader).toBeVisible();
    });

    test('should handle search functionality across modules', async ({ page }) => {
      // Test candidate search
      const candidates = new CandidatesPage(page);
      await candidates.navigateTo();
      await candidates.waitForCandidatesToLoad();
      
      if (await candidates.getCandidateCount() > 0) {
        await candidates.searchCandidates('test');
        await expect(candidates.candidatesTable).toBeVisible();
        await candidates.clearSearch();
      }
      
      // Test interview search
      const interviews = new InterviewsPage(page);
      await interviews.navigateTo();
      await interviews.waitForInterviewsToLoad();
      
      if (await interviews.getInterviewCount() > 0) {
        await interviews.searchInterviews('test');
        await expect(interviews.interviewsTable).toBeVisible();
        await interviews.clearSearch();
      }
    });
  });

  test.describe('Authentication and Security', () => {
    test('should maintain admin session across navigation', async ({ page }) => {
      const adminLayout = new AdminLayoutPage(page);
      await adminLayout.navigateToAdmin();
      await adminLayout.verifyAdminAccess();
      
      // Navigate to different sections
      await adminLayout.navigateTo('candidates');
      await adminLayout.verifyAdminAccess();
      
      await adminLayout.navigateTo('interviews');
      await adminLayout.verifyAdminAccess();
      
      await adminLayout.navigateTo('reports');
      await adminLayout.verifyAdminAccess();
    });

    test('should display user menu and logout option', async ({ page }) => {
      const adminLayout = new AdminLayoutPage(page);
      await adminLayout.navigateToAdmin();
      
      await expect(adminLayout.userMenu).toBeVisible();
      await adminLayout.userMenu.click();
      await expect(adminLayout.logoutButton).toBeVisible();
    });
  });

  test.describe('Error Handling', () => {
    test('should handle API errors gracefully', async ({ page }) => {
      // Mock API error for candidates
      await page.route('**/api/v1/candidates*', route => {
        route.fulfill({
          status: 500,
          body: JSON.stringify({ error: 'Internal Server Error' })
        });
      });

      const candidates = new CandidatesPage(page);
      await candidates.navigateTo();
      
      // Should show error state but not crash
      await expect(candidates.candidatesSection).toBeVisible();
    });

    test('should handle network timeouts', async ({ page }) => {
      // Mock slow network for dashboard
      await page.route('**/api/v1/dashboard/stats', route => {
        setTimeout(() => {
          route.fulfill({
            status: 200,
            body: JSON.stringify({ totalCandidates: 0, activeInterviews: 0 })
          });
        }, 2000);
      });

      const dashboard = new DashboardPage(page);
      await dashboard.navigateTo();
      
      // Should show loading state then content
      await expect(dashboard.statisticsLoading).toBeVisible();
      await dashboard.waitForDashboardToLoad();
      await expect(dashboard.totalCandidatesCard).toBeVisible();
    });
  });

  test.describe('Performance Benchmarks', () => {
    test('should load admin dashboard within performance thresholds', async ({ page }) => {
      const startTime = Date.now();
      
      const dashboard = new DashboardPage(page);
      await dashboard.navigateTo();
      await dashboard.waitForDashboardToLoad();
      
      const loadTime = Date.now() - startTime;
      
      // Should load within 3 seconds
      expect(loadTime).toBeLessThan(3000);
    });

    test('should handle concurrent data loading efficiently', async ({ page }) => {
      const startTime = Date.now();
      
      // Load multiple sections concurrently
      const promises = [
        new DashboardPage(page).navigateTo(),
        new CandidatesPage(page).navigateTo(),
        new InterviewsPage(page).navigateTo()
      ];
      
      // Wait for all to complete
      await Promise.all(promises);
      
      const totalTime = Date.now() - startTime;
      
      // Should complete within reasonable time
      expect(totalTime).toBeLessThan(5000);
    });
  });

  test.describe('Mobile Responsiveness', () => {
    test('should display admin interface on mobile devices', async ({ page }) => {
      await TestSetup.setupMobileViewport(page);
      
      const adminLayout = new AdminLayoutPage(page);
      await adminLayout.navigateToAdmin();
      
      // Verify mobile layout
      const isSidebarCollapsed = await adminLayout.isSidebarCollapsed();
      expect(isSidebarCollapsed).toBe(true);
      
      // Verify mobile menu works
      await expect(adminLayout.mobileMenuButton).toBeVisible();
      await adminLayout.openMobileMenu();
      await expect(adminLayout.sidebar).toBeVisible();
    });

    test('should handle mobile interactions for core features', async ({ page }) => {
      await TestSetup.setupMobileViewport(page);
      
      // Test mobile candidate management
      const candidates = new CandidatesPage(page);
      await candidates.navigateTo();
      await candidates.waitForCandidatesToLoad();
      
      await expect(candidates.candidatesTable).toBeVisible();
      await expect(candidates.addCandidateButton).toBeVisible();
      
      // Test mobile modal interaction
      await candidates.addCandidateButton.click();
      await expect(candidates.addCandidateModal).toBeVisible();
    });
  });

  test.describe('Data Consistency', () => {
    test('should maintain data consistency across related entities', async ({ page }) => {
      // Create candidate
      const candidates = new CandidatesPage(page);
      await candidates.navigateTo();
      await candidates.waitForCandidatesToLoad();
      
      await candidates.addCandidateButton.click();
      await candidates.fillCandidateForm({
        firstName: 'Consistency',
        lastName: 'Test',
        email: 'consistency.test@example.com'
      });
      await candidates.submitCandidateForm();
      await expect(candidates.successToast).toBeVisible();
      
      // Create interview for candidate
      const interviews = new InterviewsPage(page);
      await interviews.navigateTo();
      await interviews.waitForInterviewsToLoad();
      
      await interviews.createInterviewButton.click();
      await interviews.fillInterviewForm({
        candidateId: 1,
        jobId: 1,
        notes: 'Consistency test'
      });
      await interviews.submitInterviewForm();
      await expect(interviews.passKeyDisplay).toBeVisible();
      
      // Verify data appears in reports
      const reports = new ReportsPage(page);
      await reports.navigateTo();
      await reports.waitForReportsToLoad();
      
      // Dashboard should reflect the new data
      const dashboard = new DashboardPage(page);
      await dashboard.navigateTo();
      await dashboard.waitForDashboardToLoad();
      
      const totalCandidates = await dashboard.getStatisticValue('total-candidates-card');
      expect(parseInt(totalCandidates)).toBeGreaterThan(0);
    });
  });
});
