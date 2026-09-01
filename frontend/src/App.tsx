import { useState, useCallback } from 'react'
import EdaSidebar from './components/EdaSidebar'
import { ErrorBoundary } from './components/ErrorBoundary'
import ThreeColumn from './components/ThreeColumn'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DeskPage from './pages/DeskPage'
import AgentSpikePage from './pages/AgentSpikePage'
import GuidePage from './pages/GuidePage'
import { BrandMark, LangPills } from './components/UnauthHeader'
import { CsvDropZone } from './components/CsvDropZone'
import PaperPath from './components/PaperPath'
import DirectionForm from './components/DirectionForm'
import InstrumentReadout from './components/InstrumentReadout'
import WriteLoop from './components/WriteLoop'
import ChapterWriter from './components/ChapterWriter'
import ChapterList from './components/ChapterList'
import ReviewPanel from './components/ReviewPanel'
import DocExportDialog from './components/DocExportDialog'
import CodeExportDialog from './components/CodeExportDialog'
import ReviewGateDialog from './components/ReviewGateDialog'
import RunTracePanel from './components/RunTracePanel'
import StepTimeline from './components/StepTimeline'
import { useT } from './lib/i18n'
import { DEV_AUTH_BYPASS, useSession } from './lib/session'
import { useWorkspace, toDirectionInitial } from './lib/workspace'

