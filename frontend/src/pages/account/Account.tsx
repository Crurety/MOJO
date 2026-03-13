import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  ArrowRightOutlined,
  CalendarOutlined,
  CheckCircleOutlined,
  CopyOutlined,
  FileTextOutlined,
  MailOutlined,
  NotificationOutlined,
  PlayCircleOutlined,
  PhoneOutlined,
  PictureOutlined,
  ReloadOutlined,
  SafetyCertificateOutlined,
  ShoppingCartOutlined,
  UserOutlined,
  VideoCameraOutlined,
  WalletOutlined,
} from '@ant-design/icons'
import { InputNumber } from 'antd'
import { message } from 'antd'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Button, EmptyState, PageHeader, StatStrip, SurfaceCard } from '../../components'
import { paymentApi } from '../../api'
import {
  DEFAULT_PERMISSION_PRICES,
  PAYMENT_METHODS,
  type PaymentMode,
  type PermissionPrices,
  useAuth,
  useBalance,
  useContent,
  usePayment,
  usePermissions,
} from '../../hooks'
import { useI18n } from '../../i18n'
import { toLocalizedAmount } from '../../utils/currency'

type PermissionRecord = {
  id: number
  permission_type: 'script' | 'image' | 'video' | 'ad'
  payment_mode: 'per_use' | 'monthly' | 'yearly'
  total_count: number
  used_count: number
  expire_at?: string
  status: number
}

type CapabilityKey = PermissionRecord['permission_type']

type PermissionSummary = {
  type: CapabilityKey
  active: boolean
  hasSubscription: boolean
  remainingCount: number
  nearestExpireAt?: string
  modes: Array<PermissionRecord['payment_mode']>
}

type OrderRecord = {
  order_no: string
  order_type: 'balance' | 'permission'
  amount: number
  payment_method: string
  status: number
  product_name?: string
  created_at: string
  completed_at?: string
}

type TaskRecord = {
  id: number
  task_no: string
  task_type: CapabilityKey
  status: number
  progress: number
  result_url?: string
  error_message?: string
  cost_amount: number
  created_at: string
}

type WorkRecord = {
  id: number
  work_type: CapabilityKey
  title: string
  description?: string
  content_url: string
  thumbnail_url?: string
  created_at: string
}

const capabilityList: CapabilityKey[] = ['script', 'image', 'video', 'ad']

const capabilityLinks: Record<CapabilityKey, string> = {
  script: '/create/script',
  image: '/create/image',
  video: '/create/video',
  ad: '/create/ad',
}

const capabilityIcons: Record<CapabilityKey, JSX.Element> = {
  script: <FileTextOutlined />,
  image: <PictureOutlined />,
  video: <VideoCameraOutlined />,
  ad: <NotificationOutlined />,
}

const capabilityAccent: Record<CapabilityKey, string> = {
  script: 'from-[rgba(46,169,211,0.2)] to-transparent',
  image: 'from-[rgba(148,163,255,0.22)] to-transparent',
  video: 'from-[rgba(109,212,164,0.22)] to-transparent',
  ad: 'from-[rgba(255,166,102,0.22)] to-transparent',
}

const taskStatusTone: Record<number, string> = {
  0: 'border-[rgba(255,196,117,0.34)] bg-[rgba(64,39,15,0.72)] text-[#ffe5ba]',
  1: 'border-[rgba(151,232,255,0.34)] bg-[rgba(11,39,58,0.72)] text-[#d8f4ff]',
  2: 'border-[rgba(109,212,164,0.34)] bg-[rgba(20,59,46,0.72)] text-[#c9ffe2]',
  3: 'border-[rgba(255,148,148,0.34)] bg-[rgba(70,24,30,0.72)] text-[#ffd7d7]',
}

