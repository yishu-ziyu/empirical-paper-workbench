import { useState, useEffect, useRef, useCallback } from 'react'
import { WSClient } from './lib/ws'
import type { WSStatus } from './lib/ws'
import EdaSidebar from './components/EdaSidebar'
import Outline from './components/Outline'
import type { OutlineChapter } from './components/Outline'
import Editor from './components/Editor'
import AgentPanel from './components/AgentPanel'
import JourneyTimeline from './components/JourneyTimeline'
import { ErrorBoundary } from './components/ErrorBoundary'
import ThreeColumn from './components/ThreeColumn'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DeskPage from './pages/DeskPage'
import DirectionForm from './components/DirectionForm'
import type { DirectionFormData } from './components/DirectionForm'
import InstrumentReadout from './components/InstrumentReadout'
import ChapterWriter from './components/ChapterWriter'
import ReviewPanel from './components/ReviewPanel'
import DocExportDialog from './components/DocExportDialog'
import CodeExportDialog from './components/CodeExportDialog'
import { useT } from './lib/i18n'
import type { JourneyStage } from './types/journey'
import type { components } from './types/api'

const LS_KEY = 'econpaper_session_id'
const LS_TOKEN_KEY = 'econpaper_access_token'
const API_BASE = 'http://localhost:8000'
const WS_BASE = 'ws://localhost:8000'

type ReviewInfo = components['schemas']['ReviewInfoResponse']
type WrittenChapter = components['schemas']['ChapterResponse']

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

const JOURNEY_STAGE_COUNT = 8
const INTERVENING_STAGES = new Set([0, 2, 3, 5, 6])

function defaultJourneyStages(): JourneyStage[] {
  return Array.from({ length: JOURNEY_STAGE_COUNT }, (_, i) => ({
    status: i === 0 ? 'active' : 'pending',
    canIntervene: INTERVENING_STAGES.has(i),
  }))
}

