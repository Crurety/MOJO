import React, { useEffect, useMemo, useState } from 'react'
import {
  DollarCircleOutlined,
  OrderedListOutlined,
  TeamOutlined,
  UserOutlined,
} from '@ant-design/icons'
import { adminApi } from '../api'
import { useI18n } from '../i18n'

type DashboardData = {
  total_users?: number
  today_active?: number
  total_orders?: number
  total_revenue?: number
  users?: {
    total?: number
    new_today?: number
  }
  revenue?: {
    today?: number
    month?: number
  }
  recent_orders?: Array<{
    order_no: string
    user_nickname?: string
    order_type: string
    amount: number
    status: number
    created_at: string
  }>
}

const Dashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const { t } = useI18n()

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        const [data, latestOrders] = await Promise.all([adminApi.getDashboard(), adminApi.getOrders(0, 6)])
        const normalized = data as DashboardData

        if (!normalized.recent_orders?.length) {
          normalized.recent_orders = latestOrders.items || []
        }
        if (normalized.total_orders === undefined) {
          normalized.total_orders = latestOrders.total || 0
        }

        setDashboardData(normalized)
      } catch (error) {
        console.error('Failed to load dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }

    void loadDashboardData()
  }, [])

  const cards = useMemo(
    () => [
      {
        key: 'users',
        label: t('dashboard.totalUsers'),
        value: dashboardData?.total_users ?? dashboardData?.users?.total ?? 0,
        icon: <TeamOutlined />,
      },
      {
        key: 'active',
        label: t('dashboard.todayActive'),
        value: dashboardData?.today_active ?? dashboardData?.users?.new_today ?? 0,
        icon: <UserOutlined />,
      },
      {
        key: 'orders',
        label: t('dashboard.totalOrders'),
        value: dashboardData?.total_orders ?? 0,
        icon: <OrderedListOutlined />,
      },
      {
        key: 'revenue',
        label: t('dashboard.totalRevenue'),
        value: `${t('common.currency')}${dashboardData?.total_revenue ?? dashboardData?.revenue?.month ?? 0}`,
        icon: <DollarCircleOutlined />,
        accent: true,
      },
    ],
    [dashboardData, t]
  )

  if (loading) {
    return (
      <div className="admin-loader">
        <div className="admin-loader-spinner"></div>
        <p className="admin-loader-text">{t('common.loading')}</p>
      </div>
    )
  }

  return (
    <section className="admin-page space-y-4">
      <div className="admin-page-head">
        <div>
          <h1 className="admin-page-title">{t('dashboard.title')}</h1>
          <p className="admin-page-subtitle">Realtime command overview for users, revenue, and order throughput.</p>
        </div>
      </div>

      <div className="admin-kpi-grid">
        {cards.map((card) => (
          <article key={card.key} className="admin-kpi-card">
            <div className="admin-kpi-head">
              <p className="admin-kpi-label">{card.label}</p>
              <span className="admin-kpi-icon">{card.icon}</span>
            </div>
            <p className={`admin-kpi-value ${card.accent ? 'is-accent' : ''}`}>{card.value}</p>
          </article>
        ))}
      </div>

      <div className="admin-grid-2">
        <section className="admin-panel">
          <h2 className="admin-panel-title">{t('dashboard.revenueTrend')}</h2>
          <div className="admin-chart-placeholder">{t('dashboard.revenueChart')}</div>
        </section>
        <section className="admin-panel">
          <h2 className="admin-panel-title">{t('dashboard.userGrowth')}</h2>
          <div className="admin-chart-placeholder">{t('dashboard.userGrowthChart')}</div>
        </section>
      </div>

      <section className="admin-panel">
        <h2 className="admin-panel-title">{t('dashboard.recentOrders')}</h2>
        <div className="admin-table-wrap">
          <table className="admin-table">
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
              {dashboardData?.recent_orders?.length ? (
                dashboardData.recent_orders.map((order) => (
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
                      <span className={`admin-pill ${order.status === 1 ? 'admin-pill-success' : 'admin-pill-warning'}`}>
                        {order.status === 1 ? t('dashboard.orderStatus.completed') : t('dashboard.orderStatus.pending')}
                      </span>
                    </td>
                    <td>{new Date(order.created_at).toLocaleString()}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="admin-table-empty">
                    {t('dashboard.noOrders')}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </section>
  )
}

export default Dashboard
