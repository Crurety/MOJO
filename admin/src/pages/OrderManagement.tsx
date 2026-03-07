import React, { useEffect, useState } from 'react'
import { adminApi } from '../api'
import { useI18n } from '../i18n'
import * as Types from '../types/api'

const OrderManagement: React.FC = () => {
  const [orders, setOrders] = useState<Types.Order[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<{ status?: number; orderType?: string }>({})
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize] = useState(20)
  const { t } = useI18n()

  useEffect(() => {
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

    loadOrders()
  }, [filter, currentPage, pageSize])

  const getStatusLabel = (status: number) => {
    switch (status) {
      case 0:
        return t('order.status.pending')
      case 1:
        return t('order.status.completed')
      case 2:
        return t('order.status.cancelled')
      default:
        return t('common.unknown')
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

  const getPaymentMethodLabel = (method: string) => {
    switch (method) {
      case 'wechat':
        return t('order.payment.wechat')
      case 'alipay':
        return t('order.payment.alipay')
      case 'unionpay':
        return t('order.payment.unionpay')
      case 'balance':
        return t('order.payment.balance')
      default:
        return method
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">{t('order.title')}</h1>
        <div className="flex space-x-2">
          <select
            value={filter.status ?? ''}
            onChange={(e) =>
              setFilter({
                ...filter,
                status: e.target.value ? Number.parseInt(e.target.value, 10) : undefined,
              })
            }
            className="rounded-md border px-3 py-2 text-sm"
            aria-label={t('common.allStatuses')}
          >
            <option value="">{t('common.allStatuses')}</option>
            <option value="0">{t('order.status.pending')}</option>
            <option value="1">{t('order.status.completed')}</option>
            <option value="2">{t('order.status.cancelled')}</option>
          </select>
          <select
            value={filter.orderType || ''}
            onChange={(e) => setFilter({ ...filter, orderType: e.target.value || undefined })}
            className="rounded-md border px-3 py-2 text-sm"
            aria-label={t('common.allTypes')}
          >
            <option value="">{t('common.allTypes')}</option>
            <option value="permission">{t('order.type.permission')}</option>
            <option value="balance">{t('order.type.balance')}</option>
          </select>
        </div>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table>
            <thead>
              <tr>
                <th>{t('order.column.orderNo')}</th>
                <th>{t('order.column.user')}</th>
                <th>{t('order.column.type')}</th>
                <th>{t('order.column.product')}</th>
                <th>{t('order.column.amount')}</th>
                <th>{t('order.column.method')}</th>
                <th>{t('order.column.status')}</th>
                <th>{t('order.column.createdAt')}</th>
                <th>{t('order.column.completedAt')}</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={9} className="py-4 text-center text-gray-500">
                    {t('common.loading')}
                  </td>
                </tr>
              ) : orders.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-4 text-center text-gray-500">
                    {t('order.noOrders')}
                  </td>
                </tr>
              ) : (
                orders.map((order) => (
                  <tr key={order.order_no}>
                    <td>{order.order_no}</td>
                    <td>{order.user_nickname}</td>
                    <td>{order.order_type === 'permission' ? t('order.type.permission') : t('order.type.balance')}</td>
                    <td>{order.product_name || '-'}</td>
                    <td>
                      {t('common.currency')}
                      {order.amount}
                    </td>
                    <td>{getPaymentMethodLabel(order.payment_method as string)}</td>
                    <td>
                      <span className={`inline-block rounded px-2 py-1 text-xs ${getStatusClass(order.status)}`}>
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
        <div className="flex items-center justify-between border-t border-gray-200 p-4">
          <div className="text-sm text-gray-500">{t('common.totalRecords', { count: orders.length })}</div>
          <div className="flex space-x-2">
            <button
              onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
              className="rounded-md border px-3 py-1 text-sm disabled:opacity-50"
              type="button"
            >
              {t('common.previousPage')}
            </button>
            <button
              onClick={() => setCurrentPage((prev) => prev + 1)}
              className="rounded-md border px-3 py-1 text-sm"
              type="button"
            >
              {t('common.nextPage')}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default OrderManagement

