import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { api, UserInfo } from '@/lib/api';

interface AuthContextType {
  user: UserInfo | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = user !== null && api.auth.isAuthenticated();

  // Initialize auth state on mount
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        if (api.auth.isAuthenticated()) {
          // Try to get stored user first
          const storedUser = api.auth.getStoredUser();
          if (storedUser) {
            setUser(storedUser);
          }
          
          // Then refresh from server to ensure up-to-date info
          try {
            const currentUser = await api.auth.getCurrentUser();
            setUser(currentUser);
            // Update stored user info
            localStorage.setItem('user_info', JSON.stringify(currentUser));
          } catch (error) {
            // If server request fails but we have stored user, keep it
            if (!storedUser) {
              console.error('Failed to get current user:', error);
              api.auth.clearTokens();
              setUser(null);
            }
          }
        } else {
          // Clear any stale data
          api.auth.clearTokens();
          setUser(null);
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        api.auth.clearTokens();
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const signIn = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      const response = await api.auth.signIn({ email, password });
      setUser(response.user);
    } catch (error) {
      console.error('Sign in error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const signOut = async () => {
    try {
      setIsLoading(true);
      await api.auth.signOut();
    } catch (error) {
      console.error('Sign out error:', error);
      // Even if server request fails, clear local state
    } finally {
      api.auth.clearTokens();
      setUser(null);
      setIsLoading(false);
    }
  };

  const refreshUser = async () => {
    try {
      if (api.auth.isAuthenticated()) {
        const currentUser = await api.auth.getCurrentUser();
        setUser(currentUser);
        localStorage.setItem('user_info', JSON.stringify(currentUser));
      }
    } catch (error) {
      console.error('Refresh user error:', error);
      // If refresh fails, sign out
      await signOut();
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated,
    isLoading,
    signIn,
    signOut,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
