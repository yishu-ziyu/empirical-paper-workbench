import { useState } from 'react'
import type { FormEvent, KeyboardEvent } from 'react'
import UnauthHeader from '../components/UnauthHeader'
import { API_BASE, apiFetch } from '../lib/apiBase'
import { useT } from '../lib/i18n'

interface LoginPageProps {
  onLogin: (token: string) => void
  onSwitchToRegister: () => void
  onHome?: () => void
}

export default function LoginPage({ onLogin, onSwitchToRegister, onHome }: LoginPageProps) {
  const { t } = useT()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [shakeKey, setShakeKey] = useState(0)
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState(false)
  const [showPw, setShowPw] = useState(false)
  const [capsOn, setCapsOn] = useState(false)

  const detectCaps = (e: KeyboardEvent<HTMLInputElement>) => {
    setCapsOn(e.getModifierState?.('CapsLock') ?? false)
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const resp = await apiFetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })

      if (!resp.ok) {
        const data = await resp.json()
        throw new Error(data.detail || 'Login failed')
      }

      const data = await resp.json()
      // Success morph: ✓ lands before the desk takes over.
      setDone(true)
      setTimeout(() => onLogin(data.access_token), 450)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
      setShakeKey((k) => k + 1)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div data-testid="login-page" className="min-h-screen bg-bg text-ink">
      <UnauthHeader onHome={onHome} onRegister={onSwitchToRegister} />
      <main className="mx-auto flex w-full max-w-[420px] flex-col px-6 pb-24 pt-24">
        <h1 className="font-serif text-[2rem] leading-tight tracking-tight text-ink">
          {t('login.subtitle')}
        </h1>
        <p className="mt-2 text-[14px] text-muted">{t('app.title')}</p>

        <form onSubmit={handleSubmit} className="mt-10 space-y-4">
          <div>
            <label htmlFor="login-email" className="block text-[12px] text-muted mb-1.5">
              {t('login.email')}
            </label>
            <input
              id="login-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
              className="w-full rounded-lg border border-border bg-white px-3.5 py-2.5 text-sm text-ink outline-none transition-all duration-200 focus:border-ink/30 focus:shadow-[0_0_0_3px_rgba(0,0,0,0.04)]"
              placeholder={t('login.emailPlaceholder')}
            />
          </div>

          <div>
            <label htmlFor="login-password" className="block text-[12px] text-muted mb-1.5">
              {t('login.password')}
            </label>
            <div className="relative">
              <input
                id="login-password"
                type={showPw ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyUp={detectCaps}
                onKeyDown={detectCaps}
                required
                minLength={8}
                autoComplete="current-password"
                className="w-full rounded-lg border border-border bg-white px-3.5 py-2.5 pr-11 text-sm text-ink outline-none transition-all duration-200 focus:border-ink/30 focus:shadow-[0_0_0_3px_rgba(0,0,0,0.04)]"
                placeholder={t('login.passwordPlaceholder')}
              />
              <button
                type="button"
                aria-label={showPw ? t('login.hidePassword') : t('login.showPassword')}
                onClick={() => setShowPw((v) => !v)}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 rounded p-1 text-muted transition-colors duration-150 hover:text-ink"
              >
                {showPw ? (
                  <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
                    <path d="M3 3l18 18M10.6 10.6a2.4 2.4 0 002.8 2.8" />
                    <path d="M9.9 5.2A9.8 9.8 0 0121 12a15 15 0 01-2.2 2.9M6.1 6.1A14.7 14.7 0 003 12a9.8 9.8 0 0012.9 5.1" />
                  </svg>
                ) : (
                  <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
                    <path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z" />
                    <circle cx="12" cy="12" r="2.6" />
                  </svg>
                )}
              </button>
            </div>
            {capsOn && (
              <p className="mt-1 text-[11.5px] text-muted">⇪ {t('login.capsLock')}</p>
            )}
          </div>

          {error && (
            <div
              key={shakeKey}
              className="animate-shake rounded-lg border border-danger/20 bg-danger/5 px-3 py-2 text-xs text-danger"
            >
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || done}
            className={`w-full rounded-lg bg-ink px-4 py-2.5 text-sm font-medium text-white transition-all duration-200 hover:opacity-90 disabled:opacity-70 ${done ? 'animate-pop' : ''}`}
          >
            {done ? (
              <svg className="auth-check mx-auto" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 12.5l5 5L20 7" />
              </svg>
            ) : loading ? (
              t('login.signingIn')
            ) : (
              t('login.signIn')
            )}
          </button>
        </form>

        <p className="mt-6 text-center text-[13px] text-muted">
          {t('login.noAccount')}{' '}
          <button
            type="button"
            onClick={onSwitchToRegister}
            className="text-ink underline-offset-4 transition-colors duration-200 hover:underline"
          >
            {t('login.createOne')}
          </button>
        </p>
      </main>
    </div>
  )
}
