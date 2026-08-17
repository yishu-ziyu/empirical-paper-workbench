import { useT } from '../lib/i18n'

export interface GuidePageProps {
  uploading?: boolean
  uploadError?: string | null
  onPickData: () => void
  onTrySample: () => void
  onWritePaper: () => void
  onLogin?: () => void
}

const STEPS = [
  { n: '1', titleKey: 'guide.step1Title', bodyKey: 'guide.step1Body' },
  { n: '2', titleKey: 'guide.step2Title', bodyKey: 'guide.step2Body' },
  { n: '3', titleKey: 'guide.step3Title', bodyKey: 'guide.step3Body' },
] as const

export default function GuidePage({
  uploading = false,
  uploadError = null,
  onPickData,
  onTrySample,
  onWritePaper,
  onLogin,
}: GuidePageProps) {
  const { t, lang, setLang } = useT()

  return (
    <div data-testid="guide-page" className="min-h-screen bg-bg text-ink">
      <header className="flex items-center justify-between px-8 py-5">
        <p className="text-[15px] tracking-tight text-ink">{t('app.title')}</p>
        <div className="flex items-center gap-5 text-[13px] text-muted">
          {onLogin && (
            <button
              type="button"
              data-testid="open-login-btn"
              onClick={onLogin}
              className="transition-colors duration-200 hover:text-ink"
            >
              {t('app.login')}
            </button>
          )}
          <button
            type="button"
            onClick={() => setLang(lang === 'zh' ? 'en' : 'zh')}
            className="transition-colors duration-200 hover:text-ink"
          >
            {t('app.langSwitch')}
          </button>
        </div>
      </header>

      <main className="mx-auto flex max-w-[560px] flex-col px-6 pb-24 pt-16 sm:pt-20">
        <p className="font-mono text-[11px] uppercase tracking-[0.16em] text-muted">
          {t('guide.kicker')}
        </p>
        <h1 className="mt-3 font-serif text-[2.25rem] leading-tight tracking-tight text-ink sm:text-[2.5rem]">
          {t('guide.heading')}
        </h1>
        <p className="mt-4 max-w-[34em] text-[16px] leading-7 text-ink">{t('guide.lead')}</p>
        <p className="mt-3 max-w-[34em] text-[15px] leading-7 text-muted">{t('guide.sub')}</p>

        <ol data-testid="guide-steps" className="mt-10 space-y-5">
          {STEPS.map((step) => (
            <li key={step.n} className="flex gap-4">
              <span className="mt-0.5 font-mono text-sm text-accent">{step.n}</span>
              <div>
                <h2 className="font-serif text-[1.15rem] leading-snug text-ink">
                  {t(step.titleKey)}
                </h2>
                <p className="mt-1 text-[14px] leading-6 text-muted">{t(step.bodyKey)}</p>
              </div>
            </li>
          ))}
        </ol>

        <div className="mt-10 flex flex-col gap-3 sm:flex-row sm:items-center">
          <button
            type="button"
            data-testid="guide-upload-btn"
            onClick={onPickData}
            disabled={uploading}
            className="rounded-full bg-accent px-5 py-2.5 text-[14px] text-white transition-opacity duration-200 hover:opacity-90 disabled:opacity-50"
          >
            {uploading ? t('app.uploading') : t('guide.haveData')}
          </button>
          <button
            type="button"
            data-testid="guide-sample-btn"
            onClick={onTrySample}
            disabled={uploading}
            className="rounded-full border border-border bg-panel px-5 py-2.5 text-[14px] text-ink transition-colors duration-200 hover:bg-cream disabled:opacity-50"
          >
            {t('guide.trySample')}
          </button>
        </div>

        <button
          type="button"
          data-testid="guide-write-paper"
          onClick={onWritePaper}
          className="mt-5 self-start text-[13px] text-muted transition-colors duration-200 hover:text-ink"
        >
          {t('guide.writePaper')}
        </button>

        {uploadError && (
          <p data-testid="upload-error" className="mt-4 text-sm text-danger">
            {uploadError}
          </p>
        )}
      </main>
    </div>
  )
}
