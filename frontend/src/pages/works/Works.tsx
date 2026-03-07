import { Typography } from 'antd'
import { useI18n } from '../../i18n'

const { Title, Paragraph } = Typography

const Works = () => {
  const { t } = useI18n()

  return (
    <section className="section-shell border border-[rgba(132,179,219,0.3)] px-6 py-8 sm:px-8">
      <Title level={2} className="!mb-2 !text-[#f2fbff]">
        {t('page.works.title')}
      </Title>
      <Paragraph className="!mb-0 !text-[#96b5cf]">{t('page.works.desc')}</Paragraph>
    </section>
  )
}

export default Works
