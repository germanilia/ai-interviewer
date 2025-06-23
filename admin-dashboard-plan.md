# Interview Management Dashboard Implementation Plan
## AI-Powered Integrity Interview System

### Overview
This document outlines the implementation plan for enhancing the existing dashboard with interview management capabilities. The enhanced dashboard will be accessible to all users, with some features having role-based access controls. We will extend the existing layout and navigation components rather than creating separate interfaces.

---

## 🏗️ Implementation Approach

### Unified Dashboard Architecture
- **Single Dashboard**: One unified dashboard enhanced with interview management features
- **Extend Existing Components**: Enhance current AppLayout, Sidebar, and navigation components
- **Universal Access**: All users can access interview management features
- **Role-Based Features**: Specific features like user management remain admin-only
- **Consistent UX**: Maintain the same look and feel as the existing application

### Enhanced Navigation Structure
```
📊 Dashboard (Enhanced with Interview Overview) - ENHANCED existing dashboard
👥 Candidates (Candidate Management) - NEW
🎯 Interviews (Interview Management & Monitoring) - NEW
📋 Questions (Question Bank & Job Assignment) - NEW
💼 Jobs (Position Templates) - NEW
📈 Reports (Interview Reports & Analytics) - NEW
👤 Users (User Management) - Keep existing (admin-only)
⚙️ Settings (Keep existing)
```

### Completed Cleanup & Structure Fixes
- ✅ **Removed unused pages**: Documents, Data Library, Help, Analytics
- ✅ **Cleaned up test structure**: Moved from `/tests/pages/admin/` to `/tests/pages/`
- ✅ **Unified approach**: No separate admin layout - one enhanced dashboard
- ✅ **Updated test files**: AppLayoutPage.ts tests existing layout + new features
- ✅ **Simplified navigation**: Updated Sidebar.tsx and MobileNav.tsx to remove unused items

---

## 📋 Current State Summary

### What We Have Now (Clean Foundation):
```
📊 Dashboard (existing, ready to enhance)
👤 Users (existing, admin-only)
⚙️ Settings (existing)
```

### What We're Adding (Interview Management):
```
👥 Candidates (new navigation + page)
🎯 Interviews (new navigation + page)
📋 Questions (new navigation + page)
💼 Jobs (new navigation + page)
📈 Reports (new navigation + page)
```

### File Structure:
```
/src/components/layout/
├── AppLayout.tsx (existing - will be enhanced)
├── Sidebar.tsx (existing - will get new nav items)
├── MobileNav.tsx (existing - will get new nav items)
└── Header.tsx (existing)

/src/components/pages/
├── Dashboard.tsx (existing - will be enhanced)
├── Settings.tsx (existing)
├── Candidates.tsx (new)
├── Interviews.tsx (new)
├── Questions.tsx (new)
├── Jobs.tsx (new)
└── Reports.tsx (new)

/tests/pages/
├── AppLayoutPage.ts (updated - tests layout + new nav)
├── DashboardPage.ts (existing)
├── CandidatesPage.ts (moved from admin/)
├── InterviewsPage.ts (moved from admin/)
├── QuestionsPage.ts (moved from admin/)
├── JobsPage.ts (moved from admin/)
└── ReportsPage.ts (moved from admin/)
```

---

## 📊 1. Dashboard (System Overview)

### Purpose
High-level system overview with key metrics and quick actions for admins.

### Key Features
- **System Statistics Cards**
  - Total candidates in system
  - Active interviews (in-progress)
  - Completed interviews this month
  - Pending interviews awaiting scheduling
  - Average integrity score
  - High-risk candidates flagged

- **Recent Activity Feed**
  - Recently completed interviews
  - New candidates added
  - Interviews created (pending start)
  - System alerts and notifications

- **Quick Actions Panel**
  - Add new candidate
  - Create new interview (with pass key)
  - Create new question
  - Generate report

- **Charts & Visualizations**
  - Interview completion trends (last 30 days)
  - Risk level distribution pie chart
  - Integrity score distribution histogram

