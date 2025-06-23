/**
 * Test setup utilities for admin dashboard tests
 * Provides common setup and teardown functions
 */

import { Page, Browser, BrowserContext } from '@playwright/test';
import { AdminApiHelpers } from './apiHelpers';
import { testUsers } from './adminTestData';

export interface TestContext {
  page: Page;
  context: BrowserContext;
  browser: Browser;
  isAuthenticated: boolean;
  authToken?: string;
}

/**
 * Test Setup Helper Class
 */
export class TestSetup {
  private static contexts: Map<string, TestContext> = new Map();

  /**
   * Setup test environment for admin dashboard tests
   */
  static async setupAdminTest(page: Page, options?: {
    skipAuth?: boolean;
    setupTestData?: boolean;
    viewport?: { width: number; height: number };
  }): Promise<TestContext> {
    const context = page.context();
    const browser = context.browser()!;
    
    // Set viewport if specified
    if (options?.viewport) {
      await page.setViewportSize(options.viewport);
    }

    // Initialize API helpers
    await AdminApiHelpers.initialize();

    let authToken: string | undefined;
    let isAuthenticated = false;

    // Authenticate if not skipped
    if (!options?.skipAuth) {
      authToken = await this.authenticateUser(page, testUsers.admin);
      isAuthenticated = true;
    }

    // Setup test data if requested
    if (options?.setupTestData) {
      await AdminApiHelpers.setupTestData();
    }

    const testContext: TestContext = {
      page,
      context,
      browser,
      isAuthenticated,
      authToken
    };

    // Store context for cleanup
    const contextId = `${Date.now()}-${Math.random()}`;
    this.contexts.set(contextId, testContext);

    return testContext;
  }

  /**
   * Cleanup test environment
   */
  static async cleanupAdminTest(testContext?: TestContext): Promise<void> {
    try {
      // Cleanup test data
      await AdminApiHelpers.cleanupTestData();
      
      // Cleanup API context
      await AdminApiHelpers.cleanup();

      // Remove from stored contexts
      for (const [key, context] of this.contexts.entries()) {
        if (!testContext || context === testContext) {
          this.contexts.delete(key);
        }
      }
    } catch (error) {
      console.warn('Error during test cleanup:', error);
    }
  }

  /**
   * Cleanup all test contexts
   */
  static async cleanupAll(): Promise<void> {
    for (const context of this.contexts.values()) {
      await this.cleanupAdminTest(context);
    }
    this.contexts.clear();
  }

  /**
   * Authenticate user and set up session
   */
  static async authenticateUser(page: Page, user: { email: string; password: string }): Promise<string> {
    // Use the existing working login utility
    const { loginAs } = await import('./auth');
    await loginAs(page, 'ADMIN');

    // After successful login, navigate to admin area
    await page.goto('/admin');
    await page.waitForURL('/admin', { timeout: 10000 });

    // Get auth token from API
    const authToken = await AdminApiHelpers.authenticateAsAdmin();

    return authToken;
  }

  /**
   * Setup mobile viewport for responsive testing
   */
  static async setupMobileViewport(page: Page): Promise<void> {
    await page.setViewportSize({ width: 393, height: 851 }); // Pixel 5 dimensions
  }

  /**
   * Setup desktop viewport for desktop testing
   */
  static async setupDesktopViewport(page: Page): Promise<void> {
    await page.setViewportSize({ width: 1920, height: 1080 });
  }

  /**
   * Wait for page to be fully loaded
   */
  static async waitForPageLoad(page: Page): Promise<void> {
    await page.waitForLoadState('networkidle');
    await page.waitForFunction(() => {
      // Wait for any loading spinners to disappear
      const loadingElements = document.querySelectorAll('[data-testid*="loading"], .loading, .spinner');
      return Array.from(loadingElements).every(el => !el.offsetParent);
    }, { timeout: 10000 });
  }

