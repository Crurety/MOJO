import { useState } from 'react'
import { Button, Card, Form, Input, InputNumber, Select, Space, Typography, message } from 'antd'
import { useContent } from '../../hooks/useContent'
import { useI18n } from '../../i18n'

const { Title, Paragraph, Text } = Typography
const { TextArea } = Input

type ScriptFormValues = {
  title?: string
  keywords: string
  output_type: 'image_set' | 'single_image' | 'video'
  style?: string
  scene_count?: number
}

const ScriptCreate = () => {
  const { t } = useI18n()
  const { createScript, loading } = useContent()
  const [generatedScript, setGeneratedScript] = useState<string>('')
  const [form] = Form.useForm<ScriptFormValues>()

  const handleSubmit = async (values: ScriptFormValues) => {
    const response = await createScript({
      title: values.title?.trim() || undefined,
      keywords: values.keywords.trim(),
      output_type: values.output_type,
      parameters: {
        style: values.style?.trim() || undefined,
        scene_count: values.scene_count || 1,
      },
    })

    if (!response.success) {
      message.error(response.message || t('hook.content.createFailed'))
      return
    }

    const script = response.data?.data?.script
    if (script?.content) {
      setGeneratedScript(script.content)
      message.success('脚本生成成功')
      return
    }

    message.success('脚本任务已创建')
  }

  return (
    <section className="section-shell border border-[rgba(132,179,219,0.3)] px-6 py-8 sm:px-8">
      <Title level={2} className="!mb-2 !text-[#f2fbff]">
        {t('page.scriptCreate.title')}
      </Title>
      <Paragraph className="!mb-6 !text-[#96b5cf]">输入关键词后由 OpenAI 自动生成脚本。</Paragraph>

      <Card className="!mb-6 !border-[rgba(132,179,219,0.25)] !bg-[rgba(6,20,36,0.75)]">
        <Form<ScriptFormValues>
          form={form}
          layout="vertical"
          initialValues={{ output_type: 'image_set', scene_count: 3 }}
          onFinish={handleSubmit}
        >
          <Form.Item label="标题（可选）" name="title">
            <Input placeholder="例如：夏季新品短视频脚本" />
          </Form.Item>

          <Form.Item
            label="关键词"
            name="keywords"
            rules={[{ required: true, message: '请输入关键词' }]}
          >
            <TextArea rows={4} placeholder="例如：防晒、海边、年轻女性、活力、15秒" />
          </Form.Item>

          <Space style={{ width: '100%' }} size={16} wrap>
            <Form.Item label="输出类型" name="output_type" style={{ minWidth: 220 }}>
              <Select
                options={[
                  { value: 'image_set', label: '图集脚本' },
                  { value: 'single_image', label: '单图脚本' },
                  { value: 'video', label: '视频脚本' },
                ]}
              />
            </Form.Item>

            <Form.Item label="风格（可选）" name="style" style={{ minWidth: 220 }}>
              <Input placeholder="例如：科技感 / 电影感 / 极简" />
            </Form.Item>

            <Form.Item label="场景数" name="scene_count" style={{ minWidth: 180 }}>
              <InputNumber min={1} max={12} style={{ width: '100%' }} />
            </Form.Item>
          </Space>

          <Button type="primary" htmlType="submit" loading={loading}>
            生成脚本
          </Button>
        </Form>
      </Card>

      <Card className="!border-[rgba(132,179,219,0.25)] !bg-[rgba(6,20,36,0.75)]">
        <Text className="!text-[#cfe8ff]">生成结果</Text>
        <div className="mt-3 whitespace-pre-wrap rounded border border-[rgba(132,179,219,0.2)] bg-[rgba(2,10,20,0.75)] p-4 text-[#deefff]">
          {generatedScript || '暂无脚本，提交后将在这里显示。'}
        </div>
      </Card>
    </section>
  )
}

export default ScriptCreate

