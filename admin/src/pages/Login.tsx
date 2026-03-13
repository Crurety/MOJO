import React, { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authApi } from '../api'
import LanguageSwitcher from '../components/LanguageSwitcher'
import { useI18n } from '../i18n'
import { useAuthStore } from '../store'

const Login: React.FC = () => {
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()
  const { language, t } = useI18n()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    account: '',
    password: '',
  })
  const [error, setError] = useState('')
  const highlights = useMemo(
    () =>
      language === 'zh'
        ? ['统一管理用户与订单', '实时查看收入与关键指标', '集中配置 OpenAI / DeepSeek / Stability / Runway']
        : ['Manage users and orders from one console', 'Track revenue and KPI movement in real time', 'Configure OpenAI / DeepSeek / Stability / Runway centrally'],
    [language]
  )

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await authApi.login(formData)
      if (response.user && response.token) {
        setAuth(response.user, response.token.access_token)
        navigate('/')
      } else {
        setError(t('login.failed'))
      }
    } catch (requestError: any) {
      setError(requestError.response?.data?.message || t('login.retry'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="admin-auth">
      <div className="admin-auth-shell">
        <aside className="admin-auth-showcase">
          <p className="admin-auth-kicker">MOJO ADMIN</p>
          <h2 className="admin-auth-showcase-title">
            {language === 'zh' ? '创作平台运营中枢' : 'Control Center For Platform Operations'}
          </h2>
          <p className="admin-auth-showcase-copy">
            {language === 'zh'
              ? '从一个入口管理用户、订单、营收和模型配置，快速处理日常运营任务。'
              : 'Use one operational surface to manage users, orders, revenue, and model providers.'}
          </p>
          <ul className="admin-auth-feature-list">
            {highlights.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </aside>

        <div className="admin-auth-card">
          <div className="admin-auth-toolbar">
            <LanguageSwitcher />
          </div>

          <div className="admin-auth-head">
            <h1 className="admin-auth-title">{t('login.title')}</h1>
            <p className="admin-auth-subtitle">{t('login.subtitle')}</p>
          </div>

          {error && (
            <div className="admin-alert is-error mb-4" role="alert">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="admin-field">
              <label className="admin-label" htmlFor="admin-account">
                {t('login.accountLabel')}
              </label>
              <input
                id="admin-account"
                type="text"
                value={formData.account}
                onChange={(e) => setFormData({ ...formData, account: e.target.value })}
                className="admin-input w-full"
                placeholder={t('login.accountPlaceholder')}
                autoComplete="username"
                required
              />
            </div>

            <div className="admin-field">
              <label className="admin-label" htmlFor="admin-password">
                {t('login.passwordLabel')}
              </label>
              <input
                id="admin-password"
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="admin-input w-full"
                placeholder={t('login.passwordPlaceholder')}
                autoComplete="current-password"
                required
              />
            </div>

            <button type="submit" disabled={loading} className="admin-btn admin-btn-primary w-full">
              {loading ? t('login.submitting') : t('login.submit')}
            </button>
          </form>

          <p className="admin-auth-tip">
            {language === 'zh'
              ? '提示：请使用管理员账户登录，操作日志将被记录。'
              : 'Tip: Sign in with an administrator account. All management actions are logged.'}
          </p>
        </div>
      </div>
    </div>
  )
}

export default Login
