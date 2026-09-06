// 论文路径与清洗步骤的稳定标识。WorkspacePreview（Guide 里的示意）
// 与工作台测试用它们做 step 对齐；状态推导归 Overview stepper 与
// StepTimeline，各自从 snapshot 投影取值。
export const PAPER_NODES = [
  'upload_data',
  'clean_data',
  'set_direction',
  'spec_curve',
  'generate_outline',
  'generate_chapter',
  'translate_code',
  'export_docx',
] as const

export type PaperNodeId = (typeof PAPER_NODES)[number]

export const CLEAN_STEPS = [
  'profiling',
  'merge',
  'missing',
  'outliers',
  'transform',
  'filter',
  'balance',
  'audit',
] as const

export type CleanStepId = (typeof CLEAN_STEPS)[number]

export type CleanStepReport = { name: string; status?: string }
