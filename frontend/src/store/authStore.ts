import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  user_id: string
  email: string
  full_name: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  theme: 'dark' | 'light'
  login: (token: string, user: User) => void
  logout: () => void
  toggleTheme: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      theme: 'dark' as 'dark' | 'light',
      login: (token, user) => set({ token, user, isAuthenticated: true }),
      logout: () => set({ token: null, user: null, isAuthenticated: false }),
      toggleTheme: () => set((s) => ({ theme: s.theme === 'dark' ? 'light' : 'dark' })),
    }),
    { name: 'legal-ai-auth' }
  )
)
