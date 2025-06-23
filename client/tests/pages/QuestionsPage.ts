import { Page, Locator } from '@playwright/test';
import { AdminLayoutPage } from './AdminLayoutPage';

export interface QuestionData {
  title: string;
  questionText: string;
  instructions?: string;
  importance: 'optional' | 'ask_once' | 'mandatory';
  category: 'criminal_background' | 'drug_use' | 'ethics' | 'dismissals' | 'trustworthiness' | 'general';
}

export interface QuestionFilter {
  category?: string;
  importance?: string;
  search?: string;
}

/**
 * Page Object Model for Questions Management
 * Handles question bank CRUD operations, categories, and job assignments
 */
export class QuestionsPage extends AdminLayoutPage {
  // Main Section
  readonly questionsSection: Locator;
  readonly questionsList: Locator;
  readonly questionsTable: Locator;
  readonly questionRows: Locator;
  readonly emptyState: Locator;
  readonly loadingState: Locator;
  
  // Table Headers
  readonly titleHeader: Locator;
  readonly categoryHeader: Locator;
  readonly importanceHeader: Locator;
  readonly createdByHeader: Locator;
  readonly createdDateHeader: Locator;
  readonly actionsHeader: Locator;
  
  // Toolbar
  readonly toolbar: Locator;
  readonly addQuestionButton: Locator;
  readonly bulkActionsButton: Locator;
  readonly importQuestionsButton: Locator;
  readonly exportQuestionsButton: Locator;
  readonly refreshButton: Locator;
  
  // Add/Edit Question Modal
  readonly questionModal: Locator;
  readonly addQuestionModal: Locator;
  readonly editQuestionModal: Locator;
  readonly modalTitle: Locator;
  readonly questionForm: Locator;
  readonly titleInput: Locator;
  readonly questionTextArea: Locator;
  readonly instructionsTextArea: Locator;
  readonly importanceSelect: Locator;
  readonly categorySelect: Locator;
  readonly saveQuestionButton: Locator;
  readonly cancelButton: Locator;
  readonly modalCloseButton: Locator;
  
  // Form Validation
  readonly titleError: Locator;
  readonly questionTextError: Locator;
  readonly importanceError: Locator;
  readonly categoryError: Locator;
  readonly formErrors: Locator;
  
  // Question Preview
  readonly previewButton: Locator;
  readonly previewModal: Locator;
  readonly previewTitle: Locator;
  readonly previewQuestionText: Locator;
  readonly previewInstructions: Locator;
  readonly previewImportance: Locator;
  readonly previewCategory: Locator;
  readonly closePreviewButton: Locator;
  
  // Category Management
  readonly categorySection: Locator;
  readonly categoryTabs: Locator;
  readonly allCategoriesTab: Locator;
  readonly criminalBackgroundTab: Locator;
  readonly drugUseTab: Locator;
  readonly ethicsTab: Locator;
  readonly dismissalsTab: Locator;
  readonly trustworthinessTab: Locator;
  readonly generalTab: Locator;
  
  // Filters and Search
  readonly searchSection: Locator;
  readonly searchInput: Locator;
  readonly searchButton: Locator;
  readonly clearSearchButton: Locator;
  readonly filtersToggle: Locator;
  readonly filtersPanel: Locator;
  readonly categoryFilter: Locator;
  readonly importanceFilter: Locator;
  readonly createdByFilter: Locator;
  readonly applyFiltersButton: Locator;
  readonly clearFiltersButton: Locator;
  
  // Bulk Operations
  readonly selectAllCheckbox: Locator;
  readonly selectedCount: Locator;
  readonly bulkActionsBar: Locator;
  readonly bulkDeleteButton: Locator;
  readonly bulkExportButton: Locator;
  readonly bulkAssignButton: Locator;
  readonly bulkCategoryChangeButton: Locator;
  
  // Delete Confirmation
  readonly deleteConfirmationModal: Locator;
  readonly deleteConfirmationMessage: Locator;
  readonly confirmDeleteButton: Locator;
  readonly cancelDeleteButton: Locator;
  
