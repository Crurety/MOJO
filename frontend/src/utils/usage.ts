import type { Permission } from '../types/api'

export type CapabilityType = 'script' | 'image' | 'video' | 'ad'

type UsageCostInput = {
  taskType: CapabilityType
  clarity?: string
  duration?: number
  count?: number
  width?: number
  height?: number
}

type CapabilityAccessSummary = {
  hasPermission: boolean
  hasSubscription: boolean
  remainingCount: number
}

export const getCapabilityAccessSummary = (
  permissions: Permission[],
  permissionType: CapabilityType
): CapabilityAccessSummary => {
  const now = Date.now()
  const activePermissions = permissions.filter((permission) => {
    if (permission.permission_type !== permissionType || permission.status !== 1) {
      return false
    }

    if (permission.payment_mode === 'per_use') {
      return permission.total_count - permission.used_count > 0
    }

    if (!permission.expire_at) {
      return true
    }

    const expireAt = Date.parse(permission.expire_at)
    return Number.isNaN(expireAt) ? true : expireAt > now
  })

  const hasSubscription = activePermissions.some((permission) => permission.payment_mode !== 'per_use')
  const remainingCount = activePermissions
    .filter((permission) => permission.payment_mode === 'per_use')
    .reduce((sum, permission) => sum + Math.max(0, permission.total_count - permission.used_count), 0)

  return {
    hasPermission: hasSubscription || remainingCount > 0,
    hasSubscription,
    remainingCount,
  }
}

export const calculateUsageCost = ({
  taskType,
  clarity = '1080p',
  duration = 0,
  count = 1,
  width = 1920,
  height = 1080,
}: UsageCostInput): number => {
  const clarityWeights: Record<string, number> = {
    '720p': 1,
    '1080p': 1.5,
    '2k': 2,
    '4k': 2.5,
    '8k': 4,
  }

  const baseCosts: Record<CapabilityType, number> = {
    script: 1,
    image: 3,
    video: 5,
    ad: 8,
  }

  const getSizeWeight = (currentWidth: number, currentHeight: number) => {
    const pixels = currentWidth * currentHeight

    if (pixels <= 1280 * 720) return 1
    if (pixels <= 1920 * 1080) return 1.5
    if (pixels <= 2560 * 1440) return 2
    if (pixels <= 3840 * 2160) return 2.5
    return 4
  }

  const baseCost = baseCosts[taskType]
  const clarityWeight = clarityWeights[clarity] ?? 1

  if (taskType === 'video') {
    const durationWeight = Math.max(1, duration / 30)
    return Math.max(1, Math.trunc(baseCost * clarityWeight * durationWeight))
  }

  if (taskType === 'image') {
    const sizeWeight = getSizeWeight(width, height)
    return Math.max(1, Math.trunc(baseCost * clarityWeight * sizeWeight * count))
  }

  if (taskType === 'ad') {
    const complexityWeight = Math.max(1, count / 3)
    return Math.max(1, Math.trunc(baseCost * complexityWeight))
  }

  return Math.max(1, Math.trunc(baseCost * count))
}
