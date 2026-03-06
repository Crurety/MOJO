import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuthStore, useUIStore } from '../../store'

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, isAuthenticated, logout } = useAuthStore()
  const { sidebarCollapsed, toggleSidebar } = useUIStore()
  const location = useLocation()

  const navItems = [
    { path: '/', label: '首页', icon: '🏠' },
    { path: '/create/script', label: '脚本生成', icon: '📝' },
    { path: '/create/image', label: '图片生成', icon: '🖼️' },
    { path: '/create/video', label: '视频生成', icon: '🎬' },
    { path: '/create/ad', label: '广告设计', icon: '📢' },
    { path: '/works', label: '我的作品', icon: '📁' },
    { path: '/tasks', label: '任务中心', icon: '⏳' },
    { path: '/gallery', label: '作品集', icon: '🎨' },
    { path: '/pricing', label: '价格方案', icon: '💰' },
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
              <Link to="/" className="flex items-center ml-2 lg:ml-0">
                <span className="text-2xl font-bold text-indigo-600">AI创作平台</span>
              </Link>
            </div>

            <nav className="hidden lg:flex space-x-4">
              {navItems.slice(0, 5).map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    location.pathname === item.path
                      ? 'bg-indigo-100 text-indigo-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  <span className="mr-1">{item.icon}</span>
                  {item.label}
                </Link>
              ))}
            </nav>

            <div className="flex items-center space-x-4">
              {isAuthenticated ? (
                <>
                  <Link
                    to="/account"
                    className="flex items-center text-gray-600 hover:text-gray-900"
                  >
                    <span className="text-xl mr-2">👤</span>
                    <span className="hidden sm:inline">{user?.nickname}</span>
                  </Link>
                  <span className="text-gray-400">|</span>
                  <span className="text-indigo-600 font-medium">
                    ¥{user?.balance?.toFixed(2) || '0.00'}
                  </span>
                  <button
                    onClick={logout}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    退出
                  </button>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="text-gray-600 hover:text-gray-900"
                  >
                    登录
                  </Link>
                  <Link
                    to="/register"
                    className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
                  >
                    注册
                  </Link>
                </>
              )}
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
            {children}
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

export default Layout
