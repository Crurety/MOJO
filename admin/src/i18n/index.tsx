import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'

export type AdminLanguage = 'zh' | 'en'

const STORAGE_KEY = 'mojo_language'
const DEFAULT_LANGUAGE: AdminLanguage = 'zh'

type MessageParams = Record<string, string | number>
type MessageDictionary = Record<string, string>

const messages: Record<AdminLanguage, MessageDictionary> = {
  zh: {
    'common.switchLanguage': '切换语言',
    'common.currency': '¥',
    'common.loading': '加载中...',
    'common.previousPage': '上一页',
    'common.nextPage': '下一页',
    'common.totalRecords': '共 {count} 条记录',
    'common.save': '保存',
    'common.cancel': '取消',
    'common.allStatuses': '全部状态',
    'common.allTypes': '全部类型',
    'common.unknown': '未知',
    'common.query': '查询',
    'common.saving': '保存中...',

    'layout.title': '后台管理',
    'layout.logout': '退出',
    'layout.toggleSidebar': '切换侧边栏',
    'layout.nav.dashboard': '仪表盘',
    'layout.nav.users': '用户管理',
    'layout.nav.orders': '订单管理',
    'layout.nav.revenue': '收入统计',
    'layout.nav.permissions': '权限价格',
    'layout.nav.aiConfig': 'AI API 配置',

    'login.title': '后台管理登录',
    'login.subtitle': '请输入管理员账号和密码',
    'login.accountLabel': '账号',
    'login.passwordLabel': '密码',
    'login.accountPlaceholder': '请输入账号',
    'login.passwordPlaceholder': '请输入密码',
    'login.submit': '登录',
    'login.submitting': '登录中...',
    'login.failed': '登录失败',
    'login.retry': '登录失败，请重试',

    'dashboard.title': '仪表盘',
    'dashboard.totalUsers': '总用户数',
    'dashboard.todayActive': '今日活跃',
    'dashboard.totalOrders': '总订单数',
    'dashboard.totalRevenue': '总收入',
    'dashboard.revenueTrend': '收入趋势',
    'dashboard.revenueChart': '收入图表',
    'dashboard.userGrowth': '用户增长',
    'dashboard.userGrowthChart': '用户增长图表',
    'dashboard.recentOrders': '最近订单',
    'dashboard.noOrders': '暂无订单',
    'dashboard.orderNo': '订单号',
    'dashboard.user': '用户',
    'dashboard.type': '类型',
    'dashboard.amount': '金额',
    'dashboard.status': '状态',
    'dashboard.time': '时间',
    'dashboard.orderType.permission': '权限购买',
    'dashboard.orderType.balance': '余额充值',
    'dashboard.orderStatus.completed': '已完成',
    'dashboard.orderStatus.pending': '待处理',

    'user.title': '用户管理',
    'user.filterStatus': '筛选状态',
    'user.status.disabled': '禁用',
    'user.status.active': '正常',
    'user.status.unknown': '未知',
    'user.column.id': 'ID',
    'user.column.nickname': '昵称',
    'user.column.email': '邮箱',
    'user.column.phone': '手机号',
    'user.column.balance': '余额',
    'user.column.status': '状态',
    'user.column.registeredAt': '注册时间',
    'user.column.action': '操作',
    'user.noUsers': '暂无用户',
    'user.enable': '启用',
    'user.disable': '禁用',

    'order.title': '订单管理',
    'order.status.pending': '待支付',
    'order.status.completed': '已完成',
    'order.status.cancelled': '已取消',
    'order.type.permission': '权限购买',
    'order.type.balance': '余额充值',
    'order.column.orderNo': '订单号',
    'order.column.user': '用户',
    'order.column.type': '类型',
    'order.column.product': '产品',
    'order.column.amount': '金额',
    'order.column.method': '支付方式',
    'order.column.status': '状态',
    'order.column.createdAt': '创建时间',
    'order.column.completedAt': '完成时间',
    'order.noOrders': '暂无订单',
    'order.payment.wechat': '微信支付',
    'order.payment.alipay': '支付宝',
    'order.payment.unionpay': '银联支付',
    'order.payment.balance': '余额支付',

    'revenue.title': '收入统计',
    'revenue.startDate': '开始日期',
    'revenue.endDate': '结束日期',
    'revenue.totalRevenue': '总收入',
    'revenue.orderCount': '订单数量',
    'revenue.avgOrderAmount': '平均订单金额',
    'revenue.revenueTrend': '收入趋势',
    'revenue.revenueTrendChart': '收入趋势图表',
    'revenue.source': '收入来源',
    'revenue.sourceChart': '收入来源饼图',

    'permission.title': '权限价格设置',
    'permission.saveSuccess': '保存成功',
    'permission.type': '权限类型',
    'permission.mode.perUse': '按次付费',
    'permission.mode.monthly': '月度订阅',
    'permission.mode.yearly': '年度订阅',
    'permission.type.script': '脚本生成',
    'permission.type.image': '图片生成',
    'permission.type.video': '视频生成',
    'permission.type.ad': '广告设计',
  },
  en: {
    'common.switchLanguage': 'Switch language',
    'common.currency': '$',
    'common.loading': 'Loading...',
    'common.previousPage': 'Previous',
    'common.nextPage': 'Next',
    'common.totalRecords': 'Total {count} records',
    'common.save': 'Save',
    'common.cancel': 'Cancel',
    'common.allStatuses': 'All statuses',
    'common.allTypes': 'All types',
    'common.unknown': 'Unknown',
    'common.query': 'Query',
    'common.saving': 'Saving...',

    'layout.title': 'Admin Console',
    'layout.logout': 'Logout',
    'layout.toggleSidebar': 'Toggle sidebar',
    'layout.nav.dashboard': 'Dashboard',
    'layout.nav.users': 'Users',
    'layout.nav.orders': 'Orders',
    'layout.nav.revenue': 'Revenue',
    'layout.nav.permissions': 'Permission Pricing',
    'layout.nav.aiConfig': 'AI API Config',

    'login.title': 'Admin Login',
    'login.subtitle': 'Please enter administrator credentials',
    'login.accountLabel': 'Account',
    'login.passwordLabel': 'Password',
    'login.accountPlaceholder': 'Enter account',
    'login.passwordPlaceholder': 'Enter password',
    'login.submit': 'Login',
    'login.submitting': 'Signing in...',
    'login.failed': 'Login failed',
    'login.retry': 'Login failed, please try again',

    'dashboard.title': 'Dashboard',
    'dashboard.totalUsers': 'Total users',
    'dashboard.todayActive': 'Active today',
    'dashboard.totalOrders': 'Total orders',
    'dashboard.totalRevenue': 'Total revenue',
    'dashboard.revenueTrend': 'Revenue trend',
    'dashboard.revenueChart': 'Revenue chart',
    'dashboard.userGrowth': 'User growth',
    'dashboard.userGrowthChart': 'User growth chart',
    'dashboard.recentOrders': 'Recent orders',
    'dashboard.noOrders': 'No orders',
    'dashboard.orderNo': 'Order no.',
    'dashboard.user': 'User',
    'dashboard.type': 'Type',
    'dashboard.amount': 'Amount',
    'dashboard.status': 'Status',
    'dashboard.time': 'Time',
    'dashboard.orderType.permission': 'Permission purchase',
    'dashboard.orderType.balance': 'Balance top-up',
    'dashboard.orderStatus.completed': 'Completed',
    'dashboard.orderStatus.pending': 'Pending',

    'user.title': 'User Management',
    'user.filterStatus': 'Filter status',
    'user.status.disabled': 'Disabled',
    'user.status.active': 'Active',
    'user.status.unknown': 'Unknown',
    'user.column.id': 'ID',
    'user.column.nickname': 'Nickname',
    'user.column.email': 'Email',
    'user.column.phone': 'Phone',
    'user.column.balance': 'Balance',
    'user.column.status': 'Status',
    'user.column.registeredAt': 'Registered at',
    'user.column.action': 'Action',
    'user.noUsers': 'No users',
    'user.enable': 'Enable',
    'user.disable': 'Disable',

    'order.title': 'Order Management',
    'order.status.pending': 'Pending Payment',
    'order.status.completed': 'Completed',
    'order.status.cancelled': 'Cancelled',
    'order.type.permission': 'Permission purchase',
    'order.type.balance': 'Balance top-up',
    'order.column.orderNo': 'Order no.',
    'order.column.user': 'User',
    'order.column.type': 'Type',
    'order.column.product': 'Product',
    'order.column.amount': 'Amount',
    'order.column.method': 'Payment method',
    'order.column.status': 'Status',
    'order.column.createdAt': 'Created at',
    'order.column.completedAt': 'Completed at',
    'order.noOrders': 'No orders',
    'order.payment.wechat': 'WeChat Pay',
    'order.payment.alipay': 'Alipay',
    'order.payment.unionpay': 'UnionPay',
    'order.payment.balance': 'Balance',

    'revenue.title': 'Revenue Statistics',
    'revenue.startDate': 'Start date',
    'revenue.endDate': 'End date',
    'revenue.totalRevenue': 'Total revenue',
    'revenue.orderCount': 'Order count',
    'revenue.avgOrderAmount': 'Avg. order amount',
    'revenue.revenueTrend': 'Revenue trend',
    'revenue.revenueTrendChart': 'Revenue trend chart',
    'revenue.source': 'Revenue source',
    'revenue.sourceChart': 'Revenue source pie chart',

    'permission.title': 'Permission Pricing',
    'permission.saveSuccess': 'Saved successfully',
    'permission.type': 'Permission type',
    'permission.mode.perUse': 'Per-use',
    'permission.mode.monthly': 'Monthly',
    'permission.mode.yearly': 'Yearly',
    'permission.type.script': 'Script Generation',
    'permission.type.image': 'Image Generation',
    'permission.type.video': 'Video Generation',
    'permission.type.ad': 'Ad Design',
  },
}

