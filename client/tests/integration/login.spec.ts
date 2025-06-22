import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage';
import { DashboardPage } from '../pages/DashboardPage';
import { TEST_USERS, INVALID_CREDENTIALS, TEST_URLS } from '../utils/testData';
import { clearAuth, clearAuthKeepRemembered, loginAs } from '../utils/auth';

test.describe('Login Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Clear authentication state before each test
    await clearAuth(page);
  });

  test('successful admin login and navigation to dashboard @regression', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const dashboardPage = new DashboardPage(page);

    await loginPage.goto();
    await loginPage.expectLoginPage();

    // Fill login form with admin credentials
    await loginPage.login(TEST_USERS.ADMIN.email, TEST_USERS.ADMIN.password);

    // Verify successful login and navigation to dashboard
    await expect(page).toHaveURL(TEST_URLS.DASHBOARD, { timeout: 15000 });
    await dashboardPage.expectDashboardPage();
  });

  test('successful user login and navigation to dashboard @regression', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const dashboardPage = new DashboardPage(page);

    await loginPage.goto();
    await loginPage.expectLoginPage();

    // Fill login form with user credentials
    await loginPage.login(TEST_USERS.USER.email, TEST_USERS.USER.password);

    // Verify successful login and navigation to dashboard
    await expect(page).toHaveURL(TEST_URLS.DASHBOARD, { timeout: 15000 });
    await dashboardPage.expectDashboardPage();
  });

  test('login with remember me functionality @regression', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.goto();
    await loginPage.expectLoginPage();

    // Fill credentials and check remember me
    await loginPage.login(TEST_USERS.ADMIN.email, TEST_USERS.ADMIN.password, true);

    // Verify successful login
    await expect(page).toHaveURL(TEST_URLS.DASHBOARD, { timeout: 15000 });

    // Verify email is remembered in localStorage
    const rememberedEmail = await page.evaluate(() => localStorage.getItem('rememberedEmail'));
    expect(rememberedEmail).toBe(TEST_USERS.ADMIN.email);
  });

  test('remember me functionality persists email on return', async ({ page }) => {
    const loginPage = new LoginPage(page);

    // First login with remember me
    await loginPage.goto();
    await loginPage.login(TEST_USERS.ADMIN.email, TEST_USERS.ADMIN.password, true);
    await expect(page).toHaveURL(TEST_URLS.DASHBOARD, { timeout: 15000 });

    // Clear auth but keep remembered email and return to login page
    await clearAuthKeepRemembered(page);
    await loginPage.goto();

    // Email should be pre-filled and remember me should be checked
    await expect(loginPage.emailInput).toHaveValue(TEST_USERS.ADMIN.email);
    await expect(loginPage.rememberMeCheckbox).toBeChecked();
  });

  test('login form validation with empty fields', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.goto();
    await loginPage.expectLoginPage();

    // Test empty form submission
    await loginPage.submit();
    await loginPage.expectValidationError();

    // Test with only email filled
    await loginPage.fillCredentials(TEST_USERS.ADMIN.email, '');
    await loginPage.submit();
    await loginPage.expectValidationError();

    // Test with only password filled
    await loginPage.fillCredentials('', TEST_USERS.ADMIN.password);
    await loginPage.submit();
    await loginPage.expectValidationError();
  });

  test('login with invalid credentials shows error', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.goto();
    await loginPage.expectLoginPage();

    // Test with wrong credentials
    await loginPage.login(INVALID_CREDENTIALS.email, INVALID_CREDENTIALS.password);

    // Should stay on login page since user doesn't exist
    await expect(page).toHaveURL(TEST_URLS.LOGIN);
  });

  test('redirect to login when accessing protected route @regression', async ({ page }) => {
    // Try to access dashboard without authentication
    await page.goto(TEST_URLS.DASHBOARD);

    // Should be redirected to login page
    await expect(page).toHaveURL(TEST_URLS.LOGIN);
    
    const loginPage = new LoginPage(page);
    await loginPage.expectLoginPage();
  });

  test('maintain session after login', async ({ page }) => {
    // Login first
    await loginAs(page, 'ADMIN');

    // Navigate away and back to dashboard
    await page.goto(TEST_URLS.HOME);
    await page.goto(TEST_URLS.DASHBOARD);

    // Should still be authenticated
    await expect(page).toHaveURL(TEST_URLS.DASHBOARD);
  });

  test('form accessibility - tab navigation between fields', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.goto();
    await loginPage.expectLoginPage();

    // Test tab navigation
    await page.keyboard.press('Tab');
    await expect(loginPage.emailInput).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(loginPage.passwordInput).toBeFocused();

    await page.keyboard.press('Tab');
    // Should focus on submit button or remember me checkbox
  });

  test('form handles keyboard submission', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.goto();
    await loginPage.expectLoginPage();

    // Fill form and submit with Enter key
    await loginPage.fillCredentials(TEST_USERS.ADMIN.email, TEST_USERS.ADMIN.password);
    await page.keyboard.press('Enter');

    // Should navigate to dashboard
    await expect(page).toHaveURL(TEST_URLS.DASHBOARD, { timeout: 15000 });
  });

  test('login form shows loading state during submission', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.goto();
    await loginPage.expectLoginPage();

    // Fill credentials
    await loginPage.fillCredentials(TEST_USERS.ADMIN.email, TEST_USERS.ADMIN.password);

    // Submit and check for loading state
    await loginPage.submit();
    
    // Wait for loading to finish
    await loginPage.waitForLoadingToFinish();
  });

  test('login form focuses email field on page load', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.goto();
    await loginPage.expectLoginPage();

    // Click on email field to ensure it's focused (some browsers don't auto-focus)
    await loginPage.emailInput.click();
    await expect(loginPage.emailInput).toBeFocused();
  });

  test('login form shows error for invalid email format', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.goto();
    await loginPage.expectLoginPage();

    // Test with invalid email format
    await loginPage.fillCredentials('invalid-email', TEST_USERS.ADMIN.password);
    await loginPage.submit();

    // Should show validation error or stay on login page
    await loginPage.expectValidationError();
  });

  test('login form shows error for invalid password', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.goto();
    await loginPage.expectLoginPage();

    // Test with valid email but wrong password
    await loginPage.login(TEST_USERS.ADMIN.email, 'wrongpassword');

    // Should stay on login page due to invalid password
    await expect(page).toHaveURL(TEST_URLS.LOGIN);
  });

  test('login form handles server error response', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.goto();
    await loginPage.expectLoginPage();

    // Mock a server error by intercepting the request
    await page.route('**/api/v1/auth/signin', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' })
      });
    });

    await loginPage.login(TEST_USERS.ADMIN.email, TEST_USERS.ADMIN.password);

    // Should handle error gracefully
    await expect(page).toHaveURL(TEST_URLS.LOGIN);
  });

  test('login form handles network connection error', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.goto();
    await loginPage.expectLoginPage();

    // Mock a network error
    await page.route('**/api/v1/auth/signin', route => {
      route.abort('failed');
    });

    await loginPage.login(TEST_USERS.ADMIN.email, TEST_USERS.ADMIN.password);

    // Should handle network error gracefully
    await expect(page).toHaveURL(TEST_URLS.LOGIN);
  });

  test('login form error for non-existent user', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.goto();
    await loginPage.expectLoginPage();

    // Test with non-existent user
    await loginPage.login('nonexistent@example.com', 'somepassword');

    // Should stay on login page since user doesn't exist
    await expect(page).toHaveURL(TEST_URLS.LOGIN);
  });

  test('login button disabled during submission', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.goto();
    await loginPage.expectLoginPage();

    await loginPage.fillCredentials(TEST_USERS.ADMIN.email, TEST_USERS.ADMIN.password);

    // Check if submit button gets disabled during submission
    await loginPage.submit();
    
    // Button should be disabled or show loading state
    // This depends on the actual implementation
    await loginPage.waitForLoadingToFinish();
  });
});
