import { useT } from '../lib/i18n'
import {
  journalCaption,
  journalNotes,
  journalTable,
  journalTd,
  journalTh,
  journalTheadRow,
} from '../lib/paperMarkdown'
import {
  claimLabel,
  literatureLabel,
  parseEstimateRows,
  starHumanLabel,
} from '../lib/readoutTable'

export interface InstrumentReadoutProps {
  claim?: string | null
  starRating?: number | null
  treatmentRow?: string | null
  results?: string | null
  literatureSource?: string | null
  robustnessStatus?: string | null
  writeBlockers?: string[]
  identificationFailed?: boolean
  question?: string | null
}

function robustLabel(status: string | null | undefined): string {
  if (status === 'ran') return '已跑'
  if (status === 'degraded') return '降级'
  return '—'
}

function starsFromP(p: string): string {
  const n = Number(p)
  if (!Number.isFinite(n)) return ''
  if (n < 0.01) return '***'
  if (n < 0.05) return '**'
  if (n < 0.1) return '*'
  return ''
}

export default function InstrumentReadout({
  claim,
  starRating,
  treatmentRow,
  results,
  literatureSource,
  robustnessStatus,
  writeBlockers = [],
  identificationFailed = false,
  question = null,
}: InstrumentReadoutProps) {
  const { t } = useT()
  const fromTreatment = parseEstimateRows(treatmentRow)
  const rows = fromTreatment.length > 0 ? fromTreatment : parseEstimateRows(results)
  const blocked = identificationFailed || writeBlockers.length > 0

  const codeLines = rows.map(
    (row) => `${row.variable.padEnd(12)} ${row.coef}${starsFromP(row.p)}    (${row.se})`,
  )

  return (
    <section data-testid="instrument-readout" className="mb-8 space-y-3">
      {question ? (
        <p
          data-testid="readout-question"
          className="ml-auto max-w-[28em] rounded-[20px] bg-ink px-4 py-2.5 text-[13px] leading-6 text-white"
        >
          {question}
        </p>
      ) : null}

      {codeLines.length > 0 ? (
        <pre data-testid="readout-code" className="code-card">
          {codeLines.join('\n')}
        </pre>
      ) : null}

      <div className="thread-card px-5 py-5">
        <h2 className="font-serif text-[1.35rem] font-semibold tracking-tight text-ink">
          {t('readout.section')}
        </h2>
        <h3 className="mt-5 font-serif text-[1.12rem] font-semibold tracking-tight text-ink">
          {t('readout.main')}
        </h3>
        <div className="mt-4">
          <p className={journalCaption}>{t('readout.caption')}</p>
          {rows.length > 0 ? (
            <>
              <table data-testid="readout-table" className={journalTable}>
                <thead>
                  <tr className={journalTheadRow}>
                    <th className={journalTh}>{t('readout.var')}</th>
                    <th className={`${journalTh} text-center`}>{t('readout.spec')}</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row, r) => (
                    <tr
                      key={`${row.variable}-${row.coef}`}
                      className={`even:bg-[#f6f6f6] ${r === rows.length - 1 ? 'border-b-[2.5px] border-ink' : ''}`}
                    >
                      <td className={`${journalTd} font-semibold`}>{row.variable}</td>
                      <td className={`${journalTd} text-center font-serif tabular-nums`}>
                        <span className="block">
                          {row.coef}
                          {starsFromP(row.p)}
                        </span>
                        <span className="block text-[12.5px] text-ink/60">({row.se})</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className={journalNotes}>{t('readout.notes')}</p>
            </>
          ) : (
            <p data-testid="readout-table-empty" className="mt-2 font-serif text-[15px] leading-7 text-muted">
              {t('readout.empty')}
            </p>
          )}
        </div>
      </div>

      <div className="thread-card px-5 py-5">
        <p className="max-w-[40em] text-justify font-serif text-[15px] leading-[1.9] text-ink/90 indent-[2em]">
          {t('readout.lead')}
        </p>
        <dl className="mt-5 grid grid-cols-2 gap-3 text-xs sm:grid-cols-4">
          <div>
            <dt className="text-muted">{t('readout.claim')}</dt>
            <dd data-testid="readout-claim" className="mt-1 text-ink">
              {claimLabel(claim)}
            </dd>
          </div>
          <div>
            <dt className="text-muted">{t('readout.star')}</dt>
            <dd data-testid="readout-star" className="mt-1 text-ink">
              {starHumanLabel(starRating)}
            </dd>
          </div>
          <div>
            <dt className="text-muted">{t('readout.lit')}</dt>
            <dd data-testid="readout-lit" className="mt-1 text-ink">
              {literatureLabel(literatureSource)}
            </dd>
          </div>
          <div>
            <dt className="text-muted">{t('readout.robust')}</dt>
            <dd data-testid="readout-robust" className="mt-1 text-ink">
              {robustLabel(robustnessStatus)}
            </dd>
          </div>
        </dl>
        {blocked && (
          <p
            data-testid="readout-block"
            className="mt-4 font-mono text-xs text-warning"
          >
            {identificationFailed
              ? '0 星：先改研究设计。'
              : writeBlockers.join(' · ')}
          </p>
        )}
      </div>
    </section>
  )
}