  // Bulk Delete Confirmation
  readonly bulkDeleteConfirmationModal: Locator;
  readonly bulkDeleteCount: Locator;
  readonly confirmBulkDeleteButton: Locator;
  
  // Job Assignment
  readonly assignToJobButton: Locator;
  readonly jobAssignmentModal: Locator;
  readonly jobSelect: Locator;
  readonly jobOption: Locator;
  readonly assignmentOrderInput: Locator;
  readonly confirmAssignmentButton: Locator;
  readonly cancelAssignmentButton: Locator;
  
  // Import/Export
  readonly importModal: Locator;
  readonly fileUploadInput: Locator;
  readonly uploadButton: Locator;
  readonly importPreview: Locator;
  readonly confirmImportButton: Locator;
  readonly cancelImportButton: Locator;
  
  readonly exportModal: Locator;
  readonly exportFormatSelect: Locator;
  readonly exportSelectedOnly: Locator;
  readonly downloadButton: Locator;
  readonly cancelExportButton: Locator;
  
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

  constructor(page: Page) {
    super(page);
    
    // Main Section
    this.questionsSection = page.getByTestId('questions-section');
    this.questionsList = page.getByTestId('questions-list');
    this.questionsTable = page.getByTestId('questions-table');
    this.questionRows = page.getByTestId('question-row');
    this.emptyState = page.getByTestId('questions-empty-state');
    this.loadingState = page.getByTestId('questions-loading');
    
    // Table Headers
    this.titleHeader = page.getByTestId('title-header');
    this.categoryHeader = page.getByTestId('category-header');
    this.importanceHeader = page.getByTestId('importance-header');
    this.createdByHeader = page.getByTestId('created-by-header');
    this.createdDateHeader = page.getByTestId('created-date-header');
    this.actionsHeader = page.getByTestId('actions-header');
    
    // Toolbar
    this.toolbar = page.getByTestId('questions-toolbar');
    this.addQuestionButton = page.getByTestId('add-question-btn');
    this.bulkActionsButton = page.getByTestId('bulk-actions-btn');
    this.importQuestionsButton = page.getByTestId('import-questions-btn');
    this.exportQuestionsButton = page.getByTestId('export-questions-btn');
    this.refreshButton = page.getByTestId('refresh-questions-btn');
    
    // Modals
    this.questionModal = page.getByTestId('question-modal');
    this.addQuestionModal = page.getByTestId('add-question-modal');
    this.editQuestionModal = page.getByTestId('edit-question-modal');
    this.modalTitle = page.getByTestId('modal-title');
    this.questionForm = page.getByTestId('question-form');
    this.titleInput = page.getByTestId('title-input');
    this.questionTextArea = page.getByTestId('question-text-area');
    this.instructionsTextArea = page.getByTestId('instructions-text-area');
    this.importanceSelect = page.getByTestId('importance-select');
    this.categorySelect = page.getByTestId('category-select');
    this.saveQuestionButton = page.getByTestId('save-question-btn');
    this.cancelButton = page.getByTestId('cancel-btn');
    this.modalCloseButton = page.getByTestId('modal-close-btn');
    
    // Form Validation
    this.titleError = page.getByTestId('title-error');
    this.questionTextError = page.getByTestId('question-text-error');
    this.importanceError = page.getByTestId('importance-error');
    this.categoryError = page.getByTestId('category-error');
    this.formErrors = page.getByTestId('form-error');
    
    // Question Preview
    this.previewButton = page.getByTestId('preview-question-btn');
    this.previewModal = page.getByTestId('preview-modal');
    this.previewTitle = page.getByTestId('preview-title');
    this.previewQuestionText = page.getByTestId('preview-question-text');
    this.previewInstructions = page.getByTestId('preview-instructions');
    this.previewImportance = page.getByTestId('preview-importance');
    this.previewCategory = page.getByTestId('preview-category');
    this.closePreviewButton = page.getByTestId('close-preview-btn');
    
    // Category Management
    this.categorySection = page.getByTestId('category-section');
    this.categoryTabs = page.getByTestId('category-tabs');
    this.allCategoriesTab = page.getByTestId('all-categories-tab');
    this.criminalBackgroundTab = page.getByTestId('criminal-background-tab');
    this.drugUseTab = page.getByTestId('drug-use-tab');
    this.ethicsTab = page.getByTestId('ethics-tab');
    this.dismissalsTab = page.getByTestId('dismissals-tab');
    this.trustworthinessTab = page.getByTestId('trustworthiness-tab');
    this.generalTab = page.getByTestId('general-tab');
    
    // Filters and Search
    this.searchSection = page.getByTestId('search-section');
    this.searchInput = page.getByTestId('questions-search');
    this.searchButton = page.getByTestId('search-btn');
    this.clearSearchButton = page.getByTestId('clear-search-btn');
    this.filtersToggle = page.getByTestId('filters-toggle');
    this.filtersPanel = page.getByTestId('filters-panel');
    this.categoryFilter = page.getByTestId('category-filter');
    this.importanceFilter = page.getByTestId('importance-filter');
    this.createdByFilter = page.getByTestId('created-by-filter');
    this.applyFiltersButton = page.getByTestId('apply-filters-btn');
    this.clearFiltersButton = page.getByTestId('clear-filters-btn');
    
    // Bulk Operations
    this.selectAllCheckbox = page.getByTestId('select-all-checkbox');
    this.selectedCount = page.getByTestId('selected-count');
    this.bulkActionsBar = page.getByTestId('bulk-actions-bar');
    this.bulkDeleteButton = page.getByTestId('bulk-delete-btn');
    this.bulkExportButton = page.getByTestId('bulk-export-btn');
    this.bulkAssignButton = page.getByTestId('bulk-assign-btn');
    this.bulkCategoryChangeButton = page.getByTestId('bulk-category-change-btn');
    
    // Delete Confirmations
    this.deleteConfirmationModal = page.getByTestId('delete-confirmation-modal');
    this.deleteConfirmationMessage = page.getByTestId('delete-confirmation-message');
    this.confirmDeleteButton = page.getByTestId('confirm-delete-btn');
    this.cancelDeleteButton = page.getByTestId('cancel-delete-btn');
    
    this.bulkDeleteConfirmationModal = page.getByTestId('bulk-delete-confirmation-modal');
    this.bulkDeleteCount = page.getByTestId('bulk-delete-count');
    this.confirmBulkDeleteButton = page.getByTestId('confirm-bulk-delete-btn');
    
    // Job Assignment
    this.assignToJobButton = page.getByTestId('assign-to-job-btn');
    this.jobAssignmentModal = page.getByTestId('job-assignment-modal');
    this.jobSelect = page.getByTestId('job-select');
    this.jobOption = page.getByTestId('job-option');
    this.assignmentOrderInput = page.getByTestId('assignment-order-input');
    this.confirmAssignmentButton = page.getByTestId('confirm-assignment-btn');
    this.cancelAssignmentButton = page.getByTestId('cancel-assignment-btn');
    
    // Import/Export
    this.importModal = page.getByTestId('import-modal');
    this.fileUploadInput = page.getByTestId('file-upload-input');
    this.uploadButton = page.getByTestId('upload-btn');
    this.importPreview = page.getByTestId('import-preview');
    this.confirmImportButton = page.getByTestId('confirm-import-btn');
    this.cancelImportButton = page.getByTestId('cancel-import-btn');
    
    this.exportModal = page.getByTestId('export-modal');
    this.exportFormatSelect = page.getByTestId('export-format-select');
    this.exportSelectedOnly = page.getByTestId('export-selected-only');
    this.downloadButton = page.getByTestId('download-btn');
    this.cancelExportButton = page.getByTestId('cancel-export-btn');
    
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
  }

