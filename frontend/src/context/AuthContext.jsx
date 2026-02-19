import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import api, { bindLogoutHandler, setAuthTokens } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const navigate = useNavigate();
  const [accessToken, setAccessToken] = useState(localStorage.getItem("access_token"));
  const [refreshToken, setRefreshToken] = useState(localStorage.getItem("refresh_token"));

  const logout = async () => {
    try {
      if (refreshToken) {
        await api.post("/auth/logout/", { refresh: refreshToken });
      }
    } catch (error) {
      // no-op
    }
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setAccessToken(null);
    setRefreshToken(null);
    setAuthTokens(null, null);
    navigate("/login");
  };

  useEffect(() => {
    setAuthTokens(accessToken, refreshToken);
    bindLogoutHandler(logout);
  }, [accessToken, refreshToken]);

  const login = async (email, password) => {
    const { data } = await api.post("/auth/login/", { email, password });
    localStorage.setItem("access_token", data.access);
    localStorage.setItem("refresh_token", data.refresh);
    setAccessToken(data.access);
    setRefreshToken(data.refresh);
    setAuthTokens(data.access, data.refresh);
    navigate("/");
  };

  const register = async (payload) => {
    await api.post("/auth/register/", payload);
  };

  const value = useMemo(() => ({ accessToken, refreshToken, login, logout, register }), [accessToken, refreshToken]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
