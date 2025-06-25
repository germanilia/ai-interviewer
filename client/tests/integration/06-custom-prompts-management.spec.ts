import { test, expect } from '@playwright/test';
import { CustomPromptsPage } from '../pages/CustomPromptsPage';
import { loginAs, clearAuth } from '../utils/auth';

test.describe('Custom Prompts Management', () => {
  let customPromptsPage: CustomPromptsPage;

  test.beforeEach(async ({ page }) => {
    await clearAuth(page);
    customPromptsPage = new CustomPromptsPage(page);
    await loginAs(page, 'USER');
  });

  test.describe('Page Layout and Navigation', () => {
    test('should display custom prompts page correctly', async () => {
      await customPromptsPage.navigateTo();
      
      // Verify page elements
      await expect(customPromptsPage.pageTitle).toBeVisible();
      await expect(customPromptsPage.pageDescription).toBeVisible();
      await expect(customPromptsPage.createPromptButton).toBeVisible();
      
      // Verify prompt type sections
      await expect(customPromptsPage.page.getByText('Small LLM')).toBeVisible();
      await expect(customPromptsPage.page.getByText('Judge')).toBeVisible();
      await expect(customPromptsPage.page.getByText('Guardrails')).toBeVisible();
    });

    test('should show empty states when no prompts exist', async () => {
      await customPromptsPage.navigateTo();
      await customPromptsPage.waitForPromptsToLoad();
      
      // Check if empty states are shown (depends on existing data)
      const promptCount = await customPromptsPage.getPromptCount();
      if (promptCount === 0) {
        await expect(customPromptsPage.page.getByText('No small llm prompts created yet.')).toBeVisible();
        await expect(customPromptsPage.page.getByText('No judge prompts created yet.')).toBeVisible();
        await expect(customPromptsPage.page.getByText('No guardrails prompts created yet.')).toBeVisible();
      }
    });
  });

  test.describe('Create Custom Prompt', () => {
    test('should open create dialog when clicking create button', async () => {
      await customPromptsPage.navigateTo();
      await customPromptsPage.openCreateDialog();
      
      // Verify dialog is open
      await expect(customPromptsPage.promptDialog).toBeVisible();
      await expect(customPromptsPage.dialogTitle).toContainText('Create Custom Prompt');
      await expect(customPromptsPage.dialogDescription).toContainText('Create a new custom prompt');
      
      // Verify form elements
      await expect(customPromptsPage.promptTypeSelect).toBeVisible();
      await expect(customPromptsPage.promptNameInput).toBeVisible();
      await expect(customPromptsPage.promptDescriptionInput).toBeVisible();
      await expect(customPromptsPage.promptContentInput).toBeVisible();
      await expect(customPromptsPage.promptActiveCheckbox).toBeVisible();
      await expect(customPromptsPage.saveButton).toBeVisible();
      await expect(customPromptsPage.cancelButton).toBeVisible();
    });

    test('should create small LLM prompt successfully', async () => {
      await customPromptsPage.navigateTo();
      
      const uniqueId = Date.now();
      const promptData = {
        promptType: 'small_llm' as const,
        name: `Test Small LLM Prompt ${uniqueId}`,
        content: 'You are a test small LLM prompt for {candidate_name} interviewing for {interview_title}.',
        description: 'A test prompt for small LLM functionality',
        isActive: true
      };
      
      // Verify prompt doesn't exist
      expect(await customPromptsPage.promptExists(promptData.name)).toBeFalsy();
      
      // Create prompt
      await customPromptsPage.createPrompt(promptData);
      
      // Verify success
      await customPromptsPage.waitForSuccessToast();
      
      // Verify prompt appears in the list
      expect(await customPromptsPage.promptExists(promptData.name)).toBeTruthy();
      
      // Verify prompt details
      const prompt = await customPromptsPage.getPromptByName(promptData.name);
      expect(prompt.status).toContain('Active');
    });

    test('should create judge prompt successfully', async () => {
      await customPromptsPage.navigateTo();
      
      const uniqueId = Date.now();
      const promptData = {
        promptType: 'judge' as const,
        name: `Test Judge Prompt ${uniqueId}`,
        content: 'You are a judge prompt reviewing responses for {candidate_name}.',
        description: 'A test prompt for judge functionality',
        isActive: false
      };
      
      await customPromptsPage.createPrompt(promptData);
      await customPromptsPage.waitForSuccessToast();
      
      // Verify prompt appears with correct status
      const prompt = await customPromptsPage.getPromptByName(promptData.name);
      expect(prompt.status).toContain('Inactive');
    });

    test('should create guardrails prompt successfully', async () => {
      await customPromptsPage.navigateTo();
      
      const uniqueId = Date.now();
      const promptData = {
        promptType: 'guardrails' as const,
        name: `Test Guardrails Prompt ${uniqueId}`,
        content: 'You are a guardrails prompt checking content safety for {current_message}.',
        description: 'A test prompt for guardrails functionality'
      };
      
      await customPromptsPage.createPrompt(promptData);
      await customPromptsPage.waitForSuccessToast();
      
      expect(await customPromptsPage.promptExists(promptData.name)).toBeTruthy();
    });

    test('should validate required fields', async () => {
      await customPromptsPage.navigateTo();
      await customPromptsPage.openCreateDialog();
      
      // Try to submit without filling required fields
      await customPromptsPage.saveButton.click();
      
      // Verify validation errors
      expect(await customPromptsPage.verifyValidationError('prompt-name', 'Name is required')).toBeTruthy();
      expect(await customPromptsPage.verifyValidationError('prompt-content', 'Content must be at least 10 characters')).toBeTruthy();
    });

    test('should validate content length', async () => {
      await customPromptsPage.navigateTo();
      await customPromptsPage.openCreateDialog();
      
      // Fill with short content
      await customPromptsPage.promptNameInput.fill('Test Prompt');
      await customPromptsPage.promptContentInput.fill('Short');
      await customPromptsPage.saveButton.click();
      
      // Verify validation error
      expect(await customPromptsPage.verifyValidationError('prompt-content', 'Content must be at least 10 characters')).toBeTruthy();
    });

    test('should cancel creation', async () => {
      await customPromptsPage.navigateTo();
      await customPromptsPage.openCreateDialog();
      
      // Fill some data
      await customPromptsPage.promptNameInput.fill('Test Prompt');
      await customPromptsPage.promptContentInput.fill('Test content for cancellation');
      
      // Cancel
      await customPromptsPage.cancelPromptForm();
      
      // Verify dialog is closed and prompt wasn't created
      await expect(customPromptsPage.promptDialog).not.toBeVisible();
      expect(await customPromptsPage.promptExists('Test Prompt')).toBeFalsy();
    });
  });

  test.describe('Edit Custom Prompt', () => {
    test('should edit prompt successfully', async () => {
      await customPromptsPage.navigateTo();
      
      // Create a prompt first
      const uniqueId = Date.now();
      const originalData = {
        promptType: 'small_llm' as const,
        name: `Original Prompt ${uniqueId}`,
        content: 'Original content for {candidate_name}',
        description: 'Original description'
      };
      
      await customPromptsPage.createPrompt(originalData);
      await customPromptsPage.waitForSuccessToast();
      
      // Edit the prompt
      const updatedData = {
        name: `Updated Prompt ${uniqueId}`,
        content: 'Updated content for {candidate_name} and {interview_title}',
        description: 'Updated description'
      };
      
      await customPromptsPage.editPrompt(originalData.name, updatedData);
      await customPromptsPage.waitForSuccessToast();
      
      // Verify changes
      expect(await customPromptsPage.promptExists(updatedData.name)).toBeTruthy();
      expect(await customPromptsPage.promptExists(originalData.name)).toBeFalsy();
    });

    test('should not allow changing prompt type when editing', async () => {
      await customPromptsPage.navigateTo();
      
      // Create a prompt first
      const uniqueId = Date.now();
      const promptData = {
        promptType: 'judge' as const,
        name: `Judge Prompt ${uniqueId}`,
        content: 'Judge content for testing',
        description: 'Judge description'
      };
      
      await customPromptsPage.createPrompt(promptData);
      await customPromptsPage.waitForSuccessToast();
      
      // Open edit dialog
      await customPromptsPage.openEditDialog(promptData.name);
      
      // Verify prompt type select is disabled
      await expect(customPromptsPage.promptTypeSelect).toBeDisabled();
    });
  });

  test.describe('Delete Custom Prompt', () => {
    test('should delete prompt successfully', async () => {
      await customPromptsPage.navigateTo();
      
      // Create a prompt first
      const uniqueId = Date.now();
      const promptData = {
        promptType: 'guardrails' as const,
        name: `Prompt to Delete ${uniqueId}`,
        content: 'This prompt will be deleted',
        description: 'Temporary prompt for deletion test'
      };
      
      await customPromptsPage.createPrompt(promptData);
      await customPromptsPage.waitForSuccessToast();
      
      // Verify prompt exists
      expect(await customPromptsPage.promptExists(promptData.name)).toBeTruthy();
      
      // Delete the prompt
      await customPromptsPage.deletePrompt(promptData.name);
      await customPromptsPage.waitForSuccessToast();
      
      // Verify prompt is deleted
      expect(await customPromptsPage.promptExists(promptData.name)).toBeFalsy();
    });
  });

  test.describe('Toggle Prompt Status', () => {
    test('should toggle prompt active status', async () => {
      await customPromptsPage.navigateTo();
      
      // Create an active prompt
      const uniqueId = Date.now();
      const promptData = {
        promptType: 'small_llm' as const,
        name: `Toggle Test Prompt ${uniqueId}`,
        content: 'Content for toggle testing',
        isActive: true
      };
      
      await customPromptsPage.createPrompt(promptData);
      await customPromptsPage.waitForSuccessToast();
      
      // Verify initial status
      let prompt = await customPromptsPage.getPromptByName(promptData.name);
      expect(prompt.status).toContain('Active');
      
      // Toggle to inactive
      await customPromptsPage.togglePromptStatus(promptData.name);
      await customPromptsPage.waitForSuccessToast();
      
      // Verify status changed
      prompt = await customPromptsPage.getPromptByName(promptData.name);
      expect(prompt.status).toContain('Inactive');
      
      // Toggle back to active
      await customPromptsPage.togglePromptStatus(promptData.name);
      await customPromptsPage.waitForSuccessToast();
      
      // Verify status changed back
      prompt = await customPromptsPage.getPromptByName(promptData.name);
      expect(prompt.status).toContain('Active');
    });
  });

  test.describe('Empty State Actions', () => {
    test('should create prompt from empty state button', async () => {
      await customPromptsPage.navigateTo();
      await customPromptsPage.waitForPromptsToLoad();
      
      // Check if any empty state exists and click create button
      const isSmallLlmEmpty = await customPromptsPage.isEmptyStateShown('small_llm');
      
      if (isSmallLlmEmpty) {
        await customPromptsPage.clickCreateFirstPrompt('small_llm');
        
        // Verify dialog opens with correct type pre-selected
        await expect(customPromptsPage.promptDialog).toBeVisible();
        await expect(customPromptsPage.dialogTitle).toContainText('Create Custom Prompt');
        
        // The prompt type should be pre-selected or default to small_llm
        // We can verify this by checking if the form can be submitted with just name and content
        await customPromptsPage.promptNameInput.fill('Empty State Test Prompt');
        await customPromptsPage.promptContentInput.fill('Content created from empty state button');
        await customPromptsPage.submitPromptForm();
        
        await customPromptsPage.waitForSuccessToast();
        expect(await customPromptsPage.promptExists('Empty State Test Prompt')).toBeTruthy();
      }
    });
  });

  test.describe('Form Validation Edge Cases', () => {
    test('should handle very long prompt names', async () => {
      await customPromptsPage.navigateTo();
      await customPromptsPage.openCreateDialog();
      
      // Try with name longer than 100 characters
      const longName = 'A'.repeat(101);
      await customPromptsPage.promptNameInput.fill(longName);
      await customPromptsPage.promptContentInput.fill('Valid content for long name test');
      await customPromptsPage.saveButton.click();
      
      // Verify validation error
      expect(await customPromptsPage.verifyValidationError('prompt-name', 'Name must be less than 100 characters')).toBeTruthy();
    });

    test('should handle special characters in prompt content', async () => {
      await customPromptsPage.navigateTo();
      
      const uniqueId = Date.now();
      const promptData = {
        promptType: 'judge' as const,
        name: `Special Chars Prompt ${uniqueId}`,
        content: 'Content with special chars: {candidate_name}, {interview_title}, "quotes", \'single quotes\', & symbols!',
        description: 'Testing special characters handling'
      };
      
      await customPromptsPage.createPrompt(promptData);
      await customPromptsPage.waitForSuccessToast();
      
      expect(await customPromptsPage.promptExists(promptData.name)).toBeTruthy();
    });
  });
});
