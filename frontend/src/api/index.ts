import axios, { AxiosHeaders, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import * as Types from '../types/api'
import { getCurrentLanguage } from '../i18n'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

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
        const token = localStorage.getItem('token')
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
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          window.location.href = '/login'
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
  register: (data: { email?: string; phone?: string; password: string; nickname?: string }): Promise<Types.RegisterResponse> =>
    apiClient.post('/auth/register', data),
  
  login: (data: { account: string; password: string }): Promise<Types.LoginResponse> =>
    apiClient.post('/auth/login', data),
  
  getCurrentUser: (): Promise<Types.User> =>
    apiClient.get('/auth/me'),
  
  updateProfile: (data: Partial<Types.User>): Promise<Types.User> =>
    apiClient.put('/auth/me', data),
  
  getBalance: (): Promise<{ balance: number }> =>
    apiClient.get('/auth/me/balance'),
}

export const userApi = {
  getPermissions: (): Promise<Types.Permission[]> =>
    apiClient.get('/user/permissions'),
  
  checkPermission: (permissionType: string): Promise<{ has_permission: boolean }> =>
    apiClient.get(`/user/permissions/check?permission_type=${permissionType}`),
}

export const contentApi = {
  createScript: (data: any): Promise<any> =>
    apiClient.post('/content/scripts', data),
  
  getScripts: (skip = 0, limit = 20): Promise<any[]> =>
    apiClient.get(`/content/scripts?skip=${skip}&limit=${limit}`),
  
  getScript: (id: number): Promise<any> =>
    apiClient.get(`/content/scripts/${id}`),
  
  updateScript: (id: number, data: any): Promise<any> =>
    apiClient.put(`/content/scripts/${id}`, data),
  
  deleteScript: (id: number): Promise<void> =>
    apiClient.delete(`/content/scripts/${id}`),
  
  createTask: (data: any): Promise<any> =>
    apiClient.post('/content/tasks', data),
  
  getTasks: (skip = 0, limit = 20, status?: number, taskType?: string): Promise<Types.Task[]> => {
    let url = `/content/tasks?skip=${skip}&limit=${limit}`
    if (status !== undefined) url += `&status=${status}`
    if (taskType) url += `&task_type=${taskType}`
    return apiClient.get(url)
  },
  
  getTask: (taskNo: string): Promise<Types.Task> =>
    apiClient.get(`/content/tasks/${taskNo}`),
  
  getWorks: (skip = 0, limit = 20, workType?: string): Promise<Types.Work[]> => {
    let url = `/content/works?skip=${skip}&limit=${limit}`
    if (workType) url += `&work_type=${workType}`
    return apiClient.get(url)
  },
  
  getWork: (id: number): Promise<Types.Work> =>
    apiClient.get(`/content/works/${id}`),
  
  deleteWork: (id: number): Promise<void> =>
    apiClient.delete(`/content/works/${id}`),
  
  getGallery: (skip = 0, limit = 20, workType?: string): Promise<Types.Work[]> => {
    let url = `/content/gallery?skip=${skip}&limit=${limit}`
    if (workType) url += `&work_type=${workType}`
    return apiClient.get(url)
  },
}

export const paymentApi = {
  getPermissionPrices: (): Promise<Record<string, Record<string, number>>> =>
    apiClient.get('/payment/permissions/prices'),

  createOrder: (data: any): Promise<Types.Order> =>
    apiClient.post('/payment/orders', data),
  
  createBalanceOrder: (amount: number, paymentMethod: string): Promise<Types.Order> =>
    apiClient.post(`/payment/orders/balance?amount=${amount}&payment_method=${paymentMethod}`),
  
  getOrders: (skip = 0, limit = 20, status?: number): Promise<Types.Order[]> => {
    let url = `/payment/orders?skip=${skip}&limit=${limit}`
    if (status !== undefined) url += `&status=${status}`
    return apiClient.get(url)
  },
  
  getOrder: (orderNo: string): Promise<Types.Order> =>
    apiClient.get(`/payment/orders/${orderNo}`),
  
  payOrder: (orderNo: string): Promise<Types.PaymentResponse> =>
    apiClient.post(`/payment/orders/${orderNo}/pay`),
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
