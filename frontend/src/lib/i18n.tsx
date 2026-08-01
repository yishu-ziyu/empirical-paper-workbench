// ── i18n 双语支持 ──

import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'

type Lang = 'zh' | 'en'
const LS_LANG_KEY = 'econpaper_lang'

// ── 翻译字典 ──

const zh = {
  // App / Header
  'app.title': 'econpaper v0',
  'app.upload': '上传 CSV',
  'app.uploading': '上传中...',
  'app.hint': '请上传 CSV 文件开始分析',
  'app.logout': '退出',
  'app.toggleLeft': '切换左栏',
  'app.toggleRight': '切换右栏',
  'app.degradedBanner': '⚠ 部分功能以降级模式运行',
  'app.reconnecting': '连接已断开，正在重连...',
  'app.outline': '大纲',
  'app.openEda': '打开 EDA',
  'app.langSwitch': 'EN',
  'app.welcomeBadge': 'AI 驱动经济学论文',
  'app.welcomeDesc': '上传数据集，让 AI 自动生成完整经济学论文——从数据探索到格式化输出。',
  'app.step1Title': '上传数据',
  'app.step1Desc': '上传 CSV 文件开始分析，支持任何表格型经济学数据集。',
  'app.step2Title': '探索与分析',
  'app.step2Desc': '使用 EDA 工具探索描述性统计、相关性矩阵和分布情况。',
  'app.step3Title': '生成论文',
  'app.step3Desc': 'AI 实时流式生成完整论文，支持 LaTeX 排版与一键导出。',
  'app.welcomeUploadBtn': '上传 CSV 开始',
  'app.welcomeUploading': '上传中…',
  'app.welcomeHint': '支持格式：CSV · 您的数据仅用于本次会话，不会永久存储。',

  // LoginPage
  'login.subtitle': '登录您的账户',
  'login.email': '邮箱',
  'login.emailPlaceholder': 'you@example.com',
  'login.password': '密码',
  'login.passwordPlaceholder': '••••••••',
  'login.signIn': '登录',
  'login.signingIn': '登录中...',
  'login.noAccount': '没有账户？',
  'login.createOne': '创建一个',

  // RegisterPage
  'register.subtitle': '创建账户',
  'register.email': '邮箱',
  'register.emailPlaceholder': 'you@example.com',
  'register.username': '用户名',
  'register.usernamePlaceholder': 'your_username',
  'register.password': '密码',
  'register.passwordPlaceholder': '••••••••',
  'register.confirmPassword': '确认密码',
  'register.confirmPasswordPlaceholder': '••••••••',
  'register.createAccount': '创建账户',
  'register.creating': '创建中...',
  'register.hasAccount': '已有账户？',
  'register.signIn': '登录',
  'register.validateEmail': '请输入有效的邮箱地址',
  'register.validateUsername': '用户名为必填项',
  'register.validatePassword': '密码至少需要 6 个字符',
  'register.validatePasswordMatch': '两次密码不一致',

  // Editor
  'editor.title': '编辑器',
  'editor.showRaw': '显示源码',
  'editor.showFormatted': '显示格式化',
  'editor.emptyHint': '请上传 CSV 文件开始分析',
  'editor.emptyDesc': '论文内容将在此处流式生成',
  'editor.paused': '暂停：',
  'editor.degradationTitle': '⚠ 降级详情',
  'editor.confirmContinue': '确认，继续生成',
  'editor.editTitle': '修改标题',
  'editor.continueHint': '标题已生成，请确认后继续生成论文正文',

  // EdaSidebar
  'eda.title': 'EDA',
  'eda.loading': '加载中...',
  'eda.corrMatrix': '相关性矩阵：',
  'eda.charlsDetected': 'CHARLS 数据集',
  'eda.variableWizard': '变量向导',

  // AgentPanel
  'agent.title': 'Agent',
  'agent.connection': '连接',
  'agent.currentNode': '当前节点',
  'agent.status': '状态',
  'agent.degraded': '⚠ 降级',

  // Outline
  'outline.addChapter': '+ 添加章节',
  'outline.confirm': '确认大纲',
  'outline.newChapter': '新章节',

  // ErrorBoundary
  'error.panelError': '面板渲染出错',
  'error.retry': '重试',

  // CleanWizard
  'clean.profiling': '数据 Profiling',
  'clean.rows': '行数',
  'clean.cols': '列数',
  'clean.variable': '变量',
  'clean.type': '类型',
  'clean.missingRate': '缺失率',
  'clean.unique': '唯一值',
  'clean.isNumeric': '数值型',
  'clean.strategy': '缺失值处理策略',
  'clean.outlier': '异常值缩尾对比',
  'clean.before': 'Before (前) max',
  'clean.after': 'After (后) max',

  // DirectionForm
  'direction.question': '研究问题',
  'direction.dv': '因变量',
  'direction.iv': '自变量',
  'direction.controls': '控制变量 (逗号分隔)',
  'direction.method': '方法',
  'direction.template': '模板',
  'direction.submit': '提交',
  'direction.selectMethod': '选择方法…',

  // BalanceReport
  'balance.title': '面板平衡性检查',
  'balance.panelId': '个体 ID 列',
  'balance.panelIdPlaceholder': '如 id',
  'balance.timeCol': '时间列',
  'balance.timeColPlaceholder': '如 year',
  'balance.check': '检查平衡性',
  'balance.checking': '检查中...',
  'balance.metric': '指标',
  'balance.value': '值',
  'balance.balanced': '平衡个体数',
  'balance.unbalanced': '不平衡个体数',
  'balance.periods': '期数',
  'balance.attrition': '流失率 (attrition)',

  // ChapterWriter
  'chapter.streaming': '正在生成…（流式接收中）',
  'chapter.regenerate': '重新生成',
  'chapter.rollback': '回滚',
  'chapter.save': '保存',
  'chapter.edit': '编辑',
  'chapter.approve': '通过',

  // CharlsWizard
  'charls.title': '检测到 CHARLS 数据集',
  'charls.cancel': '取消',
  'charls.mapping': '变量映射（可编辑）',
  'charls.originalVar': '原始变量',
  'charls.readableVar': '可读变量名',
  'charls.waves': '调查波次',
  'charls.presets': '筛选预设',
  'charls.confirm': '确认',

  // CodeExportDialog
  'codeExport.title': '下载代码',
  'codeExport.desc': '选择要下载的代码格式。每种格式包含相同的分析逻辑，适配对应统计软件的语法。',
  'codeExport.close': '关闭',

  // DocExportDialog
  'docExport.title': '导出文档',
  'docExport.selectTemplate': '选择模板',
  'docExport.exportFormat': '导出格式',
  'docExport.session': '会话',

  // LatexPreview
  'latex.title': 'LaTeX 源码',
  'latex.refresh': '刷新预览',
  'latex.degraded': 'PDF 预览不可用：latexmk 未安装，仅支持 .tex 源码导出。',

  // ReviewPanel
  'review.title': '章节评审',
  'review.autoPass': '自动通过',
  'review.autoFail': '自动不通过',
  'review.rubric': '评审 Rubric（5 维）',
  'review.feedback': '评审反馈',
  'review.suggestions': '修改建议',
  'review.noFeedback': '暂无评审反馈',
  'review.noSuggestions': '暂无修改建议',
  'review.accept': '接受',
  'review.acceptRegen': '接受重生成',
  'review.reject': '拒绝重生成',
  'review.forcePass': '强制通过',
  'review.submitError': '决策提交失败：',

  // SampleFilter
  'filter.title': '样本筛选',
  'filter.col': '列名',
  'filter.colPlaceholder': '如 age',
  'filter.op': '操作符',
  'filter.value': '值',
  'filter.valuePlaceholder': '如 50',
  'filter.addCondition': '添加条件',
  'filter.conditions': '已添加条件 (AND)',
  'filter.apply': '应用筛选',
  'filter.applying': '筛选中...',
  'filter.nBefore': '筛选前样本量',
  'filter.nAfter': '筛选后样本量',

  // VariableConstructor
  'vc.title': '变量构造',
  'vc.type': '构造类型',
  'vc.col': '列名',
  'vc.colPlaceholder': '如 income',
  'vc.constructing': '构造中...',
  'vc.construct': '构造变量',
  'vc.constructed': '已构造变量',

  // VersionHistory
  'version.empty': '暂无版本',
  'version.label': '版本',
  'version.current': '（当前）',

  // ProgressBar
  'progress.completed': '已完成',

  // MethodSelector
  'method.select': '选择方法…',

  // StepIndicator
  'step.uploadData': '上传数据',
  'step.exploreData': '探索数据',
  'step.generatePaper': '生成论文',

  // ReviewPanel — rubric dimensions
  'review.rubricEndogeneity': '内生性',
  'review.rubricIdentification': '识别策略',
  'review.rubricRobustness': '稳健性',
  'review.rubricContribution': '贡献度',
  'review.rubricReadability': '可读性',

  // ReviewPanel — iteration and score labels
  'review.roundLabel': '第 {0}/{1} 轮',
  'review.scoreLabel': '综合 {0}',
  'review.forcePassDisabled': '自动评审已通过，无需强制通过',
}

