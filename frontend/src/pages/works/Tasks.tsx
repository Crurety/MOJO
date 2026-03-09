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

const statusColorMap: Record<number, string> = {
  0: 'default',
  1: 'processing',
  2: 'success',
  3: 'error',
}

const Tasks = () => {
  const { t } = useI18n()
  const { fetchTasks, loading } = useContent()
  const [tasks, setTasks] = useState<TaskRecord[]>([])
  const [taskType, setTaskType] = useState<string>('')
  const [status, setStatus] = useState<string>('')

  const taskTypeLabelMap = useMemo(
    () => ({
      script: t('tasks.filter.type.script'),
      image: t('tasks.filter.type.image'),
      video: t('tasks.filter.type.video'),
      ad: t('tasks.filter.type.ad'),
    }),
    [t]
  )

  const statusLabelMap = useMemo(
    () => ({
      0: t('tasks.status.0'),
      1: t('tasks.status.1'),
      2: t('tasks.status.2'),
      3: t('tasks.status.3'),
    }),
    [t]
  )

  const taskTypeOptions = useMemo(
    () => [
      { value: '', label: t('tasks.filter.allTypes') },
      { value: 'script', label: t('tasks.filter.type.script') },
      { value: 'image', label: t('tasks.filter.type.image') },
      { value: 'video', label: t('tasks.filter.type.video') },
      { value: 'ad', label: t('tasks.filter.type.ad') },
    ],
    [t]
  )

  const statusOptions = useMemo(
    () => [
      { value: '', label: t('tasks.filter.allStatuses') },
      { value: '0', label: statusLabelMap[0] },
      { value: '1', label: statusLabelMap[1] },
      { value: '2', label: statusLabelMap[2] },
      { value: '3', label: statusLabelMap[3] },
    ],
    [statusLabelMap, t]
  )

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
        title: t('tasks.table.taskNo'),
        dataIndex: 'task_no',
        key: 'task_no',
        width: 220,
      },
      {
        title: t('tasks.table.type'),
        dataIndex: 'task_type',
        key: 'task_type',
        width: 100,
        render: (value: string) => taskTypeLabelMap[value as keyof typeof taskTypeLabelMap] || value,
      },
      {
        title: t('tasks.table.status'),
        dataIndex: 'status',
        key: 'status',
        width: 120,
        render: (value: number) => {
          const label = statusLabelMap[value as keyof typeof statusLabelMap] || String(value)
          const color = statusColorMap[value] || 'default'
          return <Tag color={color}>{label}</Tag>
        },
      },
      {
        title: t('tasks.table.progress'),
        dataIndex: 'progress',
        key: 'progress',
        width: 100,
        render: (value: number) => `${value || 0}%`,
      },
      {
        title: t('tasks.table.result'),
        dataIndex: 'result_url',
        key: 'result_url',
        render: (value: string) =>
          value ? (
            <a href={value} target="_blank" rel="noreferrer">
              {t('tasks.table.view')}
            </a>
          ) : (
            '-'
          ),
      },
      {
        title: t('tasks.table.errorMessage'),
        dataIndex: 'error_message',
        key: 'error_message',
        render: (value: string) => value || '-',
      },
      {
        title: t('tasks.table.createdAt'),
        dataIndex: 'created_at',
        key: 'created_at',
        width: 180,
      },
    ],
    [statusLabelMap, t, taskTypeLabelMap]
  )

  return (
    <section className="task-center-shell section-shell border border-[rgba(132,179,219,0.3)] px-6 py-8 sm:px-8">
      <Title level={2} className="!mb-2 !text-[#f2fbff]">
        {t('page.tasks.title')}
      </Title>
      <Paragraph className="!mb-6 !text-[#96b5cf]">{t('tasks.desc.autoRefresh')}</Paragraph>

      <Card className="task-center-card !border-[rgba(132,179,219,0.25)] !bg-[rgba(6,20,36,0.75)]">
        <Space wrap className="task-center-toolbar !mb-4">
          <Select
            value={taskType}
            onChange={setTaskType}
            options={taskTypeOptions}
            popupClassName="task-center-select-dropdown"
            style={{ width: 180 }}
          />
          <Select
            value={status}
            onChange={setStatus}
            options={statusOptions}
            popupClassName="task-center-select-dropdown"
            style={{ width: 180 }}
          />
          <Button className="task-center-refresh-btn" onClick={() => void loadTasks()} loading={loading}>
            {t('tasks.actions.refresh')}
          </Button>
        </Space>

        <Table<TaskRecord>
          className="task-center-table"
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
