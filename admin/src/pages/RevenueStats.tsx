import React, { useEffect, useState } from 'react'
import { adminApi } from '../api'
import { useI18n } from '../i18n'

const RevenueStats: React.FC = () => {
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const { t } = useI18n()
  const [dateRange, setDateRange] = useState<{ start: string; end: string }>({
    start: new Date(new Date().setMonth(new Date().getMonth() - 1)).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0],
  })

  useEffect(() => {
    const loadStats = async () => {
      setLoading(true)
      try {
        const data = await adminApi.getRevenueStats(dateRange.start, dateRange.end)
        setStats(data)
      } catch (error) {
        console.error('Failed to load revenue stats:', error)
      } finally {
        setLoading(false)
      }
    }

    loadStats()
  }, [dateRange])

  const reload = async () => {
    setLoading(true)
    try {
      const data = await adminApi.getRevenueStats(dateRange.start, dateRange.end)
      setStats(data)
    } catch (error) {
      console.error('Failed to load revenue stats:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="py-12 text-center">
        <div className="mx-auto h-12 w-12 animate-spin rounded-full border-b-2 border-indigo-600"></div>
        <p className="mt-4 text-gray-600">{t('common.loading')}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">{t('revenue.title')}</h1>

      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <div className="mb-6 flex flex-col space-y-4 md:flex-row md:items-center md:justify-between md:space-y-0">
          <div className="flex space-x-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">{t('revenue.startDate')}</label>
              <input
                type="date"
                value={dateRange.start}
                onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
                className="rounded-md border px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">{t('revenue.endDate')}</label>
              <input
                type="date"
                value={dateRange.end}
                onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
                className="rounded-md border px-3 py-2 text-sm"
              />
            </div>
          </div>
          <button
            onClick={reload}
            className="rounded-md bg-indigo-600 px-4 py-2 text-sm text-white hover:bg-indigo-700"
            type="button"
          >
            {t('common.query')}
          </button>
        </div>

        <div className="mb-6 grid grid-cols-1 gap-6 md:grid-cols-3">
          <div className="rounded-lg bg-gray-50 p-4">
            <p className="text-sm font-medium text-gray-500">{t('revenue.totalRevenue')}</p>
            <p className="text-2xl font-bold text-indigo-600">
              {t('common.currency')}
              {stats?.total_revenue || 0}
            </p>
          </div>
          <div className="rounded-lg bg-gray-50 p-4">
            <p className="text-sm font-medium text-gray-500">{t('revenue.orderCount')}</p>
            <p className="text-2xl font-bold text-gray-900">{stats?.total_orders || 0}</p>
          </div>
          <div className="rounded-lg bg-gray-50 p-4">
            <p className="text-sm font-medium text-gray-500">{t('revenue.avgOrderAmount')}</p>
            <p className="text-2xl font-bold text-gray-900">
              {t('common.currency')}
              {stats?.total_orders ? (stats.total_revenue / stats.total_orders).toFixed(2) : '0.00'}
            </p>
          </div>
        </div>

        <div className="mb-6">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">{t('revenue.revenueTrend')}</h2>
          <div className="flex h-64 items-center justify-center rounded-lg bg-gray-100">
            <span className="text-gray-500">{t('revenue.revenueTrendChart')}</span>
          </div>
        </div>

        <div>
          <h2 className="mb-4 text-lg font-semibold text-gray-900">{t('revenue.source')}</h2>
          <div className="flex h-64 items-center justify-center rounded-lg bg-gray-100">
            <span className="text-gray-500">{t('revenue.sourceChart')}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default RevenueStats

