import { useState } from 'react'
import { Button, Form, Input, InputNumber, Select, Space, message } from 'antd'
import { Link } from 'react-router-dom'
import { FormMeta, PageHeader, ResultPanel, SurfaceCard } from '../../components'
import { useCapabilityAccess } from '../../hooks'
import { useContent } from '../../hooks/useContent'
import { useI18n } from '../../i18n'

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
  const { ensureUsageReady, isCheckingAccess, isAutoPurchasing } = useCapabilityAccess('script')
  const [generatedScript, setGeneratedScript] = useState<string>('')
  const [form] = Form.useForm<ScriptFormValues>()

  const handleSubmit = async (values: ScriptFormValues) => {
    const usageReady = await ensureUsageReady(1)
    if (!usageReady) {
      return
    }

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

  if (isCheckingAccess) {
    return (
      <div className="space-y-6 text-[#e8f4ff]">
        <PageHeader
          eyebrow={t('page.scriptCreate.title')}
          title={t('scriptCreate.form.title.label')}
          description={t('scriptCreate.desc')}
        />
        <SurfaceCard>
          <div className="py-20 text-center text-sm text-[#8fb1cc]">{t('common.loading')}</div>
        </SurfaceCard>
      </div>
    )
  }

  return (
    <div className="space-y-6 text-[#e8f4ff]">
      <PageHeader
        eyebrow={t('page.scriptCreate.title')}
        title={t('scriptCreate.form.title.label')}
        description={t('scriptCreate.desc')}
        actions={
          <Link to="/tasks" className="border border-[rgba(132,179,219,0.28)] px-4 py-2 text-sm font-semibold text-[#d5ecff] transition hover:border-[rgba(151,232,255,0.5)] hover:bg-[rgba(8,28,46,0.82)]">
            {t('common.goToTaskCenter')}
          </Link>
        }
      />

      <div className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr]">
        <SurfaceCard>
          <FormMeta title={t('scriptCreate.submit')} description={t('scriptCreate.form.keywords.placeholder')} />
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
              <TextArea rows={5} placeholder={t('scriptCreate.form.keywords.placeholder')} />
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

            <Button type="primary" htmlType="submit" loading={loading || isAutoPurchasing}>
              {t('scriptCreate.submit')}
            </Button>
          </Form>
        </SurfaceCard>

        <ResultPanel title={t('scriptCreate.result.title')} description={t('home.workflow.step2.desc')}>
          <div className="min-h-[360px] whitespace-pre-wrap text-sm leading-7">
            {generatedScript || t('scriptCreate.result.empty')}
          </div>
        </ResultPanel>
      </div>
    </div>
  )
}

export default ScriptCreate
