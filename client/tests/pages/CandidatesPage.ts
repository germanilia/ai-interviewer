import { Page, Locator } from '@playwright/test';

export interface CandidateData {
  firstName: string;
  lastName: string;
  email: string;
  phone?: string;
  interviewId?: string;
}

export interface CandidateFilter {
  search?: string;
  status?: 'all' | 'active' | 'completed' | 'pending';
  dateRange?: {
    from: string;
    to: string;
  };
  riskLevel?: 'low' | 'medium' | 'high' | 'critical';
}

/**
 * Page Object Model for Candidates Management
 * Handles candidate CRUD operations, search, filtering, and bulk operations
 */
export class CandidatesPage {
  readonly page: Page;
  // Main List View
  readonly candidatesSection: Locator;
  readonly candidatesList: Locator;
  readonly candidatesTable: Locator;
  readonly candidateRows: Locator;
  readonly emptyState: Locator;
  readonly loadingState: Locator;
  
  // Table Headers
  readonly nameHeader: Locator;
  readonly emailHeader: Locator;
  readonly phoneHeader: Locator;
  readonly interviewAssignmentHeader: Locator;
  readonly interviewDateHeader: Locator;
  readonly statusHeader: Locator;
  readonly actionsHeader: Locator;
  
  // Toolbar
  readonly toolbar: Locator;
  readonly addCandidateButton: Locator;
  readonly bulkActionsButton: Locator;
  readonly exportButton: Locator;
  readonly refreshButton: Locator;
  
  // Search and Filters
  readonly searchSection: Locator;
  readonly searchInput: Locator;
  readonly clearSearchButton: Locator;
  readonly statusFilter: Locator;
  
  // Pagination
  readonly paginationSection: Locator;
  readonly paginationInfo: Locator;
  readonly pageSizeSelect: Locator;
  readonly firstPageButton: Locator;
  readonly prevPageButton: Locator;
  readonly nextPageButton: Locator;
  readonly lastPageButton: Locator;
  readonly pageNumbers: Locator;
  
  // Add/Edit Modal
  readonly candidateModal: Locator;
  readonly addCandidateModal: Locator;
  readonly editCandidateModal: Locator;
  readonly modalTitle: Locator;
  readonly modalForm: Locator;
  readonly firstNameInput: Locator;
  readonly lastNameInput: Locator;
  readonly emailInput: Locator;
  readonly phoneInput: Locator;
  readonly interviewSelect: Locator;
  readonly saveCandidateButton: Locator;
  readonly cancelButton: Locator;
  readonly modalCloseButton: Locator;
  
  // Form Validation
  readonly firstNameError: Locator;
  readonly lastNameError: Locator;
  readonly emailError: Locator;
  readonly phoneError: Locator;
  readonly formErrors: Locator;
  readonly interviewError: Locator;
  
  // Detail View
  readonly candidateDetailView: Locator;
  readonly candidateInfo: Locator;
  readonly candidateAvatar: Locator;
  readonly candidateStats: Locator;
  readonly interviewHistorySection: Locator;
  readonly interviewHistoryTable: Locator;
  readonly createInterviewButton: Locator;
  readonly viewReportsButton: Locator;
  readonly editCandidateButton: Locator;
  readonly deleteCandidateButton: Locator;
  
  // Bulk Operations
  readonly selectAllCheckbox: Locator;
  readonly selectedCount: Locator;
  readonly bulkActionsBar: Locator;
  readonly bulkExportButton: Locator;
  readonly bulkDeleteButton: Locator;
  readonly bulkAssignButton: Locator;
  
  // Delete Confirmation
  readonly deleteConfirmationModal: Locator;
  readonly deleteConfirmationMessage: Locator;
  readonly confirmDeleteButton: Locator;
  readonly cancelDeleteButton: Locator;
  
