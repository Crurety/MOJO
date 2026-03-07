import React from 'react'
import { useI18n } from '../i18n'

interface LanguageSwitcherProps {
  className?: string
}

const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({ className = '' }) => {
  const { language, setLanguage, t } = useI18n()

  return (
    <div
      className={`inline-flex items-center gap-1 rounded-full border border-gray-300 bg-white p-1 ${className}`}
      role="group"
      aria-label={t('common.switchLanguage')}
    >
      <button
        type="button"
        onClick={() => setLanguage('zh')}
        className={`rounded-full px-2.5 py-1 text-xs font-semibold transition ${
          language === 'zh' ? 'bg-indigo-600 text-white' : 'text-gray-600 hover:text-gray-900'
        }`}
      >
        中
      </button>
      <button
        type="button"
        onClick={() => setLanguage('en')}
        className={`rounded-full px-2.5 py-1 text-xs font-semibold transition ${
          language === 'en' ? 'bg-indigo-600 text-white' : 'text-gray-600 hover:text-gray-900'
        }`}
      >
        EN
      </button>
    </div>
  )
}

export default LanguageSwitcher

