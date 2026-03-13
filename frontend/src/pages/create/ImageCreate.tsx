import { useState } from 'react'
import { Button, Form, Input, InputNumber, Select, Space, message } from 'antd'
import { Link } from 'react-router-dom'
import { FormMeta, PageHeader, SurfaceCard, TaskReceipt } from '../../components'
import { useCapabilityAccess } from '../../hooks'
import { useContent } from '../../hooks/useContent'
import { useI18n } from '../../i18n'
import { calculateUsageCost } from '../../utils/usage'

const { TextArea } = Input

type ImageFormValues = {
  prompt: string
  clarity: '720p' | '1080p' | '4k'
  style?: string
  count: number
}

const ImageCreate = () => {
  const { t } = useI18n()
  const { createTask, loading } = useContent()
  const { ensureUsageReady, isCheckingAccess, isAutoPurchasing } = useCapabilityAccess('image')
  const [taskNo, setTaskNo] = useState<string>('')

  const handleSubmit = async (values: ImageFormValues) => {
    const usageReady = await ensureUsageReady(
      calculateUsageCost({
        taskType: 'image',
        clarity: values.clarity,
        count: values.count,
      })
    )
    if (!usageReady) {
      return
    }

    const response = await createTask({
      task_type: 'image',
      parameters: {
        prompt: values.prompt.trim(),
        clarity: values.clarity,
        style: values.style?.trim() || undefined,
        count: values.count,
      },
    })

    if (!response.success) {
      message.error(response.message || t('hook.content.createTaskFailed'))
      return
    }

    const task = response.data?.data?.task
    setTaskNo(task?.task_no || '')
    message.success(t('imageCreate.toast.submitted'))
  }

  if (isCheckingAccess) {
    return (
      <div className="space-y-6 text-[#e8f4ff]">
        <PageHeader eyebrow={t('page.imageCreate.title')} title={t('imageCreate.form.prompt.label')} description={t('imageCreate.desc')} />
        <SurfaceCard>
          <div className="py-20 text-center text-sm text-[#8fb1cc]">{t('common.loading')}</div>
        </SurfaceCard>
      </div>
    )
  }

  return (
    <div className="space-y-6 text-[#e8f4ff]">
      <PageHeader eyebrow={t('page.imageCreate.title')} title={t('imageCreate.form.prompt.label')} description={t('imageCreate.desc')} />

      <SurfaceCard>
        <FormMeta title={t('imageCreate.submit')} description={t('imageCreate.form.prompt.placeholder')} />
        <Form<ImageFormValues> layout="vertical" initialValues={{ clarity: '1080p', count: 1 }} onFinish={handleSubmit}>
          <Form.Item
            label={t('imageCreate.form.prompt.label')}
            name="prompt"
            rules={[{ required: true, message: t('imageCreate.form.prompt.required') }]}
          >
            <TextArea rows={5} placeholder={t('imageCreate.form.prompt.placeholder')} />
          </Form.Item>

          <Space style={{ width: '100%' }} size={16} wrap>
            <Form.Item label={t('imageCreate.form.clarity.label')} name="clarity" style={{ minWidth: 180 }}>
              <Select options={[{ value: '720p', label: '720p' }, { value: '1080p', label: '1080p' }, { value: '4k', label: '4K' }]} />
            </Form.Item>
            <Form.Item label={t('imageCreate.form.style.label')} name="style" style={{ minWidth: 220 }}>
              <Input placeholder={t('imageCreate.form.style.placeholder')} />
            </Form.Item>
            <Form.Item label={t('imageCreate.form.count.label')} name="count" style={{ minWidth: 180 }}>
              <InputNumber min={1} max={4} style={{ width: '100%' }} />
            </Form.Item>
          </Space>

          <Button type="primary" htmlType="submit" loading={loading || isAutoPurchasing}>
            {t('imageCreate.submit')}
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

export default ImageCreate
