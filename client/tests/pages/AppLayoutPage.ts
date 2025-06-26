import { Page, Locator } from '@playwright/test';

/**
 * Page Object Model for App Layout - Extended with New Features
 * Handles navigation, sidebar, and common layout elements including new interview management features
 * Works with the existing AppLayout component
 */
export class AppLayoutPage {
  readonly page: Page;

  // Navigation Elements (existing layout)
  readonly sidebar: Locator;
  readonly sidebarToggle: Locator;
  readonly mainContent: Locator;
  readonly userMenu: Locator;
  readonly logoutButton: Locator;
  readonly mobileNavigation: Locator;
  
  // Navigation Links (existing + new admin features)
  readonly dashboardLink: Locator;
  readonly usersLink: Locator;
  readonly settingsLink: Locator;
  // New admin dashboard navigation links
  readonly candidatesLink: Locator;
  readonly interviewsLink: Locator;
  readonly questionsLink: Locator;
  readonly jobsLink: Locator;
  readonly reportsLink: Locator;
  
  // Mobile Navigation
  readonly mobileMenuButton: Locator;
  readonly mobileOverlay: Locator;
  
  // Breadcrumbs
  readonly breadcrumbs: Locator;
  readonly breadcrumbItems: Locator;
  
  // Page Title
  readonly pageTitle: Locator;
  readonly pageSubtitle: Locator;

  constructor(page: Page) {
    this.page = page;

    // Initialize locators for existing layout elements
    this.sidebar = page.locator('aside[aria-label="Main navigation"]'); // Use specific sidebar selector
    this.sidebarToggle = page.getByTestId('sidebar-toggle');
    this.mainContent = page.locator('main'); // Use existing main content selector
    this.userMenu = page.getByTestId('user-menu');
    this.logoutButton = page.getByTestId('logout-btn');
    this.mobileNavigation = page.getByTestId('mobile-overlay');

    // Navigation links (using test IDs for reliability)
    this.dashboardLink = page.getByTestId('nav-dashboard');
    this.usersLink = page.getByTestId('nav-users');
    this.settingsLink = page.getByTestId('nav-settings');

    // New admin dashboard navigation links
    this.candidatesLink = page.getByTestId('nav-candidates');
    this.interviewsLink = page.getByTestId('nav-interviews');
    this.questionsLink = page.getByTestId('nav-questions');
    this.jobsLink = page.getByTestId('nav-jobpositions');
    this.reportsLink = page.getByTestId('nav-reports');
    
    // Mobile navigation
    this.mobileMenuButton = page.getByTestId('mobile-menu-btn');
    this.mobileOverlay = page.getByTestId('mobile-overlay');
    
    // Breadcrumbs and titles
    this.breadcrumbs = page.getByTestId('breadcrumbs');
    this.breadcrumbItems = page.getByTestId('breadcrumb-item');
    this.pageTitle = page.getByTestId('page-title');
    this.pageSubtitle = page.getByTestId('page-subtitle');
  }

