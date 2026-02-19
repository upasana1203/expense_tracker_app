import axios from "axios";

const rawBaseUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";
const normalizedBaseUrl = rawBaseUrl.replace(/\/+$/, "");

const api = axios.create({
  baseURL: normalizedBaseUrl,
});

let accessToken = null;
let refreshToken = null;
let onLogout = null;

export const setAuthTokens = (access, refresh) => {
  accessToken = access;
  refreshToken = refresh;
};

export const bindLogoutHandler = (handler) => {
  onLogout = handler;
};

api.interceptors.request.use((config) => {
  if (typeof config.url === "string") {
    config.url = config.url.replace(/^\/+/, "");
  }
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401 && refreshToken && !error.config._retry) {
      error.config._retry = true;
      try {
        const res = await axios.post(`${api.defaults.baseURL}/auth/refresh/`, { refresh: refreshToken });
        accessToken = res.data.access;
        error.config.headers.Authorization = `Bearer ${accessToken}`;
        return api(error.config);
      } catch (refreshError) {
        if (onLogout) onLogout();
      }
    }
    return Promise.reject(error);
  }
);

export default api;