const Account = () => {
  const { t, language } = useI18n()
  const location = useLocation()
  const navigate = useNavigate()
  const { user, fetchCurrentUser, updateProfile } = useAuth()
  const { balance, fetchBalance } = useBalance()
  const { fetchPermissions } = usePermissions()
  const { createBalanceOrder, createPermissionOrder, fetchOrders, payOrder } = usePayment()
  const { fetchTasks, fetchWorks } = useContent()

  const [permissions, setPermissions] = useState<PermissionRecord[]>([])
  const [orders, setOrders] = useState<OrderRecord[]>([])
  const [tasks, setTasks] = useState<TaskRecord[]>([])
  const [works, setWorks] = useState<WorkRecord[]>([])
  const [pricePlans, setPricePlans] = useState<PermissionPrices>(DEFAULT_PERMISSION_PRICES)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [saving, setSaving] = useState(false)
  const [recharging, setRecharging] = useState(false)
  const [purchasingPlan, setPurchasingPlan] = useState<CapabilityKey | ''>('')
  const [payingOrderNo, setPayingOrderNo] = useState('')
  const [error, setError] = useState('')
  const [lastSyncedAt, setLastSyncedAt] = useState<string>('')
  const [formState, setFormState] = useState({ nickname: '', avatar: '' })
  const [rechargeAmount, setRechargeAmount] = useState<number>(100)
  const [selectedRechargeMethod, setSelectedRechargeMethod] = useState<string>('wechat')
  const [selectedPlanMode, setSelectedPlanMode] = useState<PaymentMode>('monthly')
  const [selectedPlanMethod, setSelectedPlanMethod] = useState<string>('wechat')

  const rechargeMethods = useMemo(
    () => PAYMENT_METHODS.filter((method) => method.value !== 'balance'),
    []
  )

  const formatDate = useCallback(
    (value?: string) => {
      if (!value) return '-'
      const date = new Date(value)
      if (Number.isNaN(date.getTime())) return '-'
      return date.toLocaleString(language === 'zh' ? 'zh-CN' : 'en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      })
    },
    [language]
  )

  const loadAccountData = useCallback(
    async (showToast = false) => {
      setError('')
      if (showToast) {
        setRefreshing(true)
      } else {
        setLoading(true)
      }

      try {
        const [currentUser, currentBalance, permissionRows] = await Promise.all([
          fetchCurrentUser(),
          fetchBalance(),
          fetchPermissions(),
        ])
        const orderResponse = await fetchOrders(0, 8)
        const [taskResponse, workResponse, priceResponse] = await Promise.all([
          fetchTasks(0, 4),
          fetchWorks(0, 4),
          paymentApi.getPermissionPrices().catch(() => DEFAULT_PERMISSION_PRICES),
        ])

        const nextPermissions = ((permissionRows || []) as PermissionRecord[]).filter(Boolean)
        setPermissions(nextPermissions)
        setOrders(((orderResponse?.success ? orderResponse.data : []) || []) as OrderRecord[])
        setTasks(((taskResponse?.success ? taskResponse.data : []) || []) as TaskRecord[])
        setWorks(((workResponse?.success ? workResponse.data : []) || []) as WorkRecord[])
        setPricePlans((priceResponse as PermissionPrices) || DEFAULT_PERMISSION_PRICES)

        if (currentUser) {
          setFormState({
            nickname: currentUser.nickname || '',
            avatar: currentUser.avatar || '',
          })
        }

        setLastSyncedAt(new Date().toISOString())

        if (showToast) {
          message.success(language === 'zh' ? '数据已刷新' : 'Account data refreshed')
        }

        return { currentUser, currentBalance, nextPermissions }
      } catch (requestError: any) {
        const detail =
          requestError?.response?.data?.detail ||
          requestError?.response?.data?.message ||
          (language === 'zh' ? '账户信息加载失败，请稍后重试。' : 'Failed to load account data. Please try again.')
        setError(String(detail))
        return null
      } finally {
        setLoading(false)
        setRefreshing(false)
      }
    },
    [fetchBalance, fetchCurrentUser, fetchOrders, fetchPermissions, fetchTasks, fetchWorks, language]
  )

  useEffect(() => {
    void loadAccountData()
  }, [loadAccountData])

  useEffect(() => {
    if (!user) return
    setFormState({
      nickname: user.nickname || '',
      avatar: user.avatar || '',
    })
  }, [user?.nickname, user?.avatar])

  useEffect(() => {
    if (location.hash !== '#recharge') {
      return
    }

    const timer = window.setTimeout(() => {
      document.getElementById('account-recharge-section')?.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      })
    }, 120)

    return () => window.clearTimeout(timer)
  }, [location.hash])

  const permissionSummaries = useMemo<PermissionSummary[]>(() => {
    const now = Date.now()

    return capabilityList.map((type) => {
      const rows = permissions.filter((permission) => permission.permission_type === type && permission.status === 1)
      const activeRows = rows.filter((permission) => {
        if (permission.payment_mode === 'per_use') {
          return permission.total_count - permission.used_count > 0
        }
        if (!permission.expire_at) return true
        const expireAt = Date.parse(permission.expire_at)
        return Number.isNaN(expireAt) ? true : expireAt > now
      })

      const hasSubscription = activeRows.some((permission) => permission.payment_mode !== 'per_use')
      const remainingCount = activeRows
        .filter((permission) => permission.payment_mode === 'per_use')
        .reduce((sum, permission) => sum + Math.max(0, permission.total_count - permission.used_count), 0)
      const nearestExpireAt = activeRows
        .filter((permission) => permission.payment_mode !== 'per_use' && permission.expire_at)
        .sort((a, b) => Date.parse(a.expire_at || '') - Date.parse(b.expire_at || ''))[0]?.expire_at

      return {
        type,
        active: hasSubscription || remainingCount > 0,
        hasSubscription,
        remainingCount,
        nearestExpireAt,
        modes: Array.from(new Set(activeRows.map((permission) => permission.payment_mode))),
      }
    })
  }, [permissions])

  const activeCapabilityCount = permissionSummaries.filter((item) => item.active).length
  const remainingQuota = permissionSummaries.reduce((sum, item) => sum + item.remainingCount, 0)
  const pendingOrdersCount = orders.filter((order) => order.status !== 1).length
  const totalSpend = orders.filter((order) => order.status === 1).reduce((sum, order) => sum + Number(order.amount || 0), 0)
  const totalWorks = works.length
  const completedTasks = tasks.filter((task) => task.status === 2).length

  const profileCompletion = useMemo(() => {
    const checkpoints = [
      Boolean(user?.nickname?.trim()),
      Boolean(user?.email?.trim() || user?.phone?.trim()),
      Boolean(user?.avatar?.trim()),
      Boolean(user?.created_at),
    ]
    const score = checkpoints.filter(Boolean).length / checkpoints.length
    return Math.round(score * 100)
  }, [user?.avatar, user?.created_at, user?.email, user?.nickname, user?.phone])

  const contactCoverage = useMemo(() => {
    const coverage = [Boolean(user?.email), Boolean(user?.phone)].filter(Boolean).length
    return `${coverage}/2`
  }, [user?.email, user?.phone])

  const stats = useMemo(
    () => [
      {
        label: t('layout.balance'),
        value: `${language === 'zh' ? '¥' : '$'}${toLocalizedAmount(balance || 0, language, { zhFractionDigits: 0, enFractionDigits: 2 })}`,
        hint: lastSyncedAt ? `${t('account.joined')} · ${formatDate(lastSyncedAt)}` : undefined,
      },
      {
        label: t('account.stats.activeAccess'),
        value: activeCapabilityCount,
        hint: capabilityList.length ? `${activeCapabilityCount}/${capabilityList.length}` : undefined,
      },
      {
        label: t('account.stats.remainingQuota'),
        value: remainingQuota,
        hint: language === 'zh' ? '仅统计按次权限剩余额度' : 'Pay-per-use quota only',
      },
      {
        label: t('account.stats.profileCompletion'),
        value: `${profileCompletion}%`,
        hint:
          pendingOrdersCount > 0
            ? `${t('account.orders.status.pending')} · ${pendingOrdersCount}`
            : `${t('account.stats.contactCoverage')} · ${contactCoverage}`,
      },
    ],
    [activeCapabilityCount, balance, contactCoverage, formatDate, language, lastSyncedAt, profileCompletion, remainingQuota, t]
  )

  const workbenchStats = useMemo(
    () => [
      {
        label: language === 'zh' ? '已完成任务' : 'Completed tasks',
        value: completedTasks,
        hint: language === 'zh' ? '最近 4 条任务快照' : 'From the latest 4 tasks',
      },
      {
        label: language === 'zh' ? '最近作品' : 'Recent works',
        value: totalWorks,
        hint: language === 'zh' ? '最新生成作品' : 'Latest generated works',
      },
      {
        label: language === 'zh' ? '累计实付' : 'Total paid',
        value: `${language === 'zh' ? '¥' : '$'}${toLocalizedAmount(totalSpend, language, { zhFractionDigits: 0, enFractionDigits: 2 })}`,
        hint: language === 'zh' ? '基于最近订单记录' : 'Based on recent orders',
      },
    ],
    [completedTasks, language, totalSpend, totalWorks]
  )

  const isDirty = useMemo(
    () => formState.nickname !== (user?.nickname || '') || formState.avatar !== (user?.avatar || ''),
    [formState.avatar, formState.nickname, user?.avatar, user?.nickname]
  )

  const displayName = user?.nickname || user?.email || user?.phone || t('layout.accountDefault')
  const avatarInitials = displayName.replace(/\s+/g, '').slice(0, 2).toUpperCase()
  const redirectAfterRecharge = useMemo(() => {
    const value = new URLSearchParams(location.search).get('redirect')
    return value && value.startsWith('/') ? value : ''
  }, [location.search])

  const handleCopy = async (value?: string) => {
    if (!value) return
    try {
      await navigator.clipboard.writeText(value)
      message.success(t('account.contact.copySuccess'))
    } catch {
      message.error(t('account.contact.copyFailed'))
    }
  }

  const handleSaveProfile = async () => {
    if (!formState.nickname.trim()) {
      message.error(t('account.profile.required'))
      return
    }

    setSaving(true)
    try {
      await updateProfile({
        nickname: formState.nickname.trim(),
        avatar: formState.avatar.trim() || undefined,
      })
      await loadAccountData()
      message.success(t('account.profile.saveSuccess'))
    } catch {
      message.error(t('account.profile.saveFailed'))
    } finally {
      setSaving(false)
    }
  }

  const handleRecharge = async () => {
    if (!rechargeAmount || rechargeAmount <= 0) {
      message.error(t('account.recharge.invalidAmount'))
      return
    }

    if (!selectedRechargeMethod) {
      message.error(t('account.recharge.methodRequired'))
      return
    }

    setRecharging(true)
    try {
      const created = await createBalanceOrder(rechargeAmount, selectedRechargeMethod)
      if (!created.success || !created.data?.order_no) {
        throw new Error(created.message || t('hook.payment.createOrderFailed'))
      }

      const paid = await payOrder(created.data.order_no)
      if (!paid.success) {
        throw new Error(paid.message || t('hook.payment.payFailed'))
      }

      await loadAccountData()
      message.success(t('account.recharge.success'))
      if (redirectAfterRecharge) {
        navigate(redirectAfterRecharge, { replace: true })
      }
    } catch (requestError: any) {
      message.error(requestError?.message || t('hook.payment.payFailed'))
    } finally {
      setRecharging(false)
    }
  }

  const handleOrderPayment = async (orderNo: string) => {
    setPayingOrderNo(orderNo)
    try {
      const paid = await payOrder(orderNo)
      if (!paid.success) {
        throw new Error(paid.message || t('hook.payment.payFailed'))
      }
      await loadAccountData()
      message.success(t('account.orders.paySuccess'))
    } catch (requestError: any) {
      message.error(requestError?.message || t('hook.payment.payFailed'))
    } finally {
      setPayingOrderNo('')
    }
  }

  const handlePlanPurchase = async (permissionType: CapabilityKey) => {
    setPurchasingPlan(permissionType)
    try {
      const created = await createPermissionOrder({
        permission_type: permissionType,
        payment_mode: selectedPlanMode,
        payment_method: selectedPlanMethod,
      })
      if (!created.success || !created.data?.order_no) {
        throw new Error(created.message || t('hook.payment.createOrderFailed'))
      }

      const paid = await payOrder(created.data.order_no)
      if (!paid.success) {
        throw new Error(paid.message || t('hook.payment.payFailed'))
      }
      await loadAccountData()
      message.success(t('account.orders.paySuccess'))
    } catch (requestError: any) {
      message.error(requestError?.message || t('hook.payment.createOrderFailed'))
    } finally {
      setPurchasingPlan('')
    }
  }

  const getTaskStatusLabel = (status: number) => {
    if (status === 0) return language === 'zh' ? '待处理' : 'Pending'
    if (status === 1) return language === 'zh' ? '进行中' : 'In progress'
    if (status === 2) return language === 'zh' ? '已完成' : 'Completed'
    return language === 'zh' ? '失败' : 'Failed'
  }

  const getPriceValue = (type: CapabilityKey, mode: PaymentMode) =>
    toLocalizedAmount(pricePlans[type]?.[mode] ?? DEFAULT_PERMISSION_PRICES[type][mode], language, {
      zhFractionDigits: 0,
      enFractionDigits: 2,
    })

  const resetProfile = () => {
    setFormState({
      nickname: user?.nickname || '',
      avatar: user?.avatar || '',
    })
  }

  if (loading && !user) {
    return (
      <div className="space-y-6 text-[#e8f4ff]">
        <div className="h-28 animate-pulse border border-[rgba(132,179,219,0.2)] bg-[rgba(6,18,34,0.6)]" />
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {Array.from({ length: 4 }).map((_, index) => (
            <div key={index} className="h-28 animate-pulse border border-[rgba(132,179,219,0.2)] bg-[rgba(6,18,34,0.6)]" />
          ))}
        </div>
        <div className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
          <div className="h-80 animate-pulse border border-[rgba(132,179,219,0.2)] bg-[rgba(6,18,34,0.6)]" />
          <div className="h-80 animate-pulse border border-[rgba(132,179,219,0.2)] bg-[rgba(6,18,34,0.6)]" />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 text-[#e8f4ff]">
      <PageHeader
        eyebrow={t('account.badge')}
        title={displayName}
        description={t('page.account.desc')}
        actions={
          <>
            <Button variant="ghost" onClick={() => void loadAccountData(true)} loading={refreshing}>
              <ReloadOutlined />
              {t('account.actions.refresh')}
            </Button>
            <Link to="/pricing">
              <Button variant="secondary">{t('account.actions.managePlans')}</Button>
            </Link>
          </>
        }
      />

      {error ? (
        <SurfaceCard>
          <EmptyState
            title={t('page.account.title')}
            description={error}
            action={
              <Button onClick={() => void loadAccountData(true)} loading={refreshing}>
                {t('account.actions.refresh')}
              </Button>
            }
          />
        </SurfaceCard>
      ) : null}

      <SurfaceCard className="overflow-hidden p-0">
        <div className="relative bg-[radial-gradient(circle_at_top_left,rgba(63,197,255,0.18),transparent_38%),linear-gradient(135deg,rgba(4,18,34,0.96),rgba(5,16,31,0.9))] px-5 py-6 sm:px-7 sm:py-7">
          <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[length:26px_26px] opacity-30" />
          <div className="relative grid gap-6 lg:grid-cols-[auto_1fr_auto] lg:items-center">
            <div className="flex items-center gap-4">
              {formState.avatar || user?.avatar ? (
                <img
                  src={formState.avatar || user?.avatar}
                  alt={displayName}
                  className="h-20 w-20 rounded-full border border-[rgba(151,232,255,0.36)] object-cover shadow-[0_0_24px_rgba(59,194,255,0.18)]"
                />
              ) : (
                <div className="flex h-20 w-20 items-center justify-center rounded-full border border-[rgba(151,232,255,0.36)] bg-[rgba(8,32,52,0.88)] text-2xl font-bold text-[#f2fbff] shadow-[0_0_24px_rgba(59,194,255,0.18)]">
                  {avatarInitials}
                </div>
              )}

              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <h2 className="text-2xl font-bold text-[#f8fbff] sm:text-3xl">{displayName}</h2>
                  <span
                    className={`inline-flex items-center gap-1 border px-2.5 py-1 text-xs font-semibold ${
                      user?.status === 1
                        ? 'border-[rgba(109,212,164,0.38)] bg-[rgba(20,59,46,0.72)] text-[#c9ffe2]'
                        : 'border-[rgba(255,148,148,0.34)] bg-[rgba(70,24,30,0.72)] text-[#ffd7d7]'
                    }`}
                  >
                    <SafetyCertificateOutlined />
                    {user?.status === 1 ? t('account.status.active') : t('account.status.inactive')}
                  </span>
                </div>

                <div className="mt-3 flex flex-wrap gap-3 text-sm text-[#a8c6de]">
                  <span className="inline-flex items-center gap-2">
                    <CalendarOutlined />
                    {t('account.joined')}: {formatDate(user?.created_at)}
                  </span>
                  <span className="inline-flex items-center gap-2">
                    <CheckCircleOutlined />
                    {t('account.stats.activeAccess')}: {activeCapabilityCount}
                  </span>
                </div>
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              <div className="border border-[rgba(132,179,219,0.18)] bg-[rgba(5,19,34,0.58)] px-4 py-3">
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#7ea8cd]">{t('layout.balance')}</p>
                <p className="mt-2 text-2xl font-bold text-[#f2fbff]">
                  {language === 'zh' ? '¥' : '$'}
                  {toLocalizedAmount(balance || 0, language, { zhFractionDigits: 0, enFractionDigits: 2 })}
                </p>
              </div>
              <div className="border border-[rgba(132,179,219,0.18)] bg-[rgba(5,19,34,0.58)] px-4 py-3">
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#7ea8cd]">{t('account.stats.remainingQuota')}</p>
                <p className="mt-2 text-2xl font-bold text-[#f2fbff]">{remainingQuota}</p>
              </div>
            </div>

            <div className="flex flex-wrap gap-3 lg:justify-end">
              <Link to="/tasks">
                <Button variant="secondary">{t('account.actions.goTasks')}</Button>
              </Link>
              <Link to="/pricing">
                <Button>{t('account.actions.managePlans')}</Button>
              </Link>
            </div>
          </div>
        </div>
      </SurfaceCard>

      <StatStrip items={stats} />

      <div className="grid gap-5 xl:grid-cols-[1.15fr_0.85fr]">
        <SurfaceCard title={t('account.profile.title')} subtitle={t('account.profile.subtitle')}>
          <div className="grid gap-5 lg:grid-cols-[140px_1fr]">
            <div>
              <p className="mb-3 text-xs font-semibold uppercase tracking-[0.16em] text-[#7ea8cd]">{t('account.profile.preview')}</p>
              {formState.avatar || user?.avatar ? (
                <img
                  src={formState.avatar || user?.avatar}
                  alt={displayName}
                  className="h-28 w-28 rounded-full border border-[rgba(132,179,219,0.22)] object-cover"
                />
              ) : (
                <div className="flex h-28 w-28 items-center justify-center rounded-full border border-[rgba(132,179,219,0.22)] bg-[rgba(6,18,34,0.82)] text-3xl font-bold text-[#f2fbff]">
                  {avatarInitials}
                </div>
              )}
            </div>

            <div className="space-y-4">
              <div>
                <label className="mb-2 block text-sm font-semibold text-[#d5ecff]">{t('account.profile.nickname')}</label>
                <input
                  value={formState.nickname}
                  onChange={(event) => setFormState((prev) => ({ ...prev, nickname: event.target.value }))}
                  placeholder={t('account.profile.nicknamePlaceholder')}
                  className="w-full border border-[rgba(132,179,219,0.24)] bg-[rgba(3,13,24,0.82)] px-4 py-3 text-[#f2fbff] outline-none transition placeholder:text-[#6f8ca7] focus:border-[rgba(151,232,255,0.52)]"
                />
              </div>

              <div>
                <label className="mb-2 block text-sm font-semibold text-[#d5ecff]">{t('account.profile.avatar')}</label>
                <input
                  value={formState.avatar}
                  onChange={(event) => setFormState((prev) => ({ ...prev, avatar: event.target.value }))}
                  placeholder={t('account.profile.avatarPlaceholder')}
                  className="w-full border border-[rgba(132,179,219,0.24)] bg-[rgba(3,13,24,0.82)] px-4 py-3 text-[#f2fbff] outline-none transition placeholder:text-[#6f8ca7] focus:border-[rgba(151,232,255,0.52)]"
                />
              </div>

              <div className="flex flex-wrap gap-3">
                <Button onClick={handleSaveProfile} loading={saving} disabled={!isDirty}>
                  {t('account.actions.saveProfile')}
                </Button>
                <Button variant="ghost" onClick={resetProfile} disabled={!isDirty || saving}>
                  {t('account.actions.resetProfile')}
                </Button>
              </div>
            </div>
          </div>
        </SurfaceCard>

        <SurfaceCard title={t('account.contact.title')} subtitle={t('account.contact.subtitle')}>
          <div className="space-y-3">
            {[
              { icon: <MailOutlined />, label: t('account.contact.email'), value: user?.email || t('account.contact.unset') },
              { icon: <PhoneOutlined />, label: t('account.contact.phone'), value: user?.phone || t('account.contact.unset') },
              { icon: <UserOutlined />, label: t('account.contact.userId'), value: user?.id ? String(user.id) : '-' },
            ].map((item) => (
              <div key={item.label} className="flex items-start justify-between gap-3 border border-[rgba(132,179,219,0.18)] bg-[rgba(5,19,34,0.58)] px-4 py-3">
                <div className="flex min-w-0 items-start gap-3">
                  <span className="mt-0.5 text-[#9ce9ff]">{item.icon}</span>
                  <div className="min-w-0">
                    <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#7ea8cd]">{item.label}</p>
                    <p className="mt-1 break-all text-sm leading-6 text-[#e8f4ff]">{item.value}</p>
                  </div>
                </div>
                {item.value !== t('account.contact.unset') && item.value !== '-' ? (
                  <button
                    type="button"
                    onClick={() => void handleCopy(item.value)}
                    className="inline-flex items-center gap-2 border border-[rgba(132,179,219,0.26)] bg-[rgba(8,24,40,0.78)] px-3 py-2 text-xs font-semibold text-[#d8f1ff] transition hover:border-[rgba(151,232,255,0.42)]"
                  >
                    <CopyOutlined />
                    {t('account.actions.copy')}
                  </button>
                ) : null}
              </div>
            ))}
          </div>

          <div className="mt-5 border-t border-[rgba(132,179,219,0.16)] pt-5">
            <p className="mb-3 text-xs font-semibold uppercase tracking-[0.16em] text-[#7ea8cd]">Quick Actions</p>
            <div className="grid gap-3 sm:grid-cols-2">
              <Link to="/pricing" className="group border border-[rgba(132,179,219,0.18)] bg-[rgba(5,19,34,0.58)] px-4 py-4 transition hover:border-[rgba(151,232,255,0.42)] hover:bg-[rgba(8,26,44,0.74)]">
                <p className="inline-flex items-center gap-2 text-sm font-semibold text-[#f2fbff]">
                  <WalletOutlined />
                  {t('account.actions.managePlans')}
                </p>
                <p className="mt-2 text-sm text-[#90afc9]">{t('account.permissions.locked')}</p>
              </Link>

              <Link to="/tasks" className="group border border-[rgba(132,179,219,0.18)] bg-[rgba(5,19,34,0.58)] px-4 py-4 transition hover:border-[rgba(151,232,255,0.42)] hover:bg-[rgba(8,26,44,0.74)]">
                <p className="inline-flex items-center gap-2 text-sm font-semibold text-[#f2fbff]">
                  <ReloadOutlined />
                  {t('account.actions.goTasks')}
                </p>
                <p className="mt-2 text-sm text-[#90afc9]">{language === 'zh' ? '跟踪生成进度与结果' : 'Track generation progress and results'}</p>
              </Link>
            </div>
          </div>
        </SurfaceCard>
      </div>

      <SurfaceCard title={t('account.permissions.title')} subtitle={t('account.permissions.subtitle')}>
        <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-4">
          {permissionSummaries.map((summary) => {
            const nextPath = summary.active ? capabilityLinks[summary.type] : '/pricing'

            return (
              <article
                key={summary.type}
                className="relative overflow-hidden border border-[rgba(132,179,219,0.2)] bg-[rgba(4,16,29,0.72)] p-5"
              >
                <div className={`pointer-events-none absolute inset-x-0 top-0 h-24 bg-gradient-to-br ${capabilityAccent[summary.type]} opacity-90`} />
                <div className="relative">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#7ea8cd]">{t(`pricing.planTag.${summary.type}`)}</p>
                      <h3 className="mt-2 text-xl font-semibold text-[#f2fbff]">{t(`pricing.planName.${summary.type}`)}</h3>
                    </div>
                    <span className="inline-flex h-10 w-10 items-center justify-center border border-[rgba(151,232,255,0.34)] bg-[rgba(7,28,44,0.86)] text-base text-[#c8f1ff]">
                      {capabilityIcons[summary.type]}
                    </span>
                  </div>

                  <div className="mt-4 flex flex-wrap gap-2">
                    <span
                      className={`inline-flex items-center gap-1 border px-2.5 py-1 text-xs font-semibold ${
                        summary.active
                          ? 'border-[rgba(109,212,164,0.38)] bg-[rgba(20,59,46,0.72)] text-[#c9ffe2]'
                          : 'border-[rgba(132,179,219,0.26)] bg-[rgba(7,26,44,0.72)] text-[#c8ddf0]'
                      }`}
                    >
                      {summary.active ? <CheckCircleOutlined /> : <SafetyCertificateOutlined />}
                      {summary.active ? t('account.permissions.status.active') : t('account.permissions.status.inactive')}
                    </span>

                    {summary.modes.map((mode) => (
                      <span key={mode} className="inline-flex border border-[rgba(132,179,219,0.24)] bg-[rgba(7,26,44,0.68)] px-2.5 py-1 text-xs font-semibold text-[#c8ddf0]">
                        {t(`pricing.mode.${mode}`)}
                      </span>
                    ))}
                  </div>

                  <div className="mt-5 space-y-3 text-sm text-[#9bbad3]">
                    <div className="flex items-center justify-between gap-3 border-b border-[rgba(132,179,219,0.12)] pb-3">
                      <span>{summary.hasSubscription ? t('account.permissions.subscription') : t('account.permissions.remaining')}</span>
                      <span className="font-semibold text-[#f2fbff]">
                        {summary.hasSubscription ? t('account.permissions.subscription') : summary.remainingCount}
                      </span>
                    </div>
                    <div className="flex items-center justify-between gap-3">
                      <span>{t('account.permissions.expire')}</span>
                      <span className="text-right font-semibold text-[#f2fbff]">
                        {summary.nearestExpireAt ? formatDate(summary.nearestExpireAt) : t('account.permissions.never')}
                      </span>
                    </div>
                  </div>

                  <p className="mt-4 min-h-[48px] text-sm leading-6 text-[#8fb1cc]">
                    {summary.active ? t('account.permissions.ready') : t('account.permissions.locked')}
                  </p>

                  <div className="mt-5">
                    <Link to={nextPath}>
                      <Button variant={summary.active ? 'primary' : 'secondary'} className="w-full justify-center">
                        {summary.active ? t('account.actions.startNow') : t('account.actions.unlockNow')}
                        <ArrowRightOutlined />
                      </Button>
                    </Link>
                  </div>
                </div>
              </article>
            )
          })}
        </div>

        {activeCapabilityCount === 0 ? (
          <div className="mt-6">
            <EmptyState
              title={t('account.permissions.noneTitle')}
              description={t('account.permissions.noneDesc')}
              action={
                <Link to="/pricing">
                  <Button>{t('account.actions.managePlans')}</Button>
                </Link>
              }
            />
          </div>
        ) : null}
      </SurfaceCard>

      <div className="grid gap-5 xl:grid-cols-[0.85fr_1.15fr]">
        <div id="account-recharge-section" className="scroll-mt-24">
          <SurfaceCard title={t('account.recharge.title')} subtitle={t('account.recharge.subtitle')}>
          <div className="space-y-5">
            <div>
              <p className="mb-3 text-xs font-semibold uppercase tracking-[0.16em] text-[#7ea8cd]">{t('account.recharge.amount')}</p>
              <div className="grid gap-3 sm:grid-cols-4">
                {[50, 100, 200, 500].map((amount) => (
                  <button
                    key={amount}
                    type="button"
                    onClick={() => setRechargeAmount(amount)}
                    className={`border px-4 py-3 text-left transition ${
                      rechargeAmount === amount
                        ? 'border-[rgba(151,232,255,0.52)] bg-[rgba(10,37,58,0.88)] text-[#f2fbff]'
                        : 'border-[rgba(132,179,219,0.22)] bg-[rgba(6,18,34,0.72)] text-[#b7d3ea] hover:border-[rgba(151,232,255,0.36)]'
                    }`}
                  >
                    <p className="text-xs uppercase tracking-[0.16em] text-[#7ea8cd]">Top Up</p>
                    <p className="mt-2 text-xl font-semibold">¥{amount}</p>
                  </button>
                ))}
              </div>
            </div>

            <div>
              <p className="mb-3 text-xs font-semibold uppercase tracking-[0.16em] text-[#7ea8cd]">{t('account.recharge.custom')}</p>
              <InputNumber<number>
                min={1}
                value={rechargeAmount}
                onChange={(value) => setRechargeAmount(Number(value || 0))}
                className="w-full"
                controls={false}
                formatter={(value) => `¥${value}`}
              />
            </div>

            <div>
              <p className="mb-3 text-xs font-semibold uppercase tracking-[0.16em] text-[#7ea8cd]">{t('account.recharge.method')}</p>
              <div className="grid gap-3 sm:grid-cols-3">
                {rechargeMethods.map((method) => (
                  <button
                    key={method.value}
                    type="button"
                    onClick={() => setSelectedRechargeMethod(method.value)}
                    className={`border px-4 py-3 text-left transition ${
                      selectedRechargeMethod === method.value
                        ? 'border-[rgba(151,232,255,0.52)] bg-[rgba(10,37,58,0.88)] text-[#f2fbff]'
                        : 'border-[rgba(132,179,219,0.22)] bg-[rgba(6,18,34,0.72)] text-[#b7d3ea] hover:border-[rgba(151,232,255,0.36)]'
                    }`}
                  >
                    <p className="font-semibold">{t(`pricing.payment.${method.value}`)}</p>
                    <p className="mt-1 text-xs text-[#8fb1cc]">{t('account.recharge.helper')}</p>
                  </button>
                ))}
              </div>
            </div>

            <div className="rounded border border-[rgba(132,179,219,0.18)] bg-[rgba(4,16,29,0.6)] px-4 py-3 text-sm leading-6 text-[#97b6cf]">
              {t('account.recharge.helper')}
            </div>

            <Button onClick={handleRecharge} loading={recharging} className="w-full justify-center">
              <WalletOutlined />
              {t('account.recharge.submit')}
            </Button>
          </div>
          </SurfaceCard>
        </div>

        <SurfaceCard title={t('account.orders.title')} subtitle={t('account.orders.subtitle')}>
          {orders.length === 0 ? (
            <EmptyState title={t('account.orders.emptyTitle')} description={t('account.orders.emptyDesc')} />
          ) : (
            <div className="space-y-3">
              {orders.map((order) => {
                const isPaid = order.status === 1
                return (
                  <article
                    key={order.order_no}
                    className="border border-[rgba(132,179,219,0.18)] bg-[rgba(5,19,34,0.6)] px-4 py-4"
                  >
                    <div className="flex flex-wrap items-start justify-between gap-4">
                      <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="text-sm font-semibold text-[#f2fbff]">
                            {t(`account.orders.type.${order.order_type}`)}
                          </span>
                          <span
                            className={`inline-flex border px-2 py-0.5 text-xs font-semibold ${
                              isPaid
                                ? 'border-[rgba(109,212,164,0.34)] bg-[rgba(20,59,46,0.72)] text-[#c9ffe2]'
                                : 'border-[rgba(255,196,117,0.34)] bg-[rgba(64,39,15,0.72)] text-[#ffe5ba]'
                            }`}
                          >
                            {isPaid ? t('account.orders.status.paid') : t('account.orders.status.pending')}
                          </span>
                        </div>

                        <div className="mt-3 grid gap-3 text-sm text-[#96b5cf] sm:grid-cols-3">
                          <div>
                            <p className="text-xs uppercase tracking-[0.16em] text-[#7ea8cd]">{t('account.orders.orderNo')}</p>
                            <p className="mt-1 break-all text-[#e8f4ff]">{order.order_no}</p>
                          </div>
                          <div>
                            <p className="text-xs uppercase tracking-[0.16em] text-[#7ea8cd]">{t('account.orders.amount')}</p>
                            <p className="mt-1 text-[#e8f4ff]">
                              {language === 'zh' ? '¥' : '$'}
                              {toLocalizedAmount(order.amount || 0, language, { zhFractionDigits: 0, enFractionDigits: 2 })}
                            </p>
                          </div>
                          <div>
                            <p className="text-xs uppercase tracking-[0.16em] text-[#7ea8cd]">{t('account.orders.createdAt')}</p>
                            <p className="mt-1 text-[#e8f4ff]">{formatDate(order.completed_at || order.created_at)}</p>
                          </div>
                        </div>

                        <p className="mt-3 text-sm text-[#88a9c6]">
                          {order.product_name || t(`pricing.payment.${order.payment_method}`)}
                        </p>
                      </div>

                      {!isPaid ? (
                        <Button
                          onClick={() => void handleOrderPayment(order.order_no)}
                          loading={payingOrderNo === order.order_no}
                          variant="secondary"
                        >
                          {payingOrderNo === order.order_no ? t('account.orders.paying') : t('account.orders.payNow')}
                        </Button>
                      ) : null}
                    </div>
                  </article>
                )
              })}
            </div>
          )}
        </SurfaceCard>
      </div>

      <SurfaceCard
        title={language === 'zh' ? '套餐快捷开通' : 'Quick plan purchase'}
        subtitle={language === 'zh' ? '无需离开账户页，直接选择周期和支付方式开通能力。' : 'Unlock capabilities directly from the account hub.'}
      >
        <div className="mb-5 flex flex-wrap gap-3">
          {(['per_use', 'monthly', 'yearly'] as PaymentMode[]).map((mode) => (
            <button
              key={mode}
              type="button"
              onClick={() => setSelectedPlanMode(mode)}
              className={`border px-4 py-2 text-sm font-semibold transition ${
                selectedPlanMode === mode
                  ? 'border-[rgba(151,232,255,0.52)] bg-[rgba(10,37,58,0.88)] text-[#f2fbff]'
                  : 'border-[rgba(132,179,219,0.22)] bg-[rgba(6,18,34,0.72)] text-[#b7d3ea] hover:border-[rgba(151,232,255,0.36)]'
              }`}
            >
              {t(`pricing.mode.${mode}`)}
            </button>
          ))}
        </div>

        <div className="mb-5 flex flex-wrap gap-3">
          {rechargeMethods.map((method) => (
            <button
              key={method.value}
              type="button"
              onClick={() => setSelectedPlanMethod(method.value)}
              className={`border px-4 py-2 text-sm font-semibold transition ${
                selectedPlanMethod === method.value
                  ? 'border-[rgba(151,232,255,0.52)] bg-[rgba(10,37,58,0.88)] text-[#f2fbff]'
                  : 'border-[rgba(132,179,219,0.22)] bg-[rgba(6,18,34,0.72)] text-[#b7d3ea] hover:border-[rgba(151,232,255,0.36)]'
              }`}
            >
              {t(`pricing.payment.${method.value}`)}
            </button>
          ))}
        </div>

        <div className="grid gap-4 lg:grid-cols-2 xl:grid-cols-4">
          {capabilityList.map((type) => (
            <article key={type} className="border border-[rgba(132,179,219,0.18)] bg-[rgba(4,16,29,0.72)] p-5">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#7ea8cd]">{t(`pricing.planTag.${type}`)}</p>
                  <h3 className="mt-2 text-lg font-semibold text-[#f2fbff]">{t(`pricing.planName.${type}`)}</h3>
                </div>
                <span className="inline-flex h-10 w-10 items-center justify-center border border-[rgba(151,232,255,0.34)] bg-[rgba(7,28,44,0.86)] text-base text-[#c8f1ff]">
                  {capabilityIcons[type]}
                </span>
              </div>

              <div className="mt-4 border-y border-[rgba(132,179,219,0.12)] py-4">
                <p className="text-xs uppercase tracking-[0.16em] text-[#7ea8cd]">{t(`pricing.mode.${selectedPlanMode}`)}</p>
                <p className="mt-2 text-3xl font-bold text-[#f2fbff]">
                  {language === 'zh' ? '¥' : '$'}
                  {getPriceValue(type, selectedPlanMode)}
                </p>
              </div>

              <p className="mt-4 min-h-[44px] text-sm leading-6 text-[#8fb1cc]">{t(`pricing.planDesc.${type}`)}</p>

              <Button
                onClick={() => void handlePlanPurchase(type)}
                loading={purchasingPlan === type}
                variant="secondary"
                className="mt-5 w-full justify-center"
              >
                <ShoppingCartOutlined />
                {language === 'zh' ? '立即开通' : 'Buy now'}
              </Button>
            </article>
          ))}
        </div>
      </SurfaceCard>

      <div className="grid gap-5 xl:grid-cols-[1fr_1fr]">
        <SurfaceCard
          title={language === 'zh' ? '最近任务' : 'Recent tasks'}
          subtitle={language === 'zh' ? '快速了解最近提交任务的处理状态和费用。' : 'Track the latest task statuses and estimated cost.'}
        >
          {tasks.length === 0 ? (
            <EmptyState
              title={language === 'zh' ? '还没有任务' : 'No tasks yet'}
              description={language === 'zh' ? '提交脚本、图片、视频或广告任务后，这里会显示最近记录。' : 'Your latest script, image, video, and ad tasks will appear here.'}
            />
          ) : (
            <div className="space-y-3">
              {tasks.map((task) => (
                <article key={task.task_no} className="border border-[rgba(132,179,219,0.18)] bg-[rgba(5,19,34,0.6)] px-4 py-4">
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-sm font-semibold text-[#f2fbff]">{t(`pricing.planName.${task.task_type}`)}</span>
                        <span className={`inline-flex border px-2 py-0.5 text-xs font-semibold ${taskStatusTone[task.status] || taskStatusTone[0]}`}>
                          {getTaskStatusLabel(task.status)}
                        </span>
                      </div>
                      <p className="mt-2 break-all text-sm text-[#8fb1cc]">{task.task_no}</p>
                      <div className="mt-3 grid gap-3 text-sm text-[#96b5cf] sm:grid-cols-3">
                        <div>
                          <p className="text-xs uppercase tracking-[0.16em] text-[#7ea8cd]">{language === 'zh' ? '进度' : 'Progress'}</p>
                          <p className="mt-1 text-[#e8f4ff]">{task.progress || 0}%</p>
                        </div>
                        <div>
                          <p className="text-xs uppercase tracking-[0.16em] text-[#7ea8cd]">{language === 'zh' ? '成本' : 'Cost'}</p>
                          <p className="mt-1 text-[#e8f4ff]">{task.cost_amount}</p>
                        </div>
                        <div>
                          <p className="text-xs uppercase tracking-[0.16em] text-[#7ea8cd]">{t('account.orders.createdAt')}</p>
                          <p className="mt-1 text-[#e8f4ff]">{formatDate(task.created_at)}</p>
                        </div>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-2">
                      {task.result_url ? (
                        <a href={task.result_url} target="_blank" rel="noreferrer">
                          <Button variant="secondary">
                            <PlayCircleOutlined />
                            {language === 'zh' ? '查看结果' : 'Open result'}
                          </Button>
                        </a>
                      ) : null}
                      <Link to="/tasks">
                        <Button variant="ghost">{t('account.actions.goTasks')}</Button>
                      </Link>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}
        </SurfaceCard>

        <SurfaceCard
          title={language === 'zh' ? '最近作品' : 'Recent works'}
          subtitle={language === 'zh' ? '快速打开最近生成的图片、视频和广告成品。' : 'Open your latest generated images, videos, and ad assets.'}
        >
          {works.length === 0 ? (
            <EmptyState
              title={language === 'zh' ? '还没有作品' : 'No works yet'}
              description={language === 'zh' ? '作品生成后会自动出现在这里，方便回看和继续编辑。' : 'Generated works appear here automatically for review and reuse.'}
            />
          ) : (
            <div className="grid gap-4 sm:grid-cols-2">
              {works.map((work) => {
                const previewUrl = work.thumbnail_url || work.content_url
                const isImage = /\.(png|jpe?g|webp|gif|svg)$/i.test(previewUrl || '')
                return (
                  <article key={work.id} className="overflow-hidden border border-[rgba(132,179,219,0.18)] bg-[rgba(5,19,34,0.6)]">
                    <div className="flex h-44 items-center justify-center border-b border-[rgba(132,179,219,0.12)] bg-[rgba(2,12,22,0.76)]">
                      {isImage ? (
                        <img src={previewUrl} alt={work.title} className="h-full w-full object-cover" />
                      ) : (
                        <div className="flex flex-col items-center gap-3 text-[#c8e9ff]">
                          <span className="inline-flex h-14 w-14 items-center justify-center rounded-full border border-[rgba(151,232,255,0.34)] bg-[rgba(7,28,44,0.86)] text-xl">
                            {capabilityIcons[work.work_type]}
                          </span>
                          <p className="text-sm text-[#8fb1cc]">{language === 'zh' ? '可在新标签页打开作品' : 'Open in a new tab'}</p>
                        </div>
                      )}
                    </div>
                    <div className="p-4">
                      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#7ea8cd]">{t(`pricing.planTag.${work.work_type}`)}</p>
                      <h3 className="mt-2 text-lg font-semibold text-[#f2fbff]">{work.title || t(`pricing.planName.${work.work_type}`)}</h3>
                      <p className="mt-2 text-sm text-[#8fb1cc]">{formatDate(work.created_at)}</p>
                      <div className="mt-4 flex gap-2">
                        <a href={work.content_url} target="_blank" rel="noreferrer" className="flex-1">
                          <Button variant="secondary" className="w-full justify-center">
                            <PlayCircleOutlined />
                            {language === 'zh' ? '打开作品' : 'Open work'}
                          </Button>
                        </a>
                        <Link to="/works" className="flex-1">
                          <Button variant="ghost" className="w-full justify-center">
                            {language === 'zh' ? '作品库' : 'Library'}
                          </Button>
                        </Link>
                      </div>
                    </div>
                  </article>
                )
              })}
            </div>
          )}
        </SurfaceCard>
      </div>

      <StatStrip items={workbenchStats} />
    </div>
  )
}

export default Account
