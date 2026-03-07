import type { FrontendLanguage } from '../i18n'

// Pricing values are stored in CNY; convert to USD for English UI.
export const CNY_PER_USD = 7.2

type CurrencyFormatOptions = {
  zhFractionDigits?: number
  enFractionDigits?: number
}

export const toLocalizedAmount = (
  amountCny: number,
  language: FrontendLanguage,
  options: CurrencyFormatOptions = {}
): string => {
  const value = language === 'en' ? amountCny / CNY_PER_USD : amountCny
  const fractionDigits = language === 'en' ? (options.enFractionDigits ?? 2) : (options.zhFractionDigits ?? 0)

  return value.toFixed(fractionDigits)
}

