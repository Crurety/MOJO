import { useEffect, useMemo, useState } from 'react'
import { Button, Card, Select, Space, Table, Tag, Typography, message } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useContent } from '../../hooks/useContent'
import { useI18n } from '../../i18n'

const { Title, Paragraph } = Typography

type TaskRecord = {
  id: number
  task_no: string
  task_type: string
  status: number
  progress: number
  result_url?: string
  error_message?: string
  cost_amount: number
  created_at: string
  completed_at?: string
}

const statusMap: Record<number, { label: string; color: string }> = {
  0: { label: '排队中', color: 'default' },
  1: { label: '处理中', color: 'processing' },
  2: { label: '已完成', color: 'success' },
  3: { label: '失败', color: 'error' },
}

const taskTypeOptions = [
  { value: '', label: '全部类型' },
  { value: 'script', label: '脚本' },
  { value: 'image', label: '图片' },
  { value: 'video', label: '视频' },
  { value: 'ad', label: '广告' },
]

const statusOptions = [
  { value: '', label: '全部状态' },
  { value: '0', label: '排队中' },
  { value: '1', label: '处理中' },
  { value: '2', label: '已完成' },
  { value: '3', label: '失败' },
]

const Tasks = () => {
  const { t } = useI18n()
  const { fetchTasks, loading } = useContent()
  const [tasks, setTasks] = useState<TaskRecord[]>([])
  const [taskType, setTaskType] = useState<string>('')
  const [status, setStatus] = useState<string>('')

  const loadTasks = async () => {
    const response = await fetchTasks(
      0,
      50,
      status === '' ? undefined : Number(status),
      taskType || undefined
    )

    if (!response.success) {
      message.error(response.message || t('hook.content.fetchTaskFailed'))
      return
    }
    setTasks(response.data || [])
  }

  useEffect(() => {
    void loadTasks()
    const timer = window.setInterval(() => {
      void loadTasks()
    }, 5000)
    return () => window.clearInterval(timer)
  }, [taskType, status])

  const columns: ColumnsType<TaskRecord> = useMemo(
    () => [
      {
        title: '任务号',
        dataIndex: 'task_no',
        key: 'task_no',
        width: 220,
      },
      {
        title: '类型',
        dataIndex: 'task_type',
        key: 'task_type',
        width: 100,
      },
      {
        title: '状态',
        dataIndex: 'status',
        key: 'status',
        width: 120,
        render: (value: number) => {
          const meta = statusMap[value] || { label: String(value), color: 'default' }
          return <Tag color={meta.color}>{meta.label}</Tag>
        },
      },
      {
        title: '进度',
        dataIndex: 'progress',
        key: 'progress',
        width: 100,
        render: (value: number) => `${value || 0}%`,
      },
      {
        title: '结果',
        dataIndex: 'result_url',
        key: 'result_url',
        render: (value: string) =>
          value ? (
            <a href={value} target="_blank" rel="noreferrer">
              查看
            </a>
          ) : (
            '-'
          ),
      },
      {
        title: '错误信息',
        dataIndex: 'error_message',
        key: 'error_message',
        render: (value: string) => value || '-',
      },
      {
        title: '创建时间',
        dataIndex: 'created_at',
        key: 'created_at',
        width: 180,
      },
    ],
    []
  )

  return (
    <section className="section-shell border border-[rgba(132,179,219,0.3)] px-6 py-8 sm:px-8">
      <Title level={2} className="!mb-2 !text-[#f2fbff]">
        {t('page.tasks.title')}
      </Title>
      <Paragraph className="!mb-6 !text-[#96b5cf]">任务状态每 5 秒自动刷新，点击结果可直接查看生成内容。</Paragraph>

      <Card className="!border-[rgba(132,179,219,0.25)] !bg-[rgba(6,20,36,0.75)]">
        <Space wrap className="!mb-4">
          <Select
            value={taskType}
            onChange={setTaskType}
            options={taskTypeOptions}
            style={{ width: 180 }}
          />
          <Select value={status} onChange={setStatus} options={statusOptions} style={{ width: 180 }} />
          <Button onClick={() => void loadTasks()} loading={loading}>
            刷新
          </Button>
        </Space>

        <Table<TaskRecord>
          rowKey="id"
          columns={columns}
          dataSource={tasks}
          pagination={{ pageSize: 10 }}
          loading={loading}
          scroll={{ x: 1100 }}
        />
      </Card>
    </section>
  )
}

export default Tasks
