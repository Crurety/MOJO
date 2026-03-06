import { useState } from 'react'
import { paymentApi } from '../api'

export const usePayment = () => {
  const [loading, setLoading] = useState(false)

  const createPermissionOrder = async (data: {
    permission_type: string
    payment_mode: string
    payment_method: string
    count?: number
  }) => {
    setLoading(true)
    try {
      const response = await paymentApi.createOrder(data)
      return { success: true, data: response }
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || '创建订单失败' }
    } finally {
      setLoading(false)
    }
  }

  const createBalanceOrder = async (amount: number, paymentMethod: string) => {
    setLoading(true)
    try {
      const response = await paymentApi.createBalanceOrder(amount, paymentMethod)
      return { success: true, data: response }
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || '创建订单失败' }
    } finally {
      setLoading(false)
    }
  }

  const fetchOrders = async (skip = 0, limit = 20, status?: number) => {
    setLoading(true)
    try {
      const response = await paymentApi.getOrders(skip, limit, status)
      return { success: true, data: response }
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || '获取订单失败' }
    } finally {
      setLoading(false)
    }
  }

  const fetchOrderDetail = async (orderNo: string) => {
    setLoading(true)
    try {
      const response = await paymentApi.getOrder(orderNo)
      return { success: true, data: response }
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || '获取订单详情失败' }
    } finally {
      setLoading(false)
    }
  }

  const payOrder = async (orderNo: string) => {
    setLoading(true)
    try {
      const response = await paymentApi.payOrder(orderNo)
      return { success: true, data: response }
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || '支付失败' }
    } finally {
      setLoading(false)
    }
  }

  return {
    loading,
    createPermissionOrder,
    createBalanceOrder,
    fetchOrders,
    fetchOrderDetail,
    payOrder,
  }
}

export const PRICING_PLANS = {
  script: {
    name: '文字生成脚本',
    icon: '📝',
    per_use: 1,
    monthly: 29,
    yearly: 199,
    description: '智能生成创作脚本，支持多种输出类型',
  },
  image: {
    name: '图片生成',
    icon: '🖼️',
    per_use: 3,
    monthly: 99,
    yearly: 699,
    description: 'AI图片生成，支持多种风格和分辨率',
  },
  video: {
    name: '视频生成',
    icon: '🎬',
    per_use: 5,
    monthly: 199,
    yearly: 1399,
    description: 'AI视频生成，支持自定义时长和风格',
  },
  ad: {
    name: '广告设计',
    icon: '📢',
    per_use: 8,
    monthly: 299,
    yearly: 1999,
    description: '智能广告创意设计，图文视频全覆盖',
  },
}

export const PAYMENT_METHODS = [
  { value: 'balance', label: '余额支付', icon: '💰' },
  { value: 'wechat', label: '微信支付', icon: '💚' },
  { value: 'alipay', label: '支付宝', icon: '💙' },
  { value: 'unionpay', label: '银联支付', icon: '💳' },
]
