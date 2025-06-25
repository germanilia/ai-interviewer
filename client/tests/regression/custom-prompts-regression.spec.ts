import { test, expect } from '@playwright/test';
import { CustomPromptsPage } from '../pages/CustomPromptsPage';
import { AppLayoutPage } from '../pages/AppLayoutPage';
import { loginAs, clearAuth } from '../utils/auth';

test.describe('Custom Prompts - Regression Tests', () => {
  let customPromptsPage: CustomPromptsPage;
  let appLayoutPage: AppLayoutPage;

  test.beforeEach(async ({ page }) => {
    await clearAuth(page);
    customPromptsPage = new CustomPromptsPage(page);
    appLayoutPage = new AppLayoutPage(page);
    await loginAs(page, 'USER');
  });

  test.describe('Critical User Paths', () => {
    test('should complete basic custom prompts workflow: login → navigate → create → edit → delete', async ({ page }) => {
      // 1. Login and navigate to custom prompts
      await appLayoutPage.navigateTo('custom-prompts');
      await expect(page).toHaveURL('/custom-prompts');
      await customPromptsPage.waitForPageLoad();

      // 2. Verify page loads correctly
      await expect(customPromptsPage.pageTitle).toBeVisible();
      await expect(customPromptsPage.createPromptButton).toBeVisible();

      // 3. Create a new prompt
      const uniqueId = Date.now();
      const promptData = {
        promptType: 'small_llm' as const,
        name: `Regression Test Prompt ${uniqueId}`,
        content: 'This is a regression test prompt for {candidate_name} interviewing for {interview_title}.',
        description: 'Created during regression testing'
      };

      await customPromptsPage.createPrompt(promptData);
      await customPromptsPage.waitForSuccessToast();

      // 4. Verify prompt was created
      expect(await customPromptsPage.promptExists(promptData.name)).toBeTruthy();

      // 5. Edit the prompt
      const updatedData = {
        name: `Updated ${promptData.name}`,
        content: 'Updated content for regression testing',
        description: 'Updated during regression testing'
      };

      await customPromptsPage.editPrompt(promptData.name, updatedData);
      await customPromptsPage.waitForSuccessToast();

      // 6. Verify edit was successful
      expect(await customPromptsPage.promptExists(updatedData.name)).toBeTruthy();

      // 7. Delete the prompt
      await customPromptsPage.deletePrompt(updatedData.name);
      await customPromptsPage.waitForSuccessToast();

      // 8. Verify deletion was successful
      expect(await customPromptsPage.promptExists(updatedData.name)).toBeFalsy();
    });

    test('should handle navigation between custom prompts and other sections', async ({ page }) => {
      await appLayoutPage.navigateToDashboard();

      // Test navigation to custom prompts and back
      const sections = ['custom-prompts', 'dashboard', 'candidates', 'custom-prompts', 'interviews', 'custom-prompts'] as const;

      for (const section of sections) {
        await appLayoutPage.navigateTo(section);
        await expect(page).toHaveURL(`/${section}`);

        // Verify page loads without errors
        await appLayoutPage.waitForPageLoad();
        await expect(appLayoutPage.mainContent).toBeVisible();

        // If it's custom prompts, verify specific elements
        if (section === 'custom-prompts') {
          await expect(customPromptsPage.pageTitle).toBeVisible();
          await expect(customPromptsPage.createPromptButton).toBeVisible();
        }
      }
    });
  });

  test.describe('Essential Features', () => {
    test('should create prompts of all types', async () => {
      await customPromptsPage.navigateTo();

      const promptTypes = ['small_llm', 'judge', 'guardrails'] as const;
      const uniqueId = Date.now();

      for (const promptType of promptTypes) {
        const promptData = {
          promptType,
          name: `${promptType.toUpperCase()} Regression ${uniqueId}`,
          content: `This is a ${promptType} prompt for regression testing with {candidate_name}.`,
          description: `Regression test for ${promptType} prompt type`
        };

        await customPromptsPage.createPrompt(promptData);
        await customPromptsPage.waitForSuccessToast();

        // Verify prompt was created
        expect(await customPromptsPage.promptExists(promptData.name)).toBeTruthy();
      }

      // Verify all prompts exist
      for (const promptType of promptTypes) {
        const promptName = `${promptType.toUpperCase()} Regression ${uniqueId}`;
        expect(await customPromptsPage.promptExists(promptName)).toBeTruthy();
      }
    });

    test('should handle prompt activation correctly', async () => {
      await customPromptsPage.navigateTo();

      const uniqueId = Date.now();
      
      // Create two prompts of the same type
      const prompt1Data = {
        promptType: 'judge' as const,
        name: `Judge Prompt 1 ${uniqueId}`,
        content: 'First judge prompt content',
        isActive: true
      };

      const prompt2Data = {
        promptType: 'judge' as const,
        name: `Judge Prompt 2 ${uniqueId}`,
        content: 'Second judge prompt content',
        isActive: false
      };

      // Create both prompts
      await customPromptsPage.createPrompt(prompt1Data);
      await customPromptsPage.waitForSuccessToast();

      await customPromptsPage.createPrompt(prompt2Data);
      await customPromptsPage.waitForSuccessToast();

      // Verify initial states
      let prompt1 = await customPromptsPage.getPromptByName(prompt1Data.name);
      let prompt2 = await customPromptsPage.getPromptByName(prompt2Data.name);
      expect(prompt1.status).toContain('Active');
      expect(prompt2.status).toContain('Inactive');

      // Activate the second prompt (should deactivate the first)
      await customPromptsPage.togglePromptStatus(prompt2Data.name);
      await customPromptsPage.waitForSuccessToast();

      // Verify status changes
      prompt1 = await customPromptsPage.getPromptByName(prompt1Data.name);
      prompt2 = await customPromptsPage.getPromptByName(prompt2Data.name);
      expect(prompt1.status).toContain('Inactive');
      expect(prompt2.status).toContain('Active');
    });

    test('should validate form inputs properly', async () => {
      await customPromptsPage.navigateTo();
      await customPromptsPage.openCreateDialog();

      // Test empty form submission
      await customPromptsPage.saveButton.click();
      expect(await customPromptsPage.verifyValidationError('prompt-name', 'Name is required')).toBeTruthy();

      // Test short content
      await customPromptsPage.promptNameInput.fill('Test Prompt');
      await customPromptsPage.promptContentInput.fill('Short');
      await customPromptsPage.saveButton.click();
      expect(await customPromptsPage.verifyValidationError('prompt-content', 'Content must be at least 10 characters')).toBeTruthy();

      // Test valid form
      await customPromptsPage.promptContentInput.fill('This is valid content for testing validation');
      await customPromptsPage.submitPromptForm();
      await customPromptsPage.waitForSuccessToast();

      // Verify prompt was created
      expect(await customPromptsPage.promptExists('Test Prompt')).toBeTruthy();
    });
  });

  test.describe('Error Handling', () => {
    test('should handle dialog cancellation gracefully', async () => {
      await customPromptsPage.navigateTo();

      // Open create dialog and fill some data
      await customPromptsPage.openCreateDialog();
      await customPromptsPage.promptNameInput.fill('Cancelled Prompt');
      await customPromptsPage.promptContentInput.fill('This prompt will be cancelled');

      // Cancel the dialog
      await customPromptsPage.cancelPromptForm();

      // Verify dialog is closed and no prompt was created
      await expect(customPromptsPage.promptDialog).not.toBeVisible();
      expect(await customPromptsPage.promptExists('Cancelled Prompt')).toBeFalsy();

      // Verify we can still create prompts after cancellation
      const uniqueId = Date.now();
      const promptData = {
        promptType: 'small_llm' as const,
        name: `After Cancel Prompt ${uniqueId}`,
        content: 'This prompt is created after cancelling another',
      };

      await customPromptsPage.createPrompt(promptData);
      await customPromptsPage.waitForSuccessToast();
      expect(await customPromptsPage.promptExists(promptData.name)).toBeTruthy();
    });

    test('should handle page refresh gracefully', async ({ page }) => {
      await customPromptsPage.navigateTo();

      // Create a prompt
      const uniqueId = Date.now();
      const promptData = {
        promptType: 'guardrails' as const,
        name: `Refresh Test Prompt ${uniqueId}`,
        content: 'This prompt tests page refresh behavior',
      };

      await customPromptsPage.createPrompt(promptData);
      await customPromptsPage.waitForSuccessToast();

      // Refresh the page
      await page.reload();
      await customPromptsPage.waitForPageLoad();

      // Verify the prompt still exists after refresh
      expect(await customPromptsPage.promptExists(promptData.name)).toBeTruthy();

      // Verify we can still interact with the page
      await expect(customPromptsPage.createPromptButton).toBeVisible();
      await expect(customPromptsPage.pageTitle).toBeVisible();
    });
  });

  test.describe('Integration Points', () => {
    test('should maintain authentication state across custom prompts operations', async ({ page }) => {
      await customPromptsPage.navigateTo();

      // Perform multiple operations to ensure auth is maintained
      const operations = [
        () => customPromptsPage.openCreateDialog(),
        () => customPromptsPage.cancelPromptForm(),
        () => customPromptsPage.createPrompt({
          promptType: 'small_llm' as const,
          name: `Auth Test Prompt ${Date.now()}`,
          content: 'Testing authentication persistence'
        }),
        () => customPromptsPage.waitForSuccessToast()
      ];

      for (const operation of operations) {
        await operation();
        
        // Verify we're still authenticated (no redirect to login)
        await expect(page).toHaveURL(/\/custom-prompts/);
        await expect(customPromptsPage.pageTitle).toBeVisible();
      }
    });

    test('should handle navigation sidebar correctly', async () => {
      await customPromptsPage.navigateTo();

      // Verify custom prompts is highlighted in sidebar
      await expect(appLayoutPage.sidebar).toBeVisible();
      
      // The custom prompts nav item should be active/highlighted
      const customPromptsNavItem = appLayoutPage.page.getByRole('link', { name: /custom prompts/i });
      await expect(customPromptsNavItem).toBeVisible();

      // Navigate to other sections and back
      await appLayoutPage.navigateTo('dashboard');
      await expect(appLayoutPage.page).toHaveURL('/dashboard');

      await appLayoutPage.navigateTo('custom-prompts');
      await expect(appLayoutPage.page).toHaveURL('/custom-prompts');
      await expect(customPromptsPage.pageTitle).toBeVisible();
    });
  });

  test.describe('Performance and Stability', () => {
    test('should load custom prompts page quickly', async ({ page }) => {
      const startTime = Date.now();
      
      await customPromptsPage.navigateTo();
      await customPromptsPage.waitForPageLoad();
      
      const loadTime = Date.now() - startTime;
      
      // Page should load within 5 seconds
      expect(loadTime).toBeLessThan(5000);
      
      // Verify essential elements are visible
      await expect(customPromptsPage.pageTitle).toBeVisible();
      await expect(customPromptsPage.createPromptButton).toBeVisible();
    });

    test('should handle multiple rapid operations', async () => {
      await customPromptsPage.navigateTo();

      // Rapidly open and close dialog multiple times
      for (let i = 0; i < 3; i++) {
        await customPromptsPage.openCreateDialog();
        await expect(customPromptsPage.promptDialog).toBeVisible();
        
        await customPromptsPage.cancelPromptForm();
        await expect(customPromptsPage.promptDialog).not.toBeVisible();
      }

      // Verify the page is still functional
      await expect(customPromptsPage.createPromptButton).toBeVisible();
      await expect(customPromptsPage.pageTitle).toBeVisible();

      // Create a prompt to ensure functionality is intact
      const promptData = {
        promptType: 'judge' as const,
        name: `Rapid Test Prompt ${Date.now()}`,
        content: 'Testing rapid operations handling'
      };

      await customPromptsPage.createPrompt(promptData);
      await customPromptsPage.waitForSuccessToast();
      expect(await customPromptsPage.promptExists(promptData.name)).toBeTruthy();
    });
  });
});
