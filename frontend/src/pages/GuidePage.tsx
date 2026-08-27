import UnauthHeader from '../components/UnauthHeader'
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
  { n: '1', titleKey: 'guide.step1Title', bodyKey: 'guide.step1Body' },
  { n: '2', titleKey: 'guide.step2Title', bodyKey: 'guide.step2Body' },
  { n: '3', titleKey: 'guide.step3Title', bodyKey: 'guide.step3Body' },
] as const

function scrollToId(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
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
        <section className="mx-auto flex max-w-[760px] flex-col items-center px-6 pb-20 pt-16 text-center sm:pt-24">
          <p className="inline-flex items-center rounded-full border border-border bg-cream px-3.5 py-1 text-[12px] text-muted">
            {t('guide.badge')}
          </p>
          <h1 className="mt-6 font-serif text-[2.5rem] leading-[1.12] tracking-tight text-ink sm:text-[3.25rem] lg:text-[4.5rem]">
            {t('guide.heading')}
          </h1>
          <p className="mt-5 font-serif text-[1.35rem] italic leading-snug text-muted sm:text-[1.5rem]">
            {t('guide.tagline')}
          </p>
          <p className="mt-6 max-w-[38em] text-[16px] leading-7 text-ink/80">{t('guide.lead')}</p>
          <p className="mt-3 max-w-[36em] text-[15px] leading-7 text-muted">{t('guide.sub')}</p>

          <div className="mt-10 flex flex-col items-center gap-3 sm:flex-row">
            <button
              type="button"
              data-testid="guide-upload-btn"
              onClick={onPickData}
              disabled={uploading}
              className="rounded-full bg-accent px-6 py-3 text-[15px] text-white transition-opacity duration-200 hover:opacity-90 disabled:opacity-50"
            >
              {uploading ? t('app.uploading') : t('guide.haveData')}
              {!uploading && <span aria-hidden> →</span>}
            </button>
            <button
              type="button"
              data-testid="guide-sample-btn"
              onClick={onTrySample}
              disabled={uploading}
              className="rounded-full border border-border bg-white px-6 py-3 text-[15px] text-ink transition-colors duration-200 hover:bg-cream disabled:opacity-50"
            >
              {t('guide.trySample')}
            </button>
          </div>

          <button
            type="button"
            data-testid="guide-write-paper"
            onClick={onWritePaper}
            className="mt-5 text-[13px] text-muted transition-colors duration-200 hover:text-ink"
          >
            {t('guide.writePaper')}
          </button>

          {uploadError && (
            <p data-testid="upload-error" className="mt-4 text-sm text-danger">
              {uploadError}
            </p>
          )}

          <ul className="mt-10 flex flex-wrap items-center justify-center gap-x-5 gap-y-2 text-[13px] text-muted">
            <li className="inline-flex items-center gap-1.5">
              <span aria-hidden className="text-ink/40">✓</span>
              {t('guide.trustTable')}
            </li>
            <li className="hidden h-3 w-px bg-border sm:block" aria-hidden />
            <li className="inline-flex items-center gap-1.5">
              <span aria-hidden className="font-mono text-[11px] text-ink/40">{'<>'}</span>
              {t('guide.trustCode')}
            </li>
            <li className="hidden h-3 w-px bg-border sm:block" aria-hidden />
            <li className="inline-flex items-center gap-1.5">
              <span aria-hidden className="text-ink/40">✦</span>
              {t('guide.trustWrite')}
            </li>
          </ul>
        </section>

        <section className="border-y border-border bg-panel px-6 py-14 text-center">
          <div className="mx-auto grid max-w-[900px] gap-10 sm:grid-cols-3">
            <div>
              <p className="font-mono text-[1.15rem] text-accent sm:text-[1.25rem]">{t('guide.statMethods')}</p>
              <p className="mt-2 text-[13px] text-muted">{t('guide.statMethodsLabel')}</p>
            </div>
            <div>
              <p className="font-mono text-[1.15rem] text-accent sm:text-[1.25rem]">{t('guide.statOrder')}</p>
              <p className="mt-2 text-[13px] text-muted">{t('guide.statOrderLabel')}</p>
            </div>
            <div>
              <p className="font-mono text-[1.15rem] text-accent sm:text-[1.25rem]">{t('guide.statExport')}</p>
              <p className="mt-2 text-[13px] text-muted">{t('guide.statExportLabel')}</p>
            </div>
          </div>
        </section>

        <section id="how-it-works" className="scroll-mt-20 mx-auto max-w-[960px] px-6 py-20">
          <p className="text-center font-sans text-[11px] uppercase tracking-[0.18em] text-muted">
            {t('guide.kicker')}
          </p>
          <ol data-testid="guide-steps" className="mt-12 grid gap-8 sm:grid-cols-3 sm:gap-10">
            {STEPS.map((step) => (
              <li key={step.n} className="text-center sm:text-left">
                <span className="font-mono text-[13px] text-accent">{step.n}</span>
                <h2 className="mt-3 font-serif text-[1.35rem] leading-snug text-ink">{t(step.titleKey)}</h2>
                <p className="mt-2 text-[14px] leading-6 text-muted">{t(step.bodyKey)}</p>
              </li>
            ))}
          </ol>
        </section>

        <section id="landing-preview" className="scroll-mt-20 border-t border-border bg-cream/60 px-6 py-20">
          <div className="mx-auto max-w-[760px] text-center">
            <p className="text-[11px] uppercase tracking-[0.18em] text-muted">{t('guide.samplesKicker')}</p>
            <h2 className="mt-3 font-serif text-[2rem] leading-tight text-ink sm:text-[2.35rem]">
              {t('guide.samplesTitle')}
            </h2>
            <p className="mx-auto mt-4 max-w-[36em] text-[15px] leading-7 text-muted">{t('guide.samplesBody')}</p>
          </div>

          <div className="mx-auto mt-12 max-w-[720px] overflow-hidden rounded-lg border border-border bg-panel">
            <div className="flex items-center gap-2 border-b border-border bg-cream px-4 py-2.5">
              <span className="h-2.5 w-2.5 rounded-full bg-border" />
              <span className="h-2.5 w-2.5 rounded-full bg-border" />
              <span className="h-2.5 w-2.5 rounded-full bg-border" />
              <span className="ml-3 rounded-md bg-bg px-3 py-0.5 font-mono text-[11px] text-muted">
                econpaper / desk
              </span>
            </div>
            <div className="px-8 py-10 text-center">
              <p className="inline-flex rounded-full border border-border px-3 py-1 text-[11px] uppercase tracking-[0.14em] text-muted">
                {t('guide.previewKicker')}
              </p>
              <p className="mt-5 font-serif text-[1.65rem] leading-snug text-ink">{t('guide.previewTitle')}</p>
              <p className="mt-3 text-[14px] text-muted">
                {t('guide.previewMethod')} · {t('guide.previewClaim')}
              </p>
              <div className="mx-auto mt-8 max-w-md overflow-hidden rounded-lg border border-border text-left font-mono text-[12px] leading-6">
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
              <p className="mt-6 text-[12px] text-muted">{t('guide.previewNote')}</p>
            </div>
          </div>
        </section>

        <section className="px-6 py-20 text-center">
          <h2 className="font-serif text-[2rem] leading-tight text-ink sm:text-[2.35rem]">{t('guide.footerTitle')}</h2>
          <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <button
              type="button"
              onClick={onPickData}
              disabled={uploading}
              className="rounded-full bg-accent px-6 py-3 text-[15px] text-white transition-opacity duration-200 hover:opacity-90 disabled:opacity-50"
            >
              {uploading ? t('app.uploading') : t('guide.haveData')}
            </button>
            <button
              type="button"
              onClick={onTrySample}
              disabled={uploading}
              className="rounded-full border border-border bg-white px-6 py-3 text-[15px] text-ink transition-colors duration-200 hover:bg-cream disabled:opacity-50"
            >
              {t('guide.trySample')}
            </button>
          </div>
        </section>
      </main>
    </div>
  )
}
