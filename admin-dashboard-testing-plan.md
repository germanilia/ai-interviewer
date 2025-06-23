# Interview Management Dashboard Testing Plan
## Playwright E2E Tests with Real APIs - Unified Dashboard Approach

### Overview
This document outlines a comprehensive testing strategy for the enhanced dashboard with interview management capabilities using Playwright with headless Chrome, testing against real backend APIs. The enhanced dashboard extends the existing layout and navigation components. Tests are organized to enable test-driven development where we write tests first, then implement functionality piece by piece.

---

## 🏗️ Testing Architecture - Unified Approach

### Key Principles
- **Single Dashboard**: Tests work with one unified dashboard, not separate admin interface
- **Extended Existing Layout**: Tests verify new navigation items added to existing AppLayout
- **Universal Access**: All users can access interview management features
- **Clean Structure**: Simplified test organization without admin-specific directories

### Test Organization (Updated Structure)
```
tests/
├── integration/
│   ├── admin-dashboard/
│   │   ├── 00-admin-layout.spec.ts (UPDATED - tests AppLayout + new navigation)
│   │   ├── 01-dashboard-overview.spec.ts (Enhanced existing dashboard)
│   │   ├── 02-candidates-management.spec.ts
│   │   ├── 03-interviews-management.spec.ts
│   │   ├── 04-questions-management.spec.ts
│   │   ├── 05-jobs-management.spec.ts
│   │   └── 06-reports-analytics.spec.ts
│   └── regression/
│       └── interview-dashboard-regression.spec.ts
├── pages/
│   ├── AppLayoutPage.ts (UPDATED - tests existing layout + new features)
│   ├── DashboardPage.ts (existing dashboard)
│   ├── CandidatesPage.ts (new)
│   ├── InterviewsPage.ts (new)
│   ├── QuestionsPage.ts (new)
│   ├── JobsPage.ts (new)
│   ├── ReportsPage.ts (new)
│   └── LoginPage.ts (existing)
└── utils/
    ├── interviewTestData.ts (renamed from adminTestData.ts)
    ├── apiHelpers.ts
    └── testSetup.ts
```

### Completed Structure Cleanup
- ✅ **Removed `/tests/pages/admin/` directory** - No separate admin structure needed
- ✅ **Moved all page objects to `/tests/pages/`** - Flat, clean structure
- ✅ **Renamed AdminLayoutPage to AppLayoutPage** - Tests existing layout + new features
- ✅ **Updated test imports and references** - All tests now use unified approach
- ✅ **Fixed test file references** - Updated 00-admin-layout.spec.ts to use AppLayoutPage

---

## 📋 Current Testing State

### Test Files Ready:
```
/tests/integration/admin-dashboard/
├── 00-admin-layout.spec.ts ✅ (Updated - tests AppLayout + new nav)
├── 01-dashboard-overview.spec.ts (Ready for enhanced dashboard)
├── 02-candidates-management.spec.ts (Ready for implementation)
├── 03-interviews-management.spec.ts (Ready for implementation)
├── 04-questions-management.spec.ts (Ready for implementation)
├── 05-jobs-management.spec.ts (Ready for implementation)
└── 06-reports-analytics.spec.ts (Ready for implementation)

/tests/pages/
├── AppLayoutPage.ts ✅ (Updated - tests existing layout + new features)
├── DashboardPage.ts (existing)
├── CandidatesPage.ts ✅ (moved from admin/, ready)
├── InterviewsPage.ts ✅ (moved from admin/, ready)
├── QuestionsPage.ts ✅ (moved from admin/, ready)
├── JobsPage.ts ✅ (moved from admin/, ready)
└── ReportsPage.ts ✅ (moved from admin/, ready)
```

### Test Approach:
- **Single Layout Testing**: All tests work with existing AppLayout.tsx
- **Route Testing**: Tests expect routes like `/candidates`, `/interviews` (no `/admin/` prefix)
- **Navigation Testing**: Tests verify new nav items added to existing sidebar
- **Unified Access**: Tests assume all users can access interview features

### Test Data Strategy
- **Real API Integration**: Tests will use actual backend endpoints
- **Test Database**: Isolated test database with predictable seed data
- **Mock Data Generation**: Consistent test data for each test suite
- **Cleanup Strategy**: Automatic cleanup after each test suite

---

## 📋 Implementation Order & Test Phases

### Phase 1: Foundation & Navigation (Week 1) - UNIFIED APPROACH
**Goal**: Extend existing AppLayout with new navigation items and create basic page structure

