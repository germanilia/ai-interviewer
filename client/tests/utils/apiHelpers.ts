/**
 * API Helper utilities for admin dashboard tests
 * Provides functions to interact with backend APIs during testing
 */

import { APIRequestContext, request } from '@playwright/test';
import { 
  TestCandidate, 
  TestInterview, 
  TestQuestion, 
  TestJob, 
  TestUser,
  testCandidates,
  testJobs,
  testQuestions,
  testInterviews,
  testUsers
} from './adminTestData';

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

/**
 * Admin API Helper Class
 * Handles all API interactions for admin dashboard testing
 */
export class AdminApiHelpers {
  private static baseUrl = process.env.PLAYWRIGHT_API_BASE_URL || 'http://localhost:9001';
  private static apiContext: APIRequestContext;
  private static authToken: string | null = null;

  /**
   * Initialize API context
   */
  static async initialize() {
    this.apiContext = await request.newContext({
      baseURL: this.baseUrl,
      extraHTTPHeaders: {
        'Content-Type': 'application/json',
      }
    });
  }

  /**
   * Cleanup API context
   */
  static async cleanup() {
    if (this.apiContext) {
      await this.apiContext.dispose();
    }
  }

  /**
   * Authenticate as admin user
   */
  static async authenticateAsAdmin(): Promise<string> {
    const response = await this.apiContext.post('/api/v1/auth/signin', {
      data: {
        email: testUsers.admin.email,
        password: testUsers.admin.password
      }
    });

    if (!response.ok()) {
      throw new Error(`Authentication failed: ${response.status()}`);
    }

    const data = await response.json();
    this.authToken = data.access_token;
    
    // Set auth header for future requests
    await this.apiContext.dispose();
    this.apiContext = await request.newContext({
      baseURL: this.baseUrl,
      extraHTTPHeaders: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.authToken}`
      }
    });

    return this.authToken;
  }

  /**
   * Setup test data for dashboard tests
   */
  static async setupTestData(): Promise<void> {
    await this.initialize();
    await this.authenticateAsAdmin();

    // Create test jobs first (needed for interviews)
    const jobIds = await this.createTestJobs();
    
    // Create test candidates
    const candidateIds = await this.createTestCandidates();
    
    // Create test questions
    const questionIds = await this.createTestQuestions();
    
    // Create test interviews
    await this.createTestInterviews(candidateIds, jobIds);
    
    // Assign questions to jobs
    await this.assignQuestionsToJobs(jobIds, questionIds);
  }

  /**
   * Cleanup all test data
   */
  static async cleanupTestData(): Promise<void> {
    if (!this.apiContext) return;

    try {
      // Delete in reverse order of creation to handle dependencies
      await this.deleteTestInterviews();
      await this.deleteTestCandidates();
      await this.deleteTestQuestions();
      await this.deleteTestJobs();
    } catch (error) {
      console.warn('Error during test data cleanup:', error);
    }
  }

  // Candidate API Methods
  static async createCandidate(candidate: TestCandidate): Promise<number> {
    const response = await this.apiContext.post('/api/v1/candidates', {
      data: candidate
    });

    if (!response.ok()) {
      throw new Error(`Failed to create candidate: ${response.status()}`);
    }

    const data = await response.json();
    return data.id;
  }

  static async getCandidates(params?: {
    page?: number;
    pageSize?: number;
    search?: string;
    status?: string;
  }): Promise<PaginatedResponse<any>> {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set('page', params.page.toString());
    if (params?.pageSize) searchParams.set('page_size', params.pageSize.toString());
    if (params?.search) searchParams.set('search', params.search);
    if (params?.status) searchParams.set('status', params.status);

    const response = await this.apiContext.get(`/api/v1/candidates?${searchParams}`);
    
    if (!response.ok()) {
      throw new Error(`Failed to get candidates: ${response.status()}`);
    }

    return await response.json();
  }

  static async updateCandidate(id: number, candidate: Partial<TestCandidate>): Promise<void> {
    const response = await this.apiContext.put(`/api/v1/candidates/${id}`, {
      data: candidate
    });

    if (!response.ok()) {
      throw new Error(`Failed to update candidate: ${response.status()}`);
    }
  }

  static async deleteCandidate(id: number): Promise<void> {
    const response = await this.apiContext.delete(`/api/v1/candidates/${id}`);
    
    if (!response.ok()) {
      throw new Error(`Failed to delete candidate: ${response.status()}`);
    }
  }

  // Interview API Methods
  static async createInterview(interview: TestInterview): Promise<number> {
    const response = await this.apiContext.post('/api/v1/interviews', {
      data: interview
    });

    if (!response.ok()) {
      throw new Error(`Failed to create interview: ${response.status()}`);
    }

    const data = await response.json();
    return data.id;
  }

  static async getInterviews(params?: {
    status?: string;
    candidateId?: number;
    jobId?: number;
  }): Promise<any[]> {
    const searchParams = new URLSearchParams();
    if (params?.status) searchParams.set('status', params.status);
    if (params?.candidateId) searchParams.set('candidate_id', params.candidateId.toString());
    if (params?.jobId) searchParams.set('job_id', params.jobId.toString());

    const response = await this.apiContext.get(`/api/v1/interviews?${searchParams}`);
    
    if (!response.ok()) {
      throw new Error(`Failed to get interviews: ${response.status()}`);
    }

    return await response.json();
  }

  static async updateInterviewStatus(id: number, status: string): Promise<void> {
    const response = await this.apiContext.put(`/api/v1/interviews/${id}`, {
      data: { status }
    });

    if (!response.ok()) {
      throw new Error(`Failed to update interview status: ${response.status()}`);
    }
  }

  // Job API Methods
  static async createJob(job: TestJob): Promise<number> {
    const response = await this.apiContext.post('/api/v1/jobs', {
      data: { ...job, created_by_user_id: 1 } // Assuming admin user ID is 1
    });

    if (!response.ok()) {
      throw new Error(`Failed to create job: ${response.status()}`);
    }

    const data = await response.json();
    return data.id;
  }

  static async getJobs(): Promise<any[]> {
    const response = await this.apiContext.get('/api/v1/jobs');
    
    if (!response.ok()) {
      throw new Error(`Failed to get jobs: ${response.status()}`);
    }

    return await response.json();
  }

  // Question API Methods
  static async createQuestion(question: TestQuestion): Promise<number> {
    const response = await this.apiContext.post('/api/v1/questions', {
      data: { ...question, created_by_user_id: 1 } // Assuming admin user ID is 1
    });

    if (!response.ok()) {
      throw new Error(`Failed to create question: ${response.status()}`);
    }

    const data = await response.json();
    return data.id;
  }

  static async getQuestions(params?: {
    category?: string;
    importance?: string;
  }): Promise<any[]> {
    const searchParams = new URLSearchParams();
    if (params?.category) searchParams.set('category', params.category);
    if (params?.importance) searchParams.set('importance', params.importance);

    const response = await this.apiContext.get(`/api/v1/questions?${searchParams}`);
    
    if (!response.ok()) {
      throw new Error(`Failed to get questions: ${response.status()}`);
    }

    return await response.json();
  }

  // Dashboard API Methods
  static async getDashboardStats(): Promise<any> {
    const response = await this.apiContext.get('/api/v1/dashboard/stats');
    
    if (!response.ok()) {
      throw new Error(`Failed to get dashboard stats: ${response.status()}`);
    }

    return await response.json();
  }

  static async getRecentActivity(): Promise<any[]> {
    const response = await this.apiContext.get('/api/v1/dashboard/recent-activity');
    
    if (!response.ok()) {
      throw new Error(`Failed to get recent activity: ${response.status()}`);
    }

    return await response.json();
  }

  static async getChartData(): Promise<any> {
    const response = await this.apiContext.get('/api/v1/dashboard/charts');
    
    if (!response.ok()) {
      throw new Error(`Failed to get chart data: ${response.status()}`);
    }

    return await response.json();
  }

  // Private helper methods
  private static async createTestCandidates(): Promise<number[]> {
    const candidateIds: number[] = [];
    
    // Create individual test candidates
    candidateIds.push(await this.createCandidate(testCandidates.valid));
    candidateIds.push(await this.createCandidate(testCandidates.minimal));
    candidateIds.push(await this.createCandidate(testCandidates.withSpecialChars));
    
    // Create batch candidates
    for (const candidate of testCandidates.batch) {
      candidateIds.push(await this.createCandidate(candidate));
    }
    
    return candidateIds;
  }

  private static async createTestJobs(): Promise<number[]> {
    const jobIds: number[] = [];
    
    jobIds.push(await this.createJob(testJobs.softwareEngineer));
    jobIds.push(await this.createJob(testJobs.accountant));
    jobIds.push(await this.createJob(testJobs.salesManager));
    jobIds.push(await this.createJob(testJobs.hrSpecialist));
    
    for (const job of testJobs.batch) {
      jobIds.push(await this.createJob(job));
    }
    
    return jobIds;
  }

  private static async createTestQuestions(): Promise<number[]> {
    const questionIds: number[] = [];
    
    questionIds.push(await this.createQuestion(testQuestions.criminalBackground));
    questionIds.push(await this.createQuestion(testQuestions.drugUse));
    questionIds.push(await this.createQuestion(testQuestions.ethics));
    questionIds.push(await this.createQuestion(testQuestions.dismissals));
    questionIds.push(await this.createQuestion(testQuestions.trustworthiness));
    questionIds.push(await this.createQuestion(testQuestions.general));
    
    return questionIds;
  }

  private static async createTestInterviews(candidateIds: number[], jobIds: number[]): Promise<number[]> {
    const interviewIds: number[] = [];
    
    // Create interviews with different statuses
    const interviews = [
      { ...testInterviews.pending, candidateId: candidateIds[0], jobId: jobIds[0] },
      { ...testInterviews.inProgress, candidateId: candidateIds[1], jobId: jobIds[1] },
      { ...testInterviews.completed, candidateId: candidateIds[2], jobId: jobIds[2] },
      { ...testInterviews.cancelled, candidateId: candidateIds[3], jobId: jobIds[3] },
      { ...testInterviews.highRisk, candidateId: candidateIds[4], jobId: jobIds[0] }
    ];
    
    for (const interview of interviews) {
      interviewIds.push(await this.createInterview(interview));
    }
    
    return interviewIds;
  }

  private static async assignQuestionsToJobs(jobIds: number[], questionIds: number[]): Promise<void> {
    // Assign questions to jobs (implementation depends on API structure)
    for (const jobId of jobIds) {
      const response = await this.apiContext.post(`/api/v1/jobs/${jobId}/questions`, {
        data: {
          question_ids: questionIds.slice(0, 4), // Assign first 4 questions to each job
          order: questionIds.slice(0, 4).map((id, index) => ({ question_id: id, order_index: index }))
        }
      });
      
      if (!response.ok()) {
        console.warn(`Failed to assign questions to job ${jobId}: ${response.status()}`);
      }
    }
  }

  private static async deleteTestCandidates(): Promise<void> {
    const candidates = await this.getCandidates();
    for (const candidate of candidates.items) {
      if (candidate.email.includes('@test.com')) {
        await this.deleteCandidate(candidate.id);
      }
    }
  }

  private static async deleteTestJobs(): Promise<void> {
    const jobs = await this.getJobs();
    for (const job of jobs) {
      if (job.title.includes('Test') || Object.values(testJobs).some(testJob => testJob.title === job.title)) {
        try {
          const response = await this.apiContext.delete(`/api/v1/jobs/${job.id}`);
          if (!response.ok()) {
            console.warn(`Failed to delete job ${job.id}: ${response.status()}`);
          }
        } catch (error) {
          console.warn(`Error deleting job ${job.id}:`, error);
        }
      }
    }
  }

  private static async deleteTestQuestions(): Promise<void> {
    const questions = await this.getQuestions();
    for (const question of questions) {
      if (Object.values(testQuestions).some(testQuestion => testQuestion.title === question.title)) {
        try {
          const response = await this.apiContext.delete(`/api/v1/questions/${question.id}`);
          if (!response.ok()) {
            console.warn(`Failed to delete question ${question.id}: ${response.status()}`);
          }
        } catch (error) {
          console.warn(`Error deleting question ${question.id}:`, error);
        }
      }
    }
  }

  private static async deleteTestInterviews(): Promise<void> {
    const interviews = await this.getInterviews();
    for (const interview of interviews) {
      if (interview.pass_key && interview.pass_key.startsWith('TEST')) {
        try {
          const response = await this.apiContext.delete(`/api/v1/interviews/${interview.id}`);
          if (!response.ok()) {
            console.warn(`Failed to delete interview ${interview.id}: ${response.status()}`);
          }
        } catch (error) {
          console.warn(`Error deleting interview ${interview.id}:`, error);
        }
      }
    }
  }
}
