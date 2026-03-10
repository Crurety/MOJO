import React, { useEffect, useMemo, useState } from 'react'
import { SettingOutlined } from '@ant-design/icons'
import { adminApi } from '../api'
import { useI18n } from '../i18n'

type PriceNumbers = { per_use: number; monthly: number; yearly: number }
type PriceDraft = { per_use: string; monthly: string; yearly: string }
type PriceMapNumbers = Record<string, PriceNumbers>
type PriceMapDraft = Record<string, PriceDraft>

type PriceMode = 'per_use' | 'monthly' | 'yearly'

const defaultPrices: PriceMapNumbers = {
  script: { per_use: 1, monthly: 29, yearly: 199 },
  image: { per_use: 3, monthly: 99, yearly: 699 },
  video: { per_use: 5, monthly: 199, yearly: 1399 },
  ad: { per_use: 8, monthly: 299, yearly: 1999 },
}

const toDraft = (prices: PriceMapNumbers): PriceMapDraft =>
  Object.fromEntries(
    Object.entries(prices).map(([key, value]) => [
      key,
      {
        per_use: String(value?.per_use ?? 0),
        monthly: String(value?.monthly ?? 0),
        yearly: String(value?.yearly ?? 0),
      },
    ])
  )

const parseDraftNumber = (value: string): number | null => {
  const trimmed = value.trim()
  if (trimmed === '') return 0
  const numeric = Number(trimmed)
  if (!Number.isFinite(numeric)) return null
  if (numeric < 0) return null
  return numeric
}

