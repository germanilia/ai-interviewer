import { test, expect } from '@playwright/test';

test.describe('Candidate Chat Interface', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to interview landing and login with valid pass key
    await page.goto('/interview');
    await page.getByTestId('pass-key-input').fill('XZDUN3VB');
    await page.getByTestId('candidate-login-button').click();
    
    // Wait for navigation to chat interface
    await expect(page).toHaveURL('/interview/chat');
  });

  test('should display chat interface correctly', async ({ page }) => {
    // Check header information
    await expect(page.getByText('Warehouse Supervisor')).toBeVisible();
    await expect(page.getByText('Candidate: Sarah Davis')).toBeVisible();
    await expect(page.getByTestId('end-interview-button')).toBeVisible();

    // Check chat elements
    await expect(page.getByTestId('chat-messages')).toBeVisible();
    await expect(page.getByTestId('message-input')).toBeVisible();
    await expect(page.getByTestId('send-message-button')).toBeVisible();

    // Should show welcome message
    await expect(page.getByText('Hello Sarah Davis!')).toBeVisible();
    await expect(page.getByText('Welcome to your interview for Warehouse Supervisor')).toBeVisible();
  });

  test('should send and receive messages', async ({ page }) => {
    // Type a message
    await page.getByTestId('message-input').fill('Hello, I am excited about this opportunity!');
    await page.getByTestId('send-message-button').click();

    // Should show user message
    await expect(page.getByText('Hello, I am excited about this opportunity!')).toBeVisible();

    // Should show loading indicator
    await expect(page.locator('.animate-bounce')).toBeVisible();

    // Should receive assistant response
    await expect(page.getByText('Thank you for that response')).toBeVisible({ timeout: 10000 });

    // Message input should be cleared
    await expect(page.getByTestId('message-input')).toHaveValue('');
  });

  test('should handle interview completion', async ({ page }) => {
    // Send a completion message
    await page.getByTestId('message-input').fill('I am done with the interview');
    await page.getByTestId('send-message-button').click();

    // Should show completion message
    await expect(page.getByText('Thank you Sarah Davis for taking the time to complete this interview')).toBeVisible({ timeout: 10000 });
    
    // Should show completion status
    await expect(page.getByText('Interview completed successfully')).toBeVisible();

    // Input should be disabled
    await expect(page.getByTestId('message-input')).toBeDisabled();
    await expect(page.getByTestId('send-message-button')).toBeDisabled();
  });

  test('should prevent sending empty messages', async ({ page }) => {
    // Try to send empty message
    await page.getByTestId('send-message-button').click();

    // Should not send anything (button should be disabled)
    await expect(page.getByTestId('send-message-button')).toBeDisabled();

    // Try with whitespace only
    await page.getByTestId('message-input').fill('   ');
    await expect(page.getByTestId('send-message-button')).toBeDisabled();
  });

  test('should end interview and return to landing page', async ({ page }) => {
    // Click end interview button
    await page.getByTestId('end-interview-button').click();

    // Should show loading state with spinner
    await expect(page.getByTestId('end-interview-button')).toContainText('Ending Interview...');
    await expect(page.locator('[data-testid="end-interview-button"] .animate-spin')).toBeVisible();

    // Button should be disabled during loading
    await expect(page.getByTestId('end-interview-button')).toBeDisabled();

    // Should navigate back to interview landing after completion
    await expect(page).toHaveURL('/interview');
  });

  test('should display message timestamps', async ({ page }) => {
    // Send a message
    await page.getByTestId('message-input').fill('Test message');
    await page.getByTestId('send-message-button').click();

    // Should show timestamp for user message
    const userMessage = page.locator('[data-testid="chat-messages"]').locator('text=Test message').locator('..');
    await expect(userMessage.locator('text=/\\d{1,2}:\\d{2}/')).toBeVisible();

    // Wait for assistant response
    await expect(page.getByText('Thank you for that response')).toBeVisible({ timeout: 10000 });

    // Should show timestamp for assistant message
    const assistantMessage = page.locator('[data-testid="chat-messages"]').locator('text=Thank you for that response').locator('..');
    await expect(assistantMessage.locator('text=/\\d{1,2}:\\d{2}/')).toBeVisible();
  });

  test('should handle multiple message exchanges', async ({ page }) => {
    const messages = [
      'Tell me about yourself',
      'What are your strengths?',
      'Why do you want this job?'
    ];

    for (const message of messages) {
      await page.getByTestId('message-input').fill(message);
      await page.getByTestId('send-message-button').click();

      // Wait for user message to appear
      await expect(page.getByText(message)).toBeVisible();

      // Wait for assistant response
      await expect(page.getByText('Thank you for that response')).toBeVisible({ timeout: 10000 });

      // Wait a bit before next message
      await page.waitForTimeout(1000);
    }

    // Should have all messages visible
    for (const message of messages) {
      await expect(page.getByText(message)).toBeVisible();
    }
  });

  test('should redirect to landing if no interview state', async ({ page }) => {
    // Navigate directly to chat without going through login
    await page.goto('/interview/chat');
    
    // Should redirect to interview landing
    await expect(page).toHaveURL('/interview');
    
    // Should show error message
    await expect(page.getByText('No interview session found')).toBeVisible();
  });
});
