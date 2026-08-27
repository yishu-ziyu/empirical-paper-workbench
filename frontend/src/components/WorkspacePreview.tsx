import { useT } from '../lib/i18n'
import {
  journalCaption,
  journalNotes,
  journalTable,
  journalTd,
  journalTh,
  journalTheadRow,
} from '../lib/paperMarkdown'
import { CLEAN_STEPS, PAPER_NODES } from '../lib/paperPath'

/** Landing desk face: Julius upload/results chrome, locked CONTEXT rail. No live testids. */
export default function WorkspacePreview() {
  const { t } = useT()
  const chapters = [t('chapter.type.intro'), t('chapter.type.methods'), t('chapter.type.results')]

  return (
    <div className="overflow-hidden rounded-2xl border border-black/[0.08] bg-[#f7f7f5]">
      <div className="flex items-center gap-2 border-b border-black/[0.06] bg-white px-4 py-2.5">
        <span className="h-2.5 w-2.5 rounded-full bg-[#e4e4e4]" />
        <span className="h-2.5 w-2.5 rounded-full bg-[#e4e4e4]" />
        <span className="h-2.5 w-2.5 rounded-full bg-[#e4e4e4]" />
        <div className="ml-3 flex items-center gap-1 rounded-full bg-[#f3f3f3] p-0.5 text-[11px]">
          <span className="rounded-full bg-accent px-2.5 py-0.5 text-white">{t('workbench.tabPaper')}</span>
          <span className="px-2.5 py-0.5 text-muted">{t('workbench.tabData')}</span>
          <span className="px-2.5 py-0.5 text-muted">{t('workbench.tabFormat')}</span>
        </div>
      </div>
      <div
        className="desk-preview-columns"
        style={{ display: 'grid', gridTemplateColumns: '200px minmax(0, 1fr) 240px' }}
      >
        <aside className="border-r border-black/[0.06] bg-[#f7f7f5] p-4">
          <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-muted">{t('bench.chapters')}</p>
          <ul className="mt-3 space-y-1">
            {chapters.map((title, i) => (
              <li
                key={title}
                className={`rounded-md px-2.5 py-2 font-serif text-[13px] ${
                  i === 0 ? 'bg-accent/10 text-accent' : 'text-ink/80'
                }`}
              >
                {title}
              </li>
            ))}
          </ul>
        </aside>
        <section className="flex flex-col bg-[#fbfbfa] px-5 py-6 sm:px-8">
          <div className="mb-4 inline-flex w-fit items-center gap-2 rounded-full border border-black/[0.08] bg-white px-3 py-1.5 text-[12px] text-ink/80">
            <span className="flex h-5 w-5 items-center justify-center rounded-full bg-black/[0.06] text-[14px] leading-none">+</span>
            course-panel.csv
          </div>
          <p className="ml-auto max-w-[22em] rounded-[20px] bg-ink px-4 py-2.5 text-[13px] leading-6 text-white">
            {t('guide.previewQuestion')}
          </p>
          <pre className="code-card mt-3">age          0.124***    (0.046)</pre>
          <div className="thread-card mt-3 px-4 py-4">
            <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-muted">{t('guide.previewKicker')}</p>
            <h3 className="mt-2 font-serif text-[1.25rem] leading-snug text-ink">{t('guide.previewTitle')}</h3>
            <p className="mt-1 text-[13px] text-muted">
              {t('guide.previewMethod')} · {t('guide.previewClaim')}
            </p>
            <p className={`${journalCaption} mt-4`}>{t('readout.caption')}</p>
            <table className={journalTable}>
              <thead>
                <tr className={journalTheadRow}>
                  <th className={journalTh}>{t('readout.var')}</th>
                  <th className={`${journalTh} text-center`}>(1)</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b-[2.5px] border-ink even:bg-[#f6f6f6]">
                  <td className={`${journalTd} font-semibold`}>age</td>
                  <td className={`${journalTd} text-center font-serif tabular-nums`}>
                    <span className="block">0.124***</span>
                    <span className="block text-[12.5px] text-ink/60">(0.046)</span>
                  </td>
                </tr>
              </tbody>
            </table>
            <p className={journalNotes}>{t('guide.previewNote')}</p>
          </div>
          <div className="thread-card mt-3 px-4 py-4">
            <p className="font-serif text-[14px] leading-7 text-ink/85">1. {t('readout.lead')}</p>
            <p className="mt-2 text-[13px] leading-6 text-muted">{t('guide.statMethods')}</p>
          </div>
          <div className="composer-shell mt-auto flex items-center gap-2 px-3 py-2.5">
            <span className="flex h-8 w-8 items-center justify-center rounded-full border border-black/[0.08] text-[18px] leading-none">+</span>
            <span className="text-[13px] text-muted">{t('workbench.dropBody')}</span>
          </div>
        </section>
        <aside className="border-l border-black/[0.06] bg-[#f7f7f5] p-4">
          <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-muted">{t('bench.steps')}</p>
          <ol className="relative mt-3 ml-1.5 border-l border-border">
            {PAPER_NODES.map((id, i) => (
              <li key={id} className="relative py-1.5 pl-4">
                <span
                  className={`absolute -left-[4px] top-2.5 h-2 w-2 rounded-full ${
                    i < 2 ? 'bg-accent' : i === 2 ? 'bg-warning' : 'bg-border'
                  }`}
                />
                <p className={`font-mono text-[10px] leading-4 ${i <= 2 ? 'text-ink' : 'text-muted'}`}>
                  {t(`path.${id}`)}
                </p>
                {id === 'clean_data' && (
                  <ol className="mt-1 space-y-0.5">
                    {CLEAN_STEPS.map((step) => (
                      <li key={step} className="font-mono text-[10px] leading-4 text-accent">
                        {t(`path.clean.${step}`)}
                      </li>
                    ))}
                  </ol>
                )}
              </li>
            ))}
          </ol>
        </aside>
      </div>
    </div>
  )
}
