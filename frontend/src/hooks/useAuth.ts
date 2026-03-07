import { authApi, userApi } from '../api'
import { translateStatic } from '../i18n'
import type { User } from '../types/api'
import { useAuthStore, usePermissionStore } from '../store'

export const useAuth = () => {
  const { user, token, isAuthenticated, setAuth, logout, updateUser } = useAuthStore()

  const login = async (account: string, password: string) => {
    const response = await authApi.login({ account, password })
    if (response.user && response.token) {
      setAuth(response.user, response.token.access_token)
      return { success: true }
    }
    return { success: false, message: translateStatic('hook.auth.loginFailed') }
  }

  const register = async (data: { email?: string; phone?: string; password: string; nickname?: string }) => {
    const response = await authApi.register(data)
    return { success: true, data: response }
  }

  const fetchCurrentUser = async () => {
    if (!token) return null
    try {
      const currentUser = await authApi.getCurrentUser()
      updateUser(currentUser)
      return currentUser
    } catch {
      logout()
      return null
    }
  }

  const updateProfile = async (data: Partial<User>) => {
    const response = await authApi.updateProfile(data)
    updateUser(data)
    return response
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    register,
    logout,
    fetchCurrentUser,
    updateProfile,
  }
}

export const usePermissions = () => {
  const { permissions, setPermissions, hasPermission, getRemainingCount } = usePermissionStore()

  const fetchPermissions = async () => {
    const response = await userApi.getPermissions()
    setPermissions(response)
    return response
  }

  const checkPermission = async (type: string) => {
    const response = await userApi.checkPermission(type)
    return response
  }

  return {
    permissions,
    fetchPermissions,
    checkPermission,
    hasPermission,
    getRemainingCount,
  }
}

export const useBalance = () => {
  const { user, updateUser } = useAuthStore()

  const fetchBalance = async () => {
    const response = await authApi.getBalance()
    updateUser({ balance: response.balance })
    return response.balance
  }

  return {
    balance: user?.balance || 0,
    fetchBalance,
  }
}
