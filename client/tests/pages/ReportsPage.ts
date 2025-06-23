import { Page, Locator } from '@playwright/test';

export interface ReportFilter {
  dateRange?: {
    from: string;
    to: string;
  };
  candidateId?: number;
  jobId?: number;
  riskLevel?: 'low' | 'medium' | 'high' | 'critical';
  status?: 'completed' | 'in_progress' | 'cancelled';
}

/**
 * Page Object Model for Reports and Analytics
 * Handles report generation, analytics dashboard, and export functionality
 */
export class ReportsPage {
  readonly page: Page;
  // Main Section
  readonly reportsSection: Locator;
  readonly reportsContainer: Locator;
  readonly loadingState: Locator;
  
  // Report Types Tabs
  readonly reportTypeTabs: Locator;
  readonly overviewTab: Locator;
  readonly candidateReportsTab: Locator;
  readonly interviewReportsTab: Locator;
  readonly analyticsTab: Locator;
  readonly customReportsTab: Locator;
  
  // Overview Dashboard
  readonly overviewSection: Locator;
  readonly summaryCards: Locator;
  readonly totalInterviewsCard: Locator;
  readonly completionRateCard: Locator;
  readonly avgRiskScoreCard: Locator;
  readonly flaggedCandidatesCard: Locator;
  readonly trendsChart: Locator;
  readonly riskDistributionChart: Locator;
  readonly departmentBreakdownChart: Locator;
  
  // Candidate Reports
  readonly candidateReportsSection: Locator;
  readonly candidateReportsList: Locator;
  readonly candidateReportRows: Locator;
  readonly generateCandidateReportButton: Locator;
  readonly candidateSelect: Locator;
  readonly candidateOption: Locator;
  readonly candidateReportPreview: Locator;
  
  // Interview Reports
  readonly interviewReportsSection: Locator;
  readonly interviewReportsList: Locator;
  readonly interviewReportRows: Locator;
  readonly generateInterviewReportButton: Locator;
  readonly interviewSelect: Locator;
  readonly interviewOption: Locator;
  readonly interviewReportPreview: Locator;
  
  // Analytics Dashboard
  readonly analyticsSection: Locator;
  readonly analyticsFilters: Locator;
  readonly dateRangeFilter: Locator;
  readonly departmentFilter: Locator;
  readonly jobFilter: Locator;
  readonly riskLevelFilter: Locator;
  readonly applyFiltersButton: Locator;
  readonly clearFiltersButton: Locator;
  
  // Analytics Charts
  readonly chartsContainer: Locator;
  readonly interviewVolumeChart: Locator;
  readonly riskTrendsChart: Locator;
  readonly completionRatesChart: Locator;
  readonly scoreDistributionChart: Locator;
  readonly departmentComparisonChart: Locator;
  readonly timeToCompleteChart: Locator;
  
  // Custom Reports
  readonly customReportsSection: Locator;
  readonly reportBuilder: Locator;
  readonly reportNameInput: Locator;
  readonly reportDescriptionInput: Locator;
  readonly dataSourceSelect: Locator;
  readonly fieldsSelector: Locator;
  readonly availableFields: Locator;
  readonly selectedFields: Locator;
  readonly addFieldButton: Locator;
  readonly removeFieldButton: Locator;
  readonly filtersBuilder: Locator;
  readonly addFilterButton: Locator;
  readonly filterCondition: Locator;
  readonly saveReportButton: Locator;
  readonly runReportButton: Locator;
  
  // Report Generation Modal
  readonly reportGenerationModal: Locator;
  readonly modalTitle: Locator;
  readonly reportTypeSelect: Locator;
  readonly reportFormatSelect: Locator;
  readonly includeChartsCheckbox: Locator;
  readonly includeRawDataCheckbox: Locator;
  readonly emailReportCheckbox: Locator;
  readonly emailInput: Locator;
  readonly generateReportButton: Locator;
  readonly cancelButton: Locator;
  
  // Report Preview
  readonly reportPreviewModal: Locator;
  readonly previewContent: Locator;
  readonly previewHeader: Locator;
  readonly previewSummary: Locator;
  readonly previewCharts: Locator;
  readonly previewData: Locator;
  readonly downloadPreviewButton: Locator;
  readonly closePreviewButton: Locator;
  
  // Export Options
  readonly exportModal: Locator;
  readonly exportFormatSelect: Locator;
  readonly pdfOption: Locator;
  readonly excelOption: Locator;
  readonly csvOption: Locator;
  readonly jsonOption: Locator;
  readonly exportSelectedOnly: Locator;
  readonly downloadButton: Locator;
  readonly cancelExportButton: Locator;
  
