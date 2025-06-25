import { Page, Locator } from '@playwright/test';

export interface InterviewData {
  candidateId: number;
  jobId: number;
  questions: number[]; // array of question IDs
  notes?: string;
  scheduledDate?: string;
}

export interface InterviewFilter {
  status?: 'all' | 'pending' | 'in_progress' | 'completed' | 'cancelled';
  candidateId?: number;
  jobId?: number;
  dateRange?: {
    from: string;
    to: string;
  };
}

/**
 * Page Object Model for Interview Management
 * Handles interview CRUD operations, status management, and pass keys
 */
export class InterviewsPage {
  readonly page: Page;

  // Main Section
  readonly interviewsSection: Locator;
  readonly interviewsList: Locator;
  readonly interviewsTable: Locator;
  readonly interviewRows: Locator;
  readonly emptyState: Locator;
  readonly loadingState: Locator;
  
  // Status Tabs
  readonly statusTabs: Locator;
  readonly allInterviewsTab: Locator;
  readonly pendingTab: Locator;
  readonly inProgressTab: Locator;
  readonly completedTab: Locator;
  readonly cancelledTab: Locator;
  
  // Table Headers
  readonly candidateHeader: Locator;
  readonly jobHeader: Locator;
  readonly statusHeader: Locator;
  readonly dateHeader: Locator;
  readonly passKeyHeader: Locator;
  readonly scoreHeader: Locator;
  readonly riskLevelHeader: Locator;
  readonly actionsHeader: Locator;
  readonly questionsHeader: Locator;
  
  // Toolbar
  readonly toolbar: Locator;
  readonly createInterviewButton: Locator;
  readonly bulkActionsButton: Locator;
  readonly exportButton: Locator;
  readonly refreshButton: Locator;
  
  // Create Interview Modal
  readonly createInterviewModal: Locator;
  readonly modalTitle: Locator;
  readonly candidateSelect: Locator;
  readonly candidateOption: Locator;
  readonly candidateSearchInput: Locator;
  readonly jobSelect: Locator;
  readonly jobOption: Locator;
  readonly notesInput: Locator;
  readonly scheduledDateInput: Locator;
  readonly saveInterviewButton: Locator;
  readonly cancelButton: Locator;
  readonly modalCloseButton: Locator;
  
  // Pass Key Display
  readonly passKeyDisplay: Locator;
  readonly passKeyValue: Locator;
  readonly copyPassKeyButton: Locator;
  readonly passKeyInstructions: Locator;
  readonly passKeyModal: Locator;
  
  // Interview Detail View
  readonly interviewDetailView: Locator;
  readonly interviewInfo: Locator;
  readonly candidateInfo: Locator;
  readonly jobInfo: Locator;
  readonly passKeyInfo: Locator;
  readonly interviewStatus: Locator;
  readonly interviewScore: Locator;
  readonly interviewRiskLevel: Locator;
  readonly questionsBreakdown: Locator;
  readonly conversationHistory: Locator;
  

  
  // Status Management
  readonly statusBadge: Locator;
  readonly changeStatusButton: Locator;
  readonly statusChangeModal: Locator;
  readonly newStatusSelect: Locator;
  readonly statusChangeReason: Locator;
  readonly confirmStatusChange: Locator;
  
  // Cancel Interview
  readonly cancelInterviewButton: Locator;
  readonly cancelConfirmationModal: Locator;
  readonly cancelReasonInput: Locator;
  readonly confirmCancelButton: Locator;
  readonly cancelCancelButton: Locator;
  
  // Actions
  readonly viewDetailsButton: Locator;
  readonly editInterviewButton: Locator;
  readonly deleteInterviewButton: Locator;
  readonly generateReportButton: Locator;

  readonly resumeInterviewButton: Locator;
  
  // Bulk Operations
  readonly selectAllCheckbox: Locator;
  readonly selectedCount: Locator;
  readonly bulkActionsBar: Locator;
  readonly bulkCancelButton: Locator;
  readonly bulkExportButton: Locator;
  readonly bulkDeleteButton: Locator;
  
  // Filters and Search
  readonly searchSection: Locator;
  readonly searchInput: Locator;
  readonly searchButton: Locator;
  readonly clearSearchButton: Locator;
  readonly filtersToggle: Locator;
  readonly filtersPanel: Locator;
  readonly candidateFilter: Locator;
  readonly jobFilter: Locator;
  readonly dateRangeFilter: Locator;
  readonly applyFiltersButton: Locator;
  readonly clearFiltersButton: Locator;
  