### Data Requirements
- Interview statistics (count by status)
- Candidate statistics
- Recent activity logs
- Aggregate scoring data

### API Endpoints Needed
- `GET /api/v1/dashboard/stats` - System statistics
- `GET /api/v1/dashboard/recent-activity` - Recent activity feed
- `GET /api/v1/dashboard/charts` - Chart data

---

## 👥 2. Candidates Page

### Purpose
Comprehensive candidate management with full CRUD operations and interview history.

### Key Features
- **Candidate List View**
  - Searchable/filterable table
  - Columns: Name, Email, Phone, Total Interviews, Last Interview Date, Status
  - Bulk actions (delete, export)
  - Pagination with configurable page size

- **Add/Edit Candidate Modal**
  - Form fields: First Name, Last Name, Email, Phone
  - Email validation and duplicate checking
  - Save and continue to create interview option

- **Candidate Detail View**
  - Personal information display/edit
  - Complete interview history table
  - Interview results summary
  - Quick actions (Create Interview, View Reports)

- **Advanced Filtering**
  - Filter by interview status
  - Filter by date range
  - Filter by risk level
  - Search by name/email

### Data Requirements
- Candidate CRUD operations
- Interview history per candidate
- Search and filtering capabilities

### API Endpoints Needed
- `GET /api/v1/candidates` - List candidates with pagination/filtering
- `POST /api/v1/candidates` - Create new candidate
- `GET /api/v1/candidates/{id}` - Get candidate details
- `PUT /api/v1/candidates/{id}` - Update candidate
- `DELETE /api/v1/candidates/{id}` - Delete candidate
- `GET /api/v1/candidates/{id}/interviews` - Get candidate's interview history

### Components to Create
- `CandidateList.tsx` - Main list component
- `CandidateForm.tsx` - Add/edit form modal
- `CandidateDetail.tsx` - Detailed view component
- `CandidateFilters.tsx` - Advanced filtering component

---

## 🎯 3. Interviews Page

### Purpose
Central hub for managing all interviews with real-time monitoring of in-progress sessions.

### Key Features
- **Interview Status Tabs**
  - All Interviews
  - Pending (created, awaiting candidate to start)
  - In Progress (live monitoring)
  - Completed
  - Cancelled

- **Interview List View**
  - Columns: Candidate Name, Job Position, Status, Interview Date, Pass Key, Score, Risk Level
  - Status-based color coding
  - Quick actions per row (View, Edit, Cancel, Generate Report)

- **Create Interview Modal**
  - Select candidate (searchable dropdown)
  - Select job position (determines question template)
  - Generate unique pass key for candidate access
  - Add notes/instructions

- **In-Progress Monitoring**
  - Real-time view of active interviews
  - Current question being asked
  - Progress indicator (questions completed/total)
  - Time elapsed
  - Ability to intervene or add notes

- **Interview Detail View**
  - Complete interview information
  - Question-by-question breakdown
  - AI analysis results
  - Generate/download report

### Data Requirements
- Interview CRUD operations
- Real-time interview status updates
- Question templates by job
- Interview results and analysis

### API Endpoints Needed
- `GET /api/v1/interviews` - List interviews with filtering
- `POST /api/v1/interviews` - Create new interview with pass key
- `GET /api/v1/interviews/{id}` - Get interview details
- `PUT /api/v1/interviews/{id}` - Update interview
- `DELETE /api/v1/interviews/{id}` - Cancel interview
- `GET /api/v1/interviews/in-progress` - Get active interviews
- `GET /api/v1/interviews/{id}/questions` - Get interview questions
- `POST /api/v1/interviews/{id}/complete` - Complete interview
- `POST /api/v1/interviews/start` - Start interview using pass key (candidate endpoint)

### Components to Create
- `InterviewList.tsx` - Main list with tabs
- `CreateInterviewModal.tsx` - Interview creation form with pass key generation
- `InterviewDetail.tsx` - Detailed interview view
- `InProgressMonitor.tsx` - Real-time monitoring component
- `InterviewStatusBadge.tsx` - Status indicator component
- `PassKeyDisplay.tsx` - Component to display and copy pass key

---

