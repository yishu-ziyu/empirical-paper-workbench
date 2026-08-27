import { useT } from '../lib/i18n'

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
        <article className="bg-white px-8 py-10 sm:px-14 sm:py-12">
          <p className="text-center">
            <span className="inline-block rounded-full bg-[#f3f3f3] px-3 py-1 font-sans text-[11px] tracking-[0.12em] text-[#6b6b6b]">
              {t('guide.sampleBadge')}
            </span>
          </p>
          <h3 className="mt-6 text-center font-serif text-[1.65rem] leading-snug tracking-tight text-ink sm:text-[1.9rem]">
            {t('guide.previewTitle')}
          </h3>
          <p className="mx-auto mt-6 max-w-[36em] text-justify font-serif text-[15px] leading-[1.9] text-ink/85 first-line:indent-[2em]">
            {t('guide.sampleExcerpt')}
          </p>
          <p className="mt-8 font-sans text-[13px] font-semibold text-ink">{t('readout.caption')}</p>
          <table className="mt-2 w-full border-collapse text-[13px]">
            <thead>
              <tr className="border-t-[1.5px] border-b border-ink">
                <th className="py-2 pr-3 text-left font-sans font-semibold">{t('readout.var')}</th>
                <th className="py-2 pr-3 text-center font-sans font-semibold">(1)</th>
                <th className="py-2 pr-3 text-center font-sans font-semibold">{t('readout.se')}</th>
                <th className="py-2 text-center font-sans font-semibold">{t('readout.p')}</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b-[1.5px] border-ink">
                <td className="py-2 pr-3 font-serif">age</td>
                <td className="py-2 pr-3 text-center font-serif">0.124***</td>
                <td className="py-2 pr-3 text-center font-serif">0.046</td>
                <td className="py-2 text-center font-serif">0.008</td>
              </tr>
            </tbody>
          </table>
        </article>
      </div>
    </div>
  )
}
