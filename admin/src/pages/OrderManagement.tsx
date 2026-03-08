import React, { useCallback, useEffect, useMemo, useState } from 'react'
import { adminApi } from '../api'
import { useI18n } from '../i18n'
import * as Types from '../types/api'

const OrderManagement: React.FC = () => {
  const [orders, setOrders] = useState<Types.Order[]>([])
  const [loading, setLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize] = useState(20)
  const [total, setTotal] = useState(0)
  const [keywordInput, setKeywordInput] = useState('')
  const [keyword, setKeyword] = useState('')
  const [error, setError] = useState('')
  const [filter, setFilter] = useState<{ status?: number; orderType?: string }>({})
  const { t } = useI18n()

  const totalPages = useMemo(() => Math.max(1, Math.ceil(total / pageSize)), [pageSize, total])

  const loadOrders = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const response = await adminApi.getOrders(
        (currentPage - 1) * pageSize,
        pageSize,
        filter.status,
        filter.orderType,
        keyword || undefined
      )
      setOrders(response.items || [])
      setTotal(response.total || 0)
    } catch (loadError) {
      console.error('Failed to load orders:', loadError)
      setError('Failed to load order list')
      setOrders([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }, [currentPage, filter.orderType, filter.status, keyword, pageSize])

  useEffect(() => {
    void loadOrders()
  }, [loadOrders])

  const handleQuery = () => {
    setCurrentPage(1)
    setKeyword(keywordInput.trim())
  }

  const handleReset = () => {
    setFilter({})
    setKeyword('')
    setKeywordInput('')
    setCurrentPage(1)
  }

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
        return 'admin-pill-warning'
      case 1:
        return 'admin-pill-success'
      case 2:
        return 'admin-pill-danger'
      default:
        return 'admin-pill-neutral'
    }
  }

  const getPaymentMethodLabel = (method: string | undefined) => {
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
        return method || '-'
    }
  }

  return (
    <section className="admin-page space-y-4">
      <div className="admin-page-head">
        <div>
          <h1 className="admin-page-title">{t('order.title')}</h1>
          <p className="admin-page-subtitle">Track order lifecycle, payment methods, and revenue-impacting exceptions.</p>
        </div>
        <div className="admin-filter-row">
          <input
            value={keywordInput}
            onChange={(e) => setKeywordInput(e.target.value)}
            className="admin-input"
            placeholder="Search order no./user/product"
            aria-label={t('order.title')}
          />
          <select
            value={filter.status ?? ''}
            onChange={(e) => {
              setCurrentPage(1)
              setFilter({ ...filter, status: e.target.value ? Number.parseInt(e.target.value, 10) : undefined })
            }}
            className="admin-select"
            aria-label={t('common.allStatuses')}
          >
            <option value="">{t('common.allStatuses')}</option>
            <option value="0">{t('order.status.pending')}</option>
            <option value="1">{t('order.status.completed')}</option>
            <option value="2">{t('order.status.cancelled')}</option>
          </select>
          <select
            value={filter.orderType || ''}
            onChange={(e) => {
              setCurrentPage(1)
              setFilter({ ...filter, orderType: e.target.value || undefined })
            }}
            className="admin-select"
            aria-label={t('common.allTypes')}
          >
            <option value="">{t('common.allTypes')}</option>
            <option value="permission">{t('order.type.permission')}</option>
            <option value="balance">{t('order.type.balance')}</option>
          </select>
          <button className="admin-btn admin-btn-primary" type="button" onClick={handleQuery}>
            {t('common.query')}
          </button>
          <button className="admin-btn" type="button" onClick={handleReset}>
            {t('common.cancel')}
          </button>
        </div>
      </div>

      {error && <div className="admin-alert is-error">{error}</div>}

      <section className="admin-panel">
        <div className="admin-table-wrap">
          <table className="admin-table">
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
                  <td colSpan={9} className="admin-table-empty">
                    {t('common.loading')}
                  </td>
                </tr>
              ) : orders.length === 0 ? (
                <tr>
                  <td colSpan={9} className="admin-table-empty">
                    {t('order.noOrders')}
                  </td>
                </tr>
              ) : (
                orders.map((order) => (
                  <tr key={order.order_no}>
                    <td>{order.order_no}</td>
                    <td>{order.user_nickname || '-'}</td>
                    <td>{order.order_type === 'permission' ? t('order.type.permission') : t('order.type.balance')}</td>
                    <td>{order.product_name || '-'}</td>
                    <td>
                      {t('common.currency')}
                      {order.amount}
                    </td>
                    <td>{getPaymentMethodLabel(order.payment_method)}</td>
                    <td>
                      <span className={`admin-pill ${getStatusClass(order.status)}`}>{getStatusLabel(order.status)}</span>
                    </td>
                    <td>{new Date(order.created_at).toLocaleString()}</td>
                    <td>{order.completed_at ? new Date(order.completed_at).toLocaleString() : '-'}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="admin-pagination">
          <div className="admin-pagination-info">
            {t('common.totalRecords', { count: total })} | {currentPage}/{totalPages}
          </div>
          <div className="admin-pagination-actions">
            <button
              onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
              disabled={currentPage === 1 || loading}
              className="admin-btn"
              type="button"
            >
              {t('common.previousPage')}
            </button>
            <button
              onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
              disabled={currentPage >= totalPages || loading}
              className="admin-btn"
              type="button"
            >
              {t('common.nextPage')}
            </button>
          </div>
        </div>
      </section>
    </section>
  )
}

export default OrderManagement
