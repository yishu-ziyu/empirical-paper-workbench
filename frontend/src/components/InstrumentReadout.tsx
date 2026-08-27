import { useT } from '../lib/i18n'
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
  robustnessStatus,
  writeBlockers = [],
  identificationFailed = false,
}: InstrumentReadoutProps) {
  const { t } = useT()
  const fromTreatment = parseEstimateRows(treatmentRow)
  const rows = fromTreatment.length > 0 ? fromTreatment : parseEstimateRows(results)
  const blocked = identificationFailed || writeBlockers.length > 0

  return (
    <section data-testid="instrument-readout" className="mb-8 bg-panel px-1 py-2">
      <h2 className="border-t border-ink/25 pt-3 font-sans text-[1.15rem] font-semibold tracking-tight text-ink">
        {t('readout.section')}
      </h2>
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
      <h3 className="mt-8 font-sans text-[1.05rem] font-semibold tracking-tight text-ink">
        {t('readout.main')}
      </h3>
      <p className="mt-4 max-w-[40em] text-justify font-serif text-[15px] leading-[1.9] text-ink/90 first-line:indent-[2em]">
        {t('readout.lead')}
      </p>
      <div className="mt-6">
        <p className="font-sans text-[13px] font-semibold text-ink">{t('readout.caption')}</p>
        {rows.length > 0 ? (
          <table
            data-testid="readout-table"
            className="mt-2 w-full border-collapse text-left text-[13px] text-ink"
          >
            <thead>
              <tr className="border-t-[1.5px] border-b border-ink">
                <th className="py-2 pr-3 font-sans font-semibold">{t('readout.var')}</th>
                <th className="py-2 pr-3 text-center font-sans font-semibold">{t('readout.coef')}</th>
                <th className="py-2 pr-3 text-center font-sans font-semibold">{t('readout.se')}</th>
                <th className="py-2 text-center font-sans font-semibold">{t('readout.p')}</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={`${row.variable}-${row.coef}`} className="border-b-[1.5px] border-ink">
                  <td className="py-2 pr-3 font-serif">{row.variable}</td>
                  <td className="py-2 pr-3 text-center font-serif tabular-nums">{row.coef}</td>
                  <td className="py-2 pr-3 text-center font-serif tabular-nums">{row.se}</td>
                  <td className="py-2 text-center font-serif tabular-nums">{row.p}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p data-testid="readout-table-empty" className="mt-2 font-serif text-[15px] leading-7 text-muted">
            {t('readout.empty')}
          </p>
        )}
      </div>
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
    </section>
  )
}
