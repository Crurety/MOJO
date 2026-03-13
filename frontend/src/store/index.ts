import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: number
  email?: string
  phone?: string
  nickname: string
  avatar?: string
  balance: number
  status: number
  created_at: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  setAuth: (user: User, token: string) => void
  logout: () => void
  updateUser: (user: Partial<User>) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      setAuth: (user, token) => {
        localStorage.setItem('token', token)
        set({ user, token, isAuthenticated: true })
      },
      logout: () => {
        localStorage.removeItem('token')
        set({ user: null, token: null, isAuthenticated: false })
      },
      updateUser: (userData) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...userData } : null,
        })),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user, token: state.token, isAuthenticated: state.isAuthenticated }),
    }
  )
)

interface Permission {
  id: number
  permission_type: string
  payment_mode: string
  total_count: number
  used_count: number
  expire_at?: string
  status: number
}

interface PermissionState {
  permissions: Permission[]
  setPermissions: (permissions: Permission[]) => void
  hasPermission: (type: string) => boolean
  getRemainingCount: (type: string) => number
}

export const usePermissionStore = create<PermissionState>((set, get) => ({
  permissions: [],
  setPermissions: (permissions) => set({ permissions }),
  hasPermission: (type) => {
    const now = new Date()
    const perms = get().permissions.filter((p) => p.permission_type === type && p.status === 1)
    if (!perms.length) return false

    const hasSubscription = perms.some((perm) => perm.payment_mode !== 'per_use' && (!perm.expire_at || new Date(perm.expire_at) > now))
    if (hasSubscription) return true

    const remaining = perms
      .filter((perm) => perm.payment_mode === 'per_use')
      .reduce((sum, perm) => sum + Math.max(0, perm.total_count - perm.used_count), 0)

    return remaining > 0
  },
  getRemainingCount: (type) => {
    const perms = get().permissions.filter((p) => p.permission_type === type && p.payment_mode === 'per_use')
    return perms.reduce((sum, perm) => sum + Math.max(0, perm.total_count - perm.used_count), 0)
  },
}))

interface Task {
  id: number
  task_no: string
  task_type: string
  parameters: any
  status: number
  progress: number
  result_url?: string
  error_message?: string
  cost_amount: number
  created_at: string
  completed_at?: string
}

interface TaskState {
  tasks: Task[]
  currentTask: Task | null
  setTasks: (tasks: Task[]) => void
  addTask: (task: Task) => void
  updateTask: (taskNo: string, data: Partial<Task>) => void
  setCurrentTask: (task: Task | null) => void
}

export const useTaskStore = create<TaskState>((set) => ({
  tasks: [],
  currentTask: null,
  setTasks: (tasks) => set({ tasks }),
  addTask: (task) => set((state) => ({ tasks: [task, ...state.tasks] })),
  updateTask: (taskNo, data) =>
    set((state) => ({
      tasks: state.tasks.map((t) => (t.task_no === taskNo ? { ...t, ...data } : t)),
      currentTask:
        state.currentTask?.task_no === taskNo
          ? { ...state.currentTask, ...data }
          : state.currentTask,
    })),
  setCurrentTask: (task) => set({ currentTask: task }),
}))

interface UIState {
  sidebarCollapsed: boolean
  theme: 'light' | 'dark'
  toggleSidebar: () => void
  setTheme: (theme: 'light' | 'dark') => void
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarCollapsed: false,
      theme: 'light',
      toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
      setTheme: (theme) => set({ theme }),
    }),
    {
      name: 'ui-storage',
    }
  )
)
