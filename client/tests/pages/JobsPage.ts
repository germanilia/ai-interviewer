import { Page, Locator } from '@playwright/test';

export interface JobData {
  title: string;
  description?: string;
  department?: string;
}

export interface JobFilter {
  department?: string;
  search?: string;
}

/**
 * Page Object Model for Jobs Management
 * Handles job positions, question templates, and assignment functionality
 */
export class JobsPage {
  readonly page: Page;
  // Main Section
  readonly jobsSection: Locator;
  readonly jobsList: Locator;
  readonly jobsTable: Locator;
  readonly jobRows: Locator;
  readonly emptyState: Locator;
  readonly loadingState: Locator;
  
  // Table Headers
  readonly titleHeader: Locator;
  readonly departmentHeader: Locator;
  readonly questionsCountHeader: Locator;
  readonly interviewsCountHeader: Locator;
  readonly createdByHeader: Locator;
  readonly createdDateHeader: Locator;
  readonly actionsHeader: Locator;
  
  // Toolbar
  readonly toolbar: Locator;
  readonly addJobButton: Locator;
  readonly bulkActionsButton: Locator;
  readonly exportJobsButton: Locator;
  readonly refreshButton: Locator;
  
  // Add/Edit Job Modal
  readonly jobModal: Locator;
  readonly addJobModal: Locator;
  readonly editJobModal: Locator;
  readonly modalTitle: Locator;
  readonly jobForm: Locator;
  readonly titleInput: Locator;
  readonly descriptionTextArea: Locator;
  readonly departmentInput: Locator;
  readonly saveJobButton: Locator;
  readonly cancelButton: Locator;
  readonly modalCloseButton: Locator;
  
  // Form Validation
  readonly titleError: Locator;
  readonly departmentError: Locator;
  readonly formErrors: Locator;
  
  // Job Detail View
  readonly jobDetailView: Locator;
  readonly jobInfo: Locator;
  readonly jobTitle: Locator;
  readonly jobDescription: Locator;
  readonly jobDepartment: Locator;
  readonly jobStats: Locator;
  readonly questionsCount: Locator;
  readonly interviewsCount: Locator;
  readonly avgCompletionTime: Locator;
  readonly successRate: Locator;
  
  // Template Builder
  readonly templateBuilderSection: Locator;
  readonly templateBuilder: Locator;
  readonly availableQuestions: Locator;
  readonly assignedQuestions: Locator;
  readonly questionSearchInput: Locator;
  readonly questionCategoryFilter: Locator;
  readonly questionImportanceFilter: Locator;
  readonly addQuestionButton: Locator;
  readonly removeQuestionButton: Locator;
  readonly moveUpButton: Locator;
  readonly moveDownButton: Locator;
  readonly saveTemplateButton: Locator;
  readonly previewTemplateButton: Locator;
  
  // Template Preview
  readonly templatePreviewModal: Locator;
  readonly previewQuestionsList: Locator;
  readonly previewQuestion: Locator;
  readonly previewQuestionOrder: Locator;
  readonly previewQuestionTitle: Locator;
  readonly previewQuestionImportance: Locator;
  readonly closePreviewButton: Locator;
  
  // Clone Template
  readonly cloneTemplateButton: Locator;
  readonly cloneTemplateModal: Locator;
  readonly sourceJobSelect: Locator;
  readonly targetJobSelect: Locator;
  readonly cloneOptionsCheckbox: Locator;
  readonly confirmCloneButton: Locator;
  readonly cancelCloneButton: Locator;
  
  // Drag and Drop
  readonly dragHandle: Locator;
  readonly dropZone: Locator;
  readonly dragPreview: Locator;
  
  // Statistics
  readonly statisticsSection: Locator;
  readonly totalInterviewsCard: Locator;
  readonly avgScoreCard: Locator;
  readonly completionRateCard: Locator;
  readonly avgTimeCard: Locator;
  
  // Filters and Search
  readonly searchSection: Locator;
  readonly searchInput: Locator;
  readonly searchButton: Locator;
  readonly clearSearchButton: Locator;
  readonly filtersToggle: Locator;
  readonly filtersPanel: Locator;
  readonly departmentFilter: Locator;
  readonly questionsCountFilter: Locator;
  readonly applyFiltersButton: Locator;
  readonly clearFiltersButton: Locator;
  
