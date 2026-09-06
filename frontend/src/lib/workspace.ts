// ── Workspace state & actions ──────────────────────────────────────
// Everything the workspace touch panel needs: local state, persistence,
// API orchestration, and recovery across page or process interruption.
//
// Truth owner (ADR-0013): the backend Project Snapshot (GET /sessions/{id})
// and the durable run queue. The browser keeps only
// - identity: the session id handle (session.ts), and
// - short-term command delivery keys (R2): a pending direction command and
//   a pending upload intent, each carrying its idempotency key so a lost
//   response can be replayed safely.
// Dataset metadata, run lifecycle, estimate, chapters and outline are never
// mirrored into web storage; refresh recovery re-reads the snapshot and
// reattaches to snapshot.active_run via /runs/{id}/events.

import { useState, useEffect, useRef, useCallback } from 'react'
import type { OutlineChapter } from '../components/Outline'
import type { DirectionFormData, DirectionFormInitial } from '../components/DirectionForm'
import type { PausePayload } from '../components/WriteLoop'
import { API_BASE, apiFetch } from './apiBase'
import {
  RunRequestError,
  RunTerminalError,
  waitForRun,
} from './runEvents'
import type { components } from '../types/api'
import {
  clearStoredSessionId,
  persistSessionId,
  readStoredSessionId,
} from './session'

// localStorage / sessionStorage keys owned by the workspace.
// Research truth keys (csv meta, data columns, active-run handles) were
// removed: the Project Snapshot is the only source for those (C1/C3).
export const LS_GUIDE_KEY = 'econpaper_seen_guide'
export const LS_SAMPLE_KEY = 'econpaper_sample_direction'
export const LS_PENDING_RUN_KEY = 'econpaper_pending_run_command'
export const LS_PENDING_UPLOAD_KEY = 'econpaper_pending_upload'

export const SAMPLE_CSV = '/samples/course-panel.csv'
export const CARD_DEMO_FILENAME = 'card_1995.csv'
export const SAMPLE_DIRECTION = {
  question: '这份课设样例里，年龄和收入是否相关？',
  dv: 'income',
  iv: 'age',
  controls: 'treat',
  method: 'OLS',
  template: 'undergrad',
}

type ReviewInfo = components['schemas']['ReviewInfoResponse']
type WrittenChapter = components['schemas']['ChapterResponse']
type RunAccepted = components['schemas']['RunAcceptedResponse']
type DirectionAcceptance =
  | RunAccepted
  | { immediate_result: Record<string, any> }

/** 后端唯一研究状态读模型（ADR-0013）：取代旧的自建重复业务模型。 */
export type WorkspaceSnapshot = components['schemas']['SessionInfoResponse']
export type SnapshotDataset = components['schemas']['SnapshotDatasetResponse']
export type EvidenceModel = components['schemas']['EvidenceResponse']
export type ResearchLab = NonNullable<WorkspaceSnapshot['research']>

type StoredPendingRun = {
  idempotencyKey: string
  direction: DirectionFormData
}

type RunKind = components['schemas']['RunStatusResponse']['kind']
type UploadReadiness = NonNullable<
  components['schemas']['SessionInfoResponse']['upload_readiness']
>

type PendingUploadIntent = {
  idempotencyKey: string
  fileName: string
}

type GeneratedUploadAcceptance = components['schemas']['UploadResponse']
type UploadAcceptance = Pick<
  GeneratedUploadAcceptance,
  'session_id' | 'dataset_meta'
> &
  Partial<
    Pick<GeneratedUploadAcceptance, 'run_id' | 'status' | 'events_url'>
  >

function runStorageKey(prefix: string, sessionId: string): string {
  return `${prefix}:${sessionId}`
}

function writePendingRun(sessionId: string, pending: StoredPendingRun) {
  localStorage.setItem(
    runStorageKey(LS_PENDING_RUN_KEY, sessionId),
    JSON.stringify(pending),
  )
}

function clearPendingRun(sessionId: string, idempotencyKey?: string) {
  const pending = readPendingRun(sessionId)
  if (!pending) return
  if (idempotencyKey && pending.idempotencyKey !== idempotencyKey) return
  localStorage.removeItem(runStorageKey(LS_PENDING_RUN_KEY, sessionId))
}

function readPendingRun(sessionId: string): StoredPendingRun | null {
  try {
    const raw = localStorage.getItem(runStorageKey(LS_PENDING_RUN_KEY, sessionId))
    if (!raw) return null
    const pending = JSON.parse(raw) as StoredPendingRun
    return pending.idempotencyKey && pending.direction ? pending : null
  } catch {
    return null
  }
}

function clearAllCommandStorage() {
  for (const key of Object.keys(localStorage)) {
    if (
      key === LS_PENDING_RUN_KEY ||
      key === LS_PENDING_UPLOAD_KEY ||
      key.startsWith(`${LS_PENDING_RUN_KEY}:`)
    ) {
      localStorage.removeItem(key)
    }
  }
}

export function beginUploadIntent(fileName: string): PendingUploadIntent {
  const intent = { idempotencyKey: crypto.randomUUID(), fileName }
  localStorage.setItem(LS_PENDING_UPLOAD_KEY, JSON.stringify(intent))
  return intent
}

function readPendingUploadIntent(): PendingUploadIntent | null {
  try {
    const raw = localStorage.getItem(LS_PENDING_UPLOAD_KEY)
    if (!raw) return null
    const intent = JSON.parse(raw) as Partial<PendingUploadIntent>
    return intent.idempotencyKey && intent.fileName
      ? { idempotencyKey: intent.idempotencyKey, fileName: intent.fileName }
      : null
  } catch {
    return null
  }
}

function clearPendingUpload(idempotencyKey?: string) {
  const pending = readPendingUploadIntent()
  if (idempotencyKey && pending?.idempotencyKey !== idempotencyKey) return
  localStorage.removeItem(LS_PENDING_UPLOAD_KEY)
}

async function uploadResponse(response: Response): Promise<UploadAcceptance> {
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) throw new RunRequestError(response.status)
  return payload as UploadAcceptance
}

export async function acceptCardDemoRun(
  idempotencyKey: string,
): Promise<UploadAcceptance> {
  const response = await apiFetch(`${API_BASE}/demos/card`, {
    method: 'POST',
    headers: { 'Idempotency-Key': idempotencyKey, ...authHeaders() },
  })
  return uploadResponse(response)
}

export async function acceptUploadRun(
  file: File,
  idempotencyKey: string,
): Promise<UploadAcceptance> {
  let lastError: unknown
  for (let attempt = 0; attempt < 2; attempt += 1) {
    const formData = new FormData()
    formData.append('file', file)
    try {
      const response = await apiFetch(`${API_BASE}/upload`, {
        method: 'POST',
        headers: { 'Idempotency-Key': idempotencyKey, ...authHeaders() },
        body: formData,
      })
      if (!response.ok && response.status < 500) throw new RunRequestError(response.status)
      return await uploadResponse(response)
    } catch (error) {
      if (error instanceof RunRequestError && error.status < 500) throw error
      lastError = error
    }
  }
  throw lastError
}

export async function resolvePendingUpload(): Promise<UploadAcceptance | null> {
  const pending = readPendingUploadIntent()
  if (!pending) return null
  const response = await apiFetch(`${API_BASE}/upload/resolve`, {
    method: 'POST',
    headers: { 'Idempotency-Key': pending.idempotencyKey, ...authHeaders() },
  })
  return uploadResponse(response)
}

export async function fetchSessionSnapshot(
  sessionId: string,
): Promise<WorkspaceSnapshot> {
  const response = await apiFetch(`${API_BASE}/sessions/${sessionId}`, {
    headers: authHeaders(),
  })
  if (!response.ok) throw new RunRequestError(response.status)
  return response.json()
}

export async function fetchSessionEvidence(
  sessionId: string,
): Promise<EvidenceModel> {
  const response = await apiFetch(`${API_BASE}/sessions/${sessionId}/evidence`, {
    headers: authHeaders(),
  })
  if (!response.ok) throw new Error(`HTTP ${response.status}`)
  return response.json()
}

export function eventsUrlFor(runId: string): string {
  return `${API_BASE}/runs/${runId}/events`
}

export function directionGateForReadiness(readiness: UploadReadiness | undefined): {
  disabled: boolean
  reason: UploadReadiness | null
} {
  if (!readiness || readiness === 'READY') return { disabled: false, reason: null }
  return { disabled: true, reason: readiness }
}

