import React from 'react'

type PageHeaderProps = {
  eyebrow?: string
  title: string
  description?: string
  actions?: React.ReactNode
}

export const PageHeader: React.FC<PageHeaderProps> = ({ eyebrow, title, description, actions }) => {
  return (
    <div className="flex flex-col gap-4 border-b border-[rgba(132,179,219,0.2)] pb-5 lg:flex-row lg:items-end lg:justify-between">
      <div className="max-w-3xl">
        {eyebrow ? (
          <p className="text-xs font-bold uppercase tracking-[0.2em] text-[#7ea8cd]">{eyebrow}</p>
        ) : null}
        <h1 className="mt-2 text-3xl font-bold text-[#f2fbff] sm:text-4xl">{title}</h1>
        {description ? <p className="mt-3 text-sm leading-7 text-[#96b5cf] sm:text-base">{description}</p> : null}
      </div>
      {actions ? <div className="flex flex-wrap gap-3">{actions}</div> : null}
    </div>
  )
}

type SurfaceCardProps = {
  title?: string
  subtitle?: string
  children: React.ReactNode
  className?: string
}

export const SurfaceCard: React.FC<SurfaceCardProps> = ({ title, subtitle, children, className = '' }) => {
  return (
    <section
      className={`relative overflow-hidden border border-[rgba(132,179,219,0.24)] bg-[rgba(6,20,36,0.76)] p-5 backdrop-blur-sm ${className}`}
    >
      {(title || subtitle) && (
        <div className="mb-4 border-b border-[rgba(132,179,219,0.18)] pb-4">
          {title ? <h2 className="text-lg font-semibold text-[#f2fbff]">{title}</h2> : null}
          {subtitle ? <p className="mt-1 text-sm leading-6 text-[#8fb2cf]">{subtitle}</p> : null}
        </div>
      )}
      {children}
    </section>
  )
}

type StatItem = {
  label: string
  value: React.ReactNode
  hint?: string
}

export const StatStrip: React.FC<{ items: StatItem[] }> = ({ items }) => {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {items.map((item) => (
        <div
          key={item.label}
          className="border border-[rgba(132,179,219,0.22)] bg-[rgba(7,18,34,0.72)] px-4 py-4"
        >
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#7ea8cd]">{item.label}</p>
          <p className="mt-3 text-2xl font-bold text-[#f2fbff]">{item.value}</p>
          {item.hint ? <p className="mt-2 text-sm leading-6 text-[#89a9c4]">{item.hint}</p> : null}
        </div>
      ))}
    </div>
  )
}

export const FormMeta: React.FC<{ title: string; description?: string }> = ({ title, description }) => {
  return (
    <div className="mb-5 max-w-2xl">
      <h2 className="text-xl font-semibold text-[#f2fbff]">{title}</h2>
      {description ? <p className="mt-2 text-sm leading-6 text-[#8fb2cf]">{description}</p> : null}
    </div>
  )
}

export const ResultPanel: React.FC<{
  title: string
  description?: string
  children: React.ReactNode
}> = ({ title, description, children }) => {
  return (
    <SurfaceCard title={title} subtitle={description}>
      <div className="rounded border border-[rgba(132,179,219,0.22)] bg-[rgba(2,10,20,0.78)] p-4 text-[#deefff]">
        {children}
      </div>
    </SurfaceCard>
  )
}

export const TaskReceipt: React.FC<{
  label: string
  value: string
  cta?: React.ReactNode
}> = ({ label, value, cta }) => {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 border border-[rgba(132,179,219,0.22)] bg-[rgba(6,18,34,0.74)] px-4 py-3">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#7ea8cd]">{label}</p>
        <p className="mt-1 font-semibold text-[#f2fbff]">{value}</p>
      </div>
      {cta}
    </div>
  )
}

export const EmptyState: React.FC<{
  title: string
  description: string
  action?: React.ReactNode
}> = ({ title, description, action }) => {
  return (
    <div className="border border-dashed border-[rgba(132,179,219,0.28)] bg-[rgba(6,18,34,0.52)] px-6 py-8 text-center">
      <h3 className="text-lg font-semibold text-[#eaf8ff]">{title}</h3>
      <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-[#90afc9]">{description}</p>
      {action ? <div className="mt-5 flex justify-center">{action}</div> : null}
    </div>
  )
}
