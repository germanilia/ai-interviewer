import { test, expect } from '@playwright/test';
import { QuestionsPage } from '../pages/QuestionsPage';
import { loginAs, clearAuth } from '../utils/auth';


test.describe('Questions Management', () => {
  let questionsPage: QuestionsPage;

  test.beforeEach(async ({ page }) => {
    await clearAuth(page);
    questionsPage = new QuestionsPage(page);
    // Login as admin for questions management features
    await loginAs(page, 'ADMIN');
  });

  test.describe('Questions List and Categories', () => {
    test('should display questions table with proper structure', async () => {
      await questionsPage.navigateTo();
      await questionsPage.waitForQuestionsToLoad();

      // Debug: Check if we're on the right page
      const currentUrl = questionsPage.page.url();
      console.log('Current URL:', currentUrl);

      // Debug: Check if questions section is visible
      const questionsVisible = await questionsPage.questionsSection.isVisible();
      console.log('Questions section visible:', questionsVisible);

      // Debug: Check question count
      const questionCount = await questionsPage.getQuestionCount();
      console.log('Question count:', questionCount);

      // Verify main components
      await expect(questionsPage.questionsSection).toBeVisible();

      if (questionCount > 0) {
        await expect(questionsPage.questionsTable).toBeVisible();
        await expect(questionsPage.toolbar).toBeVisible();

        // Verify table headers
        await expect(questionsPage.titleHeader).toBeVisible();
        await expect(questionsPage.categoryHeader).toBeVisible();
        await expect(questionsPage.importanceHeader).toBeVisible();
        await expect(questionsPage.createdByHeader).toBeVisible();
        await expect(questionsPage.createdDateHeader).toBeVisible();
        await expect(questionsPage.actionsHeader).toBeVisible();
      } else {
        // If no questions, check for empty state
        await expect(questionsPage.emptyState).toBeVisible();
      }
    });

    test('should display category tabs', async () => {
      await questionsPage.navigateTo();
      await questionsPage.waitForQuestionsToLoad();
      
      // Verify all category tabs are visible
      await expect(questionsPage.categoryTabs).toBeVisible();
      await expect(questionsPage.allCategoriesTab).toBeVisible();
      await expect(questionsPage.criminalBackgroundTab).toBeVisible();
      await expect(questionsPage.drugUseTab).toBeVisible();
      await expect(questionsPage.ethicsTab).toBeVisible();
      await expect(questionsPage.dismissalsTab).toBeVisible();
      await expect(questionsPage.trustworthinessTab).toBeVisible();
      await expect(questionsPage.generalTab).toBeVisible();
    });

    test('should filter questions by category', async () => {
      await questionsPage.navigateTo();
      await questionsPage.waitForQuestionsToLoad();
      
      const allCount = await questionsPage.getQuestionCount();
      
      // Test criminal background filter
      await questionsPage.filterByCategory('criminal_background');
      const criminalCount = await questionsPage.getQuestionCount();
      
      if (criminalCount > 0) {
        const firstQuestion = await questionsPage.getQuestionByIndex(0);
        expect(firstQuestion.category?.toLowerCase()).toContain('criminal');
      }
      
      // Test ethics filter
      await questionsPage.filterByCategory('ethics');
      const ethicsCount = await questionsPage.getQuestionCount();
      
      if (ethicsCount > 0) {
        const firstQuestion = await questionsPage.getQuestionByIndex(0);
        expect(firstQuestion.category?.toLowerCase()).toContain('ethics');
      }
      
      // Return to all categories
      await questionsPage.filterByCategory('all');
      const finalCount = await questionsPage.getQuestionCount();
      expect(finalCount).toBe(allCount);
    });

    test('should display question data correctly', async () => {
      await questionsPage.navigateTo();
      await questionsPage.waitForQuestionsToLoad();
      
      const questionCount = await questionsPage.getQuestionCount();
      if (questionCount > 0) {
        const firstQuestion = await questionsPage.getQuestionByIndex(0);
        
        // Verify question data structure
        expect(firstQuestion.title).toBeTruthy();
        expect(firstQuestion.category).toBeTruthy();
        expect(firstQuestion.importance).toBeTruthy();
        expect(firstQuestion.createdBy).toBeTruthy();
        expect(firstQuestion.createdDate).toBeTruthy();
        
        // Verify importance is valid value
        const validImportance = ['optional', 'ask once', 'mandatory'];
        const hasValidImportance = validImportance.some(imp => 
          firstQuestion.importance?.toLowerCase().includes(imp)
        );
        expect(hasValidImportance).toBeTruthy();
      }
    });
  });

  test.describe('Add New Question', () => {
    test('should open add question modal', async () => {
      await questionsPage.navigateTo();
      await questionsPage.waitForQuestionsToLoad();
      
      // Click add question button
      await questionsPage.addQuestionButton.click();
      
      // Verify modal opens
      await expect(questionsPage.addQuestionModal).toBeVisible();
      await expect(questionsPage.modalTitle).toContainText('Add New Question');
      await expect(questionsPage.questionForm).toBeVisible();
      await expect(questionsPage.titleInput).toBeVisible();
      await expect(questionsPage.questionTextArea).toBeVisible();
      await expect(questionsPage.importanceSelect).toBeVisible();
      await expect(questionsPage.categorySelect).toBeVisible();
    });

    test('should create new question successfully', async () => {
      await questionsPage.navigateTo();
      await questionsPage.waitForQuestionsToLoad();

      // Make sure we're on the "All" tab to see all questions
      await questionsPage.allCategoriesTab.click();
      await questionsPage.waitForQuestionsToLoad();

      // Create a unique question title to avoid conflicts
      const uniqueId = Date.now();
      const uniqueTitle = `Test Question ${uniqueId}`;

      // Verify the question doesn't exist yet
      await expect(questionsPage.page.getByText(uniqueTitle)).not.toBeVisible();

      // Open add question modal
      await questionsPage.addQuestionButton.click();

      // Fill form with valid data
      const newQuestion = {
        title: uniqueTitle,
        questionText: 'This is a test question for integrity assessment.',
        instructions: 'Please answer honestly and provide details.',
        importance: 'mandatory' as const,
        category: 'ethics' as const
      };
      
      await questionsPage.fillQuestionForm(newQuestion);
      
      // Submit form
      await questionsPage.submitQuestionForm();
      
      // Verify modal closes (indicating success)
      await expect(questionsPage.addQuestionModal).not.toBeVisible();

      // Wait for questions to reload and verify question appears in list
      await questionsPage.waitForQuestionsToLoad();

      // Make sure we're still on the "All" tab to see all questions
      await questionsPage.allCategoriesTab.click();
      await questionsPage.waitForQuestionsToLoad();

      // Check if pagination controls are visible and search through pages
      const paginationControls = questionsPage.page.getByTestId('pagination-controls');
      const isPaginationVisible = await paginationControls.isVisible();

      if (isPaginationVisible) {
        // Try to find the question on different pages
        let questionFound = false;
        const pageButtons = await questionsPage.page.getByTestId(/page-\d+-btn/).all();

        for (const pageButton of pageButtons) {
          await pageButton.click();
          await questionsPage.waitForQuestionsToLoad();

          if (await questionsPage.page.getByText(uniqueTitle).isVisible()) {
            questionFound = true;
            break;
          }
        }

        if (!questionFound) {
          // Go back to page 1 and try again
          await questionsPage.page.getByTestId('page-1-btn').click();
          await questionsPage.waitForQuestionsToLoad();
        }
      }

      // Verify the question appears in the list
      await expect(questionsPage.page.getByText(uniqueTitle)).toBeVisible({ timeout: 10000 });

      // Verify the question appears in the list
      await expect(questionsPage.page.getByText(newQuestion.title)).toBeVisible();
    });

    test('should validate required fields', async () => {
      await questionsPage.navigateTo();
      await questionsPage.waitForQuestionsToLoad();
      
      // Open add question modal
      await questionsPage.addQuestionButton.click();
      
      // Try to submit empty form
      await questionsPage.submitQuestionForm();
      
      // Verify validation errors for required fields without defaults
      await expect(questionsPage.titleError).toBeVisible();
      await expect(questionsPage.titleError).toContainText('required');
      await expect(questionsPage.questionTextError).toBeVisible();
      await expect(questionsPage.questionTextError).toContainText('required');

      // Importance and category have default values, so no validation errors expected
    });

    test('should validate question text length', async () => {
      await questionsPage.navigateTo();
      await questionsPage.waitForQuestionsToLoad();
      
      // Open add question modal
      await questionsPage.addQuestionButton.click();
      
      // Fill form with very short question text
      await questionsPage.fillQuestionForm({
        title: 'Test',
        questionText: 'Too short',
        importance: 'optional',
        category: 'general'
      });
      
      await questionsPage.submitQuestionForm();
      
      // Verify validation error for question text length
      await expect(questionsPage.questionTextError).toBeVisible();
      await expect(questionsPage.questionTextError).toContainText('at least 20 characters');
    });

    test('should preview question before saving', async () => {
      await questionsPage.navigateTo();
      await questionsPage.waitForQuestionsToLoad();
      
      // Open add question modal
      await questionsPage.addQuestionButton.click();
      
      // Fill form
      const questionData = {
        title: 'Ethics Test Question',
        questionText: 'Have you ever been involved in any ethical violations?',
        instructions: 'Please answer honestly and provide details if applicable.',
        importance: 'mandatory' as const,
        category: 'ethics' as const
      };
      await questionsPage.fillQuestionForm(questionData);
      
      // Click preview button
      await questionsPage.previewButton.click();
      
      // Verify preview modal
      await expect(questionsPage.previewModal).toBeVisible();
      await expect(questionsPage.previewTitle).toContainText(questionData.title);
      await expect(questionsPage.previewQuestionText).toContainText(questionData.questionText);
      await expect(questionsPage.previewInstructions).toContainText(questionData.instructions!);
      await expect(questionsPage.previewImportance).toContainText(questionData.importance);
      await expect(questionsPage.previewCategory).toContainText(questionData.category);
      
      // Close preview
      await questionsPage.closePreviewButton.click();
      await expect(questionsPage.previewModal).not.toBeVisible();
    });
  });

  test.describe('Edit Existing Question', () => {
    test('should open edit question modal', async () => {
      await questionsPage.navigateTo();
      await questionsPage.waitForQuestionsToLoad();
      
      const questionCount = await questionsPage.getQuestionCount();
      if (questionCount > 0) {
        // Click edit on first question
        await questionsPage.editQuestion(0);
        
        // Verify edit modal opens
        await expect(questionsPage.editQuestionModal).toBeVisible();
        await expect(questionsPage.modalTitle).toContainText('Edit Question');
        
        // Form should be pre-filled
        const title = await questionsPage.titleInput.inputValue();
        const questionText = await questionsPage.questionTextArea.inputValue();
        
        expect(title).toBeTruthy();
        expect(questionText).toBeTruthy();
      }
    });

    test('should update question successfully', async () => {
      await questionsPage.navigateTo();
      await questionsPage.waitForQuestionsToLoad();
      
      const questionCount = await questionsPage.getQuestionCount();
      if (questionCount > 0) {
        const originalQuestion = await questionsPage.getQuestionByIndex(0);
        
        // Edit question
        await questionsPage.editQuestion(0);
        
        // Update question data
        const updatedTitle = 'Updated Question Title';
        await questionsPage.titleInput.clear();
        await questionsPage.titleInput.fill(updatedTitle);
        
        // Submit form
        await questionsPage.submitQuestionForm();
        
        // Verify success
        await expect(questionsPage.successToast).toBeVisible();
        await expect(questionsPage.editQuestionModal).not.toBeVisible();
        
        // Verify question is updated in list
        await questionsPage.page.reload();
        await questionsPage.waitForQuestionsToLoad();
        const updatedQuestion = await questionsPage.getQuestionByIndex(0);
        expect(updatedQuestion.title).toContain(updatedTitle);
      }
    });
  });

  test.describe('Delete Question', () => {
    test('should show delete confirmation modal', async () => {
      await questionsPage.navigateTo();
      await questionsPage.waitForQuestionsToLoad();
      
      const questionCount = await questionsPage.getQuestionCount();
      if (questionCount > 0) {
        // Click delete on first question
        await questionsPage.deleteQuestion(0);
        
        // Verify confirmation modal
        await expect(questionsPage.deleteConfirmationModal).toBeVisible();
        await expect(questionsPage.deleteConfirmationMessage).toBeVisible();
        await expect(questionsPage.confirmDeleteButton).toBeVisible();
        await expect(questionsPage.cancelDeleteButton).toBeVisible();
      }
    });

    test('should delete question successfully', async () => {
      await questionsPage.navigateTo();
      await questionsPage.waitForQuestionsToLoad();
      
      const initialCount = await questionsPage.getQuestionCount();
      if (initialCount > 0) {
        const questionToDelete = await questionsPage.getQuestionByIndex(0);
        
        // Delete question
        await questionsPage.deleteQuestion(0);
        await questionsPage.confirmDeleteButton.click();
        
        // Verify modal closes (indicating success)
        await expect(questionsPage.deleteConfirmationModal).not.toBeVisible();

        // Wait for questions to reload and verify question count decreased
        await questionsPage.waitForQuestionsToLoad();
        const newCount = await questionsPage.getQuestionCount();
        expect(newCount).toBe(initialCount - 1);
      }
    });

    test('should cancel delete operation', async () => {
      await questionsPage.navigateTo();
      await questionsPage.waitForQuestionsToLoad();
      
      const initialCount = await questionsPage.getQuestionCount();
      if (initialCount > 0) {
        // Start delete process
        await questionsPage.deleteQuestion(0);
        
        // Cancel deletion
        await questionsPage.cancelDeleteButton.click();
        
        // Verify modal closes and count unchanged
        await expect(questionsPage.deleteConfirmationModal).not.toBeVisible();
        const finalCount = await questionsPage.getQuestionCount();
        expect(finalCount).toBe(initialCount);
      }
    });
  });

  test.describe('Search and Filtering', () => {
    test('should search questions by title', async () => {
      await questionsPage.navigateTo();
      await questionsPage.waitForQuestionsToLoad();
      
      const initialCount = await questionsPage.getQuestionCount();
      if (initialCount > 0) {
        const firstQuestion = await questionsPage.getQuestionByIndex(0);
        const searchTerm = firstQuestion.title!.split(' ')[0]; // First word
        
        // Search for question
        await questionsPage.searchQuestions(searchTerm);
        
        // Verify filtered results
        const filteredCount = await questionsPage.getQuestionCount();
        expect(filteredCount).toBeLessThanOrEqual(initialCount);
        
        // Verify search results contain the search term
        if (filteredCount > 0) {
          const firstResult = await questionsPage.getQuestionByIndex(0);
          expect(firstResult.title!.toLowerCase()).toContain(searchTerm.toLowerCase());
        }
      }
    });

    test('should clear search results', async () => {
      await questionsPage.navigateTo();
      await questionsPage.waitForQuestionsToLoad();
      
      const initialCount = await questionsPage.getQuestionCount();
      
      // Perform search
      await questionsPage.searchQuestions('test');
      const searchCount = await questionsPage.getQuestionCount();
      
      // Clear search
      await questionsPage.clearSearch();
      
      // Verify all questions are shown again
      const clearedCount = await questionsPage.getQuestionCount();
      expect(clearedCount).toBe(initialCount);
    });

    test('should handle no search results', async () => {
      await questionsPage.navigateTo();
      await questionsPage.waitForQuestionsToLoad();
      
      // Search for non-existent question
      await questionsPage.searchQuestions('nonexistentquestion12345');
      
      // Should show empty state or no results message
      const resultCount = await questionsPage.getQuestionCount();
      expect(resultCount).toBe(0);
      
      // Should show appropriate message
      await expect(questionsPage.emptyState).toBeVisible();
    });
  });

  test.describe('Question Preview', () => {
    test('should preview question from list', async () => {
      await questionsPage.navigateTo();
      await questionsPage.waitForQuestionsToLoad();
      
      const questionCount = await questionsPage.getQuestionCount();
      if (questionCount > 0) {
        const question = await questionsPage.getQuestionByIndex(0);
        
        // Preview question
        await questionsPage.previewQuestion(0);
        
        // Verify preview modal
        await expect(questionsPage.previewModal).toBeVisible();
        await expect(questionsPage.previewTitle).toContainText(question.title!);
        await expect(questionsPage.previewCategory).toContainText(question.category!);
        await expect(questionsPage.previewImportance).toContainText(question.importance!);
        
        // Close preview
        await questionsPage.closePreviewButton.click();
        await expect(questionsPage.previewModal).not.toBeVisible();
      }
    });
  });



  test.describe('Bulk Operations', () => {
    test('should select multiple questions', async () => {
      await questionsPage.navigateTo();
      await questionsPage.waitForQuestionsToLoad();
      
      const questionCount = await questionsPage.getQuestionCount();
      if (questionCount > 1) {
        // Select first two questions
        await questionsPage.selectQuestion(0);
        await questionsPage.selectQuestion(1);
        
        // Verify bulk actions bar appears
        await expect(questionsPage.bulkActionsBar).toBeVisible();
        
        // Verify selected count
        const selectedCount = await questionsPage.getSelectedCount();
        expect(selectedCount).toBe(2);
      }
    });

    test('should select all questions', async () => {
      await questionsPage.navigateTo();
      await questionsPage.waitForQuestionsToLoad();
      
      const questionCount = await questionsPage.getQuestionCount();
      if (questionCount > 0) {
        // Select all questions
        await questionsPage.selectAllQuestions();
        
        // Verify all are selected
        const selectedCount = await questionsPage.getSelectedCount();
        expect(selectedCount).toBe(questionCount);
        
        // Verify bulk actions bar appears
        await expect(questionsPage.bulkActionsBar).toBeVisible();
      }
    });

    test('should bulk delete questions', async () => {
      await questionsPage.navigateTo();
      await questionsPage.waitForQuestionsToLoad();
      
      const questionCount = await questionsPage.getQuestionCount();
      if (questionCount > 1) {
        const initialCount = questionCount;
        
        // Select some questions
        await questionsPage.selectQuestion(0);
        await questionsPage.selectQuestion(1);
        
        // Bulk delete
        await questionsPage.bulkDeleteButton.click();
        
        // Confirm bulk delete
        await expect(questionsPage.bulkDeleteConfirmationModal).toBeVisible();
        await questionsPage.confirmBulkDeleteButton.click();
        
        // Verify success
        await expect(questionsPage.successToast).toBeVisible();
        
        // Verify count decreased
        await questionsPage.page.reload();
        await questionsPage.waitForQuestionsToLoad();
        const newCount = await questionsPage.getQuestionCount();
        expect(newCount).toBe(initialCount - 2);
      }
    });
  });


});
