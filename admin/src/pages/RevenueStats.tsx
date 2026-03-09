import React, { useEffect, useMemo, useState } from 'react'
import {
  CalendarOutlined,
  DollarCircleOutlined,
  LineChartOutlined,
  ReloadOutlined,
  ShoppingCartOutlined,
} from '@ant-design/icons'
import { adminApi } from '../api'
import { useI18n } from '../i18n'

type RevenueStatsData = {
  total_revenue?: number
  total_orders?: number
}

type DateRange = {
  start: string
  end: string
}

const formatDate = (date: Date) => date.toISOString().split('T')[0]

const getDateRangeByDays = (days: number): DateRange => {
  const end = new Date()
  const start = new Date()
  start.setDate(end.getDate() - days + 1)
  return {
    start: formatDate(start),
    end: formatDate(end),
  }
}

const RevenueStats: React.FC = () => {
  const [stats, setStats] = useState<RevenueStatsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const { t, language } = useI18n()

  const [dateRange, setDateRange] = useState<DateRange>(() => getDateRangeByDays(30))
  const [activePreset, setActivePreset] = useState<number | null>(30)

  const loadStats = async (range: DateRange) => {
    setLoading(true)
    setError('')

    try {
      const data = await adminApi.getRevenueStats(range.start, range.end)
      setStats(data as RevenueStatsData)
    } catch (requestError) {
      console.error('Failed to load revenue stats:', requestError)
      setError(language === 'zh' ? '加载收入统计失败，请稍后重试。' : 'Failed to load revenue stats. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadStats(dateRange)
  }, [])

  const totalRevenue = stats?.total_revenue || 0
  const totalOrders = stats?.total_orders || 0
  const avgOrderAmount = totalOrders ? totalRevenue / totalOrders : 0

  const rangeDays = useMemo(() => {
    const start = new Date(dateRange.start)
    const end = new Date(dateRange.end)
    const diff = end.getTime() - start.getTime()
    if (Number.isNaN(diff) || diff < 0) return 1
    return Math.floor(diff / (1000 * 60 * 60 * 24)) + 1
  }, [dateRange.end, dateRange.start])

  const avgDailyRevenue = rangeDays ? totalRevenue / rangeDays : 0

  const summaryCards = [
    {
      key: 'totalRevenue',
      label: t('revenue.totalRevenue'),
      value: `${t('common.currency')}${totalRevenue.toFixed(2)}`,
      detail: language === 'zh' ? '所选时间段累计收入' : 'Accumulated revenue in selected range',
      icon: <DollarCircleOutlined />,
      accent: true,
    },
    {
      key: 'totalOrders',
      label: t('revenue.orderCount'),
      value: String(totalOrders),
      detail: language === 'zh' ? '支付成功订单数量' : 'Number of successful paid orders',
      icon: <ShoppingCartOutlined />,
    },
    {
      key: 'avgOrder',
      label: t('revenue.avgOrderAmount'),
      value: `${t('common.currency')}${avgOrderAmount.toFixed(2)}`,
      detail: language === 'zh' ? '每笔订单平均收入' : 'Average revenue per order',
      icon: <LineChartOutlined />,
    },
    {
      key: 'avgDaily',
      label: language === 'zh' ? '日均收入' : 'Daily Avg Revenue',
      value: `${t('common.currency')}${avgDailyRevenue.toFixed(2)}`,
      detail: language === 'zh' ? `${rangeDays} 天区间内日均值` : `Average over ${rangeDays} days`,
      icon: <CalendarOutlined />,
    },
  ]

  const quickRanges = [
    { key: 7, label: language === 'zh' ? '近 7 天' : '7D' },
    { key: 30, label: language === 'zh' ? '近 30 天' : '30D' },
    { key: 90, label: language === 'zh' ? '近 90 天' : '90D' },
  ]

  const handlePresetChange = (days: number) => {
    const nextRange = getDateRangeByDays(days)
    setActivePreset(days)
    setDateRange(nextRange)
    void loadStats(nextRange)
  }

  const handleQuery = () => {
    setActivePreset(null)
    void loadStats(dateRange)
  }

  if (loading) {
    return (
      <div className="admin-loader">
        <div className="admin-loader-spinner"></div>
        <p className="admin-loader-text">{t('common.loading')}</p>
      </div>
    )
  }

  return (
    <section className="admin-page admin-revenue-page space-y-4">
      <div className="admin-page-head">
        <div>
          <h1 className="admin-page-title">{t('revenue.title')}</h1>
          <p className="admin-page-subtitle">
            {language === 'zh'
              ? '按时间区间查看营收与订单表现，快速定位收入波动。'
              : 'Inspect revenue and order performance by date range to spot movement quickly.'}
          </p>
        </div>
      </div>

      {error && <div className="admin-alert is-error">{error}</div>}

      <section className="admin-panel admin-revenue-filter-panel">
        <div className="admin-revenue-filter-head">
          <h2 className="admin-panel-title !mb-0">{language === 'zh' ? '筛选区间' : 'Filter Range'}</h2>
          <button type="button" className="admin-btn" onClick={() => void loadStats(dateRange)}>
            <ReloadOutlined />
            <span>{language === 'zh' ? '刷新数据' : 'Refresh'}</span>
          </button>
        </div>

        <div className="admin-revenue-filter-body">
          <div className="admin-revenue-date-grid">
            <div>
              <label className="admin-label">{t('revenue.startDate')}</label>
              <input
                type="date"
                value={dateRange.start}
                onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
                className="admin-date w-full"
              />
            </div>
            <div>
              <label className="admin-label">{t('revenue.endDate')}</label>
              <input
                type="date"
                value={dateRange.end}
                onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
                className="admin-date w-full"
              />
            </div>
          </div>

          <div className="admin-revenue-quick-actions">
            <div className="admin-revenue-preset-group">
              {quickRanges.map((item) => (
                <button
                  key={item.key}
                  type="button"
                  className={`admin-btn ${activePreset === item.key ? 'admin-btn-primary' : ''}`}
                  onClick={() => handlePresetChange(item.key)}
                >
                  {item.label}
                </button>
              ))}
            </div>

            <button type="button" className="admin-btn admin-btn-primary" onClick={handleQuery}>
              {t('common.query')}
            </button>
          </div>
        </div>
      </section>

      <section className="admin-revenue-kpi-grid">
        {summaryCards.map((card) => (
          <article key={card.key} className={`admin-kpi-card ${card.accent ? 'is-accent-card' : ''}`}>
            <div className="admin-kpi-head">
              <p className="admin-kpi-label">{card.label}</p>
              <span className="admin-kpi-icon">{card.icon}</span>
            </div>
            <p className={`admin-kpi-value ${card.accent ? 'is-accent' : ''}`}>{card.value}</p>
            <p className="admin-revenue-kpi-detail">{card.detail}</p>
          </article>
        ))}
      </section>

      <section className="admin-revenue-grid">
        <article className="admin-panel">
          <h2 className="admin-panel-title">{t('revenue.revenueTrend')}</h2>
          <div className="admin-revenue-trend-visual" aria-hidden="true">
            {[28, 44, 39, 62, 51, 78, 66].map((height, index) => (
              <span key={height + index} style={{ height: `${height}%` }} />
            ))}
          </div>
          <p className="admin-revenue-panel-note">
            {language === 'zh'
              ? '接入明细统计后可展示真实日趋势图。'
              : 'Daily trend chart will display once detailed time-series data is connected.'}
          </p>
        </article>

        <article className="admin-panel">
          <h2 className="admin-panel-title">{t('revenue.source')}</h2>
          <div className="admin-revenue-source-list">
            <div className="admin-revenue-source-item">
              <span>{language === 'zh' ? '微信支付' : 'WeChat Pay'}</span>
              <strong>{language === 'zh' ? '待接入' : 'Pending'}</strong>
            </div>
            <div className="admin-revenue-source-item">
              <span>{language === 'zh' ? '支付宝' : 'Alipay'}</span>
              <strong>{language === 'zh' ? '待接入' : 'Pending'}</strong>
            </div>
            <div className="admin-revenue-source-item">
              <span>{language === 'zh' ? '余额支付' : 'Balance'}</span>
              <strong>{language === 'zh' ? '待接入' : 'Pending'}</strong>
            </div>
          </div>
          <p className="admin-revenue-panel-note">
            {language === 'zh'
              ? '当前后端仅返回总收入与订单数，渠道拆分可在后续版本补充。'
              : 'Backend currently returns total revenue and orders only; channel split can be added in a later iteration.'}
          </p>
        </article>
      </section>
    </section>
  )
}

export default RevenueStats
