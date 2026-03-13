import { useState } from 'react'
import { Button, Form, Input, InputNumber, Select, Space, message } from 'antd'
import { Link } from 'react-router-dom'
import { FormMeta, PageHeader, SurfaceCard, TaskReceipt } from '../../components'
import { useCapabilityAccess } from '../../hooks'
import { useContent } from '../../hooks/useContent'
import { useI18n } from '../../i18n'
import { calculateUsageCost } from '../../utils/usage'

const { TextArea } = Input

type VideoFormValues = {
  prompt: string
  duration: number
  clarity: '720p' | '1080p' | '4k'
  style?: string
}

const VideoCreate = () => {
  const { t } = useI18n()
  const { createTask, loading } = useContent()
  const { ensureUsageReady, isCheckingAccess, isAutoPurchasing } = useCapabilityAccess('video')
  const [taskNo, setTaskNo] = useState<string>('')

  const handleSubmit = async (values: VideoFormValues) => {
    const usageReady = await ensureUsageReady(
      calculateUsageCost({
        taskType: 'video',
        clarity: values.clarity,
        duration: values.duration,
      })
    )
    if (!usageReady) {
      return
    }

    const response = await createTask({
      task_type: 'video',
      parameters: {
        prompt: values.prompt.trim(),
        duration: values.duration,
        clarity: values.clarity,
        style: values.style?.trim() || undefined,
      },
    })

    if (!response.success) {
      message.error(response.message || t('hook.content.createTaskFailed'))
      return
    }

    const task = response.data?.data?.task
    setTaskNo(task?.task_no || '')
    message.success(t('videoCreate.toast.submitted'))
  }

  if (isCheckingAccess) {
    return (
      <div className="space-y-6 text-[#e8f4ff]">
        <PageHeader eyebrow={t('page.videoCreate.title')} title={t('videoCreate.form.prompt.label')} description={t('videoCreate.desc')} />
        <SurfaceCard>
          <div className="py-20 text-center text-sm text-[#8fb1cc]">{t('common.loading')}</div>
        </SurfaceCard>
      </div>
    )
  }

  return (
    <div className="space-y-6 text-[#e8f4ff]">
      <PageHeader eyebrow={t('page.videoCreate.title')} title={t('videoCreate.form.prompt.label')} description={t('videoCreate.desc')} />

      <SurfaceCard>
        <FormMeta title={t('videoCreate.submit')} description={t('videoCreate.form.prompt.placeholder')} />
        <Form<VideoFormValues> layout="vertical" initialValues={{ duration: 6, clarity: '1080p' }} onFinish={handleSubmit}>
          <Form.Item
            label={t('videoCreate.form.prompt.label')}
            name="prompt"
            rules={[{ required: true, message: t('videoCreate.form.prompt.required') }]}
          >
            <TextArea rows={5} placeholder={t('videoCreate.form.prompt.placeholder')} />
          </Form.Item>

          <Space style={{ width: '100%' }} size={16} wrap>
            <Form.Item label={t('videoCreate.form.duration.label')} name="duration" style={{ minWidth: 180 }}>
              <InputNumber min={3} max={60} style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item label={t('videoCreate.form.clarity.label')} name="clarity" style={{ minWidth: 180 }}>
              <Select options={[{ value: '720p', label: '720p' }, { value: '1080p', label: '1080p' }, { value: '4k', label: '4K' }]} />
            </Form.Item>
            <Form.Item label={t('videoCreate.form.style.label')} name="style" style={{ minWidth: 220 }}>
              <Input placeholder={t('videoCreate.form.style.placeholder')} />
            </Form.Item>
          </Space>

          <Button type="primary" htmlType="submit" loading={loading || isAutoPurchasing}>
            {t('videoCreate.submit')}
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

export default VideoCreate
