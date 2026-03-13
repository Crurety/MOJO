import React, { useMemo, useState } from 'react'
import {
  ApiOutlined,
  BarChartOutlined,
  CloseOutlined,
  DashboardOutlined,
  DollarCircleOutlined,
  MenuOutlined,
  OrderedListOutlined,
  TeamOutlined,
} from '@ant-design/icons'
import { Link, Outlet, useLocation } from 'react-router-dom'
import { useI18n } from '../i18n'
import { useAuthStore } from '../store'
import LanguageSwitcher from './LanguageSwitcher'

type NavItem = {
  path: string
  label: string
  icon: React.ReactNode
}

const AdminLayout: React.FC = () => {
  const location = useLocation()
  const { admin, logout } = useAuthStore()
  const { language, t } = useI18n()
  const [mobileOpen, setMobileOpen] = useState(false)

  const navItems: NavItem[] = useMemo(
    () => [
      { path: '/', label: t('layout.nav.dashboard'), icon: <DashboardOutlined /> },
      { path: '/users', label: t('layout.nav.users'), icon: <TeamOutlined /> },
      { path: '/orders', label: t('layout.nav.orders'), icon: <OrderedListOutlined /> },
      { path: '/revenue', label: t('layout.nav.revenue'), icon: <BarChartOutlined /> },
      { path: '/permissions', label: t('layout.nav.permissions'), icon: <DollarCircleOutlined /> },
      { path: '/ai-config', label: t('layout.nav.aiConfig'), icon: <ApiOutlined /> },
    ],
    [t]
  )

  const isActive = (path: string) => {
    if (path === '/') return location.pathname === '/'
    return location.pathname.startsWith(path)
  }

  const activeNav = navItems.find((item) => isActive(item.path)) || navItems[0]
  const sidebarNote =
    language === 'zh'
      ? '统一管理用户、订单、营收和 AI 服务配置。'
      : 'Manage users, orders, revenue, and AI services from one surface.'

  const closeMobileMenu = () => setMobileOpen(false)

  return (
    <div className="admin-app">
      <header className="admin-header">
        <div className="admin-header-inner">
          <div className="admin-brand-wrap">
            <button
              type="button"
              onClick={() => setMobileOpen((v) => !v)}
              className="admin-mobile-toggle"
              aria-label={t('layout.toggleSidebar')}
            >
              {mobileOpen ? <CloseOutlined /> : <MenuOutlined />}
            </button>
            <Link to="/" className="admin-brand">
              <span className="admin-brand-mark">MOJO</span>
              <span className="admin-brand-sub">OPERATIONS CONSOLE</span>
            </Link>
            <div className="admin-header-context">
              <p className="admin-context-kicker">{t('layout.title')}</p>
              <p className="admin-context-title">{activeNav.label}</p>
            </div>
          </div>

          <div className="admin-top-actions">
            <LanguageSwitcher />
            <span className="admin-user-chip">{admin?.nickname || 'Admin'}</span>
            <button type="button" onClick={logout} className="admin-logout-btn">
              {t('layout.logout')}
            </button>
          </div>
        </div>
      </header>

      <div className="admin-shell">
        <aside className={`admin-sidebar ${mobileOpen ? 'is-open' : ''}`}>
          <div className="admin-sidebar-head">
            <p className="admin-sidebar-eyebrow">{t('layout.title')}</p>
            <h2 className="admin-sidebar-title">Mission Panel</h2>
            <p className="admin-sidebar-note">{sidebarNote}</p>
          </div>

          <nav className="admin-nav">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                onClick={closeMobileMenu}
                className={`admin-nav-item ${isActive(item.path) ? 'is-active' : ''}`}
              >
                <span className="admin-nav-icon">{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            ))}
          </nav>

          <div className="admin-sidebar-footer">
            <p className="admin-sidebar-footer-title">{language === 'zh' ? '当前登录' : 'Current session'}</p>
            <p className="admin-sidebar-footer-text">{admin?.nickname || 'Admin'}</p>
          </div>
        </aside>

        <main className="admin-main">
          <div className="admin-main-inner">
            <Outlet />
          </div>
        </main>
      </div>

      {mobileOpen && <button type="button" className="admin-mobile-mask lg:hidden" onClick={closeMobileMenu} />}
    </div>
  )
}

export default AdminLayout
