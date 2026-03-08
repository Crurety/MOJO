import React, { useEffect, useState } from 'react'
import { adminApi } from '../api'
import { useI18n } from '../i18n'

type ProviderKey = 'openai' | 'stability' | 'runway'

type ProviderConfig = {
  enabled: boolean
  api_key: string
  api_base: string
  model?: string
  engine?: string
}

type ProviderDraft = {
  api_key: string
  api_key_masked: string
  api_base: string
  model?: string
  engine?: string
}

const providerTitles: Record<ProviderKey, string> = {
  openai: 'OpenAI',
  stability: 'Stability',
  runway: 'Runway',
}

const AIProviderConfig: React.FC = () => {
  const { t } = useI18n()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState<Record<ProviderKey, boolean>>({
    openai: false,
    stability: false,
    runway: false,
  })
  const [configs, setConfigs] = useState<Record<ProviderKey, ProviderConfig> | null>(null)
  const [drafts, setDrafts] = useState<Record<ProviderKey, ProviderDraft> | null>(null)
  const [message, setMessage] = useState<string>('')

  const loadConfigs = async () => {
    setLoading(true)
    setMessage('')
    try {
      const data = await adminApi.getAIProviderConfigs()
      setConfigs(data)
      setDrafts({
        openai: {
          api_key: '',
          api_key_masked: data.openai.api_key || '',
          api_base: data.openai.api_base || '',
          model: data.openai.model || '',
        },
        stability: {
          api_key: '',
          api_key_masked: data.stability.api_key || '',
          api_base: data.stability.api_base || '',
          engine: data.stability.engine || '',
        },
        runway: {
          api_key: '',
          api_key_masked: data.runway.api_key || '',
          api_base: data.runway.api_base || '',
        },
      })
    } catch (error) {
      console.error('Failed to load AI provider configs:', error)
      setMessage('加载 AI 配置失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadConfigs()
  }, [])

  const updateDraft = (provider: ProviderKey, key: keyof ProviderDraft, value: string) => {
    if (!drafts) return
    setDrafts({
      ...drafts,
      [provider]: {
        ...drafts[provider],
        [key]: value,
      },
    })
  }

  const saveProvider = async (provider: ProviderKey) => {
    if (!drafts) return
    setSaving((prev) => ({ ...prev, [provider]: true }))
    setMessage('')

    const draft = drafts[provider]
    const payload: Record<string, string> = {
      api_base: draft.api_base || '',
    }

    if (draft.model !== undefined) payload.model = draft.model || ''
    if (draft.engine !== undefined) payload.engine = draft.engine || ''
    if (draft.api_key.trim()) payload.api_key = draft.api_key.trim()

    try {
      await adminApi.updateAIProviderConfig(provider, payload)
      setMessage(`${providerTitles[provider]} 配置已更新`)
      await loadConfigs()
    } catch (error) {
      console.error('Failed to update AI provider config:', error)
      setMessage(`${providerTitles[provider]} 配置更新失败`)
    } finally {
      setSaving((prev) => ({ ...prev, [provider]: false }))
    }
  }

  if (loading || !configs || !drafts) {
    return (
      <div className="py-12 text-center">
        <div className="mx-auto h-12 w-12 animate-spin rounded-full border-b-2 border-indigo-600"></div>
        <p className="mt-4 text-gray-600">{t('common.loading')}</p>
      </div>
    )
  }

  const renderProviderCard = (provider: ProviderKey) => {
    const config = configs[provider]
    const draft = drafts[provider]
    return (
      <div key={provider} className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">{providerTitles[provider]}</h2>
          <span
            className={`rounded px-2 py-1 text-xs font-medium ${
              config.enabled ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
            }`}
          >
            {config.enabled ? '已启用' : '未启用'}
          </span>
        </div>

        <div className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">API Key</label>
            <input
              type="password"
              value={draft.api_key}
              onChange={(e) => updateDraft(provider, 'api_key', e.target.value)}
              placeholder={draft.api_key_masked || '输入新的 API Key（留空保持不变）'}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">API Base URL</label>
            <input
              type="text"
              value={draft.api_base || ''}
              onChange={(e) => updateDraft(provider, 'api_base', e.target.value)}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {provider === 'openai' && (
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Model</label>
              <input
                type="text"
                value={draft.model || ''}
                onChange={(e) => updateDraft(provider, 'model', e.target.value)}
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          )}

          {provider === 'stability' && (
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">Engine</label>
              <input
                type="text"
                value={draft.engine || ''}
                onChange={(e) => updateDraft(provider, 'engine', e.target.value)}
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          )}

          <button
            type="button"
            onClick={() => void saveProvider(provider)}
            disabled={saving[provider]}
            className="rounded-md bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700 disabled:bg-indigo-300"
          >
            {saving[provider] ? t('common.saving') : t('common.save')}
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">AI API 配置</h1>
      <p className="text-sm text-gray-600">在后台配置第三方 API 的 Key/Base URL/模型参数，更新后服务会自动生效。</p>
      {message && <div className="rounded-md bg-blue-50 p-3 text-sm text-blue-700">{message}</div>}
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">{(['openai', 'stability', 'runway'] as ProviderKey[]).map(renderProviderCard)}</div>
    </div>
  )
}

export default AIProviderConfig

