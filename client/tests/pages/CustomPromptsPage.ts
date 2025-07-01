import { Page, Locator } from '@playwright/test';
import type { PromptType } from '../../src/types/prompts';

export interface CustomPromptData {
  promptType: PromptType;
  name: string;
  content: string;
  description?: string;
  isActive?: boolean;
}

export interface CustomPromptFilter {
  promptType?: string;
  activeOnly?: boolean;
}

/**
 * Page Object Model for Custom Prompts Management
 * Handles custom prompt CRUD operations, types, and activation
 */
export class CustomPromptsPage {
  readonly page: Page;
  
  // Main Section
  readonly customPromptsSection: Locator;
  readonly pageTitle: Locator;
  readonly pageDescription: Locator;
  readonly createPromptButton: Locator;
  readonly loadingState: Locator;
  
  // Prompt Type Sections
  readonly evaluationSection: Locator;
  readonly judgeSection: Locator;
  readonly guardrailsSection: Locator;
  
  // Prompt Cards
  readonly promptCards: Locator;
  readonly promptCard: Locator;
  readonly promptName: Locator;
  readonly promptDescription: Locator;
  readonly promptStatus: Locator;
  readonly activeBadge: Locator;
  readonly inactiveBadge: Locator;
  
  // Prompt Actions
  readonly togglePromptButton: Locator;
  readonly editPromptButton: Locator;
  readonly deletePromptButton: Locator;
  
  // Empty States
  readonly emptyStateCard: Locator;
  readonly createFirstPromptButton: Locator;
  
  // Dialog Elements
  readonly promptDialog: Locator;
  readonly dialogTitle: Locator;
  readonly dialogDescription: Locator;
  
  // Form Elements
  readonly promptTypeSelect: Locator;
  readonly promptNameInput: Locator;
  readonly promptDescriptionInput: Locator;
  readonly promptContentInput: Locator;
  readonly promptActiveCheckbox: Locator;
  readonly saveButton: Locator;
  readonly cancelButton: Locator;
  
  // Toast Messages
  readonly successToast: Locator;
  readonly errorToast: Locator;

  constructor(page: Page) {
    this.page = page;
    
    // Main Section
    this.customPromptsSection = page.getByTestId('custom-prompts-section');
    this.pageTitle = page.getByRole('heading', { name: 'Custom Prompts' });
    this.pageDescription = page.getByText('Manage custom prompts for different AI components');
    this.createPromptButton = page.getByTestId('create-prompt-button');
    this.loadingState = page.getByText('Loading custom prompts...');
    
    // Prompt Type Sections
    this.evaluationSection = page.getByText('Evaluation').locator('..');
    this.judgeSection = page.getByText('Judge').locator('..');
    this.guardrailsSection = page.getByText('Guardrails').locator('..');
    
    // Prompt Cards
    this.promptCards = page.locator('[data-testid*="prompt-card"]');
    this.promptCard = page.locator('.card');
    this.promptName = page.locator('.card-title');
    this.promptDescription = page.locator('.card-description');
    this.promptStatus = page.locator('[data-testid*="badge"]');
    this.activeBadge = page.getByText('Active');
    this.inactiveBadge = page.getByText('Inactive');
    
    // Prompt Actions
    this.togglePromptButton = page.locator('[data-testid*="toggle-prompt"]');
    this.editPromptButton = page.locator('[data-testid*="edit-prompt"]');
    this.deletePromptButton = page.locator('[data-testid*="delete-prompt"]');
    
    // Empty States
    this.emptyStateCard = page.getByText('No').locator('..');
    this.createFirstPromptButton = page.locator('[data-testid*="create-"][data-testid*="-prompt"]');
    
    // Dialog Elements
    this.promptDialog = page.getByRole('dialog');
    this.dialogTitle = page.getByRole('heading', { name: /Create|Edit/ });
    this.dialogDescription = page.getByText(/Create a new|Edit the selected/);
    
    // Form Elements
    this.promptTypeSelect = page.getByTestId('prompt-type-select');
    this.promptNameInput = page.getByTestId('prompt-name-input');
    this.promptDescriptionInput = page.getByTestId('prompt-description-input');
    this.promptContentInput = page.getByTestId('prompt-content-input');
    this.promptActiveCheckbox = page.getByTestId('prompt-active-checkbox');
    this.saveButton = page.getByTestId('save-button');
    this.cancelButton = page.getByTestId('cancel-button');
    
    // Toast Messages
    this.successToast = page.getByText(/success/i);
    this.errorToast = page.getByText(/error/i);
  }

  /**
   * Navigate to custom prompts page
   */
  async navigateTo() {
    await this.page.goto('/custom-prompts');
    await this.waitForPageLoad();
  }

  /**
   * Wait for page to load
   */
  async waitForPageLoad() {
    await this.pageTitle.waitFor({ state: 'visible' });
    // Wait for either loading state to disappear or content to appear
    try {
      await this.loadingState.waitFor({ state: 'hidden', timeout: 5000 });
    } catch {
      // Loading state might not appear if data loads quickly
    }
  }

  /**
   * Wait for prompts to load
   */
  async waitForPromptsToLoad() {
    await this.waitForPageLoad();
    // Give a moment for any async operations to complete
    await this.page.waitForTimeout(500);
  }

  /**
   * Get count of prompt cards
   */
  async getPromptCount(): Promise<number> {
    await this.waitForPromptsToLoad();
    return await this.promptCards.count();
  }

  /**
   * Get prompt by index
   */
  async getPromptByIndex(index: number) {
    const card = this.promptCards.nth(index);
    const name = await card.locator('.card-title').textContent();
    const status = await card.locator('[data-testid*="badge"]').textContent();
    return { name, status };
  }

