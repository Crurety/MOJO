import React, { useEffect, useMemo, useState } from 'react'
import {
  AlipayCircleOutlined,
  CheckOutlined,
  CreditCardOutlined,
  DollarOutlined,
  FileTextOutlined,
  NotificationOutlined,
  PictureOutlined,
  VideoCameraOutlined,
  WalletOutlined,
  WechatOutlined,
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import { paymentApi } from '../api'
import { Button } from '../components'
import {
  useAuth,
  usePayment,
  PAYMENT_METHODS,
  PRICING_PLANS,
  type PermissionPrices,
} from '../hooks'
import { useI18n } from '../i18n'
import { toLocalizedAmount } from '../utils/currency'

type PaymentMode = 'per_use' | 'monthly' | 'yearly'
type PlanKey = keyof typeof PRICING_PLANS

const modeList: PaymentMode[] = ['per_use', 'monthly', 'yearly']

const planIcons: Record<PlanKey, React.ReactNode> = {
  script: <FileTextOutlined />,
  image: <PictureOutlined />,
  video: <VideoCameraOutlined />,
  ad: <NotificationOutlined />,
}

const paymentIcons: Record<string, React.ReactNode> = {
  balance: <WalletOutlined />,
  wechat: <WechatOutlined />,
  alipay: <AlipayCircleOutlined />,
  unionpay: <CreditCardOutlined />,
}

const cloneDefaultPrices = (): PermissionPrices => ({
  script: { ...PRICING_PLANS.script },
  image: { ...PRICING_PLANS.image },
  video: { ...PRICING_PLANS.video },
  ad: { ...PRICING_PLANS.ad },
})

const parsePermissionPrices = (raw: unknown): PermissionPrices | null => {
  if (!raw || typeof raw !== 'object') {
    return null
  }

  const source = raw as Record<string, unknown>
  const plans: PlanKey[] = ['script', 'image', 'video', 'ad']
  const modes: PaymentMode[] = ['per_use', 'monthly', 'yearly']

  const result = cloneDefaultPrices()

  for (const plan of plans) {
    const modeValues = source[plan]
    if (!modeValues || typeof modeValues !== 'object') {
      return null
    }

    for (const mode of modes) {
      const value = (modeValues as Record<string, unknown>)[mode]
      if (typeof value !== 'number' || Number.isNaN(value) || value < 0) {
        return null
      }
      result[plan][mode] = value
    }
  }

  return result
}

const Pricing: React.FC = () => {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuth()
  const { createPermissionOrder, loading } = usePayment()
  const { language, t } = useI18n()

  const [pricePlans, setPricePlans] = useState<PermissionPrices>(cloneDefaultPrices)
  const [selectedPlan, setSelectedPlan] = useState<PlanKey | null>(null)
  const [selectedMode, setSelectedMode] = useState<PaymentMode>('per_use')
  const [selectedMethod, setSelectedMethod] = useState<string>('wechat')
  const [showPaymentModal, setShowPaymentModal] = useState(false)

  useEffect(() => {
    let active = true

    const loadPermissionPrices = async () => {
      try {
        const response = await paymentApi.getPermissionPrices()
        const parsed = parsePermissionPrices(response)
        if (active && parsed) {
          setPricePlans(parsed)
        }
      } catch (error) {
        console.error('Failed to load permission prices:', error)
      }
    }

    void loadPermissionPrices()

    return () => {
      active = false
    }
  }, [])

  const planEntries = useMemo(
    () => Object.entries(pricePlans) as [PlanKey, PermissionPrices[PlanKey]][],
    [pricePlans]
  )

  const getPrice = (plan: PlanKey, mode: PaymentMode) =>
    toLocalizedAmount(pricePlans[plan][mode], language, { zhFractionDigits: 0, enFractionDigits: 2 })
  const getPlanName = (plan: PlanKey) => t(`pricing.planName.${plan}`)
  const getPlanDescription = (plan: PlanKey) => t(`pricing.planDesc.${plan}`)
  const getPlanTag = (plan: PlanKey) => t(`pricing.planTag.${plan}`) || t('pricing.planTag.default')
  const getPlanHighlights = (plan: PlanKey) => [t(`pricing.planHighlight.${plan}.1`), t(`pricing.planHighlight.${plan}.2`)]

  const handleSelectPlan = (plan: PlanKey) => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }

    setSelectedPlan(plan)
    setShowPaymentModal(true)
  }

  const handlePayment = async () => {
    if (!selectedPlan) return

    const result = await createPermissionOrder({
      permission_type: selectedPlan,
      payment_mode: selectedMode,
      payment_method: selectedMethod,
    })

    if (result.success) {
      const payUrl = (result.data as { pay_url?: string }).pay_url
      if (payUrl) window.open(payUrl, '_blank')
      setShowPaymentModal(false)
      navigate('/tasks')
    }
  }

  return (
    <div className="space-y-9 text-[#e8f4ff]">
      <section className="section-shell relative overflow-hidden border border-[rgba(132,179,219,0.3)] px-6 py-8 sm:px-10 sm:py-10">
        <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(110deg,rgba(96,226,255,0.15),transparent_42%,rgba(80,141,255,0.12)_78%,transparent)]" />

        <div className="relative">
          <span className="inline-flex border border-[rgba(151,232,255,0.52)] bg-[rgba(11,36,56,0.86)] px-3 py-1 text-xs font-bold tracking-[0.14em] text-[#c7eeff]">
            {t('pricing.badge')}
          </span>
          <h1 className="mt-4 text-3xl font-bold text-[#f2fbff] sm:text-4xl">{t('pricing.title')}</h1>
          <p className="mt-3 max-w-3xl text-base leading-7 text-[#96b5cf]">{t('pricing.subtitle')}</p>

          <div className="mt-6 flex flex-wrap gap-3">
            {modeList.map((mode) => (
              <button
                key={mode}
                type="button"
                className={`border px-5 py-2.5 text-sm font-semibold transition ${
                  selectedMode === mode
                    ? 'border-[rgba(151,232,255,0.6)] bg-[rgba(12,58,81,0.92)] text-[#eff9ff]'
                    : 'border-[rgba(132,179,219,0.3)] bg-[rgba(6,18,34,0.8)] text-[#9eb8cf] hover:border-[rgba(151,232,255,0.52)] hover:text-[#dff4ff]'
                }`}
                onClick={() => setSelectedMode(mode)}
              >
                {t(`pricing.mode.${mode}`)}
              </button>
            ))}
          </div>
        </div>
      </section>

      <section className="stagger-grid grid grid-cols-1 gap-4 lg:grid-cols-2 xl:grid-cols-4">
        {planEntries.map(([key]) => {
          const isSelected = selectedPlan === key
          const highlights = getPlanHighlights(key)

          return (
            <div
              key={key}
              className={`flex h-full flex-col border px-6 py-6 transition ${
                isSelected
                  ? 'border-[rgba(151,232,255,0.65)] bg-[rgba(9,34,52,0.86)]'
                  : 'border-[rgba(132,179,219,0.25)] bg-[rgba(6,18,34,0.66)] hover:border-[rgba(151,232,255,0.42)] hover:bg-[rgba(8,28,46,0.82)]'
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-xs font-bold uppercase tracking-[0.18em] text-[#7ea8cd]">{getPlanTag(key)}</p>
                  <h2 className="mt-2 text-2xl font-bold text-[#f2fbff]">{getPlanName(key)}</h2>
                </div>
                <span className="inline-flex h-10 w-10 items-center justify-center border border-[rgba(151,232,255,0.46)] bg-[rgba(10,37,58,0.9)] text-base text-[#b2edff]">
                  {planIcons[key] || <DollarOutlined />}
                </span>
              </div>

              <div className="mt-5 flex items-baseline gap-1 border-y border-[rgba(132,179,219,0.22)] py-4">
                <span className="text-sm font-medium text-[#90acc6]">{t('common.currency')}</span>
                <span className="text-4xl font-bold text-[#f2fbff]">{getPrice(key, selectedMode)}</span>
                <span className="text-sm font-medium text-[#90acc6]">{t(`pricing.modeSuffix.${selectedMode}`)}</span>
              </div>

              <p className="mt-4 min-h-[48px] text-sm leading-6 text-[#96b5cf]">{getPlanDescription(key)}</p>

              <div className="mt-4 space-y-2 text-sm text-[#96b5cf]">
                {highlights.map((line) => (
                  <p key={line} className="flex items-center gap-2">
                    <span className="inline-flex h-5 w-5 items-center justify-center border border-[rgba(151,232,255,0.48)] bg-[rgba(10,37,58,0.86)] text-[10px] text-[#b2edff]">
                      <CheckOutlined />
                    </span>
                    {line}
                  </p>
                ))}
              </div>

              <div className="mt-6">
                <Button
                  onClick={() => handleSelectPlan(key)}
                  className="w-full py-2.5"
                  variant={isSelected ? 'primary' : 'secondary'}
                >
                  {selectedMode === 'per_use' ? t('pricing.buyNow') : t('pricing.subscribeNow')}
                </Button>
              </div>
            </div>
          )
        })}
      </section>

      {showPaymentModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
          <button
            type="button"
            className="absolute inset-0 bg-[rgba(2,7,14,0.72)] backdrop-blur-sm"
            onClick={() => setShowPaymentModal(false)}
            aria-label={t('pricing.modal.close')}
          />

          <div className="page-enter relative z-10 w-full max-w-lg border border-[rgba(132,179,219,0.35)] bg-[rgba(4,14,28,0.96)] p-6">
            <h3 className="text-2xl font-bold text-[#f2fbff]">{t('pricing.modal.title')}</h3>
            <p className="mt-1 text-sm text-[#96b5cf]">
              {t('pricing.modal.currentPlan', {
                plan: selectedPlan ? getPlanName(selectedPlan) : '-',
                mode: t(`pricing.mode.${selectedMode}`),
              })}
            </p>

            <div className="mt-5 space-y-3">
              {PAYMENT_METHODS.map((method) => (
                <button
                  key={method.value}
                  type="button"
                  onClick={() => setSelectedMethod(method.value)}
                  className={`flex w-full items-center justify-between border px-4 py-3 text-left transition ${
                    selectedMethod === method.value
                      ? 'border-[rgba(151,232,255,0.58)] bg-[rgba(9,34,52,0.86)]'
                      : 'border-[rgba(132,179,219,0.28)] bg-[rgba(6,18,34,0.8)] hover:border-[rgba(151,232,255,0.42)]'
                  }`}
                >
                  <span className="flex items-center gap-3">
                    <span className="inline-flex h-8 w-8 items-center justify-center border border-[rgba(151,232,255,0.42)] bg-[rgba(10,37,58,0.9)] text-sm text-[#b2edff]">
                      {paymentIcons[method.value] || <WalletOutlined />}
                    </span>
                    <span className="font-medium text-[#e8f4ff]">{t(`pricing.payment.${method.value}`)}</span>
                  </span>
                  {selectedMethod === method.value && (
                    <span className="border border-[rgba(151,232,255,0.58)] bg-[rgba(10,37,58,0.86)] px-2 py-0.5 text-xs font-bold text-[#d8f4ff]">
                      {t('pricing.modal.selected')}
                    </span>
                  )}
                </button>
              ))}
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <Button variant="secondary" onClick={() => setShowPaymentModal(false)} className="px-5 py-2.5">
                {t('common.cancel')}
              </Button>
              <Button onClick={handlePayment} loading={loading} className="px-6 py-2.5">
                {t('pricing.payment.confirm')}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Pricing
