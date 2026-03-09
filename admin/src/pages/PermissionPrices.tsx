import React, { useEffect, useMemo, useState } from 'react'
import { SettingOutlined } from '@ant-design/icons'
import { adminApi } from '../api'
import { useI18n } from '../i18n'

type PriceMap = Record<string, { per_use: number; monthly: number; yearly: number }>

type PriceMode = 'per_use' | 'monthly' | 'yearly'

const defaultPrices: PriceMap = {
  script: { per_use: 1, monthly: 29, yearly: 199 },
  image: { per_use: 3, monthly: 99, yearly: 699 },
  video: { per_use: 5, monthly: 199, yearly: 1399 },
  ad: { per_use: 8, monthly: 299, yearly: 1999 },
}

const PermissionPrices: React.FC = () => {
  const [prices, setPrices] = useState<PriceMap>(defaultPrices)
  const [baselinePrices, setBaselinePrices] = useState<PriceMap>(defaultPrices)
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
        const data = await adminApi.getPermissionPrices()
        if (data) {
          setPrices(data)
          setBaselinePrices(data)
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
      await adminApi.updatePermissionPrices(prices)
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
        ...prices[type],
        [mode]: Number.parseFloat(value) || 0,
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

  const hasChanges = useMemo(
    () =>
      permissionTypes.some((type) => {
        const current = prices[type.key]
        const baseline = baselinePrices[type.key]
        return (
          current?.per_use !== baseline?.per_use ||
          current?.monthly !== baseline?.monthly ||
          current?.yearly !== baseline?.yearly
        )
      }),
    [baselinePrices, permissionTypes, prices]
  )

  const summary = useMemo(() => {
    const total = permissionTypes.length
    const monthlyAvg =
      permissionTypes.reduce((acc, type) => acc + (prices[type.key]?.monthly || 0), 0) / Math.max(1, total)
    const yearlyAvg =
      permissionTypes.reduce((acc, type) => acc + (prices[type.key]?.yearly || 0), 0) / Math.max(1, total)
    const maxPerUse = Math.max(...permissionTypes.map((type) => prices[type.key]?.per_use || 0))

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
          const price = prices[type.key] || { per_use: 0, monthly: 0, yearly: 0 }
          const yearlyEquivalent = price.yearly / 12
          const monthlyAnnualTotal = price.monthly * 12
          const yearlyDiscount =
            monthlyAnnualTotal > 0 ? ((monthlyAnnualTotal - price.yearly) / monthlyAnnualTotal) * 100 : 0

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
                <div>
                  <label className="admin-label">{t('permission.mode.perUse')}</label>
                  <div className="admin-pricing-input-wrap">
                    <span>{t('common.currency')}</span>
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      value={price.per_use}
                      onChange={(e) => handlePriceChange(type.key, 'per_use', e.target.value)}
                      className="admin-input w-full"
                    />
                  </div>
                </div>

                <div>
                  <label className="admin-label">{t('permission.mode.monthly')}</label>
                  <div className="admin-pricing-input-wrap">
                    <span>{t('common.currency')}</span>
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      value={price.monthly}
                      onChange={(e) => handlePriceChange(type.key, 'monthly', e.target.value)}
                      className="admin-input w-full"
                    />
                  </div>
                </div>

                <div>
                  <label className="admin-label">{t('permission.mode.yearly')}</label>
                  <div className="admin-pricing-input-wrap">
                    <span>{t('common.currency')}</span>
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      value={price.yearly}
                      onChange={(e) => handlePriceChange(type.key, 'yearly', e.target.value)}
                      className="admin-input w-full"
                    />
                  </div>
                </div>
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
