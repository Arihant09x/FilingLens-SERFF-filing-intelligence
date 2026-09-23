import { api } from "./client";
import type { AuthTokens, User } from "@/types/api";
export const authApi = {
  register: (email: string, password: string) =>
    api.post<User>("/auth/register", { email, password }),
  login: (email: string, password: string) =>
    api.post<AuthTokens>("/auth/login", { email, password }),
  me: () => api.get<User>("/auth/me"),
};