#### Tests to Update/Write First:
1. **Updated Layout Tests** (`00-admin-layout.spec.ts`)
   - ✅ Existing AppLayout navigation sidebar rendering
   - ✅ User authentication state
   - ✅ Responsive layout (desktop/mobile)
   - ✅ **UPDATED**: Tests now use AppLayoutPage.ts (not AdminLayoutPage.ts)
   - ✅ **UPDATED**: Tests moved from `/tests/pages/admin/` to `/tests/pages/`
   - **NEW**: Additional navigation items (Candidates, Interviews, Questions, Jobs, Reports)
   - **NEW**: Route transitions to new sections (e.g., `/candidates`, `/interviews`)
   - **NEW**: Navigation state management for new items

2. **Enhanced Dashboard Tests** (`01-dashboard-overview.spec.ts`)
   - **ENHANCED**: Existing dashboard with interview-specific statistics cards
   - **NEW**: Recent interview activity feed
   - **NEW**: Interview-focused quick actions panel
   - **NEW**: Interview analytics charts and visualizations

**API Endpoints Needed**:
```typescript
GET /api/v1/dashboard/stats        // Enhanced existing endpoint with interview metrics
GET /api/v1/dashboard/recent-activity  // Interview-focused activities
GET /api/v1/dashboard/charts       // Interview analytics charts
```

### Phase 2: Core Data Management (Week 2-3)
**Goal**: Implement CRUD operations for candidates and basic interview management

#### Tests to Write First:
3. **Candidates Management Tests** (`02-candidates-management.spec.ts`)
   - Candidate list view with pagination
   - Search and filtering functionality
   - Add/Edit candidate modal
   - Candidate detail view
   - Bulk operations
   - Interview history display

4. **Basic Interview Management Tests** (`03-interviews-management.spec.ts`)
   - Interview creation with pass key generation
   - Interview list with status filtering
   - Pass key display and copy functionality
   - Interview status updates

**API Endpoints Needed**:
```typescript
// Candidates
GET /api/v1/candidates
POST /api/v1/candidates
GET /api/v1/candidates/{id}
PUT /api/v1/candidates/{id}
DELETE /api/v1/candidates/{id}
GET /api/v1/candidates/{id}/interviews

// Interviews
GET /api/v1/interviews
POST /api/v1/interviews
GET /api/v1/interviews/{id}
PUT /api/v1/interviews/{id}
DELETE /api/v1/interviews/{id}
```

### Phase 3: Advanced Interview Features (Week 4)
**Goal**: Implement advanced interview monitoring and question management

#### Tests to Write First:
5. **Advanced Interview Tests** (extend `03-interviews-management.spec.ts`)
   - In-progress interview monitoring
   - Real-time status updates
   - Interview detail view with Q&A breakdown
   - Interview completion workflow

6. **Questions Management Tests** (`04-questions-management.spec.ts`)
   - Question bank CRUD operations
   - Category filtering and management
   - Question preview functionality
   - Bulk import/export operations

**API Endpoints Needed**:
```typescript
// Advanced Interviews
GET /api/v1/interviews/in-progress
GET /api/v1/interviews/{id}/questions
POST /api/v1/interviews/{id}/complete
POST /api/v1/interviews/start

// Questions
GET /api/v1/questions
POST /api/v1/questions
GET /api/v1/questions/{id}
PUT /api/v1/questions/{id}
DELETE /api/v1/questions/{id}
GET /api/v1/questions/categories
```

### Phase 4: Job Templates & Assignment (Week 5)
**Goal**: Implement job position management and question assignment

#### Tests to Write First:
7. **Jobs Management Tests** (`05-jobs-management.spec.ts`)
   - Job position CRUD operations
   - Question template builder
   - Drag-and-drop question assignment
   - Template preview and cloning
   - Usage statistics display

**API Endpoints Needed**:
```typescript
// Jobs
GET /api/v1/jobs
POST /api/v1/jobs
GET /api/v1/jobs/{id}
PUT /api/v1/jobs/{id}
DELETE /api/v1/jobs/{id}
GET /api/v1/jobs/{id}/template
POST /api/v1/jobs/{id}/clone
POST /api/v1/jobs/{job_id}/questions
PUT /api/v1/jobs/{job_id}/questions/order
```

### Phase 5: Reports & Analytics (Week 6)
**Goal**: Implement comprehensive reporting and analytics

#### Tests to Write First:
8. **Reports & Analytics Tests** (`06-reports-analytics.spec.ts`)
   - Report generation for individual interviews
   - Candidate summary reports
   - System analytics dashboard
   - Export functionality (PDF, Excel, CSV)
   - Interactive charts and visualizations