  // Pagination
  readonly paginationSection: Locator;
  readonly paginationInfo: Locator;
  readonly pageSizeSelect: Locator;
  readonly firstPageButton: Locator;
  readonly prevPageButton: Locator;
  readonly nextPageButton: Locator;
  readonly lastPageButton: Locator;
  readonly pageNumbers: Locator;
  
  // Toast Messages
  readonly successToast: Locator;
  readonly errorToast: Locator;
  readonly warningToast: Locator;
  readonly infoToast: Locator;
  readonly copySuccessToast: Locator;

  constructor(page: Page) {
    this.page = page;
    
    // Main Section
    this.interviewsSection = page.getByTestId('interviews-section');
    this.interviewsList = page.getByTestId('interviews-list');
    this.interviewsTable = page.getByTestId('interviews-table');
    this.interviewRows = page.getByTestId('interview-row');
    this.emptyState = page.getByTestId('interviews-empty-state');
    this.loadingState = page.getByTestId('interviews-loading');
    
    // Status Tabs
    this.statusTabs = page.getByTestId('status-tabs');
    this.allInterviewsTab = page.getByTestId('all-interviews-tab');
    this.pendingTab = page.getByTestId('pending-tab');
    this.inProgressTab = page.getByTestId('in-progress-tab');
    this.completedTab = page.getByTestId('completed-tab');
    this.cancelledTab = page.getByTestId('cancelled-tab');
    
    // Table Headers
    this.candidateHeader = page.getByTestId('candidate-header');
    this.jobHeader = page.getByTestId('job-header');
    this.statusHeader = page.getByTestId('status-header');
    this.dateHeader = page.getByTestId('date-header');
    this.passKeyHeader = page.getByTestId('pass-key-header');
    this.scoreHeader = page.getByTestId('score-header');
    this.riskLevelHeader = page.getByTestId('risk-level-header');
    this.actionsHeader = page.getByTestId('actions-header');
    this.questionsHeader = page.getByTestId('questions-header');
    
    // Toolbar
    this.toolbar = page.getByTestId('interviews-toolbar');
    this.createInterviewButton = page.getByTestId('create-interview-btn');
    this.bulkActionsButton = page.getByTestId('bulk-actions-btn');
    this.exportButton = page.getByTestId('export-interviews-btn');
    this.refreshButton = page.getByTestId('refresh-interviews-btn');
    
    // Create Interview Modal
    this.createInterviewModal = page.getByTestId('create-interview-modal');
    this.modalTitle = page.getByTestId('modal-title');
    this.candidateSelect = page.getByTestId('candidate-select');
    this.candidateOption = page.getByTestId('candidate-option');
    this.candidateSearchInput = page.getByTestId('candidate-search-input');
    this.jobSelect = page.getByTestId('job-select');
    this.jobOption = page.getByTestId('job-option');
    this.notesInput = page.getByTestId('notes-input');
    this.scheduledDateInput = page.getByTestId('scheduled-date-input');
    this.saveInterviewButton = page.getByTestId('save-interview-btn');
    this.cancelButton = page.getByTestId('cancel-btn');
    this.modalCloseButton = page.getByTestId('modal-close-btn');
    
    // Pass Key Display
    this.passKeyDisplay = page.getByTestId('pass-key-display');
    this.passKeyValue = page.getByTestId('pass-key-value');
    this.copyPassKeyButton = this.passKeyDisplay.getByTestId('copy-pass-key-btn');
    this.passKeyInstructions = page.getByTestId('pass-key-instructions');
    this.passKeyModal = page.getByTestId('pass-key-modal');
    
    // Interview Detail View
    this.interviewDetailView = page.getByTestId('interview-detail-view');
    this.interviewInfo = page.getByTestId('interview-info');
    this.candidateInfo = page.getByTestId('candidate-info');
    this.jobInfo = page.getByTestId('job-info');
    this.passKeyInfo = page.getByTestId('pass-key-info');
    this.interviewStatus = page.getByTestId('interview-status');
    this.interviewScore = page.getByTestId('interview-score');
    this.interviewRiskLevel = page.getByTestId('interview-risk-level');
    this.questionsBreakdown = page.getByTestId('questions-breakdown');
    this.conversationHistory = page.getByTestId('conversation-history');
    

    
    // Status Management
    this.statusBadge = page.getByTestId('status-badge');
    this.changeStatusButton = page.getByTestId('change-status-btn');
    this.statusChangeModal = page.getByTestId('status-change-modal');
    this.newStatusSelect = page.getByTestId('new-status-select');
    this.statusChangeReason = page.getByTestId('status-change-reason');
    this.confirmStatusChange = page.getByTestId('confirm-status-change');
    
    // Cancel Interview
    this.cancelInterviewButton = page.getByTestId('cancel-interview-btn');
    this.cancelConfirmationModal = page.getByTestId('cancel-confirmation-modal');
    this.cancelReasonInput = page.getByTestId('cancel-reason-input');
    this.confirmCancelButton = page.getByTestId('confirm-cancel-btn');
    this.cancelCancelButton = page.getByTestId('cancel-cancel-btn');
    
    // Actions
    this.viewDetailsButton = page.getByTestId('view-details-btn');
    this.editInterviewButton = page.getByTestId('edit-interview-btn');
    this.deleteInterviewButton = page.getByTestId('delete-interview-btn');
    this.generateReportButton = page.getByTestId('generate-report-btn');

    this.resumeInterviewButton = page.getByTestId('resume-interview-btn');
    
    // Bulk Operations
    this.selectAllCheckbox = page.getByTestId('select-all-checkbox');
    this.selectedCount = page.getByTestId('selected-count');
    this.bulkActionsBar = page.getByTestId('bulk-actions-bar');
    this.bulkCancelButton = page.getByTestId('bulk-cancel-btn');
    this.bulkExportButton = page.getByTestId('bulk-export-btn');
    this.bulkDeleteButton = page.getByTestId('bulk-delete-btn');
    
    // Filters and Search
    this.searchSection = page.getByTestId('search-section');
    this.searchInput = page.getByTestId('interviews-search');
    this.searchButton = page.getByTestId('search-btn');
    this.clearSearchButton = page.getByTestId('clear-search-btn');
    this.filtersToggle = page.getByTestId('filters-toggle');
    this.filtersPanel = page.getByTestId('filters-panel');
    this.candidateFilter = page.getByTestId('candidate-filter');
    this.jobFilter = page.getByTestId('job-filter');
    this.dateRangeFilter = page.getByTestId('date-range-filter');
    this.applyFiltersButton = page.getByTestId('apply-filters-btn');
    this.clearFiltersButton = page.getByTestId('clear-filters-btn');
    
    // Pagination
    this.paginationSection = page.getByTestId('pagination-section');
    this.paginationInfo = page.getByTestId('pagination-info');
    this.pageSizeSelect = page.getByTestId('page-size-select');
    this.firstPageButton = page.getByTestId('first-page-btn');
    this.prevPageButton = page.getByTestId('prev-page-btn');
    this.nextPageButton = page.getByTestId('next-page-btn');
    this.lastPageButton = page.getByTestId('last-page-btn');
    this.pageNumbers = page.getByTestId('page-number');
    
    // Toast Messages
    this.successToast = page.getByTestId('success-toast');
    this.errorToast = page.getByTestId('error-toast');
    this.warningToast = page.getByTestId('warning-toast');
    this.infoToast = page.getByTestId('info-toast');
    this.copySuccessToast = page.getByTestId('copy-success-toast');
  }

