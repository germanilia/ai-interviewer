import React from 'react';
import { render, screen, act, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';

jest.mock('@/lib/api', () => ({
  api: {
    auth: {
      signIn: jest.fn(),
      signOut: jest.fn(),
      getCurrentUser: jest.fn(),
      isAuthenticated: jest.fn(),
      getStoredUser: jest.fn(),
      clearTokens: jest.fn(),
    },
  },
}));

// Import after mocking to get typed access
import { api } from '@/lib/api';

// Get the mocked api
const mockAuth = api.auth as jest.Mocked<typeof api.auth>;

// Test component to access the auth context
const TestComponent = () => {
  const { user, isAuthenticated, isLoading, signIn, signOut, refreshUser } = useAuth();
  const [error, setError] = React.useState<string | null>(null);
  
  const handleSignIn = async () => {
    try {
      setError(null);
      await signIn('test@example.com', 'password');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    }
  };
  
  return (
    <div>
      <div data-testid="loading">{isLoading ? 'loading' : 'not-loading'}</div>
      <div data-testid="authenticated">{isAuthenticated ? 'authenticated' : 'not-authenticated'}</div>
      <div data-testid="user">{user ? JSON.stringify(user) : 'no-user'}</div>
      <div data-testid="error">{error || 'no-error'}</div>
      <button onClick={handleSignIn} data-testid="signin">
        Sign In
      </button>
      <button onClick={signOut} data-testid="signout">
        Sign Out
      </button>
      <button onClick={refreshUser} data-testid="refresh">
        Refresh User
      </button>
    </div>
  );
};

const renderWithAuthProvider = () => {
  return render(
    <AuthProvider>
      <TestComponent />
    </AuthProvider>
  );
};

describe('AuthContext', () => {
  const mockUser = {
    username: 'testuser',
    email: 'test@example.com',
    full_name: 'Test User',
    role: 'user',
    is_active: true,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  describe('initialization', () => {
    it('starts with loading state', () => {
      mockAuth.isAuthenticated.mockReturnValue(false);
      
      renderWithAuthProvider();
      
      expect(screen.getByTestId('loading')).toHaveTextContent('loading');
      expect(screen.getByTestId('authenticated')).toHaveTextContent('not-authenticated');
      expect(screen.getByTestId('user')).toHaveTextContent('no-user');
    });

    it('initializes with stored user when authenticated', async () => {
      mockAuth.isAuthenticated.mockReturnValue(true);
      mockAuth.getStoredUser.mockReturnValue(mockUser);
      mockAuth.getCurrentUser.mockResolvedValue(mockUser);
      
      renderWithAuthProvider();
      
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('not-loading');
      });
      
      expect(screen.getByTestId('authenticated')).toHaveTextContent('authenticated');
      expect(screen.getByTestId('user')).toHaveTextContent(JSON.stringify(mockUser));
    });

    it('clears auth state when not authenticated', async () => {
      mockAuth.isAuthenticated.mockReturnValue(false);
      
      renderWithAuthProvider();
      
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('not-loading');
      });
      
      expect(mockAuth.clearTokens).toHaveBeenCalled();
      expect(screen.getByTestId('authenticated')).toHaveTextContent('not-authenticated');
    });

    it('handles server error during initialization gracefully', async () => {
      mockAuth.isAuthenticated.mockReturnValue(true);
      mockAuth.getStoredUser.mockReturnValue(mockUser);
      mockAuth.getCurrentUser.mockRejectedValue(new Error('Server error'));
      
      renderWithAuthProvider();
      
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('not-loading');
      });
      
      // Should keep stored user when server request fails
      expect(screen.getByTestId('user')).toHaveTextContent(JSON.stringify(mockUser));
    });
  });

  describe('signIn', () => {
    it('successfully signs in user', async () => {
      const signInResponse = {
        access_token: 'token',
        id_token: 'id_token',
        expires_in: 3600,
        token_type: 'Bearer',
        user: mockUser,
      };
      
      mockAuth.isAuthenticated.mockReturnValue(false);
      mockAuth.signIn.mockResolvedValue(signInResponse);
      
      renderWithAuthProvider();
      
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('not-loading');
      });
      
      await act(async () => {
        screen.getByTestId('signin').click();
      });
      
      expect(mockAuth.signIn).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password',
      });
      
      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent(JSON.stringify(mockUser));
        expect(screen.getByTestId('authenticated')).toHaveTextContent('authenticated');
      });
    });

    it('handles sign in error', async () => {
      mockAuth.isAuthenticated.mockReturnValue(false);
      mockAuth.signIn.mockRejectedValue(new Error('Invalid credentials'));
      
      renderWithAuthProvider();
      
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('not-loading');
      });
      
      await act(async () => {
        screen.getByTestId('signin').click();
      });
      
      await waitFor(() => {
        expect(screen.getByTestId('error')).toHaveTextContent('Invalid credentials');
        expect(screen.getByTestId('authenticated')).toHaveTextContent('not-authenticated');
      });
    });
  });

  describe('signOut', () => {
    it('successfully signs out user', async () => {
      // Start with authenticated user
      mockAuth.isAuthenticated.mockReturnValue(true);
      mockAuth.getStoredUser.mockReturnValue(mockUser);
      mockAuth.getCurrentUser.mockResolvedValue(mockUser);
      mockAuth.signOut.mockResolvedValue({ message: 'Signed out' });
      
      renderWithAuthProvider();
      
      await waitFor(() => {
        expect(screen.getByTestId('authenticated')).toHaveTextContent('authenticated');
      });
      
      await act(async () => {
        screen.getByTestId('signout').click();
      });
      
      expect(mockAuth.signOut).toHaveBeenCalled();
      expect(mockAuth.clearTokens).toHaveBeenCalled();
      
      await waitFor(() => {
        expect(screen.getByTestId('authenticated')).toHaveTextContent('not-authenticated');
        expect(screen.getByTestId('user')).toHaveTextContent('no-user');
      });
    });

    it('clears local state even when server request fails', async () => {
      // Start with authenticated user
      mockAuth.isAuthenticated.mockReturnValue(true);
      mockAuth.getStoredUser.mockReturnValue(mockUser);
      mockAuth.getCurrentUser.mockResolvedValue(mockUser);
      mockAuth.signOut.mockRejectedValue(new Error('Server error'));
      
      renderWithAuthProvider();
      
      await waitFor(() => {
        expect(screen.getByTestId('authenticated')).toHaveTextContent('authenticated');
      });
      
      await act(async () => {
        screen.getByTestId('signout').click();
      });
      
      expect(mockAuth.clearTokens).toHaveBeenCalled();
      
      await waitFor(() => {
        expect(screen.getByTestId('authenticated')).toHaveTextContent('not-authenticated');
        expect(screen.getByTestId('user')).toHaveTextContent('no-user');
      });
    });
  });

  describe('refreshUser', () => {
    it('refreshes user data when authenticated', async () => {
      const updatedUser = { ...mockUser, full_name: 'Updated User' };
      
      // Start with authenticated user
      mockAuth.isAuthenticated.mockReturnValue(true);
      mockAuth.getStoredUser.mockReturnValue(mockUser);
      mockAuth.getCurrentUser
        .mockResolvedValueOnce(mockUser)
        .mockResolvedValueOnce(updatedUser);
      
      renderWithAuthProvider();
      
      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent(JSON.stringify(mockUser));
      });
      
      await act(async () => {
        screen.getByTestId('refresh').click();
      });
      
      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent(JSON.stringify(updatedUser));
      });
      
      expect(localStorage.setItem).toHaveBeenCalledWith('user_info', JSON.stringify(updatedUser));
    });

    it('signs out when refresh fails', async () => {
      // Start with authenticated user
      mockAuth.isAuthenticated.mockReturnValue(true);
      mockAuth.getStoredUser.mockReturnValue(mockUser);
      mockAuth.getCurrentUser
        .mockResolvedValueOnce(mockUser)
        .mockRejectedValueOnce(new Error('Token expired'));
      
      renderWithAuthProvider();
      
      await waitFor(() => {
        expect(screen.getByTestId('authenticated')).toHaveTextContent('authenticated');
      });
      
      await act(async () => {
        screen.getByTestId('refresh').click();
      });
      
      await waitFor(() => {
        expect(screen.getByTestId('authenticated')).toHaveTextContent('not-authenticated');
      });
    });
  });

  describe('error handling', () => {
    it('throws error when useAuth is used outside AuthProvider', () => {
      // Mock console.error to avoid test output noise
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      
      expect(() => {
        render(<TestComponent />);
      }).toThrow('useAuth must be used within an AuthProvider');
      
      consoleSpy.mockRestore();
    });
  });
});