**API Endpoints Needed**:
```typescript
// Reports
GET /api/v1/reports/interviews/{id}
GET /api/v1/reports/candidates/{id}
GET /api/v1/reports/analytics
POST /api/v1/reports/generate
GET /api/v1/reports/export/{report_id}
```

---

## 🧪 Detailed Test Specifications

### Test Categories

#### 1. **Smoke Tests** (Regression Suite)
- Basic navigation works
- Authentication flow
- Critical user paths
- Data loading without errors

#### 2. **Functional Tests** (Full Suite)
- Complete CRUD operations
- Form validation
- Search and filtering
- Pagination
- Modal interactions
- Real-time updates

#### 3. **UI/UX Tests**
- Responsive design (mobile/desktop)
- Loading states
- Error handling
- Accessibility compliance
- Visual consistency

#### 4. **Integration Tests**
- API error handling
- Network failure scenarios
- Data consistency
- Cross-component interactions

---

## 📱 Device & Browser Coverage

### Desktop Testing
- **Chrome Desktop** (Primary)
- **Viewport**: 1920x1080, 1366x768
- **Features**: Full functionality testing

### Mobile Testing  
- **Chrome Mobile** (Pixel 5 simulation)
- **Viewport**: 393x851
- **Features**: Responsive design, touch interactions

---

## 🔧 Test Infrastructure

### Page Object Model Structure
```typescript
// Example: CandidatesPage.ts
export class CandidatesPage {
  constructor(private page: Page) {}
  
  // Locators
  get candidatesList() { return this.page.getByTestId('candidates-list'); }
  get addCandidateButton() { return this.page.getByTestId('add-candidate-btn'); }
  get searchInput() { return this.page.getByTestId('candidates-search'); }
  
  // Actions
  async navigateTo() { await this.page.goto('/admin/candidates'); }
  async addCandidate(data: CandidateData) { /* implementation */ }
  async searchCandidates(query: string) { /* implementation */ }
  
  // Assertions
  async expectCandidateInList(name: string) { /* implementation */ }
}
```

### Test Data Management
```typescript
// adminTestData.ts
export const testCandidates = {
  valid: {
    firstName: 'John',
    lastName: 'Doe', 
    email: 'john.doe@test.com',
    phone: '+1234567890'
  },
  // ... more test data
};

export const testInterviews = {
  pending: { /* data */ },
  inProgress: { /* data */ },
  completed: { /* data */ }
};
```

### API Test Helpers
```typescript
// apiHelpers.ts
export class AdminApiHelpers {
  static async createTestCandidate(data: CandidateData) { /* implementation */ }
  static async createTestInterview(candidateId: number, jobId: number) { /* implementation */ }
  static async cleanupTestData() { /* implementation */ }
}
```

---

## ⚡ Test Execution Strategy

### Development Workflow
1. **Write Tests First**: Create failing tests for new features
2. **Implement Minimal API**: Create API endpoints that return mock data
3. **Build UI Components**: Implement React components to pass tests
4. **Integrate Real Logic**: Replace mock data with real business logic
5. **Refine & Polish**: Optimize based on test feedback

### Test Commands
```bash
# Run all admin dashboard tests
npm run test:admin

# Run specific test suite
npm run test:admin -- --grep "candidates"

# Run regression tests only
npm run test:regression

# Run with UI (for debugging)
npm run test:admin:headed
```

### Continuous Integration
- **Pre-commit**: Run regression tests
- **PR Validation**: Run full test suite
- **Nightly**: Run extended test suite with performance metrics

---

## 📊 Success Metrics

### Test Coverage Goals
- **API Integration**: 100% endpoint coverage
- **UI Components**: 90% component coverage  
- **User Workflows**: 100% critical path coverage
- **Error Scenarios**: 80% error case coverage

### Performance Benchmarks
- **Page Load**: < 2 seconds
- **API Response**: < 500ms average
- **Search Results**: < 1 second
- **Report Generation**: < 5 seconds

### Quality Gates
- All tests must pass before deployment
- No accessibility violations (WCAG 2.1 AA)
- Mobile responsiveness verified
- Cross-browser compatibility confirmed

---

## 🚀 Next Steps

1. **Set up test infrastructure** (Page Objects, test data, API helpers)
2. **Create Phase 1 tests** (Admin layout and dashboard overview)
3. **Implement minimal backend APIs** for Phase 1
4. **Build basic React components** to pass Phase 1 tests
5. **Iterate through phases** following TDD approach

This testing strategy ensures we build a robust, well-tested admin dashboard with confidence in every feature before it reaches production.

---

## 📝 Detailed Test Case Examples