  // Scheduled Reports
  readonly scheduledReportsSection: Locator;
  readonly scheduledReportsList: Locator;
  readonly scheduleReportButton: Locator;
  readonly scheduleModal: Locator;
  readonly frequencySelect: Locator;
  readonly scheduleTimeInput: Locator;
  readonly recipientsInput: Locator;
  readonly enableScheduleCheckbox: Locator;
  readonly saveScheduleButton: Locator;
  
  // Report History
  readonly reportHistorySection: Locator;
  readonly historyTable: Locator;
  readonly historyRows: Locator;
  readonly downloadHistoryButton: Locator;
  readonly deleteHistoryButton: Locator;
  
  // Search and Filters
  readonly searchSection: Locator;
  readonly searchInput: Locator;
  readonly searchButton: Locator;
  readonly clearSearchButton: Locator;
  readonly filtersToggle: Locator;
  readonly filtersPanel: Locator;
  
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
    this.reportsSection = page.getByTestId('reports-section');
    this.reportsContainer = page.getByTestId('reports-container');
    this.loadingState = page.getByTestId('reports-loading');
    
    // Report Types Tabs
    this.reportTypeTabs = page.getByTestId('report-type-tabs');
    this.overviewTab = page.getByTestId('overview-tab');
    this.candidateReportsTab = page.getByTestId('candidate-reports-tab');
    this.interviewReportsTab = page.getByTestId('interview-reports-tab');
    this.analyticsTab = page.getByTestId('analytics-tab');
    this.customReportsTab = page.getByTestId('custom-reports-tab');
    
    // Overview Dashboard
    this.overviewSection = page.getByTestId('overview-section');
    this.summaryCards = page.getByTestId('summary-cards');
    this.totalInterviewsCard = page.getByTestId('total-interviews-card');
    this.completionRateCard = page.getByTestId('completion-rate-card');
    this.avgRiskScoreCard = page.getByTestId('avg-risk-score-card');
    this.flaggedCandidatesCard = page.getByTestId('flagged-candidates-card');
    this.trendsChart = page.getByTestId('trends-chart');
    this.riskDistributionChart = page.getByTestId('risk-distribution-chart');
    this.departmentBreakdownChart = page.getByTestId('department-breakdown-chart');
    
    // Candidate Reports
    this.candidateReportsSection = page.getByTestId('candidate-reports-section');
    this.candidateReportsList = page.getByTestId('candidate-reports-list');
    this.candidateReportRows = page.getByTestId('candidate-report-row');
    this.generateCandidateReportButton = page.getByTestId('generate-candidate-report-btn');
    this.candidateSelect = page.getByTestId('candidate-select');
    this.candidateOption = page.getByTestId('candidate-option');
    this.candidateReportPreview = page.getByTestId('candidate-report-preview');
    
    // Interview Reports
    this.interviewReportsSection = page.getByTestId('interview-reports-section');
    this.interviewReportsList = page.getByTestId('interview-reports-list');
    this.interviewReportRows = page.getByTestId('interview-report-row');
    this.generateInterviewReportButton = page.getByTestId('generate-interview-report-btn');
    this.interviewSelect = page.getByTestId('interview-select');
    this.interviewOption = page.getByTestId('interview-option');
    this.interviewReportPreview = page.getByTestId('interview-report-preview');
    
    // Analytics Dashboard
    this.analyticsSection = page.getByTestId('analytics-section');
    this.analyticsFilters = page.getByTestId('analytics-filters');
    this.dateRangeFilter = page.getByTestId('date-range-filter');
    this.departmentFilter = page.getByTestId('department-filter');
    this.jobFilter = page.getByTestId('job-filter');
    this.riskLevelFilter = page.getByTestId('risk-level-filter');
    this.applyFiltersButton = page.getByTestId('apply-filters-btn');
    this.clearFiltersButton = page.getByTestId('clear-filters-btn');
    
    // Analytics Charts
    this.chartsContainer = page.getByTestId('charts-container');
    this.interviewVolumeChart = page.getByTestId('interview-volume-chart');
    this.riskTrendsChart = page.getByTestId('risk-trends-chart');
    this.completionRatesChart = page.getByTestId('completion-rates-chart');
    this.scoreDistributionChart = page.getByTestId('score-distribution-chart');
    this.departmentComparisonChart = page.getByTestId('department-comparison-chart');
    this.timeToCompleteChart = page.getByTestId('time-to-complete-chart');
    
