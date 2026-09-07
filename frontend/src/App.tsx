import { useState, useCallback, useEffect, useRef } from 'react'
import { ErrorBoundary } from './components/ErrorBoundary'
import ThreeColumn from './components/ThreeColumn'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DeskPage from './pages/DeskPage'
import AgentSpikePage from './pages/AgentSpikePage'
import GuidePage from './pages/GuidePage'
import { LangPills } from './components/UnauthHeader'
import DocExportDialog from './components/DocExportDialog'
import CodeExportDialog from './components/CodeExportDialog'
import ReviewGateDialog from './components/ReviewGateDialog'
import WorkbenchSidebar, {
  type WorkbenchViewId,
  type SidebarItem,
} from './components/WorkbenchSidebar'
import AgentRail from './components/AgentRail'
import AgentCursorRoot from './components/AgentCursorLayer'
import type { WorkspaceDecision, WorkspaceSuggestion } from './components/WorkspaceDecisionRail'
import ReadingFocus from './components/ReadingFocus'
import type { ResizableWorkspaceHandle } from './components/ResizableWorkspace'
import { useT } from './lib/i18n'
import { DEV_AUTH_BYPASS, useSession } from './lib/session'
import {
  hasConfirmedResearchQuestion,
  researchQuestionPrompt,
  useWorkspace,
} from './lib/workspace'
import { formatStatValue } from './lib/readoutTable'
import { displaySurpriseObserved } from './lib/i18nPresentation'
import WorkbenchArtifact from './components/WorkbenchArtifact'

