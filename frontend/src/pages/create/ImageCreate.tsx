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
    message.success('图片生成任务已提交')
  }

  return (
    <section className="section-shell border border-[rgba(132,179,219,0.3)] px-6 py-8 sm:px-8">
      <Title level={2} className="!mb-2 !text-[#f2fbff]">
        {t('page.imageCreate.title')}
      </Title>
      <Paragraph className="!mb-6 !text-[#96b5cf]">对接 Stability API，提交后可在任务中心查看进度与结果。</Paragraph>

      <Card className="!border-[rgba(132,179,219,0.25)] !bg-[rgba(6,20,36,0.75)]">
        <Form<ImageFormValues>
          layout="vertical"
          initialValues={{ clarity: '1080p', count: 1 }}
          onFinish={handleSubmit}
        >
          <Form.Item label="图片提示词" name="prompt" rules={[{ required: true, message: '请输入提示词' }]}>
            <TextArea rows={4} placeholder="例如：A futuristic city skyline at sunset, cinematic lighting" />
          </Form.Item>

          <Space style={{ width: '100%' }} size={16} wrap>
            <Form.Item label="清晰度" name="clarity" style={{ minWidth: 180 }}>
              <Select
                options={[
                  { value: '720p', label: '720p' },
                  { value: '1080p', label: '1080p' },
                  { value: '4k', label: '4K' },
                ]}
              />
            </Form.Item>
            <Form.Item label="风格（可选）" name="style" style={{ minWidth: 220 }}>
              <Input placeholder="photographic / digital-art / anime" />
            </Form.Item>
            <Form.Item label="生成数量" name="count" style={{ minWidth: 180 }}>
              <InputNumber min={1} max={4} style={{ width: '100%' }} />
            </Form.Item>
          </Space>

          <Button type="primary" htmlType="submit" loading={loading}>
            提交图片任务
          </Button>
        </Form>
      </Card>

      <div className="mt-5 text-sm text-[#9cc0db]">
        {taskNo ? (
          <>
            <Text className="!text-[#d6ebff]">任务号：{taskNo}</Text>，前往 <Link to="/tasks">任务中心</Link> 查看结果。
          </>
        ) : (
          '提交后会显示任务号。'
        )}
      </div>
    </section>
  )
}

export default ImageCreate