function App() {
  const { t, lang, setLang } = useT()

  const [authToken, setAuthToken] = useState<string | null>(() => localStorage.getItem(LS_TOKEN_KEY))
  const [authPage, setAuthPage] = useState<'login' | 'register' | null>(null)

  const [sessionId, setSessionId] = useState<string | null>(() => {
    return localStorage.getItem(LS_KEY) || null
  })
  const [connectionState, setConnectionState] = useState<WSStatus>('disconnected')
  const [edaOpen, setEdaOpen] = useState(true)
  const [bodyChapters, setBodyChapters] = useState<OutlineChapter[]>([
    { type: 'intro', title: 'Title' },
  ])

  const [leftOpen, setLeftOpen] = useState(true)
  const [rightOpen, setRightOpen] = useState(true)

  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [currentJourneyStage, setCurrentJourneyStage] = useState<number>(0)
  const [journeyStages, setJourneyStages] = useState<JourneyStage[]>(defaultJourneyStages)
  const [deskOpen, setDeskOpen] = useState(() => !localStorage.getItem(LS_KEY))
  const [shapedQuestion, setShapedQuestion] = useState('')

  const [chunks, setChunks] = useState<string[]>([])
  const [currentNode, setCurrentNode] = useState('')
  const [currentStatus, setCurrentStatus] = useState<'running' | 'paused' | 'done' | 'idle'>('idle')
  const [interrupt, setInterrupt] = useState<string | undefined>(undefined)
  const [wsError, setWsError] = useState<string | null>(null)
  const wsClientRef = useRef<WSClient | null>(null)

  const [globalError, setGlobalError] = useState<string | null>(null)
  const globalErrorTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const [degradations, setDegradations] = useState<Array<{ node: string; reason: string; fallback: string; timestamp: string }>>([])
  const [degraded, setDegraded] = useState(false)
  const degradationsPollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const [reconnecting, setReconnecting] = useState(false)
  const reconnectingRef = useRef(false)

  const [identBusy, setIdentBusy] = useState(false)
  const [identReport, setIdentReport] = useState<string | null>(null)
  const [robustBusy, setRobustBusy] = useState(false)
  const [robustReport, setRobustReport] = useState<string | null>(null)
  const [review, setReview] = useState<ReviewInfo | null>(null)
  const [docExportOpen, setDocExportOpen] = useState(false)
  const [codeExportOpen, setCodeExportOpen] = useState(false)
  const [directionBusy, setDirectionBusy] = useState(false)
  const [claim, setClaim] = useState<string | null>(null)
  const [starRating, setStarRating] = useState<number | null>(null)
  const [treatmentRow, setTreatmentRow] = useState<string | null>(null)
  const [mainResults, setMainResults] = useState<string | null>(null)
  const [literatureSource, setLiteratureSource] = useState<string | null>(null)
  const [writeBlockers, setWriteBlockers] = useState<string[]>([])
  const [identFailed, setIdentFailed] = useState(false)
  const [writingType, setWritingType] = useState<string | null>(null)
  const [writeBusy, setWriteBusy] = useState(false)
  const [writtenChapter, setWrittenChapter] = useState<WrittenChapter | null>(null)

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

  const refreshJourney = useCallback(async (sid: string) => {
    try {
      const resp = await fetch(`${API_BASE}/sessions/${sid}/journey`, {
        headers: authHeaders(),
      })
      if (!resp.ok) return
      const data = await resp.json()
      setCurrentJourneyStage(data.currentStage ?? 0)
      if (Array.isArray(data.stages) && data.stages.length === JOURNEY_STAGE_COUNT) {
        setJourneyStages(
          data.stages.map((s: { status?: string }, i: number) => ({
            status: (s?.status ?? (i === 0 ? 'active' : 'pending')) as JourneyStage['status'],
            canIntervene: INTERVENING_STAGES.has(i),
          })),
        )
      }
    } catch {
      // keep defaults
    }
  }, [])

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

  useEffect(() => {
    const saved = localStorage.getItem(LS_KEY)
    if (!saved) return
    fetch(`${API_BASE}/sessions/${saved}`, { headers: authHeaders() })
      .then((res) => res.json())
      .then((data: { exists: boolean }) => {
        if (!data.exists) {
          localStorage.removeItem(LS_KEY)
          setSessionId(null)
        }
      })
      .catch(() => {})
  }, [])

  useEffect(() => {
    if (sessionId) {
      localStorage.setItem(LS_KEY, sessionId)
      setDeskOpen(false)
    }
  }, [sessionId])

  useEffect(() => {
    wsClientRef.current?.close()
    wsClientRef.current = null
    if (!sessionId) {
      setConnectionState('disconnected')
      setChunks([])
      setCurrentNode('')
      setCurrentStatus('idle')
      setInterrupt(undefined)
      return
    }
    setChunks([])
    setCurrentNode('')
    setCurrentStatus('idle')
    setInterrupt(undefined)
    setWsError(null)
    const wsUrl = `${WS_BASE}/sessions/${sessionId}/stream`
    const client = new WSClient(wsUrl, {
      onChunk: (_chapterId, chunk) => setChunks((prev) => [...prev, chunk]),
      onStatus: (node, status) => { setCurrentNode(node); setCurrentStatus(status) },
      onInterrupt: (_chapterId, content) => setInterrupt(content),
      onError: (message) => setWsError(message),
      onConnectionChange: (state) => setConnectionState(state),
    })
    wsClientRef.current = client
    client.connect()
    return () => { client.close(); wsClientRef.current = null }
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
    if (connectionState === 'disconnected' && sessionId) {
      if (!reconnectingRef.current) { reconnectingRef.current = true; setReconnecting(true) }
    } else if (connectionState === 'connected') { reconnectingRef.current = false; setReconnecting(false) }
    else if (!sessionId) { reconnectingRef.current = false; setReconnecting(false) }
  }, [connectionState, sessionId])

  useEffect(() => {
    if (!sessionId) return
    refreshJourney(sessionId)
    refreshReview(sessionId)
  }, [sessionId, refreshJourney, refreshReview])

  const handleFileSelect = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    setUploadError(null)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const resp = await fetch(`${API_BASE}/upload`, { method: 'POST', headers: authHeaders(), body: formData })
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      const data = await resp.json()
      setSessionId(data.session_id)
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setUploading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }, [])

  const formatIdentReport = (starRating: number | null | undefined, report: string) => {
    if (starRating == null) return report
    return `${'★'.repeat(starRating)}${'☆'.repeat(3 - starRating)}\n${report}`
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
      if (Array.isArray(result.outline) && result.outline.length) {
        setBodyChapters(result.outline)
      }
      if (result.identification_report) {
        setIdentReport(formatIdentReport(result.star_rating, result.identification_report))
      }
      setClaim(result.claim ?? null)
      setStarRating(result.star_rating ?? null)
      setMainResults(typeof result.results === 'string' ? result.results : null)
      const row = result.estimate?.treatment_row
      setTreatmentRow(typeof row === 'string' && row ? row : null)
      setLiteratureSource(result.literature_source ?? null)
      setWriteBlockers(Array.isArray(result.write_blockers) ? result.write_blockers : [])
      setIdentFailed(Boolean(result.identification_failed))
      if (result.identification_failed) {
        showGlobalError(t('app.identBlocked'))
      }
      await refreshJourney(sid)
    } catch (err) {
      showGlobalError(err instanceof Error ? err.message : t('app.directionFailed'))
    } finally {
      setDirectionBusy(false)
    }
  }, [ensureSession, refreshJourney, showGlobalError, t])

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
      if (payload.chapter) setWrittenChapter(payload.chapter)
      setWriteBlockers([])
      await refreshReview(sessionId)
      await refreshJourney(sessionId)
    } catch (err) {
      showGlobalError(err instanceof Error ? err.message : t('bench.writeBlocked'))
    } finally {
      setWriteBusy(false)
    }
  }, [sessionId, refreshReview, refreshJourney, showGlobalError, t])

  const handleIdentify = useCallback(async () => {
    if (!sessionId) {
      showGlobalError(t('app.needSession'))
      return
    }
    setIdentBusy(true)
    try {
      const resp = await fetch(`${API_BASE}/sessions/${sessionId}/identification`, {
        method: 'POST',
        headers: authHeaders(),
      })
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      const data = await resp.json()
      const report = data.diagnosis?.report || (data.identification_failed ? t('app.identFailed') : t('app.identOk'))
      setIdentReport(formatIdentReport(data.star_rating, report))
      await refreshJourney(sessionId)
    } catch (err) {
      showGlobalError(err instanceof Error ? err.message : t('app.identFailed'))
    } finally {
      setIdentBusy(false)
    }
  }, [sessionId, refreshJourney, showGlobalError, t])

  const handleRobustness = useCallback(async () => {
    if (!sessionId) {
      showGlobalError(t('app.needSession'))
      return
    }
    setRobustBusy(true)
    try {
      const resp = await fetch(`${API_BASE}/sessions/${sessionId}/robustness`, {
        method: 'POST',
        headers: authHeaders(),
      })
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
      const data = await resp.json()
      setRobustReport(data.robustness_results?.summary_table || t('app.robustEmpty'))
      await refreshJourney(sessionId)
    } catch (err) {
      showGlobalError(err instanceof Error ? err.message : t('app.robustFailed'))
    } finally {
      setRobustBusy(false)
    }
  }, [sessionId, refreshJourney, showGlobalError, t])

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

  if (authPage === 'register') {
    return <RegisterPage onRegister={handleLogin} onSwitchToLogin={() => setAuthPage('login')} />
  }
  if (authPage === 'login') {
    return <LoginPage onLogin={handleLogin} onSwitchToRegister={() => setAuthPage('register')} />
  }

  if (deskOpen && !sessionId) {
    return (
      <>
        <input ref={fileInputRef} type="file" accept=".csv" data-testid="file-input" onChange={handleFileSelect} className="hidden" />
        <DeskPage
          uploading={uploading}
          uploadError={uploadError}
          onPickData={() => fileInputRef.current?.click()}
          onLogin={() => setAuthPage('login')}
          onConfirm={(title) => {
            setShapedQuestion(title)
            setDeskOpen(false)
          }}
        />
      </>
    )
  }

  return (
    <div className="flex min-h-screen flex-col bg-bg text-ink font-sans selection:bg-accent/20">
      {globalError && (
        <div data-testid="global-error-toast" className="fixed right-4 top-4 z-50 animate-slide-up rounded border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700 shadow-lg">
          ⚠ {globalError}
        </div>
      )}
      {reconnecting && (
        <div data-testid="reconnection-hint" className="fixed right-4 top-14 z-50 animate-slide-up rounded border border-yellow-200 bg-yellow-50 px-4 py-2 text-sm text-yellow-700 shadow-lg">
          {t('app.reconnecting')}
        </div>
      )}
      <header className="flex items-center justify-between border-b border-border bg-bg px-6 py-3 shadow-sm">
        <div className="flex items-center gap-3">
          <button type="button" onClick={() => setLeftOpen((v) => !v)} className="text-muted hover:text-ink transition-colors duration-200 lg:hidden" aria-label={t('app.toggleLeft')}>
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
            </svg>
          </button>
          <h1 className="text-lg font-semibold tracking-tight font-serif">{t('app.title')}</h1>
        </div>
        <div className="flex items-center gap-3">
          {sessionId ? (
            <span data-testid="session-id-indicator" className="rounded bg-accent/10 px-2 py-0.5 text-xs font-mono text-accent transition-colors duration-200">{sessionId}</span>
          ) : (
            <span className="text-xs text-muted font-mono">{t('app.hint')}</span>
          )}
          <input ref={fileInputRef} type="file" accept=".csv" data-testid="file-input" onChange={handleFileSelect} className="hidden" />
          <button data-testid="upload-btn" onClick={() => fileInputRef.current?.click()} disabled={uploading} className="inline-flex items-center gap-1.5 rounded bg-accent px-3 py-1 text-xs text-white transition-colors duration-200 hover:bg-accent/90 disabled:opacity-50">
            {uploading && (
              <svg className="h-3 w-3 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5}>
                <circle cx="12" cy="12" r="10" strokeDasharray="31.4 31.4" strokeLinecap="round" />
              </svg>
            )}
            {uploading ? t('app.uploading') : t('app.upload')}
          </button>
          <button data-testid="export-doc-btn" onClick={() => setDocExportOpen(true)} disabled={!sessionId} className="rounded border border-border px-2 py-1 text-xs text-muted transition-colors duration-200 hover:bg-panel hover:text-ink disabled:opacity-40">
            {t('app.exportDoc')}
          </button>
          <button data-testid="export-code-btn" onClick={() => setCodeExportOpen(true)} disabled={!sessionId} className="rounded border border-border px-2 py-1 text-xs text-muted transition-colors duration-200 hover:bg-panel hover:text-ink disabled:opacity-40">
            {t('app.exportCode')}
          </button>
          {uploadError && <span data-testid="upload-error" className="rounded bg-red-50 px-2 py-0.5 text-xs text-red-600">{uploadError}</span>}
          {authToken ? (
            <button onClick={handleLogout} className="rounded border border-border px-2 py-1 text-xs text-muted transition-colors duration-200 hover:bg-panel hover:text-ink">{t('app.logout')}</button>
          ) : (
            <button data-testid="open-login-btn" onClick={() => setAuthPage('login')} className="rounded border border-border px-2 py-1 text-xs text-muted transition-colors duration-200 hover:bg-panel hover:text-ink">{t('app.login')}</button>
          )}
          <button onClick={() => setLang(lang === 'zh' ? 'en' : 'zh')} className="rounded border border-border px-2 py-1 text-xs text-muted transition-colors duration-200 hover:bg-panel hover:text-ink">{t('app.langSwitch')}</button>
          <button type="button" onClick={() => setRightOpen((v) => !v)} className="text-muted hover:text-ink transition-colors duration-200 lg:hidden" aria-label={t('app.toggleRight')}>
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
            </svg>
          </button>
        </div>
      </header>

      <JourneyTimeline
        sessionId={sessionId}
        currentStage={currentJourneyStage}
        stages={journeyStages}
      />

      <ThreeColumn
        leftOpen={leftOpen}
        rightOpen={rightOpen}
        outline={
          <ErrorBoundary>
            <h2 className="mb-3 text-xs uppercase tracking-wider text-muted font-mono">{t('app.outline')}</h2>
            {edaOpen && sessionId ? (
              <EdaSidebar sessionId={sessionId} onClose={() => setEdaOpen(false)} />
            ) : sessionId ? (
              <button onClick={() => setEdaOpen(true)} className="text-sm text-accent transition-colors duration-200 hover:text-accent/80">{t('app.openEda')}</button>
            ) : (
              <p className="text-xs text-muted">{t('app.uploadToExplore')}</p>
            )}
          </ErrorBoundary>
        }
        editor={
          <ErrorBoundary>
            {degraded && <div data-testid="degradation-banner" className="mb-2 animate-slide-up rounded border border-yellow-200 bg-yellow-50 px-3 py-1.5 text-xs text-yellow-700">{t('app.degradedBanner')}</div>}
            <section data-testid="direction-section" className="mb-6 rounded border border-border bg-panel p-4">
              <h2 className="mb-3 text-sm font-semibold">{t('app.directionTitle')}</h2>
              <DirectionForm onSubmit={handleDirectionSubmit} initialQuestion={shapedQuestion} />
              {directionBusy && <p className="mt-2 text-xs text-muted">{t('app.directionWorking')}</p>}
            </section>
            {(claim || treatmentRow || literatureSource || identFailed) && (
              <InstrumentReadout
                claim={claim}
                starRating={starRating}
                treatmentRow={treatmentRow}
                results={mainResults}
                literatureSource={literatureSource}
                writeBlockers={writeBlockers}
                identificationFailed={identFailed}
              />
            )}
            {bodyChapters.length > 0 && !identFailed && (
              <section data-testid="chapter-write-dock" className="mb-6 rounded border border-border bg-panel p-4">
                <h2 className="mb-3 font-mono text-xs uppercase tracking-wider text-muted">
                  {t('bench.pickChapter')}
                </h2>
                <div className="flex flex-wrap gap-2">
                  {bodyChapters.map((ch) => (
                    <button
                      key={ch.type}
                      type="button"
                      data-testid={`write-chapter-${ch.type}`}
                      disabled={writeBusy}
                      onClick={() => handleWriteChapter(ch.type, ch.title)}
                      className="rounded border border-border px-3 py-1 text-xs hover:bg-paper disabled:opacity-40"
                    >
                      {writeBusy && writingType === ch.type ? t('bench.writing') : `${t('bench.writeChapter')} · ${ch.type}`}
                    </button>
                  ))}
                </div>
              </section>
            )}
            {writtenChapter && (
              <div className="mb-6">
                <ChapterWriter chapter={writtenChapter} sessionId={sessionId ?? undefined} />
              </div>
            )}
            <div className="mb-4 flex flex-wrap gap-2">
              <button data-testid="identify-btn" onClick={handleIdentify} disabled={!sessionId || identBusy} className="rounded border border-border px-3 py-1 text-xs hover:bg-panel disabled:opacity-40">
                {identBusy ? t('app.identWorking') : t('app.runIdentify')}
              </button>
              <button data-testid="robust-btn" onClick={handleRobustness} disabled={!sessionId || robustBusy} className="rounded border border-border px-3 py-1 text-xs hover:bg-panel disabled:opacity-40">
                {robustBusy ? t('app.robustWorking') : t('app.runRobust')}
              </button>
            </div>
            {identReport && (
              <pre data-testid="ident-report" className="mb-4 whitespace-pre-wrap rounded border border-border bg-paper p-3 text-xs">{identReport}</pre>
            )}
            {robustReport && (
              <pre data-testid="robust-report" className="mb-4 whitespace-pre-wrap rounded border border-border bg-paper p-3 text-xs">{robustReport}</pre>
            )}
            <Outline body_chapters={bodyChapters} onConfirm={(c) => setBodyChapters(c)} />
            <div className="mt-6">
              <Editor
                chunks={chunks}
                interrupt={interrupt}
                generating={currentStatus === 'running'}
                degraded={degraded}
                degradations={degradations}
                onContinue={async () => {
                  if (!sessionId) return
                  try {
                    const resp = await fetch(
                      `${API_BASE}/sessions/${sessionId}/resume`,
                      {
                        method: 'POST',
                        headers: {
                          'Content-Type': 'application/json',
                          ...authHeaders(),
                        },
                        body: JSON.stringify({ outline: bodyChapters }),
                      },
                    )
                    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
                    setInterrupt(undefined)
                    wsClientRef.current?.close()
                    wsClientRef.current = null
                    const wsUrl = `${WS_BASE}/sessions/${sessionId}/stream`
                    const client = new WSClient(wsUrl, {
                      onChunk: (_chapterId, chunk) => setChunks((prev) => [...prev, chunk]),
                      onStatus: (node, status) => { setCurrentNode(node); setCurrentStatus(status) },
                      onInterrupt: (_chapterId, content) => setInterrupt(content),
                      onError: (message) => setWsError(message),
                      onConnectionChange: (state) => setConnectionState(state),
                    })
                    wsClientRef.current = client
                    client.connect()
                  } catch (err) {
                    showGlobalError(
                      err instanceof Error
                        ? `继续生成失败: ${err.message}`
                        : '继续生成失败，请重试',
                    )
                  }
                }}
                onEditTitle={(title) => {
                  const newTitle = window.prompt('请输入新标题', title)
                  if (newTitle && newTitle !== title) {
                    setBodyChapters((prev) =>
                      prev.map((ch, i) =>
                        i === 0 ? { ...ch, title: newTitle } : ch,
                      ),
                    )
                  }
                }}
              />
            </div>
            {sessionId && review && (
              <div className="mt-6">
                <ReviewPanel sessionId={sessionId} review={review} onDecision={() => refreshReview(sessionId)} />
              </div>
            )}
          </ErrorBoundary>
        }
        agent={
          <ErrorBoundary>
            <AgentPanel currentNode={currentNode} currentStatus={currentStatus} connectionState={connectionState} degraded={degraded} degradations={degradations} />
            {wsError && <div className="mt-2 animate-slide-up rounded border border-red-100 bg-red-50 p-2 text-xs text-red-600">⚠ {wsError}</div>}
          </ErrorBoundary>
        }
      />

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
