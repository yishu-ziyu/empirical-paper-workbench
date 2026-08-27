import type { ReactNode } from 'react'
import { useT } from '../lib/i18n'

export function BrandMark() {
  const { t } = useT()
  return (
    <span className="inline-flex items-center gap-2.5">
      <span
        aria-hidden
        className="flex h-8 w-8 items-center justify-center rounded-full bg-ink font-serif text-[15px] leading-none text-white"
      >
        e
      </span>
      <span className="text-[15px] font-medium tracking-tight text-ink">{t('app.title')}</span>
    </span>
  )
}

export function LangPills() {
  const { lang, setLang } = useT()
  return (
    <div className="inline-flex rounded-full border border-black/10 bg-white p-0.5 text-[12px]">
      <button
        type="button"
        onClick={() => setLang('en')}
        className={`rounded-full px-2.5 py-1 transition-colors duration-200 ${
          lang === 'en' ? 'bg-black/5 text-ink' : 'text-muted hover:text-ink'
        }`}
      >
        English
      </button>
      <button
        type="button"
        onClick={() => setLang('zh')}
        className={`rounded-full px-2.5 py-1 transition-colors duration-200 ${
          lang === 'zh' ? 'bg-black/5 text-ink' : 'text-muted hover:text-ink'
        }`}
      >
        中文
      </button>
    </div>
  )
}

export function LangSwitch() {
  const { t, lang, setLang } = useT()
  return (
    <button
      type="button"
      onClick={() => setLang(lang === 'zh' ? 'en' : 'zh')}
      className="inline-flex items-center gap-1.5 rounded-full border border-black/15 bg-white px-3 py-1.5 text-[13px] text-ink/80 transition-colors duration-200 hover:border-black/30 hover:text-ink"
    >
      <svg className="h-3.5 w-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.75} aria-hidden>
        <circle cx="12" cy="12" r="9" />
        <path d="M3 12h18M12 3c2.5 3 3.8 6 3.8 9s-1.3 6-3.8 9c-2.5-3-3.8-6-3.8-9s1.3-6 3.8-9z" />
      </svg>
      {t('app.langSwitch')}
    </button>
  )
}

export interface UnauthHeaderProps {
  onLogin?: () => void
  onRegister?: () => void
  onHow?: () => void
  onPreview?: () => void
  onFeatures?: () => void
  extra?: ReactNode
}

export default function UnauthHeader({
  onLogin,
  onRegister,
  onHow,
  onPreview,
  onFeatures,
  extra,
}: UnauthHeaderProps) {
  const { t } = useT()
  const hasNav = Boolean(onHow || onPreview || onFeatures)

  return (
    <header className="sticky top-0 z-30 border-b border-black/[0.06] bg-white/90 backdrop-blur-md">
      <div className="mx-auto grid h-[64px] max-w-[1120px] grid-cols-[1fr_auto] items-center gap-4 px-6 md:grid-cols-[1fr_auto_1fr]">
        <BrandMark />
        {hasNav && (
          <nav className="hidden items-center gap-8 text-[14px] text-[#5c5c5c] md:flex">
            {onHow && (
              <button type="button" onClick={onHow} className="transition-colors duration-200 hover:text-ink">
                {t('guide.navHow')}
              </button>
            )}
            {onPreview && (
              <button type="button" onClick={onPreview} className="transition-colors duration-200 hover:text-ink">
                {t('guide.navPreview')}
              </button>
            )}
            {onFeatures && (
              <button type="button" onClick={onFeatures} className="transition-colors duration-200 hover:text-ink">
                {t('guide.navFeatures')}
              </button>
            )}
          </nav>
        )}
        <div className={`flex items-center gap-4 text-[14px] ${hasNav ? 'md:justify-self-end' : 'justify-self-end'}`}>
          {extra}
          {onLogin && (
            <button
              type="button"
              data-testid="open-login-btn"
              onClick={onLogin}
              className="text-[#5c5c5c] transition-colors duration-200 hover:text-ink"
            >
              {t('app.login')}
            </button>
          )}
          {onRegister && (
            <button
              type="button"
              onClick={onRegister}
              className="rounded-full bg-ink px-4 py-2 text-[13px] font-medium text-white transition-opacity duration-200 hover:opacity-90"
            >
              {t('app.signUp')}
            </button>
          )}
          <LangSwitch />
        </div>
      </div>
    </header>
  )
}