    // Custom Reports
    this.customReportsSection = page.getByTestId('custom-reports-section');
    this.reportBuilder = page.getByTestId('report-builder');
    this.reportNameInput = page.getByTestId('report-name-input');
    this.reportDescriptionInput = page.getByTestId('report-description-input');
    this.dataSourceSelect = page.getByTestId('data-source-select');
    this.fieldsSelector = page.getByTestId('fields-selector');
    this.availableFields = page.getByTestId('available-fields');
    this.selectedFields = page.getByTestId('selected-fields');
    this.addFieldButton = page.getByTestId('add-field-btn');
    this.removeFieldButton = page.getByTestId('remove-field-btn');
    this.filtersBuilder = page.getByTestId('filters-builder');
    this.addFilterButton = page.getByTestId('add-filter-btn');
    this.filterCondition = page.getByTestId('filter-condition');
    this.saveReportButton = page.getByTestId('save-report-btn');
    this.runReportButton = page.getByTestId('run-report-btn');
    
    // Report Generation Modal
    this.reportGenerationModal = page.getByTestId('report-generation-modal');
    this.modalTitle = page.getByTestId('modal-title');
    this.reportTypeSelect = page.getByTestId('report-type-select');
    this.reportFormatSelect = page.getByTestId('report-format-select');
    this.includeChartsCheckbox = page.getByTestId('include-charts-checkbox');
    this.includeRawDataCheckbox = page.getByTestId('include-raw-data-checkbox');
    this.emailReportCheckbox = page.getByTestId('email-report-checkbox');
    this.emailInput = page.getByTestId('email-input');
    this.generateReportButton = page.getByTestId('generate-report-btn');
    this.cancelButton = page.getByTestId('cancel-btn');
    
    // Report Preview
    this.reportPreviewModal = page.getByTestId('report-preview-modal');
    this.previewContent = page.getByTestId('preview-content');
    this.previewHeader = page.getByTestId('preview-header');
    this.previewSummary = page.getByTestId('preview-summary');
    this.previewCharts = page.getByTestId('preview-charts');
    this.previewData = page.getByTestId('preview-data');
    this.downloadPreviewButton = page.getByTestId('download-preview-btn');
    this.closePreviewButton = page.getByTestId('close-preview-btn');
    
    // Export Options
    this.exportModal = page.getByTestId('export-modal');
    this.exportFormatSelect = page.getByTestId('export-format-select');
    this.pdfOption = page.getByTestId('pdf-option');
    this.excelOption = page.getByTestId('excel-option');
    this.csvOption = page.getByTestId('csv-option');
    this.jsonOption = page.getByTestId('json-option');
    this.exportSelectedOnly = page.getByTestId('export-selected-only');
    this.downloadButton = page.getByTestId('download-btn');
    this.cancelExportButton = page.getByTestId('cancel-export-btn');
    
    // Scheduled Reports
    this.scheduledReportsSection = page.getByTestId('scheduled-reports-section');
    this.scheduledReportsList = page.getByTestId('scheduled-reports-list');
    this.scheduleReportButton = page.getByTestId('schedule-report-btn');
    this.scheduleModal = page.getByTestId('schedule-modal');
    this.frequencySelect = page.getByTestId('frequency-select');
    this.scheduleTimeInput = page.getByTestId('schedule-time-input');
    this.recipientsInput = page.getByTestId('recipients-input');
    this.enableScheduleCheckbox = page.getByTestId('enable-schedule-checkbox');
    this.saveScheduleButton = page.getByTestId('save-schedule-btn');
    
    // Report History
    this.reportHistorySection = page.getByTestId('report-history-section');
    this.historyTable = page.getByTestId('history-table');
    this.historyRows = page.getByTestId('history-row');
    this.downloadHistoryButton = page.getByTestId('download-history-btn');
    this.deleteHistoryButton = page.getByTestId('delete-history-btn');
    
    // Search and Filters
    this.searchSection = page.getByTestId('search-section');
    this.searchInput = page.getByTestId('reports-search');
    this.searchButton = page.getByTestId('search-btn');
    this.clearSearchButton = page.getByTestId('clear-search-btn');
    this.filtersToggle = page.getByTestId('filters-toggle');
    this.filtersPanel = page.getByTestId('filters-panel');
    
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
   * Navigate to reports page
   */
  async navigateTo() {
    await this.page.goto('/reports');
    await this.page.waitForLoadState('networkidle');
  }

