/**
 * Test data constants for Playwright tests
 */

export const TEST_USERS = {
  ADMIN: {
    email: 'admin@admin.com',
    password: 'Cowabunga2@',
    role: 'ADMIN',
    fullName: 'Test Admin User'
  },
  USER: {
    email: 'user@test.com',
    password: 'TestPassword123!',
    role: 'USER',
    fullName: 'Test Regular User'
  }
} as const;

export const INVALID_CREDENTIALS = {
  email: 'invalid@example.com',
  password: 'wrongpassword'
} as const;

export const TEST_URLS = {
  LOGIN: '/login',
  DASHBOARD: '/dashboard',
  HOME: '/'
} as const;

export const SELECTORS = {
  LOGIN: {
    EMAIL_INPUT: 'input#email',
    PASSWORD_INPUT: 'input#password',
    SUBMIT_BUTTON: 'button[type="submit"]',
    REMEMBER_ME: '#remember-me',
    REMEMBER_ME_LABEL: 'label[for="remember-me"]',
    ERROR_MESSAGE: '.text-destructive, [role="alert"], .error, .text-red-500, div:has-text("error"), div:has-text("Error")'
  },
  DASHBOARD: {
    TITLE: 'h1:has-text("Dashboard")',
    USER_MENU: '[data-testid="user-menu"], .user-menu, button:has-text("menu"), [aria-label*="menu"]'
  }
} as const;
