import React from 'react'
import { Link, useLocation, Outlet } from 'react-router-dom'
import { useAuthStore, useUIStore } from '../store'

const AdminLayout: React.FC = () => {
  const { admin, logout } = useAuthStore()
  const { sidebarCollapsed, toggleSidebar } = useUIStore()
  const location = useLocation()

  const navItems = [
    { path: '/admin', label: '仪表盘', icon: '📊' },
    { path: '/admin/users', label: '用户管理', icon: '👥' },
    { path: '/admin/orders', label: '订单管理', icon: '📋' },
    { path: '/admin/revenue', label: '收入统计', icon: '💰' },
    { path: '/admin/permissions', label: '权限价格', icon: '🔐' },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <button
                onClick={toggleSidebar}
                className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 lg:hidden"
              >
                <span className="text-xl">{sidebarCollapsed ? '☰' : '✕'}</span>
              </button>
              <Link to="/admin" className="flex items-center ml-2 lg:ml-0">
                <span className="text-2xl font-bold text-indigo-600">后台管理</span>
              </Link>
            </div>

            <div className="flex items-center space-x-4">
              <span className="text-gray-600">{admin?.nickname}</span>
              <span className="text-gray-400">|</span>
              <button
                onClick={logout}
                className="text-gray-500 hover:text-gray-700"
              >
                退出
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        <aside
          className={`${
            sidebarCollapsed ? '-translate-x-full' : 'translate-x-0'
          } fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 lg:w-64 pt-16 lg:pt-0`}
        >
          <nav className="mt-5 px-2">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`group flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                  location.pathname === item.path
                    ? 'bg-indigo-100 text-indigo-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <span className="text-xl mr-3">{item.icon}</span>
                {item.label}
              </Link>
            ))}
          </nav>
        </aside>

        <main className="flex-1 min-w-0">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <Outlet />
          </div>
        </main>
      </div>

      {sidebarCollapsed && (
        <div
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={toggleSidebar}
        />
      )}
    </div>
  )
}

export default AdminLayout
