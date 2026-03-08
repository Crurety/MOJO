import { useState } from 'react'
import { Button, Card, Form, Input, InputNumber, Select, Space, Typography, message } from 'antd'
import { Link } from 'react-router-dom'
import { useContent } from '../../hooks/useContent'
import { useI18n } from '../../i18n'

const { Title, Paragraph, Text } = Typography
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
  const [taskNo, setTaskNo] = useState<string>('')
  const [form] = Form.useForm<AdFormValues>()
  const adType = Form.useWatch('ad_type', form)

  const handleSubmit = async (values: AdFormValues) => {
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
    message.success('广告任务已提交')
  }

  return (
    <section className="section-shell border border-[rgba(132,179,219,0.3)] px-6 py-8 sm:px-8">
      <Title level={2} className="!mb-2 !text-[#f2fbff]">
        {t('page.adCreate.title')}
      </Title>
      <Paragraph className="!mb-6 !text-[#96b5cf]">由 OpenAI 生成创意方案，再调用 Stability/Runway 生成广告素材。</Paragraph>

      <Card className="!border-[rgba(132,179,219,0.25)] !bg-[rgba(6,20,36,0.75)]">
        <Form<AdFormValues>
          form={form}
          layout="vertical"
          initialValues={{ ad_type: 'image', clarity: '1080p', duration: 15 }}
          onFinish={handleSubmit}
        >
          <Space style={{ width: '100%' }} size={16} wrap>
            <Form.Item label="广告类型" name="ad_type" style={{ minWidth: 220 }}>
              <Select
                options={[
                  { value: 'image', label: '图像广告' },
                  { value: 'video', label: '视频广告' },
                ]}
              />
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
            {adType === 'video' && (
              <Form.Item label="时长（秒）" name="duration" style={{ minWidth: 180 }}>
                <InputNumber min={5} max={60} style={{ width: '100%' }} />
              </Form.Item>
            )}
          </Space>

          <Form.Item
            label="产品信息"
            name="product_info"
            rules={[{ required: true, message: '请输入产品信息' }]}
          >
            <TextArea rows={3} placeholder="例如：AI效率工具，主打团队协作与自动化流程" />
          </Form.Item>

          <Form.Item
            label="目标受众"
            name="target_audience"
            rules={[{ required: true, message: '请输入目标受众' }]}
          >
            <Input placeholder="例如：25-35 岁互联网产品经理" />
          </Form.Item>

          <Form.Item label="品牌风格（可选）" name="brand_style">
            <Input placeholder="例如：科技感、专业、可信赖" />
          </Form.Item>

          <Form.Item label="创意方案（可选，留空则由系统自动生成）" name="creative_plan">
            <TextArea rows={4} placeholder="可手动输入创意方案，或留空自动生成" />
          </Form.Item>

          <Button type="primary" htmlType="submit" loading={loading}>
            提交广告任务
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

export default AdCreate

