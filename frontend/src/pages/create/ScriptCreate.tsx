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
      message.success(t('scriptCreate.toast.generated'))
      return
    }

    message.success(t('scriptCreate.toast.created'))
  }

  return (
    <section className="section-shell border border-[rgba(132,179,219,0.3)] px-6 py-8 sm:px-8">
      <Title level={2} className="!mb-2 !text-[#f2fbff]">
        {t('page.scriptCreate.title')}
      </Title>
      <Paragraph className="!mb-6 !text-[#96b5cf]">{t('scriptCreate.desc')}</Paragraph>

      <Card className="!mb-6 !border-[rgba(132,179,219,0.25)] !bg-[rgba(6,20,36,0.75)]">
        <Form<ScriptFormValues>
          form={form}
          layout="vertical"
          initialValues={{ output_type: 'image_set', scene_count: 3 }}
          onFinish={handleSubmit}
        >
          <Form.Item label={t('scriptCreate.form.title.label')} name="title">
            <Input placeholder={t('scriptCreate.form.title.placeholder')} />
          </Form.Item>

          <Form.Item
            label={t('scriptCreate.form.keywords.label')}
            name="keywords"
            rules={[{ required: true, message: t('scriptCreate.form.keywords.required') }]}
          >
            <TextArea rows={4} placeholder={t('scriptCreate.form.keywords.placeholder')} />
          </Form.Item>

          <Space style={{ width: '100%' }} size={16} wrap>
            <Form.Item label={t('scriptCreate.form.outputType.label')} name="output_type" style={{ minWidth: 220 }}>
              <Select
                options={[
                  { value: 'image_set', label: t('scriptCreate.form.outputType.imageSet') },
                  { value: 'single_image', label: t('scriptCreate.form.outputType.singleImage') },
                  { value: 'video', label: t('scriptCreate.form.outputType.video') },
                ]}
              />
            </Form.Item>

            <Form.Item label={t('scriptCreate.form.style.label')} name="style" style={{ minWidth: 220 }}>
              <Input placeholder={t('scriptCreate.form.style.placeholder')} />
            </Form.Item>

            <Form.Item label={t('scriptCreate.form.sceneCount.label')} name="scene_count" style={{ minWidth: 180 }}>
              <InputNumber min={1} max={12} style={{ width: '100%' }} />
            </Form.Item>
          </Space>

          <Button type="primary" htmlType="submit" loading={loading}>
            {t('scriptCreate.submit')}
          </Button>
        </Form>
      </Card>

      <Card className="!border-[rgba(132,179,219,0.25)] !bg-[rgba(6,20,36,0.75)]">
        <Text className="!text-[#cfe8ff]">{t('scriptCreate.result.title')}</Text>
        <div className="mt-3 whitespace-pre-wrap rounded border border-[rgba(132,179,219,0.2)] bg-[rgba(2,10,20,0.75)] p-4 text-[#deefff]">
          {generatedScript || t('scriptCreate.result.empty')}
        </div>
      </Card>
    </section>
  )
}

export default ScriptCreate
