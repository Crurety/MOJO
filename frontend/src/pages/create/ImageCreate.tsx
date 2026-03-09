import { useState } from 'react'
import { Button, Card, Form, Input, InputNumber, Select, Space, Typography, message } from 'antd'
import { Link } from 'react-router-dom'
import { useContent } from '../../hooks/useContent'
import { useI18n } from '../../i18n'

const { Title, Paragraph, Text } = Typography
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
  const [taskNo, setTaskNo] = useState<string>('')

  const handleSubmit = async (values: ImageFormValues) => {
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

  return (
    <section className="section-shell border border-[rgba(132,179,219,0.3)] px-6 py-8 sm:px-8">
      <Title level={2} className="!mb-2 !text-[#f2fbff]">
        {t('page.imageCreate.title')}
      </Title>
      <Paragraph className="!mb-6 !text-[#96b5cf]">{t('imageCreate.desc')}</Paragraph>

      <Card className="!border-[rgba(132,179,219,0.25)] !bg-[rgba(6,20,36,0.75)]">
        <Form<ImageFormValues>
          layout="vertical"
          initialValues={{ clarity: '1080p', count: 1 }}
          onFinish={handleSubmit}
        >
          <Form.Item
            label={t('imageCreate.form.prompt.label')}
            name="prompt"
            rules={[{ required: true, message: t('imageCreate.form.prompt.required') }]}
          >
            <TextArea rows={4} placeholder={t('imageCreate.form.prompt.placeholder')} />
          </Form.Item>

          <Space style={{ width: '100%' }} size={16} wrap>
            <Form.Item label={t('imageCreate.form.clarity.label')} name="clarity" style={{ minWidth: 180 }}>
              <Select
                options={[
                  { value: '720p', label: '720p' },
                  { value: '1080p', label: '1080p' },
                  { value: '4k', label: '4K' },
                ]}
              />
            </Form.Item>
            <Form.Item label={t('imageCreate.form.style.label')} name="style" style={{ minWidth: 220 }}>
              <Input placeholder={t('imageCreate.form.style.placeholder')} />
            </Form.Item>
            <Form.Item label={t('imageCreate.form.count.label')} name="count" style={{ minWidth: 180 }}>
              <InputNumber min={1} max={4} style={{ width: '100%' }} />
            </Form.Item>
          </Space>

          <Button type="primary" htmlType="submit" loading={loading}>
            {t('imageCreate.submit')}
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

export default ImageCreate
