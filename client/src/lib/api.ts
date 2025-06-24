// API service for making requests to the backend
import config from './config';

// Get API URL from configuration
const API_URL = config.apiUrl;

// Types for authentication
export interface SignUpRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface SignUpResponse {
  message: string;
  user_sub: string;
  user_confirmed: boolean;
}

export interface ConfirmSignUpRequest {
  email: string;
  confirmation_code: string;
}

export interface SignInRequest {
  email: string;
  password: string;
}

export interface UserInfo {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  role: string;
  is_active: boolean;
  user_sub?: string;
}

export interface SignInResponse {
  access_token: string;
  id_token: string;
  refresh_token?: string;
  expires_in: number;
  token_type: string;
  user: UserInfo;
}

export interface RefreshTokenRequest {
  refresh_token: string;
  email: string;
}

export interface RefreshTokenResponse {
  access_token: string;
  id_token: string;
  expires_in: number;
  token_type: string;
}

// Types for candidates
export interface CandidateData {
  firstName: string;
  lastName: string;
  email: string;
  phone?: string;
}

export interface CandidateResponse {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  created_at: string;
  updated_at: string;
  full_name?: string;
  interview_count?: number;
  last_interview_date?: string;
  status?: string;
}

// Types for interviews
export interface InterviewCreateRequest {
  candidate_id: number;
  job_id: number;
  notes?: string;
  interview_date?: string;
}

export interface InterviewUpdateRequest {
  status?: string;
  notes?: string;
  interview_date?: string;
}

export interface InterviewResponse {
  id: number;
  candidate_id: number;
  job_id: number;
  status: string;
  interview_date?: string;
  pass_key: string;
  score?: number;
  integrity_score?: string;
  risk_level?: string;
  conversation?: any;
  report_summary?: string;
  risk_indicators?: any[];
  key_concerns?: any[];
  analysis_notes?: string;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  // Backend returns these fields directly for InterviewWithDetails
  candidate_name?: string;
  candidate_email?: string;
  job_title?: string;
  job_department?: string;
  // Legacy nested objects for backward compatibility
  candidate?: {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
    full_name: string;
  };
  job?: {
    id: number;
    title: string;
    department?: string;
  };
}

