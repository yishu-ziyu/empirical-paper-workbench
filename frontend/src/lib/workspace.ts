// ── Workspace state & actions ──────────────────────────────────────
// Everything the workspace touch panel needs, lifted out of App.tsx so
// the shell component only assembles routing + layout. No API contract,
// no response shape and no state field changes here — only extraction.

import { useState, useEffect, useRef, useCallback } from 'react'
import type { OutlineChapter } from '../components/Outline'
import type { DirectionFormData, DirectionFormInitial } from '../components/DirectionForm'
import type { PausePayload } from '../components/WriteLoop'
import { API_BASE, apiFetch } from './apiBase'
import type { components } from '../types/api'

// localStorage / sessionStorage keys owned by the workspace.
export const LS_GUIDE_KEY = 'econpaper_seen_guide'
export const LS_SAMPLE_KEY = 'econpaper_sample_direction'
export const LS_COLS_KEY = 'econpaper_data_columns'
export const LS_CSV_KEY = 'econpaper_csv_meta'

export const SAMPLE_CSV = '/samples/course-panel.csv'
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

export type DeskSnapshot = {
  exists?: boolean
  claim?: string | null
  star_rating?: number | null
  identification_failed?: boolean
  identification_report?: string | null
  results?: string | null
  estimate?: Record<string, any> | null
  cleaning_report?: Record<string, any> | null
  literature_source?: string | null
  write_blockers?: string[]
  robustness_status?: string | null
  outline?: OutlineChapter[]
  body_chapters?: WrittenChapter[]
  research_direction?: {
    method?: string
    dv?: string
    iv?: string
    question?: string
    controls?: string[] | string
    template?: string
    instrument?: string
    time_col?: string
    id_col?: string
    first_treat_col?: string
    running_var?: string
    cutoff?: number
    unit_col?: string
    treatment_time?: string
  } | null
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

export function readCsvMeta(
  sessionId: string | null,
): { name: string | null; rows: number | null; cols: number | null } {
  try {
    if (!sessionId) return { name: null, rows: null, cols: null }
    const raw = sessionStorage.getItem(LS_CSV_KEY)
    if (!raw) return { name: null, rows: null, cols: null }
    const parsed = JSON.parse(raw) as {
      sessionId?: unknown
      name?: unknown
      rows?: unknown
      cols?: unknown
    }
    if (parsed.sessionId !== sessionId) return { name: null, rows: null, cols: null }
    return {
      name: typeof parsed.name === 'string' ? parsed.name : null,
      rows: typeof parsed.rows === 'number' ? parsed.rows : null,
      cols: typeof parsed.cols === 'number' ? parsed.cols : null,
    }
  } catch {
    return { name: null, rows: null, cols: null }
  }
}

export function writeCsvMeta(
  sessionId: string,
  name: string | null,
  rows: number | null,
  cols: number | null,
): void {
  sessionStorage.setItem(LS_CSV_KEY, JSON.stringify({ sessionId, name, rows, cols }))
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

export function useWorkspace(opts: WorkspaceOptions) {
  const { sessionId, setSessionId, setAuthed, t } = opts

  const [edaOpen, setEdaOpen] = useState(false)
  const [outline, setOutline] = useState<OutlineChapter[]>([])

  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [deskOpen, setDeskOpen] = useState(
    () => !localStorage.getItem('econpaper_session_id'),
  )
  const [seenGuide, setSeenGuide] = useState(
    () => localStorage.getItem(LS_GUIDE_KEY) === '1',
  )
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
  const [dataColumns, setDataColumns] = useState<string[]>(() => {
    try {
      const raw = sessionStorage.getItem(LS_COLS_KEY)
      const parsed = raw ? JSON.parse(raw) : []
      return Array.isArray(parsed) ? parsed.filter((item) => typeof item === 'string') : []
    } catch {
      return []
    }
  })
  const [csvName, setCsvName] = useState<string | null>(
    () => readCsvMeta(localStorage.getItem('econpaper_session_id')).name,
  )
  const [csvRows, setCsvRows] = useState<number | null>(
    () => readCsvMeta(localStorage.getItem('econpaper_session_id')).rows,
  )
  const [csvCols, setCsvCols] = useState<number | null>(
    () => readCsvMeta(localStorage.getItem('econpaper_session_id')).cols,
  )
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
  const [codeExportOpen, setCodeExportOpen] = useState(false)
  const [workbenchTab, setWorkbenchTab] = useState<'paper' | 'data' | 'format'>('paper')
  const [directionBusy, setDirectionBusy] = useState(false)
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

  const showGlobalError = useCallback((message: string) => {
    setGlobalError(message)
    if (globalErrorTimerRef.current) clearTimeout(globalErrorTimerRef.current)
    globalErrorTimerRef.current = setTimeout(() => setGlobalError(null), 8000)
  }, [])

  const forgetCsvMeta = useCallback(() => {
    sessionStorage.removeItem(LS_CSV_KEY)
    setCsvName(null)
    setCsvRows(null)
    setCsvCols(null)
  }, [])

  const handleLogout = useCallback(() => {
    // Server revokes the refresh token and clears both cookies.
    void (async () => {
      try {
        await fetch(`${API_BASE}/auth/logout`, { method: 'POST', credentials: 'include' })
      } catch {
        /* local logout proceeds regardless */
      }
    })()
    setAuthed(false)
    setSessionId(null)
    localStorage.removeItem('econpaper_session_id')
    localStorage.removeItem(LS_GUIDE_KEY)
    forgetCsvMeta()
    setDeskOpen(false)
    setSeenGuide(false)
  }, [setAuthed, setSessionId, forgetCsvMeta])

  const ensureSession = useCallback(async (): Promise<string> => {
    if (sessionId) return sessionId
    const resp = await apiFetch(`${API_BASE}/sessions`, {
      method: 'POST',
      headers: authHeaders(),
    })
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    const data = await resp.json()
    forgetCsvMeta()
    setSessionId(data.session_id)
    return data.session_id as string
  }, [sessionId, forgetCsvMeta, setSessionId])

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

  const applyDeskSnapshot = useCallback((data: DeskSnapshot, sid?: string | null) => {
    if (data.exists === false) return
    const hasDesk = Boolean(
      data.claim ||
        data.estimate ||
        data.literature_source ||
        data.identification_report ||
        data.robustness_status ||
        data.identification_failed ||
        data.star_rating != null ||
        (data.outline && data.outline.length) ||
        (data.body_chapters && data.body_chapters.length) ||
        data.research_direction,
    )
    if (!hasDesk) return
    setClaim(data.claim ?? null)
    setStarRating(data.star_rating ?? null)
    setMainResults(typeof data.results === 'string' ? data.results : null)
    const row = data.estimate?.treatment_row
    setTreatmentRow(typeof row === 'string' && row ? row : null)
    setEstimateMeta(data.estimate ?? null)
    setCleaningReport(data.cleaning_report ?? null)
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
    const summary = directionLine(data.research_direction)
    if (summary) {
      setDirectionSummary(summary)
      setDirectionOpen(false)
    }
    const asked = data.research_direction?.question?.trim()
    if (asked) setShapedQuestion(asked)
    if (data.research_direction) {
      const rd = data.research_direction
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
    const csv = readCsvMeta(sid ?? localStorage.getItem('econpaper_session_id'))
    if (csv.name) setCsvName(csv.name)
    if (csv.rows != null) setCsvRows(csv.rows)
    if (csv.cols != null) setCsvCols(csv.cols)
  }, [])

  // 会话回填：刷新后从 session 恢复工作区
  useEffect(() => {
    const saved = localStorage.getItem('econpaper_session_id')
    if (!saved) return
    apiFetch(`${API_BASE}/sessions/${saved}`, { headers: authHeaders() })
      .then((res) => res.json())
      .then((data: DeskSnapshot & { exists: boolean }) => {
        if (!data.exists) {
          localStorage.removeItem('econpaper_session_id')
          setSessionId(null)
          forgetCsvMeta()
          return
        }
        applyDeskSnapshot(data, saved)
      })
      .catch(() => {})
  }, [setSessionId, forgetCsvMeta, applyDeskSnapshot])

  useEffect(() => {
    if (sessionId) {
      localStorage.setItem('econpaper_session_id', sessionId)
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

  const markGuideSeen = useCallback(() => {
    localStorage.setItem(LS_GUIDE_KEY, '1')
    setSeenGuide(true)
  }, [])

  const uploadCsv = useCallback(
    async (file: File) => {
      setUploading(true)
      setUploadError(null)
      try {
        const formData = new FormData()
        formData.append('file', file)
        const resp = await apiFetch(`${API_BASE}/upload`, {
          method: 'POST',
          headers: authHeaders(),
          body: formData,
        })
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
        const data = await resp.json()
        const cols = data.dataset_meta?.columns
        let colCount: number | null = null
        if (Array.isArray(cols) && cols.every((item: unknown) => typeof item === 'string')) {
          setDataColumns(cols)
          sessionStorage.setItem(LS_COLS_KEY, JSON.stringify(cols))
          colCount = cols.length
          setCsvCols(colCount)
        } else {
          try {
            const header =
              (await file.slice(0, 2048).text()).split(/\r?\n/).find(Boolean) || ''
            const parsed = header.split(',').map((name) => name.trim()).filter(Boolean)
            setDataColumns(parsed)
            sessionStorage.setItem(LS_COLS_KEY, JSON.stringify(parsed))
            colCount = parsed.length
            setCsvCols(colCount)
          } catch {
            setDataColumns([])
          }
        }
        setCsvName(file.name)
        const rowCount = data.dataset_meta?.rows
        const rows = typeof rowCount === 'number' ? rowCount : null
        setCsvRows(rows)
        writeCsvMeta(data.session_id, file.name, rows, colCount)
        markGuideSeen()
        setSessionId(data.session_id)
      } catch (err) {
        setUploadError(err instanceof Error ? err.message : 'Upload failed')
      } finally {
        setUploading(false)
        if (fileInputRef.current) fileInputRef.current.value = ''
      }
    },
    [markGuideSeen, setSessionId],
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

  const handleDirectionSubmit = useCallback(
    async (data: DirectionFormData) => {
      setDirectionBusy(true)
      try {
        const sid = await ensureSession()
        const resp = await apiFetch(`${API_BASE}/sessions/${sid}/direction`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', ...authHeaders() },
          body: JSON.stringify(data),
        })
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
        const result = await resp.json()
        applyDeskSnapshot(result, sid)
        if (result.identification_report) {
          setIdentReport(formatIdentReport(result.star_rating, result.identification_report))
        }
        const summary = directionLine(result.research_direction) || directionLine(data)
        if (summary) {
          setDirectionSummary(summary)
          setDirectionOpen(false)
        }
        if (data.question.trim()) setShapedQuestion(data.question)
        setDirectionRecord(data)
        setOutlineLocked(false)
        if (result.identification_failed) {
          showGlobalError(t('app.identBlocked'))
        }
      } catch (err) {
        showGlobalError(err instanceof Error ? err.message : t('app.directionFailed'))
      } finally {
        setDirectionBusy(false)
      }
    },
    [ensureSession, applyDeskSnapshot, showGlobalError, t],
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
        const resp = await fetch(
          `${API_BASE}/sessions/${sessionId}/doc-export?format=${format}&template=${template}`,
          { headers: authHeaders() },
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
      } catch (err) {
        showGlobalError(err instanceof Error ? err.message : t('app.exportFailed'))
      }
    },
    [sessionId, showGlobalError, t],
  )

  const hasReadout = Boolean(
    claim || treatmentRow || literatureSource || identFailed || robustnessStatus,
  )
  const canExport = writtenChapters.some((ch) => Boolean(ch.content))
  const railItems = outline.map((ch) => {
    const written = writtenChapters.find((item) => item.type === ch.type)
    return {
      type: ch.type,
      title: ch.title,
      status:
        written?.status ?? (writeBusy && writingType === ch.type ? 'streaming' : 'pending'),
      content: written?.content,
    }
  })

  return {
    // state
    edaOpen,
    outline,
    uploading,
    uploadError,
    fileInputRef,
    deskOpen,
    seenGuide,
    shapedQuestion,
    sampleDirection,
    dataColumns,
    csvName,
    csvRows,
    csvCols,
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
    // derived
    hasReadout,
    canExport,
    railItems,
    writtenChapter,
    // actions
    setEdaOpen,
    setUploadError,
    setUploading,
    setSeenGuide,
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
    forgetCsvMeta,
    handleLogout,
    ensureSession,
    refreshReview,
    markGuideSeen,
    uploadCsv,
    takeCsv,
    handleFileSelect,
    handleTrySample,
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