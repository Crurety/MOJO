// API鍝嶅簲绫诲瀷瀹氫箟

// 鐢ㄦ埛鐩稿叧绫诲瀷
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

// 璁よ瘉鐩稿叧绫诲瀷
export interface AdminAccount {
  id: number
  username: string
  email?: string
  nickname?: string
  role: string
  status: number
  created_at: string
}

export interface LoginResponse {
  user: AdminAccount
  token: {
    access_token: string
    token_type: string
  }
}

// 浠诲姟鐩稿叧绫诲瀷
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

// 浣滃搧鐩稿叧绫诲瀷
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

// 璁㈠崟鐩稿叧绫诲瀷
export interface Order {
  id?: number
  order_no: string
  user_id: number
  user_nickname?: string
  order_type: string
  product_name?: string
  amount: number
  payment_method?: string
  status: number
  created_at: string
  completed_at?: string
}

// 浠〃鐩樼浉鍏崇被鍨?
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

// 鏀跺叆缁熻鐩稿叧绫诲瀷
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

// 閫氱敤鍝嶅簲绫诲瀷
export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

// 鍒嗛〉鍝嶅簲绫诲瀷
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface AdminListResponse<T> {
  items: T[]
  total: number
  skip: number
  limit: number
}