## 📋 4. Questions Page

### Purpose
Manage the question bank and assign questions to job positions.

### Key Features
- **Question Bank Management**
  - List all questions with categories
  - CRUD operations for questions
  - Bulk import/export functionality
  - Question preview and testing

- **Question Categories**
  - Criminal Background
  - Drug Use
  - Ethics
  - Dismissals
  - Trustworthiness
  - General

- **Question Form**
  - Title and question text
  - Instructions for interviewer
  - Importance level (Optional, Ask Once, Mandatory)
  - Category selection
  - Preview functionality

- **Job Assignment Interface**
  - Drag-and-drop question assignment
  - Question ordering within job templates
  - Bulk assignment tools
  - Template preview

### Data Requirements
- Question CRUD operations
- Category management
- Job-question relationships
- Question ordering

### API Endpoints Needed
- `GET /api/v1/questions` - List questions with filtering
- `POST /api/v1/questions` - Create new question
- `GET /api/v1/questions/{id}` - Get question details
- `PUT /api/v1/questions/{id}` - Update question
- `DELETE /api/v1/questions/{id}` - Delete question
- `GET /api/v1/questions/categories` - Get question categories
- `POST /api/v1/jobs/{job_id}/questions` - Assign questions to job
- `PUT /api/v1/jobs/{job_id}/questions/order` - Update question order

### Components to Create
- `QuestionBank.tsx` - Main question management
- `QuestionForm.tsx` - Add/edit question form
- `QuestionAssignment.tsx` - Job assignment interface
- `CategoryFilter.tsx` - Category filtering component
- `QuestionPreview.tsx` - Question preview modal

---

## 💼 5. Jobs Page

### Purpose
Manage job positions and their associated interview question templates.

### Key Features
- **Job Position Management**
  - List all job positions
  - CRUD operations for jobs
  - Department organization
  - Template usage statistics

- **Job Template Builder**
  - Assign questions to job positions
  - Set question order and importance
  - Preview complete interview template
  - Clone templates between jobs

- **Template Statistics**
  - Number of interviews conducted
  - Average completion time
  - Success/failure rates
  - Template usage analytics

### Data Requirements
- Job CRUD operations
- Job-question template relationships
- Interview statistics per job
- Template usage analytics

### API Endpoints Needed
- `GET /api/v1/jobs` - List job positions
- `POST /api/v1/jobs` - Create new job
- `GET /api/v1/jobs/{id}` - Get job details with questions
- `PUT /api/v1/jobs/{id}` - Update job
- `DELETE /api/v1/jobs/{id}` - Delete job
- `GET /api/v1/jobs/{id}/template` - Get question template
- `POST /api/v1/jobs/{id}/clone` - Clone job template

### Components to Create
- `JobList.tsx` - Job positions list
- `JobForm.tsx` - Add/edit job form
- `TemplateBuilder.tsx` - Question template builder
- `JobStatistics.tsx` - Usage statistics component
- `TemplatePreview.tsx` - Template preview modal

---

## 📈 6. Reports Page

### Purpose
Generate comprehensive reports and analytics for interview insights.

### Key Features
- **Report Types**
  - Individual interview reports (generated immediately after completion)
  - Candidate summary reports
  - Job position analytics
  - System-wide trends
  - Risk assessment summaries

- **Report Generation**
  - Immediate report generation after interview completion
  - Customizable date ranges for historical reports
  - Multiple export formats (PDF, Excel, CSV)
  - Report templates

- **Analytics Dashboard**
  - Interview completion trends
  - Integrity score distributions
  - Risk level analytics
  - Template usage statistics
  - System performance metrics

- **Data Visualization**
  - Interactive charts and graphs
  - Drill-down capabilities
  - Comparative analysis tools
  - Trend identification

### Data Requirements
- Interview results aggregation
- Statistical analysis capabilities
- Report generation engine
- Export functionality

### API Endpoints Needed
- `GET /api/v1/reports/interviews/{id}` - Individual interview report
- `GET /api/v1/reports/candidates/{id}` - Candidate summary report
- `GET /api/v1/reports/analytics` - System analytics data
- `POST /api/v1/reports/generate` - Generate custom report
- `GET /api/v1/reports/export/{report_id}` - Export report

