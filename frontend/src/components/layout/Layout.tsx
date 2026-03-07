import React, { useMemo, useState } from 'react'
import {
  AppstoreOutlined,
  CloseOutlined,
  DeploymentUnitOutlined,
  DollarOutlined,
  FileTextOutlined,
  FolderOpenOutlined,
  HomeOutlined,
  MenuOutlined,
  NotificationOutlined,
  PictureOutlined,
  VideoCameraOutlined,
} from '@ant-design/icons'
import { Link, useLocation } from 'react-router-dom'
import { useI18n } from '../../i18n'
import { useAuthStore } from '../../store'
import { toLocalizedAmount } from '../../utils/currency'
import { LanguageSwitcher } from '../common'
import MeteorField from './MeteorField'

type NavItem = {
  path: string
  labelKey: string
  icon: React.ReactNode
  requireAuth?: boolean
}

const navItems: NavItem[] = [
  { path: '/', labelKey: 'nav.home', icon: <HomeOutlined /> },
  { path: '/create/script', labelKey: 'nav.script', icon: <FileTextOutlined />, requireAuth: true },
  { path: '/create/image', labelKey: 'nav.image', icon: <PictureOutlined />, requireAuth: true },
  { path: '/create/video', labelKey: 'nav.video', icon: <VideoCameraOutlined />, requireAuth: true },
  { path: '/create/ad', labelKey: 'nav.ad', icon: <NotificationOutlined />, requireAuth: true },
  { path: '/works', labelKey: 'nav.works', icon: <FolderOpenOutlined />, requireAuth: true },
  { path: '/tasks', labelKey: 'nav.tasks', icon: <DeploymentUnitOutlined />, requireAuth: true },
  { path: '/gallery', labelKey: 'nav.gallery', icon: <AppstoreOutlined /> },
  { path: '/pricing', labelKey: 'nav.pricing', icon: <DollarOutlined /> },
]

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const location = useLocation()
  const { user, isAuthenticated, logout } = useAuthStore()
  const { language, t } = useI18n()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const visibleItems = useMemo(
    () => navItems.filter((item) => !item.requireAuth || isAuthenticated),
    [isAuthenticated]
  )

  const headerItems = useMemo(() => visibleItems.slice(0, 5), [visibleItems])

  const isItemActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/'
    }
    return location.pathname === path || location.pathname.startsWith(`${path}/`)
  }

  const closeMobileMenu = () => setMobileMenuOpen(false)

  return (
    <div className="app-shell min-h-screen">
      <MeteorField />

      <header className="sticky top-0 z-40 border-b border-[rgba(132,179,219,0.24)] bg-[rgba(3,9,18,0.78)] backdrop-blur-xl">
        <div className="mx-auto flex h-20 w-full max-w-[1360px] items-center justify-between gap-3 px-4 lg:px-8">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => setMobileMenuOpen((open) => !open)}
              className="inline-flex h-10 w-10 items-center justify-center border border-[rgba(132,179,219,0.34)] bg-[rgba(5,16,30,0.92)] text-[#d9f2ff] lg:hidden"
              aria-label={t('layout.mobileMenuToggle')}
            >
              {mobileMenuOpen ? <CloseOutlined /> : <MenuOutlined />}
            </button>

            <Link to="/" className="flex items-center">
              <div>
                <p className="brand-gradient text-[1.55rem] font-bold leading-none">MOJO</p>
                <p className="text-[10px] font-semibold uppercase tracking-[0.24em] text-[#7da5c8]">
                  Creative Orbit Lab
                </p>
              </div>
            </Link>
          </div>

          <nav className="hidden items-center gap-2 lg:flex">
            {headerItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-chip ${isItemActive(item.path) ? 'nav-chip-active' : ''}`}
              >
                <span className="text-[14px] leading-none">{item.icon}</span>
                <span>{t(item.labelKey)}</span>
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-3">
            <LanguageSwitcher className="hidden sm:inline-flex" />
            {isAuthenticated ? (
              <>
                <Link
                  to="/account"
                  className="hidden border border-[rgba(132,179,219,0.3)] bg-[rgba(8,20,38,0.84)] px-3 py-1 text-sm font-medium text-[#daf1ff] sm:inline-flex"
                >
                  {user?.nickname || t('layout.accountDefault')}
                </Link>
                <span className="hidden border border-[rgba(120,238,255,0.4)] bg-[rgba(9,34,45,0.7)] px-3 py-1 text-sm font-semibold text-[#9ff4ff] sm:inline-flex">
                  {t('layout.balance')} {t('common.currency')}
                  {toLocalizedAmount(user?.balance ?? 0, language, { zhFractionDigits: 2, enFractionDigits: 2 })}
                </span>
                <button
                  type="button"
                  onClick={logout}
                  className="border border-[rgba(132,179,219,0.34)] bg-[rgba(5,16,30,0.92)] px-4 py-2 text-sm font-semibold text-[#d9f2ff] transition hover:border-[rgba(156,211,255,0.54)] hover:bg-[rgba(11,29,50,0.92)]"
                >
                  {t('layout.logout')}
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="border border-[rgba(132,179,219,0.34)] bg-[rgba(5,16,30,0.9)] px-4 py-2 text-sm font-semibold text-[#d9f2ff] transition hover:border-[rgba(156,211,255,0.54)] hover:bg-[rgba(11,29,50,0.92)]"
                >
                  {t('layout.login')}
                </Link>
                <Link
                  to="/register"
                  className="border border-[rgba(151,232,255,0.52)] bg-gradient-to-r from-[#12435d] to-[#2ea9d3] px-4 py-2 text-sm font-semibold text-[#f5fbff] transition hover:brightness-110"
                >
                  {t('layout.register')}
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      <div className="mx-auto flex w-full max-w-[1360px] gap-6 px-4 pb-8 pt-6 lg:px-8 lg:pt-8">
        <aside
          className={`fixed inset-x-4 top-[92px] z-30 border border-[rgba(132,179,219,0.3)] bg-[rgba(4,14,28,0.95)] p-4 backdrop-blur-lg transition lg:sticky lg:top-24 lg:block lg:h-[calc(100vh-8rem)] lg:w-64 lg:flex-none lg:overflow-y-auto ${
            mobileMenuOpen ? 'block' : 'hidden'
          }`}
        >
          <div className="mb-3 flex items-center justify-between px-2">
            <p className="text-xs font-bold uppercase tracking-[0.24em] text-[#8ab3d6]">{t('layout.navigation')}</p>
            <LanguageSwitcher className="sm:hidden" />
          </div>
          <nav className="space-y-1">
            {visibleItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                onClick={closeMobileMenu}
                className={`group flex items-center gap-3 border-l px-3 py-2.5 text-sm font-medium transition ${
                  isItemActive(item.path)
                    ? 'border-[rgba(157,227,255,0.9)] bg-[rgba(11,36,56,0.86)] text-[#eaf8ff]'
                    : 'border-[rgba(132,179,219,0.16)] text-[#8eb1ce] hover:border-[rgba(151,232,255,0.44)] hover:bg-[rgba(7,24,40,0.82)] hover:text-[#dff4ff]'
                }`}
              >
                <span className="text-[15px] leading-none">{item.icon}</span>
                <span>{t(item.labelKey)}</span>
              </Link>
            ))}
          </nav>
        </aside>

        <main className="min-w-0 flex-1">
          <div className="panel-surface page-enter">{children}</div>
        </main>
      </div>

      {mobileMenuOpen && (
        <button
          type="button"
          className="fixed inset-0 z-20 bg-[rgba(2,7,14,0.6)] backdrop-blur-[2px] lg:hidden"
          onClick={closeMobileMenu}
          aria-label={t('layout.closeMenu')}
        />
      )}
    </div>
  )
}

export default Layout
