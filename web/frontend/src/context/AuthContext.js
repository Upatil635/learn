import React, { createContext, useContext, useEffect, useState } from 'react';
import api, { TOKEN_KEY } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (token) {
      localStorage.setItem(TOKEN_KEY, token);
    } else {
      localStorage.removeItem(TOKEN_KEY);
    }
  }, [token]);

  useEffect(() => {
    let cancelled = false;
    const boot = async () => {
      if (!token) {
        setUser(null);
        setReady(true);
        return;
      }
      try {
        const res = await api.get('/auth/me');
        if (!cancelled) {
          setUser(res.data.user);
        }
      } catch {
        if (!cancelled) {
          setToken(null);
          setUser(null);
        }
      } finally {
        if (!cancelled) setReady(true);
      }
    };
    boot();
    return () => {
      cancelled = true;
    };
  }, [token]);

  useEffect(() => {
    const onLogout = () => {
      setToken(null);
      setUser(null);
    };
    window.addEventListener('learneasy-logout', onLogout);
    return () => window.removeEventListener('learneasy-logout', onLogout);
  }, []);

  const login = async (username, password) => {
    const res = await api.post('/auth/login', { username, password });
    setToken(res.data.token);
    setUser(res.data.user);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
  };

  const setTheme = async (theme) => {
    const res = await api.patch('/auth/me', { theme });
    setUser(res.data.user);
  };

  return (
    <AuthContext.Provider value={{ token, user, ready, login, logout, setTheme }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return ctx;
}
