import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthUser {
  user_id: string;
  organization_id: string;
  email: string;
  access_token: string;
}

interface AuthStore {
  user: AuthUser | null;
  login: (user: AuthUser) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      login: (user: AuthUser) => set({ user }),
      logout: () => set({ user: null }),
      isAuthenticated: () => get().user !== null,
    }),
    {
      name: 'auth-storage',
    }
  )
);