  /**
   * Wait for reports to load
   */
  async waitForReportsToLoad() {
    await this.reportsSection.waitFor({ state: 'visible' });
    await this.loadingState.waitFor({ state: 'hidden' });
  }

  /**
   * Switch to report type tab
   */
  async switchToTab(tab: 'overview' | 'candidate-reports' | 'interview-reports' | 'analytics' | 'custom-reports') {
    const tabMap = {
      overview: this.overviewTab,
      'candidate-reports': this.candidateReportsTab,
      'interview-reports': this.interviewReportsTab,
      analytics: this.analyticsTab,
      'custom-reports': this.customReportsTab
    };
    
    await tabMap[tab].click();
    await this.waitForReportsToLoad();
  }

  /**
   * Generate candidate report
   */
  async generateCandidateReport(candidateId: number, format: 'pdf' | 'excel' | 'csv' = 'pdf') {
    await this.generateCandidateReportButton.click();
    await this.candidateSelect.selectOption(candidateId.toString());
    await this.reportFormatSelect.selectOption(format);
    await this.generateReportButton.click();
  }

  /**
   * Generate interview report
   */
  async generateInterviewReport(interviewId: number, format: 'pdf' | 'excel' | 'csv' = 'pdf') {
    await this.generateInterviewReportButton.click();
    await this.interviewSelect.selectOption(interviewId.toString());
    await this.reportFormatSelect.selectOption(format);
    await this.generateReportButton.click();
  }

  /**
   * Apply analytics filters
   */
  async applyAnalyticsFilters(filters: ReportFilter) {
    if (filters.dateRange) {
      // Implementation would depend on date picker component
      // await this.dateRangeFilter.fill(`${filters.dateRange.from} - ${filters.dateRange.to}`);
    }
    
    if (filters.jobId) {
      await this.jobFilter.selectOption(filters.jobId.toString());
    }
    
    if (filters.riskLevel) {
      await this.riskLevelFilter.selectOption(filters.riskLevel);
    }
    
    await this.applyFiltersButton.click();
    await this.waitForReportsToLoad();
  }

  /**
   * Clear analytics filters
   */
  async clearAnalyticsFilters() {
    await this.clearFiltersButton.click();
    await this.waitForReportsToLoad();
  }

  /**
   * Create custom report
   */
  async createCustomReport(name: string, description: string, dataSource: string) {
    await this.reportNameInput.fill(name);
    await this.reportDescriptionInput.fill(description);
    await this.dataSourceSelect.selectOption(dataSource);
  }

  /**
   * Add field to custom report
   */
  async addFieldToReport(fieldIndex: number) {
    await this.availableFields.locator('[data-testid="field-item"]').nth(fieldIndex).locator('[data-testid="add-field-btn"]').click();
  }

  /**
   * Remove field from custom report
   */
  async removeFieldFromReport(fieldIndex: number) {
    await this.selectedFields.locator('[data-testid="selected-field"]').nth(fieldIndex).locator('[data-testid="remove-field-btn"]').click();
  }

  /**
   * Save custom report
   */
  async saveCustomReport() {
    await this.saveReportButton.click();
  }

  /**
   * Run custom report
   */
  async runCustomReport() {
    await this.runReportButton.click();
  }

  /**
   * Preview report
   */
  async previewReport() {
    // Implementation would depend on which report type is being previewed
    await this.reportPreviewModal.waitFor({ state: 'visible' });
  }

  /**
   * Download report
   */
  async downloadReport(format: 'pdf' | 'excel' | 'csv' | 'json' = 'pdf') {
    await this.exportFormatSelect.selectOption(format);
    await this.downloadButton.click();
  }

  /**
   * Schedule report
   */
  async scheduleReport(frequency: 'daily' | 'weekly' | 'monthly', time: string, recipients: string) {
    await this.scheduleReportButton.click();
    await this.frequencySelect.selectOption(frequency);
    await this.scheduleTimeInput.fill(time);
    await this.recipientsInput.fill(recipients);
    await this.enableScheduleCheckbox.check();
    await this.saveScheduleButton.click();
  }

  /**
   * Get report history count
   */
  async getReportHistoryCount(): Promise<number> {
    return await this.historyRows.count();
  }

  /**
   * Download report from history
   */
  async downloadFromHistory(index: number) {
    await this.historyRows.nth(index).locator('[data-testid="download-history-btn"]').click();
  }

  /**
   * Delete report from history
   */
  async deleteFromHistory(index: number) {
    await this.historyRows.nth(index).locator('[data-testid="delete-history-btn"]').click();
  }
}
