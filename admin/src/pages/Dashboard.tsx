import React, { useState, useEffect } from 'react'
import { adminApi } from '../api'

const Dashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

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

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">加载中...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">仪表盘</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">总用户数</p>
              <p className="text-3xl font-bold text-gray-900">{dashboardData?.total_users || 0}</p>
            </div>
            <div className="bg-blue-100 rounded-full p-3">
              <span className="text-2xl">👥</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">今日活跃</p>
              <p className="text-3xl font-bold text-gray-900">{dashboardData?.today_active || 0}</p>
            </div>
            <div className="bg-green-100 rounded-full p-3">
              <span className="text-2xl">📊</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">总订单数</p>
              <p className="text-3xl font-bold text-gray-900">{dashboardData?.total_orders || 0}</p>
            </div>
            <div className="bg-purple-100 rounded-full p-3">
              <span className="text-2xl">📋</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">总收入</p>
              <p className="text-3xl font-bold text-indigo-600">¥{dashboardData?.total_revenue || 0}</p>
            </div>
            <div className="bg-yellow-100 rounded-full p-3">
              <span className="text-2xl">💰</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">收入趋势</h2>
          <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
            <span className="text-gray-500">收入图表</span>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">用户增长</h2>
          <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
            <span className="text-gray-500">用户增长图表</span>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">最近订单</h2>
        <div className="overflow-x-auto">
          <table>
            <thead>
              <tr>
                <th>订单号</th>
                <th>用户</th>
                <th>类型</th>
                <th>金额</th>
                <th>状态</th>
                <th>时间</th>
              </tr>
            </thead>
            <tbody>
              {dashboardData?.recent_orders?.map((order: any) => (
                <tr key={order.order_no}>
                  <td>{order.order_no}</td>
                  <td>{order.user_nickname}</td>
                  <td>{order.order_type === 'permission' ? '权限购买' : '余额充值'}</td>
                  <td>¥{order.amount}</td>
                  <td>
                    <span className={`inline-block px-2 py-1 rounded text-xs ${
                      order.status === 1 ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                    }`}>
                      {order.status === 1 ? '已完成' : '待处理'}
                    </span>
                  </td>
                  <td>{new Date(order.created_at).toLocaleString()}</td>
                </tr>
              )) || (
                <tr>
                  <td colSpan={6} className="text-center text-gray-500 py-4">
                    暂无订单
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