  /**
   * Navigate to interviews page
   */
  async navigateTo() {
    await this.page.goto('/interviews');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Wait for interviews list to load
   */
  async waitForInterviewsToLoad() {
    await this.interviewsSection.waitFor({ state: 'visible' });
    await this.loadingState.waitFor({ state: 'hidden' });
  }

  /**
   * Get interview count
   */
  async getInterviewCount(): Promise<number> {
    return await this.interviewRows.count();
  }

  /**
   * Get interview by index
   */
  async getInterviewByIndex(index: number) {
    const row = this.interviewRows.nth(index);
    return {
      candidate: await row.locator('[data-testid="interview-candidate"]').textContent(),
      job: await row.locator('[data-testid="interview-job"]').textContent(),
      status: await row.locator('[data-testid="interview-status"]').textContent(),
      passKey: await row.locator('[data-testid="interview-pass-key"]').textContent(),
      score: await row.locator('[data-testid="interview-score"]').textContent(),
      riskLevel: await row.locator('[data-testid="interview-risk-level"]').textContent()
    };
  }

  /**
   * Filter interviews by status
   */
  async filterByStatus(status: 'all' | 'pending' | 'in_progress' | 'completed' | 'cancelled') {
    const tabMap = {
      all: this.allInterviewsTab,
      pending: this.pendingTab,
      in_progress: this.inProgressTab,
      completed: this.completedTab,
      cancelled: this.cancelledTab
    };
    
    await tabMap[status].click();
    await this.waitForInterviewsToLoad();
  }

  /**
   * Fill create interview form
   */
  async fillInterviewForm(data: InterviewData) {
    // Select candidate
    await this.candidateSelect.click();
    await this.candidateOption.nth(data.candidateId - 1).click();
    
    // Select job
    await this.jobSelect.click();
    await this.jobOption.nth(data.jobId - 1).click();
    
    // Fill notes if provided
    if (data.notes) {
      await this.notesInput.fill(data.notes);
    }
    
    // Set scheduled date if provided
    if (data.scheduledDate) {
      await this.scheduledDateInput.fill(data.scheduledDate);
    }
  }

  /**
   * Submit interview form
   */
  async submitInterviewForm() {
    await this.saveInterviewButton.click();
  }

  /**
   * Get pass key value
   */
  async getPassKeyValue(): Promise<string> {
    return await this.passKeyValue.textContent() || '';
  }

  /**
   * Copy pass key to clipboard
   */
  async copyPassKey() {
    await this.copyPassKeyButton.click({ force: true });
  }

  /**
   * View interview details
   */
  async viewInterviewDetails(index: number) {
    await this.interviewRows.nth(index).locator('[data-testid="view-details-btn"]').click();
  }



  /**
   * Cancel interview
   */
  async cancelInterview(index: number, reason: string) {
    await this.interviewRows.nth(index).locator('[data-testid="cancel-interview-btn"]').click();
    await this.cancelReasonInput.fill(reason);
    await this.confirmCancelButton.click();
  }

  /**
   * Get tab count for status
   */
  async getTabCount(status: 'pending' | 'in_progress' | 'completed' | 'cancelled'): Promise<number> {
    const tabMap = {
      pending: this.pendingTab,
      in_progress: this.inProgressTab,
      completed: this.completedTab,
      cancelled: this.cancelledTab
    };
    
    const tabText = await tabMap[status].textContent();
    const match = tabText?.match(/\((\d+)\)/);
    return match ? parseInt(match[1]) : 0;
  }

  /**
   * Search interviews
   */
  async searchInterviews(query: string) {
    await this.searchInput.fill(query);
    await this.searchButton.click();
    await this.waitForInterviewsToLoad();
  }

  /**
   * Clear search
   */
  async clearSearch() {
    await this.clearSearchButton.click();
    await this.waitForInterviewsToLoad();
  }

  /**
   * Apply filters
   */
  async applyFilters(filters: InterviewFilter) {
    // Open filters panel if not visible
    const isFiltersVisible = await this.filtersPanel.isVisible();
    if (!isFiltersVisible) {
      await this.filtersToggle.click();
    }

    if (filters.candidateId) {
      await this.candidateFilter.selectOption(filters.candidateId.toString());
    }

    if (filters.jobId) {
      await this.jobFilter.selectOption(filters.jobId.toString());
    }

    await this.applyFiltersButton.click();
    await this.waitForInterviewsToLoad();
  }

  /**
   * Clear all filters
   */
  async clearFilters() {
    await this.clearFiltersButton.click();
    await this.waitForInterviewsToLoad();
  }

  /**
   * Select interview checkbox
   */
  async selectInterview(index: number) {
    await this.interviewRows.nth(index).locator('[data-testid="interview-checkbox"]').check();
  }

  /**
   * Select all interviews
   */
  async selectAllInterviews() {
    await this.selectAllCheckbox.check();
  }

  /**
   * Get selected interviews count
   */
  async getSelectedCount(): Promise<number> {
    const countText = await this.selectedCount.textContent();
    return parseInt(countText?.match(/\d+/)?.[0] || '0');
  }
}
