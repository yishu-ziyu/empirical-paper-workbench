import { useState, useCallback, useEffect, useRef } from 'react'
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
import DirectionForm from './components/DirectionForm'
import InstrumentReadout from './components/InstrumentReadout'
import WriteLoop from './components/WriteLoop'
import ChapterWriter from './components/ChapterWriter'
import ChapterList from './components/ChapterList'
import DocExportDialog from './components/DocExportDialog'
import CodeExportDialog from './components/CodeExportDialog'
import ReviewGateDialog from './components/ReviewGateDialog'
import StepTimeline from './components/StepTimeline'
import WorkspaceDecisionRail, {
  type WorkspaceDecision,
  type WorkspaceSuggestion,
} from './components/WorkspaceDecisionRail'
import SubmissionStatus from './components/SubmissionStatus'
import ReadingFocus from './components/ReadingFocus'
import ResearchComputer from './components/ResearchComputer'
import type { ResizableWorkspaceHandle } from './components/ResizableWorkspace'
import { useT } from './lib/i18n'
import { DEV_AUTH_BYPASS, useSession } from './lib/session'
import { useWorkspace, toDirectionInitial } from './lib/workspace'

function App() {
  const { t } = useT()
  const { authed, setAuthed, sessionId, setSessionId } = useSession()
  const ws = useWorkspace({ sessionId, setSessionId, setAuthed, t })

  const [authPage, setAuthPage] = useState<'login' | 'register' | null>(null)
  const workspaceRef = useRef<ResizableWorkspaceHandle>(null)
  const evidenceRef = useRef<HTMLDetailsElement>(null)
  const [evidenceOpen, setEvidenceOpen] = useState(false)

  const spikeRoute =
    window.location.pathname === '/spike' ||
    new URLSearchParams(window.location.search).get('spike') === '1'

  const openDirection = () => {
    ws.setWorkbenchTab('paper')
    ws.setDirectionOpen(true)
  }

  const openEvidence = () => {
    ws.setWorkbenchTab('paper')
    setEvidenceOpen(true)
    workspaceRef.current?.expandRight()
  }

  useEffect(() => {
    if (!evidenceOpen) return
    const frame = window.requestAnimationFrame(() => {
      evidenceRef.current?.scrollIntoView?.({ behavior: 'smooth', block: 'start' })
    })
    return () => window.cancelAnimationFrame(frame)
  }, [evidenceOpen])

  const pendingChapter = ws.writtenChapters.find(
    (chapter) => Boolean(chapter.content) && chapter.status !== 'approved',
  )

  // 只选择一件最先需要作者处理的事，其他提示留在可展开建议中。
  let blockingDecision: WorkspaceDecision | null = null
  if (ws.identFailed) {
    blockingDecision = {
      title: '研究设计需要重开',
      reason: ws.identReport || '识别未通过，先改研究设计再写正文。',
      actionLabel: '修改研究设计',
      onAction: openDirection,
    }
  } else if (ws.writeBlockers.length > 0) {
    blockingDecision = {
      title: '写作暂时被阻塞',
      reason: ws.writeBlockers[0],
      actionLabel: '查看论文工作区',
      onAction: () => ws.setWorkbenchTab('paper'),
    }
  } else if (ws.directionOpen && !ws.directionBusy && !ws.directionDisabledReason) {
    blockingDecision = {
      title: ws.directionSummary ? '确认修改后的研究方向' : '确认研究方向',
      reason: ws.directionSummary
        ? '研究方向正在修改；提交这次修改后，系统才会按新设计继续。'
        : '需要你确认研究问题、变量和方法；确认后系统才会运行估计。',
      actionLabel: '打开研究方向',
      onAction: openDirection,
    }
  } else if (ws.outline.length > 0 && !ws.outlineLocked && !ws.writeBusy && !ws.writtenChapter?.content) {
    blockingDecision = {
      title: '确认论文大纲',
      reason: '大纲已形成，等待你确认章节结构后开始写作。',
      actionLabel: '查看大纲',
      onAction: () => ws.setWorkbenchTab('paper'),
    }
  } else if (pendingChapter) {
    blockingDecision = {
      title: '确认当前章节',
      reason: `“${pendingChapter.title || pendingChapter.type}”已生成，等待你批准、修改或打回重写。`,
      actionLabel: '查看章节',
      onAction: () => {
        const index = ws.outline.findIndex((chapter) => chapter.type === pendingChapter.type)
        if (index >= 0) ws.handleSelectChapter(index)
        ws.setWorkbenchTab('paper')
      },
    }
  }

  const waitingMessage = ws.directionBusy
    ? '等待估计与识别结果；结果回来后再决定下一步。'
    : ws.writeBusy
      ? '章节正在生成；完成后会停下来请你确认。'
      : ws.directionSummary && !ws.hasReadout
        ? '方向已提交，等待主结果返回。'
        : null

  const writtenTypes = new Set(
    ws.writtenChapters.filter((chapter) => Boolean(chapter.content)).map((chapter) => chapter.type),
  )
  const incompleteChapterCount = ws.outline.filter((chapter) => !writtenTypes.has(chapter.type)).length
  const pendingApprovalCount = ws.writtenChapters.filter(
    (chapter) => Boolean(chapter.content) && chapter.status !== 'approved',
  ).length
  const hasSuccessfulEstimate = Boolean(
    !ws.identFailed &&
      (ws.estimateMeta?.status === 'ok' || ws.treatmentRow || ws.mainResults),
  )
  const submissionBlockers = Array.from(
    new Set(
      [
        !sessionId ? '尚未建立研究会话' : null,
        !ws.directionSummary ? '研究方向尚未提交' : null,
        ws.directionOpen ? '研究方向仍在修改' : null,
        ws.directionBusy ? '研究方向仍在运行' : null,
        !hasSuccessfulEstimate ? '尚未形成可用主结果' : null,
        ws.identFailed ? '识别诊断未通过，需要重开研究设计' : null,
        ws.outline.length === 0 ? '论文大纲尚未形成' : null,
        ws.outline.length > 0 && !ws.outlineLocked ? '论文大纲尚未确认' : null,
        ws.writeBusy ? '章节仍在生成' : null,
        !ws.canExport ? '尚未写出可提交的章节' : null,
        incompleteChapterCount > 0
          ? `还有 ${incompleteChapterCount} 个章节尚未形成正文`
          : null,
        pendingApprovalCount > 0 ? `还有 ${pendingApprovalCount} 个章节待你确认` : null,
        ...ws.writeBlockers,
      ].filter((item): item is string => Boolean(item)),
    ),
  )
  const submissionReady = ws.canExport && submissionBlockers.length === 0
  const submissionPassed = [
    sessionId ? '研究会话已建立' : null,
    ws.directionSummary ? '研究方向已提交' : null,
    ws.directionSummary && !ws.directionOpen && !ws.directionBusy ? '研究方向已确认' : null,
    hasSuccessfulEstimate ? '可用主结果已记录' : null,
    ws.outline.length > 0 ? '论文大纲已形成' : null,
    ws.outline.length > 0 && ws.outlineLocked ? '论文大纲已确认' : null,
    ws.canExport && incompleteChapterCount === 0 ? '所有大纲章节已有正文' : null,
    ws.canExport && pendingApprovalCount === 0 ? '所有章节已确认' : null,
  ].filter((item): item is string => Boolean(item))

  const decisionSuggestions: WorkspaceSuggestion[] = []
  if (ws.hasReadout) {
    decisionSuggestions.push({
      title: '查看证据解释',
      detail: '识别说明、稳健性和运行摘要不会打断论文正文。',
      actionLabel: '打开 Research Computer',
      onAction: openEvidence,
    })
  }
  if (ws.degradations.length > 0) {
    decisionSuggestions.push({
      title: '有降级记录可查看',
      detail: `${ws.degradations[0].node}: ${ws.degradations[0].reason}`,
      actionLabel: '查看运行记录',
      onAction: openEvidence,
    })
  }

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
  const uploadLiveRegion = (
    <p
      role="status"
      aria-live="polite"
      aria-label={t('app.uploadStatusLabel')}
      data-testid="upload-live-status"
      className="sr-only"
    >
      {ws.uploadStatus || ''}
    </p>
  )

  // 空桌直入：GuidePage 只在显式请求（openGuide）时出现，且不拦在无会话工作台前。
  if (ws.showGuide && !sessionId) {
    return (
      <>
        {firstScreenInput}
        {uploadLiveRegion}
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
          onWritePaper={(idea) => {
            if (idea?.trim()) sessionStorage.setItem('desk_idea_draft', idea.trim())
            ws.closeGuide()
            ws.setDeskOpen(true)
          }}
          onLogin={authed || DEV_AUTH_BYPASS ? undefined : () => setAuthPage('login')}
          onRegister={authed || DEV_AUTH_BYPASS ? undefined : () => setAuthPage('register')}
          headerExtra={
            <>
              {/* 从落地页始终有可见途径回到来处（空桌或工作台），不改动 deskOpen 状态 */}
              <button
                type="button"
                data-testid="guide-back-desk"
                onClick={ws.closeGuide}
                className="rounded-full border border-black/15 px-3 py-1.5 text-[13px] text-muted transition-colors hover:text-ink"
              >
                {t('guide.backToDesk')}
              </button>
              {authed && !DEV_AUTH_BYPASS ? (
                <>
                  <button
                    type="button"
                    data-testid="guide-enter-desk"
                    onClick={() => {
                      ws.closeGuide()
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
                </>
              ) : undefined}
            </>
          }
        />
      </>
    )
  }

  if (ws.deskOpen && !sessionId) {
    return (
      <>
        {firstScreenInput}
        {uploadLiveRegion}
        <DeskPage
          authed={authed}
          uploading={ws.uploading}
          uploadError={ws.uploadError}
          onPickData={() => ws.fileInputRef.current?.click()}
          onOpenGuide={() => ws.openGuide()}
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
      {uploadLiveRegion}
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
          {ws.uploadNeedsReselect && sessionId ? (
            <button
              type="button"
              data-testid="upload-reselect-btn"
              onClick={() => ws.fileInputRef.current?.click()}
              className="rounded border border-border px-2 py-1 text-xs text-accent transition-colors hover:bg-panel"
            >
              {t('app.uploadReselect')}
            </button>
          ) : null}
          {!sessionId && (
            <button
              type="button"
              data-testid="open-guide-btn"
              onClick={() => ws.openGuide()}
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
        ref={workspaceRef}
        outline={
          <ErrorBoundary>
            <WorkspaceDecisionRail
              decision={blockingDecision}
              waiting={waitingMessage}
              suggestions={decisionSuggestions}
            >
              <section data-testid="paper-navigation" className="border-t border-border pt-4">
                <h2 className="mb-3 font-mono text-[11px] uppercase tracking-[0.16em] text-muted">
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
              </section>
            </WorkspaceDecisionRail>
          </ErrorBoundary>
        }
        editor={
          <ErrorBoundary>
            <div
              data-testid="paper-surface"
              aria-label="持续形成的论文"
              className="mx-auto max-w-[46rem] px-6 py-10 sm:px-10"
            >
              <SubmissionStatus
                canExport={submissionReady}
                blockers={submissionBlockers}
                passed={submissionPassed}
                onGenerate={() => ws.setDocExportOpen(true)}
              />
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
                      disabled={Boolean(ws.directionDisabledReason)}
                      title={ws.directionDisabledReason || undefined}
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
                    disabled={Boolean(ws.directionDisabledReason)}
                    disabledReason={ws.directionDisabledReason}
                  />
                ) : (
                  <p data-testid="direction-summary" className="text-sm text-ink">
                    {ws.directionSummary || t('bench.directionSettled')}
                  </p>
                )}
                {ws.directionBusy && (
                  <p role="status" aria-live="polite" className="mt-2 text-xs text-muted">
                    {t('app.directionWorking')}
                  </p>
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
              {ws.hasReadout && (
                <section data-testid="evidence-entry" className="mb-6 rounded-lg border border-border bg-panel px-4 py-3">
                  <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                      <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-muted">结论入口</p>
                      <p data-testid="evidence-conclusion" className="mt-1 text-sm leading-6 text-ink">
                        {ws.identFailed
                          ? '识别未通过，当前不能把结果读成可靠结论。'
                          : ws.claim
                            ? `当前主张：${ws.claim}`
                            : '主结果已记录。'}
                      </p>
                    </div>
                    <button
                      type="button"
                      data-testid="evidence-why"
                      onClick={openEvidence}
                      className="rounded-full border border-border px-3 py-1.5 text-xs text-ink transition-colors hover:bg-cream"
                    >
                      为什么？看证据
                    </button>
                  </div>
                </section>
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
            <ResearchComputer
              paperPath={{
                uploading: ws.uploading,
                hasSession: Boolean(sessionId),
                hasDirection: Boolean(ws.directionSummary),
                directionOpen: ws.directionOpen,
                hasReadout: ws.hasReadout,
                hasOutline: ws.outline.length > 0,
                writing: ws.writeBusy,
                hasChapter: Boolean(ws.writtenChapter?.content),
                awaitingApprove: ws.writtenChapter?.status === 'generated',
                canExport: ws.canExport,
                hasExported: ws.hasExported,
                cleaningSteps: Array.isArray(ws.cleaningReport?.steps)
                  ? ws.cleaningReport.steps
                  : undefined,
              }}
              onSelectPath={(id) => {
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
              sessionId={sessionId}
              review={ws.review}
              onDecision={() => {
                if (sessionId) void ws.refreshReview(sessionId)
              }}
              degradations={ws.degradations}
              csvName={ws.csvName}
              csvRows={ws.csvRows}
              csvCols={ws.csvCols}
              directionSummary={ws.directionSummary}
              directionMethod={ws.directionRecord?.method}
              directionDv={ws.directionRecord?.dv}
              directionIv={ws.directionRecord?.iv}
              hasReadout={ws.hasReadout}
              hasSuccessfulEstimate={hasSuccessfulEstimate}
              identFailed={ws.identFailed}
              identReport={ws.identReport}
              robustnessStatus={ws.robustnessStatus}
              estimate={ws.estimateMeta}
              evidenceOpen={evidenceOpen}
              evidenceRef={evidenceRef}
              onEvidenceOpenChange={setEvidenceOpen}
            />
          </ErrorBoundary>
        }
      />

      <ReadingFocus
        enabled={Boolean(sessionId) && ws.workbenchTab === 'paper'}
        workspaceRef={workspaceRef}
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
