import { useEffect, useState } from 'react'
import { useT } from '../lib/i18n'
import type { SessionDesign } from '../lib/workspace'

/** 确认提交的是所见草稿的版本，不是「当前后端草稿」的任意版本。 */
export interface DesignConfirmPayload {
  expectedRevision: string | null
}

export interface DesignProposeOptions {
  /** 修订入口：显式重提会撤销旧设计的批准与预览。 */
  revise: boolean
}

export interface DesignProposalCardProps {
  /** 当前题目（空桌确认的研究问题原文）。 */
  shapedQuestion: string
  /** 后端 snapshot 中的 session.design（null = 尚未提出）。 */
  design: SessionDesign | null
  proposing: boolean
  confirming: boolean
  error: string | null
  onPropose: (title: string, question: string, opts: DesignProposeOptions) => void
  onConfirm: (payload: DesignConfirmPayload) => void
}

const METHOD_LABEL: Record<string, string> = {
  ols: 'OLS',
  did: 'DiD',
  iv: 'IV',
  rd: 'RD',
  scm: 'SCM',
}

/**
 * 正式路径设计提出 / 编辑 / 确认（infer-design DECIDE-6）。
 * 提出只写 draft；确认才获得设计锁。未确认时不授予下游权限。
 * 一切状态以后端响应 + snapshot 回读为准。
 *
 * R5：确认的必须是用户眼前这一版草稿。改过题目还没保存时不能批准旧草稿；
 * 确认请求携带所见草稿的 revision，由服务端校验；确认后仍保留显式修订入口。
 */
