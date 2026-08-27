import UnauthHeader from '../components/UnauthHeader'
import SamplePaperPreview from '../components/SamplePaperPreview'
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
  { n: '04', titleKey: 'guide.step4Title', bodyKey: 'guide.step4Body' },
] as const

const FEATURES = [
  { n: '01', titleKey: 'guide.feat1Title', bodyKey: 'guide.feat1Body' },
  { n: '02', titleKey: 'guide.feat2Title', bodyKey: 'guide.feat2Body' },
  { n: '03', titleKey: 'guide.feat3Title', bodyKey: 'guide.feat3Body' },
] as const

function scrollToId(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function StepIcon({ n }: { n: string }) {
  return (
    <span className="relative inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-[#f3f3f3] text-ink">
      <svg className="h-6 w-6 text-ink/55" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} aria-hidden>
        {n === '01' && (
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
        )}
        {n === '02' && (
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-7 8h8a2 2 0 002-2V6a2 2 0 00-2-2H8a2 2 0 00-2 2v12a2 2 0 002 2z" />
        )}
        {n === '03' && (
          <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456z" />
        )}
        {n === '04' && (
          <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
        )}
      </svg>
      <span className="absolute -right-1.5 -top-1.5 flex h-6 w-6 items-center justify-center rounded-full bg-accent font-sans text-[10px] font-medium text-white">
        {n}
      </span>
    </span>
  )
}

