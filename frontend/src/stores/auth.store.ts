import { create } from "zustand";
import type { User } from "@/types/api";
import { authApi } from "@/api/auth.api";
import { tokenKeys } from "@/api/client";

type AuthState = {
  user: User | null;
  loading: boolean;
  setTokens: (access: string, refresh: string) => void;
  loadUser: () => Promise<void>;
  clear: () => void;
};
export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  loading: true,
  setTokens: (access, refresh) => {
    localStorage.setItem(tokenKeys.access, access);
    localStorage.setItem(tokenKeys.refresh, refresh);
  },
  loadUser: async () => {
    if (!localStorage.getItem(tokenKeys.access)) {
      set({ loading: false });
      return;
    }
    try {
      const { data } = await authApi.me();
      set({ user: data, loading: false });
    } catch {
      localStorage.removeItem(tokenKeys.access);
      localStorage.removeItem(tokenKeys.refresh);
      set({ user: null, loading: false });
    }
  },
  clear: () => {
    localStorage.removeItem(tokenKeys.access);
    localStorage.removeItem(tokenKeys.refresh);
    set({ user: null });
  },
}));