const en: typeof zh = {
  'app.title': 'econpaper v0',
  'app.upload': 'Upload CSV',
  'app.uploading': 'Uploading...',
  'app.hint': 'Upload a CSV file to start',
  'app.logout': 'Logout',
  'app.toggleLeft': 'Toggle left panel',
  'app.toggleRight': 'Toggle right panel',
  'app.degradedBanner': '⚠ Running in degraded mode',
  'app.reconnecting': 'Disconnected, reconnecting...',
  'app.outline': 'Outline',
  'app.openEda': 'Open EDA',
  'app.langSwitch': '中',
  'app.welcomeBadge': 'AI-Powered Economics Paper',
  'app.welcomeDesc': 'Upload your dataset and let AI generate a complete economics paper — from data exploration to formatted output.',
  'app.step1Title': 'Upload your data',
  'app.step1Desc': 'Upload a CSV file to get started. We accept any tabular economics dataset.',
  'app.step2Title': 'Explore and analyze',
  'app.step2Desc': 'Use EDA tools to explore descriptive statistics, correlations, and distributions.',
  'app.step3Title': 'Generate your paper',
  'app.step3Desc': 'AI writes the full paper with real-time streaming, LaTeX formatting, and export.',
  'app.welcomeUploadBtn': 'Upload CSV to Start',
  'app.welcomeUploading': 'Uploading...',
  'app.welcomeHint': 'Supported format: CSV · Your data stays private and is not stored permanently.',

  'login.subtitle': 'Sign in to your account',
  'login.email': 'Email',
  'login.emailPlaceholder': 'you@example.com',
  'login.password': 'Password',
  'login.passwordPlaceholder': '••••••••',
  'login.signIn': 'Sign in',
  'login.signingIn': 'Signing in...',
  'login.noAccount': "Don't have an account?",
  'login.createOne': 'Create one',

  'register.subtitle': 'Create your account',
  'register.email': 'Email',
  'register.emailPlaceholder': 'you@example.com',
  'register.username': 'Username',
  'register.usernamePlaceholder': 'your_username',
  'register.password': 'Password',
  'register.passwordPlaceholder': '••••••••',
  'register.confirmPassword': 'Confirm password',
  'register.confirmPasswordPlaceholder': '••••••••',
  'register.createAccount': 'Create account',
  'register.creating': 'Creating account...',
  'register.hasAccount': 'Already have an account?',
  'register.signIn': 'Sign in',
  'register.validateEmail': 'Please enter a valid email address',
  'register.validateUsername': 'Username is required',
  'register.validatePassword': 'Password must be at least 6 characters',
  'register.validatePasswordMatch': 'Passwords do not match',

  'editor.title': 'Editor',
  'editor.showRaw': 'Show raw',
  'editor.showFormatted': 'Show formatted',
  'editor.emptyHint': 'Upload a CSV file to start',
  'editor.emptyDesc': 'Paper content will be streamed here',
  'editor.paused': 'Paused:',
  'editor.degradationTitle': '⚠ Degradation details',
  'editor.confirmContinue': 'Confirm & Continue',
  'editor.editTitle': 'Edit Title',
  'editor.continueHint': 'Title has been generated. Please confirm to continue.',

  'eda.title': 'EDA',
  'eda.loading': 'Loading...',
  'eda.corrMatrix': 'Correlation matrix:',
  'eda.charlsDetected': 'CHARLS Dataset',
  'eda.variableWizard': 'Variable Wizard',

  'agent.title': 'Agent',
  'agent.connection': 'Connection',
  'agent.currentNode': 'Current Node',
  'agent.status': 'Status',
  'agent.degraded': '⚠ Degraded',

  'outline.addChapter': '+ Add Chapter',
  'outline.confirm': 'Confirm Outline',
  'outline.newChapter': 'New Chapter',

  'error.panelError': 'Panel render error',
  'error.retry': 'Retry',

  'clean.profiling': 'Data Profiling',
  'clean.rows': 'Rows',
  'clean.cols': 'Columns',
  'clean.variable': 'Variable',
  'clean.type': 'Type',
  'clean.missingRate': 'Missing Rate',
  'clean.unique': 'Unique',
  'clean.isNumeric': 'Numeric',
  'clean.strategy': 'Missing Value Strategy',
  'clean.outlier': 'Outlier Winsorization Comparison',
  'clean.before': 'Before max',
  'clean.after': 'After max',

  'direction.question': 'Research Question',
  'direction.dv': 'Dependent Variable',
  'direction.iv': 'Independent Variable',
  'direction.controls': 'Controls (comma separated)',
  'direction.method': 'Method',
  'direction.template': 'Template',
  'direction.submit': 'Submit',
  'direction.selectMethod': 'Select method…',

  'balance.title': 'Panel Balance Check',
  'balance.panelId': 'Panel ID column',
  'balance.panelIdPlaceholder': 'e.g. id',
  'balance.timeCol': 'Time column',
  'balance.timeColPlaceholder': 'e.g. year',
  'balance.check': 'Check Balance',
  'balance.checking': 'Checking...',
  'balance.metric': 'Metric',
  'balance.value': 'Value',
  'balance.balanced': 'Balanced units',
  'balance.unbalanced': 'Unbalanced units',
  'balance.periods': 'Periods',
  'balance.attrition': 'Attrition rate',

  'chapter.streaming': 'Generating… (streaming)',
  'chapter.regenerate': 'Regenerate',
  'chapter.rollback': 'Rollback',
  'chapter.save': 'Save',
  'chapter.edit': 'Edit',
  'chapter.approve': 'Approve',

  'charls.title': 'CHARLS Dataset Detected',
  'charls.cancel': 'Cancel',
  'charls.mapping': 'Variable Mapping (editable)',
  'charls.originalVar': 'Original Variable',
  'charls.readableVar': 'Readable Name',
  'charls.waves': 'Survey Waves',
  'charls.presets': 'Filter Presets',
  'charls.confirm': 'Confirm',

  'codeExport.title': 'Download Code',
  'codeExport.desc': 'Select a code format to download. Each format contains the same analysis logic adapted to the corresponding statistical software syntax.',
  'codeExport.close': 'Close',

  'docExport.title': 'Export Document',
  'docExport.selectTemplate': 'Select Template',
  'docExport.exportFormat': 'Export Format',
  'docExport.session': 'Session',

  'latex.title': 'LaTeX Source',
  'latex.refresh': 'Refresh Preview',
  'latex.degraded': 'PDF preview unavailable: latexmk is not installed. Only .tex source export is supported.',

  'review.title': 'Chapter Review',
  'review.autoPass': 'Auto Pass',
  'review.autoFail': 'Auto Fail',
  'review.rubric': 'Review Rubric (5 dimensions)',
  'review.feedback': 'Review Feedback',
  'review.suggestions': 'Suggestions',
  'review.noFeedback': 'No feedback yet',
  'review.noSuggestions': 'No suggestions yet',
  'review.accept': 'Accept',
  'review.acceptRegen': 'Accept & Regenerate',
  'review.reject': 'Reject & Regenerate',
  'review.forcePass': 'Force Pass',
  'review.submitError': 'Decision submission failed: ',

  'filter.title': 'Sample Filter',
  'filter.col': 'Column',
  'filter.colPlaceholder': 'e.g. age',
  'filter.op': 'Operator',
  'filter.value': 'Value',
  'filter.valuePlaceholder': 'e.g. 50',
  'filter.addCondition': 'Add Condition',
  'filter.conditions': 'Conditions (AND)',
  'filter.apply': 'Apply Filter',
  'filter.applying': 'Applying...',
  'filter.nBefore': 'Before filter',
  'filter.nAfter': 'After filter',

  'vc.title': 'Variable Constructor',
  'vc.type': 'Construction Type',
  'vc.col': 'Column',
  'vc.colPlaceholder': 'e.g. income',
  'vc.constructing': 'Constructing...',
  'vc.construct': 'Construct Variable',
  'vc.constructed': 'Constructed Variables',

  'version.empty': 'No versions yet',
  'version.label': 'Version',
  'version.current': ' (current)',

  'progress.completed': 'Completed',

  'method.select': 'Select method…',

  'step.uploadData': 'Upload Data',
  'step.exploreData': 'Explore Data',
  'step.generatePaper': 'Generate Paper',

  'review.rubricEndogeneity': 'Endogeneity',
  'review.rubricIdentification': 'Identification',
  'review.rubricRobustness': 'Robustness',
  'review.rubricContribution': 'Contribution',
  'review.rubricReadability': 'Readability',
  'review.roundLabel': 'Round {0}/{1}',
  'review.scoreLabel': 'Score {0}',
  'review.forcePassDisabled': 'Auto review passed, force pass is not needed',
}

// ── Context ──

interface I18nContextValue {
  lang: Lang
  setLang: (lang: Lang) => void
  t: (key: string) => string
}

const I18nContext = createContext<I18nContextValue | null>(null)

export { I18nContext }

function getInitialLang(): Lang {
  try {
    const stored = localStorage.getItem(LS_LANG_KEY)
    if (stored === 'zh' || stored === 'en') return stored
  } catch {
    // localStorage unavailable
  }
  return 'zh'
}

const dict: Record<Lang, Record<string, string>> = { zh, en }

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(getInitialLang)

  const setLang = (next: Lang) => {
    setLangState(next)
    try {
      localStorage.setItem(LS_LANG_KEY, next)
    } catch {
      // localStorage unavailable
    }
  }

  const t = (key: string): string => dict[lang][key] ?? key

  return (
    <I18nContext.Provider value={{ lang, setLang, t }}>
      {children}
    </I18nContext.Provider>
  )
}

export function useT() {
  const ctx = useContext(I18nContext)
  if (!ctx) throw new Error('useT must be used within I18nProvider')
  return ctx
}