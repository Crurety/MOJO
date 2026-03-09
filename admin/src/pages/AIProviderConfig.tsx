import React, { useEffect, useMemo, useState } from 'react'
import { ApiOutlined, RocketOutlined, ThunderboltOutlined } from '@ant-design/icons'
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

const providerDescriptions: Record<ProviderKey, { zh: string; en: string }> = {
  openai: {
    zh: '配置文本与多模态模型能力。',
    en: 'Configure text and multimodal model capabilities.',
  },
  stability: {
    zh: '配置图像生成引擎和服务地址。',
    en: 'Configure image generation engine and service endpoint.',
  },
  runway: {
    zh: '配置视频生成服务连接信息。',
    en: 'Configure video generation service connection settings.',
  },
}

const providerIcons: Record<ProviderKey, React.ReactNode> = {
  openai: <ApiOutlined />,
  stability: <ThunderboltOutlined />,
  runway: <RocketOutlined />,
}

const providerList: ProviderKey[] = ['openai', 'stability', 'runway']

const AIProviderConfig: React.FC = () => {
  const { t, language } = useI18n()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState<Record<ProviderKey, boolean>>({
    openai: false,
    stability: false,
    runway: false,
  })
  const [configs, setConfigs] = useState<Record<ProviderKey, ProviderConfig> | null>(null)
  const [drafts, setDrafts] = useState<Record<ProviderKey, ProviderDraft> | null>(null)
  const [message, setMessage] = useState<{ tone: 'success' | 'error'; text: string } | null>(null)

  const loadConfigs = async () => {
    setLoading(true)
    setMessage(null)
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
      setMessage({
        tone: 'error',
        text: language === 'zh' ? '加载服务商配置失败，请稍后重试。' : 'Failed to load provider settings.',
      })
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

  const getStatusText = (enabled: boolean) => {
    if (language === 'zh') {
      return enabled ? '已启用' : '未启用'
    }
    return enabled ? 'Enabled' : 'Disabled'
  }

  const hasProviderChanges = (provider: ProviderKey) => {
    if (!drafts || !configs) return false

    const draft = drafts[provider]
    const config = configs[provider]

    const keyChanged = Boolean(draft.api_key.trim())
    const baseChanged = (draft.api_base || '') !== (config.api_base || '')
    const modelChanged = provider === 'openai' ? (draft.model || '') !== (config.model || '') : false
    const engineChanged = provider === 'stability' ? (draft.engine || '') !== (config.engine || '') : false

    return keyChanged || baseChanged || modelChanged || engineChanged
  }

  const summary = useMemo(() => {
    if (!configs || !drafts) {
      return { enabled: 0, configured: 0, total: providerList.length }
    }

    let enabled = 0
    let configured = 0

    providerList.forEach((provider) => {
      if (configs[provider].enabled) enabled += 1
      if (drafts[provider].api_key_masked) configured += 1
    })

    return {
      enabled,
      configured,
      total: providerList.length,
    }
  }, [configs, drafts])

  const saveProvider = async (provider: ProviderKey) => {
    if (!drafts) return

    setSaving((prev) => ({ ...prev, [provider]: true }))
    setMessage(null)

    const draft = drafts[provider]
    const payload: Record<string, string> = {
      api_base: draft.api_base || '',
    }

    if (draft.model !== undefined) payload.model = draft.model || ''
    if (draft.engine !== undefined) payload.engine = draft.engine || ''
    if (draft.api_key.trim()) payload.api_key = draft.api_key.trim()

    try {
      await adminApi.updateAIProviderConfig(provider, payload)
      setMessage({
        tone: 'success',
        text:
          language === 'zh'
            ? `${providerTitles[provider]} 配置已更新。`
            : `${providerTitles[provider]} settings updated.`,
      })
      await loadConfigs()
    } catch (error) {
      console.error('Failed to update AI provider config:', error)
      setMessage({
        tone: 'error',
        text:
          language === 'zh' ? `${providerTitles[provider]} 更新失败，请检查后重试。` : `${providerTitles[provider]} update failed.`,
      })
    } finally {
      setSaving((prev) => ({ ...prev, [provider]: false }))
    }
  }

  if (loading || !configs || !drafts) {
    return (
      <div className="admin-loader">
        <div className="admin-loader-spinner"></div>
        <p className="admin-loader-text">{t('common.loading')}</p>
      </div>
    )
  }

  const renderProviderCard = (provider: ProviderKey) => {
    const config = configs[provider]
    const draft = drafts[provider]
    const hasChanges = hasProviderChanges(provider)
    const keyConfigured = Boolean(draft.api_key_masked)

    return (
      <article key={provider} className={`admin-panel admin-ai-card ${config.enabled ? 'is-enabled' : 'is-disabled'}`}>
        <header className="admin-ai-card-head">
          <div>
            <div className="admin-ai-card-title-line">
              <span className="admin-ai-provider-icon">{providerIcons[provider]}</span>
              <h2 className="admin-panel-title !mb-0">{providerTitles[provider]}</h2>
            </div>
            <p className="admin-ai-card-desc">{providerDescriptions[provider][language]}</p>
          </div>

          <div className="admin-ai-card-status">
            <span className={`admin-pill ${config.enabled ? 'admin-pill-success' : 'admin-pill-neutral'}`}>
              {getStatusText(config.enabled)}
            </span>
            <span className={`admin-ai-key-chip ${keyConfigured ? 'is-configured' : 'is-empty'}`}>
              {language === 'zh'
                ? keyConfigured
                  ? '密钥已配置'
                  : '密钥未配置'
                : keyConfigured
                  ? 'Key Configured'
                  : 'Key Missing'}
            </span>
          </div>
        </header>

        <div className="admin-ai-endpoint">
          <span className="admin-ai-endpoint-label">{language === 'zh' ? '当前 Endpoint' : 'Current Endpoint'}</span>
          <code>{draft.api_base || '-'}</code>
        </div>

        <div className="admin-ai-form-grid">
          <div className="admin-ai-field admin-ai-field-full">
            <label className="admin-label">API Key</label>
            <input
              type="password"
              value={draft.api_key}
              onChange={(e) => updateDraft(provider, 'api_key', e.target.value)}
              placeholder={
                draft.api_key_masked ||
                (language === 'zh' ? '输入新的 API Key（可留空）' : 'Enter a new API key (optional)')
              }
              className="admin-input w-full"
            />
            <p className="admin-ai-field-tip">
              {language === 'zh'
                ? '留空表示保持当前密钥不变。'
                : 'Leave empty to keep the existing key unchanged.'}
            </p>
          </div>

          <div className="admin-ai-field admin-ai-field-full">
            <label className="admin-label">API Base URL</label>
            <input
              type="text"
              value={draft.api_base || ''}
              onChange={(e) => updateDraft(provider, 'api_base', e.target.value)}
              className="admin-input w-full"
            />
          </div>

          {provider === 'openai' && (
            <div className="admin-ai-field">
              <label className="admin-label">Model</label>
              <input
                type="text"
                value={draft.model || ''}
                onChange={(e) => updateDraft(provider, 'model', e.target.value)}
                className="admin-input w-full"
              />
            </div>
          )}

          {provider === 'stability' && (
            <div className="admin-ai-field">
              <label className="admin-label">Engine</label>
              <input
                type="text"
                value={draft.engine || ''}
                onChange={(e) => updateDraft(provider, 'engine', e.target.value)}
                className="admin-input w-full"
              />
            </div>
          )}
        </div>

        <footer className="admin-ai-card-foot">
          <p className="admin-ai-change-tip">
            {hasChanges
              ? language === 'zh'
                ? '检测到未保存变更。'
                : 'Unsaved changes detected.'
              : language === 'zh'
                ? '当前配置已同步。'
                : 'Configuration is up to date.'}
          </p>

          <span className={`admin-pill ${hasChanges ? 'admin-pill-warning' : 'admin-pill-success'}`}>
            {hasChanges ? (language === 'zh' ? '待保存' : 'Pending Save') : language === 'zh' ? '已保存' : 'Saved'}
          </span>

          <button
            type="button"
            onClick={() => void saveProvider(provider)}
            disabled={saving[provider] || !hasChanges}
            className="admin-btn admin-btn-primary"
          >
            {saving[provider]
              ? t('common.saving')
              : language === 'zh'
                ? `保存 ${providerTitles[provider]}`
                : `Save ${providerTitles[provider]}`}
          </button>
        </footer>
      </article>
    )
  }

  return (
    <section className="admin-page admin-ai-page space-y-4">
      <div className="admin-page-head">
        <div>
          <h1 className="admin-page-title">{t('layout.nav.aiConfig')}</h1>
          <p className="admin-page-subtitle">
            {language === 'zh'
              ? '统一管理第三方 AI 服务的 Key、Base URL 与模型参数。保存后服务会自动生效。'
              : 'Manage provider keys, base URLs, and model parameters from one operational surface.'}
          </p>
        </div>
      </div>

      {message && <div className={`admin-alert ${message.tone === 'success' ? 'is-success' : 'is-error'}`}>{message.text}</div>}

      <section className="admin-ai-summary">
        <article className="admin-ai-summary-card">
          <p className="admin-ai-summary-label">{language === 'zh' ? '服务总数' : 'Total Providers'}</p>
          <p className="admin-ai-summary-value">{summary.total}</p>
        </article>
        <article className="admin-ai-summary-card">
          <p className="admin-ai-summary-label">{language === 'zh' ? '已启用服务' : 'Enabled Providers'}</p>
          <p className="admin-ai-summary-value">{summary.enabled}</p>
        </article>
        <article className="admin-ai-summary-card">
          <p className="admin-ai-summary-label">{language === 'zh' ? '已配置密钥' : 'Configured Keys'}</p>
          <p className="admin-ai-summary-value">{summary.configured}</p>
        </article>
      </section>

      <div className="admin-ai-grid">{providerList.map(renderProviderCard)}</div>
    </section>
  )
}

export default AIProviderConfig

