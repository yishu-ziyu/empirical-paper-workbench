import { useT } from '../lib/i18n'
import {
  JournalEquation,
  journalCaption,
  journalNotes,
  journalTable,
  journalTd,
  journalTh,
  journalTheadRow,
} from '../lib/paperMarkdown'

/** Decorative Copaper-style paper face. No live workbench testids. */
export default function SamplePaperPreview() {
  const { t } = useT()

  return (
    <div>
      <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-[13px] text-[#5c5c5c]">
        <span className="rounded-full bg-accent/10 px-2.5 py-0.5 text-[12px] text-accent">
          {t('guide.sampleTagStyle')}
        </span>
        <span>{t('guide.sampleTagField')}</span>
        <span>{t('guide.sampleTagMethods')}</span>
        <span className="ml-auto inline-flex items-center gap-1.5 text-[13px] text-ink/70">
          {t('guide.sampleView')}
        </span>
      </div>

      <div className="mt-5 overflow-hidden rounded-xl border border-black/[0.08] bg-white">
        <div className="flex items-center gap-2 border-b border-black/[0.06] bg-[#fafafa] px-4 py-2.5">
          <span className="h-2.5 w-2.5 rounded-full bg-[#e4e4e4]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#e4e4e4]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#e4e4e4]" />
          <span className="ml-3 font-mono text-[11px] text-[#8a8a8a]">econpaper / paper / course-sample</span>
        </div>
        <article className="journal-page mx-auto max-w-[40em]">
          <p className="text-center">
            <span className="inline-block rounded-full bg-[#f3f3f3] px-3 py-1 font-sans text-[11px] tracking-[0.12em] text-[#6b6b6b]">
              {t('guide.sampleBadge')}
            </span>
          </p>
          <h3 className="mt-6 text-center font-serif text-[1.65rem] leading-snug tracking-tight text-ink sm:text-[1.9rem]">
            {t('guide.previewTitle')}
          </h3>
          <p className="mt-6 text-justify indent-[2em] text-[15.5px] leading-[1.9] text-ink/90">
            {t('guide.sampleExcerpt')}
          </p>

          <h4 className="mb-3 mt-10 font-serif text-[1.35rem] font-semibold text-ink">
            {t('guide.sampleMethods')}
          </h4>
          <h5 className="mb-2 mt-6 font-serif text-[1.12rem] font-semibold text-ink">
            {t('guide.sampleMethodsSub')}
          </h5>
          <p className="text-justify indent-[2em] text-[15.5px] leading-[1.9] text-ink/90">
            {t('guide.sampleMethodsBody')}
          </p>
          <JournalEquation math={t('guide.sampleEq')} number={1} />

          <h4 className="mb-3 mt-10 font-serif text-[1.35rem] font-semibold text-ink">
            {t('guide.sampleResults')}
          </h4>
          <p className="text-justify indent-[2em] text-[15.5px] leading-[1.9] text-ink/90">
            {t('guide.sampleResultsBody')}
          </p>
          <p className={`${journalCaption} mt-6`}>{t('guide.sampleTableCaption')}</p>
          <table className={journalTable}>
            <thead>
              <tr className={journalTheadRow}>
                <th className={journalTh}>{t('readout.var')}</th>
                <th className={`${journalTh} text-center`}>(1)</th>
                <th className={`${journalTh} text-center`}>(2)</th>
              </tr>
            </thead>
            <tbody>
              <tr className="even:bg-[#f6f6f6]">
                <td className={`${journalTd} font-semibold`}>age</td>
                <td className={`${journalTd} text-center font-serif tabular-nums`}>
                  <span className="block">0.124***</span>
                  <span className="block text-[12.5px] text-ink/60">(0.046)</span>
                </td>
                <td className={`${journalTd} text-center font-serif tabular-nums`}>
                  <span className="block">0.118**</span>
                  <span className="block text-[12.5px] text-ink/60">(0.051)</span>
                </td>
              </tr>
              <tr className="even:bg-[#f6f6f6] border-b-[2.5px] border-ink">
                <td className={`${journalTd} font-semibold`}>controls</td>
                <td className={`${journalTd} text-center font-serif`}>No</td>
                <td className={`${journalTd} text-center font-serif`}>Yes</td>
              </tr>
            </tbody>
          </table>
          <p className={journalNotes}>{t('guide.sampleTableNotes')}</p>
        </article>
      </div>
    </div>
  )
}