### Phase 1: Dashboard Overview Test Cases

#### Test File: `01-dashboard-overview.spec.ts`
```typescript
import { test, expect } from '@playwright/test';
import { DashboardPage } from '../pages/admin/DashboardPage';
import { AdminApiHelpers } from '../utils/apiHelpers';

test.describe('Admin Dashboard Overview', () => {
  let dashboardPage: DashboardPage;

  test.beforeEach(async ({ page }) => {
    dashboardPage = new DashboardPage(page);
    await AdminApiHelpers.setupTestData();
    await dashboardPage.navigateTo();
  });

  test.afterEach(async () => {
    await AdminApiHelpers.cleanupTestData();
  });

  test('should display system statistics cards', async () => {
    await expect(dashboardPage.totalCandidatesCard).toBeVisible();
    await expect(dashboardPage.activeInterviewsCard).toBeVisible();
    await expect(dashboardPage.completedInterviewsCard).toBeVisible();
    await expect(dashboardPage.averageScoreCard).toBeVisible();

    // Verify statistics show correct numbers
    await expect(dashboardPage.totalCandidatesCard).toContainText('25');
    await expect(dashboardPage.activeInterviewsCard).toContainText('3');
  });

  test('should display recent activity feed', async () => {
    await expect(dashboardPage.activityFeed).toBeVisible();
    await expect(dashboardPage.activityItems).toHaveCount(5);

    // Verify activity items have correct structure
    const firstActivity = dashboardPage.activityItems.first();
    await expect(firstActivity.locator('[data-testid="activity-type"]')).toBeVisible();
    await expect(firstActivity.locator('[data-testid="activity-description"]')).toBeVisible();
    await expect(firstActivity.locator('[data-testid="activity-timestamp"]')).toBeVisible();
  });

  test('should provide working quick actions', async () => {
    // Test Add Candidate quick action
    await dashboardPage.addCandidateQuickAction.click();
    await expect(dashboardPage.page.locator('[data-testid="add-candidate-modal"]')).toBeVisible();

    // Test Create Interview quick action
    await dashboardPage.page.keyboard.press('Escape'); // Close modal
    await dashboardPage.createInterviewQuickAction.click();
    await expect(dashboardPage.page.locator('[data-testid="create-interview-modal"]')).toBeVisible();
  });

  test('should display interactive charts', async () => {
    await expect(dashboardPage.interviewTrendsChart).toBeVisible();
    await expect(dashboardPage.riskDistributionChart).toBeVisible();
    await expect(dashboardPage.scoreHistogramChart).toBeVisible();

    // Verify charts have data
    await expect(dashboardPage.interviewTrendsChart.locator('canvas')).toBeVisible();
  });

  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 393, height: 851 });

    // Statistics cards should stack vertically
    const cardsContainer = dashboardPage.statisticsCards;
    await expect(cardsContainer).toHaveCSS('flex-direction', 'column');

    // Charts should be scrollable horizontally
    await expect(dashboardPage.chartsContainer).toHaveCSS('overflow-x', 'auto');
  });
});
```

### Phase 2: Candidates Management Test Cases