### Components to Create
- `ReportsDashboard.tsx` - Main reports interface
- `ReportGenerator.tsx` - Custom report builder
- `AnalyticsCharts.tsx` - Data visualization components
- `ReportExport.tsx` - Export functionality
- `ReportPreview.tsx` - Report preview modal

---

## 🔑 Pass Key System

### Purpose
When an admin creates an interview, a unique pass key is generated that the candidate uses to access and start their interview session.

### Key Features
- **Unique Pass Key Generation**
  - Auto-generated 8-12 character alphanumeric code
  - Case-insensitive for user convenience
  - Unique per interview
  - Cannot be reused

- **Pass Key Display**
  - Prominently displayed in interview creation confirmation
  - Copy-to-clipboard functionality
  - Admin can view pass key in interview details
  - Pass key shown in interview list for easy reference

- **Candidate Access**
  - Candidate enters pass key to start interview
  - Pass key validates and loads correct interview
  - Single-use authentication (interview can only be started once)
  - Pass key expires after interview completion

### Implementation Requirements
- Add `pass_key` field to Interview model
- Generate unique pass key on interview creation
- Validate pass key for candidate interview access
- Update all schemas and API endpoints
- Add pass key to database population script
- Update tests to include pass key functionality

---

## 🔧 Technical Implementation Notes

### Layout & Navigation
- **Extend Existing Components**: Update Sidebar.tsx and MobileNav.tsx with new navigation items
- **Reuse AppLayout**: No need for separate AdminLayout component
- **Route Structure**: Add new routes to App.tsx using existing AppLayout wrapper
- **Consistent Styling**: Follow existing design patterns and component structure

### State Management
- Use React Context for global state (user, theme) - existing
- Local state for component-specific data
- Consider React Query for server state management

### UI Components
- Leverage existing shadcn/ui components
- Create reusable components for common patterns
- Implement responsive design for mobile/tablet
- Follow existing component structure in `/src/components/pages/`

### Data Fetching
- Implement proper loading states
- Error handling and retry mechanisms
- Optimistic updates where appropriate

### Real-time Features
- WebSocket connection for in-progress interview monitoring
- Server-sent events for notifications
- Polling fallback for real-time updates

### Testing Strategy
- Unit tests for all components
- Integration tests for critical workflows
- E2E tests with Playwright using existing layout structure
- Update existing AdminLayoutPage.ts to work with extended navigation

---

## 📋 Implementation Priority

### Phase 1 (Foundation & Navigation) - CURRENT
1. ✅ **Cleanup existing unused pages** (Documents, DataLibrary, Analytics, Help)
2. ✅ **Fix test structure** (Moved from `/tests/pages/admin/` to `/tests/pages/`)
3. ✅ **Unified dashboard approach** (No separate admin layout)
4. **Update navigation** - Add new menu items to existing Sidebar.tsx and MobileNav.tsx
5. **Add new routes** - Extend App.tsx with new page routes using existing AppLayout
6. **Create page components** - Basic page structure for each new section in `/src/components/pages/`
7. **Verify tests** - Run updated AppLayoutPage.ts tests with new navigation

### Phase 2 (Enhanced Dashboard)
8. **Enhance existing Dashboard.tsx** with interview-specific statistics and overview
9. Add pass key to Interview model and schemas
10. Create basic API endpoints for dashboard statistics

### Phase 3 (Core Functionality)
11. Candidates management (CRUD operations)
12. Basic interview creation with pass key generation
13. Interview list and status management

### Phase 4 (Advanced Interview Management)
14. Interview monitoring and real-time status updates
15. Questions management and categorization
16. Job templates and question assignment

### Phase 5 (Reports & Analytics)
17. Reports generation and export functionality
18. Advanced analytics and visualizations
19. Real-time monitoring enhancements

### Phase 6 (Polish & Optimization)
20. Performance optimization
21. Advanced filtering and search
22. Bulk operations
23. Export functionality
