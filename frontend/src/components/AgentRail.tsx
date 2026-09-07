import type { WorkspaceApi } from '../lib/workspace'
import { formatStatValue } from '../lib/readoutTable'
import { useAgentCursor } from '../lib/agentCursor/context'
import type { WorkspaceDecision, WorkspaceSuggestion } from './WorkspaceDecisionRail'
import WorkspaceDecisionRail from './WorkspaceDecisionRail'
import { useT, type Translate } from '../lib/i18n'

/**
 * Workbench v2 右侧 Agent 栏（契约 C5）：上半当前任务（只在真的有事
 * 发生时出现，空闲不空转），下半下一步决策卡（amber 语义色）。
 * Paper 视图时顶部追加 Linked Evidence 绑定栏（契约 C4）。
 * 全部状态来自 snapshot 投影与本地 run 订阅，不伪造任务。
 */

interface CurrentTask {
  label: string
  why: string
}

function deriveCurrentTask(ws: WorkspaceApi, t: Translate): CurrentTask | null {
  if (ws.uploading) {
    return { label: t('agent.receiving'), why: t('agent.receivingWhy') }
  }
  if (ws.directionBusy) {
    return { label: t('agent.estimating'), why: t('agent.estimatingWhy') }
  }
  if (ws.writeBusy) {
    return {
      label: t('agent.writing', { title: ws.writingType || t('agent.chapterFallback') }),
      why: t('agent.writingWhy'),
    }
  }
  if (ws.activeRun?.kind === 'spec_run') {
    // 进度来自真实 run 事件（逐 spec）；分母不可数时 indeterminate，不虚构。
    const progress = ws.specRunProgress
    return progress
      ? {
          label: t('agent.specRunning', { done: progress.done, total: progress.total }),
          why: t('agent.specRunningWhy'),
        }
      : {
          label: t('agent.specRunningIndeterminate'),
          why: t('agent.specRunningWhy'),
        }
  }
  if (ws.activeRun) {
    return {
      label: t('agent.background'),
      why: t('agent.backgroundWhy', { id: ws.activeRun.run_id.slice(0, 8) }),
    }
  }
  return null
}

