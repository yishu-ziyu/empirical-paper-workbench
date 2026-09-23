import { useT } from '../lib/i18n'
import type { BlockingDecision } from '../lib/workspace'
import type { ContinuePermission } from '../lib/confirmationCommands'

export interface PrewriteConfirmCardProps {
  /** 后端真实 Table 1（prewrite_preview 产出）。 */
  table1: Record<string, any> | null
  specificationEquation: string | null
  table1Confirmed: boolean
  specConfirmed: boolean
  blockingDecision: BlockingDecision | null
  /** record_confirms 进行中（'table1' | 'spec' | 'risk'），只显示等待。 */
  confirmBusy: 'table1' | 'spec' | 'risk' | null
  confirmError: string | null
  estimateStarting: boolean
  /** 方向 run 停在预览处（prewrite_gate = awaiting_estimate）。 */
  awaitingEstimate: boolean
  estimateComplete: boolean
  /** #40 三档许可：unknown 既不是通过也不是禁止。 */
  continuePermission: ContinuePermission
  /** 当前诊断 + 设计版本上已有风险决定。 */
  riskConfirmed: boolean
  onConfirmTable1: () => void
  onConfirmSpec: () => void
  onConfirmRisk: () => void
  onStartEstimate: () => void
}

function formatCell(value: unknown): string {
  if (value == null) return '—'
  if (typeof value === 'number') return Number.isInteger(value) ? String(value) : value.toFixed(3)
  return String(value)
}

/**
 * 估计前两段确认（PREWRITE-PAUSE）：先确认真实样本（Table 1），再确认
 * 具体分析设定（方程）。两个确认互不代替；两项未齐不启动估计；
 * 200 只回读标志，202 才跟踪返回的 run（FORMAL-CONFIRMATION-CHAIN-1 C5/C6）。
 */
