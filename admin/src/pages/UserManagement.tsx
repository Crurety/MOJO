import React, { useEffect, useState } from 'react'
import { adminApi } from '../api'
import { useI18n } from '../i18n'
import * as Types from '../types/api'

const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<Types.User[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<{ status?: number }>({})
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize] = useState(20)
  const { t } = useI18n()

  useEffect(() => {
    const loadUsers = async () => {
      setLoading(true)
      try {
        const data = await adminApi.getUsers((currentPage - 1) * pageSize, pageSize, filter.status)
        setUsers(data || [])
      } catch (error) {
        console.error('Failed to load users:', error)
      } finally {
        setLoading(false)
      }
    }

    loadUsers()
  }, [filter, currentPage, pageSize])

  const handleUpdateStatus = async (userId: number, status: number) => {
    try {
      await adminApi.updateUserStatus(userId, status)
      const refreshed = await adminApi.getUsers((currentPage - 1) * pageSize, pageSize, filter.status)
      setUsers(refreshed || [])
    } catch (error) {
      console.error('Failed to update user status:', error)
    }
  }

  const getStatusLabel = (status: number) => {
    switch (status) {
      case 0:
        return t('user.status.disabled')
      case 1:
        return t('user.status.active')
      default:
        return t('user.status.unknown')
    }
  }

  const getStatusClass = (status: number) => {
    switch (status) {
      case 0:
        return 'bg-red-100 text-red-700'
      case 1:
        return 'bg-green-100 text-green-700'
      default:
        return 'bg-gray-100 text-gray-700'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">{t('user.title')}</h1>
        <select
          value={filter.status ?? ''}
          onChange={(e) => setFilter({ status: e.target.value ? Number.parseInt(e.target.value, 10) : undefined })}
          className="rounded-md border px-3 py-2 text-sm"
          aria-label={t('user.filterStatus')}
        >
          <option value="">{t('common.allStatuses')}</option>
          <option value="0">{t('user.status.disabled')}</option>
          <option value="1">{t('user.status.active')}</option>
        </select>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table>
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
                  <td colSpan={8} className="py-4 text-center text-gray-500">
                    {t('common.loading')}
                  </td>
                </tr>
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-4 text-center text-gray-500">
                    {t('user.noUsers')}
                  </td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr key={user.id}>
                    <td>{user.id}</td>
                    <td>{user.nickname}</td>
                    <td>{user.email || '-'}</td>
                    <td>{user.phone || '-'}</td>
                    <td>
                      {t('common.currency')}
                      {user.balance || 0}
                    </td>
                    <td>
                      <span className={`inline-block rounded px-2 py-1 text-xs ${getStatusClass(user.status)}`}>
                        {getStatusLabel(user.status)}
                      </span>
                    </td>
                    <td>{new Date(user.created_at).toLocaleString()}</td>
                    <td>
                      <button
                        onClick={() => handleUpdateStatus(user.id, user.status === 1 ? 0 : 1)}
                        className={`rounded px-2 py-1 text-xs ${
                          user.status === 1
                            ? 'bg-red-100 text-red-700 hover:bg-red-200'
                            : 'bg-green-100 text-green-700 hover:bg-green-200'
                        }`}
                        type="button"
                      >
                        {user.status === 1 ? t('user.disable') : t('user.enable')}
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        <div className="flex items-center justify-between border-t border-gray-200 p-4">
          <div className="text-sm text-gray-500">{t('common.totalRecords', { count: users.length })}</div>
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

export default UserManagement