  // Bulk Operations
  readonly selectAllCheckbox: Locator;
  readonly selectedCount: Locator;
  readonly bulkActionsBar: Locator;
  readonly bulkDeleteButton: Locator;
  readonly bulkExportButton: Locator;
  readonly bulkCloneButton: Locator;
  
  // Delete Confirmation
  readonly deleteConfirmationModal: Locator;
  readonly deleteConfirmationMessage: Locator;
  readonly confirmDeleteButton: Locator;
  readonly cancelDeleteButton: Locator;
  
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
    this.page = page;
    
    // Main Section
    this.jobsSection = page.getByTestId('jobs-section');
    this.jobsList = page.getByTestId('jobs-list');
    this.jobsTable = page.getByTestId('jobs-table');
    this.jobRows = page.getByTestId('job-row');
    this.emptyState = page.getByTestId('jobs-empty-state');
    this.loadingState = page.getByTestId('jobs-loading');
    
    // Table Headers
    this.titleHeader = page.getByTestId('title-header');
    this.departmentHeader = page.getByTestId('department-header');
    this.questionsCountHeader = page.getByTestId('questions-count-header');
    this.interviewsCountHeader = page.getByTestId('interviews-count-header');
    this.createdByHeader = page.getByTestId('created-by-header');
    this.createdDateHeader = page.getByTestId('created-date-header');
    this.actionsHeader = page.getByTestId('actions-header');
    
    // Toolbar
    this.toolbar = page.getByTestId('jobs-toolbar');
    this.addJobButton = page.getByTestId('add-job-btn');
    this.bulkActionsButton = page.getByTestId('bulk-actions-btn');
    this.exportJobsButton = page.getByTestId('export-jobs-btn');
    this.refreshButton = page.getByTestId('refresh-jobs-btn');
    
    // Modals
    this.jobModal = page.getByTestId('job-modal');
    this.addJobModal = page.getByTestId('add-job-modal');
    this.editJobModal = page.getByTestId('edit-job-modal');
    this.modalTitle = page.getByTestId('modal-title');
    this.jobForm = page.getByTestId('job-form');
    this.titleInput = page.getByTestId('title-input');
    this.descriptionTextArea = page.getByTestId('description-text-area');
    this.departmentInput = page.getByTestId('department-input');
    this.saveJobButton = page.getByTestId('save-job-btn');
    this.cancelButton = page.getByTestId('cancel-btn');
    this.modalCloseButton = page.getByTestId('modal-close-btn');
    
    // Form Validation
    this.titleError = page.getByTestId('title-error');
    this.departmentError = page.getByTestId('department-error');
    this.formErrors = page.getByTestId('form-error');
    
    // Job Detail View
    this.jobDetailView = page.getByTestId('job-detail-view');
    this.jobInfo = page.getByTestId('job-info');
    this.jobTitle = page.getByTestId('job-title');
    this.jobDescription = page.getByTestId('job-description');
    this.jobDepartment = page.getByTestId('job-department');
    this.jobStats = page.getByTestId('job-stats');
    this.questionsCount = page.getByTestId('questions-count');
    this.interviewsCount = page.getByTestId('interviews-count');
    this.avgCompletionTime = page.getByTestId('avg-completion-time');
    this.successRate = page.getByTestId('success-rate');
    
    // Template Builder
    this.templateBuilderSection = page.getByTestId('template-builder-section');
    this.templateBuilder = page.getByTestId('template-builder');
    this.availableQuestions = page.getByTestId('available-questions');
    this.assignedQuestions = page.getByTestId('assigned-questions');
    this.questionSearchInput = page.getByTestId('question-search-input');
    this.questionCategoryFilter = page.getByTestId('question-category-filter');
    this.questionImportanceFilter = page.getByTestId('question-importance-filter');
    this.addQuestionButton = page.getByTestId('add-question-btn');
    this.removeQuestionButton = page.getByTestId('remove-question-btn');
    this.moveUpButton = page.getByTestId('move-up-btn');
    this.moveDownButton = page.getByTestId('move-down-btn');
    this.saveTemplateButton = page.getByTestId('save-template-btn');
    this.previewTemplateButton = page.getByTestId('preview-template-btn');
    