function App() {
  const { t, lang } = useT()
  const viewLabel: Record<WorkbenchViewId, string> = {
    overview: t('nav.overview'),
    question: t('nav.question'),
    data: t('nav.data'),
    design: t('nav.design'),
    evidence: t('nav.evidence'),
    literature: t('nav.literature'),
    paper: t('nav.paper'),
  }
  const { authed, setAuthed, sessionId, setSessionId } = useSession()
  const ws = useWorkspace({ sessionId, setSessionId, setAuthed, t })

  const [authPage, setAuthPage] = useState<'login' | 'register' | null>(null)
  const workspaceRef = useRef<ResizableWorkspaceHandle>(null)

  const spikeRoute =
    window.location.pathname === '/spike' ||
    new URLSearchParams(window.location.search).get('spike') === '1'

  const openDirection = () => {
    ws.setWorkbenchTab('question')
    ws.setDirectionOpen(true)
  }
  const openEvidence = () => {
    ws.setWorkbenchTab('evidence')
    workspaceRef.current?.expandRight()
  }

  // 方向一确认，中栏回到论文工作区（写作流）；刷新恢复的落地在
  // workspace.ts 里决定（有研究内容时直接落 Overview）。
  useEffect(() => {
    if (ws.directionSummary && ws.workbenchTab === 'question') {
      ws.setWorkbenchTab('paper')
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ws.directionSummary])

  const pendingChapter = ws.writtenChapters.find(
    (chapter) => Boolean(chapter.content) && chapter.status !== 'approved',
  )

  // 只选择一件最先需要作者处理的事，其他提示留在可展开建议中。
  // 输入全部来自 snapshot 投影字段（C6），这里只做 presentation 推导。
  const currentTab = ws.workbenchTab || 'question'
  const isEvidenceTab = currentTab === 'evidence'
  const isPaperTab = currentTab === 'paper'
  const isQuestionGroup = !isEvidenceTab && !isPaperTab

  let blockingDecision: WorkspaceDecision | null = null

  if (ws.bootFailure) {
    // C21：终态失败时只有 failure surface 一个真相，抑制一切推进文案。
    blockingDecision = null
  } else if (isQuestionGroup) {
    if (ws.identFailed) {
      blockingDecision = {
        title: t('decision.redesign'),
        reason: ws.identReport || t('decision.redesignReason'),
        actionLabel: t('decision.editDesign'),
        onAction: openDirection,
      }
    } else if (ws.runFailure) {
      blockingDecision = {
        title: t('decision.runFailed'),
        reason: t('decision.runFailedReason', { error: ws.runFailure }),
        actionLabel: t('decision.rerun'),
        onAction: openDirection,
      }
    } else if (
      ws.research?.teaching_case &&
      !ws.research.specification_space?.frozen_at &&
      !ws.directionBusy
    ) {
      blockingDecision = {
        title: t('decision.confirmPlans'),
        reason: t('decision.confirmPlansReason'),
        actionLabel: t('decision.viewPlans'),
        onAction: () => ws.setWorkbenchTab('design'),
      }
    } else if (
      !ws.research?.teaching_case &&
      ws.directionOpen &&
      !ws.directionBusy &&
      !ws.directionDisabledReason
    ) {
      blockingDecision = {
        title: ws.directionSummary ? t('decision.confirmDirectionEdit') : t('decision.confirmDirection'),
        reason: ws.directionSummary
          ? t('decision.confirmDirectionEditReason')
          : t('decision.confirmDirectionReason'),
        actionLabel: t('decision.openDirection'),
        onAction: openDirection,
      }
    }
  } else if (isEvidenceTab) {
    if (ws.runFailure) {
      blockingDecision = {
        title: t('decision.runFailed'),
        reason: t('decision.runFailedReason', { error: ws.runFailure }),
        actionLabel: t('decision.rerun'),
        onAction: openDirection,
      }
    } else if (
      ws.research?.teaching_case &&
      Boolean(ws.research.specification_space?.frozen_at) &&
      !(ws.research.specification_runs && ws.research.specification_runs.length) &&
      !ws.activeRun
    ) {
      blockingDecision = {
        title: t('decision.runSpecs'),
        reason: t('decision.runSpecsReason'),
        actionLabel: t('decision.runSpecs'),
        onAction: () => {
          ws.setWorkbenchTab('evidence')
          void ws.handleRunSpecSpace()
        },
      }
    } else if (ws.research?.surprise?.status === 'Unexpected') {
      blockingDecision = {
        title: t('decision.unexpected'),
        reason:
          displaySurpriseObserved(
            ws.research.expectation?.criteria,
            ws.research.specification_runs,
            t,
          ) || t('agent.unexpectedObserved'),
      }
    }
  } else if (isPaperTab) {
    if (ws.runFailure) {
      blockingDecision = {
        title: t('decision.runFailed'),
        reason: t('decision.runFailedReason', { error: ws.runFailure }),
        actionLabel: t('decision.rerun'),
        onAction: openDirection,
      }
    } else if (ws.writeBlockers.length > 0) {
      blockingDecision = {
        title: t('decision.writeBlocked'),
        reason: ws.writeBlockers[0],
        actionLabel: t('decision.viewPaper'),
        onAction: () => ws.setWorkbenchTab('paper'),
      }
    } else if (pendingChapter) {
      blockingDecision = {
        title: t('decision.confirmChapter'),
        reason: t('decision.confirmChapterReason', {
          title: pendingChapter.title || pendingChapter.type,
        }),
        actionLabel: t('decision.viewChapter'),
        onAction: () => {
          const index = ws.outline.findIndex((chapter) => chapter.type === pendingChapter.type)
          if (index >= 0) ws.handleSelectChapter(index)
          ws.setWorkbenchTab('paper')
        },
      }
    } else if (ws.outline.length > 0 && !ws.outlineLocked && !ws.writeBusy && !ws.writtenChapter?.content) {
      blockingDecision = {
        title: t('decision.confirmOutline'),
        reason: t('decision.confirmOutlineReason'),
        actionLabel: t('decision.viewOutline'),
        onAction: () => ws.setWorkbenchTab('paper'),
      }
    }
  }

  const waitingMessage = ws.directionBusy
    ? t('agent.waitingEstimate')
    : ws.writeBusy
      ? t('agent.waitingWrite')
      : ws.directionSummary && !ws.hasReadout
        ? t('agent.waitingMain')
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
  const decisionSuggestions: WorkspaceSuggestion[] = []
  if (isPaperTab) {
    if (ws.hasReadout) {
      decisionSuggestions.push({
        title: t('decision.viewEvidence'),
        detail: t('decision.viewEvidenceDetail'),
        actionLabel: t('decision.openEvidence'),
        onAction: openEvidence,
      })
    }
    if (ws.degradations.length > 0) {
      decisionSuggestions.push({
        title: t('decision.degraded'),
        detail: `${ws.degradations[0].node}: ${ws.degradations[0].reason}`,
        actionLabel: t('decision.viewTrace'),
        onAction: openEvidence,
      })
    }
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
          onTryCard={() => {
            void ws.handleTryCard()
          }}
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

  const cardQuestion = researchQuestionPrompt(ws.research, lang)
  const questionConfirmed = hasConfirmedResearchQuestion(
    ws.research,
    ws.directionSummary,
  )
  const projectName =
    cardQuestion ||
    ws.directionSummary ||
    ws.shapedQuestion ||
    (ws.research?.teaching_case ? `${t('workbench.teachingCase')} Card 1995` : null) ||
    ws.csvName ||
    t('app.hint')

  const sidebarItems: SidebarItem[] = [
    {
      id: 'overview',
      label: viewLabel.overview,
      hint: ws.directionSummary
        ? t('nav.hint.inProgress')
        : sessionId
          ? t('nav.hint.stats')
          : t('nav.hint.startUpload'),
      status: 'pending',
    },
    {
      id: 'question',
      label: viewLabel.question,
      hint: questionConfirmed ? t('nav.hint.questionDone') : t('nav.hint.questionPending'),
      status: questionConfirmed
        ? ws.directionOpen && !ws.research?.teaching_case
          ? 'active'
          : 'done'
        : 'pending',
    },
    {
      id: 'data',
      label: viewLabel.data,
      hint: ws.csvName
        ? `${ws.csvName}${ws.csvRows != null ? ` · ${t('nav.hint.rows', { n: ws.csvRows })}` : ''}`
        : t('nav.hint.noUpload'),
      status:
        ws.uploadReadiness === 'FAILED' || ws.uploadReadiness === 'CANCELLED'
          ? 'blocked'
          : ws.csvName
            ? 'done'
            : ws.uploading
              ? 'active'
              : 'pending',
    },
    {
      id: 'design',
      label: viewLabel.design,
      hint: ws.directionSummary
        ? ws.directionRecord?.method || t('nav.hint.designSet')
        : ws.research?.specification_space?.frozen_at
          ? t('nav.hint.spaceFrozen')
          : ws.research?.teaching_case
            ? t('nav.hint.designPending')
            : t('nav.hint.designNeedDirection'),
      status: ws.identFailed
        ? 'blocked'
        : ws.directionSummary || ws.research?.specification_space?.frozen_at
          ? 'done'
          : 'pending',
    },
    {
      id: 'evidence',
      label: viewLabel.evidence,
      hint: hasSuccessfulEstimate
        ? `β ${formatStatValue(ws.estimateMeta?.coef, 'coef')}`
        : ws.directionBusy
          ? t('nav.hint.estimating')
          : t('nav.hint.noMainResult'),
      status: hasSuccessfulEstimate ? 'done' : ws.directionBusy ? 'active' : 'pending',
    },
    {
      id: 'literature',
      label: viewLabel.literature,
      hint: ws.literatureSource
        ? t('nav.hint.litSource', { source: String(ws.literatureSource) })
        : t('nav.hint.litNone'),
      status: ws.literatureSource ? 'done' : 'pending',
    },
    {
      id: 'paper',
      label: viewLabel.paper,
      hint:
        ws.outline.length > 0
          ? t('nav.hint.chaptersWritten', {
              done: writtenTypes.size,
              total: ws.outline.length,
            })
          : t('nav.hint.outlinePending'),
      status:
        ws.canExport && incompleteChapterCount === 0 && pendingApprovalCount === 0
          ? 'done'
          : ws.writeBusy
            ? 'active'
            : ws.outline.length > 0
              ? 'active'
              : 'pending',
    },
  ]

  const selectView = (id: WorkbenchViewId) => {
    ws.setWorkbenchTab(id)
    if (id === 'data' && sessionId) ws.setEdaOpen(true)
  }

  const headerSubtitle = ws.directionSummary
    ? ws.directionSummary
    : ws.research?.teaching_case
      ? `${t('workbench.teachingCase')} Card 1995`
      : cardQuestion
        ? cardQuestion
        : sessionId
          ? t('workbench.subtitleNeedDirection')
          : t('workbench.subtitleUpload')

  return (
    <div
      data-testid="workbench-shell"
      className="flex h-screen min-h-0 flex-col overflow-hidden bg-wb-canvas font-sans text-wb-ink selection:bg-wb-primary/20"
    >
      {uploadLiveRegion}
      {firstScreenInput}
      {ws.globalError && (
        <div
          data-testid="global-error-toast"
          className="fixed right-4 top-4 z-50 animate-slide-up rounded-md border border-wb-danger/30 bg-wb-surface px-4 py-2 text-sm text-wb-danger shadow-sm"
        >
          ⚠ {ws.globalError}
        </div>
      )}

      <AgentCursorRoot
        workbenchTab={ws.workbenchTab}
        research={ws.research}
        onOpenEvidence={() => ws.setWorkbenchTab('evidence')}
        onRunPreview={async (specId) => {
          await ws.handleRunSpec(specId, 'preview')
        }}
        onPromote={async () => {
          const preview = ws.research?.specification_runs?.find((run) => run.relation === 'preview')
          if (preview) await ws.handlePromotePreview(preview.id)
        }}
      >
      <ThreeColumn
        ref={workspaceRef}
        outline={
          <ErrorBoundary>
            <WorkbenchSidebar
              items={sidebarItems}
              activeId={ws.workbenchTab}
              onSelect={selectView}
            >
              <div className="space-y-2 px-4 pb-3 pt-2">
                {sessionId ? (
                  <>
                    <span data-testid="session-ready" hidden />
                    <button
                      type="button"
                      data-testid="new-study-entry"
                      onClick={ws.handleNewStudy}
                      className="wb-press w-full rounded-md border border-wb-line px-2.5 py-1.5 text-left text-[12px] text-wb-muted transition-colors hover:bg-wb-surface hover:text-wb-ink"
                    >
                      {t('workbench.newStudy')}
                    </button>
                  </>
                ) : (
                  <button
                    type="button"
                    data-testid="open-guide-btn"
                    onClick={() => ws.openGuide()}
                    className="text-xs text-wb-muted transition-colors hover:text-wb-ink"
                  >
                    {t('guide.nowAgain')}
                  </button>
                )}
              </div>
            </WorkbenchSidebar>
          </ErrorBoundary>
        }
        editor={
          <ErrorBoundary>
            {/* boot 终态失败的唯一 failure surface（C21）：稳定原因 +
                Retry Card（新 idempotency key 重发）/ Back to desk。 */}
            {ws.bootFailure && sessionId ? (
              <div
                data-testid="boot-failure-card"
                role="alert"
                className="mx-6 mt-6 rounded-lg border border-wb-danger/40 bg-wb-danger-soft px-4 py-4"
              >
                <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-wb-danger">
                  {t('workbench.bootFailed')}
                </p>
                <p className="mt-1.5 text-[14px] font-medium text-wb-ink">
                  {t('workbench.bootFailedBody')}
                </p>
                <p className="mt-1 font-mono text-[11px] text-wb-danger">
                  <span data-testid="boot-failure-category">{ws.bootFailure.category}</span>
                </p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {ws.bootFailure.kind === 'card' ? (
                    <button
                      type="button"
                      data-testid="boot-failure-retry"
                      onClick={() => {
                        void ws.handleTryCard()
                      }}
                      className="wb-press rounded-md bg-wb-ink px-3 py-1.5 text-[12px] font-medium text-white"
                    >
                      {t('workbench.retryCard')}
                    </button>
                  ) : (
                    <button
                      type="button"
                      data-testid="boot-failure-retry"
                      onClick={() => ws.fileInputRef.current?.click()}
                      className="wb-press rounded-md bg-wb-ink px-3 py-1.5 text-[12px] font-medium text-white"
                    >
                      {t('workbench.reupload')}
                    </button>
                  )}
                  <button
                    type="button"
                    data-testid="boot-failure-back-desk"
                    onClick={ws.handleNewStudy}
                    className="wb-press rounded-md border border-wb-line bg-wb-surface px-3 py-1.5 text-[12px] text-wb-ink"
                  >
                    {t('workbench.backToDesk')}
                  </button>
                </div>
              </div>
            ) : null}
            {/* 主区顶部：面包屑 + 项目标题 + 动作区（契约 C1） */}
            <header
              data-testid="workbench-header"
              className="sticky top-0 z-10 border-b border-wb-line bg-wb-canvas/90 px-6 pb-3 pt-3 backdrop-blur-sm"
            >
              <div className="flex min-h-[26px] flex-wrap items-center justify-between gap-x-4 gap-y-1">
                <nav
                  data-testid="workbench-breadcrumb"
                  aria-label={t('nav.breadcrumb')}
                  className="flex min-w-0 items-center gap-1.5 text-[12px] text-wb-muted"
                >
                  <span>{t('nav.breadcrumb')}</span>
                  <span aria-hidden className="text-wb-faint">›</span>
                  <span
                    data-testid="project-name"
                    className="max-w-[36ch] truncate"
                    title={projectName}
                  >
                    {projectName}
                  </span>
                  <span aria-hidden className="text-wb-faint">›</span>
                  <span data-testid="breadcrumb-current" className="text-wb-ink">
                    {viewLabel[ws.workbenchTab]}
                  </span>
                </nav>
                <div className="flex items-center gap-2.5">
                  {ws.csvName && !ws.uploadNeedsReselect ? null : (
                    <button
                      data-testid="upload-btn"
                      onClick={() => ws.fileInputRef.current?.click()}
                      disabled={ws.uploading}
                      className="wb-press inline-flex items-center gap-1.5 rounded-md border border-wb-line-strong bg-wb-surface px-2.5 py-1 text-[12px] font-medium text-wb-ink hover:bg-wb-subtle disabled:opacity-50"
                    >
                      {ws.uploading ? t('app.uploading') : t('app.upload')}
                    </button>
                  )}
                  {ws.uploadError && (
                    <span
                      data-testid="upload-error"
                      className="rounded bg-wb-danger-soft px-2 py-0.5 text-xs text-wb-danger"
                    >
                      {ws.uploadError}
                    </span>
                  )}
                  {ws.uploadNeedsReselect && sessionId ? (
                    <button
                      type="button"
                      data-testid="upload-reselect-btn"
                      onClick={() => ws.fileInputRef.current?.click()}
                      className="rounded-md border border-wb-line px-2 py-1 text-xs text-wb-primary transition-colors hover:bg-wb-surface"
                    >
                      {t('app.uploadReselect')}
                    </button>
                  ) : null}
                  {!DEV_AUTH_BYPASS &&
                    (authed ? (
                      <button
                        onClick={ws.handleLogout}
                        className="rounded-md px-1.5 py-1 text-xs text-wb-muted transition-colors duration-150 hover:text-wb-ink"
                      >
                        {t('app.logout')}
                      </button>
                    ) : (
                      <button
                        data-testid="open-login-btn"
                        onClick={() => setAuthPage('login')}
                        className="rounded-md px-1.5 py-1 text-xs text-wb-muted transition-colors duration-150 hover:text-wb-ink"
                      >
                        {t('app.login')}
                      </button>
                    ))}
                  <LangPills />
                </div>
              </div>
              <div className="mt-1 flex flex-wrap items-end justify-between gap-x-4 gap-y-2">
                <div className="min-w-0">
                  <h1
                    data-testid="workbench-title"
                    className="max-w-[52ch] truncate font-serif text-[21px] font-semibold leading-tight tracking-[-0.01em] text-wb-ink"
                    title={cardQuestion || ws.shapedQuestion || projectName}
                  >
                    {cardQuestion || ws.shapedQuestion || projectName}
                  </h1>
                  <p
                    data-testid="workbench-subtitle"
                    className="mt-0.5 max-w-[68ch] truncate font-mono text-[12px] text-wb-muted"
                  >
                    {headerSubtitle}
                  </p>
                </div>
                <div className="flex shrink-0 items-center gap-2">
                  <button
                    type="button"
                    data-testid="run-btn"
                    onClick={openDirection}
                    className="wb-press inline-flex items-center gap-1.5 rounded-md bg-wb-primary px-3.5 py-1.5 text-[12.5px] font-medium text-white transition-colors duration-150 hover:bg-wb-primary-strong"
                  >
                    {ws.directionBusy ? t('app.directionWorking') : t('workbench.run')}
                  </button>
                  <button
                    data-testid="export-doc-btn"
                    onClick={() => ws.setDocExportOpen(true)}
                    disabled={!ws.canExport}
                    className="wb-press rounded-md border border-wb-line-strong bg-wb-surface px-2.5 py-1.5 text-[12px] text-wb-ink transition-colors duration-150 hover:bg-wb-subtle disabled:opacity-40"
                  >
                    {t('app.exportDoc')}
                  </button>
                  <button
                    data-testid="export-code-btn"
                    onClick={() => ws.setCodeExportOpen(true)}
                    disabled={!ws.canExport}
                    className="wb-press rounded-md border border-wb-line-strong bg-wb-surface px-2.5 py-1.5 text-[12px] text-wb-ink transition-colors duration-150 hover:bg-wb-subtle disabled:opacity-40"
                  >
                    {t('app.exportCode')}
                  </button>
                </div>
              </div>
            </header>
            <WorkbenchArtifact
              ws={ws}
              sessionId={sessionId}
              hasSuccessfulEstimate={hasSuccessfulEstimate}
              onOpenDirection={openDirection}
              onOpenEvidence={openEvidence}
              onSelectView={selectView}
              onOpenCode={() => ws.setCodeExportOpen(true)}
            />
          </ErrorBoundary>
        }
        agent={
          <ErrorBoundary>
            <AgentRail
              ws={ws}
              decision={blockingDecision}
              waiting={waitingMessage}
              suggestions={decisionSuggestions}
              showLinkedEvidence={ws.workbenchTab === 'paper'}
              hasSuccessfulEstimate={hasSuccessfulEstimate}
              onOpenEvidence={openEvidence}
            />
          </ErrorBoundary>
        }
      />
      </AgentCursorRoot>

      <footer
        data-testid="run-status-bar"
        className="flex h-8 shrink-0 items-center gap-4 overflow-hidden border-t border-wb-line bg-wb-surface px-5 font-mono text-[11px] text-wb-muted"
      >
        <span data-testid="run-state" className="flex items-center gap-1.5">
          <span
            aria-hidden
            className={`h-1.5 w-1.5 rounded-full ${
              ws.uploading || ws.directionBusy
                ? 'wb-dot-running bg-wb-primary'
                : ws.runFailure
                  ? 'bg-wb-danger'
                  : 'bg-wb-success'
            }`}
          />
          {ws.uploading
            ? t('status.cleaning')
            : ws.directionBusy
              ? t('status.estimating')
              : ws.activeRun
                ? t('status.backgroundRun', { id: ws.activeRun.run_id.slice(0, 8) })
                : ws.runFailure
                  ? t('status.lastFailed', { error: ws.runFailure })
                  : t('status.idle')}
        </span>
        {ws.degraded ? (
          <span data-testid="run-degradations" className="text-wb-warning">
            {t('status.degradations', { n: ws.degradations.length })}
          </span>
        ) : null}
        {sessionId ? (
          <span
            data-testid="run-trace-hint"
            className="truncate"
            title={`/api/sessions/${sessionId}/trace`}
          >
            {t('status.traceHint')}
          </span>
        ) : null}
      </footer>

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
