import React from 'react'
import {
  FileTextOutlined,
  NotificationOutlined,
  PictureOutlined,
  VideoCameraOutlined,
} from '@ant-design/icons'
import { Link } from 'react-router-dom'
import { Button } from '../components'
import { useI18n } from '../i18n'

const Home: React.FC = () => {
  const { t } = useI18n()

  const featureItems = [
    {
      icon: <FileTextOutlined />,
      title: t('home.feature.script.title'),
      description: t('home.feature.script.desc'),
      link: '/create/script',
    },
    {
      icon: <PictureOutlined />,
      title: t('home.feature.image.title'),
      description: t('home.feature.image.desc'),
      link: '/create/image',
    },
    {
      icon: <VideoCameraOutlined />,
      title: t('home.feature.video.title'),
      description: t('home.feature.video.desc'),
      link: '/create/video',
    },
    {
      icon: <NotificationOutlined />,
      title: t('home.feature.ad.title'),
      description: t('home.feature.ad.desc'),
      link: '/create/ad',
    },
  ]

  const workflow = [
    { title: t('home.workflow.step1.title'), text: t('home.workflow.step1.desc') },
    { title: t('home.workflow.step2.title'), text: t('home.workflow.step2.desc') },
    { title: t('home.workflow.step3.title'), text: t('home.workflow.step3.desc') },
  ]

  const stats = [
    { label: t('home.stat.templates'), value: '24+' },
    { label: t('home.stat.tasks'), value: '18k+' },
    { label: t('home.stat.efficiency'), value: '3.6x' },
  ]

  return (
    <div className="space-y-12 text-[#e8f4ff]">
      <section className="grid gap-6 lg:grid-cols-[1.25fr_0.75fr]">
        <div className="section-shell relative overflow-hidden border border-[rgba(132,179,219,0.3)] px-6 py-8 sm:px-10 sm:py-10">
          <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(115deg,rgba(96,226,255,0.16),transparent_36%,rgba(75,137,255,0.12)_72%,transparent)]" />
          <div className="relative">
            <span className="inline-flex border border-[rgba(151,232,255,0.52)] bg-[rgba(11,36,56,0.86)] px-3 py-1 text-xs font-bold tracking-[0.16em] text-[#c7eeff]">
              {t('home.badge')}
            </span>
            <h1 className="mt-4 text-3xl font-bold leading-tight text-[#f2fbff] sm:text-4xl lg:text-[2.7rem]">
              {t('home.title')}
            </h1>
            <p className="mt-4 max-w-2xl text-base leading-7 text-[#9cb9d3] sm:text-lg">{t('home.subtitle')}</p>

            <div className="mt-7 flex flex-wrap items-center gap-3">
              <Link to="/create/script">
                <Button className="px-7 py-3">{t('home.ctaStart')}</Button>
              </Link>
              <Link to="/gallery">
                <Button variant="secondary" className="px-7 py-3">
                  {t('home.ctaGallery')}
                </Button>
              </Link>
            </div>
          </div>
        </div>

        <div className="section-shell border border-[rgba(132,179,219,0.3)] px-6 py-8 sm:px-8 sm:py-9">
          <h2 className="text-sm font-bold uppercase tracking-[0.2em] text-[#7ea8cd]">{t('home.overview')}</h2>
          <div className="mt-4 divide-y divide-[rgba(132,179,219,0.2)] border-y border-[rgba(132,179,219,0.2)]">
            {stats.map((item) => (
              <div key={item.label} className="flex items-end justify-between py-4">
                <p className="text-3xl font-semibold text-[#f0fbff]">{item.value}</p>
                <p className="text-sm text-[#8caac5]">{item.label}</p>
              </div>
            ))}
          </div>
          <p className="mt-5 border-l-2 border-[rgba(137,223,255,0.72)] pl-3 text-sm text-[#9cb9d3]">{t('home.newTemplates')}</p>
        </div>
      </section>

      <section>
        <div className="mb-5 flex items-end justify-between gap-4 border-b border-[rgba(132,179,219,0.24)] pb-4">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.18em] text-[#7ea8cd]">{t('home.coreBadge')}</p>
            <h2 className="mt-1 text-2xl font-bold text-[#f2fbff]">{t('home.coreTitle')}</h2>
          </div>
          <Link to="/pricing" className="text-sm font-semibold text-[#86d9ff] hover:text-[#caf0ff]">
            {t('home.viewPricing')}
          </Link>
        </div>

        <div className="stagger-grid grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          {featureItems.map((feature) => (
            <Link
              key={feature.link}
              to={feature.link}
              className="group block border border-[rgba(132,179,219,0.25)] bg-[rgba(6,18,34,0.66)] px-5 py-6 transition hover:border-[rgba(151,232,255,0.55)] hover:bg-[rgba(9,31,52,0.82)]"
            >
              <span className="inline-flex h-10 w-10 items-center justify-center border border-[rgba(151,232,255,0.46)] bg-[rgba(10,37,58,0.9)] text-base text-[#b2edff]">
                {feature.icon}
              </span>
              <h3 className="mt-3 text-xl font-semibold text-[#f2fbff]">{feature.title}</h3>
              <p className="mt-2 text-sm leading-6 text-[#96b5cf]">{feature.description}</p>
            </Link>
          ))}
        </div>
      </section>

      <section className="section-shell border border-[rgba(132,179,219,0.3)] px-6 py-8 sm:px-8">
        <p className="text-sm font-bold uppercase tracking-[0.18em] text-[#7ea8cd]">{t('home.workflowBadge')}</p>
        <h2 className="mt-2 text-2xl font-bold text-[#f2fbff]">{t('home.workflowTitle')}</h2>

        <div className="stagger-grid mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">
          {workflow.map((step, index) => (
            <div key={step.title} className="border-l border-[rgba(132,179,219,0.34)] px-4 py-1">
              <p className="text-sm font-semibold tracking-[0.2em] text-[#81c3e8]">{String(index + 1).padStart(2, '0')}</p>
              <h3 className="mt-2 text-lg font-semibold text-[#f2fbff]">{step.title}</h3>
              <p className="mt-2 text-sm leading-6 text-[#96b5cf]">{step.text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="section-shell border border-[rgba(151,232,255,0.34)] bg-[linear-gradient(100deg,rgba(7,30,48,0.92),rgba(12,60,84,0.78),rgba(10,24,43,0.9))] px-6 py-8 sm:px-8">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.2em] text-[#bdeeff]">{t('home.readyBadge')}</p>
            <h2 className="mt-2 text-2xl font-bold text-[#f2fbff]">{t('home.readyTitle')}</h2>
            <p className="mt-2 text-sm text-[#c1deef] sm:text-base">{t('home.readySubtitle')}</p>
          </div>
          <div className="flex gap-3">
            <Link to="/register">
              <Button className="px-6 py-3">{t('home.readyRegister')}</Button>
            </Link>
            <Link to="/pricing">
              <Button variant="secondary" className="px-6 py-3">
                {t('home.readyPlans')}
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}

export default Home
