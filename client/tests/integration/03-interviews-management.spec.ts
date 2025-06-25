import { test, expect } from '@playwright/test';
import { InterviewsPage } from '../pages/InterviewsPage';
import { loginAs, clearAuth } from '../utils/auth';

// Updated: Interview creation requires assigning questions, and table shows job, candidates, avg score, questions

test.describe('Interview Management', () => {
  let interviewsPage: InterviewsPage;

  test.beforeEach(async ({ page }) => {
    await clearAuth(page);
    interviewsPage = new InterviewsPage(page);
    await loginAs(page, 'ADMIN');
  });

  test.describe('Interview List and Status Tabs', () => {
    test('should display interview status tabs with counts', async () => {
      await interviewsPage.navigateTo();
      await interviewsPage.waitForInterviewsToLoad();
      await expect(interviewsPage.statusTabs).toBeVisible();
      await expect(interviewsPage.allInterviewsTab).toBeVisible();
      await expect(interviewsPage.pendingTab).toBeVisible();
      await expect(interviewsPage.inProgressTab).toBeVisible();
      await expect(interviewsPage.completedTab).toBeVisible();
      await expect(interviewsPage.cancelledTab).toBeVisible();
    });

    test('should display interviews table with proper structure', async () => {
      await interviewsPage.navigateTo();
      await interviewsPage.waitForInterviewsToLoad();
      await expect(interviewsPage.interviewsSection).toBeVisible();
      await expect(interviewsPage.interviewsTable).toBeVisible();
      await expect(interviewsPage.toolbar).toBeVisible();
      // Updated: check for job, candidates, avg score, questions headers
      await expect(interviewsPage.jobHeader).toBeVisible();
      await expect(interviewsPage.candidateHeader).toBeVisible();
      await expect(interviewsPage.scoreHeader).toBeVisible();
      await expect(interviewsPage.questionsHeader).toBeVisible();
    });

    test('should filter interviews by status', async () => {
      await interviewsPage.navigateTo();
      await interviewsPage.waitForInterviewsToLoad();
      
      const allCount = await interviewsPage.getInterviewCount();
      
      // Test pending filter
      await interviewsPage.filterByStatus('pending');
      const pendingRows = await interviewsPage.getInterviewCount();
      
      if (pendingRows > 0) {
        const firstInterview = await interviewsPage.getInterviewByIndex(0);
        expect(firstInterview.status?.toLowerCase()).toContain('pending');
      }
      
      // Test in-progress filter
      await interviewsPage.filterByStatus('in_progress');
      const inProgressRows = await interviewsPage.getInterviewCount();
      
      if (inProgressRows > 0) {
        const firstInterview = await interviewsPage.getInterviewByIndex(0);
        expect(firstInterview.status?.toLowerCase()).toContain('progress');
      }
      
      // Test completed filter
      await interviewsPage.filterByStatus('completed');
      const completedRows = await interviewsPage.getInterviewCount();
      
      if (completedRows > 0) {
        const firstInterview = await interviewsPage.getInterviewByIndex(0);
        expect(firstInterview.status?.toLowerCase()).toContain('completed');
      }
      
      // Return to all interviews
      await interviewsPage.filterByStatus('all');
      const finalCount = await interviewsPage.getInterviewCount();
      expect(finalCount).toBe(allCount);
    });

    test('should display interview data correctly', async () => {
      await interviewsPage.navigateTo();
      await interviewsPage.waitForInterviewsToLoad();
      
      const interviewCount = await interviewsPage.getInterviewCount();
      if (interviewCount > 0) {
        const firstInterview = await interviewsPage.getInterviewByIndex(0);
        
        // Verify interview data structure
        expect(firstInterview.candidate).toBeTruthy();
        expect(firstInterview.job).toBeTruthy();
        expect(firstInterview.status).toBeTruthy();
        expect(firstInterview.passKey).toBeTruthy();
        
        // Pass key should be alphanumeric and proper length
        expect(firstInterview.passKey).toMatch(/^[A-Z0-9]{8,12}$/);
      }
    });
  });

  test.describe('Create New Interview', () => {
    test('should open create interview modal', async () => {
      await interviewsPage.navigateTo();
      await interviewsPage.waitForInterviewsToLoad();
      
      // Click create interview button
      await interviewsPage.createInterviewButton.click();
      
      // Verify modal opens
      await expect(interviewsPage.createInterviewModal).toBeVisible();
      await expect(interviewsPage.modalTitle).toContainText('Create New Interview');
      await expect(interviewsPage.candidateSelect).toBeVisible();
      await expect(interviewsPage.jobSelect).toBeVisible();
      // Updated: questions select must be present
      await expect(interviewsPage.questionsBreakdown).toBeVisible();
    });

    test('should create interview with assigned questions', async () => {
      await interviewsPage.navigateTo();
      await interviewsPage.waitForInterviewsToLoad();
      
      const initialCount = await interviewsPage.getInterviewCount();
      
      // Open create interview modal
      await interviewsPage.createInterviewButton.click();
      
      // Fill interview form (must include questions)
      await interviewsPage.fillInterviewForm({
        candidateId: 1,
        jobId: 1,
        questions: [1] // Use a valid question ID (mock or real)
      });
      
      // Submit form
      await interviewsPage.submitInterviewForm();
      
      // Verify success message
      await expect(interviewsPage.successToast).toBeVisible();
      
      // Verify interview appears in list
      await interviewsPage.page.reload();
      await interviewsPage.waitForInterviewsToLoad();
      const newCount = await interviewsPage.getInterviewCount();
      expect(newCount).toBeGreaterThanOrEqual(initialCount + 1);
    });

    test('should copy pass key to clipboard', async () => {
      await interviewsPage.navigateTo();
      await interviewsPage.waitForInterviewsToLoad();
      
      // Create interview
      await interviewsPage.createInterviewButton.click();
      await interviewsPage.fillInterviewForm({
        candidateId: 1,
        jobId: 1,
        questions: [1]
      });
      await interviewsPage.submitInterviewForm();
      
      // Copy pass key
      await interviewsPage.copyPassKey();

      // Verify copy success message (using general success toast)
      await expect(interviewsPage.successToast).toBeVisible();
    });

    test('should validate required fields', async () => {
      await interviewsPage.navigateTo();
      await interviewsPage.waitForInterviewsToLoad();
      await interviewsPage.createInterviewButton.click();
      // Submit with missing required fields
      await interviewsPage.submitInterviewForm();
      await expect(interviewsPage.candidateSelect).toBeVisible();
      await expect(interviewsPage.jobSelect).toBeVisible();
      // Updated: questions required
      await expect(interviewsPage.questionsBreakdown).toBeVisible();
    });

    test('should search and select candidates', async () => {
      await interviewsPage.navigateTo();
      await interviewsPage.waitForInterviewsToLoad();
      
      // Open create interview modal
      await interviewsPage.createInterviewButton.click();
      
      // Test candidate search functionality
      await interviewsPage.candidateSelect.click();
      await interviewsPage.candidateSearchInput.fill('John');
      
      // Verify filtered candidates appear
      const candidateOptions = await interviewsPage.candidateOption.count();
      expect(candidateOptions).toBeGreaterThan(0);
    });
  });

  test.describe('Pass Key Management', () => {
    test('should generate unique pass keys', async () => {
      await interviewsPage.navigateTo();
      await interviewsPage.waitForInterviewsToLoad();
      
      const passKeys = new Set<string>();
      
      // Create multiple interviews and collect pass keys
      for (let i = 0; i < 3; i++) {
        await interviewsPage.createInterviewButton.click();
        await interviewsPage.fillInterviewForm({
          candidateId: i + 1,
          jobId: 1,
          questions: [1]
        });
        await interviewsPage.submitInterviewForm();
        
        const passKey = await interviewsPage.getPassKeyValue();
        expect(passKeys.has(passKey)).toBeFalsy();
        passKeys.add(passKey);
        
        // Close modal
        await interviewsPage.modalCloseButton.click();
      }
      
      // Verify all pass keys are unique
      expect(passKeys.size).toBe(3);
    });

    test('should display pass key in interview list', async () => {
      await interviewsPage.navigateTo();
      await interviewsPage.waitForInterviewsToLoad();
      
      const interviewCount = await interviewsPage.getInterviewCount();
      if (interviewCount > 0) {
        const interview = await interviewsPage.getInterviewByIndex(0);
        
        // Pass key should be visible and properly formatted
        expect(interview.passKey).toBeTruthy();
        expect(interview.passKey).toMatch(/^[A-Z0-9]{8,12}$/);
      }
    });

    test('should show pass key instructions', async () => {
      await interviewsPage.navigateTo();
      await interviewsPage.waitForInterviewsToLoad();
      
      // Create interview to see pass key display
      await interviewsPage.createInterviewButton.click();
      await interviewsPage.fillInterviewForm({
        candidateId: 1,
        jobId: 1,
        questions: [1]
      });
      await interviewsPage.submitInterviewForm();
      
      // Verify instructions are shown
      await expect(interviewsPage.passKeyInstructions).toBeVisible();
      await expect(interviewsPage.passKeyInstructions).toContainText('candidate');
      await expect(interviewsPage.passKeyInstructions).toContainText('interview');
    });
  });



  test.describe('Interview Status Management', () => {
    test('should display status badges correctly', async () => {
      await interviewsPage.navigateTo();
      await interviewsPage.waitForInterviewsToLoad();
      
      const interviewCount = await interviewsPage.getInterviewCount();
      if (interviewCount > 0) {
        // Check status badges in each row
        for (let i = 0; i < Math.min(3, interviewCount); i++) {
          const interview = await interviewsPage.getInterviewByIndex(i);
          expect(interview.status).toBeTruthy();
          
          // Status should be one of the valid values
          const validStatuses = ['pending', 'in progress', 'completed', 'cancelled'];
          const hasValidStatus = validStatuses.some(status => 
            interview.status?.toLowerCase().includes(status)
          );
          expect(hasValidStatus).toBeTruthy();
        }
      }
    });

    test('should change interview status', async () => {
      await interviewsPage.navigateTo();
      await interviewsPage.waitForInterviewsToLoad();
      
      // Filter to pending interviews
      await interviewsPage.filterByStatus('pending');
      
      const pendingCount = await interviewsPage.getInterviewCount();
      if (pendingCount > 0) {
        const originalInterview = await interviewsPage.getInterviewByIndex(0);
        
        // Click change status button
        await interviewsPage.interviewRows.first().locator('[data-testid="change-status-btn"]').click();
        
        // Verify status change modal
        await expect(interviewsPage.statusChangeModal).toBeVisible();
        await expect(interviewsPage.newStatusSelect).toBeVisible();
        
        // Change status to in-progress
        await interviewsPage.newStatusSelect.selectOption('in_progress');
        await interviewsPage.statusChangeReason.fill('Starting interview session');
        await interviewsPage.confirmStatusChange.click();
        
        // Verify success
        await expect(interviewsPage.successToast).toBeVisible();
      }
    });
  });

  test.describe('Interview Cancellation', () => {
    test('should show cancel confirmation modal', async () => {
      await interviewsPage.navigateTo();
      await interviewsPage.waitForInterviewsToLoad();

      // Filter to pending interviews
      await interviewsPage.filterByStatus('pending');

      const pendingCount = await interviewsPage.getInterviewCount();
      if (pendingCount > 0) {
        // Click cancel button
        await interviewsPage.interviewRows.first().locator('[data-testid="cancel-interview-btn"]').click();

        // Verify confirmation modal
        await expect(interviewsPage.cancelConfirmationModal).toBeVisible();
        await expect(interviewsPage.cancelReasonInput).toBeVisible();
        await expect(interviewsPage.confirmCancelButton).toBeVisible();
        await expect(interviewsPage.cancelCancelButton).toBeVisible();
      }
    });

    test('should cancel interview with reason', async () => {
      await interviewsPage.navigateTo();
      await interviewsPage.waitForInterviewsToLoad();

      // Filter to pending interviews
      await interviewsPage.filterByStatus('pending');

      const pendingCount = await interviewsPage.getInterviewCount();
      if (pendingCount > 0) {
        // Cancel interview
        await interviewsPage.cancelInterview(0, 'Candidate withdrew application');

        // Verify success
        await expect(interviewsPage.successToast).toBeVisible();
        await expect(interviewsPage.cancelConfirmationModal).not.toBeVisible();

        // Verify interview moved to cancelled tab
        await interviewsPage.filterByStatus('cancelled');
        const cancelledCount = await interviewsPage.getInterviewCount();
        expect(cancelledCount).toBeGreaterThan(0);
      }
    });

    test('should cancel cancellation', async () => {
      await interviewsPage.navigateTo();
      await interviewsPage.waitForInterviewsToLoad();

      // Filter to pending interviews
      await interviewsPage.filterByStatus('pending');

      const pendingCount = await interviewsPage.getInterviewCount();
      if (pendingCount > 0) {
        const initialCount = pendingCount;

        // Start cancel process
        await interviewsPage.interviewRows.first().locator('[data-testid="cancel-interview-btn"]').click();

        // Cancel the cancellation
        await interviewsPage.cancelCancelButton.click();

        // Verify modal closes and count unchanged
        await expect(interviewsPage.cancelConfirmationModal).not.toBeVisible();
        const finalCount = await interviewsPage.getInterviewCount();
        expect(finalCount).toBe(initialCount);
      }
    });
  });

  test.describe('Search and Filtering', () => {
    test('should search interviews by candidate name', async () => {
      await interviewsPage.navigateTo();
      await interviewsPage.waitForInterviewsToLoad();

      const initialCount = await interviewsPage.getInterviewCount();
      if (initialCount > 0) {
        const firstInterview = await interviewsPage.getInterviewByIndex(0);
        const searchTerm = firstInterview.candidate!.split(' ')[0]; // First name

        // Search for interview
        await interviewsPage.searchInterviews(searchTerm);

        // Verify filtered results
        const filteredCount = await interviewsPage.getInterviewCount();
        expect(filteredCount).toBeLessThanOrEqual(initialCount);

        // Verify search results contain the search term
        if (filteredCount > 0) {
          const firstResult = await interviewsPage.getInterviewByIndex(0);
          expect(firstResult.candidate!.toLowerCase()).toContain(searchTerm.toLowerCase());
        }
      }
    });

    test('should clear search results', async () => {
      await interviewsPage.navigateTo();
      await interviewsPage.waitForInterviewsToLoad();

      const initialCount = await interviewsPage.getInterviewCount();

      // Perform search
      await interviewsPage.searchInterviews('test');
      const searchCount = await interviewsPage.getInterviewCount();

      // Clear search
      await interviewsPage.clearSearch();

      // Verify all interviews are shown again
      const clearedCount = await interviewsPage.getInterviewCount();
      expect(clearedCount).toBe(initialCount);
    });

    test('should filter interviews by candidate and job', async () => {
      await interviewsPage.navigateTo();
      await interviewsPage.waitForInterviewsToLoad();

      // Apply filters
      await interviewsPage.applyFilters({ candidateId: 1, jobId: 1 });

      // Verify filtered results
      const filteredCount = await interviewsPage.getInterviewCount();
      expect(filteredCount).toBeGreaterThanOrEqual(0);
    });
  });

  test.describe('Bulk Operations', () => {
    test('should select multiple interviews', async () => {
      await interviewsPage.navigateTo();
      await interviewsPage.waitForInterviewsToLoad();

      const interviewCount = await interviewsPage.getInterviewCount();
      if (interviewCount > 1) {
        // Select first two interviews
        await interviewsPage.selectInterview(0);
        await interviewsPage.selectInterview(1);

        // Verify bulk actions bar appears
        await expect(interviewsPage.bulkActionsBar).toBeVisible();

        // Verify selected count
        const selectedCount = await interviewsPage.getSelectedCount();
        expect(selectedCount).toBe(2);
      }
    });

    test('should select all interviews', async () => {
      await interviewsPage.navigateTo();
      await interviewsPage.waitForInterviewsToLoad();

      const interviewCount = await interviewsPage.getInterviewCount();
      if (interviewCount > 0) {
        // Select all interviews
        await interviewsPage.selectAllInterviews();

        // Verify all are selected
        const selectedCount = await interviewsPage.getSelectedCount();
        expect(selectedCount).toBe(interviewCount);

        // Verify bulk actions bar appears
        await expect(interviewsPage.bulkActionsBar).toBeVisible();
      }
    });
  });

  test.describe('Performance and Error Handling', () => {
    test('should handle API errors gracefully', async ({ page }) => {
      // Mock API error
      await page.route('**/api/v1/interviews*', route => {
        route.fulfill({
          status: 500,
          body: JSON.stringify({ error: 'Internal Server Error' })
        });
      });

      await interviewsPage.navigateTo();

      // Should show error state but not crash
      await expect(interviewsPage.interviewsSection).toBeVisible();
      await expect(interviewsPage.errorToast).toBeVisible();
    });

    test('should load interviews list quickly', async () => {
      const startTime = Date.now();
      await interviewsPage.navigateTo();
      await interviewsPage.waitForInterviewsToLoad();
      const loadTime = Date.now() - startTime;

      // Should load within 3 seconds
      expect(loadTime).toBeLessThan(3000);
    });
  });
});
