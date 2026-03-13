import { useState } from 'react'
import { Button, Form, Input, Typography, message } from 'antd'
import { LockOutlined, MailOutlined, UserOutlined } from '@ant-design/icons'
import { Link, useNavigate } from 'react-router-dom'
import { AuthShell, LanguageSwitcher } from '../../components'
import { useAuth } from '../../hooks'
import { useI18n } from '../../i18n'

const { Paragraph } = Typography

const Register = () => {
  const navigate = useNavigate()
  const { register } = useAuth()
  const { t } = useI18n()
  const [loading, setLoading] = useState(false)

  const onFinish = async (values: { email: string; phone?: string; password: string }) => {
    setLoading(true)
    try {
      const normalizedPhone = values.phone?.trim()
      const result = await register({
        email: values.email.trim(),
        phone: normalizedPhone || undefined,
        password: values.password,
        nickname: values.email.split('@')[0],
      })
      if (result && result.success) {
        message.success(t('auth.register.success'))
        navigate('/login')
      } else {
        message.error(t('auth.register.failed'))
      }
    } catch (error: any) {
      console.error(error)
      const detail = error?.response?.data?.detail
      if (Array.isArray(detail) && detail[0]?.msg) {
        message.error(detail[0].msg)
      } else if (typeof detail === 'string') {
        message.error(detail)
      } else {
        message.error(t('auth.register.error'))
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthShell
      eyebrow={t('auth.register.portal')}
      title={t('auth.register.title')}
      description={t('home.readySubtitle')}
      highlights={[t('home.feature.script.desc'), t('home.feature.image.desc'), t('home.feature.video.desc')]}
      toolbar={<LanguageSwitcher />}
    >
      <Paragraph className="!mb-6 !text-[#96b5cf]">{t('auth.register.haveAccount')}</Paragraph>

      <Form name="register" onFinish={onFinish} autoComplete="off" layout="vertical">
        <Form.Item
          name="email"
          rules={[
            { required: true, message: t('auth.register.emailRequired') },
            { type: 'email', message: t('auth.register.emailInvalid') },
          ]}
        >
          <Input prefix={<MailOutlined />} placeholder={t('auth.register.emailPlaceholder')} size="large" />
        </Form.Item>

        <Form.Item name="phone" rules={[{ pattern: /^1[3-9]\d{9}$/, message: t('auth.register.phoneInvalid') }]}>
          <Input prefix={<UserOutlined />} placeholder={t('auth.register.phonePlaceholder')} size="large" />
        </Form.Item>

        <Form.Item
          name="password"
          rules={[
            { required: true, message: t('auth.register.passwordRequired') },
            { pattern: /^(?=.*[A-Za-z])(?=.*\d)[^\s]{6,}$/, message: t('auth.register.passwordMin') },
          ]}
        >
          <Input.Password prefix={<LockOutlined />} placeholder={t('auth.register.passwordPlaceholder')} size="large" />
        </Form.Item>

        <Form.Item
          name="confirmPassword"
          dependencies={['password']}
          rules={[
            { required: true, message: t('auth.register.confirmRequired') },
            ({ getFieldValue }) => ({
              validator(_, value) {
                if (!value || getFieldValue('password') === value) {
                  return Promise.resolve()
                }
                return Promise.reject(new Error(t('auth.register.passwordMismatch')))
              },
            }),
          ]}
        >
          <Input.Password prefix={<LockOutlined />} placeholder={t('auth.register.confirmPlaceholder')} size="large" />
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" block size="large" loading={loading}>
            {t('auth.register.submit')}
          </Button>
        </Form.Item>

        <div className="text-center text-sm text-[#8caac5]">
          {t('auth.register.haveAccount')}
          <Link to="/login" className="ml-1 font-medium text-[#9ce9ff] hover:text-[#d8f6ff]">
            {t('auth.register.loginNow')}
          </Link>
        </div>
      </Form>
    </AuthShell>
  )
}

export default Register
