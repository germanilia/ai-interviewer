import { Page, expect, Locator } from '@playwright/test';
import { TEST_URLS, SELECTORS } from '../utils/testData';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly rememberMeCheckbox: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.locator(SELECTORS.LOGIN.EMAIL_INPUT);
    this.passwordInput = page.locator(SELECTORS.LOGIN.PASSWORD_INPUT);
    this.submitButton = page.locator(SELECTORS.LOGIN.SUBMIT_BUTTON);
    this.rememberMeCheckbox = page.locator(SELECTORS.LOGIN.REMEMBER_ME);
    this.errorMessage = page.locator(SELECTORS.LOGIN.ERROR_MESSAGE);
  }

  async goto() {
    await this.page.goto(TEST_URLS.LOGIN);
  }

  async fillCredentials(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
  }

  async checkRememberMe() {
    // Check if remember me checkbox exists before trying to check it
    if (await this.rememberMeCheckbox.isVisible()) {
      await this.rememberMeCheckbox.click();
    }
  }

  async submit() {
    await this.submitButton.click();
  }

  async login(email: string, password: string, rememberMe = false) {
    await this.fillCredentials(email, password);
    if (rememberMe) {
      await this.checkRememberMe();
    }
    await this.submit();
  }

  async expectLoginPage() {
    await expect(this.page).toHaveURL(TEST_URLS.LOGIN);
    await expect(this.emailInput).toBeVisible();
    await expect(this.passwordInput).toBeVisible();
    await expect(this.submitButton).toBeVisible();
  }

  async expectValidationError() {
    await expect(this.page).toHaveURL(TEST_URLS.LOGIN);
    // Check for HTML5 validation or custom error messages
    const hasValidationError = await this.page.evaluate(() => {
      // Check for HTML5 validation
      const emailInput = document.querySelector('#email') as HTMLInputElement;
      const passwordInput = document.querySelector('#password') as HTMLInputElement;

      if (emailInput && !emailInput.validity.valid) return true;
      if (passwordInput && !passwordInput.validity.valid) return true;

      // Check for custom error messages
      const errorElement = document.querySelector('.text-destructive, [role="alert"], .error, .text-red-500');
      return errorElement !== null;
    });

    expect(hasValidationError).toBe(true);
  }

  async expectErrorMessage(message?: string) {
    await expect(this.errorMessage).toBeVisible();
    if (message) {
      await expect(this.errorMessage).toContainText(message);
    }
  }

  async waitForLoadingToFinish() {
    // Wait for any loading states to finish
    await this.page.waitForLoadState('networkidle');
  }
}
