import { test, expect } from '@playwright/test';

test.describe('Interview Landing Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/interview');
  });

  test('should display dual login options', async ({ page }) => {
    // Check that both login cards are visible
    await expect(page.getByTestId('candidate-login-card')).toBeVisible();
    await expect(page.getByTestId('operator-login-card')).toBeVisible();

    // Check candidate login elements
    await expect(page.getByText('Candidate Access')).toBeVisible();
    await expect(page.getByText('Enter your unique pass key to start your interview')).toBeVisible();
    await expect(page.getByTestId('pass-key-input')).toBeVisible();
    await expect(page.getByTestId('candidate-login-button')).toBeVisible();

    // Check operator login elements
    await expect(page.getByText('Operator Access')).toBeVisible();
    await expect(page.getByText('Access the admin dashboard to manage interviews')).toBeVisible();
    await expect(page.getByTestId('operator-login-button')).toBeVisible();
  });

  test('should navigate to operator login when operator button is clicked', async ({ page }) => {
    await page.getByTestId('operator-login-button').click();
    await expect(page).toHaveURL('/login');
  });

  test('should show error for empty pass key', async ({ page }) => {
    await page.getByTestId('candidate-login-button').click();
    
    // Should show error toast
    await expect(page.getByText('Please enter your pass key')).toBeVisible();
  });

  test('should show error for invalid pass key', async ({ page }) => {
    await page.getByTestId('pass-key-input').fill('INVALID123');
    await page.getByTestId('candidate-login-button').click();
    
    // Should show error toast
    await expect(page.getByText('Invalid pass key')).toBeVisible();
  });

  test('should successfully login with valid pass key and navigate to chat', async ({ page }) => {
    // Use a valid pass key from test data
    await page.getByTestId('pass-key-input').fill('XZDUN3VB');
    await page.getByTestId('candidate-login-button').click();
    
    // Should show success message
    await expect(page.getByText('Login Successful')).toBeVisible();
    
    // Should navigate to chat interface
    await expect(page).toHaveURL('/interview/chat');
  });

  test('should handle pass key input correctly', async ({ page }) => {
    const passKeyInput = page.getByTestId('pass-key-input');
    
    // Should accept text input
    await passKeyInput.fill('TEST1234');
    await expect(passKeyInput).toHaveValue('TEST1234');
    
    // Should trim whitespace
    await passKeyInput.fill('  XZDUN3VB  ');
    await page.getByTestId('candidate-login-button').click();
    
    // Should still work with trimmed value
    await expect(page.getByText('Login Successful')).toBeVisible();
  });

  test('should disable form during loading', async ({ page }) => {
    await page.getByTestId('pass-key-input').fill('XZDUN3VB');
    
    // Start the login process
    await page.getByTestId('candidate-login-button').click();
    
    // During loading, elements should be disabled
    await expect(page.getByTestId('pass-key-input')).toBeDisabled();
    await expect(page.getByTestId('candidate-login-button')).toBeDisabled();
  });
});
