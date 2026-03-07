import React from 'react'
import { useI18n } from '../../i18n'

interface LanguageSwitcherProps {
  className?: string
}

const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({ className = '' }) => {
  const { language, setLanguage, t } = useI18n()

  return (
    <div
      className={`inline-flex items-center gap-1 border border-[rgba(132,179,219,0.34)] bg-[rgba(6,18,34,0.88)] p-1 ${className}`}
      role="group"
      aria-label={t('common.switchLanguage')}
    >
      <button
        type="button"
        onClick={() => setLanguage('zh')}
        className={`px-2.5 py-1 text-xs font-semibold transition ${
          language === 'zh'
            ? 'border border-[rgba(151,232,255,0.55)] bg-[rgba(14,56,81,0.92)] text-[#f4fbff]'
            : 'text-[#8eb1ce] hover:text-[#dff4ff]'
        }`}
      >
        ZH
      </button>
      <button
        type="button"
        onClick={() => setLanguage('en')}
        className={`px-2.5 py-1 text-xs font-semibold transition ${
          language === 'en'
            ? 'border border-[rgba(151,232,255,0.55)] bg-[rgba(14,56,81,0.92)] text-[#f4fbff]'
            : 'text-[#8eb1ce] hover:text-[#dff4ff]'
        }`}
      >
        EN
      </button>
    </div>
  )
}

export default LanguageSwitcher
