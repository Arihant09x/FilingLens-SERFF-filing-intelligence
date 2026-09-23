import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";
export const tokenKeys = {
  access: "filinglens_access_token",
  refresh: "filinglens_refresh_token",
};

export const api = axios.create({ baseURL: API_URL, timeout: 30000 });
let refreshing: Promise<string | null> | null = null;

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(tokenKeys.access);
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (
      error.response?.status !== 401 ||
      original?._retry ||
      original?.url?.includes("/auth/refresh")
    )
      throw error;
    original._retry = true;
    const refreshToken = localStorage.getItem(tokenKeys.refresh);
    if (!refreshToken) throw error;
    refreshing ||= api
      .post(`/auth/refresh?refresh_token=${encodeURIComponent(refreshToken)}`)
      .then(({ data }) => {
        localStorage.setItem(tokenKeys.access, data.access_token);
        localStorage.setItem(tokenKeys.refresh, data.refresh_token);
        return data.access_token as string;
      })
      .catch(() => null)
      .finally(() => {
        refreshing = null;
      });
    const accessToken = await refreshing;
    if (!accessToken) {
      localStorage.removeItem(tokenKeys.access);
      localStorage.removeItem(tokenKeys.refresh);
      window.location.assign("/login");
      throw error;
    }
    original.headers.Authorization = `Bearer ${accessToken}`;
    return api(original);
  },
);
