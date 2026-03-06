import React, { useState } from 'react'
import { Layout, Card, Button } from '../components'
import { usePayment, PRICING_PLANS, PAYMENT_METHODS } from '../hooks'
import { useAuth } from '../hooks'
import { useNavigate } from 'react-router-dom'

const Pricing: React.FC = () => {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuth()
  const { createPermissionOrder, loading } = usePayment()
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null)
  const [selectedMode, setSelectedMode] = useState<'per_use' | 'monthly' | 'yearly'>('per_use')
  const [selectedMethod, setSelectedMethod] = useState<string>('wechat')
  const [showPaymentModal, setShowPaymentModal] = useState(false)

  const handleSelectPlan = (plan: string) => {
    if (!isAuthenticated) {
      navigate('/login')
      return
    }
    setSelectedPlan(plan)
    setShowPaymentModal(true)
  }

  const handlePayment = async () => {
    if (!selectedPlan) return

    const result = await createPermissionOrder({
      permission_type: selectedPlan,
      payment_mode: selectedMode,
      payment_method: selectedMethod,
    })

    if (result.success) {
      const { pay_url } = result.data as any
      if (pay_url) {
        window.open(pay_url, '_blank')
      }
      setShowPaymentModal(false)
      navigate('/tasks')
    }
  }

  const getPrice = (plan: string, mode: 'per_use' | 'monthly' | 'yearly') => {
    const planData = PRICING_PLANS[plan as keyof typeof PRICING_PLANS]
    if (!planData) return 0
    return planData[mode]
  }

  return (
    <Layout>
      <div className="space-y-12">
        <section className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">价格方案</h1>
          <p className="text-xl text-gray-600">选择适合您的付费模式</p>
        </section>

        <div className="flex justify-center space-x-4">
          {(['per_use', 'monthly', 'yearly'] as const).map((mode) => (
            <button
              key={mode}
              className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                selectedMode === mode
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
              onClick={() => setSelectedMode(mode)}
            >
              {mode === 'per_use' ? '按次付费' : mode === 'monthly' ? '月度订阅' : '年度订阅'}
            </button>
          ))}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {Object.entries(PRICING_PLANS).map(([key, plan]) => (
            <Card
              key={key}
              className={`h-full transition-all ${
                selectedPlan === key ? 'ring-2 ring-indigo-600' : ''
              }`}
            >
              <div className="text-center">
                <span className="text-5xl mb-4 block">{plan.icon}</span>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{plan.name}</h3>
                <div className="mb-4">
                  <span className="text-3xl font-bold text-indigo-600">
                    ¥{getPrice(key, selectedMode)}
                  </span>
                  <span className="text-gray-500">
                    {selectedMode === 'per_use' ? '/次' : selectedMode === 'monthly' ? '/月' : '/年'}
                  </span>
                </div>
                <p className="text-gray-600 text-sm mb-6">{plan.description}</p>
                <Button
                  onClick={() => handleSelectPlan(key)}
                  className="w-full"
                  variant={selectedPlan === key ? 'primary' : 'secondary'}
                >
                  {selectedMode === 'per_use' ? '购买' : '订阅'}
                </Button>
              </div>
            </Card>
          ))}
        </div>

        {showPaymentModal && (
          <Card className="max-w-md mx-auto">
            <h2 className="text-xl font-bold text-gray-900 mb-6">选择支付方式</h2>
            <div className="space-y-4">
              {PAYMENT_METHODS.map((method) => (
                <button
                  key={method.value}
                  className={`w-full flex items-center justify-between p-4 border rounded-lg transition-colors ${
                    selectedMethod === method.value
                      ? 'border-indigo-600 bg-indigo-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setSelectedMethod(method.value)}
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{method.icon}</span>
                    <span className="font-medium">{method.label}</span>
                  </div>
                  {selectedMethod === method.value && (
                    <span className="text-indigo-600">✓</span>
                  )}
                </button>
              ))}
            </div>
            <div className="mt-6 flex space-x-4">
              <Button variant="secondary" onClick={() => setShowPaymentModal(false)}>
                取消
              </Button>
              <Button onClick={handlePayment} loading={loading}>
                确认支付
              </Button>
            </div>
          </Card>
        )}
      </div>
    </Layout>
  )
}

export default Pricing