  /**
   * Navigate to dashboard (interview management features are integrated into main app)
   */
  async navigateToDashboard() {
    await this.page.goto('/dashboard');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Legacy method name for backward compatibility
   */
  async navigateToAdmin() {
    return this.navigateToDashboard();
  }

  /**
   * Navigate to specific admin section
   */
  async navigateTo(section: 'dashboard' | 'candidates' | 'interviews' | 'questions' | 'job-positions' | 'reports' | 'users' | 'settings' | 'custom-prompts') {
    // Use direct navigation for more reliable testing
    const expectedUrl = section === 'job-positions' ? '/job-positions' : `/${section}`;
    await this.page.goto(expectedUrl);
    await this.page.waitForLoadState('networkidle');
    await this.waitForPageLoad();
  }

  /**
   * Toggle sidebar visibility
   */
  async toggleSidebar() {
    await this.sidebarToggle.click();
  }

  /**
   * Open mobile menu
   */
  async openMobileMenu() {
    await this.mobileMenuButton.click();
  }

  /**
   * Close mobile menu by clicking overlay
   */
  async closeMobileMenu() {
    // Click outside the mobile menu content to close it
    await this.page.keyboard.press('Escape');
    // Wait for the overlay to disappear
    await this.mobileOverlay.waitFor({ state: 'hidden', timeout: 5000 });
  }

  /**
   * Get current active navigation item
   */
  async getActiveNavItem(): Promise<string> {
    // Get current URL and determine active section from it
    const currentUrl = this.page.url();
    const pathname = new URL(currentUrl).pathname;

    // Map URL paths to section names
    const urlToSectionMap: Record<string, string> = {
      '/dashboard': 'dashboard',
      '/candidates': 'candidates',
      '/interviews': 'interviews',
      '/questions': 'questions',
      '/job-positions': 'job-positions',
      '/reports': 'reports',
      '/users': 'users',
      '/settings': 'settings',
      '/custom-prompts': 'custom-prompts'
    };

    return urlToSectionMap[pathname] || 'dashboard';
  }

  /**
   * Verify user is logged in and has admin access
   */
  async verifyAdminAccess() {
    // Check if we're on mobile
    const isMobile = await this.mobileMenuButton.isVisible().catch(() => false);

    if (isMobile) {
      // On mobile, just check that the mobile menu button and user menu are visible
      await this.mobileMenuButton.waitFor({ state: 'visible' });
      await this.userMenu.waitFor({ state: 'visible' });
    } else {
      // On desktop, check that sidebar and user menu are visible
      await this.sidebar.waitFor({ state: 'visible' });
      await this.userMenu.waitFor({ state: 'visible' });
    }
  }

  /**
   * Logout from admin panel
   */
  async logout() {
    await this.userMenu.click();
    await this.logoutButton.click();
  }

  /**
   * Get breadcrumb trail
   */
  async getBreadcrumbTrail(): Promise<string[]> {
    const items = await this.breadcrumbItems.allTextContents();
    return items;
  }

  /**
   * Verify page title and subtitle
   */
  async verifyPageHeader(expectedTitle: string, expectedSubtitle?: string) {
    await this.pageTitle.waitFor({ state: 'visible' });
    const actualTitle = await this.pageTitle.textContent();
    if (actualTitle !== expectedTitle) {
      throw new Error(`Expected page title "${expectedTitle}", got "${actualTitle}"`);
    }
    
    if (expectedSubtitle) {
      const actualSubtitle = await this.pageSubtitle.textContent();
      if (actualSubtitle !== expectedSubtitle) {
        throw new Error(`Expected page subtitle "${expectedSubtitle}", got "${actualSubtitle}"`);
      }
    }
  }

  /**
   * Check if sidebar is collapsed (for responsive testing)
   */
  async isSidebarCollapsed(): Promise<boolean> {
    // Check if we're on mobile by looking for the mobile menu button
    const isMobile = await this.mobileMenuButton.isVisible().catch(() => false);

    if (isMobile) {
      // On mobile, sidebar is always "collapsed" (hidden) unless the mobile menu is open
      const isSheetOpen = await this.mobileOverlay.isVisible().catch(() => false);
      return !isSheetOpen;
    } else {
      // On desktop, check the sidebar width to determine if it's collapsed
      const sidebarBox = await this.sidebar.boundingBox().catch(() => null);
      if (!sidebarBox) return true; // If we can't get the box, assume collapsed

      // Collapsed sidebar should be around 64px wide (w-16), expanded should be 256px (w-64)
      return sidebarBox.width < 100; // Threshold between collapsed and expanded
    }
  }

  /**
   * Wait for page to be fully loaded
   */
  async waitForPageLoad() {
    await this.page.waitForLoadState('networkidle');
    await this.mainContent.waitFor({ state: 'visible' });
  }
}