    // Template Preview
    this.templatePreviewModal = page.getByTestId('template-preview-modal');
    this.previewQuestionsList = page.getByTestId('preview-questions-list');
    this.previewQuestion = page.getByTestId('preview-question');
    this.previewQuestionOrder = page.getByTestId('preview-question-order');
    this.previewQuestionTitle = page.getByTestId('preview-question-title');
    this.previewQuestionImportance = page.getByTestId('preview-question-importance');
    this.closePreviewButton = page.getByTestId('close-preview-btn');
    
    // Clone Template
    this.cloneTemplateButton = page.getByTestId('clone-template-btn');
    this.cloneTemplateModal = page.getByTestId('clone-template-modal');
    this.sourceJobSelect = page.getByTestId('source-job-select');
    this.targetJobSelect = page.getByTestId('target-job-select');
    this.cloneOptionsCheckbox = page.getByTestId('clone-options-checkbox');
    this.confirmCloneButton = page.getByTestId('confirm-clone-btn');
    this.cancelCloneButton = page.getByTestId('cancel-clone-btn');
    
    // Drag and Drop
    this.dragHandle = page.getByTestId('drag-handle');
    this.dropZone = page.getByTestId('drop-zone');
    this.dragPreview = page.getByTestId('drag-preview');
    
    // Statistics
    this.statisticsSection = page.getByTestId('statistics-section');
    this.totalInterviewsCard = page.getByTestId('total-interviews-card');
    this.avgScoreCard = page.getByTestId('avg-score-card');
    this.completionRateCard = page.getByTestId('completion-rate-card');
    this.avgTimeCard = page.getByTestId('avg-time-card');
    
    // Filters and Search
    this.searchSection = page.getByTestId('search-section');
    this.searchInput = page.getByTestId('jobs-search');
    this.searchButton = page.getByTestId('search-btn');
    this.clearSearchButton = page.getByTestId('clear-search-btn');
    this.filtersToggle = page.getByTestId('filters-toggle');
    this.filtersPanel = page.getByTestId('filters-panel');
    this.departmentFilter = page.getByTestId('department-filter');
    this.questionsCountFilter = page.getByTestId('questions-count-filter');
    this.applyFiltersButton = page.getByTestId('apply-filters-btn');
    this.clearFiltersButton = page.getByTestId('clear-filters-btn');
    
    // Bulk Operations
    this.selectAllCheckbox = page.getByTestId('select-all-checkbox');
    this.selectedCount = page.getByTestId('selected-count');
    this.bulkActionsBar = page.getByTestId('bulk-actions-bar');
    this.bulkDeleteButton = page.getByTestId('bulk-delete-btn');
    this.bulkExportButton = page.getByTestId('bulk-export-btn');
    this.bulkCloneButton = page.getByTestId('bulk-clone-btn');
    
