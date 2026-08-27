import { useState, useEffect, useRef, useCallback } from 'react'
import EdaSidebar from './components/EdaSidebar'
import type { OutlineChapter } from './components/Outline'
import { ErrorBoundary } from './components/ErrorBoundary'
import ThreeColumn from './components/ThreeColumn'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DeskPage from './pages/DeskPage'
import GuidePage from './pages/GuidePage'
import { BrandMark, LangPills } from './components/UnauthHeader'
import { CsvDropZone } from './components/CsvDropZone'
import PaperPath from './components/PaperPath'
import DirectionForm from './components/DirectionForm'
import type { DirectionFormData } from './components/DirectionForm'
import InstrumentReadout from './components/InstrumentReadout'
import ChapterWriter from './components/ChapterWriter'
import ChapterList from './components/ChapterList'
import ReviewPanel from './components/ReviewPanel'
import DocExportDialog from './components/DocExportDialog'
import CodeExportDialog from './components/CodeExportDialog'
import ReviewGateDialog from './components/ReviewGateDialog'
import RunTracePanel from './components/RunTracePanel'
import { API_BASE } from './lib/apiBase'
import { useT } from './lib/i18n'
import type { components } from './types/api'

const LS_KEY = 'econpaper_session_id'
const LS_TOKEN_KEY = 'econpaper_access_token'
const LS_GUIDE_KEY = 'econpaper_seen_guide'
const LS_SAMPLE_KEY = 'econpaper_sample_direction'
const LS_COLS_KEY = 'econpaper_data_columns'
const SAMPLE_CSV = '/samples/course-panel.csv'
const SAMPLE_DIRECTION = {
  question: '这份课设样例里，年龄和收入是否相关？',
  dv: 'income',
  iv: 'age',
  controls: 'treat',
  method: 'OLS',
  template: 'undergrad',
}

type ReviewInfo = components['schemas']['ReviewInfoResponse']
type WrittenChapter = components['schemas']['ChapterResponse']

type DeskSnapshot = {
  exists?: boolean
  claim?: string | null
  star_rating?: number | null
  identification_failed?: boolean
  identification_report?: string | null
  results?: string | null
  estimate?: { treatment_row?: string | null } | null
  literature_source?: string | null
  write_blockers?: string[]
  robustness_status?: string | null
  outline?: OutlineChapter[]
  body_chapters?: WrittenChapter[]
  research_direction?: { method?: string; dv?: string; iv?: string } | null
}

function storeToken(token: string): void {
  localStorage.setItem(LS_TOKEN_KEY, token)
}

function clearToken(): void {
  localStorage.removeItem(LS_TOKEN_KEY)
}

function authHeaders(): Record<string, string> {
  const token = localStorage.getItem(LS_TOKEN_KEY)
  return token ? { Authorization: `Bearer ${token}` } : {}
}

function directionLine(rd: { method?: string; dv?: string; iv?: string } | null | undefined): string | null {
  if (!rd) return null
  const method = rd.method?.trim()
  const dv = rd.dv?.trim()
  const iv = rd.iv?.trim()
  if (!method && !dv && !iv) return null
  if (dv && iv) return `${method || 'OLS'} · ${dv} ~ ${iv}`
  return method || null
}

