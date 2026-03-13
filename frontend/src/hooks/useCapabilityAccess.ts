import { useCallback, useEffect, useState } from 'react'
import { message } from 'antd'
import { useLocation, useNavigate } from 'react-router-dom'
import { useI18n } from '../i18n'
import { getCapabilityAccessSummary, type CapabilityType } from '../utils/usage'
import { useBalance, usePermissions } from './useAuth'
import { usePayment } from './usePayment'

const buildRechargePath = (permissionType: CapabilityType, redirectTo: string) => {
  const params = new URLSearchParams()
  params.set('permission', permissionType)
  params.set('redirect', redirectTo)
  return `/account?${params.toString()}#recharge`
}

export const useCapabilityAccess = (permissionType: CapabilityType) => {
  const navigate = useNavigate()
  const location = useLocation()
  const { language } = useI18n()
  const { fetchBalance } = useBalance()
  const { fetchPermissions } = usePermissions()
  const { createPermissionOrder, payOrder, loading } = usePayment()
  const [isCheckingAccess, setIsCheckingAccess] = useState(true)

  const blockedMessage =
    language === 'zh'
      ? '当前余额和可用次数都不足，已为你跳转到充值页。'
      : 'Your balance and usage quota are exhausted. Redirecting you to the recharge page.'

  const balanceMessage =
    language === 'zh'
      ? '当前余额不足以支付本次使用，请先充值。'
      : 'Your balance is not enough to cover this usage. Please recharge first.'

  const redirectToRecharge = useCallback(
    (notice?: string) => {
      if (notice) {
        message.warning(notice)
      }

      const redirectTo = `${location.pathname}${location.search}${location.hash}`
      navigate(buildRechargePath(permissionType, redirectTo), { replace: true })
    },
    [location.hash, location.pathname, location.search, navigate, permissionType]
  )

  const refreshAccess = useCallback(async () => {
    const [currentBalance, permissionRows] = await Promise.all([fetchBalance(), fetchPermissions()])
    return {
      balance: currentBalance,
      summary: getCapabilityAccessSummary(permissionRows || [], permissionType),
    }
  }, [fetchBalance, fetchPermissions, permissionType])

  const ensureEntryAccess = useCallback(async () => {
    setIsCheckingAccess(true)
    try {
      const { balance, summary } = await refreshAccess()
      if (summary.hasPermission || balance > 0) {
        return true
      }

      redirectToRecharge(blockedMessage)
      return false
    } catch {
      return true
    } finally {
      setIsCheckingAccess(false)
    }
  }, [blockedMessage, redirectToRecharge, refreshAccess])

  useEffect(() => {
    void ensureEntryAccess()
  }, [ensureEntryAccess])

  const ensureUsageReady = useCallback(
    async (requiredCount = 1) => {
      let balance = 0
      let summary = {
        hasPermission: false,
        hasSubscription: false,
        remainingCount: 0,
      }

      try {
        const access = await refreshAccess()
        balance = access.balance
        summary = access.summary
      } catch {
        return true
      }

      if (summary.hasSubscription || summary.remainingCount >= requiredCount) {
        return true
      }

      if (balance <= 0) {
        redirectToRecharge(blockedMessage)
        return false
      }

      const missingCount = Math.max(0, requiredCount - summary.remainingCount)

      const created = await createPermissionOrder({
        permission_type: permissionType,
        payment_mode: 'per_use',
        payment_method: 'balance',
        count: missingCount,
      })
      if (!created.success || !created.data?.order_no) {
        redirectToRecharge(created.message || balanceMessage)
        return false
      }

      const paid = await payOrder(created.data.order_no)
      if (!paid.success) {
        redirectToRecharge(paid.message || balanceMessage)
        return false
      }

      await refreshAccess().catch(() => undefined)
      return true
    },
    [balanceMessage, blockedMessage, createPermissionOrder, payOrder, permissionType, redirectToRecharge, refreshAccess]
  )

  return {
    isCheckingAccess,
    isAutoPurchasing: loading,
    ensureUsageReady,
  }
}
