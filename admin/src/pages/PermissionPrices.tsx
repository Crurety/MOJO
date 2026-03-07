import React, { useEffect, useState } from 'react'
import { adminApi } from '../api'
import { useI18n } from '../i18n'

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
  const { t } = useI18n()

  useEffect(() => {
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

    loadPrices()
  }, [])

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
        [mode]: Number.parseFloat(value) || 0,
      },
    })
  }

  const permissionTypes = [
    { key: 'script', name: t('permission.type.script') },
    { key: 'image', name: t('permission.type.image') },
    { key: 'video', name: t('permission.type.video') },
    { key: 'ad', name: t('permission.type.ad') },
  ]

  if (loading) {
    return (
      <div className="py-12 text-center">
        <div className="mx-auto h-12 w-12 animate-spin rounded-full border-b-2 border-indigo-600"></div>
        <p className="mt-4 text-gray-600">{t('common.loading')}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">{t('permission.title')}</h1>

      <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        {success && <div className="mb-4 rounded-md bg-green-50 p-3 text-green-600">{t('permission.saveSuccess')}</div>}

        <div className="overflow-x-auto">
          <table>
            <thead>
              <tr>
                <th>{t('permission.type')}</th>
                <th>{t('permission.mode.perUse')}</th>
                <th>{t('permission.mode.monthly')}</th>
                <th>{t('permission.mode.yearly')}</th>
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
                      className="w-24 rounded-md border px-2 py-1 text-sm"
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      value={prices[type.key].monthly}
                      onChange={(e) => handlePriceChange(type.key, 'monthly', e.target.value)}
                      className="w-24 rounded-md border px-2 py-1 text-sm"
                    />
                  </td>
                  <td>
                    <input
                      type="number"
                      min="0"
                      step="0.01"
                      value={prices[type.key].yearly}
                      onChange={(e) => handlePriceChange(type.key, 'yearly', e.target.value)}
                      className="w-24 rounded-md border px-2 py-1 text-sm"
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
            className="rounded-md bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700 disabled:bg-indigo-300"
            type="button"
          >
            {saving ? t('common.saving') : t('common.save')}
          </button>
        </div>
      </div>
    </div>
  )
}

export default PermissionPrices