#### Test File: `02-candidates-management.spec.ts`
```typescript
import { test, expect } from '@playwright/test';
import { CandidatesPage } from '../pages/admin/CandidatesPage';
import { testCandidates } from '../utils/adminTestData';

test.describe('Candidates Management', () => {
  let candidatesPage: CandidatesPage;

  test.beforeEach(async ({ page }) => {
    candidatesPage = new CandidatesPage(page);
    await candidatesPage.navigateTo();
  });

  test('should display candidates list with pagination', async () => {
    await expect(candidatesPage.candidatesList).toBeVisible();
    await expect(candidatesPage.candidatesTable).toBeVisible();

    // Verify table headers
    await expect(candidatesPage.nameHeader).toContainText('Name');
    await expect(candidatesPage.emailHeader).toContainText('Email');
    await expect(candidatesPage.phoneHeader).toContainText('Phone');
    await expect(candidatesPage.interviewsHeader).toContainText('Interviews');

    // Verify pagination
    await expect(candidatesPage.paginationInfo).toBeVisible();
    await expect(candidatesPage.nextPageButton).toBeVisible();
  });

  test('should create new candidate successfully', async () => {
    await candidatesPage.addCandidateButton.click();
    await expect(candidatesPage.addCandidateModal).toBeVisible();

    // Fill form
    await candidatesPage.fillCandidateForm(testCandidates.valid);
    await candidatesPage.saveCandidateButton.click();

    // Verify success
    await expect(candidatesPage.successToast).toBeVisible();
    await expect(candidatesPage.addCandidateModal).not.toBeVisible();

    // Verify candidate appears in list
    await candidatesPage.expectCandidateInList(testCandidates.valid.firstName + ' ' + testCandidates.valid.lastName);
  });

  test('should validate candidate form fields', async () => {
    await candidatesPage.addCandidateButton.click();

    // Try to save empty form
    await candidatesPage.saveCandidateButton.click();

    // Verify validation errors
    await expect(candidatesPage.firstNameError).toContainText('First name is required');
    await expect(candidatesPage.lastNameError).toContainText('Last name is required');
    await expect(candidatesPage.emailError).toContainText('Email is required');

    // Test invalid email
    await candidatesPage.emailInput.fill('invalid-email');
    await candidatesPage.saveCandidateButton.click();
    await expect(candidatesPage.emailError).toContainText('Invalid email format');
  });

  test('should search and filter candidates', async () => {
    // Test search functionality
    await candidatesPage.searchInput.fill('John');
    await candidatesPage.searchButton.click();

    // Verify filtered results
    const visibleRows = candidatesPage.candidateRows;
    await expect(visibleRows).toHaveCount(2); // Assuming 2 Johns in test data

    // Test filter by interview status
    await candidatesPage.statusFilter.selectOption('completed');
    await expect(visibleRows).toHaveCount(1);

    // Clear filters
    await candidatesPage.clearFiltersButton.click();
    await expect(visibleRows.count()).toBeGreaterThan(5);
  });

  test('should edit existing candidate', async () => {
    // Click edit on first candidate
    await candidatesPage.candidateRows.first().locator('[data-testid="edit-candidate-btn"]').click();
    await expect(candidatesPage.editCandidateModal).toBeVisible();

    // Modify candidate data
    await candidatesPage.firstNameInput.fill('Updated Name');
    await candidatesPage.saveCandidateButton.click();

    // Verify update
    await expect(candidatesPage.successToast).toBeVisible();
    await candidatesPage.expectCandidateInList('Updated Name');
  });

  test('should delete candidate with confirmation', async () => {
    const initialCount = await candidatesPage.candidateRows.count();

    // Click delete on first candidate
    await candidatesPage.candidateRows.first().locator('[data-testid="delete-candidate-btn"]').click();
    await expect(candidatesPage.deleteConfirmationModal).toBeVisible();

    // Confirm deletion
    await candidatesPage.confirmDeleteButton.click();

    // Verify deletion
    await expect(candidatesPage.successToast).toBeVisible();
    await expect(candidatesPage.candidateRows).toHaveCount(initialCount - 1);
  });

  test('should display candidate detail view', async () => {
    // Click on first candidate name
    await candidatesPage.candidateRows.first().locator('[data-testid="candidate-name"]').click();

    // Verify detail view
    await expect(candidatesPage.candidateDetailView).toBeVisible();
    await expect(candidatesPage.candidateInfo).toBeVisible();
    await expect(candidatesPage.interviewHistoryTable).toBeVisible();

    // Verify quick actions
    await expect(candidatesPage.createInterviewButton).toBeVisible();
    await expect(candidatesPage.viewReportsButton).toBeVisible();
  });

  test('should handle bulk operations', async () => {
    // Select multiple candidates
    await candidatesPage.selectAllCheckbox.click();
    await expect(candidatesPage.bulkActionsBar).toBeVisible();

    // Test bulk export
    await candidatesPage.bulkExportButton.click();
    // Verify download initiated (implementation depends on how downloads are handled)

    // Test bulk delete
    await candidatesPage.bulkDeleteButton.click();
    await expect(candidatesPage.bulkDeleteConfirmationModal).toBeVisible();
  });
});
```

### Phase 3: Interview Management Test Cases