  /**
   * Navigate to questions page
   */
  async navigateTo() {
    await this.page.goto('/admin/questions');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Wait for questions list to load
   */
  async waitForQuestionsToLoad() {
    await this.questionsSection.waitFor({ state: 'visible' });
    await this.loadingState.waitFor({ state: 'hidden' });
  }

  /**
   * Fill question form
   */
  async fillQuestionForm(data: QuestionData) {
    await this.titleInput.fill(data.title);
    await this.questionTextArea.fill(data.questionText);
    
    if (data.instructions) {
      await this.instructionsTextArea.fill(data.instructions);
    }
    
    await this.importanceSelect.selectOption(data.importance);
    await this.categorySelect.selectOption(data.category);
  }

  /**
   * Clear question form
   */
  async clearQuestionForm() {
    await this.titleInput.clear();
    await this.questionTextArea.clear();
    await this.instructionsTextArea.clear();
  }

  /**
   * Submit question form
   */
  async submitQuestionForm() {
    await this.saveQuestionButton.click();
  }

  /**
   * Cancel question form
   */
  async cancelQuestionForm() {
    await this.cancelButton.click();
  }

  /**
   * Get question count
   */
  async getQuestionCount(): Promise<number> {
    return await this.questionRows.count();
  }

  /**
   * Get question by index
   */
  async getQuestionByIndex(index: number) {
    const row = this.questionRows.nth(index);
    return {
      title: await row.locator('[data-testid="question-title"]').textContent(),
      category: await row.locator('[data-testid="question-category"]').textContent(),
      importance: await row.locator('[data-testid="question-importance"]').textContent(),
      createdBy: await row.locator('[data-testid="question-created-by"]').textContent(),
      createdDate: await row.locator('[data-testid="question-created-date"]').textContent()
    };
  }

  /**
   * Filter questions by category
   */
  async filterByCategory(category: 'all' | 'criminal_background' | 'drug_use' | 'ethics' | 'dismissals' | 'trustworthiness' | 'general') {
    const tabMap = {
      all: this.allCategoriesTab,
      criminal_background: this.criminalBackgroundTab,
      drug_use: this.drugUseTab,
      ethics: this.ethicsTab,
      dismissals: this.dismissalsTab,
      trustworthiness: this.trustworthinessTab,
      general: this.generalTab
    };
    
    await tabMap[category].click();
    await this.waitForQuestionsToLoad();
  }

  /**
   * Search questions
   */
  async searchQuestions(query: string) {
    await this.searchInput.fill(query);
    await this.searchButton.click();
    await this.waitForQuestionsToLoad();
  }

  /**
   * Clear search
   */
  async clearSearch() {
    await this.clearSearchButton.click();
    await this.waitForQuestionsToLoad();
  }

  /**
   * Preview question
   */
  async previewQuestion(index: number) {
    await this.questionRows.nth(index).locator('[data-testid="preview-question-btn"]').click();
  }

  /**
   * Edit question
   */
  async editQuestion(index: number) {
    await this.questionRows.nth(index).locator('[data-testid="edit-question-btn"]').click();
  }

  /**
   * Delete question
   */
  async deleteQuestion(index: number) {
    await this.questionRows.nth(index).locator('[data-testid="delete-question-btn"]').click();
  }

  /**
   * Assign question to job
   */
  async assignQuestionToJob(index: number, jobId: number, order?: number) {
    await this.questionRows.nth(index).locator('[data-testid="assign-to-job-btn"]').click();
    await this.jobSelect.selectOption(jobId.toString());
    
    if (order) {
      await this.assignmentOrderInput.fill(order.toString());
    }
    
    await this.confirmAssignmentButton.click();
  }

  /**
   * Select question checkbox
   */
  async selectQuestion(index: number) {
    await this.questionRows.nth(index).locator('[data-testid="question-checkbox"]').check();
  }

  /**
   * Select all questions
   */
  async selectAllQuestions() {
    await this.selectAllCheckbox.check();
  }

  /**
   * Get selected questions count
   */
  async getSelectedCount(): Promise<number> {
    const countText = await this.selectedCount.textContent();
    return parseInt(countText?.match(/\d+/)?.[0] || '0');
  }
}
