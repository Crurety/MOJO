import React, { useState, useEffect } from 'react'
import { adminApi } from '../api'
import * as Types from '../types/api'

const UserManagement: React.FC = () => {
  const [users, setUsers] = useState<Types.User[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<{ status?: number }>({})
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize] = useState(20)

  useEffect(() => {
    loadUsers()
  }, [filter, currentPage, pageSize])

  const loadUsers = async () => {
    setLoading(true)
    try {
      const data = await adminApi.getUsers(
        (currentPage - 1) * pageSize,
        pageSize,
        filter.status
      )
      setUsers(data || [])
    } catch (error) {
      console.error('Failed to load users:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateStatus = async (userId: number, status: number) => {
    try {
      await adminApi.updateUserStatus(userId, status)
      loadUsers()
    } catch (error) {
      console.error('Failed to update user status:', error)
    }
  }

  const getStatusLabel = (status: number) => {
    switch (status) {
      case 0:
        return '禁用'
      case 1:
        return '正常'
      default:
        return '未知'
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
        <h1 className="text-2xl font-bold text-gray-900">用户管理</h1>
        <select
          value={filter.status || ''}
          onChange={(e) => setFilter({ status: e.target.value ? parseInt(e.target.value) : undefined })}
          className="px-3 py-2 border rounded-md text-sm"
        >
          <option value="">全部状态</option>
          <option value="0">禁用</option>
          <option value="1">正常</option>
        </select>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="overflow-x-auto">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>昵称</th>
                <th>邮箱</th>
                <th>手机号</th>
                <th>余额</th>
                <th>状态</th>
                <th>注册时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={8} className="text-center text-gray-500 py-4">
                    加载中...
                  </td>
                </tr>
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan={8} className="text-center text-gray-500 py-4">
                    暂无用户
                  </td>
                </tr>
              ) : (
                users.map((user) => (
                  <tr key={user.id}>
                    <td>{user.id}</td>
                    <td>{user.nickname}</td>
                    <td>{user.email || '-'}</td>
                    <td>{user.phone || '-'}</td>
                    <td>¥{user.balance || 0}</td>
                    <td>
                      <span className={`inline-block px-2 py-1 rounded text-xs ${getStatusClass(user.status)}`}>
                        {getStatusLabel(user.status)}
                      </span>
                    </td>
                    <td>{new Date(user.created_at).toLocaleString()}</td>
                    <td>
                      <button
                        onClick={() => handleUpdateStatus(user.id, user.status === 1 ? 0 : 1)}
                        className={`px-2 py-1 text-xs rounded ${
                          user.status === 1
                            ? 'bg-red-100 text-red-700 hover:bg-red-200'
                            : 'bg-green-100 text-green-700 hover:bg-green-200'
                        }`}
                      >
                        {user.status === 1 ? '禁用' : '启用'}
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        <div className="p-4 flex items-center justify-between border-t border-gray-200">
          <div className="text-sm text-gray-500">
            共 {users.length} 条记录
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

export default UserManagement