function FeatureIcon({ n }: { n: string }) {
  return (
    <span className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-accent/10 text-accent">
      <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6} aria-hidden>
        {n === '01' && (
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
        )}
        {n === '02' && (
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
        )}
        {n === '03' && (
          <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.076-4.076a1.526 1.526 0 011.037-.443 48.282 48.282 0 005.68-.494c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" />
        )}
      </svg>
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
    <div data-testid="guide-page" className="min-h-screen bg-white text-ink">
      <UnauthHeader
        onLogin={onLogin}
        onRegister={onRegister}
        onHow={() => scrollToId('how-it-works')}
        onPreview={() => scrollToId('landing-preview')}
        onFeatures={() => scrollToId('landing-features')}
      />

      <main>
        <section className="mx-auto flex max-w-[820px] flex-col items-center px-6 pb-24 pt-24 text-center sm:pt-32">
          <p className="inline-flex items-center gap-2 rounded-full bg-[#f3f3f3] px-4 py-1.5 text-[13px] text-[#5c5c5c]">
            <span aria-hidden className="flex h-4 w-4 items-center justify-center rounded-full bg-ink font-serif text-[9px] leading-none text-white">
              e
            </span>
            {t('guide.badge')}
          </p>

          <h1 className="mt-10 font-serif text-[2.6rem] leading-[1.12] tracking-tight text-ink sm:text-[3.75rem] lg:text-[4.35rem]">
            <span className="block">{t('guide.heading')}</span>
            <span className="mt-3 block font-serif text-[1.65rem] leading-snug sm:text-[2.15rem] lg:text-[2.35rem]">
              <span className="text-[#5a6f82]">{t('guide.headlineLine2')}</span>
            </span>
          </h1>

          <p className="mt-7 text-[15px] italic leading-relaxed text-[#7a7a7a] sm:text-[16px]">
            {t('guide.tagline')}
          </p>
          <p className="mt-8 max-w-[38em] text-[15px] leading-7 text-[#6b6b6b]">{t('guide.lead')}</p>
          <p className="mt-3 max-w-[34em] text-[14px] leading-7 text-[#8a8a8a]">{t('guide.sub')}</p>
          <p className="mt-4 max-w-[34em] font-mono text-[12px] leading-6 text-[#8a8a8a]">{t('guide.statMethods')}</p>

          <div className="mt-14 flex w-full max-w-[26rem] flex-col items-center gap-3 sm:max-w-none sm:flex-row sm:justify-center">
            <button
              type="button"
              data-testid="guide-upload-btn"
              onClick={onPickData}
              disabled={uploading}
              className="w-full rounded-full bg-ink px-7 py-3 text-[15px] font-medium text-white transition-opacity duration-200 hover:opacity-90 disabled:opacity-50 sm:w-auto"
            >
              {uploading ? t('app.uploading') : t('guide.haveData')}
            </button>
            <button
              type="button"
              data-testid="guide-sample-btn"
              onClick={onTrySample}
              disabled={uploading}
              className="w-full rounded-full border border-black/15 bg-white px-7 py-3 text-[15px] text-ink transition-colors duration-200 hover:bg-black/[0.03] disabled:opacity-50 sm:w-auto"
            >
              {t('guide.trySample')}
            </button>
          </div>

          <button
            type="button"
            data-testid="guide-write-paper"
            onClick={onWritePaper}
            className="mt-8 text-[14px] text-[#8a8a8a] underline-offset-4 transition-colors duration-200 hover:text-ink hover:underline"
          >
            {t('guide.writePaper')}
          </button>

          {uploadError && (
            <p data-testid="upload-error" className="mt-4 text-sm text-danger">
              {uploadError}
            </p>
          )}
        </section>

        <section id="how-it-works" className="scroll-mt-24 mx-auto max-w-[1120px] px-6 py-28">
          <p className="text-center text-[12px] uppercase tracking-[0.18em] text-[#8a8a8a]">
            {t('guide.kicker')}
          </p>
          <h2 className="mt-4 text-center font-serif text-[2.1rem] leading-tight text-ink sm:text-[2.5rem]">
            {t('guide.howTitle')}
          </h2>
          <ol data-testid="guide-steps" className="mt-16 grid gap-12 sm:grid-cols-2 lg:grid-cols-4 lg:gap-8">
            {STEPS.map((step) => (
              <li key={step.n} className="flex flex-col items-center text-center">
                <StepIcon n={step.n} />
                <h3 className="mt-6 font-serif text-[1.35rem] leading-snug text-ink">{t(step.titleKey)}</h3>
                <p className="mt-3 max-w-[22em] text-[14px] leading-7 text-[#6b6b6b]">{t(step.bodyKey)}</p>
              </li>
            ))}
          </ol>
        </section>

        <section id="landing-preview" className="scroll-mt-24 px-6 py-28">
          <div className="mx-auto max-w-[720px] text-center">
            <p className="text-[12px] uppercase tracking-[0.18em] text-[#8a8a8a]">{t('guide.samplesKicker')}</p>
            <h2 className="mt-4 font-serif text-[2.1rem] leading-tight text-ink sm:text-[2.5rem]">
              {t('guide.samplesTitle')}
            </h2>
            <p className="mx-auto mt-5 max-w-[34em] text-[15px] leading-7 text-[#6b6b6b]">{t('guide.samplesBody')}</p>
          </div>
          <div className="mx-auto mt-14 max-w-[860px]">
            <SamplePaperPreview />
          </div>
          <p className="mx-auto mt-16 max-w-[720px] text-center text-[12px] uppercase tracking-[0.18em] text-[#8a8a8a]">
            {t('guide.deskKicker')}
          </p>
          <div className="mx-auto mt-6 max-w-[1080px]">
            <WorkspacePreview />
          </div>
        </section>

        <section id="landing-features" className="scroll-mt-24 mx-auto max-w-[1080px] px-6 py-28">
          <p className="text-center text-[12px] uppercase tracking-[0.18em] text-[#8a8a8a]">
            {t('guide.featuresKicker')}
          </p>
          <h2 className="mt-4 text-center font-serif text-[2.1rem] leading-tight text-ink sm:text-[2.5rem]">
            {t('guide.featuresTitle')}
          </h2>
          <p className="mx-auto mt-5 max-w-[34em] text-center text-[15px] leading-7 text-[#6b6b6b]">
            {t('guide.featuresLead')}
          </p>
          <ul className="mt-14 grid gap-5 sm:grid-cols-3">
            {FEATURES.map((feat) => (
              <li key={feat.n} className="rounded-xl border border-black/[0.06] bg-white p-6">
                <FeatureIcon n={feat.n} />
                <h3 className="mt-5 font-sans text-[16px] font-semibold text-ink">{t(feat.titleKey)}</h3>
                <p className="mt-2 text-[14px] leading-7 text-[#6b6b6b]">{t(feat.bodyKey)}</p>
              </li>
            ))}
          </ul>
        </section>

        <section className="px-6 py-28 text-center">
          <h2 className="font-serif text-[2.1rem] leading-tight text-ink sm:text-[2.5rem]">{t('guide.footerTitle')}</h2>
          <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <button
              type="button"
              onClick={onPickData}
              disabled={uploading}
              className="rounded-full bg-ink px-7 py-3 text-[15px] font-medium text-white transition-opacity duration-200 hover:opacity-90 disabled:opacity-50"
            >
              {uploading ? t('app.uploading') : t('guide.haveData')}
            </button>
            <button
              type="button"
              onClick={onTrySample}
              disabled={uploading}
              className="rounded-full border border-black/15 bg-white px-7 py-3 text-[15px] text-ink transition-colors duration-200 hover:bg-black/[0.03] disabled:opacity-50"
            >
              {t('guide.trySample')}
            </button>
          </div>
        </section>
      </main>
    </div>
  )
}