export interface InterviewListResponse {
  items: InterviewResponse[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  status_counts?: { [key: string]: number };
}

export interface JobResponse {
  id: number;
  title: string;
  department?: string;
  description?: string;
  requirements?: string;
  created_at: string;
  updated_at: string;
}

export interface CandidateListResponse {
  items: CandidateResponse[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface CandidateCreateRequest {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
}

export interface CandidateUpdateRequest {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
}

// Question types to match backend schemas
export interface QuestionResponse {
  id: number;
  title: string;
  question_text: string;
  instructions?: string;
  importance: 'optional' | 'ask_once' | 'mandatory';
  category: 'criminal_background' | 'drug_use' | 'ethics' | 'dismissals' | 'trustworthiness' | 'general';
  created_by_user_id: number;
  created_by_name?: string;
  created_at: string;
  updated_at: string;
}

export interface QuestionCreate {
  title: string;
  question_text: string;
  instructions?: string;
  importance: 'optional' | 'ask_once' | 'mandatory';
  category: 'criminal_background' | 'drug_use' | 'ethics' | 'dismissals' | 'trustworthiness' | 'general';
  created_by_user_id: number;
}

export interface QuestionUpdate {
  title?: string;
  question_text?: string;
  instructions?: string;
  importance?: 'optional' | 'ask_once' | 'mandatory';
  category?: 'criminal_background' | 'drug_use' | 'ethics' | 'dismissals' | 'trustworthiness' | 'general';
}

export interface QuestionListResponse {
  questions: QuestionResponse[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface QuestionFilter {
  category?: 'criminal_background' | 'drug_use' | 'ethics' | 'dismissals' | 'trustworthiness' | 'general';
  importance?: 'optional' | 'ask_once' | 'mandatory';
  search?: string;
  created_by_user_id?: number;
}

export interface BulkQuestionDelete {
  question_ids: number[];
}

export interface BulkQuestionCategoryUpdate {
  question_ids: number[];
  new_category: 'criminal_background' | 'drug_use' | 'ethics' | 'dismissals' | 'trustworthiness' | 'general';
}

export interface JobQuestionAssignment {
  question_id: number;
  job_id: number;
  order_index?: number;
}

/**
 * Get stored auth token
 */
function getAuthToken(): string | null {
  return localStorage.getItem('access_token');
}

/**
 * Store auth tokens
 */
function storeAuthTokens(tokens: {
  access_token: string;
  id_token: string;
  refresh_token?: string;
  expires_in: number;
}) {
  localStorage.setItem('access_token', tokens.access_token);
  localStorage.setItem('id_token', tokens.id_token);
  if (tokens.refresh_token) {
    localStorage.setItem('refresh_token', tokens.refresh_token);
  }
  // Store expiration time
  const expiresAt = Date.now() + (tokens.expires_in * 1000);
  localStorage.setItem('token_expires_at', expiresAt.toString());
}

/**
 * Clear stored auth tokens
 */
function clearAuthTokens() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('id_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('token_expires_at');
  localStorage.removeItem('user_info');
}

/**
 * Check if token is expired
 */
function isTokenExpired(): boolean {
  const expiresAt = localStorage.getItem('token_expires_at');
  if (!expiresAt) return true;
  return Date.now() > parseInt(expiresAt);
}

/**
 * Fetch data from the API with error handling and auth
 */
async function fetchFromApi(endpoint: string, options: RequestInit = {}) {
  try {
    const token = getAuthToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {}),
    };

    if (token && !isTokenExpired()) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      if (response.status === 401) {
        // Token expired or invalid, clear tokens
        clearAuthTokens();
        throw new Error('Authentication required');
      }

      // Try to get error message from response body
      let errorMessage = `Request failed with status ${response.status}`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = errorData.detail;
        } else if (errorData.message) {
          errorMessage = errorData.message;
        }
      } catch (parseError) {
        // If we can't parse the error response, use the default message
        console.warn('Could not parse error response:', parseError);
      }

      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

// API endpoints
export const api = {
  // Health check
  getHealth: () => fetchFromApi('/health'),

  // User endpoints
  getUsers: () => fetchFromApi('/api/v1/users/'),
  getUser: (id: number) => fetchFromApi(`/api/v1/users/${id}`),

  // Authentication endpoints
  auth: {
    signUp: async (data: SignUpRequest): Promise<SignUpResponse> => {
      return fetchFromApi('/api/v1/auth/signup', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },

    confirmSignUp: async (data: ConfirmSignUpRequest): Promise<{ message: string }> => {
      return fetchFromApi('/api/v1/auth/confirm-signup', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },

    signIn: async (data: SignInRequest): Promise<SignInResponse> => {
      const response = await fetchFromApi('/api/v1/auth/signin', {
        method: 'POST',
        body: JSON.stringify(data),
      });

      // Store tokens and user info
      storeAuthTokens(response);
      localStorage.setItem('user_info', JSON.stringify(response.user));

      return response;
    },

    refreshToken: async (data: RefreshTokenRequest): Promise<RefreshTokenResponse> => {
      const response = await fetchFromApi('/api/v1/auth/refresh-token', {
        method: 'POST',
        body: JSON.stringify(data),
      });

      // Update stored tokens
      storeAuthTokens(response);

      return response;
    },

    getCurrentUser: async (): Promise<UserInfo> => {
      return fetchFromApi('/api/v1/auth/me');
    },

    signOut: async (): Promise<{ message: string }> => {
      const response = await fetchFromApi('/api/v1/auth/signout', {
        method: 'POST',
      });

      // Clear stored tokens
      clearAuthTokens();

      return response;
    },

    // Helper functions
    isAuthenticated: (): boolean => {
      const token = getAuthToken();
      return token !== null && !isTokenExpired();
    },

    getStoredUser: (): UserInfo | null => {
      const userInfo = localStorage.getItem('user_info');
      if (!userInfo) return null;

      try {
        return JSON.parse(userInfo);
      } catch (error) {
        // If JSON is invalid, clear it and return null
        localStorage.removeItem('user_info');
        return null;
      }
    },

    clearTokens: clearAuthTokens,
  },

  // Candidate endpoints
  candidates: {
    getAll: async (params?: {
      page?: number;
      page_size?: number;
      search?: string;
      status?: string;
    }): Promise<CandidateListResponse> => {
      const searchParams = new URLSearchParams();
      if (params?.page) searchParams.set('page', params.page.toString());
      if (params?.page_size) searchParams.set('page_size', params.page_size.toString());
      if (params?.search) searchParams.set('search', params.search);
      if (params?.status) searchParams.set('status', params.status);

      const endpoint = `/api/v1/candidates${searchParams.toString() ? `?${searchParams}` : ''}`;
      return fetchFromApi(endpoint);
    },

    getById: async (id: number): Promise<CandidateResponse> => {
      return fetchFromApi(`/api/v1/candidates/${id}`);
    },

    create: async (data: CandidateCreateRequest): Promise<CandidateResponse> => {
      return fetchFromApi('/api/v1/candidates', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },

    update: async (id: number, data: CandidateUpdateRequest): Promise<CandidateResponse> => {
      return fetchFromApi(`/api/v1/candidates/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    },

    delete: async (id: number): Promise<void> => {
      return fetchFromApi(`/api/v1/candidates/${id}`, {
        method: 'DELETE',
      });
    },

    getInterviews: async (id: number): Promise<any> => {
      return fetchFromApi(`/api/v1/candidates/${id}/interviews`);
    },
  },

  // Interview endpoints
  interviews: {
    getAll: async (params?: {
      page?: number;
      page_size?: number;
      status?: string;
      search?: string;
      candidate_id?: number;
      job_id?: number;
    }): Promise<InterviewListResponse> => {
      const searchParams = new URLSearchParams();
      if (params?.page) searchParams.set('page', params.page.toString());
      if (params?.page_size) searchParams.set('page_size', params.page_size.toString());
      if (params?.status) searchParams.set('status', params.status);
      if (params?.search) searchParams.set('search', params.search);
      if (params?.candidate_id) searchParams.set('candidate_id', params.candidate_id.toString());
      if (params?.job_id) searchParams.set('job_id', params.job_id.toString());

      const endpoint = `/api/v1/interviews${searchParams.toString() ? `?${searchParams}` : ''}`;
      return fetchFromApi(endpoint);
    },

    getById: async (id: number): Promise<InterviewResponse> => {
      return fetchFromApi(`/api/v1/interviews/${id}`);
    },

    create: async (data: InterviewCreateRequest): Promise<InterviewResponse> => {
      return fetchFromApi('/api/v1/interviews', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },

    update: async (id: number, data: InterviewUpdateRequest): Promise<InterviewResponse> => {
      return fetchFromApi(`/api/v1/interviews/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    },

    delete: async (id: number): Promise<void> => {
      return fetchFromApi(`/api/v1/interviews/${id}`, {
        method: 'DELETE',
      });
    },

    changeStatus: async (id: number, status: string, reason?: string): Promise<InterviewResponse> => {
      return fetchFromApi(`/api/v1/interviews/${id}/status`, {
        method: 'PATCH',
        body: JSON.stringify({ new_status: status, reason }),
      });
    },

    cancel: async (id: number, reason: string): Promise<InterviewResponse> => {
      return fetchFromApi(`/api/v1/interviews/${id}/cancel`, {
        method: 'PATCH',
        body: JSON.stringify({ reason }),
      });
    },

    bulkCancel: async (interview_ids: number[], reason: string): Promise<any> => {
      return fetchFromApi('/api/v1/interviews/bulk/cancel', {
        method: 'POST',
        body: JSON.stringify({ interview_ids, reason }),
      });
    },

    bulkDelete: async (interview_ids: number[]): Promise<any> => {
      return fetchFromApi('/api/v1/interviews/bulk/delete', {
        method: 'POST',
        body: JSON.stringify({ interview_ids }),
      });
    },

    monitor: async (id: number): Promise<any> => {
      return fetchFromApi(`/api/v1/interviews/${id}/monitor`);
    },
  },

  // Job endpoints
  jobs: {
    getAll: async (params?: {
      page?: number;
      page_size?: number;
      search?: string;
    }): Promise<{ jobs: JobResponse[]; total: number; page: number; page_size: number; total_pages: number }> => {
      const searchParams = new URLSearchParams();
      if (params?.page) searchParams.set('page', params.page.toString());
      if (params?.page_size) searchParams.set('page_size', params.page_size.toString());
      if (params?.search) searchParams.set('search', params.search);

      const endpoint = `/api/v1/jobs${searchParams.toString() ? `?${searchParams}` : ''}`;
      return fetchFromApi(endpoint);
    },

    getById: async (id: number): Promise<JobResponse> => {
      return fetchFromApi(`/api/v1/jobs/${id}`);
    },
  },

  // Question endpoints
  questions: {
    getAll: async (params?: {
      page?: number;
      page_size?: number;
      category?: QuestionFilter['category'];
      importance?: QuestionFilter['importance'];
      search?: string;
      created_by_user_id?: number;
    }): Promise<QuestionListResponse> => {
      const searchParams = new URLSearchParams();
      if (params?.page) searchParams.set('page', params.page.toString());
      if (params?.page_size) searchParams.set('page_size', params.page_size.toString());
      if (params?.category) searchParams.set('category', params.category);
      if (params?.importance) searchParams.set('importance', params.importance);
      if (params?.search) searchParams.set('search', params.search);
      if (params?.created_by_user_id) searchParams.set('created_by_user_id', params.created_by_user_id.toString());

      const endpoint = `/api/v1/questions${searchParams.toString() ? `?${searchParams}` : ''}`;
      return fetchFromApi(endpoint);
    },

    getById: async (id: number): Promise<QuestionResponse> => {
      return fetchFromApi(`/api/v1/questions/${id}`);
    },

    create: async (data: QuestionCreate): Promise<QuestionResponse> => {
      return fetchFromApi('/api/v1/questions', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },

    update: async (id: number, data: QuestionUpdate): Promise<QuestionResponse> => {
      return fetchFromApi(`/api/v1/questions/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      });
    },

    delete: async (id: number): Promise<void> => {
      return fetchFromApi(`/api/v1/questions/${id}`, {
        method: 'DELETE',
      });
    },

    getByCategory: async (category: QuestionFilter['category'], params?: {
      page?: number;
      page_size?: number;
    }): Promise<QuestionListResponse> => {
      const searchParams = new URLSearchParams();
      if (params?.page) searchParams.set('page', params.page.toString());
      if (params?.page_size) searchParams.set('page_size', params.page_size.toString());
      
      const endpoint = `/api/v1/questions/category/${category}${searchParams.toString() ? `?${searchParams}` : ''}`;
      return fetchFromApi(endpoint);
    },

    search: async (searchTerm: string, params?: {
      page?: number;
      page_size?: number;
    }): Promise<QuestionListResponse> => {
      const searchParams = new URLSearchParams();
      if (params?.page) searchParams.set('page', params.page.toString());
      if (params?.page_size) searchParams.set('page_size', params.page_size.toString());
      
      const endpoint = `/api/v1/questions/search/${encodeURIComponent(searchTerm)}${searchParams.toString() ? `?${searchParams}` : ''}`;
      return fetchFromApi(endpoint);
    },

    bulkDelete: async (data: BulkQuestionDelete): Promise<{ message: string }> => {
      return fetchFromApi('/api/v1/questions/bulk/delete', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },

    bulkUpdateCategory: async (data: BulkQuestionCategoryUpdate): Promise<{ message: string }> => {
      return fetchFromApi('/api/v1/questions/bulk/update-category', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },

    assignToJob: async (data: JobQuestionAssignment): Promise<{ message: string }> => {
      return fetchFromApi('/api/v1/questions/assign-to-job', {
        method: 'POST',
        body: JSON.stringify(data),
      });
    },

    getWithCreatorInfo: async (params?: {
      page?: number;
      page_size?: number;
    }): Promise<QuestionListResponse> => {
      const searchParams = new URLSearchParams();
      if (params?.page) searchParams.set('page', params.page.toString());
      if (params?.page_size) searchParams.set('page_size', params.page_size.toString());
      
      const endpoint = `/api/v1/questions/with-creator-info${searchParams.toString() ? `?${searchParams}` : ''}`;
      return fetchFromApi(endpoint);
    },
  },
};

export default api;