export async function acceptDirectionRun(
  sessionId: string,
  direction: DirectionFormData,
  idempotencyKey: string,
): Promise<DirectionAcceptance> {
  const response = await apiFetch(`${API_BASE}/sessions/${sessionId}/direction`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Idempotency-Key': idempotencyKey,
      ...authHeaders(),
    },
    body: JSON.stringify(direction),
  })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    if (response.status < 500) clearPendingRun(sessionId, idempotencyKey)
    const retryAfter = response.headers.get('Retry-After')
    throw new Error(retryAfter ? `HTTP ${response.status}; retry after ${retryAfter}s` : `HTTP ${response.status}`)
  }
  // Rolling deploy compatibility: an older API may still complete this
  // command synchronously with the former DirectionResponse body.
  if (!payload.run_id) return { immediate_result: payload as Record<string, any> }
  return payload as RunAccepted
}

export type RecoveredCommand =
  | { kind: 'run'; runId: string; runKind: RunKind }
  | { kind: 'result'; result: Record<string, any> }

/**
 * 刷新恢复（C3）：研究状态一律来自后端。
 * - snapshot.active_run 存在 → 重新订阅该 durable run；
 * - 否则存在未投递完成的 direction command → 用原 idempotency key 重放
 *   （R2 豁免：重放必须凭客户端侧 key）。
 * 不读任何 run 句柄 / 数据集副本。
 */
export async function recoverFromSnapshot(
  sessionId: string,
  snapshot: WorkspaceSnapshot,
): Promise<RecoveredCommand | null> {
  if (snapshot.exists === false) return null
  const active = snapshot.active_run
  if (active) {
    return { kind: 'run', runId: active.run_id, runKind: active.kind }
  }
  const pending = readPendingRun(sessionId)
  if (!pending) return null
  const accepted = await acceptDirectionRun(
    sessionId,
    pending.direction,
    pending.idempotencyKey,
  )
  if ('immediate_result' in accepted) {
    clearPendingRun(sessionId, pending.idempotencyKey)
    return { kind: 'result', result: accepted.immediate_result }
  }
  clearPendingRun(sessionId, pending.idempotencyKey)
  return { kind: 'run', runId: accepted.run_id, runKind: 'prewrite' }
}

// authHeaders() survives only so legacy call sites compile; the auth
// rides the httpOnly cookie pair and this returns nothing.
function authHeaders(): Record<string, string> {
  return {}
}

export function directionLine(
  rd: { method?: string; dv?: string; iv?: string } | null | undefined,
): string | null {
  if (!rd) return null
  const method = rd.method?.trim()
  const dv = rd.dv?.trim()
  const iv = rd.iv?.trim()
  if (!method && !dv && !iv) return null
  if (dv && iv) return `${method || 'OLS'} · ${dv} ~ ${iv}`
  return method || null
}

export function asControlList(raw: unknown): string[] | undefined {
  if (Array.isArray(raw)) return raw.filter((item): item is string => typeof item === 'string')
  if (typeof raw === 'string') {
    const parts = raw.split(',').map((item) => item.trim()).filter(Boolean)
    return parts
  }
  return undefined
}

export function chapterIndexForApply(
  accepted: { type: string }[],
  opts: {
    freshIDecide: boolean
    iDecideLocked: boolean
    currentType?: string
    currentIndex: number
  },
): number {
  if (!accepted.length) return 0
  if (opts.freshIDecide) return 0
  if (opts.iDecideLocked && opts.currentType) {
    const idx = accepted.findIndex((ch) => ch.type === opts.currentType)
    return idx >= 0 ? idx : 0
  }
  return Math.min(Math.max(0, opts.currentIndex), accepted.length - 1)
}

export function createRestoreSnapshotGate() {
  let runApplied = false
  return {
    applySession(apply: () => void) {
      if (!runApplied) apply()
    },
    applyRun(apply: () => void) {
      runApplied = true
      apply()
    },
  }
}

export function toDirectionInitial(
  record: DirectionFormData | null,
): DirectionFormInitial | undefined {
  if (!record) return undefined
  return {
    question: record.question,
    dv: record.dv,
    iv: record.iv,
    controls: Array.isArray(record.controls) ? record.controls.join(', ') : record.controls,
    method: record.method,
    template: record.template,
    instrument: record.instrument,
    time_col: record.time_col,
    id_col: record.id_col,
    first_treat_col: record.first_treat_col,
    running_var: record.running_var,
    cutoff: record.cutoff,
    unit_col: record.unit_col,
    treatment_time: record.treatment_time,
  }
}

export function formatIdentReport(
  nextStar: number | null | undefined,
  report: string,
): string {
  if (nextStar == null) return report
  return `${'★'.repeat(nextStar)}${'☆'.repeat(3 - nextStar)}\n${report}`
}

export interface WorkspaceOptions {
  sessionId: string | null
  setSessionId: (id: string | null) => void
  setAuthed: (v: boolean) => void
  t: (key: string) => string
}

export type WorkspaceApi = ReturnType<typeof useWorkspace>

/** snapshot 里是否已有任何工作台内容（决定投影是否值得应用）。 */
export function snapshotHasDesk(data: WorkspaceSnapshot): boolean {
  return Boolean(
    data.claim ||
      data.estimate ||
      data.literature_source ||
      data.identification_report ||
      data.robustness_status ||
      data.cleaning_report ||
      data.upload_readiness ||
      data.identification_failed ||
      data.star_rating != null ||
      (data.outline && data.outline.length) ||
      (data.body_chapters && data.body_chapters.length) ||
      data.research_direction ||
      data.dataset ||
      data.research,
  )
}

/**
 * snapshot 是否已推进到「研究方向及以上」——刷新恢复时据此把工作台
 * 直接落在 Overview。仅有数据集（刚上传、还没提交方向）不算：
 * 此时用户应该停在研究问题表单，而不是被甩到仪表盘。
 */
export function researchQuestionPrompt(
  research: ResearchLab | null | undefined,
): string | null {
  const q = research?.question
  if (!q || typeof q !== 'object') return null
  const en = typeof q.prompt_en === 'string' ? q.prompt_en.trim() : ''
  const zh = typeof q.prompt_zh === 'string' ? q.prompt_zh.trim() : ''
  return en || zh || null
}

export function hasConfirmedResearchQuestion(
  research: ResearchLab | null | undefined,
  directionSummary?: string | null,
): boolean {
  return Boolean(
    directionSummary ||
      researchQuestionPrompt(research) ||
      research?.question ||
      research?.teaching_case,
  )
}

export function snapshotHasResearchContent(data: WorkspaceSnapshot): boolean {
  const lab = data.research
  return Boolean(
    data.claim ||
      data.results ||
      data.literature_source ||
      data.robustness_status ||
      data.identification_report ||
      (Array.isArray(data.outline) && data.outline.length) ||
      (Array.isArray(data.body_chapters) && data.body_chapters.length) ||
      data.research_direction ||
      lab?.specification_space?.frozen_at ||
      (Array.isArray(lab?.specification_runs) && lab.specification_runs.length > 0) ||
      lab?.claim,
  )
}

