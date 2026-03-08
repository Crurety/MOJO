import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'

export type FrontendLanguage = 'zh' | 'en'

const STORAGE_KEY = 'mojo_language'
const DEFAULT_LANGUAGE: FrontendLanguage = 'zh'

type MessageParams = Record<string, string | number>
type MessageDictionary = Record<string, string>

const messages: Record<FrontendLanguage, MessageDictionary> = {
  zh: {
    'common.switchLanguage': '切换语言',
    'common.currency': '¥',
    'common.loading': '加载中...',
    'common.save': '保存',
    'common.cancel': '取消',
    'common.previousPage': '上一页',
    'common.nextPage': '下一页',
    'common.totalRecords': '共 {count} 条记录',
    'lang.zh': '中文',
    'lang.en': 'English',

    'nav.home': '首页',
    'nav.script': '脚本生成',
    'nav.image': '图片生成',
    'nav.video': '视频生成',
    'nav.ad': '广告设计',
    'nav.works': '我的作品',
    'nav.tasks': '任务中心',
    'nav.gallery': '作品集',
    'nav.pricing': '价格方案',

    'layout.mobileMenuToggle': '切换菜单',
    'layout.accountDefault': '我的账户',
    'layout.balance': '余额',
    'layout.logout': '退出',
    'layout.login': '登录',
    'layout.register': '注册',
    'layout.navigation': '导航',
    'layout.closeMenu': '关闭菜单',

    'home.badge': 'AI CREATIVE SYSTEM',
    'home.title': '用一套流程完成从想法到发布',
    'home.subtitle':
      '将脚本生成、图像创作、视频合成和广告设计连接到一个工作台。你只需描述需求，剩下的交给 AI 流程自动推进。',
    'home.ctaStart': '立即开始',
    'home.ctaGallery': '浏览作品集',
    'home.overview': '实时概览',
    'home.stat.templates': '可用工作流模板',
    'home.stat.tasks': '日均生成任务',
    'home.stat.efficiency': '创作效率提升',
    'home.newTemplates': '新增模板：电商短视频、品牌故事脚本、产品图文广告',
    'home.coreBadge': '核心能力',
    'home.coreTitle': '一个界面完成多模态创作',
    'home.viewPricing': '查看价格方案 →',
    'home.feature.script.title': '脚本生成',
    'home.feature.script.desc': '根据产品目标快速生成脚本，支持不同风格和时长要求。',
    'home.feature.image.title': '图片生成',
    'home.feature.image.desc': '按提示词输出高质量图像，可扩展到封面、海报和素材图。',
    'home.feature.video.title': '视频生成',
    'home.feature.video.desc': '从创意到分镜再到视频输出，缩短制作链路。',
    'home.feature.ad.title': '广告设计',
    'home.feature.ad.desc': '快速产出图文和短视频广告素材，支持多渠道投放。',
    'home.workflowBadge': '工作方式',
    'home.workflowTitle': '三步完成高质量内容生产',
    'home.workflow.step1.title': '定义目标',
    'home.workflow.step1.desc': '输入主题、受众和风格，系统自动规划创作方向。',
    'home.workflow.step2.title': '批量生成',
    'home.workflow.step2.desc': '脚本、图片、视频并行生成，减少重复沟通成本。',
    'home.workflow.step3.title': '审核发布',
    'home.workflow.step3.desc': '统一在任务中心追踪状态，确认后直接用于发布。',
    'home.readyBadge': 'READY TO BUILD',
    'home.readyTitle': '开始构建你的 AI 创作流水线',
    'home.readySubtitle': '立即开通并体验统一任务编排，减少多工具切换与重复劳动。',
    'home.readyRegister': '免费注册',
    'home.readyPlans': '查看套餐',

    'pricing.badge': 'PRICING',
    'pricing.title': '灵活付费，按你的创作节奏扩展',
    'pricing.subtitle': '支持按次、月度、年度三种模式。先小规模试用，再按团队和业务增长逐步升级。',
    'pricing.mode.per_use': '按次付费',
    'pricing.mode.monthly': '月度订阅',
    'pricing.mode.yearly': '年度订阅',
    'pricing.modeSuffix.per_use': '/次',
    'pricing.modeSuffix.monthly': '/月',
    'pricing.modeSuffix.yearly': '/年',
    'pricing.planTag.default': '通用方案',
    'pricing.planTag.script': '脚本创作',
    'pricing.planTag.image': '图像创作',
    'pricing.planTag.video': '视频创作',
    'pricing.planTag.ad': '广告创作',
    'pricing.planName.script': '脚本生成',
    'pricing.planName.image': '图片生成',
    'pricing.planName.video': '视频生成',
    'pricing.planName.ad': '广告设计',
    'pricing.planDesc.script': '智能生成创作脚本，支持多种输出类型。',
    'pricing.planDesc.image': 'AI 图片生成，支持多种风格和分辨率。',
    'pricing.planDesc.video': 'AI 视频生成，支持自定义时长和风格。',
    'pricing.planDesc.ad': '智能广告创意设计，图文视频全覆盖。',
    'pricing.planHighlight.script.1': '高频产出',
    'pricing.planHighlight.script.2': '低成本起步',
    'pricing.planHighlight.image.1': '多风格生成',
    'pricing.planHighlight.image.2': '支持素材扩展',
    'pricing.planHighlight.video.1': '分镜到成片',
    'pricing.planHighlight.video.2': '支持时长配置',
    'pricing.planHighlight.ad.1': '多渠道广告',
    'pricing.planHighlight.ad.2': '图文视频联动',
    'pricing.buyNow': '立即购买',
    'pricing.subscribeNow': '立即订阅',
    'pricing.modal.title': '选择支付方式',
    'pricing.modal.currentPlan': '当前方案：{plan} · {mode}',
    'pricing.modal.selected': '已选',
    'pricing.modal.close': '关闭支付弹窗',
    'pricing.payment.balance': '余额支付',
    'pricing.payment.wechat': '微信支付',
    'pricing.payment.alipay': '支付宝',
    'pricing.payment.unionpay': '银联支付',
    'pricing.payment.confirm': '确认支付',

    'auth.login.portal': 'Access Portal',
    'auth.login.title': '登录',
    'auth.login.success': '登录成功',
    'auth.login.failed': '登录失败，请检查账号和密码',
    'auth.login.error': '登录发生错误',
    'auth.login.accountRequired': '请输入邮箱或手机号',
    'auth.login.passwordRequired': '请输入密码',
    'auth.login.accountPlaceholder': '邮箱或手机号',
    'auth.login.passwordPlaceholder': '密码',
    'auth.login.submit': '登录',
    'auth.login.registerNow': '立即注册',
    'auth.login.forgotPassword': '忘记密码',

    'auth.register.portal': 'Create Account',
    'auth.register.title': '注册',
    'auth.register.success': '注册成功，请登录',
    'auth.register.failed': '注册失败',
    'auth.register.error': '注册发生错误',
    'auth.register.emailRequired': '请输入邮箱',
    'auth.register.emailInvalid': '请输入有效的邮箱地址',
    'auth.register.phoneInvalid': '请输入有效的手机号',
    'auth.register.passwordRequired': '请输入密码',
    'auth.register.passwordMin': '密码至少6位，且必须包含字母和数字',
    'auth.register.confirmRequired': '请确认密码',
    'auth.register.passwordMismatch': '两次密码不一致',
    'auth.register.emailPlaceholder': '邮箱',
    'auth.register.phonePlaceholder': '手机号（选填）',
    'auth.register.passwordPlaceholder': '密码',
    'auth.register.confirmPlaceholder': '确认密码',
    'auth.register.submit': '注册',
    'auth.register.haveAccount': '已有账号？',
    'auth.register.loginNow': '立即登录',

    'page.scriptCreate.title': '文字生成脚本',
    'page.scriptCreate.desc': '文字生成脚本功能开发中...',
    'page.imageCreate.title': '图片生成',
    'page.imageCreate.desc': '图片生成功能开发中...',
    'page.videoCreate.title': '视频生成',
    'page.videoCreate.desc': '视频生成功能开发中...',
    'page.adCreate.title': '广告设计',
    'page.adCreate.desc': '广告设计功能开发中...',
    'page.works.title': '我的作品',
    'page.works.desc': '作品管理功能开发中...',
    'page.tasks.title': '任务中心',
    'page.tasks.desc': '任务中心功能开发中...',
    'page.gallery.title': '作品集',
    'page.gallery.desc': '作品集功能开发中...',
    'page.account.title': '个人中心',
    'page.account.desc': '个人中心功能开发中...',

    'hook.auth.loginFailed': '登录失败',
    'hook.content.createFailed': '创建失败',
    'hook.content.fetchFailed': '获取失败',
    'hook.content.createTaskFailed': '创建任务失败',
    'hook.content.fetchTaskFailed': '获取任务失败',
    'hook.content.fetchTaskDetailFailed': '获取任务详情失败',
    'hook.content.fetchWorksFailed': '获取作品失败',
    'hook.content.deleteFailed': '删除失败',
    'hook.content.fetchGalleryFailed': '获取作品集失败',
    'hook.payment.createOrderFailed': '创建订单失败',
    'hook.payment.fetchOrderFailed': '获取订单失败',
    'hook.payment.fetchOrderDetailFailed': '获取订单详情失败',
    'hook.payment.payFailed': '支付失败',
  },
  en: {
    'common.switchLanguage': 'Switch language',
    'common.currency': '$',
    'common.loading': 'Loading...',
    'common.save': 'Save',
    'common.cancel': 'Cancel',
    'common.previousPage': 'Previous',
    'common.nextPage': 'Next',
    'common.totalRecords': 'Total {count} records',
    'lang.zh': '中文',
    'lang.en': 'English',

    'nav.home': 'Home',
    'nav.script': 'Script',
    'nav.image': 'Image',
    'nav.video': 'Video',
    'nav.ad': 'Ad Design',
    'nav.works': 'My Works',
    'nav.tasks': 'Tasks',
    'nav.gallery': 'Gallery',
    'nav.pricing': 'Pricing',

    'layout.mobileMenuToggle': 'Toggle menu',
    'layout.accountDefault': 'My Account',
    'layout.balance': 'Balance',
    'layout.logout': 'Logout',
    'layout.login': 'Login',
    'layout.register': 'Register',
    'layout.navigation': 'Navigation',
    'layout.closeMenu': 'Close menu',

    'home.badge': 'AI CREATIVE SYSTEM',
    'home.title': 'Go from idea to launch in one workflow',
    'home.subtitle':
      'Unify script generation, image creation, video synthesis, and ad design in one workspace. Describe your goal and let AI move execution forward.',
    'home.ctaStart': 'Start now',
    'home.ctaGallery': 'Browse gallery',
    'home.overview': 'Live overview',
    'home.stat.templates': 'Workflow templates',
    'home.stat.tasks': 'Tasks per day',
    'home.stat.efficiency': 'Productivity gain',
    'home.newTemplates': 'New templates: ecommerce shorts, brand story scripts, product ad creatives',
    'home.coreBadge': 'Core Capabilities',
    'home.coreTitle': 'Create across formats in one interface',
    'home.viewPricing': 'View pricing →',
    'home.feature.script.title': 'Script Generation',
    'home.feature.script.desc': 'Generate scripts fast with style and duration control.',
    'home.feature.image.title': 'Image Generation',
    'home.feature.image.desc': 'Create high-quality images for covers, posters, and assets.',
    'home.feature.video.title': 'Video Generation',
    'home.feature.video.desc': 'Move from concept and storyboard to rendered video faster.',
    'home.feature.ad.title': 'Ad Design',
    'home.feature.ad.desc': 'Generate image and short-form ad creatives for multiple channels.',
    'home.workflowBadge': 'Workflow',
    'home.workflowTitle': 'Produce high-quality content in three steps',
    'home.workflow.step1.title': 'Define goals',
    'home.workflow.step1.desc': 'Input topic, audience, and style; get an auto-planned direction.',
    'home.workflow.step2.title': 'Generate at scale',
    'home.workflow.step2.desc': 'Create scripts, images, and videos in parallel.',
    'home.workflow.step3.title': 'Review and publish',
    'home.workflow.step3.desc': 'Track status in one task center, then publish directly.',
    'home.readyBadge': 'READY TO BUILD',
    'home.readyTitle': 'Build your AI content pipeline',
    'home.readySubtitle': 'Launch quickly with unified task orchestration and fewer tool switches.',
    'home.readyRegister': 'Free sign up',
    'home.readyPlans': 'View plans',

    'pricing.badge': 'PRICING',
    'pricing.title': 'Flexible pricing that scales with your production pace',
    'pricing.subtitle':
      'Choose pay-per-use, monthly, or yearly plans. Start small and scale as your team grows.',
    'pricing.mode.per_use': 'Pay per use',
    'pricing.mode.monthly': 'Monthly',
    'pricing.mode.yearly': 'Yearly',
    'pricing.modeSuffix.per_use': '/use',
    'pricing.modeSuffix.monthly': '/month',
    'pricing.modeSuffix.yearly': '/year',
    'pricing.planTag.default': 'General',
    'pricing.planTag.script': 'Script',
    'pricing.planTag.image': 'Image',
    'pricing.planTag.video': 'Video',
    'pricing.planTag.ad': 'Advertising',
    'pricing.planName.script': 'Script Generation',
    'pricing.planName.image': 'Image Generation',
    'pricing.planName.video': 'Video Generation',
    'pricing.planName.ad': 'Ad Design',
    'pricing.planDesc.script': 'Generate content scripts with multiple output styles.',
    'pricing.planDesc.image': 'Create AI images across styles and resolutions.',
    'pricing.planDesc.video': 'Generate AI videos with custom duration and style.',
    'pricing.planDesc.ad': 'Design ad creatives across image and video formats.',
    'pricing.planHighlight.script.1': 'High-frequency output',
    'pricing.planHighlight.script.2': 'Low-cost start',
    'pricing.planHighlight.image.1': 'Multi-style generation',
    'pricing.planHighlight.image.2': 'Asset extension support',
    'pricing.planHighlight.video.1': 'Storyboard to final cut',
    'pricing.planHighlight.video.2': 'Duration control',
    'pricing.planHighlight.ad.1': 'Multi-channel ads',
    'pricing.planHighlight.ad.2': 'Image-video synergy',
    'pricing.buyNow': 'Buy now',
    'pricing.subscribeNow': 'Subscribe now',
    'pricing.modal.title': 'Choose payment method',
    'pricing.modal.currentPlan': 'Current plan: {plan} · {mode}',
    'pricing.modal.selected': 'Selected',
    'pricing.modal.close': 'Close payment dialog',
    'pricing.payment.balance': 'Balance',
    'pricing.payment.wechat': 'WeChat Pay',
    'pricing.payment.alipay': 'Alipay',
    'pricing.payment.unionpay': 'UnionPay',
    'pricing.payment.confirm': 'Confirm payment',

    'auth.login.portal': 'Access Portal',
    'auth.login.title': 'Login',
    'auth.login.success': 'Logged in successfully',
    'auth.login.failed': 'Login failed. Check your account and password.',
    'auth.login.error': 'An error occurred during login',
    'auth.login.accountRequired': 'Please enter email or phone number',
    'auth.login.passwordRequired': 'Please enter password',
    'auth.login.accountPlaceholder': 'Email or phone number',
    'auth.login.passwordPlaceholder': 'Password',
    'auth.login.submit': 'Login',
    'auth.login.registerNow': 'Create account',
    'auth.login.forgotPassword': 'Forgot password',

    'auth.register.portal': 'Create Account',
    'auth.register.title': 'Register',
    'auth.register.success': 'Registration successful. Please log in.',
    'auth.register.failed': 'Registration failed',
    'auth.register.error': 'An error occurred during registration',
    'auth.register.emailRequired': 'Please enter email',
    'auth.register.emailInvalid': 'Please enter a valid email address',
    'auth.register.phoneInvalid': 'Please enter a valid phone number',
    'auth.register.passwordRequired': 'Please enter password',
    'auth.register.passwordMin': 'Password must be at least 6 characters and include letters and numbers',
    'auth.register.confirmRequired': 'Please confirm your password',
    'auth.register.passwordMismatch': 'Passwords do not match',
    'auth.register.emailPlaceholder': 'Email',
    'auth.register.phonePlaceholder': 'Phone (optional)',
    'auth.register.passwordPlaceholder': 'Password',
    'auth.register.confirmPlaceholder': 'Confirm password',
    'auth.register.submit': 'Register',
    'auth.register.haveAccount': 'Already have an account?',
    'auth.register.loginNow': 'Login now',

    'page.scriptCreate.title': 'Script Creation',
    'page.scriptCreate.desc': 'Script generation is under development...',
    'page.imageCreate.title': 'Image Creation',
    'page.imageCreate.desc': 'Image generation is under development...',
    'page.videoCreate.title': 'Video Creation',
    'page.videoCreate.desc': 'Video generation is under development...',
    'page.adCreate.title': 'Ad Design',
    'page.adCreate.desc': 'Ad design is under development...',
    'page.works.title': 'My Works',
    'page.works.desc': 'Work management is under development...',
    'page.tasks.title': 'Task Center',
    'page.tasks.desc': 'Task center is under development...',
    'page.gallery.title': 'Gallery',
    'page.gallery.desc': 'Gallery is under development...',
    'page.account.title': 'Account Center',
    'page.account.desc': 'Account center is under development...',

    'hook.auth.loginFailed': 'Login failed',
    'hook.content.createFailed': 'Create failed',
    'hook.content.fetchFailed': 'Fetch failed',
    'hook.content.createTaskFailed': 'Failed to create task',
    'hook.content.fetchTaskFailed': 'Failed to fetch task',
    'hook.content.fetchTaskDetailFailed': 'Failed to fetch task details',
    'hook.content.fetchWorksFailed': 'Failed to fetch works',
    'hook.content.deleteFailed': 'Delete failed',
    'hook.content.fetchGalleryFailed': 'Failed to fetch gallery',
    'hook.payment.createOrderFailed': 'Failed to create order',
    'hook.payment.fetchOrderFailed': 'Failed to fetch order',
    'hook.payment.fetchOrderDetailFailed': 'Failed to fetch order details',
    'hook.payment.payFailed': 'Payment failed',
  },
}

const detectLanguage = (): FrontendLanguage => {
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

const translateByLanguage = (
  language: FrontendLanguage,
  key: string,
  params?: MessageParams
): string => {
  const localized = messages[language][key] ?? messages.zh[key] ?? key
  return interpolate(localized, params)
}

type I18nContextValue = {
  language: FrontendLanguage
  setLanguage: (next: FrontendLanguage) => void
  t: (key: string, params?: MessageParams) => string
}

const I18nContext = createContext<I18nContextValue | null>(null)

export const I18nProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<FrontendLanguage>(detectLanguage)

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, language)
    document.documentElement.lang = language
  }, [language])

  const setLanguage = useCallback((next: FrontendLanguage) => {
    setLanguageState(next)
  }, [])

  const t = useCallback(
    (key: string, params?: MessageParams) => translateByLanguage(language, key, params),
    [language]
  )

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

export const getCurrentLanguage = (): FrontendLanguage => detectLanguage()

export const translateStatic = (key: string, params?: MessageParams): string =>
  translateByLanguage(detectLanguage(), key, params)
