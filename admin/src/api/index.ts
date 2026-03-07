import axios, { AxiosHeaders, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import * as Types from '../types/api'
import { getCurrentLanguage } from '../i18n'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.client.interceptors.request.use(
      (config) => {
        const headers = AxiosHeaders.from(config.headers)
        const token = localStorage.getItem('admin_token')
        if (token) {
          headers.set('Authorization', `Bearer ${token}`)
        }

        const language = getCurrentLanguage() === 'zh' ? 'zh-CN' : 'en-US'
        headers.set('Accept-Language', language)
        config.headers = headers

        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('admin_token')
          window.location.href = '/admin/login'
        }
        return Promise.reject(error)
      }
    )
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.get(url, config)
    return response.data
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.post(url, data, config)
    return response.data
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.put(url, data, config)
    return response.data
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.delete(url, config)
    return response.data
  }
}

export const apiClient = new ApiClient()

export const authApi = {
  login: (data: { account: string; password: string }): Promise<Types.LoginResponse> =>
    apiClient.post('/auth/login', data),
  
  getCurrentUser: (): Promise<Types.User> =>
    apiClient.get('/auth/me'),
}

export const adminApi = {
  getDashboard: (): Promise<Types.DashboardData> =>
    apiClient.get('/admin/dashboard'),
  
  getUsers: (skip = 0, limit = 20, status?: number): Promise<Types.User[]> => {
    let url = `/admin/users?skip=${skip}&limit=${limit}`
    if (status !== undefined) url += `&status=${status}`
    return apiClient.get(url)
  },
  
  updateUserStatus: (userId: number, status: number): Promise<void> =>
    apiClient.put(`/admin/users/${userId}/status?status=${status}`),
  
  getOrders: (skip = 0, limit = 20, status?: number, orderType?: string): Promise<Types.Order[]> => {
    let url = `/admin/orders?skip=${skip}&limit=${limit}`
    if (status !== undefined) url += `&status=${status}`
    if (orderType) url += `&order_type=${orderType}`
    return apiClient.get(url)
  },
  
  getRevenueStats: (startDate?: string, endDate?: string): Promise<Types.RevenueStats> => {
    let url = '/admin/revenue/stats'
    const params = []
    if (startDate) params.push(`start_date=${startDate}`)
    if (endDate) params.push(`end_date=${endDate}`)
    if (params.length) url += '?' + params.join('&')
    return apiClient.get(url)
  },
  
  getPermissionPrices: (): Promise<any> =>
    apiClient.get('/admin/permissions/prices'),
  
  updatePermissionPrices: (prices: any): Promise<void> =>
    apiClient.put('/admin/permissions/prices', prices),
}
