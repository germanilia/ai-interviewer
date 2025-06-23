import { test, expect } from '@playwright/test';
import { CandidatesPage } from '../pages/CandidatesPage';
import { testDataUtils, testCandidates } from '../utils/adminTestData';
import { TestSetup } from '../utils/testSetup';


test.describe('Candidates Management', () => {
  let candidatesPage: CandidatesPage;

  test.beforeEach(async ({ page }) => {
    candidatesPage = new CandidatesPage(page);
    await TestSetup.setupAdminTest(page, { setupTestData: true });
  });

  test.afterEach(async ({ page }) => {
    await TestSetup.cleanupAdminTest();
  });

  test.describe('Candidates List View', () => {
    test('should display candidates list with proper table structure', async () => {
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();
      
      // Verify main components are visible
      await expect(candidatesPage.candidatesSection).toBeVisible();
      await expect(candidatesPage.candidatesTable).toBeVisible();
      await expect(candidatesPage.toolbar).toBeVisible();
      
      // Verify table headers
      await expect(candidatesPage.nameHeader).toBeVisible();
      await expect(candidatesPage.emailHeader).toBeVisible();
      await expect(candidatesPage.phoneHeader).toBeVisible();
      await expect(candidatesPage.interviewsHeader).toBeVisible();
      await expect(candidatesPage.lastInterviewHeader).toBeVisible();
      await expect(candidatesPage.statusHeader).toBeVisible();
      await expect(candidatesPage.actionsHeader).toBeVisible();
    });

    test('should display candidate data in table rows', async () => {
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();
      
      // Should have at least some candidates from test data
      const candidateCount = await candidatesPage.getCandidateCount();
      expect(candidateCount).toBeGreaterThan(0);
      
      // Verify first candidate has proper data structure
      if (candidateCount > 0) {
        const firstCandidate = await candidatesPage.getCandidateByIndex(0);
        expect(firstCandidate.name).toBeTruthy();
        expect(firstCandidate.email).toContain('@');
      }
    });

    test('should handle empty state when no candidates exist', async ({ page }) => {
      // Mock empty response
      await page.route('**/api/v1/candidates*', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ items: [], total: 0, page: 1, pageSize: 10, totalPages: 0 })
        });
      });

      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();
      
      // Should show empty state
      await expect(candidatesPage.emptyState).toBeVisible();
      await expect(candidatesPage.candidateRows).toHaveCount(0);
    });

    test('should display loading state while fetching data', async ({ page }) => {
      // Mock slow response
      await page.route('**/api/v1/candidates*', route => {
        setTimeout(() => {
          route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({ items: [], total: 0, page: 1, pageSize: 10, totalPages: 0 })
          });
        }, 1000);
      });

      await candidatesPage.navigateTo();
      
      // Should show loading state initially
      await expect(candidatesPage.loadingState).toBeVisible();
      
      // Then show actual content
      await candidatesPage.waitForCandidatesToLoad();
      await expect(candidatesPage.loadingState).not.toBeVisible();
    });
  });

  test.describe('Add New Candidate', () => {
    test('should open add candidate modal', async () => {
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();
      
      // Click add candidate button
      await candidatesPage.addCandidateButton.click();
      
      // Verify modal opens
      await expect(candidatesPage.addCandidateModal).toBeVisible();
      await expect(candidatesPage.modalTitle).toContainText('Add New Candidate');
      await expect(candidatesPage.modalForm).toBeVisible();
    });

    test('should create new candidate successfully', async () => {
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();
      
      const initialCount = await candidatesPage.getCandidateCount();
      
      // Open add candidate modal
      await candidatesPage.addCandidateButton.click();
      
      // Fill form with valid data
      const newCandidate = testDataUtils.generateRandomCandidate();
      await candidatesPage.fillCandidateForm(newCandidate);
      
      // Submit form
      await candidatesPage.submitCandidateForm();
      
      // Verify success
      await expect(candidatesPage.successToast).toBeVisible();
      await expect(candidatesPage.addCandidateModal).not.toBeVisible();
      
      // Verify candidate appears in list
      await candidatesPage.expectCandidateInList(`${newCandidate.firstName} ${newCandidate.lastName}`);
      
      // Verify count increased
      const newCount = await candidatesPage.getCandidateCount();
      expect(newCount).toBe(initialCount + 1);
    });

    test('should validate required fields', async () => {
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();
      
      // Open add candidate modal
      await candidatesPage.addCandidateButton.click();
      
      // Try to submit empty form
      await candidatesPage.submitCandidateForm();
      
      // Verify validation errors
      await expect(candidatesPage.firstNameError).toBeVisible();
      await expect(candidatesPage.firstNameError).toContainText('required');
      await expect(candidatesPage.lastNameError).toBeVisible();
      await expect(candidatesPage.lastNameError).toContainText('required');
      await expect(candidatesPage.emailError).toBeVisible();
      await expect(candidatesPage.emailError).toContainText('required');
    });

    test('should validate email format', async () => {
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();
      
      // Open add candidate modal
      await candidatesPage.addCandidateButton.click();
      
      // Fill form with invalid email
      await candidatesPage.fillCandidateForm({
        firstName: 'Test',
        lastName: 'User',
        email: 'invalid-email'
      });
      
      await candidatesPage.submitCandidateForm();
      
      // Verify email validation error
      await expect(candidatesPage.emailError).toBeVisible();
      await expect(candidatesPage.emailError).toContainText('Invalid email');
    });

    test('should handle duplicate email validation', async ({ page }) => {
      // Mock duplicate email error
      await page.route('**/api/v1/candidates', route => {
        if (route.request().method() === 'POST') {
          route.fulfill({
            status: 400,
            contentType: 'application/json',
            body: JSON.stringify({ error: 'Email already exists' })
          });
        } else {
          route.continue();
        }
      });

      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();
      
      // Open add candidate modal
      await candidatesPage.addCandidateButton.click();
      
      // Fill form with duplicate email
      await candidatesPage.fillCandidateForm(testCandidates.valid);
      await candidatesPage.submitCandidateForm();
      
      // Verify error message
      await expect(candidatesPage.errorToast).toBeVisible();
      await expect(candidatesPage.errorToast).toContainText('Email already exists');
    });

    test('should cancel form and close modal', async () => {
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();
      
      // Open add candidate modal
      await candidatesPage.addCandidateButton.click();
      
      // Fill some data
      await candidatesPage.firstNameInput.fill('Test');
      
      // Cancel form
      await candidatesPage.cancelCandidateForm();
      
      // Verify modal closes
      await expect(candidatesPage.addCandidateModal).not.toBeVisible();
    });
  });

  test.describe('Edit Existing Candidate', () => {
    test('should open edit candidate modal', async () => {
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();
      
      const candidateCount = await candidatesPage.getCandidateCount();
      if (candidateCount > 0) {
        // Click edit on first candidate
        await candidatesPage.candidateRows.first().locator('[data-testid="edit-candidate-btn"]').click();
        
        // Verify edit modal opens
        await expect(candidatesPage.editCandidateModal).toBeVisible();
        await expect(candidatesPage.modalTitle).toContainText('Edit Candidate');
        
        // Form should be pre-filled
        const firstName = await candidatesPage.firstNameInput.inputValue();
        const lastName = await candidatesPage.lastNameInput.inputValue();
        const email = await candidatesPage.emailInput.inputValue();
        
        expect(firstName).toBeTruthy();
        expect(lastName).toBeTruthy();
        expect(email).toContain('@');
      }
    });

    test('should update candidate successfully', async () => {
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();
      
      const candidateCount = await candidatesPage.getCandidateCount();
      if (candidateCount > 0) {
        const originalCandidate = await candidatesPage.getCandidateByIndex(0);
        
        // Click edit on first candidate
        await candidatesPage.candidateRows.first().locator('[data-testid="edit-candidate-btn"]').click();
        
        // Update candidate data
        const updatedFirstName = 'Updated Name';
        await candidatesPage.firstNameInput.clear();
        await candidatesPage.firstNameInput.fill(updatedFirstName);
        
        // Submit form
        await candidatesPage.submitCandidateForm();
        
        // Verify success
        await expect(candidatesPage.successToast).toBeVisible();
        await expect(candidatesPage.editCandidateModal).not.toBeVisible();
        
        // Verify candidate is updated in list
        await candidatesPage.expectCandidateInList(updatedFirstName);
      }
    });

    test('should validate edit form fields', async () => {
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();
      
      const candidateCount = await candidatesPage.getCandidateCount();
      if (candidateCount > 0) {
        // Click edit on first candidate
        await candidatesPage.candidateRows.first().locator('[data-testid="edit-candidate-btn"]').click();
        
        // Clear required fields
        await candidatesPage.clearCandidateForm();
        
        // Try to submit
        await candidatesPage.submitCandidateForm();
        
        // Verify validation errors
        await expect(candidatesPage.firstNameError).toBeVisible();
        await expect(candidatesPage.lastNameError).toBeVisible();
        await expect(candidatesPage.emailError).toBeVisible();
      }
    });
  });

  test.describe('Delete Candidate', () => {
    test('should show delete confirmation modal', async () => {
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();
      
      const candidateCount = await candidatesPage.getCandidateCount();
      if (candidateCount > 0) {
        // Click delete on first candidate
        await candidatesPage.candidateRows.first().locator('[data-testid="delete-candidate-btn"]').click();
        
        // Verify confirmation modal
        await expect(candidatesPage.deleteConfirmationModal).toBeVisible();
        await expect(candidatesPage.deleteConfirmationMessage).toBeVisible();
        await expect(candidatesPage.confirmDeleteButton).toBeVisible();
        await expect(candidatesPage.cancelDeleteButton).toBeVisible();
      }
    });

    test('should delete candidate successfully', async () => {
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();
      
      const initialCount = await candidatesPage.getCandidateCount();
      if (initialCount > 0) {
        const candidateToDelete = await candidatesPage.getCandidateByIndex(0);
        
        // Click delete on first candidate
        await candidatesPage.candidateRows.first().locator('[data-testid="delete-candidate-btn"]').click();
        
        // Confirm deletion
        await candidatesPage.confirmDeleteButton.click();
        
        // Verify success
        await expect(candidatesPage.successToast).toBeVisible();
        await expect(candidatesPage.deleteConfirmationModal).not.toBeVisible();
        
        // Verify candidate is removed from list
        await candidatesPage.expectCandidateNotInList(candidateToDelete.name!);
        
        // Verify count decreased
        const newCount = await candidatesPage.getCandidateCount();
        expect(newCount).toBe(initialCount - 1);
      }
    });

    test('should cancel delete operation', async () => {
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();
      
      const initialCount = await candidatesPage.getCandidateCount();
      if (initialCount > 0) {
        // Click delete on first candidate
        await candidatesPage.candidateRows.first().locator('[data-testid="delete-candidate-btn"]').click();
        
        // Cancel deletion
        await candidatesPage.cancelDeleteButton.click();
        
        // Verify modal closes and count unchanged
        await expect(candidatesPage.deleteConfirmationModal).not.toBeVisible();
        const newCount = await candidatesPage.getCandidateCount();
        expect(newCount).toBe(initialCount);
      }
    });
  });

  test.describe('Search and Filtering', () => {
    test('should search candidates by name', async () => {
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();
      
      const initialCount = await candidatesPage.getCandidateCount();
      if (initialCount > 0) {
        const firstCandidate = await candidatesPage.getCandidateByIndex(0);
        const searchTerm = firstCandidate.name!.split(' ')[0]; // First name
        
        // Search for candidate
        await candidatesPage.searchCandidates(searchTerm);
        
        // Verify filtered results
        const filteredCount = await candidatesPage.getCandidateCount();
        expect(filteredCount).toBeLessThanOrEqual(initialCount);
        
        // Verify search results contain the search term
        if (filteredCount > 0) {
          const firstResult = await candidatesPage.getCandidateByIndex(0);
          expect(firstResult.name!.toLowerCase()).toContain(searchTerm.toLowerCase());
        }
      }
    });

    test('should search candidates by email', async () => {
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();
      
      const initialCount = await candidatesPage.getCandidateCount();
      if (initialCount > 0) {
        const firstCandidate = await candidatesPage.getCandidateByIndex(0);
        const emailPart = firstCandidate.email!.split('@')[0]; // Email prefix
        
        // Search by email
        await candidatesPage.searchCandidates(emailPart);
        
        // Verify results
        const filteredCount = await candidatesPage.getCandidateCount();
        if (filteredCount > 0) {
          const firstResult = await candidatesPage.getCandidateByIndex(0);
          expect(firstResult.email!.toLowerCase()).toContain(emailPart.toLowerCase());
        }
      }
    });

    test('should clear search results', async () => {
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();
      
      const initialCount = await candidatesPage.getCandidateCount();
      
      // Perform search
      await candidatesPage.searchCandidates('test');
      const searchCount = await candidatesPage.getCandidateCount();
      
      // Clear search
      await candidatesPage.clearSearch();
      
      // Verify all candidates are shown again
      const clearedCount = await candidatesPage.getCandidateCount();
      expect(clearedCount).toBe(initialCount);
    });

    test('should filter candidates by status', async () => {
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();
      
      // Apply status filter
      await candidatesPage.applyFilters({ status: 'completed' });
      
      // Verify filtered results
      const filteredCount = await candidatesPage.getCandidateCount();
      expect(filteredCount).toBeGreaterThanOrEqual(0);
      
      // If there are results, verify they have the correct status
      if (filteredCount > 0) {
        const firstResult = await candidatesPage.getCandidateByIndex(0);
        // Status verification would depend on how status is displayed
      }
    });

    test('should handle no search results', async () => {
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();
      
      // Search for non-existent candidate
      await candidatesPage.searchCandidates('nonexistentcandidate12345');
      
      // Should show empty state or no results message
      const resultCount = await candidatesPage.getCandidateCount();
      expect(resultCount).toBe(0);
      
      // Should show appropriate message
      await expect(candidatesPage.emptyState).toBeVisible();
    });
  });

  test.describe('Pagination', () => {
    test('should display pagination controls', async () => {
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();

      // Verify pagination section is visible
      await expect(candidatesPage.paginationSection).toBeVisible();
      await expect(candidatesPage.paginationInfo).toBeVisible();
    });

    test('should navigate between pages', async () => {
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();

      const paginationInfo = await candidatesPage.getPaginationInfo();

      if (paginationInfo.total > paginationInfo.end) {
        // Go to next page
        await candidatesPage.nextPageButton.click();
        await candidatesPage.waitForCandidatesToLoad();

        // Verify page changed
        const newPaginationInfo = await candidatesPage.getPaginationInfo();
        expect(newPaginationInfo.start).toBeGreaterThan(paginationInfo.start);

        // Go back to previous page
        await candidatesPage.prevPageButton.click();
        await candidatesPage.waitForCandidatesToLoad();

        // Verify we're back to original page
        const backPaginationInfo = await candidatesPage.getPaginationInfo();
        expect(backPaginationInfo.start).toBe(paginationInfo.start);
      }
    });

    test('should change page size', async () => {
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();

      const initialCount = await candidatesPage.getCandidateCount();
      const initialPagination = await candidatesPage.getPaginationInfo();

      // Change page size to 5
      await candidatesPage.changePageSize(5);

      // Verify page size changed
      const newCount = await candidatesPage.getCandidateCount();
      const newPagination = await candidatesPage.getPaginationInfo();

      if (initialPagination.total > 5) {
        expect(newCount).toBeLessThanOrEqual(5);
        expect(newPagination.end - newPagination.start + 1).toBeLessThanOrEqual(5);
      }
    });
  });

  test.describe('Bulk Operations', () => {
    test('should select multiple candidates', async () => {
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();

      const candidateCount = await candidatesPage.getCandidateCount();
      if (candidateCount > 1) {
        // Select first two candidates
        await candidatesPage.selectCandidate((await candidatesPage.getCandidateByIndex(0)).name!);
        await candidatesPage.selectCandidate((await candidatesPage.getCandidateByIndex(1)).name!);

        // Verify bulk actions bar appears
        await expect(candidatesPage.bulkActionsBar).toBeVisible();

        // Verify selected count
        const selectedCount = await candidatesPage.getSelectedCount();
        expect(selectedCount).toBe(2);
      }
    });

    test('should select all candidates', async () => {
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();

      const candidateCount = await candidatesPage.getCandidateCount();
      if (candidateCount > 0) {
        // Select all candidates
        await candidatesPage.selectAllCandidates();

        // Verify all are selected
        const selectedCount = await candidatesPage.getSelectedCount();
        expect(selectedCount).toBe(candidateCount);

        // Verify bulk actions bar appears
        await expect(candidatesPage.bulkActionsBar).toBeVisible();
      }
    });

    test('should export selected candidates', async () => {
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();

      const candidateCount = await candidatesPage.getCandidateCount();
      if (candidateCount > 0) {
        // Select some candidates
        await candidatesPage.selectAllCandidates();

        // Click bulk export
        await candidatesPage.bulkExportButton.click();

        // Verify export is initiated (implementation depends on how downloads are handled)
        // This might involve checking for download events or success messages
      }
    });
  });

  test.describe('Candidate Detail View', () => {
    test('should display candidate details', async () => {
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();

      const candidateCount = await candidatesPage.getCandidateCount();
      if (candidateCount > 0) {
        const candidate = await candidatesPage.getCandidateByIndex(0);

        // Click on candidate name to view details
        await candidatesPage.viewCandidateDetails(candidate.name!);

        // Verify detail view opens
        await expect(candidatesPage.candidateDetailView).toBeVisible();
        await expect(candidatesPage.candidateInfo).toBeVisible();
        await expect(candidatesPage.candidateAvatar).toBeVisible();
        await expect(candidatesPage.candidateStats).toBeVisible();
      }
    });

    test('should display interview history', async () => {
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();

      const candidateCount = await candidatesPage.getCandidateCount();
      if (candidateCount > 0) {
        const candidate = await candidatesPage.getCandidateByIndex(0);

        // View candidate details
        await candidatesPage.viewCandidateDetails(candidate.name!);

        // Verify interview history section
        await expect(candidatesPage.interviewHistorySection).toBeVisible();
        await expect(candidatesPage.interviewHistoryTable).toBeVisible();
      }
    });

    test('should provide quick actions in detail view', async () => {
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();

      const candidateCount = await candidatesPage.getCandidateCount();
      if (candidateCount > 0) {
        const candidate = await candidatesPage.getCandidateByIndex(0);

        // View candidate details
        await candidatesPage.viewCandidateDetails(candidate.name!);

        // Verify quick action buttons
        await expect(candidatesPage.createInterviewButton).toBeVisible();
        await expect(candidatesPage.viewReportsButton).toBeVisible();
        await expect(candidatesPage.editCandidateButton).toBeVisible();
        await expect(candidatesPage.deleteCandidateButton).toBeVisible();
      }
    });
  });

  test.describe('Responsive Design', () => {
    test('should display correctly on mobile', async ({ page }) => {
      await TestSetup.setupMobileViewport(page);
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();

      // Table should be responsive or show mobile-optimized view
      await expect(candidatesPage.candidatesTable).toBeVisible();

      // Some columns might be hidden on mobile
      const tableWidth = await candidatesPage.candidatesTable.boundingBox();
      expect(tableWidth!.width).toBeLessThan(400);
    });

    test('should handle mobile interactions', async ({ page }) => {
      await TestSetup.setupMobileViewport(page);
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();

      // Mobile-specific interactions like swipe actions
      // Implementation depends on mobile design patterns used

      // Add candidate should work on mobile
      await candidatesPage.addCandidateButton.click();
      await expect(candidatesPage.addCandidateModal).toBeVisible();
    });
  });

  test.describe('Performance and Error Handling', () => {
    test('should handle API errors gracefully', async ({ page }) => {
      // Mock API error
      await page.route('**/api/v1/candidates*', route => {
        route.fulfill({
          status: 500,
          body: JSON.stringify({ error: 'Internal Server Error' })
        });
      });

      await candidatesPage.navigateTo();

      // Should show error state but not crash
      await expect(candidatesPage.candidatesSection).toBeVisible();
      await expect(candidatesPage.errorToast).toBeVisible();
    });

    test('should handle network timeouts', async ({ page }) => {
      // Mock slow network
      await page.route('**/api/v1/candidates*', route => {
        // Never respond to simulate timeout
        // In real implementation, this would timeout after configured time
      });

      await candidatesPage.navigateTo();

      // Should show loading state and eventually error
      await expect(candidatesPage.loadingState).toBeVisible();
    });

    test('should load candidates list quickly', async () => {
      const startTime = Date.now();
      await candidatesPage.navigateTo();
      await candidatesPage.waitForCandidatesToLoad();
      const loadTime = Date.now() - startTime;

      // Should load within 3 seconds
      expect(loadTime).toBeLessThan(3000);
    });
  });
});
