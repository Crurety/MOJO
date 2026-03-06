// API响应类型定义

// 用户相关类型
export interface User {
  id: number
  email?: string
  phone?: string
  nickname: string
  avatar?: string
  balance: number
  status: number
  created_at: string
}

// 认证相关类型
export interface LoginResponse {
  user: User
  token: {
    access_token: string
    token_type: string
  }
}

export interface RegisterResponse {
  user: User
  token: {
    access_token: string
    token_type: string
  }
}

// 权限相关类型
export interface Permission {
  id: number
  permission_type: string
  payment_mode: string
  total_count: number
  used_count: number
  expire_at?: string
  status: number
}

// 任务相关类型
export interface Task {
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

// 作品相关类型
export interface Work {
  id: number
  work_type: string
  title: string
  description?: string
  content_url: string
  thumbnail_url?: string
  status: number
  created_at: string
  updated_at: string
}

// 订单相关类型
export interface Order {
  order_no: string
  user_id: number
  user_nickname: string
  order_type: string
  product_name?: string
  amount: number
  payment_method: string
  status: number
  created_at: string
  completed_at?: string
}

// 支付相关类型
export interface PaymentResponse {
  order_no: string
  pay_url?: string
  status: string
}

// 仪表盘相关类型
export interface DashboardData {
  total_users: number
  total_orders: number
  total_revenue: number
  recent_orders: Order[]
  revenue_trend: {
    date: string
    amount: number
  }[]
}

// 收入统计相关类型
export interface RevenueStats {
  total_revenue: number
  daily_stats: {
    date: string
    amount: number
  }[]
  payment_method_stats: {
    method: string
    amount: number
    count: number
  }[]
  order_type_stats: {
    type: string
    amount: number
    count: number
  }[]
}

// 通用响应类型
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

// 分页响应类型
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}
