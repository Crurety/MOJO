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
    message.success('视频生成任务已提交')
  }

  return (
    <section className="section-shell border border-[rgba(132,179,219,0.3)] px-6 py-8 sm:px-8">
      <Title level={2} className="!mb-2 !text-[#f2fbff]">
        {t('page.videoCreate.title')}
      </Title>
      <Paragraph className="!mb-6 !text-[#96b5cf]">对接 Runway API，视频任务会异步生成并在任务中心更新状态。</Paragraph>

      <Card className="!border-[rgba(132,179,219,0.25)] !bg-[rgba(6,20,36,0.75)]">
        <Form<VideoFormValues>
          layout="vertical"
          initialValues={{ duration: 6, clarity: '1080p' }}
          onFinish={handleSubmit}
        >
          <Form.Item label="视频提示词" name="prompt" rules={[{ required: true, message: '请输入提示词' }]}>
            <TextArea rows={4} placeholder="例如：A startup product launch clip, energetic pacing, bold typography" />
          </Form.Item>

          <Space style={{ width: '100%' }} size={16} wrap>
            <Form.Item label="时长（秒）" name="duration" style={{ minWidth: 180 }}>
              <InputNumber min={3} max={60} style={{ width: '100%' }} />
            </Form.Item>
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
              <Input placeholder="cinematic / commercial / documentary" />
            </Form.Item>
          </Space>

          <Button type="primary" htmlType="submit" loading={loading}>
            提交视频任务
          </Button>
        </Form>
      </Card>

      <div className="mt-5 text-sm text-[#9cc0db]">
        {taskNo ? (
          <>
            <Text className="!text-[#d6ebff]">任务号：{taskNo}</Text>，前往 <Link to="/tasks">任务中心</Link> 查看进度。
          </>
        ) : (
          '提交后会显示任务号。'
        )}
      </div>
    </section>
  )
}

export default VideoCreate

