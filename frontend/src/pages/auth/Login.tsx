import { useState } from 'react'
import { Button, Form, Input, Typography, message } from 'antd'
import { LockOutlined, UserOutlined } from '@ant-design/icons'
import { Link, useNavigate } from 'react-router-dom'
import { LanguageSwitcher } from '../../components'
import { useAuth } from '../../hooks'
import { useI18n } from '../../i18n'

const { Title } = Typography

const Login = () => {
  const navigate = useNavigate()
  const { login } = useAuth()
  const { t } = useI18n()
  const [loading, setLoading] = useState(false)

  const onFinish = async (values: { account: string; password: string }) => {
    setLoading(true)
    try {
      const result = await login(values.account, values.password)
      if (result && result.success) {
        message.success(t('auth.login.success'))
        navigate('/')
      } else {
        message.error(result?.message || t('auth.login.failed'))
      }
    } catch (error) {
      console.error(error)
      message.error(t('auth.login.error'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto flex min-h-[68vh] w-full max-w-md items-center">
      <section className="section-shell w-full border border-[rgba(132,179,219,0.36)] px-6 py-7 sm:px-8 sm:py-8">
        <div className="mb-6 text-center">
          <div className="mb-3 flex justify-end">
            <LanguageSwitcher />
          </div>
          <p className="text-xs font-bold uppercase tracking-[0.22em] text-[#80a9cc]">{t('auth.login.portal')}</p>
          <Title level={2} className="!mb-0 !mt-2 !text-[#f2fbff]">
            {t('auth.login.title')}
          </Title>
        </div>

        <Form name="login" onFinish={onFinish} autoComplete="off" layout="vertical">
          <Form.Item name="account" rules={[{ required: true, message: t('auth.login.accountRequired') }]}>
            <Input prefix={<UserOutlined />} placeholder={t('auth.login.accountPlaceholder')} size="large" />
          </Form.Item>

          <Form.Item name="password" rules={[{ required: true, message: t('auth.login.passwordRequired') }]}>
            <Input.Password
              prefix={<LockOutlined />}
              placeholder={t('auth.login.passwordPlaceholder')}
              size="large"
            />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" block size="large" loading={loading}>
              {t('auth.login.submit')}
            </Button>
          </Form.Item>

          <div className="text-center text-sm text-[#8caac5]">
            <Link to="/register" className="font-medium text-[#9ce9ff] hover:text-[#d8f6ff]">
              {t('auth.login.registerNow')}
            </Link>
            <span className="mx-2">|</span>
            <Link to="/forgot-password" className="font-medium text-[#9ce9ff] hover:text-[#d8f6ff]">
              {t('auth.login.forgotPassword')}
            </Link>
          </div>
        </Form>
      </section>
    </div>
  )
}

export default Login
