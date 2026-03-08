import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authApi } from '../api'
import LanguageSwitcher from '../components/LanguageSwitcher'
import { useI18n } from '../i18n'
import { useAuthStore } from '../store'

const Login: React.FC = () => {
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()
  const { t } = useI18n()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    account: '',
    password: '',
  })
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await authApi.login(formData)
      if (response.user && response.token) {
        setAuth(response.user, response.token.access_token)
        navigate('/admin')
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
      <div className="admin-auth-card">
        <div className="mb-5 flex justify-end">
          <LanguageSwitcher />
        </div>

        <div className="admin-auth-head">
          <h1 className="admin-auth-title">{t('login.title')}</h1>
          <p className="admin-auth-subtitle">{t('login.subtitle')}</p>
        </div>

        {error && <div className="admin-alert is-error mb-4">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="admin-field">
            <label className="admin-label">{t('login.accountLabel')}</label>
            <input
              type="text"
              value={formData.account}
              onChange={(e) => setFormData({ ...formData, account: e.target.value })}
              className="admin-input w-full"
              placeholder={t('login.accountPlaceholder')}
            />
          </div>

          <div className="admin-field">
            <label className="admin-label">{t('login.passwordLabel')}</label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              className="admin-input w-full"
              placeholder={t('login.passwordPlaceholder')}
            />
          </div>

          <button type="submit" disabled={loading} className="admin-btn admin-btn-primary w-full">
            {loading ? t('login.submitting') : t('login.submit')}
          </button>
        </form>
      </div>
    </div>
  )
}

export default Login
