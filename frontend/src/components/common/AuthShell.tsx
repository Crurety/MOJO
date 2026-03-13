import React from 'react'

type AuthShellProps = {
  eyebrow: string
  title: string
  description: string
  highlights: string[]
  toolbar?: React.ReactNode
  children: React.ReactNode
}

const AuthShell: React.FC<AuthShellProps> = ({ eyebrow, title, description, highlights, toolbar, children }) => {
  return (
    <div className="grid min-h-[78vh] items-center py-8 lg:grid-cols-[1.05fr_0.95fr] lg:gap-8">
      <section className="section-shell border border-[rgba(132,179,219,0.3)] px-6 py-8 sm:px-8 lg:px-10 lg:py-10">
        <p className="text-xs font-bold uppercase tracking-[0.22em] text-[#80a9cc]">{eyebrow}</p>
        <h1 className="mt-3 text-3xl font-bold text-[#f2fbff] sm:text-4xl">{title}</h1>
        <p className="mt-4 max-w-2xl text-sm leading-7 text-[#96b5cf] sm:text-base">{description}</p>

        <div className="mt-8 grid gap-3">
          {highlights.map((line, index) => (
            <div
              key={line}
              className="flex items-start gap-3 border border-[rgba(132,179,219,0.22)] bg-[rgba(6,18,34,0.68)] px-4 py-4"
            >
              <span className="inline-flex h-8 w-8 items-center justify-center border border-[rgba(151,232,255,0.42)] bg-[rgba(10,37,58,0.86)] text-xs font-bold text-[#b2edff]">
                {String(index + 1).padStart(2, '0')}
              </span>
              <p className="text-sm leading-6 text-[#cfe7f8]">{line}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mt-6 border border-[rgba(132,179,219,0.32)] bg-[rgba(4,14,28,0.9)] px-6 py-7 sm:px-8 sm:py-8 lg:mt-0">
        <div className="mb-6 flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-[#7ea8cd]">Access</p>
            <p className="mt-2 text-2xl font-semibold text-[#f2fbff]">{title}</p>
          </div>
          {toolbar}
        </div>
        {children}
      </section>
    </div>
  )
}

export default AuthShell
