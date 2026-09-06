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
import type { WorkspaceDecision, WorkspaceSuggestion } from './components/WorkspaceDecisionRail'
import ReadingFocus from './components/ReadingFocus'
import type { ResizableWorkspaceHandle } from './components/ResizableWorkspace'
import { useT } from './lib/i18n'
import { DEV_AUTH_BYPASS, useSession } from './lib/session'
import { useWorkspace } from './lib/workspace'
import { formatStatValue } from './lib/readoutTable'
import WorkbenchArtifact from './components/WorkbenchArtifact'

const VIEW_LABEL: Record<WorkbenchViewId, string> = {
  overview: 'Overview',
  question: 'Research Question',
  data: 'Data',
  design: 'Design · Specification',
  evidence: 'Evidence',
  literature: 'Literature',
  paper: 'Paper',
}

function App() {
  const { t } = useT()
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
  let blockingDecision: WorkspaceDecision | null = null
  if (ws.identFailed) {
    blockingDecision = {
      title: '研究设计需要重开',
      reason: ws.identReport || '识别未通过，先改研究设计再写正文。',
      actionLabel: '修改研究设计',
      onAction: openDirection,
    }
  } else if (ws.runFailure) {
    blockingDecision = {
      title: '上一次运行失败',
      reason: `${ws.runFailure}。检查数据与方向后可重新运行。`,
      actionLabel: '重新运行',
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
  const decisionSuggestions: WorkspaceSuggestion[] = []
  if (ws.hasReadout) {
    decisionSuggestions.push({
      title: '查看证据解释',
      detail: '识别说明、稳健性和运行摘要不会打断论文正文。',
      actionLabel: '打开 Evidence',
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

  const projectName =
    ws.directionSummary ||
    ws.shapedQuestion ||
    ws.csvName ||
    t('app.hint')

  const sidebarItems: SidebarItem[] = [
    {
      id: 'overview',
      label: 'Overview',
      hint: ws.directionSummary
        ? '研究进行中'
        : sessionId
          ? '统计与进度'
          : '从上传数据开始',
      status: 'pending',
    },
    {
      id: 'question',
      label: 'Research Question',
      hint: ws.directionSummary ? '已确认' : '待确认方向',
      status: ws.directionSummary
        ? ws.directionOpen
          ? 'active'
          : 'done'
        : 'pending',
    },
    {
      id: 'data',
      label: 'Data',
      hint: ws.csvName
        ? `${ws.csvName}${ws.csvRows != null ? ` · ${ws.csvRows} 行` : ''}`
        : '未上传',
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
      label: 'Design · Specification',
      hint: ws.directionSummary ? ws.directionRecord?.method || '已设定' : '待方向',
      status: ws.identFailed ? 'blocked' : ws.directionSummary ? 'done' : 'pending',
    },
    {
      id: 'evidence',
      label: 'Evidence',
      hint: hasSuccessfulEstimate
        ? `β ${formatStatValue(ws.estimateMeta?.coef, 'coef')}`
        : ws.directionBusy
          ? '估计中'
          : '暂无主结果',
      status: hasSuccessfulEstimate ? 'done' : ws.directionBusy ? 'active' : 'pending',
    },
    {
      id: 'literature',
      label: 'Literature',
      hint: ws.literatureSource ? `来源：${ws.literatureSource}` : '未检索',
      status: ws.literatureSource ? 'done' : 'pending',
    },
    {
      id: 'paper',
      label: 'Paper',
      hint:
        ws.outline.length > 0
          ? `${writtenTypes.size}/${ws.outline.length} 章有正文`
          : '待大纲',
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
    : sessionId
      ? '尚未设定研究方向；先在 Research Question 提交方向。'
      : '上传数据后开始研究。'

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

      <ThreeColumn
        ref={workspaceRef}
        outline={
          <ErrorBoundary>
            <WorkbenchSidebar
              items={sidebarItems}
              activeId={ws.workbenchTab}
              onSelect={selectView}
            >
              <div className="px-4 pb-3 pt-2">
                {sessionId ? (
                  <span data-testid="session-ready" hidden />
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
            {/* 主区顶部：面包屑 + 项目标题 + 动作区（契约 C1） */}
            <header
              data-testid="workbench-header"
              className="sticky top-0 z-10 border-b border-wb-line bg-wb-canvas/90 px-6 pb-3 pt-3 backdrop-blur-sm"
            >
              <div className="flex min-h-[26px] flex-wrap items-center justify-between gap-x-4 gap-y-1">
                <nav
                  data-testid="workbench-breadcrumb"
                  aria-label="面包屑"
                  className="flex min-w-0 items-center gap-1.5 text-[12px] text-wb-muted"
                >
                  <span>项目</span>
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
                    {VIEW_LABEL[ws.workbenchTab]}
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
                    title={ws.shapedQuestion || projectName}
                  >
                    {ws.shapedQuestion || projectName}
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
                    {ws.directionBusy ? t('app.directionWorking') : 'Run'}
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
            ? '数据清理中…'
            : ws.directionBusy
              ? '正在估计…'
              : ws.activeRun
                ? `后台 run ${ws.activeRun.run_id.slice(0, 8)} 进行中`
                : ws.runFailure
                  ? `上次运行失败：${ws.runFailure}`
                  : '空闲'}
        </span>
        {ws.degraded ? (
          <span data-testid="run-degradations" className="text-wb-warning">
            {ws.degradations.length} 条降级记录
          </span>
        ) : null}
        {sessionId ? (
          <span
            data-testid="run-trace-hint"
            className="truncate"
            title={`/api/sessions/${sessionId}/trace`}
          >
            运行记录与 trace 可查
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
