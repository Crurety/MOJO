import React from 'react'
import { useI18n } from '../i18n'

interface LanguageSwitcherProps {
  className?: string
}

const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({ className = '' }) => {
  const { language, setLanguage, t } = useI18n()

  return (
    <div className={`admin-lang-switch ${className}`.trim()} role="group" aria-label={t('common.switchLanguage')}>
      <button
        type="button"
        onClick={() => setLanguage('zh')}
        className={`admin-lang-btn ${language === 'zh' ? 'is-active' : ''}`}
      >
        ZH
      </button>
      <button
        type="button"
        onClick={() => setLanguage('en')}
        className={`admin-lang-btn ${language === 'en' ? 'is-active' : ''}`}
      >
        EN
      </button>
    </div>
  )
}

export default LanguageSwitcher
