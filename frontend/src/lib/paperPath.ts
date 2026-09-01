export type PathStatus = 'pending' | 'active' | 'completed' | 'paused'

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

export interface PaperPathState {
  uploading: boolean
  hasSession: boolean
  hasDirection: boolean
  directionOpen: boolean
  hasReadout: boolean
  hasOutline: boolean
  writing: boolean
  hasChapter: boolean
  awaitingApprove: boolean
  canExport: boolean
  /** 用户点过导出且成功。与 canExport 解耦：此前两站同源于 canExport，永远同步跳变。 */
  hasExported?: boolean
  cleaningSteps?: CleanStepReport[]
}

const CLEAN_SET = new Set<string>(CLEAN_STEPS)

function toCleanId(name: string): CleanStepId | null {
  if (CLEAN_SET.has(name)) return name as CleanStepId
  const stripped = name.replace(/Step$/, '').toLowerCase()
  if (CLEAN_SET.has(stripped)) return stripped as CleanStepId
  return null
}

function reportStatus(status: string | undefined): PathStatus | null {
  if (status === 'paused' || status === 'failed') return 'paused'
  if (status === 'success' || status === 'skipped' || status === 'ok') return 'completed'
  if (status === 'running') return 'active'
  return null
}

function emptyClean(): Record<CleanStepId, PathStatus> {
  return {
    profiling: 'pending',
    merge: 'pending',
    missing: 'pending',
    outliers: 'pending',
    transform: 'pending',
    filter: 'pending',
    balance: 'pending',
    audit: 'pending',
  }
}

export function derivePaperPath(state: PaperPathState): {
  nodes: Record<PaperNodeId, PathStatus>
  clean: Record<CleanStepId, PathStatus>
} {
  const upload: PathStatus = state.hasSession ? 'completed' : state.uploading ? 'active' : 'pending'
  const direction: PathStatus = state.hasDirection
    ? 'completed'
    : state.hasSession
      ? state.directionOpen
        ? 'paused'
        : 'active'
      : 'pending'
  const spec: PathStatus = state.hasReadout ? 'completed' : state.hasDirection ? 'active' : 'pending'
  const outline: PathStatus = state.hasOutline ? 'completed' : state.hasReadout ? 'active' : 'pending'
  let chapter: PathStatus = 'pending'
  if (state.hasOutline) {
    if (state.awaitingApprove) chapter = 'paused'
    else if (state.writing) chapter = 'active'
    else if (state.hasChapter) chapter = 'completed'
    else chapter = 'paused'
  }
  // translate_code（生成 Stata/R 复现代码）是导出动作的一部分，后端在 doc-export
  // 请求内生成——导出前它并不在进行中。旧逻辑挂在 canExport 上，导致
  // 「翻译代码」在写完章节后就永远显示进行中（谎报）。
  const translate: PathStatus = state.hasExported ? 'completed' : 'pending'
  const exportDoc: PathStatus = state.hasExported
    ? 'completed'
    : state.canExport
      ? 'active'
      : 'pending'

  const clean = emptyClean()
  let cleanData: PathStatus = 'pending'

  if (state.cleaningSteps?.length) {
    for (const step of state.cleaningSteps) {
      const id = toCleanId(step.name)
      if (!id) continue
      const mapped = reportStatus(step.status)
      if (mapped) clean[id] = mapped
    }
    const paused = CLEAN_STEPS.some((id) => clean[id] === 'paused')
    const active = CLEAN_STEPS.some((id) => clean[id] === 'active')
    const allDone = CLEAN_STEPS.every((id) => clean[id] === 'completed')
    if (paused) cleanData = 'paused'
    else if (allDone) cleanData = 'completed'
    else cleanData = 'active'
    if (!paused && !active && !allDone) {
      const next = CLEAN_STEPS.find((id) => clean[id] === 'pending')
      if (next) clean[next] = 'active'
    }
  } else if (state.uploading) {
    clean.profiling = 'active'
    cleanData = 'active'
  }

  return {
    nodes: {
      upload_data: upload,
      clean_data: cleanData,
      set_direction: direction,
      spec_curve: spec,
      generate_outline: outline,
      generate_chapter: chapter,
      translate_code: translate,
      export_docx: exportDoc,
    },
    clean,
  }
}
