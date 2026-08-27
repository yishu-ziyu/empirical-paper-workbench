import UnauthHeader from '../components/UnauthHeader'
import WorkspacePreview from '../components/WorkspacePreview'
import { useT } from '../lib/i18n'

export interface GuidePageProps {
  uploading?: boolean
  uploadError?: string | null
  onPickData: () => void
  onTrySample: () => void
  onWritePaper: () => void
  onLogin?: () => void
  onRegister?: () => void
}

const STEPS = [
  { n: '01', titleKey: 'guide.step1Title', bodyKey: 'guide.step1Body' },
  { n: '02', titleKey: 'guide.step2Title', bodyKey: 'guide.step2Body' },
  { n: '03', titleKey: 'guide.step3Title', bodyKey: 'guide.step3Body' },
] as const

function scrollToId(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function StepIcon({ n }: { n: string }) {
  return (
    <span className="relative inline-flex h-14 w-14 items-center justify-center rounded-full bg-cream text-ink">
      <svg className="h-6 w-6 text-ink/70" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} aria-hidden>
        {n === '01' && (
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
        )}
        {n === '02' && (
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-7 8h8a2 2 0 002-2V6a2 2 0 00-2-2H8a2 2 0 00-2 2v12a2 2 0 002 2z" />
        )}
        {n === '03' && (
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 7.5h18M3 12h12M3 16.5h8" />
        )}
      </svg>
      <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-accent font-mono text-[10px] text-white">
        {n}
      </span>
    </span>
  )
}

