import { useState, useEffect, useRef, useCallback } from 'react'
import { WSClient } from './lib/ws'
import type { WSStatus } from './lib/ws'
import EdaSidebar from './components/EdaSidebar'
import Outline from './components/Outline'
import type { OutlineChapter } from './components/Outline'
import Editor from './components/Editor'
import AgentPanel from './components/AgentPanel'
import StepIndicator from './components/StepIndicator'
import { ErrorBoundary } from './components/ErrorBoundary'
import ThreeColumn from './components/ThreeColumn'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import { useT } from './lib/i18n'

const LS_KEY = 'econpaper_session_id'
const LS_TOKEN_KEY = 'econpaper_access_token'
const API_BASE = 'http://localhost:8000'
const WS_BASE = 'ws://localhost:8000'

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

function App() {
  const { t, lang, setLang } = useT()

  const [authToken, setAuthToken] = useState<string | null>(() => localStorage.getItem(LS_TOKEN_KEY))
  const [authPage, setAuthPage] = useState<'login' | 'register'>('login')
  const isAuthenticated = authToken !== null

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
    if (sessionId) localStorage.setItem(LS_KEY, sessionId)
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

  if (!isAuthenticated) {
    if (authPage === 'register') {
      return <RegisterPage onRegister={handleLogin} onSwitchToLogin={() => setAuthPage('login')} />
    }
    return <LoginPage onLogin={handleLogin} onSwitchToRegister={() => setAuthPage('register')} />
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
        <StepIndicator sessionId={sessionId} currentStatus={currentStatus} />
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
          {uploadError && <span data-testid="upload-error" className="rounded bg-red-50 px-2 py-0.5 text-xs text-red-600">{uploadError}</span>}
          <button onClick={handleLogout} className="rounded border border-border px-2 py-1 text-xs text-muted transition-colors duration-200 hover:bg-panel hover:text-ink">{t('app.logout')}</button>
          <button onClick={() => setLang(lang === 'zh' ? 'en' : 'zh')} className="rounded border border-border px-2 py-1 text-xs text-muted transition-colors duration-200 hover:bg-panel hover:text-ink">{t('app.langSwitch')}</button>
          <button type="button" onClick={() => setRightOpen((v) => !v)} className="text-muted hover:text-ink transition-colors duration-200 lg:hidden" aria-label={t('app.toggleRight')}>
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
            </svg>
          </button>
        </div>
      </header>

      {!sessionId ? (
        <main className="flex flex-1 items-center justify-center bg-bg p-6">
          <div data-testid="welcome-card" className="mx-auto max-w-md animate-fade-in text-center">
            <div className="mb-2 inline-flex items-center gap-2 rounded-full bg-accent/10 px-4 py-1.5">
              <span className="text-xs font-semibold tracking-wider text-accent uppercase">{t('app.welcomeBadge')}</span>
            </div>
            <h1 className="mt-4 text-3xl font-bold tracking-tight font-serif text-ink">{t('app.title')}</h1>
            <p className="mt-2 text-sm leading-relaxed text-muted">{t('app.welcomeDesc')}</p>
            <div className="mt-10 space-y-3 text-left">
              <div className="flex items-start gap-4 rounded-lg border border-border bg-panel p-4 transition-colors hover:border-accent/30">
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-accent text-sm font-medium text-white">1</span>
                <div>
                  <p className="text-sm font-medium text-ink">{t('app.step1Title')}</p>
                  <p className="mt-0.5 text-xs text-muted">{t('app.step1Desc')}</p>
                </div>
              </div>
              <div className="flex items-start gap-4 rounded-lg border border-border bg-panel p-4 transition-colors hover:border-accent/30">
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-accent/30 text-sm font-medium text-ink">2</span>
                <div>
                  <p className="text-sm font-medium text-ink">{t('app.step2Title')}</p>
                  <p className="mt-0.5 text-xs text-muted">{t('app.step2Desc')}</p>
                </div>
              </div>
              <div className="flex items-start gap-4 rounded-lg border border-border bg-panel p-4 transition-colors hover:border-accent/30">
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-accent/30 text-sm font-medium text-ink">3</span>
                <div>
                  <p className="text-sm font-medium text-ink">{t('app.step3Title')}</p>
                  <p className="mt-0.5 text-xs text-muted">{t('app.step3Desc')}</p>
                </div>
              </div>
            </div>
            <button data-testid="welcome-upload-btn" onClick={() => fileInputRef.current?.click()} disabled={uploading} className="mt-8 inline-flex items-center gap-2 rounded-lg bg-accent px-8 py-2.5 text-sm font-medium text-white shadow-sm transition-colors duration-200 hover:bg-accent/90 disabled:opacity-50">
              {uploading && (
                <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5}>
                  <circle cx="12" cy="12" r="10" strokeDasharray="31.4 31.4" strokeLinecap="round" />
                </svg>
              )}
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
              </svg>
              {uploading ? t('app.welcomeUploading') : t('app.welcomeUploadBtn')}
            </button>
            <p className="mt-4 text-xs text-muted/60">{t('app.welcomeHint')}</p>
          </div>
        </main>
      ) : (
        <ThreeColumn
          leftOpen={leftOpen}
          rightOpen={rightOpen}
          outline={
            <ErrorBoundary>
              <h2 className="mb-3 text-xs uppercase tracking-wider text-muted font-mono">{t('app.outline')}</h2>
              {edaOpen && sessionId ? (
                <EdaSidebar sessionId={sessionId} onClose={() => setEdaOpen(false)} />
              ) : (
                <button onClick={() => setEdaOpen(true)} className="text-sm text-accent transition-colors duration-200 hover:text-accent/80">{t('app.openEda')}</button>
              )}
            </ErrorBoundary>
          }
          editor={
            <ErrorBoundary>
              {degraded && <div data-testid="degradation-banner" className="mb-2 animate-slide-up rounded border border-yellow-200 bg-yellow-50 px-3 py-1.5 text-xs text-yellow-700">{t('app.degradedBanner')}</div>}
              <Outline body_chapters={bodyChapters} onConfirm={(c) => setBodyChapters(c)} />
              <div className="mt-6">
                <Editor chunks={chunks} interrupt={interrupt} generating={currentStatus === 'running'} degraded={degraded} degradations={degradations} />
              </div>
            </ErrorBoundary>
          }
          agent={
            <ErrorBoundary>
              <AgentPanel currentNode={currentNode} currentStatus={currentStatus} connectionState={connectionState} degraded={degraded} degradations={degradations} />
              {wsError && <div className="mt-2 animate-slide-up rounded border border-red-100 bg-red-50 p-2 text-xs text-red-600">⚠ {wsError}</div>}
            </ErrorBoundary>
          }
        />
      )}
    </div>
  )
}

export default App