  // Bulk Delete Confirmation
  readonly bulkDeleteConfirmationModal: Locator;
  readonly bulkDeleteCount: Locator;
  readonly confirmBulkDeleteButton: Locator;
  
  // Toast Messages
  readonly successToast: Locator;
  readonly errorToast: Locator;
  readonly errorToastDescription: Locator;
  readonly warningToast: Locator;
  readonly infoToast: Locator;

  constructor(page: Page) {
    this.page = page;
    
    // Main List View
    this.candidatesSection = page.getByTestId('candidates-section');
    this.candidatesList = page.getByTestId('candidates-list');
    this.candidatesTable = page.getByTestId('candidates-table');
    this.candidateRows = page.getByTestId('candidate-row');
    this.emptyState = page.getByTestId('candidates-empty-state');
    this.loadingState = page.getByTestId('candidates-loading');
    
    // Table Headers
    this.nameHeader = page.getByTestId('name-header');
    this.emailHeader = page.getByTestId('email-header');
    this.phoneHeader = page.getByTestId('phone-header');
    this.interviewAssignmentHeader = page.getByTestId('interview-assignment-header');
    this.interviewDateHeader = page.getByTestId('interview-date-header');
    this.statusHeader = page.getByTestId('status-header');
    this.actionsHeader = page.getByTestId('actions-header');
    
    // Toolbar
    this.toolbar = page.getByTestId('candidates-toolbar');
    this.addCandidateButton = page.getByTestId('add-candidate-btn');
    this.bulkActionsButton = page.getByTestId('bulk-actions-btn');
    this.exportButton = page.getByTestId('export-candidates-btn');
    this.refreshButton = page.getByTestId('refresh-candidates-btn');
    
    // Search and Filters
    this.searchSection = page.getByTestId('search-section');
    this.searchInput = page.getByTestId('candidates-search');
    this.clearSearchButton = page.getByTestId('clear-search-btn');
    this.statusFilter = page.getByTestId('status-filter');
    
    // Pagination
    this.paginationSection = page.getByTestId('pagination-section');
    this.paginationInfo = page.getByTestId('pagination-info');
    this.pageSizeSelect = page.getByTestId('page-size-select');
    this.firstPageButton = page.getByTestId('first-page-btn');
    this.prevPageButton = page.getByTestId('prev-page-btn');
    this.nextPageButton = page.getByTestId('next-page-btn');
    this.lastPageButton = page.getByTestId('last-page-btn');
    this.pageNumbers = page.getByTestId('page-number');
    
    // Modals
    this.candidateModal = page.getByTestId('candidate-modal');
    this.addCandidateModal = page.getByTestId('add-candidate-modal');
    this.editCandidateModal = page.getByTestId('edit-candidate-modal');
    this.modalTitle = page.getByTestId('modal-title');
    this.modalForm = page.getByTestId('candidate-form');
    this.firstNameInput = page.getByTestId('first-name-input');
    this.lastNameInput = page.getByTestId('last-name-input');
    this.emailInput = page.getByTestId('email-input');
    this.phoneInput = page.getByTestId('phone-input');
    this.interviewSelect = page.getByTestId('interview-select');
    this.saveCandidateButton = page.getByTestId('save-candidate-btn');
    this.cancelButton = page.getByTestId('cancel-btn');
    this.modalCloseButton = page.getByTestId('modal-close-btn');
    
    // Form Validation
    this.firstNameError = page.getByTestId('first-name-error');
    this.lastNameError = page.getByTestId('last-name-error');
    this.emailError = page.getByTestId('email-error');
    this.phoneError = page.getByTestId('phone-error');
    this.formErrors = page.getByTestId('form-error');
    this.interviewError = page.getByTestId('interview-error');
    
    // Detail View
    this.candidateDetailView = page.getByTestId('candidate-detail-view');
    this.candidateInfo = page.getByTestId('candidate-info');
    this.candidateAvatar = page.getByTestId('candidate-avatar');
    this.candidateStats = page.getByTestId('candidate-stats');
    this.interviewHistorySection = page.getByTestId('interview-history-section');
    this.interviewHistoryTable = page.getByTestId('interview-history-table');
    this.createInterviewButton = page.getByTestId('create-interview-button');
    this.viewReportsButton = page.getByTestId('view-reports-button');
    this.editCandidateButton = page.getByTestId('edit-candidate-button');
    this.deleteCandidateButton = page.getByTestId('delete-candidate-button');
    
    // Bulk Operations
    this.selectAllCheckbox = page.getByTestId('select-all-checkbox');
    this.selectedCount = page.getByTestId('selected-count');
    this.bulkActionsBar = page.getByTestId('bulk-actions-bar');
    this.bulkExportButton = page.getByTestId('bulk-export-btn');
    this.bulkDeleteButton = page.getByTestId('bulk-delete-btn');
    this.bulkAssignButton = page.getByTestId('bulk-assign-btn');
    
    // Delete Confirmations
    this.deleteConfirmationModal = page.getByTestId('delete-confirmation-modal');
    this.deleteConfirmationMessage = page.getByTestId('delete-confirmation-message');
    this.confirmDeleteButton = page.getByTestId('confirm-delete-btn');
    this.cancelDeleteButton = page.getByTestId('cancel-delete-btn');
    
    this.bulkDeleteConfirmationModal = page.getByTestId('bulk-delete-confirmation-modal');
    this.bulkDeleteCount = page.getByTestId('bulk-delete-count');
    this.confirmBulkDeleteButton = page.getByTestId('confirm-bulk-delete-btn');
    
    // Toast Messages
    this.successToast = page.getByTestId('success-toast');
    this.errorToast = page.getByTestId('error-toast');
    this.errorToastDescription = page.getByTestId('error-toast').locator('[data-radix-toast-description]');
    this.warningToast = page.getByTestId('warning-toast');
    this.infoToast = page.getByTestId('info-toast');
  }

