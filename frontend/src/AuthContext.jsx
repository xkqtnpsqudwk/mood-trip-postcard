import { createContext, useContext, useEffect, useState } from "react";
import {
  clearToken,
  fetchMe,
  getToken,
  login as apiLogin,
  logout as apiLogout,
  setToken,
  signup as apiSignup,
} from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!getToken()) {
      setIsLoading(false);
      return;
    }
    fetchMe()
      .then((me) => setUser(me))
      .catch(() => clearToken())
      .finally(() => setIsLoading(false));
  }, []);

  const signup = async (username, password) => {
    const result = await apiSignup(username, password);
    setToken(result.token);
    setUser({ username: result.username });
    return result;
  };

  const login = async (username, password) => {
    const result = await apiLogin(username, password);
    setToken(result.token);
    setUser({ username: result.username });
    return result;
  };

  const logout = async () => {
    try {
      await apiLogout();
    } catch {
      // best-effort: clear local state regardless of network failure
    }
    clearToken();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, signup, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
