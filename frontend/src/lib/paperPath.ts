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
  const translate: PathStatus = state.canExport ? 'active' : 'pending'
  const exportDoc: PathStatus = state.canExport ? 'active' : 'pending'

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
  } else if (state.hasSession) {
    for (const id of CLEAN_STEPS) clean[id] = 'completed'
    cleanData = 'completed'
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
