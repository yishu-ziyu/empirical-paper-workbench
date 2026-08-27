import { useT } from '../lib/i18n'
import { CLEAN_STEPS, PAPER_NODES } from '../lib/paperPath'

/** Decorative SciSpace-style desk for the landing. No live testids. */
export default function WorkspacePreview() {
  const { t } = useT()
  const chapters = [t('chapter.type.intro'), t('chapter.type.methods'), t('chapter.type.results')]

  return (
    <div className="overflow-hidden rounded-lg border border-border bg-cream">
      <div className="flex items-center gap-2 border-b border-border bg-panel px-4 py-2.5">
        <span className="h-2.5 w-2.5 rounded-full bg-border" />
        <span className="h-2.5 w-2.5 rounded-full bg-border" />
        <span className="h-2.5 w-2.5 rounded-full bg-border" />
        <div className="ml-3 flex items-center gap-1 rounded-full bg-bg p-0.5 text-[11px]">
          <span className="rounded-full bg-accent px-2.5 py-0.5 text-white">{t('workbench.tabPaper')}</span>
          <span className="px-2.5 py-0.5 text-muted">{t('workbench.tabData')}</span>
          <span className="px-2.5 py-0.5 text-muted">{t('workbench.tabFormat')}</span>
        </div>
      </div>
      <div className="grid min-h-[420px] grid-cols-1 lg:grid-cols-[200px_minmax(0,1fr)_240px]">
        <aside className="hidden border-r border-border bg-cream p-4 lg:block">
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
        <section className="bg-bg px-6 py-8 sm:px-10">
          <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-muted">{t('guide.previewKicker')}</p>
          <h3 className="mt-3 font-serif text-[1.45rem] leading-snug text-ink">{t('guide.previewTitle')}</h3>
          <p className="mt-2 text-[13px] text-muted">
            {t('guide.previewMethod')} · {t('guide.previewClaim')}
          </p>
          <div className="mt-6 overflow-hidden rounded-md border border-border bg-panel font-mono text-[12px] leading-6">
            <div className="grid grid-cols-4 bg-cream px-4 py-2 text-muted">
              <span>var</span>
              <span>coef</span>
              <span>se</span>
              <span>p</span>
            </div>
            <div className="grid grid-cols-4 px-4 py-2 text-ink">
              <span>age</span>
              <span>0.124</span>
              <span>0.046</span>
              <span>0.008</span>
            </div>
          </div>
          <p className="mt-5 font-serif text-[15px] leading-[1.8] text-ink/80">{t('guide.previewNote')}</p>
        </section>
        <aside className="hidden border-l border-border bg-cream p-4 lg:block">
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
