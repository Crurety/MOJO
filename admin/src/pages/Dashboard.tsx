import React, { useEffect, useState } from 'react'
import { adminApi } from '../api'
import { useI18n } from '../i18n'

const Dashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const { t } = useI18n()

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        const data = await adminApi.getDashboard()
        setDashboardData(data)
      } catch (error) {
        console.error('Failed to load dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }

    loadDashboardData()
  }, [])

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
      <h1 className="text-2xl font-bold text-gray-900">{t('dashboard.title')}</h1>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">{t('dashboard.totalUsers')}</p>
              <p className="text-3xl font-bold text-gray-900">{dashboardData?.total_users || 0}</p>
            </div>
            <div className="rounded-full bg-blue-100 p-3">
              <span className="text-2xl">👤</span>
            </div>
          </div>
        </div>

        <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">{t('dashboard.todayActive')}</p>
              <p className="text-3xl font-bold text-gray-900">{dashboardData?.today_active || 0}</p>
            </div>
            <div className="rounded-full bg-green-100 p-3">
              <span className="text-2xl">📈</span>
            </div>
          </div>
        </div>

        <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">{t('dashboard.totalOrders')}</p>
              <p className="text-3xl font-bold text-gray-900">{dashboardData?.total_orders || 0}</p>
            </div>
            <div className="rounded-full bg-purple-100 p-3">
              <span className="text-2xl">🧾</span>
            </div>
          </div>
        </div>

        <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">{t('dashboard.totalRevenue')}</p>
              <p className="text-3xl font-bold text-indigo-600">
                {t('common.currency')}
                {dashboardData?.total_revenue || 0}
              </p>
            </div>
            <div className="rounded-full bg-yellow-100 p-3">
              <span className="text-2xl">💰</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">{t('dashboard.revenueTrend')}</h2>
          <div className="flex h-64 items-center justify-center rounded-lg bg-gray-100">
            <span className="text-gray-500">{t('dashboard.revenueChart')}</span>
          </div>
        </div>

        <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-lg font-semibold text-gray-900">{t('dashboard.userGrowth')}</h2>
          <div className="flex h-64 items-center justify-center rounded-lg bg-gray-100">
            <span className="text-gray-500">{t('dashboard.userGrowthChart')}</span>
          </div>
        </div>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">{t('dashboard.recentOrders')}</h2>
        <div className="overflow-x-auto">
          <table>
            <thead>
              <tr>
                <th>{t('dashboard.orderNo')}</th>
                <th>{t('dashboard.user')}</th>
                <th>{t('dashboard.type')}</th>
                <th>{t('dashboard.amount')}</th>
                <th>{t('dashboard.status')}</th>
                <th>{t('dashboard.time')}</th>
              </tr>
            </thead>
            <tbody>
              {dashboardData?.recent_orders?.map((order: any) => (
                <tr key={order.order_no}>
                  <td>{order.order_no}</td>
                  <td>{order.user_nickname}</td>
                  <td>
                    {order.order_type === 'permission'
                      ? t('dashboard.orderType.permission')
                      : t('dashboard.orderType.balance')}
                  </td>
                  <td>
                    {t('common.currency')}
                    {order.amount}
                  </td>
                  <td>
                    <span
                      className={`inline-block rounded px-2 py-1 text-xs ${
                        order.status === 1 ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                      }`}
                    >
                      {order.status === 1 ? t('dashboard.orderStatus.completed') : t('dashboard.orderStatus.pending')}
                    </span>
                  </td>
                  <td>{new Date(order.created_at).toLocaleString()}</td>
                </tr>
              )) || (
                <tr>
                  <td colSpan={6} className="py-4 text-center text-gray-500">
                    {t('dashboard.noOrders')}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Dashboard