export default function DesignProposalCard({
  shapedQuestion,
  design,
  proposing,
  confirming,
  error,
  onPropose,
  onConfirm,
}: DesignProposalCardProps) {
  const { t } = useT()
  const confirmed = design?.status === 'confirmed' && design.confirmed === true
  const savedTitle = (design?.source?.title || shapedQuestion || '').trim()
  const [title, setTitle] = useState(savedTitle)
  const [revising, setRevising] = useState(false)

  useEffect(() => {
    // 跟随 snapshot 已保存的题目；用户正在输入时 savedTitle 不变，不覆盖（C2）。
    setTitle(savedTitle)
  }, [savedTitle])

  useEffect(() => {
    // 一旦不再是已确认状态（例如修订已提交），修订态自然结束。
    if (!confirmed) setRevising(false)
  }, [confirmed])

  const dirty = title.trim() !== savedTitle
  const draftVisible = design != null && !confirmed
  const editing = !confirmed || revising
  const busy = proposing || confirming

  const proposeButton = (
    <button
      type="button"
      data-testid="design-propose-btn"
      onClick={() => onPropose(title.trim(), '', { revise: revising })}
      disabled={busy || !title.trim()}
      className="rounded-lg border border-wb-line-strong bg-wb-surface px-4 py-2 text-[13px] font-medium text-wb-ink hover:bg-wb-subtle disabled:cursor-not-allowed disabled:opacity-40"
    >
      {proposing
        ? t('designProposal.proposing')
        : revising
          ? t('designProposal.proposeRevision')
          : t('designProposal.propose')}
    </button>
  )

  return (
    <section
      data-testid="design-proposal"
      className="mb-8 rounded-lg border border-border bg-panel p-6"
    >
      <header className="mb-4">
        <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-wb-faint">
          {t('designProposal.kicker')}
        </p>
        <h2 className="mt-1 font-serif text-[1.15rem] text-ink">
          {t('designProposal.title')}
        </h2>
        <p className="mt-2 text-[13px] leading-6 text-muted">{t('designProposal.lead')}</p>
      </header>

      {!editing ? (
        <div data-testid="design-confirmed" className="space-y-3">
          <p className="text-[13px] leading-6 text-ink">
            <span className="mr-2 inline-block rounded-full bg-wb-primary/10 px-2 py-0.5 text-[11px] font-medium text-wb-primary">
              {t('designProposal.confirmedBadge')}
            </span>
            <span data-testid="design-confirmed-title">{design.source?.title || title}</span>
          </p>
          <dl className="grid grid-cols-2 gap-3 text-xs sm:grid-cols-4">
            <div>
              <dt className="text-muted">{t('design.method')}</dt>
              <dd data-testid="design-confirmed-method" className="mt-1 text-ink">
                {METHOD_LABEL[design.method] || design.method}
              </dd>
            </div>
            <div>
              <dt className="text-muted">{t('designProposal.outcome')}</dt>
              <dd data-testid="design-confirmed-outcome" className="mt-1 text-ink">
                {design.outcome || '—'}
              </dd>
            </div>
            <div>
              <dt className="text-muted">{t('designProposal.treatment')}</dt>
              <dd data-testid="design-confirmed-treatment" className="mt-1 text-ink">
                {design.treatment || '—'}
              </dd>
            </div>
            <div>
              <dt className="text-muted">{t('designProposal.qType')}</dt>
              <dd className="mt-1 text-ink">{design.qType || '—'}</dd>
            </div>
          </dl>
          <p className="font-mono text-[11px] text-muted">
            {t('designProposal.confirmedAt', { at: design.confirmed_at || '' })}
          </p>
          {/* C8：不禁止修订，但修订必须是显式动作。 */}
          <div className="border-t border-border pt-3">
            <button
              type="button"
              data-testid="design-revise-btn"
              onClick={() => setRevising(true)}
              className="rounded-lg border border-wb-line-strong bg-wb-surface px-3.5 py-1.5 text-[12px] font-medium text-wb-ink hover:bg-wb-subtle"
            >
              {t('designProposal.revise')}
            </button>
            <p className="mt-2 text-[12px] leading-5 text-wb-muted">
              {t('designProposal.reviseHint')}
            </p>
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          <div>
            <label htmlFor="design-title-input" className="mb-1 block text-[12px] text-muted">
              {t('designProposal.titleLabel')}
            </label>
            <input
              id="design-title-input"
              data-testid="design-title-input"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              disabled={busy}
              className="w-full rounded-md border border-border bg-paper px-3 py-2 text-[13px] text-ink"
            />
            {dirty ? (
              <p
                data-testid="design-dirty-hint"
                role="status"
                className="mt-1.5 text-[12px] leading-5 text-wb-warning"
              >
                {t('designProposal.dirtyHint')}
              </p>
            ) : null}
          </div>

          {design != null && (revising || !confirmed) ? (
            <div
              data-testid={revising ? 'design-revise-current' : 'design-draft'}
              className="rounded-md border border-wb-line bg-wb-subtle px-3 py-2"
            >
              <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-wb-faint">
                {revising ? t('designProposal.currentBadge') : t('designProposal.draftBadge')}
              </p>
              <dl className="mt-2 grid grid-cols-2 gap-3 text-xs sm:grid-cols-4">
                <div>
                  <dt className="text-muted">{t('design.method')}</dt>
                  <dd data-testid="design-draft-method" className="mt-1 text-ink">
                    {METHOD_LABEL[design.method] || design.method}
                  </dd>
                </div>
                <div>
                  <dt className="text-muted">{t('designProposal.outcome')}</dt>
                  <dd className="mt-1 text-ink">{design.outcome || '—'}</dd>
                </div>
                <div>
                  <dt className="text-muted">{t('designProposal.treatment')}</dt>
                  <dd className="mt-1 text-ink">{design.treatment || '—'}</dd>
                </div>
                <div>
                  <dt className="text-muted">{t('designProposal.qType')}</dt>
                  <dd className="mt-1 text-ink">{design.qType || '—'}</dd>
                </div>
              </dl>
            </div>
          ) : null}

          <div className="flex flex-wrap items-center gap-3 border-t border-border pt-3">
            {proposeButton}
            {revising ? (
              <button
                type="button"
                data-testid="design-revise-cancel"
                onClick={() => setRevising(false)}
                disabled={busy}
                className="text-[12px] text-wb-muted hover:text-wb-ink disabled:opacity-40"
              >
                {t('designProposal.reviseCancel')}
              </button>
            ) : null}
            {revising ? null : (
              <button
                type="button"
                data-testid="design-confirm-btn"
                onClick={() => onConfirm({ expectedRevision: design?.revision ?? null })}
                disabled={busy || !draftVisible || dirty}
                title={
                  dirty
                    ? t('designProposal.confirmNeedSaved')
                    : !draftVisible
                      ? t('designProposal.confirmNeedDraft')
                      : undefined
                }
                className="rounded-lg bg-accent px-4 py-2 text-[13px] font-medium text-white hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
              >
                {confirming ? t('designProposal.confirming') : t('designProposal.confirm')}
              </button>
            )}
          </div>
        </div>
      )}

      {error ? (
        <p data-testid="design-error" role="alert" className="mt-3 text-[12px] text-danger">
          {error}
        </p>
      ) : null}
    </section>
  )
}