function App() {
  const { t } = useT()

  const [authToken, setAuthToken] = useState<string | null>(() => localStorage.getItem(LS_TOKEN_KEY))
  const [authPage, setAuthPage] = useState<'login' | 'register' | null>(null)

  const [sessionId, setSessionId] = useState<string | null>(() => {
    return localStorage.getItem(LS_KEY) || null
  })
  const [edaOpen, setEdaOpen] = useState(false)
  const [outline, setOutline] = useState<OutlineChapter[]>([])

  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [deskOpen, setDeskOpen] = useState(() => !localStorage.getItem(LS_KEY))
  const [seenGuide, setSeenGuide] = useState(() => localStorage.getItem(LS_GUIDE_KEY) === '1')
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
  const [sampleDirection, setSampleDirection] = useState<typeof SAMPLE_DIRECTION | null>(() => {
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

  const [globalError, setGlobalError] = useState<string | null>(null)
  const globalErrorTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const [degradations, setDegradations] = useState<Array<{ node: string; reason: string; fallback: string; timestamp: string }>>([])
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
  const [mainResults, setMainResults] = useState<string | null>(null)
  const [literatureSource, setLiteratureSource] = useState<string | null>(null)
  const [robustnessStatus, setRobustnessStatus] = useState<string | null>(null)
  const [writeBlockers, setWriteBlockers] = useState<string[]>([])
  const [identFailed, setIdentFailed] = useState(false)
  const [identReport, setIdentReport] = useState<string | null>(null)
  const [writingType, setWritingType] = useState<string | null>(null)
  const [writeBusy, setWriteBusy] = useState(false)
  const [writtenChapters, setWrittenChapters] = useState<WrittenChapter[]>([])
  const [currentChapterIndex, setCurrentChapterIndex] = useState(0)

  const showGlobalError = useCallback((message: string) => {
    setGlobalError(message)
    if (globalErrorTimerRef.current) clearTimeout(globalErrorTimerRef.current)
    globalErrorTimerRef.current = setTimeout(() => setGlobalError(null), 8000)
  }, [])

  const handleLogin = useCallback((token: string) => {
    storeToken(token)
    setAuthToken(token)
  }, [])

  const handleLogout = useCallback(() => {
    clearToken()
    setAuthToken(null)
    setSessionId(null)
    localStorage.removeItem(LS_KEY)
    setAuthPage(null)
  }, [])

  const ensureSession = useCallback(async (): Promise<string> => {
    if (sessionId) return sessionId
    const resp = await fetch(`${API_BASE}/sessions`, {
      method: 'POST',
      headers: authHeaders(),
    })
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    const data = await resp.json()
    setSessionId(data.session_id)
    return data.session_id as string
  }, [sessionId])

  const refreshReview = useCallback(async (sid: string) => {
    try {
      const resp = await fetch(`${API_BASE}/sessions/${sid}/review`, {
        headers: authHeaders(),
      })
      if (!resp.ok) return
      const data = await resp.json()
      if (data && (data.feedback || data.score > 0)) setReview(data)
    } catch {
      // empty review is fine
    }
  }, [])

  const applyDeskSnapshot = useCallback((data: DeskSnapshot) => {
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
    }
    const summary = directionLine(data.research_direction)
    if (summary) {
      setDirectionSummary(summary)
      setDirectionOpen(false)
    }
  }, [])

  useEffect(() => {
    const saved = localStorage.getItem(LS_KEY)
    if (!saved) return
    fetch(`${API_BASE}/sessions/${saved}`, { headers: authHeaders() })
      .then((res) => res.json())
      .then((data: DeskSnapshot & { exists: boolean }) => {
        if (!data.exists) {
          localStorage.removeItem(LS_KEY)
          setSessionId(null)
          return
        }
        applyDeskSnapshot(data)
      })
      .catch(() => {})
  }, [applyDeskSnapshot])

  useEffect(() => {
    if (sessionId) {
      localStorage.setItem(LS_KEY, sessionId)
      setDeskOpen(false)
    }
  }, [sessionId])

  useEffect(() => {
    if (!sessionId) { setDegradations([]); setDegraded(false); return }
    const fetchDegradations = async () => {
      try {
        const resp = await fetch(`${API_BASE}/sessions/${sessionId}/degradation`)
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
    return () => { if (degradationsPollRef.current) clearInterval(degradationsPollRef.current) }
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
    async (
      chapter: components['schemas']['ChapterResponse'],
      force: boolean,
    ) => {
      const resp = await fetch(`${API_BASE}/sessions/${sessionId}/approve-chapter`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeaders() },
        body: JSON.stringify({
          // 精确指定章节类型：后端缺省只批"最后一章"，这里不依赖该假设
          ...(chapter.type ? { chapter_type: chapter.type } : {}),
          ...(force ? { force: true } : {}),
        }),
      })
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
      const resp = await fetch(`${API_BASE}/sessions/${sessionId}/regenerate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeaders() },
        body: JSON.stringify({
          chapter_index: Math.max(0, chapterIndex),
        }),
      })
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

  const uploadCsv = useCallback(async (file: File) => {
    setUploading(true)
    setUploadError(null)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const resp = await fetch(`${API_BASE}/upload`, { method: 'POST', headers: authHeaders(), body: formData })
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      const data = await resp.json()
      const cols = data.dataset_meta?.columns
      if (Array.isArray(cols) && cols.every((item: unknown) => typeof item === 'string')) {
        setDataColumns(cols)
        sessionStorage.setItem(LS_COLS_KEY, JSON.stringify(cols))
      } else {
        try {
          const header = (await file.slice(0, 2048).text()).split(/\r?\n/).find(Boolean) || ''
          const parsed = header.split(',').map((name) => name.trim()).filter(Boolean)
          setDataColumns(parsed)
          sessionStorage.setItem(LS_COLS_KEY, JSON.stringify(parsed))
        } catch {
          setDataColumns([])
        }
      }
      markGuideSeen()
      setSessionId(data.session_id)
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }, [markGuideSeen])

  const takeCsv = useCallback(async (file: File) => {
    sessionStorage.removeItem(LS_SAMPLE_KEY)
    setSampleDirection(null)
    await uploadCsv(file)
  }, [uploadCsv])

  const handleFileSelect = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    await takeCsv(file)
  }, [takeCsv])

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

  const formatIdentReport = (nextStar: number | null | undefined, report: string) => {
    if (nextStar == null) return report
    return `${'★'.repeat(nextStar)}${'☆'.repeat(3 - nextStar)}\n${report}`
  }

  const handleDirectionSubmit = useCallback(async (data: DirectionFormData) => {
    setDirectionBusy(true)
    try {
      const sid = await ensureSession()
      const resp = await fetch(`${API_BASE}/sessions/${sid}/direction`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeaders() },
        body: JSON.stringify(data),
      })
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      const result = await resp.json()
      applyDeskSnapshot(result)
      if (result.identification_report) {
        setIdentReport(formatIdentReport(result.star_rating, result.identification_report))
      }
      const summary = directionLine(result.research_direction) || directionLine(data)
      if (summary) {
        setDirectionSummary(summary)
        setDirectionOpen(false)
      }
      if (result.identification_failed) {
        showGlobalError(t('app.identBlocked'))
      }
    } catch (err) {
      showGlobalError(err instanceof Error ? err.message : t('app.directionFailed'))
    } finally {
      setDirectionBusy(false)
    }
  }, [ensureSession, applyDeskSnapshot, showGlobalError, t])

  const handleWriteChapter = useCallback(async (chapterType: string, title: string) => {
    if (!sessionId) {
      showGlobalError(t('app.needSession'))
      return
    }
    setWriteBusy(true)
    setWritingType(chapterType)
    try {
      const resp = await fetch(`${API_BASE}/sessions/${sessionId}/generate-chapter`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeaders() },
        body: JSON.stringify({ chapter: { type: chapterType, title } }),
      })
      const payload = await resp.json().catch(() => ({}))
      if (resp.status === 409) {
        const detail = payload.detail && typeof payload.detail === 'object' ? payload.detail : payload
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
    } catch (err) {
      showGlobalError(err instanceof Error ? err.message : t('bench.writeBlocked'))
    } finally {
      setWriteBusy(false)
    }
  }, [sessionId, refreshReview, showGlobalError, t])

  const handleSelectChapter = useCallback((index: number) => {
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
  }, [outline, writtenChapters, identFailed, handleWriteChapter, showGlobalError, t])

  const handleDocExport = useCallback(async (format: 'tex' | 'pdf' | 'docx', template: string) => {
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
  }, [sessionId, showGlobalError, t])

  const hasReadout = Boolean(claim || treatmentRow || literatureSource || identFailed || robustnessStatus)
  const canExport = writtenChapters.some((ch) => Boolean(ch.content))
  const writtenChapter = outline[currentChapterIndex]
    ? writtenChapters.find((ch) => ch.type === outline[currentChapterIndex].type) ?? null
    : writtenChapters[writtenChapters.length - 1] ?? null
  const railItems = outline.map((ch) => {
    const written = writtenChapters.find((item) => item.type === ch.type)
    return {
      type: ch.type,
      title: ch.title,
      status: written?.status ?? (writeBusy && writingType === ch.type ? 'streaming' : 'pending'),
      content: written?.content,
    }
  })

  if (authPage === 'register') {
    return <RegisterPage onRegister={handleLogin} onSwitchToLogin={() => setAuthPage('login')} />
  }
  if (authPage === 'login') {
    return <LoginPage onLogin={handleLogin} onSwitchToRegister={() => setAuthPage('register')} />
  }

  const firstScreenInput = (
    <input ref={fileInputRef} type="file" accept=".csv" data-testid="file-input" onChange={handleFileSelect} className="hidden" />
  )

  if (!sessionId && !seenGuide) {
    return (
      <>
        {firstScreenInput}
        <GuidePage
          uploading={uploading}
          uploadError={uploadError}
          onPickData={() => fileInputRef.current?.click()}
          onTrySample={() => { void handleTrySample() }}
          onWritePaper={() => {
            markGuideSeen()
            setDeskOpen(true)
          }}
          onLogin={() => setAuthPage('login')}
          onRegister={() => setAuthPage('register')}
        />
      </>
    )
  }

  if (deskOpen && !sessionId) {
    return (
      <>
        {firstScreenInput}
        <DeskPage
          uploading={uploading}
          uploadError={uploadError}
          onPickData={() => fileInputRef.current?.click()}
          onLogin={() => setAuthPage('login')}
          onRegister={() => setAuthPage('register')}
          onConfirm={(title) => {
            setShapedQuestion(title)
            setDeskOpen(false)
          }}
        />
      </>
    )
  }

  return (
    <div className="flex h-screen min-h-0 flex-col overflow-x-auto overflow-y-hidden bg-bg text-ink font-sans selection:bg-accent/20">
      {globalError && (
        <div data-testid="global-error-toast" className="fixed right-4 top-4 z-50 animate-slide-up rounded border border-danger/30 bg-panel px-4 py-2 text-sm text-danger">
          ⚠ {globalError}
        </div>
      )}
      <header className="grid h-[56px] shrink-0 grid-cols-[1fr_auto_1fr] items-center border-b border-border bg-cream px-5">
        <div className="flex items-center gap-3">
          <BrandMark />
        </div>
        <div className="hidden items-center rounded-lg bg-bg p-0.5 sm:flex">
          {([
            ['paper', t('workbench.tabPaper')],
            ['data', t('workbench.tabData')],
            ['format', t('workbench.tabFormat')],
          ] as const).map(([id, label]) => (
            <button
              key={id}
              type="button"
              data-testid={`workbench-tab-${id}`}
              onClick={() => {
                setWorkbenchTab(id)
                if (id === 'data' && sessionId) setEdaOpen(true)
              }}
              className={`rounded-md px-3.5 py-1.5 text-[13px] transition-colors duration-200 ${
                workbenchTab === id ? 'bg-accent text-white' : 'text-muted hover:text-ink'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
        <div className="flex items-center justify-end gap-2.5">
          {sessionId ? (
            <span data-testid="session-ready" hidden />
          ) : (
            <span className="text-xs text-muted font-mono">{t('app.hint')}</span>
          )}
          <input ref={fileInputRef} type="file" accept=".csv" data-testid="file-input" onChange={handleFileSelect} className="hidden" />
          <button data-testid="upload-btn" onClick={() => fileInputRef.current?.click()} disabled={uploading} className="inline-flex items-center gap-1.5 rounded-md bg-accent px-3 py-1.5 text-[12px] font-medium text-white transition-colors duration-200 hover:bg-accent/90 disabled:opacity-50">
            {uploading && (
              <svg className="h-3 w-3 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5}>
                <circle cx="12" cy="12" r="10" strokeDasharray="31.4 31.4" strokeLinecap="round" />
              </svg>
            )}
            {uploading ? t('app.uploading') : t('app.upload')}
          </button>
          <button data-testid="export-doc-btn" onClick={() => setDocExportOpen(true)} disabled={!canExport} className="rounded border border-border px-2 py-1 text-xs text-muted transition-colors duration-200 hover:bg-panel hover:text-ink disabled:opacity-40">
            {t('app.exportDoc')}
          </button>
          <button data-testid="export-code-btn" onClick={() => setCodeExportOpen(true)} disabled={!canExport} className="rounded border border-border px-2 py-1 text-xs text-muted transition-colors duration-200 hover:bg-panel hover:text-ink disabled:opacity-40">
            {t('app.exportCode')}
          </button>
          {uploadError && <span data-testid="upload-error" className="rounded bg-panel px-2 py-0.5 text-xs text-danger">{uploadError}</span>}
          {!sessionId && (
            <button
              type="button"
              data-testid="open-guide-btn"
              onClick={() => {
                localStorage.removeItem(LS_GUIDE_KEY)
                setSeenGuide(false)
              }}
              className="rounded border border-border px-2 py-1 text-xs text-muted transition-colors duration-200 hover:bg-panel hover:text-ink"
            >
              {t('guide.nowAgain')}
            </button>
          )}
          {authToken ? (
            <button onClick={handleLogout} className="rounded border border-border px-2 py-1 text-xs text-muted transition-colors duration-200 hover:bg-panel hover:text-ink">{t('app.logout')}</button>
          ) : (
            <button data-testid="open-login-btn" onClick={() => setAuthPage('login')} className="text-xs text-muted transition-colors duration-200 hover:text-ink">{t('app.login')}</button>
          )}
          <LangPills />
        </div>
      </header>

      <ThreeColumn
        outline={
          <ErrorBoundary>
            <h2 className="mb-4 font-mono text-[11px] uppercase tracking-[0.16em] text-muted">{t('bench.chapters')}</h2>
            {outline.length > 0 && !identFailed ? (
              <div data-testid="chapter-write-dock">
                <p className="mb-2 text-xs leading-6 text-muted">{t('bench.pickChapter')}</p>
                <ChapterList
                  body_chapters={railItems}
                  currentIndex={currentChapterIndex}
                  onSelectChapter={handleSelectChapter}
                />
                {outline.map((ch) => (
                  <button
                    key={ch.type}
                    type="button"
                    data-testid={`write-chapter-${ch.type}`}
                    className="sr-only"
                    disabled={writeBusy}
                    aria-label={`${t('bench.writeChapter')} ${ch.type}`}
                    onClick={() => {
                      const idx = outline.findIndex((item) => item.type === ch.type)
                      handleSelectChapter(idx)
                    }}
                  />
                ))}
              </div>
            ) : (
              <p className="text-xs leading-6 text-muted">{t('bench.noChapters')}</p>
            )}
            <div className="mt-6 border-t border-border pt-4">
              {sessionId ? (
                <button
                  type="button"
                  onClick={() => {
                    setWorkbenchTab('data')
                    setEdaOpen(true)
                  }}
                  className="text-sm text-accent transition-colors duration-200 hover:text-accent/80"
                >
                  {t('bench.openData')}
                </button>
              ) : (
                <p className="text-xs text-muted">{t('app.uploadToExplore')}</p>
              )}
            </div>
          </ErrorBoundary>
        }
        editor={
          <ErrorBoundary>
            <div className="mx-auto max-w-[46rem] px-6 py-10 sm:px-10">
            {workbenchTab === 'data' && (
              <section className="mb-6">
                <h2 className="mb-4 font-serif text-[1.35rem] text-ink">{t('workbench.dataTitle')}</h2>
                <CsvDropZone
                  uploading={uploading}
                  onBrowse={() => fileInputRef.current?.click()}
                  onFile={(file) => { void takeCsv(file) }}
                />
                {sessionId && edaOpen ? (
                  <div className="mt-4">
                    <EdaSidebar sessionId={sessionId} onClose={() => setEdaOpen(false)} />
                  </div>
                ) : (
                  <p className="mt-4 text-sm text-muted">{t('workbench.dataEmpty')}</p>
                )}
              </section>
            )}
            {workbenchTab === 'format' && (
              <section className="mb-8 rounded-lg border border-border bg-panel p-6">
                <h2 className="font-serif text-lg text-ink">{t('workbench.formatTitle')}</h2>
                <p className="mt-2 text-sm leading-6 text-muted">{t('workbench.formatBody')}</p>
              </section>
            )}
            {degraded && <div data-testid="degradation-banner" className="mb-2 animate-slide-up rounded border border-warning/30 bg-panel px-3 py-1.5 text-xs text-warning">{t('app.degradedBanner')}</div>}
            {!hasReadout && (
              <p data-testid="now-hint" className="mb-6 font-serif text-[15px] leading-7 text-ink">
                {t('guide.nowDirection')}
              </p>
            )}
            {hasReadout && !writtenChapter?.content && !writeBusy && (
              <p data-testid="now-hint" className="mb-6 font-serif text-[15px] leading-7 text-ink">
                {t('guide.nowWrite')}
              </p>
            )}
            <section data-testid="direction-section" className="mb-8 rounded-lg border border-border bg-panel p-6">
              <div className="mb-3 flex items-center justify-between gap-3">
                <h2 className="font-serif text-[1.15rem] text-ink">{t('app.directionTitle')}</h2>
                {!directionOpen && directionSummary ? (
                  <button
                    type="button"
                    data-testid="edit-direction-btn"
                    onClick={() => setDirectionOpen(true)}
                    className="text-xs text-accent"
                  >
                    {t('bench.editDirection')}
                  </button>
                ) : null}
              </div>
              {directionOpen ? (
                <DirectionForm
                  onSubmit={handleDirectionSubmit}
                  initialQuestion={shapedQuestion}
                  initial={sampleDirection ?? (shapedQuestion ? { question: shapedQuestion } : undefined)}
                  columns={dataColumns}
                />
              ) : (
                <p data-testid="direction-summary" className="text-sm text-ink">
                  {directionSummary || t('bench.directionSettled')}
                </p>
              )}
              {directionBusy && <p className="mt-2 text-xs text-muted">{t('app.directionWorking')}</p>}
            </section>
            {hasReadout && (
              <InstrumentReadout
                claim={claim}
                starRating={starRating}
                treatmentRow={treatmentRow}
                results={mainResults}
                literatureSource={literatureSource}
                robustnessStatus={robustnessStatus}
                writeBlockers={writeBlockers}
                identificationFailed={identFailed}
              />
            )}
            {identReport && (
              <details className="mb-4 rounded border border-border bg-paper px-3 py-2">
                <summary className="cursor-pointer font-mono text-xs text-muted">识别说明</summary>
                <pre data-testid="ident-report" className="mt-2 whitespace-pre-wrap text-xs">{identReport}</pre>
              </details>
            )}
            {writeBusy ? (
              <p data-testid="chapter-writing" className="font-serif text-sm leading-7 text-muted">
                {t('bench.writing').replace(
                  '{title}',
                  outline.find((ch) => ch.type === writingType)?.title || writingType || '',
                )}
              </p>
            ) : writtenChapter?.content ? (
              <div className="mb-6">
                <ChapterWriter chapter={writtenChapter} sessionId={sessionId ?? undefined} onApprove={handleApprove} />
              </div>
            ) : (
              <p className="font-serif text-[15px] leading-[1.8] text-muted">{t('bench.paperEmpty')}</p>
            )}
            </div>
          </ErrorBoundary>
        }
        agent={
          <ErrorBoundary>
            <PaperPath
              uploading={uploading}
              hasSession={Boolean(sessionId)}
              hasDirection={Boolean(directionSummary)}
              directionOpen={directionOpen}
              hasReadout={hasReadout}
              hasOutline={outline.length > 0}
              writing={writeBusy}
              hasChapter={Boolean(writtenChapter?.content)}
              awaitingApprove={writtenChapter?.status === 'generated'}
              canExport={canExport}
              onSelect={(id) => {
                if (id === 'upload_data' || id === 'clean_data') {
                  setWorkbenchTab('data')
                  if (sessionId) setEdaOpen(true)
                } else if (id === 'translate_code' || id === 'export_docx') {
                  setWorkbenchTab('format')
                } else {
                  setWorkbenchTab('paper')
                }
              }}
            />
            {sessionId && review ? (
              <div className="mt-4">
                <ReviewPanel sessionId={sessionId} review={review} onDecision={() => refreshReview(sessionId)} />
              </div>
            ) : (
              <p data-testid="review-idle" className="mt-4 text-xs leading-6 text-muted">
                {hasReadout ? t('bench.reviewAfterWrite') : t('bench.reviewAfterDirection')}
              </p>
            )}
            {degradations.length > 0 && (
              <p className="mt-4 text-[11px] leading-5 text-muted">
                {degradations[0].node}: {degradations[0].reason}
              </p>
            )}
            {sessionId && <RunTracePanel sessionId={sessionId} />}
          </ErrorBoundary>
        }
      />

      {gateInfo && (
        <ReviewGateDialog
          score={gateInfo.score}
          threshold={gateInfo.threshold}
          feedback={
            review && review.chapter_index === gateInfo.chapter.chapter_index
              ? review.feedback || ''
              : ''
          }
          busy={gateBusy}
          onRegenerate={handleGateRegenerate}
          onForce={handleGateForce}
          onClose={() => setGateInfo(null)}
        />
      )}
      {docExportOpen && sessionId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/40">
          <DocExportDialog
            sessionId={sessionId}
            onClose={() => setDocExportOpen(false)}
            onExport={handleDocExport}
          />
        </div>
      )}
      <CodeExportDialog
        sessionId={sessionId ?? ''}
        isOpen={codeExportOpen && !!sessionId}
        onClose={() => setCodeExportOpen(false)}
      />
    </div>
  )
}

export default App
