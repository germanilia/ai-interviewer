import { api } from '@/lib/api';

// Mock fetch globally
const mockFetch = global.fetch as jest.MockedFunction<typeof fetch>;

// Mock the config module to avoid import.meta issues
jest.mock('@/lib/config', () => ({
  __esModule: true,
  default: {
    apiUrl: 'http://localhost:9000'
  }
}));

describe('API Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    
    // Set up auth token for authenticated requests
    localStorage.setItem('access_token', 'test-token');
    // Set token expiry to 1 hour from now
    localStorage.setItem('token_expires_at', (Date.now() + 3600000).toString());
    
    // Reset fetch mock
    mockFetch.mockClear();
  });

  describe('authentication methods', () => {
    describe('signUp', () => {
      it('makes POST request to signup endpoint', async () => {
        const mockResponse = {
          message: 'User created successfully',
          user_sub: 'user123',
          user_confirmed: true,
        };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockResponse,
        } as Response);

        const signUpData = {
          email: 'test@example.com',
          password: 'password123',
          full_name: 'Test User',
        };

        const result = await api.auth.signUp(signUpData);

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/v1/auth/signup'),
          expect.objectContaining({
            method: 'POST',
            headers: expect.objectContaining({
              'Content-Type': 'application/json',
            }),
            body: JSON.stringify(signUpData),
          })
        );

        expect(result).toEqual(mockResponse);
      });
    });

    describe('signIn', () => {
      it('makes POST request to signin endpoint and stores tokens', async () => {
        const mockResponse = {
          access_token: 'access123',
          id_token: 'id123',
          refresh_token: 'refresh123',
          expires_in: 3600,
          token_type: 'Bearer',
          user: {
            username: 'testuser',
            email: 'test@example.com',
            full_name: 'Test User',
            role: 'user',
            is_active: true,
          },
        };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockResponse,
        } as Response);

        const signInData = {
          email: 'test@example.com',
          password: 'password123',
        };

        const result = await api.auth.signIn(signInData);

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/v1/auth/signin'),
          expect.objectContaining({
            method: 'POST',
            body: JSON.stringify(signInData),
          })
        );

        expect(result).toEqual(mockResponse);

        // Check that tokens are stored
        expect(localStorage.setItem).toHaveBeenCalledWith(
          'access_token',
          mockResponse.access_token
        );
        expect(localStorage.setItem).toHaveBeenCalledWith(
          'id_token',
          mockResponse.id_token
        );
        expect(localStorage.setItem).toHaveBeenCalledWith(
          'user_info',
          JSON.stringify(mockResponse.user)
        );
      });
    });

    describe('getCurrentUser', () => {
      it('makes GET request to /me endpoint with auth header', async () => {
        const mockUser = {
          username: 'testuser',
          email: 'test@example.com',
          full_name: 'Test User',
          role: 'user',
          is_active: true,
        };

        const futureTime = Date.now() + 3600000; // 1 hour from now
        (localStorage.getItem as jest.Mock).mockImplementation((key: string) => {
          if (key === 'access_token') return 'test-token';
          if (key === 'token_expires_at') return futureTime.toString();
          return null;
        });

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockUser,
        } as Response);

        const result = await api.auth.getCurrentUser();

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/v1/auth/me'),
          expect.objectContaining({
            headers: expect.objectContaining({
              Authorization: 'Bearer test-token',
            }),
          })
        );

        expect(result).toEqual(mockUser);
      });
    });

    describe('signOut', () => {
      it('makes POST request to signout endpoint and clears tokens', async () => {
        const mockResponse = { message: 'Signed out successfully' };

        const futureTime = Date.now() + 3600000; // 1 hour from now
        (localStorage.getItem as jest.Mock).mockImplementation((key: string) => {
          if (key === 'access_token') return 'test-token';
          if (key === 'token_expires_at') return futureTime.toString();
          return null;
        });

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockResponse,
        } as Response);

        const result = await api.auth.signOut();

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/v1/auth/signout'),
          expect.objectContaining({
            method: 'POST',
            headers: expect.objectContaining({
              Authorization: 'Bearer test-token',
            }),
          })
        );

        expect(result).toEqual(mockResponse);

        // Check that tokens are cleared
        expect(localStorage.removeItem).toHaveBeenCalledWith('access_token');
        expect(localStorage.removeItem).toHaveBeenCalledWith('id_token');
        expect(localStorage.removeItem).toHaveBeenCalledWith('refresh_token');
        expect(localStorage.removeItem).toHaveBeenCalledWith('user_info');
      });
    });
  });

  describe('authentication helpers', () => {
    describe('isAuthenticated', () => {
      it('returns true when valid token exists and not expired', () => {
        const futureTime = Date.now() + 3600000; // 1 hour from now
        
        (localStorage.getItem as jest.Mock).mockImplementation((key: string) => {
          if (key === 'access_token') return 'test-token';
          if (key === 'token_expires_at') return futureTime.toString();
          return null;
        });

        expect(api.auth.isAuthenticated()).toBe(true);
      });

      it('returns false when no token exists', () => {
        (localStorage.getItem as jest.Mock).mockReturnValue(null);

        expect(api.auth.isAuthenticated()).toBe(false);
      });

      it('returns false when token is expired', () => {
        const pastTime = Date.now() - 3600000; // 1 hour ago
        
        (localStorage.getItem as jest.Mock).mockImplementation((key: string) => {
          if (key === 'access_token') return 'test-token';
          if (key === 'token_expires_at') return pastTime.toString();
          return null;
        });

        expect(api.auth.isAuthenticated()).toBe(false);
      });
    });

    describe('getStoredUser', () => {
      it('returns parsed user from localStorage', () => {
        const mockUser = {
          username: 'testuser',
          email: 'test@example.com',
          full_name: 'Test User',
          role: 'user',
          is_active: true,
        };

        (localStorage.getItem as jest.Mock).mockReturnValue(JSON.stringify(mockUser));

        const result = api.auth.getStoredUser();

        expect(localStorage.getItem).toHaveBeenCalledWith('user_info');
        expect(result).toEqual(mockUser);
      });

      it('returns null when no user stored', () => {
        (localStorage.getItem as jest.Mock).mockReturnValue(null);

        const result = api.auth.getStoredUser();

        expect(result).toBeNull();
      });

      it('returns null when stored data is invalid JSON', () => {
        (localStorage.getItem as jest.Mock).mockReturnValue('invalid-json');

        const result = api.auth.getStoredUser();

        expect(result).toBeNull();
        // Should also clear the invalid data
        expect(localStorage.removeItem).toHaveBeenCalledWith('user_info');
      });
    });

    describe('clearTokens', () => {
      it('removes all auth-related items from localStorage', () => {
        api.auth.clearTokens();

        expect(localStorage.removeItem).toHaveBeenCalledWith('access_token');
        expect(localStorage.removeItem).toHaveBeenCalledWith('id_token');
        expect(localStorage.removeItem).toHaveBeenCalledWith('refresh_token');
        expect(localStorage.removeItem).toHaveBeenCalledWith('token_expires_at');
        expect(localStorage.removeItem).toHaveBeenCalledWith('user_info');
      });
    });
  });

  describe('error handling', () => {
    it('throws error for 404 response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: async () => 'Not Found',
      } as Response);

      await expect(api.auth.getCurrentUser()).rejects.toThrow('Request failed with status 404');
    });

    it('throws error for 500 response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({ detail: 'Server error' }),
      } as Response);

      await expect(api.auth.getCurrentUser()).rejects.toThrow('Server error');
    });

    it('handles network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(api.auth.getCurrentUser()).rejects.toThrow('Network error');
    });

    it('handles invalid JSON response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockRejectedValue(new Error('Invalid JSON')),
      } as unknown as Response);

      await expect(api.auth.getCurrentUser()).rejects.toThrow('Invalid JSON');
    });
  });

  describe('other endpoints', () => {
    describe('getUsers', () => {
      it('makes GET request to users endpoint', async () => {
        const mockUsers = [
          { id: 1, username: 'user1', email: 'user1@example.com' },
          { id: 2, username: 'user2', email: 'user2@example.com' },
        ];

        const futureTime = Date.now() + 3600000; // 1 hour from now
        (localStorage.getItem as jest.Mock).mockImplementation((key: string) => {
          if (key === 'access_token') return 'test-token';
          if (key === 'token_expires_at') return futureTime.toString();
          return null;
        });

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockUsers,
        } as Response);

        const result = await api.getUsers();

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/api/v1/users/'),
          expect.objectContaining({
            headers: expect.objectContaining({
              Authorization: 'Bearer test-token',
            }),
          })
        );

        expect(result).toEqual(mockUsers);
      });
    });

    describe('getHealth', () => {
      it('makes GET request to health endpoint', async () => {
        const mockHealth = { status: 'healthy' };

        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => mockHealth,
        } as Response);

        const result = await api.getHealth();

        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/health'),
          expect.objectContaining({
            headers: expect.objectContaining({
              'Content-Type': 'application/json',
            }),
          })
        );

        expect(result).toEqual(mockHealth);
      });
    });
  });
});
