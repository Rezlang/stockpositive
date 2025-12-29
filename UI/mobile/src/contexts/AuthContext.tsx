import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  useMemo,
  ReactNode,
} from 'react';
import { UserResponse, RegisterRequest } from '@/types/api';
import { authService, apiClient } from '@/services/api';
import { storageService } from '@/services/storage';

interface AuthContextValue {
  user: UserResponse | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Handle unauthorized responses from API
  const handleUnauthorized = useCallback(async () => {
    setUser(null);
    setToken(null);
    await storageService.removeToken();
  }, []);

  // Set up the unauthorized handler on mount
  useEffect(() => {
    apiClient.setUnauthorizedHandler(handleUnauthorized);
  }, [handleUnauthorized]);

  // Check for existing token on mount
  useEffect(() => {
    const initAuth = async () => {
      try {
        const savedToken = await storageService.getToken();
        if (savedToken) {
          setToken(savedToken);
          // Validate token by fetching user
          const userData = await authService.getCurrentUser();
          setUser(userData);
        }
      } catch {
        // Token is invalid or expired
        await storageService.removeToken();
      } finally {
        setIsLoading(false);
      }
    };
    initAuth();
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const tokenResponse = await authService.login(email, password);
      const newToken = tokenResponse.access_token;

      // Save token first
      await storageService.setToken(newToken);
      setToken(newToken);

      // Fetch user data
      const userData = await authService.getCurrentUser();
      setUser(userData);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(async (data: RegisterRequest) => {
    setIsLoading(true);
    setError(null);
    try {
      // Register the user
      await authService.register(data);

      // Auto-login after registration
      const tokenResponse = await authService.login(data.email, data.password);
      const newToken = tokenResponse.access_token;

      await storageService.setToken(newToken);
      setToken(newToken);

      const userData = await authService.getCurrentUser();
      setUser(userData);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Registration failed';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    setIsLoading(true);
    try {
      await storageService.removeToken();
      await storageService.removeActiveFeedId();
      setUser(null);
      setToken(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const refreshUser = useCallback(async () => {
    if (!token) return;
    try {
      const userData = await authService.getCurrentUser();
      setUser(userData);
    } catch {
      // Token might be invalid
      await handleUnauthorized();
    }
  }, [token, handleUnauthorized]);

  const value = useMemo(
    () => ({
      user,
      token,
      isLoading,
      isAuthenticated: !!user && !!token,
      error,
      login,
      register,
      logout,
      clearError,
      refreshUser,
    }),
    [user, token, isLoading, error, login, register, logout, clearError, refreshUser]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
