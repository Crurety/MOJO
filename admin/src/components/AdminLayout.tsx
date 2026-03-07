import React from 'react'
import { Link, Outlet, useLocation } from 'react-router-dom'
import { useI18n } from '../i18n'
import { useAuthStore, useUIStore } from '../store'
import LanguageSwitcher from './LanguageSwitcher'

const AdminLayout: React.FC = () => {
  const { admin, logout } = useAuthStore()
  const { sidebarCollapsed, toggleSidebar } = useUIStore()
  const { t } = useI18n()
  const location = useLocation()

  const navItems = [
    { path: '/admin', label: t('layout.nav.dashboard'), icon: '📊' },
    { path: '/admin/users', label: t('layout.nav.users'), icon: '👤' },
    { path: '/admin/orders', label: t('layout.nav.orders'), icon: '🧾' },
    { path: '/admin/revenue', label: t('layout.nav.revenue'), icon: '💰' },
    { path: '/admin/permissions', label: t('layout.nav.permissions'), icon: '⚙️' },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b border-gray-200 bg-white shadow-sm">
        <div className="mx-auto h-16 max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-full items-center justify-between">
            <div className="flex items-center">
              <button
                onClick={toggleSidebar}
                className="rounded-md p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-500 lg:hidden"
                aria-label={t('layout.toggleSidebar')}
                type="button"
              >
                <span className="text-xl">{sidebarCollapsed ? '☰' : '×'}</span>
              </button>
              <Link to="/admin" className="ml-2 flex items-center lg:ml-0">
                <span className="text-2xl font-bold text-indigo-600">{t('layout.title')}</span>
              </Link>
            </div>

            <div className="flex items-center space-x-4">
              <LanguageSwitcher />
              <span className="text-gray-600">{admin?.nickname}</span>
              <span className="text-gray-400">|</span>
              <button onClick={logout} className="text-gray-500 hover:text-gray-700" type="button">
                {t('layout.logout')}
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        <aside
          className={`${
            sidebarCollapsed ? '-translate-x-full' : 'translate-x-0'
          } fixed inset-y-0 left-0 z-50 w-64 transform border-r border-gray-200 bg-white pt-16 transition-transform duration-300 ease-in-out lg:static lg:inset-0 lg:w-64 lg:translate-x-0 lg:pt-0`}
        >
          <nav className="mt-5 px-2">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`group flex items-center rounded-md px-3 py-2 text-sm font-medium ${
                  location.pathname === item.path
                    ? 'bg-indigo-100 text-indigo-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <span className="mr-3 text-xl">{item.icon}</span>
                {item.label}
              </Link>
            ))}
          </nav>
        </aside>

        <main className="min-w-0 flex-1">
          <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
            <Outlet />
          </div>
        </main>
      </div>

      {sidebarCollapsed && (
        <div className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden" onClick={toggleSidebar} />
      )}
    </div>
  )
}

export default AdminLayout

