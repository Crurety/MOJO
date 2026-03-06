import { useState, useCallback } from 'react'
import { contentApi } from '../api'
import { useTaskStore } from '../store'

export const useContent = () => {
  const { tasks, setTasks, addTask, currentTask, setCurrentTask } = useTaskStore()
  const [loading, setLoading] = useState(false)

  const createScript = async (data: any) => {
    setLoading(true)
    try {
      const response = await contentApi.createScript(data)
      return { success: true, data: response }
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || '创建失败' }
    } finally {
      setLoading(false)
    }
  }

  const fetchScripts = async (skip = 0, limit = 20) => {
    setLoading(true)
    try {
      const response = await contentApi.getScripts(skip, limit)
      return { success: true, data: response }
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || '获取失败' }
    } finally {
      setLoading(false)
    }
  }

  const createTask = async (data: any) => {
    setLoading(true)
    try {
      const response = await contentApi.createTask(data)
      addTask(response)
      return { success: true, data: response }
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || '创建任务失败' }
    } finally {
      setLoading(false)
    }
  }

  const fetchTasks = async (skip = 0, limit = 20, status?: number, taskType?: string) => {
    setLoading(true)
    try {
      const response = await contentApi.getTasks(skip, limit, status, taskType)
      setTasks(response)
      return { success: true, data: response }
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || '获取任务失败' }
    } finally {
      setLoading(false)
    }
  }

  const fetchTaskDetail = async (taskNo: string) => {
    setLoading(true)
    try {
      const response = await contentApi.getTask(taskNo)
      setCurrentTask(response)
      return { success: true, data: response }
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || '获取任务详情失败' }
    } finally {
      setLoading(false)
    }
  }

  const fetchWorks = async (skip = 0, limit = 20, workType?: string) => {
    setLoading(true)
    try {
      const response = await contentApi.getWorks(skip, limit, workType)
      return { success: true, data: response }
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || '获取作品失败' }
    } finally {
      setLoading(false)
    }
  }

  const deleteWork = async (id: number) => {
    setLoading(true)
    try {
      await contentApi.deleteWork(id)
      return { success: true }
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || '删除失败' }
    } finally {
      setLoading(false)
    }
  }

  const fetchGallery = async (skip = 0, limit = 20, workType?: string) => {
    setLoading(true)
    try {
      const response = await contentApi.getGallery(skip, limit, workType)
      return { success: true, data: response }
    } catch (error: any) {
      return { success: false, message: error.response?.data?.message || '获取作品集失败' }
    } finally {
      setLoading(false)
    }
  }

  return {
    tasks,
    currentTask,
    loading,
    createScript,
    fetchScripts,
    createTask,
    fetchTasks,
    fetchTaskDetail,
    fetchWorks,
    deleteWork,
    fetchGallery,
  }
}

export const useTaskPolling = (taskNo: string, onComplete?: (result: any) => void) => {
  const { updateTask } = useTaskStore()
  const [isPolling, setIsPolling] = useState(false)

  const startPolling = useCallback(() => {
    setIsPolling(true)
    const interval = setInterval(async () => {
      try {
        const response = await contentApi.getTask(taskNo)
        updateTask(taskNo, response)
        
        if (response.status === 2 || response.status === 3) {
          clearInterval(interval)
          setIsPolling(false)
          if (response.status === 2 && onComplete) {
            onComplete(response)
          }
        }
      } catch {
        clearInterval(interval)
        setIsPolling(false)
      }
    }, 3000)

    return () => {
      clearInterval(interval)
      setIsPolling(false)
    }
  }, [taskNo, updateTask, onComplete])

  return { isPolling, startPolling }
}