#### Test File: `03-interviews-management.spec.ts`
```typescript
import { test, expect } from '@playwright/test';
import { InterviewsPage } from '../pages/admin/InterviewsPage';
import { testInterviews } from '../utils/adminTestData';

test.describe('Interview Management', () => {
  let interviewsPage: InterviewsPage;

  test.beforeEach(async ({ page }) => {
    interviewsPage = new InterviewsPage(page);
    await interviewsPage.navigateTo();
  });

  test('should display interview status tabs', async () => {
    await expect(interviewsPage.allInterviewsTab).toBeVisible();
    await expect(interviewsPage.pendingTab).toBeVisible();
    await expect(interviewsPage.inProgressTab).toBeVisible();
    await expect(interviewsPage.completedTab).toBeVisible();
    await expect(interviewsPage.cancelledTab).toBeVisible();

    // Verify tab counts
    await expect(interviewsPage.pendingTab).toContainText('(5)'); // Assuming 5 pending
    await expect(interviewsPage.inProgressTab).toContainText('(2)'); // Assuming 2 in progress
  });

  test('should create new interview with pass key', async () => {
    await interviewsPage.createInterviewButton.click();
    await expect(interviewsPage.createInterviewModal).toBeVisible();

    // Fill interview form
    await interviewsPage.candidateSelect.click();
    await interviewsPage.candidateOption.first().click();

    await interviewsPage.jobSelect.click();
    await interviewsPage.jobOption.first().click();

    await interviewsPage.notesInput.fill('Test interview notes');

    // Create interview
    await interviewsPage.createInterviewButton.click();

    // Verify pass key generation
    await expect(interviewsPage.passKeyDisplay).toBeVisible();
    await expect(interviewsPage.passKeyValue).toHaveText(/^[A-Z0-9]{8,12}$/);

    // Test copy pass key functionality
    await interviewsPage.copyPassKeyButton.click();
    await expect(interviewsPage.copySuccessToast).toBeVisible();
  });

  test('should filter interviews by status', async () => {
    // Test pending filter
    await interviewsPage.pendingTab.click();
    const pendingRows = interviewsPage.interviewRows;
    await expect(pendingRows.first().locator('[data-testid="status-badge"]')).toContainText('Pending');

    // Test in-progress filter
    await interviewsPage.inProgressTab.click();
    const inProgressRows = interviewsPage.interviewRows;
    await expect(inProgressRows.first().locator('[data-testid="status-badge"]')).toContainText('In Progress');

    // Test completed filter
    await interviewsPage.completedTab.click();
    const completedRows = interviewsPage.interviewRows;
    await expect(completedRows.first().locator('[data-testid="status-badge"]')).toContainText('Completed');
  });

  test('should monitor in-progress interviews', async () => {
    await interviewsPage.inProgressTab.click();

    // Click on in-progress interview
    await interviewsPage.interviewRows.first().locator('[data-testid="monitor-btn"]').click();

    // Verify monitoring view
    await expect(interviewsPage.monitoringView).toBeVisible();
    await expect(interviewsPage.currentQuestionDisplay).toBeVisible();
    await expect(interviewsPage.progressIndicator).toBeVisible();
    await expect(interviewsPage.timeElapsed).toBeVisible();

    // Verify progress indicator shows correct values
    await expect(interviewsPage.progressText).toContainText('3 of 10 questions');
    await expect(interviewsPage.progressBar).toHaveAttribute('value', '30');
  });

  test('should display interview details', async () => {
    // Click on interview to view details
    await interviewsPage.interviewRows.first().locator('[data-testid="interview-title"]').click();

    // Verify detail view
    await expect(interviewsPage.interviewDetailView).toBeVisible();
    await expect(interviewsPage.candidateInfo).toBeVisible();
    await expect(interviewsPage.jobInfo).toBeVisible();
    await expect(interviewsPage.passKeyInfo).toBeVisible();
    await expect(interviewsPage.questionsBreakdown).toBeVisible();

    // Verify action buttons
    await expect(interviewsPage.generateReportButton).toBeVisible();
    await expect(interviewsPage.editInterviewButton).toBeVisible();
  });

  test('should handle interview cancellation', async () => {
    // Click cancel on pending interview
    await interviewsPage.pendingTab.click();
    await interviewsPage.interviewRows.first().locator('[data-testid="cancel-btn"]').click();

    // Verify confirmation modal
    await expect(interviewsPage.cancelConfirmationModal).toBeVisible();
    await expect(interviewsPage.cancelReasonInput).toBeVisible();

    // Provide cancellation reason
    await interviewsPage.cancelReasonInput.fill('Candidate withdrew application');
    await interviewsPage.confirmCancelButton.click();

    // Verify cancellation
    await expect(interviewsPage.successToast).toBeVisible();

    // Verify interview moved to cancelled tab
    await interviewsPage.cancelledTab.click();
    await expect(interviewsPage.interviewRows.first().locator('[data-testid="status-badge"]')).toContainText('Cancelled');
  });

  test('should validate pass key uniqueness', async () => {
    // Create multiple interviews and verify each has unique pass key
    const passKeys = new Set();

    for (let i = 0; i < 3; i++) {
      await interviewsPage.createInterviewButton.click();
      await interviewsPage.candidateSelect.click();
      await interviewsPage.candidateOption.nth(i).click();
      await interviewsPage.jobSelect.click();
      await interviewsPage.jobOption.first().click();
      await interviewsPage.createInterviewButton.click();

      const passKey = await interviewsPage.passKeyValue.textContent();
      expect(passKeys.has(passKey)).toBeFalsy();
      passKeys.add(passKey);

      await interviewsPage.closeModalButton.click();
    }
  });
});
```

