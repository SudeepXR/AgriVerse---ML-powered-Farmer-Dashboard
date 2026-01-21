import React, { createContext, useContext, useState, useEffect } from 'react';

/* =======================
   User Types
======================= */

export type FarmerUser = {
  id: number;
  username: string;
  village?: string;
  district?: string;
};

export type HeadUser = {
  id: number;
  username: string;
  full_name?: string;
  role: string;
};

export type User = FarmerUser | HeadUser;

/* =======================
   Auth Context Type
======================= */

interface AuthContextType {
  user: User | null;
  role: 'farmer' | 'head' | null;
  login: (role: 'farmer' | 'head', userData: User) => void;
  logout: () => void;
  isAuthenticated: boolean;
}

/* =======================
   Context Creation
======================= */

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/* =======================
   Provider
======================= */

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [role, setRole] = useState<'farmer' | 'head' | null>(null);

  // Restore auth state from localStorage
  useEffect(() => {
    const storedAuth = localStorage.getItem('auth');
    if (storedAuth) {
      const parsed = JSON.parse(storedAuth);
      setUser(parsed.user);
      setRole(parsed.role);
    }
  }, []);

  const login = (userRole: 'farmer' | 'head', userData: User) => {
    setUser(userData);
    setRole(userRole);

    localStorage.setItem(
      'auth',
      JSON.stringify({
        user: userData,
        role: userRole
      })
    );
  };

  const logout = () => {
    setUser(null);
    setRole(null);
    localStorage.removeItem('auth');
  };

  const value: AuthContextType = {
    user,
    role,
    login,
    logout,
    isAuthenticated: !!user
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

/* =======================
  Hook
======================= */

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
