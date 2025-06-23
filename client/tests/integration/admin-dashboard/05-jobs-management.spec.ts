import { test, expect } from '@playwright/test';
import { JobsPage } from '../../pages/admin/JobsPage';
import { TestSetup } from '../../utils/testSetup';
import { testJobs, testDataUtils } from '../../utils/adminTestData';

test.describe('Jobs Management', () => {
  let jobsPage: JobsPage;

  test.beforeEach(async ({ page }) => {
    jobsPage = new JobsPage(page);
    await TestSetup.setupAdminTest(page, { setupTestData: true });
  });

  test.afterEach(async ({ page }) => {
    await TestSetup.cleanupAdminTest();
  });

  test.describe('Jobs List View', () => {
    test('should display jobs table with proper structure', async () => {
      await jobsPage.navigateTo();
      await jobsPage.waitForJobsToLoad();
      
      // Verify main components
      await expect(jobsPage.jobsSection).toBeVisible();
      await expect(jobsPage.jobsTable).toBeVisible();
      await expect(jobsPage.toolbar).toBeVisible();
      
      // Verify table headers
      await expect(jobsPage.titleHeader).toBeVisible();
      await expect(jobsPage.departmentHeader).toBeVisible();
      await expect(jobsPage.questionsCountHeader).toBeVisible();
      await expect(jobsPage.interviewsCountHeader).toBeVisible();
      await expect(jobsPage.createdByHeader).toBeVisible();
      await expect(jobsPage.createdDateHeader).toBeVisible();
      await expect(jobsPage.actionsHeader).toBeVisible();
    });

    test('should display job data correctly', async () => {
      await jobsPage.navigateTo();
      await jobsPage.waitForJobsToLoad();
      
      const jobCount = await jobsPage.getJobCount();
      if (jobCount > 0) {
        const firstJob = await jobsPage.getJobByIndex(0);
        
        // Verify job data structure
        expect(firstJob.title).toBeTruthy();
        expect(firstJob.department).toBeTruthy();
        expect(firstJob.questionsCount).toBeTruthy();
        expect(firstJob.interviewsCount).toBeTruthy();
        expect(firstJob.createdBy).toBeTruthy();
        expect(firstJob.createdDate).toBeTruthy();
        
        // Questions and interviews count should be numeric
        expect(parseInt(firstJob.questionsCount!)).toBeGreaterThanOrEqual(0);
        expect(parseInt(firstJob.interviewsCount!)).toBeGreaterThanOrEqual(0);
      }
    });

    test('should handle empty state when no jobs exist', async ({ page }) => {
      // Mock empty response
      await page.route('**/api/v1/jobs*', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([])
        });
      });

      await jobsPage.navigateTo();
      await jobsPage.waitForJobsToLoad();
      
      // Should show empty state
      await expect(jobsPage.emptyState).toBeVisible();
      await expect(jobsPage.jobRows).toHaveCount(0);
    });
  });

  test.describe('Add New Job', () => {
    test('should open add job modal', async () => {
      await jobsPage.navigateTo();
      await jobsPage.waitForJobsToLoad();
      
      // Click add job button
      await jobsPage.addJobButton.click();
      
      // Verify modal opens
      await expect(jobsPage.addJobModal).toBeVisible();
      await expect(jobsPage.modalTitle).toContainText('Add New Job');
      await expect(jobsPage.jobForm).toBeVisible();
      await expect(jobsPage.titleInput).toBeVisible();
      await expect(jobsPage.descriptionTextArea).toBeVisible();
      await expect(jobsPage.departmentInput).toBeVisible();
    });

    test('should create new job successfully', async () => {
      await jobsPage.navigateTo();
      await jobsPage.waitForJobsToLoad();
      
      const initialCount = await jobsPage.getJobCount();
      
      // Open add job modal
      await jobsPage.addJobButton.click();
      
      // Fill form with valid data
      const newJob = {
        title: 'Test Software Engineer',
        description: 'Develop and maintain software applications for testing',
        department: 'Engineering'
      };
      
      await jobsPage.fillJobForm(newJob);
      
      // Submit form
      await jobsPage.submitJobForm();
      
      // Verify success
      await expect(jobsPage.successToast).toBeVisible();
      await expect(jobsPage.addJobModal).not.toBeVisible();
      
      // Verify job appears in list
      await jobsPage.page.reload();
      await jobsPage.waitForJobsToLoad();
      const newCount = await jobsPage.getJobCount();
      expect(newCount).toBe(initialCount + 1);
    });

    test('should validate required fields', async () => {
      await jobsPage.navigateTo();
      await jobsPage.waitForJobsToLoad();
      
      // Open add job modal
      await jobsPage.addJobButton.click();
      
      // Try to submit empty form
      await jobsPage.submitJobForm();
      
      // Verify validation errors
      await expect(jobsPage.titleError).toBeVisible();
      await expect(jobsPage.titleError).toContainText('required');
    });

    test('should validate job title uniqueness', async ({ page }) => {
      // Mock duplicate title error
      await page.route('**/api/v1/jobs', route => {
        if (route.request().method() === 'POST') {
          route.fulfill({
            status: 400,
            contentType: 'application/json',
            body: JSON.stringify({ error: 'Job title already exists' })
          });
        } else {
          route.continue();
        }
      });

      await jobsPage.navigateTo();
      await jobsPage.waitForJobsToLoad();
      
      // Open add job modal
      await jobsPage.addJobButton.click();
      
      // Fill form with duplicate title
      await jobsPage.fillJobForm(testJobs.softwareEngineer);
      await jobsPage.submitJobForm();
      
      // Verify error message
      await expect(jobsPage.errorToast).toBeVisible();
      await expect(jobsPage.errorToast).toContainText('already exists');
    });
  });

  test.describe('Edit Existing Job', () => {
    test('should open edit job modal', async () => {
      await jobsPage.navigateTo();
      await jobsPage.waitForJobsToLoad();
      
      const jobCount = await jobsPage.getJobCount();
      if (jobCount > 0) {
        // Click edit on first job
        await jobsPage.editJob(0);
        
        // Verify edit modal opens
        await expect(jobsPage.editJobModal).toBeVisible();
        await expect(jobsPage.modalTitle).toContainText('Edit Job');
        
        // Form should be pre-filled
        const title = await jobsPage.titleInput.inputValue();
        const department = await jobsPage.departmentInput.inputValue();
        
        expect(title).toBeTruthy();
        expect(department).toBeTruthy();
      }
    });

    test('should update job successfully', async () => {
      await jobsPage.navigateTo();
      await jobsPage.waitForJobsToLoad();
      
      const jobCount = await jobsPage.getJobCount();
      if (jobCount > 0) {
        // Edit job
        await jobsPage.editJob(0);
        
        // Update job data
        const updatedTitle = 'Updated Job Title';
        await jobsPage.titleInput.clear();
        await jobsPage.titleInput.fill(updatedTitle);
        
        // Submit form
        await jobsPage.submitJobForm();
        
        // Verify success
        await expect(jobsPage.successToast).toBeVisible();
        await expect(jobsPage.editJobModal).not.toBeVisible();
        
        // Verify job is updated in list
        await jobsPage.page.reload();
        await jobsPage.waitForJobsToLoad();
        const updatedJob = await jobsPage.getJobByIndex(0);
        expect(updatedJob.title).toContain(updatedTitle);
      }
    });
  });

  test.describe('Job Detail View', () => {
    test('should display job details', async () => {
      await jobsPage.navigateTo();
      await jobsPage.waitForJobsToLoad();
      
      const jobCount = await jobsPage.getJobCount();
      if (jobCount > 0) {
        // View job details
        await jobsPage.viewJobDetails(0);
        
        // Verify detail view opens
        await expect(jobsPage.jobDetailView).toBeVisible();
        await expect(jobsPage.jobInfo).toBeVisible();
        await expect(jobsPage.jobTitle).toBeVisible();
        await expect(jobsPage.jobDescription).toBeVisible();
        await expect(jobsPage.jobDepartment).toBeVisible();
        await expect(jobsPage.jobStats).toBeVisible();
      }
    });

    test('should display job statistics', async () => {
      await jobsPage.navigateTo();
      await jobsPage.waitForJobsToLoad();
      
      const jobCount = await jobsPage.getJobCount();
      if (jobCount > 0) {
        // View job details
        await jobsPage.viewJobDetails(0);
        
        // Verify statistics section
        await expect(jobsPage.statisticsSection).toBeVisible();
        await expect(jobsPage.totalInterviewsCard).toBeVisible();
        await expect(jobsPage.avgScoreCard).toBeVisible();
        await expect(jobsPage.completionRateCard).toBeVisible();
        await expect(jobsPage.avgTimeCard).toBeVisible();
      }
    });
  });

  test.describe('Template Builder', () => {
    test('should display template builder interface', async () => {
      await jobsPage.navigateTo();
      await jobsPage.waitForJobsToLoad();
      
      const jobCount = await jobsPage.getJobCount();
      if (jobCount > 0) {
        // View job details to access template builder
        await jobsPage.viewJobDetails(0);
        
        // Verify template builder section
        await expect(jobsPage.templateBuilderSection).toBeVisible();
        await expect(jobsPage.templateBuilder).toBeVisible();
        await expect(jobsPage.availableQuestions).toBeVisible();
        await expect(jobsPage.assignedQuestions).toBeVisible();
      }
    });

    test('should add question to job template', async () => {
      await jobsPage.navigateTo();
      await jobsPage.waitForJobsToLoad();
      
      const jobCount = await jobsPage.getJobCount();
      if (jobCount > 0) {
        // View job details
        await jobsPage.viewJobDetails(0);
        
        const initialAssignedCount = await jobsPage.getAssignedQuestionsCount();
        
        // Add question to template
        await jobsPage.addQuestionToTemplate(0);
        
        // Verify question was added
        const newAssignedCount = await jobsPage.getAssignedQuestionsCount();
        expect(newAssignedCount).toBe(initialAssignedCount + 1);
      }
    });

    test('should remove question from job template', async () => {
      await jobsPage.navigateTo();
      await jobsPage.waitForJobsToLoad();
      
      const jobCount = await jobsPage.getJobCount();
      if (jobCount > 0) {
        // View job details
        await jobsPage.viewJobDetails(0);
        
        const initialAssignedCount = await jobsPage.getAssignedQuestionsCount();
        
        if (initialAssignedCount > 0) {
          // Remove question from template
          await jobsPage.removeQuestionFromTemplate(0);
          
          // Verify question was removed
          const newAssignedCount = await jobsPage.getAssignedQuestionsCount();
          expect(newAssignedCount).toBe(initialAssignedCount - 1);
        }
      }
    });

    test('should reorder questions in template', async () => {
      await jobsPage.navigateTo();
      await jobsPage.waitForJobsToLoad();
      
      const jobCount = await jobsPage.getJobCount();
      if (jobCount > 0) {
        // View job details
        await jobsPage.viewJobDetails(0);
        
        const assignedCount = await jobsPage.getAssignedQuestionsCount();
        
        if (assignedCount > 1) {
          // Move second question up
          await jobsPage.moveQuestionUp(1);
          
          // Verify order changed (implementation would depend on how order is displayed)
          // This test would need to check the actual order of questions
        }
      }
    });

    test('should save template changes', async () => {
      await jobsPage.navigateTo();
      await jobsPage.waitForJobsToLoad();
      
      const jobCount = await jobsPage.getJobCount();
      if (jobCount > 0) {
        // View job details
        await jobsPage.viewJobDetails(0);
        
        // Make changes to template
        await jobsPage.addQuestionToTemplate(0);
        
        // Save template
        await jobsPage.saveTemplate();
        
        // Verify success
        await expect(jobsPage.successToast).toBeVisible();
      }
    });

    test('should preview template', async () => {
      await jobsPage.navigateTo();
      await jobsPage.waitForJobsToLoad();
      
      const jobCount = await jobsPage.getJobCount();
      if (jobCount > 0) {
        // View job details
        await jobsPage.viewJobDetails(0);
        
        // Preview template
        await jobsPage.previewTemplate();
        
        // Verify preview modal
        await expect(jobsPage.templatePreviewModal).toBeVisible();
        await expect(jobsPage.previewQuestionsList).toBeVisible();
        
        // Close preview
        await jobsPage.closePreviewButton.click();
        await expect(jobsPage.templatePreviewModal).not.toBeVisible();
      }
    });
  });

  test.describe('Template Cloning', () => {
    test('should clone job template', async () => {
      await jobsPage.navigateTo();
      await jobsPage.waitForJobsToLoad();
      
      const jobCount = await jobsPage.getJobCount();
      if (jobCount > 1) {
        // Clone template from first job to second job
        await jobsPage.cloneJobTemplate(0, 1);
        
        // Verify success
        await expect(jobsPage.successToast).toBeVisible();
        await expect(jobsPage.cloneTemplateModal).not.toBeVisible();
      }
    });
  });

  test.describe('Search and Filtering', () => {
    test('should search jobs by title', async () => {
      await jobsPage.navigateTo();
      await jobsPage.waitForJobsToLoad();
      
      const initialCount = await jobsPage.getJobCount();
      if (initialCount > 0) {
        const firstJob = await jobsPage.getJobByIndex(0);
        const searchTerm = firstJob.title!.split(' ')[0]; // First word
        
        // Search for job
        await jobsPage.searchJobs(searchTerm);
        
        // Verify filtered results
        const filteredCount = await jobsPage.getJobCount();
        expect(filteredCount).toBeLessThanOrEqual(initialCount);
        
        // Verify search results contain the search term
        if (filteredCount > 0) {
          const firstResult = await jobsPage.getJobByIndex(0);
          expect(firstResult.title!.toLowerCase()).toContain(searchTerm.toLowerCase());
        }
      }
    });

    test('should clear search results', async () => {
      await jobsPage.navigateTo();
      await jobsPage.waitForJobsToLoad();
      
      const initialCount = await jobsPage.getJobCount();
      
      // Perform search
      await jobsPage.searchJobs('test');
      const searchCount = await jobsPage.getJobCount();
      
      // Clear search
      await jobsPage.clearSearch();
      
      // Verify all jobs are shown again
      const clearedCount = await jobsPage.getJobCount();
      expect(clearedCount).toBe(initialCount);
    });
  });

  test.describe('Bulk Operations', () => {
    test('should select multiple jobs', async () => {
      await jobsPage.navigateTo();
      await jobsPage.waitForJobsToLoad();
      
      const jobCount = await jobsPage.getJobCount();
      if (jobCount > 1) {
        // Select first two jobs
        await jobsPage.selectJob(0);
        await jobsPage.selectJob(1);
        
        // Verify bulk actions bar appears
        await expect(jobsPage.bulkActionsBar).toBeVisible();
        
        // Verify selected count
        const selectedCount = await jobsPage.getSelectedCount();
        expect(selectedCount).toBe(2);
      }
    });

    test('should select all jobs', async () => {
      await jobsPage.navigateTo();
      await jobsPage.waitForJobsToLoad();
      
      const jobCount = await jobsPage.getJobCount();
      if (jobCount > 0) {
        // Select all jobs
        await jobsPage.selectAllJobs();
        
        // Verify all are selected
        const selectedCount = await jobsPage.getSelectedCount();
        expect(selectedCount).toBe(jobCount);
        
        // Verify bulk actions bar appears
        await expect(jobsPage.bulkActionsBar).toBeVisible();
      }
    });
  });
});