---

## 🔧 Page Object Implementation Examples

### DashboardPage.ts
```typescript
import { Page, Locator } from '@playwright/test';

export class DashboardPage {
  readonly page: Page;

  // Statistics Cards
  readonly totalCandidatesCard: Locator;
  readonly activeInterviewsCard: Locator;
  readonly completedInterviewsCard: Locator;
  readonly averageScoreCard: Locator;
  readonly statisticsCards: Locator;

  // Activity Feed
  readonly activityFeed: Locator;
  readonly activityItems: Locator;

  // Quick Actions
  readonly addCandidateQuickAction: Locator;
  readonly createInterviewQuickAction: Locator;
  readonly createQuestionQuickAction: Locator;
  readonly generateReportQuickAction: Locator;

  // Charts
  readonly interviewTrendsChart: Locator;
  readonly riskDistributionChart: Locator;
  readonly scoreHistogramChart: Locator;
  readonly chartsContainer: Locator;

  constructor(page: Page) {
    this.page = page;

    // Initialize locators
    this.totalCandidatesCard = page.getByTestId('total-candidates-card');
    this.activeInterviewsCard = page.getByTestId('active-interviews-card');
    this.completedInterviewsCard = page.getByTestId('completed-interviews-card');
    this.averageScoreCard = page.getByTestId('average-score-card');
    this.statisticsCards = page.getByTestId('statistics-cards');

    this.activityFeed = page.getByTestId('activity-feed');
    this.activityItems = page.getByTestId('activity-item');

    this.addCandidateQuickAction = page.getByTestId('quick-add-candidate');
    this.createInterviewQuickAction = page.getByTestId('quick-create-interview');
    this.createQuestionQuickAction = page.getByTestId('quick-create-question');
    this.generateReportQuickAction = page.getByTestId('quick-generate-report');

    this.interviewTrendsChart = page.getByTestId('interview-trends-chart');
    this.riskDistributionChart = page.getByTestId('risk-distribution-chart');
    this.scoreHistogramChart = page.getByTestId('score-histogram-chart');
    this.chartsContainer = page.getByTestId('charts-container');
  }

  async navigateTo() {
    await this.page.goto('/dashboard');
    await this.page.waitForLoadState('networkidle');
  }

  async waitForStatisticsToLoad() {
    await this.totalCandidatesCard.waitFor({ state: 'visible' });
    await this.page.waitForFunction(() => {
      const card = document.querySelector('[data-testid="total-candidates-card"]');
      return card && card.textContent && !card.textContent.includes('Loading');
    });
  }

  async getStatisticValue(cardTestId: string): Promise<string> {
    const card = this.page.getByTestId(cardTestId);
    const valueElement = card.locator('[data-testid="stat-value"]');
    return await valueElement.textContent() || '0';
  }
}
```

