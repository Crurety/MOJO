import { useState } from 'react'
import { paymentApi } from '../api'
import { translateStatic } from '../i18n'
import { resolveApiErrorMessage } from '../utils/apiError'

export type PermissionType = 'script' | 'image' | 'video' | 'ad'
export type PaymentMode = 'per_use' | 'monthly' | 'yearly'
export type PermissionPrices = Record<PermissionType, Record<PaymentMode, number>>

export const usePayment = () => {
  const [loading, setLoading] = useState(false)

  const createPermissionOrder = async (data: {
    permission_type: PermissionType
    payment_mode: PaymentMode
    payment_method: string
    count?: number
  }) => {
    setLoading(true)
    try {
      const response = await paymentApi.createOrder(data)
      return { success: true, data: response }
    } catch (error: any) {
      return { success: false, message: resolveApiErrorMessage(error, translateStatic('hook.payment.createOrderFailed')) }
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
      return { success: false, message: resolveApiErrorMessage(error, translateStatic('hook.payment.createOrderFailed')) }
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
      return { success: false, message: resolveApiErrorMessage(error, translateStatic('hook.payment.fetchOrderFailed')) }
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
      return {
        success: false,
        message: resolveApiErrorMessage(error, translateStatic('hook.payment.fetchOrderDetailFailed')),
      }
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
      return { success: false, message: resolveApiErrorMessage(error, translateStatic('hook.payment.payFailed')) }
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

export const DEFAULT_PERMISSION_PRICES: PermissionPrices = {
  script: {
    per_use: 1,
    monthly: 29,
    yearly: 199,
  },
  image: {
    per_use: 3,
    monthly: 99,
    yearly: 699,
  },
  video: {
    per_use: 5,
    monthly: 199,
    yearly: 1399,
  },
  ad: {
    per_use: 8,
    monthly: 299,
    yearly: 1999,
  },
}

// Backward-compatible alias for existing imports.
export const PRICING_PLANS = DEFAULT_PERMISSION_PRICES

export const PAYMENT_METHODS = [
  { value: 'balance' },
  { value: 'wechat' },
  { value: 'alipay' },
  { value: 'unionpay' },
] as const