export default function PrewriteConfirmCard({
  table1,
  specificationEquation,
  table1Confirmed,
  specConfirmed,
  blockingDecision,
  confirmBusy,
  confirmError,
  estimateStarting,
  awaitingEstimate,
  estimateComplete,
  continuePermission,
  riskConfirmed,
  onConfirmTable1,
  onConfirmSpec,
  onConfirmRisk,
  onStartEstimate,
}: PrewriteConfirmCardProps) {
  const { t } = useT()
  const columns: string[] = Array.isArray(table1?.columns) ? table1.columns : []
  const rows: Array<Record<string, unknown>> = Array.isArray(table1?.rows)
    ? table1.rows
    : []
  const sampleN = typeof table1?.n === 'number' ? table1.n : null
  const blocked = blockingDecision?.blocked === true
  const forbidden = continuePermission === 'forbid'
  const riskRequired = continuePermission === 'confirm' && !riskConfirmed
  const permissionNote =
    continuePermission === 'forbid'
      ? t('prewrite.permissionForbid')
      : continuePermission === 'confirm'
        ? t('prewrite.permissionConfirm')
        : continuePermission === 'allow'
          ? t('prewrite.permissionAllow')
          : t('prewrite.permissionUnknown')
  const startDisabledReason = forbidden
    ? t('prewrite.startForbidden')
    : riskRequired
      ? t('prewrite.startNeedRisk')
      : !table1Confirmed || !specConfirmed
        ? t('prewrite.startNeedBoth')
        : blocked
          ? blockingDecision?.reason || undefined
          : undefined

  if (estimateComplete) {
    return (
      <section
        data-testid="prewrite-confirm"
        className="mb-8 rounded-lg border border-border bg-panel p-6"
      >
        <p data-testid="prewrite-estimate-complete" className="text-[13px] leading-6 text-ink">
          {t('prewrite.estimateComplete')}
        </p>
      </section>
    )
  }

  if (!awaitingEstimate) return null

  return (
    <section
      data-testid="prewrite-confirm"
      className="mb-8 rounded-lg border border-border bg-panel p-6"
    >
      <header className="mb-4">
        <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-wb-faint">
          {t('prewrite.kicker')}
        </p>
        <h2 className="mt-1 font-serif text-[1.15rem] text-ink">{t('prewrite.title')}</h2>
        <p className="mt-2 text-[13px] leading-6 text-muted">{t('prewrite.lead')}</p>
        <p
          data-testid="prewrite-permission-note"
          className="mt-2 text-[12px] leading-5 text-wb-muted"
        >
          {permissionNote}
        </p>
      </header>

      <div className="mb-5">
        <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
          <h3 className="text-[13px] font-medium text-ink">{t('prewrite.table1Title')}</h3>
          {sampleN != null ? (
            <span data-testid="table1-n" className="font-mono text-[11px] text-muted">
              {t('prewrite.sampleN', { n: sampleN })}
            </span>
          ) : null}
        </div>
        {rows.length > 0 ? (
          <div data-testid="table1-preview" className="overflow-x-auto rounded-md border border-wb-line">
            <table className="w-full text-[12px]">
              <thead>
                <tr className="border-b border-wb-line bg-wb-subtle text-left text-muted">
                  {columns.map((col) => (
                    <th key={col} className="px-2 py-1.5 font-medium">{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((row, index) => (
                  <tr key={index} className="border-b border-wb-line last:border-0">
                    {columns.map((col) => (
                      <td key={col} className="px-2 py-1.5 text-ink">
                        {formatCell(row[col])}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p data-testid="table1-preview" className="text-[12px] text-muted">
            {t('prewrite.table1Empty')}
          </p>
        )}
        <div className="mt-2 flex items-center gap-3">
          <button
            type="button"
            data-testid="confirm-table1-btn"
            onClick={onConfirmTable1}
            disabled={table1Confirmed || confirmBusy !== null}
            className="rounded-lg border border-wb-line-strong bg-wb-surface px-3.5 py-1.5 text-[12px] font-medium text-wb-ink hover:bg-wb-subtle disabled:cursor-not-allowed disabled:opacity-40"
          >
            {confirmBusy === 'table1'
              ? t('prewrite.confirmSending')
              : table1Confirmed
                ? t('prewrite.table1Confirmed')
                : t('prewrite.confirmTable1')}
          </button>
          <span data-testid="table1-flag" className="font-mono text-[11px] text-muted">
            {table1Confirmed ? t('prewrite.flagYes') : t('prewrite.flagNo')}
          </span>
        </div>
      </div>

      <div className="mb-5">
        <h3 className="mb-2 text-[13px] font-medium text-ink">{t('prewrite.specTitle')}</h3>
        <p data-testid="spec-equation" className="rounded-md border border-wb-line bg-wb-subtle px-3 py-2 font-mono text-[13px] text-ink">
          {specificationEquation || '—'}
        </p>
        <div className="mt-2 flex items-center gap-3">
          <button
            type="button"
            data-testid="confirm-spec-btn"
            onClick={onConfirmSpec}
            // 顺序由服务端强制（sample_confirmation_required）；这里也不
            // 提供越过样本确认的入口。
            disabled={specConfirmed || !table1Confirmed || confirmBusy !== null}
            title={!table1Confirmed ? t('prewrite.refusedSampleFirst') : undefined}
            className="rounded-lg border border-wb-line-strong bg-wb-surface px-3.5 py-1.5 text-[12px] font-medium text-wb-ink hover:bg-wb-subtle disabled:cursor-not-allowed disabled:opacity-40"
          >
            {confirmBusy === 'spec'
              ? t('prewrite.confirmSending')
              : specConfirmed
                ? t('prewrite.specConfirmed')
                : t('prewrite.confirmSpec')}
          </button>
          <span data-testid="spec-flag" className="font-mono text-[11px] text-muted">
            {specConfirmed ? t('prewrite.flagYes') : t('prewrite.flagNo')}
          </span>
        </div>
      </div>

      {continuePermission === 'confirm' ? (
        <div
          data-testid="risk-block"
          className="mb-5 rounded-md border border-wb-warning/35 bg-wb-warning-soft px-3 py-3"
        >
          <h3 className="text-[13px] font-medium text-wb-ink">{t('prewrite.riskTitle')}</h3>
          <p className="mt-1 text-[12px] leading-5 text-wb-muted">{t('prewrite.riskLead')}</p>
          <div className="mt-2 flex items-center gap-3">
            <button
              type="button"
              data-testid="confirm-risk-btn"
              onClick={onConfirmRisk}
              disabled={riskConfirmed || confirmBusy !== null}
              className="rounded-lg border border-wb-warning/40 bg-wb-surface px-3.5 py-1.5 text-[12px] font-medium text-wb-ink hover:bg-wb-warning-soft disabled:cursor-not-allowed disabled:opacity-40"
            >
              {confirmBusy === 'risk'
                ? t('prewrite.confirmSending')
                : riskConfirmed
                  ? t('prewrite.riskFlagYes')
                  : t('prewrite.confirmRisk')}
            </button>
            <span data-testid="risk-flag" className="font-mono text-[11px] text-wb-muted">
              {riskConfirmed ? t('prewrite.riskFlagYes') : t('prewrite.riskFlagNo')}
            </span>
          </div>
        </div>
      ) : null}

      {blocked && blockingDecision?.reason ? (
        <p data-testid="blocking-reason" role="alert" className="mb-3 rounded-md border border-wb-danger/30 bg-wb-danger-soft px-3 py-2 text-[12px] text-wb-danger">
          {blockingDecision.reason}
        </p>
      ) : null}
      {confirmError ? (
        <p data-testid="prewrite-confirm-error" role="alert" className="mb-3 text-[12px] text-danger">
          {confirmError}
        </p>
      ) : null}

      <div className="border-t border-border pt-3">
        <button
          type="button"
          data-testid="start-estimate-btn"
          onClick={onStartEstimate}
          disabled={
            !table1Confirmed ||
            !specConfirmed ||
            blocked ||
            forbidden ||
            riskRequired ||
            estimateStarting
          }
          title={startDisabledReason}
          className="rounded-lg bg-accent px-4 py-2 text-[13px] font-medium text-white hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {estimateStarting ? t('prewrite.starting') : t('prewrite.startEstimate')}
        </button>
        {forbidden ? (
          <p
            data-testid="prewrite-forbid-reason"
            role="alert"
            className="mt-2 rounded-md border border-wb-danger/30 bg-wb-danger-soft px-3 py-2 text-[12px] text-wb-danger"
          >
            {t('prewrite.startForbidden')}
          </p>
        ) : startDisabledReason && !estimateStarting ? (
          <p
            data-testid="prewrite-start-reason"
            className="mt-2 text-[12px] leading-5 text-wb-muted"
          >
            {startDisabledReason}
          </p>
        ) : null}
        {estimateStarting ? (
          <p data-testid="estimate-starting" role="status" aria-live="polite" className="mt-2 text-[12px] text-muted">
            {t('prewrite.starting')}
          </p>
        ) : null}
      </div>
    </section>
  )
}