export default function GuidePage({
  uploading = false,
  uploadError = null,
  onPickData,
  onTrySample,
  onWritePaper,
  onLogin,
  onRegister,
}: GuidePageProps) {
  const { t } = useT()

  return (
    <div data-testid="guide-page" className="min-h-screen bg-bg text-ink">
      <UnauthHeader
        onLogin={onLogin}
        onRegister={onRegister}
        onHow={() => scrollToId('how-it-works')}
        onPreview={() => scrollToId('landing-preview')}
      />

      <main>
        <section className="mx-auto flex max-w-[880px] flex-col items-center px-6 pb-16 pt-20 text-center sm:pt-28">
          <p className="inline-flex items-center rounded-full border border-border bg-panel px-3.5 py-1 text-[12px] text-muted">
            {t('guide.badge')}
          </p>
          <h1 className="mt-8 font-serif text-[2.75rem] leading-[1.08] tracking-tight text-ink sm:text-[4rem] lg:text-[4.75rem]">
            {t('guide.heading')}
          </h1>
          <p className="mt-6 font-serif text-[1.45rem] italic leading-snug text-muted sm:text-[1.75rem]">
            {t('guide.tagline')}
          </p>
          <p className="mt-7 max-w-[34em] text-[17px] leading-8 text-ink/80">{t('guide.lead')}</p>
          <p className="mt-3 max-w-[32em] text-[15px] leading-7 text-muted">{t('guide.sub')}</p>

          <div className="mt-12 flex w-full max-w-[28rem] flex-col items-center gap-3 sm:max-w-none sm:flex-row sm:justify-center">
            <button
              type="button"
              data-testid="guide-upload-btn"
              onClick={onPickData}
              disabled={uploading}
              className="w-full rounded-lg bg-accent px-7 py-3.5 text-[15px] font-medium text-white transition-opacity duration-200 hover:opacity-90 disabled:opacity-50 sm:w-auto"
            >
              {uploading ? t('app.uploading') : t('guide.haveData')}
              {!uploading && <span aria-hidden> →</span>}
            </button>
            <button
              type="button"
              data-testid="guide-sample-btn"
              onClick={onTrySample}
              disabled={uploading}
              className="w-full rounded-lg border border-border bg-panel px-7 py-3.5 text-[15px] text-ink transition-colors duration-200 hover:bg-cream disabled:opacity-50 sm:w-auto"
            >
              {t('guide.trySample')}
            </button>
          </div>

          <button
            type="button"
            className="mt-8 w-full max-w-[36rem] rounded-lg border border-dashed border-border bg-panel/70 px-6 py-8 text-center transition-colors hover:border-accent/40 hover:bg-panel"
            onClick={onPickData}
            disabled={uploading}
          >
            <svg className="mx-auto h-8 w-8 text-muted" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} aria-hidden>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
            </svg>
            <p className="mt-3 text-[14px] text-ink">{t('workbench.dropBody')}</p>
            <p className="mt-1 text-[12px] text-muted">{t('workbench.dropFormats')}</p>
          </button>

          <button
            type="button"
            data-testid="guide-write-paper"
            onClick={onWritePaper}
            className="mt-6 text-[14px] text-muted underline-offset-4 transition-colors duration-200 hover:text-ink hover:underline"
          >
            {t('guide.writePaper')}
          </button>

          {uploadError && (
            <p data-testid="upload-error" className="mt-4 text-sm text-danger">
              {uploadError}
            </p>
          )}

          <ul className="mt-12 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-[13px] text-muted">
            <li className="inline-flex items-center gap-1.5">
              <span aria-hidden className="text-accent">✓</span>
              {t('guide.trustTable')}
            </li>
            <li className="hidden h-3 w-px bg-border sm:block" aria-hidden />
            <li className="inline-flex items-center gap-1.5">
              <span aria-hidden className="font-mono text-[11px] text-accent">{'<>'}</span>
              {t('guide.trustCode')}
            </li>
            <li className="hidden h-3 w-px bg-border sm:block" aria-hidden />
            <li className="inline-flex items-center gap-1.5">
              <span aria-hidden className="text-accent">✦</span>
              {t('guide.trustWrite')}
            </li>
          </ul>
        </section>

        <section className="border-y border-border bg-cream px-6 py-16 text-center">
          <div className="mx-auto grid max-w-[960px] gap-12 sm:grid-cols-3">
            <div>
              <p className="font-mono text-[1.35rem] tracking-tight text-ink sm:text-[1.5rem]">{t('guide.statMethods')}</p>
              <p className="mt-2 text-[13px] text-muted">{t('guide.statMethodsLabel')}</p>
            </div>
            <div>
              <p className="font-serif text-[1.7rem] italic text-ink">{t('guide.statOrder')}</p>
              <p className="mt-2 text-[13px] text-muted">{t('guide.statOrderLabel')}</p>
            </div>
            <div>
              <p className="font-mono text-[1.35rem] text-ink sm:text-[1.5rem]">{t('guide.statExport')}</p>
              <p className="mt-2 text-[13px] text-muted">{t('guide.statExportLabel')}</p>
            </div>
          </div>
        </section>

        <section id="how-it-works" className="scroll-mt-24 mx-auto max-w-[1080px] px-6 py-24">
          <p className="text-center font-mono text-[11px] uppercase tracking-[0.2em] text-muted">
            {t('guide.kicker')}
          </p>
          <ol data-testid="guide-steps" className="mt-14 grid gap-12 sm:grid-cols-3 sm:gap-8">
            {STEPS.map((step) => (
              <li key={step.n} className="flex flex-col items-center text-center sm:items-start sm:text-left">
                <StepIcon n={step.n} />
                <h2 className="mt-5 font-serif text-[1.55rem] leading-snug text-ink">{t(step.titleKey)}</h2>
                <p className="mt-3 text-[15px] leading-7 text-muted">{t(step.bodyKey)}</p>
              </li>
            ))}
          </ol>
        </section>

        <section id="landing-preview" className="scroll-mt-24 border-t border-border bg-cream/80 px-6 py-24">
          <div className="mx-auto max-w-[760px] text-center">
            <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-muted">{t('guide.samplesKicker')}</p>
            <h2 className="mt-4 font-serif text-[2.15rem] leading-tight text-ink sm:text-[2.6rem]">
              {t('guide.samplesTitle')}
            </h2>
            <p className="mx-auto mt-5 max-w-[34em] text-[16px] leading-8 text-muted">{t('guide.samplesBody')}</p>
          </div>
          <div className="mx-auto mt-14 max-w-[1080px]">
            <WorkspacePreview />
          </div>
        </section>

        <section className="px-6 py-24 text-center">
          <h2 className="font-serif text-[2.15rem] leading-tight text-ink sm:text-[2.6rem]">{t('guide.footerTitle')}</h2>
          <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <button
              type="button"
              onClick={onPickData}
              disabled={uploading}
              className="rounded-lg bg-accent px-7 py-3.5 text-[15px] font-medium text-white transition-opacity duration-200 hover:opacity-90 disabled:opacity-50"
            >
              {uploading ? t('app.uploading') : t('guide.haveData')}
            </button>
            <button
              type="button"
              onClick={onTrySample}
              disabled={uploading}
              className="rounded-lg border border-border bg-panel px-7 py-3.5 text-[15px] text-ink transition-colors duration-200 hover:bg-cream disabled:opacity-50"
            >
              {t('guide.trySample')}
            </button>
          </div>
        </section>
      </main>
    </div>
  )
}
