import React, { useState, useEffect } from 'react'
import { adminApi } from '../api'

const PermissionPrices: React.FC = () => {
  const [prices, setPrices] = useState<any>({
    script: { per_use: 1, monthly: 29, yearly: 199 },
    image: { per_use: 3, monthly: 99, yearly: 699 },
    video: { per_use: 5, monthly: 199, yearly: 1399 },
    ad: { per_use: 8, monthly: 299, yearly: 1999 },
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    loadPrices()
  }, [])

  const loadPrices = async () => {
    setLoading(true)
    try {
      const data = await adminApi.getPermissionPrices()
      if (data) {
        setPrices(data)
      }
    } catch (error) {
      console.error('Failed to load permission prices:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    setSuccess(false)
    try {
      await adminApi.updatePermissionPrices(prices)
      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
    } catch (error) {
      console.error('Failed to update permission prices:', error)
    } finally {
      setSaving(false)
    }
  }

  const handlePriceChange = (type: string, mode: 'per_use' | 'monthly' | 'yearly', value: string) => {
    setPrices({
      ...prices,
      [type]: {
        ...prices[type],
        [mode]: parseFloat(value) || 0,
      },
    })
  }

  const permissionTypes = [
    { key: 'script', name: '脚本生成' },
    { key: 'image', name: '图片生成' },
    { key: 'video', name: '视频生成' },
    { key: 'ad', name: '广告设计' },
  ]

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">加载中...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">权限价格设置</h1>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        {success && (
          <div className="mb-4 p-3 bg-green-50 text-green-600 rounded-md">
            保存成功
          </div>
        )}

        <div className="overflow-x-auto">
          <table>
            <thead>
              <tr>
                <th>权限类型</th>
                <th>按次付费</th>
                <th>月度订阅</th>
                <th>年度订阅</th>
              </tr>
            </thead>
            <tbody>
              {permissionTypes.map((type) => (
                <tr key={type.key}>
                  <td>{type.name}</td>
                  <td>
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      value={prices[type.key].per_use}
                      onChange={(e) => handlePriceChange(type.key, 'per_use', e.target.value)}
                      className="w-24 px-2 py-1 border rounded-md text-sm"
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      value={prices[type.key].monthly}
                      onChange={(e) => handlePriceChange(type.key, 'monthly', e.target.value)}
                      className="w-24 px-2 py-1 border rounded-md text-sm"
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      value={prices[type.key].yearly}
                      onChange={(e) => handlePriceChange(type.key, 'yearly', e.target.value)}
                      className="w-24 px-2 py-1 border rounded-md text-sm"
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-6 flex justify-end">
          <button
            onClick={handleSave}
            disabled={saving}
            className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 disabled:bg-indigo-300"
          >
            {saving ? '保存中...' : '保存'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default PermissionPrices
