import React, { useState, useEffect } from 'react'
import { adminApi } from '../api'
import * as Types from '../types/api'

const OrderManagement: React.FC = () => {
  const [orders, setOrders] = useState<Types.Order[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<{ status?: number; orderType?: string }>({})
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize] = useState(20)

  useEffect(() => {
    loadOrders()
  }, [filter, currentPage, pageSize])

  const loadOrders = async () => {
    setLoading(true)
    try {
      const data = await adminApi.getOrders(
        (currentPage - 1) * pageSize,
        pageSize,
        filter.status,
        filter.orderType
      )
      setOrders(data || [])
    } catch (error) {
      console.error('Failed to load orders:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusLabel = (status: number) => {
    switch (status) {
      case 0:
        return '待支付'
      case 1:
        return '已完成'
      case 2:
        return '已取消'
      default:
        return '未知'
    }
  }

  const getStatusClass = (status: number) => {
    switch (status) {
      case 0:
        return 'bg-yellow-100 text-yellow-700'
      case 1:
        return 'bg-green-100 text-green-700'
      case 2:
        return 'bg-red-100 text-red-700'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">订单管理</h1>
        <div className="flex space-x-2">
          <select
            value={filter.status || ''}
            onChange={(e) => setFilter({ ...filter, status: e.target.value ? parseInt(e.target.value) : undefined })}
            className="px-3 py-2 border rounded-md text-sm"
          >
            <option value="">全部状态</option>
            <option value="0">待支付</option>
            <option value="1">已完成</option>
            <option value="2">已取消</option>
          </select>
          <select
            value={filter.orderType || ''}
            onChange={(e) => setFilter({ ...filter, orderType: e.target.value || undefined })}
            className="px-3 py-2 border rounded-md text-sm"
          >
            <option value="">全部类型</option>
            <option value="permission">权限购买</option>
            <option value="balance">余额充值</option>
          </select>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="overflow-x-auto">
          <table>
            <thead>
              <tr>
                <th>订单号</th>
                <th>用户</th>
                <th>类型</th>
                <th>产品</th>
                <th>金额</th>
                <th>支付方式</th>
                <th>状态</th>
                <th>创建时间</th>
                <th>完成时间</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={9} className="text-center text-gray-500 py-4">
                    加载中...
                  </td>
                </tr>
              ) : orders.length === 0 ? (
                <tr>
                  <td colSpan={9} className="text-center text-gray-500 py-4">
                    暂无订单
                  </td>
                </tr>
              ) : (
                orders.map((order) => (
                  <tr key={order.order_no}>
                    <td>{order.order_no}</td>
                    <td>{order.user_nickname}</td>
                    <td>{order.order_type === 'permission' ? '权限购买' : '余额充值'}</td>
                    <td>{order.product_name || '-'}</td>
                    <td>¥{order.amount}</td>
                    <td>
                      {{
                        wechat: '微信支付',
                        alipay: '支付宝',
                        unionpay: '银联支付',
                        balance: '余额支付'
                      }[order.payment_method as string] || order.payment_method}
                    </td>
                    <td>
                      <span className={`inline-block px-2 py-1 rounded text-xs ${getStatusClass(order.status)}`}>
                        {getStatusLabel(order.status)}
                      </span>
                    </td>
                    <td>{new Date(order.created_at).toLocaleString()}</td>
                    <td>{order.completed_at ? new Date(order.completed_at).toLocaleString() : '-'}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        <div className="p-4 flex items-center justify-between border-t border-gray-200">
          <div className="text-sm text-gray-500">
            共 {orders.length} 条记录
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
              className="px-3 py-1 border rounded-md text-sm disabled:opacity-50"
            >
              上一页
            </button>
            <button
              onClick={() => setCurrentPage((prev) => prev + 1)}
              className="px-3 py-1 border rounded-md text-sm"
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default OrderManagement
