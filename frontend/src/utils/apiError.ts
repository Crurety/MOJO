import { translateStatic } from '../i18n'

type ApiErrorPayload = {
  detail?: unknown
  message?: unknown
  error_code?: unknown
  error_params?: Record<string, string | number>
}

export const resolveApiErrorMessage = (error: any, fallback: string) => {
  const data = (error?.response?.data || {}) as ApiErrorPayload
  const detail = data.detail

  if (typeof data.error_code === 'string') {
    return translateStatic(`api.error.${data.error_code}`, data.error_params)
  }

  if (Array.isArray(detail) && detail[0]?.msg) return detail[0].msg as string
  if (typeof detail === 'string') return detail
  if (typeof data.message === 'string') return data.message
  return fallback
}