    // Delete Confirmation
    this.deleteConfirmationModal = page.getByTestId('delete-confirmation-modal');
    this.deleteConfirmationMessage = page.getByTestId('delete-confirmation-message');
    this.confirmDeleteButton = page.getByTestId('confirm-delete-btn');
    this.cancelDeleteButton = page.getByTestId('cancel-delete-btn');
    
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
   * Navigate to job positions page
   */
  async navigateTo() {
    await this.page.goto('/job-positions');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Wait for jobs list to load
   */
  async waitForJobsToLoad() {
    await this.jobsSection.waitFor({ state: 'visible' });
    await this.loadingState.waitFor({ state: 'hidden' });
  }

  /**
   * Fill job form
   */
  async fillJobForm(data: JobData) {
    await this.titleInput.fill(data.title);
    
    if (data.description) {
      await this.descriptionTextArea.fill(data.description);
    }
    
    if (data.department) {
      await this.departmentInput.fill(data.department);
    }
  }

  /**
   * Clear job form
   */
  async clearJobForm() {
    await this.titleInput.clear();
    await this.descriptionTextArea.clear();
    await this.departmentInput.clear();
  }

  /**
   * Submit job form
   */
  async submitJobForm() {
    await this.saveJobButton.click();
  }

  /**
   * Cancel job form
   */
  async cancelJobForm() {
    await this.cancelButton.click();
  }

  /**
   * Get job count
   */
  async getJobCount(): Promise<number> {
    return await this.jobRows.count();
  }

  /**
   * Get job by index
   */
  async getJobByIndex(index: number) {
    const row = this.jobRows.nth(index);
    return {
      title: await row.locator('[data-testid="job-title"]').textContent(),
      department: await row.locator('[data-testid="job-department"]').textContent(),
      questionsCount: await row.locator('[data-testid="job-questions-count"]').textContent(),
      interviewsCount: await row.locator('[data-testid="job-interviews-count"]').textContent(),
      createdBy: await row.locator('[data-testid="job-created-by"]').textContent(),
      createdDate: await row.locator('[data-testid="job-created-date"]').textContent()
    };
  }

  /**
   * View job details
   */
  async viewJobDetails(index: number) {
    await this.jobRows.nth(index).locator('[data-testid="view-details-btn"]').click();
  }

  /**
   * Edit job
   */
  async editJob(index: number) {
    await this.jobRows.nth(index).locator('[data-testid="edit-job-btn"]').click();
  }

  /**
   * Delete job
   */
  async deleteJob(index: number) {
    await this.jobRows.nth(index).locator('[data-testid="delete-job-btn"]').click();
  }

  /**
   * Clone job template
   */
  async cloneJobTemplate(sourceIndex: number, targetIndex: number) {
    await this.jobRows.nth(sourceIndex).locator('[data-testid="clone-template-btn"]').click();
    await this.targetJobSelect.selectOption(targetIndex.toString());
    await this.confirmCloneButton.click();
  }

  /**
   * Search jobs
   */
  async searchJobs(query: string) {
    await this.searchInput.fill(query);
    await this.searchButton.click();
    await this.waitForJobsToLoad();
  }

  /**
   * Clear search
   */
  async clearSearch() {
    await this.clearSearchButton.click();
    await this.waitForJobsToLoad();
  }

  /**
   * Add question to job template
   */
  async addQuestionToTemplate(questionIndex: number) {
    await this.availableQuestions.locator('[data-testid="question-item"]').nth(questionIndex).locator('[data-testid="add-question-btn"]').click();
  }

  /**
   * Remove question from job template
   */
  async removeQuestionFromTemplate(questionIndex: number) {
    await this.assignedQuestions.locator('[data-testid="assigned-question"]').nth(questionIndex).locator('[data-testid="remove-question-btn"]').click();
  }

  /**
   * Move question up in template
   */
  async moveQuestionUp(questionIndex: number) {
    await this.assignedQuestions.locator('[data-testid="assigned-question"]').nth(questionIndex).locator('[data-testid="move-up-btn"]').click();
  }

  /**
   * Move question down in template
   */
  async moveQuestionDown(questionIndex: number) {
    await this.assignedQuestions.locator('[data-testid="assigned-question"]').nth(questionIndex).locator('[data-testid="move-down-btn"]').click();
  }

  /**
   * Save template
   */
  async saveTemplate() {
    await this.saveTemplateButton.click();
  }

  /**
   * Preview template
   */
  async previewTemplate() {
    await this.previewTemplateButton.click();
  }

  /**
   * Get assigned questions count
   */
  async getAssignedQuestionsCount(): Promise<number> {
    return await this.assignedQuestions.locator('[data-testid="assigned-question"]').count();
  }

  /**
   * Select job checkbox
   */
  async selectJob(index: number) {
    await this.jobRows.nth(index).locator('[data-testid="job-checkbox"]').check();
  }

  /**
   * Select all jobs
   */
  async selectAllJobs() {
    await this.selectAllCheckbox.check();
  }

  /**
   * Get selected jobs count
   */
  async getSelectedCount(): Promise<number> {
    const countText = await this.selectedCount.textContent();
    return parseInt(countText?.match(/\d+/)?.[0] || '0');
  }
}
