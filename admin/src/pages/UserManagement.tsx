import React, { useCallback, useEffect, useMemo, useState } from 'react'
import { adminApi } from '../api'
import { useI18n } from '../i18n'
import * as Types from '../types/api'

const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<Types.User[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<{ status?: number }>({})
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize] = useState(20)
  const [total, setTotal] = useState(0)
  const [keywordInput, setKeywordInput] = useState('')
  const [keyword, setKeyword] = useState('')
  const [updatingUserId, setUpdatingUserId] = useState<number | null>(null)
  const [error, setError] = useState('')
  const { t } = useI18n()

  const totalPages = useMemo(() => Math.max(1, Math.ceil(total / pageSize)), [total, pageSize])

  const loadUsers = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const response = await adminApi.getUsers(
        (currentPage - 1) * pageSize,
        pageSize,
        filter.status,
        keyword || undefined
      )
      setUsers(response.items || [])
      setTotal(response.total || 0)
    } catch (loadError) {
      console.error('Failed to load users:', loadError)
      setError('Failed to load user list')
      setUsers([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }, [currentPage, filter.status, keyword, pageSize])

  useEffect(() => {
    void loadUsers()
  }, [loadUsers])

  const handleUpdateStatus = async (userId: number, status: number) => {
    setUpdatingUserId(userId)
    setError('')
    try {
      await adminApi.updateUserStatus(userId, status)
      await loadUsers()
    } catch (updateError) {
      console.error('Failed to update user status:', updateError)
      setError('Failed to update user status')
    } finally {
      setUpdatingUserId(null)
    }
  }

  const handleQuery = () => {
    setCurrentPage(1)
    setKeyword(keywordInput.trim())
  }

  const handleReset = () => {
    setFilter({})
    setKeywordInput('')
    setKeyword('')
    setCurrentPage(1)
  }

  const statusMeta = (status: number) => {
    if (status === 0) return { label: t('user.status.disabled'), className: 'admin-pill-danger' }
    if (status === 1) return { label: t('user.status.active'), className: 'admin-pill-success' }
    return { label: t('user.status.unknown'), className: 'admin-pill-neutral' }
  }

  return (
    <section className="admin-page space-y-4">
      <div className="admin-page-head">
        <div>
          <h1 className="admin-page-title">{t('user.title')}</h1>
          <p className="admin-page-subtitle">Review accounts, balances, and activation status in one control surface.</p>
        </div>
        <div className="admin-filter-row">
          <input
            value={keywordInput}
            onChange={(e) => setKeywordInput(e.target.value)}
            className="admin-input"
            placeholder="Search nickname/email/phone"
            aria-label={t('user.filterStatus')}
          />
          <select
            value={filter.status ?? ''}
            onChange={(e) => {
              setCurrentPage(1)
              setFilter({ status: e.target.value ? Number.parseInt(e.target.value, 10) : undefined })
            }}
            className="admin-select"
            aria-label={t('user.filterStatus')}
          >
            <option value="">{t('common.allStatuses')}</option>
            <option value="0">{t('user.status.disabled')}</option>
            <option value="1">{t('user.status.active')}</option>
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
                <th>{t('user.column.id')}</th>
                <th>{t('user.column.nickname')}</th>
                <th>{t('user.column.email')}</th>
                <th>{t('user.column.phone')}</th>
                <th>{t('user.column.balance')}</th>
                <th>{t('user.column.status')}</th>
                <th>{t('user.column.registeredAt')}</th>
                <th>{t('user.column.action')}</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={8} className="admin-table-empty">
                    {t('common.loading')}
                  </td>
                </tr>
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan={8} className="admin-table-empty">
                    {t('user.noUsers')}
                  </td>
                </tr>
              ) : (
                users.map((user) => {
                  const meta = statusMeta(user.status)
                  const toggling = updatingUserId === user.id
                  return (
                    <tr key={user.id}>
                      <td>{user.id}</td>
                      <td>{user.nickname || '-'}</td>
                      <td>{user.email || '-'}</td>
                      <td>{user.phone || '-'}</td>
                      <td>
                        {t('common.currency')}
                        {user.balance || 0}
                      </td>
                      <td>
                        <span className={`admin-pill ${meta.className}`}>{meta.label}</span>
                      </td>
                      <td>{new Date(user.created_at).toLocaleString()}</td>
                      <td>
                        <button
                          onClick={() => void handleUpdateStatus(user.id, user.status === 1 ? 0 : 1)}
                          className={`admin-btn ${user.status === 1 ? 'admin-btn-danger' : 'admin-btn-primary'}`}
                          disabled={toggling}
                          type="button"
                        >
                          {toggling ? t('common.loading') : user.status === 1 ? t('user.disable') : t('user.enable')}
                        </button>
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>

        <div className="admin-pagination">
          <div className="admin-pagination-info">
            {t('common.totalRecords', { count: total })} · {currentPage}/{totalPages}
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

export default UserManagement
