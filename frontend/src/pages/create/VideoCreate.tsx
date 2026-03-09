import { useState } from 'react'
import { Button, Card, Form, Input, InputNumber, Select, Space, Typography, message } from 'antd'
import { Link } from 'react-router-dom'
import { useContent } from '../../hooks/useContent'
import { useI18n } from '../../i18n'

const { Title, Paragraph, Text } = Typography
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
  const [taskNo, setTaskNo] = useState<string>('')

  const handleSubmit = async (values: VideoFormValues) => {
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

  return (
    <section className="section-shell border border-[rgba(132,179,219,0.3)] px-6 py-8 sm:px-8">
      <Title level={2} className="!mb-2 !text-[#f2fbff]">
        {t('page.videoCreate.title')}
      </Title>
      <Paragraph className="!mb-6 !text-[#96b5cf]">{t('videoCreate.desc')}</Paragraph>

      <Card className="!border-[rgba(132,179,219,0.25)] !bg-[rgba(6,20,36,0.75)]">
        <Form<VideoFormValues>
          layout="vertical"
          initialValues={{ duration: 6, clarity: '1080p' }}
          onFinish={handleSubmit}
        >
          <Form.Item
            label={t('videoCreate.form.prompt.label')}
            name="prompt"
            rules={[{ required: true, message: t('videoCreate.form.prompt.required') }]}
          >
            <TextArea rows={4} placeholder={t('videoCreate.form.prompt.placeholder')} />
          </Form.Item>

          <Space style={{ width: '100%' }} size={16} wrap>
            <Form.Item label={t('videoCreate.form.duration.label')} name="duration" style={{ minWidth: 180 }}>
              <InputNumber min={3} max={60} style={{ width: '100%' }} />
            </Form.Item>
            <Form.Item label={t('videoCreate.form.clarity.label')} name="clarity" style={{ minWidth: 180 }}>
              <Select
                options={[
                  { value: '720p', label: '720p' },
                  { value: '1080p', label: '1080p' },
                  { value: '4k', label: '4K' },
                ]}
              />
            </Form.Item>
            <Form.Item label={t('videoCreate.form.style.label')} name="style" style={{ minWidth: 220 }}>
              <Input placeholder={t('videoCreate.form.style.placeholder')} />
            </Form.Item>
          </Space>

          <Button type="primary" htmlType="submit" loading={loading}>
            {t('videoCreate.submit')}
          </Button>
        </Form>
      </Card>

      <div className="mt-5 text-sm text-[#9cc0db]">
        {taskNo ? (
          <Space size={8} wrap>
            <Text className="!text-[#d6ebff]">
              {t('common.taskNoLabel')}：{taskNo}
            </Text>
            <Link to="/tasks">{t('common.goToTaskCenter')}</Link>
          </Space>
        ) : (
          t('common.afterSubmitShowTaskNo')
        )}
      </div>
    </section>
  )
}

export default VideoCreate
