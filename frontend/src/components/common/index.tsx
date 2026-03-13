import React from 'react'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  children: React.ReactNode
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  children,
  className = '',
  disabled,
  ...props
}) => {
  const baseStyles =
    'inline-flex items-center justify-center gap-2 border font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-cyan-300/60 disabled:cursor-not-allowed disabled:opacity-50'

  const variants = {
    primary:
      'border-[rgba(151,232,255,0.62)] bg-gradient-to-r from-[#12435d] to-[#2ea9d3] text-[#f5fbff] hover:brightness-110',
    secondary:
      'border-[rgba(132,179,219,0.34)] bg-[rgba(6,18,34,0.82)] text-[#d7ecff] hover:border-[rgba(156,211,255,0.6)] hover:bg-[rgba(11,29,50,0.9)]',
    danger:
      'border-[rgba(255,143,160,0.55)] bg-gradient-to-r from-[#7c1b30] to-[#c63d55] text-white hover:brightness-110',
    ghost:
      'border-transparent bg-transparent text-[#89aeca] hover:border-[rgba(132,179,219,0.28)] hover:bg-[rgba(9,26,43,0.7)] hover:text-[#e5f5ff]',
  }

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base',
  }

  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <svg className="-ml-1 mr-1 h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.37 0 0 5.37 0 12h4zm2 5.29A7.96 7.96 0 014 12H0c0 3.04 1.14 5.82 3 7.94l3-2.65z"
          />
        </svg>
      )}
      {children}
    </button>
  )
}

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
}

export const Input: React.FC<InputProps> = ({ label, error, className = '', ...props }) => {
  return (
    <div className="w-full">
      {label && <label className="mb-1 block text-sm font-medium text-[#9eb8cf]">{label}</label>}
      <input
        className={`w-full border bg-[rgba(4,14,28,0.85)] px-3 py-2 text-[#e8f4ff] focus:border-[rgba(151,232,255,0.6)] focus:outline-none focus:ring-2 focus:ring-[rgba(151,232,255,0.32)] ${
          error ? 'border-rose-400/80' : 'border-[rgba(132,179,219,0.3)]'
        } ${className}`}
        {...props}
      />
      {error && <p className="mt-1 text-sm text-rose-300">{error}</p>}
    </div>
  )
}

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
  error?: string
}

export const Textarea: React.FC<TextareaProps> = ({ label, error, className = '', ...props }) => {
  return (
    <div className="w-full">
      {label && <label className="mb-1 block text-sm font-medium text-[#9eb8cf]">{label}</label>}
      <textarea
        className={`w-full border bg-[rgba(4,14,28,0.85)] px-3 py-2 text-[#e8f4ff] focus:border-[rgba(151,232,255,0.6)] focus:outline-none focus:ring-2 focus:ring-[rgba(151,232,255,0.32)] ${
          error ? 'border-rose-400/80' : 'border-[rgba(132,179,219,0.3)]'
        } ${className}`}
        {...props}
      />
      {error && <p className="mt-1 text-sm text-rose-300">{error}</p>}
    </div>
  )
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  error?: string
  options: { value: string; label: string }[]
}

export const Select: React.FC<SelectProps> = ({
  label,
  error,
  options,
  className = '',
  ...props
}) => {
  return (
    <div className="w-full">
      {label && <label className="mb-1 block text-sm font-medium text-[#9eb8cf]">{label}</label>}
      <select
        className={`w-full border bg-[rgba(4,14,28,0.85)] px-3 py-2 text-[#e8f4ff] focus:border-[rgba(151,232,255,0.6)] focus:outline-none focus:ring-2 focus:ring-[rgba(151,232,255,0.32)] ${
          error ? 'border-rose-400/80' : 'border-[rgba(132,179,219,0.3)]'
        } ${className}`}
        {...props}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && <p className="mt-1 text-sm text-rose-300">{error}</p>}
    </div>
  )
}

interface CardProps {
  title?: string
  children: React.ReactNode
  className?: string
}

export const Card: React.FC<CardProps> = ({ title, children, className = '' }) => {
  return (
    <div className={`surface-card ${className}`}>
      {title && (
        <div className="border-b border-[rgba(132,179,219,0.28)] px-6 py-4">
          <h3 className="text-lg font-semibold text-[#e8f4ff]">{title}</h3>
        </div>
      )}
      <div className="px-6 py-4 text-[#a9c4da]">{children}</div>
    </div>
  )
}

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  children: React.ReactNode
}

export const Modal: React.FC<ModalProps> = ({ isOpen, onClose, title, children }) => {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center px-4">
        <div className="fixed inset-0 bg-[rgba(2,7,14,0.72)] backdrop-blur-sm" onClick={onClose} />
        <div className="surface-card relative w-full max-w-lg border border-[rgba(132,179,219,0.36)] bg-[rgba(4,14,28,0.95)]">
          {title && (
            <div className="border-b border-[rgba(132,179,219,0.28)] px-6 py-4">
              <h3 className="text-lg font-semibold text-[#e8f4ff]">{title}</h3>
              <button
                onClick={onClose}
                className="absolute right-4 top-4 text-[#8eb1ce] transition hover:text-[#dff4ff]"
                type="button"
              >
                x
              </button>
            </div>
          )}
          <div className="px-6 py-4 text-[#a9c4da]">{children}</div>
        </div>
      </div>
    </div>
  )
}

interface ProgressProps {
  value: number
  max?: number
  label?: string
}

export const Progress: React.FC<ProgressProps> = ({ value, max = 100, label }) => {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100))

  return (
    <div className="w-full">
      {label && (
        <div className="mb-1 flex justify-between">
          <span className="text-sm font-medium text-[#a7c2d9]">{label}</span>
          <span className="text-sm text-[#7f9ab3]">{Math.round(percentage)}%</span>
        </div>
      )}
      <div className="h-2 w-full bg-[rgba(10,29,47,0.82)]">
        <div
          className="h-2 bg-gradient-to-r from-[#1d6e90] to-[#4bd2fa] transition-all duration-300"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}

interface BadgeProps {
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info'
  children: React.ReactNode
}

export const Badge: React.FC<BadgeProps> = ({ variant = 'default', children }) => {
  const variants = {
    default: 'border border-[rgba(132,179,219,0.3)] bg-[rgba(8,20,38,0.8)] text-[#a8c8e1]',
    success: 'border border-emerald-300/30 bg-emerald-900/20 text-emerald-200',
    warning: 'border border-amber-300/30 bg-amber-900/20 text-amber-200',
    danger: 'border border-rose-300/35 bg-rose-900/20 text-rose-200',
    info: 'border border-cyan-300/35 bg-cyan-900/20 text-cyan-200',
  }

  return <span className={`inline-flex items-center px-2.5 py-0.5 text-xs font-medium ${variants[variant]}`}>{children}</span>
}

export { default as LanguageSwitcher } from './LanguageSwitcher'
export { default as AuthShell } from './AuthShell'
export {
  EmptyState,
  FormMeta,
  PageHeader,
  ResultPanel,
  StatStrip,
  SurfaceCard,
  TaskReceipt,
} from './PageScaffold'