function LinkedEvidenceCard({
  ws,
  hasSuccessfulEstimate,
  onOpenEvidence,
}: {
  ws: WorkspaceApi
  hasSuccessfulEstimate: boolean
  onOpenEvidence: () => void
}) {
  const { t } = useT()
  const claim = ws.research?.claim ?? ws.research?.claims?.[0]
  const claimsExist = Boolean(claim?.id) || (ws.research?.claims?.length ?? 0) > 0
  const resultsChapter = ws.writtenChapters.find((chapter) => chapter.type === 'results')
  const labRevision = ws.research?.evidence_revision
  const revisionMismatch =
    labRevision != null &&
    (claim?.based_on_evidence_revision == null ||
      claim.based_on_evidence_revision !== labRevision)
  const claimOk =
    !claimsExist ||
    (Boolean(claim?.approved_by_user) &&
      !claim?.stale &&
      !revisionMismatch &&
      !resultsChapter?.stale &&
      !resultsChapter?.needs_regeneration)
  const grounded =
    hasSuccessfulEstimate &&
    !ws.identFailed &&
    ws.writeBlockers.length === 0 &&
    claimOk &&
    resultsChapter?.grounded === true
  return (
    <section
      data-testid="linked-evidence"
      className="rounded-lg border border-wb-line bg-wb-surface px-3.5 py-3.5"
    >
      <div className="flex items-center justify-between gap-2">
        <h3 className="text-[13px] font-semibold text-wb-ink">{t('agent.linkedEvidence')}</h3>
        <span
          data-testid="evidence-grounded-badge"
          data-grounded={grounded}
          className={`rounded-full px-2 py-0.5 text-[10.5px] font-medium ${
            grounded
              ? 'bg-wb-success-soft text-wb-success'
              : 'bg-wb-warning-soft text-wb-warning'
          }`}
        >
          {grounded ? t('agent.grounded') : t('agent.notGrounded')}
        </span>
      </div>
      <p className="mt-0.5 text-[11px] leading-4 text-wb-faint">
        {t('agent.linkedHint')}
      </p>

      {hasSuccessfulEstimate ? (
        <dl className="mt-2.5 space-y-1 font-mono text-[12px] tabular-nums text-wb-ink">
          <div className="flex justify-between gap-2">
            <dt className="text-wb-muted">β {t('agent.coef')}</dt>
            <dd>{formatStatValue(ws.estimateMeta?.coef, 'coef')}</dd>
          </div>
          <div className="flex justify-between gap-2">
            <dt className="text-wb-muted">SE</dt>
            <dd>{formatStatValue(ws.estimateMeta?.se, 'se')}</dd>
          </div>
          <div className="flex justify-between gap-2">
            <dt className="text-wb-muted">p</dt>
            <dd>{formatStatValue(ws.estimateMeta?.p, 'p')}</dd>
          </div>
          <div className="flex justify-between gap-2">
            <dt className="text-wb-muted">N</dt>
            <dd>{formatStatValue(ws.estimateMeta?.n, 'n')}</dd>
          </div>
        </dl>
      ) : (
        <p className="mt-2.5 rounded-md border border-dashed border-wb-line-strong px-2.5 py-2 text-[11.5px] leading-4 text-wb-muted">
          {ws.identFailed ? t('agent.identFailed') : t('agent.noMain')}
        </p>
      )}

      {!grounded && ws.writeBlockers.length > 0 ? (
        <ul className="mt-2 space-y-1 text-[11px] leading-4 text-wb-warning">
          {ws.writeBlockers.slice(0, 3).map((blocker) => (
            <li key={blocker}>· {blocker}</li>
          ))}
        </ul>
      ) : null}

      <button
        type="button"
        data-testid="linked-evidence-open"
        onClick={onOpenEvidence}
        className="wb-press mt-3 w-full rounded-md border border-wb-line px-2.5 py-1.5 text-[12px] text-wb-ink hover:bg-wb-subtle"
      >
        {t('agent.openEvidence')} →
      </button>
    </section>
  )
}

export interface AgentRailProps {
  ws: WorkspaceApi
  decision: WorkspaceDecision | null
  waiting: string | null
  suggestions: WorkspaceSuggestion[]
  showLinkedEvidence: boolean
  hasSuccessfulEstimate: boolean
  onOpenEvidence: () => void
}

