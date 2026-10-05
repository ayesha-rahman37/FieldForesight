import React, { createContext, useContext, useState, useEffect } from 'react';
import type { User } from '../features/personalization/types';
import { getMe, logoutUser } from '../api/auth';

interface AuthContextType {
  token: string | null;
  user: User | null;
  login: (token: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'));
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const loadCurrentUser = async () => {
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const u = await getMe();
      setUser(u);
    } catch (err) {
      localStorage.removeItem('access_token');
      setToken(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCurrentUser();
  }, [token]);

  const login = async (newToken: string) => {
    localStorage.setItem('access_token', newToken);
    setToken(newToken);
  };

  const logout = async () => {
    await logoutUser();
    localStorage.removeItem('access_token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ token, user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
