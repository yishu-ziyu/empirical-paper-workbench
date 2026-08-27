// 方向提交后的读数台：主张、星、主表、稳健、文献、开写阻断。
// 没有主表时结果章不许假装已经有数字。

import {
  claimLabel,
  literatureLabel,
  parseEstimateRows,
  starHumanLabel,
} from '../lib/readoutTable'

export type LiteratureReadoutEntry = {
  title?: string
  authors?: string[]
  year?: number | null
  url?: string
  stance?: string | null
}

export interface InstrumentReadoutProps {
  claim?: string | null
  starRating?: number | null
  treatmentRow?: string | null
  results?: string | null
  literatureSource?: string | null
  literatureEntries?: LiteratureReadoutEntry[]
  robustnessStatus?: string | null
  writeBlockers?: string[]
  identificationFailed?: boolean
}

function robustLabel(status: string | null | undefined): string {
  if (status === 'ran') return '已跑'
  if (status === 'degraded') return '降级'
  return '—'
}

export default function InstrumentReadout({
  claim,
  starRating,
  treatmentRow,
  results,
  literatureSource,
  literatureEntries = [],
  robustnessStatus,
  writeBlockers = [],
  identificationFailed = false,
}: InstrumentReadoutProps) {
  const fromTreatment = parseEstimateRows(treatmentRow)
  const rows = fromTreatment.length > 0 ? fromTreatment : parseEstimateRows(results)
  const blocked = identificationFailed || writeBlockers.length > 0

  return (
    <section
      data-testid="instrument-readout"
      className="mb-6 rounded border border-border bg-panel p-4"
    >
      <h2 className="mb-3 text-xs tracking-wider text-muted">
        读数
      </h2>
      <dl className="grid grid-cols-2 gap-3 text-xs sm:grid-cols-3">
        <div>
          <dt className="text-muted">主张</dt>
          <dd data-testid="readout-claim" className="mt-1 text-ink">
            {claimLabel(claim)}
          </dd>
        </div>
        <div>
          <dt className="text-muted">识别星级</dt>
          <dd data-testid="readout-star" className="mt-1 text-ink">
            {starHumanLabel(starRating)}
          </dd>
        </div>
        <div>
          <dt className="text-muted">文献来源</dt>
          <dd data-testid="readout-lit" className="mt-1 text-ink">
            {literatureLabel(literatureSource)}
          </dd>
        </div>
        <div>
          <dt className="text-muted">稳健性</dt>
          <dd data-testid="readout-robust" className="mt-1 text-ink">
            {robustLabel(robustnessStatus)}
          </dd>
        </div>
      </dl>
      <div className="mt-3">
        <div className="text-xs text-muted">主估计</div>
        {rows.length > 0 ? (
          <table
            data-testid="readout-table"
            className="mt-1 w-full border-collapse text-left text-xs text-ink"
          >
            <thead>
              <tr className="border-b border-border text-muted">
                <th className="py-1 pr-3 font-normal">变量</th>
                <th className="py-1 pr-3 font-normal">系数</th>
                <th className="py-1 pr-3 font-normal">标准误</th>
                <th className="py-1 font-normal">p 值</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={`${row.variable}-${row.coef}`} className="border-b border-border/60">
                  <td className="py-1 pr-3">{row.variable}</td>
                  <td className="py-1 pr-3 font-mono">{row.coef}</td>
                  <td className="py-1 pr-3 font-mono">{row.se}</td>
                  <td className="py-1 font-mono">{row.p}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p data-testid="readout-table-empty" className="mt-1 text-xs text-muted">
            还没有主表。结果章不能写。
          </p>
        )}
      </div>
      {literatureEntries.length > 0 && (
        <div className="mt-3" data-testid="readout-literature-list">
          <div className="text-xs text-muted">文献</div>
          <ul className="mt-1 space-y-2">
            {literatureEntries.map((entry, index) => {
              const authors = (entry.authors || []).join(', ')
              const head = [authors, entry.year ? `(${entry.year})` : '']
                .filter(Boolean)
                .join(' ')
              const stance =
                entry.stance === '支持' ||
                entry.stance === '不支持' ||
                entry.stance === '说不清'
                  ? entry.stance
                  : null
              const doiUrl =
                entry.url &&
                entry.url.startsWith('https://doi.org/') &&
                entry.url.length > 'https://doi.org/'.length
                  ? entry.url
                  : ''
              return (
                <li
                  key={`${entry.title || 'paper'}-${index}`}
                  className="border-b border-border/60 py-1 last:border-0"
                  data-testid="readout-literature-item"
                >
                  <div className="text-ink">
                    {head ? `${head}. ` : ''}
                    {entry.title || '无题名'}
                  </div>
                  {doiUrl ? (
                    <a
                      className="mt-0.5 block text-accent break-all"
                      href={doiUrl}
                      target="_blank"
                      rel="noreferrer"
                    >
                      {doiUrl}
                    </a>
                  ) : null}
                  {stance ? (
                    <div className="mt-0.5 text-muted">对研究方向：{stance}</div>
                  ) : null}
                </li>
              )
            })}
          </ul>
        </div>
      )}
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
