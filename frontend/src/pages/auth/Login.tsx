import { useState } from 'react'
import { Button, Form, Input, Typography, message } from 'antd'
import { LockOutlined, UserOutlined } from '@ant-design/icons'
import { Link, useNavigate } from 'react-router-dom'
import { AuthShell, LanguageSwitcher } from '../../components'
import { useAuth } from '../../hooks'
import { useI18n } from '../../i18n'

const { Paragraph } = Typography

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
    <AuthShell
      eyebrow={t('auth.login.portal')}
      title={t('auth.login.title')}
      description={t('home.subtitle')}
      highlights={[t('home.workflow.step1.desc'), t('home.workflow.step2.desc'), t('home.workflow.step3.desc')]}
      toolbar={<LanguageSwitcher />}
    >
      <Paragraph className="!mb-6 !text-[#96b5cf]">{t('auth.login.failed')}</Paragraph>

      <Form name="login" onFinish={onFinish} autoComplete="off" layout="vertical">
        <Form.Item name="account" rules={[{ required: true, message: t('auth.login.accountRequired') }]}>
          <Input prefix={<UserOutlined />} placeholder={t('auth.login.accountPlaceholder')} size="large" />
        </Form.Item>

        <Form.Item name="password" rules={[{ required: true, message: t('auth.login.passwordRequired') }]}>
          <Input.Password prefix={<LockOutlined />} placeholder={t('auth.login.passwordPlaceholder')} size="large" />
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
    </AuthShell>
  )
}

export default Login