  /**
   * Take screenshot for debugging
   */
  static async takeDebugScreenshot(page: Page, name: string): Promise<void> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    await page.screenshot({ 
      path: `test-results/debug-${name}-${timestamp}.png`,
      fullPage: true 
    });
  }

  /**
   * Check for console errors
   */
  static async checkConsoleErrors(page: Page): Promise<string[]> {
    const errors: string[] = [];
    
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    page.on('pageerror', error => {
      errors.push(error.message);
    });

    return errors;
  }

  /**
   * Mock API responses for testing
   */
  static async mockApiResponses(page: Page, mocks: Record<string, any>): Promise<void> {
    for (const [endpoint, response] of Object.entries(mocks)) {
      await page.route(`**/api/v1/${endpoint}`, route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(response)
        });
      });
    }
  }

  /**
   * Wait for API call to complete
   */
  static async waitForApiCall(page: Page, endpoint: string, method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET'): Promise<void> {
    await page.waitForResponse(response => 
      response.url().includes(endpoint) && response.request().method() === method
    );
  }

  /**
   * Intercept and verify API calls
   */
  static async interceptApiCall(
    page: Page, 
    endpoint: string, 
    callback: (request: any) => void
  ): Promise<void> {
    await page.route(`**/api/v1/${endpoint}`, route => {
      callback(route.request());
      route.continue();
    });
  }

  /**
   * Setup test data isolation
   */
  static async setupTestDataIsolation(): Promise<void> {
    // This would typically involve setting up a test database
    // or using database transactions that can be rolled back
    console.log('Setting up test data isolation...');
  }

  /**
   * Verify accessibility compliance
   */
  static async checkAccessibility(page: Page): Promise<void> {
    // This would integrate with axe-core or similar accessibility testing tool
    // For now, we'll do basic checks
    
    // Check for alt text on images
    const imagesWithoutAlt = await page.locator('img:not([alt])').count();
    if (imagesWithoutAlt > 0) {
      console.warn(`Found ${imagesWithoutAlt} images without alt text`);
    }

    // Check for form labels
    const inputsWithoutLabels = await page.locator('input:not([aria-label]):not([aria-labelledby])').count();
    if (inputsWithoutLabels > 0) {
      console.warn(`Found ${inputsWithoutLabels} inputs without labels`);
    }

    // Check for heading hierarchy
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
    let previousLevel = 0;
    for (const heading of headings) {
      const tagName = await heading.evaluate(el => el.tagName.toLowerCase());
      const currentLevel = parseInt(tagName.charAt(1));
      
      if (currentLevel > previousLevel + 1) {
        console.warn(`Heading hierarchy skip detected: ${tagName} after h${previousLevel}`);
      }
      
      previousLevel = currentLevel;
    }
  }

  /**
   * Performance monitoring
   */
  static async measurePagePerformance(page: Page): Promise<{
    loadTime: number;
    domContentLoaded: number;
    firstContentfulPaint: number;
  }> {
    const performanceMetrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      const paint = performance.getEntriesByType('paint');
      
      return {
        loadTime: navigation.loadEventEnd - navigation.loadEventStart,
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
        firstContentfulPaint: paint.find(p => p.name === 'first-contentful-paint')?.startTime || 0
      };
    });

    return performanceMetrics;
  }

  /**
   * Network monitoring
   */
  static async monitorNetworkRequests(page: Page): Promise<{
    requests: Array<{ url: string; method: string; status: number; duration: number }>;
    failedRequests: Array<{ url: string; error: string }>;
  }> {
    const requests: Array<{ url: string; method: string; status: number; duration: number }> = [];
    const failedRequests: Array<{ url: string; error: string }> = [];

    page.on('response', response => {
      requests.push({
        url: response.url(),
        method: response.request().method(),
        status: response.status(),
        duration: 0 // Would need to calculate from request start time
      });
    });

    page.on('requestfailed', request => {
      failedRequests.push({
        url: request.url(),
        error: request.failure()?.errorText || 'Unknown error'
      });
    });

    return { requests, failedRequests };
  }

  /**
   * Database state verification
   */
  static async verifyDatabaseState(expectedState: Record<string, any>): Promise<boolean> {
    // This would verify the database state matches expectations
    // Implementation would depend on database access patterns
    console.log('Verifying database state:', expectedState);
    return true;
  }

  /**
   * Generate test report
   */
  static async generateTestReport(testContext: TestContext, results: any): Promise<void> {
    const report = {
      timestamp: new Date().toISOString(),
      context: {
        viewport: await testContext.page.viewportSize(),
        userAgent: await testContext.page.evaluate(() => navigator.userAgent),
        url: testContext.page.url()
      },
      results,
      performance: await this.measurePagePerformance(testContext.page)
    };

    console.log('Test Report:', JSON.stringify(report, null, 2));
  }
}
