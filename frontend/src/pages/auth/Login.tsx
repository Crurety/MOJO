import { useState } from 'react'
import { Form, Input, Button, Card, Typography, message } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks'

const { Title } = Typography

const Login = () => {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [loading, setLoading] = useState(false)

  const onFinish = async (values: any) => {
    setLoading(true)
    try {
      const result = await login(values.account, values.password)
      if (result && result.success) {
        message.success('登录成功')
        navigate('/')
      } else {
        message.error(result?.message || '登录失败，请检查账号密码')
      }
    } catch (error) {
      console.error(error)
      message.error('登录发生错误')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <Card className="w-full max-w-md">
        <Title level={2} className="text-center mb-8">登录</Title>
        <Form
          name="login"
          onFinish={onFinish}
          autoComplete="off"
          layout="vertical"
        >
          <Form.Item
            name="account"
            rules={[{ required: true, message: '请输入邮箱或手机号' }]}
          >
            <Input prefix={<UserOutlined />} placeholder="邮箱或手机号" size="large" />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="密码" size="large" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" block size="large" loading={loading}>
              登录
            </Button>
          </Form.Item>

          <div className="text-center">
            <Link to="/register" className="text-blue-500">立即注册</Link>
            <span className="mx-2">|</span>
            <Link to="/forgot-password" className="text-blue-500">忘记密码</Link>
          </div>
        </Form>
      </Card>
    </div>
  )
}

export default Login
