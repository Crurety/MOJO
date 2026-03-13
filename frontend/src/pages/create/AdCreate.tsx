import { useState } from 'react'
import { Button, Form, Input, InputNumber, Select, Space, message } from 'antd'
import { Link } from 'react-router-dom'
import { FormMeta, PageHeader, SurfaceCard, TaskReceipt } from '../../components'
import { useCapabilityAccess } from '../../hooks'
import { useContent } from '../../hooks/useContent'
import { useI18n } from '../../i18n'
import { calculateUsageCost } from '../../utils/usage'

const { TextArea } = Input

type AdFormValues = {
  ad_type: 'image' | 'video'
  product_info: string
  target_audience: string
  brand_style?: string
  clarity: '720p' | '1080p' | '4k'
  duration?: number
  creative_plan?: string
}

const AdCreate = () => {
  const { t } = useI18n()
  const { createTask, loading } = useContent()
  const { ensureUsageReady, isCheckingAccess, isAutoPurchasing } = useCapabilityAccess('ad')
  const [taskNo, setTaskNo] = useState<string>('')
  const [form] = Form.useForm<AdFormValues>()
  const adType = Form.useWatch('ad_type', form)

  const handleSubmit = async (values: AdFormValues) => {
    const usageReady = await ensureUsageReady(
      calculateUsageCost({
        taskType: 'ad',
      })
    )
    if (!usageReady) {
      return
    }

    const response = await createTask({
      task_type: 'ad',
      parameters: {
        ad_type: values.ad_type,
        product_info: values.product_info.trim(),
        target_audience: values.target_audience.trim(),
        brand_style: values.brand_style?.trim() || undefined,
        clarity: values.clarity,
        duration: values.ad_type === 'video' ? values.duration || 15 : undefined,
        creative_plan: values.creative_plan?.trim() || undefined,
      },
    })

    if (!response.success) {
      message.error(response.message || t('hook.content.createTaskFailed'))
      return
    }

    const task = response.data?.data?.task
    setTaskNo(task?.task_no || '')
    message.success(t('adCreate.toast.submitted'))
  }

  if (isCheckingAccess) {
    return (
      <div className="space-y-6 text-[#e8f4ff]">
        <PageHeader eyebrow={t('page.adCreate.title')} title={t('adCreate.form.adType.label')} description={t('adCreate.desc')} />
        <SurfaceCard>
          <div className="py-20 text-center text-sm text-[#8fb1cc]">{t('common.loading')}</div>
        </SurfaceCard>
      </div>
    )
  }

  return (
    <div className="space-y-6 text-[#e8f4ff]">
      <PageHeader eyebrow={t('page.adCreate.title')} title={t('adCreate.form.adType.label')} description={t('adCreate.desc')} />

      <SurfaceCard>
        <FormMeta title={t('adCreate.submit')} description={t('adCreate.form.productInfo.placeholder')} />
        <Form<AdFormValues>
          form={form}
          layout="vertical"
          initialValues={{ ad_type: 'image', clarity: '1080p', duration: 15 }}
          onFinish={handleSubmit}
        >
          <Space style={{ width: '100%' }} size={16} wrap>
            <Form.Item label={t('adCreate.form.adType.label')} name="ad_type" style={{ minWidth: 220 }}>
              <Select options={[{ value: 'image', label: t('adCreate.form.adType.image') }, { value: 'video', label: t('adCreate.form.adType.video') }]} />
            </Form.Item>
            <Form.Item label={t('adCreate.form.clarity.label')} name="clarity" style={{ minWidth: 180 }}>
              <Select options={[{ value: '720p', label: '720p' }, { value: '1080p', label: '1080p' }, { value: '4k', label: '4K' }]} />
            </Form.Item>
            {adType === 'video' ? (
              <Form.Item label={t('adCreate.form.duration.label')} name="duration" style={{ minWidth: 180 }}>
                <InputNumber min={5} max={60} style={{ width: '100%' }} />
              </Form.Item>
            ) : null}
          </Space>

          <Form.Item
            label={t('adCreate.form.productInfo.label')}
            name="product_info"
            rules={[{ required: true, message: t('adCreate.form.productInfo.required') }]}
          >
            <TextArea rows={3} placeholder={t('adCreate.form.productInfo.placeholder')} />
          </Form.Item>

          <Form.Item
            label={t('adCreate.form.targetAudience.label')}
            name="target_audience"
            rules={[{ required: true, message: t('adCreate.form.targetAudience.required') }]}
          >
            <Input placeholder={t('adCreate.form.targetAudience.placeholder')} />
          </Form.Item>

          <Form.Item label={t('adCreate.form.brandStyle.label')} name="brand_style">
            <Input placeholder={t('adCreate.form.brandStyle.placeholder')} />
          </Form.Item>

          <Form.Item label={t('adCreate.form.creativePlan.label')} name="creativePlan">
            <TextArea rows={4} placeholder={t('adCreate.form.creativePlan.placeholder')} />
          </Form.Item>

          <Button type="primary" htmlType="submit" loading={loading || isAutoPurchasing}>
            {t('adCreate.submit')}
          </Button>
        </Form>
      </SurfaceCard>

      {taskNo ? (
        <TaskReceipt
          label={t('common.taskNoLabel')}
          value={taskNo}
          cta={<Link to="/tasks" className="text-sm font-semibold text-[#86d9ff] hover:text-[#d8f6ff]">{t('common.goToTaskCenter')}</Link>}
        />
      ) : null}
    </div>
  )
}

export default AdCreate
