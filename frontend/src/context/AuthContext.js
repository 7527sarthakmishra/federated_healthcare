import React, { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('fedhealth_token');
      const savedUser = localStorage.getItem('fedhealth_user');

      if (token) {
        if (savedUser) {
          try {
            setUser(JSON.parse(savedUser));
          } catch (e) {
            console.error('Failed to parse cached user:', e);
          }
        }
        try {
          const profile = await authAPI.getProfile();
          if (profile) {
            setUser(profile);
            localStorage.setItem('fedhealth_user', JSON.stringify(profile));
          }
        } catch (error) {
          console.warn('Backend unavailable, proceeding with cached user credentials.');
        }
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (email, password) => {
    setLoading(true);
    try {
      const response = await authAPI.login({ email, password });
      const token = response.access_token || response.token || 'mock-token';
      const userData = response.user || {
        email,
        username: email.split('@')[0],
        role: email.includes('admin') ? 'admin' : 'researcher',
      };

      localStorage.setItem('fedhealth_token', token);
      localStorage.setItem('fedhealth_user', JSON.stringify(userData));
      setUser(userData);
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.detail || error.response?.data?.message || 'Login failed. Please check your credentials.';
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    setLoading(true);
    try {
      const response = await authAPI.register(userData);
      const token = response.access_token || response.token || 'mock-token';
      const createdUser = response.user || {
        username: userData.username,
        email: userData.email,
        role: userData.role || 'researcher',
      };

      localStorage.setItem('fedhealth_token', token);
      localStorage.setItem('fedhealth_user', JSON.stringify(createdUser));
      setUser(createdUser);
      return { success: true };
    } catch (error) {
      const message = error.response?.data?.detail || error.response?.data?.message || 'Registration failed.';
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('fedhealth_token');
    localStorage.removeItem('fedhealth_user');
    setUser(null);
  };

  const value = {
    user,
    isAuthenticated: !!user,
    loading,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