const PermissionPrices: React.FC = () => {
  const [prices, setPrices] = useState<PriceMapDraft>(() => toDraft(defaultPrices))
  const [baselinePrices, setBaselinePrices] = useState<PriceMapDraft>(() => toDraft(defaultPrices))
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState('')
  const { t, language } = useI18n()

  useEffect(() => {
    const loadPrices = async () => {
      setLoading(true)
      setError('')
      try {
        const data = (await adminApi.getPermissionPrices()) as PriceMapNumbers | null
        if (data && typeof data === 'object') {
          const draft = toDraft(data)
          setPrices(draft)
          setBaselinePrices(draft)
        }
      } catch (requestError) {
        console.error('Failed to load permission prices:', requestError)
        setError(language === 'zh' ? '加载权限价格失败，请稍后重试。' : 'Failed to load permission prices. Please try again.')
      } finally {
        setLoading(false)
      }
    }

    void loadPrices()
  }, [language])

  const handleSave = async () => {
    setSaving(true)
    setSuccess(false)
    setError('')
    try {
      const payload: PriceMapNumbers = {}
      for (const [key, value] of Object.entries(prices)) {
        const perUse = parseDraftNumber(value.per_use)
        const monthly = parseDraftNumber(value.monthly)
        const yearly = parseDraftNumber(value.yearly)
        if (perUse === null || monthly === null || yearly === null) {
          setError(
            language === 'zh'
              ? '请输入有效的非负数字后再保存。'
              : 'Please enter a valid non-negative number before saving.'
          )
          return
        }
        payload[key] = { per_use: perUse, monthly, yearly }
      }

      await adminApi.updatePermissionPrices(payload)
      setBaselinePrices(prices)
      setSuccess(true)
      setTimeout(() => setSuccess(false), 2500)
    } catch (requestError) {
      console.error('Failed to update permission prices:', requestError)
      setError(language === 'zh' ? '保存失败，请检查输入后重试。' : 'Save failed. Please review fields and retry.')
    } finally {
      setSaving(false)
    }
  }

  const handleReset = () => {
    setPrices(baselinePrices)
    setSuccess(false)
    setError('')
  }

  const handlePriceChange = (type: string, mode: PriceMode, value: string) => {
    setPrices({
      ...prices,
      [type]: {
        ...(prices[type] ?? { per_use: '0', monthly: '0', yearly: '0' }),
        [mode]: value,
      },
    })
  }

  const permissionTypes = useMemo(
    () => [
      {
        key: 'script',
        name: t('permission.type.script'),
        description: language === 'zh' ? '脚本生成与改写能力' : 'Script generation and rewriting',
      },
      {
        key: 'image',
        name: t('permission.type.image'),
        description: language === 'zh' ? '图片创作与编辑能力' : 'Image generation and editing',
      },
      {
        key: 'video',
        name: t('permission.type.video'),
        description: language === 'zh' ? '视频生成能力与渲染资源' : 'Video generation and rendering resources',
      },
      {
        key: 'ad',
        name: t('permission.type.ad'),
        description: language === 'zh' ? '广告创意与投放素材能力' : 'Ad creative and marketing asset capability',
      },
    ],
    [language, t]
  )

  const priceModes = useMemo(
    () => [
      { key: 'per_use' as const, label: t('permission.mode.perUse') },
      { key: 'monthly' as const, label: t('permission.mode.monthly') },
      { key: 'yearly' as const, label: t('permission.mode.yearly') },
    ],
    [t]
  )

  const hasChanges = useMemo(
    () =>
      permissionTypes.some((type) => {
        const current = prices[type.key]
        const baseline = baselinePrices[type.key]
        const currentPerUse = parseDraftNumber(current?.per_use ?? '') ?? 0
        const currentMonthly = parseDraftNumber(current?.monthly ?? '') ?? 0
        const currentYearly = parseDraftNumber(current?.yearly ?? '') ?? 0
        const baselinePerUse = parseDraftNumber(baseline?.per_use ?? '') ?? 0
        const baselineMonthly = parseDraftNumber(baseline?.monthly ?? '') ?? 0
        const baselineYearly = parseDraftNumber(baseline?.yearly ?? '') ?? 0
        return (
          currentPerUse !== baselinePerUse ||
          currentMonthly !== baselineMonthly ||
          currentYearly !== baselineYearly
        )
      }),
    [baselinePrices, permissionTypes, prices]
  )

  const summary = useMemo(() => {
    const total = permissionTypes.length
    const monthlyAvg =
      permissionTypes.reduce((acc, type) => acc + (parseDraftNumber(prices[type.key]?.monthly ?? '') ?? 0), 0) /
      Math.max(1, total)
    const yearlyAvg =
      permissionTypes.reduce((acc, type) => acc + (parseDraftNumber(prices[type.key]?.yearly ?? '') ?? 0), 0) /
      Math.max(1, total)
    const maxPerUse = Math.max(...permissionTypes.map((type) => parseDraftNumber(prices[type.key]?.per_use ?? '') ?? 0))

    return {
      total,
      monthlyAvg,
      yearlyAvg,
      maxPerUse,
    }
  }, [permissionTypes, prices])

  if (loading) {
    return (
      <div className="admin-loader">
        <div className="admin-loader-spinner"></div>
        <p className="admin-loader-text">{t('common.loading')}</p>
      </div>
    )
  }

  return (
    <section className="admin-page admin-pricing-page space-y-4">
      <div className="admin-page-head">
        <div>
          <h1 className="admin-page-title">{t('permission.title')}</h1>
          <p className="admin-page-subtitle">
            {language === 'zh'
              ? '统一维护能力套餐价格，支持按次、月度与年度三种计费模式。'
              : 'Maintain pricing across per-use, monthly, and yearly billing modes in one workspace.'}
          </p>
        </div>
      </div>

      {success && <div className="admin-alert is-success">{t('permission.saveSuccess')}</div>}
      {error && <div className="admin-alert is-error">{error}</div>}

      <section className="admin-pricing-summary-grid">
        <article className="admin-pricing-summary-card">
          <p className="admin-pricing-summary-label">{language === 'zh' ? '配置能力数' : 'Configured Capabilities'}</p>
          <p className="admin-pricing-summary-value">{summary.total}</p>
        </article>
        <article className="admin-pricing-summary-card">
          <p className="admin-pricing-summary-label">{language === 'zh' ? '月度均价' : 'Average Monthly Price'}</p>
          <p className="admin-pricing-summary-value">
            {t('common.currency')}
            {summary.monthlyAvg.toFixed(2)}
          </p>
        </article>
        <article className="admin-pricing-summary-card">
          <p className="admin-pricing-summary-label">{language === 'zh' ? '年度均价' : 'Average Yearly Price'}</p>
          <p className="admin-pricing-summary-value">
            {t('common.currency')}
            {summary.yearlyAvg.toFixed(2)}
          </p>
        </article>
        <article className="admin-pricing-summary-card">
          <p className="admin-pricing-summary-label">{language === 'zh' ? '最高按次价格' : 'Highest Per-use Price'}</p>
          <p className="admin-pricing-summary-value">
            {t('common.currency')}
            {summary.maxPerUse.toFixed(2)}
          </p>
        </article>
      </section>

      <section className="admin-pricing-grid">
        {permissionTypes.map((type) => {
          const price = prices[type.key] || { per_use: '0', monthly: '0', yearly: '0' }
          const monthlyValue = parseDraftNumber(price.monthly) ?? 0
          const yearlyValue = parseDraftNumber(price.yearly) ?? 0
          const yearlyEquivalent = yearlyValue / 12
          const monthlyAnnualTotal = monthlyValue * 12
          const yearlyDiscount =
            monthlyAnnualTotal > 0 ? ((monthlyAnnualTotal - yearlyValue) / monthlyAnnualTotal) * 100 : 0

          return (
            <article key={type.key} className="admin-panel admin-pricing-card">
              <header className="admin-pricing-card-head">
                <div className="admin-pricing-card-title-wrap">
                  <span className="admin-pricing-card-icon">
                    <SettingOutlined />
                  </span>
                  <div>
                    <h2 className="admin-panel-title !mb-0">{type.name}</h2>
                    <p className="admin-pricing-card-subtitle">{type.description}</p>
                  </div>
                </div>
              </header>

              <div className="admin-pricing-input-grid">
                {priceModes.map((mode) => {
                  const fieldId = `${type.key}-${mode.key}`
                  return (
                    <div key={mode.key} className="admin-pricing-field">
                      <label htmlFor={fieldId} className="admin-label admin-pricing-field-label">
                        {mode.label}
                      </label>
                      <div className="admin-pricing-input-wrap">
                        <span className="admin-pricing-input-prefix">{t('common.currency')}</span>
                        <input
                          id={fieldId}
                          type="number"
                          min="0"
                          step="0.01"
                          inputMode="decimal"
                          value={price[mode.key]}
                          onChange={(e) => handlePriceChange(type.key, mode.key, e.target.value)}
                          className="admin-input admin-pricing-input"
                        />
                      </div>
                    </div>
                  )
                })}
              </div>

              <footer className="admin-pricing-card-foot">
                <p>
                  {language === 'zh' ? '年付折算月均：' : 'Yearly / month equivalent: '}
                  <strong>
                    {t('common.currency')}
                    {yearlyEquivalent.toFixed(2)}
                  </strong>
                </p>
                <p>
                  {language === 'zh' ? '年付相对月付优惠：' : 'Yearly discount vs monthly: '}
                  <strong>{yearlyDiscount > 0 ? `${yearlyDiscount.toFixed(1)}%` : '0%'}</strong>
                </p>
              </footer>
            </article>
          )
        })}
      </section>

      <section className="admin-panel admin-pricing-actions">
        <p className="admin-pricing-change-tip">
          {hasChanges
            ? language === 'zh'
              ? '检测到未保存变更。'
              : 'Unsaved changes detected.'
            : language === 'zh'
              ? '当前价格配置已同步。'
              : 'Pricing configuration is up to date.'}
        </p>

        <div className="admin-pricing-action-buttons">
          <button type="button" onClick={handleReset} disabled={saving || !hasChanges} className="admin-btn">
            {language === 'zh' ? '重置修改' : 'Reset Changes'}
          </button>
          <button
            type="button"
            onClick={() => void handleSave()}
            disabled={saving || !hasChanges}
            className="admin-btn admin-btn-primary"
          >
            {saving ? t('common.saving') : t('common.save')}
          </button>
        </div>
      </section>
    </section>
  )
}

export default PermissionPrices
