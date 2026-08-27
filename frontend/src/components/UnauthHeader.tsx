import type { ReactNode } from 'react'
import { useT } from '../lib/i18n'

export function BrandMark() {
  const { t } = useT()
  return (
    <span className="inline-flex items-center gap-2.5">
      <span
        aria-hidden
        className="flex h-8 w-8 items-center justify-center rounded-lg bg-ink font-serif text-[16px] leading-none text-white"
      >
        e
      </span>
      <span className="text-[16px] font-medium tracking-tight text-ink">{t('app.title')}</span>
    </span>
  )
}

export function LangPills() {
  const { lang, setLang } = useT()
  return (
    <div className="inline-flex rounded-lg border border-border bg-panel p-0.5 text-[12px]">
      <button
        type="button"
        onClick={() => setLang('en')}
        className={`rounded-md px-2.5 py-1 transition-colors duration-200 ${
          lang === 'en' ? 'bg-accent/15 text-ink' : 'text-muted hover:text-ink'
        }`}
      >
        English
      </button>
      <button
        type="button"
        onClick={() => setLang('zh')}
        className={`rounded-md px-2.5 py-1 transition-colors duration-200 ${
          lang === 'zh' ? 'bg-accent/15 text-ink' : 'text-muted hover:text-ink'
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
      className="inline-flex items-center gap-1.5 text-[13px] text-muted transition-colors duration-200 hover:text-ink"
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
  extra?: ReactNode
}

export default function UnauthHeader({
  onLogin,
  onRegister,
  onHow,
  onPreview,
  extra,
}: UnauthHeaderProps) {
  const { t } = useT()
  const hasNav = Boolean(onHow || onPreview)

  return (
    <header className="sticky top-0 z-30 border-b border-border/80 bg-bg/92 backdrop-blur-md">
      <div className="mx-auto grid h-[72px] max-w-[1200px] grid-cols-[1fr_auto] items-center gap-4 px-6 md:grid-cols-[1fr_auto_1fr]">
        <BrandMark />
        {hasNav && (
          <nav className="hidden items-center gap-8 text-[14px] text-ink/75 md:flex">
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
          </nav>
        )}
        <div className={`flex items-center gap-4 text-[14px] ${hasNav ? 'md:justify-self-end' : 'justify-self-end'}`}>
          {extra}
          {onLogin && (
            <button
              type="button"
              data-testid="open-login-btn"
              onClick={onLogin}
              className="text-muted transition-colors duration-200 hover:text-ink"
            >
              {t('app.login')}
            </button>
          )}
          {onRegister && (
            <button
              type="button"
              onClick={onRegister}
              className="rounded-lg bg-accent px-4 py-2 text-[13px] font-medium text-white transition-opacity duration-200 hover:opacity-90"
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