export function useWorkspace(opts: WorkspaceOptions) {
  const { sessionId, setSessionId, setAuthed, t } = opts

  const [edaOpen, setEdaOpen] = useState(false)
  const [outline, setOutline] = useState<OutlineChapter[]>([])

  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [uploadReadiness, setUploadReadiness] = useState<UploadReadiness | undefined>()
  const [uploadNeedsReselect, setUploadNeedsReselect] = useState(false)
  const [uploadStatus, setUploadStatus] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [deskOpen, setDeskOpen] = useState(
    () => !readStoredSessionId(),
  )
  // 空桌直入：落地页不再拦截首次访问。showGuide 只由显式请求
  // （页眉「了解产品」/「再看一次产品页」）置位；LS_GUIDE_KEY 退化为
  // 「看过」记录，与进门与否无关。
  const [showGuide, setShowGuide] = useState(false)
  const [shapedQuestion, setShapedQuestion] = useState(() => {
    try {
      const raw = sessionStorage.getItem(LS_SAMPLE_KEY)
      if (!raw) return ''
      const parsed = JSON.parse(raw) as { question?: string }
      return parsed.question || ''
    } catch {
      return ''
    }
  })
  const [sampleDirection, setSampleDirection] =
    useState<typeof SAMPLE_DIRECTION | null>(() => {
      try {
        const raw = sessionStorage.getItem(LS_SAMPLE_KEY)
        return raw ? (JSON.parse(raw) as typeof SAMPLE_DIRECTION) : null
      } catch {
        return null
      }
    })
  // 数据集元信息：唯一来源是后端 snapshot（C1），不再有 sessionStorage 副本。
  const [dataset, setDataset] = useState<SnapshotDataset | null>(null)
  const [directionRecord, setDirectionRecord] = useState<DirectionFormData | null>(null)

  const [globalError, setGlobalError] = useState<string | null>(null)
  const globalErrorTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const [degradations, setDegradations] = useState<
    Array<{ node: string; reason: string; fallback: string; timestamp: string }>
  >([])
  const [degraded, setDegraded] = useState(false)
  const degradationsPollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const [review, setReview] = useState<ReviewInfo | null>(null)
  // 审批硬证据门：409 后弹出的未过审信息（分数 + 阈值 + 章节引用）
  const [gateInfo, setGateInfo] = useState<{
    chapter: components['schemas']['ChapterResponse']
    score: number | null
    threshold: number
  } | null>(null)
  const [gateBusy, setGateBusy] = useState(false)
  const [docExportOpen, setDocExportOpen] = useState(false)
  // 导出成功后置 true：paperPath 的 export_docx / translate_code 依赖它区分
  // 「可导出但未导出」与「已导出」。此前两站同源于 canExport，永远同步跳变。
  const [hasExported, setHasExported] = useState(false)
  const [codeExportOpen, setCodeExportOpen] = useState(false)
  const [workbenchTab, setWorkbenchTab] = useState<
    'overview' | 'paper' | 'data' | 'question' | 'design' | 'evidence' | 'literature'
  >('question')
  const [directionBusy, setDirectionBusy] = useState(false)
  const [runFailure, setRunFailure] = useState<string | null>(null)
  const activeSessionRef = useRef(sessionId)
  const sessionEpochRef = useRef(0)
  const runAbortRef = useRef<AbortController | null>(null)
  const uploadRecoveryEpochRef = useRef(0)
  const directionOperationRef = useRef<symbol | null>(null)
  const uploadOperationRef = useRef<string | null>(readPendingUploadIntent()?.idempotencyKey ?? null)
  const [directionOpen, setDirectionOpen] = useState(true)
  const [directionSummary, setDirectionSummary] = useState<string | null>(null)
  const [claim, setClaim] = useState<string | null>(null)
  const [starRating, setStarRating] = useState<number | null>(null)
  const [treatmentRow, setTreatmentRow] = useState<string | null>(null)
  const [estimateMeta, setEstimateMeta] = useState<Record<string, any> | null>(null)
  const [cleaningReport, setCleaningReport] = useState<Record<string, any> | null>(null)
  const [mainResults, setMainResults] = useState<string | null>(null)
  const [literatureSource, setLiteratureSource] = useState<string | null>(null)
  const [robustnessStatus, setRobustnessStatus] = useState<string | null>(null)
  const [writeBlockers, setWriteBlockers] = useState<string[]>([])
  const [identFailed, setIdentFailed] = useState(false)
  const [identReport, setIdentReport] = useState<string | null>(null)
  const [writingType, setWritingType] = useState<string | null>(null)
  const [writeBusy, setWriteBusy] = useState(false)
  const writeBusyRef = useRef(false)
  const [writtenChapters, setWrittenChapters] = useState<WrittenChapter[]>([])
  const [currentChapterIndex, setCurrentChapterIndex] = useState(0)
  const [outlineLocked, setOutlineLocked] = useState(false)
  // Evidence 读模型的刷新信号：run 结束后 +1，Evidence 视图据此重取。
  const [evidenceRefreshKey, setEvidenceRefreshKey] = useState(0)
  // snapshot.active_run 投影：Overview「上次运行」卡与 Agent 栏当前任务共用。
  const [activeRun, setActiveRun] = useState<WorkspaceSnapshot['active_run']>(null)
  const [research, setResearch] = useState<ResearchLab | null>(null)

  const showGlobalError = useCallback((message: string) => {
    setGlobalError(message)
    if (globalErrorTimerRef.current) clearTimeout(globalErrorTimerRef.current)
    globalErrorTimerRef.current = setTimeout(() => setGlobalError(null), 8000)
  }, [])

  const invalidateSessionWork = useCallback(() => {
    sessionEpochRef.current += 1
    runAbortRef.current?.abort()
    runAbortRef.current = null
    directionOperationRef.current = null
    setDirectionBusy(false)
    setUploading(false)
    setActiveRun(null)
    setResearch(null)
  }, [])

  const switchSession = useCallback(
    (nextSessionId: string | null) => {
      if (activeSessionRef.current !== nextSessionId) {
        invalidateSessionWork()
        activeSessionRef.current = nextSessionId
        setUploadReadiness(undefined)
        setUploadNeedsReselect(false)
      }
      setSessionId(nextSessionId)
    },
    [invalidateSessionWork, setSessionId],
  )

  useEffect(() => {
    if (activeSessionRef.current !== sessionId) {
      invalidateSessionWork()
      activeSessionRef.current = sessionId
    }
  }, [invalidateSessionWork, sessionId])

  const handleLogout = useCallback(() => {
    // Server revokes the refresh token and clears both cookies.
    void (async () => {
      try {
        await fetch(`${API_BASE}/auth/logout`, { method: 'POST', credentials: 'include' })
      } catch {
        /* local logout proceeds regardless */
      }
    })()
    invalidateSessionWork()
    uploadOperationRef.current = null
    setAuthed(false)
    switchSession(null)
    clearStoredSessionId()
    localStorage.removeItem(LS_GUIDE_KEY)
    clearAllCommandStorage()
    setShowGuide(false)
    setDeskOpen(true)
  }, [invalidateSessionWork, setAuthed, switchSession])

  const ensureSession = useCallback(async (): Promise<string> => {
    if (activeSessionRef.current) return activeSessionRef.current
    const resp = await apiFetch(`${API_BASE}/sessions`, {
      method: 'POST',
      headers: authHeaders(),
    })
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    const data = await resp.json()
    return data.session_id as string
  }, [])

  const refreshReview = useCallback(
    async (sid: string) => {
      try {
        const resp = await apiFetch(`${API_BASE}/sessions/${sid}/review`, {
          headers: authHeaders(),
        })
        if (!resp.ok) return
        const data = await resp.json()
        if (data && (data.feedback || data.score > 0)) setReview(data)
      } catch {
        // empty review is fine
      }
    },
    [],
  )

  const applySnapshot = useCallback((data: WorkspaceSnapshot) => {
    if (data.exists === false) return
    if (!snapshotHasDesk(data)) return
    setActiveRun(data.active_run ?? null)
    setClaim(data.claim ?? null)
    setStarRating(data.star_rating ?? null)
    setMainResults(typeof data.results === 'string' ? data.results : null)
    const row = (data.estimate as Record<string, any> | null)?.treatment_row
    setTreatmentRow(typeof row === 'string' && row ? row : null)
    setEstimateMeta((data.estimate as Record<string, any> | null) ?? null)
    setCleaningReport((data.cleaning_report as Record<string, any> | null) ?? null)
    if (Object.prototype.hasOwnProperty.call(data, 'upload_readiness')) {
      setUploadReadiness(data.upload_readiness ?? undefined)
      setUploadNeedsReselect(
        data.upload_readiness === 'FAILED' || data.upload_readiness === 'CANCELLED',
      )
    }
    if (data.dataset) setDataset(data.dataset)
    setResearch(data.research ?? null)
    setLiteratureSource(data.literature_source ?? null)
    setWriteBlockers(Array.isArray(data.write_blockers) ? data.write_blockers : [])
    setIdentFailed(Boolean(data.identification_failed))
    setRobustnessStatus(data.robustness_status ?? null)
    if (data.identification_report) setIdentReport(data.identification_report)
    if (Array.isArray(data.outline) && data.outline.length) {
      setOutline(data.outline)
    }
    if (Array.isArray(data.body_chapters) && data.body_chapters.length) {
      setWrittenChapters(data.body_chapters)
      const lastWithText = [...data.body_chapters].reverse().find((ch) => ch.content)
      if (lastWithText) {
        const idx = data.outline?.findIndex((item) => item.type === lastWithText.type) ?? -1
        if (idx >= 0) setCurrentChapterIndex(idx)
      }
      if (data.body_chapters.some((ch) => ch.content)) setOutlineLocked(true)
    }
    const researchDirection = (data.research_direction ?? null) as Record<string, any> | null
    const summary = directionLine(researchDirection)
    if (summary) {
      setDirectionSummary(summary)
      setDirectionOpen(false)
    } else if (data.research?.teaching_case) {
      setDirectionOpen(false)
    }
    const asked = researchDirection?.question?.trim()
    const prompt = researchQuestionPrompt(data.research)
    if (asked) setShapedQuestion(asked)
    else if (prompt) setShapedQuestion(prompt)
    if (researchDirection) {
      const rd = researchDirection
      const controls = asControlList(rd.controls)
      setDirectionRecord((prev) => ({
        question: asked || prev?.question || '',
        dv: rd.dv || prev?.dv || '',
        iv: rd.iv || prev?.iv || '',
        controls: controls ?? prev?.controls ?? [],
        method: rd.method || prev?.method || '',
        template: rd.template || prev?.template || 'undergrad',
        instrument: rd.instrument || prev?.instrument,
        time_col: rd.time_col || prev?.time_col,
        id_col: rd.id_col || prev?.id_col,
        first_treat_col: rd.first_treat_col || prev?.first_treat_col,
        running_var: rd.running_var || prev?.running_var,
        cutoff: rd.cutoff ?? prev?.cutoff,
        unit_col: rd.unit_col || prev?.unit_col,
        treatment_time: rd.treatment_time || prev?.treatment_time,
      }))
    }
  }, [])

  const returnToUploadDesk = useCallback(
    (message: string, clearAuth = false) => {
      uploadOperationRef.current = null
      clearAllCommandStorage()
      clearStoredSessionId()
      switchSession(null)
      setShowGuide(false)
      setDeskOpen(true)
      setUploadError(message)
      setUploadStatus(message)
      if (clearAuth) setAuthed(false)
    },
    [setAuthed, switchSession],
  )

  const handleUploadRunError = useCallback(
    (error: unknown, _sid: string | null, _runId: string | null) => {
      if (error instanceof DOMException && error.name === 'AbortError') return
      setUploading(false)
      if (error instanceof RunRequestError && (error.status === 401 || error.status === 403)) {
        returnToUploadDesk(
          error.status === 401 ? t('app.uploadAuthRequired') : t('app.uploadPermissionRequired'),
          error.status === 401,
        )
        return
      }
      if (error instanceof RunRequestError && error.status === 404) {
        returnToUploadDesk(t('app.uploadMissing'))
        return
      }
      if (error instanceof RunRequestError && error.status < 500) {
        clearPendingUpload()
        uploadOperationRef.current = null
        setUploadNeedsReselect(true)
        setUploadError(t('app.uploadFailedReselect'))
        setUploadStatus(t('app.uploadFailedReselect'))
        return
      }
      if (error instanceof RunTerminalError) {
        clearPendingUpload()
        uploadOperationRef.current = null
        setUploadReadiness(error.status)
        setUploadNeedsReselect(true)
        const message =
          error.status === 'CANCELLED' ? t('app.uploadCancelled') : t('app.uploadFailedReselect')
        setUploadError(message)
        setUploadStatus(message)
        return
      }
      setUploadError(t('app.uploadRetryRefresh'))
      setUploadStatus(t('app.uploadRetryRefresh'))
    },
    [returnToUploadDesk, t],
  )

  // 会话回填：刷新后从后端 Project Snapshot 恢复工作区（C3）。
  // 研究状态与进行中的 run 全部来自 snapshot；active_run 存在则重新订阅。
  useEffect(() => {
    const saved = readStoredSessionId()
    if (!saved) return
    const restoreEpoch = sessionEpochRef.current
    const snapshotGate = createRestoreSnapshotGate()
    let cancelled = false
    let restoreController: AbortController | null = null
    const isCurrent = () =>
      !cancelled &&
      sessionEpochRef.current === restoreEpoch &&
      activeSessionRef.current === saved
    const attach = (command: RecoveredCommand, sid: string) => {
      const isUpload = command.kind === 'run' && command.runKind === 'upload_pipeline'
      if (isUpload) {
        setUploading(true)
        setUploadStatus(t('app.uploadRecovering'))
      } else if (command.kind === 'run') {
        setDirectionBusy(true)
      }
      const controller = new AbortController()
      restoreController = controller
      runAbortRef.current?.abort()
      runAbortRef.current = controller
      const waitFor = command.kind === 'run'
        ? waitForRun(command.runId, eventsUrlFor(command.runId), controller.signal)
        : Promise.resolve(command.result)
      void waitFor
        .then((result) => {
          if (!isCurrent()) return
          if (isUpload) {
            clearPendingUpload()
            uploadOperationRef.current = null
            setUploadReadiness('READY')
            setUploadStatus(t('app.uploadReady'))
          }
          snapshotGate.applyRun(() => applySnapshot(result as WorkspaceSnapshot))
        })
        // The durable terminal state is the snapshot; re-read it once the
        // run finishes so every field (dataset, blockers, chapters) is
        // restored from the backend rather than the event payload.
        .then(() => (isCurrent() ? fetchSessionSnapshot(sid) : null))
        .then((fresh) => {
          if (fresh && isCurrent()) snapshotGate.applyRun(() => applySnapshot(fresh))
        })
        .catch((error) => {
          if (!isCurrent()) return
          if (isUpload) {
            handleUploadRunError(error, sid, null)
          } else if (!(error instanceof DOMException && error.name === 'AbortError')) {
            setRunFailure(error instanceof Error ? error.message : String(error))
            showGlobalError(error instanceof Error ? error.message : String(error))
          }
        })
        .finally(() => {
          if (runAbortRef.current === controller) runAbortRef.current = null
          if (isCurrent()) {
            if (isUpload) setUploading(false)
            else setDirectionBusy(false)
            setEvidenceRefreshKey((key) => key + 1)
          }
        })
    }
    fetchSessionSnapshot(saved)
      .then((data) => {
        if (!isCurrent()) return
        if (data.exists === false) {
          returnToUploadDesk(t('app.uploadMissing'))
          return
        }
        snapshotGate.applySession(() => applySnapshot(data))
        // 刷新恢复落地（契约 C2）：会话已推进到研究方向及以上时，
        // 工作台直接落在 Overview；空会话/仅数据集仍停在问题卡。
        if (snapshotHasResearchContent(data)) setWorkbenchTab('overview')
        const pendingIntent = readPendingUploadIntent()
        void recoverFromSnapshot(saved, data)
          .then((command) => {
            // 待投递的新上传意图独占 upload run 的处理权（R2）；这里只 attach 其余 run。
            if (
              command &&
              command.kind === 'run' &&
              command.runKind === 'upload_pipeline' &&
              pendingIntent
            ) {
              return
            }
            if (command) attach(command, saved)
          })
          .catch((error) => {
            if (!isCurrent()) return
            setRunFailure(error instanceof Error ? error.message : String(error))
            showGlobalError(error instanceof Error ? error.message : String(error))
          })
      })
      .catch(() => {})
    return () => {
      cancelled = true
      if (restoreController && runAbortRef.current === restoreController) {
        restoreController.abort()
        runAbortRef.current = null
      }
    }
  }, [applySnapshot, handleUploadRunError, returnToUploadDesk, showGlobalError, t])

  useEffect(() => {
    if (sessionId) {
      persistSessionId(sessionId)
      setDeskOpen(false)
    }
  }, [sessionId])

  useEffect(() => {
    if (!sessionId) {
      setDegradations([])
      setDegraded(false)
      return
    }
    const fetchDegradations = async () => {
      try {
        const resp = await apiFetch(`${API_BASE}/sessions/${sessionId}/degradation`)
        if (resp.ok) {
          const data = await resp.json()
          const degs = data.degradations || []
          setDegradations(degs)
          setDegraded(degs.length > 0)
        }
      } catch {}
    }
    fetchDegradations()
    degradationsPollRef.current = setInterval(fetchDegradations, 5000)
    return () => {
      if (degradationsPollRef.current) clearInterval(degradationsPollRef.current)
    }
  }, [sessionId])

  useEffect(() => {
    if (!sessionId) return
    refreshReview(sessionId)
  }, [sessionId, refreshReview])

  // ── 审批硬证据门（review_gate）────────────────────────────────
  // 北极星：未经核对的章节不许静默进入论文。批准按钮 → 后端 409 时
  // 弹 ReviewGateDialog，只有显式 force 才能旁路，且留下永久痕迹。

  const markChapterUpdated = useCallback(
    (chapter: components['schemas']['ChapterResponse']) => {
      setWrittenChapters((prev) => {
        const idx = prev.findIndex((item) => item.type === chapter.type)
        if (idx === -1) return [...prev, chapter]
        const next = [...prev]
        next[idx] = chapter
        return next
      })
    },
    [],
  )

  const postApprove = useCallback(
    async (chapter: components['schemas']['ChapterResponse'], force: boolean) => {
      const resp = await apiFetch(
        `${API_BASE}/sessions/${sessionId}/approve-chapter`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', ...authHeaders() },
          body: JSON.stringify({
            // 精确指定章节类型：后端缺省只批"最后一章"，这里不依赖该假设
            ...(chapter.type ? { chapter_type: chapter.type } : {}),
            ...(force ? { force: true } : {}),
          }),
        },
      )
      const payload = await resp.json().catch(() => ({}))
      return { status: resp.status, payload }
    },
    [sessionId],
  )

  const handleApprove = useCallback(
    async (chapter: components['schemas']['ChapterResponse']) => {
      if (!sessionId) return
      try {
        const { status, payload } = await postApprove(chapter, false)
        if (status === 409) {
          const detail =
            payload.detail && typeof payload.detail === 'object'
              ? payload.detail
              : {}
          if (detail.review_gate) {
            setGateInfo({
              chapter,
              score: typeof detail.score === 'number' ? detail.score : null,
              threshold:
                typeof detail.threshold === 'number' ? detail.threshold : 0.7,
            })
            return
          }
          showGlobalError(payload.detail?.detail || t('bench.writeBlocked'))
          return
        }
        if (status >= 400 || !payload.ok) throw new Error(`HTTP ${status}`)
        markChapterUpdated(payload.chapter)
        await refreshReview(sessionId)
      } catch (err) {
        showGlobalError(err instanceof Error ? err.message : String(err))
      }
    },
    [sessionId, postApprove, markChapterUpdated, refreshReview, showGlobalError, t],
  )

  const handleGateRegenerate = useCallback(async () => {
    if (!gateInfo || !sessionId) return
    const chapterIndex =
      gateInfo.chapter.chapter_index ??
      outline.findIndex((item) => item.type === gateInfo.chapter.type)
    setGateBusy(true)
    try {
      const resp = await apiFetch(
        `${API_BASE}/sessions/${sessionId}/regenerate`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', ...authHeaders() },
          body: JSON.stringify({
            chapter_index: Math.max(0, chapterIndex),
          }),
        },
      )
      const payload = await resp.json().catch(() => ({}))
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      // regenerate 返回整列表；覆盖本地缓存保持一致
      if (Array.isArray(payload.body_chapters)) {
        setWrittenChapters(
          payload.body_chapters.filter(
            (c: components['schemas']['ChapterResponse']) => c.content,
          ),
        )
      }
      setGateInfo(null)
      await refreshReview(sessionId)
    } catch (err) {
      showGlobalError(err instanceof Error ? err.message : String(err))
    } finally {
      setGateBusy(false)
    }
  }, [gateInfo, sessionId, outline, refreshReview, showGlobalError])

  const handleGateForce = useCallback(async () => {
    if (!gateInfo || !sessionId) return
    setGateBusy(true)
    try {
      const { status, payload } = await postApprove(gateInfo.chapter, true)
      if (status >= 400 || !payload.ok) throw new Error(`HTTP ${status}`)
      markChapterUpdated(payload.chapter)
      setGateInfo(null)
      await refreshReview(sessionId)
    } catch (err) {
      showGlobalError(err instanceof Error ? err.message : String(err))
    } finally {
      setGateBusy(false)
    }
  }, [gateInfo, sessionId, postApprove, markChapterUpdated, refreshReview, showGlobalError])

  // 落地页降级为可选入口后的两种操作：显式打开、显式关闭（关闭即记录「看过」）。
  const openGuide = useCallback(() => setShowGuide(true), [])
  const closeGuide = useCallback(() => {
    localStorage.setItem(LS_GUIDE_KEY, '1')
    setShowGuide(false)
  }, [])

  const applyUploadMetadata = useCallback(
    (data: UploadAcceptance, fileName: string) => {
      const meta = data.dataset_meta
      setDataset({
        name: fileName,
        rows: typeof meta?.rows === 'number' ? meta.rows : null,
        columns: Array.isArray(meta?.columns)
          ? meta.columns.filter((item): item is string => typeof item === 'string')
          : [],
      })
      persistSessionId(data.session_id)
      closeGuide()
      switchSession(data.session_id)
    },
    [closeGuide, switchSession],
  )

  useEffect(() => {
    const pending = readPendingUploadIntent()
    if (!pending) return

    uploadOperationRef.current = pending.idempotencyKey
    const recoveryEpoch = ++uploadRecoveryEpochRef.current
    let cancelled = false
    setUploading(true)
    setUploadError(null)
    setUploadStatus(t('app.uploadRecovering'))
    let sid: string | null = null
    let controller: AbortController | null = null
    const isCurrent = () =>
      !cancelled
      && uploadRecoveryEpochRef.current === recoveryEpoch
      && uploadOperationRef.current === pending.idempotencyKey

    void resolvePendingUpload()
      .then(async (accepted) => {
        if (!accepted || !isCurrent()) return null
        sid = accepted.session_id
        applyUploadMetadata(accepted, pending.fileName)
        if (!isCurrent()) return null
        if (!accepted.run_id || !accepted.events_url) {
          clearPendingUpload(pending.idempotencyKey)
          uploadOperationRef.current = null
          setUploadReadiness('READY')
          setUploadStatus(t('app.uploadReady'))
          setUploading(false)
          return null
        }
        setUploadReadiness('PROCESSING')
        controller = new AbortController()
        runAbortRef.current?.abort()
        runAbortRef.current = controller
        return waitForRun(accepted.run_id, accepted.events_url, controller.signal)
      })
      .then(async (result) => {
        if (!result || !sid || !isCurrent()) return
        clearPendingUpload(pending.idempotencyKey)
        uploadOperationRef.current = null
        setUploadReadiness('READY')
        setUploadStatus(t('app.uploadReady'))
        setUploading(false)
        applySnapshot(result as WorkspaceSnapshot)
        const fresh = await fetchSessionSnapshot(sid).catch(() => null)
        if (fresh && isCurrent()) applySnapshot(fresh)
      })
      .catch((error) => {
        if (!isCurrent()) return
        if (error instanceof RunRequestError && error.status === 404 && !sid) {
          clearPendingUpload(pending.idempotencyKey)
          uploadOperationRef.current = null
          setUploadNeedsReselect(true)
          setUploadError(t('app.uploadNotAccepted'))
          setUploadStatus(t('app.uploadNotAccepted'))
          setUploading(false)
          return
        }
        handleUploadRunError(error, sid, null)
      })
      .finally(() => {
        if (runAbortRef.current === controller) runAbortRef.current = null
        if (isCurrent()) setUploading(false)
      })
    return () => {
      cancelled = true
      if (controller && runAbortRef.current === controller) {
        controller.abort()
        runAbortRef.current = null
      }
    }
  }, [applySnapshot, applyUploadMetadata, handleUploadRunError, t])

  const uploadCsv = useCallback(
    async (file: File) => {
      invalidateSessionWork()
      uploadRecoveryEpochRef.current += 1
      const intent = beginUploadIntent(file.name)
      uploadOperationRef.current = intent.idempotencyKey
      setUploading(true)
      setCleaningReport(null)
      setUploadError(null)
      setUploadNeedsReselect(false)
      setUploadStatus(t('app.uploadSubmitting'))
      let sid: string | null = null
      let controller: AbortController | null = null
      const isCurrent = () => uploadOperationRef.current === intent.idempotencyKey
      try {
        const accepted = await acceptUploadRun(file, intent.idempotencyKey)
        if (!isCurrent()) return
        sid = accepted.session_id
        applyUploadMetadata(accepted, file.name)
        if (!isCurrent()) return
        if (!accepted.run_id || !accepted.events_url) {
          clearPendingUpload(intent.idempotencyKey)
          uploadOperationRef.current = null
          setUploadReadiness('READY')
          setUploadStatus(t('app.uploadReady'))
          setUploading(false)
          return
        }
        setUploadReadiness('PROCESSING')
        setUploading(true)
        setUploadStatus(t('app.uploadProcessing'))
        controller = new AbortController()
        runAbortRef.current?.abort()
        runAbortRef.current = controller
        const result = await waitForRun(accepted.run_id, accepted.events_url, controller.signal)
        if (!isCurrent() || activeSessionRef.current !== accepted.session_id) return
        clearPendingUpload(intent.idempotencyKey)
        uploadOperationRef.current = null
        setUploadReadiness('READY')
        setUploadStatus(t('app.uploadReady'))
        setUploading(false)
        applySnapshot(result as WorkspaceSnapshot)
        applySnapshot(await fetchSessionSnapshot(accepted.session_id))
      } catch (err) {
        if (isCurrent()) handleUploadRunError(err, sid, null)
      } finally {
        if (runAbortRef.current === controller) runAbortRef.current = null
        if (isCurrent()) {
          setUploading(false)
          if (fileInputRef.current) fileInputRef.current.value = ''
        }
      }
    },
    [applySnapshot, applyUploadMetadata, handleUploadRunError, invalidateSessionWork, t],
  )

  const takeCsv = useCallback(
    async (file: File) => {
      sessionStorage.removeItem(LS_SAMPLE_KEY)
      setSampleDirection(null)
      await uploadCsv(file)
    },
    [uploadCsv],
  )

  const handleFileSelect = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (!file) return
      await takeCsv(file)
    },
    [takeCsv],
  )

  const handleTrySample = useCallback(async () => {
    setUploading(true)
    setUploadError(null)
    try {
      const res = await fetch(SAMPLE_CSV)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const blob = await res.blob()
      const file = new File([blob], 'course-panel.csv', { type: 'text/csv' })
      setShapedQuestion(SAMPLE_DIRECTION.question)
      setSampleDirection(SAMPLE_DIRECTION)
      sessionStorage.setItem(LS_SAMPLE_KEY, JSON.stringify(SAMPLE_DIRECTION))
      await uploadCsv(file)
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Upload failed')
      setUploading(false)
    }
  }, [uploadCsv])

  const handleTryCard = useCallback(async () => {
    sessionStorage.removeItem(LS_SAMPLE_KEY)
    setSampleDirection(null)
    invalidateSessionWork()
    uploadRecoveryEpochRef.current += 1
    const intent = beginUploadIntent(CARD_DEMO_FILENAME)
    uploadOperationRef.current = intent.idempotencyKey
    setUploading(true)
    setCleaningReport(null)
    setUploadError(null)
    setUploadNeedsReselect(false)
    setUploadStatus(t('app.uploadSubmitting'))
    let sid: string | null = null
    let controller: AbortController | null = null
    const isCurrent = () => uploadOperationRef.current === intent.idempotencyKey
    try {
      const accepted = await acceptCardDemoRun(intent.idempotencyKey)
      if (!isCurrent()) return
      sid = accepted.session_id
      applyUploadMetadata(accepted, CARD_DEMO_FILENAME)
      if (!isCurrent()) return
      const snap = await fetchSessionSnapshot(accepted.session_id).catch(() => null)
      if (snap && isCurrent()) applySnapshot(snap)
      if (!accepted.run_id || !accepted.events_url) {
        clearPendingUpload(intent.idempotencyKey)
        uploadOperationRef.current = null
        setUploadReadiness('READY')
        setUploadStatus(t('app.uploadReady'))
        setUploading(false)
        return
      }
      setUploadReadiness('PROCESSING')
      setUploading(true)
      setUploadStatus(t('app.uploadProcessing'))
      controller = new AbortController()
      runAbortRef.current?.abort()
      runAbortRef.current = controller
      const result = await waitForRun(accepted.run_id, accepted.events_url, controller.signal)
      if (!isCurrent() || activeSessionRef.current !== accepted.session_id) return
      clearPendingUpload(intent.idempotencyKey)
      uploadOperationRef.current = null
      setUploadReadiness('READY')
      setUploadStatus(t('app.uploadReady'))
      setUploading(false)
      applySnapshot(result as WorkspaceSnapshot)
      applySnapshot(await fetchSessionSnapshot(accepted.session_id))
    } catch (err) {
      if (isCurrent()) handleUploadRunError(err, sid, null)
    } finally {
      if (runAbortRef.current === controller) runAbortRef.current = null
      if (isCurrent()) setUploading(false)
    }
  }, [applySnapshot, applyUploadMetadata, handleUploadRunError, invalidateSessionWork, t])

  const handleSaveExpectation = useCallback(
    async (payload: { text: string; confidence: 'low' | 'medium' | 'high'; locale?: string }) => {
      const sid = activeSessionRef.current
      if (!sid) return
      const resp = await apiFetch(`${API_BASE}/sessions/${sid}/research/expectation`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', ...authHeaders() },
        body: JSON.stringify(payload),
      })
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      applySnapshot(await fetchSessionSnapshot(sid))
    },
    [applySnapshot],
  )

  const handleFreezeSpecSpace = useCallback(async () => {
    const sid = activeSessionRef.current
    if (!sid) return
    const resp = await apiFetch(
      `${API_BASE}/sessions/${sid}/research/specification-space/freeze`,
      {
        method: 'POST',
        headers: authHeaders(),
      },
    )
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    applySnapshot(await fetchSessionSnapshot(sid))
  }, [applySnapshot])

  const waitForSpecRun = useCallback(
    async (sid: string, accepted: { run_id: string; events_url: string }) => {
      const controller = new AbortController()
      runAbortRef.current?.abort()
      runAbortRef.current = controller
      setActiveRun({ run_id: accepted.run_id, kind: 'spec_run', status: 'PENDING' })
      try {
        await waitForRun(accepted.run_id, accepted.events_url, controller.signal)
        if (activeSessionRef.current !== sid) return
        applySnapshot(await fetchSessionSnapshot(sid))
        setEvidenceRefreshKey((key) => key + 1)
      } finally {
        if (runAbortRef.current === controller) runAbortRef.current = null
      }
    },
    [applySnapshot],
  )

  const handleRunSpecSpace = useCallback(async () => {
    const sid = activeSessionRef.current
    if (!sid) return
    const resp = await apiFetch(
      `${API_BASE}/sessions/${sid}/research/specification-space/run`,
      {
        method: 'POST',
        headers: { 'Idempotency-Key': crypto.randomUUID(), ...authHeaders() },
      },
    )
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    const accepted = (await resp.json()) as RunAccepted
    await waitForSpecRun(sid, accepted)
  }, [waitForSpecRun])

  const handleRunSpec = useCallback(
    async (specId: string, mode: 'canonical' | 'preview' = 'preview') => {
      const sid = activeSessionRef.current
      if (!sid) return
      const resp = await apiFetch(`${API_BASE}/sessions/${sid}/research/specs/${specId}/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Idempotency-Key': crypto.randomUUID(),
          ...authHeaders(),
        },
        body: JSON.stringify({ mode }),
      })
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      const accepted = (await resp.json()) as RunAccepted
      await waitForSpecRun(sid, accepted)
    },
    [waitForSpecRun],
  )

  const handleCompareSpecs = useCallback(async (a: string, b: string) => {
    const sid = activeSessionRef.current
    if (!sid) return null
    const resp = await apiFetch(`${API_BASE}/sessions/${sid}/research/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify({ a, b }),
    })
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    return resp.json()
  }, [])

  const handlePromotePreview = useCallback(
    async (runId: string) => {
      const sid = activeSessionRef.current
      if (!sid) return
      const resp = await apiFetch(`${API_BASE}/sessions/${sid}/research/preview/promote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeaders() },
        body: JSON.stringify({ run_id: runId }),
      })
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      applySnapshot(await fetchSessionSnapshot(sid))
    },
    [applySnapshot],
  )

  const handleRevertPreview = useCallback(async () => {
    const sid = activeSessionRef.current
    if (!sid) return
    const resp = await apiFetch(`${API_BASE}/sessions/${sid}/research/preview/revert`, {
      method: 'POST',
      headers: authHeaders(),
    })
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    applySnapshot(await fetchSessionSnapshot(sid))
  }, [applySnapshot])

  const handleAcceptChallenge = useCallback(
    async (challengeId: string) => {
      const sid = activeSessionRef.current
      if (!sid) return
      const resp = await apiFetch(
        `${API_BASE}/sessions/${sid}/research/challenges/${challengeId}/accept`,
        {
          method: 'POST',
          headers: { 'Idempotency-Key': crypto.randomUUID(), ...authHeaders() },
        },
      )
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      const accepted = (await resp.json()) as RunAccepted
      await waitForSpecRun(sid, accepted)
    },
    [waitForSpecRun],
  )

  const handleApproveClaim = useCallback(
    async (claimId: string) => {
      const sid = activeSessionRef.current
      if (!sid) return
      const resp = await apiFetch(
        `${API_BASE}/sessions/${sid}/research/claims/${claimId}/approve`,
        {
          method: 'POST',
          headers: authHeaders(),
        },
      )
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      applySnapshot(await fetchSessionSnapshot(sid))
    },
    [applySnapshot],
  )

  const handlePreparePaper = useCallback(async () => {
    const sid = activeSessionRef.current
    if (!sid) return
    const prepared = await apiFetch(`${API_BASE}/sessions/${sid}/research/prepare-paper`, {
      method: 'POST',
      headers: authHeaders(),
    })
    if (!prepared.ok) throw new Error(`HTTP ${prepared.status}`)
    applySnapshot(await fetchSessionSnapshot(sid))
    const written = await apiFetch(`${API_BASE}/sessions/${sid}/generate-chapter`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeaders() },
      body: JSON.stringify({ chapter: { type: 'results', title: '结果' } }),
    })
    if (!written.ok) throw new Error(`HTTP ${written.status}`)
    applySnapshot(await fetchSessionSnapshot(sid))
    setWorkbenchTab('paper')
  }, [applySnapshot])

  const handleDirectionSubmit = useCallback(
    async (data: DirectionFormData) => {
      if (directionGateForReadiness(uploadReadiness).disabled) {
        showGlobalError(t('app.directionUploadNotReady'))
        return
      }
      if (directionOperationRef.current) return
      const operation = Symbol('direction-run')
      directionOperationRef.current = operation
      setDirectionBusy(true)
      setRunFailure(null)
      const startingEpoch = sessionEpochRef.current
      let sid: string | null = null
      let operationEpoch = sessionEpochRef.current
      let controller: AbortController | null = null
      try {
        sid = await ensureSession()
        if (
          directionOperationRef.current !== operation ||
          sessionEpochRef.current !== startingEpoch
        ) return
        if (activeSessionRef.current !== sid) switchSession(sid)
        // Creating the first session invalidates older work, but this exact
        // submission owns that transition and remains the active single flight.
        directionOperationRef.current = operation
        operationEpoch = sessionEpochRef.current
        const idempotencyKey = crypto.randomUUID()
        writePendingRun(sid, { idempotencyKey, direction: data })
        const accepted = await acceptDirectionRun(sid, data, idempotencyKey)
        if ('immediate_result' in accepted) {
          clearPendingRun(sid, idempotencyKey)
          applySnapshot(accepted.immediate_result as WorkspaceSnapshot)
        } else {
          clearPendingRun(sid, idempotencyKey)
          controller = new AbortController()
          runAbortRef.current?.abort()
          runAbortRef.current = controller
          await waitForRun(
            accepted.run_id,
            accepted.events_url,
            controller.signal,
          )
          if (
            sessionEpochRef.current !== operationEpoch ||
            activeSessionRef.current !== sid
          ) return
          // Terminal durable state lives in the snapshot; read it back.
          applySnapshot(await fetchSessionSnapshot(sid))
        }
        if (
          sessionEpochRef.current !== operationEpoch ||
          activeSessionRef.current !== sid
        ) return
        const summary = directionLine(data)
        if (summary) {
          setDirectionSummary(summary)
          setDirectionOpen(false)
        }
        if (data.question.trim()) setShapedQuestion(data.question)
        setDirectionRecord(data)
        setOutlineLocked(false)
        setEvidenceRefreshKey((key) => key + 1)
      } catch (err) {
        if (!(err instanceof DOMException && err.name === 'AbortError')) {
          const message = err instanceof Error ? err.message : String(err)
          setRunFailure(message)
          showGlobalError(err instanceof Error && err.message !== 'HTTP 500' ? message : t('app.directionFailed'))
        }
      } finally {
        if (runAbortRef.current === controller) runAbortRef.current = null
        if (directionOperationRef.current === operation) {
          directionOperationRef.current = null
          setDirectionBusy(false)
        }
      }
    },
    [ensureSession, applySnapshot, showGlobalError, switchSession, t, uploadReadiness],
  )

  const runGenerateChapter = useCallback(
    async (
      chapterType: string,
      title: string,
      renderKwargs?: Record<string, number>,
    ) => {
      if (!sessionId) {
        showGlobalError(t('app.needSession'))
        return
      }
      const resp = await apiFetch(`${API_BASE}/sessions/${sessionId}/generate-chapter`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeaders() },
        body: JSON.stringify({
          chapter: { type: chapterType, title },
          ...(renderKwargs &&
          Object.keys(renderKwargs).length
            ? { render_kwargs: renderKwargs }
            : {}),
        }),
      })
      const payload = await resp.json().catch(() => ({}))
      if (resp.status === 409) {
        const detail =
          payload.detail && typeof payload.detail === 'object' ? payload.detail : payload
        const blockers = Array.isArray(detail.write_blockers) ? detail.write_blockers : []
        setWriteBlockers(blockers)
        showGlobalError(t('bench.writeBlocked'))
        return
      }
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      if (payload.chapter) {
        setWrittenChapters((prev) => {
          const next = prev.filter((ch) => ch.type !== payload.chapter.type)
          return [...next, payload.chapter]
        })
      }
      setWriteBlockers([])
      await refreshReview(sessionId)
    },
    [sessionId, refreshReview, showGlobalError, t],
  )

  const handleWriteChapter = useCallback(
    async (chapterType: string, title: string, renderKwargs?: Record<string, number>) => {
      if (!sessionId) {
        showGlobalError(t('app.needSession'))
        return
      }
      if (writeBusyRef.current) return
      writeBusyRef.current = true
      setWriteBusy(true)
      setWritingType(chapterType)
      try {
        await runGenerateChapter(chapterType, title, renderKwargs)
      } catch (err) {
        showGlobalError(err instanceof Error ? err.message : t('bench.writeBlocked'))
      } finally {
        writeBusyRef.current = false
        setWriteBusy(false)
      }
    },
    [sessionId, runGenerateChapter, showGlobalError, t],
  )

  const handleSelectChapter = useCallback(
    (index: number) => {
      if (writeBusyRef.current) return
      const ch = outline[index]
      if (!ch) return
      setCurrentChapterIndex(index)
      const existing = writtenChapters.find((item) => item.type === ch.type && item.content)
      if (existing) return
      if (identFailed) {
        showGlobalError(t('app.identBlocked'))
        return
      }
      void handleWriteChapter(ch.type, ch.title)
    },
    [outline, writtenChapters, identFailed, handleWriteChapter, showGlobalError, t],
  )

  const writtenChapter = outline[currentChapterIndex]
    ? writtenChapters.find((ch) => ch.type === outline[currentChapterIndex].type) ?? null
    : writtenChapters[writtenChapters.length - 1] ?? null

  const handleSaveEdit = useCallback(
    async (content: string, boundIndex?: number) => {
      if (!sessionId) {
        const err = new Error('无法保存：章节未就绪')
        showGlobalError(err.message)
        throw err
      }
      const chapterIndex =
        typeof boundIndex === 'number' && Number.isFinite(boundIndex) && boundIndex >= 0
          ? boundIndex
          : writtenChapter?.chapter_index ?? currentChapterIndex
      if (
        typeof chapterIndex !== 'number' ||
        !Number.isFinite(chapterIndex) ||
        chapterIndex < 0
      ) {
        const err = new Error('无法保存：章节序号未知')
        showGlobalError(err.message)
        throw err
      }
      try {
        const resp = await apiFetch(
          `${API_BASE}/sessions/${sessionId}/edit-chapter`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', ...authHeaders() },
            body: JSON.stringify({
              chapter_index: chapterIndex,
              content,
            }),
          },
        )
        const payload = await resp.json().catch(() => ({}))
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
        if (Array.isArray(payload.body_chapters)) {
          setWrittenChapters(
            payload.body_chapters.filter(
              (c: components['schemas']['ChapterResponse']) => c.content,
            ),
          )
        } else if (payload.chapter) {
          markChapterUpdated(payload.chapter)
        }
        if (review?.chapter_index === chapterIndex) setReview(null)
      } catch (err) {
        showGlobalError(err instanceof Error ? err.message : String(err))
        throw err
      }
    },
    [sessionId, writtenChapter, currentChapterIndex, review, markChapterUpdated, showGlobalError],
  )

  const postResumeOutline = useCallback(
    async (nextOutline: PausePayload['outline']) => {
      if (!sessionId) {
        showGlobalError(t('app.needSession'))
        return null
      }
      const resp = await apiFetch(`${API_BASE}/sessions/${sessionId}/resume`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeaders() },
        body: JSON.stringify({ outline: nextOutline }),
      })
      const result = await resp.json().catch(() => ({}))
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      const accepted =
        Array.isArray(result.outline) && result.outline.length ? result.outline : nextOutline
      setOutline(accepted)
      setOutlineLocked(true)
      setCurrentChapterIndex(0)
      return accepted as PausePayload['outline']
    },
    [sessionId, showGlobalError, t],
  )

  const handleApplyGenerate = useCallback(
    async (payload?: PausePayload) => {
      if (writeBusyRef.current) return
      const list = payload?.outline?.length ? payload.outline : outline
      if (!list.length) return
      if (!sessionId) {
        showGlobalError(t('app.needSession'))
        return
      }
      writeBusyRef.current = true
      setWriteBusy(true)
      try {
        const freshIDecide = payload?.decideChapters === 'me' && !outlineLocked
        let accepted = list
        if (freshIDecide) {
          const resumed = await postResumeOutline(list)
          if (resumed?.length) accepted = resumed
        }
        const useIdx = chapterIndexForApply(accepted, {
          freshIDecide,
          iDecideLocked: payload?.decideChapters === 'me' && outlineLocked,
          currentType: outline[currentChapterIndex]?.type,
          currentIndex: currentChapterIndex,
        })
        const ch = accepted[useIdx]
        if (!ch) return
        setCurrentChapterIndex(useIdx)
        setWritingType(ch.type)
        await runGenerateChapter(ch.type, ch.title, payload?.render_kwargs)
      } catch (err) {
        showGlobalError(err instanceof Error ? err.message : t('bench.writeBlocked'))
      } finally {
        writeBusyRef.current = false
        setWriteBusy(false)
      }
    },
    [
      outline,
      outlineLocked,
      currentChapterIndex,
      sessionId,
      postResumeOutline,
      runGenerateChapter,
      showGlobalError,
      t,
    ],
  )

  const handleApproveOutline = useCallback(
    async (nextOutline: PausePayload['outline']) => {
      if (writeBusyRef.current) return
      if (!sessionId) {
        showGlobalError(t('app.needSession'))
        return
      }
      writeBusyRef.current = true
      setWriteBusy(true)
      try {
        await postResumeOutline(nextOutline)
      } catch (err) {
        showGlobalError(err instanceof Error ? err.message : String(err))
      } finally {
        writeBusyRef.current = false
        setWriteBusy(false)
      }
    },
    [sessionId, postResumeOutline, showGlobalError, t],
  )

  const handleRefine = useCallback(
    async (instruction: string) => {
      if (!sessionId) return
      if (writeBusyRef.current) return
      writeBusyRef.current = true
      setWriteBusy(true)
      try {
        const resp = await apiFetch(`${API_BASE}/sessions/${sessionId}/regenerate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', ...authHeaders() },
          body: JSON.stringify({
            chapter_index: Math.max(0, currentChapterIndex),
            instruction,
          }),
        })
        const payload = await resp.json().catch(() => ({}))
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
        if (Array.isArray(payload.body_chapters)) {
          setWrittenChapters(
            payload.body_chapters.filter(
              (c: components['schemas']['ChapterResponse']) => c.content,
            ),
          )
        } else if (payload.chapter) {
          markChapterUpdated(payload.chapter)
        }
        await refreshReview(sessionId)
      } catch (err) {
        showGlobalError(err instanceof Error ? err.message : String(err))
      } finally {
        writeBusyRef.current = false
        setWriteBusy(false)
      }
    },
    [sessionId, currentChapterIndex, markChapterUpdated, refreshReview, showGlobalError],
  )

  const handleDocExport = useCallback(
    async (format: 'tex' | 'pdf' | 'docx', template: string) => {
      if (!sessionId) return
      try {
        const resp = await apiFetch(
          `${API_BASE}/sessions/${sessionId}/doc-export?format=${format}&template=${template}`,
        )
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
        const blob = await resp.blob()
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `paper.${format}`
        a.click()
        URL.revokeObjectURL(url)
        setDocExportOpen(false)
        setHasExported(true)
      } catch (err) {
        showGlobalError(err instanceof Error ? err.message : t('app.exportFailed'))
      }
    },
    [sessionId, showGlobalError, t],
  )

  const hasReadout = Boolean(
    claim || treatmentRow || literatureSource || identFailed || robustnessStatus,
  )
  const directionGate = directionGateForReadiness(uploadReadiness)
  const directionDisabledReason = directionGate.disabled
    ? uploadReadiness === 'PROCESSING'
      ? t('app.directionBlockedProcessing')
      : t('app.directionBlockedUploadFailed')
    : null
  const canExport = writtenChapters.some((ch) => Boolean(ch.content))
  const railItems = outline.map((ch) => {
    const written = writtenChapters.find((item) => item.type === ch.type)
    return {
      type: ch.type,
      title: ch.title,
      status:
        written?.status ?? (writeBusy && writingType === ch.type ? 'streaming' : 'pending'),
      content: written?.content,
      generation_degraded: written?.generation_degraded ?? false,
      review_degraded: written?.review_degraded ?? false,
      review_typed: written?.review_typed ?? false,
    }
  })

  return {
    // state
    edaOpen,
    outline,
    uploading,
    uploadError,
    uploadReadiness,
    uploadNeedsReselect,
    uploadStatus,
    fileInputRef,
    deskOpen,
    showGuide,
    shapedQuestion,
    sampleDirection,
    dataset,
    dataColumns: dataset?.columns ?? [],
    csvName: dataset?.name ?? null,
    csvRows: dataset?.rows ?? null,
    csvCols: dataset?.columns?.length ?? null,
    directionRecord,
    globalError,
    degradations,
    degraded,
    review,
    gateInfo,
    gateBusy,
    docExportOpen,
    codeExportOpen,
    workbenchTab,
    directionBusy,
    directionDisabledReason,
    directionOpen,
    directionSummary,
    claim,
    starRating,
    treatmentRow,
    estimateMeta,
    cleaningReport,
    mainResults,
    literatureSource,
    robustnessStatus,
    writeBlockers,
    identFailed,
    identReport,
    writingType,
    writeBusy,
    writtenChapters,
    currentChapterIndex,
    outlineLocked,
    runFailure,
    evidenceRefreshKey,
    activeRun,
    research,
    // derived
    hasReadout,
    canExport,
    hasExported,
    railItems,
    writtenChapter,
    // actions
    setEdaOpen,
    setUploadError,
    setUploading,
    openGuide,
    closeGuide,
    setShapedQuestion,
    setSampleDirection,
    setDeskOpen,
    setDirectionRecord,
    setWriteBlockers,
    setWorkbenchTab,
    setDirectionOpen,
    setDirectionSummary,
    setDocExportOpen,
    setCodeExportOpen,
    setGateInfo,
    setCurrentChapterIndex,
    showGlobalError,
    handleLogout,
    ensureSession,
    refreshReview,
    uploadCsv,
    takeCsv,
    handleFileSelect,
    handleTrySample,
    handleTryCard,
    handleSaveExpectation,
    handleFreezeSpecSpace,
    handleRunSpecSpace,
    handleRunSpec,
    handleCompareSpecs,
    handlePromotePreview,
    handleRevertPreview,
    handleAcceptChallenge,
    handleApproveClaim,
    handlePreparePaper,
    handleDirectionSubmit,
    handleWriteChapter,
    handleSelectChapter,
    handleSaveEdit,
    handleApprove,
    handleGateRegenerate,
    handleGateForce,
    postResumeOutline,
    handleApplyGenerate,
    handleApproveOutline,
    handleRefine,
    handleDocExport,
  }
}