export default function AgentRail({
  ws,
  decision,
  waiting,
  suggestions,
  showLinkedEvidence,
  hasSuccessfulEstimate,
  onOpenEvidence,
}: AgentRailProps) {
  const { t } = useT()
  const task = deriveCurrentTask(ws, t)
  const cursor = useAgentCursor()
  const isEvidence = ws.workbenchTab === 'evidence'
  const unexpected = ws.research?.surprise?.status === 'Unexpected'
  const cursorActive =
    isEvidence &&
    (cursor.presentation.status === 'running' ||
      cursor.presentation.status === 'paused' ||
      cursor.presentation.status === 'awaiting-confirm' ||
      cursor.presentation.status === 'done' ||
      cursor.presentation.status === 'aborted')
  const showMe =
    isEvidence &&
    unexpected &&
    (cursor.presentation.status === 'idle' ||
      cursor.presentation.status === 'done' ||
      cursor.presentation.status === 'aborted')
  return (
    <div data-testid="agent-rail" className="space-y-4 px-4 py-4">
      {showLinkedEvidence ? (
        <LinkedEvidenceCard
          ws={ws}
          hasSuccessfulEstimate={hasSuccessfulEstimate}
          onOpenEvidence={onOpenEvidence}
        />
      ) : null}

      {/* 当前任务：只在有事发生时出现（C5 空闲不空转） */}
      <section data-testid="agent-current-task" data-busy={Boolean(task)}>
        <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-wb-faint">
          {t('agent.currentTask')}
        </p>
        {task ? (
          <div className="mt-1.5 rounded-lg border border-wb-line bg-wb-surface px-3 py-2.5">
            <p className="flex items-center gap-2 text-[13px] font-medium text-wb-ink">
              <span
                aria-hidden
                className="wb-dot-running h-1.5 w-1.5 shrink-0 rounded-full bg-wb-primary"
              />
              {task.label}
            </p>
            <p className="mt-1 text-[11.5px] leading-4 text-wb-muted">{task.why}</p>
          </div>
        ) : (
          <p className="mt-1.5 text-[12px] leading-5 text-wb-faint">{t('agent.idle')}</p>
        )}
      </section>

      {showMe ? (
        <section
          data-testid="agent-cursor-prompt"
          className="rounded-lg border border-wb-line bg-wb-surface px-3 py-2.5"
        >
          <p className="text-[13px] font-medium text-wb-ink">{t('agent.showMeTitle')}</p>
          <p className="mt-1 text-[11.5px] leading-4 text-wb-muted">
            {ws.research?.surprise?.observed || 'OLS and IV do not match the recorded expectation.'}
          </p>
          <button
            type="button"
            data-testid="agent-cursor-show-me"
            data-agent-cursor-control=""
            onClick={cursor.playShowMe}
            className="wb-press mt-2.5 rounded-md border border-wb-line bg-wb-subtle px-2.5 py-1 text-[12px] text-wb-ink"
          >
            {t('agent.showMe')}
          </button>
        </section>
      ) : null}

      {cursor.presentation.status === 'awaiting-confirm' &&
      cursor.presentation.awaiting === 'runPreview' ? (
        <section className="rounded-lg border border-wb-line bg-wb-surface px-3 py-2.5">
          <p className="text-[13px] font-medium text-wb-ink">{t('agent.runPreviewQ')}</p>
          <p className="mt-1 text-[11.5px] leading-4 text-wb-muted">
            {t('agent.runPreviewHint')}
          </p>
          <button
            type="button"
            data-testid="agent-cursor-run-preview"
            data-agent-cursor-control=""
            onClick={cursor.confirmRunPreview}
            className="wb-press mt-2.5 rounded-md bg-wb-ink px-2.5 py-1 text-[12px] font-medium text-white"
          >
            {t('agent.runPreview')}
          </button>
        </section>
      ) : null}

      {cursorActive ? (
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            data-testid="agent-cursor-cancel"
            data-agent-cursor-control=""
            onClick={cursor.cancel}
            className="wb-press rounded-md border border-wb-line px-2.5 py-1 text-[12px] text-wb-ink"
          >
            {t('agent.cancel')}
          </button>
          <button
            type="button"
            data-testid="agent-cursor-replay"
            data-agent-cursor-control=""
            onClick={cursor.replay}
            className="wb-press rounded-md border border-wb-line px-2.5 py-1 text-[12px] text-wb-ink"
          >
            {t('agent.replay')}
          </button>
        </div>
      ) : null}

      {cursor.presentation.status === 'paused' ? (
        <div className="flex flex-wrap items-center gap-2">
          <p className="text-[12px] text-wb-muted">{t('agent.paused')}</p>
          <button
            type="button"
            data-testid="agent-cursor-resume"
            data-agent-cursor-control=""
            onClick={cursor.resume}
            className="wb-press rounded-md border border-wb-line bg-wb-subtle px-2.5 py-1 text-[12px] text-wb-ink"
          >
            {t('agent.resume')}
          </button>
        </div>
      ) : null}

      <WorkspaceDecisionRail decision={decision} waiting={waiting} suggestions={suggestions} />
    </div>
  )
}
