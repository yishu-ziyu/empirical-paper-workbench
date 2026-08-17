// 方向提交后的读数台：主张、星、主表、文献、开写阻断。
// 没有主表时结果章不许假装已经有数字。

export interface InstrumentReadoutProps {
  claim?: string | null
  starRating?: number | null
  treatmentRow?: string | null
  results?: string | null
  literatureSource?: string | null
  writeBlockers?: string[]
  identificationFailed?: boolean
}

function starLabel(star: number | null | undefined): string {
  if (star === 0) return '0'
  if (star == null) return 'NONE'
  return String(star)
}

export default function InstrumentReadout({
  claim,
  starRating,
  treatmentRow,
  results,
  literatureSource,
  writeBlockers = [],
  identificationFailed = false,
}: InstrumentReadoutProps) {
  const table = treatmentRow || ''
  const blocked = identificationFailed || writeBlockers.length > 0

  return (
    <section
      data-testid="instrument-readout"
      className="mb-6 rounded border border-border bg-panel p-4"
    >
      <h2 className="mb-3 font-mono text-xs uppercase tracking-wider text-muted">
        读数
      </h2>
      <dl className="grid grid-cols-2 gap-3 text-xs sm:grid-cols-3">
        <div>
          <dt className="font-mono uppercase tracking-wider text-muted">Claim</dt>
          <dd data-testid="readout-claim" className="mt-1 text-ink">
            {claim || '—'}
          </dd>
        </div>
        <div>
          <dt className="font-mono uppercase tracking-wider text-muted">Star</dt>
          <dd data-testid="readout-star" className="mt-1 font-mono text-ink">
            {starLabel(starRating)}
          </dd>
        </div>
        <div>
          <dt className="font-mono uppercase tracking-wider text-muted">Lit</dt>
          <dd data-testid="readout-lit" className="mt-1 text-ink">
            {literatureSource || '—'}
          </dd>
        </div>
      </dl>
      <div className="mt-3">
        <div className="font-mono text-xs uppercase tracking-wider text-muted">
          Table
        </div>
        {table ? (
          <pre
            data-testid="readout-table"
            className="mt-1 overflow-x-auto rounded bg-paper p-2 font-mono text-xs text-ink"
          >
            {table}
          </pre>
        ) : (
          <p data-testid="readout-table-empty" className="mt-1 text-xs text-muted">
            还没有主表。结果章不能写。
          </p>
        )}
        {results && !table ? (
          <pre className="mt-2 overflow-x-auto whitespace-pre-wrap rounded bg-paper p-2 font-mono text-[11px] text-muted">
            {results}
          </pre>
        ) : null}
      </div>
      {blocked && (
        <p
          data-testid="readout-block"
          className="mt-3 font-mono text-xs text-warning"
        >
          {identificationFailed
            ? '0 星：先改研究设计。'
            : writeBlockers.join(' · ')}
        </p>
      )}
    </section>
  )
}
