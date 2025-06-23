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
    this.sidebar = page.locator('aside'); // Use existing sidebar selector
    this.sidebarToggle = page.getByTestId('sidebar-toggle');
    this.mainContent = page.locator('main'); // Use existing main content selector
    this.userMenu = page.getByTestId('user-menu');
    this.logoutButton = page.getByTestId('logout-btn');

    // Navigation links (existing + new)
    this.dashboardLink = page.getByRole('link', { name: 'Dashboard' });
    this.usersLink = page.getByRole('link', { name: 'Users' });
    this.settingsLink = page.getByRole('link', { name: 'Settings' });

    // New admin dashboard navigation links (to be added)
    this.candidatesLink = page.getByRole('link', { name: 'Candidates' });
    this.interviewsLink = page.getByRole('link', { name: 'Interviews' });
    this.questionsLink = page.getByRole('link', { name: 'Questions' });
    this.jobsLink = page.getByRole('link', { name: 'Jobs' });
    this.reportsLink = page.getByRole('link', { name: 'Reports' });
    
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
  async navigateTo(section: 'dashboard' | 'candidates' | 'interviews' | 'questions' | 'job-positions' | 'reports' | 'users' | 'settings') {
    const linkMap = {
      dashboard: this.dashboardLink,
      candidates: this.candidatesLink,
      interviews: this.interviewsLink,
      questions: this.questionsLink,
      'job-positions': this.jobsLink,
      reports: this.reportsLink,
      users: this.usersLink,
      settings: this.settingsLink
    };
    
    await linkMap[section].click();
    await this.page.waitForLoadState('networkidle');
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
    await this.mobileOverlay.click();
  }

  /**
   * Get current active navigation item
   */
  async getActiveNavItem(): Promise<string> {
    const activeItem = this.sidebar.locator('[data-testid^="nav-"].active, [data-testid^="nav-"][aria-current="page"]');
    const testId = await activeItem.getAttribute('data-testid');
    return testId?.replace('nav-', '') || '';
  }

  /**
   * Verify user is logged in and has admin access
   */
  async verifyAdminAccess() {
    await this.sidebar.waitFor({ state: 'visible' });
    await this.userMenu.waitFor({ state: 'visible' });
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
    const sidebarClass = await this.sidebar.getAttribute('class');
    return sidebarClass?.includes('collapsed') || sidebarClass?.includes('hidden') || false;
  }

  /**
   * Wait for page to be fully loaded
   */
  async waitForPageLoad() {
    await this.page.waitForLoadState('networkidle');
    await this.mainContent.waitFor({ state: 'visible' });
  }
}
