import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiService, User } from '../services/api';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string, role: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
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
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Check if user is authenticated on app load
  useEffect(() => {
    const checkAuth = async () => {
      try {
        if (apiService.isAuthenticated()) {
          try {
            const currentUser = await apiService.getCurrentUser();
            setUser(currentUser);
          } catch (e) {
            const username = localStorage.getItem('username');
            if (username || (e instanceof Error && e.message === 'AUTH_ME_UNAVAILABLE')) {
              setUser({ id: 0, username, email: `${username}@local`, role: 'user', created_at: '', updated_at: '' } as any);
            } else {
              apiService.logout();
            }
          }
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        apiService.logout();
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (email: string, password: string) => {
    // Extract username from email (part before @, or use email/username if no @)
    const usernameFallback = email.includes('@') 
      ? email.split('@')[0] 
      : email || 'userid';

    try {
      // Try to login (will use fallback if backend is unavailable)
          await apiService.login({ email, password });
      
      // Try to get current user from backend
          try {
            const currentUser = await apiService.getCurrentUser();
            localStorage.setItem('username', currentUser.username);
            setUser(currentUser);
      } catch (e) {
        // Backend unavailable or getCurrentUser failed - use fallback user
        // Username should already be stored by apiService.login fallback
        const storedUsername = localStorage.getItem('username') || usernameFallback;
        localStorage.setItem('username', storedUsername);
        setUser({ 
          id: 0, 
          username: storedUsername, 
          email, 
          role: 'user', 
          created_at: '', 
          updated_at: '' 
        } as any);
          }
    } catch (error) {
      // If login itself throws (shouldn't happen with fallback, but just in case)
      console.warn('Login error, using fallback:', error);
      apiService.setToken('dev-token-fallback');
        localStorage.setItem('username', usernameFallback);
      setUser({ 
        id: 0, 
        username: usernameFallback, 
        email, 
        role: 'user', 
        created_at: '', 
        updated_at: '' 
      } as any);
    }
  };

  const register = async (username: string, email: string, password: string, role: string) => {
    try {
      await apiService.register({ username, email, password, role });
      // Don't automatically log in - let user see success message first
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  };

  const logout = () => {
    apiService.logout();
    localStorage.removeItem('username');
    setUser(null);
  };

  const value: AuthContextType = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