  /**
   * Navigate to candidates page
   */
  async navigateTo() {
    await this.page.goto('/candidates');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Wait for candidates list to load
   */
  async waitForCandidatesToLoad() {
    await this.candidatesSection.waitFor({ state: 'visible' });
    await this.loadingState.waitFor({ state: 'hidden' });
  }

  /**
   * Fill candidate form with data
   */
  async fillCandidateForm(data: CandidateData) {
    await this.firstNameInput.fill(data.firstName);
    await this.lastNameInput.fill(data.lastName);
    await this.emailInput.fill(data.email);
    if (data.phone) {
      await this.phoneInput.fill(data.phone);
    }
    if (data.interviewId) {
      await this.interviewSelect.selectOption(data.interviewId);
    }
  }

  /**
   * Clear candidate form
   */
  async clearCandidateForm() {
    await this.firstNameInput.clear();
    await this.lastNameInput.clear();
    await this.emailInput.clear();
    await this.phoneInput.clear();
    // Note: Interview select will be cleared when modal reopens
  }

  /**
   * Submit candidate form
   */
  async submitCandidateForm() {
    await this.saveCandidateButton.click();
  }

  /**
   * Cancel candidate form
   */
  async cancelCandidateForm() {
    await this.cancelButton.click();
  }

  /**
   * Search for candidates
   */
  async searchCandidates(query: string) {
    await this.searchInput.fill(query);
    await this.searchButton.click();
    await this.waitForCandidatesToLoad();
  }

  /**
   * Clear search
   */
  async clearSearch() {
    await this.clearSearchButton.click();
    await this.waitForCandidatesToLoad();
  }

  /**
   * Apply filters
   */
  async applyFilters(filters: CandidateFilter) {
    if (filters.search) {
      await this.searchInput.fill(filters.search);
      // Wait for debounced search to trigger
      await this.page.waitForTimeout(500);
    }

    if (filters.status) {
      // Click the select trigger to open dropdown
      await this.statusFilter.click();
      // Click the specific option
      await this.page.getByRole('option', { name: filters.status }).click();
    }

    await this.waitForCandidatesToLoad();
  }

  /**
   * Clear search
   */
  async clearSearch() {
    if (await this.clearSearchButton.isVisible()) {
      await this.clearSearchButton.click();
      await this.waitForCandidatesToLoad();
    }
  }

  /**
   * Get candidate count
   */
  async getCandidateCount(): Promise<number> {
    return await this.candidateRows.count();
  }

  /**
   * Get candidate by index
   */
  async getCandidateByIndex(index: number) {
    const row = this.candidateRows.nth(index);
    return {
      name: await row.locator('[data-testid="candidate-name"]').textContent(),
      email: await row.locator('[data-testid="candidate-email"]').textContent(),
      phone: await row.locator('[data-testid="candidate-phone"]').textContent(),
      interviewAssignment: await row.locator('[data-testid="candidate-interview"]').textContent(),
      interviewDate: await row.locator('[data-testid="candidate-interview-date"]').textContent(),
      status: await row.locator('[data-testid="candidate-status"]').textContent()
    };
  }

  /**
   * Click candidate by name to view details
   */
  async viewCandidateDetails(candidateName: string) {
    const candidateRow = this.candidateRows.filter({ hasText: candidateName });
    await candidateRow.locator('[data-testid="candidate-name"]').click();
  }

  /**
   * Edit candidate by name
   */
  async editCandidate(candidateName: string) {
    const candidateRow = this.candidateRows.filter({ hasText: candidateName });
    await candidateRow.locator('[data-testid="edit-candidate-btn"]').click();
  }

  /**
   * Delete candidate by name
   */
  async deleteCandidate(candidateName: string) {
    const candidateRow = this.candidateRows.filter({ hasText: candidateName });
    await candidateRow.locator('[data-testid="delete-candidate-btn"]').click();
  }

  /**
   * Select candidate checkbox
   */
  async selectCandidate(candidateName: string) {
    const candidateRow = this.candidateRows.filter({ hasText: candidateName });
    await candidateRow.locator('[data-testid="candidate-checkbox"]').check();
  }

  /**
   * Select all candidates
   */
  async selectAllCandidates() {
    await this.selectAllCheckbox.check();
  }

  /**
   * Get selected candidates count
   */
  async getSelectedCount(): Promise<number> {
    const countText = await this.selectedCount.textContent();
    return parseInt(countText?.match(/\d+/)?.[0] || '0');
  }

  /**
   * Verify candidate exists in list
   */
  async expectCandidateInList(fullName: string) {
    const candidateRow = this.candidateRows.filter({ hasText: fullName });
    await candidateRow.waitFor({ state: 'visible' });
  }

  /**
   * Verify candidate does not exist in list
   */
  async expectCandidateNotInList(fullName: string) {
    const candidateRow = this.candidateRows.filter({ hasText: fullName });
    await candidateRow.waitFor({ state: 'hidden' });
  }

  /**
   * Go to specific page
   */
  async goToPage(pageNumber: number) {
    const pageButton = this.pageNumbers.filter({ hasText: pageNumber.toString() });
    await pageButton.click();
    await this.waitForCandidatesToLoad();
  }

  /**
   * Change page size
   */
  async changePageSize(size: number) {
    await this.pageSizeSelect.selectOption(size.toString());
    await this.waitForCandidatesToLoad();
  }

  /**
   * Get pagination info
   */
  async getPaginationInfo() {
    const infoText = await this.paginationInfo.textContent();
    const match = infoText?.match(/(\d+)-(\d+) of (\d+)/);
    if (match) {
      return {
        start: parseInt(match[1]),
        end: parseInt(match[2]),
        total: parseInt(match[3])
      };
    }
    return { start: 0, end: 0, total: 0 };
  }
}
