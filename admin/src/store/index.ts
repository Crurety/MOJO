import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface Admin {
  id: number
  username: string
  email?: string
  nickname?: string
  role: string
  status: number
  created_at?: string
}

interface AuthState {
  admin: Admin | null
  token: string | null
  isAuthenticated: boolean
  setAuth: (admin: Admin, token: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      admin: null,
      token: null,
      isAuthenticated: false,
      setAuth: (admin, token) => {
        localStorage.setItem('admin_token', token)
        set({ admin, token, isAuthenticated: true })
      },
      logout: () => {
        localStorage.removeItem('admin_token')
        set({ admin: null, token: null, isAuthenticated: false })
      },
    }),
    {
      name: 'admin-auth-storage',
      partialize: (state) => ({ admin: state.admin, token: state.token, isAuthenticated: state.isAuthenticated }),
    }
  )
)

interface UIState {
  sidebarCollapsed: boolean
  toggleSidebar: () => void
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarCollapsed: false,
      toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
    }),
    {
      name: 'admin-ui-storage',
    }
  )
)