function App() {
  const { t } = useT()
  const { authed, setAuthed, sessionId, setSessionId } = useSession()
  const ws = useWorkspace({ sessionId, setSessionId, setAuthed, t })

  const [authPage, setAuthPage] = useState<'login' | 'register' | null>(null)

  const spikeRoute =
    window.location.pathname === '/spike' ||
    new URLSearchParams(window.location.search).get('spike') === '1'

  const handleLogin = useCallback(
    (_token: string) => {
      // Identity is the server session cookie; the token argument is a
      // Bearer-era leftover and is ignored.
      setAuthed(true)
      setAuthPage(null)
    },
    [setAuthed],
  )

  if (authPage === 'register') {
    return (
      <RegisterPage
        onRegister={handleLogin}
        onSwitchToLogin={() => setAuthPage('login')}
        onHome={() => setAuthPage(null)}
      />
    )
  }
  if (authPage === 'login') {
    return (
      <LoginPage
        onLogin={handleLogin}
        onSwitchToRegister={() => setAuthPage('register')}
        onHome={() => setAuthPage(null)}
      />
    )
  }

  if (spikeRoute) {
    return <AgentSpikePage />
  }

  const firstScreenInput = (
    <input
      ref={ws.fileInputRef}
      type="file"
      accept=".csv,.dta,.xlsx,.xls"
      data-testid="file-input"
      onChange={ws.handleFileSelect}
      className="hidden"
    />
  )

  if (!sessionId && !ws.seenGuide) {
    return (
      <>
        {firstScreenInput}
        <GuidePage
          uploading={ws.uploading}
          uploadError={ws.uploadError}
          onPickData={() => ws.fileInputRef.current?.click()}
          onFile={(file) => {
            void ws.takeCsv(file)
          }}
          onTrySample={() => {
            void ws.handleTrySample()
          }}
          onWritePaper={() => {
            ws.markGuideSeen()
            ws.setDeskOpen(true)
          }}
          onLogin={authed || DEV_AUTH_BYPASS ? undefined : () => setAuthPage('login')}
          onRegister={authed || DEV_AUTH_BYPASS ? undefined : () => setAuthPage('register')}
          headerExtra={
            authed && !DEV_AUTH_BYPASS ? (
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  data-testid="guide-enter-desk"
                  onClick={() => {
                    ws.markGuideSeen()
                    ws.setDeskOpen(true)
                  }}
                  className="rounded-full bg-ink px-3.5 py-1.5 text-[13px] font-medium text-white transition-opacity hover:opacity-90"
                >
                  {t('guide.enterDesk')}
                </button>
                <button
                  type="button"
                  data-testid="guide-logout"
                  onClick={ws.handleLogout}
                  className="rounded-full border border-black/15 px-3 py-1.5 text-[13px] text-muted transition-colors hover:text-ink"
                >
                  {t('app.logout')}
                </button>
              </div>
            ) : undefined
          }
        />
      </>
    )
  }

  if (ws.deskOpen && !sessionId) {
    return (
      <>
        {firstScreenInput}
        <DeskPage
          authed={authed}
          uploading={ws.uploading}
          uploadError={ws.uploadError}
          onPickData={() => ws.fileInputRef.current?.click()}
          onLogin={DEV_AUTH_BYPASS ? undefined : () => setAuthPage('login')}
          onRegister={DEV_AUTH_BYPASS ? undefined : () => setAuthPage('register')}
          onConfirm={(title) => {
            ws.setShapedQuestion(title)
            ws.setDeskOpen(false)
          }}
        />
      </>
    )
  }

  return (
    <div className="flex h-screen min-h-0 flex-col overflow-x-auto overflow-y-hidden bg-bg text-ink font-sans selection:bg-accent/20">
      {ws.globalError && (
        <div
          data-testid="global-error-toast"
          className="fixed right-4 top-4 z-50 animate-slide-up rounded border border-danger/30 bg-panel px-4 py-2 text-sm text-danger"
        >
          ⚠ {ws.globalError}
        </div>
      )}
      <header className="grid h-[56px] shrink-0 grid-cols-[1fr_auto_1fr] items-center border-b border-border bg-cream px-5">
        <div className="flex items-center gap-3">
          <BrandMark />
        </div>
        <div className="flex items-center rounded-lg bg-bg p-0.5">
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
                ws.setWorkbenchTab(id)
                if (id === 'data' && sessionId) ws.setEdaOpen(true)
              }}
              className={`rounded-md px-3.5 py-1.5 text-[13px] transition-colors duration-200 ${
                ws.workbenchTab === id
                  ? 'bg-accent text-white'
                  : 'text-muted hover:text-ink'
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
          <input
            ref={ws.fileInputRef}
            type="file"
            accept=".csv,.dta,.xlsx,.xls"
            data-testid="file-input"
            onChange={ws.handleFileSelect}
            className="hidden"
          />
          <button
            data-testid="upload-btn"
            onClick={() => ws.fileInputRef.current?.click()}
            disabled={ws.uploading}
            className="inline-flex items-center gap-1.5 rounded-md bg-accent px-3 py-1.5 text-[12px] font-medium text-white transition-colors duration-200 hover:bg-accent/90 disabled:opacity-50"
          >
            {ws.uploading && (
              <svg
                className="h-3 w-3 animate-spin"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth={2.5}
              >
                <circle
                  cx="12"
                  cy="12"
                  r="10"
                  strokeDasharray="31.4 31.4"
                  strokeLinecap="round"
                />
              </svg>
            )}
            {ws.uploading ? t('app.uploading') : t('app.upload')}
          </button>
          <button
            data-testid="export-doc-btn"
            onClick={() => ws.setDocExportOpen(true)}
            disabled={!ws.canExport}
            className="rounded border border-border px-2 py-1 text-xs text-muted transition-colors duration-200 hover:bg-panel hover:text-ink disabled:opacity-40"
          >
            {t('app.exportDoc')}
          </button>
          <button
            data-testid="export-code-btn"
            onClick={() => ws.setCodeExportOpen(true)}
            disabled={!ws.canExport}
            className="rounded border border-border px-2 py-1 text-xs text-muted transition-colors duration-200 hover:bg-panel hover:text-ink disabled:opacity-40"
          >
            {t('app.exportCode')}
          </button>
          {ws.uploadError && (
            <span
              data-testid="upload-error"
              className="rounded bg-panel px-2 py-0.5 text-xs text-danger"
            >
              {ws.uploadError}
            </span>
          )}
          {!sessionId && (
            <button
              type="button"
              data-testid="open-guide-btn"
              onClick={() => {
                localStorage.removeItem('econpaper_seen_guide')
                ws.setSeenGuide(false)
              }}
              className="rounded border border-border px-2 py-1 text-xs text-muted transition-colors duration-200 hover:bg-panel hover:text-ink"
            >
              {t('guide.nowAgain')}
            </button>
          )}
          {!DEV_AUTH_BYPASS &&
            (authed ? (
              <button
                onClick={ws.handleLogout}
                className="rounded border border-border px-2 py-1 text-xs text-muted transition-colors duration-200 hover:bg-panel hover:text-ink"
              >
                {t('app.logout')}
              </button>
            ) : (
              <button
                data-testid="open-login-btn"
                onClick={() => setAuthPage('login')}
                className="text-xs text-muted transition-colors duration-200 hover:text-ink"
              >
                {t('app.login')}
              </button>
            ))}
          <LangPills />
        </div>
      </header>

      <ThreeColumn
        outline={
          <ErrorBoundary>
            <h2 className="mb-4 font-mono text-[11px] uppercase tracking-[0.16em] text-muted">
              {t('bench.chapters')}
            </h2>
            {ws.outline.length > 0 && !ws.identFailed ? (
              <div data-testid="chapter-write-dock">
                <p className="mb-2 text-xs leading-6 text-muted">{t('bench.pickChapter')}</p>
                <ChapterList
                  body_chapters={ws.railItems}
                  currentIndex={ws.currentChapterIndex}
                  onSelectChapter={ws.handleSelectChapter}
                />
                {ws.outline.map((ch) => (
                  <button
                    key={ch.type}
                    type="button"
                    data-testid={`write-chapter-${ch.type}`}
                    className="sr-only"
                    disabled={ws.writeBusy}
                    aria-label={`${t('bench.writeChapter')} ${ch.type}`}
                    onClick={() => {
                      const idx = ws.outline.findIndex((item) => item.type === ch.type)
                      ws.handleSelectChapter(idx)
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
                    ws.setWorkbenchTab('data')
                    ws.setEdaOpen(true)
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
              {ws.workbenchTab === 'data' && (
                <section className="mb-6">
                  <h2 className="mb-4 font-serif text-[1.35rem] text-ink">
                    {t('workbench.dataTitle')}
                  </h2>
                  <CsvDropZone
                    uploading={ws.uploading}
                    onBrowse={() => ws.fileInputRef.current?.click()}
                    onFile={(file) => {
                      void ws.takeCsv(file)
                    }}
                  />
                  {sessionId && ws.edaOpen ? (
                    <div className="mt-4">
                      <EdaSidebar
                        sessionId={sessionId}
                        onClose={() => ws.setEdaOpen(false)}
                      />
                    </div>
                  ) : (
                    <p className="mt-4 text-sm text-muted">{t('workbench.dataEmpty')}</p>
                  )}
                </section>
              )}
              {ws.workbenchTab === 'format' && (
                <section
                  data-testid="format-pane"
                  className="mb-8 rounded-lg border border-border bg-panel p-6"
                >
                  <h2 className="font-serif text-lg text-ink">{t('workbench.formatTitle')}</h2>
                  <p className="mt-2 text-sm leading-6 text-muted">
                    {t('workbench.formatBody')}
                  </p>
                  <div className="mt-5 flex flex-wrap gap-2">
                    <button
                      type="button"
                      data-testid="format-export-doc-btn"
                      onClick={() => ws.setDocExportOpen(true)}
                      title={!sessionId || !ws.canExport ? t('app.exportLockedHint') : undefined}
                      disabled={!sessionId || !ws.canExport}
                      className="rounded border border-border px-3 py-1.5 text-xs text-ink transition-colors duration-200 hover:bg-cream disabled:opacity-40"
                    >
                      {t('app.exportDoc')}
                    </button>
                    <button
                      type="button"
                      data-testid="format-export-code-btn"
                      onClick={() => ws.setCodeExportOpen(true)}
                      title={!sessionId || !ws.canExport ? t('app.exportLockedHint') : undefined}
                      disabled={!sessionId || !ws.canExport}
                      className="rounded border border-border px-3 py-1.5 text-xs text-ink transition-colors duration-200 hover:bg-cream disabled:opacity-40"
                    >
                      {t('app.exportCode')}
                    </button>
                  </div>
                </section>
              )}
              {ws.degraded && (
                <div
                  data-testid="degradation-banner"
                  className="mb-2 animate-slide-up rounded border border-warning/30 bg-panel px-3 py-1.5 text-xs text-warning"
                >
                  {t('app.degradedBanner')}
                </div>
              )}
              {!ws.hasReadout && (
                <p data-testid="now-hint" className="mb-6 font-serif text-[15px] leading-7 text-ink">
                  {t('guide.nowDirection')}
                </p>
              )}
              {ws.hasReadout && !ws.writtenChapter?.content && !ws.writeBusy && (
                <p data-testid="now-hint" className="mb-6 font-serif text-[15px] leading-7 text-ink">
                  {t('guide.nowWrite')}
                </p>
              )}
              {ws.hasReadout && Boolean(ws.writtenChapter?.content) &&
                (() => {
                  const writtenTypes = new Set(
                    ws.writtenChapters.filter((c) => c.content).map((c) => c.type),
                  )
                  const pending = ws.outline.find((ch) => !writtenTypes.has(ch.type))
                  if (pending) {
                    return (
                      <p
                        data-testid="now-hint"
                        className="mb-6 font-serif text-[15px] leading-7 text-ink"
                      >
                        {t('guide.nowProgress')
                          .replace('{done}', String(writtenTypes.size))
                          .replace('{total}', String(ws.outline.length))
                          .replace('{title}', pending.title)}
                      </p>
                    )
                  }
                  return (
                    <p
                      data-testid="now-hint"
                      className="mb-6 font-serif text-[15px] leading-7 text-ink"
                    >
                      {t('guide.nowExport')}
                    </p>
                  )
                })()}
              <StepTimeline
                sessionId={sessionId}
                directionSummary={ws.directionSummary}
                cleaningReport={ws.cleaningReport}
                estimate={ws.estimateMeta}
                estimateBusy={ws.directionBusy}
                hasReadout={ws.hasReadout}
                identFailed={ws.identFailed}
                outline={ws.outline}
                currentChapterIndex={ws.currentChapterIndex}
                writtenChapters={ws.writtenChapters}
                writeBusy={ws.writeBusy}
              />
              <WriteLoop
                fileName={ws.csvName}
                rows={ws.csvRows}
                cols={ws.csvCols ?? (ws.dataColumns.length || null)}
                direction={ws.directionRecord}
                outline={ws.outline}
                outlineLocked={ws.outlineLocked}
                hasDirection={Boolean(ws.directionSummary)}
                hasOutline={ws.outline.length > 0 && !ws.identFailed}
                hasChapter={Boolean(ws.writtenChapter?.content)}
                isResultsPart={ws.outline[ws.currentChapterIndex]?.type === 'results'}
                partIndex={ws.currentChapterIndex + 1}
                agentPct={
                  ws.writeBusy ? 10 : ws.directionBusy || ws.uploading ? 0 : null
                }
                writeBusy={ws.writeBusy}
                onAddMore={() => ws.setDirectionOpen(true)}
                onGoPart1={() => ws.setWorkbenchTab('paper')}
                onApplyGenerate={ws.handleApplyGenerate}
                onReviseOutline={() => ws.setDirectionOpen(true)}
                onApproveOutline={ws.handleApproveOutline}
                onRefine={ws.handleRefine}
              />
              <section
                data-testid="direction-section"
                className="mb-8 rounded-lg border border-border bg-panel p-6"
              >
                <div className="mb-3 flex items-center justify-between gap-3">
                  <h2 className="font-serif text-[1.15rem] text-ink">
                    {t('app.directionTitle')}
                  </h2>
                  {!ws.directionOpen && ws.directionSummary ? (
                    <button
                      type="button"
                      data-testid="edit-direction-btn"
                      onClick={() => ws.setDirectionOpen(true)}
                      className="text-xs text-accent"
                    >
                      {t('bench.editDirection')}
                    </button>
                  ) : null}
                </div>
                {ws.directionOpen ? (
                  <DirectionForm
                    onSubmit={ws.handleDirectionSubmit}
                    initialQuestion={ws.shapedQuestion}
                    initial={
                      toDirectionInitial(ws.directionRecord) ??
                      ws.sampleDirection ??
                      (ws.shapedQuestion ? { question: ws.shapedQuestion } : undefined)
                    }
                    columns={ws.dataColumns}
                  />
                ) : (
                  <p data-testid="direction-summary" className="text-sm text-ink">
                    {ws.directionSummary || t('bench.directionSettled')}
                  </p>
                )}
                {ws.directionBusy && (
                  <p className="mt-2 text-xs text-muted">{t('app.directionWorking')}</p>
                )}
              </section>
              {ws.hasReadout && (
                <InstrumentReadout
                  claim={ws.claim}
                  starRating={ws.starRating}
                  treatmentRow={ws.treatmentRow}
                  results={ws.mainResults}
                  literatureSource={ws.literatureSource}
                  robustnessStatus={ws.robustnessStatus}
                  writeBlockers={ws.writeBlockers}
                  identificationFailed={ws.identFailed}
                  question={ws.shapedQuestion || null}
                />
              )}
              {ws.identReport && (
                <details className="mb-4 rounded border border-border bg-paper px-3 py-2">
                  <summary className="cursor-pointer font-mono text-xs text-muted">
                    识别说明
                  </summary>
                  <pre
                    data-testid="ident-report"
                    className="mt-2 whitespace-pre-wrap text-xs"
                  >
                    {ws.identReport}
                  </pre>
                </details>
              )}
              {ws.writeBusy ? (
                <p
                  data-testid="chapter-writing"
                  className="font-serif text-sm leading-7 text-muted"
                >
                  {t('bench.writing').replace(
                    '{title}',
                    ws.outline.find((ch) => ch.type === ws.writingType)?.title ||
                      ws.writingType ||
                      '',
                  )}
                </p>
              ) : ws.writtenChapter?.content ? (
                <div className="mb-6">
                  <ChapterWriter
                    key={`${ws.writtenChapter.type}:${ws.writtenChapter.chapter_index ?? ws.currentChapterIndex}`}
                    chapter={ws.writtenChapter}
                    sessionId={sessionId ?? undefined}
                    chapterIndex={
                      ws.writtenChapter.chapter_index ?? ws.currentChapterIndex
                    }
                    versions={ws.writtenChapter.versions}
                    onApprove={ws.handleApprove}
                    onSaveEdit={ws.handleSaveEdit}
                  />
                </div>
              ) : (
                <p className="font-serif text-[15px] leading-[1.8] text-muted">
                  {t('bench.paperEmpty')}
                </p>
              )}
            </div>
          </ErrorBoundary>
        }
        agent={
          <ErrorBoundary>
            <PaperPath
              uploading={ws.uploading}
              hasSession={Boolean(sessionId)}
              hasDirection={Boolean(ws.directionSummary)}
              directionOpen={ws.directionOpen}
              hasReadout={ws.hasReadout}
              hasOutline={ws.outline.length > 0}
              writing={ws.writeBusy}
              hasChapter={Boolean(ws.writtenChapter?.content)}
              awaitingApprove={ws.writtenChapter?.status === 'generated'}
              canExport={ws.canExport}
              hasExported={ws.hasExported}
              onSelect={(id) => {
                if (id === 'upload_data' || id === 'clean_data') {
                  ws.setWorkbenchTab('data')
                  if (sessionId) ws.setEdaOpen(true)
                } else if (id === 'translate_code') {
                  ws.setWorkbenchTab('format')
                  if (sessionId) ws.setCodeExportOpen(true)
                } else if (id === 'export_docx') {
                  ws.setWorkbenchTab('format')
                  if (sessionId) ws.setDocExportOpen(true)
                } else {
                  ws.setWorkbenchTab('paper')
                }
              }}
            />
            {sessionId && ws.review ? (
              <div className="mt-4">
                <ReviewPanel
                  sessionId={sessionId}
                  review={ws.review}
                  onDecision={() => ws.refreshReview(sessionId)}
                />
              </div>
            ) : (
              <p
                data-testid="review-idle"
                className="mt-4 text-xs leading-6 text-muted"
              >
                {ws.hasReadout
                  ? t('bench.reviewAfterWrite')
                  : t('bench.reviewAfterDirection')}
              </p>
            )}
            {ws.degradations.length > 0 && (
              <p className="mt-4 text-[11px] leading-5 text-muted">
                {ws.degradations[0].node}: {ws.degradations[0].reason}
              </p>
            )}
            {sessionId && <RunTracePanel sessionId={sessionId} />}
          </ErrorBoundary>
        }
      />

      {ws.gateInfo && (
        <ReviewGateDialog
          score={ws.gateInfo.score}
          threshold={ws.gateInfo.threshold}
          feedback={
            ws.review && ws.review.chapter_index === ws.gateInfo.chapter.chapter_index
              ? ws.review.feedback || ''
              : ''
          }
          busy={ws.gateBusy}
          onRegenerate={ws.handleGateRegenerate}
          onForce={ws.handleGateForce}
          onClose={() => ws.setGateInfo(null)}
        />
      )}
      {ws.docExportOpen && sessionId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink/40">
          <DocExportDialog
            sessionId={sessionId}
            onClose={() => ws.setDocExportOpen(false)}
            onExport={ws.handleDocExport}
          />
        </div>
      )}
      <CodeExportDialog
        sessionId={sessionId ?? ''}
        isOpen={ws.codeExportOpen && !!sessionId}
        onClose={() => ws.setCodeExportOpen(false)}
      />
    </div>
  )
}

export default App