### CandidatesPage.ts
```typescript
import { Page, Locator } from '@playwright/test';

export interface CandidateData {
  firstName: string;
  lastName: string;
  email: string;
  phone?: string;
}

export class CandidatesPage {
  readonly page: Page;

  // Main List View
  readonly candidatesList: Locator;
  readonly candidatesTable: Locator;
  readonly candidateRows: Locator;
  readonly addCandidateButton: Locator;

  // Table Headers
  readonly nameHeader: Locator;
  readonly emailHeader: Locator;
  readonly phoneHeader: Locator;
  readonly interviewsHeader: Locator;

  // Search and Filters
  readonly searchInput: Locator;
  readonly searchButton: Locator;
  readonly statusFilter: Locator;
  readonly clearFiltersButton: Locator;

  // Pagination
  readonly paginationInfo: Locator;
  readonly nextPageButton: Locator;
  readonly prevPageButton: Locator;

  // Add/Edit Modal
  readonly addCandidateModal: Locator;
  readonly editCandidateModal: Locator;
  readonly firstNameInput: Locator;
  readonly lastNameInput: Locator;
  readonly emailInput: Locator;
  readonly phoneInput: Locator;
  readonly saveCandidateButton: Locator;
  readonly cancelButton: Locator;

  // Validation Errors
  readonly firstNameError: Locator;
  readonly lastNameError: Locator;
  readonly emailError: Locator;

  // Detail View
  readonly candidateDetailView: Locator;
  readonly candidateInfo: Locator;
  readonly interviewHistoryTable: Locator;
  readonly createInterviewButton: Locator;
  readonly viewReportsButton: Locator;

  // Bulk Operations
  readonly selectAllCheckbox: Locator;
  readonly bulkActionsBar: Locator;
  readonly bulkExportButton: Locator;
  readonly bulkDeleteButton: Locator;
  readonly bulkDeleteConfirmationModal: Locator;

  // Delete Confirmation
  readonly deleteConfirmationModal: Locator;
  readonly confirmDeleteButton: Locator;

  // Toast Messages
  readonly successToast: Locator;
  readonly errorToast: Locator;

  constructor(page: Page) {
    this.page = page;

    // Initialize all locators
    this.candidatesList = page.getByTestId('candidates-list');
    this.candidatesTable = page.getByTestId('candidates-table');
    this.candidateRows = page.getByTestId('candidate-row');
    this.addCandidateButton = page.getByTestId('add-candidate-btn');

    this.nameHeader = page.getByTestId('name-header');
    this.emailHeader = page.getByTestId('email-header');
    this.phoneHeader = page.getByTestId('phone-header');
    this.interviewsHeader = page.getByTestId('interviews-header');

    this.searchInput = page.getByTestId('candidates-search');
    this.searchButton = page.getByTestId('search-btn');
    this.statusFilter = page.getByTestId('status-filter');
    this.clearFiltersButton = page.getByTestId('clear-filters-btn');

    this.paginationInfo = page.getByTestId('pagination-info');
    this.nextPageButton = page.getByTestId('next-page-btn');
    this.prevPageButton = page.getByTestId('prev-page-btn');

    this.addCandidateModal = page.getByTestId('add-candidate-modal');
    this.editCandidateModal = page.getByTestId('edit-candidate-modal');
    this.firstNameInput = page.getByTestId('first-name-input');
    this.lastNameInput = page.getByTestId('last-name-input');
    this.emailInput = page.getByTestId('email-input');
    this.phoneInput = page.getByTestId('phone-input');
    this.saveCandidateButton = page.getByTestId('save-candidate-btn');
    this.cancelButton = page.getByTestId('cancel-btn');

    this.firstNameError = page.getByTestId('first-name-error');
    this.lastNameError = page.getByTestId('last-name-error');
    this.emailError = page.getByTestId('email-error');

    this.candidateDetailView = page.getByTestId('candidate-detail-view');
    this.candidateInfo = page.getByTestId('candidate-info');
    this.interviewHistoryTable = page.getByTestId('interview-history-table');
    this.createInterviewButton = page.getByTestId('create-interview-btn');
    this.viewReportsButton = page.getByTestId('view-reports-btn');

    this.selectAllCheckbox = page.getByTestId('select-all-checkbox');
    this.bulkActionsBar = page.getByTestId('bulk-actions-bar');
    this.bulkExportButton = page.getByTestId('bulk-export-btn');
    this.bulkDeleteButton = page.getByTestId('bulk-delete-btn');
    this.bulkDeleteConfirmationModal = page.getByTestId('bulk-delete-confirmation-modal');

    this.deleteConfirmationModal = page.getByTestId('delete-confirmation-modal');
    this.confirmDeleteButton = page.getByTestId('confirm-delete-btn');

    this.successToast = page.getByTestId('success-toast');
    this.errorToast = page.getByTestId('error-toast');
  }

  async navigateTo() {
    await this.page.goto('/candidates');
    await this.page.waitForLoadState('networkidle');
  }

  async fillCandidateForm(data: CandidateData) {
    await this.firstNameInput.fill(data.firstName);
    await this.lastNameInput.fill(data.lastName);
    await this.emailInput.fill(data.email);
    if (data.phone) {
      await this.phoneInput.fill(data.phone);
    }
  }

  async expectCandidateInList(fullName: string) {
    const candidateRow = this.candidateRows.filter({ hasText: fullName });
    await candidateRow.waitFor({ state: 'visible' });
  }

  async getCandidateCount(): Promise<number> {
    return await this.candidateRows.count();
  }

  async searchCandidates(query: string) {
    await this.searchInput.fill(query);
    await this.searchButton.click();
    await this.page.waitForLoadState('networkidle');
  }
}
```

This comprehensive testing plan provides:

1. **Structured approach** with clear phases and priorities
2. **Detailed test cases** for each major feature
3. **Page Object Models** for maintainable test code
4. **Real API integration** strategy
5. **Mobile and desktop** coverage
6. **Test-driven development** workflow

The plan enables you to write tests first, then implement features incrementally while maintaining high confidence in the functionality.
