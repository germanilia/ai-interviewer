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
};

export default api;