  /**
   * Get prompt by name
   */
  async getPromptByName(name: string) {
    const card = this.page.locator('.card').filter({ hasText: name });
    const status = await card.locator('[data-testid*="badge"]').textContent();
    return { name, status };
  }

  /**
   * Check if prompt exists
   */
  async promptExists(name: string): Promise<boolean> {
    await this.waitForPromptsToLoad();
    const count = await this.page.locator('.card').filter({ hasText: name }).count();
    return count > 0;
  }

  /**
   * Open create prompt dialog
   */
  async openCreateDialog() {
    await this.createPromptButton.click();
    await this.promptDialog.waitFor({ state: 'visible' });
  }

  /**
   * Open edit prompt dialog
   */
  async openEditDialog(promptName: string) {
    const card = this.page.locator('.card').filter({ hasText: promptName });
    await card.locator('[data-testid*="edit-prompt"]').click();
    await this.promptDialog.waitFor({ state: 'visible' });
  }

  /**
   * Fill prompt form
   */
  async fillPromptForm(data: CustomPromptData) {
    // Select prompt type (only for create)
    if (await this.promptTypeSelect.isEnabled()) {
      await this.promptTypeSelect.click();
      await this.page.getByRole('option', { name: this.getPromptTypeLabel(data.promptType) }).click();
    }

    // Fill name
    await this.promptNameInput.fill(data.name);

    // Fill content
    await this.promptContentInput.fill(data.content);

    // Fill description if provided
    if (data.description) {
      await this.promptDescriptionInput.fill(data.description);
    }

    // Set active status if specified
    if (data.isActive !== undefined) {
      const isChecked = await this.promptActiveCheckbox.isChecked();
      if (isChecked !== data.isActive) {
        await this.promptActiveCheckbox.click();
      }
    }
  }

  /**
   * Submit prompt form
   */
  async submitPromptForm() {
    await this.saveButton.click();
    await this.promptDialog.waitFor({ state: 'hidden' });
  }

  /**
   * Cancel prompt form
   */
  async cancelPromptForm() {
    await this.cancelButton.click();
    await this.promptDialog.waitFor({ state: 'hidden' });
  }

  /**
   * Create new prompt
   */
  async createPrompt(data: CustomPromptData) {
    await this.openCreateDialog();
    await this.fillPromptForm(data);
    await this.submitPromptForm();
  }

  /**
   * Edit existing prompt
   */
  async editPrompt(promptName: string, data: Partial<CustomPromptData>) {
    await this.openEditDialog(promptName);
    
    // Only fill provided fields
    if (data.name) {
      await this.promptNameInput.fill(data.name);
    }
    if (data.content) {
      await this.promptContentInput.fill(data.content);
    }
    if (data.description !== undefined) {
      await this.promptDescriptionInput.fill(data.description);
    }
    if (data.isActive !== undefined) {
      const isChecked = await this.promptActiveCheckbox.isChecked();
      if (isChecked !== data.isActive) {
        await this.promptActiveCheckbox.click();
      }
    }
    
    await this.submitPromptForm();
  }

  /**
   * Delete prompt
   */
  async deletePrompt(promptName: string) {
    const card = this.page.locator('.card').filter({ hasText: promptName });
    
    // Set up dialog handler before clicking delete
    this.page.on('dialog', dialog => dialog.accept());
    
    await card.locator('[data-testid*="delete-prompt"]').click();
    
    // Wait for the prompt to be removed
    await this.page.waitForTimeout(1000);
  }

  /**
   * Toggle prompt active status
   */
  async togglePromptStatus(promptName: string) {
    const card = this.page.locator('.card').filter({ hasText: promptName });
    await card.locator('[data-testid*="toggle-prompt"]').click();
    
    // Wait for status to update
    await this.page.waitForTimeout(1000);
  }

  /**
   * Get prompt type label for UI
   */
  private getPromptTypeLabel(promptType: string): string {
    const labels: Record<PromptType, string> = {
      'EVALUATION': 'Evaluation',
      'JUDGE': 'Judge',
      'GUARDRAILS': 'Guardrails',
      'QUESTION_EVALUATION': 'Question Evaluation'
    };
    return labels[promptType as PromptType] || promptType;
  }

  /**
   * Check if empty state is shown for a prompt type
   */
  async isEmptyStateShown(promptType: PromptType): Promise<boolean> {
    const typeLabel = this.getPromptTypeLabel(promptType);
    const emptyText = `No ${typeLabel.toLowerCase()} prompt configured yet.`;
    return await this.page.getByText(emptyText).isVisible();
  }

  /**
   * Click create first prompt button for a specific type
   */
  async clickCreateFirstPrompt(promptType: 'evaluation' | 'judge' | 'guardrails') {
    await this.page.getByTestId(`create-${promptType}-prompt`).click();
    await this.promptDialog.waitFor({ state: 'visible' });
  }

  /**
   * Check if create button is visible (only when not all types are configured)
   */
  async isCreateButtonVisible(): Promise<boolean> {
    return await this.createPromptButton.isVisible();
  }

  /**
   * Verify form validation error
   */
  async verifyValidationError(fieldName: string, expectedError: string) {
    const errorElement = this.page.locator(`[data-testid="${fieldName}-input"] ~ .text-destructive, [data-testid="${fieldName}-select"] ~ .text-destructive`).first();
    await errorElement.waitFor({ state: 'visible' });
    const errorText = await errorElement.textContent();
    return errorText?.includes(expectedError) || false;
  }

  /**
   * Wait for success toast
   */
  async waitForSuccessToast() {
    await this.successToast.waitFor({ state: 'visible' });
  }

  /**
   * Wait for error toast
   */
  async waitForErrorToast() {
    await this.errorToast.waitFor({ state: 'visible' });
  }
}