const detectLanguage = (): AdminLanguage => {
  if (typeof window === 'undefined') {
    return DEFAULT_LANGUAGE
  }

  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored === 'zh' || stored === 'en') {
    return stored
  }

  const browserLanguage = window.navigator.language.toLowerCase()
  return browserLanguage.startsWith('zh') ? 'zh' : 'en'
}

const interpolate = (template: string, params?: MessageParams): string => {
  if (!params) {
    return template
  }

  let content = template
  Object.entries(params).forEach(([key, value]) => {
    content = content.split(`{${key}}`).join(String(value))
  })
  return content
}

const translateByLanguage = (language: AdminLanguage, key: string, params?: MessageParams): string => {
  const localized = messages[language][key] ?? messages.zh[key] ?? key
  return interpolate(localized, params)
}

type I18nContextValue = {
  language: AdminLanguage
  setLanguage: (next: AdminLanguage) => void
  t: (key: string, params?: MessageParams) => string
}

const I18nContext = createContext<I18nContextValue | null>(null)

export const I18nProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<AdminLanguage>(detectLanguage)

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, language)
    document.documentElement.lang = language
  }, [language])

  const setLanguage = useCallback((next: AdminLanguage) => {
    setLanguageState(next)
  }, [])

  const t = useCallback((key: string, params?: MessageParams) => translateByLanguage(language, key, params), [language])

  const value = useMemo(
    () => ({
      language,
      setLanguage,
      t,
    }),
    [language, setLanguage, t]
  )

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>
}

export const useI18n = (): I18nContextValue => {
  const context = useContext(I18nContext)
  if (!context) {
    throw new Error('useI18n must be used within I18nProvider')
  }
  return context
}

export const getCurrentLanguage = (): AdminLanguage => detectLanguage()
