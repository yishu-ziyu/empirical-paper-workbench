import { useEffect, useState, type ReactNode } from 'react'
import { useT } from '../lib/i18n'
import { fetchSessionEvidence, type EvidenceModel } from '../lib/workspace'
import {
  claimLabel,
  formatStatValue,
  normalizeEstimateTableSource,
  parseEstimateRows,
} from '../lib/readoutTable'
import type { DirectionFormData } from './DirectionForm'

/**
 * Evidence 一等视图（契约 C3）：主张句标题 + 设定 chips + 真实回归表 +
 * Specification Details + 右侧溯源链时间线。数据只来自
 * GET /api/sessions/{id}/evidence 与 snapshot 投影；某一层没有数据
 * 就显式「暂无」，可溯源完整性如实计数，不无脑写 Fully traceable。
 * estimate 失败时显式呈现失败态与下一步，绝不显示伪成功。
 */

interface ProvenanceLayer {
  id: string
  title: string
  detail: ReactNode
  present: boolean
}

export interface EvidenceViewProps {
  sessionId: string
  refreshKey?: number
  fallbackEstimate?: Record<string, any> | null
  direction?: DirectionFormData | null
  onOpenCode?: () => void
}

export default function EvidenceView({
  sessionId,
  refreshKey,
  fallbackEstimate,
  direction,
  onOpenCode,
}: EvidenceViewProps) {
  const { t } = useT()
  const [evidence, setEvidence] = useState<EvidenceModel | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    fetchSessionEvidence(sessionId)
      .then((data) => {
        if (!cancelled) {
          setEvidence(data)
          setLoadError(null)
        }
      })
      .catch((err) => {
        if (!cancelled) setLoadError(err instanceof Error ? err.message : String(err))
      })
    return () => {
      cancelled = true
    }
  }, [sessionId, refreshKey])

  const estimate: Record<string, any> =
    (evidence?.estimate as Record<string, any> | null) ?? fallbackEstimate ?? {}
  const failed = Boolean(
    !evidence?.available &&
      ((evidence?.blockers ?? []).includes('estimate_failed') ||
        estimate?.status === 'error'),
  )
  const missing = !evidence?.available && !failed
  const spec = evidence?.specification ?? null
  const provenance = evidence?.provenance
  const dataset = provenance?.dataset ?? null
  const blockers = evidence?.blockers ?? []
  const statCards = [
    { label: t('evidenceView.statCoef'), kind: 'coef', value: estimate?.coef, testId: 'evidence-coef' },
    { label: t('evidenceView.statSe'), kind: 'se', value: estimate?.se, testId: 'evidence-se' },
    { label: t('evidenceView.statP'), kind: 'p', value: estimate?.p, testId: 'evidence-p' },
    { label: t('evidenceView.statN'), kind: 'n', value: estimate?.n, testId: 'evidence-n' },
  ] as const

  const specLabel =
    [
      spec?.method,
      spec?.dv && spec?.iv ? `${spec.dv} ~ ${spec.iv}` : null,
      Array.isArray(spec?.controls) && spec.controls.length
        ? `controls: ${spec.controls.join(', ')}`
        : typeof spec?.controls === 'string' && spec.controls
          ? `controls: ${spec.controls}`
          : null,
    ]
      .filter(Boolean)
      .join(' · ') || null

  const chips = [
    spec?.method ? String(spec.method) : null,
    estimate?.formula ? String(estimate.formula) : null,
    spec?.dv && spec?.iv ? `${spec.dv} ~ ${spec.iv}` : null,
    Array.isArray(spec?.controls) && spec.controls.length
      ? `controls ${spec.controls.join(', ')}`
      : typeof spec?.controls === 'string' && spec.controls
        ? `controls ${spec.controls}`
        : null,
  ].filter((chip): chip is string => Boolean(chip))

  const tableSource =
    (typeof evidence?.results === 'string' && evidence.results.trim()
      ? evidence.results
      : null) ??
    (typeof estimate?.results === 'string' && estimate.results.trim()
      ? estimate.results
      : null) ??
    normalizeEstimateTableSource(estimate?.table_rows) ??
    normalizeEstimateTableSource(estimate?.treatment_row)
  const tableRows = parseEstimateRows(tableSource)
  const codeArtifacts = Array.isArray(provenance?.code) ? provenance.code : []
  const hasCodeArtifact = codeArtifacts.length > 0

  const none = t('legacy.none')
  const detailRows: Array<{ label: string; value: string }> = direction
    ? [
        { label: t('evidenceView.dv'), value: direction.dv || '—' },
        { label: t('evidenceView.iv'), value: direction.iv || '—' },
        {
          label: t('evidenceView.controls'),
          value: direction.controls.length > 0 ? direction.controls.join(', ') : '—',
        },
        { label: t('evidenceView.method'), value: direction.method || '—' },
        { label: t('evidenceView.template'), value: direction.template || '—' },
      ]
    : []

  const specValue = (raw: unknown): string | null => {
    if (raw == null || raw === '') return null
    return String(raw)
  }

  const layers: ProvenanceLayer[] = [
    {
      id: 'result',
      title: t('legacy.result'),
      detail: (
        <span className="font-mono tabular-nums">
          β {formatStatValue(estimate?.coef, 'coef')}
          {estimate?.treatment ? ` · ${String(estimate.treatment)}` : ''}
        </span>
      ),
      present: estimate?.coef != null || Boolean(estimate?.treatment_row),
    },
    {
      id: 'specification',
      title: t('legacy.specification'),
      detail: <span>{specLabel ?? none}</span>,
      present: Boolean(specLabel),
    },
    {
      id: 'estimator',
      title: t('legacy.estimator'),
      detail: (
        <span>
          {estimate?.estimator ? String(estimate.estimator) : none}
          {estimate?.formula ? ` · ${String(estimate.formula)}` : ''}
        </span>
      ),
      present: Boolean(estimate?.estimator),
    },
    {
      id: 'run',
      title: t('legacy.run'),
      detail: (
        <span>
          {provenance?.run_id ? (
            <>
              <a
                data-testid="evidence-run-link"
                className="text-wb-primary underline-offset-2 hover:underline"
                href={provenance.run_events_url ?? '#'}
              >
                {provenance.run_id.slice(0, 12)}
              </a>
              {provenance.run_status ? ` · ${provenance.run_status}` : ''}
            </>
          ) : (
            none
          )}
          {provenance?.trace_events?.length
            ? ` · ${t('evidenceView.traceEvents', { n: provenance.trace_events.length })}`
            : ''}
        </span>
      ),
      present: Boolean(provenance?.run_id),
    },
    {
      id: 'dataset',
      title: t('legacy.dataset'),
      detail: (
        <span>
          {dataset
            ? `${dataset.name ?? t('evidenceView.unnamed')}${dataset.role ? ` · ${dataset.role}` : ''} · ${t(
                'evidenceView.rowsCols',
                { rows: dataset.rows ?? '?', cols: dataset.columns?.length ?? 0 },
              )}`
            : none}
        </span>
      ),
      present: Boolean(dataset?.path || dataset?.hash || dataset?.version),
    },
    {
      id: 'code',
      title: t('legacy.code'),
      detail: (
        <span>
          {hasCodeArtifact ? (
            <button
              type="button"
              data-testid="evidence-code-link"
              onClick={onOpenCode}
              className="text-wb-primary underline-offset-2 hover:underline"
            >
              {t('evidenceView.viewCode')}
            </button>
          ) : (
            none
          )}
        </span>
      ),
      present: hasCodeArtifact,
    },
  ]
  const presentCount = layers.filter((layer) => layer.present).length
  const missingLayers = layers.filter((layer) => !layer.present).map((layer) => layer.title)
  const fullyTraceable = missingLayers.length === 0

  return (
    <div data-testid="evidence-view" className="wb-pane-enter mx-auto max-w-[52rem] px-6 py-8 sm:px-8">
      <header className="mb-5">
        <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-wb-faint">
          {t('legacy.evidenceKicker')}
        </p>
        {evidence?.claim || fallbackEstimate != null ? (
          <h2 data-testid="evidence-claim" className="mt-1.5 font-serif text-[1.3rem] leading-snug text-wb-ink">
            {evidence?.claim
              ? t('evidenceView.currentClaim', { text: claimLabel(evidence.claim) })
              : t('evidenceView.mainRecorded')}
          </h2>
        ) : (
          <h2 className="mt-1.5 font-serif text-[1.3rem] leading-snug text-wb-ink">
            {t('evidenceView.mainEvidence')}
          </h2>
        )}
      </header>

      {failed ? (
        <div
          data-testid="evidence-failed"
          className="mb-4 rounded-lg border border-wb-danger/30 bg-wb-danger-soft px-4 py-3 text-[13px] leading-6 text-wb-danger"
        >
          {t('evidenceView.estimateFailed')}
        </div>
      ) : null}
      {missing ? (
        <div
          data-testid="evidence-missing"
          className="mb-4 rounded-lg border border-wb-line bg-wb-surface px-4 py-3 text-[13px] leading-6 text-wb-muted"
        >
          {t('evidenceView.noMain')}
        </div>
      ) : null}
      {loadError ? (
        <p data-testid="evidence-load-error" className="mb-3 text-xs text-wb-warning">
          {t('evidenceView.unreadable', { error: loadError })}
        </p>
      ) : null}

      {chips.length > 0 && (
        <div data-testid="evidence-chips" className="mb-4 flex flex-wrap gap-1.5">
          {chips.map((chip, index) => (
            <span
              key={`${index}-${chip}`}
              className="rounded-full border border-wb-line bg-wb-subtle px-2.5 py-0.5 font-mono text-[11px] text-wb-muted"
            >
              {chip}
            </span>
          ))}
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_240px]">
        {/* 左：数字 + 回归表 + 设定详情 */}
        <div className="min-w-0 space-y-4">
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
            {statCards.map(({ label, kind, value, testId }) => (
              <div
                key={testId}
                data-testid={testId}
                title={value != null ? String(value) : undefined}
                className="rounded-lg border border-wb-line bg-wb-surface px-3 py-2.5"
              >
                <p className="font-mono text-[10px] uppercase tracking-[0.1em] text-wb-faint">
                  {label}
                </p>
                <p className="mt-0.5 font-mono text-lg tabular-nums text-wb-ink">
                  {formatStatValue(value, kind)}
                </p>
              </div>
            ))}
          </div>

          <section
            data-testid="evidence-table"
            className="rounded-lg border border-wb-line bg-wb-surface px-4 py-3.5"
          >
            <h3 className="text-[13px] font-semibold text-wb-ink">{t('evidenceView.regression')}</h3>
            {tableRows.length > 0 ? (
              <div className="mt-2 overflow-x-auto">
                <table className="w-full border-collapse text-left">
                  <thead>
                    <tr className="border-b border-wb-line-strong text-[11px] text-wb-muted">
                      <th className="py-1.5 pr-3 font-medium">{t('overview.variable')}</th>
                      <th className="py-1.5 pr-3 text-right font-medium">{t('overview.coef')}</th>
                      <th className="py-1.5 pr-3 text-right font-medium">{t('overview.se')}</th>
                      <th className="py-1.5 text-right font-medium">{t('overview.p')}</th>
                    </tr>
                  </thead>
                  <tbody className="font-mono text-[12.5px] tabular-nums text-wb-ink">
                    {tableRows.map((row) => (
                      <tr key={`${row.variable}-${row.coef}`} className="border-b border-wb-line last:border-0">
                        <td className="py-1.5 pr-3">{row.variable}</td>
                        <td className="py-1.5 pr-3 text-right">{row.coef}</td>
                        <td className="py-1.5 pr-3 text-right">{row.se}</td>
                        <td className="py-1.5 text-right">{row.p}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="mt-2 text-[12.5px] text-wb-muted">
                {failed ? t('evidenceView.noTableFailed') : t('evidenceView.noTable')}
              </p>
            )}
            <div className="mt-3 flex flex-wrap gap-x-5 gap-y-1 border-t border-wb-line pt-2.5 text-[12px] text-wb-muted">
              <span data-testid="evidence-identification">
                {t('evidenceView.identification')}：
                {evidence?.identification?.failed
                  ? t('evidenceView.identFail')
                  : evidence?.identification?.report
                    ? `${t('evidenceView.identPass')}（${
                        evidence?.identification?.star_rating != null
                          ? '★'.repeat(evidence.identification.star_rating) +
                            '☆'.repeat(3 - evidence.identification.star_rating)
                          : '—'
                      }）`
                    : t('evidenceView.identNone')}
              </span>
              <span data-testid="evidence-robustness">
                {t('evidenceView.robustness')}：
                {evidence?.robustness?.ran
                  ? evidence?.robustness?.status === 'degraded'
                    ? t('evidenceView.robustDegraded')
                    : t('evidenceView.robustRan')
                  : t('evidenceView.identNone')}
              </span>
            </div>
          </section>

          <section
            data-testid="evidence-spec-details"
            className="rounded-lg border border-wb-line bg-wb-surface px-4 py-3.5"
          >
            <h3 className="text-[13px] font-semibold text-wb-ink">{t('evidenceView.specDetails')}</h3>
            {detailRows.length > 0 ? (
              <dl className="mt-2 grid grid-cols-1 gap-x-6 gap-y-1.5 text-[12.5px] sm:grid-cols-[auto_1fr]">
                {detailRows.map((row) => (
                  <div key={row.label} className="contents">
                    <dt className="text-wb-muted sm:w-20">{row.label}</dt>
                    <dd className="font-mono text-wb-ink">{row.value}</dd>
                  </div>
                ))}
              </dl>
            ) : (
              <p data-testid="evidence-spec" className="mt-2 font-mono text-xs leading-6 text-wb-muted">
                {specLabel ?? none}
              </p>
            )}
            {spec ? (
              <p className="mt-2 border-t border-wb-line pt-2 text-[11px] leading-5 text-wb-faint">
                {[
                  specValue(spec.method) && `method: ${String(spec.method)}`,
                  specValue(spec.dv) && specValue(spec.iv) && `dv ~ iv: ${String(spec.dv)} ~ ${String(spec.iv)}`,
                ]
                  .filter(Boolean)
                  .join(' · ')}
              </p>
            ) : null}
          </section>

          {blockers.length > 0 ? (
            <p data-testid="evidence-blockers" className="font-mono text-[11px] text-wb-warning">
              blockers: {blockers.join(' · ')}
            </p>
          ) : null}
        </div>

        {/* 右：Result Provenance 溯源链时间线 */}
        <aside
          data-testid="evidence-provenance"
          aria-label={t('evidenceView.ariaProvenance')}
          className="rounded-lg border border-wb-line bg-wb-surface px-3.5 py-3.5"
        >
          <h3 className="text-[13px] font-semibold text-wb-ink">{t('evidenceView.provenanceTitle')}</h3>
          <p className="mt-0.5 text-[11px] leading-4 text-wb-faint">
            {t('evidenceView.provenanceLead')}
            {estimate?.coef != null ? `：β ${formatStatValue(estimate.coef, 'coef')}` : ''}。
          </p>
          <ol className="mt-3">
            {layers.map((layer, index) => (
              <li
                key={layer.id}
                data-layer={layer.id}
                data-present={layer.present}
                className="relative flex gap-2.5 pb-3 last:pb-0"
              >
                {index < layers.length - 1 && (
                  <span
                    aria-hidden
                    className={`absolute left-[8px] top-[20px] h-[calc(100%-16px)] w-px ${
                      layer.present ? 'bg-wb-success/45' : 'bg-wb-line'
                    }`}
                  />
                )}
                <span
                  aria-hidden
                  className={`mt-0.5 flex h-[17px] w-[17px] shrink-0 items-center justify-center rounded-full border text-[9px] font-semibold ${
                    layer.present
                      ? 'border-wb-success/60 bg-wb-success-soft text-wb-success'
                      : 'border-wb-line-strong bg-wb-subtle text-wb-faint'
                  }`}
                >
                  {index + 1}
                </span>
                <div className="min-w-0 flex-1">
                  <p
                    className={`text-[12px] font-medium leading-4 ${
                      layer.present ? 'text-wb-ink' : 'text-wb-faint'
                    }`}
                  >
                    {layer.title}
                  </p>
                  <p className="mt-0.5 break-words text-[11px] leading-4 text-wb-muted">
                    {layer.detail}
                  </p>
                </div>
              </li>
            ))}
          </ol>
          <div
            data-testid="evidence-traceability"
            data-fully-traceable={fullyTraceable}
            className={`mt-2 rounded-md border px-3 py-2 text-[11.5px] leading-5 ${
              fullyTraceable
                ? 'border-wb-success/35 bg-wb-success-soft text-wb-success'
                : 'border-wb-line bg-wb-subtle text-wb-muted'
            }`}
          >
            {fullyTraceable ? (
              <p>
                <span className="font-semibold">{t('evidenceView.fullyTraceable')}</span>
                <br />
                {t('evidenceView.fullyTraceableBody')}
              </p>
            ) : (
              <p>
                <span className="font-semibold">
                  {t('evidenceView.traceability', {
                    present: presentCount,
                    total: layers.length,
                  })}
                </span>
                <br />
                {t('evidenceView.missingLayers', { layers: missingLayers.join('、') })}
              </p>
            )}
          </div>
        </aside>
      </div>
    </div>
  )
}
